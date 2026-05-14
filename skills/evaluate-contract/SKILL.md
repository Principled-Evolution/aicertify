---
name: evaluate-contract
description: Evaluate a user-provided AI application contract JSON against a chosen regulation and generate a compliance report. Use this when the user has their own contract file and wants to run AICertify against a specific framework.
argument-hint: "<contract.json> <framework> [report-format]"
---

# Evaluate Contract

Run AICertify against a user-supplied contract file and produce a report.

## Inputs

The user provides:
- **contract** — Path to a contract JSON. See `examples/sample_contract.json` for the schema.
- **framework** — One of: `eu_ai_act`, `nist`, `india`, `brazil`, `healthcare`, `bfs`, `automotive`, `aviation`, `education`. Map this to the policy directory under `aicertify/opa_policies/`.
- **report-format** — Optional. `pdf` (default), `markdown`, `json`, `html`.

## Steps

1. **Validate the contract** — Read the file, confirm it parses as JSON and contains at minimum: `application.name`, `model`, `interactions`. If any are missing, stop and tell the user which fields are absent.

2. **Resolve the policy path** — Look in `aicertify/opa_policies/` for the framework directory. Most frameworks live at:
   - `international/<framework>/v1/`
   - `industry_specific/<framework>/v1/`
   If the framework directory doesn't exist or is marked as a placeholder, surface that to the user before running.

3. **Run the evaluation**:
   ```bash
   python -m aicertify.cli \
     --contract <contract_path> \
     --policy <resolved_policy_path> \
     --report-format <format> \
     --output-dir reports/
   ```

4. **Locate and summarize the report**:
   - Identify the new file in `reports/`.
   - Print: framework evaluated, headline pass/fail, count of policies evaluated, count of failures.
   - If the report is JSON, parse and surface the top 3 failing rules with their `deny[msg]` strings.

5. **Suggest next actions** if there are failures:
   - For each top failure, identify the corresponding `.rego` file and quote the rule.
   - Recommend either fixing the AI application input or filing an issue if the policy is wrong.

## Notes

- Never edit `aicertify/opa_policies/*.rego` files in this repo without considering whether the change should land upstream in [gopal](https://github.com/Principled-Evolution/gopal) first. They are a vendored copy.
- If the user's contract is missing captured interactions, point them at `examples/sample_contract.json` for the shape.
