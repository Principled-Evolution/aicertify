"""Every command-line flag a README documents must exist.

This exists because two flags drifted in one week and neither was caught.

`--evaluators` was removed in #91 for never having affected a run. The English
README dropped it; the four translations kept documenting it, in four
languages, for a flag that no longer parsed. And `--params` has always existed
and was documented nowhere at all.

Neither shows up in a test run, a lint, or a build. A reader following the
translated README simply gets `unrecognized arguments` and concludes the tool
is broken. So the check belongs somewhere that runs on every commit, which is
here rather than in a workflow step, so it also fails on a laptop.

The reverse direction is deliberately not asserted. A flag missing from a
translation needs a native speaker to add a row, and failing the build until
somebody translates a sentence would either block the release or invite a
machine translation nobody can vouch for. Undocumented flags are reported by
`test_english_readme_documents_every_flag` for English only, where we can
actually write the sentence.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

import pytest

from aicertify.cli import _build_parser

REPO = Path(__file__).resolve().parent.parent
READMES = sorted(REPO.glob("README*.md"))

# A row in a flag table: `| `--flag` | description |`
FLAG_ROW = re.compile(r"^\|\s*`(--[a-z][a-z-]*)`", re.MULTILINE)


def _real_flags() -> set[str]:
    """Every option string the parser accepts, across all subcommands."""
    found: set[str] = set()

    def collect(parser: argparse.ArgumentParser) -> None:
        for action in parser._actions:  # noqa: SLF001 - argparse has no public API
            found.update(opt for opt in action.option_strings if opt.startswith("--"))
            if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
                for sub in action.choices.values():
                    collect(sub)

    collect(_build_parser())
    return found


def test_the_parser_exposes_flags_at_all() -> None:
    """Guards the guard: if introspection breaks, the tests below pass vacuously."""
    flags = _real_flags()
    assert "--contract" in flags, f"parser introspection returned {flags}"
    assert len(flags) > 5


@pytest.mark.parametrize("readme", READMES, ids=lambda p: p.name)
def test_readme_documents_no_flag_that_does_not_exist(readme: Path) -> None:
    documented = set(FLAG_ROW.findall(readme.read_text(encoding="utf-8")))
    if not documented:
        pytest.skip(f"{readme.name} documents no flags")

    unreal = sorted(documented - _real_flags())
    assert not unreal, (
        f"{readme.name} documents {unreal}, which the CLI does not accept. "
        "A reader following it gets 'unrecognized arguments'."
    )


def _flags_of(command: str) -> set[str]:
    """The `--flags` one subcommand accepts."""
    parser = _build_parser()
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            sub = action.choices[command]
            return {
                opt
                for a in sub._actions  # noqa: SLF001
                for opt in a.option_strings
                if opt.startswith("--")
            }
    raise AssertionError(f"no subcommand {command}")


def test_english_readme_documents_every_evaluate_flag() -> None:
    """The flag table documents `evaluate`, so hold it to that command.

    Scoped rather than allow-listed. An allow-list of "flags documented
    elsewhere" is a place to quietly park anything inconvenient, and it grows
    until the check means nothing. `demo`, `init-contract`, `explain` and
    `score-card` carry their own flags and are described in prose, so asserting
    the table lists those too would only invite the exemption.
    """
    readme = REPO / "README.md"
    documented = set(FLAG_ROW.findall(readme.read_text(encoding="utf-8")))

    # --help and --verbose are on every subcommand and are not worth a row.
    missing = sorted(_flags_of("evaluate") - documented - {"--help", "--verbose"})
    assert not missing, (
        f"README.md documents the `evaluate` flag table but omits {missing}. "
        "`--params` was missing from all five READMEs for exactly this reason."
    )
