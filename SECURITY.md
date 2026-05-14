# Security Policy

## Reporting a Vulnerability

Please report security issues **privately** by emailing
[security@principledevolution.ai](mailto:security@principledevolution.ai).

**Do not open public GitHub issues** for suspected vulnerabilities. Public disclosure
before a fix is shipped puts every AICertify user at risk.

We aim to acknowledge reports within **5 business days** and to publish a fix or a
written mitigation plan within 30 days of confirming a valid report. Severity is
assessed against the [CVSS 3.1](https://www.first.org/cvss/v3.1/specification-document)
framework.

If you would like to encrypt your report, request our PGP key in the initial email and
we will share it before you send the technical detail.

## Scope

This policy covers:

- the `aicertify` Python package and its public API,
- the AICertify CLI (`python -m aicertify.cli`),
- the bundled examples under `examples/`,
- the policy evaluation logic against the vendored [gopal](https://github.com/Principled-Evolution/gopal) Rego policies,
- the report generation pipeline (PDF, Markdown, JSON, HTML).

Out of scope:

- vulnerabilities in upstream dependencies that already have a published CVE — please
  report those upstream (we track them via GitHub Dependabot),
- attacks that require physical access to a machine running AICertify,
- denial-of-service via legitimate but expensive evaluation workloads.

## Coordinated Disclosure

We follow a coordinated disclosure model. Once a fix is available, we will:

1. Publish a patched release on PyPI (or the equivalent install path),
2. Publish a [GitHub Security Advisory](https://github.com/Principled-Evolution/aicertify/security/advisories) with credit to the reporter (unless anonymity is requested),
3. Reference the advisory in [CHANGELOG.md](CHANGELOG.md),
4. Update affected examples and documentation.

We are happy to publicly credit reporters who request it; we will never publish your
identity without explicit permission.

## Hardening notes

For users running AICertify in regulated or audit-sensitive environments:

- pin AICertify to a specific patched version in your dependency manifest,
- run evaluations in an isolated environment (container or virtual machine) when the AI
  application under test handles sensitive data,
- review the captured contract JSON before sharing it — by design, contracts include
  the AI application's input and output text.

For policy authors: see the [gopal](https://github.com/Principled-Evolution/gopal)
SECURITY policy for upstream policy library reporting.
