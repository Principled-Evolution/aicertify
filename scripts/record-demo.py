#!/usr/bin/env python3
"""Compose the AICertify demo asciicast: real output, typed at a human pace.

Every command here is actually run and its output captured, so nothing on the
screen is written by hand. What is synthesised is the *timing*. The four
commands take about three minutes between them, most of it downloading model
weights and waiting on OPA, and a cast at real speed is unwatchable. A `script`
capture would also have no typing in it at all, and output that materialises
instantly reads as a screenshot rather than a session.

Being explicit about which half is real matters. The scores, the field counts,
the verdicts and the report are what the commands printed. The rhythm is
invented, the way any screencast's rhythm is invented by the person recording.

Four acts, because AICertify does a different job from GOPAL and needs the
room. GOPAL decides things, so its demo is one beat: swap the model, the build
fails. AICertify gathers things, and the interesting thing about it is how
honest it is about the part it cannot gather.

    1. score-card   a real Hugging Face card, scored, in one screen
    2. explain      150 fields you must declare, 14 an evaluator computes
    3. init/eval    scaffold a contract, run it, get 0 of 29
    4. gap report   22 of 27 metrics supplied, and the five that are not

Act 3 ends on nothing passing. That is the point rather than an embarrassment:
the scaffold asserts none of the 150 declarations, so none of the obligations
that turn on them can be met. It is the same argument act 2 makes, arriving as
a verdict instead of a number.

Usage:
    record-demo.py <full.cast> [short.cast]

The short cast is acts 1 and 2 only, for the README, where a 90-second loop is
too long and JavaScript does not run.
"""

from __future__ import annotations

import json
import random
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PY = str(REPO / ".venv" / "bin" / "python")
CLI = [PY, "-m", "aicertify.cli"]

# Deterministic jitter. The keystrokes look uneven, and they are the same
# uneven every time, so regenerating does not churn the file in review.
RNG = random.Random(20260830)

CPS_MIN, CPS_MAX = 0.038, 0.092  # seconds per keystroke
REACH_FOR_ENTER = 0.42  # hand leaves the letters, finds the return key
ENTER_SETTLES = 0.16  # and the press registers before anything happens
FIRST_BYTE = 0.30  # a command does not answer instantly
THINKING = 1.9  # a command that clearly did some work
READ_SHORT = 2.6
READ_LONG = 5.4  # long enough to read a verdict and understand it
BLINK = 0.53
BLINKS = 6
CURSOR = "█"

SWEEP = 0.028  # per character, the pace of a pen moving
HL_ON = "\x1b[43;30m"
HL_OFF = "\x1b[0m"
SAVE, RESTORE = "\x1b7", "\x1b8"

TYPO_CHANCE = 0.55  # per command, not per character
NOTICE_TYPO = (0.22, 0.46)
AFTER_FIX = (0.08, 0.19)

NEIGHBOURS = {
    "a": "sq",
    "b": "vn",
    "c": "xv",
    "d": "sf",
    "e": "wr",
    "f": "dg",
    "g": "fh",
    "h": "gj",
    "i": "uo",
    "j": "hk",
    "k": "jl",
    "l": "k",
    "m": "n",
    "n": "bm",
    "o": "ip",
    "p": "o",
    "q": "wa",
    "r": "et",
    "s": "ad",
    "t": "ry",
    "u": "yi",
    "v": "cb",
    "w": "qe",
    "x": "zc",
    "y": "tu",
    "z": "x",
    ".": "/",
    "/": ".",
    "-": "0",
    "_": "-",
}

WIDTH, HEIGHT = 100, 30


class Cast:
    def __init__(self) -> None:
        self.t = 0.0
        self.events: list[list] = []

    def wait(self, seconds: float) -> None:
        self.t += seconds

    def out(self, text: str) -> None:
        self.events.append([round(self.t, 4), "o", text])

    def type(self, text: str, typo_at: int | None = None) -> None:
        """One keystroke at a time, with the pauses and the mistakes.

        A typo is the neighbouring key, noticed a moment later, backspaced and
        retyped. It is the single thing that separates a recording of somebody
        working from text replayed at a plausible speed.
        """
        for i, ch in enumerate(text):
            if i == typo_at:
                wrong = NEIGHBOURS.get(ch.lower())
                if wrong:
                    self.wait(RNG.uniform(CPS_MIN, CPS_MAX))
                    self.out(RNG.choice(wrong))
                    self.wait(RNG.uniform(*NOTICE_TYPO))
                    self.out("\b \b")
                    self.wait(RNG.uniform(*AFTER_FIX))
            self.wait(RNG.uniform(CPS_MIN, CPS_MAX))
            if ch == " " and RNG.random() < 0.35:
                self.wait(RNG.uniform(0.05, 0.16))
            self.out(ch)

    def command(self, text: str) -> None:
        self.out("$ ")
        typo_at = None
        if len(text) > 14 and RNG.random() < TYPO_CHANCE:
            typo_at = RNG.randrange(6, len(text) - 2)
        self.type(text, typo_at)
        # Pressing return is two beats: reaching for the key, and the press
        # landing. Without them a command line ends and output begins in the
        # same instant, which nothing on a real keyboard does.
        self.wait(REACH_FOR_ENTER)
        self.out("\r\n")
        self.wait(ENTER_SETTLES)

    def block(self, text: str, first_byte: float = FIRST_BYTE) -> None:
        """Output arriving in a few pieces, as a real command does."""
        self.wait(first_byte)
        lines = text.rstrip("\n").split("\n")
        for i in range(0, len(lines), 3):
            self.out("\r\n".join(lines[i : i + 3]) + "\r\n")
            self.wait(0.09)

    def blink(self, times: int = BLINKS) -> None:
        self.out("$ ")
        for _ in range(times):
            self.out(CURSOR)
            self.wait(BLINK)
            self.out("\b \b")
            self.wait(BLINK)

    def highlight(self, rows_up: int, col: int, text: str) -> None:
        """Draw a highlighter left to right over text already on screen."""
        # CSI 0 C moves the cursor forward one column, not zero: ANSI reads a
        # zero parameter as one. Emitting it for a phrase at column 0 draws the
        # highlight one place right and leaves the original first letter behind.
        forward = f"\x1b[{col}C" if col > 0 else ""
        for i in range(1, len(text) + 1):
            self.out(
                f"{SAVE}\x1b[{rows_up}A\r{forward}"
                f"{HL_ON}{text[:i]}{HL_OFF}{RESTORE}"
            )
            self.wait(SWEEP)

    def sweep(self, block: str, pairs: list[tuple[str, str]]) -> None:
        """Highlight each phrase in a block of output just written.

        The cursor is moved up by *screen rows*, not by lines. A line longer
        than the terminal is wrapped by the emulator and occupies several rows,
        so counting lines puts the highlighter above where the text actually
        is. Two 130-character warnings at the end of one command were enough to
        draw `BELOW THRESHOLD` across an unrelated score three rows below it.
        """
        lines = block.rstrip("\n").split("\n")

        def rows(line: str) -> int:
            return max(1, math.ceil(len(line) / WIDTH))

        for needle, phrase in pairs:
            for idx, line in enumerate(lines):
                if needle in line and phrase in line:
                    up = sum(rows(rest) for rest in lines[idx:])
                    self.highlight(up, line.index(phrase), phrase)
                    self.wait(0.34)
                    break

    def write(self, dst: Path, title: str) -> None:
        header = {
            "version": 2,
            "width": WIDTH,
            "height": HEIGHT,
            "idle_time_limit": 3.0,
            "title": title,
        }
        with dst.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(header) + "\n")
            for event in self.events:
                fh.write(json.dumps(event) + "\n")
        print(f"Wrote {dst} ({len(self.events)} events, {self.t:.1f}s)")


def run(args: list[str], cwd: Path | None = None, stderr: bool = True) -> str:
    done = subprocess.run(
        args, cwd=cwd or REPO, capture_output=True, text=True, timeout=900
    )
    out = done.stdout or ""
    # stderr is dropped where it carries only environment noise, such as the
    # Hugging Face hub advising you to set a token. It is real, but it is not
    # the command answering the question, and it would leave the act ending on
    # a warning rather than on the verdict.
    return out + (done.stderr or "") if stderr else out


def shell(cmd: str, cwd: Path | None = None) -> str:
    done = subprocess.run(
        cmd, cwd=cwd or REPO, shell=True, capture_output=True, text=True, timeout=900
    )
    return (done.stdout or "") + (done.stderr or "")


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"refusing to record: {message}", file=sys.stderr)
        raise SystemExit(1)


def main() -> int:
    if len(sys.argv) not in (2, 3):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    full_dst = Path(sys.argv[1])
    short_dst = Path(sys.argv[2]) if len(sys.argv) == 3 else None

    work = Path(tempfile.mkdtemp(prefix="aicertify-demo-"))
    try:
        print("running the commands (this takes a few minutes)...", file=sys.stderr)

        card = run(CLI + ["score-card", "bert-base-uncased"], stderr=False)
        declare = shell(
            f"{PY} -m aicertify.cli explain eu_ai_act 2>/dev/null | head -12"
        )
        measure = shell(
            f"{PY} -m aicertify.cli explain eu_ai_act 2>/dev/null"
            ' | grep -A8 "produced by evaluators"'
        )

        contract = work / "contract.json"
        shell(
            f"{PY} -m aicertify.cli init-contract --policy eu_ai_act "
            f"2>/dev/null > {contract}"
        )
        require(
            contract.exists() and contract.stat().st_size > 1000,
            "init-contract produced no usable contract",
        )
        # A declarations-only contract. The scaffold ships one placeholder
        # interaction, and evaluating it pulls DeepEval into an LLM call that
        # needs a provider key. The point of this act is the policy verdict,
        # not the toxicity classifier, and act 4 covers the evaluators.
        doc = json.loads(contract.read_text())
        doc["interactions"] = []
        contract.write_text(json.dumps(doc, indent=2))

        evaluate = shell(
            f"{PY} -m aicertify.cli evaluate --contract contract.json "
            f"--policy eu_ai_act --report-format markdown --output-dir ./reports "
            "2>&1 | tail -5",
            cwd=work,
        )
        summary = shell("head -8 reports/*.md", cwd=work)
        gaps = shell(f"{PY} scripts/metric_gap_report.py 2>/dev/null | tail -12")

        # Guards. Each of these is a fact the cast puts on screen, so if the
        # tool stops saying it the recording is a lie and must not be written.
        require(
            "0.49" in card and "BELOW THRESHOLD" in card,
            "bert-base-uncased no longer scores 0.49 below the threshold",
        )
        require(
            "Fields you must declare (150)" in declare,
            "explain no longer reports 150 declared fields; it disagrees "
            "with the published figure and one of them is wrong",
        )
        require(
            "Fields produced by evaluators (14)" in measure,
            "explain no longer reports 14 measured fields",
        )
        require(
            "defeats the point" in measure,
            "the line explaining why you must not hand-write metrics is gone",
        )
        require(
            "Red Count:** 29" in summary and "Green Count:** 0" in summary,
            "an empty contract no longer fails all 29 policies, so act 3 "
            "has lost its point",
        )
        require(
            "22 of 27" in gaps,
            "the metric gap report no longer says 22 of 27; act 4's "
            "contribution hook needs the real number",
        )

        acts = build(card, declare, measure, evaluate, summary, gaps)
        acts.write(full_dst, "AICertify: what it measures, and what it cannot")

        if short_dst:
            short = build_short(card, declare, measure)
            short.write(short_dst, "AICertify: 150 declared, 14 measured")
        return 0
    finally:
        shutil.rmtree(work, ignore_errors=True)


def act_one(cast: Cast, card: str) -> None:
    """A famous model, scored, with no setup at all."""
    cast.wait(0.6)
    cast.command("aicertify score-card bert-base-uncased")
    cast.block(card, first_byte=THINKING)
    cast.wait(0.8)
    cast.sweep(
        card,
        [
            ("completeness", "0.49"),
            ("BELOW THRESHOLD", "BELOW THRESHOLD"),
        ],
    )
    cast.wait(READ_LONG)


def act_two(cast: Cast, declare: str, measure: str) -> None:
    """The split that the whole product turns on."""
    cast.command("# so what does the EU AI Act actually ask for?")
    cast.wait(0.5)
    cast.command("aicertify explain eu_ai_act | head -12")
    cast.block(declare, first_byte=THINKING)
    cast.wait(0.7)
    cast.sweep(declare, [("Fields you must declare", "150")])
    cast.wait(READ_SHORT)

    cast.command('aicertify explain eu_ai_act | grep -A8 "produced by evaluators"')
    cast.block(measure, first_byte=THINKING)
    cast.wait(0.7)
    cast.sweep(
        measure,
        [
            ("produced by evaluators", "14"),
            ("defeats the point", "defeats the point"),
        ],
    )
    cast.wait(READ_LONG)


def build_short(card: str, declare: str, measure: str) -> Cast:
    cast = Cast()
    act_one(cast, card)
    act_two(cast, declare, measure)
    cast.blink()
    return cast


def build(card, declare, measure, evaluate, summary, gaps) -> Cast:
    cast = Cast()
    act_one(cast, card)
    act_two(cast, declare, measure)

    # Act 3: scaffold, run, and find out you have answered nothing.
    cast.command("aicertify init-contract --policy eu_ai_act > contract.json")
    cast.wait(THINKING + 0.9)
    cast.command("aicertify evaluate --contract contract.json --policy eu_ai_act")
    cast.block(evaluate, first_byte=THINKING)
    cast.wait(0.8)

    cast.command("head -8 reports/*.md")
    cast.block(summary)
    cast.wait(0.7)
    cast.sweep(summary, [("Red Count", "29"), ("Green Count", "0")])
    cast.wait(READ_LONG)

    # Act 4: the tool enumerating its own gaps, which is a contributor's
    # to-do list rather than a caveat.
    cast.command("# which metrics can an evaluator supply today?")
    cast.wait(0.5)
    cast.command("python scripts/metric_gap_report.py | tail -12")
    cast.block(gaps, first_byte=THINKING)
    cast.wait(0.8)
    cast.sweep(gaps, [("TOTAL", "22 of 27")])
    cast.wait(READ_LONG)
    cast.blink()
    return cast


if __name__ == "__main__":
    raise SystemExit(main())
