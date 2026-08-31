# Methodology

**Methodology** — `.methodology` — a small muted block for a brief's sources / window / caveats; an optional standalone component (not part of the shell).

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
