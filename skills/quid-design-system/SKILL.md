---
name: quid-design-system
description: >
  Apply the Quid (Terminal) design aesthetic to any HTML artifact before generation.
  Inlines a single stylesheet that exposes all Figma tokens (colors, typography, radius,
  shadows) as CSS custom properties wired to shadcn/ui semantics, plus a small set of
  Quid-branded utility classes, a full-page shell container (side-nav rail with
  scroll-spy, hero, and section primitives — the frame a
  multi-section brief is built on), an optional KPI metric strip, colored tag badges, a ranked-theme list (rank + badge + metrics + verbatim quotes), chart-series color tokens, a data table, an accordion, a media-beside ranked-theme variant, featured-post cards, a caption-insight presentation for ranked themes (with a shared post-detail modal), an optional methodology block, and example-post components (post cards with
  images, per-platform image sourcing, large creative-showcase cards in a 3-up grid,
  live social embeds). Use BEFORE creating an HTML brief, dashboard, report, or any
  other Quid-branded artifact so the output inherits correct fonts, colors, radius, and
  spacing. Triggers: "make this Quid-branded", "apply Quid styling", "use our design
  system", "Quid look and feel", "add a side nav", "on-this-page rail", "shell layout",
  "multi-section brief", "show example posts in the brief", "embed the posts",
  "creative in the wild", "showcase the top creatives", any HTML brief generation,
  push-brief.
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

Inline `quid.css` in `<head>` so the brief stays **one HTML file with no sibling asset files** — push-brief uploads a single file. External URLs are expected and fine: the Inter stylesheet below, post images (see "Image policy: hotlink-only"), and platform embed scripts all load over the network. The requirement is one file to upload, not zero network requests.

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
- **KPI strip** — `.kpi-grid`, `.kpi-card`, `.kpi-card .label` / `.value` / `.delta` (`.up` / `.down`) / `.period` — optional top-accent metric cards (see the dedicated section below).
- **Tags / badges** — `.tag` + `.tag-opportunity` / `-risk` / `-trend` / `-signal` / `-watch` / `-neutral` — colored pill labels (see the dedicated section below).
- **Ranked theme — with quotes** — `.theme-list`, `.theme-card`, `.theme-head`, `.theme-rank`, `.theme-name`, `.theme-metrics` / `.theme-metric` (`.up` / `.down`), `.theme-desc`, `.theme-quote` / `.q-src`, `.theme-examples-label` (uses the shared `.tag` badge). Boxless ranked list with inline verbatim quotes (see the dedicated section below).
- **Chart palette & convention** — series-color tokens `--chart-1…14` (categorical), `--sentiment-positive` / `-neutral` / `-negative`, `--citrus-1…6` (wordcloud). Read by charts via `getComputedStyle` (see the dedicated section below).
- **Table** — `.table-wrap` (+ `.clickable`) wrapping a `<table>`; `.num` right-aligns numeric cells (see the dedicated section below).
- **Accordion** — `.accordion` wrapping native `<details>` / `<summary>` (+ `.acc-meta`, `.acc-body`) — expandable stacked rows (see the dedicated section below).
- **Ranked theme — with media** — `.theme-card.with-media` + `.theme-text` / `.theme-thumb` / `.theme-cols` (extends the ranked-theme base; composes `.sc-carousel`) — text left, thumbnail right, carousel below (see the dedicated section below).
- **Featured posts** — `.posts-featured`, `.post`, `.post-thumb`, `.post-rank`, `.post-body`, `.post-author` (`.handle` / `.src`), `.post-text`, `.post-foot` (`.stat`) — 2-up rich cards for standout posts (see the dedicated section below).
- **Ranked theme — caption-insight** — `.ci-list`, `.ci-card`, `.ci-num`, `.ci-body`, `.ci-head`, `.ci-name`, `.ci-text`, `.ci-quotes`, `.ci-quote` / `.cq-handle` / `.cq-text` / `.cq-more`. A third presentation option for ranked themes (alongside with-quotes and with-media): ghost number + caption read + quote cards that open the shared **post-detail modal** (see the dedicated section below).
- **Post-detail modal** — `.post-modal-overlay` / `.post-modal` / `.post-modal-head` / `.post-modal-body` / `.pm-media` / `.pm-tabs` / `.pm-tab` / `.pm-panel` / `.pm-section` / `.pm-highlights` / `.pm-caption` / `.post-modal-foot`. A shared page singleton (markup + JS go in the brief once) opened by `.ci-quote`, `.post`, `.post-tile`, `.large-card`, and example-post `.sc-card[data-modal]` (see the dedicated section below).
- **Example-post components** — `.sc-carousel`, `.sc-card`, `.sc-thumb`, `.sc-thumb-ph`, `.sc-meta`, `.sc-who`, `.sc-handle`, `.sc-plat`, `.sc-quote`, `.sc-link` (see the dedicated section below).
- **Large cards (creative in the wild)** — `.large-cards`, `.large-card`, `.lc-media`, `.lc-thumb`, `.lc-logo`, `.lc-play`, `.lc-meta`, `.lc-head`, `.lc-author`, `.lc-src`, `.lc-text`, `.lc-stats` (see the dedicated section below).
- **Social embeds (native)** — `.embed-grid`, `.embed-tile`, `.embed-plat`, `.dot`, `.embed-body`, `.yt`, `.embed-note` — chrome for the platforms' own embed snippets (iframe or script blockquote), one tile per platform (see the dedicated section below).
- **Methodology** — `.methodology` — a small muted block for a brief's sources / window / caveats; an optional standalone component (not part of the shell) — see the dedicated section below.

## The Shell (page container)

The Shell is the **page container** every multi-section brief starts from — not a widget you drop in. It is the frame; the catalog components (KPI strips, charts, `.sc-carousel`, `.large-cards`, `.embed-*`, tables, pull-quotes) are the content that composes **inside** its sections. Reach for it whenever a brief has enough parts to be worth a structure and an "on this page" rail.

The container is two fixed regions plus one slot:

1. **Side-nav rail** (`.sidenav`) — sticky "on this page" list, one link per section, with a scroll-spy that tracks the section in view.
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

## KPI strip

Optional summary metrics that sit above the slot (inside `.container-brief`, or inside any `.section`). Primary top-accent cards: a `.label` over a big `.value`, with an optional directional `.delta`. Auto-fits 3–4 cards; omit it when a brief has no headline numbers.

Contract (one `.kpi-card` per metric):

```html
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="label">{Metric name}</div>
    <div class="value">{Number}</div>
    <div class="delta up">+31% <span class="period">vs last month</span></div>
  </div>
  <!-- …3–4 cards… -->
</div>
```

Rules the markup can't show:

- **Label first, value second** — the eyebrow-style `.label` sits *above* the big `.value`; don't invert them.
- **`.delta` is optional and directional** — `.up` renders a green ▲, `.down` a red ▼ (the arrow is a `::before`, so put only the number in the text). The `.period` span is the comparison window ("vs last month"), muted and inline.
- **Only show a delta you can source.** A delta implies a real prior-window comparison — omit the `.delta` row entirely for a snapshot metric with no baseline (a value-only card is valid). Never invent a percentage.
- Use **3 or 4 cards**; the grid auto-fits and wraps below ~160px per card.

Reference markup (up, down, and value-only cards): the "KPI strip" section of `example.html`.

## Tags / badges

Small colored pill labels for tagging a theme, post, or insight with a category. Six semantic variants, each an intent-colored fill:

```html
<span class="tag tag-opportunity">Opportunity</span>   <!-- blue -->
<span class="tag tag-risk">Risk</span>                 <!-- red -->
<span class="tag tag-trend">Trend</span>               <!-- purple -->
<span class="tag tag-signal">Signal</span>             <!-- green -->
<span class="tag tag-watch">Watch</span>               <!-- orange -->
<span class="tag tag-neutral">Neutral</span>           <!-- gray -->
```

Rules the markup can't show:

- **Pick the variant by meaning, not by color** — `opportunity`/`signal` read positive, `risk`/`watch` read cautionary, `trend` is neutral-notable, `neutral` is unweighted. The colors come from the ramp tokens; don't restyle with raw hex.
- **`.tag` is the base class** — always pair it with exactly one `.tag-*` variant. Keep the label short (1–2 words).
- Distinct from `.quid-badge` (a plain gray count/meta chip); reach for `.tag-*` when the label carries a category or sentiment.

Reference markup (all six variants): the "Tags / badges" section of `example.html`.

## Ranked themes — choosing a presentation

Ranked themes have **three interchangeable presentations** — same ordered set of themes, different emphasis. Pick one per section:

- **With quotes** (this section) — rank + badge + metrics + description + inline verbatim pull-quotes. The default; best when the *quotes themselves* are the evidence.
- **With media** (`.theme-card.with-media`) — text left, a thumbnail top-right, and a full-width example-post carousel below. Best when a hero image or several example posts per theme carry the story.
- **Caption-insight** (`.ci-*`) — a big ghost number + name/tag + a one-line caption **read**, then a 2-up grid of clickable quote cards that open the post-detail modal. Best when the *interpretation* leads and readers drill into individual posts.

Each is documented below.

## Ranked theme — with quotes

Use to present the top themes of a conversation as a ranked list — rank + title + a category badge + metrics + a short description, then a couple of **verbatim** quotes as evidence. It is **boxless**: ranked items sit directly on the section surface, separated by a bottom hairline (no card chrome), so several themes read as one ordered list.

Contract (one `.theme-card` per ranked theme, inside a `.theme-list`):

```html
<div class="theme-list">
  <div class="theme-card">
    <div class="theme-head">
      <span class="theme-rank">1</span>
      <span class="theme-name">{Theme title}</span>
      <span class="tag tag-trend">{Category}</span>
      <span class="theme-metrics">
        <span class="theme-metric">Mentions <b>{n}</b></span>
        <span class="theme-metric">YoY <span class="up">+{n}%</span></span>
      </span>
    </div>
    <p class="theme-desc">{1–2 sentence description.} <em>{optional emphasis}</em></p>
    <blockquote class="theme-quote">"{verbatim quote}" <a class="q-src" href="{url}">{Source} →</a></blockquote>
    <!-- …1–3 quotes… -->
  </div>
  <!-- …more ranked .theme-card items… -->
</div>
```

Rules the markup can't show:

- **Quotes are verbatim.** `.theme-quote` text is the post's own words, in quotation marks, with a `.q-src` link to the source — never paraphrase or invent, and don't strip a quote of its attribution.
- **The badge is a shared `.tag`** (see "Tags / badges") — pick the variant by meaning; one badge per theme.
- **Metrics are flexible slots** (`.theme-metric` with a bold `<b>` value). Use whatever you actually have — Mentions, Authors, Share, YoY. Wrap a trend figure in `.up` (green) or `.down` (red); **only show a trend you can source** — omit it for a snapshot with no prior-window baseline (don't invent a YoY).
- **Boxless is the point** — don't wrap `.theme-card`s in `.quid-card`/`.section` boxes each; the hairline divider between items carries the ranking. The whole `.theme-list` goes inside one `.section`.
- `.theme-examples-label` ("Example posts") is an optional lead-in when you follow the quotes with an example-post carousel.

Reference markup (three ranked themes with real verbatim quotes + source links): the "Ranked theme — with quotes" section of `example.html`.

## Chart palette & convention

Series colors for charts are **tokens**, not hard-coded hex — so a chart re-themes with the rest of the design system and a client override is a token swap.

- **Categorical** (bars, lines, pies, multi-series): cycle `--chart-1` … `--chart-14` in order. Fourteen hues chosen to stay distinct; don't repeat before you've used them.
- **Sentiment**: `--sentiment-positive` (green), `--sentiment-neutral` (gray), `--sentiment-negative` (red). Use these — not the categorical ramp — whenever the dimension is sentiment.
- **Wordcloud / density**: the Citrus set `--citrus-1` … `--citrus-6`.
- **Axes & labels**: grid lines use `--border`; tick/legend labels use `--muted-foreground`.

Charts (e.g. Chart.js) should read these at runtime via `getComputedStyle(document.documentElement).getPropertyValue('--chart-1')` rather than pasting hex, so dark mode and per-client overrides flow through. Any chart type works inside a `.chart-card`.

Reference swatches (all three sets): the "Chart palette & convention" section of `example.html`.

## Table

For metrics and comparisons. Wrap a plain `<table>` in `.table-wrap` (which supplies the surface, top/bottom rules, and header styling):

```html
<div class="table-wrap">
  <table>
    <thead><tr><th>Layer</th><th class="num">Posts</th><th class="num">Net</th></tr></thead>
    <tbody>
      <tr><td>UGC</td><td class="num">303K</td><td class="num">+72</td></tr>
    </tbody>
  </table>
</div>
```

Rules the markup can't show:

- **`.num` on every numeric cell** — both the `<th>` and the `<td>` — right-aligns and turns on tabular figures so columns line up. Text cells stay left-aligned.
- **No row hover by default.** Add `class="clickable"` to `.table-wrap` only when rows are actually interactive (then wire the click yourself); otherwise leave it off so a static table doesn't imply clickability.
- Keep it a real `<table>` (thead/tbody) for semantics — don't fake rows with divs.

Reference markup (a real platform breakdown): the "Table" section of `example.html`.

## Accordion

Expandable stacked rows for FAQs, per-item or per-source comparisons — built on the **native `<details>`/`<summary>`** element, so it works with no JavaScript.

```html
<div class="accordion">
  <details open>
    <summary>Recommendations &amp; on-property experience <span class="acc-meta">19K mentions</span></summary>
    <div class="acc-body"><p>…</p></div>
  </details>
  <details>
    <summary>Nostalgia &amp; anticipation <span class="acc-meta">10K mentions</span></summary>
    <div class="acc-body"><p>…</p></div>
  </details>
</div>
```

Rules the markup can't show:

- **Native element, no JS.** Each row is a `<details>` with a `<summary>` (the clickable header) and a `.acc-body` (the revealed content). The rotating ▸ caret and marker hiding are handled in CSS.
- **`open` sets the default-expanded row(s)** — put it on the one(s) you want open on load (often just the first). Any number can be open at once.
- **`.acc-meta` is an optional right-aligned label** in the summary (a count, a `Watch` flag) — keep it short. `.acc-body` holds the prose.

Reference markup (three real subtopic rows): the "Accordion" section of `example.html`.

## Ranked theme — with media

The **media-beside** variant of the ranked theme (see "Ranked theme — with quotes" for the base). Same boxless ranked list, but each item is a grid: title/metrics/description on the left, a thumbnail top-right, and a full-width example-posts carousel below. Reach for it when the themes have a representative image and you want to show example posts inline rather than a couple of pull-quotes.

Contract (add `with-media` to `.theme-card`):

```html
<div class="theme-list">
  <div class="theme-card with-media">
    <div class="theme-text">
      <div class="theme-head"><span class="theme-rank">1</span><span class="theme-name">{Title}</span><span class="tag tag-trend">{Category}</span><span class="theme-metrics"><span class="theme-metric">SoV <b>{n}%</b></span></span></div>
      <p class="theme-desc">{Description.} <em>{Opportunity/signal.}</em></p>
    </div>
    <img class="theme-thumb" src="{coverage image}" alt="" referrerpolicy="no-referrer">
    <!-- …or, when the theme has no image: <div class="theme-thumb"></div> (gray placeholder) -->
    <div class="theme-cols">
      <p class="theme-examples-label">Example posts</p>
      <div class="sc-carousel"><!-- .sc-card items (see Example-post components) --></div>
    </div>
  </div>
</div>
```

Rules the markup can't show:

- **Three regions, fixed grid**: `.theme-text` (left), `.theme-thumb` (top-right, 200×140 → full-width under 760px), `.theme-cols` (carousel, full width). Keep that order; the grid areas place them.
- **`.theme-thumb` is the image *element*, not a wrapper** — for a real theme image use `<img class="theme-thumb" src="…" referrerpolicy="no-referrer">`; it fills the 200×140 box via `object-fit: cover`. When the theme has no image, use an empty `<div class="theme-thumb"></div>` — that renders the gray `--muted` box (a deliberate placeholder, not a missing asset). Use a real coverage image for the theme (same sourcing as example posts); never stretch an unrelated stock image.
- **The carousel is the standard `.sc-carousel`** — same `.sc-card` contract and image rules as "Example-post components" (verbatim quotes, `referrerpolicy="no-referrer"`, domain-tile fallback).
- Everything from the base ranked theme still holds (verbatim quotes, `.tag` badge, sourced trend only, boxless hairline between items).

Reference markup (two real themes with example-post carousels): the "Ranked theme — with media" section of `example.html`.

## Featured posts

A 2-up grid of rich cards for a handful of standout posts — bigger than the `.sc-carousel` tiles, with a thumbnail, author, a few lines of text, and a footer. Use it for "top posts of the week" / a few flagship posts; use `.sc-carousel` when the point is *many* posts to scan.

```html
<h3 class="sub-head">Featured posts <span class="count">6</span></h3>
<div class="posts-featured">
  <article class="post">
    <div class="post-thumb"><span class="post-rank">1</span><!-- optional <img> --></div>
    <div class="post-body">
      <div class="post-author"><span class="handle">@espn</span><span class="src">Instagram</span></div>
      <p class="post-text">{the post's own text, verbatim}</p>
      <div class="post-foot"><span class="stat"><b>184K</b> likes</span><span class="stat"><b>3.2K</b> comments</span></div>
    </div>
  </article>
  <!-- …one <article class="post"> per featured post… -->
</div>
```

Rules the markup can't show:

- **`.post-text` is the post's own text, verbatim** (it clamps to 3 lines). `.handle` is the author/handle as shown; `.src` is the platform name only.
- **`.post-rank` is optional** — a small badge pinned inside `.post-thumb` (so the thumb is present even as a gray placeholder). Put a real coverage `<img>` in `.post-thumb` when you have one (same hotlink/`no-referrer` rules as example-post cards), else leave it as the gray box.
- **`.post-foot` is engagement stats *or* a category tag — not invented numbers.** Use `.stat` (`<b>{n}</b> likes`) **only** when the counts come verbatim from the data source; otherwise use a `.tag-*` badge (category/sentiment) and omit stats. Never estimate engagement.
- **Cards are static by default.** To make a card open the post-detail modal, add `tabindex="0" role="button" data-url="{url}"` and wire the modal (a separate component) — the CSS styles both the same.

Reference markup (two real featured posts): the "Featured posts" section of `example.html`.

## Ranked theme — caption-insight

The **caption-insight** presentation of ranked themes (the third option — see "Ranked themes — choosing a presentation" above): each theme is a big **ghost number** + name/tag + a caption **read** (a sentence on what the captions *collectively* say), then a 2-up grid of quote cards. Each quote card is clickable and opens the shared **post-detail modal** with that post's fuller detail. Reach for it when the interpretation should lead and readers drill into individual posts.

Contract (one `.ci-card` per theme, inside a `.ci-list`):

```html
<div class="ci-list">
  <div class="ci-card">
    <div class="ci-num">1</div>
    <div class="ci-body">
      <div class="ci-head"><span class="ci-name">{Theme}</span><span class="tag tag-trend">{Category}</span></div>
      <p class="ci-text">{The caption read — what the captions collectively say.} <strong>{emphasis}</strong></p>
      <div class="ci-quotes">
        <div class="ci-quote" tabindex="0" role="button" data-url="{post URL}">
          <script type="application/json" class="post-data">{"handle":"@x","source":"X","url":"{post URL}","caption":"{verbatim quote}"}</script>
          <span class="cq-handle">@x</span><span class="cq-text">"{verbatim quote}"</span><span class="cq-more">Post detail →</span>
        </div>
        <!-- …quote cards (2-up grid)… -->
      </div>
    </div>
  </div>
</div>
```

Rules the markup can't show:

- **The `.ci-text` is an interpretation** — it summarizes what the captions collectively convey. It's editorial, so keep it faithful to the set; the **`.cq-text` quotes stay verbatim**.
- **Each `.ci-quote` opens the post-detail modal** — it needs `tabindex="0" role="button"` and a `data-url`, plus an inline `<script type="application/json" class="post-data">` blob for the modal to read (falls back to `.cq-handle`/`.cq-text` if the blob is absent). See "Post-detail modal" below — the modal singleton + its script must be present once in the brief for clicks to do anything.
- The badge is the shared `.tag`; one per theme (optional). Ghost number is decorative (`--border`-colored) — keep the list short so the numbers stay meaningful.

Reference markup (two real Taiwan themes with clickable quotes): the "Caption-insight themes" section of `example.html`.

## Post-detail modal

A shared **page singleton** — one overlay + one script per brief — that any clickable card opens to show a post's fuller detail (media, tabbed Summary / Highlights / Caption, and an "Open on {platform}" link). Openers are `.ci-quote`, `.post`, `.post-tile`, `.large-card`, and — opt-in — example-post `.sc-card[data-modal]`; the CSS ships in `quid.css`, but the **markup and JS live in the brief** (they can't ship in a stylesheet).

**Example posts ↔ caption-insight are interchangeable, and both feed this modal.** A theme's supporting posts can be shown as an example-post carousel (`.sc-carousel`, image-forward, links out by default) or as a caption-insight quote grid (`.ci-quotes`, quote-forward, opens the modal) — swap one for the other freely. To give example-post cards the same drilldown, add `data-modal` to the `.sc-card` (it then opens the modal, populated from its `.sc-handle` / `.sc-quote` / `.sc-thumb` image / `href`, instead of linking out). Add a `post-data` blob to any opener for the richer tabbed view.

Wire-up (once per brief, near `</body>`):

1. **The overlay markup** — copy the `<div class="post-modal-overlay" id="postModal">…</div>` block from the end of `example.html` verbatim (it has the fixed ids the script binds to: `pmHandle`, `pmMedia`, `pmTabs`, `pmPanels`, `pmFoot`, `pmClose`).
2. **The opener script** — copy the `<script>` that follows it. It delegates clicks/Enter on any opener, reads the card's `post-data` blob (or falls back to the card's handle/text/thumb/href), builds the tabs, and toggles `body.modal-open`.

Each openable card carries an inline data blob for the richer view:

```html
<script type="application/json" class="post-data">{
  "handle":"@x", "source":"TikTok", "url":"…", "thumb":"…",
  "summary":[{"label":"Overall","text":"…"}],
  "highlights":["…","…"],
  "caption":"…"
}</script>
```

Rules the markup can't show:

- **One modal per page.** Include the overlay + script exactly once, even with many openers — the handler is delegated, so new cards work without re-wiring.
- **Tabs appear only for the fields you provide.** `summary` → Summary tab, `highlights` → Highlights tab, `caption` → Caption tab; with one field the tab bar hides. Provide only what you can source — don't invent a `Visual`/`Audio` read for a text post.
- **`thumb`** should be a real, still-live image (same hotlink rules as example posts); omit it and the modal shows a placeholder icon rather than a broken image.
- Without a `post-data` blob the modal still opens, falling back to the card's `.cq-handle`/`.cq-text` (or `.handle`/`.post-text`) and its `href`/`data-url`.

Reference: the overlay markup + script at the end of `example.html`, opened by the "Caption-insight themes" quote cards.

## Methodology

An **optional standalone** block for a brief's provenance — data source, date range, query, and caveats. It is **not part of the shell** (the shell doesn't prescribe it); add it wherever that note belongs, typically as the **last `.section`** in a brief. `.methodology` caps the reading width (~900px) and renders its paragraphs as small muted text so it reads as a footnote, not primary narrative.

```html
<section class="section" id="section-methodology">
  <p class="section-label">Methodology</p>
  <div class="methodology">
    <p>{Data source, date range, query, caveats.}</p>
    <p>{Analysis notes / exploratory caveats.}</p>
  </div>
</section>
```

- **It's an ordinary `.section`** — wrap `.methodology` in one so it gets the card surface; the `.section-label` "Methodology" is the eyebrow. If the brief has a side-nav, add a rail link to its id like any other section.
- **Use it for provenance and caveats, not headline content** — the small muted type is deliberate.

Reference markup: the "Methodology" section of `example.html`.

## Example-post components

Use when a brief shows real social or news posts as evidence — top posts, example posts per theme, quote cards. The `.sc-*` styles ship inside `quid.css`, so inlining `quid.css` is all the setup needed; copy the markup shape from the "Example posts" section of `example.html`.

**Interchangeable with the caption-insight quote grid** (`.ci-quotes`): both present a theme's supporting posts, so you can swap this carousel for that grid (or vice versa) depending on whether images or quotes should lead. By default `.sc-card` links out to the post; add `data-modal` to open the shared **post-detail modal** instead (same drilldown the caption-insight cards use).

Card contract (each card is one post):

```html
<a class="sc-card" href="{post URL}" target="_blank" rel="noopener">
  <div class="sc-thumb"><img src="{image URL}" loading="lazy" alt="" referrerpolicy="no-referrer"
    onerror="this.parentElement.classList.add('sc-thumb-ph'); this.parentElement.innerHTML='<span>{domain}</span>'"></div>
  <div class="sc-meta">
    <div class="sc-who"><span class="sc-handle">{@handle}</span> <span class="sc-plat">{platform}</span></div>
    <p class="sc-quote">"{the post's own text, verbatim}"</p>
    <span class="sc-link">View post ↗</span>
  </div>
</a>
```

Quotes are the post's real text — never paraphrase or invent. `.sc-plat` is the platform name only.

### Image policy: hotlink-only

Put the platform's own image URL in `src` — no local files, no base64 — so the brief stays one file with no sibling assets. Some platform URLs expire; that is accepted, with two rules making it safe:

1. **Every post `<img>` carries `referrerpolicy="no-referrer"` and the `onerror` handler** shown above. `no-referrer` is load-bearing: Instagram/Facebook/TikTok CDNs reject hotlinks that send a Referer header, and pass them without one. `onerror` makes an expired or dead image degrade to the domain gradient tile (`.sc-thumb-ph`) instead of a broken-image icon.
2. **A post with no image at all** (deleted, or the source exposes none) renders `.sc-thumb-ph` with its domain from the start. Never leave the slot empty and never substitute an unrelated image.

Where the image URL comes from — these are platform traits, not tool instructions, and none of them depends on any other skill existing:

| URL trait | Platforms (as of 2026) | What to do |
| --- | --- | --- |
| Stable public image CDN | YouTube (`i.ytimg.com/vi/{id}/hqdefault.jpg`), X media (`pbs.twimg.com`), Bluesky (`cdn.bsky.app`), many news CDNs (e.g. espncdn) | Hotlink; effectively durable |
| Signed, expiring URL | Instagram & Facebook `og:image` (fetch the post page server-side to read it), TikTok covers (oEmbed `thumbnail_url`) | Hotlink anyway; dies in days — rule 1 covers it |
| Blocked front door | Reddit (`www.reddit.com` pages and JSON API reject plain fetches; `old.reddit.com` still serves full HTML with `og:image` / `i.redd.it` links) | Use the alternate route |
| Nothing to fetch | Deleted posts; text-only posts | Rule 2: domain tile |

If the workspace has a data-collection skill for the platform, prefer its response over scraping — e.g. X search results typically already include media URLs — but the table above works without any of them.

**Prefer real images; a tile is a per-post last resort, not the plan for a whole carousel.** A report reads as more compelling and credible when its example posts show real images. Accepting that a URL may *expire later* (rule 1) is not the same as accepting a tile *now* — so before settling for a tile, put in the work to get a real image:

- **Resolve before you tile.** For every post without a ready image URL, try the route in the table above (`og:image` via a server-side page fetch; the platform's alternate route where its front door is blocked) before falling back. Some platforms won't yield an image to an unauthenticated fetch at all — that is expected, not a failure; those tile. Also skip images that aren't the post's own content: site logos and generic share/`og-default` banners, and permalinks that point at a comment/reply rather than the post itself. These skip patterns are examples, not an exhaustive list — the test is "is this the post's own image?"
- **A resolved URL isn't proven until it renders.** Server-side fetch success ≠ browser load success — some hosts return an `og:image` to a fetch but still reject the cross-origin `<img>` request even with `no-referrer`. So confirm each `<img>` actually loads in the rendered page (a programmatic check works in headless runs where no one is watching), and if it doesn't, backfill rather than trusting the resolved URL. The `onerror` tile in rule 1 is the safety net; this check is what keeps a working image from being downgraded to a tile unnecessarily.
- **Backfill from your candidate pool, don't settle.** The 2–3 posts you show per group are *chosen*, not fixed. If a given post can't produce a real image (never resolved, or resolved-but-won't-load), swap in another relevant post that can. This works best when you pick from the full set of source records for that group rather than a short pre-picked shortlist, which rarely has enough candidates to find image-bearing ones. Reach for the fuller pool as soon as the ask is "more / better / image-bearing example posts."

(Platform-specific behaviours — which hosts block unauthenticated fetches, which need an alternate route — change over time; treat the table above as current best-practice pointers, not fixed rules, and re-check if one stops working.)

## Large cards (creative in the wild)

Use when a brief showcases a handful of hero posts — campaign creatives spotted in the wild, top posts of the week, one flagship post per theme. Cards sit in a responsive 3-up grid (2-up under 900px, 1-up under 560px) with a square image on top, and the **whole card** is the click target. Prefer the `.sc-carousel` (previous section) when the point is *many* evidence posts to scan; prefer `.large-cards` when the point is a *few* posts worth a big visual.

Card contract (each card is one post; the card itself is the link):

```html
<div class="large-cards">
  <a class="large-card" href="{post URL}" target="_blank" rel="noopener">
    <div class="lc-media"><img class="lc-thumb" src="{image URL}" loading="lazy" alt="" referrerpolicy="no-referrer"
        onerror="this.parentElement.classList.add('sc-thumb-ph'); this.parentElement.innerHTML='<span>{domain}</span>'">
      <span class="lc-logo" title="{platform}"><svg …>{platform logo}</svg></span>
      <span class="lc-play"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg></span></div>
    <div class="lc-meta">
      <div class="lc-head"><span class="lc-author">{author name or @handle}</span><span class="lc-src">{platform}</span></div>
      <p class="lc-text">{the post's own text, verbatim}</p>
    </div>
  </a>
</div>
```

Rules the markup can't show:

- **Always wrap the image in `.lc-media`** (never a bare `.lc-thumb` as the card's first child) — the `onerror` fallback swaps the *parent* into the shared `.sc-thumb-ph` domain-gradient tile, so the parent must be the media box. A post with no image at all renders `<div class="lc-media sc-thumb-ph"><span>{domain}</span></div>` from the start.
- **Image sourcing is identical to the example-post carousel** — hotlink-only, `referrerpolicy="no-referrer"` mandatory, per-platform URL traits and expiry rules in the "Image policy: hotlink-only" table above.
- `.lc-play` marks video posts (TikTok, YouTube, Reels) — omit it on image posts. `.lc-logo` is the platform (or channel) logo overlay; copy a logo SVG from `example.html` rather than sourcing new artwork. Both are optional; a plain image card is just `.lc-media` + `.lc-thumb`.
- `.lc-text` is the post's own text verbatim (it line-clamps at 2 lines); `.lc-author` is the display name or handle as the platform shows it; `.lc-src` is the platform name only.
- `.lc-stats` (`<div class="lc-stats"><span><b>{n}</b> likes</span>…</div>`, last child of `.lc-meta`) exists for engagement counts. Include it only when the numbers come verbatim from the data source for that post — never estimate or invent; omit the row entirely otherwise.
- In a brief that has a post-detail modal, replace the anchor with `<div class="large-card" tabindex="0" role="button" data-url="{post URL}">` and let the modal's opener read `data-url` — the CSS styles both shapes identically.

Reference markup with one real card per media pattern: the "Large cards (creative in the wild)" section of `example.html`.

### Live embeds (optional upgrade)

When the brief should show the *living* post itself (playable video, live like counts) instead of a card, use the **Social embeds (native)** component below. Prefer cards when durability matters (a deleted post leaves an embed blank with no fallback), or pair each embed with a card as backup.

## Social embeds (native)

Use when the brief should show the living post itself — playable video, live like counts, the real thread — instead of a styled card. Each tile wraps **the platform's own embed snippet** in Quid chrome; the design system owns only the tile (`.embed-tile` label + body over `var(--card)`/`var(--border)`/`var(--radius)`), never the embedded content. Cards (the sections above) are the durable default; reach for native embeds when liveness is the point.

Grid contract (one `.embed-tile` per platform):

```html
<div class="embed-grid">
  <div class="embed-tile">
    <div class="embed-plat"><span class="dot" style="background:{platform color}"></span>{Platform}</div>
    <div class="embed-body">{the platform's native embed snippet}</div>
  </div>
  <!-- …one tile per platform… -->
</div>
<p class="embed-note">{one-line note on what renders live vs. what needs a real post ID}</p>
```

The tile chrome is identical across platforms; only the `.embed-body` payload differs. Pick the payload by platform trait — **how that platform embeds**, not which tool fetched the post:

| Embed method | Platforms (as of 2026) | `.embed-body` payload | Extra setup |
| --- | --- | --- | --- |
| Plain iframe | YouTube | `<div class="yt"><iframe src="https://www.youtube.com/embed/{id}" … allowfullscreen loading="lazy"></iframe></div>` (the `.yt` wrapper gives a responsive 16:9 box) | none |
| Plain iframe | Facebook | `<iframe src="https://www.facebook.com/plugins/post.php?href={URL-encoded post URL}&show_text=true&width=300" … loading="lazy"></iframe>` | none |
| Direct `/embed/` iframe | Instagram, Threads | `<iframe src="{post URL}/embed/" width="100%" height="560" frameborder="0" scrolling="no" allowtransparency="true" loading="lazy"></iframe>` (Threads uses `/embed`, no trailing slash) | none — do **not** use blockquote+embed.js |
| Script-processed blockquote | X / Twitter | `<blockquote class="twitter-tweet"><a href="{tweet URL}"></a></blockquote>` | `platform.twitter.com/widgets.js` |
| Script-processed blockquote | TikTok | `<blockquote class="tiktok-embed" cite="{video URL}" data-video-id="{id}"><section></section></blockquote>` | `www.tiktok.com/embed.js` |
| Script-processed blockquote | Reddit | `<blockquote class="reddit-embed-bq" style="height:500px" data-embed-height="500"><a href="{post URL}">{title}</a></blockquote>` | `embed.reddit.com/widgets.js` |
| Script-processed blockquote | Bluesky | `<blockquote class="bluesky-embed" data-bluesky-uri="{at:// URI}" data-bluesky-cid="{CID}"></blockquote>` | `embed.bsky.app/static/embed.js` |

Rules the markup can't show:

- **Instagram/Threads use the direct `/embed/` iframe, never blockquote+embed.js.** The blockquote path needs a `postMessage` handshake with the parent page that never completes on a static, script-less brief, so the embed stays blank. Appending `/embed/` to the post URL is the path that renders.
- **Script-processed platforms need their widget script loaded once per page** (the four `<script async>` tags above, near `</body>`). Add `window.twttr.widgets.load()` on `window.load` so late-injected `.twitter-tweet` nodes rehydrate. In a single-file brief for `push-brief`, these scripts run only when the file is viewed over http — never `file://`.
- **Sandbox the cross-origin iframes.** Instagram/Facebook/Threads iframes should carry `sandbox="allow-scripts allow-same-origin allow-popups"` — a login-walled or deleted post can otherwise frame-bust and navigate the whole brief away.
- **Only public, still-live posts render; there is no fallback.** A deleted or private post leaves the tile blank. When durability matters, use a card (sections above) instead, or pair each embed with a card as backup.
- `.embed-plat` is the platform name plus a brand-colored `.dot`; keep the label to the platform only. `.embed-note` is an optional caption under the grid.

Reference markup with one tile per embed method: the "Social embeds (native)" section of `example.html` (with the required `<script>` tags near `</body>`).

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
├── example.html        ← component reference: type scale, cards, buttons, swatches, KPI strip, tags/badges, ranked theme (with quotes + with media), chart palette, table, accordion, featured posts, caption-insight themes + post-detail modal, example-post carousel, large cards, social embeds, methodology
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
