# Plugging in tools you already run

You probably already measure some of this. Adapters take what an existing tool
produced and turn it into the metric names GOPAL policies read, so you do not
have to write an evaluator for something you have already measured.

Every adapter is a pure function of one argument. It imports nothing from the
tool it adapts, so you can convert a saved Detoxify result without installing
Detoxify, and none of them adds a dependency for anyone not using them.

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

Two numbers come out because GOPAL asks two different questions.
`metrics.toxicity.score` is the aggregate, compared against 0.1.
`metrics.toxicity.max_toxicity` is the worst single output, compared against
0.7. In the example above the average is 0.317 and the maximum is 0.92: report
only the average and the one genuinely toxic output has been averaged into
invisibility.

`predict()` returns a list per class for a list of texts and a numpy scalar per
class for a single string. Both are accepted, and numpy floats are coerced,
because a `float32` reaching OPA fails there rather than here.

The five other Detoxify classes have no canonical GOPAL name. They are kept
under `metrics.toxicity.categories` rather than dropped.

## Hugging Face model cards

A model card is the most widely published description of an AI system that
exists. It is not a compliance document, and this adapter is a good way to see
exactly how far short it falls.

```python
from huggingface_hub import ModelCard
from aicertify.adapters import from_model_card

fragment = from_model_card(ModelCard.load("bert-base-uncased").content)
```

Two things come out.

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
under `metrics.accuracy.score`. A self-reported number on a benchmark of the
author's choosing is a claim about a dataset, not a measurement of your
deployed system, and promoting it would let a good SST-2 score answer a
question nobody asked about it.

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

The version line is not decoration. A figure quoted anywhere has to be
reproducible, and without it a reader who reruns this later and gets a
different number cannot tell a changed rubric from a wrong claim. It names
GOPAL rather than a rubric version because the rubric *is* a GOPAL policy.

`--file` scores a local `README.md`, `--json` is machine-readable, and
`--threshold` compares against something other than 0.8.

### Where the rubric lives

Not here. Which sections a card must carry, what each is worth and how much
text counts as content are normative judgements about required documentation,
which is what GOPAL is for, so they are a policy:
[`global/v1/documentation/model_card_score`](https://github.com/Principled-Evolution/gopal/blob/main/global/v1/documentation/model_card_score.rego).

`score_model_card` shells out to `opa` and reads the answer. The playground
runs the same policy compiled to WebAssembly. Neither reimplements it, so the
number you get here and the number the site shows are the same number because
they come from the same rules, not because two implementations happen to agree.

That also means `opa` is required, and a missing binary raises
`GopalUnavailable` rather than falling back to an approximation. An
approximation would produce something that looks like the real number and is
not.

The heading table that maps card headings onto those sections comes from the
policy too, through `load_heading_sources()`. A copy per parser drifts exactly
the way a copy of the scoring did.

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

None of them passes, and the two best are among the most downloaded models in
the world. That is not a defect in the cards or in the adapter. A model card
answers part of what Annex IV asks and stops, and the gap is the point: see
[GOPAL's field-by-field accounting](https://github.com/Principled-Evolution/gopal/blob/main/docs/model-cards-vs-compliance.md).

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

**The direction matters more than the number.** GOPAL compares
`metrics.fairness.score` with `>=`, so higher is better. Fairlearn's
`difference()` is 0 at its best and points the other way; handing it over
unchanged reports the fairest possible system as the least fair. That is how
`is_toxic` once answered `true` for a system with no toxicity in it.

So `ratio()` is preferred, and not only to dodge the sign: a ratio is already
bounded on [0, 1] with 1 as the ideal, which is the shape a `>= 0.85` threshold
expects, and it is the form the four-fifths rule in fair lending is written in.
A `difference=` is accepted and converted to `1 - difference`, with `basis`
recording which way the number was turned.

Both `MetricFrame` shapes work: a multi-metric frame returns a Series keyed by
metric name, a single-metric frame returns bare scalars, and the second is the
one that breaks a `[metric]` lookup written for the first.

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
attribute is left out rather than read as 0.0, which would report text nobody
could score as clean.

Unlike the others, this adapter was written against Perspective's documented
response schema rather than live calls, because the API needs a key this
project does not hold. The shape is stable and long-published, but that is a
weaker warrant than the rest of this page has and it is better said than
implied.

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

Three rules, each of which exists because breaking it caused a real bug here.

**Absent is not zero.** Nothing measurable in, empty dict out. Never a default
score. On a scale where lower is worse a zero reports an unmeasured system as
clean, and GOPAL will believe it.

**The name has to describe what you measured.** Do not map a documentation
count onto `metrics.patient_safety.score` because it is the nearest available
slot. GOPAL gates that at 0.95 and means a clinical measurement.

**Keep statistics apart.** An average and a maximum answer different
questions. If your tool gives you both, emit both.

If you find yourself needing an evaluator rather than an adapter, because there
is a measurement to run rather than a result to convert, that is
[docs/writing-an-evaluator.md](writing-an-evaluator.md).
