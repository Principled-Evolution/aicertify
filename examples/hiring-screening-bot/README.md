# Example: Hiring Screening Bot

A recruiting-AI example: an LLM-powered candidate-screening assistant evaluated against **EU AI Act high-risk obligations**, **gopal's banking & financial-services fair-lending policies** (the closest gopal proxy for fair-employment patterns), and the global fairness baseline.

## Why hiring is high-risk

Employment AI is named in EU AI Act **Annex III(4)** as a high-risk use case. Obligations:

- Mandatory **risk-management system** (Article 9)
- Mandatory **fundamental-rights impact assessment** for deployers (Article 27)
- Mandatory **human oversight** (Article 14) — no fully-automated rejection without human review
- Mandatory **non-discrimination** (Article 10) — bias testing across protected attributes
- Mandatory **transparency** — candidates must know AI is involved

In the US, EEOC, ADA, and state laws (e.g. NYC Local Law 144) impose overlapping audit obligations. Many of the same patterns surface in fair-lending policies (gopal `industry_specific/bfs/v1/loan_evaluation/fair_lending.rego`), which is why we evaluate against that bundle as an interim proxy until a dedicated `hiring/` framework lands.

## What this evaluates

| Aspect | Coverage |
|---|---|
| Application | First-pass candidate screening / question-answering assistant |
| Risk class (EU AI Act) | **High-risk** — Annex III(4) |
| Frameworks | EU AI Act + gopal `industry_specific/bfs/v1/loan_evaluation/fair_lending` + global |
| Evaluators | Fairness, ContentSafety, RiskManagement, Compliance, Transparency |
| Interactions | 8 captured input/output pairs (mixed candidate questions + recruiter questions) |

## Run it

```bash
python examples/hiring-screening-bot/run.py
```

## Adapt it

To use this pattern for your own recruiting tool:

1. **Audit your captured interactions** before evaluating. AICertify can only detect bias in what you record — if your screening logic happens in a hidden pre-prompt that never reaches the contract, the report will be falsely green.
2. **Never let the AI emit a final hire/no-hire decision.** Every output should be a candidate-fact summary, a question, or a routing action. Hire decisions require Article 14 human review.
3. **Disclose AI involvement to candidates.** Annex III + GDPR Article 22 require it.
4. **Run the bias evaluation against a diverse interaction set.** A green report on 5 interactions tells you very little. Aim for hundreds.

## Honest scope

A green AICertify report is **necessary but not sufficient** for deploying hiring AI. You also need:

- A documented fundamental-rights impact assessment (FRIA) under Article 27
- Bias testing on a real candidate population, not a 8-interaction fixture
- A clear appeals and human-review process
- Post-market monitoring (Article 72)
- Engagement with your employment-law counsel in every jurisdiction you operate

See [docs/why-aicertify.md](../../docs/why-aicertify.md) for what AICertify *does* and *doesn't* substitute for.

## Files

| File | Purpose |
|---|---|
| `input_contract.json` | Screening app + 8 captured interactions |
| `policy_config.yaml` | EU AI Act + fair-lending proxy + global bundle |
| `run.py` | Runnable AICertify Python API script |
| `expected_report.md` | What a successful run looks like |
