"""
Compare PolicyEngine vs TAXSIM-35 EITC calculations.

Uses CPS households from policyengine-taxsim repo.
"""

import pandas as pd
import numpy as np
import subprocess
import tempfile
from pathlib import Path
from policyengine_us import Simulation

POLICYENGINE_TAXSIM_DIR = Path.home() / "PolicyEngine" / "policyengine-taxsim"
TAXSIM_EXE = POLICYENGINE_TAXSIM_DIR / "resources" / "taxsim35" / "taxsim35-osx.exe"


def run_taxsim(df: pd.DataFrame) -> pd.DataFrame:
    """Run TAXSIM-35 on input DataFrame."""
    df = df.copy()
    df["idtl"] = 2  # Full output (includes EITC as v25)

    taxsim_cols = [
        "taxsimid", "year", "state", "mstat", "page", "sage", "depx",
        "pwages", "psemp", "swages", "ssemp", "dividends", "intrec",
        "stcg", "ltcg", "otherprop", "nonprop", "pensions", "gssi",
        "pui", "sui", "transfers", "rentpaid", "proptax", "otheritem",
        "childcare", "mortgage", "scorp", "idtl"
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        df[taxsim_cols].fillna(0).to_csv(f, index=False)
        input_file = f.name

    result = subprocess.run(
        [str(TAXSIM_EXE)],
        stdin=open(input_file),
        capture_output=True,
        text=True
    )

    return pd.read_csv(pd.io.common.StringIO(result.stdout))


def run_policyengine(df: pd.DataFrame, year: int = 2021) -> pd.DataFrame:
    """Run PolicyEngine on input DataFrame."""
    results = []

    for _, row in df.iterrows():
        pwages = float(row["pwages"] or 0)
        swages = float(row["swages"] or 0)
        depx = int(row["depx"] or 0)
        mstat = int(row["mstat"])
        page = int(row["page"] or 40)
        sage = int(row["sage"] or 0) if mstat == 2 else 0

        situation = {
            "people": {
                "adult": {
                    "age": {str(year): page},
                    "employment_income": {str(year): pwages},
                }
            },
            "tax_units": {
                "tu": {
                    "members": ["adult"],
                    "filing_status": {str(year): "JOINT" if mstat == 2 else "SINGLE"},
                }
            },
            "households": {
                "h": {"members": ["adult"], "state_code": {str(year): "CA"}}
            }
        }

        if mstat == 2:
            situation["people"]["spouse"] = {
                "age": {str(year): sage if sage > 0 else page},
                "employment_income": {str(year): swages},
            }
            situation["tax_units"]["tu"]["members"].append("spouse")
            situation["households"]["h"]["members"].append("spouse")

        for i in range(min(depx, 5)):
            child = f"c{i}"
            situation["people"][child] = {
                "age": {str(year): 10},
                "is_tax_unit_dependent": {str(year): True},
            }
            situation["tax_units"]["tu"]["members"].append(child)
            situation["households"]["h"]["members"].append(child)

        try:
            sim = Simulation(situation=situation)
            pe_eitc = round(sim.calculate("eitc", year)[0])
        except Exception as e:
            pe_eitc = None

        results.append({"taxsimid": row["taxsimid"], "pe_eitc": pe_eitc})

    return pd.DataFrame(results)


def compare_eitc(sample_size: int = 500, year: int = 2021) -> pd.DataFrame:
    """Run comparison and return merged results."""
    # Load CPS data
    cps_path = POLICYENGINE_TAXSIM_DIR / "cps_households.csv"
    df = pd.read_csv(cps_path)

    # Filter EITC-eligible
    sample = df[
        (df["pwages"] + df["swages"] > 0) &
        (df["pwages"] + df["swages"] < 60000) &
        (df["year"] == year)
    ].head(sample_size).copy()

    print(f"Running comparison on {len(sample)} households...")

    # Run both systems
    taxsim_df = run_taxsim(sample)
    pe_df = run_policyengine(sample, year)

    # Merge results
    merged = pd.merge(
        sample[["taxsimid", "pwages", "swages", "depx", "mstat", "page", "sage"]],
        taxsim_df[["taxsimid", "v25"]].rename(columns={"v25": "taxsim_eitc"}),
        on="taxsimid"
    ).merge(pe_df, on="taxsimid")

    merged["income"] = merged["pwages"] + merged["swages"]
    merged["diff"] = merged["pe_eitc"] - merged["taxsim_eitc"]
    merged["abs_diff"] = abs(merged["diff"])

    return merged


def print_summary(merged: pd.DataFrame):
    """Print comparison summary."""
    print("=" * 80)
    print("EITC Comparison: PolicyEngine vs TAXSIM-35")
    print("=" * 80)
    print(f"Sample size: {len(merged)}")

    print(f"\nAggregate totals:")
    print(f"  PolicyEngine: ${merged['pe_eitc'].sum():,.0f}")
    print(f"  TAXSIM:       ${merged['taxsim_eitc'].sum():,.0f}")
    diff_pct = 100 * merged["diff"].sum() / merged["taxsim_eitc"].sum()
    print(f"  Difference:   ${merged['diff'].sum():,.0f} ({diff_pct:.1f}%)")

    print(f"\nRecipient counts:")
    print(f"  PolicyEngine: {(merged['pe_eitc'] > 0).sum()}")
    print(f"  TAXSIM:       {(merged['taxsim_eitc'] > 0).sum()}")

    # Agreement stats
    both_zero = ((merged["pe_eitc"] == 0) & (merged["taxsim_eitc"] == 0)).sum()
    both_positive = ((merged["pe_eitc"] > 0) & (merged["taxsim_eitc"] > 0)).sum()
    pe_only = ((merged["pe_eitc"] > 0) & (merged["taxsim_eitc"] == 0)).sum()
    taxsim_only = ((merged["pe_eitc"] == 0) & (merged["taxsim_eitc"] > 0)).sum()

    print(f"\nAgreement on eligibility:")
    print(f"  Both zero:     {both_zero}")
    print(f"  Both positive: {both_positive}")
    print(f"  PE only:       {pe_only}")
    print(f"  TAXSIM only:   {taxsim_only}")

    # Cases with large differences
    big_diff = merged[merged["abs_diff"] > 100].sort_values("abs_diff", ascending=False)
    print(f"\nCases with >$100 difference: {len(big_diff)}")


if __name__ == "__main__":
    merged = compare_eitc(sample_size=500)
    print_summary(merged)

    # Save results
    output_path = Path(__file__).parent / "pe_taxsim_results.csv"
    merged.to_csv(output_path, index=False)
    print(f"\nResults saved to {output_path}")
