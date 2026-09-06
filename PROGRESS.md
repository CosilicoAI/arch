# Israel statute pilot progress

## State

- Worktree: `_worktrees/axiom-corpus-il-ingest`; branch `ingest/il-taxben-pilot`,
  cut from `origin/main` at `f22e9a45`.
- Scope/version: `il/statute` / `2026-09-06-il-taxben-pilot`.
- Bounded pilot on a **secondary consolidation**. The claim is source fidelity,
  not coverage: every provision the captured OpenLaw pages render becomes a row,
  reconciled 1,414 against 1,414 with 0 missing and 0 extra. That is a
  row-generation reconciliation, not a statement that the scope is the complete
  statute as administered, and not certification of anything.
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
  228 navigation nodes, 1,414 provisions, reconciled 1,414 against 1,414
  inventory entries with 0 missing and 0 extra.
- Repaired the two defects an offline adversarial review verdicted DO-NOT-SHIP:
  editorial-note removal was deleting the statutory tables it should only have
  annotated (NII לוח ח׳2, the §337(א)/§340(א) contribution-rate tables under
  לוח י׳, and לוח י״ז all fell back to heading-only bodies), and h4 statutory
  subheadings were dropped from bodies and overwritten in metadata, so the two
  identically-headed retirement ladders of לוח א׳1 lost גיל הפרישה לגבר /
  גיל הפרישה לאישה. Tables are now identified individually — only a table
  introduced by an unparenthesised, colon-terminated lead-in and carrying no
  note of its own is the project's apparatus — and every h4 stays in the body at
  its printed position and in `metadata.captions` in order.
- Repaired the third defect a multi-agent audit of that repair then found: the
  tables came back without the labels that qualify them, because `span.law-note`
  was still stripped unconditionally. `schedule-j/sign-1` printed both
  §337(א)/§340(א) contribution-rate tables under the identical header with
  nothing between them, and (הוראת שעה לשנים 2025–2026): / (הנוסח הקבוע): sat in
  a positionless list; two entries of לוח ח׳2 read as in force with
  (יבוטל ביום 31.12.2026): and (פקע). deleted. A parenthesised note inside a table
  cell, and a parenthesised colon-terminated label printed above a table, now stay
  in the body where the source prints them and are recorded in
  `metadata.statutory_notes`. That is 11 notes in 2 rows across both snapshots;
  amendment history, OpenLaw's indexed-amount glosses, its footnote letters and
  its comparison lead-in are unchanged and still never reach a body.
- Net effect of all three repairs: 1,414 rows before and after, 0 added,
  0 removed, 40 nav bodies grew, no section, schedule-item or document body
  changed, and no row lost a line of its previous body.
- Added `tests/test_israel_openlaw.py` (81 tests) covering the transliteration,
  the false-split hazards, editorial-apparatus removal, the four real table
  shapes and their labels, both statutory note shapes with negative controls for
  the glosses that must stay out, status lines, schedule binding, manifest
  validation, fail-before-write drift checks, and the checked-in pack.
- Committed the unsigned ingest manifest and the `il-rulespec-2026-09-06`
  release-cut plan; `validate-release` reports 0 issues.

## Next

1. Dispatcher **re-signs** `.axiom/ingest-manifests/il/statute/2026-09-06-il-taxben-pilot.json`
   from a clean root checkout, then CI `guard-ingested` goes green. The first
   signature (commit `da222e7c`) covered the pre-repair artifacts and no longer
   describes the tree; the manifest is committed unsigned again on purpose.
2. Land the PR with a true **merge commit**; never squash or rebase — the
   manifest attests the head of this branch.
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
- **One transcription defect in the consolidation, carried through unrepaired.**
  ITO §187 reads "בסעיף 59א(א)" and links to a `#סעיף_59א` that does not exist;
  Nevo reads "בסעיף 159א(א)" there and prints that form 22 times with no
  occurrence of the short one. The corpus stores the source verbatim. The spot
  check pins it as the only known dangling internal reference so that any other
  one — which would mean a lost section — fails.
- **One printed-label disagreement.** OpenLaw prints "57א" against the anchor
  `סעיף_57ג`. The anchor wins; `metadata.printed_label_mismatch` records it.
- **Citation-scheme extensions, ratified.** This scope needed two extensions
  beyond the suffix mapping `ops/il-lane/CITATION-SCHEME.md` originally
  enumerated: suffix ordinals past 26 continuing in bijective base-26
  (כז→aa … לד→ah), and `…/schedule-<ident>/item-<ident>` for schedules. The
  dispatcher ratified both on 2026-09-06 and the scheme file now states the
  gematria-value rule through לד=34; a naive letter-position mapping was not
  merely underspecified but collided (כ with יא on ITO §103, §195 and NII §179).
