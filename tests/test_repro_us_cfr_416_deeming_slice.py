"""Keep the approved section-only slice reproducible as appendix support grows."""

from pathlib import Path

from axiom_corpus.corpus.artifacts import sha256_bytes
from scripts.repro_us_cfr_416_deeming_slice import (
    GENERATED_RELATIVE_PATHS,
    PROVISIONS_RELATIVE_PATH,
    reproduce,
)


def test_deeming_reproduction_preserves_pinned_section_scope(tmp_path):
    source_base = Path(__file__).parents[1] / "data" / "corpus"

    report = reproduce(tmp_path, source_base)

    assert report["full_source_count"] == 622
    assert report["selected_count"] == 14
    assert report["coverage_complete"]
    for relative_path in GENERATED_RELATIVE_PATHS:
        actual = (tmp_path / relative_path).read_bytes()
        if relative_path == PROVISIONS_RELATIVE_PATH:
            # Main f22e9a45's reproduction includes newer body normalization
            # than the published July snapshot; preserve that baseline exactly.
            assert sha256_bytes(actual) == (
                "94b7ada5c604b276813b0854b67a15d869baae6e846159730801b412b7f4daa6"
            )
        else:
            assert actual == (source_base / relative_path).read_bytes()
