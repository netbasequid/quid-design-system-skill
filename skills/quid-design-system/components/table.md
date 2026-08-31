# Table

**Table** — `.table-wrap` (+ `.clickable`) wrapping a `<table>`; `.num` right-aligns numeric cells.

For metrics and comparisons. Wrap a plain `<table>` in `.table-wrap` (which supplies the surface, top/bottom rules, and header styling):

```html
<div class="table-wrap">
  <table>
    <thead><tr><th>Layer</th><th class="num">Posts</th><th class="num">Net</th></tr></thead>
    <tbody>
      <tr><td>UGC</td><td class="num">303K</td><td class="num">+72</td></tr>
    </tbody>
  </table>
</div>
```

Rules the markup can't show:

- **`.num` on every numeric cell** — both the `<th>` and the `<td>` — right-aligns and turns on tabular figures so columns line up. Text cells stay left-aligned.
- **No row hover by default.** Add `class="clickable"` to `.table-wrap` only when rows are actually interactive (then wire the click yourself); otherwise leave it off so a static table doesn't imply clickability.
- Keep it a real `<table>` (thead/tbody) for semantics — don't fake rows with divs.

Reference markup (a real platform breakdown): the "Table" section of `example.html`.
