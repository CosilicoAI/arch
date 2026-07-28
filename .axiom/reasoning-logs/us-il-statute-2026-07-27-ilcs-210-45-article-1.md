# Illinois 210 ILCS 45 Article I ingest

## Scope

- Jurisdiction: `us-il`
- Document class: `statute`
- Declared scope: `210 ILCS 45`, Article I only
- Source as of: `2026-07-27`
- Expression date: `2026-07-27`
- Fetched at: `2026-07-27`

This is an Article I slice, not the whole Nursing Home Care Act. The staged
source contains the Article I heading and 39 unique section tables, from
`210 ILCS 45/1-101` through `210 ILCS 45/1-132`. All 39 sections are
represented, together with the chapter and act containers. The following
Article II heading is treated only as the end boundary; no Article II section
is declared or ingested.

## Official source

- Source URL:
  `https://www.ilga.gov/legislation/ILCS/details?MajorTopic=&Chapter=&ActName=Nursing+Home+Care+Act.&ActID=1225&ChapterID=21&ChapAct=210+ILCS+45%2F&SeqStart=100000&SeqEnd=4200000&Print=True`
- Snapshot:
  `data/corpus/sources/us-il/statute/2026-07-27-ilcs-210-45-article-1/illinois-ilcs/210-ilcs-45-art1.html`
- SHA-256:
  `f7642bde9e15719659721ba7242d5fd34b1a04d9ca18ef39556368a5caa659c8`

The official aggregate HTML was staged outside the repository after retrieval
from ILGA. It is retained byte-for-byte as the source snapshot. Statutory text
was produced only by stripping HTML markup and normalizing the markup's
whitespace through the existing Illinois `_html_text` routine.

## Extraction

The existing local Illinois command accepts only one-section FTP-style files,
so it cannot accurately consume this aggregate article page. The records were
constructed locally with the repository's `CorpusArtifactStore`,
`SourceInventoryItem`, `ProvisionRecord`, Illinois text helpers, deterministic
provision IDs, and coverage comparator. No network source or secondary text was
used.

The official `1-113` table contains two explicitly labeled text variants. The
record includes the complete block labeled
`(Text of Section from P.A. 104-147)` through
`(Source: P.A. 104-147, eff. 8-1-25.)` and excludes the following P.A. 104-234
variant, as required.

The resulting scope contains 41 records: one chapter, one act, and 39
Article I sections. It includes `1-113`.

