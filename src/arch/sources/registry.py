"""Registry of statute sources by jurisdiction.

Maps jurisdiction IDs to source adapters and configurations.
Configurations can be loaded from YAML files in sources/ directory.
"""

from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from arch.sources.base import SourceConfig, StatuteSource

if TYPE_CHECKING:
    pass


# Source configs loaded from YAML or defined here
_SOURCE_CONFIGS: dict[str, SourceConfig] = {}


def _load_yaml_configs(sources_dir: Path | None = None) -> dict[str, SourceConfig]:
    """Load source configurations from YAML files.

    YAML files are in sources/ directory, named by jurisdiction:
    - sources/us.yaml
    - sources/us-ca.yaml
    - sources/us-ny.yaml
    """
    sources_dir = sources_dir or Path(__file__).parent.parent.parent.parent / "sources"

    configs = {}
    if not sources_dir.exists():
        return configs

    for yaml_file in sources_dir.glob("*.yaml"):
        try:
            with open(yaml_file) as f:
                data = yaml.safe_load(f)

            if not data:
                continue

            jurisdiction = data.get("jurisdiction", yaml_file.stem)
            configs[jurisdiction] = SourceConfig(
                jurisdiction=jurisdiction,
                name=data.get("name", jurisdiction),
                source_type=data.get("source_type", "html"),
                base_url=data.get("base_url", ""),
                api_key=data.get("api_key"),
                section_url_pattern=data.get("section_url_pattern"),
                toc_url_pattern=data.get("toc_url_pattern"),
                content_selector=data.get("content_selector"),
                title_selector=data.get("title_selector"),
                history_selector=data.get("history_selector"),
                codes=data.get("codes", {}),
                priority_codes=data.get("priority_codes", []),
                rate_limit=data.get("rate_limit", 0.5),
                max_retries=data.get("max_retries", 3),
                custom_parser=data.get("custom_parser"),
            )
        except Exception as e:
            print(f"Error loading {yaml_file}: {e}")

    return configs


def _get_builtin_configs() -> dict[str, SourceConfig]:
    """Get built-in source configurations."""
    from arch.sources.uslm import get_federal_config

    return {
        "us": get_federal_config(),
        # Ohio
        "us-oh": SourceConfig(
            jurisdiction="us-oh",
            name="Ohio",
            source_type="html",
            base_url="https://codes.ohio.gov",
            section_url_pattern="/ohio-revised-code/section-{section}",
            toc_url_pattern="/ohio-revised-code/title-{code}",
            content_selector="main",
            title_selector="title",
            codes={
                "57": "Taxation",
                "51": "Public Welfare",
                "41": "Labor and Industry",
                "33": "Education-Libraries",
                "37": "Health-Safety-Morals",
            },
            priority_codes=["57", "51", "41"],
        ),
        # Pennsylvania
        "us-pa": SourceConfig(
            jurisdiction="us-pa",
            name="Pennsylvania",
            source_type="html",
            base_url="https://www.palegis.us",
            section_url_pattern="/statutes/consolidated/view-statute?txtType=HTM&ttl={code}&sctn={section}",
            toc_url_pattern="/statutes/consolidated/view-statute?txtType=HTM&ttl={code}",
            content_selector="div.statute-content, div#content, body",
            title_selector="h1, h2.title",
            codes={
                "72": "Taxation and Fiscal Affairs",
                "62": "Public Welfare",
                "43": "Labor",
                "40": "Insurance",
                "24": "Education",
            },
            priority_codes=["72", "62", "43"],
        ),
        # North Carolina
        "us-nc": SourceConfig(
            jurisdiction="us-nc",
            name="North Carolina",
            source_type="html",
            base_url="https://www.ncleg.gov",
            section_url_pattern="/EnactedLegislation/Statutes/HTML/BySection/Chapter_{code}/GS_{section}.html",
            toc_url_pattern="/EnactedLegislation/Statutes/HTML/ByChapter/Chapter_{code}.html",
            content_selector="body",
            title_selector="title",
            codes={
                "105": "Taxation",
                "108A": "Social Services",
                "95": "Department of Labor",
                "96": "Employment Security",
                "58": "Insurance",
            },
            priority_codes=["105", "108A", "95", "96"],
        ),
        # Illinois
        "us-il": SourceConfig(
            jurisdiction="us-il",
            name="Illinois",
            source_type="html",
            base_url="https://www.ilga.gov",
            section_url_pattern="/legislation/ilcs/ilcs4.asp?ActID={act}&ChapterID={code}",
            toc_url_pattern="/legislation/ilcs/ilcs2.asp?ChapterID={code}",
            content_selector="div.ilcs-content, td.content, body",
            title_selector="h1, h2",
            codes={
                "35": "Revenue",
                "305": "Public Aid",
                "820": "Employment",
                "215": "Insurance",
                "105": "Schools",
            },
            priority_codes=["35", "305", "820"],
        ),
        # Michigan
        "us-mi": SourceConfig(
            jurisdiction="us-mi",
            name="Michigan",
            source_type="html",
            base_url="https://www.legislature.mi.gov",
            section_url_pattern="/Laws/MCL?objectId=mcl-{section}",
            toc_url_pattern="/Laws/MCL?chapter={code}",
            content_selector="div.content, main, body",
            title_selector="title, h1",
            codes={
                "206": "Income Tax Act",
                "400": "Social Welfare",
                "408": "Labor",
                "421": "Michigan Employment Security Act",
                "500": "Insurance Code",
            },
            priority_codes=["206", "400", "408", "421"],
        ),
        # Georgia
        "us-ga": SourceConfig(
            jurisdiction="us-ga",
            name="Georgia",
            source_type="html",
            base_url="https://www.legis.ga.gov",
            section_url_pattern="/api/legislation/document/{session}/{doc_id}",
            toc_url_pattern="/legislation/en-US/Search/Legislation",
            content_selector="body",
            title_selector="title",
            codes={
                "48": "Revenue and Taxation",
                "49": "Social Services",
                "34": "Labor and Industrial Relations",
                "33": "Insurance",
            },
            priority_codes=["48", "49", "34"],
        ),
    }


def get_all_configs() -> dict[str, SourceConfig]:
    """Get all source configurations (built-in + YAML)."""
    global _SOURCE_CONFIGS

    if not _SOURCE_CONFIGS:
        _SOURCE_CONFIGS = _get_builtin_configs()
        _SOURCE_CONFIGS.update(_load_yaml_configs())

    return _SOURCE_CONFIGS


def get_config_for_jurisdiction(jurisdiction: str) -> SourceConfig | None:
    """Get source configuration for a jurisdiction."""
    configs = get_all_configs()
    return configs.get(jurisdiction.lower())


def get_source_for_jurisdiction(jurisdiction: str) -> StatuteSource | None:
    """Get a source adapter instance for a jurisdiction.

    Args:
        jurisdiction: Jurisdiction ID (e.g., "us", "us-ca")

    Returns:
        StatuteSource instance or None if not configured
    """
    config = get_config_for_jurisdiction(jurisdiction)
    if not config:
        return None

    # Select adapter based on source type
    if config.source_type == "uslm":
        from arch.sources.uslm import USLMSource

        return USLMSource(config)
    elif config.source_type == "api":
        from arch.sources.api import APISource

        if jurisdiction == "us-ny":
            from arch.sources.api import NYLegislationSource

            return NYLegislationSource(config.api_key)
        return APISource(config)
    else:
        from arch.sources.html import HTMLSource

        return HTMLSource(config)


def list_supported_jurisdictions() -> list[dict]:
    """List all supported jurisdictions with their configs."""
    configs = get_all_configs()
    return [
        {
            "jurisdiction": j,
            "name": c.name,
            "source_type": c.source_type,
            "codes": list(c.codes.keys()),
        }
        for j, c in sorted(configs.items())
    ]


def register_source(jurisdiction: str, config: SourceConfig):
    """Register a source configuration."""
    global _SOURCE_CONFIGS
    _SOURCE_CONFIGS[jurisdiction.lower()] = config
