"""Parsers for various legal document formats."""

from arch.parsers.uslm import USLMParser

# State parsers - imported conditionally to avoid import errors
try:
    from arch.parsers.ny_laws import (
        NY_LAW_CODES,
        NYLegislationClient,
        NYStateCitation,
        download_ny_law,
    )
except ImportError:
    NY_LAW_CODES = {}
    NYLegislationClient = None  # type: ignore[misc, assignment]
    NYStateCitation = None  # type: ignore[misc, assignment]
    download_ny_law = None  # type: ignore[misc, assignment]

try:
    from arch.parsers.ca_statutes import (
        CA_CODES,
        CACodeParser,
        CASection,
        CaliforniaStatutesParser,
    )
except ImportError:
    CA_CODES = {}
    CACodeParser = None  # type: ignore[misc, assignment]
    CASection = None  # type: ignore[misc, assignment]
    CaliforniaStatutesParser = None  # type: ignore[misc, assignment]

try:
    from arch.parsers.fl_statutes import (
        FL_TAX_CHAPTERS,
        FL_WELFARE_CHAPTERS,
        FLStatutesClient,
        FLSection,
    )
except ImportError:
    FL_TAX_CHAPTERS = {}
    FL_WELFARE_CHAPTERS = {}
    FLStatutesClient = None  # type: ignore[misc, assignment]
    FLSection = None  # type: ignore[misc, assignment]

try:
    from arch.parsers.tx_statutes import (
        TX_CODES,
        TXStatutesClient,
        TXSection,
    )
except ImportError:
    TX_CODES = {}
    TXStatutesClient = None  # type: ignore[misc, assignment]
    TXSection = None  # type: ignore[misc, assignment]

__all__ = [
    # Federal
    "USLMParser",
    # New York
    "NY_LAW_CODES",
    "NYLegislationClient",
    "NYStateCitation",
    "download_ny_law",
    # California
    "CA_CODES",
    "CACodeParser",
    "CASection",
    "CaliforniaStatutesParser",
    # Florida
    "FL_TAX_CHAPTERS",
    "FL_WELFARE_CHAPTERS",
    "FLStatutesClient",
    "FLSection",
    # Texas
    "TX_CODES",
    "TXStatutesClient",
    "TXSection",
]
