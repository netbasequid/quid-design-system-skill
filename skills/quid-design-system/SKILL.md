---
name: quid-design-system
description: >
  Apply the Quid (Terminal) design aesthetic to any HTML artifact before generation.
  Inlines a single stylesheet that exposes all Figma tokens (colors, typography, radius,
  shadows) as CSS custom properties wired to shadcn/ui semantics, plus a full-page shell
  container (side-nav rail with scroll-spy, hero, section primitives — the frame a
  multi-section brief is built on) and a catalog of brief components, each documented in
  its own file under components/ (KPI metric strip, tags, ranked-theme lists, chart
  palette, tables, accordions, featured posts, post-detail modal, insight callouts,
  example-post carousels, large creative cards, live social embeds, methodology). Use
  BEFORE creating an HTML brief, dashboard, report, or any other Quid-branded artifact
  so the output inherits correct fonts, colors, radius, and spacing. Triggers: "make
  this Quid-branded", "apply Quid styling", "use our design system", "Quid look and
  feel", "add a side nav", "on-this-page rail", "shell layout", "multi-section brief",
  "show example posts in the brief", "embed the posts", "creative in the wild",
  "showcase the top creatives", any HTML brief generation, push-brief.
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

Inline `quid.css` in `<head>` so the brief stays **one HTML file with no sibling asset files** — push-brief uploads a single file. External URLs are expected and fine: the Inter stylesheet below, post images (see the "Image policy: hotlink-only" section of `components/example-posts.md`), and platform embed scripts all load over the network. The requirement is one file to upload, not zero network requests.

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
- **Shell (page container)** — layout: `.with-sidenav` (toggle), `.body-layout`, `.container-brief`, `.main`, `.brief-body`; rail: `.sidenav`, `.sidenav-title`, `.sidenav a` / `:hover` / `.active`; hero: `.hero`, `.hero-card` (`.has-img`), `.eyebrow`, `.lede`; section primitives: `.section`, `.section-label`, `.section-sub`, `.divider`, `.section-divider`, `.prose`. Hero-gradient brand tokens `--hero-overlay` / `--hero-img` / `--grad-*`. The page container every multi-section brief starts from (see the dedicated section below).
- **Component classes** — each catalog component's classes are listed at the top of its `components/*.md` doc.

## The Shell (page container)

The Shell is the **page container** every multi-section brief starts from — not a widget you drop in. It is the frame; the catalog components (KPI strips, charts, `.sc-carousel`, `.large-cards`, `.embed-*`, tables, pull-quotes) are the content that composes **inside** its sections. Reach for it whenever a brief has enough parts to be worth a structure and an "on this page" rail.

The container is two fixed regions plus one slot:

1. **Side-nav rail** (`.sidenav`) — sticky "on this page" list, one link per section, with a scroll-spy that tracks the section in view. Author link labels in natural sentence case; the rail renders them Title Case via `text-transform: capitalize` (don't pre-capitalize or UPPERCASE them in markup).
2. **Hero** (`.hero` / `.hero-card`) — eyebrow + title + lede. Dark Quid gradient by default; add `has-img` + set `--hero-img` for a photo hero, or `.hero-card.light` for the pale primary-container hero.
3. **The slot** (`.brief-body`) — the flexible region: any number of `<section class="section" id="…">` blocks, each composing catalog components based on what the data needs. There is no fixed section layout. (If a brief wants a sources/caveats footer, add it here as an ordinary final `.section` — it is not part of the shell.)

It all ships in `quid.css`, so inlining `quid.css` is the only CSS setup; the rail also wants the small scroll-spy script below. Section primitives (`.section`, `.section-label`, `.section-sub`, `.divider`, `.section-divider`, `.prose`) come with the shell.

Container contract:

```html
<body class="with-sidenav">
  <div class="body-layout">

    <aside class="sidenav">                          <!-- rail: one <a> per section id -->
      <p class="sidenav-title">On this page</p>
      <nav>
        <a href="#section-1">{Section 1 eyebrow}</a>
        <a href="#section-2">{Section 2 eyebrow}</a>
      </nav>
    </aside>

    <main class="main">
      <header class="hero">                           <!-- hero -->
        <div class="container-brief">
          <div class="hero-card has-img" style="--hero-img: url('{image}');">
            <span class="eyebrow">{Client · Scope · Period}</span>
            <h1 class="quid-hero">{Title}</h1>
            <p class="lede">{One-sentence lede.}</p>
          </div>
        </div>
      </header>

      <div class="container-brief">
        <div class="brief-body">                       <!-- THE SLOT: compose components in here -->
          <section class="section" id="section-1">
            <p class="section-label">{Section 1 eyebrow}</p>
            <h2 class="quid-h2">{Heading}</h2>
            <!-- KPI cards / chart / .sc-carousel / table / prose … -->
          </section>
          <section class="section" id="section-2"> … </section>
        </div>
      </div>
    </main>

  </div>
</body>
```

Scroll-spy — highlights the section in view (put near `</body>`; a no-op when there's no rail):

```html
<script>
  (function () {
    const links = document.querySelectorAll('.sidenav a'); if (!links.length) return;
    const byId = new Map([...links].map(a => [a.getAttribute('href').slice(1), a]));
    const obs = new IntersectionObserver((es) => es.forEach((e) => {
      if (e.isIntersecting) { links.forEach(a => a.classList.remove('active')); const l = byId.get(e.target.id); if (l) l.classList.add('active'); }
    }), { rootMargin: '-20% 0px -70% 0px', threshold: 0 });
    document.querySelectorAll('.section[id], .section-divider[id]').forEach(s => obs.observe(s));
  })();
</script>
```

Rules the markup can't show:

- **The shell is the frame; components live in the slot.** Keep the four fixed regions as-is and compose everything data-specific into `.brief-body` sections — don't restructure the hero, rail, or footer per brief.
- **Each nav link's text is the target section's blue eyebrow (`.section-label`), verbatim** — the rail mirrors the section labels, not the `<h2>` headings, so the two always read the same.
- **Every rail `<a href="#id">` must match a real `id`** on a `.section` (or `.section-divider`) in the slot; each section already carries `scroll-margin-top` so the sticky offset doesn't hide its top on jump.
- **The rail is desktop-only by design.** `.sidenav` is `display:none` until `min-width:1024px`; below that the main column goes full-width and the rail drops out — no hamburger, nothing to wire. Intended, not a gap.
- **The rail is optional and removable in one move.** Drop `class="with-sidenav"` (and delete the `<aside>`) and the same page renders as a single full-width column — so add it only when there are enough sections to be worth navigating.
- **Hero:** the default `.hero-card` is the dark `--hero-gradient` (navy→teal, white text). Add `has-img` + set `--hero-img` inline for a photo (the shell multiplies the dark `--hero-overlay` over it); add `.hero-card.light` for the pale primary-container hero. All brand tokens, overridable per client — never hand-pick hero hex.
- **Smooth-scroll and the page canvas ship with the shell.** Side-nav anchor clicks smooth-scroll (`html { scroll-behavior: smooth }`), and the page sits on the soft `--shell-canvas` tint behind the white section cards. Both are automatic — nothing to wire.
- The active rail link uses `--primary-container-foreground` / `--primary-container-background` with a `--primary` left border; hover uses `--secondary`. All from tokens — no raw hex.

Full-page reference (hero + rail + real components composed into sections + working scroll-spy): **`shell-example.html`**. Open it over http — it is a complete brief, the honest picture of the shell as a page container, unlike the boxed component tiles in `example.html`.

## Component catalog

Every component is documented in its own file under `components/` — the markup contract and the rules the markup can't show live **there**, not here. Before building a section with a component, read its doc; read only the docs for components the brief actually uses. Each doc starts with the component's class list, and each component has a real-data reference section in `example.html`.

| Component | Use when | Doc |
|---|---|---|
| KPI strip | Headline metrics in tinted cards, colored by a fixed metric→color standard | `components/kpi-strip.md` |
| Tags / badges | Colored pill labels for a category or sentiment | `components/tags-badges.md` |
| Ranked themes | Ranked list of conversation themes — three interchangeable presentations (with quotes / with media / caption-insight) and how to choose | `components/ranked-themes.md` |
| Chart palette & convention | Series colors for any chart (categorical / sentiment / wordcloud) | `components/chart-palette.md` |
| Table | Metrics and comparisons in a real `<table>` | `components/table.md` |
| Accordion | Expandable stacked rows on native `<details>` | `components/accordion.md` |
| Featured posts | 2-up rich cards for a few standout posts | `components/featured-posts.md` |
| Post-detail modal | Shared drilldown singleton opened by post/quote cards | `components/post-detail-modal.md` |
| Insight / callout | Single-takeaway callout + 2-up insight grid | `components/insight-callout.md` |
| Example-post carousel | Many evidence posts to scan; includes the image-sourcing policy | `components/example-posts.md` |
| Large cards (creative in the wild) | A few hero posts worth a big visual | `components/large-cards.md` |
| Social embeds (native) | The living post itself — playable video, live counts | `components/social-embeds.md` |
| Methodology | Provenance / caveats footnote block | `components/methodology.md` |

## Theming

Light mode is the default. To activate dark mode, add `class="dark"` (or `data-theme="dark"`) to `<html>` or `<body>`. Every semantic token, including shadows, swaps to its dark counterpart.

## Files

```
~/.claude/skills/quid-design-system/
├── SKILL.md            ← this file: how to apply, the Shell, and the component catalog
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
├── components/         ← one doc per catalog component (read the ones the brief uses)
├── example.html        ← component reference: one boxed real-data demo per catalog component
└── shell-example.html  ← full-page reference: the Shell as a page container (hero + rail + sections)
```

## Updating after a Figma change

1. Replace the relevant file(s) in `tokens/` with the new Figma export.
2. From this directory, run `python3 build_tokens.py` to regenerate `quid.css`.
3. Spot-check `example.html` and `shell-example.html` in a browser before using the skill on a real brief.

## Authoring conventions

- Always reference semantic tokens (`var(--card)`, `var(--primary)`) in component code, not raw ramp colors. The ramps are for charts, illustrations, and one-off accents.
- Default body text is **14 / 20 Inter Regular**. Use `.quid-body` to be explicit, `.quid-body-lg` for hero copy.
- Default radius is **8px** (`--radius`, the shadcn alias) — use it for cards, buttons, inputs, and most surfaces. Reach for `--radius-sm` (6) only on dense controls/chips, and `--radius-lg` (12) on hero / floating panels where you specifically want the chunkier corner.
- Default elevation on cards is `--shadow-sm-recipe`; promote to `--shadow-rg-recipe` only for floating panels (popovers, dropdowns).

## Extending the system (maintainers)

- New color / type / shadow → edit `tokens/`, rerun `build_tokens.py`.
- New utility class or component CSS → a new block in `build_tokens.py`, then regenerate `quid.css` (never hand-edit it).
- New component → a new file in `components/`, **one catalog row** in this file, and a real-data demo in `example.html`. Never paste a full component spec into this file — it only points. Maintainers: follow the `add-gallery-component` runbook in the internal working repo.
