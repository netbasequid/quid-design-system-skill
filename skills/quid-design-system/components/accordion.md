# Accordion

**Accordion** — `.accordion` wrapping native `<details>` / `<summary>` (+ `.acc-meta`, `.acc-body`) — expandable stacked rows.

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
