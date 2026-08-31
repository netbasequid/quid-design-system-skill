# Post-detail modal

**Post-detail modal** — `.post-modal-overlay` / `.post-modal` / `.post-modal-head` / `.post-modal-body` / `.pm-media` / `.pm-tabs` / `.pm-tab` / `.pm-panel` / `.pm-section` / `.pm-highlights` / `.pm-caption` / `.post-modal-foot`. A shared page singleton (markup + JS go in the brief once) opened by `.ci-quote`, `.post`, `.post-tile`, `.large-card`, and example-post `.sc-card[data-modal]`.

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
