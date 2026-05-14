---
name: run-compliance-check
description: Run the AICertify end-to-end quickstart against the EU AI Act policy set and inspect the generated compliance report. Use this when the user wants to verify AICertify works in their environment, see a sample audit deliverable, or smoke-test after a change.
argument-hint: "[optional: report-format pdf|markdown|json|html]"
---

# Run Compliance Check

Execute the canonical AICertify quickstart and produce a real compliance report.

## Steps

1. **Verify environment** — confirm the user is in the AICertify repo root and `pip install -e .` has run. If not, instruct them once.

2. **Choose the report format** — default to `pdf`. If the user passed an argument, honor it.

3. **Run the quickstart**:
   ```bash
   python examples/quickstart.py
   ```
   This wires a sample AI application through the EU AI Act policy set.

4. **Locate the output** — reports land in `reports/` (relative to repo root). List the directory and identify the new files by timestamp.

5. **Summarize for the user**:
   - Path of the generated report(s)
   - File size + format
   - One-sentence summary of the headline pass/fail result (parse the JSON report if present, else open the markdown header)
   - Inline a 5-line excerpt of the report's Executive Summary if available

6. **Surface anything broken** — if the run errors, capture the stack trace, identify the failing module, and suggest the most likely fix (missing dep, OPA binary not in PATH, Python version mismatch). Do not silently retry.

## Notes

- The quickstart accumulates artifacts in `reports/`. If the directory gets large, suggest archiving but do not delete without confirmation.
- For CLI-style usage instead of the quickstart, run:
  ```bash
  python -m aicertify.cli \
    --contract examples/sample_contract.json \
    --policy aicertify/opa_policies/international/eu_ai_act/v1 \
    --report-format pdf
  ```
