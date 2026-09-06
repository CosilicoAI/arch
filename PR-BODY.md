# il: Israel statute ingest (Income Tax Ordinance + National Insurance Law) — pilot

Bounded Israel pilot scope for supervised RuleSpec-IL encoding. **Merge commit only** —
this PR carries an ingest manifest; squashing or rebasing breaks the attested ancestry.

## Documents

| instrument | Knesset IsraelLawID | sections | schedule items | navigation nodes | rows |
|---|---|---|---|---|---|
| פקודת מס הכנסה [נוסח חדש] — Income Tax Ordinance [New Version] | 2000944 | 548 | 0 | 88 (16 parts, 41 chapters, 31 signs) | 637 |
| חוק הביטוח הלאומי [נוסח משולב], התשנ״ה–1995 — National Insurance Law [Consolidated Version] | 2000198 | 561 | 30 | 136 (0 parts, 22 chapters, 88 signs, 26 schedules) | 728 |
| **total** | | **1,109** | **30** | **224** | **1,365** |

Coverage 1,365/1,365, complete. Scope `il/statute`, version `2026-09-06-il-taxben-pilot`.

## Sources, and the tier caveat

Both instruments come from the ספר החוקים הפתוח (OpenLaw) consolidation on
he.wikisource.org — the page the Knesset National Legislation Database itself links to
as "לחוק המלא", because the Knesset's own consolidated full text is behind a
client-rendered SharePoint app that returns a JavaScript shell to a plain fetch.

| file | url | sha256 | retrieved |
|---|---|---|---|
| `ito-wikisource.html` | https://he.wikisource.org/wiki/פקודת_מס_הכנסה | `87535c2b8cd8aa50b27d32301dc2ddd768390ef64e9fb4f391c3e65fe99dc228` | 2026-09-06T11:41:55Z |
| `nii-law-wikisource.html` | https://he.wikisource.org/wiki/חוק_הביטוח_הלאומי | `7dbaaa757912c71b361381640d2578bf2c6ab52f2002817b85d677c2267f0715` | 2026-09-06T11:41:55Z |

**This is a secondary consolidation, not an official gazette text.** `AGENTS.md` prefers
primary official government sources; this scope is the explicitly directed non-canonical
experiment for the Israel pilot, and it says so on every row (`metadata.source_tier`).
The two acts declare **different** tiers, because the evidence differs: the Knesset
database's "לחוק המלא" link was followed to the Wikisource page for the Ordinance
(`consolidation-knesset-linked`), and that check is still pending for the National
Insurance Law (`consolidation-wikisource`). Israeli Copyright Act 5768-2007 §6
places no copyright in statutes; the OpenLaw project's *editorial* layer is CC BY-SA and is
deliberately excluded from provision bodies (see below), so only the statutory text is stored.

`expression_date` is **not** taken from the page. It comes from the Knesset registry — OData
`KNS_IsraelLaw.LatestPublicationDate`, queried 2026-09-06: 2026-06-08 for IsraelLawID 2000944
and 2026-06-15 for 2000198, both `LawValidityDesc` תקף. The basis string is recorded on every
row as `metadata.expression_date_basis`.

## Adapter

`src/axiom_corpus/corpus/israel_openlaw.py`, CLI `extract-il-openlaw`, modelled on the
Armenia ARLIS adapter: manifest-pinned, hash-verified, fully parsed and count-checked before
the first artifact is written.

The OpenLaw pages are anchor-structured, so the parser is anchor-driven rather than
line-regex driven. That is what makes it safe on Israeli section numbering:

- **Sub-item anchors fold, they do not split.** `div.law-number` with `id="סעיף_2"` opens
  §2; the same class with a *dotted* id (`סעיף_2.1`) is a sub-item whose text belongs to §2.
  The Ordinance has 106 of them. An in-text cross-reference such as
  "יהא משתלם לפי סעיף 121ב" never opens a section, because it is not an anchor.
- **Hebrew suffixes transliterate by enumeration ordinal (gematria), not letter position.**
  121ב → `section-121b`, 66א → `section-66a`, 103יא → `section-103k`, 103כ → `section-103t`.
  A letter-position mapping would collide כ with יא on four real sections (ITO §103, §195;
  NII §179) and ל with יב on one. Ordinals past 26 continue in bijective base-26, which the
  National Insurance Law needs: 179לד → `section-179ah`. Interleaved arabic runs pass
  through: 64א7ב → `section-64a7b`, 75טז1 → `section-75p1`.
- **`span.law-note` is editorial apparatus everywhere.** Amendment-history brackets
  (`[תיקון: …]`), editorial parentheticals, cross-reference notes, and the 2019–2027
  comparison table OpenLaw prints under §121 are all kept out of provision bodies and
  preserved in `metadata` (`amendment_history`, `editorial_notes`).
- **A note-only block that is the section's own status line** — (בוטל), (פקע), (נמחק) —
  becomes the body, with `metadata.operative = false`. 111 rows.
- **Identity is verified against the page**: the `h1.law-title` must equal the manifest
  title and the page's header line must open with the manifest's IsraelLawID.
- Text is NFC throughout; `language: he` on every row.

Citation paths follow `ops/il-lane/CITATION-SCHEME.md`: sections are flat
(`il/statute/income-tax-ordinance/section-121`) with nested navigation parents
(`…/part-7/chapter-1`), matching the ARLIS precedent. Two documented extensions, flagged
rather than assumed: suffix ordinals past 26 (bijective base-26), and schedules as
`…/schedule-<ident>/item-<ident>`.

## Two independent checks of the captured text against the official gazette

Neither is part of the scope; both are evidence that the consolidation is faithful where
the pilot leans on it hardest.

1. **§120ב(ה), the 2025–2027 indexation freeze.** Amendment 276 (ספר החוקים 3342,
   26.12.2024) inserted it. The captured §120ב body carries it verbatim — "ב־1 בינואר של
   שנות המס 2025 עד 2027 לא יתואמו הסכומים… והסכומים באותן שנות מס יהיו כפי שהיו ביום
   כ׳ בטבת התשפ״ד (1 בינואר 2024)…".
2. **§121's 2026 bracket edges.** Amendment 288, chapter ג' of the 2026 Economic
   Efficiency Law (ספר החוקים 3511 p.415, 31.03.2026), replaces §121(א)(1) with 301,200,
   §121(א)(2) with "מ־301,201… עד 560,280… – 35%", §121(ב)(1)(ג) with "…עד 228,000
   שקלים חדשים –", and §121(ב)(1)(ד) with "מ־228,001… עד 301,200… – 31%", effective
   1 January 2026. Those are exactly the edges in the captured §121 body.

Together they answer a question the pilot brief left open — whether the 20%/31% bands
widened for 2026 or were frozen. Both: §120ב(ה) freezes *indexation* for 2025–2027, and
the 2026 budget law amended the *statutory amounts* directly, with §7 of that chapter
splicing the new amounts into the frozen baseline. The corpus scope stores the
consolidated §121 and §120ב text; it does not itself assert that reconciliation.

## Spot checks (all green)

- §121 (שיעור המס ליחיד) carries 10/14/20/31/35/47 and the captured bracket edges
  84,120 / 120,720 / 228,000 / 301,200 / 560,280 — and **excludes** the editorial
  history table, which is recorded in metadata instead.
- §34 reads "…יובאו בחשבון שתי נקודות זיכוי" — **two** credit points; §36 adds the
  ¼ travel point, rendered inline as `1⁄4`. (The TaxBEN 2.25 is 2 + ¼, not a §34 figure.)
- §121ב present (3% surtax); NII §65, §66, §335 present; NII §66 still cites
  "סעיף 121ב לפקודת מס הכנסה", so the two instruments share one slug convention.
- Citation paths unique; no row with an empty body; `source_as_of`, `expression_date`
  and `language: he` populated on every row; every parent resolves inside the scope.

## Known limits

- Statute text only. No regulations, no Tax Authority / National Insurance Institute
  amount publications, no gazette-verified amendment history. Current-year regulated
  amounts must not be taken from this scope.
- NII §283 is printed twice by OpenLaw — the operative text and a version conditioned on
  publication of the 2026 budget law. Both land, as `section-283` and `section-283-alt2`,
  declared in the manifest so an *undeclared* duplicate anchor stays a hard error. This
  PR does not decide which is in force.
- OpenLaw prints "57א" against the anchor `סעיף_57ג`; the anchor wins and
  `metadata.printed_label_mismatch` records the disagreement.

## Release-cut plan

`manifests/releases/il-rulespec-2026-09-06.json`, one scope, quality profile
`complete-expression-dates-v1`. `validate-release` reports 0 issues, 0 warnings.
The plan is a cut plan only — publication and activation are separate, deliberate steps
and are not part of this PR.

## Manifest is UNSIGNED

`.axiom/ingest-manifests/il/statute/2026-09-06-il-taxben-pilot.json` is committed **without
a `signature` key**, attesting commit `02a78529`. The CI step "Guard generated corpus
artifacts" will fail with `Missing ingest manifest signature.` until it is signed from a
clean root checkout. That signing is deliberately out of this lane's hands.

## Checks

- `uv run --extra dev python -m pytest tests/test_israel_openlaw.py -q` — 55 passed.
- `uv run --extra dev ruff check .` — pass.
- `uv run --extra dev mypy src/axiom_corpus/corpus --ignore-missing-imports` — clean.
- `uv run --extra dev towncrier check` — pass.
- `axiom-corpus-ingest coverage …` — 1,365/1,365 complete.
- `axiom-corpus-ingest validate-release …` — ok.
