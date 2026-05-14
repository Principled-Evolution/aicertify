"""Generate marketing diagrams for the AICertify README.

Run from repo root:  python diagrams/generate_diagrams.py
Outputs 5 PNGs (1600x900, ~retina-2x) into the diagrams/ directory.
"""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

# ---------- shared style ----------
PURPLE = "#7D4698"
PURPLE_DARK = "#5C2E76"
BLUE = "#1971c2"
GREEN = "#2f9e44"
ORANGE = "#e8590c"
TEXT = "#212529"
MUTED = "#495057"
LIGHT_BG = "#f1f3f5"
LIGHTER_BG = "#f8f9fa"
BORDER = "#dee2e6"
WHITE = "#ffffff"
RED = "#c92a2a"

# Figure size: 16x9 inches at 100 dpi -> 1600x900px (retina-friendly)
FIGSIZE = (16, 9)
DPI = 100

# Typography
TITLE_SIZE = 30
SUBTITLE_SIZE = 18
BODY_SIZE = 16
SMALL_SIZE = 13

HERE = Path(__file__).resolve().parent


# ---------- helpers ----------
def new_fig():
    """Create a clean 16:9 figure with white background."""
    fig, ax = plt.subplots(figsize=FIGSIZE, dpi=DPI)
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 56.25)  # keeps a 16:9 aspect in data coords
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    return fig, ax


def title(ax, text, y=52, color=TEXT, size=TITLE_SIZE, weight="bold"):
    ax.text(
        50,
        y,
        text,
        ha="center",
        va="center",
        fontsize=size,
        fontweight=weight,
        color=color,
    )


def subtitle(ax, text, y=47, color=MUTED, size=SUBTITLE_SIZE):
    ax.text(50, y, text, ha="center", va="center", fontsize=size, color=color)


def draw_box(
    ax,
    x,
    y,
    w,
    h,
    facecolor=WHITE,
    edgecolor=PURPLE,
    linewidth=2.2,
    rounding=0.4,
    shadow=False,
):
    """Draw a rounded rectangle centered on (x, y) with width w, height h."""
    if shadow:
        # offset shadow
        shadow_box = FancyBboxPatch(
            (x - w / 2 + 0.25, y - h / 2 - 0.35),
            w,
            h,
            boxstyle=f"round,pad=0.02,rounding_size={rounding}",
            linewidth=0,
            facecolor="#000000",
            alpha=0.08,
            zorder=1,
        )
        ax.add_patch(shadow_box)
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={rounding}",
        linewidth=linewidth,
        edgecolor=edgecolor,
        facecolor=facecolor,
        zorder=2,
    )
    ax.add_patch(box)
    return box


def labeled_box(
    ax,
    cx,
    cy,
    w,
    h,
    title_text,
    subtitle_text=None,
    facecolor=WHITE,
    edgecolor=PURPLE,
    title_color=None,
    subtitle_color=None,
    title_size=BODY_SIZE + 2,
    subtitle_size=SMALL_SIZE,
    shadow=True,
):
    draw_box(
        ax,
        cx,
        cy,
        w,
        h,
        facecolor=facecolor,
        edgecolor=edgecolor,
        shadow=shadow,
    )
    tc = (
        title_color
        if title_color
        else (WHITE if facecolor in (PURPLE, PURPLE_DARK) else TEXT)
    )
    sc = (
        subtitle_color
        if subtitle_color
        else (WHITE if facecolor in (PURPLE, PURPLE_DARK) else MUTED)
    )
    if subtitle_text:
        title_lines = title_text.count("\n") + 1
        sub_lines = subtitle_text.count("\n") + 1
        # vertical spacing roughly proportional to font size (1 unit ~ 14pt)
        title_line_h = title_size / 14.0
        sub_line_h = subtitle_size / 14.0
        gap = 0.8
        total_h = title_lines * title_line_h + gap + sub_lines * sub_line_h
        # top of text block
        top = cy + total_h / 2
        # title block center
        title_cy = top - (title_lines * title_line_h) / 2
        sub_cy = (
            title_cy
            - (title_lines * title_line_h) / 2
            - gap
            - (sub_lines * sub_line_h) / 2
        )
        ax.text(
            cx,
            title_cy,
            title_text,
            ha="center",
            va="center",
            fontsize=title_size,
            fontweight="bold",
            color=tc,
            zorder=3,
            linespacing=1.0,
        )
        ax.text(
            cx,
            sub_cy,
            subtitle_text,
            ha="center",
            va="center",
            fontsize=subtitle_size,
            color=sc,
            zorder=3,
            linespacing=1.1,
        )
    else:
        ax.text(
            cx,
            cy,
            title_text,
            ha="center",
            va="center",
            fontsize=title_size,
            fontweight="bold",
            color=tc,
            zorder=3,
        )


def draw_arrow(ax, x1, y1, x2, y2, color=PURPLE, lw=2.8, mutation_scale=28):
    arr = FancyArrowPatch(
        (x1, y1),
        (x2, y2),
        arrowstyle="-|>",
        mutation_scale=mutation_scale,
        linewidth=lw,
        color=color,
        zorder=2,
    )
    ax.add_patch(arr)


def save_fig(fig, name):
    out = HERE / name
    fig.savefig(out, dpi=DPI, bbox_inches="tight", facecolor=WHITE, pad_inches=0.25)
    plt.close(fig)
    size_kb = os.path.getsize(out) / 1024
    print(f"  wrote {name}  ({size_kb:.1f} KB)")


# ---------- diagram 1: hero flow ----------
def diagram1_hero_flow():
    fig, ax = new_fig()
    title(ax, "From AI app to audit-ready report")
    subtitle(
        ax,
        "One contract. One command. One report your auditor accepts.",
    )

    steps = [
        ("AI\nApplication", "model + interactions\n+ metadata", BLUE),
        ("AICertify\nContract", "captured\nas JSON", PURPLE),
        ("OPA Policy\nEvaluation", "EU AI Act, NIST\n+ 13 more", GREEN),
        ("Compliance\nReport", "PDF, Markdown,\nJSON, HTML", ORANGE),
    ]

    box_w = 19
    box_h = 18
    y = 26
    # 4 boxes spaced with clear gaps for arrows
    centers = [12, 37.33, 62.66, 88]

    for i, (cx, (t, s, color)) in enumerate(zip(centers, steps)):
        # numbered circle on top of each box
        circle = plt.Circle(
            (cx - box_w / 2 + 1.8, y + box_h / 2 - 1.2),
            1.3,
            color=color,
            zorder=4,
        )
        ax.add_patch(circle)
        ax.text(
            cx - box_w / 2 + 1.8,
            y + box_h / 2 - 1.2,
            str(i + 1),
            ha="center",
            va="center",
            color=WHITE,
            fontsize=14,
            fontweight="bold",
            zorder=5,
        )
        labeled_box(
            ax,
            cx,
            y,
            box_w,
            box_h,
            t,
            s,
            facecolor=WHITE,
            edgecolor=color,
            title_size=18,
            subtitle_size=13,
            shadow=True,
        )

    # arrows
    for i in range(3):
        x_from = centers[i] + box_w / 2 + 0.2
        x_to = centers[i + 1] - box_w / 2 - 0.2
        draw_arrow(ax, x_from, y, x_to, y, color=MUTED, lw=2.5, mutation_scale=24)

    # footer tag
    ax.text(
        50,
        7,
        "Open source - Apache 2.0   |   Built on Open Policy Agent   |   94 Rego policies",
        ha="center",
        va="center",
        fontsize=14,
        color=MUTED,
    )

    save_fig(fig, "diagram1_hero_flow.png")


# ---------- diagram 2: architecture ----------
def diagram2_architecture():
    fig, ax = new_fig()
    title(ax, "How AICertify works", y=53)
    subtitle(
        ax,
        "Pluggable evaluators feed OPA. OPA produces the report.",
        y=48.5,
    )

    # LEFT: your AI app
    labeled_box(
        ax,
        10,
        24,
        14,
        11,
        "Your AI App",
        "any LLM, agent,\nor pipeline",
        facecolor=BLUE,
        edgecolor=BLUE,
        title_color=WHITE,
        subtitle_color=WHITE,
        title_size=16,
        subtitle_size=11,
        shadow=True,
    )

    # CENTER stack
    cx = 50
    box_w = 44
    box_h = 7.2
    rows = [
        (
            38.5,
            "Contract",
            "model_name  |  version  |  interactions  |  metadata",
            PURPLE,
        ),
        (
            29,
            "Evaluators",
            "Fairness  |  ContentSafety  |  RiskManagement  |  Compliance",
            PURPLE,
        ),
        (
            19.5,
            "OPA Engine + Rego Policies",
            "94 policies sourced from the gopal library",
            PURPLE_DARK,
        ),
        (
            10,
            "Report Generator",
            "ReportLab PDF  |  Markdown  |  JSON  |  HTML",
            PURPLE,
        ),
    ]

    for y, t, s, color in rows:
        labeled_box(
            ax,
            cx,
            y,
            box_w,
            box_h,
            t,
            s,
            facecolor=color,
            edgecolor=color,
            title_color=WHITE,
            subtitle_color="#e9d5f0",
            title_size=17,
            subtitle_size=12,
            shadow=True,
        )

    # arrows down the stack
    for i in range(len(rows) - 1):
        y_from = rows[i][0] - box_h / 2 - 0.05
        y_to = rows[i + 1][0] + box_h / 2 + 0.05
        draw_arrow(ax, cx, y_from, cx, y_to, color=MUTED, lw=2.4, mutation_scale=22)

    # arrow from left box into center stack (top)
    draw_arrow(ax, 10 + 14 / 2 + 0.2, 24, cx - box_w / 2 - 0.2, rows[0][0], color=MUTED)

    # RIGHT: audit deliverable
    labeled_box(
        ax,
        90,
        24,
        14,
        11,
        "Audit\nDeliverable",
        "dated, signed,\nreproducible",
        facecolor=ORANGE,
        edgecolor=ORANGE,
        title_color=WHITE,
        subtitle_color=WHITE,
        title_size=16,
        subtitle_size=11,
        shadow=True,
    )
    # arrow from bottom of stack out to the right box
    draw_arrow(
        ax,
        cx + box_w / 2 + 0.2,
        rows[-1][0],
        90 - 14 / 2 - 0.2,
        24,
        color=MUTED,
    )

    save_fig(fig, "diagram2_architecture.png")


# ---------- diagram 3: regulatory coverage ----------
def diagram3_regulatory_coverage():
    fig, ax = new_fig()
    title(ax, "Regulatory coverage - 15+ frameworks", y=53)
    ax.text(
        50,
        47.5,
        "94 policies   |   15+ frameworks   |   5 industries",
        ha="center",
        va="center",
        fontsize=22,
        fontweight="bold",
        color=PURPLE,
    )

    # row category labels
    row_labels = [
        "International",
        "Aviation Safety",
        "Industry",
        "Cross-cutting",
    ]

    cells = [
        # row 1: International
        [
            ("EU AI Act", "29"),
            ("NIST AI RMF", "5"),
            ("India DPDP", "1"),
            ("Brazil AI Bill", "1"),
        ],
        # row 2: Aviation Safety
        [
            ("RTCA DO-365/366", "2"),
            ("FAA Part 107", "2"),
            ("EASA SORA", "2"),
            ("ICAO Doc 10019", "1"),
        ],
        # row 3: Industry
        [
            ("Healthcare", "2"),
            ("Banking & FS", "2"),
            ("Automotive", "1"),
            ("Education", "12"),
        ],
        # row 4: Cross-cutting
        [
            ("Global", "9"),
            ("Aviation Vertical", "17"),
            ("AIOps", "1"),
            ("Corporate", "2"),
        ],
    ]

    # grid layout area: rows centered at y values, columns centered at x values
    col_x = [22, 41, 60, 79]
    row_y = [37, 28, 19, 10]
    cell_w = 16.5
    cell_h = 7.4

    # row labels on the far left
    for ry, label in zip(row_y, row_labels):
        ax.text(
            6.5,
            ry,
            label,
            ha="center",
            va="center",
            fontsize=13,
            fontweight="bold",
            color=MUTED,
            rotation=0,
        )

    for r_i, row in enumerate(cells):
        for c_i, (name, count) in enumerate(row):
            cx = col_x[c_i]
            cy = row_y[r_i]
            draw_box(
                ax,
                cx,
                cy,
                cell_w,
                cell_h,
                facecolor=PURPLE,
                edgecolor=PURPLE_DARK,
                linewidth=1.5,
                rounding=0.3,
                shadow=True,
            )
            # framework name
            ax.text(
                cx,
                cy + 1.1,
                name,
                ha="center",
                va="center",
                fontsize=14,
                fontweight="bold",
                color=WHITE,
                zorder=3,
            )
            # policy count pill
            ax.text(
                cx,
                cy - 1.5,
                f"{count} {'policy' if count == '1' else 'policies'}",
                ha="center",
                va="center",
                fontsize=12,
                color="#e9d5f0",
                zorder=3,
            )

    save_fig(fig, "diagram3_regulatory_coverage.png")


# ---------- diagram 4: comparison ----------
def diagram4_comparison():
    fig, ax = new_fig()
    title(ax, "AICertify vs alternatives", y=53.5)
    subtitle(
        ax,
        "The only open-source, policy-as-code option with named regulatory coverage.",
        y=48.8,
    )

    columns = [
        "Feature",
        "AICertify",
        "Fairlearn",
        "AI Fairness 360",
        "MS RAI Toolbox",
        "Credo AI",
    ]
    rows = [
        (
            "Open source (Apache 2.0)",
            ["YES", "YES (MIT)", "YES (MIT)", "YES (MIT)", "NO"],
        ),
        ("On-prem capable", ["YES", "YES", "YES", "YES", "NO"]),
        ("Policy-as-code (OPA / Rego)", ["YES", "NO", "NO", "NO", "NO"]),
        ("Named regulatory frameworks (15+)", ["YES", "NO", "NO", "NO", "PARTIAL"]),
        ("Industry verticals out of box", ["YES", "NO", "NO", "NO", "PARTIAL"]),
        ("Audit-ready report output", ["YES", "NO", "NO", "PARTIAL", "YES"]),
        ("Custom policies via `.rego`", ["YES", "NO", "NO", "NO", "PAID"]),
    ]

    # Layout: columns
    col_x = [18, 39, 52, 65, 78, 91]
    col_w = [26, 11, 13, 13, 13, 11]
    header_y = 42
    row_h = 4.2
    first_row_y = 38

    # column header strip
    for cx, cw, name in zip(col_x, col_w, columns):
        is_aic = name == "AICertify"
        ax.add_patch(
            Rectangle(
                (cx - cw / 2, header_y - row_h / 2),
                cw,
                row_h,
                facecolor=PURPLE if is_aic else "#343a40",
                edgecolor="none",
                zorder=2,
            )
        )
        ax.text(
            cx,
            header_y,
            name,
            ha="center",
            va="center",
            fontsize=14 if is_aic else 12,
            fontweight="bold",
            color=WHITE,
            zorder=3,
        )

    # highlight strip for AICertify column behind rows
    aic_x = col_x[1]
    aic_w = col_w[1]
    rows_total_h = row_h * len(rows)
    ax.add_patch(
        Rectangle(
            (aic_x - aic_w / 2, first_row_y - row_h * (len(rows) - 1) - row_h / 2),
            aic_w,
            rows_total_h,
            facecolor="#f3e8f7",
            edgecolor="none",
            zorder=1,
        )
    )

    def cell_marker(value):
        if value == "YES":
            return ("Yes", GREEN, "bold")
        if value == "NO":
            return ("No", RED, "bold")
        if value == "PARTIAL":
            return ("Partial", ORANGE, "bold")
        if value == "PAID":
            return ("Paid", ORANGE, "bold")
        if value.startswith("YES "):
            return (value.replace("YES ", "Yes "), GREEN, "bold")
        return (value, TEXT, "normal")

    for r_i, (feature, vals) in enumerate(rows):
        y = first_row_y - r_i * row_h
        # alternating row band
        if r_i % 2 == 0:
            ax.add_patch(
                Rectangle(
                    (col_x[0] - col_w[0] / 2, y - row_h / 2),
                    sum(col_w)
                    + (col_x[-1] + col_w[-1] / 2 - (col_x[0] - col_w[0] / 2))
                    - sum(col_w),
                    row_h,
                    facecolor=LIGHTER_BG,
                    edgecolor="none",
                    zorder=0,
                )
            )
        # feature label (left col)
        ax.text(
            col_x[0] - col_w[0] / 2 + 1,
            y,
            feature,
            ha="left",
            va="center",
            fontsize=13,
            color=TEXT,
            zorder=3,
        )
        # value cells
        for c_i, v in enumerate(vals):
            label, color, weight = cell_marker(v)
            ax.text(
                col_x[c_i + 1],
                y,
                label,
                ha="center",
                va="center",
                fontsize=13,
                color=color,
                fontweight=weight,
                zorder=3,
            )

    # bottom border
    ax.plot(
        [col_x[0] - col_w[0] / 2, col_x[-1] + col_w[-1] / 2],
        [
            first_row_y - len(rows) * row_h + row_h / 2,
            first_row_y - len(rows) * row_h + row_h / 2,
        ],
        color=BORDER,
        lw=1.5,
        zorder=2,
    )

    # footer
    ax.text(
        50,
        4,
        "Source: public docs and source repos as of 2025.  AICertify is community-maintained.",
        ha="center",
        va="center",
        fontsize=11,
        color=MUTED,
        style="italic",
    )

    save_fig(fig, "diagram4_comparison.png")


# ---------- diagram 5: report anatomy ----------
def diagram5_report_anatomy():
    fig, ax = new_fig()
    title(ax, "Anatomy of an audit-ready report", y=53.5)
    subtitle(
        ax,
        "What the generated PDF actually contains.",
        y=48.8,
    )

    # The "document" page
    page_x, page_y = 50, 23.5
    page_w, page_h = 70, 41

    # shadow
    shadow_rect = Rectangle(
        (page_x - page_w / 2 + 0.5, page_y - page_h / 2 - 0.6),
        page_w,
        page_h,
        facecolor="#000000",
        alpha=0.10,
        edgecolor="none",
        zorder=1,
    )
    ax.add_patch(shadow_rect)
    # page background
    ax.add_patch(
        Rectangle(
            (page_x - page_w / 2, page_y - page_h / 2),
            page_w,
            page_h,
            facecolor=WHITE,
            edgecolor=BORDER,
            linewidth=1.5,
            zorder=2,
        )
    )

    left = page_x - page_w / 2 + 2.5
    right = page_x + page_w / 2 - 2.5
    top = page_y + page_h / 2

    # Header band
    ax.add_patch(
        Rectangle(
            (page_x - page_w / 2, top - 5.5),
            page_w,
            5.5,
            facecolor=PURPLE,
            edgecolor="none",
            zorder=3,
        )
    )
    ax.text(
        left,
        top - 2.0,
        "EU AI Act Compliance Report",
        ha="left",
        va="center",
        fontsize=17,
        fontweight="bold",
        color=WHITE,
        zorder=4,
    )
    ax.text(
        left,
        top - 4.0,
        "customer-support-bot   |   gpt-4o   |   2026-05-14",
        ha="left",
        va="center",
        fontsize=12,
        color="#e9d5f0",
        zorder=4,
    )
    # PASS stamp on header
    ax.add_patch(
        FancyBboxPatch(
            (right - 9, top - 4.6),
            8,
            3.4,
            boxstyle="round,pad=0.02,rounding_size=0.4",
            facecolor=GREEN,
            edgecolor=GREEN,
            zorder=4,
        )
    )
    ax.text(
        right - 5,
        top - 2.9,
        "PASS",
        ha="center",
        va="center",
        fontsize=15,
        fontweight="bold",
        color=WHITE,
        zorder=5,
    )

    # Section 1: Executive Summary
    sec_y = top - 8.5
    ax.text(
        left,
        sec_y,
        "1.  Executive Summary",
        ha="left",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=PURPLE,
        zorder=4,
    )
    for i, line in enumerate(
        [
            "27 of 29 EU AI Act policies passed.  2 advisory findings.",
            "Risk classification: limited risk (Article 52 transparency).",
        ]
    ):
        ax.text(
            left,
            sec_y - 2 - i * 1.7,
            line,
            ha="left",
            va="center",
            fontsize=11.5,
            color=TEXT,
            zorder=4,
        )

    # Section 2: Policy Results table
    sec_y2 = sec_y - 7.5
    ax.text(
        left,
        sec_y2,
        "2.  Policy Results",
        ha="left",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=PURPLE,
        zorder=4,
    )

    tbl_top = sec_y2 - 2
    # header row
    ax.add_patch(
        Rectangle(
            (left, tbl_top - 1.4),
            right - left - 22,
            1.4,
            facecolor=LIGHT_BG,
            edgecolor=BORDER,
            zorder=3,
        )
    )
    headers = ["Policy", "Status", "Evidence"]
    hxs = [left + 0.5, left + 22, left + 30]
    for hx, h in zip(hxs, headers):
        ax.text(
            hx,
            tbl_top - 0.7,
            h,
            ha="left",
            va="center",
            fontsize=11,
            fontweight="bold",
            color=MUTED,
            zorder=4,
        )

    rows = [
        ("Art. 5  Prohibited practices", "Pass", "0/127 interactions flagged"),
        ("Art. 10 Data governance", "Pass", "training set documented"),
        ("Art. 13 Transparency", "Pass", "user notice present"),
        ("Art. 14 Human oversight", "Advisory", "review queue partial"),
    ]
    for i, (p, status, ev) in enumerate(rows):
        y = tbl_top - 1.4 - 1.4 - i * 1.5
        color = GREEN if status == "Pass" else ORANGE
        ax.text(
            left + 0.5,
            y,
            p,
            ha="left",
            va="center",
            fontsize=10.5,
            color=TEXT,
            zorder=4,
        )
        ax.text(
            left + 22,
            y,
            status,
            ha="left",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color=color,
            zorder=4,
        )
        ax.text(
            left + 30,
            y,
            ev,
            ha="left",
            va="center",
            fontsize=10.5,
            color=MUTED,
            zorder=4,
        )

    # Section 3: Risk Assessment with mini bar chart
    sec_y3 = sec_y2 - 12.5
    ax.text(
        left,
        sec_y3,
        "3.  Risk Assessment",
        ha="left",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=PURPLE,
        zorder=4,
    )
    bar_labels = ["Fair", "Safe", "Priv", "Robust"]
    bar_vals = [0.92, 0.88, 0.95, 0.71]
    bar_colors = [GREEN, GREEN, GREEN, ORANGE]
    bx_start = left + 0.5
    bar_w = 3.6
    gap = 1.6
    base_y = sec_y3 - 6.2
    max_h = 4.5
    for i, (lbl, v, c) in enumerate(zip(bar_labels, bar_vals, bar_colors)):
        bx = bx_start + i * (bar_w + gap)
        ax.add_patch(
            Rectangle(
                (bx, base_y),
                bar_w,
                v * max_h,
                facecolor=c,
                edgecolor="none",
                zorder=4,
            )
        )
        ax.text(
            bx + bar_w / 2,
            base_y - 0.7,
            lbl,
            ha="center",
            va="top",
            fontsize=10,
            color=MUTED,
            zorder=4,
        )
        ax.text(
            bx + bar_w / 2,
            base_y + v * max_h + 0.3,
            f"{int(v * 100)}",
            ha="center",
            va="bottom",
            fontsize=9.5,
            color=TEXT,
            zorder=4,
        )

    # Section 4: Remediation Guidance (right side, next to chart)
    ax.text(
        left + 24,
        sec_y3,
        "4.  Remediation Guidance",
        ha="left",
        va="center",
        fontsize=14,
        fontweight="bold",
        color=PURPLE,
        zorder=4,
    )
    for i, line in enumerate(
        [
            "- Expand human-in-loop for low-confidence replies",
            "- Add adversarial test set for robustness",
            "- Document data-source provenance",
        ]
    ):
        ax.text(
            left + 24,
            sec_y3 - 2 - i * 1.6,
            line,
            ha="left",
            va="center",
            fontsize=11,
            color=TEXT,
            zorder=4,
        )

    # Footer band
    foot_y = page_y - page_h / 2
    ax.add_patch(
        Rectangle(
            (page_x - page_w / 2, foot_y),
            page_w,
            2.0,
            facecolor=LIGHTER_BG,
            edgecolor="none",
            zorder=3,
        )
    )
    ax.text(
        page_x,
        foot_y + 1.0,
        "Generated by AICertify v0.7.0   |   Apache 2.0   |   reproducible from contract.json",
        ha="center",
        va="center",
        fontsize=10.5,
        color=MUTED,
        zorder=4,
    )

    save_fig(fig, "diagram5_report_anatomy.png")


# ---------- entrypoint ----------
def main():
    print(f"Generating diagrams into {HERE}")
    diagram1_hero_flow()
    diagram2_architecture()
    diagram3_regulatory_coverage()
    diagram4_comparison()
    diagram5_report_anatomy()
    print("done.")


if __name__ == "__main__":
    main()
