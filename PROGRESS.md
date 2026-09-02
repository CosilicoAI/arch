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
- Extracted two document roots and 662 body-bearing units: 25 release blocks,
  seven backgrounder paragraphs, one table-context parent, and 629 tariff-item
  children.
- Generated a 664-item inventory and provisions file with complete 664/664
  coverage; all 629 HTML rows equal the pinned TSV oracle field-for-field.
- Repeated the extraction with byte-identical source, inventory, provisions,
  and coverage hashes, and documented the run and pending legal instrument.

## Next

- Run the offline scope, citation, and repository validations and commit the
  complete content scope.
- Sign the ingest manifest from the clean content commit, commit it separately,
  and run the protected-ingest verifier.
