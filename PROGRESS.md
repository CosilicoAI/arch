# Canada countermeasures ingest progress

## State

Content and offline validation are complete on branch
`ca/2026-08-25-us-countermeasures-ingest`, based on local `origin/main` at
`3ecdb83f9c3474bc293566d5ba9fdd046ef286b6`. A follow-up session with the
unlocked key store signed the ingest manifest, verified the protected-ingest
guard against `origin/main`, pushed the branch, and opened pull request
[#637](https://github.com/TheAxiomFoundation/axiom-corpus/pull/637).
Review then found four provision bodies that were not verbatim
source-visible text (a fabricated space before punctuation following inline
links, introduced by `get_text(" ")` separator insertion). The lane-local
extractor was corrected to walk the DOM without inventing separators inside
inline runs, exactly the four affected provisions were regenerated (all
other artifacts byte-identical, second run reproducible), and the manifest
was re-signed from the corrected clean descendant commit.

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
- Passed the coverage, tracked-scope, citation-path, schema, parent-path,
  Ruff, and mypy validations.
- Ran the full test suite: 4,313 tests passed, 74 skipped, and one unchanged
  PostgreSQL unit test failed identically at the base commit in this Python
  environment.
- Confirmed the GitNexus change assessment is low risk, with no affected
  indexed symbols or execution flows.
- Attempted the required key retrieval without exposing secret material;
  `agent-secret get agent/axiom-corpus-ingest-private-key` stopped with
  `agent-secret: missing unlock password. Run: agent-secret init`.

## Next

1. Merge pull request #637 through a true merge commit — never rebase or
   squash — after review agreement and green CI.
2. Add the formal United States Surtax Order as a separate source when it is
   registered and gazetted.
