<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/hero_banner_dark.svg">
    <img src="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/hero_banner_light.svg" alt="AICertify — Compliance-as-code for AI systems" width="100%">
  </picture>
</div>

<p align="center">
  <em>Audit your AI against the EU AI Act, NIST AI RMF, and 13 more frameworks — one contract, one command, one report.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/aicertify/"><img src="https://img.shields.io/pypi/v/aicertify?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml"><img src="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/stargazers"><img src="https://img.shields.io/github/stars/Principled-Evolution/aicertify?style=flat-square" alt="Stars"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square" alt="Python 3.12+"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="Apache 2.0"></a>
  <a href="https://www.openpolicyagent.org/ecosystem/entry/principled-evolution"><img src="https://img.shields.io/badge/built%20on-OPA-7D4698.svg?style=flat-square" alt="Built on OPA"></a>
  <a href="https://github.com/Principled-Evolution/gopal"><img src="https://img.shields.io/badge/policies-94%20rego-2f9e44.svg?style=flat-square" alt="94 Rego Policies"></a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/diagram1_hero_flow_dark.svg">
    <img src="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/diagrams/diagram1_hero_flow_light.svg" alt="From AI app to audit-ready report: AI Application -> AICertify Contract -> OPA Policy Evaluation -> Compliance Report" width="85%" />
  </picture>
</p>

<br>

> 📦 **Full documentation, examples, contributing guide, translations (zh-CN / ja-JP / ko-KR / hi-IN), and 94 Rego policies** live in the [GitHub repository](https://github.com/Principled-Evolution/aicertify).

Regulators are moving faster than your governance docs. The EU AI Act is in force. NIST AI RMF is the de-facto US standard. India, Brazil, and Singapore are next. `AICertify` lets you encode those obligations as executable [Open Policy Agent](https://www.openpolicyagent.org/) policies, run them against captured AI interactions, and produce audit-ready reports in PDF, Markdown, JSON, or HTML.

It's the missing link between *"we have a responsible-AI policy"* and *"we can prove it."*

**Use it when you need to:**

- turn AI governance policies into executable checks
- produce audit-ready compliance evidence on every release
- evaluate AI interactions against named regulatory frameworks (EU AI Act, NIST AI RMF, FERPA, fair-lending, FAA/EASA aviation, …)
- generate Markdown, JSON, HTML, or PDF reports your auditor can read
- integrate AI compliance checks into CI/CD

AICertify is part of the [Open Policy Agent ecosystem](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution) — built on the same policy engine that powers Kubernetes admission, microservice authorisation, and infrastructure governance at scale.

> ⭐ **If AICertify helps you, please star the [repo](https://github.com/Principled-Evolution/aicertify).** It helps AI governance and policy-as-code practitioners discover the project.

---

## Quick Start

```bash
# 1. Install AICertify (~3–5 min on first install; pulls langchain + transformers)
pip install aicertify

# 2. Install the OPA binary, one-time (~80 MB)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa

# 3. Run the bundled demo — no contract file, no API keys, ~10 seconds
aicertify demo
```

`aicertify demo` loads a bundled sample contract, evaluates it against the EU AI Act policy set via OPA, and writes `aicertify_demo_report.md` to the current directory. Open the report — that's what your audit deliverable looks like.

<p align="center">
  <img src="https://raw.githubusercontent.com/Principled-Evolution/aicertify/main/docs/demo.gif" alt="aicertify demo recording — banner, spinners, evaluation progress, generated report path" width="85%" />
</p>

For richer evaluations (LangFair fairness metrics, DeepEval content-safety scoring, PDF reports), see [`examples/quickstart.py`](https://github.com/Principled-Evolution/aicertify/blob/main/examples/quickstart.py) and the [forkable example bots](https://github.com/Principled-Evolution/aicertify/tree/main/examples) — each ships an `input_contract.json`, a `policy_config.yaml`, and a `run.py`.

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

## Why AICertify?

Most AI governance programs live in PDFs, spreadsheets, and policy documents. They describe what *should* happen but do not prove what *did*.

AICertify turns governance rules into executable policy checks.

Instead of saying:

> "Our chatbot follows our responsible AI policy."

You can produce:

> "Here is the captured interaction, the policy version, the OPA evaluation result, and the generated audit report."

AICertify is for AI teams, governance teams, auditors, and platform engineers who need AI compliance evidence that can be **read, run, reviewed, and repeated**.

See the full positioning in [docs/why-aicertify.md on GitHub](https://github.com/Principled-Evolution/aicertify/blob/main/docs/why-aicertify.md).

---

## Compared with alternatives

Most AI-governance tooling is either:

- **A vendor SaaS** that locks your audit trail behind a login (Credo AI, Holistic AI), or
- **A research toolkit** focused on a single dimension — fairness metrics (Fairlearn, AI Fairness 360) or explainability (Microsoft RAI Toolbox).

Neither produces the document a regulator actually asks for: *evidence that you tested this AI system against a named regulation, with reproducible policies and a dated report.*

|  | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Credo AI |
|---|---|---|---|---|
| Open source | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | ❌ Closed |
| On-prem / air-gapped | ✅ | ✅ | ✅ | ❌ |
| Named regulatory frameworks | **EU AI Act, NIST RMF, Brazil AI Bill, India DPDP, +11 more** | ❌ (fairness only) | ❌ (toolkit) | ✅ |
| Policy-as-code (auditable, diff-able) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| Industry verticals out of the box | Aviation, Banking, Healthcare, Automotive, Education | ❌ | ❌ | Partial |
| Generates audit-ready reports | ✅ PDF / MD / JSON / HTML | ❌ | Partial | ✅ |
| Custom policies | ✅ Drop a `.rego` file | ❌ | N/A | ✅ (paid) |

---

## For OPA / Rego users

If you already use OPA, AICertify gives you the **AI-application context layer** OPA was missing. You bring your AI app; AICertify captures the interactions, feeds them through the OPA engine against AI-specific Rego policies sourced from [gopal](https://github.com/Principled-Evolution/gopal), and emits audit-ready evidence.

The whole stack is policy-as-code — same workflow you already use for Kubernetes admission, microservice authorisation, and infrastructure governance.

---

## Forkable examples

Copy any of these and substitute your own contract:

- **[customer-support-bot](https://github.com/Principled-Evolution/aicertify/tree/main/examples/customer-support-bot)** — limited-risk EU AI Act + global cross-cutting policies
- **[healthcare-triage-bot](https://github.com/Principled-Evolution/aicertify/tree/main/examples/healthcare-triage-bot)** — EU AI Act high-risk Annex III(5)(a) + gopal healthcare patient-safety policies
- **[hiring-screening-bot](https://github.com/Principled-Evolution/aicertify/tree/main/examples/hiring-screening-bot)** — EU AI Act high-risk Annex III(4) + fair-lending proxy + FRIA metadata pattern

Each example ships an `input_contract.json`, `policy_config.yaml`, `sample_interactions.json`, an `expected_report.md`, and a `run.py` you can execute directly.

---

## See the output

You don't have to install anything to see what AICertify produces. A sample pre-generated PDF is in the repo:

- **[demo-report-eu-ai-act.pdf](https://github.com/Principled-Evolution/aicertify/blob/main/docs/demo-report-eu-ai-act.pdf)** — a customer-support agent evaluated against the EU AI Act
- **[examples/outputs/](https://github.com/Principled-Evolution/aicertify/tree/main/examples/outputs)** — canonical full outputs for EU AI Act, loan evaluation, and medical diagnosis

---

## More on GitHub

- Full [README with diagrams](https://github.com/Principled-Evolution/aicertify) (English / [简体中文](https://github.com/Principled-Evolution/aicertify/blob/main/README.zh-CN.md) / [日本語](https://github.com/Principled-Evolution/aicertify/blob/main/README.ja-JP.md) / [한국어](https://github.com/Principled-Evolution/aicertify/blob/main/README.ko-KR.md) / [हिन्दी](https://github.com/Principled-Evolution/aicertify/blob/main/README.hi-IN.md))
- [CONTRIBUTING.md](https://github.com/Principled-Evolution/aicertify/blob/main/CONTRIBUTING.md) — how to add policies, examples, or framework coverage
- [SECURITY.md](https://github.com/Principled-Evolution/aicertify/blob/main/SECURITY.md) — private vulnerability disclosure
- [CHANGELOG.md](https://github.com/Principled-Evolution/aicertify/blob/main/CHANGELOG.md) — what changed in each release
- [gopal](https://github.com/Principled-Evolution/gopal) — the upstream OPA/Rego policy library AICertify uses

---

## License

Apache 2.0 — see the [LICENSE file](https://github.com/Principled-Evolution/aicertify/blob/main/LICENSE).
