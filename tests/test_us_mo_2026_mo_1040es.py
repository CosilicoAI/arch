from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION = "2026-07-26-mo-2026-mo-1040es"
ROOT_CITATION = "us-mo/form/individual-income-tax/2026/mo-1040es"
RATE_CHART_CITATION = f"{ROOT_CITATION}/tax-rate-chart"
SOURCE_SHA256 = "660f9c44610bb911f5652c42710cf86d49f693eb151dff35640932e7cae58793"


def _provisions() -> list[dict[str, object]]:
    path = REPO_ROOT / f"data/corpus/provisions/us-mo/form/{VERSION}.jsonl"
    return [json.loads(line) for line in path.read_text().splitlines()]


def test_mo_2026_mo_1040es_source_and_coverage_are_complete() -> None:
    source = (
        REPO_ROOT
        / f"data/corpus/sources/us-mo/form/{VERSION}/official-documents/"
        "us-mo-dor-2026-mo-1040es.pdf"
    )
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA256

    coverage_path = REPO_ROOT / f"data/corpus/coverage/us-mo/form/{VERSION}.json"
    coverage = json.loads(coverage_path.read_text())
    assert coverage == {
        "complete": True,
        "document_class": "form",
        "duplicate_provision_citations": [],
        "duplicate_source_citations": [],
        "extra_provisions": [],
        "jurisdiction": "us-mo",
        "matched_count": 2,
        "missing_from_provisions": [],
        "provision_count": 2,
        "source_count": 2,
        "version": VERSION,
    }
    assert [row["citation_path"] for row in _provisions()] == [
        ROOT_CITATION,
        RATE_CHART_CITATION,
    ]


def test_mo_2026_mo_1040es_preserves_the_full_rate_chart() -> None:
    chart = _provisions()[1]
    assert chart["body"] == (
        "Use the amount from Line 9 (Missouri taxable income) to calculate your "
        "Missouri tax. If you are filing combined, you must calculate separate tax "
        "amounts and enter the amounts on 10Y for yourself and 10S for your spouse. "
        "The total amount should be entered on Line 10T. Single filers should enter "
        "the tax amount on Line 10T. If the Missouri taxable income is: The tax is: "
        "$0 to $1,348 $0 "
        "Over $1,348 but not over $2,696 2.0% of excess over $1,348 "
        "Over $2,696 but not over $4,044 $27 plus 2.5% of excess over $2,696 "
        "Over $4,044 but not over $5,392 $61 plus 3.0% of excess over $4,044 "
        "Over $5,392 but not over $6,740 $101 plus 3.5% of excess over $5,392 "
        "Over $6,740 but not over $8,088 $148 plus 4.0% of excess over $6,740 "
        "Over $8,088 but not over $9,436 $202 plus 4.5% of excess over $8,088 "
        "Over $9,436 ............................... "
        "$263 plus 4.7% of excess over $9,436"
    )


def test_mo_2026_mo_1040es_is_bounded_to_estimated_tax() -> None:
    chart = _provisions()[1]
    metadata = chart["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["tax_year"] == "2026"
    assert metadata["form_number"] == "MO-1040ES"
    assert metadata["application_scope"] == "estimated_tax_rate_schedule_only"
    assert metadata["source_status"] == "current_official_tax_year_estimated_form"
    assert metadata["higher_authority_citation_paths"] == [
        "us-mo/statute/143.011",
        "us-mo/statute/143.021",
    ]

    source_note = metadata["source_note"]
    assert isinstance(source_note, str)
    assert "does not establish final Form MO-1040 liability" in source_note
    assert "annual-return taxable-income construction" in source_note
    assert "final-return ordering" in source_note
