# Insight / callout

**Insight / callout** — `.insight-box` (+ `.accent-2` / `.accent-3` / `.warn` / `.neg`) for a single bordered takeaway; `.insight-grid` / `.insight-card` (+ `h4`) for a 2-up set of small takeaways. Uses the shared `.tag` badge.

A bordered callout that spotlights a **single takeaway** — a colored left rule keyed to sentiment, an optional `.tag` above, and one or two short lines. Use it to punctuate a section with the "so what," not to hold body content.

```html
<div class="insight-box neg">
  <span class="tag tag-risk">Risk</span>
  <p><strong>{Headline.}</strong> {One or two sentences.}</p>
</div>
```

For a set of small paired takeaways, use the 2-up grid:

```html
<div class="insight-grid">
  <div class="insight-card"><span class="tag tag-trend">Trend</span><h4>{Short title}</h4><p>{One line.}</p></div>
  <div class="insight-card"><span class="tag tag-opportunity">Opportunity</span><h4>{Short title}</h4><p>{One line.}</p></div>
</div>
```

Rules the markup can't show:

- **The left rule is keyed to meaning** — default (blue `--primary`), `.accent-2` (purple), `.accent-3` (green, positive/signal), `.warn` (orange, caution), `.neg` (red, risk/negative). Pair the accent with a matching `.tag` variant, not a clashing one.
- **Keep it short.** `.insight-box` is a callout, not a section — a bold lead-in plus a sentence or two. Reach for a `.section` + `.prose` when there's more to say.
- **The `.tag` is optional** (see `components/tags-badges.md`); the `.insight-grid` collapses to one column under 760px.

Reference markup (all box variants + the 2-up grid): the "Insight / callout" section of `example.html`.
