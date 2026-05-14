# Changelog

All notable changes to **AICertify** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Centered HTML hero, ordered badge wall, value-prop tagline, and 5 programmatically-generated marketing diagrams in the README (regulatory coverage, architecture, comparison vs Fairlearn / AIF360 / MS RAI / Credo AI, report anatomy, end-to-end flow).
- `AGENTS.md` and `CLAUDE.md` — operational instructions for AI coding agents working in this repository.
- `skills/` directory with 4 Claude Code skills: `run-compliance-check`, `evaluate-contract`, `explain-regulation`, `draft-policy`. Each ships as a slash command once installed into `~/.claude/skills/`.
- Comparison table vs Fairlearn / IBM AI Fairness 360 / Microsoft RAI Toolbox / Credo AI in the README.
- `diagrams/generate_diagrams.py` — reproducible matplotlib script that regenerates every marketing PNG.

### Changed
- README rewritten for product-page clarity: value-prop first, then quickstart, then differentiation, then coverage.

## [0.7.0] — 2025-04

### Added
- Reporting subsystem (`aicertify.report_generation`) producing audit-ready artifacts in PDF (via ReportLab), Markdown, JSON, and HTML.
- Quickstart example (`examples/quickstart.py`) wiring sample interactions through the EU AI Act policy set and emitting a full report.
- Pluggable evaluator classes — `FairnessEvaluator`, `ContentSafetyEvaluator`, `RiskManagementEvaluator`, `ComplianceEvaluator`.
- Sample pre-generated reports under `examples/outputs/` for EU AI Act, loan evaluation, and medical diagnosis use cases.

### Changed
- OPA policies migrated to the standalone [gopal](https://github.com/Principled-Evolution/gopal) library; AICertify now vendors the policy tree under `aicertify/opa_policies/` via Git submodule.
- Enhanced logging across the evaluation pipeline.
- Pre-commit hooks: `ruff`, `black`, security checks.

### Fixed
- Security: bumped `protobuf` to 5.29.5 and `pycares` to 4.9.0 to resolve advisory exposure.
- Security: bumped `transformers` and `setuptools` to resolve security alerts.
- Auto-labeling workflow no longer produces excessive labels.

## Earlier history

For changes prior to 0.7.0, see the [Git log](https://github.com/Principled-Evolution/aicertify/commits/main).

[Unreleased]: https://github.com/Principled-Evolution/aicertify/compare/v0.7.0...HEAD
[0.7.0]: https://github.com/Principled-Evolution/aicertify/releases/tag/v0.7.0
