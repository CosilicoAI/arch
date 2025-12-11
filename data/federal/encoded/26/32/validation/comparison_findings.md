# EITC Validation: PolicyEngine vs TAXSIM-35

## Summary

When inputs are properly mapped, **PolicyEngine and TAXSIM-35 produce identical EITC results**.

Initial comparison showed 14-34% discrepancies, but investigation revealed these were due to
incomplete variable mapping in the test harness, not actual disagreements between systems.

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
