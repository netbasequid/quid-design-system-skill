---
name: quid-design-system
description: >
  Apply the Quid (Terminal) design aesthetic to any HTML artifact before generation.
  Inlines one to three stylesheets (tokens, the Quid Sans webfont, and optionally the modern shell) that expose all Figma tokens (colors, typography, radius,
  shadows) as CSS custom properties wired to shadcn/ui semantics, plus a full-page shell
  container (side-nav rail with scroll-spy, hero, section primitives — the frame a
  multi-section brief is built on) and a catalog of brief components, each documented in
  its own file under components/ (KPI metric strip, tags, ranked-theme lists, chart
  palette, tables, accordions, featured posts, post-detail modal, insight callouts,
  example-post carousels, large creative cards, live social embeds, the standard
  collapsed methodology disclosure). Use
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

The skill ships **three** stylesheets plus the source Figma tokens. Which ones you need depends on the layout; how you include them does not.

### Which stylesheets each layout needs

**There is one shell.** Black masthead, right-hand rail, boxless sections, Quid Sans headings. Copy `shell-modern-example.html`: the `<body class="with-sidenav brief-modern">` and all three stylesheets come with it, so there is nothing to choose and nothing to switch on.

| | required for every brief |
|---|---|
| `quid.css` — tokens and components | **yes** |
| `quid-fonts.css` — Quid Sans faces + heading binding | **yes** |
| `quid-modern-shell.css` — masthead, rail, boxless sections | **yes** |
| `<body>` class | `with-sidenav brief-modern` |
| reference markup | `shell-modern-example.html` |
| components in context | `example-modern.html` |

#### The older card-based shell

Briefs written before this shell use a card-based layout: `.body-layout` as the
flex row, `<aside class="sidenav">` on the left, `.section` as a white card. **That
CSS still ships in `quid.css`** — it has to, or every existing brief that links
the stylesheet would lose its layout overnight.

What is gone is the *path*: there is no longer a `shell-example.html` to copy,
and no reason to start a brief that way. Leave existing briefs alone; they work.
Everything the old reference file demonstrated — including the Methodology
disclosure and the example-post carousel — is in `example-modern.html`, in the
shell you should actually be using. The Methodology disclosure is also in
`shell-modern-example.html`, so the starter you copy closes correctly without
your having to remember to add it.

#### Why `brief-modern` is still a class rather than the default styling

Everything in `quid-modern-shell.css` is scoped to `.brief-modern`, which looks like an opt-in you have to remember. For a brief it is not: the class is already in the reference markup you copy.

The scope exists for the other consumers of this design system, where one stylesheet bundle can serve many pages. Without it, adding this file for one page restyles every other page that shares the bundle. Briefs do not hit that case because each brief is a single self-contained file, but the design system ships to surfaces that do.

So: start from `shell-modern-example.html` and you never think about the class. Do not remove the scope from the stylesheet to "simplify" it; that trades a copy-paste convenience for a silent restyle somewhere else.

Order matters: **`quid.css`, then `quid-fonts.css`, then `quid-modern-shell.css`.** The shell reads tokens defined in `quid.css`, and the font binding must be able to see `--font-display`.

`quid-fonts.css` is optional for the standard shell only in the sense that the shell works without it — headings simply stay in Inter. Include it whenever the brand typeface is wanted. It is **required** for the modern shell, which is designed around Quid Sans headings.

#### Adding a component that renders at a heading size

**Size and family are separate tokens.** `font-size: var(--font-size-h3)` buys the 22px scale and nothing else; it does not bring Quid Sans with it. The typeface comes from a binding rule at the bottom of `quid-fonts.css` that lists which selectors get `--font-display`.

So a new `<span class="whatever">` styled at a heading size renders *at heading scale in the body font*, sitting next to real headings in Quid Sans. It reads as an inconsistency rather than a choice, and nothing warns you — this is exactly how `.theme-name`, `.ci-name` and `.ci-num` shipped wrong.

Two ways to avoid it, in order of preference:

1. **Use a heading element.** `<h3 class="theme-name">` is already covered by the binding, needs no edit here, and is better for screen readers and document outline. Zero out the UA margin if the parent is a flex or grid container.
2. **Add the class to the binding list** in `quid-fonts.css`, if the element genuinely should not be a heading.

To find anything already drifting, render a page that uses the classes and walk the DOM, comparing each element's computed family against the body font:

```js
[...document.querySelectorAll('*')]
  .filter(e => parseFloat(getComputedStyle(e).fontSize) >= 22)
  .filter(e => !getComputedStyle(e).fontFamily.startsWith('QuidSans'))
  .map(e => e.tagName + '.' + e.className)
```

**Do not audit this with a grep.** A line-based scan reports only the selector that shares the `font-size` line, so on a multi-line selector group it names one selector and hides the others. That is exactly how `.quid-subtitle` and `.quid-pull-quote` shipped in the body font: they shared a rule with `.quid-h2`, which was already bound, and `.quid-subtitle` never appeared in the scan output at all. The same grouping also had them taking h2's **size**, so a scan looking only for a missing family would have caught half the bug at best.

The DOM walk only sees classes the page actually uses, so check that every utility class in the inventory above appears somewhere in `example.html` or `example-modern.html`. An unexercised class is one no reference render can catch.

Not everything flagged wants binding. `.accordion summary::before` and `.methodology summary::before` take a heading size but their content is a glyph (`▸`), and changing the family changes the shape of the arrow. They are deliberately left out.

### INLINE THEM. A delivered brief has no sibling files.

Every stylesheet above must be **pasted into a `<style>` block in the brief itself**. A delivered brief is a single HTML file: push-brief uploads one file, and readers open it from an inbox, a download folder, or Terminal — never from the directory it was authored in.

A `<link href="./quid-fonts.css">` works on the author's machine and nowhere else. The brief will look correct to the person who made it and wrong to everybody else, with nothing in the console a reader would notice. **This is the single most common way a delivered brief breaks.**

Inlining also carries the typeface: `quid-fonts.css` embeds Quid Sans as base64, so the font travels inside the file. No font host, no CORS header, nothing for a reader to install, and it still renders offline.

External **URLs** are fine and expected — the Inter stylesheet below, post images (see the "Image policy: hotlink-only" section of `components/example-posts.md`), and platform embed scripts all load over the network. The rule is *one file to upload*, not *zero network requests*. The difference is that a URL resolves from anywhere; a relative path does not.

### A. Standalone HTML brief (default)

Inline the stylesheets your layout needs, in the order given above, so the brief stays **one HTML file with no sibling asset files**.

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{{Brief title}}</title>
    <link rel="preconnect" href="https://rsms.me/" />
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />

    <!-- 1. tokens, components, standard layout -->
    <style>
      /* paste the full contents of quid.css */
    </style>

    <!-- 2. Quid Sans faces + heading binding. Carries the font as base64,
            so nothing is fetched and nothing is installed. -->
    <style>
      /* paste the full contents of quid-fonts.css */
    </style>

    <!-- 3. Modern shell: masthead, rail, boxless sections. -->
    <style>
      /* paste the full contents of quid-modern-shell.css */
    </style>
  </head>

  <body class="with-sidenav brief-modern">
    <!-- markup: see "Container contract" below -->
    <!-- scroll-spy script goes just before </body> -->
  </body>
</html>
```

Keeping an **existing** brief on the standard shell: drop block 3 and the
`brief-modern` class. Block 2 is then optional, and the headings fall back to
Inter. Do not start new work that way.

Read each file at generation time and paste its contents. From a synced Aesop
workspace:

```bash
cat skills/quid-design-system/quid.css
cat skills/quid-design-system/quid-fonts.css        # if using Quid Sans
cat skills/quid-design-system/quid-modern-shell.css # modern shell only
```

The path differs per workspace; what matters is that the **contents** end up in
the brief, not a reference to where they came from.

**Check before delivering.** The brief should contain no `<link>`, `<script>`,
`<img>` or `<iframe>` with a relative `href`/`src` — anything starting with
`./`, `../`, or a bare filename. Absolute `https://` URLs, `data:` URIs and
in-page `#` anchors are fine.

```bash
python3 skills/quid-design-system/check_delivery.py brief.html
```

It says `PASS` or `FAIL` in words and lists every offending line. Exit codes are
`0` pass, `1` findings, `2` the check itself could not run.

> **Do not substitute a `grep` for this.** The obvious one-liner,
> `grep -nE '(href|src)="(?!https?://|data:|#)'`, uses a negative lookahead.
> That is PCRE, not POSIX ERE: BSD grep on macOS rejects it, and so does ugrep,
> which is what `grep` resolves to on many macOS setups. `grep -P` is not a
> portable fallback either, since stock BSD grep has no `-P`.
>
> The failure mode is the dangerous kind. The broken command exits 2 and prints
> its complaint on **stderr**, while a genuinely clean brief exits 1 and prints
> nothing on **stdout**. An author who runs it, sees no filenames, and concludes
> "no relative references" gets exactly the same impression from a check that
> never ran — a false pass on the single most common way a delivered brief
> breaks.

### B. shadcn/ui project

Drop `quid.css` into the project's `globals.css` (or @import it). The semantic tokens (`--background`, `--foreground`, `--primary`, `--card`, etc.) match shadcn's component contract, so existing shadcn components (`<Button />`, `<Card />`, etc.) inherit Quid styling without code changes. The `--radius` alias (`8px`) feeds shadcn's `rounded-lg` math.

## What is in the stylesheet

- **Base color ramps** — `--color-red-100..1000`, plus orange / yellow / green / blue / purple / pink / gray, with `-a80` / `-a90` alpha variants on hot colors.
- **Semantic tokens** (shadcn-aligned) — `--background`, `--foreground`, `--muted`, `--muted-foreground`, `--card`, `--popover`, `--border`, `--input`, `--primary`, `--primary-foreground`, `--secondary`, `--accent`, `--destructive`, `--ring`, plus `--sidebar-*` for shell layouts and `--hover-*` / `--pressed-*` interaction states.
- **Radius** — `--radius-sm` (6), `--radius-rg` (8, default), `--radius-lg` (12), `--radius-full`, plus shadcn aliases `--radius` (8), `--radius-md` (6), `--radius-xs` (4).
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
3. **The slot** (`.brief-body`) — the flexible region: any number of `<section class="section" id="…">` blocks, each composing catalog components based on what the data needs. There is no fixed section layout, with one exception: a client brief always closes the slot with a single collapsed Methodology disclosure (`details.methodology`, see `components/methodology.md`). It sits after the last section, is not a `.section` card, and never gets a rail link.

The modern shell needs `quid.css`, `quid-fonts.css` and `quid-modern-shell.css`, in that order — see the table under "How to apply". The standard shell ships entirely in `quid.css`, so for an existing brief on it that one file is the only CSS setup. Either way the rail needs the scroll-spy script below; without it the rail renders and the first link stays highlighted forever, which reads as a styling bug rather than a missing script. Section primitives (`.section`, `.section-label`, `.section-sub`, `.divider`, `.section-divider`, `.prose`) come with the shell.

Container contract — this is the modern shell, matching `shell-modern-example.html`:

```html
<body class="with-sidenav brief-modern">
  <div class="body-layout">

    <header class="hero">                             <!-- masthead: full-bleed, above the row -->
      <div class="container-brief">
        <div class="hero-card has-img" style="--hero-img: url('{image}');">
          <div class="bb-text">                       <!-- carries the measure cap; don't omit -->
            <h1 class="quid-hero">{Title in Title Case}</h1>
            <p class="lede">{One-sentence lede.}</p>
            <dl class="hero-meta">                    <!-- labelled meta row, not stacked -->
              <div class="hm-item"><dt>Brand</dt><dd>{Brand}</dd></div>
              <div class="hm-item"><dt>Report Date</dt><dd>{Oct 27, 2026}</dd></div>
            </dl>
          </div>
        </div>
      </div>
    </header>

    <div class="page-row">                            <!-- rail + body are flex siblings HERE -->
      <nav class="sidenav" aria-label="On this page">  <!-- <nav>, not <aside> -->
        <p class="sidenav-title">On this page</p>
        <a href="#section-1" class="active">{Section 1 eyebrow}</a>
        <a href="#section-2">{Section 2 eyebrow}</a>
      </nav>

      <div class="main">
        <div class="container-brief">
          <div class="brief-body">                    <!-- THE SLOT: compose components in here -->
            <section class="section" id="section-1">
              <p class="section-label">{Section 1 eyebrow}</p>
              <h2 class="quid-h1">{Heading}</h2>
              <!-- KPI cards / chart / .sc-carousel / table / prose … -->
            </section>
            <section class="section" id="section-2"> … </section>
            <details class="methodology" data-methodology> … </details>  <!-- always last; collapsed; no rail link -->
          </div>
        </div>
      </div>
    </div>

  </div>
  <!-- scroll-spy script here, just before </body> -->
</body>
```

Four things differ from the standard shell's markup, and all four matter:

- **The masthead sits above `.page-row`, not inside `.main`.** Nested in `.main`
  it is the flex item beside the rail, so a full-bleed band drawn there starts
  240px in and runs under the rail.
- **`.page-row` is the flex row**, not `.body-layout`. The masthead has to stay
  in normal flow above it.
- **`<nav class="sidenav">`, not `<aside>`.** Terminal's PDF exporter strips
  `<nav>`, which is what you want: the rail is screen furniture and should not
  appear in an export.
- **`.bb-text` wraps the hero copy** and carries the measure cap. Omit it and
  the headline and lede run the full masthead width.

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
- **The rail is optional and removable in one move.** Drop `class="with-sidenav"` (and delete the `<nav class="sidenav">`) and the same page renders as a single full-width column — so add it only when there are enough sections to be worth navigating. The scroll-spy script is a no-op with no rail, so it is safe to leave in place.
- **Hero:** the default `.hero-card` is the dark `--hero-gradient` (navy→teal, white text). Add `has-img` + set `--hero-img` inline for a photo (the shell multiplies the dark `--hero-overlay` over it); add `.hero-card.light` for the pale primary-container hero. All brand tokens, overridable per client — never hand-pick hero hex.
- **Headings are Title Case** — capitalize principal words and leave articles, coordinating conjunctions, and prepositions of four letters or fewer lowercase, unless one falls first or last: "Momentum Builds Behind the 2026 Squad", "Where the Next Lift Could Come From". This governs the hero `<h1 class="quid-hero">` and every section heading. Headings carry no `text-transform` — write the case you want into the markup, because CSS `capitalize` would raise "the" too. Sub-lines stay sentence case: `.section-sub`, `.lede`, and body copy are not headings.
- **Section headings are `<h2 class="quid-h1">`** — the element stays `<h2>` so the document outline is correct under the hero `<h1>`, but the type class is `quid-h1` (28px), not `quid-h2`. A section heading is a major landmark in a brief and is sized accordingly; `quid-h2` is for sub-headings *inside* a section.
- **Dates in the eyebrow pill read `Mmm D, YYYY`, ranges joined by a spaced en dash** — "Sep 14, 2026 – Sep 21, 2026": abbreviated month, no leading zero on the day, four-digit year, `–` (not a hyphen) between the two ends. A single date just drops the second half. The pill's other segments are unchanged and stay middot-separated (`Client · Scope · …`).
- **Smooth-scroll and the page canvas ship with the shell.** Side-nav anchor clicks smooth-scroll (`html { scroll-behavior: smooth }`), and the page sits on the soft `--shell-canvas` tint behind the white section cards. Both are automatic — nothing to wire.
- **Reduced motion is handled for you.** `quid.css` ends with a `@media (prefers-reduced-motion: reduce)` block that reverts `scroll-behavior` to `auto` and collapses every transition and animation to `.01ms`. A reader who has asked their OS for less motion gets a brief that jumps rather than glides. It deliberately does **not** strip `transform`: the open/closed state of the Methodology and accordion disclosures is drawn by rotating a `▸` glyph, so removing transforms would delete a state indicator for exactly the people asking for the accommodation. Nothing to wire, and nothing to add per brief — but if you hand-write a keyframe animation into a brief, it is covered only while it respects `animation-duration`.
- The active rail link uses `--primary-container-foreground` / `--primary-container-background` with a `--primary` left border; hover uses `--secondary`. All from tokens — no raw hex.

Full-page reference (masthead + rail + working scroll-spy): **`shell-modern-example.html`** — copy this to start a brief. For the same shell with every catalog component composed into it, open **`example-modern.html`**. Both over http; they are complete briefs, unlike the boxed component tiles in `example.html`.

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
| Methodology | **Standard on every client brief:** the collapsed, small-type sources / window / caveats note that closes the slot | `components/methodology.md` |

## Theming

Light mode is the default. To activate dark mode, add `class="dark"` (or `data-theme="dark"`) to `<html>` or `<body>`. Every semantic token, including shadows, swaps to its dark counterpart.

## Files

```
~/.claude/skills/quid-design-system/
├── SKILL.md            ← this file: how to apply, the Shell, and the component catalog
├── quid.css            ← tokens, components, standard shell (generated; inline or @import)
├── quid-fonts.css      ← Quid Sans faces, base64, + the heading binding (generated)
├── quid-modern-shell.css ← modern shell: black masthead, right rail, boxless sections
├── shell-modern-example.html ← START HERE for a new brief: the shell, with scroll-spy
├── example.html        ← every component, bare, in a flat gallery
├── example-modern.html ← the same components inside the modern shell (generated)
├── build_example_modern.py ← example.html → example-modern.html; re-run after editing a demo
├── build_tokens.py     ← parser: tokens/*.json → quid.css
├── check_delivery.py   ← pre-delivery check: no relative href/src in a brief
├── tokens/             ← source Figma DTCG exports (see the patch note below)
│   ├── base-colors.tokens.json
│   ├── primitives.tokens.json
│   ├── system-colors-light.tokens.json
│   ├── system-colors-dark.tokens.json
│   ├── shadow-colors-light.tokens.json
│   ├── shadow-colors-dark.tokens.json
│   ├── typography-desktop.tokens.json
│   └── typography-mobile.tokens.json
└── components/         ← one doc per catalog component (read the ones the brief uses)
```

**`tokens/` carries one local patch.** It is normally a verbatim Figma export:

| token | exported | patched to | why |
|---|---|---|---|
| light `primary-container-foreground` | `#13797D` | `#246C6F` | teal-on-pale-teal is 4.05:1, down from 5.59:1 before the migration. `#246C6F` is already in the teal ramp and gives 4.77:1 |

Every semantic background/foreground pair clears 4.5:1 in both themes.

### Token-name collisions: fixed at the source, and guarded here

Tokens are emitted under their **leaf** name, so two Figma groups sharing a leaf
collapse onto one custom property. The 2026-11-02 exports resolved every such
collision at the source, and `build_tokens.py --strict` now passes clean. Two
are worth knowing about, because both were live hazards and both could return:

- **`font-family/font-size-h1`** and seven siblings collided with the real
  `font-size/*` and `font-weight/*` tokens. `--font-headings` was declared twice
  — once as an unresolved `{font-family.font-display}`, once as `700` — and
  headings got their weight only because the valid declaration happened to be
  emitted second. Reordering the groups would have stripped the weight from
  every heading on every brief, silently. Now renamed to `font-family/font-family-h1`
  and friends.
- **`radius(open-source)/radius-sm`** (4px) briefly collided with the Quid
  `radius/radius-sm` (6px), which six rules in this stylesheet read. It is now
  `radius-xs` again.

`build_tokens.py` no longer depends on any of that being right. It resolves
collisions deterministically rather than by emit order — the token whose leaf
carries its own group prefix keeps the canonical name, the other is emitted as
`<group>-<leaf>` — prints what it did, and `--strict` exits non-zero so CI can
refuse. `assert_unique` is a hard backstop: no block may declare the same
property twice.

**If a future export reintroduces a collision, rename the leaf in Figma rather
than deleting it.** Variables are bound by ID, so renaming preserves existing
bindings and deleting breaks them. `font-family/font-size-h1` was bound by two
text nodes on the `styles` page when this came up.

Two earlier patches were **dropped** because the export fixed them better:

- **Dark `primary`** is now `#37A1A5` rather than `#13797D`, with
  `primary-foreground` back to `#212121`. Lightening the dark-mode primary so
  dark text reads on it is the right answer; the previous local patch forced
  white text instead. 5.22:1.
- **`hover:primary` / `pressed:primary`** now carry distinct alphas per theme
  rather than the flat teal that was patched in. Note that **nothing in
  `quid.css` consumes these two tokens** — `.quid-button:hover` changes only
  `box-shadow`. They exist for app consumers. A consumer that paints a button
  background with them should check contrast after compositing: at the exported
  alphas, `primary-foreground` over the composited state falls below 4.5:1 in
  both themes.

**These will be silently reverted by the next Figma re-export.** The durable fix
is in Figma: restore the radius group, and finish the teal migration through
`primary-foreground`, `hover:primary` and `pressed:primary`. Re-run
`build_tokens.py` after any export and re-check contrast.

## Updating after a Figma change

1. Replace the relevant file(s) in `tokens/` with the new Figma export.
2. **Check whether the local patch above is still needed, then re-apply only if
   it is.** A re-export silently drops it, but it may also have fixed it — the
   2026-11-02 exports resolved four of five. Re-applying a patch the designer
   has superseded is as wrong as losing one.
3. From this directory, run `python3 build_tokens.py` to regenerate `quid.css`.
   **Read the warnings.** It reports any token-name collision in the Figma
   source and says how it resolved each one. `python3 build_tokens.py --strict`
   exits non-zero instead, for CI.
4. **Diff the token names, not just the output.** The last export dropped an
   entire group; the regenerated file looked fine and `var(--radius)` was
   invalid in 34 places. Any token that disappears is a regression until proven
   otherwise.
5. **Re-check primary-button contrast in both themes.** `--primary` against
   `--primary-foreground` must be at least 4.5:1 for normal text.
6. Spot-check `example-modern.html` and `shell-modern-example.html` in a browser
   before using the skill on a real brief.

## Authoring conventions

- Always reference semantic tokens (`var(--card)`, `var(--primary)`) in component code, not raw ramp colors. The ramps are for charts, illustrations, and one-off accents.
- Default body text is **14 / 20 Inter Regular**. Use `.quid-body` to be explicit, `.quid-body-lg` for hero copy.
- Default radius is **8px** (`--radius`, the shadcn alias) — use it for cards, buttons, inputs, and most surfaces. Reach for `--radius-sm` (6) only on dense controls/chips, and `--radius-lg` (12) on hero / floating panels where you specifically want the chunkier corner.
- Default elevation on cards is `--shadow-sm-recipe`; promote to `--shadow-rg-recipe` only for floating panels (popovers, dropdowns).

## Extending the system (maintainers)

- New color / type / shadow → edit `tokens/`, rerun `build_tokens.py`.
- New utility class or component CSS → a new block in `build_tokens.py`, then regenerate `quid.css` (never hand-edit it).
- New component → a new file in `components/`, **one catalog row** in this file, and a real-data demo in `example.html`. Never paste a full component spec into this file — it only points. Maintainers: follow the `add-gallery-component` runbook in the internal working repo.
