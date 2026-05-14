# Example: Healthcare Triage Bot

A medical-AI example: an LLM-powered triage assistant that helps patients decide whether a symptom needs urgent care, evaluated against **EU AI Act high-risk obligations** and **gopal's healthcare patient-safety policies**.

> **Closes [Issue #8](https://github.com/Principled-Evolution/aicertify/issues/8)** — the long-standing request for a medical-industry example.

## Why healthcare is special

Healthcare AI in the EU AI Act is **high-risk** (Annex III), which means tighter obligations than the customer-support example:

- Mandatory **human oversight** (Article 14)
- Mandatory **technical documentation** (Article 11)
- Mandatory **record keeping** of decisions and inputs (Article 12)
- Mandatory **risk-management system** (Article 9)
- Mandatory **post-market monitoring** (Article 72)

Plus US/EU healthcare-specific obligations:

- Patient safety: diagnostic accuracy claims must be calibrated to evidence
- Privacy: explicit consent and minimisation (HIPAA-equivalent / GDPR Article 9)
- Disclosure: the patient must know they are interacting with AI

This example demonstrates a **safe** medical-triage interaction set — one that *passes* the policies — alongside notes on the common failure modes.

## What this evaluates

| Aspect | Coverage |
|---|---|
| Application | Patient-facing symptom triage assistant |
| Risk class (EU AI Act) | **High-risk** — Annex III, point 5(a) |
| Frameworks | EU AI Act + gopal `industry_specific/healthcare/v1/` |
| Evaluators | ContentSafety, RiskManagement, Compliance, Transparency |
| Interactions evaluated | 8 captured input/output pairs (symptom triage + escalation paths) |

## Run it

```bash
python examples/healthcare-triage-bot/run.py
```

Report lands in `reports/`.

## Adapt it

This example is intentionally conservative — the bot **never** issues a diagnosis or treatment recommendation and **always** routes to a clinician for anything beyond the most common self-care guidance. If you fork this:

1. Confirm your clinical decision boundary is at least as conservative.
2. Update `input_contract.json` with your captured interactions and model metadata.
3. If your jurisdiction has additional obligations (FDA Software-as-a-Medical-Device, MDR in the EU), open a [gopal](https://github.com/Principled-Evolution/gopal) issue requesting framework coverage.

## What "passing" means here

A green report does **not** clear the application for clinical deployment. It demonstrates that the captured interactions are compatible with the encoded policies. Clearance for clinical use requires additional clinical evaluation, regulator notification (where applicable), and a clinician-in-the-loop validation that AICertify does not substitute for. See [SECURITY.md](../../SECURITY.md) and [docs/why-aicertify.md](../../docs/why-aicertify.md) for the honest scope.

## Files

| File | Purpose |
|---|---|
| `input_contract.json` | Triage application + 8 captured interactions |
| `policy_config.yaml` | EU AI Act + healthcare/v1 policy bundle |
| `run.py` | Runnable AICertify Python API script |
| `expected_report.md` | What a successful run looks like |
