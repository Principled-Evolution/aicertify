"""Run AICertify against a hiring-screening-bot contract.

From the repo root::

    python examples/hiring-screening-bot/run.py

This example demonstrates an EU AI Act *high-risk* evaluation of a recruiting AI
against the EU AI Act framework, fair-lending policies as a fair-employment proxy,
and the global cross-cutting bundle.

The captured interactions are intentionally *safe* — the bot refuses to issue a
hire/no-hire decision, declines to consider protected attributes, and routes every
material judgement to a human reviewer.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from aicertify import application, regulations

EXAMPLE_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = EXAMPLE_DIR / "input_contract.json"
OUTPUT_DIR = Path.cwd() / "reports"


async def main() -> int:
    contract = json.loads(CONTRACT_PATH.read_text())

    regs = regulations.create("hiring-screening-bot-eval")
    regs.add("eu_ai_act")
    regs.add("bfs")  # fair-lending proxy until hiring/ framework lands

    app = application.create(
        name=contract["application_name"],
        model_name=contract["model"]["model_name"],
        model_version=contract["model"]["model_version"],
        model_metadata=contract["model"].get("metadata", {}),
    )
    for interaction in contract["interactions"]:
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
        "\nReminder: a green AICertify report does NOT clear this AI for production "
        "hiring use. A fundamental-rights impact assessment (Article 27), real-"
        "population bias testing, and engagement with employment-law counsel are "
        "additional requirements. See docs/why-aicertify.md."
    )
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
