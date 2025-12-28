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
        # Virginia
        "us-va": SourceConfig(
            jurisdiction="us-va",
            name="Virginia",
            source_type="html",
            base_url="https://law.lis.virginia.gov",
            section_url_pattern="/vacode/title{title}/chapter{chapter}/section{section}/",
            toc_url_pattern="/vacode/title{code}/",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "58.1": "Taxation",
                "63.2": "Welfare (Social Services)",
                "40.1": "Labor and Employment",
                "60.2": "Unemployment Compensation",
                "38.2": "Insurance",
            },
            priority_codes=["58.1", "63.2", "40.1", "60.2"],
        ),
        # Washington
        "us-wa": SourceConfig(
            jurisdiction="us-wa",
            name="Washington",
            source_type="html",
            base_url="https://app.leg.wa.gov",
            section_url_pattern="/RCW/default.aspx?cite={section}",
            toc_url_pattern="/RCW/default.aspx?cite={code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "82": "Excise Taxes",
                "83": "Estate Taxation",
                "74": "Public Assistance",
                "50": "Unemployment Compensation",
                "49": "Labor Regulations",
                "48": "Insurance",
            },
            priority_codes=["82", "74", "50", "49"],
        ),
        # Arizona
        "us-az": SourceConfig(
            jurisdiction="us-az",
            name="Arizona",
            source_type="html",
            base_url="https://www.azleg.gov",
            section_url_pattern="/ars/{title}/{section}.htm",
            toc_url_pattern="/arsDetail?title={code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "42": "Taxation",
                "46": "Welfare",
                "23": "Labor",
                "20": "Insurance",
            },
            priority_codes=["42", "46", "23"],
        ),
        # Massachusetts
        "us-ma": SourceConfig(
            jurisdiction="us-ma",
            name="Massachusetts",
            source_type="html",
            base_url="https://malegislature.gov",
            section_url_pattern="/Laws/GeneralLaws/Part{part}/Title{title}/Chapter{chapter}/Section{section}",
            toc_url_pattern="/Laws/GeneralLaws/Part{part}/Title{title}/Chapter{code}",
            content_selector="div.lawContent, main, body",
            title_selector="h1, title",
            codes={
                "62": "Taxation of Incomes",
                "62C": "Administrative Provisions Relative to State Taxation",
                "118": "Aid to Families with Dependent Children",
                "151A": "Unemployment Insurance",
                "149": "Labor and Industries",
                "175": "Insurance",
            },
            priority_codes=["62", "62C", "118", "151A", "149"],
        ),
        # Maryland
        "us-md": SourceConfig(
            jurisdiction="us-md",
            name="Maryland",
            source_type="html",
            base_url="https://mgaleg.maryland.gov",
            section_url_pattern="/mgawebsite/Laws/StatuteText?article={code}&section={section}",
            toc_url_pattern="/mgawebsite/Laws/StatuteText?article={code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "tg": "Tax - General",
                "tp": "Tax - Property",
                "hu": "Human Services",
                "le": "Labor and Employment",
                "in": "Insurance",
            },
            priority_codes=["tg", "tp", "hu", "le"],
        ),
        # Minnesota
        "us-mn": SourceConfig(
            jurisdiction="us-mn",
            name="Minnesota",
            source_type="html",
            base_url="https://www.revisor.mn.gov",
            section_url_pattern="/statutes/cite/{section}",
            toc_url_pattern="/statutes/cite/{code}",
            content_selector="div.statute, main, body",
            title_selector="h1, title",
            codes={
                "290": "Individual Income Tax",
                "290A": "Property Tax Refund",
                "256": "Human Services",
                "268": "Unemployment Insurance",
                "177": "Hours and Wages",
                "60A": "Insurance",
            },
            priority_codes=["290", "290A", "256", "268", "177"],
        ),
        # Wisconsin
        "us-wi": SourceConfig(
            jurisdiction="us-wi",
            name="Wisconsin",
            source_type="html",
            base_url="https://docs.legis.wisconsin.gov",
            section_url_pattern="/document/statutes/{section}",
            toc_url_pattern="/statutes/statutes/{code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "71": "Income and Franchise Taxes",
                "49": "Public Assistance",
                "108": "Unemployment Insurance",
                "103": "Employment Regulations",
                "632": "Insurance Contracts",
            },
            priority_codes=["71", "49", "108", "103"],
        ),
        # Missouri
        "us-mo": SourceConfig(
            jurisdiction="us-mo",
            name="Missouri",
            source_type="html",
            base_url="https://revisor.mo.gov",
            section_url_pattern="/main/OneSection.aspx?section={section}",
            toc_url_pattern="/main/OneChapter.aspx?chapter={code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "143": "Income Tax",
                "208": "Social Services",
                "288": "Employment Security",
                "290": "Labor and Industrial Relations",
                "375": "Insurance",
            },
            priority_codes=["143", "208", "288", "290"],
        ),
        # New Jersey
        "us-nj": SourceConfig(
            jurisdiction="us-nj",
            name="New Jersey",
            source_type="html",
            base_url="https://lis.njleg.state.nj.us",
            section_url_pattern="/nxt/gateway.dll/statutes/1?f=templates&fn=default.htm",
            toc_url_pattern="/nxt/gateway.dll/statutes/1?f=templates&fn=default.htm",
            content_selector="body",
            title_selector="title",
            codes={
                "54": "Taxation",
                "44": "Poor and Welfare",
                "43": "Labor and Workmen's Compensation",
                "34": "Labor and Industrial Relations",
                "17": "Insurance",
            },
            priority_codes=["54", "44", "43", "34"],
            custom_parser="arch.parsers.nj_statutes",  # Needs custom parser
        ),
        # Colorado - Official PDFs from leg.colorado.gov
        "us-co": SourceConfig(
            jurisdiction="us-co",
            name="Colorado",
            source_type="bulk",  # PDF downloads, needs PDF parser
            base_url="https://content.leg.colorado.gov",
            section_url_pattern="/sites/default/files/images/olls/crs2024-title-{title}.pdf",
            toc_url_pattern="/agencies/office-legislative-legal-services/2024-crs-titles-download",
            content_selector="body",
            title_selector="title",
            codes={
                "39": "Taxation",
                "26": "Human Services",
                "8": "Labor and Industry",
                "10": "Insurance",
                "22": "Education",
            },
            priority_codes=["39", "26", "8"],
            custom_parser="arch.parsers.co_statutes",  # Needs PDF parser
        ),
        # Indiana
        "us-in": SourceConfig(
            jurisdiction="us-in",
            name="Indiana",
            source_type="html",
            base_url="https://iga.in.gov",
            section_url_pattern="/laws/current/ic/titles/{title}",
            toc_url_pattern="/laws/current/ic/titles/{code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "6": "Taxation",
                "12": "Human Services",
                "22": "Labor and Safety",
                "27": "Insurance",
            },
            priority_codes=["6", "12", "22"],
        ),
        # Kentucky
        "us-ky": SourceConfig(
            jurisdiction="us-ky",
            name="Kentucky",
            source_type="html",
            base_url="https://apps.legislature.ky.gov",
            section_url_pattern="/law/statutes/statute.aspx?id={section}",
            toc_url_pattern="/law/statutes/chapter.aspx?id={code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "141": "Income Tax",
                "205": "Assistance to Needy Persons",
                "341": "Unemployment Compensation",
                "337": "Wages and Hours",
                "304": "Insurance",
            },
            priority_codes=["141", "205", "341", "337"],
        ),
        # Louisiana
        "us-la": SourceConfig(
            jurisdiction="us-la",
            name="Louisiana",
            source_type="html",
            base_url="https://legis.la.gov",
            section_url_pattern="/Legis/Law.aspx?d={section}",
            toc_url_pattern="/Legis/Laws_Toc.aspx?folder={code}",
            content_selector="div.content, main, body",
            title_selector="h1, title",
            codes={
                "47": "Revenue and Taxation",
                "46": "Public Welfare and Assistance",
                "23": "Labor and Workers Compensation",
                "22": "Insurance",
            },
            priority_codes=["47", "46", "23"],
        ),
        # Oregon
        "us-or": SourceConfig(
            jurisdiction="us-or",
            name="Oregon",
            source_type="html",
            base_url="https://www.oregonlegislature.gov",
            section_url_pattern="/bills_laws/ors/ors{chapter}.html",
            toc_url_pattern="/bills_laws/pages/ors.aspx",
            content_selector="body",
            title_selector="title",
            codes={
                "316": "Personal Income Tax",
                "411": "State Public Assistance",
                "657": "Unemployment Insurance",
                "653": "Minimum Wages; Employment Conditions",
                "746": "Insurance",
            },
            priority_codes=["316", "411", "657", "653"],
        ),
        # Tennessee (via LexisNexis free access)
        "us-tn": SourceConfig(
            jurisdiction="us-tn",
            name="Tennessee",
            source_type="html",
            base_url="https://www.lexisnexis.com",
            section_url_pattern="/hottopics/tncode/",
            toc_url_pattern="/hottopics/tncode/",
            content_selector="body",
            title_selector="title",
            codes={
                "67": "Taxes and Licenses",
                "71": "Welfare",
                "50": "Employer and Employee",
                "56": "Insurance",
            },
            priority_codes=["67", "71", "50"],
            custom_parser="arch.parsers.tn_statutes",  # Needs custom for LexisNexis
        ),
        # Connecticut
        "us-ct": SourceConfig(
            jurisdiction="us-ct",
            name="Connecticut",
            source_type="html",
            base_url="https://www.cga.ct.gov",
            section_url_pattern="/current/pub/chap_{chapter}.htm",
            toc_url_pattern="/current/pub/titles.htm",
            content_selector="body",
            title_selector="title",
            codes={
                "12": "Taxation",
                "17a": "Social and Human Services",
                "31": "Labor",
                "38a": "Insurance",
            },
            priority_codes=["12", "17a", "31"],
        ),
        # Iowa
        "us-ia": SourceConfig(
            jurisdiction="us-ia",
            name="Iowa",
            source_type="html",
            base_url="https://www.legis.iowa.gov",
            section_url_pattern="/docs/code/{year}/{section}.pdf",
            toc_url_pattern="/law/statutory",
            content_selector="body",
            title_selector="title",
            codes={
                "422": "Individual Income Tax",
                "239B": "Family Investment Program",
                "96": "Employment Security",
                "91A": "Wage Payment Collection",
                "505": "Insurance",
            },
            priority_codes=["422", "239B", "96", "91A"],
        ),
        # Oklahoma
        "us-ok": SourceConfig(
            jurisdiction="us-ok",
            name="Oklahoma",
            source_type="html",
            base_url="https://www.oscn.net",
            section_url_pattern="/applications/oscn/DeliverDocument.asp?CiteID={cite}",
            toc_url_pattern="/applications/oscn/Index.asp?ftdb=STOKST&level=1",
            content_selector="body",
            title_selector="title",
            codes={
                "68": "Revenue and Taxation",
                "56": "Poor Persons",
                "40": "Labor",
                "36": "Insurance",
            },
            priority_codes=["68", "56", "40"],
        ),
        # South Carolina
        "us-sc": SourceConfig(
            jurisdiction="us-sc",
            name="South Carolina",
            source_type="html",
            base_url="https://www.scstatehouse.gov",
            section_url_pattern="/code/t{title}c{chapter}.php",
            toc_url_pattern="/code/statmast.php",
            content_selector="body",
            title_selector="title",
            codes={
                "12": "Taxation",
                "43": "Social Services",
                "41": "Labor and Employment",
                "38": "Insurance",
            },
            priority_codes=["12", "43", "41"],
        ),
        # Alabama
        "us-al": SourceConfig(
            jurisdiction="us-al",
            name="Alabama",
            source_type="html",
            base_url="https://alisondb.legislature.state.al.us",
            section_url_pattern="/alison/CodeOfAlabama/1975/{title}-{chapter}-{section}.htm",
            toc_url_pattern="/alison/CodeOfAlabama/1975/coatoc.htm",
            content_selector="body",
            title_selector="title",
            codes={
                "40": "Revenue and Taxation",
                "38": "Public Welfare",
                "25": "Industrial Relations and Labor",
                "27": "Insurance",
            },
            priority_codes=["40", "38", "25"],
        ),
        # Utah
        "us-ut": SourceConfig(
            jurisdiction="us-ut",
            name="Utah",
            source_type="html",
            base_url="https://le.utah.gov",
            section_url_pattern="/xcode/Title{title}/Chapter{chapter}/{title}-{chapter}-S{section}.html",
            toc_url_pattern="/xcode/code.html",
            content_selector="body",
            title_selector="title",
            codes={
                "59": "Revenue and Taxation",
                "35A": "Utah Workforce Services Code",
                "34A": "Utah Labor Code",
                "31A": "Insurance Code",
            },
            priority_codes=["59", "35A", "34A"],
        ),
        # Nevada
        "us-nv": SourceConfig(
            jurisdiction="us-nv",
            name="Nevada",
            source_type="html",
            base_url="https://www.leg.state.nv.us",
            section_url_pattern="/NRS/NRS-{chapter}.html#{section}",
            toc_url_pattern="/NRS/",
            content_selector="body",
            title_selector="title",
            codes={
                "360": "Revenue and Taxation",
                "422": "Public Assistance",
                "612": "Unemployment Compensation",
                "608": "Compensation, Wages and Hours",
                "679A": "Insurance",
            },
            priority_codes=["360", "422", "612", "608"],
        ),
        # Arkansas
        "us-ar": SourceConfig(
            jurisdiction="us-ar",
            name="Arkansas",
            source_type="html",
            base_url="https://www.lexisnexis.com",
            section_url_pattern="/hottopics/arcode/",
            toc_url_pattern="/hottopics/arcode/",
            content_selector="body",
            title_selector="title",
            codes={
                "26": "Taxation",
                "20": "Public Health and Welfare",
                "11": "Labor and Industrial Relations",
                "23": "Insurance",
            },
            priority_codes=["26", "20", "11"],
            custom_parser="arch.parsers.ar_statutes",
        ),
        # Kansas
        "us-ks": SourceConfig(
            jurisdiction="us-ks",
            name="Kansas",
            source_type="html",
            base_url="https://www.ksrevisor.org",
            section_url_pattern="/statutes/chapters/ch{chapter}/",
            toc_url_pattern="/statutes/ksa.html",
            content_selector="body",
            title_selector="title",
            codes={
                "79": "Taxation",
                "39": "Public Assistance and Welfare",
                "44": "Labor and Industries",
                "40": "Insurance",
            },
            priority_codes=["79", "39", "44"],
        ),
        # Mississippi
        "us-ms": SourceConfig(
            jurisdiction="us-ms",
            name="Mississippi",
            source_type="html",
            base_url="https://www.lexisnexis.com",
            section_url_pattern="/hottopics/mscode/",
            toc_url_pattern="/hottopics/mscode/",
            content_selector="body",
            title_selector="title",
            codes={
                "27": "Taxation and Finance",
                "43": "Public Welfare",
                "71": "Labor and Industries",
                "83": "Insurance",
            },
            priority_codes=["27", "43", "71"],
            custom_parser="arch.parsers.ms_statutes",
        ),
        # New Mexico
        "us-nm": SourceConfig(
            jurisdiction="us-nm",
            name="New Mexico",
            source_type="html",
            base_url="https://nmonesource.com",
            section_url_pattern="/nmos/nmsa/en/nav.do",
            toc_url_pattern="/nmos/nmsa/en/nav.do",
            content_selector="body",
            title_selector="title",
            codes={
                "7": "Taxation",
                "27": "Public Assistance",
                "52": "Workers Compensation",
                "50": "Employment Law",
                "59A": "Insurance",
            },
            priority_codes=["7", "27", "52", "50"],
        ),
        # Nebraska
        "us-ne": SourceConfig(
            jurisdiction="us-ne",
            name="Nebraska",
            source_type="html",
            base_url="https://nebraskalegislature.gov",
            section_url_pattern="/laws/statutes.php?statute={section}",
            toc_url_pattern="/laws/browse-chapters.php",
            content_selector="body",
            title_selector="title",
            codes={
                "77": "Revenue and Taxation",
                "68": "Public Assistance",
                "48": "Labor",
                "44": "Insurance",
            },
            priority_codes=["77", "68", "48"],
        ),
        # West Virginia
        "us-wv": SourceConfig(
            jurisdiction="us-wv",
            name="West Virginia",
            source_type="html",
            base_url="https://www.wvlegislature.gov",
            section_url_pattern="/wvcode/code.cfm?chap={chapter}&art={article}",
            toc_url_pattern="/wvcode/",
            content_selector="body",
            title_selector="title",
            codes={
                "11": "Taxation",
                "9": "Human Services",
                "21": "Labor",
                "33": "Insurance",
            },
            priority_codes=["11", "9", "21"],
        ),
        # Idaho
        "us-id": SourceConfig(
            jurisdiction="us-id",
            name="Idaho",
            source_type="html",
            base_url="https://legislature.idaho.gov",
            section_url_pattern="/statutesrules/idstat/Title{title}/T{title}CH{chapter}/SECT{title}-{chapter}{section}/",
            toc_url_pattern="/statutesrules/idstat/",
            content_selector="body",
            title_selector="title",
            codes={
                "63": "Revenue and Taxation",
                "56": "Public Assistance and Welfare",
                "72": "Workers Compensation",
                "45": "Liens and Labor",
                "41": "Insurance",
            },
            priority_codes=["63", "56", "72", "45"],
        ),
        # Hawaii
        "us-hi": SourceConfig(
            jurisdiction="us-hi",
            name="Hawaii",
            source_type="html",
            base_url="https://www.capitol.hawaii.gov",
            section_url_pattern="/hrscurrent/Vol{vol}/Chr{chapter}/HRS_{chapter}-{section}.htm",
            toc_url_pattern="/hrscurrent/",
            content_selector="body",
            title_selector="title",
            codes={
                "235": "Income Tax",
                "346": "Public Welfare",
                "383": "Hawaii Employment Security",
                "388": "Wages and Hours",
                "431": "Insurance",
            },
            priority_codes=["235", "346", "383", "388"],
        ),
        # Maine
        "us-me": SourceConfig(
            jurisdiction="us-me",
            name="Maine",
            source_type="html",
            base_url="https://legislature.maine.gov",
            section_url_pattern="/statutes/{title}/title{title}sec{section}.html",
            toc_url_pattern="/statutes/",
            content_selector="body",
            title_selector="title",
            codes={
                "36": "Taxation",
                "22": "Health and Welfare",
                "26": "Labor and Industry",
                "24-A": "Maine Insurance Code",
            },
            priority_codes=["36", "22", "26"],
        ),
        # New Hampshire
        "us-nh": SourceConfig(
            jurisdiction="us-nh",
            name="New Hampshire",
            source_type="html",
            base_url="https://www.gencourt.state.nh.us",
            section_url_pattern="/rsa/html/V/{chapter}/{chapter}-mrg.htm",
            toc_url_pattern="/rsa/html/nhtoc.htm",
            content_selector="body",
            title_selector="title",
            codes={
                "77": "Taxation of Incomes",
                "161": "Division of Human Services",
                "282-A": "Unemployment Compensation",
                "275": "Hours of Labor",
                "401": "Insurance",
            },
            priority_codes=["77", "161", "282-A", "275"],
        ),
        # Rhode Island
        "us-ri": SourceConfig(
            jurisdiction="us-ri",
            name="Rhode Island",
            source_type="html",
            base_url="https://webserver.rilegislature.gov",
            section_url_pattern="/Statutes/TITLE{title}/{title}-{chapter}/{title}-{chapter}-{section}.htm",
            toc_url_pattern="/Statutes/",
            content_selector="body",
            title_selector="title",
            codes={
                "44": "Taxation",
                "40": "Human Services",
                "28": "Labor and Labor Relations",
                "27": "Insurance",
            },
            priority_codes=["44", "40", "28"],
        ),
        # Montana
        "us-mt": SourceConfig(
            jurisdiction="us-mt",
            name="Montana",
            source_type="html",
            base_url="https://leg.mt.gov",
            section_url_pattern="/bills/mca/title_{title:04d}/chapter_{chapter:03d}/part_{part:02d}/section_{section}/",
            toc_url_pattern="/bills/mca_toc/",
            content_selector="body",
            title_selector="title",
            codes={
                "15": "Taxation",
                "53": "Social Services and Institutions",
                "39": "Labor",
                "33": "Insurance",
            },
            priority_codes=["15", "53", "39"],
        ),
        # Delaware
        "us-de": SourceConfig(
            jurisdiction="us-de",
            name="Delaware",
            source_type="html",
            base_url="https://delcode.delaware.gov",
            section_url_pattern="/title{title}/c{chapter:03d}/sc{subchapter:02d}/index.html",
            toc_url_pattern="/title{title}/index.html",
            content_selector="body",
            title_selector="title",
            codes={
                "30": "State Taxes",
                "31": "Welfare",
                "19": "Labor",
                "18": "Insurance",
            },
            priority_codes=["30", "31", "19"],
        ),
        # South Dakota
        "us-sd": SourceConfig(
            jurisdiction="us-sd",
            name="South Dakota",
            source_type="html",
            base_url="https://sdlegislature.gov",
            section_url_pattern="/Statutes/Codified_Laws/DisplayStatute.aspx?Type=Statute&Statute={section}",
            toc_url_pattern="/Statutes/Codified_Laws/",
            content_selector="body",
            title_selector="title",
            codes={
                "10": "Taxation",
                "28": "Human Services",
                "61": "Unemployment Compensation",
                "60": "Labor and Employment",
                "58": "Insurance",
            },
            priority_codes=["10", "28", "61", "60"],
        ),
        # North Dakota
        "us-nd": SourceConfig(
            jurisdiction="us-nd",
            name="North Dakota",
            source_type="html",
            base_url="https://ndlegis.gov",
            section_url_pattern="/cencode/t{title}c{chapter}.pdf",
            toc_url_pattern="/cencode/",
            content_selector="body",
            title_selector="title",
            codes={
                "57": "Taxation",
                "50": "Public Welfare",
                "52": "Unemployment Compensation",
                "34": "Labor and Employment",
                "26.1": "Insurance",
            },
            priority_codes=["57", "50", "52", "34"],
        ),
        # Alaska
        "us-ak": SourceConfig(
            jurisdiction="us-ak",
            name="Alaska",
            source_type="html",
            base_url="https://www.akleg.gov",
            section_url_pattern="/basis/statutes.asp#43.{section}",
            toc_url_pattern="/basis/statutes.asp",
            content_selector="body",
            title_selector="title",
            codes={
                "43": "Revenue and Taxation",
                "47": "Welfare, Social Services, and Institutions",
                "23": "Labor and Workers Compensation",
                "21": "Insurance",
            },
            priority_codes=["43", "47", "23"],
        ),
        # Vermont
        "us-vt": SourceConfig(
            jurisdiction="us-vt",
            name="Vermont",
            source_type="html",
            base_url="https://legislature.vermont.gov",
            section_url_pattern="/statutes/section/{title}/{chapter}/{section}",
            toc_url_pattern="/statutes/",
            content_selector="body",
            title_selector="title",
            codes={
                "32": "Taxation and Finance",
                "33": "Human Services",
                "21": "Labor",
                "8": "Insurance",
            },
            priority_codes=["32", "33", "21"],
        ),
        # Wyoming
        "us-wy": SourceConfig(
            jurisdiction="us-wy",
            name="Wyoming",
            source_type="html",
            base_url="https://wyoleg.gov",
            section_url_pattern="/statutes/compress/title{title}.pdf",
            toc_url_pattern="/statutes/",
            content_selector="body",
            title_selector="title",
            codes={
                "39": "Taxation and Revenue",
                "42": "Public Assistance and Social Services",
                "27": "Labor and Employment",
                "26": "Insurance",
            },
            priority_codes=["39", "42", "27"],
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
