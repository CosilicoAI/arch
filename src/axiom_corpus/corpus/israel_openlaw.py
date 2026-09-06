"""Israeli consolidated-statute extraction from the ספר החוקים הפתוח (OpenLaw) HTML.

The Knesset National Legislation Database renders client-side and its
``לחוק המלא`` link points at the he.wikisource.org ספר החוקים הפתוח project, so
that project's server-rendered HTML is the reachable consolidation for this
pilot.  It is a *secondary* consolidation: statutes themselves carry no
copyright (Copyright Act 5768-2007 §6), but the editorial apparatus — amendment
history brackets, cross-reference notes, historical rate tables — belongs to the
project and is not statutory text.  This adapter keeps that apparatus out of
provision bodies and records it in provision metadata instead.

Like the Armenian ARLIS adapter, extraction is local-file first: a manifest binds
every input to its official URL, an immutable SHA-256, an expression date with a
declared basis, and the expected structural counts, and every source is fully
parsed before the first artifact is written.

Structure of the source markup (``div#law-content``):

* ``div.law-number.tc_.selflink`` with ``id="סעיף_<ident>"`` opens a section;
  the same class with a dotted id (``סעיף_2.1``) is a *sub-item* anchor whose
  text belongs to the enclosing section, not to a new one.  Treating those as
  section starts is the false-split failure this adapter is built to avoid.
* ``id="לוח_<schedule>_פרט_<item>"`` opens a schedule item.
* ``div.law-desc`` carries the section heading, ``div.law-main`` the body.
* ``h1.law-part`` / ``h2.law-section`` / ``h3.law-subsection`` are the
  חלק / פרק (or לוח) / סימן navigation levels.
* ``span.law-note`` is editorial apparatus everywhere it appears.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Self, cast
from urllib.parse import unquote, urlparse

import yaml
from bs4 import BeautifulSoup
from bs4.element import NavigableString, PageElement, Tag

from axiom_corpus.corpus.artifacts import CorpusArtifactStore
from axiom_corpus.corpus.coverage import (
    ProvisionCoverageReport,
    compare_provision_coverage,
)
from axiom_corpus.corpus.models import (
    DocumentClass,
    ProvisionRecord,
    SourceInventoryItem,
)
from axiom_corpus.corpus.supabase import deterministic_provision_id

ISRAEL_OPENLAW_SOURCE_FORMAT = "he.wikisource.org-openlaw-consolidated-html"
ISRAEL_OPENLAW_JURISDICTION = "il"
ISRAEL_OPENLAW_DOCUMENT_CLASS = DocumentClass.STATUTE.value
ISRAEL_OPENLAW_LANGUAGE = "he"
ISRAEL_OPENLAW_SOURCE_AUTHORITY = "ספר החוקים הפתוח (he.wikisource.org OpenLaw project)"
# Two tiers, because the evidence differs per act.  The Knesset National
# Legislation Database's "לחוק המלא" link was followed to the Wikisource page for
# the Income Tax Ordinance; the same check is still pending for the National
# Insurance Law, so that act may not claim the stronger tier.
ISRAEL_OPENLAW_SOURCE_TIERS = frozenset(
    {"consolidation-knesset-linked", "consolidation-wikisource"}
)
ISRAEL_OPENLAW_HOST = "he.wikisource.org"

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_ASCII_WHITESPACE_RE = re.compile(r"[ \t\r\f\v]+")
# Removing an inline editorial note leaves the space that preceded it stranded
# in front of the punctuation that followed it.  HTML whitespace is not
# semantic, so collapse it the same way runs of spaces are collapsed.
_SPACE_BEFORE_PUNCTUATION_RE = re.compile(r" +(?=[.,;:])")

_SECTION_ANCHOR_PREFIX = "סעיף_"
_SCHEDULE_ANCHOR_PREFIX = "לוח_"
_SCHEDULE_ITEM_INFIX = "_פרט_"
_TABLE_OF_CONTENTS_HEADING = "תוכן עניינים"
_SCHEDULE_HEADING_RE = re.compile(r"^לוח\s+(?P<ident>\S+)")
_HEBREW_PUNCTUATION = "״׳\"'"
_ORIGIN_MARKER_RE = re.compile(r"\[(?P<marker>\d+[א-ת]*)\]\s*$")
# OpenLaw styles a repealed/expired/deleted section's own status line as a note.
# That line is how the consolidated text reads for that section, not commentary,
# so it becomes the provision body with the status recorded in metadata.
_STATUS_MARKER_RE = re.compile(r"^\(\s*(?P<status>בוטל|פקע|נמחק)\b")

# Hebrew numeral values, as used for section suffixes (gematria).  Section
# suffixes are written without final forms, so only the base letters appear.
_HEBREW_NUMERALS: dict[str, int] = {
    "א": 1,
    "ב": 2,
    "ג": 3,
    "ד": 4,
    "ה": 5,
    "ו": 6,
    "ז": 7,
    "ח": 8,
    "ט": 9,
    "י": 10,
    "כ": 20,
    "ל": 30,
    "מ": 40,
    "נ": 50,
    "ס": 60,
    "ע": 70,
    "פ": 80,
    "צ": 90,
    "ק": 100,
    "ר": 200,
    "ש": 300,
    "ת": 400,
}
_HEBREW_FINAL_FORMS = {"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"}
_HEBREW_LETTER_RE = re.compile(r"[א-ת]+")
_DIGIT_RUN_RE = re.compile(r"\d+")
_IDENT_TOKEN_RE = re.compile(r"\d+|[א-ת]+")

_NAV_LEVELS = {"part": 1, "chapter": 2, "schedule": 2, "sign": 3}


def hebrew_numeral_value(letters: str) -> int:
    """Return the gematria value of a Hebrew numeral run such as ``יא``."""
    if not letters:
        raise ValueError("empty Hebrew numeral")
    total = 0
    for char in letters:
        base = _HEBREW_FINAL_FORMS.get(char, char)
        value = _HEBREW_NUMERALS.get(base)
        if value is None:
            raise ValueError(f"not a Hebrew numeral letter: {char!r} in {letters!r}")
        total += value
    return total


def latin_ordinal_slug(value: int) -> str:
    """Return the ordinal-position slug for ``value``: 1->a, 26->z, 27->aa.

    ``ops/il-lane/CITATION-SCHEME.md`` fixes 1..12 (א->a … יב->l) and elides the
    rest.  Bijective base-26 is the total, collision-free continuation of that
    sequence; the National Insurance Law needs it, reaching לד (34) -> ``ah``.
    """
    if value < 1:
        raise ValueError(f"ordinal slug requires a positive value, got {value}")
    out = ""
    while value > 0:
        value, remainder = divmod(value - 1, 26)
        out = chr(ord("a") + remainder) + out
    return out


def hebrew_suffix_slug(letters: str) -> str:
    """Transliterate one Hebrew suffix run by ordinal: ב->b, י->j, יא->k."""
    return latin_ordinal_slug(hebrew_numeral_value(letters))


def israeli_ident_slug(ident: str) -> str:
    """Transliterate a printed section identifier such as ``121ב`` or ``64א7א``.

    Digit runs pass through; Hebrew-letter runs become their ordinal slug.  Runs
    alternate, so the transformation stays injective across identifiers.
    """
    normalized = unicodedata.normalize("NFC", ident).strip()
    for char in _HEBREW_PUNCTUATION:
        normalized = normalized.replace(char, "")
    if not normalized:
        raise ValueError("empty section identifier")
    tokens = _IDENT_TOKEN_RE.findall(normalized)
    if "".join(tokens) != normalized:
        raise ValueError(f"unsupported characters in section identifier: {ident!r}")
    return "".join(token if token.isdigit() else hebrew_suffix_slug(token) for token in tokens)


@dataclass(frozen=True)
class IsraelOpenLawSource:
    """One hash-pinned Israeli consolidated statute snapshot."""

    source_id: str
    instrument_slug: str
    israel_law_id: str
    title: str
    title_en: str
    source_url: str
    source_file: str
    sha256: str
    source_as_of: str
    expression_date: str
    expression_date_basis: str
    source_tier: str
    language: str
    expected_section_count: int
    expected_schedule_item_count: int
    expected_part_count: int
    expected_chapter_count: int
    expected_sign_count: int
    alternate_version_sections: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> Self:
        """Validate and construct one manifest source."""
        jurisdiction = str(data.get("jurisdiction", ISRAEL_OPENLAW_JURISDICTION))
        if jurisdiction != ISRAEL_OPENLAW_JURISDICTION:
            raise ValueError(f"Israel source jurisdiction must be il, got {jurisdiction!r}")
        document_class = str(data.get("document_class", ISRAEL_OPENLAW_DOCUMENT_CLASS))
        if document_class != ISRAEL_OPENLAW_DOCUMENT_CLASS:
            raise ValueError(
                f"Israel source document_class must be statute, got {document_class!r}"
            )

        source_id = _required_text(data, "source_id")
        if not _SLUG_RE.fullmatch(source_id):
            raise ValueError(f"invalid Israel source_id: {source_id!r}")
        instrument_slug = _required_text(data, "instrument_slug")
        if not _SLUG_RE.fullmatch(instrument_slug):
            raise ValueError(f"invalid Israel instrument_slug: {instrument_slug!r}")

        israel_law_id = _required_text(data, "israel_law_id")
        if not israel_law_id.isdigit():
            raise ValueError(f"israel_law_id must contain only digits: {israel_law_id!r}")

        language_value = data.get("language")
        if isinstance(language_value, bool):
            raise ValueError("Israel language must be the string 'he', not a YAML boolean")
        language = _required_text(data, "language")
        if language != ISRAEL_OPENLAW_LANGUAGE:
            raise ValueError(f"Israel source language must be he, got {language!r}")

        source_file = _required_text(data, "source_file")
        if Path(source_file).name != source_file or Path(source_file).is_absolute():
            raise ValueError(f"Israel source_file must be a plain file name: {source_file!r}")
        if not source_file.lower().endswith((".html", ".htm")):
            raise ValueError(f"Israel source_file must be HTML: {source_file!r}")

        source_url = _required_text(data, "source_url")
        parsed_url = urlparse(source_url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc != ISRAEL_OPENLAW_HOST
            or not parsed_url.path.startswith("/wiki/")
            or parsed_url.query
            or parsed_url.fragment
        ):
            raise ValueError(
                f"Israel source_url must be an he.wikisource.org /wiki/ page: {source_url!r}"
            )

        sha256 = _required_text(data, "sha256")
        if not _SHA256_RE.fullmatch(sha256):
            raise ValueError(f"invalid lowercase SHA-256 for {source_id}: {sha256!r}")

        counts = {
            name: _required_count(data, name)
            for name in (
                "expected_section_count",
                "expected_part_count",
                "expected_chapter_count",
                "expected_sign_count",
            )
        }
        schedule_items = data.get("expected_schedule_item_count", 0)
        if (
            isinstance(schedule_items, bool)
            or not isinstance(schedule_items, int)
            or schedule_items < 0
        ):
            raise ValueError(
                f"Israel source {source_id} requires a non-negative expected_schedule_item_count"
            )

        source_tier = _required_text(data, "source_tier")
        if source_tier not in ISRAEL_OPENLAW_SOURCE_TIERS:
            raise ValueError(
                f"Israel source {source_id} has unsupported source_tier: {source_tier!r}"
            )

        alternates = data.get("alternate_version_sections", [])
        if not isinstance(alternates, list) or not all(
            isinstance(item, str) and item.strip() for item in alternates
        ):
            raise ValueError(
                f"Israel source {source_id} alternate_version_sections must be a list of strings"
            )

        return cls(
            source_id=source_id,
            instrument_slug=instrument_slug,
            israel_law_id=israel_law_id,
            title=_required_text(data, "title"),
            title_en=_required_text(data, "title_en"),
            source_url=source_url,
            source_file=source_file,
            sha256=sha256,
            source_as_of=_required_iso_date(data, "source_as_of"),
            expression_date=_required_iso_date(data, "expression_date"),
            expression_date_basis=_required_text(data, "expression_date_basis"),
            source_tier=source_tier,
            language=language,
            expected_section_count=counts["expected_section_count"],
            expected_schedule_item_count=schedule_items,
            expected_part_count=counts["expected_part_count"],
            expected_chapter_count=counts["expected_chapter_count"],
            expected_sign_count=counts["expected_sign_count"],
            alternate_version_sections=tuple(
                unicodedata.normalize("NFC", item) for item in alternates
            ),
        )

    @property
    def document_citation_path(self) -> str:
        return (
            f"{ISRAEL_OPENLAW_JURISDICTION}/{ISRAEL_OPENLAW_DOCUMENT_CLASS}/{self.instrument_slug}"
        )

    @property
    def page_title(self) -> str:
        """The decoded he.wikisource page title from ``source_url``."""
        return unquote(urlparse(self.source_url).path[len("/wiki/") :])


@dataclass(frozen=True)
class IsraelOpenLawManifest:
    """Manifest binding local snapshots to official Israeli statute identities."""

    documents: tuple[IsraelOpenLawSource, ...]

    @classmethod
    def load(cls, path: str | Path) -> Self:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Israel manifest must be a YAML mapping")
        rows = data.get("documents")
        if not isinstance(rows, list) or not rows:
            raise ValueError("Israel manifest must contain a non-empty documents list")
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("every Israel manifest document must be a mapping")
        manifest = cls(
            documents=tuple(
                IsraelOpenLawSource.from_mapping(cast(dict[str, Any], row)) for row in rows
            )
        )
        manifest.require_unique_sources()
        return manifest

    def require_unique_sources(self) -> None:
        for field_name in ("source_id", "instrument_slug", "israel_law_id", "source_file"):
            values = [str(getattr(source, field_name)) for source in self.documents]
            duplicates = sorted(value for value in set(values) if values.count(value) > 1)
            if duplicates:
                raise ValueError(f"duplicate Israel {field_name}: {', '.join(duplicates)}")


@dataclass(frozen=True)
class IsraelOpenLawProvision:
    """One document, navigation node, section, or schedule item."""

    citation_path: str
    parent_citation_path: str | None
    kind: str
    label: str
    heading: str | None
    body: str | None
    level: int
    ordinal: int
    metadata: dict[str, Any]


@dataclass(frozen=True)
class IsraelOpenLawDocumentExtractReport:
    """Extraction result for one Israeli statute."""

    source_id: str
    instrument_slug: str
    israel_law_id: str
    section_count: int
    schedule_item_count: int
    navigation_count: int
    provisions_written: int
    source_path: Path
    sha256: str


@dataclass(frozen=True)
class IsraelOpenLawExtractReport:
    """Artifact report for one Israeli OpenLaw extraction run."""

    jurisdiction: str
    document_class: str
    version: str
    document_count: int
    section_count: int
    schedule_item_count: int
    navigation_count: int
    provisions_written: int
    inventory_path: Path
    provisions_path: Path
    coverage_path: Path
    coverage: ProvisionCoverageReport
    source_paths: tuple[Path, ...]
    document_reports: tuple[IsraelOpenLawDocumentExtractReport, ...]


@dataclass
class _PendingProvision:
    citation_path: str
    parent_citation_path: str | None
    kind: str
    label: str
    level: int
    ordinal: int
    heading: str | None = None
    blocks: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    editorial_notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class _PreparedSource:
    source: IsraelOpenLawSource
    content: bytes
    provisions: tuple[IsraelOpenLawProvision, ...]
    section_count: int
    schedule_item_count: int
    navigation_count: int


def extract_israel_openlaw(
    store: CorpusArtifactStore,
    *,
    version: str,
    manifest_path: str | Path,
    source_dir: str | Path,
) -> IsraelOpenLawExtractReport:
    """Verify and extract hash-pinned Israeli consolidated statutes.

    Every manifest row, input hash, and structural count is validated before the
    first artifact is written, so a drifted snapshot fails loudly instead of
    landing a plausible-looking partial scope.
    """
    if not str(version).strip():
        raise ValueError("Israel extraction version must not be empty")
    manifest = IsraelOpenLawManifest.load(manifest_path)
    source_root = Path(source_dir).resolve()
    if not source_root.is_dir():
        raise ValueError(f"Israel source directory does not exist: {source_root}")

    prepared: list[_PreparedSource] = []
    for source in manifest.documents:
        source_path = (source_root / source.source_file).resolve()
        try:
            source_path.relative_to(source_root)
        except ValueError as exc:
            raise ValueError(
                f"Israel source path escapes source directory: {source.source_file!r}"
            ) from exc
        if not source_path.is_file():
            raise ValueError(f"Israel source file does not exist: {source_path}")
        content = source_path.read_bytes()
        actual_sha256 = hashlib.sha256(content).hexdigest()
        if actual_sha256 != source.sha256:
            raise ValueError(
                f"Israel SHA-256 mismatch for {source.source_id}: "
                f"expected {source.sha256}, got {actual_sha256}"
            )
        provisions = parse_israel_openlaw_html(content, source=source)
        counts = _kind_counts(provisions)
        _require_expected_counts(source, counts)
        prepared.append(
            _PreparedSource(
                source=source,
                content=content,
                provisions=provisions,
                section_count=counts["section"],
                schedule_item_count=counts["schedule-item"],
                navigation_count=counts["part"]
                + counts["chapter"]
                + counts["sign"]
                + counts["schedule"],
            )
        )

    records: list[ProvisionRecord] = []
    inventory: list[SourceInventoryItem] = []
    source_paths: list[Path] = []
    document_reports: list[IsraelOpenLawDocumentExtractReport] = []
    for item in prepared:
        source = item.source
        relative_name = f"openlaw/{source.source_file}"
        artifact_path = store.source_path(
            ISRAEL_OPENLAW_JURISDICTION,
            ISRAEL_OPENLAW_DOCUMENT_CLASS,
            version,
            relative_name,
        )
        written_sha256 = store.write_bytes(artifact_path, item.content)
        if written_sha256 != source.sha256:
            raise RuntimeError(
                f"written Israel source hash changed for {source.source_id}: {written_sha256}"
            )
        source_paths.append(artifact_path)
        source_key = (
            f"sources/{ISRAEL_OPENLAW_JURISDICTION}/{ISRAEL_OPENLAW_DOCUMENT_CLASS}/"
            f"{version}/{relative_name}"
        )
        document_id = deterministic_provision_id(source.document_citation_path, version)
        for provision in item.provisions:
            metadata = {**_source_metadata(source), **provision.metadata}
            inventory.append(
                SourceInventoryItem(
                    citation_path=provision.citation_path,
                    source_url=source.source_url,
                    source_path=source_key,
                    source_format=ISRAEL_OPENLAW_SOURCE_FORMAT,
                    sha256=source.sha256,
                    metadata=metadata,
                )
            )
            citation_label = _citation_label(source, provision)
            records.append(
                ProvisionRecord(
                    id=deterministic_provision_id(provision.citation_path, version),
                    jurisdiction=ISRAEL_OPENLAW_JURISDICTION,
                    document_class=ISRAEL_OPENLAW_DOCUMENT_CLASS,
                    citation_path=provision.citation_path,
                    body=provision.body,
                    heading=provision.heading,
                    citation_label=citation_label,
                    version=version,
                    source_url=source.source_url,
                    source_path=source_key,
                    source_id=f"he.wikisource.org:openlaw:{source.instrument_slug}",
                    source_format=ISRAEL_OPENLAW_SOURCE_FORMAT,
                    source_document_id=document_id,
                    source_as_of=source.source_as_of,
                    expression_date=source.expression_date,
                    parent_citation_path=provision.parent_citation_path,
                    parent_id=(
                        deterministic_provision_id(provision.parent_citation_path, version)
                        if provision.parent_citation_path
                        else None
                    ),
                    level=provision.level,
                    ordinal=provision.ordinal,
                    kind=provision.kind,
                    language=source.language,
                    legal_identifier=citation_label,
                    identifiers={
                        "knesset.gov.il:israel_law_id": source.israel_law_id,
                        "he.wikisource.org:page": source.page_title,
                        "openlaw:instrument": source.instrument_slug,
                        "openlaw:source_id": source.source_id,
                        f"openlaw:{provision.kind}": provision.label,
                    },
                    metadata=metadata,
                )
            )
        document_reports.append(
            IsraelOpenLawDocumentExtractReport(
                source_id=source.source_id,
                instrument_slug=source.instrument_slug,
                israel_law_id=source.israel_law_id,
                section_count=item.section_count,
                schedule_item_count=item.schedule_item_count,
                navigation_count=item.navigation_count,
                provisions_written=len(item.provisions),
                source_path=artifact_path,
                sha256=written_sha256,
            )
        )

    _require_unique_citations(records)
    inventory_path = store.inventory_path(
        ISRAEL_OPENLAW_JURISDICTION, ISRAEL_OPENLAW_DOCUMENT_CLASS, version
    )
    provisions_path = store.provisions_path(
        ISRAEL_OPENLAW_JURISDICTION, ISRAEL_OPENLAW_DOCUMENT_CLASS, version
    )
    coverage_path = store.coverage_path(
        ISRAEL_OPENLAW_JURISDICTION, ISRAEL_OPENLAW_DOCUMENT_CLASS, version
    )
    store.write_inventory(inventory_path, inventory)
    store.write_provisions(provisions_path, records)
    coverage = compare_provision_coverage(
        tuple(inventory),
        tuple(records),
        jurisdiction=ISRAEL_OPENLAW_JURISDICTION,
        document_class=ISRAEL_OPENLAW_DOCUMENT_CLASS,
        version=version,
    )
    if not coverage.complete:
        raise RuntimeError("Israel extraction produced incomplete provision coverage")
    store.write_json(coverage_path, coverage.to_mapping())

    return IsraelOpenLawExtractReport(
        jurisdiction=ISRAEL_OPENLAW_JURISDICTION,
        document_class=ISRAEL_OPENLAW_DOCUMENT_CLASS,
        version=version,
        document_count=len(document_reports),
        section_count=sum(report.section_count for report in document_reports),
        schedule_item_count=sum(report.schedule_item_count for report in document_reports),
        navigation_count=sum(report.navigation_count for report in document_reports),
        provisions_written=len(records),
        inventory_path=inventory_path,
        provisions_path=provisions_path,
        coverage_path=coverage_path,
        coverage=coverage,
        source_paths=tuple(source_paths),
        document_reports=tuple(document_reports),
    )


def parse_israel_openlaw_html(
    html: str | bytes,
    *,
    source: IsraelOpenLawSource,
) -> tuple[IsraelOpenLawProvision, ...]:
    """Parse one ספר החוקים הפתוח consolidation into document-order provisions."""
    soup = BeautifulSoup(html, "lxml")
    roots = soup.select("div#law-content")
    if len(roots) != 1:
        raise ValueError(
            f"Israel source {source.source_id} must contain exactly one "
            f"div#law-content, got {len(roots)}"
        )
    root = roots[0]
    publication_history = _require_source_identity(root, source)

    document_path = source.document_citation_path
    parsed: list[IsraelOpenLawProvision] = []
    parsed.append(
        IsraelOpenLawProvision(
            citation_path=document_path,
            parent_citation_path=None,
            kind="document",
            label=source.israel_law_id,
            heading=source.title,
            body=publication_history or source.title,
            level=0,
            ordinal=0,
            metadata=_document_metadata(soup, source, publication_history),
        )
    )

    # Navigation context: kind -> (citation_path, level).  A new node at one
    # level clears every deeper level.
    context: dict[str, tuple[str, int]] = {}
    counters = {"part": 0, "chapter": 0, "sign": 0}
    section_ordinal = 0
    schedule_item_ordinal = 0
    seen_section_idents: dict[str, int] = {}
    pending: _PendingProvision | None = None
    pending_sub_item: str | None = None
    last_anchor_was_provision = False

    def deepest() -> tuple[str, int]:
        for kind in ("sign", "chapter", "schedule", "part"):
            if kind in context:
                return context[kind]
        return document_path, 0

    def clear_deeper(level: int) -> None:
        for kind in [k for k, (_, node_level) in context.items() if node_level >= level]:
            del context[kind]

    def flush() -> None:
        nonlocal pending, pending_sub_item, last_anchor_was_provision
        pending_sub_item = None
        last_anchor_was_provision = False
        if pending is None:
            return
        metadata = dict(pending.metadata)
        if pending.editorial_notes:
            metadata["editorial_notes"] = list(pending.editorial_notes)
        body = _joined_body(pending.blocks)
        if body is None and pending.kind in _NAV_LEVELS:
            body = pending.heading
        parsed.append(
            IsraelOpenLawProvision(
                citation_path=pending.citation_path,
                parent_citation_path=pending.parent_citation_path,
                kind=pending.kind,
                label=pending.label,
                heading=pending.heading,
                body=body,
                level=pending.level,
                ordinal=pending.ordinal,
                metadata=metadata,
            )
        )
        pending = None

    for node in root.children:
        if not isinstance(node, Tag):
            continue
        classes = _classes(node)

        if node.name in {"h1", "h2", "h3"}:
            if "law-title" in classes:
                continue
            heading = _inline_text(node)
            flush()
            if node.name == "h1":
                clear_deeper(_NAV_LEVELS["part"])
                counters["part"] += 1
                counters["chapter"] = 0
                counters["sign"] = 0
                path = f"{document_path}/part-{counters['part']}"
                pending = _PendingProvision(
                    citation_path=path,
                    parent_citation_path=document_path,
                    kind="part",
                    label=str(counters["part"]),
                    level=_NAV_LEVELS["part"],
                    ordinal=counters["part"],
                    heading=heading,
                    metadata={"raw_marker": heading},
                )
                context["part"] = (path, _NAV_LEVELS["part"])
                continue
            if node.name == "h2":
                clear_deeper(_NAV_LEVELS["chapter"])
                counters["sign"] = 0
                if heading == _TABLE_OF_CONTENTS_HEADING:
                    # The rendered table of contents is navigation chrome, not law.
                    continue
                schedule = _SCHEDULE_HEADING_RE.match(heading)
                if schedule is not None:
                    ident = _strip_hebrew_punctuation(schedule.group("ident"))
                    path = f"{document_path}/schedule-{israeli_ident_slug(ident)}"
                    pending = _PendingProvision(
                        citation_path=path,
                        parent_citation_path=document_path,
                        kind="schedule",
                        label=ident,
                        level=_NAV_LEVELS["schedule"],
                        ordinal=0,
                        heading=heading,
                        metadata={"raw_marker": heading, "printed_identifier": ident},
                    )
                    context["schedule"] = (path, _NAV_LEVELS["schedule"])
                    continue
                counters["chapter"] += 1
                parent_path = context["part"][0] if "part" in context else document_path
                path = f"{parent_path}/chapter-{counters['chapter']}"
                pending = _PendingProvision(
                    citation_path=path,
                    parent_citation_path=parent_path,
                    kind="chapter",
                    label=str(counters["chapter"]),
                    level=_NAV_LEVELS["chapter"],
                    ordinal=counters["chapter"],
                    heading=heading,
                    metadata={"raw_marker": heading},
                )
                context["chapter"] = (path, _NAV_LEVELS["chapter"])
                continue
            clear_deeper(_NAV_LEVELS["sign"])
            counters["sign"] += 1
            parent_path, _ = deepest()
            path = f"{parent_path}/sign-{counters['sign']}"
            pending = _PendingProvision(
                citation_path=path,
                parent_citation_path=parent_path,
                kind="sign",
                label=str(counters["sign"]),
                level=_NAV_LEVELS["sign"],
                ordinal=counters["sign"],
                heading=heading,
                metadata={"raw_marker": heading},
            )
            context["sign"] = (path, _NAV_LEVELS["sign"])
            continue

        if node.name != "div":
            continue

        if any(name.startswith("law-number") for name in classes) and node.get("id"):
            anchor_id = unicodedata.normalize("NFC", str(node["id"]))
            label = _inline_text(node).rstrip(".").strip()
            if anchor_id.startswith(_SECTION_ANCHOR_PREFIX):
                ident = anchor_id[len(_SECTION_ANCHOR_PREFIX) :]
                if "." in ident:
                    # Sub-item anchor (סעיף_2.1): its text belongs to the open
                    # section.  Splitting here is the false-split failure mode.
                    if pending is None or pending.kind != "section":
                        raise ValueError(
                            f"Israel source {source.source_id} has sub-item anchor "
                            f"{anchor_id!r} outside a section"
                        )
                    if label:
                        raise ValueError(
                            f"Israel source {source.source_id} sub-item anchor "
                            f"{anchor_id!r} carries a printed label {label!r}"
                        )
                    pending_sub_item = ident
                    last_anchor_was_provision = False
                    continue
                if not label:
                    raise ValueError(
                        f"Israel source {source.source_id} section anchor "
                        f"{anchor_id!r} has no printed label"
                    )
                flush()
                occurrence = seen_section_idents.get(ident, 0) + 1
                seen_section_idents[ident] = occurrence
                slug = israeli_ident_slug(ident)
                if occurrence == 1:
                    path = f"{document_path}/section-{slug}"
                else:
                    if ident not in source.alternate_version_sections:
                        raise ValueError(
                            f"Israel source {source.source_id} repeats section {ident!r} "
                            "without declaring it in alternate_version_sections"
                        )
                    path = f"{document_path}/section-{slug}-alt{occurrence}"
                section_ordinal += 1
                parent_path, parent_level = deepest()
                metadata: dict[str, Any] = {
                    "printed_identifier": ident,
                    "printed_label": label,
                    "anchor_id": anchor_id,
                }
                if _strip_hebrew_punctuation(label) != ident:
                    # OpenLaw prints "57א" against id סעיף_57ג; the anchor wins.
                    metadata["printed_label_mismatch"] = True
                if occurrence > 1:
                    metadata["alternate_version"] = True
                    metadata["alternate_version_index"] = occurrence
                    metadata["alternate_of"] = f"{document_path}/section-{slug}"
                pending = _PendingProvision(
                    citation_path=path,
                    parent_citation_path=parent_path,
                    kind="section",
                    label=ident,
                    level=parent_level + 1,
                    ordinal=section_ordinal,
                    metadata=metadata,
                )
                last_anchor_was_provision = True
                continue

            if anchor_id.startswith(_SCHEDULE_ANCHOR_PREFIX):
                if _SCHEDULE_ITEM_INFIX not in anchor_id:
                    raise ValueError(
                        f"Israel source {source.source_id} has unrecognized schedule anchor "
                        f"{anchor_id!r}"
                    )
                schedule_ident, item_ident = anchor_id[len(_SCHEDULE_ANCHOR_PREFIX) :].split(
                    _SCHEDULE_ITEM_INFIX, 1
                )
                if "schedule" not in context:
                    raise ValueError(
                        f"Israel source {source.source_id} has schedule item {anchor_id!r} "
                        "outside a schedule heading"
                    )
                schedule_path = context["schedule"][0]
                expected_path = f"{document_path}/schedule-{israeli_ident_slug(schedule_ident)}"
                if schedule_path != expected_path:
                    raise ValueError(
                        f"Israel source {source.source_id} schedule item {anchor_id!r} "
                        f"does not belong to the open schedule {schedule_path!r}"
                    )
                flush()
                schedule_item_ordinal += 1
                path = f"{schedule_path}/item-{israeli_ident_slug(item_ident)}"
                pending = _PendingProvision(
                    citation_path=path,
                    parent_citation_path=schedule_path,
                    kind="schedule-item",
                    label=item_ident,
                    level=_NAV_LEVELS["schedule"] + 1,
                    ordinal=schedule_item_ordinal,
                    metadata={
                        "printed_identifier": item_ident,
                        "printed_label": label,
                        "anchor_id": anchor_id,
                        "schedule_identifier": schedule_ident,
                    },
                )
                last_anchor_was_provision = True
                continue

            raise ValueError(
                f"Israel source {source.source_id} has unrecognized anchor id {anchor_id!r}"
            )

        if "law-desc" in classes:
            heading, amendment_history = _split_description(node)
            if pending_sub_item is not None:
                if pending is None:
                    raise ValueError(
                        f"Israel source {source.source_id} has a sub-item description "
                        "outside a section"
                    )
                sub_items = cast(
                    list[dict[str, str]], pending.metadata.setdefault("sub_item_headings", [])
                )
                entry = {"identifier": pending_sub_item}
                if heading:
                    entry["heading"] = heading
                if amendment_history:
                    entry["amendment_history"] = amendment_history
                sub_items.append(entry)
                continue
            if pending is None or not last_anchor_was_provision:
                continue
            pending.heading = heading or None
            if amendment_history:
                pending.metadata["amendment_history"] = amendment_history
            if heading:
                origin = _ORIGIN_MARKER_RE.search(heading)
                if origin is not None:
                    pending.metadata["consolidation_origin_marker"] = origin.group("marker")
            last_anchor_was_provision = False
            continue

        if "law-main" in classes:
            statutory, notes = _render_law_main(node)
            if pending is None:
                if statutory:
                    raise ValueError(
                        f"Israel source {source.source_id} has statutory text before the "
                        "first structural marker"
                    )
                continue
            if statutory is None:
                status = _status_marker(notes)
                if status is not None and not pending.blocks:
                    statutory, status_word = status
                    pending.metadata["status_marker"] = status_word
                    pending.metadata["operative"] = False
            if statutory:
                pending.blocks.append(statutory)
            pending.editorial_notes.extend(notes)
            last_anchor_was_provision = False
            continue

    flush()
    parsed = _mark_alternate_bases(parsed)
    _require_unique_parsed_citations(parsed, source.source_id)
    return tuple(parsed)


def _required_text(data: Mapping[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Israel manifest requires a non-empty {field_name}")
    return unicodedata.normalize("NFC", value.strip())


def _required_iso_date(data: Mapping[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Israel manifest requires a quoted ISO date for {field_name}")
    return date.fromisoformat(value.strip()).isoformat()


def _required_count(data: Mapping[str, Any], field_name: str) -> int:
    value = data.get(field_name)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"Israel manifest requires a non-negative integer {field_name}")
    return value


def _classes(tag: Tag) -> list[str]:
    """Return a tag's CSS classes as a list, whatever bs4 hands back."""
    value = tag.get("class")
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    return list(value)


def _strip_hebrew_punctuation(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    for char in _HEBREW_PUNCTUATION:
        normalized = normalized.replace(char, "")
    return normalized.strip()


def _require_source_identity(root: Tag, source: IsraelOpenLawSource) -> str | None:
    """Check the page's own title and Knesset law id, and return its header line."""
    title_node = root.select_one("h1.law-title")
    if title_node is None:
        raise ValueError(f"Israel source {source.source_id} has no h1.law-title")
    title = _inline_text(title_node)
    if title != source.title:
        raise ValueError(
            f"Israel source {source.source_id} title mismatch: "
            f"manifest {source.title!r}, page {title!r}"
        )
    header = _publication_history(root)
    if header is None or not header.startswith(source.israel_law_id):
        raise ValueError(
            f"Israel source {source.source_id} does not open with IsraelLawID "
            f"{source.israel_law_id}"
        )
    return header


def _publication_history(root: Tag) -> str | None:
    """Return the publication-history line OpenLaw prints under the title rule."""
    separator = root.select_one("hr.law-separator")
    if separator is None:
        return None
    for sibling in separator.next_siblings:
        if not isinstance(sibling, Tag):
            continue
        if sibling.name in {"h1", "h2", "h3"}:
            return None
        if sibling.name != "div" or sibling.get("class"):
            continue
        text = _inline_text(sibling)
        if text:
            return text
    return None


def _document_metadata(
    soup: BeautifulSoup,
    source: IsraelOpenLawSource,
    publication_history: str | None,
) -> dict[str, Any]:
    metadata: dict[str, Any] = {"wikisource_page": source.page_title}
    if publication_history:
        metadata["publication_history"] = publication_history
    revision = soup.find(attrs={"id": "footer-info-lastmod"})
    if isinstance(revision, Tag):
        metadata["wikisource_last_edited_note"] = _inline_text(revision)
    return metadata


def _split_description(node: Tag) -> tuple[str, str | None]:
    """Split a ``div.law-desc`` into its heading and its amendment-history note."""
    notes = [_inline_text(note) for note in node.find_all("span", class_="law-note")]
    working = _without(node, lambda tag: "law-note" in _classes(tag))
    heading = _inline_text(working)
    amendment_history = " ".join(note for note in notes if note) or None
    return heading, amendment_history


def _render_law_main(block: Tag) -> tuple[str | None, list[str]]:
    """Return (statutory text, editorial notes) for one ``div.law-main``.

    ``span.law-note`` is always editorial.  A block whose only remaining content
    is a table introduced by such a note — OpenLaw's historical rate tables under
    §121, for instance — is editorial in full.
    """
    notes = [
        text
        for text in (_inline_text(note) for note in block.find_all("span", class_="law-note"))
        if text
    ]
    working = _without(block, lambda tag: "law-note" in _classes(tag))
    statutory = _render_law_main_text(working)
    if statutory is None:
        return None, notes
    if notes:
        untabled = _without(working, lambda tag: tag.name == "table")
        if _render_law_main_text(untabled) is None:
            return None, notes
    return statutory, notes


def _status_marker(notes: Sequence[str]) -> tuple[str, str] | None:
    """Return (line, status) when a note-only block is a section status line."""
    if len(notes) != 1:
        return None
    match = _STATUS_MARKER_RE.match(notes[0])
    if match is None:
        return None
    return notes[0], match.group("status")


def _without(node: Tag, predicate: Any) -> Tag:
    """Return a detached copy of ``node`` with matching descendants removed."""
    working = node.__copy__()
    for tag in list(working.find_all(True)):
        if tag.decomposed or tag.attrs is None:
            # Already destroyed together with a matching ancestor.
            continue
        if predicate(tag):
            tag.decompose()
    return working


def _render_law_main_text(block: Tag) -> str | None:
    """Render one law-main body, pairing ``law-numberN`` markers with their text."""
    lines: list[str] = []
    markers: list[str] = []
    for child in block.children:
        if isinstance(child, NavigableString):
            text = _render_text(str(child))
            if text:
                lines.append(text)
            continue
        if not isinstance(child, Tag):
            continue
        classes = _classes(child)
        if any(name.startswith("law-number") for name in classes):
            marker = _inline_text(child)
            if marker:
                markers.append(marker)
            continue
        text = _render_block(child)
        if not text:
            continue
        if markers:
            text = f"{' '.join(markers)} {text}"
            markers = []
        lines.append(text)
    if markers:
        lines.append(" ".join(markers))
    return _joined_body(lines)


def _collapse_spaces(value: str) -> str:
    return _SPACE_BEFORE_PUNCTUATION_RE.sub("", value)


def _inline_text(tag: Tag) -> str:
    raw = (
        tag.get_text("", strip=False).replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    )
    return _collapse_spaces(
        unicodedata.normalize("NFC", _ASCII_WHITESPACE_RE.sub(" ", raw.replace("\n", " ")).strip())
    )


def _render_block(block: Tag) -> str:
    if block.name == "table":
        return _render_table(block)
    raw = "".join(_render_element(child) for child in block.children)
    return _render_text(raw)


def _render_element(node: PageElement) -> str:
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    if node.name == "br":
        return "\n"
    if node.name == "table":
        return _render_table(node)
    if node.name in {"div", "p"}:
        inner = "".join(_render_element(child) for child in node.children)
        return f"\n{inner}\n"
    return "".join(_render_element(child) for child in node.children)


def _render_table(table: Tag) -> str:
    rendered_rows: list[str] = []
    for row in table.find_all("tr"):
        cells = row.find_all(["td", "th"], recursive=False)
        if not cells:
            continue
        rendered_cells = [
            _render_text("".join(_render_element(child) for child in cell.children))
            for cell in cells
        ]
        rendered_rows.append(" | ".join(cell for cell in rendered_cells if cell))
    return _joined_body(rendered_rows) or ""


def _render_text(raw: str) -> str:
    raw = unicodedata.normalize("NFC", raw)
    raw = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    lines = [
        _collapse_spaces(_ASCII_WHITESPACE_RE.sub(" ", line).strip()) for line in raw.split("\n")
    ]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    compacted: list[str] = []
    for line in lines:
        if line or not compacted or compacted[-1]:
            compacted.append(line)
    return "\n".join(compacted)


def _joined_body(blocks: Sequence[str]) -> str | None:
    values = [value for value in blocks if value.strip()]
    return "\n".join(values) if values else None


def _kind_counts(provisions: Sequence[IsraelOpenLawProvision]) -> dict[str, int]:
    counts = {
        "document": 0,
        "part": 0,
        "chapter": 0,
        "sign": 0,
        "schedule": 0,
        "section": 0,
        "schedule-item": 0,
    }
    for provision in provisions:
        if provision.kind not in counts:
            raise ValueError(f"unexpected Israel provision kind: {provision.kind!r}")
        counts[provision.kind] += 1
    return counts


def _require_expected_counts(source: IsraelOpenLawSource, counts: Mapping[str, int]) -> None:
    expectations = (
        ("section", source.expected_section_count, "expected_section_count"),
        ("schedule-item", source.expected_schedule_item_count, "expected_schedule_item_count"),
        ("part", source.expected_part_count, "expected_part_count"),
        ("chapter", source.expected_chapter_count, "expected_chapter_count"),
        ("sign", source.expected_sign_count, "expected_sign_count"),
    )
    for kind, expected, field_name in expectations:
        if counts[kind] != expected:
            raise ValueError(
                f"Israel {field_name} mismatch for {source.source_id}: "
                f"expected {expected}, got {counts[kind]}"
            )


def _mark_alternate_bases(
    provisions: Sequence[IsraelOpenLawProvision],
) -> list[IsraelOpenLawProvision]:
    """Flag the base section of every alternate-version pair."""
    bases = {
        str(provision.metadata["alternate_of"])
        for provision in provisions
        if provision.metadata.get("alternate_version")
    }
    if not bases:
        return list(provisions)
    marked: list[IsraelOpenLawProvision] = []
    for provision in provisions:
        if provision.citation_path in bases:
            metadata = {**provision.metadata, "has_alternate_versions": True}
            marked.append(
                IsraelOpenLawProvision(
                    citation_path=provision.citation_path,
                    parent_citation_path=provision.parent_citation_path,
                    kind=provision.kind,
                    label=provision.label,
                    heading=provision.heading,
                    body=provision.body,
                    level=provision.level,
                    ordinal=provision.ordinal,
                    metadata=metadata,
                )
            )
            continue
        marked.append(provision)
    return marked


def _citation_label(source: IsraelOpenLawSource, provision: IsraelOpenLawProvision) -> str:
    if provision.kind == "document":
        return source.title
    if provision.kind == "section":
        suffix = ""
        if provision.metadata.get("alternate_version"):
            suffix = f" (נוסח חלופי {provision.metadata['alternate_version_index']})"
        return f"{source.title}, סעיף {provision.label}{suffix}"
    if provision.kind == "schedule-item":
        schedule = provision.metadata.get("schedule_identifier", "")
        return f"{source.title}, לוח {schedule} פרט {provision.label}"
    if provision.heading:
        return f"{source.title}, {provision.heading}"
    return f"{source.title}, {provision.kind} {provision.label}"


def _source_metadata(source: IsraelOpenLawSource) -> dict[str, Any]:
    return {
        "source_id": source.source_id,
        "instrument_slug": source.instrument_slug,
        "israel_law_id": source.israel_law_id,
        "title": source.title,
        "title_en": source.title_en,
        "source_authority": ISRAEL_OPENLAW_SOURCE_AUTHORITY,
        "source_tier": source.source_tier,
        "knesset_full_text_link_verified": (source.source_tier == "consolidation-knesset-linked"),
        "source_language": source.language,
        "consolidated_expression": True,
        "expression_date_basis": source.expression_date_basis,
        "expected_section_count": source.expected_section_count,
        "verified_source_sha256": source.sha256,
        "editorial_apparatus_removed": True,
    }


def _require_unique_parsed_citations(
    provisions: Sequence[IsraelOpenLawProvision],
    source_id: str,
) -> None:
    paths = [provision.citation_path for provision in provisions]
    duplicates = sorted(path for path in set(paths) if paths.count(path) > 1)
    if duplicates:
        raise ValueError(
            f"Israel source {source_id} produced duplicate citation paths: "
            f"{', '.join(duplicates[:5])}"
        )


def _require_unique_citations(records: Sequence[ProvisionRecord]) -> None:
    paths = [record.citation_path for record in records]
    duplicates = sorted(path for path in set(paths) if paths.count(path) > 1)
    if duplicates:
        raise ValueError(
            f"Israel extraction produced duplicate citation paths: {', '.join(duplicates[:5])}"
        )
