"""Demo runner used by ``aicertify demo``.

Loads the bundled sample contract, runs an OPA evaluation against a chosen
vendored policy folder, and writes a Markdown report to the user's CWD.

Designed to work after ``pip install aicertify`` with no extra configuration
beyond the OPA binary on PATH. Mirrors ``examples/quickstart.py`` exactly:
banner + spinners + MessageGroup + success markers via
``aicertify.utils.logging_config``.

The evaluation runs through the canonical ``application.create() +
app.evaluate()`` API. Heavy ML evaluators (DeepEval, LangFair) skip
gracefully if OPENAI_API_KEY is unset; the OPA verdict is the substance.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import platform
import shutil
import sys
import tempfile
from importlib.resources import files
from pathlib import Path
from typing import Optional

logger = logging.getLogger("aicertify.demo")


DEFAULT_POLICY = "eu_ai_act"
DEFAULT_REPORT_NAME = "aicertify_demo_report.md"

# Map friendly framework names to the bundled directory under aicertify/opa_policies/
# that we use as an existence probe (so the demo fails fast with a clear
# message if the wheel was stripped or the framework name is unknown).
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
    to the high-level ``application.evaluate()`` API, which resolves it.
    """
    probe = _BUNDLED_POLICY_PROBE_PATH.get(policy)
    if probe is None:
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
    # The OPA-binary check uses only stdlib (shutil.which) so it's safe to
    # run BEFORE the stderr redirect — failure messages stay visible.
    if opa_binary_path() is None:
        print_opa_install_instructions()
        return 1

    # Don't expose CUDA — matches examples/quickstart.py to keep behaviour
    # reproducible across machines with and without GPUs.
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

    # The downstream evaluators emit a lot of WARNING / ERROR log chatter —
    # much of it expected in the no-API-key demo path. Capture stderr to a
    # tempfile and only surface it on failure. Started BEFORE any
    # ``importlib.resources.files("aicertify…")`` or ``from aicertify`` call
    # — those trigger the aicertify package init which eagerly imports the
    # OPA policy_loader and emits "Skipping policy file…" warnings.
    logging.getLogger().setLevel(logging.WARNING)
    saved_stderr_fd = os.dup(2)
    captured_stderr = tempfile.NamedTemporaryFile(
        mode="w+b", prefix="aicertify-demo-stderr-", delete=False
    )
    os.dup2(captured_stderr.fileno(), 2)

    exit_code = 0
    try:
        # Remaining bundled-resource probes now run quietly (aicertify package
        # init lives in the captured-stderr window).
        contract_file = bundled_contract_path()
        if not contract_file.exists():
            print(
                f"✗ Bundled sample contract missing at {contract_file}. "
                f"This is a packaging bug — please file an issue.",
                file=sys.__stderr__,
            )
            exit_code = 1
            return exit_code

        policy_dir = bundled_policy_path(policy)
        if not policy_dir.exists():
            print(
                f"✗ Bundled policy directory '{policy}' not found at "
                f"{policy_dir}. Try one of: eu_ai_act, nist, global",
                file=sys.__stderr__,
            )
            exit_code = 1
            return exit_code

        # Deferred imports happen inside the capture so eager-import-time
        # warnings go to the tempfile, not the user's terminal.
        from aicertify import application, regulations
        from aicertify.utils.logging_config import (
            AIC_LOGO,
            MessageGroup,
            error,
            info,
            spinner,
            success,
            print_banner,
        )

        print_banner()
        info(
            "Self-contained demo: bundled sample contract → "
            f"{policy} policy set → {report_format} report.",
            category="EVALUATION",
        )

        # Step 1: regulations set
        with spinner("Creating regulations set", emoji="🔍"):
            regs_set = regulations.create("aicertify-demo")

        try:
            with spinner(f"Adding {policy} regulations", emoji="⚖️"):
                regs_set.add(policy)
            success(f"Loaded {policy} policy set")
        except ValueError as exc:
            error(f"Could not add regulation '{policy}': {exc}")
            exit_code = 2
            return exit_code

        # Step 2: application + interactions from the bundled fixture
        contract_data = json.loads(contract_file.read_text())
        model_info = contract_data.get("model_info", {})

        info(
            f"Building application from bundled fixture: " f"{contract_file.name}",
            category="APPLICATION",
        )
        with spinner(
            f"Creating application: {contract_data['application_name']}",
            emoji="🤖",
        ):
            app = application.create(
                name=contract_data["application_name"],
                model_name=model_info.get("model_name", "demo-model"),
                model_version=model_info.get("model_version", "v1"),
                model_metadata=model_info.get("metadata", {}),
            )
        success(f"Created application: {contract_data['application_name']}")

        interactions = contract_data.get("interactions", [])
        with spinner(f"Loading {len(interactions)} bundled interactions", emoji="💬"):
            for ix in interactions:
                app.add_interaction(
                    input_text=ix["input_text"],
                    output_text=ix["output_text"],
                )
        success(f"Added {len(interactions)} interactions to the application")

        # Step 3: evaluate
        output_path = Path(output).resolve()
        output_dir = output_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        info(
            f"\n{AIC_LOGO} Starting evaluation against {policy}",
            category="EVALUATION",
        )
        with MessageGroup("Evaluation progress") as eval_group:
            with spinner(
                f"Evaluating {contract_data['application_name']} against {policy}",
                emoji="🧪",
            ):
                eval_group.add("Initializing evaluators")
                eval_group.add("Loading policy files")
                eval_group.add("Running OPA policy evaluation")
                await app.evaluate(
                    regulations=regs_set,
                    report_format=report_format,
                    output_dir=str(output_dir),
                )
                eval_group.add(f"Writing {report_format} report")
        success("Evaluation complete")

        # Step 4: surface the produced report path
        reports = app.get_report()
        if not reports:
            error("Evaluation finished but no report path was returned.")
            exit_code = 3
            return exit_code

        for reg_name, report_path in reports.items():
            success(f"Report for {reg_name}: {report_path}")

        success("\n🎉 Demo complete 🎉")
        info(
            "Open the report above to see what an AICertify audit deliverable "
            "looks like — generated, not handwritten."
        )
        return 0
    except Exception:
        exit_code = 99
        raise
    finally:
        # Restore real stderr
        sys.stderr.flush()
        os.dup2(saved_stderr_fd, 2)
        os.close(saved_stderr_fd)
        captured_stderr.flush()
        captured_stderr.close()
        try:
            if exit_code != 0:
                # Demo failed — replay the captured chatter for debugging
                with open(captured_stderr.name, "rb") as f:
                    data = f.read()
                if data:
                    sys.stderr.write(
                        "\n--- captured downstream output (demo failed) ---\n"
                    )
                    sys.stderr.write(data.decode("utf-8", errors="replace"))
        finally:
            with contextlib.suppress(FileNotFoundError):
                Path(captured_stderr.name).unlink()
