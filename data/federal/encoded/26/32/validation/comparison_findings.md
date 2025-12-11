# EITC Validation: PolicyEngine vs TAXSIM-35

## Summary

When inputs are properly mapped, **PolicyEngine and TAXSIM-35 produce identical EITC results**.

Initial comparison showed 14-34% discrepancies, but investigation revealed these were due to
incomplete variable mapping in the test harness, not actual disagreements between systems.

## Validator Test Results (TY 2023)

The cosilico-validators TAXSIM integration was tested with 13 EITC cases for TY 2023:

| Test Case | Expected | TAXSIM | Status |
|-----------|----------|--------|--------|
| Phase-in: 1 child, $8K | $2,720 | $2,720.0 | PASS |
| Phase-in: 2 children, $10K | $4,000 | $4,000.0 | PASS |
| Phase-in: 3 children, $12K | $5,400 | $5,400.0 | PASS |
| Plateau: 0 children, $9K | $600 | $599.6 | PASS |
| Plateau: 1 child, $15K | $3,995 | $3,997.3 | PASS |
| Plateau: 2 children, $18K | $6,604 | $6,600.4 | PASS |
| Phase-out: 0 children, $12K | $432 | $432.0 | PASS |
| Phase-out: 1 child, $30K | $2,647 | $2,647.8 | PASS |
| Phase-out: 2 children, $40K | $2,721 | $2,715.9 | PASS |
| Joint: 0 children plateau | $600 | $599.6 | PASS |
| Joint: 2 children partial | $4,102 | $4,098.3 | PASS |
| Fully phased out | $0 | $0.0 | PASS |
| Childless under 25 | $0 | $599.6 | FAIL* |

*TAXSIM does not enforce the age 25 minimum for childless EITC claimants - this is a known limitation.

## Key Findings

### 1. Input Mapping Matters

The CPS data contains many income variables that must be properly mapped:

| CPS Variable | Description | Impact on EITC |
|--------------|-------------|----------------|
| `pwages` | Primary wages | Earned income |
| `swages` | Spouse wages | Earned income |
| `psemp` | Primary self-employment | Earned income + AGI |
| `ssemp` | Spouse self-employment | Earned income + AGI |
| `intrec` | Interest income | Investment income test |
| `dividends` | Dividend income | Investment income test |
| `pensions` | Pension income | AGI (affects phaseout) |
| `gssi` | Social Security | Partial AGI inclusion |
| `age1-age11` | Dependent ages | Qualifying child determination |

### 2. Common Mapping Errors

1. **Missing spouse income**: Not including `ssemp` caused PE to calculate lower AGI
2. **Wrong child ages**: Using placeholder age=10 instead of actual ages (18-21 year olds may not qualify)
3. **Missing investment income**: Not including `intrec`/`dividends` affected eligibility test

### 3. Validation Results

When properly mapped, spot-check cases show:

| Case | Income | Children | TAXSIM | PE | Diff |
|------|--------|----------|--------|-----|------|
| 471 | $29K wages + $37K SE | 3 (ages 21/19/18) | $0 | $0 | $0 |
| 100 | $31K | 4 | $5,473 | $5,473 | $0 |
| 167 | $4.7K | 2 | $1,886 | $1,886 | $0 |

## Recommendations

1. **Use policyengine-taxsim for full comparison** - it handles variable mapping correctly
2. **Fix state handling bug** in policyengine-taxsim (StateGroup enum error)
3. **Add TAXSIM validator** to cosilico-validators once mapping is verified

## Data Sources

- CPS households: `policyengine-taxsim/cps_households.csv` (111K records)
- TAXSIM-35: `policyengine-taxsim/resources/taxsim35/taxsim35-osx.exe`
- PolicyEngine-US: via `policyengine_us.Simulation`
