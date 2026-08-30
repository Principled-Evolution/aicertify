# AICertify Examples

Forkable references for evaluating real AI applications with AICertify.

## Quickstart

A minimal end-to-end demo of the AICertify API.

```bash
python examples/quickstart.py
```

Creates a sample app, adds a few interactions, evaluates against the EU AI Act, and writes a report into `reports/`. Read [`quickstart.py`](quickstart.py) before adapting it.

## Forkable application examples

Each folder is a self-contained reference you can copy as the starting point for evaluating your own AI application. The shape is the same in every example so the pattern is easy to follow:

```
example-name/
├── README.md                  How to run + how to adapt
├── input_contract.json        AI application contract (model + interactions + metadata)
├── sample_interactions.json   Standalone interaction set you can splice into a contract
├── policy_config.yaml         Which gopal policies + evaluators to run against
├── run.py                     Runnable script using the Python API
└── expected_report.md         What a successful run looks like
```

### Available examples

| Example | Risk class | Primary frameworks |
|---|---|---|
| [`customer-support-bot/`](customer-support-bot/) | Limited risk | EU AI Act transparency obligations + global baselines |
| [`healthcare-triage-bot/`](healthcare-triage-bot/) | **High risk** (Annex III) | EU AI Act high-risk + gopal healthcare patient-safety |
| [`hiring-screening-bot/`](hiring-screening-bot/) | **High risk** (Annex III) | EU AI Act high-risk + fair-lending proxy + global fairness |

### Contributing an example

Additional examples should follow the same directory shape so they remain directly forkable. Current contribution areas include:

- FastAPI integration example
- LangChain integration example
- LlamaIndex integration example
- Financial-advice bot
- EdTech tutor
- Docker quickstart

See the [`good first issue`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) and [`help wanted`](https://github.com/Principled-Evolution/aicertify/issues?q=is%3Aissue+is%3Aopen+label%3A%22help+wanted%22) labels.

## Inspecting expected output

Each maintained application example includes an `expected_report.md`, so its report structure and expected policy results can be inspected without running evaluator dependencies:

- [`customer-support-bot/expected_report.md`](customer-support-bot/expected_report.md)
- [`healthcare-triage-bot/expected_report.md`](healthcare-triage-bot/expected_report.md)
- [`hiring-screening-bot/expected_report.md`](hiring-screening-bot/expected_report.md)

A generated PDF from the bundled demonstration is available at [`docs/demo-report-eu-ai-act.pdf`](../docs/demo-report-eu-ai-act.pdf). The [`outputs/loan_evaluation/`](outputs/loan_evaluation/) directory also retains a historical contract and PDF from a fair-lending run.

## Authoring conventions

When you add an example:

1. Match the directory layout above. Keep the directory shape consistent so examples can be forked and compared directly.
2. The `metadata` block in `input_contract.json` must declare jurisdiction, risk class, and (if Annex III) the relevant subpoint.
3. `policy_config.yaml` must include a `rationale:` for each framework explaining *why* that framework applies.
4. `expected_report.md` should describe both the pass case **and** the common failure modes expected when the example is adapted.
5. State scope and evidence limitations explicitly. A passing policy result establishes only that the supplied evidence satisfied the encoded rule at that rule's evidence depth.
