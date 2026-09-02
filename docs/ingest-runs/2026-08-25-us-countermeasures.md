# Canada 2026 United States countermeasures announcement sources

This local source-first run retains and extracts the Department of Finance
Canada news release and backgrounder/product list published on August 25,
2026 as announcement-stage rulemaking source material. The announced
counter-tariffs take effect September 8, 2026.

This scope is not the legal instrument. At capture, the formal United States
Surtax Order under section 53 of the *Customs Tariff* had not been gazetted.

## Scope

| Source | Citation root | Composition | Provisions |
| --- | --- | --- | ---: |
| Finance Canada news release | `ca/rulemaking/finance-canada/2026-08-25/us-countermeasures-announcement` | 1 document root + 16 news-release units + 4 quotations + 5 quick facts | 26 |
| Finance Canada backgrounder and product list | `ca/rulemaking/finance-canada/2026-08-25/us-countermeasures-product-list` | 1 document root + 7 backgrounder paragraphs + 1 table-context unit + 629 tariff-item rows | 638 |
| **Total** |  | 2 document roots + 662 body-bearing units | **664** |

The table context is separately citable at:

`ca/rulemaking/finance-canada/2026-08-25/us-countermeasures-product-list/table`

Each tariff item is its child. For example, tariff item `0402.10.10` is:

`ca/rulemaking/finance-canada/2026-08-25/us-countermeasures-product-list/table/0402.10.10`

The backgrounder separately preserves the matching-rate announcement, origin
rule, 12:01 a.m. effective time, transit exception, and *Customs Tariff*
context in `backgrounder-2` through `backgrounder-7`.

## Sources and provenance

Both pages were captured on September 1, 2026 at approximately 19:15–19:25
ET through a same-origin browser fetch, transferred as raw response bytes, and
re-verified locally.

### News release

- Official URL: `https://www.canada.ca/en/department-finance/news/2026/08/canada-announces-targeted-countermeasures-and-substantive-support-for-workers-and-businesses-in-response-to-us-tariffs.html`
- Published: 2026-08-25 11:05:23.
- Modified: 2026-08-26 20:06:58.
- Retained size: 39,681 bytes.
- Retained SHA-256: `cd111fd549ed0f2b6e1b0c8ec0d1c9c26ca111dfa3386e6a186937c3d19f49da`.
- Retained path: `data/corpus/sources/ca/rulemaking/2026-08-25-us-countermeasures/official-documents/2026-08-25-finance-countermeasures-release.html`.

### Backgrounder and product list

- Official URL: `https://www.canada.ca/en/department-finance/news/2026/08/list-of-products-from-the-united-states-subject-to-counter-tariffs-effective-september-8-2026.html`
- Published: 2026-08-25 11:04:15.
- Modified: 2026-08-26 20:15:31; the visible list label says `List updated as of August 26, 2026`.
- Retained size: 317,676 bytes.
- Retained SHA-256: `6e802306889dbfa910f7984e7075a63977729ede83ceba6e8aa399de86f651ec`.
- Retained path: `data/corpus/sources/ca/rulemaking/2026-08-25-us-countermeasures/official-documents/2026-08-25-finance-product-list.html`.

Canada.ca embeds per-request nonces, so a later fetch is not expected to
reproduce these hashes. The hashes authenticate these captures, not an
immutable legal-document identity. The gazetted Surtax Order will provide the
stable legal identity.

The coordinator also supplied a 141,516-byte TSV convenience derivative with
SHA-256
`fdb02fa6e867ac56f228d9daf2b87f0c850fa4b40275379f127ed423f5052e34`.
It is neither retained nor used as a source. It is used only as a 629-row
equality oracle for the independently parsed HTML table.

## Extraction

The release extractor selects the visible news-release body, four quotations,
and five quick facts. It excludes the hidden teaser, associated-links
navigation, contacts, and Canada.ca site chrome.

The product extractor selects the seven direct backgrounder paragraphs, the
visible update label, caption and four headers, and all 629 direct `tbody`
rows. Each tariff-item body is a newline rendering of the exact visible header
and cell strings in source-column order. It does not paraphrase descriptions
or add a percent sign to the source rate. Standard corpus visible-text
normalization collapses HTML whitespace and `<br>` boundaries in the same way
as the reference official-document extractor. Thirteen intentionally blank
indicative-description cells remain blank.

The exact successful generation command was:

```bash
PYTHONPATH=src /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python /Users/maxghenis/PolicyEngine/_tariff-p5/ca-countermeasures/ingest-lane/build_ca_countermeasures.py --base data/corpus --tsv /Users/maxghenis/PolicyEngine/_tariff-p5/ca-countermeasures/pins/2026-08-25-finance-product-list-extracted.tsv
```

The extraction driver is lane-local and is not added to the corpus repository
because this ingest is restricted to the new source scope, its derived corpus
artifacts, the ingest-run record, progress ledger, and signed manifest.

## Verification

- Both retained HTML files match the coordinator handoff byte-for-byte.
- Inventory, provisions, and coverage contain 664 unique paths; coverage is
  complete with `source_count=664`, `provision_count=664`, and
  `matched_count=664`.
- The product list contains 629 unique, ascending tariff items from
  `0402.10.10` through `9507.10.90`.
- Rate census: 413 items at 50 per cent, 195 at 25 per cent, and 21 at 15 per
  cent.
- Independently parsed HTML cell text matches every pinned TSV field with no
  differences.
- A second generation run produced identical hashes for both retained sources,
  inventory, provisions, and coverage.
- The coverage verifier reported 664 source paths, 664 provision paths, 664
  matches, and no missing, extra, or duplicate paths.
- The tracked-scope verifier reported `Verified 2 referenced files across 1
  inventory scopes.`
- Citation-path validation reported 664 records and 664 unique paths with no
  JSON, pattern, jurisdiction, document-class, or drift failures.
- Ruff passed, and mypy reported `Success: no issues found in 91 source files`.
- The full test suite reported `4313 passed, 74 skipped, 208 deselected` and
  one failure in
  `TestPostgresStorageSubsectionConversion.test_dict_to_subsection`. The same
  isolated test fails identically at the untouched base commit, so it is a
  pre-existing Python/dependency-environment failure unrelated to this
  data-only change.
- Towncrier's branch check reported no new news fragment. No fragment was
  added because this ingest's binding scope restriction forbids unrelated
  changelog edits.
- GitNexus classified the changed indexed documentation as low risk, with no
  affected symbols or execution flows. Corpus data files are not indexed as
  code symbols.

## Manifest authentication status

The clean content commit is
`a67f0012585f91c66c944f9e32c2b7ba09497162`. The required retrieval command
was attempted without printing or persisting secret material:

```bash
agent-secret get agent/axiom-corpus-ingest-private-key
```

It exited 17 with:

```text
agent-secret: missing unlock password. Run: agent-secret init
```

Initializing a replacement key store would not unlock the pinned corpus key,
so this run did not improvise around the blocker. No manifest has been
created, and signature verification must wait for a session in which the
existing key store is unlocked. The signing commit must remain separate and
must be made from a clean checkout after all documentation changes.

## Deferred legal-instrument work

When the United States Surtax Order is registered and gazetted, retain it as a
separate authoritative source root with its schedule and legal identifiers.
Do not represent this announcement-stage scope as the Order itself. Any later
amendment to the Finance Canada list also requires a new pinned expression;
these nonce-bearing captures must not be silently replaced.

Publication must preserve the signed ancestry and use a true merge commit.
Do not squash or rebase the corpus pull request.
