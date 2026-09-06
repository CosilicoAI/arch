import hashlib
import json
from pathlib import Path

import pytest

from axiom_corpus.corpus.artifacts import CorpusArtifactStore
from axiom_corpus.corpus.io import load_provisions, load_source_inventory
from axiom_corpus.corpus.israel_openlaw import (
    ISRAEL_OPENLAW_SOURCE_FORMAT,
    IsraelOpenLawManifest,
    IsraelOpenLawSource,
    extract_israel_openlaw,
    hebrew_suffix_slug,
    israeli_ident_slug,
    latin_ordinal_slug,
    parse_israel_openlaw_html,
)
from axiom_corpus.corpus.supabase import deterministic_provision_id

REPO_ROOT = Path(__file__).resolve().parents[1]
IL_PILOT_VERSION = "2026-09-06-il-taxben-pilot"
IL_PILOT_MANIFEST = REPO_ROOT / "manifests" / "il-taxben-pilot-openlaw.yaml"
IL_PILOT_SOURCE_DIR = (
    REPO_ROOT / "data" / "corpus" / "sources" / "il" / "statute" / IL_PILOT_VERSION / "openlaw"
)
ITO = "il/statute/income-tax-ordinance"
NII = "il/statute/national-insurance-law-1995"

SAMPLE_TITLE = "פקודת דוגמה [נוסח חדש]"
SAMPLE_URL = "https://he.wikisource.org/wiki/%D7%A4%D7%A7%D7%95%D7%93%D7%AA_%D7%93%D7%95%D7%92%D7%9E%D7%94"

# A miniature OpenLaw page exercising every structural hazard the real snapshots
# contain: nested navigation, a suffixed section, a two-letter suffix whose
# gematria value differs from its letter position, a letter+digit tail, folded
# sub-item anchors, an editorial note, a note-introduced historical table, a
# repeal status line, and an in-text cross-reference that must not split.
SAMPLE_HTML = """\
<!doctype html>
<html lang="he" dir="rtl">
  <body>
    <div class="mw-parser-output">
      <div class="law" id="law-content">
        <h1 class="law-title mw-html-heading">פקודת דוגמה [נוסח חדש]</h1>
        <hr class="law-separator"/>
        <div>2000944 ס״ח תשכ״א, 47</div>
        <h2 class="law-section mw-html-heading">תוכן עניינים</h2>
        <div><div class="law-toc-2">חלק א׳</div></div>
        <h1 class="law-part mw-html-heading">חלק א׳: פרשנות</h1>
        <h2 class="law-section mw-html-heading">פרק ראשון: המקור</h2>
        <h3 class="law-subsection mw-html-heading">סימן א׳: פטור</h3>
        <div class="law-number tc_ selflink" id="סעיף_2"><a href="#סעיף_2">2.</a> </div>
        <div class="law-desc"><span class="law-float"></span>מקורות הכנסה <span
          class="law-note">[תיקון: תשס״ב־9]</span></div>
        <div class="law-main"><div>
        </div>
        <div class="law-content1"> מס הכנסה יהא משתלם לפי סעיף 121ב לפקודה.
        </div></div>
        <div class="law-cleaner"></div>
        <div class="law-number tc_ selflink" id="סעיף_2.1"><a href="#סעיף_2.1"></a> </div>
        <div class="law-desc"><span class="law-float"></span>עסק ומשלח־יד</div>
        <div class="law-main"><div>
        </div>
        <div class="law-number2 tc_">(1) </div><div class="law-content2"> השתכרות מכל עסק.
        </div></div>
        <div class="law-cleaner"></div>
        <div class="law-number tc_ selflink" id="סעיף_103כ"><a href="#סעיף_103כ">103כ.</a> </div>
        <div class="law-desc"><span class="law-float"></span>הוראות מעבר</div>
        <div class="law-main"><div>
        </div>
        <div class="law-number2 tc_">(א) </div><div class="law-content2"> הוראה ראשונה.
        </div>
        <div class="law-number2 tc_">(ב) </div><div class="law-content2"> הוראה שנייה <span
          class="law-note">(הערת עורך)</span>.
        </div></div>
        <div class="law-cleaner"></div>
        <div class="law-main"><div>
        </div>
        <div class="law-content1"> <span class="law-note">להלן מדרגות המס:</span>
        <div style="text-align: right;">
        <table><tbody><tr><td>2019</td><td>10%</td></tr></tbody></table>
        </div>
        </div></div>
        <div class="law-cleaner"></div>
        <div class="law-number tc_ selflink" id="סעיף_64א7ב"><a href="#סעיף_64א7ב">64א7ב.</a> </div>
        <div class="law-desc"><span class="law-float"></span> <span
          class="law-note">[תיקון: תשפ״ה־2]</span></div>
        <div class="law-main"><div>
        </div>
        <div class="law-content1"> <span class="law-note">(בוטל).</span>
        </div></div>
        <div class="law-cleaner"></div>
        <h2 class="law-section mw-html-heading">לוח ט״ז1</h2>
        <div class="law-number tc_ selflink" id="לוח_טז1_פרט_א"><a href="#לוח_טז1_פרט_א">(א)</a> </div>
        <div class="law-desc"><span class="law-float"></span>פרט ראשון</div>
        <div class="law-main"><div>
        </div>
        <div class="law-content1"> סכום הפרט.
        </div></div>
      </div>
    </div>
  </body>
</html>
"""


def _sample_mapping(**overrides: object) -> dict[str, object]:
    mapping: dict[str, object] = {
        "source_id": "sample-ordinance",
        "jurisdiction": "il",
        "document_class": "statute",
        "instrument_slug": "sample-ordinance",
        "israel_law_id": "2000944",
        "title": SAMPLE_TITLE,
        "title_en": "Sample Ordinance [New Version]",
        "source_url": SAMPLE_URL,
        "source_file": "sample.html",
        "sha256": "0" * 64,
        "source_as_of": "2026-09-06",
        "expression_date": "2026-06-08",
        "expression_date_basis": "Knesset OData KNS_IsraelLaw.LatestPublicationDate",
        "language": "he",
        "expected_section_count": 3,
        "expected_schedule_item_count": 1,
        "expected_part_count": 1,
        "expected_chapter_count": 1,
        "expected_sign_count": 1,
    }
    mapping.update(overrides)
    return mapping


def _sample_source(**overrides: object) -> IsraelOpenLawSource:
    return IsraelOpenLawSource.from_mapping(_sample_mapping(**overrides))


def _write_manifest(path: Path, source: dict[str, object]) -> None:
    path.write_text(json.dumps({"documents": [source]}, ensure_ascii=False), encoding="utf-8")


# --- transliteration -------------------------------------------------------


@pytest.mark.parametrize(
    ("suffix", "expected"),
    [
        ("א", "a"),
        ("ב", "b"),
        ("ט", "i"),
        ("י", "j"),
        ("יא", "k"),
        ("יב", "l"),
        ("טו", "o"),
        ("טז", "p"),
        ("יט", "s"),
        # כ is the 11th Hebrew letter but the 20th enumeration position; a
        # letter-position mapping would collide it with יא -> k.
        ("כ", "t"),
        ("כו", "z"),
        ("כז", "aa"),
        ("ל", "ad"),
        ("לד", "ah"),
    ],
)
def test_hebrew_suffix_slug_follows_enumeration_ordinal(suffix: str, expected: str) -> None:
    assert hebrew_suffix_slug(suffix) == expected


def test_enumeration_suffixes_never_collide() -> None:
    canonical = [
        "א", "ב", "ג", "ד", "ה", "ו", "ז", "ח", "ט", "י",
        "יא", "יב", "יג", "יד", "טו", "טז", "יז", "יח", "יט", "כ",
        "כא", "כב", "כג", "כד", "כה", "כו", "כז", "כח", "כט", "ל",
        "לא", "לב", "לג", "לד",
    ]
    slugs = [hebrew_suffix_slug(suffix) for suffix in canonical]
    assert slugs == [latin_ordinal_slug(index) for index in range(1, len(canonical) + 1)]
    assert len(set(slugs)) == len(slugs)


@pytest.mark.parametrize(
    ("ident", "expected"),
    [
        ("121", "121"),
        ("121ב", "121b"),
        ("120ב", "120b"),
        ("66א", "66a"),
        ("103יא", "103k"),
        ("103כ", "103t"),
        ("75טז1", "75p1"),
        ("64א7ב", "64a7b"),
        ("179לד", "179ah"),
        ("ט״ז1", "p1"),
    ],
)
def test_israeli_ident_slug(ident: str, expected: str) -> None:
    assert israeli_ident_slug(ident) == expected


@pytest.mark.parametrize("ident", ["", "121(א)", "121-ב", "121x"])
def test_israeli_ident_slug_rejects_unsupported_identifiers(ident: str) -> None:
    with pytest.raises(ValueError):
        israeli_ident_slug(ident)


def test_hebrew_suffix_slug_accepts_final_forms() -> None:
    assert hebrew_suffix_slug("ך") == hebrew_suffix_slug("כ")


# --- parser ----------------------------------------------------------------


def test_parse_folds_sub_items_and_keeps_editorial_apparatus_out_of_bodies() -> None:
    provisions = parse_israel_openlaw_html(SAMPLE_HTML, source=_sample_source())

    assert [item.kind for item in provisions] == [
        "document",
        "part",
        "chapter",
        "sign",
        "section",
        "section",
        "section",
        "schedule",
        "schedule-item",
    ]
    document, part, chapter, sign, section_2, section_103t, section_64a7b, schedule, item = (
        provisions
    )

    # Navigation nests; sections stay flat, per the Israel citation scheme.
    assert document.citation_path == "il/statute/sample-ordinance"
    assert part.citation_path == "il/statute/sample-ordinance/part-1"
    assert chapter.citation_path == "il/statute/sample-ordinance/part-1/chapter-1"
    assert sign.citation_path == "il/statute/sample-ordinance/part-1/chapter-1/sign-1"
    assert section_2.citation_path == "il/statute/sample-ordinance/section-2"
    assert section_2.parent_citation_path == sign.citation_path
    assert section_2.level == sign.level + 1

    # The table of contents is navigation chrome, never a provision.
    assert all((item.heading or "") != "תוכן עניינים" for item in provisions)

    # A dotted sub-item anchor folds into its section instead of splitting it,
    # and an in-text cross-reference to §121ב does not open a new section.
    assert section_2.body == "מס הכנסה יהא משתלם לפי סעיף 121ב לפקודה.\n(1) השתכרות מכל עסק."
    assert section_2.metadata["sub_item_headings"] == [
        {"identifier": "2.1", "heading": "עסק ומשלח־יד"}
    ]
    assert section_2.heading == "מקורות הכנסה"
    assert section_2.metadata["amendment_history"] == "[תיקון: תשס״ב־9]"
    assert "[תיקון" not in section_2.body


def test_parse_drops_note_only_blocks_but_records_them() -> None:
    provisions = parse_israel_openlaw_html(SAMPLE_HTML, source=_sample_source())
    section = next(item for item in provisions if item.citation_path.endswith("/section-103t"))

    assert section.body == "(א) הוראה ראשונה.\n(ב) הוראה שנייה."
    # The editorial parenthetical and the note-introduced historical table are
    # both gone from the body and both preserved in metadata.
    assert section.metadata["editorial_notes"] == ["(הערת עורך)", "להלן מדרגות המס:"]
    assert "2019" not in (section.body or "")
    assert "10%" not in (section.body or "")


def test_parse_keeps_a_repeal_status_line_as_the_body() -> None:
    provisions = parse_israel_openlaw_html(SAMPLE_HTML, source=_sample_source())
    section = next(item for item in provisions if item.citation_path.endswith("/section-64a7b"))

    assert section.body == "(בוטל)."
    assert section.metadata["status_marker"] == "בוטל"
    assert section.metadata["operative"] is False
    assert section.heading is None


def test_parse_binds_schedule_items_to_their_schedule() -> None:
    provisions = parse_israel_openlaw_html(SAMPLE_HTML, source=_sample_source())
    schedule = next(item for item in provisions if item.kind == "schedule")
    item = next(item for item in provisions if item.kind == "schedule-item")

    assert schedule.citation_path == "il/statute/sample-ordinance/schedule-p1"
    assert schedule.heading == "לוח ט״ז1"
    assert item.citation_path == "il/statute/sample-ordinance/schedule-p1/item-a"
    assert item.parent_citation_path == schedule.citation_path
    assert item.body == "סכום הפרט."


def test_parse_rejects_a_title_that_disagrees_with_the_manifest() -> None:
    with pytest.raises(ValueError, match="title mismatch"):
        parse_israel_openlaw_html(SAMPLE_HTML, source=_sample_source(title="פקודה אחרת"))


def test_parse_rejects_a_page_for_another_knesset_law_id() -> None:
    with pytest.raises(ValueError, match="IsraelLawID"):
        parse_israel_openlaw_html(SAMPLE_HTML, source=_sample_source(israel_law_id="2000198"))


def test_parse_rejects_an_undeclared_duplicate_section_anchor() -> None:
    duplicated = SAMPLE_HTML.replace(
        '<div class="law-number tc_ selflink" id="סעיף_64א7ב">'
        '<a href="#סעיף_64א7ב">64א7ב.</a> </div>',
        '<div class="law-number tc_ selflink" id="סעיף_103כ">'
        '<a href="#סעיף_103כ">103כ.</a> </div>',
    )
    with pytest.raises(ValueError, match="alternate_version_sections"):
        parse_israel_openlaw_html(duplicated, source=_sample_source())

    provisions = parse_israel_openlaw_html(
        duplicated,
        source=_sample_source(alternate_version_sections=["103כ"]),
    )
    paths = [item.citation_path for item in provisions]
    assert "il/statute/sample-ordinance/section-103t" in paths
    assert "il/statute/sample-ordinance/section-103t-alt2" in paths
    base = next(item for item in provisions if item.citation_path.endswith("/section-103t"))
    alternate = next(
        item for item in provisions if item.citation_path.endswith("/section-103t-alt2")
    )
    assert base.metadata["has_alternate_versions"] is True
    assert alternate.metadata["alternate_of"] == base.citation_path


# --- manifest --------------------------------------------------------------


@pytest.mark.parametrize(
    ("overrides", "error"),
    [
        ({"jurisdiction": "us"}, "jurisdiction must be il"),
        ({"document_class": "regulation"}, "document_class must be statute"),
        ({"language": "en"}, "language must be he"),
        ({"language": True}, "not a YAML boolean"),
        ({"source_url": "https://www.nevo.co.il/law_html/law01/255_001.htm"}, "he.wikisource.org"),
        ({"sha256": "abc"}, "SHA-256"),
        ({"source_file": "../escape.html"}, "plain file name"),
        ({"source_file": "sample.pdf"}, "must be HTML"),
        ({"israel_law_id": "2000944x"}, "only digits"),
        ({"expected_section_count": -1}, "expected_section_count"),
        ({"instrument_slug": "Income_Tax"}, "instrument_slug"),
    ],
)
def test_manifest_rejects_invalid_rows(overrides: dict[str, object], error: str) -> None:
    with pytest.raises(ValueError, match=error):
        IsraelOpenLawSource.from_mapping(_sample_mapping(**overrides))


def test_manifest_rejects_duplicate_instruments(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    path.write_text(
        json.dumps(
            {"documents": [_sample_mapping(), _sample_mapping(source_id="other")]},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate Israel instrument_slug"):
        IsraelOpenLawManifest.load(path)


# --- extraction ------------------------------------------------------------


def test_extract_writes_versioned_complete_artifacts(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    payload = SAMPLE_HTML.encode("utf-8")
    (source_dir / "sample.html").write_bytes(payload)
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, _sample_mapping(sha256=hashlib.sha256(payload).hexdigest()))
    store = CorpusArtifactStore(tmp_path / "corpus")

    report = extract_israel_openlaw(
        store,
        version="2026-09-06-sample",
        manifest_path=manifest_path,
        source_dir=source_dir,
    )

    assert report.jurisdiction == "il"
    assert report.document_class == "statute"
    assert report.section_count == 3
    assert report.schedule_item_count == 1
    assert report.provisions_written == 9
    assert report.coverage.complete

    provisions = load_provisions(report.provisions_path)
    inventory = load_source_inventory(report.inventory_path)
    assert len(provisions) == len(inventory) == 9
    assert {record.language for record in provisions} == {"he"}
    assert {record.source_format for record in provisions} == {ISRAEL_OPENLAW_SOURCE_FORMAT}
    assert {record.expression_date for record in provisions} == {"2026-06-08"}
    assert {record.source_as_of for record in provisions} == {"2026-09-06"}
    assert all(record.body for record in provisions)
    section = next(record for record in provisions if record.citation_path.endswith("/section-2"))
    assert section.id == deterministic_provision_id(section.citation_path, "2026-09-06-sample")
    assert section.source_path == (
        "sources/il/statute/2026-09-06-sample/openlaw/sample.html"
    )
    assert section.metadata is not None
    assert section.metadata["source_tier"] == "consolidation-knesset-linked"
    assert section.identifiers is not None
    assert section.identifiers["knesset.gov.il:israel_law_id"] == "2000944"


def test_extract_rejects_a_hash_mismatch_before_writing_artifacts(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "sample.html").write_bytes(SAMPLE_HTML.encode("utf-8"))
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, _sample_mapping())
    corpus_root = tmp_path / "corpus"

    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        extract_israel_openlaw(
            CorpusArtifactStore(corpus_root),
            version="2026-09-06-sample",
            manifest_path=manifest_path,
            source_dir=source_dir,
        )
    assert not corpus_root.exists()


def test_extract_rejects_a_structural_count_drift_before_writing_artifacts(tmp_path: Path) -> None:
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    payload = SAMPLE_HTML.encode("utf-8")
    (source_dir / "sample.html").write_bytes(payload)
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        _sample_mapping(sha256=hashlib.sha256(payload).hexdigest(), expected_section_count=4),
    )
    corpus_root = tmp_path / "corpus"

    with pytest.raises(ValueError, match="expected_section_count mismatch"):
        extract_israel_openlaw(
            CorpusArtifactStore(corpus_root),
            version="2026-09-06-sample",
            manifest_path=manifest_path,
            source_dir=source_dir,
        )
    assert not corpus_root.exists()


# --- checked-in pilot pack -------------------------------------------------


def test_pilot_manifest_pins_both_instruments() -> None:
    manifest = IsraelOpenLawManifest.load(IL_PILOT_MANIFEST)

    assert {source.instrument_slug for source in manifest.documents} == {
        "income-tax-ordinance",
        "national-insurance-law-1995",
    }
    assert {source.israel_law_id: source.expression_date for source in manifest.documents} == {
        "2000944": "2026-06-08",
        "2000198": "2026-06-15",
    }
    assert {source.source_as_of for source in manifest.documents} == {"2026-09-06"}
    assert {source.language for source in manifest.documents} == {"he"}
    counts = {source.instrument_slug: source.expected_section_count for source in manifest.documents}
    assert counts == {"income-tax-ordinance": 548, "national-insurance-law-1995": 561}
    for source in manifest.documents:
        snapshot = IL_PILOT_SOURCE_DIR / source.source_file
        assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == source.sha256


def test_checked_in_pilot_pack_parses_to_exact_counts(tmp_path: Path) -> None:
    store = CorpusArtifactStore(tmp_path / "corpus")
    report = extract_israel_openlaw(
        store,
        version=IL_PILOT_VERSION,
        manifest_path=IL_PILOT_MANIFEST,
        source_dir=IL_PILOT_SOURCE_DIR,
    )

    assert report.document_count == 2
    assert report.section_count == 1109
    assert report.schedule_item_count == 30
    assert report.navigation_count == 224
    assert report.provisions_written == 1365
    assert report.coverage.complete

    provisions = {record.citation_path: record for record in load_provisions(report.provisions_path)}

    rate_schedule = provisions[f"{ITO}/section-121"]
    assert rate_schedule.heading == "שיעור המס ליחיד"
    assert rate_schedule.body is not None
    for percentage in ("10%", "14%", "20%", "31%", "35%", "47%"):
        assert percentage in rate_schedule.body
    for edge in ("84,120", "120,720", "228,000", "301,200", "560,280"):
        assert edge in rate_schedule.body
    # The 2019-2027 comparison table OpenLaw prints under §121 is editorial.
    assert "75,720" not in rate_schedule.body
    assert rate_schedule.metadata is not None
    assert any(
        note.startswith("(הסכומים מתואמים")
        for note in rate_schedule.metadata["editorial_notes"]
    )

    resident_credit = provisions[f"{ITO}/section-34"]
    assert resident_credit.body == (
        "בחישוב המס של יחיד שהיה תושב ישראל בשנת המס יובאו בחשבון שתי נקודות זיכוי."
    )
    travel_credit = provisions[f"{ITO}/section-36"]
    assert travel_credit.body is not None
    assert "1⁄4" in travel_credit.body

    surtax = provisions[f"{ITO}/section-121b"]
    assert surtax.heading == "מס נוסף על הכנסות גבוהות"

    child_allowance = provisions[f"{NII}/section-66"]
    assert child_allowance.heading is not None
    assert child_allowance.heading.startswith("זכות לקצבת ילדים")
    assert child_allowance.body is not None
    assert "סעיף 121ב לפקודת מס הכנסה" in child_allowance.body
    assert f"{NII}/section-65" in provisions
    assert f"{NII}/section-335" in provisions

    # The National Insurance Law prints §283 twice; both survive, distinctly.
    assert provisions[f"{NII}/section-283-alt2"].metadata is not None
    assert provisions[f"{NII}/section-283-alt2"].metadata["alternate_version"] is True

    # OpenLaw prints "57א" against the anchor for §57ג; the anchor wins and the
    # disagreement is recorded rather than silently resolved.
    mismatched = provisions[f"{NII}/section-57c"]
    assert mismatched.metadata is not None
    assert mismatched.metadata["printed_label_mismatch"] is True
    assert mismatched.metadata["printed_label"] == "57א"

    assert all(record.body for record in provisions.values())
    assert all(record.expression_date for record in provisions.values())
    assert all(record.language == "he" for record in provisions.values())


def test_checked_in_pilot_artifacts_match_a_fresh_extraction(tmp_path: Path) -> None:
    committed = load_provisions(
        REPO_ROOT / "data" / "corpus" / "provisions" / "il" / "statute" / f"{IL_PILOT_VERSION}.jsonl"
    )
    report = extract_israel_openlaw(
        CorpusArtifactStore(tmp_path / "corpus"),
        version=IL_PILOT_VERSION,
        manifest_path=IL_PILOT_MANIFEST,
        source_dir=IL_PILOT_SOURCE_DIR,
    )
    assert load_provisions(report.provisions_path) == committed
