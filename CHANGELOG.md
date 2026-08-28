# Changelog

All notable changes to **AICertify** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet.

## [0.8.0]: 2026-08-28

### Fixed

- **AICertify could only report on four of gopal's 91 policies.** It queried `data.<package>.report_output` for every policy, and four define that rule. An EU AI Act evaluation reported 4 verdicts out of 29; UK, NIST, BFS, legal, global, healthcare and education evaluations reported nothing at all, while still exiting successfully.

  The policies were never silent, they were being asked the wrong question. A survey of the library found `report` on 59 policies and `policy_metrics` on 63, and gopal's coverage data names a decision rule for all 84 policies that reach a verdict. The query is now the whole package, and extraction reads the richest shape available: `report_output`, then `compliance_report`, then `report`, then the decision rule with `policy_metrics`.

  | Framework | Before | After |
  | --- | --- | --- |
  | eu_ai_act | 4 | 29 |
  | uk | 0 | 6 |
  | nist | 0 | 5 |
  | bfs | 0 | 4 |
  | legal | 0 | 3 |
  | global | 0 | 4 |
  | healthcare | 0 | 2 |
  | education | 0 | 4 |

  The decision rule is read from coverage data rather than assumed: eight distinct names are in use across the library, so guessing `allow` would have dropped seven policies. A policy whose decision rule produces no boolean is omitted rather than reported as a failure, because in Rego an undefined value is not `false`. And `academic_integrity` is a detector whose `true` means a concern was found, so its verdict is inverted before reporting.

- **CI never checked out the policy submodule**, so tests reading the real library passed vacuously against an empty index. It now fetches submodules, and those tests skip with a clear reason on a non-recursive clone.

- **Test files are no longer evaluated.** `*_test.rego` files declare their own packages and contribute no verdicts.

### Added

- **`CITATION.cff` and `.zenodo.json`.** GitHub now offers a "Cite this repository" button, and each release is archived by Zenodo with a DOI. The citation metadata records gopal as a referenced work via its concept DOI, `10.5281/zenodo.22142302`.

### Changed

- **gopal submodule bumped 28 commits**, which is what makes the decision-rule data available. It also brings gopal's Article 13/50 citation correction, the FERPA §99.30 consent rewrite, and the prohibited-practice fixes.

### Fixed

- **`aicertify demo` no longer crashes on a fresh install.** Importing `aicertify.application` hard-crashed with `ModuleNotFoundError: No module named 'langchain_core.tracers.langchain_v1'` — a third-party version incompatibility between `deepeval` and the resolved `langchain_core`/`langchain_community` — because six evaluator modules (`accuracy_evaluator.py`, `biometric_categorization_evaluator.py`, and the four `evaluators/prohibited_practices/*.py` modules) imported `deepeval` at module level without the graceful-degradation guard already used elsewhere in the codebase (`content_safety_evaluator.py`, `fairness_evaluator.py`). All six now follow the same `try/except ImportError` + `DEEPEVAL_AVAILABLE` pattern, reporting the affected evaluator unavailable instead of crashing the whole package. This was the first command a new user runs, and it was completely broken.
- **`pytest` itself couldn't start.** `deepeval` registers a pytest plugin under the entry-point name `plugins`, which pytest autoloads unconditionally before any test file is collected — so the same broken `langchain_core` dependency crashed `pytest` outright, independent of the evaluator fix above and independent of whether any test imported `deepeval`. Disabled via `addopts = "-p no:plugins"` in `pyproject.toml`.
- **`import aicertify` fired a `DeprecationWarning` against itself.** The package `__init__.py`, plus six internal call sites, imported `AiCertifyContract`/`AiEvaluationResult`/etc. from the deprecated `aicertify.models.contract_models` / `aicertify.models.evaluation_models` shims instead of their non-deprecated replacements (`aicertify.models.contract`, `aicertify.models.evaluation`). Every import of the library warned about its own internals. Repointed all internal usages; the shims remain for external backward compatibility.
- **`tests/` was restored.** The directory referenced by `AGENTS.md` and the CI workflow didn't exist — two test modules had been left under `aicertify/report_generation/` instead. Moved back to `tests/report_generation/`, fixed a stale pre-rename policy path in test fixture data, replaced a `pytest.skip`-based no-op test with a real assertion against `ReportGenerator.generate_html_report`, and converted several `return`-based pseudo-tests into real `assert`-based tests (they were passing regardless of outcome).
- **Re-enabled the `pytest` step in `.github/workflows/aicertify-ci.yaml`**, disabled since April 2025 pending "more reliable tests" — now that the above is fixed, it is.
- **`gopal` submodule bumped** from a commit ~15 months stale (49 policies) to current main (85 policies), which includes real aviation-standards coverage the README already claimed but the vendored policies didn't actually contain.
- **README, translated READMEs (zh-CN/ja-JP/ko-KR/hi-IN), README-pypi.md, AGENTS.md, CLAUDE.md, and docs/why-aicertify.md** corrected to match the bumped submodule: policy count (94 → 85), framework count, aviation standards list (dropped `ASTM F3442`, `RTCA DO-365/366` → `RTCA DO-365`), India DPDP → India Digital Policy naming, and an honest scaffold-vs-implemented breakdown per framework in the Status section instead of a flat "production-ready" claim.
- **Closed all 57 open Dependabot alerts** (23 high, 28 medium, 6 low across 18 packages: `pypdf`, `aiohttp`, `pillow`, `starlette`, `torch`, `transformers`, `setuptools`, `nltk`, `langchain`, `langsmith`, `langgraph-sdk`, `langgraph-checkpoint`, `pydantic-settings`, `pyasn1`, `soupsieve`, `cryptography`). Raised each `pyproject.toml` lower bound to the version that actually clears every open advisory for that package (several existing floors were a patch or two short) and added explicit floors for five packages that were only ever pulled in transitively. `transformers>=5.5.0` (an RCE fix) required relaxing `huggingface-hub`'s upper bound from `<1.0` to `<2.0` to keep the two resolvable together; neither package is imported directly by AICertify's own code. As a side effect, the newer `langchain-core`/`langchain-community` versions resolve compatibly with `deepeval` again, so the graceful-degradation guards added above now report `DEEPEVAL_AVAILABLE = True` instead of falling back.

## [0.7.3] — 2026-05-14

### Fixed

- **PyPI README rendering.** The PyPI project page previously showed broken images and broken `docs/` / `examples/` cross-links because PyPI doesn't resolve relative paths against the source repo. `pyproject.toml`'s `readme` field now points at a new **`README-pypi.md`** — a hand-maintained, slightly-trimmed variant of `README.md` with every image and cross-link rewritten to absolute `https://raw.githubusercontent.com/...` or `https://github.com/...` URLs. The hero banner, diagram1, `docs/demo.gif`, and every cross-link now render correctly on <https://pypi.org/project/aicertify/>. The GitHub `README.md` is unchanged — keep both files in sync when updating Quick Start, comparison table, or examples list.

## [0.7.2] — 2026-05-14

### Changed

- **`aicertify demo` rewritten for the canonical rich-UX flow.** The previous demo runner produced plain `print()` output; it now mirrors [`examples/quickstart.py`](examples/quickstart.py) exactly — uses the high-level `application.create()` + `app.evaluate()` API and wraps each step in `print_banner`, `spinner`, `MessageGroup`, and `success` markers from `aicertify.utils.logging_config`. Visually identical to the canonical SDK experience.
- **CLI default verbosity now WARNING, not INFO.** `aicertify demo` and `aicertify evaluate` no longer flood the terminal with INFO-level chatter from `langfair`, `deepeval`, the OPA policy loader, etc. Pass `--verbose` to opt back in (raises root logger to INFO and `aicertify` namespace to DEBUG).
- **OPA `policy_loader` no longer warns on `helper_functions/`** — those `.rego` files are shared library code (reporting helpers, validation helpers), not policies, and were always meant to be skipped silently. Same for dot-prefixed config directories.

### Added

- **`docs/demo.cast` + `docs/demo.gif`** — asciinema recording of `aicertify demo` running end-to-end, embedded near the top of the README so visitors see the rich UX before installing anything.

## [0.7.1] — 2026-05-14

### Added

- **`aicertify demo` subcommand** — a self-contained, no-config demo entry point. Loads a bundled sample contract (`aicertify/_demo/sample_contract.json`), runs an OPA evaluation against the EU AI Act policy set, and writes `aicertify_demo_report.md` to the current directory. Requires only the `opa` binary on PATH (no API keys, no contract file). The CLI now also detects a missing `opa` binary and prints a one-line, platform-aware install command instead of stack-tracing.
- **`aicertify evaluate` subcommand** — the previous flat CLI behaviour, now under an explicit subcommand. The pre-0.7.1 invocation `aicertify --contract X --policy Y …` is still accepted (transparently routed to `evaluate`).
- **Updated README Quick Start** — collapses to three commands: `pip install aicertify`, `curl … opa`, `aicertify demo`. Honest first-install timing called out (~3–5 min for deps + the one-time OPA install).

### Changed

- **Visual refresh** — all README diagrams replaced with hand-authored, theme-aware SVGs in [`diagrams/`](diagrams/). Each diagram now ships as a paired `_light.svg` + `_dark.svg` and is embedded via `<picture>` so GitHub light- and dark-theme readers each see the variant that matches their canvas. The top-of-README logo is replaced with a hero banner SVG. The previous matplotlib generator (`diagrams/generate_diagrams.py`) and 5 baked-in PNG diagrams have been removed in favour of the hand-authored SVG system documented in [`diagrams/STYLE.md`](diagrams/STYLE.md).
- **OG / social card** — added [`diagrams/og_card.png`](diagrams/og_card.png) (1200×630) for GitHub Settings → Social preview, plus its `_light` / `_dark` SVG sources.
- **AGENTS.md** — added a "Diagrams and visual assets" section pointing future agents at the new style system.

## [0.7.0] — 2026-05-14 (first PyPI release)

This is the first AICertify release on PyPI (`pip install aicertify`). It bundles the v0.7 development line (started April 2025) plus the marketing, security, and developer-experience overhaul shipped in May 2026.

### Added

- **First-party Claude Code skills** under [`skills/`](skills/): `run-compliance-check`, `evaluate-contract`, `explain-regulation`, `draft-policy`. Install with `cp -r skills/* ~/.claude/skills/`.
- **AGENTS.md and CLAUDE.md** for AI coding agents (Claude Code, Cursor, Codex, Gemini CLI, Copilot, …).
- **Marketing diagrams** — five PNG diagrams generated by a matplotlib script, embedded in the README. _(Superseded in the next release by hand-authored, theme-aware SVGs; see Unreleased.)_
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
