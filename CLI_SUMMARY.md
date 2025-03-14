# AICertify CLI Implementation Summary

## Overview

We have implemented a command-line interface (CLI) for the AICertify tool that allows users to run evaluations from the command line. The CLI provides a simple and intuitive way to evaluate AI contracts against OPA policies and generate reports.

## Files Created

1. **aicertify/cli.py**: The main CLI module that parses arguments and calls the appropriate functions.
2. **aicertify_cli.py**: A wrapper script that provides a simple entry point for the CLI.
3. **CLI_README.md**: Documentation on how to use the CLI tool.
4. **CLI_ARCHITECTURE.md**: A component diagram showing the architecture of the CLI tool.
5. **CLI_SEQUENCE.md**: A sequence diagram showing the flow of the CLI tool.
6. **test_cli.sh**: A shell script that demonstrates how to use the CLI tool.
7. **example_params.json**: An example parameters file for the eu_fairness policy.

## How to Use the CLI Tool

### Basic Usage

```bash
python aicertify_cli.py --contract <path_to_contract.json> --policy <policy_folder>
```

### With Custom Parameters

```bash
python aicertify_cli.py --contract <path_to_contract.json> --policy <policy_folder> --params <params_file.json>
```

### Running the Test Script

```bash
./test_cli.sh
```

## Implementation Details

The CLI tool leverages the existing functionality in the AICertify API, particularly the `evaluate_contract_by_folder` function. This function performs a comprehensive evaluation of a contract using both Phase 1 evaluators and OPA policies.

The CLI tool provides a simple interface to this functionality, allowing users to specify the contract, policy folder, and other options via command-line arguments.

## Architecture

The CLI tool follows a modular architecture, with clear separation of concerns:

- **CLI Module**: Handles argument parsing and user interaction.
- **API Module**: Provides the core functionality for contract evaluation.
- **Contract Loader**: Loads contracts from JSON files.
- **OPA Evaluator**: Evaluates contracts against OPA policies.
- **Report Generator**: Generates reports based on evaluation results.

This architecture ensures that the CLI tool is maintainable, extensible, and easy to use.

## Next Steps

1. **Testing**: Thoroughly test the CLI tool with various contracts and policies.
2. **Documentation**: Update the main AICertify documentation to include information about the CLI tool.
3. **Integration**: Consider integrating the CLI tool into the main AICertify package.
4. **Extensions**: Add support for additional features, such as batch processing of multiple contracts.

## Conclusion

The AICertify CLI tool provides a convenient way to run evaluations from the command line, making it easier for users to integrate AICertify into their workflows. The tool is designed to be simple, intuitive, and powerful, providing access to the full functionality of the AICertify API. 