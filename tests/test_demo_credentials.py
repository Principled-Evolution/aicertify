"""Tests that `aicertify demo` does not spend the caller's money uninvited.

The README advertises the demo as needing no API keys, and that quietly stopped
being true for anyone with `OPENAI_API_KEY` exported. The LLM-judged evaluators
activate off the presence of that variable, so DeepEval would make a billable
completion call per interaction. A run was observed blocked on those calls for
over 19 minutes without producing a report.

The demo therefore hides the variable for the duration of its own run unless
`--with-llm-metrics` is passed. What matters is that the caller's environment is
left exactly as it was found, including when the run raises.
"""

from __future__ import annotations

import asyncio
import inspect
import os

import pytest

from aicertify._demo import runner


class TestTheOptInExists:
    def test_run_demo_takes_with_llm_metrics(self):
        params = inspect.signature(runner.run_demo).parameters
        assert "with_llm_metrics" in params

    def test_it_defaults_to_off(self):
        """Off by default is the whole point: no uninvited billable calls."""
        default = (
            inspect.signature(runner.run_demo).parameters["with_llm_metrics"].default
        )
        assert default is False

    def test_the_cli_exposes_the_flag(self):
        from aicertify.cli import _build_parser

        parser = _build_parser()
        # argparse offers no public API for reaching a subparser's options, so
        # the rendered help is the accessible surface.
        help_text = parser.format_help()
        assert "demo" in help_text

        sub = next(
            action
            for action in parser._actions
            if isinstance(action, __import__("argparse")._SubParsersAction)
        )
        demo_help = sub.choices["demo"].format_help()
        assert "--with-llm-metrics" in demo_help
        assert "billable" in demo_help


class TestTheEnvironmentIsRestored:
    """The demo mutates os.environ, so it must put it back.

    Each test drives run_demo far enough to reach the credential handling and
    then lets it fail, which exercises the `finally` path rather than the happy
    one. Failing early is deliberate: the point is that the restore happens even
    when the run does not complete.
    """

    @staticmethod
    def _run_and_fail_early(monkeypatch, **kwargs) -> None:
        # Make the OPA check fail immediately so we return before doing work,
        # but after the credential gate.
        monkeypatch.setattr(runner, "opa_binary_path", lambda: "/nonexistent/opa")
        monkeypatch.setattr(
            runner,
            "bundled_policy_path",
            lambda policy: (_ for _ in ()).throw(RuntimeError("stop here")),
        )
        with pytest.raises(BaseException):
            asyncio.run(runner.run_demo(**kwargs))

    def test_an_existing_key_is_restored_after_the_run(self, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-sentinel-value")
        self._run_and_fail_early(monkeypatch)
        assert (
            os.environ.get("OPENAI_API_KEY") == "sk-sentinel-value"
        ), "the demo removed the caller's key and did not put it back"

    def test_no_key_is_invented_when_none_was_set(self, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        self._run_and_fail_early(monkeypatch)
        assert "OPENAI_API_KEY" not in os.environ

    def test_the_key_is_left_alone_when_opted_in(self, monkeypatch):
        """--with-llm-metrics means the caller asked for the billable path."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-sentinel-value")
        self._run_and_fail_early(monkeypatch, with_llm_metrics=True)
        assert os.environ.get("OPENAI_API_KEY") == "sk-sentinel-value"
