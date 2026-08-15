"""Grouped top-level help must stay complete and non-breaking (#471)."""

from __future__ import annotations

import argparse

import pytest

from axiom_corpus.corpus.cli import _COMMAND_GROUPS, build_parser


def _subparsers_action(parser: argparse.ArgumentParser) -> argparse._SubParsersAction:
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    raise AssertionError("no subparsers action on the corpus CLI parser")


def _grouped_names() -> list[str]:
    return [name for _, names in _COMMAND_GROUPS for name in names]


def test_every_command_grouped_exactly_once() -> None:
    grouped = _grouped_names()
    assert len(grouped) == len(set(grouped)), "a command appears in two groups"

    registered = set(_subparsers_action(build_parser()).choices)
    assert set(grouped) == registered, (
        "command groups and registered subcommands diverged; update "
        "_COMMAND_GROUPS in the same change that adds or removes a command "
        f"(missing from groups: {sorted(registered - set(grouped))}; "
        f"stale in groups: {sorted(set(grouped) - registered)})"
    )


def test_help_renders_every_command_under_its_group(capsys: pytest.CaptureFixture[str]) -> None:
    parser = build_parser()
    with pytest.raises(SystemExit) as excinfo:
        parser.parse_args(["--help"])
    assert excinfo.value.code == 0
    out = capsys.readouterr().out

    for title, names in _COMMAND_GROUPS:
        assert f"{title}:" in out
        for name in names:
            assert f"\n  {name}" in out, f"{name} missing from grouped help"
    # The flat alphabetical block is replaced, not duplicated.
    assert out.count("\n  validate-manifest") == 1
    assert "Ungrouped" not in out
    assert "same CLI under two names" in out


def test_help_summaries_survive_the_grouping() -> None:
    # The epilog is built from add_parser(help=...) text via argparse
    # internals; if those internals change shape, fail loudly here rather
    # than silently rendering a bare name list.
    parser = build_parser()
    assert parser.epilog is not None
    assert "Validate a corpus manifest." in parser.epilog


def test_parsing_still_routes_commands() -> None:
    args = build_parser().parse_args(["validate-manifest", "some/path.yaml"])
    assert args.command == "validate-manifest"
    assert callable(args.func)
