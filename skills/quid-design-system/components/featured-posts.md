# Featured posts

**Featured posts** — `.posts-featured`, `.post`, `.post-thumb`, `.post-rank`, `.post-body`, `.post-author` (`.handle` / `.src`), `.post-text`, `.post-foot` (`.stat`) — 2-up rich cards for standout posts.

A 2-up grid of rich cards for a handful of standout posts — bigger than the `.sc-carousel` tiles, with a thumbnail, author, a few lines of text, and a footer. Use it for "top posts of the week" / a few flagship posts; use `.sc-carousel` when the point is *many* posts to scan.

```html
<h3 class="sub-head">Featured posts <span class="count">6</span></h3>
<div class="posts-featured">
  <article class="post">
    <div class="post-thumb"><span class="post-rank">1</span><!-- optional <img> --></div>
    <div class="post-body">
      <div class="post-author"><span class="handle">@espn</span><span class="src">Instagram</span></div>
      <p class="post-text">{the post's own text, verbatim}</p>
      <div class="post-foot"><span class="stat"><b>184K</b> likes</span><span class="stat"><b>3.2K</b> comments</span></div>
    </div>
  </article>
  <!-- …one <article class="post"> per featured post… -->
</div>
```

Rules the markup can't show:

- **`.post-text` is the post's own text, verbatim** (it clamps to 3 lines). `.handle` is the author/handle as shown; `.src` is the platform name only.
- **`.post-rank` is optional** — a small badge pinned inside `.post-thumb` (so the thumb is present even as a gray placeholder). Put a real coverage `<img>` in `.post-thumb` when you have one (same hotlink/`no-referrer` rules as example-post cards), else leave it as the gray box.
- **`.post-foot` is engagement stats *or* a category tag — not invented numbers.** Use `.stat` (`<b>{n}</b> likes`) **only** when the counts come verbatim from the data source; otherwise use a `.tag-*` badge (category/sentiment) and omit stats. Never estimate engagement.
- **Cards are static by default.** To make a card open the post-detail modal, add `tabindex="0" role="button" data-url="{url}"` and wire the modal (see `components/post-detail-modal.md`) — the CSS styles both the same.

Reference markup (two real featured posts): the "Featured posts" section of `example.html`.
