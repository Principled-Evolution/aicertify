# Writing an evaluator

A gopal policy reads two kinds of input. **Declared facts**, which a person
asserts about their organisation, and **measured metrics**, which a tool
computes. You can answer the declared facts yourself. The measured ones you
cannot, and a policy that reads one you cannot supply can never be satisfied.

An evaluator is what supplies them. This is how to write one.

None of this is required to use GOPAL. A shell script that writes JSON and
calls `opa` is a complete integration, and GOPAL's
[Plug your evaluator into GOPAL](https://github.com/Principled-Evolution/gopal/blob/main/docs/tutorials/supplying-metrics.md)
walks that path with no Python in it. What AICertify adds is the scaffolding:
the base class, the discovery, the gap report, and the merge that puts your
measurements where the policies actually read them. Read this one if you want
that; read the other if you would rather own the plumbing.

## 1. Find out what is missing

```
python scripts/metric_gap_report.py
```

```
global  (4/4 measured metrics have an evaluator)
  ok   content_safety.toxicity_score                  ContentSafetyEvaluator
  ok   documentation.model_card.completeness_score    ModelCardEvaluator
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

## 3. Wire it in

One line, in `ComplianceEvaluator.EVALUATOR_CLASSES`:

```python
EVALUATOR_CLASSES = {
    ...
    "audit_logging": AuditLoggingEvaluator,
}
```

This is the step that is easy to skip, because everything looks fine without
it. `SUPPORTED_METRICS` is what the gap report reads, so an unregistered
evaluator still shows up there, while `ComplianceEvaluator` only ever
instantiates what is in this dict. You get an evaluator that is discovered,
reported as coverage, and never run.

The report now refuses to be fooled by that. Leave the registration out and
the row reads:

```
  WIRE governance.audit_logging.completeness_score    AuditLoggingEvaluator declares
       this but is not in ComplianceEvaluator.EVALUATOR_CLASSES, so it never runs
```

Add the line and it reads:

```
global  (4/4 measured metrics have an evaluator)
  ok   governance.audit_logging.completeness_score    AuditLoggingEvaluator
```

`WIRE` does not count toward the total. A metric nothing produces at runtime is
not covered, whatever the class attributes say.

## 4. Publish under the canonical name

Registration gets your evaluator run. It does not get its numbers to a policy.

GOPAL reads measured metrics at `input.metrics.<domain>.<name>`. Evaluator
output arrives keyed by evaluator name, as `results.<evaluator>`, and for a long
time the only canonical names that resolved were the three where those two
happened to coincide: `metrics.fairness.score`, `metrics.content_safety.score`
and `metrics.risk_management.score` each spell an evaluator name in the middle
with `score` on the end. `metrics.model_card.completeness` does not, so no
policy reading it ever saw a measurement.

So publish explicitly, by putting the metric under `details["metrics"]` in the
shape GOPAL reads:

```python
return EvaluationResult(
    ...,
    details={"metrics": {"audit_logging": {"completeness": score}}},
)
```

`attach_measured_metrics` merges every evaluator's block into the top level of
the OPA input. What you emit there is what the policy sees, under the name you
gave it. `SUPPORTED_METRICS` is a claim about what you supply; this is the
supply.

`tests/test_metric_delivery.py` checks the whole path with `opa eval` against
GOPAL's own resolver, so a metric that stops arriving fails a test rather than
quietly reverting to a policy that can never be satisfied.

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

## The four metrics still showing GAP

Three of them are clinical: `patient_safety`, `clinical_validation` and
`risk_assessment`. They are deliberately not closed. GOPAL gates the first at
0.95, and it means a measurement from a clinical evaluation. The only thing
this codebase could compute in-process is how many safety fields a document
contains, and publishing that under the name `patient_safety.score` would let a
system with complete paperwork clear a patient-safety gate it was never
assessed against. Supply those from the evaluation that produced them, through
the contract, or leave them absent and let the policy fail closed.

The fourth is `metrics.model_card.compliance_level`. `ModelCardEvaluator`
declared it and never computed it, and nothing it measures yields a compliance
level distinct from completeness. The declaration was removed rather than
backfilled, which is why the EU AI Act line reads 12/13 rather than 13/13. That
number went down because it got honest, not because anything regressed.
