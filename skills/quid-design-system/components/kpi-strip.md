# KPI strip

**KPI strip** — `.kpi-grid`, `.kpi-card`, `.kpi-card .label` / `.value` / `.delta` (`.up` / `.down`) / `.period` / `.kpi-note`, plus per-metric tint classes `.kpi-card--volume` / `--mentions` / `--authors` / `--engagement` / `--reach` / `--sentiment` / `--positives` / `--negatives` / `--passion` / `--score` / `--video` (each sets `--kpi-tint` to a `--chart-*` token) — optional metric cards, colored by metric.

Optional summary metrics that sit above the slot (inside `.container-brief`, or inside any `.section`). Center-aligned cards with a light per-metric gradient fill: a bold `.label` over a big `.value`, with an optional directional `.delta` and an optional `.kpi-note` sub-metric. Auto-fits 3–4 cards; omit it when a brief has no headline numbers.

Contract (one `.kpi-card` per metric):

```html
<div class="kpi-grid">
  <div class="kpi-card kpi-card--{metric}">
    <div class="label">{Metric name}</div>
    <div class="value">{Number}</div>
    <div class="delta up">+31% <span class="period">vs last month</span></div>
    <div class="kpi-note"><b>{sub-value}</b> {sub-metric}</div>   <!-- optional; usually omitted -->
  </div>
  <!-- …3–4 cards… -->
</div>
```

## Metric → color standard (color by metric, not by hue)

A KPI card is colored by **which metric it shows** — the same metric always gets the same color across every brief. Add a **metric-semantic class**; each sets one custom property, `--kpi-tint`, to a design-system chart token. `--kpi-tint` drives *both* the gradient fill and the label color (the label auto-darkens from the tint, so any token stays legible). Never re-pick a color per brief.

| Metric (and synonyms) | Class | Chart token | Color |
|---|---|---|---|
| Posts / volume | `kpi-card--volume` | `--chart-1` | blue |
| Mentions (2nd volume metric; co-occurs with Posts) | `kpi-card--mentions` | `--chart-9` | berry |
| Active authors / unique voices | `kpi-card--authors` | `--chart-4` | teal |
| Engagements / interactions | `kpi-card--engagement` | `--chart-7` | orange |
| Potential impressions / reach | `kpi-card--reach` | `--chart-14` | grey |
| Net sentiment | `kpi-card--sentiment` | `--chart-2` | purple |
| Positives / positive mentions | `kpi-card--positives` | `--chart-6` | green |
| Negatives / negative mentions | `kpi-card--negatives` | `--chart-11` | red |
| Passion Intensity / emotional intensity | `kpi-card--passion` | `--chart-13` | violet |
| Trend Score / momentum | `kpi-card--score` | `--chart-5` | amber |
| Video / media volume | `kpi-card--video` | `--chart-3` | magenta |

Rules the markup can't show:

- **Color by metric.** Pick the class by what the number *is*, not by position or by taste. Mentions and Posts are both volume: when only one appears use `--volume` (blue); when both appear, keep Posts on `--volume` and put Mentions on `--mentions` (berry) — a low fill tint blurs two blues together, so Mentions takes a distinct hue to stay legibly separate.
- **Off-standard metric** → set the tint inline with the next unused chart token (`style="--kpi-tint: var(--chart-9)"`) rather than inventing a raw hex; a bare `.kpi-card` with no metric class falls back to `--primary`.
- **Label first, value second** — the eyebrow-style `.label` sits *above* the big `.value`; don't invert them.
- **`.delta` is optional and directional** — `.up` renders a green ▲, `.down` a red ▼ (the arrow is a `::before`, so put only the number in the text). The `.period` span is the comparison window ("vs last month"), muted and inline.
- **Only show a delta you can source.** A delta implies a real prior-window comparison — omit the `.delta` row entirely for a snapshot metric with no baseline (a value-only card is valid). Never invent a percentage.
- **`.kpi-note` is optional and usually omitted** — a sub-metric line (e.g. "1.2M comments · 2% of engagements"); include only when the brief calls for it.
- Use **3 or 4 cards** per row; the grid auto-fits and wraps below ~160px per card (the full metric set wraps to multiple rows).

Reference markup: the "KPI strip" and "KPI strip — full metric set (Monitor Summary)" sections of `example.html`.
