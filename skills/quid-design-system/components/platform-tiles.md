# Platform source tiles

**Platform source tile** — `.pt-logo` + `data-plat="…"`, plus the `--pt-ink` and
`--pt-mark` custom properties it sets. The branded square a post card shows when
it has no image.

Drop one inside any `.post-thumb` (featured posts) or `.sc-thumb` (example-post
carousel). It fills the slot and paints the source platform's mark on that
platform's brand colour.

```html
<div class="post-thumb">
  <span class="pt-logo" data-plat="reddit" aria-hidden="true"></span>
</div>
```

That is the whole contract. **The span is empty** — the mark is a CSS mask, not
an `<svg>`, so there is no sprite to paste into the brief and nothing to forget.

## Put it under every card, not only the image-less ones

```html
<div class="post-thumb">
  <span class="pt-logo" data-plat="instagram" aria-hidden="true"></span>
  <img src="{image}" loading="lazy" alt="" referrerpolicy="no-referrer"
       onerror="this.remove()">
</div>
```

The tile is the layer underneath; the image covers it. Social CDN URLs expire —
Instagram and Threads links die within days — so `onerror` reveals a branded
chip instead of leaving a hole in a brief someone opens next month. **This is
the main reason the component exists**, and it is the easy half to leave out.

`referrerpolicy="no-referrer"` stays load-bearing: Instagram, Facebook and
TikTok CDNs reject hotlinks that send a Referer and serve them without one.

## Supported `data-plat` values

`facebook` · `instagram` · `x` · `threads` · `tiktok` · `youtube` · `linkedin` ·
`reddit` · `pinterest` · `snapchat` · `twitch` · `tumblr` · `bluesky` ·
`discord` · `telegram` · `whatsapp` · `vimeo` · `podcast` · `news`

Anything else, including a missing `data-plat`, falls back to a globe on
`#1A1A1A` rather than breaking the layout.

Rules the markup can't show:

- **The colours are raw hex, deliberately.** Every other component here
  references semantic tokens. These cannot: they identify an external brand,
  exactly as the mark does. Do not "fix" them to Quid tokens.
- **Two of the nineteen are not brands.** `podcast` and `news` have no brand
  colour, so theirs are assigned, not official. For podcasts the convention is
  RSS orange (`#F26522`), but a podcast tile and a Reddit tile sit adjacent in a
  2-up grid and two oranges read as a matched pair, so this ships purple.
- **Snapchat inverts the mark.** `#FFFC00` against white is 1.1:1, so the ghost
  would be invisible; it is the one platform setting `--pt-ink: #000000`. Any
  light brand colour added later needs the same treatment — check it rather
  than assuming white works.
- **`aria-hidden="true"`.** The tile is decoration; the platform is already
  named in `.post-author .src`, so announcing it twice is noise.
- **Adding a platform is two values**, both on one rule: a `background` and a
  `--pt-mark` data URI. Marks are [Simple Icons](https://simpleicons.org)
  path data (CC0). They have not been taken from each company's own brand kit,
  so check that platform's guidelines before using one at large size.

## Why a mask and not an `<svg>` sprite

A sprite costs about the same bytes, but it has to be pasted into every brief
and a `<use href="#plat-x">` with no matching `<symbol>` renders **nothing, with
no error**. The mask cannot fail that way: the CSS either reached the page or
the whole stylesheet is missing.

The trade is roughly 16KB added to `quid.css` for consumers that never show a
post card.

Reference: the "Platform source tiles" section of `example.html`.
