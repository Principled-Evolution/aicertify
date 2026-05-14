"""Demo runner used by ``aicertify demo``.

Loads the bundled sample contract, runs an OPA evaluation against a chosen
vendored policy folder, and writes a Markdown report to the user's CWD.

Designed to work after ``pip install aicertify`` with no extra configuration
beyond the OPA binary on PATH. Heavy ML-based evaluators are skipped by
default; the OPA verdict is the substance.
"""

from __future__ import annotations

import json
import logging
import platform
import shutil
import sys
from importlib.resources import files
from pathlib import Path
from typing import Optional

logger = logging.getLogger("aicertify.demo")


DEFAULT_POLICY = "eu_ai_act"
DEFAULT_REPORT_NAME = "aicertify_demo_report.md"

# Map friendly framework names to the bundled directory under aicertify/opa_policies/
# that we use to verify the framework is present in the wheel.
_BUNDLED_POLICY_PROBE_PATH = {
    "eu_ai_act": ("international", "eu_ai_act", "v1"),
    "nist": ("international", "nist", "v1"),
    "global": ("global", "v1"),
    "global/v1": ("global", "v1"),
}


def opa_binary_path() -> Optional[str]:
    """Return the path to the opa binary on PATH, or None."""
    return shutil.which("opa")


def print_opa_install_instructions() -> None:
    """Print friendly, platform-specific OPA install instructions to stderr."""
    system = platform.system().lower()
    if system == "linux":
        url = "https://openpolicyagent.org/downloads/latest/opa_linux_amd64"
        install = (
            f"curl -L {url} -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa"
        )
    elif system == "darwin":
        url = "https://openpolicyagent.org/downloads/latest/opa_darwin_amd64"
        install = (
            f"curl -L {url} -o /usr/local/bin/opa && sudo chmod +x /usr/local/bin/opa"
        )
    elif system == "windows":
        url = "https://openpolicyagent.org/downloads/latest/opa_windows_amd64.exe"
        install = f"curl -L {url} -o opa.exe (or download from {url})"
    else:
        url = "https://openpolicyagent.org/docs/latest/#1-download-opa"
        install = f"see {url}"

    msg = f"""
✗ The OPA binary was not found on PATH.

OPA (Open Policy Agent) is the engine that evaluates Rego policy files.
AICertify uses it to evaluate AI-governance rules against your AI's
captured interactions.

Install it with one command:

  {install}

Then re-run: aicertify demo

More info: https://openpolicyagent.org/docs/latest/#1-download-opa
"""
    print(msg, file=sys.stderr)


def bundled_contract_path() -> Path:
    """Return the path to the bundled sample contract JSON."""
    return Path(str(files("aicertify._demo") / "sample_contract.json"))


def bundled_policy_path(policy: str) -> Path:
    """Return the bundled policy directory we expect to exist for ``policy``.

    Used only as an existence probe so the demo can fail fast with a friendly
    message if the wheel was stripped or the framework name is unknown. The
    actual evaluation passes the friendly framework name (e.g. ``eu_ai_act``)
    to the lib's ``find_matching_policy_folders``, which then resolves it to
    the absolute directory and recurses for ``.rego`` files.
    """
    probe = _BUNDLED_POLICY_PROBE_PATH.get(policy)
    if probe is None:
        # Unknown friendly name; fall back to treating the input as a
        # path relative to opa_policies/.
        probe = ("opa_policies", *policy.split("/"))
    else:
        probe = ("opa_policies", *probe)
    p = files("aicertify")
    for part in probe:
        p = p / part
    return Path(str(p))


async def run_demo(
    output: str = DEFAULT_REPORT_NAME,
    report_format: str = "markdown",
    policy: str = DEFAULT_POLICY,
) -> int:
    """Run the bundled demo. Returns a shell-style exit code."""
    if opa_binary_path() is None:
        print_opa_install_instructions()
        return 1

    contract_file = bundled_contract_path()
    if not contract_file.exists():
        print(
            f"✗ Bundled sample contract missing at {contract_file}. "
            f"This is a packaging bug — please file an issue.",
            file=sys.stderr,
        )
        return 1

    policy_dir = bundled_policy_path(policy)
    if not policy_dir.exists():
        print(
            f"✗ Bundled policy directory {policy} not found at {policy_dir}. "
            f"Try one of: international/eu_ai_act/v1, global/v1, "
            f"international/nist/v1",
            file=sys.stderr,
        )
        return 1

    # Load sample contract as an AiCertifyContract
    from aicertify.api import load_contract

    contract_data = json.loads(contract_file.read_text())
    # load_contract accepts a path; serialise the bundled JSON to a tmp file
    # via the API's existing path-based loader so we don't reimplement.
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        json.dump(contract_data, tmp)
        tmp_path = tmp.name

    try:
        contract = load_contract(tmp_path)
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    output_path = Path(output).resolve()
    output_dir = output_path.parent

    print(
        f"→ Running AICertify demo:\n"
        f"  contract: {contract.application_name} "
        f"({len(contract.interactions)} interactions)\n"
        f"  policy:   {policy}\n"
        f"  report:   {report_format}\n"
    )

    from aicertify.api import aicertify_app_for_policy

    # Pass the relative policy name (not the absolute path); the library's
    # find_matching_policy_folders() rejects absolute patterns.
    results = await aicertify_app_for_policy(
        contract=contract,
        policy_folder=policy,
        output_dir=str(output_dir),
        report_format=report_format,
        generate_report=True,
    )

    # The API writes a timestamped report; surface the path it produced.
    report_path = results.get("report_path")
    if report_path:
        print(f"\n✓ Report written to: {report_path}")
        print(
            f"\nOpen the report to see what an AICertify audit deliverable "
            f"looks like.\n"
        )
        return 0

    err = results.get("error")
    if err:
        print(f"\n✗ Demo failed: {err}", file=sys.stderr)
        return 2

    print(
        "\n⚠ Demo completed but no report path was returned. "
        "Check logs above for details.",
        file=sys.stderr,
    )
    return 3
