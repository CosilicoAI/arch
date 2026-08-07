# ELI adapter

`extract-eli-documents` ingests acts exposed through the European Legislation
Identifier (ELI) model. Denmark's official `retsinformation.dk` service is the
phase-1 reference host.

The adapter reads the ELI `LegalResource`, `LegalExpression`, and `Format`
nodes. It records `in_force`, `consolidated_by`, `changed_by`, `consolidates`,
`title`, `title_short`, `title_alternative`, `date_document`,
`responsibility_of`, and XML/HTML/PDF manifestation URLs and their
`legal_value`. These graph facts are copied into every normalized provision's
metadata as the mechanical amendment-diligence trail.

Before downloading the structured text, the currency gate refuses an act when
`in_force` is `notInForce` or `consolidated_by` names a successor. Use
`--allow-superseded` only for an intentional historical ingest.

For Denmark, LexDania `Dokument/DokumentIndhold` XML is mapped one `Paragraf`
per level-2 corpus provision. `Paragraf@localId` supplies the paragraph number,
including letter suffixes such as `1a`; `Explicatus` supplies the displayed
section label; and child `Stk` elements are concatenated in document order.
The surrounding `Afsnit` and `Kapitel` `localId` and `Explicatus` values are
retained as block metadata. The manifest's citation path is the root document
path and section paths append citation-safe labels such as `paragraf-1-a`.

Paragraph labels are resolved after every `Paragraf` in an act has been built.
Labels that occur once retain that exact shape. When a paragraph label repeats,
every instance is prefixed by its outer-to-inner structural chain: numbered
`Afsnit` and `Kapitel` components produce labels such as
`afsnit-2-kapitel-4-paragraf-29`, while a paragraph in an `Ikraft` block uses a
label such as `ikraft-paragraf-29`. Amendment acts also use the literal
`AendringCentreretParagraf` wrapper's `localId` as a structural component, for
example `aendringcentreretparagraf-6-paragraf-22-a`. If those structural labels
are still not unique (for example, two paragraph 29 elements in the same afsnit
and chapter), extraction fails instead of dropping a provision or adding an
ordinal suffix.

Phase 1 supports structured XML extraction. Entries requesting PDF, or graphs
without an XML manifestation, receive an error directing them to
`extract-official-documents`, which remains the PDF fallback. A Belgium/Justel
host profile is future work; the existing Belgian adapter handles its current
HTML-specific workflow.
