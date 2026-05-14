# AICertify diagram style

A short, opinionated reference so future diagrams (yours, mine, or a contributor's) stay visually coherent with the existing set. If you can read [diagram1_hero_flow_light.svg](diagram1_hero_flow_light.svg) and the matching `_dark.svg`, you have already seen the whole system applied.

## The principle

Two colors with intent, flat fills, no animation, no shadows. The polish is in restraint and consistency, not effects.

## Palette

| Token | Light | Dark | Used for |
|---|---|---|---|
| **Indigo (primary)** | `#4f46e5` | `#6366f1` | Process, structure, the "happy path" |
| **Indigo (light fill)** | `#eef2ff` | `#312e81` | Card backgrounds for indigo elements |
| **Indigo (text on fill)** | `#4338ca` | `#c7d2fe` | Text inside indigo chips/badges |
| **Amber (accent)** | `#d97706` | `#fbbf24` | The **output** of the flow — audit report, deliverable, industry-specific framework |
| **Amber (light fill)** | `#fffbeb` / `#fef3c7` | `#2a1f06` / `#533404` | Card / chip backgrounds for amber elements |
| **Amber (text on fill)** | `#92400e` / `#b45309` | `#fcd34d` / `#fde68a` | Text inside amber chips |
| **Foreground (text)** | `#0f172a` | `#f0f6fc` | Primary body / heading text |
| **Foreground (muted)** | `#64748b` | `#8b949e` | Secondary captions, labels |
| **Border** | `#e2e8f0` | `#30363d` | Card outlines, dividers |
| **Card surface** | `#ffffff` | `#161b22` | Card backgrounds |
| **Arrow / line** | `#94a3b8` | `#6e7681` | Connectors |

**Amber is precious.** Reserve it for the deliverable in a flow and for industry-specific (vertical) frameworks. If everything is highlighted, nothing is highlighted.

## Typography

- Single stack, declared on every `<svg>`: `font-family="system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"`. No webfont hosting, no licensing, picks up the reader's OS font.
- **Headings inside cards**: 13–15px, `font-weight="500"`.
- **Body / captions**: 10–12px, `font-weight="400"`.
- **Stat numerals** (e.g. "94"): 36px, `font-weight="500"`, amber.
- Wordmark on the hero banner / OG card uses `letter-spacing="-0.025em"` for tightness at large sizes.

## Shape language

- **Cards / chips**: rounded rectangles. Corner radius `rx="10"` for cards, `rx="12"` (or larger) for chip pills.
- **Card stroke**: `1px` border in the border token, no shadows, no gradients.
- **Arrows**: `1.5px` line in the muted line color, with the marker defined per-file in `<defs>`. Don't reuse `id="al"` etc. across files in case both are inlined.
- **Icons inside cards**: `1.5px` stroke in the indigo (or dark variant) color, `stroke-linecap="round"`, `stroke-linejoin="round"`. Compact (~24×24 unit) line icons, no fills unless intentional.

## Light/dark pattern

Diagrams ship as **paired files** with matching `_light.svg` and `_dark.svg`. README markup uses `<picture>`:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="diagrams/<name>_dark.svg">
  <img src="diagrams/<name>_light.svg" alt="<descriptive alt text>" width="85%">
</picture>
```

That gives GitHub-light readers the light variant and GitHub-dark readers the dark variant — same on mobile, on PR previews, and anywhere else `<picture>` is honored.

- Light variants use white card surfaces, slate text.
- Dark variants use `#161b22` cards (GitHub's `--color-canvas-subtle`) and `#30363d` borders so cards sit into the page rather than floating on top of it.
- Don't bake in a background `<rect>` filling the viewBox unless the asset is meant to be self-contained (e.g. OG cards). Otherwise let GitHub's page color show through.

## Files and naming

```
diagrams/
├── STYLE.md                                    (this file)
├── hero_banner_{light,dark}.svg                top-of-README banner
├── logo_{light,dark}.svg                       standalone square mark
├── og_card_{light,dark}.svg                    1200×630 social-preview card
├── og_card.png                                 rasterized light variant (1200×630), for GitHub Settings → Social preview
├── diagram1_hero_flow_{light,dark}.svg         contract → OPA → report
├── diagram2_architecture_{light,dark}.svg      evaluator bus + OPA engine
├── diagram3_regulatory_coverage_{light,dark}.svg  stats + four category cards
└── diagram5_report_anatomy_{light,dark}.svg    report mockup with callouts
```

Diagram 4 (comparison) was deliberately removed — the markdown comparison table in the README is the single source of truth.

## Adding a new diagram

1. Sketch the content first in markdown (what does the reader need to understand?). Cut anything that is also said in nearby text.
2. Pick a layout that mirrors an existing diagram if you can — most additions are variations of "flow", "bus", or "stats + cards".
3. Hand-author the SVG. Use the existing files as templates; copy a card definition, swap the content.
4. Validate XML: `python3 -c "import xml.etree.ElementTree as ET; ET.parse('diagrams/<name>_light.svg')"`. Repeat for the dark variant.
5. Embed with the `<picture>` snippet above in every README that should reference it (en + 4 translated).
6. **No automation, no matplotlib, no Python generator.** The old `generate_diagrams.py` was retired because hand-authored SVGs are easier to read, edit, and review than rendered raster output. Keep them hand-authored.

## Rasterizing (only when needed)

The only raster output we keep in the repo is `og_card.png` — GitHub's Social Preview upload requires PNG/JPG. To regenerate:

```bash
inkscape --export-type=png --export-width=1200 --export-height=630 \
  --export-filename=diagrams/og_card.png diagrams/og_card_light.svg
```

GitHub social preview is uploaded manually at: **Settings → General → Social preview → Edit → Upload an image**. The repo's checked-in `og_card.png` is the source artifact.
