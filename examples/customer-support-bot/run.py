"""Run AICertify against a customer-support-bot contract.

From the repo root::

    python examples/customer-support-bot/run.py

Produces a PDF + Markdown report under ``reports/`` showing how the bot's captured
interactions evaluate against the EU AI Act and global cross-cutting policies.
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

    regs = regulations.create("customer-support-bot-eval")
    regs.add("eu_ai_act")

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
    print(f"\nOpen any of the above to see the audit-ready deliverable.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
