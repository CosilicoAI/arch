# Illinois SCRETD cross-reference ingest report

## Outcome

The staged official Illinois General Assembly HTML was ingested into three
separately declared statute scopes. All six requested citation paths now
resolve exactly once across corpus inventory records. The three source
snapshots, inventories, provision JSONL files, coverage reports, and reasoning
logs are committed in `fba2c93f`.

The corpus records are complete and validated. Authorized signed ingest
manifests could not be written because this shell does not have
`AXIOM_CORPUS_INGEST_PRIVATE_KEY`; no replacement key or signature was
fabricated. Push and draft-PR creation were also attempted and blocked by the
network-disabled sandbox.

## Citation-path resolution

The final exact-equality search scanned 143,950 inventory records:

| Citation path | Exact matches | Inventory version |
| --- | ---: | --- |
| `us-il/statute/320/25/3.05` | 1 | `2026-07-27-ilcs-320-25-whole-act` |
| `us-il/statute/320/25/3.05a` | 1 | `2026-07-27-ilcs-320-25-whole-act` |
| `us-il/statute/320/25/3.06` | 1 | `2026-07-27-ilcs-320-25-whole-act` |
| `us-il/statute/320/25/3.07` | 1 | `2026-07-27-ilcs-320-25-whole-act` |
| `us-il/statute/35/200/15-172` | 1 | `2026-07-27-ilcs-35-200-article-15` |
| `us-il/statute/210/45/1-113` | 1 | `2026-07-27-ilcs-210-45-article-1` |

## Declared scopes

| Version | Declared scope | Sections | Normalized records | Coverage |
| --- | --- | ---: | ---: | --- |
| `2026-07-27-ilcs-320-25-whole-act` | All of `320 ILCS 25` | 40 | 42 | `complete: true` (42/42) |
| `2026-07-27-ilcs-35-200-article-15` | `35 ILCS 200`, Article 15 only | 54 | 56 | `complete: true` (56/56) |
| `2026-07-27-ilcs-210-45-article-1` | `210 ILCS 45`, Article I only | 39 | 41 | `complete: true` (41/41) |

Each normalized count includes one chapter container, one act container, and
every section within the declared source scope. Article-heading tables are
scope boundaries rather than separate ILCS section records, matching the
existing Illinois adapter convention.

## Official sources and provenance

All snapshots were copied byte-for-byte from the staged files and record
`fetched_at: 2026-07-27` in inventory and provision metadata.

| Scope | Official source URL | Snapshot SHA-256 |
| --- | --- | --- |
| `320 ILCS 25`, whole act | `https://www.ilga.gov/Legislation/ILCS/Articles?ActID=1453&ChapterID=31&Chapter=AGING&MajorTopic=HUMAN%20NEEDS` | `62b418b2f877c41b6b71ebb58ea52f3708dedac9762e341653fed76f23370a6c` |
| `35 ILCS 200`, Article 15 only | `https://www.ilga.gov/legislation/ILCS/details?MajorTopic=&Chapter=&ActName=Property%20Tax%20Code.&ActID=596&ChapterID=8&ChapAct=35+ILCS+200%2F&SeqStart=38400000&SeqEnd=43899999&Print=True` | `64eb4f69ac8741242ce2a61ce2ca300a816d182ed59b52672723ffad8efcf6a8` |
| `210 ILCS 45`, Article I only | `https://www.ilga.gov/legislation/ILCS/details?MajorTopic=&Chapter=&ActName=Nursing+Home+Care+Act.&ActID=1225&ChapterID=21&ChapAct=210+ILCS+45%2F&SeqStart=100000&SeqEnd=4200000&Print=True` | `f7642bde9e15719659721ba7242d5fd34b1a04d9ca18ef39556368a5caa659c8` |

## Verbatim extraction result

Every one of the 133 section bodies was compared with the corresponding
official source table after applying only the existing Illinois HTML
markup/whitespace normalization. All 133 comparisons matched exactly.

No requested text was truncated, ambiguous, or unavailable:

- `320 ILCS 25/3.05`, `3.05a`, `3.06`, and `3.07` are complete through their
  official source notes.
- `35 ILCS 200/15-172` is complete through subsection (d), the State Mandates
  paragraph, and `(Source: P.A. 104-452, eff. 12-12-25.)`.
- The official `210 ILCS 45/1-113` table contains two explicitly labeled
  variants. The provision retains the complete requested
  `(Text of Section from P.A. 104-147)` block, including exclusion (16), through
  `(Source: P.A. 104-147, eff. 8-1-25.)`. The following P.A. 104-234 variant is
  excluded.

The official `35 ILCS 200/15-160` table also presents labeled WITH/WITHOUT
variants concerning P.A. 97-1161. Both official labeled blocks are retained
verbatim in that section record rather than choosing or synthesizing text.

## Validation

- Coverage command: all three scopes passed with no missing, extra, or
  duplicate citation paths.
- Independent source-to-inventory audit: 40/40, 54/54, and 39/39 source
  section markers matched inventory and provision bodies.
- Source integrity: all copied source bytes match the staged originals; every
  inventory row has the correct source path, URL, SHA-256, scope declaration,
  and fetch date.
- `verify-scope-tracked`: passed for all three versions.
- Focused Illinois tests: 20 passed.
- Ruff: passed.
- Mypy for `src/axiom_corpus/corpus`: passed, 89 files checked.
- Towncrier: passed.
- Full pytest: 4,114 passed, 69 skipped, 208 deselected, and 1 unrelated
  existing failure in
  `tests/test_storage_postgres.py::TestPostgresStorageSubsectionConversion::test_dict_to_subsection`.
  Neither the failing implementation nor its test differs from `origin/main`;
  the same failure was present before this ingest.

GitNexus tools were unavailable in this session. This resumed work changed no
code symbols; the diff from the resume commit contains only new ingest
records, reasoning logs, and the required progress ledger/final report.

## Manifest, push, and pull-request status

Unsigned v1 manifest payload construction succeeded for all three scopes,
including all four inferred files and each reasoning log. The required signing
command then failed with:

```text
AXIOM_CORPUS_INGEST_PRIVATE_KEY is required to sign ingest manifests.
```

Accordingly, no `.axiom/ingest-manifests/...` file was written. An authorized
lane must sign the three committed versions; this report does not represent an
unsigned file as a valid ingest manifest.

The requested push failed with:

```text
fatal: unable to access 'https://github.com/TheAxiomFoundation/axiom-corpus.git/':
Could not resolve host: github.com
```

The draft-PR command was attempted after the push and failed while connecting
to `api.github.com`. No pull request was created. The local branch is
`ingest/il-scretd-cross-references`; its new ingest artifact commit is
`fba2c93f`.

## Remaining delivery steps

1. Provide the authorized ingest private/public keys and sign the three
   versions from a clean tracked state.
2. Commit the signed manifests.
3. Push `ingest/il-scretd-cross-references`.
4. Open the requested draft pull request against `main`.
