# Agent Instructions — AICertify

This file is the canonical operational guide for AI coding agents working in this repository (Claude Code, Cursor, Codex, Windsurf, Gemini CLI, Copilot, etc.). Tool-specific files (`CLAUDE.md`, `GEMINI.md`) inherit from this and add only platform-specific notes.

## What this project is

**AICertify** is a Python framework that evaluates AI applications against regulatory frameworks using [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) policies sourced from the sister project [gopal](https://github.com/Principled-Evolution/gopal). It produces audit-ready compliance reports in PDF, Markdown, JSON, and HTML.

The user-facing surface is:

1. **Python API** — `aicertify.application`, `aicertify.regulations`, evaluator classes
2. **CLI** — `python -m aicertify.cli`
3. **Reports** — generated artifacts in `examples/outputs/` you can show to an auditor

## Repository layout

```
aicertify/                          Python package
├── __init__.py                     Public API (re-exports the surface a user sees)
├── cli.py                          Argparse CLI entry — see "Useful commands" below
├── application.py / regulations.py User-facing fluent API
├── api.py / contract_models.py     Contract data model (Pydantic)
├── evaluators/                     Pluggable evaluators (Fairness, ContentSafety, …)
├── opa_policies/                   Vendored Rego policy tree (mirrors gopal layout)
│   ├── global/v1/                  Cross-cutting categories
│   ├── international/              EU AI Act, NIST, India, …
│   ├── industry_specific/          Healthcare, BFS, Automotive, Aviation, …
│   └── operational/                AIOps, cost, corporate
├── report_generation/              ReportLab-based PDF + Markdown + HTML + JSON writers
└── assets/                         Logos, images
examples/
├── quickstart.py                   End-to-end demo — the canonical "does this work?" script
├── sample_contract.json            Contract structure reference
└── outputs/                        Pre-generated reports for inspection
tests/                              pytest tests
pyproject.toml                      Poetry-managed project metadata
```

## Useful commands

```bash
# Install (editable)
pip install -e .

# Self-contained demo — bundled sample contract, OPA-only, no API keys
aicertify demo
# → writes ./aicertify_demo_report.md

# Full quickstart (uses the heavy ML evaluators)
python examples/quickstart.py

# CLI evaluation against a user contract
aicertify evaluate \
  --contract examples/sample_contract.json \
  --policy eu_ai_act \
  --report-format pdf \
  --output-dir reports/

# Tests
pytest tests/ -v

# Lint / format
ruff check aicertify/
black aicertify/
```

## Conventions

- **Python 3.12 only** (see `requires-python` in `pyproject.toml`). Do not introduce syntax incompatible with 3.12 — do not assume 3.13.
- **Line length 88** (black + ruff default). Don't change this.
- **Pydantic v2** — when defining models, use `model_config` not `class Config`.
- **OPA policies** — never hand-edit `aicertify/opa_policies/*.rego` files in this repo without considering whether the change should land upstream in [gopal](https://github.com/Principled-Evolution/gopal) first. They are a vendored copy.
- **Reports are user-facing legal artifacts** — when changing report generation, run the quickstart and inspect the output PDF before claiming success.
- **Avoid breaking the public API** — anything re-exported from `aicertify/__init__.py` is part of the user-facing contract. Bump the version and note in CHANGELOG.md if you must.

## Diagrams and visual assets

All README diagrams live in [`diagrams/`](diagrams/) as paired **light and dark SVGs**, embedded via `<picture>` for GitHub theme switching. The full design system (palette, type, shape language, naming, contribution flow) is documented in [`diagrams/STYLE.md`](diagrams/STYLE.md). Read it before adding or modifying any diagram.

- **Edit existing diagrams in place** — they are hand-authored SVGs, not generated. Open the file, change it, validate with `python3 -c "import xml.etree.ElementTree as ET; ET.parse('<path>')"`.
- **Do not reintroduce a matplotlib generator** — the previous `generate_diagrams.py` was deliberately removed. Hand-authored SVGs are the source of truth.
- **New diagrams must ship both `_light.svg` and `_dark.svg` variants.** Use `<picture>` markup; verify GitHub theme switching by viewing the rendered README on both light and dark settings.
- **The logo `aicertify/assets/aic.png`** is *not* the README asset — it is bundled into generated PDF reports via [`aicertify/report_generation/report_generator.py`](aicertify/report_generation/report_generator.py). Don't delete it. README assets are the SVGs in `diagrams/`.

## What NOT to do

- Don't pin new dependencies aggressively — many users will install AICertify alongside their own stack; tight pins create conflicts.
- Don't replace OPA with another policy engine. The whole value proposition is policy-as-code in Rego.
- Don't commit `reports/` or `examples/outputs/` content unless deliberately updating the canonical samples.
- Don't introduce calls to closed-source SaaS services (Credo AI, etc.) — this is a self-hostable, on-prem-capable framework.
- Don't add a feature that requires `python >= 3.13` — the project is intentionally pinned to 3.12.

## Sister projects

- **[gopal](https://github.com/Principled-Evolution/gopal)** — the upstream Rego policy library. If you find yourself adding a new framework, contribute the `.rego` there, then vendor it here.
- **[Open Policy Agent](https://www.openpolicyagent.org/)** — the engine.

## Conservatism

The author prefers **surgical changes**: do only what was asked, present the plan first when there's any ambiguity, and ask before introducing new abstractions. Critique your own design once for elegance, DRY, KISS, and explainability before presenting it.
