<div align="center">
  <img src="aicertify/assets/aic.png" alt="AICertify" width="180"/>
</div>

<h1 align="center">AICertify</h1>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja-JP.md">日本語</a> |
  <a href="README.ko-KR.md">한국어</a> |
  <a href="README.hi-IN.md">हिन्दी</a>
</p>

<p align="center">
  <strong>Compliance-as-code for AI systems.</strong>
</p>

<p align="center">
  <em>Audit your AI against the EU AI Act, NIST AI RMF, and 13 more frameworks — one contract, one command, one report.</em>
</p>

<p align="center">
  <a href="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml"><img src="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/stargazers"><img src="https://img.shields.io/github/stars/Principled-Evolution/aicertify?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/releases"><img src="https://img.shields.io/badge/version-0.7.0-brightgreen.svg?style=flat-square" alt="Version 0.7.0"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square" alt="Python 3.12+"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="Apache 2.0"></a>
  <a href="https://www.openpolicyagent.org/"><img src="https://img.shields.io/badge/built%20on-OPA-7D4698.svg?style=flat-square" alt="Built on OPA"></a>
  <a href="https://github.com/Principled-Evolution/gopal"><img src="https://img.shields.io/badge/policies-94%20rego-orange.svg?style=flat-square" alt="94 Rego Policies"></a>
  <a href="https://github.com/Principled-Evolution/aicertify#status"><img src="https://img.shields.io/badge/status-beta-orange.svg?style=flat-square" alt="Beta"></a>
  <a href="https://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"></a>
</p>

<p align="center">
  <img src="diagrams/diagram1_hero_flow.png" alt="From AI app to audit-ready report: AI Application -> AICertify Contract -> OPA Policy Evaluation -> Compliance Report" width="85%" />
</p>

<br>

Regulators are moving faster than your governance docs. The EU AI Act is in force. NIST AI RMF is the de-facto US standard. India, Brazil, and Singapore are next. `AICertify` lets you encode those obligations as executable [Open Policy Agent](https://www.openpolicyagent.org/) policies, run them against captured AI interactions, and produce audit-ready reports in PDF, Markdown, JSON, or HTML.

It's the missing link between *"we have a responsible-AI policy"* and *"we can prove it."*

---

## Quick Start

```bash
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify
pip install -e .
python examples/quickstart.py
```

The quickstart wires a sample AI application through the EU AI Act policy set and writes a compliance report into `reports/`. Open it. That's what your audit deliverable looks like — generated, not handwritten.

### Minimal Python usage

```python
from aicertify import regulations, application

# 1. Pick the regulations you want to certify against
regs = regulations.create("my_regulations")
regs.add("eu_ai_act")

# 2. Wrap your AI app
app = application.create(
    name="customer-support-bot",
    model_name="gpt-4o",
    model_version="2024-08-06",
)

# 3. Feed it real interactions
app.add_interaction(
    input_text="I want a refund for my order",
    output_text="I can help with that. Could you share your order number?",
)

# 4. Evaluate and get reports back
await app.evaluate(regulations=regs, report_format="pdf", output_dir="reports")
```

That's the whole loop. **Contract → interactions → evaluate → report.**

---

## Why AICertify

Most AI-governance tooling is either:

- **A vendor SaaS** that locks your audit trail behind a login (Credo AI, Holistic AI), or
- **A research toolkit** focused on a single dimension — fairness metrics (Fairlearn, AI Fairness 360) or explainability (Microsoft RAI Toolbox).

Neither produces the document a regulator actually asks for: *evidence that you tested this AI system against a named regulation, with reproducible policies and a dated report.*

AICertify is built for that artifact.

<p align="center">
  <img src="diagrams/diagram4_comparison.png" alt="AICertify vs alternatives: AICertify is the only open-source, policy-as-code option with named regulatory frameworks, industry verticals, and audit-ready reports out of the box" width="85%" />
</p>

| | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Credo AI |
|---|---|---|---|---|
| Open source | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | ❌ Closed |
| On-prem / air-gapped | ✅ | ✅ | ✅ | ❌ |
| Named regulatory frameworks | **EU AI Act, NIST RMF, Brazil AI Bill, India DPDP, +11 more** | ❌ (fairness only) | ❌ (toolkit) | ✅ |
| Policy-as-code (auditable, diff-able) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| Industry verticals out of the box | Aviation, Banking, Healthcare, Automotive, Education | ❌ | ❌ | Partial |
| Generates audit-ready reports | ✅ PDF / MD / JSON / HTML | ❌ | Partial | ✅ |
| Custom policies | ✅ Drop a `.rego` file | ❌ | N/A | ✅ (paid) |

---

## How It Works

<p align="center">
  <img src="diagrams/diagram2_architecture.png" alt="AICertify architecture: Your AI App feeds a Contract, which flows through Evaluators (Fairness, ContentSafety, RiskManagement, Compliance) into the OPA Engine with 94 Rego policies, producing an audit deliverable via the Report Generator" width="85%" />
</p>

1. **Contract** — A JSON description of your AI application: model, version, captured interactions, metadata.
2. **Evaluators** — Pluggable Python evaluators (Fairness, ContentSafety, RiskManagement, Compliance) extract metrics from your interactions.
3. **OPA policies** — The metrics get evaluated against the regulation's Rego policies (sourced from the [gopal](https://github.com/Principled-Evolution/gopal) policy library).
4. **Report** — A formatted, dated artifact you can hand to legal, an auditor, or your AI risk committee.

Because the policies are declarative Rego, they version, diff, and review like any other code. When a regulation changes, you bump the policy — not your evaluation harness.

---

## Regulatory Coverage

<p align="center">
  <img src="diagrams/diagram3_regulatory_coverage.png" alt="Regulatory coverage: 94 policies across 15+ frameworks and 5 industries -- EU AI Act, NIST AI RMF, India DPDP, Brazil AI Bill, RTCA DO-365/366, FAA Part 107, EASA SORA, ICAO Doc 10019, Healthcare, Banking and Financial Services, Automotive, Education, Global, Aviation, AIOps, Corporate" width="85%" />
</p>

AICertify runs against the [gopal](https://github.com/Principled-Evolution/gopal) policy library — **94 production OPA policies** across these frameworks:

### International
- **EU AI Act** — 29 policies covering prohibited practices, biometric ID, manipulation, transparency, technical documentation, human oversight, GPAI obligations
- **NIST AI RMF** — Govern, Map, Measure, Manage + AI 600-1
- **India Digital Policy** — DPDP-aligned obligations
- **Brazil AI Governance Bill** — Algorithmic governance requirements
- **Aviation standards** — ICAO Doc 10019, RTCA DO-365/366, ASTM F3442, ISO 21384, FAA Part 107, EASA SORA

### Industry-specific
- **Aviation** (17 policies) — Detect-and-avoid, certification, design, integration validation
- **Education** (12 policies) — FERPA, COPPA, proctoring, human-in-the-loop grading
- **Banking & Financial Services** — Model risk, fair lending
- **Healthcare** — Patient safety, diagnostic safety
- **Automotive** — Vehicle safety integration

### Global & Operational
- **Global** — Accountability, fairness, transparency, explainability, content safety, risk management, security
- **Corporate** — InfoSec, governance
- **AIOps & Cost** — Scalability, resource efficiency

Don't see your regulation? [Add a Rego file](https://github.com/Principled-Evolution/gopal/blob/main/CONTRIBUTING.md). The library is designed to be extended.

---

## CLI

```bash
python -m aicertify.cli \
  --contract path/to/contract.json \
  --policy aicertify/opa_policies/international/eu_ai_act/v1 \
  --report-format pdf \
  --output-dir reports/
```

Useful flags:

| Flag | Purpose |
|---|---|
| `--contract` | Path to the AI application contract JSON |
| `--policy` | Path to the OPA policy folder to evaluate against |
| `--report-format` | `pdf`, `markdown`, `json`, `html` (default: `pdf`) |
| `--evaluators` | Restrict to specific evaluators (e.g. `Fairness ContentSafety`) |
| `--output-dir` | Where reports land (default: `./reports`) |
| `--verbose` | Verbose logging |

See [`examples/quickstart.py`](examples/quickstart.py) for the full Python API.

---

## Sample Reports

<p align="center">
  <img src="diagrams/diagram5_report_anatomy.png" alt="Anatomy of an audit-ready report: header with framework name, application, model and date; executive summary; policy results table; risk assessment bar chart; remediation guidance; footer attributing AICertify v0.7.0" width="85%" />
</p>

The `examples/outputs/` directory contains generated reports from real evaluations you can inspect before running anything:

- `eu_ai_act/` — A customer-support agent evaluated against the EU AI Act
- `loan_evaluation/` — A credit-scoring model evaluated for fair lending
- `medical_diagnosis/` — A clinical-decision-support model evaluated for patient safety

Open the PDFs. That's what your auditor wants.

---

## Status

AICertify is in **beta (v0.7.0)** — the API may evolve before the 1.0 release. Production-ready frameworks today:

- ✅ EU AI Act
- ✅ Global evaluators (fairness, content safety, transparency)
- ✅ Healthcare, BFS, Automotive industry policies
- ✅ Aviation policy set (RTCA, ASTM, FAA, EASA)
- 🚧 NIST AI RMF — partial coverage
- 🚧 India Digital Policy — early stage

Track progress in the [policy library roadmap](https://github.com/Principled-Evolution/gopal).

---

## Contributing

We welcome:

- New regulatory frameworks (open an issue first to align scope)
- Industry-specific policies you've battle-tested
- New evaluators (fairness, safety, robustness — see `aicertify/evaluators/`)
- Bug reports with a minimal reproducing contract

Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Related Projects

- **[gopal](https://github.com/Principled-Evolution/gopal)** — The OPA policy library AICertify uses under the hood. Use it standalone with the OPA CLI if you don't need the Python framework.
- **[Open Policy Agent](https://www.openpolicyagent.org/)** — The policy engine.
- **[Regal](https://github.com/StyraInc/regal)** — Rego linter used to keep policies clean.

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

<p align="center"><sub>Built by <a href="https://github.com/Principled-Evolution">Principled Evolution</a> · Policies you can read, run, and prove.</sub></p>
