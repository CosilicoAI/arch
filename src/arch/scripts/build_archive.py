#!/usr/bin/env python3
"""
Build the complete arch source archive.

This script downloads, ingests, and uploads all source documents:
- US Code titles (from uscode.house.gov)
- IRS guidance (from irs.gov)
- State statutes (from state APIs)

Usage:
    python -m arch.scripts.build_archive --all
    python -m arch.scripts.build_archive --uscode 26 42
    python -m arch.scripts.build_archive --guidance --years 2024
    python -m arch.scripts.build_archive --state ny
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Default US Code titles to download
DEFAULT_USC_TITLES = [
    2,   # Congress
    5,   # Government Employees
    7,   # Agriculture (SNAP)
    19,  # Customs
    20,  # Education
    26,  # Internal Revenue Code
    29,  # Labor
    38,  # Veterans
    42,  # Public Health (SSI, TANF, Medicaid)
    45,  # Railroads (Railroad Retirement)
]

# Default guidance years
DEFAULT_GUIDANCE_YEARS = [2020, 2021, 2022, 2023, 2024]

# Default states (requires API keys)
DEFAULT_STATES = ["ny"]


def run_arch_command(args: list[str]) -> bool:
    """Run an arch CLI command."""
    cmd = ["uv", "run", "arch"] + args
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode == 0


def download_uscode(titles: list[int], output_dir: str = "data/uscode") -> None:
    """Download US Code titles."""
    print(f"\n📜 Downloading {len(titles)} US Code titles...")
    for title in titles:
        print(f"\n  Downloading Title {title}...")
        run_arch_command(["download", str(title), "-o", output_dir])


def ingest_uscode(titles: list[int], input_dir: str = "data/uscode") -> None:
    """Ingest US Code titles into database."""
    print(f"\n📥 Ingesting {len(titles)} US Code titles...")
    for title in titles:
        xml_path = Path(input_dir) / f"usc{title}.xml"
        if xml_path.exists():
            print(f"\n  Ingesting Title {title}...")
            run_arch_command(["ingest", str(xml_path)])
        else:
            print(f"  ⚠️  Title {title} not found at {xml_path}")


def fetch_guidance(years: list[int], download_pdfs: bool = True) -> None:
    """Fetch IRS guidance documents."""
    print(f"\n📋 Fetching IRS guidance for years {years}...")
    args = ["fetch-guidance"]
    for year in years:
        args.extend(["-y", str(year)])
    if download_pdfs:
        args.append("--download-pdfs")
    run_arch_command(args)


def download_state(state: str, laws: list[str] | None = None) -> None:
    """Download state statutes."""
    print(f"\n🏛️  Downloading {state.upper()} state statutes...")
    args = ["download-state", state]
    if laws:
        for law in laws:
            args.extend(["--law", law])
    run_arch_command(args)


def upload_to_r2() -> None:
    """Upload local data to R2 bucket."""
    print("\n☁️  Uploading to R2...")

    # Load credentials
    creds_path = Path.home() / ".config/cosilico/r2-credentials.json"
    if not creds_path.exists():
        print("  ⚠️  R2 credentials not found. Skipping upload.")
        return

    with open(creds_path) as f:
        creds = json.load(f)

    import boto3
    from botocore.config import Config

    s3 = boto3.client(
        's3',
        endpoint_url=creds['endpoint_url'],
        aws_access_key_id=creds['access_key_id'],
        aws_secret_access_key=creds['secret_access_key'],
        config=Config(signature_version='s3v4'),
        region_name='auto'
    )

    # Upload guidance PDFs
    guidance_dir = Path("data/guidance/irs")
    if guidance_dir.exists():
        pdfs = list(guidance_dir.glob("*.pdf"))
        print(f"  Uploading {len(pdfs)} IRS guidance PDFs...")
        for i, pdf in enumerate(pdfs, 1):
            key = f"us/guidance/irs/{pdf.name}"
            s3.upload_file(str(pdf), creds['bucket'], key)
            if i % 100 == 0:
                print(f"    Uploaded {i}/{len(pdfs)}...")
        print(f"  ✓ Uploaded {len(pdfs)} guidance PDFs")


def main():
    parser = argparse.ArgumentParser(
        description="Build arch source archive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--all", action="store_true", help="Build everything")
    parser.add_argument("--uscode", nargs="*", type=int, metavar="TITLE",
                        help="Download US Code titles (default: all)")
    parser.add_argument("--guidance", action="store_true",
                        help="Fetch IRS guidance")
    parser.add_argument("--years", nargs="+", type=int, metavar="YEAR",
                        help="Guidance years (default: 2020-2024)")
    parser.add_argument("--state", nargs="*", metavar="STATE",
                        help="Download state statutes")
    parser.add_argument("--upload", action="store_true",
                        help="Upload to R2 after building")
    parser.add_argument("--no-ingest", action="store_true",
                        help="Skip database ingestion")

    args = parser.parse_args()

    # Determine what to build
    if args.all:
        titles = DEFAULT_USC_TITLES
        do_guidance = True
        years = DEFAULT_GUIDANCE_YEARS
        states = DEFAULT_STATES
    else:
        titles = args.uscode if args.uscode is not None else []
        do_guidance = args.guidance
        years = args.years or DEFAULT_GUIDANCE_YEARS
        states = args.state or []

    # Build
    if titles:
        download_uscode(titles)
        if not args.no_ingest:
            ingest_uscode(titles)

    if do_guidance:
        fetch_guidance(years)

    for state in states:
        download_state(state)

    if args.upload or args.all:
        upload_to_r2()

    print("\n✅ Build complete!")


if __name__ == "__main__":
    main()
