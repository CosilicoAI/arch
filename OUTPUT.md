# Illinois SCRETD cross-reference ingest report

## Outcome

**BLOCKED — no corpus ingest was generated.**

The existing Illinois source-first route and exact whole-act scopes were
confirmed, and the adapter was repaired for ILGA's current section URL.
However, this environment could not retrieve authentic Illinois General
Assembly source bytes. No provision text was reconstructed from browser/search
output, and no secondary source was substituted.

## Citation-path result

The check scanned all 143,811 inventory records in this checkout by exact
`citation_path` equality, both before and after the work:

| Requested citation path | Exact matches |
| --- | ---: |
| `us-il/statute/320/25/3.05` | 0 |
| `us-il/statute/320/25/3.05a` | 0 |
| `us-il/statute/320/25/3.07` | 0 |
| `us-il/statute/35/200/15-172` | 0 |
| `us-il/statute/210/45/1-113` | 0 |

No parent inventory rows exist for `320/25`, `35/200`, or `210/45` either.

## Declared scope

There is no new ingest manifest or coverage record, so this branch does **not**
declare or certify an ingest scope and does not claim `complete: true`.

The exact existing `320 ILCS 30` route naturally produces whole acts. Once
source access is available, the correct scopes are three separate whole-act
runs:

- `320 ILCS 25` — Senior Citizens and Persons with Disabilities Property Tax
  Relief Act
- `35 ILCS 200` — Property Tax Code
- `210 ILCS 45` — Nursing Home Care Act

Each run must contain its chapter and act containers plus every section in that
act. A future `complete: true` result would certify only that one declared act.

Semantic note: `320 ILCS 25/3.05` defines “Household,” `3.05a` defines
“Additional resident,” and `3.07` defines “Income.” The literal “Household
income” definition is `3.06`, which a whole `320 ILCS 25` run would also
include.

## Official sources and retrieval result

The official target stems are:

- `032000250K3.05`, `032000250K3.05a`, `032000250K3.07`
- `003502000K15-172`
- `021000450K1-113`

ILGA's current section route is:

```text
https://www.ilga.gov/legislation/ilcs/fulltext?DocName=<stem>
```

The repository still used the retired `fulltext.asp` route. This branch updates
`ILLINOIS_ILCS_FULLTEXT_URL` to the current official route and adds a focused
regression test and changelog fragment.

Source acquisition was attempted through every available non-transcription
path:

- Shell `curl` and the actual corpus command could not resolve
  `www.ilga.gov`.
- The actual `320 ILCS 25` extractor was run against an isolated temporary
  base and failed at the FTP root before writing a source or corpus file.
- Direct byte retrieval through the connected JavaScript runtime also failed.
- No interactive browser backend was available.
- The web proxy verified live official ILGA pages, but cannot persist the
  original response bytes or establish the retained-source SHA-256.
- An exhaustive local search found no target bytes in the repository, any
  reachable or unreachable Git object, sibling worktrees, temporary
  directories, Downloads, or browser caches.

Accordingly, this branch adds **zero** source, inventory, provision, coverage,
or signed-ingest-manifest artifacts. Existing SNAP and title-26 ingests were not
modified.

## Validation

- Focused Illinois tests: 20 passed.
- Ruff: passed.
- Mypy for `src/axiom_corpus/corpus`: passed, 89 files checked.
- Towncrier: passed and found the Illinois route fragment.
- Full pytest: 4,114 passed, 69 skipped, 208 deselected, 1 unrelated existing
  failure in
  `tests/test_storage_postgres.py::TestPostgresStorageSubsectionConversion::test_dict_to_subsection`.
- GitNexus assessed the affected URL-building path as LOW risk; the staged
  change scan found no affected execution process.

## Git and pull request

- Branch: `ingest/il-scretd-cross-references`
- The branch was pushed to `origin`.
- Draft PR creation is blocked: the GitHub CLI reports its stored token as
  invalid, the agent secret store is locked, and the GitHub connector is not
  installed. No credential was extracted from another store.

## Unblock

From a network-enabled lane, rerun the direct `extract-illinois-ilcs` command
three times with paired `--only-chapter` and `--only-act` filters for `320/25`,
`35/200`, and `210/45`. Reject any run with nonzero extraction errors or
skipped fetches even if coverage says `complete: true`, then verify the five
exact inventory citation paths before signing or promotion.
