import json
import re
from pathlib import Path

import pytest
import yaml

from axiom_corpus.corpus.artifacts import CorpusArtifactStore
from axiom_corpus.corpus.eli import extract_eli_documents, extract_lexdania_sections
from axiom_corpus.corpus.io import load_provisions, load_source_inventory

FIXTURES = Path(__file__).parent / "fixtures" / "eli"


@pytest.mark.parametrize(
    ("fixture_name", "expected_labels"),
    [
        (
            "dk-retsinfo-2013-9724-principafgoerelse.lexdania.xml",
            (
                "resume",
                "tekst",
                "tekst/1-baggrund-for-at-behandle-sagen",
                "tekst/2-reglerne",
                "tekst/3-andre-principafgoerelser",
                "tekst/4-den-konkrete-afgoerelse",
            ),
        ),
        (
            "dk-retsinfo-2023-9456-principmeddelelse.lexdania.xml",
            (
                "resume",
                "tekst",
                "tekst/baggrund-for-at-behandle-sagerne-principielt",
                "tekst/reglerne",
                "tekst/love-og-bekendtgoerelser",
                "tekst/praksis",
                "tekst/de-konkrete-afgoerelser",
            ),
        ),
        (
            "dk-retsinfo-2014-9267-vejledning.lexdania.xml",
            ("tekst",),
        ),
    ],
)
def test_extract_lexdania_routes_prose_fixtures_and_extracts_sections(
    fixture_name: str,
    expected_labels: tuple[str, ...],
) -> None:
    sections = extract_lexdania_sections((FIXTURES / fixture_name).read_bytes())

    assert tuple(section.label for section in sections) == expected_labels
    assert tuple(section.metadata["citation_suffix"] for section in sections) == (
        expected_labels
    )
    assert all(section.body for section in sections)
    for section in sections:
        if section.label.startswith("tekst/"):
            assert section.body.startswith(section.heading)

    schema_path = Path(__file__).resolve().parents[1] / "schema" / "citation-path.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    citation_pattern = re.compile(schema["$defs"]["citation_path"]["pattern"])
    root_path = "dk/guidance/retsinfo-prose-fixture"
    assert all(
        citation_pattern.fullmatch(f"{root_path}/{section.label}")
        for section in sections
    )


def test_extract_lexdania_prose_collapses_empty_paragraphs_and_renders_tables() -> None:
    xml = b"""\
        <Dokument id="prose-body-rules">
          <TitelGruppe>Artificial prose body rules</TitelGruppe>
          <DokumentIndhold>
            <Resume>
              <Exitus>
                <Linea>First <Char>line</Char></Linea>
                <Linea>second line</Linea>
              </Exitus>
              <Exitus />
              <Exitus />
              <Exitus><Linea>Last paragraph</Linea></Exitus>
            </Resume>
            <TekstGruppe>
              <Exitus><Table>
                <Tr><Td>A</Td><Td>B</Td></Tr>
                <Tr><Td>C</Td><Td>D</Td></Tr>
              </Table></Exitus>
              <Exitus />
              <Exitus><Linea>After table</Linea></Exitus>
            </TekstGruppe>
          </DokumentIndhold>
        </Dokument>
    """

    resume, text = extract_lexdania_sections(xml)

    assert resume.body == "First line second line\n\nLast paragraph"
    assert text.body == "A | B\nC | D\n\nAfter table"


def test_extract_lexdania_prose_uses_normalized_itertext_for_inline_punctuation() -> None:
    xml = b"""\
        <Dokument id="prose-inline-punctuation">
          <TitelGruppe>Artificial prose inline punctuation</TitelGruppe>
          <DokumentIndhold><TekstGruppe>
            <Exitus><Linea>A</Linea>, B</Exitus>
          </TekstGruppe></DokumentIndhold>
        </Dokument>
    """

    (text,) = extract_lexdania_sections(xml)

    assert text.body == "A, B"


def test_extract_lexdania_prose_merges_multiple_text_groups_in_document_order() -> None:
    xml = b"""\
        <Dokument id="multiple-text-groups">
          <TitelGruppe>Artificial multiple text groups</TitelGruppe>
          <DokumentIndhold>
            <TekstGruppe><Exitus><Linea>First group</Linea></Exitus></TekstGruppe>
            <TekstGruppe><Exitus><Linea>Second group</Linea></Exitus></TekstGruppe>
          </DokumentIndhold>
        </Dokument>
    """

    (text,) = extract_lexdania_sections(xml)

    assert text.label == "tekst"
    assert text.body == "First group\n\nSecond group"


def test_extract_lexdania_prose_real_table_joins_cells_and_rows() -> None:
    (text,) = extract_lexdania_sections(
        (FIXTURES / "dk-retsinfo-2014-9267-vejledning.lexdania.xml").read_bytes()
    )

    assert (
        "Område – Overenskomstens artikel 1, bogstav a) | 2.\n"
        "Forsikringsperiode – Overenskomstens artikel 1, bogstav f) | 3.\n"
        "Sagligt anvendelsesområde – Overenskomstens artikel 2 | 4."
    ) in text.body


def test_extract_lexdania_prose_sections_stop_before_next_matched_heading() -> None:
    sections = {
        section.label: section
        for section in extract_lexdania_sections(
            (
                FIXTURES / "dk-retsinfo-2023-9456-principmeddelelse.lexdania.xml"
            ).read_bytes()
        )
    }

    assert "Reglerne" in sections["tekst"].body
    assert "Reglerne" not in sections[
        "tekst/baggrund-for-at-behandle-sagerne-principielt"
    ].body
    assert sections["tekst/reglerne"].body == "Reglerne"
    assert "Praksis" not in sections["tekst/love-og-bekendtgoerelser"].body


def test_extract_lexdania_numbered_sections_stop_at_each_observed_heading() -> None:
    sections = {
        section.label: section
        for section in extract_lexdania_sections(
            (
                FIXTURES / "dk-retsinfo-2013-9724-principafgoerelse.lexdania.xml"
            ).read_bytes()
        )
    }

    assert "3. Andre Principafgørelser" not in sections["tekst/2-reglerne"].body
    assert sections["tekst/3-andre-principafgoerelser"].body.startswith(
        "3. Andre Principafgørelser"
    )
    assert "4. Den konkrete afgørelse" not in sections[
        "tekst/3-andre-principafgoerelser"
    ].body


def test_extract_lexdania_prose_collapses_real_consecutive_empty_exitus() -> None:
    sections = extract_lexdania_sections(
        (FIXTURES / "dk-retsinfo-2023-9456-principmeddelelse.lexdania.xml").read_bytes()
    )

    assert "\n\n\n" not in sections[0].body
    assert "\n\n\n" not in sections[1].body


def test_extract_lexdania_existing_shapes_still_route_as_before() -> None:
    consolidation = extract_lexdania_sections(
        (FIXTURES / "dk-lta-2025-603.lexdania.xml").read_bytes()
    )
    centered = extract_lexdania_sections(
        (FIXTURES / "dk-lta-2022-252-amendment-only.lexdania.xml").read_bytes()
    )

    assert len(consolidation) == 24
    assert consolidation[0].label == "paragraf-1"
    assert tuple(section.label for section in centered) == (
        "aendringcentreretparagraf-1",
        "ikraftcentreretparagraf-2",
    )


def test_extract_lexdania_prose_rejects_foreign_direct_element_with_identity() -> None:
    xml = b"""\
        <Dokument id="foreign-prose-element">
          <TitelGruppe>Artificial foreign prose element</TitelGruppe>
          <DokumentIndhold>
            <TekstGruppe><Exitus><Linea>Text</Linea></Exitus></TekstGruppe>
            <Ukendt />
          </DokumentIndhold>
        </Dokument>
    """

    with pytest.raises(ValueError) as caught:
        extract_lexdania_sections(xml)

    message = str(caught.value)
    assert "title='Artificial foreign prose element'" in message
    assert "root_id='foreign-prose-element'" in message
    assert "unknown direct element(s): Ukendt" in message


@pytest.mark.parametrize(
    "other_shape",
    [
        '<Paragraf localId="1"><Explicatus>standard</Explicatus></Paragraf>',
        '<AendringCentreretParagraf localId="1">centered</AendringCentreretParagraf>',
    ],
)
def test_extract_lexdania_prose_rejects_mixed_direct_shapes(
    other_shape: str,
) -> None:
    xml = f"""\
        <Dokument id="mixed-prose-shape">
          <TitelGruppe>Artificial mixed prose shape</TitelGruppe>
          <DokumentIndhold>
            <TekstGruppe><Exitus><Linea>Text</Linea></Exitus></TekstGruppe>
            {other_shape}
          </DokumentIndhold>
        </Dokument>
    """.encode()

    with pytest.raises(ValueError, match="mixes direct prose"):
        extract_lexdania_sections(xml)


def test_extract_lexdania_prose_rejects_duplicate_template_heading() -> None:
    xml = b"""\
        <Dokument id="duplicate-prose-heading">
          <TitelGruppe>Artificial duplicate prose heading</TitelGruppe>
          <DokumentIndhold><TekstGruppe>
            <Exitus><Linea>Reglerne</Linea></Exitus>
            <Exitus><Linea>First body</Linea></Exitus>
            <Exitus><Linea>REGLERNE</Linea></Exitus>
          </TekstGruppe></DokumentIndhold>
        </Dokument>
    """

    with pytest.raises(ValueError) as caught:
        extract_lexdania_sections(xml)

    message = str(caught.value)
    assert "title='Artificial duplicate prose heading'" in message
    assert "root_id='duplicate-prose-heading'" in message
    assert "repeats prose template heading 'REGLERNE'" in message
    assert "duplicate label 'tekst/reglerne'" in message


def test_extract_eli_prose_writes_guidance_hierarchy_coverage_and_valid_paths(
    tmp_path: Path,
) -> None:
    eli_uri = "https://retsinformation.dk/eli/retsinfo/2023/9456"
    graph_url = "https://example.test/9456.json"
    xml_url = "https://example.test/9456.xml"
    root_path = "dk/guidance/retsinfo-2023-9456"
    manifest = tmp_path / "eli-prose.yaml"
    manifest.write_text(
        yaml.safe_dump(
            {
                "documents": [
                    {
                        "source_id": "dk-retsinfo-2023-9456",
                        "eli_uri": eli_uri,
                        "graph_url": graph_url,
                        "xml_url": xml_url,
                        "jurisdiction": "dk",
                        "document_class": "guidance",
                        "citation_path": root_path,
                        "title": "Ankestyrelsens principmeddelelse 11-23",
                        "language": "da",
                    }
                ]
            }
        )
    )
    graph_bytes = (FIXTURES / "dk-lta-2025-603.jsonld").read_bytes().replace(
        b"https://retsinformation.dk/eli/lta/2025/603",
        eli_uri.encode(),
    )
    xml_bytes = (
        FIXTURES / "dk-retsinfo-2023-9456-principmeddelelse.lexdania.xml"
    ).read_bytes()

    report = extract_eli_documents(
        CorpusArtifactStore(tmp_path / "corpus"),
        manifest_path=manifest,
        version="2023-06-03",
        fetcher={graph_url: graph_bytes, xml_url: xml_bytes}.__getitem__,
    )
    inventory = load_source_inventory(report.inventory_path)
    provisions = load_provisions(report.provisions_path)
    paths = tuple(record.citation_path for record in provisions)
    expected_paths = (
        root_path,
        f"{root_path}/resume",
        f"{root_path}/tekst",
        f"{root_path}/tekst/baggrund-for-at-behandle-sagerne-principielt",
        f"{root_path}/tekst/reglerne",
        f"{root_path}/tekst/love-og-bekendtgoerelser",
        f"{root_path}/tekst/praksis",
        f"{root_path}/tekst/de-konkrete-afgoerelser",
    )

    assert paths == expected_paths
    assert tuple(item.citation_path for item in inventory) == expected_paths
    assert tuple(record.level for record in provisions) == (1, 2, 2, 3, 3, 3, 3, 3)
    text = provisions[2]
    assert all(record.parent_citation_path == text.citation_path for record in provisions[3:])
    assert all(record.parent_id == text.id for record in provisions[3:])
    assert report.block_count == 7
    assert report.provisions_written == 8
    assert report.coverage.complete
    assert report.coverage.provision_count == report.coverage.matched_count == 8

    schema_path = Path(__file__).resolve().parents[1] / "schema" / "citation-path.v1.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    citation_pattern = re.compile(schema["$defs"]["citation_path"]["pattern"])
    assert all(citation_pattern.fullmatch(path) for path in paths)
