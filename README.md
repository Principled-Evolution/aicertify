# AICertify: AI Regulatory Compliance Framework

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Status: Beta](https://img.shields.io/badge/status-beta-orange.svg)](https://github.com/Principled-Evolution/aicertify)
[![Version: 0.7.0](https://img.shields.io/badge/version-0.7.0-brightgreen.svg)](https://github.com/Principled-Evolution/aicertify)

AICertify is a library for evaluating AI applications against various compliance frameworks and regulations.

> **Note:** AICertify is currently in beta stage (v0.7.0). The API may change between versions as we work toward a stable 1.0.0 release.

## Overview

AICertify provides tools to:

- Create and manage AI application contracts
- Evaluate AI interactions against regulatory frameworks
- Generate compliance reports
- Identify potential risks and issues in AI systems

## Installation

```bash
# Install from source
pip install -e .
```

## Quickstart

The simplest way to get started with AICertify is to run the quickstart example:

```bash
python examples/quickstart.py
```

This example demonstrates:
- Creating a regulations set
- Selecting target regulations
- Creating AI applications
- Adding interactions to applications
- Evaluating applications against regulations
- Generating and viewing reports

## Core Components

- **Application Management**: Create and configure AI applications
- **Regulation Sets**: Select and manage regulatory frameworks
- **Evaluation**: Evaluate applications against regulations
- **Reporting**: Generate detailed compliance reports

## OPA Policy Integration

AICertify uses Open Policy Agent (OPA) for policy definition and evaluation. Policies are organized in the following structure:

- `global/`: Globally applicable policies
- `industry_specific/`: Industry-specific policies
- `international/`: Policies for international regulations
- `custom/`: Directory for user-defined policies

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
