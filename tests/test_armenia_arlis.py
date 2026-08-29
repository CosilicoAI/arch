import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from axiom_corpus.corpus.armenia_arlis import (
    ARMENIA_ARLIS_SOURCE_FORMAT,
    ArmeniaARLISManifest,
    ArmeniaARLISSource,
    extract_armenia_arlis,
    parse_armenia_arlis_html,
)
from axiom_corpus.corpus.artifacts import CorpusArtifactStore
from axiom_corpus.corpus.io import load_provisions, load_source_inventory
from axiom_corpus.corpus.supabase import deterministic_provision_id

REPO_ROOT = Path(__file__).resolve().parents[1]
AM_TAXBEN_CORE_VERSION = "2026-08-29-am-taxben-core"

SAMPLE_ARLIS_HTML = """\
<!doctype html>
<html lang="hy">
  <head><title>ՓՈՐՁՆԱԿԱՆ ՕՐԵՆՔ</title></head>
  <body>
    <div class="act-info__item">
      <div class="act-info__label">Համար</div>
      <div class="act-info__value">ՀՕ-1-Ն</div>
    </div>
    <div class="act-info__item">
      <div class="act-info__label">Ընդունման ամսաթիվ</div>
      <div class="act-info__value">01.01.2026</div>
    </div>
    <div class="act-info__item">
      <div class="act-info__label">Փաստաթղթի տեսակ</div>
      <div class="act-info__value">
        Պաշտոնական Ինկորպորացիա (01.09.2026-մինչ օրս)
      </div>
    </div>
    <div class="act-changes-history__couple current-act">
      <div class="act-changes-history__item">
        <a class="act-link" href="/hy/acts/999999">Amendment</a>
      </div>
      <div class="act-changes-history__item">
        <a class="act-link" href="/hy/acts/230171">Current act</a>
      </div>
      <div class="act-changes-history__couple-compare"
           data-request-url="/hy/acts/230171/compare/230171"></div>
    </div>
    <div id="act_body">
      <div class="act-block__section">
        <p>ՀԱՅԱՍՏԱՆԻ ՀԱՆՐԱՊԵՏՈՒԹՅԱՆ ՕՐԵՆՔԸ</p>
        <p>Մ Ա Ս 1</p>
        <p>ԸՆԴՀԱՆՈՒՐ ՄԱՍ</p>
        <p>Բ Ա Ժ Ի Ն 2</p>
        <p>ՀԱՐԿԵՐ</p>
        <p>Գ Լ ՈՒ Խ 3.1(գլուխը լրաց. 01.09.26 ՀՕ-1-Ն)</p>
        <p>ՍՈՑԻԱԼԱԿԱՆ ԾԱԽՍԵՐ</p>
        <p><strong>
          <table><tr>
            <td>&nbsp;<a href="/acts/files/court"><b>⚖</b></a><strong>Հ<a name="split"></a>ոդված 293․1.</strong></td>
            <td><strong>Սոցիալական<b> ծախսերը</b></strong></td>
          </tr></table>
        </strong></p>
        <p>1. Շահառուն վճարում է 10 տոկոս։</p>
        <p>(293․1-ին հոդվածը լրաց. 01.09.26 ՀՕ-1-Ն)</p>
        <table><tr>
          <td><strong>Հոդված294.</strong></td>
          <td><strong>Հաջորդ դրույթը</strong></td>
        </tr></table>
        <p>1. Պահպանվում են «մեջբերումը», շեշտը՝ և հարցականը՞</p>
        <table><tr><td>&nbsp;Հավելված 1</td></tr></table>
        <p>ՀԱՎԵԼՎԱԾԻ ՎԵՐՆԱԳԻՐԸ</p>
        <p>Հավելվածի դրույթը։</p>
        <table><tr>
          <td>Հայաստանի Հանրապետության Նախագահ</td>
          <td>Ա. Անուն</td>
        </tr></table>
      </div>
    </div>
  </body>
</html>
"""


def _source_mapping(*, sha256: str, expected_article_count: int = 2) -> dict[str, object]:
    return {
        "source_id": "sample-statute",
        "jurisdiction": "am",
        "document_class": "statute",
        "act_id": "230171",
        "official_number": "ՀՕ-1-Ն",
        "adopted": "2026-01-01",
        "title": "ՓՈՐՁՆԱԿԱՆ ՕՐԵՆՔ",
        "source_url": "https://www.arlis.am/hy/acts/230171/latest",
        "source_file": "sample.html",
        "sha256": sha256,
        "source_as_of": "2026-08-29",
        "expression_date": "2026-09-01",
        "language": "hy",
        "expected_article_count": expected_article_count,
    }


def _sample_source() -> ArmeniaARLISSource:
    content = SAMPLE_ARLIS_HTML.encode()
    return ArmeniaARLISSource.from_mapping(
        _source_mapping(sha256=hashlib.sha256(content).hexdigest())
    )


def _write_manifest(path: Path, source: dict[str, object]) -> None:
    path.write_text(
        json.dumps({"documents": [source]}, ensure_ascii=False),
        encoding="utf-8",
    )


def test_campaign_manifest_pins_all_six_corrected_article_counts_and_dates():
    manifest = ArmeniaARLISManifest.load(REPO_ROOT / "manifests" / "am-taxben-core-arlis.yaml")

    counts = {source.source_id: source.expected_article_count for source in manifest.documents}
    assert counts == {
        "tax-code": 474,
        "funded-pensions": 81,
        "universal-health-insurance": 46,
        "servicemen-compensation": 32,
        "state-benefits": 44,
        "state-pensions": 58,
    }
    assert sum(counts.values()) == 735
    assert {source.source_id: source.expression_date for source in manifest.documents} == {
        "tax-code": "2026-09-01",
        "funded-pensions": "2026-05-18",
        "universal-health-insurance": "2026-05-08",
        "servicemen-compensation": "2026-09-01",
        "state-benefits": "2026-09-01",
        "state-pensions": "2026-09-01",
    }
    assert {source.source_as_of for source in manifest.documents} == {"2026-08-29"}
    assert {source.language for source in manifest.documents} == {"hy"}


def test_parse_armenia_arlis_preserves_split_headers_hierarchy_and_punctuation():
    provisions = parse_armenia_arlis_html(
        SAMPLE_ARLIS_HTML,
        source=_sample_source(),
    )

    assert [item.kind for item in provisions] == [
        "document",
        "part",
        "section",
        "chapter",
        "article",
        "article",
        "appendix",
    ]
    document, part, section, chapter, article, next_article, appendix = provisions
    assert document.citation_path == "am/statute/act-230171"
    assert part.citation_path == "am/statute/act-230171/part-1"
    assert section.citation_path == "am/statute/act-230171/part-1/section-2"
    assert chapter.citation_path.endswith("/part-1/section-2/chapter-3.1")
    assert chapter.heading == "ՍՈՑԻԱԼԱԿԱՆ ԾԱԽՍԵՐ"
    assert chapter.body is not None
    assert chapter.body.startswith("(գլուխը լրաց. 01.09.26 ՀՕ-1-Ն)")

    assert article.citation_path == "am/statute/act-230171/article-293.1"
    assert article.parent_citation_path == chapter.citation_path
    assert article.heading == "Սոցիալական ծախսերը"
    assert article.body == (
        "1. Շահառուն վճարում է 10 տոկոս։\n(293․1-ին հոդվածը լրաց. 01.09.26 ՀՕ-1-Ն)"
    )
    assert article.metadata["raw_article_marker"].endswith("Հոդված 293․1.")
    assert article.metadata["court_decision_urls"] == ["https://www.arlis.am/acts/files/court"]
    assert next_article.label == "294"
    assert next_article.body == "1. Պահպանվում են «մեջբերումը», շեշտը՝ և հարցականը՞"
    assert appendix.citation_path == "am/statute/act-230171/appendix-1"
    assert appendix.heading == "ՀԱՎԵԼՎԱԾԻ ՎԵՐՆԱԳԻՐԸ"
    assert document.body is not None
    assert "Հայաստանի Հանրապետության Նախագահ" in document.body


def test_extract_armenia_arlis_writes_versioned_complete_artifacts(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    content = SAMPLE_ARLIS_HTML.encode()
    (source_dir / "sample.html").write_bytes(content)
    source_mapping = _source_mapping(sha256=hashlib.sha256(content).hexdigest())
    manifest_path = tmp_path / "manifest.yaml"
    _write_manifest(manifest_path, source_mapping)
    base = tmp_path / "corpus"

    report = extract_armenia_arlis(
        CorpusArtifactStore(base),
        version=AM_TAXBEN_CORE_VERSION,
        manifest_path=manifest_path,
        source_dir=source_dir,
    )

    assert report.jurisdiction == "am"
    assert report.document_class == "statute"
    assert report.document_count == 1
    assert report.article_count == 2
    assert report.structural_count == 4
    assert report.provisions_written == 7
    assert report.coverage.complete
    assert len(report.source_paths) == 1
    assert report.source_paths[0].read_bytes() == content

    records = load_provisions(report.provisions_path)
    inventory = load_source_inventory(report.inventory_path)
    article = next(record for record in records if record.kind == "article")
    assert article.id == deterministic_provision_id(
        article.citation_path,
        AM_TAXBEN_CORE_VERSION,
    )
    assert article.parent_citation_path is not None
    assert article.parent_id == deterministic_provision_id(
        article.parent_citation_path,
        AM_TAXBEN_CORE_VERSION,
    )
    assert article.source_as_of == "2026-08-29"
    assert article.expression_date == "2026-09-01"
    assert article.language == "hy"
    assert article.source_path is not None
    assert article.source_path.endswith(f"/am/statute/{AM_TAXBEN_CORE_VERSION}/arlis/sample.html")
    assert inventory[0].source_format == ARMENIA_ARLIS_SOURCE_FORMAT
    assert inventory[0].sha256 == hashlib.sha256(content).hexdigest()


def test_checked_in_six_document_pack_parses_to_exact_counts(tmp_path):
    source_dir = (
        REPO_ROOT
        / "data"
        / "corpus"
        / "sources"
        / "am"
        / "statute"
        / AM_TAXBEN_CORE_VERSION
        / "arlis"
    )

    report = extract_armenia_arlis(
        CorpusArtifactStore(tmp_path / "corpus"),
        version=AM_TAXBEN_CORE_VERSION,
        manifest_path=REPO_ROOT / "manifests" / "am-taxben-core-arlis.yaml",
        source_dir=source_dir,
    )

    assert {
        item.source_id: (item.article_count, item.structural_count)
        for item in report.document_reports
    } == {
        "tax-code": (474, 114),
        "funded-pensions": (81, 15),
        "universal-health-insurance": (46, 9),
        "servicemen-compensation": (32, 5),
        "state-benefits": (44, 14),
        "state-pensions": (58, 10),
    }
    assert report.article_count == 735
    assert report.structural_count == 167
    assert report.provisions_written == 908
    assert report.coverage.complete
    records = load_provisions(report.provisions_path)
    assert {record.expression_date for record in records} == {
        "2026-05-08",
        "2026-05-18",
        "2026-09-01",
    }
    assert {record.source_as_of for record in records} == {"2026-08-29"}
    records_by_path = {record.citation_path: record for record in records}
    assert len(records_by_path) == len(records)
    children_by_parent = {}
    for record in records:
        if record.parent_citation_path is None:
            continue
        parent = records_by_path[record.parent_citation_path]
        assert record.level == parent.level + 1
        children_by_parent.setdefault(record.parent_citation_path, []).append(record)
    for siblings in children_by_parent.values():
        ordinals = [record.ordinal for record in siblings]
        assert None not in ordinals
        assert ordinals == sorted(ordinals)
        assert len(ordinals) == len(set(ordinals))

    tax_document_path = "am/statute/act-230171"
    assert records_by_path[f"{tax_document_path}/article-1"].parent_citation_path == (
        f"{tax_document_path}/part-1/section-1/chapter-1"
    )
    assert records_by_path[f"{tax_document_path}/article-458"].parent_citation_path == (
        f"{tax_document_path}/part-4/section-22/chapter-82"
    )
    tax_appendices = [
        record
        for record in records
        if record.citation_path.startswith(f"{tax_document_path}/appendix-")
    ]
    assert len(tax_appendices) == 3
    assert {record.parent_citation_path for record in tax_appendices} == {tax_document_path}
    for label, heading_start, body_start in (
        (
            "78",
            "Ավելացված արժեքի հարկի գումարի վճարումը",
            "1. ԱԱՀ վճարողները",
        ),
        ("147.1", "Սոցիալական ծախսերը", "1. Սոցիալական ծախսեր են համարվում"),
    ):
        matches = [
            record
            for record in records
            if record.citation_path == f"am/statute/act-230171/article-{label}"
        ]
        assert len(matches) == 1
        assert matches[0].heading == heading_start
        assert matches[0].body is not None
        assert matches[0].body.startswith(body_start)
        assert matches[0].parent_citation_path is not None
        assert matches[0].parent_citation_path.startswith("am/statute/act-230171/")
    assert all("\xa0" not in (record.heading or "") for record in records)
    assert all("\xa0" not in (record.body or "") for record in records)
    servicemen_article_1 = next(
        record for record in records if record.citation_path == "am/statute/act-230046/article-1"
    )
    assert servicemen_article_1.heading == "Օրենքի կարգավորման առարկան"


def test_extract_armenia_arlis_rejects_hash_before_writing_artifacts(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "sample.html").write_text(SAMPLE_ARLIS_HTML, encoding="utf-8")
    manifest_path = tmp_path / "manifest.yaml"
    _write_manifest(manifest_path, _source_mapping(sha256="0" * 64))
    base = tmp_path / "corpus"

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        extract_armenia_arlis(
            CorpusArtifactStore(base),
            version=AM_TAXBEN_CORE_VERSION,
            manifest_path=manifest_path,
            source_dir=source_dir,
        )

    assert not base.exists()


def test_extract_armenia_arlis_rejects_article_count_before_writing_artifacts(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    content = SAMPLE_ARLIS_HTML.encode()
    (source_dir / "sample.html").write_bytes(content)
    manifest_path = tmp_path / "manifest.yaml"
    _write_manifest(
        manifest_path,
        _source_mapping(
            sha256=hashlib.sha256(content).hexdigest(),
            expected_article_count=3,
        ),
    )
    base = tmp_path / "corpus"

    with pytest.raises(ValueError, match="article count mismatch"):
        extract_armenia_arlis(
            CorpusArtifactStore(base),
            version=AM_TAXBEN_CORE_VERSION,
            manifest_path=manifest_path,
            source_dir=source_dir,
        )

    assert not base.exists()


def test_parse_armenia_arlis_rejects_unbound_article_marker():
    malformed = SAMPLE_ARLIS_HTML.replace(
        "<p>1. Շահառուն վճարում է 10 տոկոս։</p>",
        "<p><strong>Հոդված 999.</strong> Չկապված վերնագիր</p>",
    )

    with pytest.raises(ValueError, match="unrecognized article marker"):
        parse_armenia_arlis_html(malformed, source=_sample_source())


def test_parse_armenia_arlis_rejects_expression_date_drift():
    source = ArmeniaARLISSource.from_mapping(
        {
            **_source_mapping(sha256=hashlib.sha256(SAMPLE_ARLIS_HTML.encode()).hexdigest()),
            "expression_date": "2026-08-29",
        }
    )

    with pytest.raises(ValueError, match="expression_date mismatch"):
        parse_armenia_arlis_html(SAMPLE_ARLIS_HTML, source=source)


@pytest.mark.parametrize(
    ("changes", "error"),
    [
        ({"title": "ԱՅԼ ՕՐԵՆՔ"}, "title mismatch"),
        ({"official_number": "ՀՕ-999-Ն"}, "official_number mismatch"),
        ({"adopted": "2026-01-02"}, "adopted mismatch"),
        (
            {
                "act_id": "999999",
                "source_url": "https://www.arlis.am/hy/acts/999999/latest",
            },
            "act_id mismatch",
        ),
    ],
)
def test_parse_armenia_arlis_rejects_cross_labeled_source_identity(changes, error):
    source = replace(_sample_source(), **changes)

    with pytest.raises(ValueError, match=error):
        parse_armenia_arlis_html(SAMPLE_ARLIS_HTML, source=source)


def test_extract_armenia_arlis_rejects_cross_label_before_writing_artifacts(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    content = SAMPLE_ARLIS_HTML.encode()
    (source_dir / "sample.html").write_bytes(content)
    manifest_path = tmp_path / "manifest.yaml"
    source_mapping = _source_mapping(sha256=hashlib.sha256(content).hexdigest())
    source_mapping["official_number"] = "ՀՕ-999-Ն"
    _write_manifest(manifest_path, source_mapping)
    base = tmp_path / "corpus"

    with pytest.raises(ValueError, match="official_number mismatch"):
        extract_armenia_arlis(
            CorpusArtifactStore(base),
            version=AM_TAXBEN_CORE_VERSION,
            manifest_path=manifest_path,
            source_dir=source_dir,
        )

    assert not base.exists()


def test_extract_armenia_arlis_rejects_cross_labeled_act_id_before_writing_artifacts(
    tmp_path,
):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    content = SAMPLE_ARLIS_HTML.encode()
    (source_dir / "sample.html").write_bytes(content)
    manifest_path = tmp_path / "manifest.yaml"
    source_mapping = _source_mapping(sha256=hashlib.sha256(content).hexdigest())
    source_mapping["act_id"] = "999999"
    source_mapping["source_url"] = "https://www.arlis.am/hy/acts/999999/latest"
    _write_manifest(manifest_path, source_mapping)
    base = tmp_path / "corpus"

    with pytest.raises(ValueError, match="act_id mismatch"):
        extract_armenia_arlis(
            CorpusArtifactStore(base),
            version=AM_TAXBEN_CORE_VERSION,
            manifest_path=manifest_path,
            source_dir=source_dir,
        )

    assert not base.exists()


def test_parse_armenia_arlis_rejects_duplicate_article_label_across_chapters():
    duplicate = SAMPLE_ARLIS_HTML.replace(
        "        <table><tr><td>&nbsp;Հավելված 1</td></tr></table>",
        """\
        <p>Գ Լ ՈՒ Խ 4</p>
        <p>ԱՅԼ ԳԼՈՒԽ</p>
        <table><tr>
          <td><strong>Հոդված 293․1.</strong></td>
          <td><strong>Կրկնվող դրույթ</strong></td>
        </tr></table>
        <p>1. Կրկնվող հոդվածի տեքստը։</p>
        <table><tr><td>&nbsp;Հավելված 1</td></tr></table>""",
    )

    with pytest.raises(ValueError, match=r"duplicate article labels: 293\.1"):
        parse_armenia_arlis_html(duplicate, source=_sample_source())


def test_manifest_requires_quoted_dates_and_armenian_language():
    valid = _source_mapping(sha256="0" * 64)
    with pytest.raises(ValueError, match="explicitly quoted ISO date"):
        ArmeniaARLISSource.from_mapping({**valid, "source_as_of": object()})
    with pytest.raises(ValueError, match="language must be hy"):
        ArmeniaARLISSource.from_mapping({**valid, "language": "en"})
