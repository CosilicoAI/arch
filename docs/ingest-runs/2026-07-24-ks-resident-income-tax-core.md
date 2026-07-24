# Kansas 2026 resident individual income-tax core

This scope preserves current official Kansas Revisor primary authority for a
tax-year-2026 full-year-resident individual income-tax pipeline. It includes
the resident definition, tax schedules and annual rate-reduction mechanism,
Kansas adjusted gross and taxable income, standard and itemized deductions,
both official personal-exemption amendment versions, the resident credit for
tax paid to another state, the refundable earned-income credit, and the
refundable pass-through-entity credit.

The scope also retains enacted 2026 Senate Bill 82. Its first section creates
a nonrefundable credit, with carryforward, for a resident individual's
qualifying lockable gun and ammunition storage expenditures in tax years 2026
through 2028.

Both official versions of the multiply amended exemption section are retained.
RuleSpec consumers must fail closed for branches where the versions differ;
the source set does not silently reconcile those texts. Likewise, this focused
scope does not claim that every specialty credit in Kansas law is captured or
that the unavailable 2026 Form K-40 and its ordering instructions have been
published.

Artifacts are generated without publication or database loading:

```bash
uv run --extra dev axiom-corpus-ingest extract-official-documents \
  --base data/corpus \
  --version 2026-07-24-ks-resident-income-tax-core \
  --manifest manifests/us-ks-2026-resident-income-tax-core.yaml
```
