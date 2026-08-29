# Armenia ARLIS ingest progress

## State

- Branch: `ingest/am-taxben-core` from `origin/main` at `620527d7`.
- Target scope/version: `am/statute` / `2026-08-29-am-taxben-core`.
- Current phase: required repository and precedent reconnaissance.
- Constraints: offline only; no signing, publishing, pushing, PR creation, or edits to protected toolchain/workflow ownership files.

## Done

- Read `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md` in the required order.
- Loaded the GitNexus exploration, impact-analysis, and CLI instructions.
- Confirmed the requested branch and base commit and that the tracked worktree began clean.
- Built an offline GitNexus index for this exact worktree and commit and exposed it through an isolated writable registry for query/context/impact/change checks.

## Next

1. Read the DK ingest history/layout, ELI documentation, existing HTML adapters, and CI manifest validator end-to-end.
2. Characterize all six harvested ARLIS documents and provenance without modifying the read-only inputs.
3. Run GitNexus impact checks, implement the fail-closed adapter/CLI/manifest path, and add fixtures/tests.
4. Generate all four `am/statute` artifact classes with explicit `source_as_of: 2026-08-29` and validate exact article coverage.
5. Add the changelog, `PR-BODY.md`, final report, and run the full required check suite.

## Validation log

- Pending implementation and artifact validation.

## Decisions and risks

- ARLIS amendment annotations and Armenian punctuation must remain verbatim in stored provision text.
- Parsing must reject unrecognized or trailing legislative content instead of silently dropping it.
- The configured GitNexus MCP was unavailable, so the installed local MCP is running against an isolated registry; its first change scan reports low risk and no affected execution flows for this ledger-only edit.
