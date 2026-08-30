# Why AICertify

AICertify exists to make the evidence used in AI-governance decisions inspectable, repeatable, and suitable for automation.

## The problem it addresses

An AI system can change independently of the documents that describe its governance or compliance state. Model versions, prompts, retrieval indexes, application logic, and operating context can change between formal reviews. When the system state and the evidence record are maintained separately, a later report may describe a different system from the one currently being operated.

AICertify does not solve that problem by assigning a universal compliance score. Within a pinned source checkout, it assembles the available system evidence, evaluates that evidence against the checkout's GOPAL revision, and produces structured verdicts and reports. Reproducing the evaluation later requires retaining or recording the relevant AICertify/GOPAL revision together with the policy inputs.

## The evidence model

An AICertify evaluation can contain four distinct inputs and outputs:

1. **Declared facts** — information about the system or governance process that is supplied in the contract, such as whether human intervention is available or whether a required assessment has been completed.
2. **Captured interactions** — prompts, outputs, and related application data used as evaluation material.
3. **Measured metrics** — values computed or imported by evaluators and adapters, such as fairness, toxicity, content-safety, or model-card completeness metrics.
4. **Versioned policy decisions** — OPA evaluates the assembled input against Rego policies from the pinned [GOPAL](https://github.com/Principled-Evolution/gopal) revision, and AICertify exposes the resulting verdicts and reports.

These evidence types are intentionally not treated as equivalent. A measured metric can support a threshold check. A declared fact records an assertion and allows a rule to require it, but the rule does not independently verify that the asserted process or event occurred.

## Reproducibility and provenance

The GOPAL policy library is pinned as a git submodule. An AICertify repository revision therefore identifies the policy revision used by that checkout.

Once the policy input values and Rego revision are fixed, OPA rule evaluation is deterministic. Reproducibility of the inputs themselves depends on how they were produced: deterministic metric adapters can be reproduced from the same source data, while evaluators that call external or generative models may have additional model-version, service, and sampling dependencies.

A reproducible evaluation record therefore needs the following provenance chain:

**system/version → contract and interactions → measured metrics + declared facts → policy revision → OPA verdicts → retained report**

AICertify makes these stages explicit; the calling workflow is responsible for retaining the revisions and source evidence needed to reproduce them.

## Where AICertify fits

AICertify combines components that are useful independently:

- **Evaluator libraries** produce measurements from application behavior or artifacts.
- **GOPAL** provides named AI-governance and regulatory policies as readable Rego.
- **OPA** evaluates those policies against a supplied input document.
- **AICertify** captures application context, runs or ingests evaluators, assembles policy input, invokes OPA, and generates retained outputs for local, CI, and assurance workflows.

If your facts and metrics already exist and you only need Rego evaluation, GOPAL with OPA is the smaller tool. AICertify is useful when the evaluation pipeline also needs application context, measured metrics, policy discovery, reporting, or CI integration.

## Who it is for

AICertify is designed for teams that need the evaluation record to be understandable by both engineering and governance functions:

- **AI engineers** integrating policy checks with application development and release workflows.
- **Governance, risk, and compliance teams** maintaining evidence for named controls or regulatory requirements.
- **Auditors and model-risk teams** reviewing the inputs, policy version, and resulting decisions.
- **Platform engineers and OPA/Rego users** applying existing policy-as-code practices to AI-system evidence.
- **Responsible-AI researchers and evaluator authors** connecting measured behavior to explicit policy thresholds.

## What AICertify does not establish

AICertify is an evaluation and evidence framework, not a certification authority.

- A Rego policy is an explicit implementation of a regulatory or governance interpretation; it is reviewable code, not legal advice.
- A passing verdict means the supplied evidence satisfies the encoded rule at the evidence depth that rule uses. It does not convert a declaration into independent verification.
- A generated report records an evaluation result. Whether that result is sufficient for a regulatory submission, assurance opinion, internal approval, or certification remains a decision for the responsible organization and its advisers.
- AICertify complements governance processes; it does not replace organizational controls that cannot be established from software inputs.

This boundary is a design property rather than a limitation to hide. The policy, required inputs, evidence type, and resulting verdict remain inspectable.

## Why policy-as-code matters here

Readable Rego policies make the evaluation criteria reviewable in the same workflow as other code. A policy revision can be diffed, tested, pinned, cited, and run against the same input before it is adopted. That makes changes to the rule itself distinguishable from changes to the AI system or its measured behavior.

For policy coverage and per-policy input requirements, see [GOPAL](https://github.com/Principled-Evolution/gopal). For AICertify's evaluator adapters, see [adapters.md](adapters.md).

## Next steps

- **Inspect a generated artifact without installing:** [demo-report-eu-ai-act.pdf](demo-report-eu-ai-act.pdf)
- **Run the bundled demo:** `aicertify demo`
- **See what a framework requires:** `aicertify explain eu_ai_act`
- **Scaffold a contract:** `aicertify init-contract --policy eu_ai_act > contract.json`
- **Run the Python example:** [`examples/quickstart.py`](../examples/quickstart.py)
- **Integrate a pull-request gate:** [GitHub Actions guide](integrations/github-actions.md)
