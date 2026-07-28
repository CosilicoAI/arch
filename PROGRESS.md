# Progress

## State

- Complete; ready for main-lane review and signing.
- Active worktree: `/Users/maxghenis/TheAxiomFoundation/axiom-corpus/.claude/worktrees/usc-amt-ftc`
- Branch: `ingest/usc-amt-ftc-sections`
- Base: local `origin/main` at `db12795577c5809009168982cf8a72fb58440620`
- Head: `c2f51414d0f94a0d7f9d895b01a4bb3c550bbc93`
- Reports intentionally untracked per the task's explicit report-handling instruction.
- Sandbox limitation: `git fetch origin main` failed because `github.com` could not be resolved.
- Sandbox limitation: GitNexus indexed this worktree successfully but could not register it at `~/.gitnexus/registry.json`; mandatory impact queries ran against the prior repository index, while `detect_changes` cannot target this unregistered checkout.

## Done

- Created an isolated worktree and branch from the locally available `origin/main`.
- Mapped the merged PR #523 official-USLM ingestion and reproduction pattern.
- Verified the retained OLRC ZIP and byte-equal `usc26.xml` cover every requested section.
- Probed full subsection granularity: 552 rows including title and repeal-only §902.
- Confirmed §§901 and 904 retain references to §902 and that official §902 is marked `status="repealed"` with no operative descendants.
- Added official USLM section-status preservation with focused tests (15 passed).
- Confirmed no requested section hits duplicate-numbered sibling or mixed-child traversal classes; all official identifiers survive in document order.
- Committed exact source bytes, deterministic reproduction script, and 552/552 inventory/provision/coverage artifacts.
- Ran the literal repro command and byte-compared all five scoped artifacts against a fresh temporary reproduction.
- Added the strict release selector, ingest documentation, changelog, and artifact integrity tests.
- Regenerated the citation census; only `uppercase_segments` changed, from 6,327 to 6,710.
- Focused USC/artifact/citation tests pass (50/50); strict targeted release validation has zero issues.
- All 78 release selectors pass; coverage is complete at 552/552.
- Ruff, mypy, towncrier, and tracked-scope checks pass.
- Full pytest completed with 4,116 passing and only the known unrelated PostgreSQL failure.
- Attempted signing; private/public keys are unavailable, so an unsigned ancestor-attesting manifest was committed last for main-lane signing.
- Reviewed `git diff --name-only origin/main..HEAD`; all 14 tracked files are in expected PR B scope.
- Wrote the final untracked `WORKER-REPORT.md` with counts, hashes, gates, structural findings, and sandbox limitations.

## Next

- Main lane signs the ingest manifest.
- During integration with corpus PR A, regenerate the shared citation census rather than choosing either branch's `schema/citation-path.v1.json` verbatim.
