# Writing an evaluator

A GOPAL policy can read **declared facts** supplied about the system or its
operating context and **measured metrics** produced by an evaluation tool. An
evaluator supplies measured values in the canonical input fields expected by
the policy.

This guide describes how to implement and register an AICertify evaluator.

GOPAL does not require AICertify. A shell script can write the expected JSON
and invoke `opa` directly; GOPAL's
[Plug your evaluator into GOPAL](https://github.com/Principled-Evolution/gopal/blob/main/docs/tutorials/supplying-metrics.md)
documents that path. AICertify adds evaluator base classes, discovery, metric-gap
reporting, registration, and delivery of measured values into the OPA input
shape.

## 1. Find out what is missing

```
python scripts/metric_gap_report.py
```

```
global  (4/4 measured metrics have an evaluator)
  ok   content_safety.toxicity_score                  ContentSafetyEvaluator
  calc metrics.model_card.completeness                computed by model_card_score
  ok   evaluation.toxicity_score                      ContentSafetyEvaluator
  ok   governance.audit_logging.completeness_score    AuditLoggingEvaluator

industry_specific/healthcare  (3/6 measured metrics have an evaluator)
  GAP  evaluation.clinical_validation.score           no evaluator declares this
  GAP  evaluation.patient_safety.score                no evaluator declares this
  GAP  evaluation.risk_assessment.score               no evaluator declares this

international/eu_ai_act  (12/13 measured metrics have an evaluator)
  GAP  metrics.model_card.compliance_level            no evaluator declares this

TOTAL: 22 of 26 measured metrics can be supplied today.
```

Each `GAP` identifies a metric required by a policy for which no registered
evaluator currently declares coverage. Use `--framework eu_ai_act` to restrict
the report or `--json` for machine-readable output.

## 2. Write the evaluator

An evaluator requires three elements: subclass `BaseEvaluator`, declare the
metrics it supplies, and implement `evaluate`.

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

The implementation in
[`aicertify/evaluators/audit_logging_evaluator.py`](../aicertify/evaluators/audit_logging_evaluator.py)
follows this pattern. It requires no model, API key, or inference; it computes
a completeness score from the audit-logging fields present in the contract.

**Use GOPAL's canonical metric names in `SUPPORTED_METRICS`.** The gap report
matches evaluators to policy requirements by field name. A non-canonical name
therefore does not satisfy the policy requirement. GOPAL's
`helper_functions/metrics.rego` defines the canonical names and supported
historical aliases.

## 3. Wire it in

One line, in `ComplianceEvaluator.EVALUATOR_CLASSES`:

```python
EVALUATOR_CLASSES = {
    ...
    "audit_logging": AuditLoggingEvaluator,
}
```

Registration is separate from metric declaration. The gap report reads
`SUPPORTED_METRICS`, while `ComplianceEvaluator` instantiates only evaluators
listed in `EVALUATOR_CLASSES`. An evaluator can therefore declare coverage but
remain unavailable at runtime if it is not registered.

The gap report distinguishes this state with `WIRE`. Without registration, the
row reads:

```
  WIRE governance.audit_logging.completeness_score    AuditLoggingEvaluator declares
       this but is not in ComplianceEvaluator.EVALUATOR_CLASSES, so it never runs
```

Add the line and it reads:

```
global  (4/4 measured metrics have an evaluator)
  ok   governance.audit_logging.completeness_score    AuditLoggingEvaluator
```

`WIRE` does not count toward runtime metric coverage because the evaluator is
not instantiated during evaluation.

## 4. Publish under the canonical name

Registration controls whether the evaluator runs; metric delivery is a separate
step.

GOPAL reads measured metrics at `input.metrics.<domain>.<name>`, while raw
evaluator results are keyed by evaluator name as `results.<evaluator>`. Those
names are not generally equivalent, so evaluator output must be published
explicitly under the canonical metric path read by GOPAL.

Publish the metric under `details["metrics"]` in the shape read by GOPAL:

```python
return EvaluationResult(
    ...,
    details={"metrics": {"audit_logging": {"completeness": score}}},
)
```

`attach_measured_metrics` merges each evaluator's metric block into the OPA
input. `SUPPORTED_METRICS` declares which metrics the evaluator can provide;
`details["metrics"]` carries the values provided by a specific evaluation.

`tests/test_metric_delivery.py` checks the delivery path with `opa eval` against
GOPAL's resolver. A regression that prevents a metric from reaching the policy
therefore fails a test.

## Metric semantics

**Represent missing measurements as missing.** If a metric cannot be computed,
do not substitute a default numeric value. Returning `0.0` for an unavailable
toxicity measurement would cause policy evaluation to treat an unmeasured
system as if it had received a clean score.

**Match the policy's metric direction and statistic.** A safety score where
higher is better is not interchangeable with a toxicity score where higher is
worse. A maximum and an average also represent different properties. GOPAL
therefore keeps `metrics.toxicity.score` and
`metrics.toxicity.max_toxicity` separate and applies different thresholds to
them.

## Using it in CI

Once the metric is supplied, the policy that reads it becomes a check that can
fail a pull request:

```yaml
- name: Evaluate compliance
  run: aicertify evaluate --contract contract.json --policy eu_ai_act
```

Before implementing an evaluator, use `aicertify explain <framework>` to inspect
the required inputs and `aicertify init-contract --policy <framework>` to
scaffold the declared fields. Together with the metric-gap report, these
commands expose the required input paths without manual inspection of each Rego
file.

The evaluators run, their metrics are written into the contract, and the gopal
bundle is evaluated against the result. A policy that is not satisfied fails the
step, naming the article and the control. See
[gopal's GitHub Actions example](https://github.com/Principled-Evolution/gopal/tree/main/examples/github-actions).

## Testing yours

[`tests/test_audit_logging_evaluator.py`](../tests/test_audit_logging_evaluator.py)
provides a compact test pattern. In particular, preserve the distinction between
an explicit negative value and a missing value:

```python
def test_a_negative_answer_still_counts_as_answered(self, evaluator):
    """
    "tamper evident: no" is a real answer. Treating False as unanswered
    would drop it from the denominator and flatter the score.
    """
```

An explicit negative answer must remain distinct from an absent answer; otherwise
the denominator and resulting completeness score can be incorrect.

## The four metrics still showing GAP

Three are clinical: `patient_safety`, `clinical_validation`, and
`risk_assessment`. GOPAL interprets these as measurements from clinical
evaluation. A documentation-completeness count is not equivalent to a clinical
patient-safety score and must not be published under that metric name. Supply
these metrics from the evaluation that produced them or leave them absent so
the policy can fail closed.

The fourth is `metrics.model_card.compliance_level`. It was declared by an
evaluator that never computed it, and nothing GOPAL derives from a card yields
a compliance level distinct from completeness, so the declaration was removed
rather than backfilled.

The other model-card metrics are not gaps and no longer need an evaluator at
all. `global/v1/documentation/model_card_score` computes them from the card
itself, and declares as much in a `ProvidedMetrics` block, so the report marks
them `calc` rather than asking anyone to write tooling for work already done:

```
calc metrics.model_card.completeness    computed by global.v1.documentation.model_card_score
```

When a value is a policy judgement over supplied documentation rather than a
measurement of running-system behavior, implement that derivation as a policy
rule rather than as an evaluator.
