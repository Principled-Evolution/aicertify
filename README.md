<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/hero_banner_dark.svg">
    <img src="diagrams/hero_banner_light.svg" alt="AICertify — Compliance-as-code for AI systems" width="100%">
  </picture>
</div>

<p align="center">
  <a href="README.md">English</a> |
  <a href="README.zh-CN.md">简体中文</a> |
  <a href="README.ja-JP.md">日本語</a> |
  <a href="README.ko-KR.md">한국어</a> |
  <a href="README.hi-IN.md">हिन्दी</a>
</p>

<p align="center">
  <em>Audit your AI against the EU AI Act, the UK AI framework, NIST AI RMF and six more international frameworks: one contract, one command, one report.</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/aicertify/"><img src="https://img.shields.io/pypi/v/aicertify?style=flat-square&color=blue" alt="PyPI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml"><img src="https://github.com/Principled-Evolution/aicertify/actions/workflows/aicertify-ci.yaml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Principled-Evolution/aicertify/stargazers"><img src="https://img.shields.io/github/stars/Principled-Evolution/aicertify?style=flat-square" alt="Stars"></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12%2B-blue.svg?style=flat-square" alt="Python 3.12+"></a>
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square" alt="Apache 2.0"></a>
  <a href="https://www.openpolicyagent.org/ecosystem/entry/principled-evolution"><img src="https://img.shields.io/badge/built%20on-OPA-7D4698.svg?style=flat-square" alt="Built on OPA"></a>
  <a href="https://github.com/Principled-Evolution/gopal"><img src="https://img.shields.io/badge/policies-91%20rego-2f9e44.svg?style=flat-square" alt="91 Rego Policies"></a>
  <a href="https://makeapullrequest.com"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"></a>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram1_hero_flow_dark.svg">
    <img src="diagrams/diagram1_hero_flow_light.svg" alt="From AI app to audit-ready report: AI Application -> AICertify Contract -> OPA Policy Evaluation -> Compliance Report" width="85%" />
  </picture>
</p>

<br>

Regulators are moving faster than your governance docs. The EU AI Act is in force. NIST AI RMF is the de-facto US standard. India, Brazil, and Singapore are next. `AICertify` lets you encode those obligations as executable [Open Policy Agent](https://www.openpolicyagent.org/) policies, run them against captured AI interactions, and produce audit-ready reports in PDF, Markdown, JSON, or HTML.

It's the missing link between *"we have a responsible-AI policy"* and *"we can prove it."*

**Use it when you need to:**

- turn AI governance policies into executable checks
- produce audit-ready compliance evidence on every release
- evaluate AI interactions against named regulatory frameworks (EU AI Act, NIST AI RMF, FERPA, fair-lending, FAA/EASA aviation, …)
- generate Markdown, JSON, HTML, or PDF reports your auditor can read
- integrate AI compliance checks into CI/CD ([GitHub Actions guide](docs/integrations/github-actions.md))

AICertify is part of the [Open Policy Agent ecosystem](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution), built on the same policy engine that powers Kubernetes admission, microservice authorisation, and infrastructure governance at scale.

> ⭐ **If AICertify helps you, please star the repo.** It helps AI governance and policy-as-code practitioners discover the project.

---

## Quick Start

```bash
# 1. Install AICertify (~3–5 min on first install; pulls langchain + transformers)
pip install aicertify

# 2. Install the OPA binary, one-time (~80 MB)
curl -L https://openpolicyagent.org/downloads/latest/opa_linux_amd64 -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa

# 3. Run the bundled demo (no contract file, no API keys, ~10 seconds)
aicertify demo
```

`aicertify demo` loads a bundled sample contract, evaluates it against the EU AI Act policy set via OPA, and writes `aicertify_demo_report.md` to the current directory. Open the report: that's what your audit deliverable looks like.

<p align="center">
  <img src="docs/demo.gif" alt="aicertify demo recording: banner, spinners, evaluation progress, generated report path" width="85%" />
</p>

For richer evaluations (LangFair fairness metrics, DeepEval content-safety scoring, PDF reports), see [`examples/quickstart.py`](examples/quickstart.py) and the [forkable example bots](examples/), each of which ships an `input_contract.json`, a `policy_config.yaml`, and a `run.py`.

### Finding out what a framework needs

The hard part of a first real run is not installing anything, it is knowing what to put
in the contract. The EU AI Act policies need 155 distinct input fields, and guessing
them from evaluation failures is miserable. Two commands answer it up front.

`aicertify explain` lists every field a framework's policies read, split by who is
supposed to supply it:

```bash
aicertify explain uk
```

```
uk  —  6 policies

Fields you must declare (31)
  No evaluator can observe these. They are facts about your system,
  your process, or your paperwork, so you assert them in the contract.

  decision.article_9_condition                   automated_decision_making
  decision.meaningful_human_involvement          automated_decision_making
  ...
  governance.oversight_body_in_place             accountability_governance
  safeguards.human_intervention_available        automated_decision_making
```

Nothing in a transcript reveals whether a conformity assessment was completed or
whether a human can intervene in an automated decision, so those are declarations.
Fairness and toxicity scores are the opposite: the evaluators compute them, and the
command marks them as such so you do not hand-write your own results.

`aicertify init-contract` turns that list into a file to fill in, nested into the shape
the policies actually read:

```bash
aicertify init-contract --policy uk > contract.json
```

```json
{
  "application_name": "your-application",
  "model_info": { "model_name": "your-model", "model_version": "v1", "metadata": {} },
  "interactions": [ { "input_text": "Replace with a real prompt from your system.", "…": "…" } ],
  "context": {
    "decision": { "significant": null, "special_category_data_involved": null },
    "governance": { "accountable_person_named": null, "oversight_body_in_place": null },
    "safeguards": { "human_intervention_available": null, "information_provided": null }
  }
}
```

Replace the nulls and run `aicertify evaluate --contract contract.json --policy uk`.
A field left as `null` is dropped rather than sent as an explicit null, so an
unfilled scaffold denies instead of being read as "assessed, and false".

Add `--policies` to see the individual policies, or `--json` for machine-readable
output. `aicertify explain <framework>` with no valid match prints the list of
frameworks it accepts.

### For development

```bash
git clone https://github.com/Principled-Evolution/aicertify.git
cd aicertify
pip install -e .
```

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
- **A research toolkit** focused on a single dimension: fairness metrics (Fairlearn, AI Fairness 360) or explainability (Microsoft RAI Toolbox).

Neither produces the document a regulator actually asks for: *evidence that you tested this AI system against a named regulation, with reproducible policies and a dated report.*

AICertify is built for that artifact.

| | AICertify | Fairlearn / AIF360 | MS RAI Toolbox | Credo AI |
|---|---|---|---|---|
| Open source | ✅ Apache 2.0 | ✅ MIT | ✅ MIT | ❌ Closed |
| On-prem / air-gapped | ✅ | ✅ | ✅ | ❌ |
| Named regulatory frameworks | **EU AI Act, NIST RMF, Brazil AI Bill, India Digital Policy, +9 more** | ❌ (fairness only) | ❌ (toolkit) | ✅ |
| Policy-as-code (auditable, diff-able) | ✅ OPA / Rego | ❌ | ❌ | ❌ |
| Industry verticals out of the box | Aviation, Banking, Healthcare, Automotive, Education | ❌ | ❌ | Partial |
| Generates audit-ready reports | ✅ PDF / MD / JSON / HTML | ❌ | Partial | ✅ |
| Custom policies | ✅ Drop a `.rego` file | ❌ | N/A | ✅ (paid) |

---

## How It Works

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram2_architecture_dark.svg">
    <img src="diagrams/diagram2_architecture_light.svg" alt="AICertify architecture: Your AI App feeds a Contract, which flows through Evaluators (Fairness, ContentSafety, RiskManagement, Compliance) into the OPA Engine with 91 Rego policies, producing an audit deliverable via the Report Generator" width="85%" />
  </picture>
</p>

1. **Contract**: a JSON description of your AI application: model, version, captured interactions, metadata.
2. **Evaluators**: pluggable Python evaluators (Fairness, ContentSafety, RiskManagement, Compliance) extract metrics from your interactions.
3. **OPA policies**: the metrics get evaluated against the regulation's Rego policies (sourced from the [gopal](https://github.com/Principled-Evolution/gopal) policy library).
4. **Report**: a formatted, dated artifact you can hand to legal, an auditor, or your AI risk committee.

Because the policies are declarative Rego, they version, diff, and review like any other code. When a regulation changes, you bump the policy, not your evaluation harness.

---

## Regulatory Coverage

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram3_regulatory_coverage_dark.svg">
    <img src="diagrams/diagram3_regulatory_coverage_light.svg" alt="Regulatory coverage: 91 policies across 9 frameworks and 6 industries -- EU AI Act, NIST AI RMF, India Digital Policy, Brazil AI Bill, RTCA DO-365, FAA Part 107, EASA SORA, ICAO Doc 10019, Healthcare, Banking and Financial Services, Automotive, Education, Global, Aviation, AIOps, Corporate" width="85%" />
  </picture>
</p>

AICertify runs against the [gopal](https://github.com/Principled-Evolution/gopal) policy library: **91 production OPA policies** across these frameworks:

### International
- **EU AI Act** (29 policies): prohibited practices, biometric ID, manipulation, transparency, technical documentation, human oversight, GPAI obligations, conformity assessment and CE marking. Every obligation area is implemented; see [gopal's coverage matrix](https://github.com/Principled-Evolution/gopal/blob/main/docs/coverage/eu-ai-act.md) for the article-by-article mapping.
- **UK AI framework** (6 policies): the five pro-innovation principles, plus UK GDPR Articles 22A-22D as substituted by section 80 of the Data (Use and Access) Act 2025. The UK and EU automated-decision regimes have diverged, and both are encoded
- **NIST AI RMF** (5 policies): Govern, Map, Measure, Manage + AI 600-1
- **India Digital Policy**: aligned with NITI Aayog's National Strategy for Artificial Intelligence (the separate India DPDP Act isn't covered yet)
- **Brazil AI Governance Bill**: algorithmic governance requirements
- **Aviation standards** (7 policies): ICAO Doc 10019, FAA Part 107, FAA Remote ID, EASA Regulation 2019/947, EASA SORA, RTCA DO-365, ISO 21384

### Industry-specific
- **Aviation** (12 policies): airworthiness, autonomous systems, data management, flight operations
- **Education** (12 policies): FERPA, COPPA, proctoring, human-in-the-loop grading
- **Banking & Financial Services** (4 policies): model risk (SR 11-7, OCC 2011-12, BCBS 239), fair lending, PRA SS1/23, FCA Consumer Duty
- **Legal services** (3 policies): citation verification, client confidentiality, competence and supervision, following the SRA and BSB guidance on AI use
- **Healthcare** (2 policies): patient safety, diagnostic safety
- **Automotive**: vehicle safety integration

### Global & Operational
- **Global**: accountability, fairness, transparency, explainability, content safety, risk management, security
- **Corporate**: InfoSec, governance
- **AIOps & Cost**: scalability, resource efficiency

No category is a scaffold any more. Every policy checks concrete input fields, has a sibling test, and is asserted to deny an input carrying no evidence. `docs/coverage/coverage.json` in gopal is generated from the policy files and records, per policy, the fields it requires and whether it has that test.

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

## See the output

You don't have to install anything to see what AICertify produces. Pre-generated reports are committed to the repo:

- **[demo-report-eu-ai-act.pdf](docs/demo-report-eu-ai-act.pdf)**: a customer-support agent evaluated against the EU AI Act
- [examples/outputs/eu_ai_act/](examples/outputs/eu_ai_act/): the canonical full output
- [examples/outputs/loan_evaluation/](examples/outputs/loan_evaluation/): a credit-scoring model evaluated for fair lending
- [examples/outputs/medical_diagnosis/](examples/outputs/medical_diagnosis/): a clinical-decision-support model evaluated for patient safety

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="diagrams/diagram5_report_anatomy_dark.svg">
    <img src="diagrams/diagram5_report_anatomy_light.svg" alt="Anatomy of an audit-ready report: header with framework name, application, model and date; executive summary; policy results table; risk assessment bar chart; remediation guidance; footer attributing AICertify v0.7.3" width="85%" />
  </picture>
</p>

Open the PDFs. That's what your auditor wants.

---

## Status

AICertify is in **beta (v0.7.3)**. The API may evolve before the 1.0 release. Production-ready frameworks today:

Every policy in the library is implemented. There are no scaffolds left, so the useful
distinction is no longer implemented-or-not but **how deep the check goes**:

- ✅ **Threshold checks against measured values.** Global (fairness, content safety, toxicity, transparency), EU AI Act fairness, healthcare diagnostic safety, BFS fair lending and model risk. These compare a number your evaluators produced against a threshold.
- ✅ **Structural checks against the document you supply.** The EU AI Act's 29 policies, the aviation set (19 across the regulators and the vertical), automotive, education, legal.
- ⚠️ **Declared booleans.** NIST AI RMF Map, Measure and Manage, the UK principles, and the operational categories gate on a self-attestation such as `input.map.intended_use_documented` rather than inspecting the artefact behind it. That is a claim the policy records and enforces, not independent verification. gopal's [NIST matrix](https://github.com/Principled-Evolution/gopal/blob/main/docs/coverage/nist-ai-rmf.md) states this in the same terms, and notes that the orchestrator's verdict inherits that shallowness.

Which category a policy falls into is derivable: `docs/coverage/coverage.json` in gopal
lists the fields each policy requires, and a policy asking for `metrics.*` is comparing
measurements while one asking for `governance.*` is recording declarations.

---

## For OPA / Rego users

If you already use OPA for Kubernetes admission, microservice authorisation, or infrastructure governance, AICertify is the AI-system slot in your existing policy strategy.

- **Bring your own Rego policies.** Drop a `.rego` file into the policy folder and it evaluates alongside the bundled set.
- **Evaluate AI interactions through OPA.** Captured inputs, outputs, and metrics flow into your policies via the standard OPA `input` document.
- **Generate audit-ready evidence.** PDF / Markdown / JSON / HTML, one command.
- **Use [gopal](https://github.com/Principled-Evolution/gopal) as the policy library underneath.** 91 production Rego policies covering the EU AI Act, the UK AI framework, NIST AI RMF, aviation safety, FERPA, fair lending, UK financial services and legal practice.

AICertify is listed in the [Open Policy Agent ecosystem](https://www.openpolicyagent.org/ecosystem/entry/principled-evolution) as the AI-governance entry alongside Gopal.

---

## Why AICertify?

Most AI governance programs live in PDFs, spreadsheets, and policy documents. They describe what *should* happen but do not prove what *did*.

AICertify turns governance rules into executable policy checks.

Instead of saying:

> "Our chatbot follows our responsible AI policy."

You can produce:

> "Here is the captured interaction, the policy version, the OPA evaluation result, and the generated audit report."

AICertify is for AI teams, governance teams, auditors, and platform engineers who need AI compliance evidence that can be **read, run, reviewed, and repeated**.

See the full positioning in [docs/why-aicertify.md](docs/why-aicertify.md).

---

## Who should contribute?

AICertify is especially useful for:

- **AI engineers** building regulated AI systems
- **Governance, risk, and compliance (GRC) teams** producing audit evidence
- **Auditors and model risk professionals** evaluating third-party AI
- **OPA / Rego users** interested in AI-specific policy authoring
- **Responsible AI researchers** wanting reproducible benchmarks
- **Python developers** interested in compliance automation

**Non-code contributions are welcome:** examples, policy mappings, docs, tests, report templates, and regulatory notes.

A good place to start is the [`good first issue`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and [`help wanted`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) labels.

---

## Contributing

We welcome:

- New regulatory frameworks (open an issue first to align scope)
- Industry-specific policies you've battle-tested
- New evaluators (fairness, safety, robustness, see `aicertify/evaluators/`)
- Bug reports with a minimal reproducing contract
- Documentation, examples, and tutorials

Start with [CONTRIBUTING.md](CONTRIBUTING.md), the [Code of Conduct](CODE_OF_CONDUCT.md), and the open [contributor issues](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

For security issues, please follow the [Security Policy](SECURITY.md): report privately to [security@principledevolution.ai](mailto:security@principledevolution.ai), not via public issue.

---

## Related Projects

- **[gopal](https://github.com/Principled-Evolution/gopal)**: the OPA policy library AICertify uses under the hood. Use it standalone with the OPA CLI if you don't need the Python framework.
- **[Open Policy Agent](https://www.openpolicyagent.org/)**: the policy engine.
- **[Regal](https://github.com/StyraInc/regal)**: Rego linter used to keep policies clean.

---

## License

Apache License 2.0, see [LICENSE](LICENSE).

---

<p align="center">
  <strong>⭐ If AICertify is useful to you, please star the repo and share it with one colleague.</strong><br>
  <sub>Every star helps AI governance and policy-as-code practitioners discover the project.</sub>
</p>

<p align="center"><sub>Built by <a href="https://github.com/Principled-Evolution">Principled Evolution</a> · Policies you can read, run, and prove.</sub></p>
