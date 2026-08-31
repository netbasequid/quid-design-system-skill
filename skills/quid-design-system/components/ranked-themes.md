# Ranked themes

**Ranked theme — with quotes** — `.theme-list`, `.theme-card`, `.theme-head`, `.theme-rank`, `.theme-name`, `.theme-metrics` / `.theme-metric` (`.up` / `.down`), `.theme-desc`, `.theme-quote` / `.q-src`, `.theme-examples-label` (uses the shared `.tag` badge). Boxless ranked list with inline verbatim quotes.
**Ranked theme — with media** — `.theme-card.with-media` + `.theme-text` / `.theme-thumb` / `.theme-cols` (extends the ranked-theme base; composes `.sc-carousel`) — text left, thumbnail right, carousel below.
**Ranked theme — caption-insight** — `.ci-list`, `.ci-card`, `.ci-num`, `.ci-body`, `.ci-head`, `.ci-name`, `.ci-text`, `.ci-quotes`, `.ci-quote` / `.cq-handle` / `.cq-text` / `.cq-more`. A third presentation option for ranked themes (alongside with-quotes and with-media): ghost number + caption read + quote cards that open the shared **post-detail modal**.

## Ranked themes — choosing a presentation

Ranked themes have **three interchangeable presentations** — same ordered set of themes, different emphasis. Pick one per section:

- **With quotes** (below) — rank + badge + metrics + description + inline verbatim pull-quotes. The default; best when the *quotes themselves* are the evidence.
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
- **The badge is a shared `.tag`** (see `components/tags-badges.md`) — pick the variant by meaning; one badge per theme.
- **Metrics are flexible slots** (`.theme-metric` with a bold `<b>` value). Use whatever you actually have — Mentions, Authors, Share, YoY. Wrap a trend figure in `.up` (green) or `.down` (red); **only show a trend you can source** — omit it for a snapshot with no prior-window baseline (don't invent a YoY).
- **Boxless is the point** — don't wrap `.theme-card`s in `.quid-card`/`.section` boxes each; the hairline divider between items carries the ranking. The whole `.theme-list` goes inside one `.section`.
- `.theme-examples-label` ("Example posts") is an optional lead-in when you follow the quotes with an example-post carousel.

Reference markup (three ranked themes with real verbatim quotes + source links): the "Ranked theme — with quotes" section of `example.html`.

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
      <div class="sc-carousel"><!-- .sc-card items (see `components/example-posts.md`) --></div>
    </div>
  </div>
</div>
```

Rules the markup can't show:

- **Three regions, fixed grid**: `.theme-text` (left), `.theme-thumb` (top-right, 200×140 → full-width under 760px), `.theme-cols` (carousel, full width). Keep that order; the grid areas place them.
- **`.theme-thumb` is the image *element*, not a wrapper** — for a real theme image use `<img class="theme-thumb" src="…" referrerpolicy="no-referrer">`; it fills the 200×140 box via `object-fit: cover`. When the theme has no image, use an empty `<div class="theme-thumb"></div>` — that renders the gray `--muted` box (a deliberate placeholder, not a missing asset). Use a real coverage image for the theme (same sourcing as example posts); never stretch an unrelated stock image.
- **The carousel is the standard `.sc-carousel`** — same `.sc-card` contract and image rules as `components/example-posts.md` (verbatim quotes, `referrerpolicy="no-referrer"`, domain-tile fallback).
- Everything from the base ranked theme still holds (verbatim quotes, `.tag` badge, sourced trend only, boxless hairline between items).

Reference markup (two real themes with example-post carousels): the "Ranked theme — with media" section of `example.html`.

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
- **Each `.ci-quote` opens the post-detail modal** — it needs `tabindex="0" role="button"` and a `data-url`, plus an inline `<script type="application/json" class="post-data">` blob for the modal to read (falls back to `.cq-handle`/`.cq-text` if the blob is absent). See `components/post-detail-modal.md` — the modal singleton + its script must be present once in the brief for clicks to do anything.
- The badge is the shared `.tag`; one per theme (optional). Ghost number is decorative (`--border`-colored) — keep the list short so the numbers stay meaningful.

Reference markup (two real Taiwan themes with clickable quotes): the "Caption-insight themes" section of `example.html`.
