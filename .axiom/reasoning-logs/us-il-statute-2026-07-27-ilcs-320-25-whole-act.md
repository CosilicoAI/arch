# Illinois 320 ILCS 25 whole-act ingest

## Scope

- Jurisdiction: `us-il`
- Document class: `statute`
- Declared scope: all of `320 ILCS 25`
- Source as of: `2026-07-27`
- Expression date: `2026-07-27`
- Fetched at: `2026-07-27`

This scope is the whole Senior Citizens and Persons with Disabilities Property
Tax Relief Act. The staged source contains 40 unique section tables, from
`320 ILCS 25/1` through `320 ILCS 25/13`; all 40 are represented, together
with the chapter and act containers.

## Official source

- Source URL:
  `https://www.ilga.gov/Legislation/ILCS/Articles?ActID=1453&ChapterID=31&Chapter=AGING&MajorTopic=HUMAN%20NEEDS`
- Snapshot:
  `data/corpus/sources/us-il/statute/2026-07-27-ilcs-320-25-whole-act/illinois-ilcs/320-ilcs-25-full.html`
- SHA-256:
  `62b418b2f877c41b6b71ebb58ea52f3708dedac9762e341653fed76f23370a6c`

The official aggregate HTML was staged outside the repository after retrieval
from ILGA. It is retained byte-for-byte as the source snapshot. Statutory text
was produced only by stripping HTML markup and normalizing the markup's
whitespace through the existing Illinois `_html_text` routine.

## Extraction

The existing local Illinois command accepts only one-section FTP-style files,
so it cannot accurately consume this aggregate whole-act page. The records
were constructed locally with the repository's `CorpusArtifactStore`,
`SourceInventoryItem`, `ProvisionRecord`, Illinois text helpers, deterministic
provision IDs, and coverage comparator. No network source or secondary text was
used.

The resulting scope contains 42 records: one chapter, one act, and 40
sections. It includes `3.05`, `3.05a`, `3.06`, and `3.07`.

