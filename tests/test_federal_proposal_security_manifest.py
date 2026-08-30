from pathlib import Path

from axiom_corpus.corpus.documents import OfficialDocumentManifest

MANIFEST = (
    Path(__file__).parents[1]
    / "manifests/us-federal-proposal-security-2026.yaml"
)


def test_federal_proposal_security_manifest_has_stable_scoped_sources():
    manifest = OfficialDocumentManifest.load(MANIFEST)
    manifest.require_unique_sources()

    assert len(manifest.documents) == 6
    by_id = {document.source_id: document for document in manifest.documents}

    chapter_i = by_id["nsf-pappg-24-1-chapter-i-submission-security"]
    assert chapter_i.extraction is not None
    assert [
        row["section_label"] for row in chapter_i.extraction["anchor_ranges"]
    ] == ["submission-instructions", "uei-and-sam"]

    supplement_2 = by_id["nsf-pappg-24-1-supplement-2-dmsp"]
    assert supplement_2.extraction is not None
    assert "s" in supplement_2.extraction["html_drop_selectors"]
    assert supplement_2.extraction["section_label"] == "dmsp"

    notice = by_id["nsf-important-notice-149-proposal-security"]
    assert notice.extraction is not None
    assert notice.extraction["stop_text_pattern"] == r"^5\."

    faq = by_id["nsf-important-notice-149-implementation-faq"]
    assert faq.extraction is not None
    assert len(faq.extraction["anchor_ranges"]) == 9

    tip = by_id["nsf-tip-person-entity-of-concern-prohibition"]
    assert tip.metadata is not None
    assert tip.metadata["dynamic_external_lists"] is True
    assert tip.metadata["prohibited_entity_names_must_not_be_encoded"] is True
