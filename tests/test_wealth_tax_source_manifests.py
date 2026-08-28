from __future__ import annotations

from pathlib import Path

import fitz

from axiom_corpus.corpus.documents import OfficialDocumentManifest, _extract_blocks

REPO_ROOT = Path(__file__).resolve().parents[1]
SPAIN_MANIFEST = REPO_ROOT / "manifests/es-wealth-tax-statutes-official-documents.yaml"
ZURICH_MANIFEST = REPO_ROOT / "manifests/ch-zh-wealth-tax-official-documents.yaml"


def _source(manifest_path: Path, source_id: str):
    manifest = OfficialDocumentManifest.load(manifest_path)
    return next(source for source in manifest.documents if source.source_id == source_id)


def test_rdl_8_2023_extracts_only_retroactive_article_17() -> None:
    source = _source(SPAIN_MANIFEST, "es-rdl-8-2023-itsgf-exemption-amendment")
    html = """
    <main>
      <h3>Artículo 16. Unrelated prior provision</h3>
      <p>Prior body.</p>
      <h3>Artículo 17. Modificación del impuesto</h3>
      <p>Article 17 amendment body.</p>
      <h3>Artículo 18. Unrelated following provision</h3>
      <p>Following body.</p>
    </main>
    """.encode()

    blocks = _extract_blocks(
        html,
        "html",
        source_url=source.source_url,
        title=source.title,
        extraction=source.extraction,
    )

    assert source.expression_date == "2022-12-29"
    assert len(blocks) == 1
    assert blocks[0].metadata["citation_suffix"] == "articulo-17"
    assert blocks[0].body == "Article 17 amendment body."
    assert "Prior" not in blocks[0].body
    assert "Following" not in blocks[0].body


def test_zurich_2022_uses_direct_pdf_and_retains_only_section_47() -> None:
    source = _source(ZURICH_MANIFEST, "ch-zh-stg-2022-section-47-wealth-tax")
    assert source.download_url is not None
    assert "/WebView/" in source.download_url
    assert "/%24File/631.1_8.6.97_115.pdf" in source.download_url

    document = fitz.open()
    for page_number in range(1, 26):
        page = document.new_page()
        if page_number == 24:
            page.insert_text((72, 72), "§ 46. Prior provision")
            page.insert_text((72, 96), "§ 47. Wealth-tax tariff")
            page.insert_text((72, 120), "Tariff body on page 24")
        elif page_number == 25:
            page.insert_text((72, 72), "§ 47 continuation")
            page.insert_text((72, 96), "D. Ausgleich der kalten Progression")
            page.insert_text((72, 120), "§ 48. Following provision")
            page.insert_text((72, 144), "Following body")
    pdf = document.tobytes()
    document.close()

    blocks = _extract_blocks(
        pdf,
        "pdf",
        source_url=source.source_url,
        title=source.title,
        extraction=source.extraction,
    )

    assert len(blocks) == 1
    assert "§ 47. Wealth-tax tariff" in blocks[0].body
    assert "§ 47 continuation" in blocks[0].body
    assert "§ 46" not in blocks[0].body
    assert "D. Ausgleich" not in blocks[0].body
    assert "§ 48" not in blocks[0].body
    assert "Following body" not in blocks[0].body
