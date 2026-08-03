from pathlib import Path

MIGRATION = Path(
    "supabase/migrations/20260722021000_chunked_release_activation_upload.sql"
)


def test_chunked_activation_transport_is_private_and_hash_verified() -> None:
    sql = MIGRATION.read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS corpus.release_activation_upload_chunks" in sql
    assert "ENABLE ROW LEVEL SECURITY" in sql
    assert (
        "REVOKE ALL ON corpus.release_activation_upload_chunks\n"
        "  FROM anon, authenticated, service_role, PUBLIC"
    ) in sql
    assert "CREATE OR REPLACE FUNCTION corpus.load_release_activation_upload" in sql
    assert "sha256(convert_to(v_raw, 'UTF8'))" in sql
    assert "release activation upload is incomplete" in sql
    assert "release activation upload object digest mismatch" in sql
    assert "release activation upload identity mismatch" in sql
    assert (
        "REVOKE EXECUTE ON FUNCTION "
        "corpus.load_release_activation_upload(text, text, text, text)\n"
        "  FROM anon, authenticated, service_role, PUBLIC"
    ) in sql


def test_protected_activation_installs_transport_after_preview() -> None:
    workflow = Path(".github/workflows/activate-release.yml").read_text(encoding="utf-8")

    revalidate = workflow.index("- name: Revalidate takeover preview")
    migrate = workflow.index("- name: Ensure bounded release upload transport")
    activate = workflow.index("- name: Activate signed release")
    assert revalidate < migrate < activate
    assert "python scripts/apply_release_activation_upload_migration.py" in workflow
    assert workflow.count("SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}") == 4


def test_publication_registers_signed_object_before_retaining_activation_artifact() -> None:
    workflow = Path(".github/workflows/publish.yml").read_text(encoding="utf-8")

    migrate = workflow.index("python scripts/apply_release_object_staging_migration.py")
    publish = workflow.index("python scripts/publish_corpus.py")
    stage = workflow.index("python scripts/stage_release_object.py")
    retain = workflow.index("- name: Retain the signed release object for activation")
    assert migrate < publish < stage < retain
    assert "--expected-project-ref swocpijqqahhuwtuahwc" in workflow


def test_activation_gate_pipelines_fail_when_the_gate_command_fails() -> None:
    workflow = Path(".github/workflows/activate-release.yml").read_text(encoding="utf-8")

    assert workflow.count("set -o pipefail") == 1
    assert workflow.count("| tee \"$RUNNER_TEMP/release-gate.txt\"") == 1
