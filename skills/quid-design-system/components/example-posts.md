# Example-post components

**Example-post components** — `.sc-carousel`, `.sc-card`, `.sc-thumb`, `.sc-thumb-ph`, `.sc-meta`, `.sc-who`, `.sc-handle`, `.sc-plat`, `.sc-quote`, `.sc-link`.

Use when a brief shows real social or news posts as evidence — top posts, example posts per theme, quote cards. The `.sc-*` styles ship inside `quid.css`, so inlining `quid.css` is all the setup needed; copy the markup shape from the "Example posts" section of `example.html`.

**Interchangeable with the caption-insight quote grid** (`.ci-quotes`, see `components/ranked-themes.md`): both present a theme's supporting posts, so you can swap this carousel for that grid (or vice versa) depending on whether images or quotes should lead. By default `.sc-card` links out to the post; add `data-modal` to open the shared **post-detail modal** instead (same drilldown the caption-insight cards use; see `components/post-detail-modal.md`).

Card contract (each card is one post):

```html
<a class="sc-card" href="{post URL}" target="_blank" rel="noopener">
  <div class="sc-thumb"><img src="{image URL}" loading="lazy" alt="" referrerpolicy="no-referrer"
    onerror="this.parentElement.classList.add('sc-thumb-ph'); this.parentElement.innerHTML='<span>{domain}</span>'"></div>
  <div class="sc-meta">
    <div class="sc-who"><span class="sc-handle">{@handle}</span> <span class="sc-plat">{platform}</span></div>
    <p class="sc-quote">"{the post's own text, verbatim}"</p>
    <span class="sc-link">View post ↗</span>
  </div>
</a>
```

Quotes are the post's real text — never paraphrase or invent. `.sc-plat` is the platform name only.

## Image policy: hotlink-only

Put the platform's own image URL in `src` — no local files, no base64 — so the brief stays one file with no sibling assets. Some platform URLs expire; that is accepted, with two rules making it safe:

1. **Every post `<img>` carries `referrerpolicy="no-referrer"` and the `onerror` handler** shown above. `no-referrer` is load-bearing: Instagram/Facebook/TikTok CDNs reject hotlinks that send a Referer header, and pass them without one. `onerror` makes an expired or dead image degrade to the domain gradient tile (`.sc-thumb-ph`) instead of a broken-image icon.
2. **A post with no image at all** (deleted, or the source exposes none) renders `.sc-thumb-ph` with its domain from the start. Never leave the slot empty and never substitute an unrelated image.

Where the image URL comes from — these are platform traits, not tool instructions, and none of them depends on any other skill existing:

| URL trait | Platforms (as of 2026) | What to do |
| --- | --- | --- |
| Stable public image CDN | YouTube (`i.ytimg.com/vi/{id}/hqdefault.jpg`), X media (`pbs.twimg.com`), Bluesky (`cdn.bsky.app`), many news CDNs (e.g. espncdn) | Hotlink; effectively durable |
| Signed, expiring URL | Instagram & Facebook `og:image` (fetch the post page server-side to read it), TikTok covers (oEmbed `thumbnail_url`) | Hotlink anyway; dies in days — rule 1 covers it |
| Blocked front door | Reddit (`www.reddit.com` pages and JSON API reject plain fetches; `old.reddit.com` still serves full HTML with `og:image` / `i.redd.it` links) | Use the alternate route |
| Nothing to fetch | Deleted posts; text-only posts | Rule 2: domain tile |

If the workspace has a data-collection skill for the platform, prefer its response over scraping — e.g. X search results typically already include media URLs — but the table above works without any of them.

**Prefer real images; a tile is a per-post last resort, not the plan for a whole carousel.** A report reads as more compelling and credible when its example posts show real images. Accepting that a URL may *expire later* (rule 1) is not the same as accepting a tile *now* — so before settling for a tile, put in the work to get a real image:

- **Resolve before you tile.** For every post without a ready image URL, try the route in the table above (`og:image` via a server-side page fetch; the platform's alternate route where its front door is blocked) before falling back. Some platforms won't yield an image to an unauthenticated fetch at all — that is expected, not a failure; those tile. Also skip images that aren't the post's own content: site logos and generic share/`og-default` banners, and permalinks that point at a comment/reply rather than the post itself. These skip patterns are examples, not an exhaustive list — the test is "is this the post's own image?"
- **A resolved URL isn't proven until it renders.** Server-side fetch success ≠ browser load success — some hosts return an `og:image` to a fetch but still reject the cross-origin `<img>` request even with `no-referrer`. So confirm each `<img>` actually loads in the rendered page (a programmatic check works in headless runs where no one is watching), and if it doesn't, backfill rather than trusting the resolved URL. The `onerror` tile in rule 1 is the safety net; this check is what keeps a working image from being downgraded to a tile unnecessarily.
- **Backfill from your candidate pool, don't settle.** The 2–3 posts you show per group are *chosen*, not fixed. If a given post can't produce a real image (never resolved, or resolved-but-won't-load), swap in another relevant post that can. This works best when you pick from the full set of source records for that group rather than a short pre-picked shortlist, which rarely has enough candidates to find image-bearing ones. Reach for the fuller pool as soon as the ask is "more / better / image-bearing example posts."

(Platform-specific behaviours — which hosts block unauthenticated fetches, which need an alternate route — change over time; treat the table above as current best-practice pointers, not fixed rules, and re-check if one stops working.)
