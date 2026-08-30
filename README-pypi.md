<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/hero_banner_dark.svg">
    <img src="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/hero_banner_light.svg" alt="AICertify — Compliance-as-code for AI systems" width="100%">
  </picture>
</div>

<p align="center">
  <em>Open-source compliance-as-code for AI systems: one contract, executable OPA/Rego policies, and reproducible evidence across the EU AI Act, UK AI governance, NIST AI RMF, and more.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/aicertify/"><img src="https://img.shields.io/pypi/v/aicertify?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://pepy.tech/project/aicertify"><img src="https://img.shields.io/pepy/dt/aicertify?style=flat-square" alt="Downloads"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml"><img src="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/stargazers"><img src="https://img.shields.io/github/stars/Principled-Evolution/aicertify?style=flat-square" alt="Stars"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12-blue.svg?style=flat-square" alt="Python 3.12"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="Apache 2.0"></a>
  <a href="https://www.openpolicyagent.org/ecosystem/entry/principled-evolution"><img src="https://img.shields.io/badge/built%20on-OPA-7D4698.svg?style=flat-square" alt="Built on OPA"></a>
  <a href="https://github.com/Principled-Evolution/gopal"><img src="https://img.shields.io/badge/policies-92%20rego-2f9e44.svg?style=flat-square" alt="92 Rego Policies"></a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/diagram1_hero_flow_dark.svg">
    <img src="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/diagram1_hero_flow_light.svg" alt="From AI app to audit-ready report: AI Application -> AICertify Contract -> OPA Policy Evaluation -> Compliance Report" width="85%" />
  </picture>
</p>

<br>

> 📦 **Full documentation, forkable examples, contributing guides, translations, and 92 GOPAL/Rego policies** live in the [GitHub repository](https://github.com/Principled-Evolution/aicertify).

**AICertify is the open execution and evidence layer for AI governance.** Describe an AI system in a contract, supply organisation-known facts, attach or compute measured metrics, evaluate that evidence against versioned [GOPAL](https://github.com/Principled-Evolution/gopal) policies through [Open Policy Agent](https://www.openpolicyagent.org/), and generate dated PDF, Markdown, JSON, or HTML reports.

**The goal is simple: move from “we have an AI policy” to evidence another engineer, auditor, or risk team can inspect and reproduce.**

**Use AICertify to:**

- evaluate an AI system against named governance and regulatory policy sets
- keep declared facts distinct from evaluator-produced measurements
- run inspectable OPA/Rego policy logic locally, in CI/CD, or air-gapped
- generate portable PDF, Markdown, JSON, or HTML evidence with per-policy results
- extend the stack with your own Rego policies and evaluator adapters

AICertify is part of the [Open Policy Agent ecosystem](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution), using the same policy engine widely used for Kubernetes admission, service authorisation, and infrastructure policy.

> ⭐ **Building AI governance as code? Star the [GitHub repo](https://github.com/Principled-Evolution/aicertify) so other practitioners can find it.**

---

## Quick Start

```bash
# 1. Install AICertify (~3–5 min on first install; pulls langchain + transformers)
pip install aicertify

# 2. Install the OPA binary, one-time (~80 MB)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa

# 3. Run the bundled demo (no contract file or API keys)
aicertify demo
```

`aicertify demo` loads a bundled sample contract, evaluates it against the EU AI Act policy set via OPA, and writes `aicertify_demo_report.md`. The sample intentionally contains no compliance declarations, so evidence-dependent policies deny; this demonstrates fail-closed behavior rather than an artificially green demo.

<p align="center">
  <img src="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/docs/demo.gif" alt="aicertify demo recording: banner, spinners, evaluation progress, generated report path" width="85%" />
</p>

For richer evaluations (LangFair fairness metrics, DeepEval content-safety scoring, PDF reports), see [`examples/quickstart.py`](https://github.com/Principled-Evolution/aicertify/blob/main/examples/quickstart.py) and the [forkable example bots](https://github.com/Principled-Evolution/aicertify/tree/main/examples), each of which ships an `input_contract.json`, a `policy_config.yaml`, and a `run.py`.

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

That's the whole loop. **Contract → evidence → policy evaluation → report.**

---

## Why AICertify?

Evaluation libraries such as Fairlearn and AI Fairness 360 measure specific properties. Governance platforms address broader inventory and workflow needs. **AICertify provides the open execution layer between them:** combine declared system facts with measured evidence, run inspectable GOPAL/Rego policies through OPA, and emit portable, dated results.

The differentiator is reproducibility: inspect the rules, pin versions, run locally or air-gapped, review changes in Git, and retain the evidence outside a vendor account.

See the full positioning in [docs/why-aicertify.md on GitHub](https://github.com/Principled-Evolution/aicertify/blob/main/docs/why-aicertify.md).

---

## Compared with alternatives

|  | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Governance SaaS |
|---|---|---|---|---|
| Open source | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | Varies |
| Local / air-gapped execution | ✅ | ✅ | ✅ | Varies |
| Named governance / regulatory policy sets | ✅ via GOPAL | ❌ (measurement library) | ❌ (toolkit) | Common |
| Inspectable policy-as-code | ✅ OPA / Rego | ❌ | ❌ | Varies |
| Industry-specific policy coverage | ✅ | ❌ | ❌ | Varies |
| Portable dated reports | ✅ PDF / MD / JSON / HTML | ❌ | Partial | Common |
| Custom policy logic | ✅ Rego | ❌ | N/A | Product-specific |

---

## For OPA / Rego users

If you already use OPA, AICertify gives you the **AI-application context layer** OPA was missing. You bring your AI app; AICertify captures the interactions, feeds them through the OPA engine against AI-specific Rego policies sourced from [gopal](https://github.com/Principled-Evolution/gopal), and emits audit-ready evidence.

The whole stack is policy-as-code: the same workflow you already use for Kubernetes admission, microservice authorisation, and infrastructure governance.

---

## Forkable examples

Copy any of these and substitute your own contract:

- **[customer-support-bot](https://github.com/Principled-Evolution/aicertify/tree/main/examples/customer-support-bot)**: limited-risk EU AI Act + global cross-cutting policies
- **[healthcare-triage-bot](https://github.com/Principled-Evolution/aicertify/tree/main/examples/healthcare-triage-bot)**: EU AI Act high-risk Annex III(5)(a) + gopal healthcare patient-safety policies
- **[hiring-screening-bot](https://github.com/Principled-Evolution/aicertify/tree/main/examples/hiring-screening-bot)**: EU AI Act high-risk Annex III(4) + fair-lending proxy + FRIA metadata pattern

Each example ships an `input_contract.json`, `policy_config.yaml`, `sample_interactions.json`, an `expected_report.md`, and a `run.py` you can execute directly.

---

## See the output

You don't have to install anything to see what AICertify produces. A sample pre-generated PDF is in the repo:

- **[demo-report-eu-ai-act.pdf](https://github.com/Principled-Evolution/aicertify/blob/main/docs/demo-report-eu-ai-act.pdf)**: a customer-support agent evaluated against the EU AI Act
- **[expected reports](https://github.com/Principled-Evolution/aicertify/tree/main/examples)**: committed Markdown reports for the customer-support, healthcare-triage and hiring-screening examples, and a retained fair-lending PDF under `examples/outputs/loan_evaluation/`

---

## More on GitHub

- Full [README with diagrams](https://github.com/Principled-Evolution/aicertify) (English / [简体中文](https://github.com/Principled-Evolution/aicertify/blob/main/README.zh-CN.md) / [日本語](https://github.com/Principled-Evolution/aicertify/blob/main/README.ja-JP.md) / [한국어](https://github.com/Principled-Evolution/aicertify/blob/main/README.ko-KR.md) / [हिन्दी](https://github.com/Principled-Evolution/aicertify/blob/main/README.hi-IN.md))
- [CONTRIBUTING.md](https://github.com/Principled-Evolution/aicertify/blob/main/CONTRIBUTING.md): how to add policies, examples, or framework coverage
- [SECURITY.md](https://github.com/Principled-Evolution/aicertify/blob/main/SECURITY.md): private vulnerability disclosure
- [CHANGELOG.md](https://github.com/Principled-Evolution/aicertify/blob/main/CHANGELOG.md): what changed in each release
- [gopal](https://github.com/Principled-Evolution/gopal): the upstream OPA/Rego policy library AICertify uses

---

## License

Apache 2.0, see the [LICENSE file](https://github.com/Principled-Evolution/aicertify/blob/main/LICENSE).
