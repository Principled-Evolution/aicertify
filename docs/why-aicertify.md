# Why AICertify?

## The gap

Most AI governance programs live in PDFs, spreadsheets, and policy documents. They describe what *should* happen — but do not prove what *did*.

Auditors don't accept "we have a policy." They accept evidence: a dated record of the AI system under test, the rule it was evaluated against, the result, and the document signed off by the responsible owner. Producing that evidence by hand, every release, for every regulation, for every AI system in your portfolio, is not a sustainable program.

## The shift

The DevOps and platform engineering communities solved a similar problem ten years ago by moving infrastructure from documents into code: Terraform replaced cloud-architecture diagrams, Helm replaced runbooks, [Open Policy Agent](https://www.openpolicyagent.org/) replaced security-policy memos. The pattern in every case was the same — *take the rule out of the document and put it into a thing that runs.*

AICertify applies that shift to AI governance.

## The artifact AICertify produces

Instead of saying:

> "Our customer-support chatbot follows our responsible AI policy."

You produce:

> "Here is the contract that captured the chatbot's model version, the captured user-AI interactions, the EU AI Act v1 transparency policy (commit `a52d605`), the OPA evaluation result, the per-rule deny messages where applicable, and the dated PDF report sent to the audit committee."

Every artifact is reproducible: same input, same policy, same result. Every claim is traceable: the policy is code in git, the evaluation is deterministic, the report is generated, not handwritten.

## Who is this for?

AICertify exists for teams that need to **read, run, review, and repeat** their AI compliance evidence:

- **AI engineers** building under the EU AI Act, NIST AI RMF, India DPDP, Brazil AI Bill, FERPA/COPPA, FAA UAS rules, or any other named framework.
- **Governance, risk, and compliance (GRC) teams** who want their controls to *execute*, not just describe.
- **Auditors and model risk professionals** evaluating third-party AI systems.
- **Platform engineers** integrating AI compliance checks into CI/CD next to their linting, type-checking, and dependency scanning.
- **OPA / Rego users** who already trust policy-as-code for infrastructure and want the same discipline for AI.
- **Responsible AI researchers** who need reproducible bias, content-safety, and risk-management benchmarks.

## How AICertify is different

| | AICertify | Vendor SaaS (Credo AI, Holistic AI) | Research toolkit (Fairlearn, AIF360, MS RAI Toolbox) |
|---|---|---|---|
| Open source | ✅ Apache 2.0 | ❌ Closed | ✅ MIT |
| Air-gapped / on-prem deployable | ✅ | ❌ | ✅ |
| Policy-as-code (versioned, diff-able, reviewable) | ✅ OPA / Rego | ❌ | ❌ |
| Named regulatory frameworks (EU AI Act, NIST RMF, +13 more) | ✅ via [gopal](https://github.com/Principled-Evolution/gopal) | ✅ | ❌ (fairness/explainability only) |
| Industry verticals out of the box (aviation, banking, healthcare, education, automotive) | ✅ | Partial | ❌ |
| Audit-ready report output (PDF / Markdown / JSON / HTML) | ✅ | ✅ | Partial |
| Custom policies | ✅ Drop a `.rego` file | ✅ (paid tier) | N/A |
| Reproducible from a git checkout | ✅ | ❌ | ✅ |

## The honest scope

AICertify is **infrastructure**, not magic.

- It does not interpret regulations for you. Encoding "EU AI Act Article 13 transparency" as a Rego policy is a deliberate, reviewable act, and the policy is a human's interpretation, not a legal opinion. Read [SECURITY.md](../SECURITY.md), the per-framework READMEs, and the disclaimer on every policy directory before claiming compliance.
- It does not certify your AI system. It produces the evidence a human or organisation needs in order to assert compliance, internally or to a regulator. The certification authority remains your auditor, your legal counsel, or the relevant supervisor.
- It does not replace your governance program. It replaces the *paperwork* in your governance program.

What it *does* give you is the missing link between *"we have a responsible-AI policy"* and *"we can prove it."*

## Next steps

- **See the output without installing:** open [demo-report-eu-ai-act.pdf](demo-report-eu-ai-act.pdf).
- **Run the quickstart:** [`examples/quickstart.py`](../examples/quickstart.py).
- **Explore the policy library:** [gopal](https://github.com/Principled-Evolution/gopal) — 94 production Rego policies across 15+ frameworks.
- **Open a [good first issue](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).**
