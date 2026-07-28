# Progress

## State

- Defensive correctness and completeness audit is blocked at byte-faithful
  source acquisition; the branch is intentionally not production-ready.
- Active worktree: `/Users/maxghenis/TheAxiomFoundation/axiom-corpus/.worktrees/ca-bbce-authority`
- Branch: `ingest/ca-bbce-authority`
- Base: locally available `origin/main` at `10142cb0f07403c2de4599c76bec01e96640fda9`
- Reports will remain intentionally untracked.
- Sandbox limitation: `git fetch origin main` failed because `github.com` could not be resolved; no remote ref changed.
- Source-acquisition blocker: terminal networking cannot resolve either official
  host, and no byte-identical source copies exist in the accessible filesystem.
  Browser verification can read the official endpoints but cannot transfer the
  response bytes into the worktree.

## Done

- Created an isolated worktree and branch from the locally available `origin/main`.
- Read the stopped rulespec-us #1098 worker report before implementation.
- Identified the required authority functions: California's modified-categorical trigger, 200% gross screen, waived resource/net tests, current exclusions, and zero-benefit treatment.
- Refreshed the worktree-local GitNexus index. Indexing completed, but registry
  registration failed with `EPERM` outside the writable workspace; local graph
  queries remain available through the fresh index.
- Verified the current official WIC §18901.5 text and the official CDSS PDF
  endpoints, page counts, issue dates, source roles, and absence of a stated
  supersession on the CDSS annual indexes.
- Fixed the minimum defensible source hierarchy:
  - WIC §18901.5 for California's categorical-eligibility mandate;
  - ACL 14-56 for the PUB 275 trigger, inclusive 200% FPL screen, resource
    exclusion, and zero-benefit handling;
  - ACL 14-56E because CDSS says it must be read with ACL 14-56;
  - ACL 15-42 for later operational treatment of the 200% boundary;
  - ACL 14-100 for the later drug-felony exclusion change; and
  - ACL 13-32 for the preserved elderly/disabled route.
- Determined that PUB 275 is the triggering service brochure, not an independent
  CalFresh authority, and that ACL 14-63 is redundant for the #1098 facts already
  carried by ACL 14-56.
- Added the official-document source manifest for the five required CDSS PDFs.
- Ran upstream impact analysis for the existing `PROGRESS.md` symbol: LOW risk,
  zero direct dependents, zero affected processes, and zero affected modules.
- Fixed the literal portable reproduction command:
  `uv run --extra dev python scripts/repro/us_ca_calfresh_bbce_authority.py --base data/corpus`.
- Designed an offline reproduction path that feeds pre-verified retained bytes
  through the existing California section and official-document extractors while
  preserving official endpoint metadata rather than recording `file://` URLs.
- Fixed the expected generated scope at 44 guidance rows (five document roots
  plus 39 PDF pages) and one statute row, with complete inventory/provision/
  coverage parity and hard excerpt assertions for every #1098 authority fact.
- Ran the pre-change citation-path census: 143,730 rows and 125,202 unique paths
  pass; the `page_n` live count and baseline are both 31,358. The intended 39
  new page paths will move that ratchet to 31,397.
- Confirmed that neither ingest signing key is available. The supported CLI
  cannot emit an unsigned manifest; any programmatically generated unsigned
  payload will not authorize protected paths until the main lane signs it.
- Confirmed a second sandbox limitation: plain `uv run` cannot write its default
  cache, and a writable-cache retry cannot resolve build wheels because outbound
  DNS is blocked. Direct checks through the existing repository virtual
  environment remain available, but this does not substitute for the required
  final literal-command validation.
- Ran partial static validation at `ca9e26be`: the direct Ruff fallback passes
  and `git diff --check origin/main..HEAD` is clean. The direct mypy fallback
  reports 180 pre-existing errors across 26 untouched Python files. Exact `uv`
  wrappers stop at the cache permission error before running any check.
- Added a narrowly scoped changelog fragment for the verified source manifest.
- Re-ran the direct Towncrier fallback after committing the fragment; it passes.
- Exhaustively scanned all 25,094 reachable and unreachable Git blobs
  (2.86 GiB), every reflog/dangling commit tree, ignored paths, and the stash.
  None contains the WIC HTML or any target ACL PDF bytes.
- Ran the full direct pytest fallback: 4,117 passed, 69 skipped, 208 deselected,
  and two failed in 250.98 seconds. One is the known PostgreSQL mock/Pydantic
  failure. The other is a USC inventory-status test that reproduces alone and
  has no source or test diff from `origin/main`, so it is an upstream/base
  failure unrelated to this Markdown/YAML-only branch.

## Next

- Resume in a network-enabled lane or supply the exact official response bytes
  as `WIC-18901.5.html`, `14-56.pdf`, `14-56e.pdf`, `15-42.pdf`,
  `14-100.pdf`, and `13-32.pdf`.
- Fill the pinned source hashes, implement and execute the deterministic
  reproduction script, and commit every generated artifact.
- Add focused byte/parity/excerpt/offline tests, a release selector, run
  documentation, and update the changelog fragment for the completed ingest.
- Validate citation paths, release scope, tracked scope, static checks, and the full test suite.
- Sign the manifest last if local signing material is available; otherwise leave it unsigned for the main lane.
- Write the final untracked `WORKER-REPORT.md` and verify `git diff --name-only origin/main..HEAD`.
