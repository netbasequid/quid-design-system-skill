# Methodology

**Methodology** — `details.methodology` (`data-methodology`) + `summary` + `.methodology-body` — the standard closing disclosure every client brief ends with: collapsed by default, caption-scale muted type, plain client language.

Every client-facing brief carries **exactly one** Methodology section, and it is the **last thing in `.brief-body`** (below the final content section, above any footer). It tells the reader where the conversation came from, what window it covers, what the numbers count, and what to be careful about. Nothing more. The full internal record (topic IDs, queries, requests, skills) belongs in the session's methodology report, never in the brief.

```html
<details class="methodology" data-methodology>
  <summary>Methodology</summary>
  <div class="methodology-body">
    <ul>
      <li><b>Source.</b> {Where the conversation came from, in reader terms: language, platforms.}</li>
      <li><b>Scope.</b> {What was included, described in words, never as a query.}</li>
      <li><b>Time frame.</b> {Dates written out; flag any partial period.}</li>
      <li><b>How it's measured.</b> {What each headline figure counts.}</li>
      <li><b>Example posts.</b> {How posts and quotes were chosen.}</li>
      <li><b>Notes.</b> {Caveats a client needs to read the figures correctly.}</li>
    </ul>
  </div>
</details>
```

Rules the markup can't show:

- **Hidden by default.** Native `<details>` with **no `open` attribute**; no JavaScript. The reader sees one quiet line with a dropdown arrow.
- **Smaller and quieter than the brief.** The summary is `--font-size-13`, the notes `--font-size-12`, both `--muted-foreground`: a full tier below the 15px prose. Don't wrap it in a `.section` card, a callout, or a colored heading.
- **Never in the side-nav rail.** It gets no `id` link in `.sidenav`; it is a footnote, not a section.
- **One per brief.** Replace any other methodology paragraph, footer note, or "topic definition" disclosure. Keep the label **Methodology** unless the user asks for another, such as "About This Data."
- **Three to six bullets, one or two sentences each**, in the order above; skip any bullet with nothing to say.
- **Client language only.** No topic, analysis, dashboard, or theme IDs; no boolean or query text; no product, API, or skill names (Monitor, Aesop, Terminal, …); no metric enums (`TOTAL_POSTS`); no "we analyzed." Caveats may be reworded but never dropped or softened.

The copy rules (the "never show" list, the internal-to-client translation table) and the leak checker live in the **`brief-methodology-section`** Shared Expertise skill. Use it whenever you write or revise this section's content; this doc owns the markup and look.

Reference markup: the "Methodology" section of `example.html`, and the end of the slot in `shell-example.html`.
