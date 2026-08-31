# Large cards (creative in the wild)

**Large cards (creative in the wild)** — `.large-cards`, `.large-card`, `.lc-media`, `.lc-thumb`, `.lc-logo`, `.lc-play`, `.lc-meta`, `.lc-head`, `.lc-author`, `.lc-src`, `.lc-text`, `.lc-stats`.

Use when a brief showcases a handful of hero posts — campaign creatives spotted in the wild, top posts of the week, one flagship post per theme. Cards sit in a responsive 3-up grid (2-up under 900px, 1-up under 560px) with a square image on top, and the **whole card** is the click target. Prefer the `.sc-carousel` (see `components/example-posts.md`) when the point is *many* evidence posts to scan; prefer `.large-cards` when the point is a *few* posts worth a big visual.

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
- **Image sourcing is identical to the example-post carousel** — hotlink-only, `referrerpolicy="no-referrer"` mandatory, per-platform URL traits and expiry rules in the "Image policy: hotlink-only" table in `components/example-posts.md`.
- `.lc-play` marks video posts (TikTok, YouTube, Reels) — omit it on image posts. `.lc-logo` is the platform (or channel) logo overlay; copy a logo SVG from `example.html` rather than sourcing new artwork. Both are optional; a plain image card is just `.lc-media` + `.lc-thumb`.
- `.lc-text` is the post's own text verbatim (it line-clamps at 2 lines); `.lc-author` is the display name or handle as the platform shows it; `.lc-src` is the platform name only.
- `.lc-stats` (`<div class="lc-stats"><span><b>{n}</b> likes</span>…</div>`, last child of `.lc-meta`) exists for engagement counts. Include it only when the numbers come verbatim from the data source for that post — never estimate or invent; omit the row entirely otherwise.
- In a brief that has a post-detail modal, replace the anchor with `<div class="large-card" tabindex="0" role="button" data-url="{post URL}">` and let the modal's opener read `data-url` — the CSS styles both shapes identically.

Reference markup with one real card per media pattern: the "Large cards (creative in the wild)" section of `example.html`.

## Live embeds (optional upgrade)

When the brief should show the *living* post itself (playable video, live like counts) instead of a card, use the **Social embeds (native)** component (`components/social-embeds.md`). Prefer cards when durability matters (a deleted post leaves an embed blank with no fallback), or pair each embed with a card as backup.
