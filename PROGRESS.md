# Progress

## State

- Defensive correctness and completeness audit in progress.
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

## Next

- Obtain byte-faithful official responses for WIC §18901.5 and the five retained
  CDSS PDFs without reconstructing or normalizing source bytes.
- Implement the deterministic reproduction script, corpus artifacts, focused
  tests, release selector, run documentation, and changelog.
- Validate citation paths, release scope, tracked scope, static checks, and the full test suite.
- Sign the manifest last if local signing material is available; otherwise leave it unsigned for the main lane.
- Write the final untracked `WORKER-REPORT.md` and verify `git diff --name-only origin/main..HEAD`.
