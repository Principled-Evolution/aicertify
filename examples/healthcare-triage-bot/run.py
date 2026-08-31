"""Run AICertify against a healthcare-triage-bot contract.

From the repo root::

    python examples/healthcare-triage-bot/run.py

This example demonstrates an EU AI Act *high-risk* AI evaluation against both the
EU AI Act framework and gopal's healthcare patient-safety policies.

The captured interactions are intentionally *safe* — the bot refuses to diagnose,
escalates on red-flag symptoms, and routes to a clinician for medication advice.
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from pathlib import Path

# The LLM-judged evaluators activate off the presence of OPENAI_API_KEY, and
# this example is something a first-time reader copies and runs. Hide the key
# unless they ask for those metrics, so the example behaves the same on every
# machine and never spends somebody's money without being asked. Same treatment
# the bundled demo gets in aicertify/_demo/runner.py.
#
# Without it, a reader with an exhausted quota watches nine retries per
# interaction scroll past and reasonably concludes the example is broken.
WITH_LLM_METRICS = os.environ.get("AICERTIFY_WITH_LLM_METRICS") == "1"
if not WITH_LLM_METRICS:
    os.environ.pop("OPENAI_API_KEY", None)

# Not exposed, to match examples/quickstart.py and keep the run reproducible
# across machines with and without GPUs.
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")


# Imported after the environment guard above, not before: the evaluator
# stack reads OPENAI_API_KEY at import time, so popping it afterwards
# would be too late. Same ordering as aicertify/_demo/runner.py.
from aicertify import application, regulations  # noqa: E402

EXAMPLE_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = EXAMPLE_DIR / "input_contract.json"
OUTPUT_DIR = Path.cwd() / "reports"


async def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text())

    regs = regulations.create("healthcare-triage-bot-eval")
    regs.add("eu_ai_act")
    regs.add("healthcare")

    app = application.create(
        name=contract["application_name"],
        model_name=contract["model"]["model_name"],
        model_version=contract["model"]["model_version"],
        model_metadata=contract["model"].get("metadata", {}),
    )
    for interaction in contract["interactions"]:
        if interaction.get("metadata", {}).get("role") == "system_disclosure":
            continue
        app.add_interaction(
            input_text=interaction["input_text"],
            output_text=interaction["output_text"],
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    await app.evaluate(
        regulations=regs,
        report_format="pdf",
        output_dir=str(OUTPUT_DIR),
    )

    report_paths = app.get_report()
    print("\nGenerated reports:")
    for framework, path in report_paths.items():
        print(f"  - {framework}: {path}")

    print(
        "\nReminder: a green AICertify report does NOT clear this AI for clinical "
        "deployment. Clinical evaluation, regulator notification, and clinician-"
        "in-the-loop validation remain mandatory. See docs/why-aicertify.md."
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
