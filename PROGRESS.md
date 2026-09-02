# Canada countermeasures ingest progress

## State

In progress on branch `ca/2026-08-25-us-countermeasures-ingest`, based on
local `origin/main` at
`3ecdb83f9c3474bc293566d5ba9fdd046ef286b6`.

## Done

- Read the byte-pin provenance and both local Canada countermeasure context
  memos.
- Read the complete artifact layout and extraction pattern for the
  `2026-08-18-canada-338-suspension` reference ingest.
- Confirmed that `ca` is already supported by the generic corpus layout and
  that no jurisdiction registry change is required.
- Created this isolated linked worktree without modifying the dirty primary
  checkout or any existing worktree.
- Retained the Finance Canada release and product-list HTML captures as
  byte-identical official documents; their sizes and SHA-256 digests match the
  handoff pins.

## Next

- Extract verbatim announcement and per-item product-list provisions.
- Write matching inventory and complete coverage artifacts plus the ingest-run
  note.
- Commit content, sign the ingest manifest from a clean tracked checkout, and
  run offline verification.
