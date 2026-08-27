"""Tests for the wall-clock bound on LLM-judged content-safety evaluation.

DeepEval's ToxicityMetric is LLM-judged, so `measure()` is a network call. With
no bound, an unreachable or throttled provider hangs the evaluation: a demo run
was observed idle in `select()` inside `deepeval/metrics/toxicity/toxicity.py`
for over 19 minutes, having produced nothing and never returning.

Two properties are asserted, and the second is the subtle one:

* the call is bounded, and a timeout fails *closed* — worst-case toxicity and
  `passed=False`, matching the existing unavailable path. A content-safety check
  that did not complete has established nothing, and reporting it as clean would
  be the same fail-open this library has closed three times in the policies.
* the abandoned worker is a daemon thread. A ThreadPoolExecutor would not do:
  its threads are non-daemon and the interpreter joins them at exit, so a call
  still blocked in the provider would keep the process alive after we had
  stopped waiting for it, defeating the bound entirely.
"""

from __future__ import annotations

import threading
import time

import pytest

from aicertify.evaluators.content_safety_evaluator import (
    DEFAULT_LLM_TIMEOUT_SECONDS,
    ContentSafetyEvaluator,
)


@pytest.fixture
def evaluator():
    """An evaluator that degrades rather than raising when DeepEval is absent."""
    return ContentSafetyEvaluator(
        config={"use_mock_if_unavailable": True, "llm_timeout_seconds": 1}
    )


class TestDefaults:
    def test_there_is_a_default_timeout(self):
        assert DEFAULT_LLM_TIMEOUT_SECONDS > 0

    def test_the_default_is_generous_enough_for_one_completion(self):
        """Too tight and legitimate slow calls fail; too loose and it hangs."""
        assert 15 <= DEFAULT_LLM_TIMEOUT_SECONDS <= 300


class TestBounding:
    def test_a_hanging_call_is_abandoned(self, evaluator):
        evaluator._evaluate_interaction = lambda i, o: time.sleep(60)
        started = time.time()
        result = evaluator._evaluate_interaction_bounded("in", "out")
        elapsed = time.time() - started
        assert elapsed < 10, f"took {elapsed:.1f}s; the bound did not apply"
        assert result["method"] == "timeout"

    def test_a_timeout_fails_closed(self, evaluator):
        """The property that matters. Never report unmeasured content as clean."""
        evaluator._evaluate_interaction = lambda i, o: time.sleep(60)
        result = evaluator._evaluate_interaction_bounded("in", "out")
        assert result["passed"] is False
        assert result["toxicity_score"] == 1.0
        assert "timed out" in result["reason"]

    def test_a_fast_call_passes_its_result_through_untouched(self, evaluator):
        sentinel = {"toxicity_score": 0.02, "passed": True, "method": "deepeval"}
        evaluator._evaluate_interaction = lambda i, o: dict(sentinel)
        assert evaluator._evaluate_interaction_bounded("in", "out") == sentinel

    def test_an_exception_still_propagates(self, evaluator):
        """The bound must not turn a real error into a timeout verdict."""

        def boom(_i, _o):
            raise ValueError("provider rejected the request")

        evaluator._evaluate_interaction = boom
        with pytest.raises(ValueError, match="provider rejected"):
            evaluator._evaluate_interaction_bounded("in", "out")

    def test_the_bound_can_be_disabled(self):
        """Setting the timeout to 0 restores the previous unbounded behaviour."""
        ev = ContentSafetyEvaluator(
            config={"use_mock_if_unavailable": True, "llm_timeout_seconds": 0}
        )
        ev._evaluate_interaction = lambda i, o: {"passed": True, "method": "direct"}
        assert ev._evaluate_interaction_bounded("in", "out")["method"] == "direct"


class TestTheWorkerIsADaemon:
    def test_the_abandoned_thread_is_a_daemon(self, evaluator):
        """Otherwise the interpreter joins it at exit and the bound is moot."""
        seen: dict = {}
        release = threading.Event()

        def capture(_i, _o):
            current = threading.current_thread()
            seen["daemon"] = current.daemon
            seen["name"] = current.name
            release.wait(30)
            return {}

        evaluator._evaluate_interaction = capture
        evaluator._evaluate_interaction_bounded("in", "out")
        release.set()  # let the abandoned worker finish so it does not linger

        assert seen.get("daemon") is True, (
            "the worker must be a daemon thread; a non-daemon worker still "
            "blocked in the provider would hold up interpreter exit"
        )
        assert "content-safety" in seen.get("name", "")
