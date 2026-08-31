# Chart palette & convention

**Chart palette & convention** — series-color tokens `--chart-1…14` (categorical), `--sentiment-positive` / `-neutral` / `-negative`, `--citrus-1…6` (wordcloud). Read by charts via `getComputedStyle`.

Series colors for charts are **tokens**, not hard-coded hex — so a chart re-themes with the rest of the design system and a client override is a token swap.

- **Categorical** (bars, lines, pies, multi-series): cycle `--chart-1` … `--chart-14` in order. Fourteen hues chosen to stay distinct; don't repeat before you've used them.
- **Sentiment**: `--sentiment-positive` (green), `--sentiment-neutral` (gray), `--sentiment-negative` (red). Use these — not the categorical ramp — whenever the dimension is sentiment.
- **Wordcloud / density**: the Citrus set `--citrus-1` … `--citrus-6`.
- **Axes & labels**: grid lines use `--border`; tick/legend labels use `--muted-foreground`.

Charts (e.g. Chart.js) should read these at runtime via `getComputedStyle(document.documentElement).getPropertyValue('--chart-1')` rather than pasting hex, so dark mode and per-client overrides flow through. Any chart type works inside a `.chart-card`.

Reference swatches (all three sets): the "Chart palette & convention" section of `example.html`.
