# Tags / badges

**Tags / badges** — `.tag` + `.tag-opportunity` / `-risk` / `-trend` / `-signal` / `-watch` / `-neutral` — colored pill labels.

Small colored pill labels for tagging a theme, post, or insight with a category. Six semantic variants, each an intent-colored fill:

```html
<span class="tag tag-opportunity">Opportunity</span>   <!-- blue -->
<span class="tag tag-risk">Risk</span>                 <!-- red -->
<span class="tag tag-trend">Trend</span>               <!-- purple -->
<span class="tag tag-signal">Signal</span>             <!-- green -->
<span class="tag tag-watch">Watch</span>               <!-- orange -->
<span class="tag tag-neutral">Neutral</span>           <!-- gray -->
```

Rules the markup can't show:

- **Pick the variant by meaning, not by color** — `opportunity`/`signal` read positive, `risk`/`watch` read cautionary, `trend` is neutral-notable, `neutral` is unweighted. The colors come from the ramp tokens; don't restyle with raw hex.
- **`.tag` is the base class** — always pair it with exactly one `.tag-*` variant. Keep the label short (1–2 words).
- Distinct from `.quid-badge` (a plain gray count/meta chip); reach for `.tag-*` when the label carries a category or sentiment.

Reference markup (all six variants): the "Tags / badges" section of `example.html`.
