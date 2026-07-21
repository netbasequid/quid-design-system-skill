---
name: quid-design-system
description: >
  Apply the Quid (Terminal) design aesthetic to any HTML artifact before generation.
  Inlines a single stylesheet that exposes all Figma tokens (colors, typography, radius,
  shadows) as CSS custom properties wired to shadcn/ui semantics, plus a small set of
  Quid-branded utility classes and example-post components (post cards with images,
  per-platform image sourcing, large creative-showcase cards in a 3-up grid, live
  social embeds). Use BEFORE creating an HTML brief, dashboard, report, or any other
  Quid-branded artifact so the output inherits correct fonts, colors, radius, and
  spacing. Triggers: "make this Quid-branded", "apply Quid styling", "use our design
  system", "Quid look and feel", "show example posts in the brief", "embed the posts",
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
- **Example-post components** — `.sc-carousel`, `.sc-card`, `.sc-thumb`, `.sc-thumb-ph`, `.sc-meta`, `.sc-who`, `.sc-handle`, `.sc-plat`, `.sc-quote`, `.sc-link` (see the dedicated section below).
- **Large cards (creative in the wild)** — `.large-cards`, `.large-card`, `.lc-media`, `.lc-thumb`, `.lc-logo`, `.lc-play`, `.lc-meta`, `.lc-head`, `.lc-author`, `.lc-src`, `.lc-text`, `.lc-stats` (see the dedicated section below).

## Example-post components

Use when a brief shows real social or news posts as evidence — top posts, example posts per theme, quote cards. The `.sc-*` styles ship inside `quid.css`, so inlining `quid.css` is all the setup needed; copy the markup shape from the "Example posts" section of `example.html`.

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

Put the platform's own image URL in `src` — no local files, no base64 — so the brief stays a single self-contained file. Some platform URLs expire; that is accepted, with two rules making it safe:

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

When the brief should show the living post itself (playable video, live like counts) instead of a card: YouTube and Facebook embed via plain iframes; Instagram and Threads embed via a direct iframe with `/embed/` appended to the post URL (do **not** use blockquote+embed.js — its handshake fails on static pages); X, TikTok, Reddit, and Bluesky use their official script-processed blockquotes. Two hard rules:

- Instagram/Facebook iframes must carry `sandbox="allow-scripts allow-same-origin allow-popups"` — a login-walled or deleted post can otherwise frame-bust and navigate the whole brief away.
- Only public, still-live posts render; a deleted post leaves the embed blank with no fallback. Prefer cards when durability matters, or pair each embed with a card as backup.

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
└── example.html        ← reference markup for type scale, cards, buttons, swatches, example-post carousel, large cards
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
