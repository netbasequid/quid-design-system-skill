# Social embeds (native)

**Social embeds (native)** — `.embed-grid`, `.embed-tile`, `.embed-plat`, `.dot`, `.embed-body`, `.yt`, `.embed-note` — chrome for the platforms' own embed snippets (iframe or script blockquote), one tile per platform.

Use when the brief should show the living post itself — playable video, live like counts, the real thread — instead of a styled card. Each tile wraps **the platform's own embed snippet** in Quid chrome; the design system owns only the tile (`.embed-tile` label + body over `var(--card)`/`var(--border)`/`var(--radius)`), never the embedded content. Cards (`components/example-posts.md`, `components/large-cards.md`) are the durable default; reach for native embeds when liveness is the point.

Grid contract (one `.embed-tile` per platform):

```html
<div class="embed-grid">
  <div class="embed-tile">
    <div class="embed-plat"><span class="dot" style="background:{platform color}"></span>{Platform}</div>
    <div class="embed-body">{the platform's native embed snippet}</div>
  </div>
  <!-- …one tile per platform… -->
</div>
<p class="embed-note">{one-line note on what renders live vs. what needs a real post ID}</p>
```

The tile chrome is identical across platforms; only the `.embed-body` payload differs. Pick the payload by platform trait — **how that platform embeds**, not which tool fetched the post:

| Embed method | Platforms (as of 2026) | `.embed-body` payload | Extra setup |
| --- | --- | --- | --- |
| Plain iframe | YouTube | `<div class="yt"><iframe src="https://www.youtube.com/embed/{id}" … allowfullscreen loading="lazy"></iframe></div>` (the `.yt` wrapper gives a responsive 16:9 box) | none |
| Plain iframe | Facebook | `<iframe src="https://www.facebook.com/plugins/post.php?href={URL-encoded post URL}&show_text=true&width=300" … loading="lazy"></iframe>` | none |
| Direct `/embed/` iframe | Instagram, Threads | `<iframe src="{post URL}/embed/" width="100%" height="560" frameborder="0" scrolling="no" allowtransparency="true" loading="lazy"></iframe>` (Threads uses `/embed`, no trailing slash) | none — do **not** use blockquote+embed.js |
| Script-processed blockquote | X / Twitter | `<blockquote class="twitter-tweet"><a href="{tweet URL}"></a></blockquote>` | `platform.twitter.com/widgets.js` |
| Script-processed blockquote | TikTok | `<blockquote class="tiktok-embed" cite="{video URL}" data-video-id="{id}"><section></section></blockquote>` | `www.tiktok.com/embed.js` |
| Script-processed blockquote | Reddit | `<blockquote class="reddit-embed-bq" style="height:500px" data-embed-height="500"><a href="{post URL}">{title}</a></blockquote>` | `embed.reddit.com/widgets.js` |
| Script-processed blockquote | Bluesky | `<blockquote class="bluesky-embed" data-bluesky-uri="{at:// URI}" data-bluesky-cid="{CID}"></blockquote>` | `embed.bsky.app/static/embed.js` |

Rules the markup can't show:

- **Instagram/Threads use the direct `/embed/` iframe, never blockquote+embed.js.** The blockquote path needs a `postMessage` handshake with the parent page that never completes on a static, script-less brief, so the embed stays blank. Appending `/embed/` to the post URL is the path that renders.
- **Script-processed platforms need their widget script loaded once per page** (the four `<script async>` tags above, near `</body>`). Add `window.twttr.widgets.load()` on `window.load` so late-injected `.twitter-tweet` nodes rehydrate. In a single-file brief for `push-brief`, these scripts run only when the file is viewed over http — never `file://`.
- **Sandbox the cross-origin iframes.** Instagram/Facebook/Threads iframes should carry `sandbox="allow-scripts allow-same-origin allow-popups"` — a login-walled or deleted post can otherwise frame-bust and navigate the whole brief away.
- **Only public, still-live posts render; there is no fallback.** A deleted or private post leaves the tile blank. When durability matters, use a card (`components/example-posts.md` / `components/large-cards.md`) instead, or pair each embed with a card as backup.
- `.embed-plat` is the platform name plus a brand-colored `.dot`; keep the label to the platform only. `.embed-note` is an optional caption under the grid.

Reference markup with one tile per embed method: the "Social embeds (native)" section of `example.html` (with the required `<script>` tags near `</body>`).
