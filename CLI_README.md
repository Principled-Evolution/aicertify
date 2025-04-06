# AICertify Command Line Interface

This tool allows you to run AICertify evaluations from the command line.

## Installation

No additional installation is required if you already have AICertify installed.

## Usage

You can run the CLI tool using the wrapper script:

```bash
python aicertify_cli.py --contract <path_to_contract.json> --policy <policy_folder>
```

Or directly using the module:

```bash
python -m aicertify.cli --contract <path_to_contract.json> --policy <policy_folder>
```

## Arguments

### Required Arguments

- `--contract`: Path to the contract JSON file
- `--policy`: Path or name of the OPA policy folder

### Optional Arguments

- `--output-dir`: Directory to save the report (default: ./reports)
- `--report-format`: Format of the report (choices: json, markdown, pdf; default: pdf)
- `--evaluators`: Specific evaluators to use (space-separated list)
- `--params`: JSON string or path to JSON file with custom parameters for OPA policies
- `--verbose`: Enable verbose logging

## Examples

### Basic Usage

```bash
python aicertify_cli.py --contract examples/outputs/medical_diagnosis/contract_2025-03-03_183048.json --policy eu_fairness
```

### Specifying Output Directory and Report Format

```bash
python aicertify_cli.py --contract examples/outputs/medical_diagnosis/contract_2025-03-03_183048.json --policy eu_fairness --output-dir ./my_reports --report-format markdown
```

### Using Custom Parameters

```bash
python aicertify_cli.py --contract examples/outputs/medical_diagnosis/contract_2025-03-03_183048.json --policy eu_fairness --params '{"fairness_threshold": 0.9, "toxicity_threshold": 0.5}'
```

Or using a parameters file:

```bash
python aicertify_cli.py --contract examples/outputs/medical_diagnosis/contract_2025-03-03_183048.json --policy eu_fairness --params params.json
```

### Specifying Evaluators

```bash
python aicertify_cli.py --contract examples/outputs/medical_diagnosis/contract_2025-03-03_183048.json --policy eu_fairness --evaluators fairness content_safety
```

## Output

The tool will generate a report in the specified format and save it to the output directory. It will also print a summary of the evaluation results to the console.

## Troubleshooting

If you encounter any issues, try running with the `--verbose` flag to get more detailed logging information:

```bash
python aicertify_cli.py --contract examples/outputs/medical_diagnosis/contract_2025-03-03_183048.json --policy eu_fairness --verbose
```
