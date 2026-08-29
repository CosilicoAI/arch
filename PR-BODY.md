## Summary

- add a fail-closed `extract-am-arlis` path for local Armenian Legal Information System (ARLIS) consolidated HTML snapshots
- pin the six tax-and-benefit statutes harvested on 2026-08-29, including each source hash, official identity, language, retrieval date, consolidation expression date, and expected article count
- preserve Armenian article text, amendment annotations, decimal article numbers, court-decision links, and part/section/chapter/appendix hierarchy
- keep article identities stable at `am/statute/act-<id>/article-<label>` while carrying hierarchy through explicit parent links and metadata
- add the complete `am/statute/2026-08-29-am-taxben-core` source, inventory, provision, and coverage artifacts

This gives `rulespec-am` a resolvable primary-law corpus for the first encoding tranche required by TheAxiomFoundation/.github#39. It does not encode or interpret any policy rule.

## Extracted scope

| Source | Articles | Structural records |
| --- | ---: | ---: |
| Tax Code | 474 | 114 |
| Funded pensions | 81 | 15 |
| Universal health insurance | 46 | 9 |
| Servicemen compensation | 32 | 5 |
| State benefits | 44 | 14 |
| State pensions | 58 | 10 |
| **Total** | **735** | **167** |

Together with six document roots, the scope contains 908 provisions. Inventory-to-provision coverage is complete: 908/908 matched, with no missing or extra citations.

The exact count is higher than the initial text-only reconnaissance estimate because ARLIS splits the Armenian word for “Article” around an empty anchor in Tax Code Articles 78 and 147.1. The DOM-based extractor binds both substantive provisions and locks that markup variant in tests.

## Integrity contract

The extractor validates every manifest and all six sources before writing any artifact. It rejects:

- an unpinned or changed source hash
- a source path outside the requested source directory
- a non-ARLIS or mismatched act URL
- identity or consolidation-date metadata that disagrees with the official page
- an unquoted or missing date, a non-Armenian language tag, or an unexpected article count
- unbound article markers, duplicate citations, or incomplete inventory/provision coverage

`source_as_of` records the 2026-08-29 retrieval. `expression_date` records the official consolidation expression shown by each ARLIS page: 2026-05-08, 2026-05-18, or 2026-09-01, depending on the act.

## Verification

- `uv run --extra dev ruff check .`
- `uv run --extra dev ruff format --check src/axiom_corpus/corpus/armenia_arlis.py tests/test_armenia_arlis.py`
- `uv run --extra dev mypy src/axiom_corpus/corpus --ignore-missing-imports`
- `uv run --extra dev python -m pytest -q`
- `uv run --extra dev towncrier check`
- `git diff --check`

The full suite passes with 4,266 tests passed, 79 skipped, and 208 deselected. The focused Armenia and CLI-group suites cover the full checked-in six-source pack, malformed ARLIS markup variants, exact counts/dates, deterministic parent identities, fail-before-write hash/count/identity drift, and grouped CLI registration.

## Publication boundary

No signing, R2/Supabase load, release publication, RuleSpec change, push, or PR creation is part of this branch preparation. The dispatcher must add the authenticated ingest manifest from a clean checkout before the normal protected publication workflow can proceed.
