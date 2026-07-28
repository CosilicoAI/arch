# Illinois 35 ILCS 200 Article 15 ingest

## Scope

- Jurisdiction: `us-il`
- Document class: `statute`
- Declared scope: `35 ILCS 200`, Article 15 only
- Source as of: `2026-07-27`
- Expression date: `2026-07-27`
- Fetched at: `2026-07-27`

This is an Article 15 slice, not the whole Property Tax Code. The staged source
contains the Article 15 heading and 54 unique section tables, from
`35 ILCS 200/15-5` through `35 ILCS 200/15-185`. All 54 sections are
represented, together with the chapter and act containers. No section outside
Article 15 is declared or ingested.

## Official source

- Source URL:
  `https://www.ilga.gov/legislation/ILCS/details?MajorTopic=&Chapter=&ActName=Property%20Tax%20Code.&ActID=596&ChapterID=8&ChapAct=35+ILCS+200%2F&SeqStart=38400000&SeqEnd=43899999&Print=True`
- Snapshot:
  `data/corpus/sources/us-il/statute/2026-07-27-ilcs-35-200-article-15/illinois-ilcs/35-ilcs-200-art15.html`
- SHA-256:
  `64eb4f69ac8741242ce2a61ce2ca300a816d182ed59b52672723ffad8efcf6a8`

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

The resulting scope contains 56 records: one chapter, one act, and 54
Article 15 sections. It includes `15-172`.

