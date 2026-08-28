"""Adapters from real evaluation tools to GOPAL's canonical names.

The fixtures here are synthetic but structurally faithful: the two model cards
reproduce the conventions found on real repositories, one using the current
Hugging Face template and one using the older style that most of the
highest-download models still carry. There is an opt-in test at the bottom that
runs against the live Hub, because a fixture cannot tell you the conventions
have moved on.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from aicertify.adapters import from_detoxify, from_model_card, from_model_index

GOPAL = Path(__file__).resolve().parent.parent / "aicertify" / "opa_policies"
METRICS_REGO = GOPAL / "helper_functions" / "metrics.rego"


# The current template: "Uses", "Bias, Risks, and Limitations", "Training
# Details", with prose in subsections under a bare parent heading.
MODERN_CARD = """---
license: apache-2.0
datasets:
  - squad
  - wikipedia
pipeline_tag: text-classification
library_name: transformers
model-index:
  - name: demo-model
    results:
      - task:
          type: text-classification
          name: Text Classification
        dataset:
          name: glue
          type: glue
        metrics:
          - type: accuracy
            value: 0.9105
            name: Accuracy
            verified: true
          - type: f1
            value: 0.8998
            name: F1
---

# Demo Model

## Model Details

A transformer classifier trained for demonstration purposes, with enough
prose here to clear the minimal content threshold that the evaluator applies
when it scores how substantial a section is rather than merely present.

## Uses

### Direct Use

Intended for classifying short passages of English text in low-risk settings
where a human reviews the output before anything happens as a result of it.

### Out-of-Scope Use

Not for medical, legal, hiring or credit decisions, and not for any setting
where an incorrect classification carries consequences for a person.

## Bias, Risks, and Limitations

Trained on web text and carries its biases. Performance degrades on dialects
under-represented in the training corpus, and on text longer than the
sequence length it was trained against.

## Training Details

### Training Data

Trained on SQuAD and an English Wikipedia dump, deduplicated and filtered for
length before use.

### Preprocessing

Lowercased, tokenised with WordPiece, truncated to 512 tokens.

## Evaluation

Evaluated on the GLUE benchmark. Accuracy and F1 are reported in the metadata
block above, measured on the validation split rather than a held-out test set.

## Recommendations

Review outputs before acting on them, and re-evaluate on your own data before
deploying into any new domain.
"""

# The older convention, still carried by bert-base-uncased and gpt2.
LEGACY_CARD = """---
license: mit
language: en
---

# Legacy Style Model

## Model description

An older card that predates the current template, written with the headings
that were conventional at the time and that a great many popular repositories
still use today without modification.

## Intended uses & limitations

Usable for masked language modelling and for fine-tuning on downstream tasks.
Not intended to be used to generate factual text.

## Limitations and bias

The training data contains a great deal of unfiltered internet content, and
the model reproduces stereotypes present in it. Predictions should not be
treated as neutral.

## Training data

Trained on BookCorpus and English Wikipedia.

## Training procedure

### Preprocessing

Texts are lowercased and tokenised using WordPiece with a vocabulary size of
30,000.

## Evaluation results

Reported GLUE scores are in the paper. This section exists so that the card
documents that an evaluation was carried out at all.
"""


class TestDetoxify:
    """
    Detoxify's predict() returns one float per class per input, as a list when
    given a list and a numpy scalar when given a single string. The scalar
    shape is the one most people hit first and the one most likely to be
    mishandled, so both are covered.
    """

    BATCH = {
        "toxicity": [0.001, 0.92, 0.03],
        "severe_toxicity": [0.0, 0.41, 0.0],
        "insult": [0.0, 0.79, 0.01],
        "identity_attack": [0.0, 0.05, 0.0],
    }

    def test_the_aggregate_and_the_maximum_are_different_numbers(self):
        tox = from_detoxify(self.BATCH)["metrics"]["toxicity"]
        assert tox["score"] == pytest.approx((0.001 + 0.92 + 0.03) / 3)
        assert tox["max_toxicity"] == 0.92
        assert tox["score"] != tox["max_toxicity"]

    def test_one_toxic_output_among_many_is_not_averaged_away(self):
        """
        The whole reason GOPAL keeps the two apart. The aggregate here sits
        comfortably under the 0.1 threshold it is compared against, while the
        maximum is over the 0.7 the transparency policy uses. Report only the
        average and the toxic output disappears.
        """
        tox = from_detoxify(self.BATCH)["metrics"]["toxicity"]
        assert tox["score"] < 0.7
        assert tox["max_toxicity"] > 0.7

    def test_the_other_classes_are_kept(self):
        cats = from_detoxify(self.BATCH)["metrics"]["toxicity"]["categories"]
        assert cats["insult"]["max"] == 0.79
        assert "toxicity" not in cats

    def test_a_single_string_prediction_works(self):
        """predict("text") returns scalars, not lists."""
        tox = from_detoxify({"toxicity": 0.87})["metrics"]["toxicity"]
        assert tox["score"] == pytest.approx(0.87)
        assert tox["sample_size"] == 1

    def test_the_result_survives_json(self):
        """
        Detoxify returns numpy floats. A numpy float32 reaching OPA fails
        there, a long way from anything that would explain it.
        """
        json.dumps(from_detoxify(self.BATCH))

    @pytest.mark.parametrize(
        "bad", [{}, None, [], {"insult": [0.5]}, {"toxicity": []}, {"toxicity": "x"}]
    )
    def test_nothing_measurable_produces_nothing(self, bad):
        """Absent is not zero: 0.0 toxicity means measured and clean."""
        assert from_detoxify(bad) == {}


class TestHuggingFaceModelCard:
    def test_the_modern_template_is_read(self):
        mc = from_model_card(MODERN_CARD)["documentation"]["model_card"]
        assert mc["intended_use"]["primary_uses"]
        assert mc["intended_use"]["out_of_scope_uses"]
        assert mc["training_data"]["datasets"]
        assert mc["ethical_considerations"]["data_bias"]

    def test_the_legacy_template_is_read_too(self):
        """
        bert-base-uncased and gpt2 still use these headings. Matching only the
        current template scores the two most-downloaded models on the Hub as
        almost entirely undocumented, which is a fact about the matcher.
        """
        mc = from_model_card(LEGACY_CARD)["documentation"]["model_card"]
        assert mc["intended_use"]["primary_uses"]
        assert mc["training_data"]["datasets"]
        assert mc["caveats_recommendations"]["limitations"]
        assert mc["model_details"]

    def test_prose_in_subsections_is_not_read_as_an_empty_section(self):
        """
        "## Training Details" holds nothing directly; its content is under
        "### Training Data". Cutting a section at the next heading of any
        level rather than the next of equal or higher level reported real
        cards as not documenting their training at all.
        """
        mc = from_model_card(MODERN_CARD)["documentation"]["model_card"]
        assert "squad" in mc["training_data"]["datasets"].lower()
        assert mc["training_data"]["preprocessing"]

    def test_frontmatter_datasets_reach_the_training_section(self):
        mc = from_model_card(MODERN_CARD)["documentation"]["model_card"]
        assert "wikipedia" in mc["training_data"]["datasets"]

    def test_declared_facts_come_from_the_yaml_only(self):
        """
        A licence named in the frontmatter is a declaration. A licence
        mentioned in a sentence is not, and treating the two alike is how a
        documentation score stops meaning anything.
        """
        doc = from_model_card(MODERN_CARD)["documentation"]
        assert doc["license"] == "apache-2.0"
        assert "squad" in doc["training_datasets"]

    def test_unmapped_subsections_stay_absent(self):
        """
        A card almost never states decision thresholds or intersectional
        results. Leaving them unfilled is what makes the resulting score
        honest rather than flattering.
        """
        mc = from_model_card(MODERN_CARD)["documentation"]["model_card"]
        assert "decision_thresholds" not in mc.get("metrics", {})
        assert "intersectional_results" not in mc.get("quantitative_analyses", {})

    @pytest.mark.parametrize("bad", ["", "   ", None, 123])
    def test_an_empty_card_produces_nothing(self, bad):
        assert from_model_card(bad) == {}

    def test_a_card_with_no_frontmatter_still_parses(self):
        out = from_model_card("# Title\n\n## Uses\n\nSome described use.\n")
        assert out["documentation"]["model_card"]["intended_use"]["primary_uses"]


class TestModelIndex:
    def test_reported_results_are_extracted_with_their_context(self):
        front = {
            "model-index": [
                {
                    "results": [
                        {
                            "task": {"type": "text-classification"},
                            "dataset": {"name": "glue"},
                            "metrics": [
                                {"type": "accuracy", "value": 0.91, "verified": True}
                            ],
                        }
                    ]
                }
            ]
        }
        rep = from_model_index(front)["metrics"]["reported"]
        assert rep["accuracy"][0]["value"] == 0.91
        assert rep["accuracy"][0]["verified"] is True
        assert rep["accuracy"][0]["dataset"] == "glue"

    def test_reported_results_do_not_become_canonical_metrics(self):
        """
        A card's self-reported accuracy on a benchmark of the author's
        choosing is a claim about a dataset, not a measurement of the deployed
        system. Promoting it to metrics.accuracy.score would let a good SST-2
        number answer a question about a system in production.
        """
        out = from_model_card(MODERN_CARD)
        assert "reported" in out["metrics"]
        assert "accuracy" not in out["metrics"]

    @pytest.mark.parametrize(
        "bad",
        [
            {},
            {"model-index": None},
            {"model-index": [{"results": [{"metrics": [{"type": "acc"}]}]}]},
            {"model-index": [{"results": [{"metrics": [{"value": 1}]}]}]},
        ],
    )
    def test_an_unusable_index_produces_nothing(self, bad):
        assert from_model_index(bad) == {}


class TestTheCardActuallyScores:
    """
    The point of the adapter. Before it, ModelCardEvaluator read
    data["model_card"] and nothing else, while ComplianceEvaluator hands every
    evaluator contract.dict(), whose keys never include one. The evaluator ran
    on every contract, scored all nine sections missing and reported 0.0.
    """

    def test_a_card_scores_above_zero_through_the_pipeline_path(self):
        from aicertify.evaluators.documentation import ModelCardEvaluator
        from aicertify.models.contract import create_contract

        contract = create_contract(
            application_name="adapter test",
            model_info={"model_name": "demo"},
            interactions=[],
            context=from_model_card(MODERN_CARD),
        )
        result = ModelCardEvaluator().evaluate(contract.dict())
        emitted = (result.details or {}).get("metrics", {}).get("model_card", {})
        assert emitted.get("completeness", 0) > 0.0, (
            "the card did not reach the evaluator; _locate_model_card no longer "
            "finds it where a contract carries it"
        )

    def test_a_well_documented_card_still_fails_the_threshold(self):
        """
        Not a defect. GOPAL's technical-documentation check wants 0.8, and a
        model card, however good, answers part of what Annex IV asks. This
        asserts the honest ceiling rather than a pass.
        """
        from aicertify.evaluators.documentation import ModelCardEvaluator

        result = ModelCardEvaluator().evaluate(from_model_card(MODERN_CARD))
        emitted = (result.details or {}).get("metrics", {}).get("model_card", {})
        assert 0.0 < emitted.get("completeness", 0) < 0.8


@pytest.mark.skipif(
    shutil.which("opa") is None or not METRICS_REGO.exists(),
    reason="needs the opa binary and the pinned gopal checkout",
)
def test_the_card_reaches_a_gopal_policy(tmp_path):
    """End to end: card text in, GOPAL verdict out."""
    from aicertify.evaluators.documentation import ModelCardEvaluator
    from aicertify.opa_core.introspection import attach_measured_metrics

    result = ModelCardEvaluator().evaluate(from_model_card(MODERN_CARD))
    phase1 = {"results": {"model_card": json.loads(result.model_dump_json())}}
    opa_input = attach_measured_metrics(dict(phase1), phase1)

    probe = tmp_path / "probe.rego"
    probe.write_text(
        "package probe\n\nimport rego.v1\nimport data.helper_functions.metrics\n\n"
        'value := metrics.resolve(input, "metrics.model_card.completeness")\n'
    )
    inp = tmp_path / "in.json"
    inp.write_text(json.dumps(opa_input, default=str))
    out = subprocess.run(
        [
            "opa",
            "eval",
            "-d",
            str(METRICS_REGO),
            "-d",
            str(probe),
            "-i",
            str(inp),
            "data.probe.value",
            "--format",
            "json",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert out.returncode == 0, out.stderr
    payload = json.loads(out.stdout).get("result")
    assert payload, "GOPAL could not resolve metrics.model_card.completeness"
    assert payload[0]["expressions"][0]["value"] > 0.0


@pytest.mark.skipif(
    os.environ.get("AICERTIFY_LIVE_HUB") != "1",
    reason="set AICERTIFY_LIVE_HUB=1 to check the adapter against the real Hub",
)
@pytest.mark.parametrize("repo_id", ["bert-base-uncased", "openai-community/gpt2"])
def test_against_real_cards(repo_id):
    """
    A fixture cannot tell you the conventions have moved on. These two are the
    most-downloaded models on the Hub and both use the older heading style.
    """
    from huggingface_hub import ModelCard

    mc = from_model_card(ModelCard.load(repo_id).content)
    sections = mc.get("documentation", {}).get("model_card", {})
    assert len(sections) >= 6, f"{repo_id} parsed to only {sorted(sections)}"
