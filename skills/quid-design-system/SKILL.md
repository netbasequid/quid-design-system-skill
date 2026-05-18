---
name: quid-design-system
description: >
  Apply the Quid (Terminal) design aesthetic to any HTML artifact before generation.
  Inlines a single stylesheet that exposes all Figma tokens (colors, typography, radius,
  shadows) as CSS custom properties wired to shadcn/ui semantics, plus a small set of
  Quid-branded utility classes. Use BEFORE creating an HTML brief, dashboard, report,
  or any other Quid-branded artifact so the output inherits correct fonts, colors,
  radius, and spacing. Triggers: "make this Quid-branded", "apply Quid styling",
  "use our design system", "Quid look and feel", any HTML brief generation, push-brief.
---

# Quid Design System

Use this skill **before** producing any HTML artifact that should look and feel like a Quid product (Terminal). It guarantees the output uses the right font, colors, radius, shadows, and shadcn/ui-aligned semantic tokens, in both light and dark mode.

## When to use

- Any HTML brief, dashboard, or report that will be uploaded via `push-brief`.
- Any standalone HTML deliverable for a Quid client or internal stakeholder.
- Any Tailwind / shadcn/ui project that should adopt the Terminal palette and type scale.

If you are not generating an HTML/CSS artifact, do not use this skill.

## How to apply

The skill is a single static stylesheet (`quid.css`) plus the source Figma tokens. There are two ways to wire it in.

### A. Standalone HTML brief (default)

Inline `quid.css` in `<head>` so the brief is self-contained — push-brief uploads need a single file.

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{Brief title}}</title>
    <link rel="preconnect" href="https://rsms.me/" />
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
    <style>
      /* paste the full contents of ~/.claude/skills/quid-design-system/quid.css */
    </style>
  </head>
  <body>
    <!-- content -->
  </body>
</html>
```

To inline at generation time, read the file directly:

```bash
cat ~/.claude/skills/quid-design-system/quid.css
```

### B. shadcn/ui project

Drop `quid.css` into the project's `globals.css` (or @import it). The semantic tokens (`--background`, `--foreground`, `--primary`, `--card`, etc.) match shadcn's component contract, so existing shadcn components (`<Button />`, `<Card />`, etc.) inherit Quid styling without code changes. The `--radius` alias (`8px`) feeds shadcn's `rounded-lg` math.

## What is in the stylesheet

- **Base color ramps** — `--color-red-100..1000`, plus orange / yellow / green / blue / purple / pink / gray, with `-a80` / `-a90` alpha variants on hot colors.
- **Semantic tokens** (shadcn-aligned) — `--background`, `--foreground`, `--muted`, `--muted-foreground`, `--card`, `--popover`, `--border`, `--input`, `--primary`, `--primary-foreground`, `--secondary`, `--accent`, `--destructive`, `--ring`, plus `--sidebar-*` for shell layouts and `--hover-*` / `--pressed-*` interaction states.
- **Radius** — `--radius-sm` (6), `--radius-rg` (8, default), `--radius-lg` (12), `--radius-full`, plus shadcn aliases `--radius` (8), `--radius-md`, `--radius-xs`.
- **Typography** — `--font-sans` (Inter), `--font-size-12 / 13 / 14 / 15 / 16 / h0..h3 / hero / subtitle / pull-quote / blob-caption / code-large`, matching `--font-line-height-*`, weights `--font-light / regular / medium / semibold / bold / headings / h0`. A `@media (max-width: 768px)` block automatically swaps in the mobile size scale.
- **Shadows** — `--shadow-sm`, `--shadow-rg`, `--shadow-lg`, `--shadow-sm-hover`, `--shadow-rg-hover` (raw rgba), and ready-to-use recipes `--shadow-sm-recipe`, `--shadow-rg-recipe`, `--shadow-lg-recipe`.
- **Utility classes** — `.quid-hero`, `.quid-h0`, `.quid-h1`, `.quid-h2`, `.quid-h3`, `.quid-subtitle`, `.quid-pull-quote`, `.quid-body`, `.quid-body-lg`, `.quid-caption`, `.quid-muted`, `.quid-card`, `.quid-button`, `.quid-badge`.

## Theming

Light mode is the default. To activate dark mode, add `class="dark"` (or `data-theme="dark"`) to `<html>` or `<body>`. Every semantic token, including shadows, swaps to its dark counterpart.

## Files

```
~/.claude/skills/quid-design-system/
├── SKILL.md            ← this file
├── quid.css            ← the compiled stylesheet (inline or @import this)
├── build_tokens.py     ← parser: tokens/*.json → quid.css
├── tokens/             ← source Figma DTCG exports (do not edit)
│   ├── base-colors.tokens.json
│   ├── primitives.tokens.json
│   ├── system-colors-light.tokens.json
│   ├── system-colors-dark.tokens.json
│   ├── shadow-colors-light.tokens.json
│   ├── shadow-colors-dark.tokens.json
│   ├── typography-desktop.tokens.json
│   └── typography-mobile.tokens.json
└── example.html        ← reference markup for type scale, cards, buttons, swatches
```

## Updating after a Figma change

1. Replace the relevant file(s) in `tokens/` with the new Figma export.
2. From this directory, run `python3 build_tokens.py` to regenerate `quid.css`.
3. Spot-check `example.html` in a browser before using the skill on a real brief.

## Authoring conventions

- Always reference semantic tokens (`var(--card)`, `var(--primary)`) in component code, not raw ramp colors. The ramps are for charts, illustrations, and one-off accents.
- Default body text is **14 / 20 Inter Regular**. Use `.quid-body` to be explicit, `.quid-body-lg` for hero copy.
- Default radius is **8px** (`--radius`, the shadcn alias) — use it for cards, buttons, inputs, and most surfaces. Reach for `--radius-sm` (6) only on dense controls/chips, and `--radius-lg` (12) on hero / floating panels where you specifically want the chunkier corner.
- Default elevation on cards is `--shadow-sm-recipe`; promote to `--shadow-rg-recipe` only for floating panels (popovers, dropdowns).
