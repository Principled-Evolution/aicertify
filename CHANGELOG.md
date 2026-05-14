# Changelog

All notable changes to **AICertify** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

_No unreleased changes._

## [0.7.0] — 2026-05-14 (first PyPI release)

This is the first AICertify release on PyPI (`pip install aicertify`). It bundles the v0.7 development line (started April 2025) plus the marketing, security, and developer-experience overhaul shipped in May 2026.

### Added

- **First-party Claude Code skills** under [`skills/`](skills/): `run-compliance-check`, `evaluate-contract`, `explain-regulation`, `draft-policy`. Install with `cp -r skills/* ~/.claude/skills/`.
- **AGENTS.md and CLAUDE.md** for AI coding agents (Claude Code, Cursor, Codex, Gemini CLI, Copilot, …).
- **Marketing diagrams** (5 PNG, regenerable via [`diagrams/generate_diagrams.py`](diagrams/generate_diagrams.py)) embedded in the README.
- **Translated READMEs** for Simplified Chinese, Japanese, Korean, and Hindi.
- **SECURITY.md** with a private vulnerability-disclosure flow at `security@principledevolution.ai`.
- **docs/why-aicertify.md** — long-form positioning doc covering the gap, the shift, the artefact AICertify produces, and the honest scope of what it does not do.
- **docs/INDEX.md** — Diátaxis-organised documentation hub.
- **docs/demo-report-eu-ai-act.pdf** — bundled sample deliverable so visitors can see the output before installing.
- **Forkable application examples** under [`examples/`](examples/):
  - `customer-support-bot/` — Limited-risk EU AI Act + global baseline
  - `healthcare-triage-bot/` — High-risk Annex III(5)(a) + gopal healthcare patient-safety (closes the long-standing medical-example request)
  - `hiring-screening-bot/` — High-risk Annex III(4) + fair-lending proxy + FRIA metadata pattern
- **Reporting subsystem** (`aicertify.report_generation`) producing audit-ready artifacts in PDF (via ReportLab), Markdown, JSON, and HTML.
- **Quickstart example** ([`examples/quickstart.py`](examples/quickstart.py)) wiring sample interactions through the EU AI Act policy set and emitting a full report.
- **Pluggable evaluator classes** — `FairnessEvaluator`, `ContentSafetyEvaluator`, `RiskManagementEvaluator`, `ComplianceEvaluator`.
- **Sample pre-generated reports** under `examples/outputs/` for EU AI Act, loan evaluation, and medical diagnosis use cases.
- **Comparison table** in the README vs Fairlearn / IBM AI Fairness 360 / Microsoft RAI Toolbox / Credo AI.
- **15 GitHub topics** for discoverability (`ai-governance`, `eu-ai-act`, `nist-ai-rmf`, `policy-as-code`, `opa`, `rego`, …).
- **10 starter contributor issues** plus a pinned umbrella issue.
- **4 new contributor labels** (`📦 examples`, `🦜 llm-apps`, `⚙️ ci`, `🛠️ developer-experience`).

### Changed

- **README rewritten** for product-page clarity: value-prop first, then quickstart, then differentiation, then coverage.
- **OPA policies migrated** to the standalone [gopal](https://github.com/Principled-Evolution/gopal) library; AICertify vendors the policy tree under `aicertify/opa_policies/` via Git submodule.
- **Enhanced logging** across the evaluation pipeline.
- **Pre-commit hooks** added: `ruff`, `black`, security checks.
- **`langfair` dependency** switched from a git URL (`mantric/langfair-mantric@python-3.12-support`) to the upstream PyPI release (`langfair>=0.8.0,<1.0`) now that upstream supports Python 3.12+ natively.
- **`pyproject.toml` overhauled** for PyPI publication: SPDX license expression, 16 keywords, 13 classifiers, `[project.urls]` block, `aicertify` console-script entry point, duplicate `[tool.poetry]` block removed.

### Fixed (security)

This release clears ~95 of the ~96 Dependabot advisories that were open against the development line. The remaining alert is `transformers <5.0.0rc3` (Trainer-class arbitrary code execution), which is upstream-blocked behind a release candidate.

Direct dependency bumps:

- `transformers >=4.53.0` — 8 ReDoS advisories
- `huggingface-hub >=0.34.0,<1.0` — compatibility with transformers ≥4.53
- `requests >=2.33.0` — insecure temp file reuse
- `python-dotenv >=1.2.2` — symlink-following arbitrary write
- `markdown >=3.8.1` — uncaught exception
- `protobuf >=5.29.6` — JSON recursion depth bypass (already done earlier in dev)
- `pycares >=4.9.0` (done earlier in dev)
- `setuptools >=78.1.1` (done earlier in dev)
- `black >=26.3.1` — arbitrary file writes from unsanitised cache filename
- `pytest >=9.0.3` — `tmpdir` handling
- `pytest-asyncio >=1.0.0` — pytest 9 compatibility
- `fastapi >=0.119.0` — starlette 0.49+ compatibility
- `starlette >=0.49.1` — O(n²) Range-header DoS + multipart parser DoS

Explicit lower bounds on transitive dependencies that ship security fixes:

- `aiohttp >=3.13.4` — 13 advisories (zip bomb, SSRF, header smuggling, CRLF injection, …)
- `urllib3 >=2.7.0` — 4 advisories (decompression bombs, cross-origin header leak)
- `pillow >=12.2.0` — 4 advisories (PSD OOB write, FITS GZIP bomb, font overflow)
- `pypdf >=6.10.2` — 14 advisories (multiple RAM exhaustion + infinite-loop fixes)
- `nltk >=3.9.4` — 1 critical zip slip + 4 high
- `langchain-core >=1.2.22` — 1 critical serialization injection + 4 high (path traversal, template injection, SSRF, unsafe load)
- `langchain >=1.0.0` — match langchain-core 1.x line
- `langchain-openai >=1.1.14` — DNS-rebind SSRF
- `langchain-text-splitters >=1.1.2` — XXE + SSRF
- `langchain-community >=0.3.27` — XXE
- `langsmith >=0.8.0` — deserialization + token-redaction bypass
- `pyasn1 >=0.6.3` — 2 high DoS (unbounded recursion)
- `banks >=2.4.2` — critical RCE via Jinja2 SSTI
- `sentencepiece >=0.2.1` — heap overflow
- `orjson >=3.11.6` — unbounded recursion
- `brotli >=1.2.0` — DoS
- `marshmallow >=3.26.2`, `filelock >=3.20.3`, `virtualenv >=20.36.1`, `Pygments >=2.20.0` — medium / low fixes

CodeQL alerts:

- Fixed: added explicit `permissions: contents: read` to `.github/workflows/aicertify-ci.yaml` and `.github/workflows/pre-commit.yaml`.
- Dismissed as false positives (7 alerts): `py/clear-text-logging-sensitive-data` warnings on logger calls that emit aggregate fairness-detection metrics (counts and scores) and hardcoded keyword lists, not actual PII.

Other fixes:

- Auto-labeling workflow no longer produces excessive labels.

## Earlier history

For pre-PyPI development history, see the [Git log](https://github.com/Principled-Evolution/aicertify/commits/main).

[Unreleased]: https://github.com/Principled-Evolution/aicertify/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/Principled-Evolution/aicertify/releases/tag/v0.7.0
