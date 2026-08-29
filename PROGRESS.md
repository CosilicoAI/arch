# Armenia ARLIS ingest progress

## State

- Branch: `ingest/am-taxben-core` from `origin/main` at `620527d7`.
- Target scope/version: `am/statute` / `2026-08-29-am-taxben-core`.
- Current phase: implementation and artifact validation complete; local commit and dispatcher signing handoff remain.
- Constraints: offline only; no signing, publishing, pushing, PR creation, or edits to protected toolchain/workflow ownership files.

## Done

- Read `AGENTS.md`, `CLAUDE.md`, and `CONTRIBUTING.md` in the required order.
- Loaded the GitNexus exploration, impact-analysis, and CLI instructions.
- Confirmed the requested branch and base commit and that the tracked worktree began clean.
- Read the DK ingest history/layout, ELI documentation, relevant HTML adapters, manifest/guard implementation, release-quality validator, provision-identity contract, and CLI grouping tests.
- Characterized and hash-verified all six read-only ARLIS snapshots, including source identity, expression metadata, malformed Word HTML, court icons, NBSPs, split-word article markers, decimal labels, amendment annotations, hierarchy, and appendices.
- Added a local-only, fail-closed `extract-am-arlis` command and source manifest.
- Generated and deliberately force-added all four protected artifact families plus the six byte-identical official source snapshots.
- Extracted 6 roots + 735 articles + 167 structural/appendix records = 908 total provisions with 908/908 complete coverage.
- Stabilized article identity at document scope while preserving hierarchy through explicit parent links and metadata.
- Added real-pack and adversarial regression tests, the changelog fragment, `PR-BODY.md`, and the external lane report.
- Completed an independent staged-diff review with no actionable findings.

## Next

1. Commit the validated branch and record the post-commit receipts.
2. Dispatcher: add the authenticated ingest manifest from a clean root checkout.
3. Run the protected ingest guard and normal CI review, then decide whether to push/open the merge-commit PR.
4. After corpus main contains the signed ingest, cut the separate immutable `am-rulespec-*` release; no selector belongs in this lane.

## Validation log

- `extract-am-arlis`: 6 documents, 735 articles, 167 structural records, 908 provisions, 908/908 coverage.
- Focused Armenia + CLI grouping: 22 passed.
- Full pytest: 4,266 passed, 79 skipped, 208 deselected.
- Repository Ruff: pass.
- Corpus mypy: 91 source files, no issues.
- Citation-path validator: 310,771 records scanned; no grammar, class, jurisdiction, ratchet, or identity-drift failure.
- Deep synthetic `complete-expression-dates-v1` release validation: 0 errors, 0 warnings.
- `git diff --check`: clean; official HTML sources are cataloged as binary to preserve their pinned bytes.

## Decisions and risks

- The initial 733-article estimate was wrong: Tax Articles 78 and 147.1 split `Հոդված` around an empty anchor. The verified pack has 735 articles.
- The initial 119-hierarchy estimate also undercounted malformed Word HTML. Raw and repaired-DOM audits agree on 162 hierarchy nodes plus 5 appendices.
- `source_as_of` remains 2026-08-29; official consolidation expression dates are 2026-05-08, 2026-05-18, or 2026-09-01 and are checked against each page.
- Stored source snapshots remain byte-identical; resolved text normalizes NBSP to ordinary space while retaining Armenian punctuation, line structure, and all amendment references in the legal root.
- Future unseen ARLIS markup intentionally fails closed and will require an adapter update.
- The local GitNexus refresh crashed in the Node native layer, so impact/context checks used the existing origin-main index; the CLI change was classified low risk and targeted/grouped tests cover the affected surface.
- Signing is still a hard gate. This lane did not sign, load, publish, push, or create a PR.
