# Writing an evaluator

A gopal policy reads two kinds of input. **Declared facts**, which a person
asserts about their organisation, and **measured metrics**, which a tool
computes. You can answer the declared facts yourself. The measured ones you
cannot, and a policy that reads one you cannot supply can never be satisfied.

An evaluator is what supplies them. This is how to write one.

## 1. Find out what is missing

```
python scripts/metric_gap_report.py
```

```
global  (2/4 measured metrics have an evaluator)
  GAP  content_safety.toxicity_score                  no evaluator declares this
  ok   documentation.model_card.completeness_score    ModelCardEvaluator
  GAP  evaluation.toxicity_score                      no evaluator declares this
  ok   governance.audit_logging.completeness_score    AuditLoggingEvaluator

international/eu_ai_act  (13/13 measured metrics have an evaluator)
  ...

TOTAL: 21 of 26 measured metrics can be supplied today.
```

Every `GAP` is a metric some policy needs and nothing produces. That is the
list. Add `--framework eu_ai_act` to narrow it, or `--json` to consume it.

## 2. Write the evaluator

Three things: subclass `BaseEvaluator`, declare which metrics you supply, and
implement `evaluate`.

```python
from aicertify.evaluators.base_evaluator import BaseEvaluator, EvaluationResult

class AuditLoggingEvaluator(BaseEvaluator):
    SUPPORTED_METRICS = (
        "metrics.audit_logging.completeness",
        "governance.audit_logging.completeness_score",
    )

    def _initialize(self) -> None:
        self.threshold = float(self.config.get("threshold", 0.8))

    def evaluate(self, data: dict) -> EvaluationResult:
        block = (data.get("governance") or {}).get("audit_logging") or {}
        expected = ("enabled", "retention_period_days", "records_access",
                    "records_changes", "tamper_evident")
        present = [f for f in expected if block.get(f) not in (None, "")]
        score = len(present) / len(expected)

        return EvaluationResult(
            evaluator_name="AuditLoggingEvaluator",
            compliant=score >= self.threshold,
            score=score,
            threshold=self.threshold,
            reason=f"{len(present)} of {len(expected)} audit-logging facts present",
            details={"metrics": {"audit_logging": {"completeness": score}}},
        )

    async def evaluate_async(self, data: dict) -> EvaluationResult:
        return self.evaluate(data)
```

That is the whole of
[`aicertify/evaluators/audit_logging_evaluator.py`](../aicertify/evaluators/audit_logging_evaluator.py),
lightly trimmed. It needs no model, no API key and no inference: it counts how
many audit-logging facts a contract actually carries, which is a real
measurement of a real thing.

**Use gopal's canonical name in `SUPPORTED_METRICS`.** The gap report matches
evaluators to policies by name. Invent a spelling and the policy still looks
unsupplied, however good your evaluator is. `helper_functions/metrics.rego` in
gopal is the list of canonical names, and it accepts the historical spellings
as fallbacks.

## 3. There is no step three

No registration call, no entry in a list, no configuration file. Discovery is
by the `SUPPORTED_METRICS` attribute. Re-run the report:

```
global  (2/4 measured metrics have an evaluator)
  ok   governance.audit_logging.completeness_score    AuditLoggingEvaluator
```

The gap closed on the strength of the class attribute alone.

## Two things worth getting right

**Absent is not zero.** If your metric cannot be computed, say so rather than
returning a flattering default. A toxicity evaluator that returns `0.0` when it
could not run reports an unmeasured system as safe, and gopal will believe it.
This is the failure mode the whole library exists to prevent, and it has caught
us more than once.

**Say which direction your number points.** A *safety* score where higher is
better and a *toxicity* score where higher is worse are not interchangeable, and
gopal's `is_toxic` once answered `true` for one of the safest possible systems
because they had been treated as if they were. If your metric is a rate, a
maximum and an average are also different questions: gopal keeps
`metrics.toxicity.score` and `metrics.toxicity.max_toxicity` apart precisely
because one is compared against 0.1 and the other against 0.7.

## Using it in CI

Once the metric is supplied, the policy that reads it becomes a check that can
fail a pull request:

```yaml
- name: Evaluate compliance
  run: aicertify evaluate --contract contract.json --policy eu_ai_act
```

Two related commands are worth knowing before you write anything:
`aicertify explain <framework>` prints what input a framework's policies need
and why, and `aicertify init-contract <framework>` scaffolds a contract with
every field in it. Between them and the gap report, you should not have to read
any Rego to find out what is expected of you.

The evaluators run, their metrics are written into the contract, and the gopal
bundle is evaluated against the result. A policy that is not satisfied fails the
step, naming the article and the control. See
[gopal's GitHub Actions example](https://github.com/Principled-Evolution/gopal/tree/main/examples/github-actions).

## Testing yours

[`tests/test_audit_logging_evaluator.py`](../tests/test_audit_logging_evaluator.py)
is a short model. The case worth copying is this one:

```python
def test_a_negative_answer_still_counts_as_answered(self, evaluator):
    """
    "tamper evident: no" is a real answer. Treating False as unanswered
    would drop it from the denominator and flatter the score.
    """
```

Distinguishing "answered no" from "not answered" is the single most common way
an evaluator quietly reports a system as better than it is.
