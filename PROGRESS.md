# Lane E witness-line corpus ingest progress

## State

Complete on `laneE/witness-line-sources` from `origin/main` at `598317e7`.
The implementation is one local unsigned feature commit. No signing,
publication, Supabase/R2 writes, or push operations were performed.

## Done

- Read `CLAUDE.md` and the worktree `AGENTS.md` instructions.
- Verified the branch/base and preserved the operator-provided untracked
  `.laneE-sources/` inputs.
- Began a fresh local GitNexus index and read-only review of existing HTS,
  page-PDF, citation-validator, and CI conventions.
- Completed the read-only architecture and blast-radius review. Shared corpus
  storage and coverage symbols are high-impact and remain unchanged; all new
  work is additive.
- Confirmed strict release validation requires each version to own regular
  source files beneath its version path, so the four HTS JSON inputs are
  copied byte-for-byte. Git reuses their existing blob objects.
- Implemented and reproduced four `2026-08-02` HTS witness-line versions.
  Each has complete 11/11 coverage (one document root plus ten exact beer and
  solar rows), pinned source hashes, exact raw footnote metadata, and built-in
  regime sanity checks.
- Implemented and reproduced the page-level Proclamation 10339 version from
  the pinned six-page Federal Register PDF. It has complete 6/6 coverage,
  standard unsorted PyMuPDF text extraction without OCR or replacements, and
  direct checks for the critical solar staged-rate and HTS amendment text.
- Implemented and reproduced the Section 338 alcohol annex text-rendition
  version from the two pinned White House PDFs. It has two same-scope annex
  roots, ten exact page bodies, complete 12/12 coverage, and direct checks for
  the beer list, full note 51 exception families, and inserted 9903 headings.
  The graphics-only Federal Register PDF is pinned in metadata but omitted as
  an unreferenced source and is never used for provision bodies.
- Added the changelog entry and deliberately raised only the reviewed
  `page_n` citation-path ratchet by 16, from 35,652 to 35,668.
- Reproduced all 25 generated artifacts into a fresh corpus from retained
  sources and matched them byte-for-byte; all 124 stored repro-command
  instances are shlex-canonical.
- Passed ruff, mypy (89 corpus source files), both requested pytest runs
  (4,168 passed, 73 skipped, 208 deselected), towncrier check/draft,
  actionlint, citation-path validation (35,668/35,668 `page_n`), all six
  coverage and tracked-source checks, and all 82 named release selectors.
- Confirmed the branch remains exactly one commit above `598317e7` and only
  adds new dated corpus artifacts; the four HTS source paths reuse the exact
  existing Git blob objects.

## Next

- Operator reviews `.laneE-sources/REPORT.md`, supplies the configured ingest
  verification key, signs the new scopes from the clean commit, and reruns the
  signed-ingest guard before any separately authorized publication.
