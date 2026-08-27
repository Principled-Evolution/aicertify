# Running AICertify in GitHub Actions

AI compliance checks belong on every pull request, not only at release time. This page shows how to copy [`.github/workflows/example-aicertify.yaml`](../../.github/workflows/example-aicertify.yaml) into your own repository and turn it into a required status check.

## What you copy

| File | Where it goes | What it does |
| --- | --- | --- |
| [`.github/workflows/example-aicertify.yaml`](../../.github/workflows/example-aicertify.yaml) | `.github/workflows/ai-compliance.yaml` | Installs AICertify and OPA, evaluates a contract, uploads the report |
| [`examples/github-actions/gate.py`](../../examples/github-actions/gate.py) | anywhere the workflow can reach | Turns the verdict into an exit code |

## Inputs

Three values control the run. In the example they are `workflow_dispatch` inputs so you can try combinations from the Actions tab; in your own copy, hard-code them in `env:` and drop the inputs block.

| Input | Meaning | Default |
| --- | --- | --- |
| `contract` | Path to the contract JSON describing your AI system | `examples/customer-support-bot/input_contract.json` |
| `framework` | Framework to evaluate against: `eu_ai_act`, `uk`, `bfs`, `legal`, `nist`, … | `eu_ai_act` |
| `fail_on` | `any` fails the build when a policy denies. `none` reports only | `none` |

Run `aicertify explain <framework>` to see the frameworks available and the fields each one reads.

## Adopt it in three steps

**1. Start on `fail_on: none`.**

Your first run will almost certainly report denials, and that is informative rather than alarming: most GOPAL obligations turn on facts no evaluator can observe, and a contract that has not declared them cannot satisfy them. Reporting first lets you see the gap without a red build.

**2. Populate the contract.**

```bash
aicertify explain eu_ai_act                              # what the policies read
aicertify init-contract --policy eu_ai_act > contract.json   # the same fields, to fill in
```

`init-contract` writes every declared field as a `null` under `context`, nested into the shape the policies read. Replace the nulls. A field left as `null` is dropped rather than sent as an explicit null, so a half-filled contract denies rather than being read as "assessed, and false".

**3. Switch to `fail_on: any` and make it required.**

Once the report is clean, set `fail_on: any`, then **Settings → Branches → Branch protection rules → Require status checks to pass** and select the job.

## Two things that will bite you

**Check out the submodule.** The policy library lives at `aicertify/opa_policies` as a git submodule. Without `submodules: true` on `actions/checkout`, there are no policies at all, and the failure mode is quiet: the evaluation produces zero verdicts rather than an obvious error.

```yaml
- uses: actions/checkout@v4
  with:
    submodules: true
```

`gate.py` treats zero verdicts as exit code 2 rather than a pass, specifically so this misconfiguration cannot look like success.

**Cache the model downloads.** The fairness and content-safety evaluators pull transformer models on first use, and that dominates the run time. A cold run takes many minutes; a warm one is far quicker.

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/huggingface
      ~/.cache/torch
    key: aicertify-models-${{ runner.os }}-${{ hashFiles('pyproject.toml') }}
```

## Exit codes

`gate.py` distinguishes three outcomes, and the distinction is the point:

| Code | Meaning |
| --- | --- |
| 0 | Every policy passed, or `--fail-on none` |
| 1 | At least one policy denied, and `--fail-on any` |
| 2 | The evaluation could not be carried out |

Code 2 covers a missing contract, an OPA failure, and an evaluation that produced no verdicts. A run that failed to produce verdicts has told you nothing, and folding that into "not a failure" is how a compliance pipeline reports green while checking nothing.

## What you get out

- **A job summary table** of every policy and its verdict, visible on the run page without opening the log.
- **Annotations** on each denied policy, so the reason appears inline on the pull request.
- **`compliance-summary.json`**, machine-readable, for anything downstream:

  ```json
  {
    "framework": "uk",
    "total": 6,
    "passed": 6,
    "failed": 0,
    "policies": [{ "name": "UK GDPR Automated Decision-Making (Articles 22A-22D)", "passed": true }]
  }
  ```

- **The generated report**, uploaded with `if: always()` so it survives a failing gate. That artifact is the evidence the check ran and what it decided.

## Evaluating more than one framework

Call the gate once per framework with a matrix. `fail-fast: false` so one denial does not hide the rest:

```yaml
strategy:
  fail-fast: false
  matrix:
    framework: [eu_ai_act, uk, global]
steps:
  # …
  - run: |
      python examples/github-actions/gate.py \
        --contract contract.json \
        --policy ${{ matrix.framework }} \
        --fail-on any \
        --summary-json compliance-summary-${{ matrix.framework }}.json
```

## Policies without the Python stack

If you only want the Rego verdicts and none of the evaluator machinery, skip AICertify and run the GOPAL bundles directly. That job needs OPA and nothing else, and finishes in seconds. See [gopal's GitHub Actions example](https://github.com/Principled-Evolution/gopal/tree/main/examples/github-actions).

Use AICertify's workflow when you want fairness and content-safety metrics computed from real interactions, and the audit-ready report. Use the GOPAL bundle when your compliance facts are declarations and you just need them checked.
