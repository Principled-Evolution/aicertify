# Plugging in tools you already run

Adapters convert outputs from existing evaluation tools into the canonical
metric names read by GOPAL policies. Use an adapter when the measurement already
exists and only the data shape needs to be translated.

Every adapter is a pure function of one argument. It does not import the tool
it adapts, so a saved Detoxify result can be converted without installing
Detoxify. Adapters therefore do not add dependencies for users who do not call
them.

```python
from aicertify.adapters import from_detoxify, from_model_card
```

The return value is always a GOPAL input fragment, the same JSON you would
write by hand. Merge it into a contract's `context`, or dump it to a file and
run `opa eval` against it directly.

## Detoxify

[Detoxify](https://github.com/unitaryai/detoxify) is the most widely used open
toxicity classifier.

```python
from detoxify import Detoxify
from aicertify.adapters import from_detoxify

outputs = [turn["output_text"] for turn in interactions]
fragment = from_detoxify(Detoxify("original").predict(outputs))
```

```json
{"metrics": {"toxicity": {
  "score": 0.317, "max_toxicity": 0.92, "sample_size": 3,
  "categories": {"insult": {"score": 0.27, "max": 0.79}, "...": {}}
}}}
```

The adapter emits two toxicity statistics because GOPAL evaluates them
separately. `metrics.toxicity.score` is the aggregate, compared against 0.1,
while `metrics.toxicity.max_toxicity` is the maximum per-output score, compared
against 0.7. In the example above the aggregate is 0.317 and the maximum is
0.92. Retaining both prevents an aggregate from obscuring an individual
high-toxicity output.

`predict()` returns a list per class for a list of texts and a NumPy scalar per
class for a single string. Both shapes are accepted. NumPy floating-point
values are converted to native Python values before the fragment reaches OPA.

The five other Detoxify classes have no canonical GOPAL name. They are kept
under `metrics.toxicity.categories` rather than dropped.

## Hugging Face model cards

Model cards are widely used to document AI models, but their structure and
scope differ from a compliance evidence record. This adapter maps model-card
content into the documentation metrics that GOPAL policies can evaluate.

```python
from huggingface_hub import ModelCard
from aicertify.adapters import from_model_card

fragment = from_model_card(ModelCard.load("bert-base-uncased").content)
```

The adapter produces two groups of output.

**Documentation sections.** GOPAL's
`global/v1/documentation/model_card_score` scores nine sections from Mitchell
et al., *Model Cards for Model Reporting*, each made of named subsections.
Hugging Face cards use none of those names. They use the current
template (`Uses`, `Bias, Risks, and Limitations`, `Training Details`), or the
older convention that most high-download repositories still carry (`Intended
uses & limitations`, `Limitations and bias`, `Training data`), or something
their author invented. The adapter maps all three onto the subsections they
genuinely establish.

**Reported results.** `model-index` frontmatter is a structured record of
benchmark results. These land under `metrics.reported.*`, deliberately not
under `metrics.accuracy.score`. A self-reported benchmark result describes the
reported dataset and evaluation configuration; it does not establish the
accuracy of the deployed system. Keeping it under `metrics.reported.*`
preserves that distinction.

### One command

```
$ aicertify score-card bert-base-uncased

bert-base-uncased
  completeness  0.49   (threshold 0.8)
  quality       0.66
  BELOW THRESHOLD

    intended_use             1.00  ####################
    training_data            0.67  #############
    factors                  0.50  ##########
    ...
    evaluation_data          0.00

scored with aicertify 0.7.0, gopal 1.3.1, rubric v1
```

The version line records the implementations needed to reproduce the score. If
a later run produces a different result, the recorded AICertify and GOPAL
versions allow a changed rubric to be distinguished from a change in the input.
GOPAL is recorded because the rubric is implemented as a GOPAL policy.

`--file` scores a local `README.md`, `--json` is machine-readable, and
`--threshold` compares against something other than 0.8.

### Where the rubric lives

The rubric is defined in GOPAL rather than in the adapter. Requirements about
which sections are expected, how they are weighted, and what counts as content
are policy decisions, so they are implemented as a Rego policy:
[`global/v1/documentation/model_card_score`](https://github.com/Principled-Evolution/gopal/blob/main/global/v1/documentation/model_card_score.rego).

`score_model_card` invokes `opa` and reads the policy result. The playground
runs the same policy compiled to WebAssembly. Both surfaces therefore use the
same scoring rules rather than separate implementations of the rubric.

`opa` is therefore required. If the binary is unavailable,
`score_model_card` raises `GopalUnavailable` rather than returning an
approximate score under the same metric name.

The heading table that maps card headings onto those sections is also loaded
from the policy through `load_heading_sources()`. Keeping the mapping and the
scoring rubric in the same policy prevents independent parser copies from
diverging.

### What real cards actually score

Against the 0.8 threshold GOPAL's EU AI Act technical-documentation check
applies:

| Card | Completeness | Quality | Passes 0.8? |
| --- | --- | --- | --- |
| `bert-base-uncased` | 0.49 | 0.66 | No |
| `openai-community/gpt2` | 0.49 | 0.66 | No |
| `distilbert-base-uncased-finetuned-sst-2-english` | 0.41 | 0.42 | No |
| `HuggingFaceTB/SmolLM2-135M-Instruct` | 0.17 | 0.31 | No |
| `sentence-transformers/all-MiniLM-L6-v2` | 0.16 | 0.19 | No |

None of these cards reaches the 0.8 threshold. The result reflects a scope
difference rather than a defect in the cards: a model card can supply part of
the documentation requested by Annex IV without covering the complete set of
fields. See [GOPAL's field-by-field accounting](https://github.com/Principled-Evolution/gopal/blob/main/docs/model-cards-vs-compliance.md).

The subsections a card cannot fill are left unfilled rather than guessed at.
Decision thresholds, intersectional results and the motivation behind an
evaluation set are almost never in a card, and filling them with prose from
somewhere else would raise the score without raising the documentation.

## Fairlearn

[Fairlearn](https://fairlearn.org/) is the standard fairness toolkit for Python.

```python
from fairlearn.metrics import MetricFrame, selection_rate
from aicertify.adapters import from_fairlearn

frame = MetricFrame(metrics=selection_rate, y_true=y, y_pred=pred,
                    sensitive_features=group)
fragment = from_fairlearn(frame)
```

```json
{"metrics": {"fairness": {
  "score": 0.667, "basis": "ratio", "ratio": 0.667,
  "by_group": {"a": 0.4, "b": 0.6}
}}}
```

### Metric direction

GOPAL compares `metrics.fairness.score` with `>=`, so higher values must
represent better outcomes. Fairlearn's `difference()` uses the opposite
direction, with 0 as its best value. Passing that value through unchanged would
invert the meaning of the policy threshold.

`ratio()` is therefore preferred. It is bounded on [0, 1] with 1 as the ideal,
which matches the direction expected by a `>= 0.85` threshold and the ratio
form used by the four-fifths rule in fair lending.
A `difference=` is accepted and converted to `1 - difference`, with `basis`
recording which way the number was turned.

Both `MetricFrame` result shapes are supported. A multi-metric frame returns a
Series keyed by metric name, while a single-metric frame returns bare scalars;
the adapter handles both explicitly.

Against `healthcare/v1/diagnostic_safety`, which gates at 0.85:

| Ratio | `fairness_passes` | `fairness_eval_fails` |
| --- | --- | --- |
| 0.6667 | undefined | `true` |
| 0.95 | `true` | undefined |
| nothing supplied | undefined | `true` |

## Perspective API

Jigsaw's [Perspective API](https://perspectiveapi.com/) returns a summary score
per attribute per comment, higher being worse.

```python
from aicertify.adapters import from_perspective

scored = [client.comments().analyze(body=req).execute() for req in requests]
fragment = from_perspective(scored)
```

The mapping matches Detoxify's, because GOPAL asks the same two questions of
any toxicity measurement: the aggregate against 0.1 and the worst single output
against 0.7.

Perspective omits `summaryScore` for a language it does not support. That
attribute is omitted rather than converted to 0.0, because an unavailable
measurement must not be represented as a clean result.

This adapter is implemented against Perspective's documented response schema
rather than live integration tests because the repository does not hold a
Perspective API key. The documented schema is stable, but this provides weaker
validation than testing against live API responses; that limitation is stated
explicitly here.

## Using a fragment

Into a contract, where the evaluators will also run:

```python
from aicertify.models.contract import create_contract

contract = create_contract(
    application_name="my-app",
    model_info={"model_name": "bert-base-uncased"},
    interactions=interactions,
    context=fragment,
)
```

Or straight to OPA, with no AICertify in the loop at all:

```python
import json
json.dump(fragment, open("metrics.json", "w"))
```

```bash
opa eval -d gopal/international/eu_ai_act/v1 -d gopal/global -d gopal/helper_functions \
         -i metrics.json --format raw \
         'data.international.eu_ai_act.v1.documentation.technical_documentation.completeness_sufficient'
```

GOPAL's
[Plug your evaluator into GOPAL](https://github.com/Principled-Evolution/gopal/blob/main/docs/tutorials/supplying-metrics.md)
covers that second path, including the same mappings written as plain JSON for
people not using Python.

## Writing another one

An adapter is a function from a tool's output to a fragment. There is no base
class and nothing to register.

```python
def from_your_tool(report: dict) -> dict:
    scores = [r["toxicity"] for r in report.get("results", [])]
    if not scores:
        return {}
    return {"metrics": {"toxicity": {
        "score": sum(scores) / len(scores),
        "max_toxicity": max(scores),
    }}}
```

Three constraints apply to new adapters.

**Do not convert absence to zero.** If no measurement is available, return an
empty fragment rather than a default score. A default numeric value would cause
policy evaluation to treat an unmeasured system as if a measurement had been
performed.

**Use a metric name that describes the measurement.** Do not map a
documentation count onto `metrics.patient_safety.score` because it is the
nearest available field. GOPAL interprets that field as a clinical measurement
and applies a 0.95 threshold.

**Keep statistics apart.** An average and a maximum answer different
questions. If your tool gives you both, emit both.

If a measurement must be executed rather than an existing result converted,
implement an evaluator instead; see
[Writing an evaluator](writing-an-evaluator.md).
