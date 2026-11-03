# Chart card

**Chart card** — `.chart-grid`, `.chart-card`, `.chart-title`, `.chart-sub`, `.chart-box`.

A boxed container for a **plotted figure**: a chart, a graph, a wordcloud — anything with a plot area, axis labels or a legend. Pair with `.chart-grid` for a responsive row of them.

This is **the one surface that keeps its box in the modern shell.** Sections there are boxless and the tinted page canvas is switched off, which is right for prose: the eyebrow, the heading and the whitespace do the separating. A plotted figure has no such structure. Dropped loose on the page its axis labels and legend run straight into the surrounding copy with nothing marking where the figure stops and the argument resumes. The card supplies that edge.

## Not for tables

A table is not a plotted figure and does not go in a `.chart-card`. Use `.table-wrap` (see `components/table.md`), which is deliberately a different treatment: a top and bottom hairline, no side borders, no radius, no shadow.

The reason is that a table already carries its own structure. Its header row, its rules between rows and its aligned columns do the work a card border would otherwise have to do, so boxing it adds a second boundary around something that is already bounded. A chart has none of that — the plot area bleeds into whatever surrounds it — which is exactly why it needs the card and the table does not.

If a brief shows a chart and a table in the same section, the difference in treatment is intentional and should not be "tidied up" into matching containers.

Contract:

```html
<div class="chart-grid">
  <div class="chart-card">
    <h3 class="quid-h3 chart-title">{Chart title}</h3>
    <p class="chart-sub">{One line on what the reader is looking at.}</p>
    <div class="chart-box"><canvas id="{unique-id}"></canvas></div>
  </div>
  <!-- …more cards; the grid drops to one column under 280px per track… -->
</div>
```

Rules the markup can't show:

- **Colors are not set here.** This component is chrome only. Series colors come from the `--chart-*` and `--sentiment-*` tokens, read at runtime — see `components/chart-palette.md`. Never paste hex into chart config; it breaks dark mode and per-client overrides.
- **`.chart-box` is load-bearing.** Chart.js sizes a canvas against its nearest positioned parent. Without a wrapper of fixed height the canvas grows on every resize event, a few pixels at a time, until the page is unusable. Height is a plain `260px`, so override it inline on a chart that needs more room rather than editing the class.
- **The title is an `<h3 class="quid-h3 chart-title">`.** The element keeps the document outline correct under the section's `<h2>`; `.chart-title` only zeroes the margin. A `<div>` styled at heading size would render in the body font — size and family are separate tokens (see the heading binding in `quid-fonts.css`).
- **The border is not optional.** In dark mode `--card` and `--background` are both `#212121`, so the fill disappears and the 1px border carries the whole boundary. Dropping it for a "cleaner" look leaves the card invisible on half the themes.
- **Same four declarations as `.quid-card`**, deliberately. This is not a second card style; if the card treatment changes, both should change together.
- **No chart library ships with the design system.** The catalog renders its demo with Chart.js from a CDN to prove the chrome works, and takes no position on what a brief uses. A wordcloud is usually an `<svg>` or a `<canvas>` from a different library; it goes in the same `.chart-box` and gets the same card.

Reference markup: the "Chart card" section of `example.html`, and the same component inside the modern shell in `example-modern.html`.
