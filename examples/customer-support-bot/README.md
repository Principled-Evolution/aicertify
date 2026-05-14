# Example: Customer Support Bot

A canonical AICertify example: a customer-support LLM evaluated against the **EU AI Act**.

This is the simplest realistic use case — a chatbot answering refund/billing questions — and it demonstrates the full AICertify loop with minimal boilerplate. Fork this directory as the starting point for your own AI-application evaluation.

## What this evaluates

| Aspect | Coverage |
|---|---|
| Application | Customer-facing support agent |
| Risk class (EU AI Act) | Limited risk — transparency obligations apply |
| Framework | EU AI Act (v1, gopal) |
| Evaluators | ContentSafety, Fairness, Transparency, RiskManagement |
| Interactions evaluated | 8 captured input/output pairs |
| Report format | PDF + Markdown |

## Files

| File | Purpose |
|---|---|
| `input_contract.json` | The AI application contract — name, model, captured interactions |
| `sample_interactions.json` | Standalone interaction set you can add to a contract |
| `policy_config.yaml` | Which gopal policies to evaluate against |
| `run.py` | Runnable script using the AICertify Python API |
| `expected_report.md` | What you should see after running |

## Run it

From the repo root:

```bash
python examples/customer-support-bot/run.py
```

The report lands in `reports/` (relative to the repo root). Open the PDF — that's what a regulator wants to see.

## Adapt it

To make this example your own AI application:

1. Edit `input_contract.json`. Change `application_name`, `model.model_name`, and `model.model_version` to your system.
2. Replace `interactions[]` with your captured input/output pairs. Each interaction is `{input_text, output_text, metadata}`.
3. Update `policy_config.yaml` to add the frameworks that matter to your jurisdiction or industry.
4. Re-run `python run.py`.

## What to look for in the report

- **Executive Summary** — headline pass/fail per framework
- **Policy Results** — per-policy `allow` / `deny` with the deny message where applicable
- **Risk Assessment** — aggregated bias, content-safety, and risk-management metrics
- **Remediation Guidance** — what to fix to close the gap

If everything is green, your contract + interactions + chosen policies all align. If any rule fails, the report tells you which article of the regulation it maps to and what specifically failed.

## Beyond this example

For more elaborate setups, see the sibling examples:

- [`healthcare-triage-bot/`](../healthcare-triage-bot/) — medical AI evaluated for patient safety
- [`hiring-screening-bot/`](../hiring-screening-bot/) — recruiting AI evaluated for fair-employment compliance
