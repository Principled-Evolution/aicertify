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

# Run the end-to-end demo (writes reports/ into the repo)
python examples/quickstart.py

# CLI evaluation
python -m aicertify.cli \
  --contract examples/sample_contract.json \
  --policy aicertify/opa_policies/international/eu_ai_act/v1 \
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
