#!/usr/bin/env python3
"""Reproduce the California CalFresh BBCE authority ingest from exact sources."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import fitz

from axiom_corpus.corpus import documents
from axiom_corpus.corpus.artifacts import CorpusArtifactStore, safe_segment, sha256_bytes
from axiom_corpus.corpus.coverage import compare_provision_coverage
from axiom_corpus.corpus.documents import OfficialDocumentManifest
from axiom_corpus.corpus.models import DocumentClass, ProvisionRecord, SourceInventoryItem
from axiom_corpus.corpus.states import extract_california_code_sections

REPO_ROOT = Path(__file__).resolve().parents[2]
RETAINED_BASE = REPO_ROOT / "data/corpus"
MANIFEST_PATH = REPO_ROOT / "manifests/us-ca-cdss-calfresh-bbce-authority.yaml"

VERSION = "2026-07-28-ca-cdss-calfresh-bbce-authority"
GUIDANCE_VERSION = VERSION
STATUTE_VERSION = f"{VERSION}-us-ca-sections-wic-18901.5"
SOURCE_AS_OF = "2026-07-28"
REPRO_COMMAND = (
    "uv run --extra dev python "
    "scripts/repro/us_ca_calfresh_bbce_authority.py --base data/corpus"
)

GUIDANCE_INPUT_BY_SOURCE_ID = {
    "ca-cdss-acl-2014-14-56": "14-56.pdf",
    "ca-cdss-acl-2014-14-56e": "14-56e.pdf",
    "ca-cdss-acl-2015-15-42": "15-42.pdf",
    "ca-cdss-acl-2014-14-100": "14-100.pdf",
    "ca-cdss-acl-2013-13-32": "13-32.pdf",
}
ROOT_CITATION_BY_SOURCE_ID = {
    "ca-cdss-acl-2014-14-56": "us-ca/guidance/cdss/acl-2014-14-56",
    "ca-cdss-acl-2014-14-56e": "us-ca/guidance/cdss/acl-2014-14-56e",
    "ca-cdss-acl-2015-15-42": "us-ca/guidance/cdss/acl-2015-15-42",
    "ca-cdss-acl-2014-14-100": "us-ca/guidance/cdss/acl-2014-14-100",
    "ca-cdss-acl-2013-13-32": "us-ca/guidance/cdss/acl-2013-13-32",
}
EXPECTED_SHA256 = {
    "WIC-18901.5.html": (
        "97cae778729e0dd5d3c15797934690467876a14057e7d856d1500326e72d004e"
    ),
    "14-56.pdf": "8677c1d3e5c2ec9ecef23206b24061999817a46fa469ccb68a000b8f2f570d5e",
    "14-56e.pdf": "67e33a2613009abaef3759ebc2a583417fb852120f009848e3b1a1e3c3c11cbd",
    "15-42.pdf": "6aab92e4e2a2c9e0f234eba2b1c0eeb68d4d9d5dbc7ba752465a2358d9f2db33",
    "14-100.pdf": "c981081163b361eea20aeeccec7934509dc5bf23d8d66c8035895586db60131e",
    "13-32.pdf": "1a0bbfc2d6d69fd378aff3f1285d03d20b8b6abf2ff64c749b9897fd1cc55506",
}
EXPECTED_SIZE_BYTES = {
    "WIC-18901.5.html": 164_166,
    "14-56.pdf": 278_260,
    "14-56e.pdf": 189_729,
    "15-42.pdf": 249_307,
    "14-100.pdf": 209_290,
    "13-32.pdf": 204_909,
}
EXPECTED_PAGE_COUNTS = {
    "14-56.pdf": 7,
    "14-56e.pdf": 4,
    "15-42.pdf": 13,
    "14-100.pdf": 12,
    "13-32.pdf": 3,
}
EXPECTED_ROWS_BY_SOURCE_ID = {
    source_id: EXPECTED_PAGE_COUNTS[input_name] + 1
    for source_id, input_name in GUIDANCE_INPUT_BY_SOURCE_ID.items()
}
EXPECTED_ROWS_BY_INPUT = {
    "WIC-18901.5.html": 1,
    **{
        input_name: EXPECTED_ROWS_BY_SOURCE_ID[source_id]
        for source_id, input_name in GUIDANCE_INPUT_BY_SOURCE_ID.items()
    },
}

GUIDANCE_SOURCE_BASE = (
    Path("sources/us-ca/guidance") / GUIDANCE_VERSION / "official-documents"
)
STATUTE_SOURCE = (
    Path("sources/us-ca/statute")
    / STATUTE_VERSION
    / "california-leginfo-sections/WIC-18901.5.html"
)
CANONICAL_SOURCE_BY_INPUT = {
    "WIC-18901.5.html": STATUTE_SOURCE,
    **{
        input_name: GUIDANCE_SOURCE_BASE / f"{safe_segment(source_id)}.pdf"
        for source_id, input_name in GUIDANCE_INPUT_BY_SOURCE_ID.items()
    },
}
GUIDANCE_INVENTORY = (
    Path("inventory/us-ca/guidance") / f"{GUIDANCE_VERSION}.json"
)
GUIDANCE_PROVISIONS = (
    Path("provisions/us-ca/guidance") / f"{GUIDANCE_VERSION}.jsonl"
)
GUIDANCE_COVERAGE = Path("coverage/us-ca/guidance") / f"{GUIDANCE_VERSION}.json"
STATUTE_INVENTORY = Path("inventory/us-ca/statute") / f"{STATUTE_VERSION}.json"
STATUTE_PROVISIONS = Path("provisions/us-ca/statute") / f"{STATUTE_VERSION}.jsonl"
STATUTE_COVERAGE = Path("coverage/us-ca/statute") / f"{STATUTE_VERSION}.json"
GENERATED_RELATIVE_PATHS = (
    *CANONICAL_SOURCE_BY_INPUT.values(),
    GUIDANCE_INVENTORY,
    GUIDANCE_PROVISIONS,
    GUIDANCE_COVERAGE,
    STATUTE_INVENTORY,
    STATUTE_PROVISIONS,
    STATUTE_COVERAGE,
)

EXPECTED_EXCERPTS = {
    "us-ca/statute/wic/18901.5": (
        "The department shall establish a program of categorical eligibility "
        "for CalFresh",
    ),
    "us-ca/guidance/cdss/acl-2014-14-56/page-1": (
        "all households (with certain exceptions as cited in this letter) with "
        "gross income at or below 200 percent of the Federal Poverty Level "
        "(FPL), must be conferred MCE status",
    ),
    "us-ca/guidance/cdss/acl-2014-14-56e/page-2": (
        "gross income at or less than 200 percent of the FPL",
    ),
    "us-ca/guidance/cdss/acl-2014-14-56/page-3": (
        "receipt of the PUB 275 exempts all resources in the determination of "
        "eligibility",
        "Receipt of the PUB 275, in and of itself, does not confer MCE status.",
    ),
    "us-ca/guidance/cdss/acl-2015-15-42/page-2": (
        "must be conferred MCE status if they are issued or have online access "
        "to the TANF-funded “Family Planning – PUB 275” brochure",
    ),
    "us-ca/guidance/cdss/acl-2015-15-42/page-3": (
        "Any household member who is disqualified for an Intentional Program "
        "Violation (IPV).",
        "The head of household who does not comply with work requirements.",
    ),
    "us-ca/guidance/cdss/acl-2015-15-42/page-4": (
        "entitled to the minimum CalFresh benefit even though the household’s "
        "net income exceeds the maximum allowable for the household size",
        "entitled to the allotment amount indicated in the tables of benefit "
        "issuance by household size even if the household’s net income exceeds "
        "the maximum amount allowable",
    ),
    "us-ca/guidance/cdss/acl-2014-14-100/page-2": (
        "Effective April 1, 2015, no person will be denied aid because they "
        "have a prior felony drug conviction",
    ),
    "us-ca/guidance/cdss/acl-2014-14-56/page-6": (
        "California has opted to deny these household who are otherwise CE or "
        "MCE and entitled to no benefits.",
    ),
    "us-ca/guidance/cdss/acl-2013-13-32/page-1": (
        "E/D households are not subject to a gross income test for actual "
        "program eligibility",
    ),
}


def _resolve_input_path(source_dir: Path, input_name: str) -> Path:
    candidates = (
        source_dir / input_name,
        source_dir / CANONICAL_SOURCE_BY_INPUT[input_name],
    )
    for candidate in candidates:
        if candidate.is_symlink():
            raise ValueError(f"official source must not be a symlink: {candidate}")
        if candidate.is_file():
            return candidate
    choices = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"official source {input_name} not found; checked {choices}")


def _read_verified_sources(source_dir: Path) -> dict[str, bytes]:
    source_bytes: dict[str, bytes] = {}
    for input_name, expected_hash in EXPECTED_SHA256.items():
        source_path = _resolve_input_path(source_dir, input_name)
        content = source_path.read_bytes()
        actual_hash = sha256_bytes(content)
        if actual_hash != expected_hash:
            raise ValueError(
                f"official source hash mismatch for {input_name}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        expected_size = EXPECTED_SIZE_BYTES[input_name]
        if len(content) != expected_size:
            raise ValueError(
                f"official source size mismatch for {input_name}: "
                f"expected {expected_size}, got {len(content)}"
            )
        source_bytes[input_name] = content

    for input_name, expected_pages in EXPECTED_PAGE_COUNTS.items():
        with fitz.open(stream=source_bytes[input_name], filetype="pdf") as pdf:
            if pdf.page_count != expected_pages:
                raise ValueError(
                    f"official PDF page-count mismatch for {input_name}: "
                    f"expected {expected_pages}, got {pdf.page_count}"
                )
            empty_pages = [
                page.number + 1 for page in pdf if not page.get_text().strip()
            ]
        if empty_pages:
            raise ValueError(
                f"official PDF contains empty extracted pages for {input_name}: "
                f"{empty_pages}"
            )
    return source_bytes


def _guidance_manifest() -> OfficialDocumentManifest:
    manifest = OfficialDocumentManifest.load(MANIFEST_PATH)
    manifest.require_unique_sources()
    expected_ids = set(GUIDANCE_INPUT_BY_SOURCE_ID)
    actual_ids = {source.source_id for source in manifest.documents}
    if actual_ids != expected_ids:
        raise ValueError(
            f"guidance manifest source IDs changed: expected {expected_ids}, got {actual_ids}"
        )
    for source in manifest.documents:
        if source.document_class != DocumentClass.GUIDANCE.value:
            raise ValueError(f"unexpected document class for {source.source_id}")
        if source.source_format != "pdf":
            raise ValueError(f"unexpected source format for {source.source_id}")
        if source.local_path is not None:
            raise ValueError(f"manifest must not use local_path for {source.source_id}")
        if source.citation_path != ROOT_CITATION_BY_SOURCE_ID[source.source_id]:
            raise ValueError(f"unexpected citation path for {source.source_id}")
    return manifest


def _build_guidance_scope(
    staging_base: Path,
    source_bytes: dict[str, bytes],
) -> dict[str, Any]:
    store = CorpusArtifactStore(staging_base)
    inventory: list[SourceInventoryItem] = []
    records: list[ProvisionRecord] = []
    block_count = 0
    manifest = _guidance_manifest()

    for source in manifest.documents:
        input_name = GUIDANCE_INPUT_BY_SOURCE_ID[source.source_id]
        content = source_bytes[input_name]
        relative_source = (
            f"official-documents/{safe_segment(source.source_id)}.pdf"
        )
        artifact_path = store.source_path(
            source.jurisdiction,
            source.document_class,
            GUIDANCE_VERSION,
            relative_source,
        )
        source_sha = store.write_bytes(artifact_path, content)
        source_key = (
            f"sources/{source.jurisdiction}/{source.document_class}/"
            f"{GUIDANCE_VERSION}/{relative_source}"
        )
        blocks = documents._extract_blocks(
            content,
            "pdf",
            source_url=source.source_url,
            title=source.title,
            extraction=source.extraction,
        )
        expected_pages = EXPECTED_PAGE_COUNTS[input_name]
        if len(blocks) != expected_pages:
            raise ValueError(
                f"unexpected PDF block count for {input_name}: "
                f"expected {expected_pages}, got {len(blocks)}"
            )
        block_count += len(blocks)
        inventory.extend(
            documents._inventory_items(
                source,
                blocks=blocks,
                source_key=source_key,
                source_format="pdf",
                source_sha=source_sha,
                content_type="application/pdf",
                final_url=source.source_url,
            )
        )
        source_as_of = source.source_as_of or GUIDANCE_VERSION
        expression_date = source.expression_date or source_as_of
        records.extend(
            documents._provision_records(
                source,
                blocks=blocks,
                version=GUIDANCE_VERSION,
                source_key=source_key,
                source_format="pdf",
                source_as_of=source_as_of,
                expression_date=expression_date,
                content_type="application/pdf",
                final_url=source.source_url,
            )
        )

    store.write_inventory(staging_base / GUIDANCE_INVENTORY, inventory)
    store.write_provisions(staging_base / GUIDANCE_PROVISIONS, records)
    coverage = compare_provision_coverage(
        tuple(inventory),
        tuple(records),
        jurisdiction="us-ca",
        document_class=DocumentClass.GUIDANCE.value,
        version=GUIDANCE_VERSION,
    )
    if not coverage.complete:
        raise ValueError(f"incomplete guidance coverage: {coverage.to_mapping()}")
    store.write_json(staging_base / GUIDANCE_COVERAGE, coverage.to_mapping())
    return {
        "block_count": block_count,
        "document_count": len(manifest.documents),
        "row_count": len(records),
    }


def _build_statute_scope(
    staging_base: Path,
    source_bytes: dict[str, bytes],
) -> dict[str, Any]:
    with TemporaryDirectory(prefix="ca-bbce-leginfo-cache-") as cache_name:
        cache_root = Path(cache_name)
        cache_path = (
            cache_root / "california-leginfo-sections/WIC-18901.5.html"
        )
        cache_store = CorpusArtifactStore(cache_root)
        cache_store.write_bytes(cache_path, source_bytes["WIC-18901.5.html"])
        store = CorpusArtifactStore(staging_base)
        report = extract_california_code_sections(
            store,
            version=VERSION,
            sections=("WIC:18901.5",),
            source_as_of=SOURCE_AS_OF,
            expression_date=SOURCE_AS_OF,
            download_dir=cache_root,
            request_delay_seconds=0,
        )
    if report.errors:
        raise ValueError(f"California section extractor errors: {report.errors}")
    if not report.coverage.complete or report.provisions_written != 1:
        raise ValueError(
            f"unexpected California statute report: {report.coverage.to_mapping()}"
        )
    return {
        "row_count": report.provisions_written,
        "section_count": report.section_count,
    }


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _verify_coverage(
    path: Path,
    *,
    document_class: str,
    version: str,
    expected_count: int,
) -> None:
    coverage = json.loads(path.read_text(encoding="utf-8"))
    expected_fields = {
        "complete": True,
        "document_class": document_class,
        "jurisdiction": "us-ca",
        "matched_count": expected_count,
        "provision_count": expected_count,
        "source_count": expected_count,
        "version": version,
    }
    for key, expected in expected_fields.items():
        if coverage.get(key) != expected:
            raise ValueError(
                f"unexpected coverage field {key} in {path}: "
                f"expected {expected!r}, got {coverage.get(key)!r}"
            )
    for key in (
        "duplicate_provision_citations",
        "duplicate_source_citations",
        "extra_provisions",
        "missing_from_provisions",
    ):
        if coverage.get(key) != []:
            raise ValueError(f"non-empty coverage issue list {key} in {path}")


def _verify_generated_scope(
    staging_base: Path,
    source_bytes: dict[str, bytes],
) -> None:
    for input_name, relative_path in CANONICAL_SOURCE_BY_INPUT.items():
        generated = (staging_base / relative_path).read_bytes()
        if generated != source_bytes[input_name]:
            raise ValueError(f"generated source is not byte-equal for {input_name}")
        actual_hash = sha256_bytes(generated)
        if actual_hash != EXPECTED_SHA256[input_name]:
            raise ValueError(f"generated source hash mismatch for {input_name}")

    guidance_rows = _load_jsonl(staging_base / GUIDANCE_PROVISIONS)
    statute_rows = _load_jsonl(staging_base / STATUTE_PROVISIONS)
    guidance_by_path = {row["citation_path"]: row for row in guidance_rows}
    statute_by_path = {row["citation_path"]: row for row in statute_rows}
    if len(guidance_rows) != len(guidance_by_path) or len(guidance_rows) != 44:
        raise ValueError("guidance scope must contain 44 unique rows")
    if set(statute_by_path) != {"us-ca/statute/wic/18901.5"}:
        raise ValueError("statute scope must contain only WIC 18901.5")

    actual_rows_by_source = Counter(row["source_id"] for row in guidance_rows)
    if actual_rows_by_source != Counter(EXPECTED_ROWS_BY_SOURCE_ID):
        raise ValueError(
            "unexpected per-source guidance rows: "
            f"expected {EXPECTED_ROWS_BY_SOURCE_ID}, got {dict(actual_rows_by_source)}"
        )

    expected_guidance_paths: set[str] = set()
    for source_id, root_citation in ROOT_CITATION_BY_SOURCE_ID.items():
        expected_guidance_paths.add(root_citation)
        input_name = GUIDANCE_INPUT_BY_SOURCE_ID[source_id]
        expected_guidance_paths.update(
            f"{root_citation}/page-{page_number}"
            for page_number in range(1, EXPECTED_PAGE_COUNTS[input_name] + 1)
        )
    if set(guidance_by_path) != expected_guidance_paths:
        raise ValueError("guidance citation paths changed")

    manifest_by_id = {
        source.source_id: source for source in _guidance_manifest().documents
    }
    for row in guidance_rows:
        source = manifest_by_id[row["source_id"]]
        if row["source_url"] != source.source_url:
            raise ValueError(f"official source URL changed for {row['citation_path']}")
        download_url = row.get("metadata", {}).get("download_url")
        if download_url != source.source_url or str(download_url).startswith("file:"):
            raise ValueError(
                f"non-official download URL for {row['citation_path']}: {download_url}"
            )

    guidance_inventory = json.loads(
        (staging_base / GUIDANCE_INVENTORY).read_text(encoding="utf-8")
    )["items"]
    statute_inventory = json.loads(
        (staging_base / STATUTE_INVENTORY).read_text(encoding="utf-8")
    )["items"]
    if {item["citation_path"] for item in guidance_inventory} != set(
        guidance_by_path
    ):
        raise ValueError("guidance inventory/provision paths differ")
    if {item["citation_path"] for item in statute_inventory} != set(
        statute_by_path
    ):
        raise ValueError("statute inventory/provision paths differ")

    all_rows_by_path = guidance_by_path | statute_by_path
    for citation_path, excerpts in EXPECTED_EXCERPTS.items():
        body = str(all_rows_by_path[citation_path].get("body") or "")
        for excerpt in excerpts:
            if excerpt not in body:
                raise ValueError(
                    f"required authority excerpt missing from {citation_path}: {excerpt}"
                )

    _verify_coverage(
        staging_base / GUIDANCE_COVERAGE,
        document_class=DocumentClass.GUIDANCE.value,
        version=GUIDANCE_VERSION,
        expected_count=44,
    )
    _verify_coverage(
        staging_base / STATUTE_COVERAGE,
        document_class=DocumentClass.STATUTE.value,
        version=STATUTE_VERSION,
        expected_count=1,
    )


def reproduce(base: Path, source_dir: Path | None = None) -> dict[str, Any]:
    target_base = base.resolve()
    input_root = (source_dir or RETAINED_BASE).resolve()
    source_bytes = _read_verified_sources(input_root)

    with TemporaryDirectory(prefix="repro-us-ca-calfresh-bbce-") as staging_name:
        staging_base = Path(staging_name) / "corpus"
        guidance = _build_guidance_scope(staging_base, source_bytes)
        statute = _build_statute_scope(staging_base, source_bytes)
        _verify_generated_scope(staging_base, source_bytes)

        target_store = CorpusArtifactStore(target_base)
        generated_hashes: dict[str, str] = {}
        for relative_path in GENERATED_RELATIVE_PATHS:
            content = (staging_base / relative_path).read_bytes()
            target_store.write_bytes(target_base / relative_path, content)
            generated_hashes[relative_path.as_posix()] = sha256_bytes(content)

    return {
        "base": str(target_base),
        "command": REPRO_COMMAND,
        "files": generated_hashes,
        "guidance": guidance,
        "per_source_rows": EXPECTED_ROWS_BY_INPUT,
        "source_sha256": EXPECTED_SHA256,
        "statute": statute,
        "versions": {
            "guidance": GUIDANCE_VERSION,
            "statute": STATUTE_VERSION,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        type=Path,
        required=True,
        help="Destination corpus base.",
    )
    parser.add_argument(
        "--source-dir",
        type=Path,
        help=(
            "Optional local input root. Accepts the six flat original filenames "
            "or the retained canonical paths; defaults to repository data/corpus."
        ),
    )
    args = parser.parse_args()
    print(json.dumps(reproduce(args.base, args.source_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
