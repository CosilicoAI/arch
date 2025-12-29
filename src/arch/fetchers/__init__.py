"""Fetchers for downloading regulatory documents."""

from arch.fetchers.ecfr import ECFRFetcher
from arch.fetchers.state_benefits import (
    CCDFFetcher,
    CCDFPolicyData,
    SNAPSUAFetcher,
    StateBenefitsFetcher,
    SUAData,
    TANFFetcher,
    TANFPolicyData,
)

__all__ = [
    "ECFRFetcher",
    "SNAPSUAFetcher",
    "TANFFetcher",
    "CCDFFetcher",
    "StateBenefitsFetcher",
    "SUAData",
    "TANFPolicyData",
    "CCDFPolicyData",
]
