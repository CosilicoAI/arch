# Israel statute pilot progress

## State

- Worktree: `_worktrees/axiom-corpus-il-ingest`; branch `ingest/il-taxben-pilot`,
  cut from `origin/main` at `f22e9a45`.
- Scope/version: `il/statute` / `2026-09-06-il-taxben-pilot`.
- Bounded pilot on a **secondary consolidation**. No completeness claim beyond
  "both instruments in full", no certification language.
- The ingest manifest is committed **unsigned**; the dispatcher signs it from a
  clean root checkout. CI `guard-ingested` is expected to be red until then.

## Done

- Read `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, the Israel campaign brief,
  the binding citation scheme, and the Armenia ARLIS adapter as the template.
- Characterized both hash-pinned snapshots without ever printing raw HTML: the
  ספר החוקים הפתוח (OpenLaw) pages are anchor-structured (`div#law-content`,
  `div.law-number[id="סעיף_…"]`, `div.law-desc`, `div.law-main`,
  `h1.law-part` / `h2.law-section` / `h3.law-subsection`, `span.law-note`), so
  the adapter is anchor-driven, not line-regex driven.
- Verified `expression_date` first-hand against the Knesset registry rather than
  asserting it from the page: OData `KNS_IsraelLaw` returned
  `LatestPublicationDate` 2026-06-08 for IsraelLawID 2000944 and 2026-06-15 for
  2000198, both `LawValidityDesc` תקף. Response captured at
  `ops/il-lane/sources/knesset-israel-law-metadata.json` outside this repo.
- Added `src/axiom_corpus/corpus/israel_openlaw.py` and the
  `extract-il-openlaw` CLI command, grouped under "Extract: international".
- Added `manifests/il-taxben-pilot-openlaw.yaml` pinning both instruments by
  SHA-256, expression date + declared basis, and expected structural counts.
- Found that the Ordinance's full-page Wikisource render is silently truncated
  by MediaWiki's post-expand include limit (`Post-expand include size:
  2097152/2097152 bytes`, 240 omitted-template markers): §§235-247 and all four
  תוספות never render, and §235 was landing as 30,059 characters of MediaWiki
  error text. The adapter now refuses an undeclared truncated render, cuts the
  primary at the start of the damaged section, and completes the document from a
  hash-pinned supplement rendered from the same revision (3079834) via
  `api.php?action=parse`. +49 rows, 0 removed, and no other provision body
  changes.
- Extracted the scope: 2 documents, 1,138 sections, 46 schedule items,
  228 navigation nodes, 1,414 provisions, 1,414/1,414 coverage.
- Added `tests/test_israel_openlaw.py` (71 tests) covering the transliteration,
  the false-split hazards, editorial-apparatus removal, status lines, schedule
  binding, manifest validation, fail-before-write drift checks, and the
  checked-in pack.
- Committed the unsigned ingest manifest and the `il-rulespec-2026-09-06`
  release-cut plan; `validate-release` reports 0 issues.

## Next

1. Dispatcher **re-signs** `.axiom/ingest-manifests/il/statute/2026-09-06-il-taxben-pilot.json`
   from a clean root checkout, then CI `guard-ingested` goes green. The first
   signature (commit `da222e7c`) covered the pre-repair artifacts and no longer
   describes the tree; the manifest is committed unsigned again on purpose.
2. Land the PR with a true **merge commit**; never squash or rebase — the
   manifest attests commit `271bac97`.
3. Cut and publish `il-rulespec-2026-09-06` only after corpus `main` carries the
   signed ingest. Publication and activation are not this lane's to do.
4. Before any Israeli amount is cited as current law, add a separate scope for
   the Tax Authority and National Insurance Institute amount publications and
   for the gazette PDFs of the 2025/2026 amending acts. This scope carries
   statute text only.

## Known limits of this scope

- **Source tier, per act.** Provision text is the he.wikisource.org
  ספר החוקים הפתוח consolidation — a volunteer consolidation, not an official
  gazette text. The Knesset database's "לחוק המלא" link was followed to the
  Wikisource page for the Ordinance (`consolidation-knesset-linked`); the same
  check is still pending for the National Insurance Law, which therefore claims
  only `consolidation-wikisource`. The tier is on every row.
- **The Ordinance is assembled from two rendered fragments.** The full-page
  render cannot carry the whole law (MediaWiki post-expand include limit), so
  §§235-247 and the four תוספות come from a supplement rendered from the same
  revision's wikitext. Both fragments are hash-pinned in the manifest and stored
  in the scope; every row records which one it came from. The National Insurance
  Law's render is undamaged and uses no supplement.
- **Gazette cross-checks done for two provisions only.** §120ב(ה) (the
  2025-2027 indexation freeze, amendment 276, ספר החוקים 3342) and §121's 2026
  bracket edges (amendment 288, ספר החוקים 3511 p.415) both match the captured
  consolidation, checked against the gazette PDFs this session. Every other
  provision in the scope rests on the consolidation alone.
- **§283 of the National Insurance Law appears twice** — the operative text and
  a version conditioned on publication of the 2026 budget law. Both are landed,
  as `section-283` and `section-283-alt2`; this lane does not decide which is
  in force.
- **One printed-label disagreement.** OpenLaw prints "57א" against the anchor
  `סעיף_57ג`. The anchor wins; `metadata.printed_label_mismatch` records it.
- **Citation-scheme extensions.** `ops/il-lane/CITATION-SCHEME.md` fixes section
  paths and enumerates the suffix mapping only to יב→l. This scope extends it in
  two places, flagged for the dispatcher rather than assumed:
  suffix ordinals past 26 continue in bijective base-26 (כז→aa … לד→ah), and
  schedules use `…/schedule-<ident>/item-<ident>`.
