# Lane C1 — `be-rulespec-2026-08-23` corpus-promotion report

## Outcome

The release-preparation content is committed locally on
`be-rulespec-2026-08-23-promotion` and has not been pushed, published, signed,
mirrored, activated, loaded into Supabase, or written to R2.

The content commits are:

```text
d52c0e68fed54d9cc98dde80c38a2da79087f491  Prepare BE RuleSpec 2026-08-23 release artifacts (#617)
6c9f4bf5549a4a40021118c19c316d63bb435e89  Record unsigned BE promotion ingest manifest (#617)
```

They are preserved as two commits deliberately. The ingest-manifest provenance
names `d52c0e68fed54d9cc98dde80c38a2da79087f491`; do not squash or rebase these
commits. The key holder must sign on top and fable must integrate with ancestry
preserved.

Prepared files:

- `manifests/releases/be-rulespec-2026-08-23.json`
- `.axiom/ingest-manifests/be/statute/2026-08-23-be-rulespec-source-promotion.json`
- `data/corpus/{provisions,inventory,coverage}/be/statute/2026-08-23-be-rulespec-source-promotion.*`
- all files under `data/corpus/sources/be/statute/2026-08-23-be-rulespec-source-promotion/inputs/`
- `tests/test_be_rulespec_2026_08_23_promotion.py`
- `changelog.d/be-rulespec-2026-08-23-release.added.md`

The historical migration manifest
`manifests/migrations/rulespec-be-source-promotion.json` is intentionally
unchanged: it is immutable provenance for the 2026-07-10 cut, not a reusable
successor-release selector.

## Selection and preservation evidence

This direct line count produced the old/new provision and CIR input-boundary
counts:

```bash
wc -l \
  data/corpus/provisions/be/statute/2026-07-10-be-rulespec-source-promotion.jsonl \
  data/corpus/provisions/be/statute/2026-08-23-be-rulespec-source-promotion.jsonl \
  data/corpus/sources/be/statute/2026-07-10-be-rulespec-source-promotion/inputs/axiom-corpus-9be12db7c693-2026-06-30-be-income-tax-consolidated.selected.jsonl \
  data/corpus/sources/be/statute/2026-08-23-be-rulespec-source-promotion/inputs/axiom-corpus-9be12db7c693-2026-06-30-be-income-tax-consolidated.selected.jsonl
```

```text
169  .../2026-07-10-be-rulespec-source-promotion.jsonl
184  .../2026-08-23-be-rulespec-source-promotion.jsonl
 37  .../2026-07-10-...income-tax-consolidated.selected.jsonl
 52  .../2026-08-23-...income-tax-consolidated.selected.jsonl
```

The regression command below verifies the exact selection, not just the
counts. It asserts that the old 169 rows become an exact 169-row subset after
changing only `version` and the version segment of `source_path`; that every
UTF-8 body byte is unchanged; that exactly the 11 required plus four
recommended pages are added from the tracked 2026-06-30 source; that those
added bodies are byte-identical; and that every parent exists. It also asserts
that the expanded 52-line CIR boundary is the exact raw-line union in original
source order, while the other ten input files remain byte-identical.

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" \
  /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python \
  -m pytest -q -p no:cacheprovider \
  tests/test_be_rulespec_2026_08_23_promotion.py
```

```text
5 passed in 0.84s
```

The same contract was also printed by a stdlib JSONL audit:

```text
old_rows=169 new_rows=184 added_rows=15
required_pages=11 recommended_pages=4 exact_added_set=True
old_transform_mismatches=0 old_body_byte_mismatches=0
added_transform_mismatches=0 added_body_byte_mismatches=0 missing_parents=0
cir_page_rows=67 old_boundary_rows=37 new_boundary_rows=52 exact_full_source_union=True
input_files=11 byte_identical_copied_inputs=10 copied_input_mismatches=0
inventory_items=184 missing_sources=0 source_sha_mismatches=0
release_scopes=13 changed_scopes=1 quality_profile=complete-expression-dates-v1
```

That output came from loading the three tracked provision JSONL files with
Python's `json` module, keying rows by `citation_path`, applying the exact
field transforms asserted in
`tests/test_be_rulespec_2026_08_23_promotion.py`, comparing `body.encode()`
bytes, hashing each inventory `source_path`, and comparing the two release
selectors by `(jurisdiction, document_class)`. The test command above is the
committed, rerunnable form of that audit.

No extra structural row was needed. All added rows name the already-selected
parent `be/statute/fisconetplus/cir92/revenus-2025`, whose stable ID is
`c5f9e915-a354-5b58-a3ac-f2b082f5029d`. The deep validator derives one
navigation node per provision.

Artifact bytes and hashes were produced by:

```bash
wc -l -c \
  data/corpus/sources/be/statute/2026-08-23-be-rulespec-source-promotion/inputs/axiom-corpus-9be12db7c693-2026-06-30-be-income-tax-consolidated.selected.jsonl \
  data/corpus/provisions/be/statute/2026-08-23-be-rulespec-source-promotion.jsonl
shasum -a 256 \
  data/corpus/sources/be/statute/2026-08-23-be-rulespec-source-promotion/inputs/axiom-corpus-9be12db7c693-2026-06-30-be-income-tax-consolidated.selected.jsonl \
  data/corpus/provisions/be/statute/2026-08-23-be-rulespec-source-promotion.jsonl \
  data/corpus/inventory/be/statute/2026-08-23-be-rulespec-source-promotion.json \
  data/corpus/coverage/be/statute/2026-08-23-be-rulespec-source-promotion.json
```

```text
52 lines, 257579 bytes  cd51b5039be2c043f736d902ffe410aaa06ee26d40d37a0362fb0830f83ea042  CIR selected boundary
184 lines, 1246121 bytes  72061a12dcba4c7a1bd11af0fb8149bf6f2aa585de4d7f7c6b24772c008061b1  provisions
8fe288caf18f25b9516c6b7a6801d0e43f6470127b2bb7c9118f1a9e411befd5  inventory
78641ad8e232f635690ec7907631848382b82be0d6c01fb738063d21ec118e39  coverage
```

The named selector has the same 13 scope pairs as the 2026-07-10 selector.
Only `be/statute` changes version; the other 12 scopes reuse their immutable
2026-07-10 versions. This is asserted by the focused test above and was also
printed by the selector comparison in the stdlib audit.

## Local validation

### Corpus/release gates that pass

Coverage command:

```bash
PYTHONPATH=src /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python \
  -m axiom_corpus.corpus.cli coverage \
  --base data/corpus \
  --source-inventory data/corpus/inventory/be/statute/2026-08-23-be-rulespec-source-promotion.json \
  --provisions data/corpus/provisions/be/statute/2026-08-23-be-rulespec-source-promotion.jsonl \
  --jurisdiction be --document-class statute \
  --version 2026-08-23-be-rulespec-source-promotion
```

Result: `complete=true`, with `source_count=184`,
`provision_count=184`, `matched_count=184`, and zero missing, extra, or
duplicate citations.

Strict deep release validation:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" \
  /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python \
  -m axiom_corpus.corpus.cli validate-release \
  --base data/corpus \
  --release manifests/releases/be-rulespec-2026-08-23.json \
  --strict-warnings --max-issues 200
```

Result: `ok=true`, `scope_count=13`, `issue_count=0`, `error_count=0`, and
`warning_count=0`.

Tracked-source check:

```bash
PYTHONPATH=src /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python \
  -m axiom_corpus.corpus.cli verify-scope-tracked \
  --repo . --jurisdiction be --document-class statute \
  --version 2026-08-23-be-rulespec-source-promotion
```

Result: `Verified 11 referenced files across 1 inventory scopes.`

Clean-tree, no-write publication planning at committed HEAD:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" \
  /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python \
  scripts/publish_corpus.py \
  --release manifests/releases/be-rulespec-2026-08-23.json \
  --repo-root . --base data/corpus --dry-run
```

```json
{
  "artifact_count": 94,
  "dry_run": true,
  "provision_rows": 641,
  "release": "be-rulespec-2026-08-23",
  "scope_count": 13
}
```

Release-focused tests:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" \
  /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python \
  -m pytest -q -p no:cacheprovider \
  tests/test_be_rulespec_2026_08_23_promotion.py \
  tests/test_rulespec_be_source_promotion.py \
  tests/test_corpus_release_quality.py \
  tests/test_release_manifest.py \
  tests/test_release_publication.py \
  tests/test_publish_corpus.py
```

Result: `172 passed in 50.27s`.

Sandbox-equivalent required checks used the existing project virtualenv because
the exact `uv run` commands cannot write the sandboxed user cache:

```bash
/Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/ruff check .
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" \
  /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/mypy \
  src/axiom_corpus/corpus --ignore-missing-imports \
  --cache-dir=/private/tmp/lane-c1-root-mypy-cache
/Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/towncrier check
```

Results: Ruff passed; mypy found no issues in 90 source files; Towncrier found
the new fragment and passed.

GitNexus impact was run before the new test symbols were added; each target was
absent, so there were no indexed upstream dependents to update. After refreshing
the local graph, the compare-to-`origin/main` change detector reported 18 files,
12 indexed file/test symbols, zero affected execution processes, and `low` risk.
The refresh parsed successfully but could not register globally because the
sandbox denied writes to `~/.gitnexus/registry.json`; a direct read of the new
local graph supplied the stated result.

### Failures and boundaries, reported flat

1. The required commands below all exited 2 before running their tool because
   `uv` could not open `/Users/maxghenis/.cache/uv/sdists-v9/.git` (`Operation
   not permitted`):

   ```bash
   uv run --extra dev ruff check .
   uv run --extra dev mypy src/axiom_corpus/corpus --ignore-missing-imports
   uv run --extra dev python -m pytest -q
   uv run --extra dev towncrier check
   uv run --extra dev axiom-corpus-ingest coverage ... --write
   ```

   The virtualenv commands above separate that one sandbox-cache mechanism from
   the actual validation results.

2. System Python could not import the validator: the coverage invocation failed
   with `ModuleNotFoundError: No module named '_cffi_backend'` through
   `cryptography`. The existing project virtualenv command then passed.

3. The full fallback suite was run as:

   ```bash
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/src" \
     /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python \
     -m pytest -q -p no:cacheprovider
   ```

   It finished with exactly one failure: `1 failed, 4256 passed, 75 skipped,
   208 deselected, 37 warnings in 314.28s`. The failing test is
   `tests/test_storage_postgres.py::TestPostgresStorageSubsectionConversion::test_dict_to_subsection`.
   Its named mechanism is a `MagicMock(spec=PostgresStorage)` recursive method
   call returning a `MagicMock` child, which Pydantic 2.12 rejects as
   `children.0`. This command proves both implicated files are unchanged by the
   lane:

   ```bash
   git diff --quiet origin/main...HEAD -- \
     src/axiom_corpus/storage/postgres.py tests/test_storage_postgres.py
   echo $?
   # 0
   ```

4. Before the inputs were force-added and committed, the publication dry-run
   failed because 15 required paths were not tracked: 14 scoped artifacts plus
   the selector. After explicit `git add -f`, two commits, and a clean checkout,
   the same planner passed with the result shown above.

5. The first ad hoc inventory audit used the wrong field name
   `source_sha256` and failed with `KeyError`; the canonical inventory field is
   `sha256`. The corrected audit produced zero missing sources and zero digest
   mismatches. A separate shell wrapper initially tried to assign zsh's
   read-only `status` variable; rerunning it with `rc` produced the unchanged-file
   result above. Neither invocation changed an artifact.

## Unsigned ingest-manifest TODO

The checked-in manifest is intentionally unsigned. This command produced its
current state:

```bash
python - <<'PY'
import json
from pathlib import Path
m=json.loads(Path('.axiom/ingest-manifests/be/statute/2026-08-23-be-rulespec-source-promotion.json').read_text())
print(f'applied_files={len(m["applied_files"])}')
print('coverage=' + '/'.join(str(m['coverage'][k]) for k in ('source_count','provision_count','matched_count')))
print(f'signature_present={"signature" in m}')
print(f'provenance_commit={m["axiom_corpus_git"]["commit"]}')
print(f'dirty_tracked={m["axiom_corpus_git"]["dirty_tracked"]}')
PY
```

```text
applied_files=14
coverage=184/184/184
signature_present=False
provenance_commit=d52c0e68fed54d9cc98dde80c38a2da79087f491
dirty_tracked=False
```

The exact signing attempt exited 2 with
`AXIOM_CORPUS_INGEST_PRIVATE_KEY is required to sign ingest manifests.` No
signature was fabricated. The local guard also exits 1 because
`AXIOM_CORPUS_INGEST_PUBLIC_KEY` is absent and lists the same 14 protected
files. With the org public key present, an unsigned manifest will still fail;
the key holder must regenerate and sign it from a clean checkout:

```bash
cd /path/to/axiom-corpus
test -z "$(git status --porcelain=v1 --untracked-files=all)"
: "${AXIOM_CORPUS_INGEST_PRIVATE_KEY:?missing org ingest-manifest signing key}"

uv run --extra dev axiom-corpus-ingest sign-ingest-manifest \
  --repo . \
  --base data/corpus \
  --jurisdiction be \
  --document-class statute \
  --version 2026-08-23-be-rulespec-source-promotion \
  --command "Build the 2026-08-23 RuleSpec-BE statute source promotion as the byte-preserving 2026-07-10 statute selection plus CIR92 pages 183, 188, 189, 190, 192, 252, 254, 257, 258, 268, 269, 270, 271, 272, and 275 from data/corpus/provisions/be/statute/2026-06-30-be-income-tax-consolidated.jsonl." \
  --output .axiom/ingest-manifests/be/statute/2026-08-23-be-rulespec-source-promotion.json

git add .axiom/ingest-manifests/be/statute/2026-08-23-be-rulespec-source-promotion.json
git commit -m "Sign BE RuleSpec 2026-08-23 ingest manifest (#617)"
uv run --extra dev axiom-corpus-ingest guard-ingested \
  --repo . --base-ref origin/main --head-ref HEAD --json
```

Do not squash or rebase after signing: the signed generator commit must remain
an ancestor of the guarded/published head.

## Publish, public-mirror, activation, and RuleSpec re-pin

`publish.yml` auto-runs when the new selector lands on `main`. Use this one
command only if that push-triggered run was not created; do not double-dispatch:

```bash
REPO=TheAxiomFoundation/axiom-corpus
RELEASE=be-rulespec-2026-08-23
gh workflow run publish.yml --repo "$REPO" --ref main -f release="$RELEASE"
```

Publication requires the org R2, Supabase, and release-signing credentials. It
stages and signs the immutable release object but does not activate serving and
does not copy the object to the public bucket used by RuleSpec CI.

Capture the successful publish run and its two downstream identities:

```bash
PUBLISH_RUN_ID=<successful-publish-run-id>
gh run watch "$PUBLISH_RUN_ID" --repo "$REPO" --exit-status

PUB_TMP="$(mktemp -d)"
gh run download "$PUBLISH_RUN_ID" --repo "$REPO" \
  -n signed-corpus-release-object -D "$PUB_TMP"
RELEASE_OBJECT="$PUB_TMP/be-rulespec-2026-08-23-release-object.json"
test -f "$RELEASE_OBJECT"

CONTENT_SHA="$(python3 - "$RELEASE_OBJECT" "$RELEASE" <<'PY'
import json, re, sys
p=json.load(open(sys.argv[1], encoding='utf-8'))
if p.get('release') != sys.argv[2]: raise SystemExit('release name mismatch')
sha=p.get('content_sha256', '')
if re.fullmatch(r'[0-9a-f]{64}', sha) is None: raise SystemExit('invalid content_sha256')
print(sha)
PY
)"
CORPUS_PROVENANCE_SHA="$(python3 - "$RELEASE_OBJECT" <<'PY'
import json, re, sys
sha=json.load(open(sys.argv[1], encoding='utf-8'))['content']['git']['commit']
if re.fullmatch(r'[0-9a-f]{40}', sha) is None: raise SystemExit('invalid corpus provenance commit')
print(sha)
PY
)"
printf 'PUBLISH_RUN_ID=%s\nCONTENT_SHA=%s\nCORPUS_PROVENANCE_SHA=%s\n' \
  "$PUBLISH_RUN_ID" "$CONTENT_SHA" "$CORPUS_PROVENANCE_SHA"
```

The content SHA cannot be known honestly before publication: it binds the
final committed Git identity plus R2 readback and Supabase projection evidence.

Public mirror — required before RuleSpec re-pin/CI:

```bash
gh workflow run mirror-release.yml --repo "$REPO" --ref main \
  -f publish_run_id="$PUBLISH_RUN_ID" \
  -f release="$RELEASE" \
  -f content-sha256="$CONTENT_SHA"
```

Approve/watch the protected `release-mirror` environment and require its public
probe to pass. The input name here is `content-sha256` with a hyphen.

Activation is a separate serving-state decision. Preview first, inspect all
scope takeovers, then request the protected mutation:

```bash
gh workflow run activate-release.yml --repo "$REPO" --ref main \
  -f publish_run_id="$PUBLISH_RUN_ID" -f release="$RELEASE" \
  -f content_sha="$CONTENT_SHA" -f allow_regression=false \
  -f request_activation=false

gh workflow run activate-release.yml --repo "$REPO" --ref main \
  -f publish_run_id="$PUBLISH_RUN_ID" -f release="$RELEASE" \
  -f content_sha="$CONTENT_SHA" -f allow_regression=false \
  -f request_activation=true
```

The activation input is `content_sha` with an underscore.

After the public-mirror probe passes, re-pin the RuleSpec ledger tree. Two files
must change: the release identity in `.axiom/toolchain.toml`, and the checked-out
corpus commit in `.github/workflows/repository-checks.yml`. The latter must not
predate the signed object's provenance commit.

```bash
RULESPEC=/path/to/rulespec-be
cd "$RULESPEC"

AXIOM_NEW_RELEASE="$RELEASE" AXIOM_NEW_RELEASE_SHA="$CONTENT_SHA" \
perl -0pi -e '
  s/^axiom_corpus_release = ".*"$/axiom_corpus_release = "$ENV{AXIOM_NEW_RELEASE}"/m;
  s/^axiom_corpus_release_content_sha256 = "[0-9a-f]{64}"$/axiom_corpus_release_content_sha256 = "$ENV{AXIOM_NEW_RELEASE_SHA}"/m;
' .axiom/toolchain.toml

AXIOM_NEW_CORPUS_REF="$CORPUS_PROVENANCE_SHA" perl -0pi -e '
  s/^([ \t]*axiom-corpus-ref:[ \t]*)[0-9a-f]{40}[ \t]*$/$1$ENV{AXIOM_NEW_CORPUS_REF}/m;
' .github/workflows/repository-checks.yml

test "$(shasum -a 256 known-validation-gaps.yaml | cut -d ' ' -f 1)" = \
  258a1b9eae033e2e3cff6982bccc596d755bc5e0094b6d51eba5841f532bed25
git diff --check
git diff -- .axiom/toolchain.toml .github/workflows/repository-checks.yml
```

Expected toolchain values after re-pin:

```toml
axiom_corpus_release = "be-rulespec-2026-08-23"
axiom_corpus_release_content_sha256 = "<CONTENT_SHA from signed publish artifact>"
validation_waiver_set_sha256 = "258a1b9eae033e2e3cff6982bccc596d755bc5e0094b6d51eba5841f532bed25"
```

The waiver digest is unchanged. The command that produced its current value was:

```bash
shasum -a 256 /Users/maxghenis/TheAxiomFoundation/_cape-prep/beI/rulespec-be/known-validation-gaps.yaml
# 258a1b9eae033e2e3cff6982bccc596d755bc5e0094b6d51eba5841f532bed25
```

## RuleSpec frontier resolution dry-run

Authenticated CI resolution cannot run before the signed object exists in the
public mirror and the two RuleSpec pins above are changed. The exact remaining
mechanism is therefore three-boundary, not a corpus-row residual: no published
content SHA, no org-signed/public release object, and the current workflow still
checks out corpus commit `644ee891c69b4632b0ce48d5432a6104df255571`.

The pre-publication static dry-run scanned both the current ledger tree and the
held dependants tree, loaded the new selected provisions, and required every
quoted proof excerpt to be a byte substring of its selected body:

```bash
PYTHONDONTWRITEBYTECODE=1 \
  /Users/maxghenis/TheAxiomFoundation/axiom-corpus/.venv/bin/python - <<'PY'
import json
from pathlib import Path
import yaml
corpus=Path('/Users/maxghenis/TheAxiomFoundation/_cape-prep/corpus-promo/data/corpus/provisions/be/statute/2026-08-23-be-rulespec-source-promotion.jsonl')
roots=[Path('/Users/maxghenis/TheAxiomFoundation/_cape-prep/beF/rulespec-be'), Path('/Users/maxghenis/TheAxiomFoundation/_cape-prep/beI/rulespec-be')]
expected={f'be/statute/fisconetplus/cir92/revenus-2025/page-{n}' for n in (183,188,189,190,192,268,269,270,271,272,275)}
rows={r['citation_path']:r for line in corpus.read_text().splitlines() if line for r in [json.loads(line)]}
cited=set(); anchors=[]
def walk(v):
    if isinstance(v,dict):
        c=v.get('corpus_citation_path')
        if c in expected:
            cited.add(c)
            if isinstance(v.get('excerpt'),str): anchors.append((c,v['excerpt']))
        for x in v.values(): walk(x)
    elif isinstance(v,list):
        for x in v: walk(x)
for root in roots:
    for path in root.rglob('*.yaml'): walk(yaml.safe_load(path.read_text()))
misses=[(c,e) for c,e in anchors if e not in rows[c]['body']]
print(f'expected={len(expected)} cited={len(cited)} corpus_rows={sum(c in rows for c in expected)} anchors={len(anchors)} anchor_misses={len(misses)}')
for c in sorted(cited,key=lambda x:int(x.rsplit('-',1)[1])): print(c)
if cited != expected or not expected <= rows.keys() or misses: raise SystemExit(1)
PY
```

```text
expected=11 cited=11 corpus_rows=11 anchors=45 anchor_misses=0
be/statute/fisconetplus/cir92/revenus-2025/page-183
be/statute/fisconetplus/cir92/revenus-2025/page-188
be/statute/fisconetplus/cir92/revenus-2025/page-189
be/statute/fisconetplus/cir92/revenus-2025/page-190
be/statute/fisconetplus/cir92/revenus-2025/page-192
be/statute/fisconetplus/cir92/revenus-2025/page-268
be/statute/fisconetplus/cir92/revenus-2025/page-269
be/statute/fisconetplus/cir92/revenus-2025/page-270
be/statute/fisconetplus/cir92/revenus-2025/page-271
be/statute/fisconetplus/cir92/revenus-2025/page-272
be/statute/fisconetplus/cir92/revenus-2025/page-275
```

These are exact child rows in the new `be/statute` scope, so CI will resolve
them directly rather than slicing page text from the structural parent. The
parent remains present for fail-closed navigation and descendant checks.

LANE C1 DONE
