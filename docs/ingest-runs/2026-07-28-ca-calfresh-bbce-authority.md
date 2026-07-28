# California CalFresh BBCE authority

This source-first scope retains the minimum official California authority
hierarchy for CalFresh broad-based categorical eligibility, called modified
categorical eligibility (MCE) by California. It adds current Welfare and
Institutions Code §18901.5 and five CDSS All County Letters.

## Retained official sources

The source payloads were downloaded directly from the official California
Legislative Information and CDSS endpoints. They are retained byte-for-byte
without reserialization, OCR, or source-text correction.

| Source | Bytes | PDF pages | Rows | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| WIC §18901.5 HTML | 164,166 | — | 1 | `97cae778729e0dd5d3c15797934690467876a14057e7d856d1500326e72d004e` |
| ACL 14-56 | 278,260 | 7 | 8 | `8677c1d3e5c2ec9ecef23206b24061999817a46fa469ccb68a000b8f2f570d5e` |
| ACL 14-56E | 189,729 | 4 | 5 | `67e33a2613009abaef3759ebc2a583417fb852120f009848e3b1a1e3c3c11cbd` |
| ACL 15-42 | 249,307 | 13 | 14 | `6aab92e4e2a2c9e0f234eba2b1c0eeb68d4d9d5dbc7ba752465a2358d9f2db33` |
| ACL 14-100 | 209,290 | 12 | 13 | `c981081163b361eea20aeeccec7934509dc5bf23d8d66c8035895586db60131e` |
| ACL 13-32 | 204,909 | 3 | 4 | `1a0bbfc2d6d69fd378aff3f1285d03d20b8b6abf2ff64c749b9897fd1cc55506` |

All 39 PDF pages contain embedded text and each emits one page provision. The
five PDF document roots bring guidance coverage to 44/44 rows; WIC §18901.5
adds one complete statute row at `us-ca/statute/wic/18901.5`.
Because this is a one-section slice, its unresolved top-level parent link is
cleared for release self-containment; the official `us-ca/statute/wic` source
hierarchy remains recorded in metadata.

## Authority boundary

- WIC §18901.5 carries California's statutory categorical-eligibility mandate.
- ACL 14-56 carries the statewide PUB 275 trigger, inclusive 200 percent
  screen, resource exclusion, and zero-benefit operation.
- ACL 14-56E is the formal correction that CDSS requires readers to use with
  ACL 14-56.
- ACL 15-42 later restates the 200 percent boundary, MCE continuation/removal,
  net-income treatment, and exclusions.
- ACL 14-100 removes the former blanket prior-drug-felony exclusion effective
  April 1, 2015.
- ACL 13-32 carries the separate elderly/disabled route.

Historical dollar amounts and procedural workarounds in these letters are not
asserted as current figures. Current annual CalFresh amounts remain in the
separately retained ACIN I-46-25 scope.

## Deterministic offline reproduction

The 12 scoped artifacts—six exact source snapshots plus inventory, provisions,
and coverage for the guidance and statute scopes—are reproduced by this
literal portable command:

```bash
uv run --extra dev python scripts/repro/us_ca_calfresh_bbce_authority.py --base data/corpus
```

The script's `REPRO_COMMAND` constant is byte-for-byte identical to that
invocation. By default it reads the committed retained source paths. For a
bootstrap or CI lane supplied with the six flat original files, it also accepts
a local source directory:

```bash
uv run --extra dev python scripts/repro/us_ca_calfresh_bbce_authority.py \
  --base data/corpus \
  --source-dir .ca-bbce-sources
```

Before writing output, the script hard-checks all six hashes and sizes, all
five PDF page counts, and nonempty embedded text on every PDF page. It stages
both scopes, requires 44/44 and 1/1 coverage, verifies exact citation paths,
per-source row counts, retained-byte equality, official (non-`file://`)
metadata URLs, and controlling authority excerpts.

No publication, R2 upload, Supabase load, release activation, RuleSpec
repository change, push, or GitHub mutation is part of this ingest. The ingest
manifests remain unsigned for the main lane to sign after the final content
commit is an ancestor.
