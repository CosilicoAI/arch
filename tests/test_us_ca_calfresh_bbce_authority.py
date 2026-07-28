from __future__ import annotations

import json
import shutil
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import NoReturn

import requests

from axiom_corpus.corpus.release_quality import validate_release
from axiom_corpus.corpus.releases import ReleaseManifest
from scripts.repro.us_ca_calfresh_bbce_authority import (
    CANONICAL_SOURCE_BY_INPUT,
    EXPECTED_EXCERPTS,
    EXPECTED_PAGE_COUNTS,
    EXPECTED_ROWS_BY_INPUT,
    EXPECTED_ROWS_BY_SOURCE_ID,
    EXPECTED_SHA256,
    GENERATED_RELATIVE_PATHS,
    GUIDANCE_COVERAGE,
    GUIDANCE_INPUT_BY_SOURCE_ID,
    GUIDANCE_INVENTORY,
    GUIDANCE_PROVISIONS,
    GUIDANCE_VERSION,
    REPRO_COMMAND,
    ROOT_CITATION_BY_SOURCE_ID,
    STATUTE_COVERAGE,
    STATUTE_INVENTORY,
    STATUTE_PROVISIONS,
    STATUTE_VERSION,
    reproduce,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
CORPUS_ROOT = REPO_ROOT / "data/corpus"
RELEASE_PATH = (
    REPO_ROOT
    / "manifests/releases/us-ca-2026-07-28-calfresh-bbce-authority.json"
)
RUN_DOC_PATH = (
    REPO_ROOT
    / "docs/ingest-runs/2026-07-28-ca-calfresh-bbce-authority.md"
)
LITERAL_REPRO_COMMAND = (
    "uv run --extra dev python "
    "scripts/repro/us_ca_calfresh_bbce_authority.py --base data/corpus"
)


def _jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line
    ]


def _coverage(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_retained_sources_are_exact_and_scopes_are_complete() -> None:
    for input_name, relative_path in CANONICAL_SOURCE_BY_INPUT.items():
        content = (CORPUS_ROOT / relative_path).read_bytes()
        assert sha256(content).hexdigest() == EXPECTED_SHA256[input_name]

    guidance_rows = _jsonl(CORPUS_ROOT / GUIDANCE_PROVISIONS)
    statute_rows = _jsonl(CORPUS_ROOT / STATUTE_PROVISIONS)
    guidance_inventory = json.loads(
        (CORPUS_ROOT / GUIDANCE_INVENTORY).read_text(encoding="utf-8")
    )["items"]
    statute_inventory = json.loads(
        (CORPUS_ROOT / STATUTE_INVENTORY).read_text(encoding="utf-8")
    )["items"]

    assert len(guidance_rows) == len(guidance_inventory) == 44
    assert len(statute_rows) == len(statute_inventory) == 1
    assert Counter(row["source_id"] for row in guidance_rows) == Counter(
        EXPECTED_ROWS_BY_SOURCE_ID
    )
    assert {
        row["citation_path"] for row in statute_rows
    } == {"us-ca/statute/wic/18901.5"}
    assert statute_rows[0].get("parent_citation_path") is None
    assert statute_rows[0].get("parent_id") is None
    assert statute_rows[0]["metadata"]["parent_citation_path"] == (
        "us-ca/statute/wic"
    )

    expected_guidance_paths: set[str] = set()
    for source_id, root_path in ROOT_CITATION_BY_SOURCE_ID.items():
        expected_guidance_paths.add(root_path)
        input_name = GUIDANCE_INPUT_BY_SOURCE_ID[source_id]
        expected_guidance_paths.update(
            f"{root_path}/page-{page}"
            for page in range(1, EXPECTED_PAGE_COUNTS[input_name] + 1)
        )
    assert {row["citation_path"] for row in guidance_rows} == expected_guidance_paths
    assert {item["citation_path"] for item in guidance_inventory} == (
        expected_guidance_paths
    )

    for path, document_class, version, count in (
        (GUIDANCE_COVERAGE, "guidance", GUIDANCE_VERSION, 44),
        (STATUTE_COVERAGE, "statute", STATUTE_VERSION, 1),
    ):
        coverage = _coverage(CORPUS_ROOT / path)
        assert coverage["complete"] is True
        assert coverage["document_class"] == document_class
        assert coverage["jurisdiction"] == "us-ca"
        assert coverage["version"] == version
        assert coverage["source_count"] == count
        assert coverage["provision_count"] == count
        assert coverage["matched_count"] == count
        assert coverage["missing_from_provisions"] == []
        assert coverage["extra_provisions"] == []
        assert coverage["duplicate_source_citations"] == []
        assert coverage["duplicate_provision_citations"] == []

    serialized_scope = json.dumps(
        guidance_rows + statute_rows + guidance_inventory + statute_inventory
    )
    assert "file://" not in serialized_scope


def test_rulespec_1098_parameters_have_retained_controlling_text() -> None:
    rows = _jsonl(CORPUS_ROOT / GUIDANCE_PROVISIONS) + _jsonl(
        CORPUS_ROOT / STATUTE_PROVISIONS
    )
    rows_by_path = {row["citation_path"]: row for row in rows}

    for citation_path, excerpts in EXPECTED_EXCERPTS.items():
        body = rows_by_path[citation_path]["body"]
        assert body is not None
        for excerpt in excerpts:
            assert excerpt in body


def test_offline_reproduction_is_byte_deterministic(
    tmp_path: Path,
    monkeypatch,
) -> None:
    source_dir = tmp_path / "flat-sources"
    source_dir.mkdir()
    for input_name, relative_path in CANONICAL_SOURCE_BY_INPUT.items():
        shutil.copyfile(CORPUS_ROOT / relative_path, source_dir / input_name)

    def fail_network(*_args, **_kwargs) -> NoReturn:
        raise AssertionError("offline reproducer attempted network access")

    monkeypatch.setattr(requests.sessions.Session, "request", fail_network)
    replay_base = tmp_path / "replayed-corpus"
    report = reproduce(replay_base, source_dir)

    assert report["command"] == REPRO_COMMAND == LITERAL_REPRO_COMMAND
    assert report["per_source_rows"] == EXPECTED_ROWS_BY_INPUT
    for relative_path in GENERATED_RELATIVE_PATHS:
        assert (replay_base / relative_path).read_bytes() == (
            CORPUS_ROOT / relative_path
        ).read_bytes()


def test_repro_command_is_literal_and_release_passes_strictly() -> None:
    run_doc = RUN_DOC_PATH.read_text(encoding="utf-8")
    assert f"```bash\n{LITERAL_REPRO_COMMAND}\n```" in run_doc

    release = ReleaseManifest.load(RELEASE_PATH)
    assert release.name == "us-ca-2026-07-28-calfresh-bbce-authority"
    assert release.scope_keys == (
        ("us-ca", "guidance", GUIDANCE_VERSION),
        ("us-ca", "statute", STATUTE_VERSION),
    )
    report = validate_release(
        CORPUS_ROOT,
        release,
        strict_warnings=True,
        max_issues=200,
    )
    assert report.to_mapping() == {
        "release": "us-ca-2026-07-28-calfresh-bbce-authority",
        "scope_count": 2,
        "ok": True,
        "error_count": 0,
        "warning_count": 0,
        "strict_warnings": True,
        "issue_count": 0,
        "issues_returned": 0,
        "issues_truncated": False,
        "issues": [],
    }
