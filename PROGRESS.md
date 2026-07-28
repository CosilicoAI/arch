# Progress

## State

- Repair round 2 is active as a defensive correctness-and-completeness audit
  of PR #552 on branch `ingest/ca-bbce-authority`.
- Starting head: `058cf9ff662161de6ea008e7d0098cb38e9571d8`.
- The round-1 reviewer returned `REQUEST-CHANGES`: PyMuPDF 1.28.0 does not
  byte-reproduce the committed PDF rows, the current MCE-exclusion map is
  incomplete, ACL 14-63 is missing as the focused zero-benefit authority, and
  tracked final-state documentation misstates signing.
- At the start of this repair, both ingest manifests are signed and their
  applied-file hashes match the existing 45-row corpus state. Content changes
  in this round will make those attestations stale. Per instruction, their
  existing signatures will be left as-is for the main lane to replace after
  the repaired content lands.
- The supplied source cache and session reports remain intentionally
  untracked. No push, GitHub write, R2/Supabase publication, release
  activation, production-row deletion, or signing is authorized.

## Done

- Round 1 retained six byte-verified official sources and emitted 45 rows:
  44 guidance rows from five CDSS PDFs plus one WIC §18901.5 statute row.
- Round 1 added an offline reproducer, focused tests, strict two-scope release
  selection, coverage, manifests, a run document, and signed the two manifests
  in the final two commits.
- Read the pinned round-1 review at commit `4cbf22f3` before beginning repair
  work and accepted all four findings as the repair scope.
- Verified the two newly supplied official-source bytes:
  - ACL 14-63 PDF: SHA-256
    `4392ab0dedfcfb6f247bb7d3d913e90ff2a97a673ea01efac02ec9f3d6ee2841`.
  - WIC §18901.3 HTML: SHA-256
    `793afbd116aa7664fde4137f55d34ad659e80c10f37849d59bb4ea07b43fffdc`.
- Confirmed the worktree begins with only the supplied source cache and prior
  worker report untracked.
- Read the GitNexus debugging and impact-analysis instructions. GitNexus MCP
  tools are not exposed in this session; the local index/CLI and explicit
  caller/diff inspection will be used where possible, with any remaining
  limitation disclosed.

## Next

- Trace the reproduction/extractor flow, run upstream impact analysis before
  editing symbols, and implement the repository-conventional fix for
  PyMuPDF-version determinism.
- Prove byte-identical regeneration under both PyMuPDF 1.26.7 and 1.28.0.
- Ingest ACL 14-63 and WIC §18901.3, preserve all prior 45 rows, regenerate
  inventory/provisions/coverage, and update the zero-benefit authority map.
- Rebuild the MCE-exclusion map gate by gate against retained current
  7 CFR 273.2(j)(2)(vii) rows and the WIC §18901.3 state overlay; add semantic
  completeness tests.
- Correct the tracked run document, update this ledger after each coherent
  step, and run focused plus repository-wide validation, citation census,
  tracked-scope checks, release validation, and conservation checks.
- Write the final per-parameter authority audit to an untracked report. Leave
  stale manifest signatures untouched and identify re-signing as a main-lane
  follow-up.
