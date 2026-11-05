#!/usr/bin/env python3
"""
Compile Figma DTCG-style tokens into a single Quid stylesheet.

Inputs (in ./tokens/):
  base-colors.tokens.json           — full color ramps (Red, Orange, ..., Gray, etc.)
  primitives.tokens.json            — radius, opacity state
  system-colors-light.tokens.json   — semantic shadcn tokens (light)
  system-colors-dark.tokens.json    — semantic shadcn tokens (dark)
  shadow-colors-light.tokens.json   — shadow alpha values (light)
  shadow-colors-dark.tokens.json    — shadow alpha values (dark)
  typography-desktop.tokens.json    — sizes, line-heights, weights (desktop)
  typography-mobile.tokens.json     — sizes, line-heights, weights (mobile)

Output:
  quid.css — single stylesheet exposing every token as a CSS custom property,
             plus base typography rules and a small set of utility classes
             aligned with shadcn/ui conventions.

Run:
  python3 build_tokens.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parent
TOKENS = ROOT / "tokens"
OUT = ROOT / "quid.css"


def load(name: str) -> dict:
    return json.loads((TOKENS / name).read_text())


def is_token(node: dict) -> bool:
    return isinstance(node, dict) and "$type" in node and "$value" in node


def walk(node: dict, prefix: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], dict]]:
    """Yield (path, token) for every leaf token in a Figma DTCG tree."""
    out: list[tuple[tuple[str, ...], dict]] = []
    for key, value in node.items():
        if key.startswith("$"):
            continue
        if is_token(value):
            out.append((prefix + (key,), value))
        elif isinstance(value, dict):
            out.extend(walk(value, prefix + (key,)))
    return out


def _clean(part: str) -> str:
    """Lowercase a path part into something valid in a CSS custom-property name.

    Collapses every run of non-alphanumerics to a single hyphen, so group names
    carrying punctuation survive being used as a qualifier. `radius(open-source)`
    has to become `radius-open-source`: the parentheses were harmless while the
    group name was always dropped, but they produce an unparseable property the
    moment a collision forces the group into the name.
    """
    import re as _re
    return _re.sub(r"[^a-z0-9]+", "-", part.lower()).strip("-")


def slug(parts: tuple[str, ...]) -> str:
    """Join path parts into a CSS-safe slug, collapsing redundant repeats.

    e.g. ('font-size','font-size-14') -> 'font-size-14'
         ('Red','500')                -> 'red-500'
         ('hover:primary',)           -> 'hover-primary'
    """
    cleaned = [_clean(p) for p in parts]
    out: list[str] = []
    for piece in cleaned:
        if out and (piece == out[-1] or piece.startswith(out[-1] + "-")):
            out[-1] = piece
        else:
            out.append(piece)
    return "-".join(out)


def hex_with_alpha(token_value: dict) -> str:
    """Return #rrggbb or rgba(...) depending on alpha."""
    alpha = token_value.get("alpha", 1)
    hex_ = token_value["hex"]
    if abs(alpha - 1) < 1e-3:
        return hex_
    r, g, b = (int(hex_[i : i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r}, {g}, {b}, {round(alpha, 3)})"


def resolve_alias(ref: str) -> str:
    """Convert a Figma alias like '{sidebar.primary}' into 'var(--sidebar-primary)'."""
    inner = ref.strip().strip("{}")
    inner = inner.replace(".", "-").replace(":", "-").replace(" ", "-").lower()
    return f"var(--{inner})"


def is_alias(value) -> bool:
    """True for a DTCG brace reference like '{font-family.font-display}'."""
    return isinstance(value, str) and value.strip().startswith("{") and value.strip().endswith("}")


def alias_leaf(ref: str) -> str:
    """Last segment of a brace alias: '{font-family.font-display}' -> 'font-display'.

    The emitters below name a token by its LEAF, not its full path, so an alias
    has to be resolved the same way or it would point at a variable that is
    never declared.
    """
    return _clean(ref.strip().strip("{}").split(".")[-1])


def assign_names(entries: list[tuple[str, str]]) -> tuple[dict[int, str], list[str]]:
    """Give every (group, leaf) a unique CSS custom-property name.

    WHY THIS EXISTS. Tokens are emitted under their LEAF name, so two different
    Figma groups holding the same leaf collapse onto one custom property. The
    typography collection does exactly that: `font-family/font-size-h1` and
    `font-size/font-size-h1` both want `--font-size-h1`, and `font-headings`
    exists in both `font-family` and `font-weight`.

    Today the duplicate is resolved by EMIT ORDER — the later declaration wins,
    and it happens to be the one callers want. Nothing enforces that. Reorder
    the groups and every heading silently loses its weight, with no error and
    no visibly broken output until someone looks at a rendered brief.

    This makes the outcome explicit instead of incidental:

      * the winner keeps the canonical name, chosen as the entry whose leaf
        already carries its own group prefix (`font-size/font-size-h1`), since
        that is the token the name is actually describing;
      * if no entry qualifies (`font-headings` sits in two groups and matches
        neither), the LAST one wins — preserving exactly what emit order does
        today, so this change cannot alter a resolved value;
      * every loser is renamed to `<group>-<leaf>`, which keeps its declaration
        valid and reachable rather than letting it be silently overwritten.

    Returns the index->name map and a list of human-readable collision notes.
    """
    canonical = [f"{_clean(leaf)}" for _group, leaf in entries]
    seen: dict[str, list[int]] = {}
    for i, name in enumerate(canonical):
        seen.setdefault(name, []).append(i)

    names: dict[int, str] = {}
    notes: list[str] = []
    for name, idxs in seen.items():
        if len(idxs) == 1:
            names[idxs[0]] = name
            continue
        prefixed = [i for i in idxs
                    if _clean(entries[i][1]).startswith(_clean(entries[i][0]))]
        winner = prefixed[-1] if prefixed else idxs[-1]
        for i in idxs:
            if i == winner:
                names[i] = name
            else:
                names[i] = f"{_clean(entries[i][0])}-{name}"
        notes.append(
            "--%s claimed by %d tokens (%s); kept for %s/%s, others qualified"
            % (name, len(idxs),
               ", ".join(f"{entries[i][0]}/{entries[i][1]}" for i in idxs),
               entries[winner][0], entries[winner][1])
        )
    return names, notes


def assert_unique(block: str, lines: list[str]) -> None:
    """Refuse to emit a block that declares the same custom property twice.

    A backstop for the emitters this module does not route through
    assign_names. Redeclaring across blocks is legitimate — .dark overrides
    :root by design — so this only looks within one block.
    """
    import re as _re
    counts: dict[str, int] = {}
    for line in lines:
        m = _re.match(r"\s*(--[\w-]+)\s*:", line)
        if m:
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
    dupes = {k: v for k, v in counts.items() if v > 1}
    if dupes:
        raise SystemExit(
            f"FAIL  {block} declares {len(dupes)} custom property/properties twice: "
            + ", ".join(f"{k} x{v}" for k, v in sorted(dupes.items()))
            + "\n      The later declaration would silently win. Fix the token source."
        )


def color_vars(tree: dict, prefix: str) -> list[str]:
    lines: list[str] = []
    for path, tok in walk(tree):
        if tok["$type"] != "color":
            continue
        name = f"--{prefix}-{slug(path)}" if prefix else f"--{slug(path)}"
        value = tok["$value"]
        if isinstance(value, str):
            rendered = resolve_alias(value)
        else:
            rendered = hex_with_alpha(value)
        lines.append(f"  {name}: {rendered};")
    return lines


def number_vars(tree: dict, prefix: str = "", unit: str = "") -> list[str]:
    lines: list[str] = []
    for path, tok in walk(tree):
        if tok["$type"] != "number":
            continue
        name = f"--{prefix}-{slug(path)}" if prefix else f"--{slug(path)}"
        val = tok["$value"]
        # Render integers without trailing zeros, floats with up to 4 decimals.
        if isinstance(val, float) and not val.is_integer():
            val_str = f"{round(val, 4)}"
        else:
            val_str = str(int(val))
        if unit and val != 0:
            val_str = f"{val_str}{unit}"
        lines.append(f"  {name}: {val_str};")
    return lines


def string_vars(tree: dict, prefix: str = "") -> list[str]:
    lines: list[str] = []
    for path, tok in walk(tree):
        if tok["$type"] != "string":
            continue
        name = f"--{prefix}-{slug(path)}" if prefix else f"--{slug(path)}"
        lines.append(f"  {name}: {tok['$value']};")
    return lines


def section(title: str, body: list[str]) -> str:
    return f"  /* ---- {title} ---- */\n" + "\n".join(body)


def build() -> str:
    base = load("base-colors.tokens.json")
    primitives = load("primitives.tokens.json")
    sys_light = load("system-colors-light.tokens.json")
    sys_dark = load("system-colors-dark.tokens.json")
    shadow_light = load("shadow-colors-light.tokens.json")
    shadow_dark = load("shadow-colors-dark.tokens.json")
    type_desktop = load("typography-desktop.tokens.json")
    type_mobile = load("typography-mobile.tokens.json")

    parts: list[str] = []

    parts.append(
        "/*\n"
        " * Quid (Terminal) Design System — generated from Figma DTCG tokens.\n"
        " * Do not edit by hand. Re-run skills/quid-design-system/build_tokens.py.\n"
        " */"
    )

    # ---- :root (light is default) ----
    root: list[str] = []

    # Base color ramps (Red, Orange, Yellow, Green, Blue, Purple, Pink, Gray, etc.)
    root.append(section("base color ramps", color_vars(base, "color")))

    # Semantic shadcn tokens (background, foreground, primary, ...) — light values
    root.append(section("semantic colors (light)", color_vars(sys_light, "")))

    # Shadow alpha tokens (light)
    root.append(section("shadow rgba (light)", color_vars(shadow_light, "")))

    # Radius primitives (radius-sm, radius-rg, radius-lg, ...)
    #
    # Routed through assign_names for the same reason typography is: the Quid
    # scale and the shadcn-compatibility group both contain a `radius-sm`, with
    # DIFFERENT values (6 and 4). Dropping the group name collapses them onto
    # one property, and six rules in this stylesheet read --radius-sm expecting
    # the Quid 6px. Letting the other one land there would shrink all six by
    # 2px with nothing to show for it in the build output.
    radius_entries: list[tuple[str, str]] = []
    radius_vals: list[float] = []
    state_lines: list[str] = []
    for path, tok in walk(primitives):
        if tok["$type"] != "number":
            continue
        # primitives.tokens.json contains both radius (px) and state (opacity %).
        if path[0].startswith("radius"):
            radius_entries.append((path[0], path[-1]))
            radius_vals.append(tok["$value"])
        elif path[0] == "state":
            state_lines.append(f"  --opacity-{slug(path[1:])}: {tok['$value']}%;")

    radius_names, radius_notes = assign_names(radius_entries)
    radius_lines: list[str] = []
    for i, val in enumerate(radius_vals):
        if isinstance(val, float) and not val.is_integer():
            val_str = f"{round(val, 4)}px"
        else:
            val_str = f"{int(val)}px"
        radius_lines.append(f"  --{radius_names[i]}: {val_str};")
    root.append(section("radius & state primitives", radius_lines + state_lines))

    # Typography (desktop). Emit using only the leaf token name — the Figma leaves
    # already carry the prefix (font-sans, font-size-14, font-line-height-h1, font-bold, ...).
    #
    # Collected first, then named in one pass: leaves collide across groups, and
    # the winner cannot be decided until every entry is known. See assign_names.
    entries: list[tuple[str, str]] = []
    renderers: list = []

    for path, tok in walk(type_desktop["font-family"]):
        if tok["$type"] != "string":
            continue
        entries.append(("font-family", path[-1]))
        value = tok["$value"]
        if is_alias(value):
            # A brace alias was previously written into the CSS verbatim, e.g.
            # `--font-size-h1: {font-family.font-display}, ui-sans-serif, ...`,
            # which is not a value any browser can parse. Point it at the
            # target custom property instead. No fallback stack is appended:
            # the target already carries one, and repeating it would nest the
            # same three families twice.
            renderers.append(lambda v=value: f"var(--{alias_leaf(v)})")
        else:
            renderers.append(lambda v=value: f"{v}, ui-sans-serif, system-ui, sans-serif")

    for cat in ("font-size", "line-height"):
        for path, tok in walk(type_desktop[cat]):
            entries.append((cat, path[-1]))
            renderers.append(lambda t=tok: f"{int(t['$value'])}px")

    for path, tok in walk(type_desktop["font-weight"]):
        entries.append(("font-weight", path[-1]))
        renderers.append(lambda t=tok: f"{int(t['$value'])}")

    names, collision_notes = assign_names(entries)
    type_lines = [f"  --{names[i]}: {renderers[i]()};" for i in range(len(entries))]
    assert_unique("typography (desktop)", type_lines)
    root.append(section("typography (desktop default)", type_lines))
    build.collision_notes = radius_notes + collision_notes

    # Composed shadow recipes (built from shadow color tokens)
    root.append(
        section(
            "shadow recipes (light)",
            [
                "  --shadow-sm-recipe: 0 1px 2px 0 var(--shadow-sm);",
                "  --shadow-rg-recipe: 0 1px 3px 0 var(--shadow-rg), 0 1px 2px -1px var(--shadow-rg);",
                "  --shadow-lg-recipe: 0 10px 15px -3px var(--shadow-lg), 0 4px 6px -4px var(--shadow-lg);",
                "  --shadow-sm-hover-recipe: 0 4px 6px -1px var(--shadow-sm-hover), 0 2px 4px -2px var(--shadow-sm-hover);",
                "  --shadow-rg-hover-recipe: 0 4px 6px -1px var(--shadow-rg-hover), 0 2px 4px -2px var(--shadow-rg-hover);",
            ],
        )
    )

    assert_unique(":root", [ln for blk in root for ln in blk.splitlines()])
    css = ":root {\n" + "\n\n".join(root) + "\n}\n"
    parts.append(css)

    # ---- .dark / [data-theme=\"dark\"] override ----
    dark_lines: list[str] = []
    dark_lines.append(section("semantic colors (dark)", color_vars(sys_dark, "")))
    dark_lines.append(section("shadow rgba (dark)", color_vars(shadow_dark, "")))
    assert_unique(".dark", [ln for blk in dark_lines for ln in blk.splitlines()])
    parts.append('.dark, [data-theme="dark"] {\n' + "\n\n".join(dark_lines) + "\n}\n")

    # ---- Mobile typography override ----
    mobile_lines: list[str] = []
    for cat in ("font-size", "line-height"):
        for path, tok in walk(type_mobile[cat]):
            mobile_lines.append(f"    --{_clean(path[-1])}: {int(tok['$value'])}px;")
    parts.append(
        "@media (max-width: 768px) {\n  :root {\n"
        + "\n".join(mobile_lines)
        + "\n  }\n}\n"
    )

    # ---- Base + utility layer ----
    parts.append(
        """/* ---- Base + shadcn-aligned utilities ---- */
*, *::before, *::after { box-sizing: border-box; border-color: var(--border, #e5e5e5); }

html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  font-family: var(--font-sans);
  font-size: var(--font-size-14, 14px);
  line-height: var(--font-line-height-14, 20px);
  font-weight: var(--font-regular);
  color: var(--foreground);
  background: var(--background);
  -webkit-font-smoothing: antialiased;
  /* ss03 = Inter's "Round quotes & commas".
     cv11 ("Single-story a") was removed: it swapped the default double-storey a
     for a round, single-storey form, which read as a rendering fault rather than
     a deliberate letterform to people reading Quid briefs. It also only ever
     applied when Inter itself loaded, so artifacts falling back to a system font
     silently lost it — the same text set two different ways depending on the
     viewer. ss03 is kept: it is subtle, and nobody has objected to it. */
  font-feature-settings: "ss03";
}

h1, h2, h3, h4, h5, h6 { margin: 0; font-weight: var(--font-headings); color: var(--foreground); }

/* ONE RULE PER NAMED TYPE STYLE, each consuming its own tokens. Do not group
   two of these onto a third one's variables to save a line: hero, subtitle and
   pull-quote all used to ride along on h0 and h2, which silently shipped three
   type styles at the wrong size for as long as the grouping existed. The
   typography collection names them separately because Figma sets them
   separately. */
.quid-hero { font-size: var(--font-size-hero); line-height: var(--font-line-height-hero); font-weight: var(--font-h0); letter-spacing: -0.02em; }
.quid-h0   { font-size: var(--font-size-h0); line-height: var(--font-line-height-h0); font-weight: var(--font-h0); letter-spacing: -0.02em; }
.quid-h1   { font-size: var(--font-size-h1); line-height: var(--font-line-height-h1); font-weight: var(--font-headings); letter-spacing: -0.015em; }
.quid-h2   { font-size: var(--font-size-h2); line-height: var(--font-line-height-h2); font-weight: var(--font-headings); letter-spacing: -0.01em; }
.quid-subtitle   { font-size: var(--font-size-subtitle); line-height: var(--font-line-height-subtitle); font-weight: var(--font-headings); letter-spacing: -0.01em; }
.quid-pull-quote { font-size: var(--font-size-pull-quote); line-height: var(--font-line-height-pull-quote); font-weight: var(--font-headings); letter-spacing: -0.01em; }
.quid-h3   { font-size: var(--font-size-h3); line-height: var(--font-line-height-h3); font-weight: var(--font-headings); }
.quid-body { font-size: var(--font-size-14); line-height: var(--font-line-height-14); }
.quid-body-lg { font-size: var(--font-size-16); line-height: var(--font-line-height-16); }
.quid-caption { font-size: var(--font-size-12); line-height: var(--font-line-height-12); color: var(--muted-foreground); }
.quid-muted   { color: var(--muted-foreground); }

/* shadcn-style card */
.quid-card {
  background: var(--card);
  color: var(--card-foreground);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm-recipe);
}

.quid-button {
  display: inline-flex; align-items: center; gap: 8px;
  height: 36px; padding: 0 14px;
  font-size: var(--font-size-14); font-weight: var(--font-medium);
  background: var(--primary); color: var(--primary-foreground);
  border: 0; border-radius: var(--radius);
  box-shadow: var(--shadow-sm-recipe);
  cursor: pointer;
  transition: box-shadow 120ms ease, opacity 120ms ease;
}
.quid-button:hover { box-shadow: var(--shadow-sm-hover-recipe); }
.quid-button[disabled], .quid-button:disabled { opacity: var(--opacity-disabled); cursor: not-allowed; }

.quid-badge {
  display: inline-flex; align-items: center;
  height: 22px; padding: 0 8px;
  font-size: var(--font-size-12); line-height: 1; font-weight: var(--font-medium);
  background: var(--muted); color: var(--muted-foreground);
  border-radius: var(--radius-full);
}
"""
    )

    # ---- Example-post components ----
    # Post cards for social/news evidence in briefs (image-top carousel).
    # Markup contract + image-sourcing rules: SKILL.md "Example-post components";
    # reference markup: example.html "Example posts" section.
    parts.append(
        """/* ---- Example-post components (image-top carousel) ---- */
.sub-head { display: flex; align-items: center; gap: 10px; font-size: var(--font-size-h3); line-height: var(--font-line-height-h3); font-weight: var(--font-bold); margin: 26px 0 12px; }
.sub-head:first-child { margin-top: 0; }
.sub-head .count { font-size: var(--font-size-12); font-weight: var(--font-semibold); color: var(--muted-foreground); background: var(--muted); border-radius: var(--radius-full); padding: 2px 10px; }

.sc-carousel { display: flex; gap: 12px; overflow-x: auto; margin: 12px 0; padding-bottom: 10px; scroll-snap-type: x proximity; -webkit-overflow-scrolling: touch; scrollbar-color: var(--unselected-border) transparent; }
.sc-carousel::-webkit-scrollbar { height: 8px; }
.sc-carousel::-webkit-scrollbar-thumb { background: var(--unselected-border); border-radius: var(--radius-full); }
.sc-carousel::-webkit-scrollbar-track { background: transparent; }

.sc-card {
  flex: 0 0 244px; scroll-snap-align: start;
  display: flex; flex-direction: column;
  background: var(--card); border: 1px solid var(--border); border-radius: var(--radius);
  overflow: hidden; box-shadow: var(--shadow-sm-recipe); text-decoration: none;
  transition: box-shadow .15s, border-color .15s, transform .15s;
}
.sc-card:hover { box-shadow: var(--shadow-lg-recipe); border-color: var(--hover-border); transform: translateY(-2px); }

.sc-thumb { aspect-ratio: 16 / 9; background: var(--muted); flex: none; overflow: hidden; }
.sc-thumb img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; display: block; }
.sc-thumb-ph { display: flex; align-items: center; justify-content: center; text-align: center; padding: 14px; background: linear-gradient(135deg, var(--primary-container-background), var(--secondary)); }
.sc-thumb-ph span { font-size: var(--font-size-13); font-weight: var(--font-semibold); color: var(--primary); word-break: break-word; }

.sc-meta { display: flex; flex-direction: column; padding: 14px 16px; }
.sc-who { display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
.sc-handle { font-size: var(--font-size-13); font-weight: var(--font-bold); color: var(--foreground); }
.sc-plat { font-size: var(--font-size-12); color: var(--muted-foreground); }
.sc-quote { font-size: var(--font-size-13); line-height: var(--font-line-height-15); color: var(--card-foreground); margin: 0 0 12px; font-style: italic; }
.sc-link { margin-top: auto; font-size: var(--font-size-12); font-weight: var(--font-semibold); color: var(--primary); }
.sc-card:hover .sc-link { text-decoration: underline; }
"""
    )

    # ---- Large cards (creative in the wild) ----
    # Image-top post cards in a 3-up grid; the whole card is the click target.
    # Markup contract + sourcing rules: SKILL.md "Large cards (creative in the wild)";
    # reference markup: example.html "Large cards" section.
    parts.append(
        """/* ---- Large cards (creative in the wild) — image-top, whole card is the click target ---- */
.large-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin: 12px 0; }
@media (max-width: 900px) { .large-cards { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 560px) { .large-cards { grid-template-columns: 1fr; } }
.large-card { display: flex; flex-direction: column; background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; box-shadow: var(--shadow-sm-recipe); text-decoration: none; color: inherit; cursor: pointer; transition: box-shadow .15s ease, transform .15s ease; }
.large-card:hover { box-shadow: var(--shadow-lg-recipe); transform: translateY(-2px); }
.large-card:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }
.large-card .lc-thumb { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; background: var(--muted); display: block; }
.large-card .lc-meta { padding: 14px 16px; display: flex; flex-direction: column; gap: 6px; flex: 1; }
.large-card .lc-head { display: flex; align-items: center; gap: 8px; }
.large-card .lc-author { font-size: var(--font-size-13); font-weight: var(--font-semibold); color: var(--card-foreground); }
.large-card .lc-src { font-size: var(--font-size-12); color: var(--muted-foreground); margin-left: auto; }
.large-card .lc-text { font-size: var(--font-size-13); line-height: var(--font-line-height-15); color: var(--muted-foreground); display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
.large-card .lc-stats { margin-top: auto; display: flex; gap: 14px; font-size: var(--font-size-12); color: var(--muted-foreground); padding-top: 4px; }
.large-card .lc-stats b { color: var(--foreground); font-weight: var(--font-semibold); }
/* video variant — thumbnail with channel/platform logo overlay + play affordance */
.large-card .lc-media { position: relative; aspect-ratio: 1 / 1; background: var(--muted); overflow: hidden; }
.large-card .lc-media .lc-thumb { width: 100%; height: 100%; aspect-ratio: auto; }
.large-card .lc-logo { position: absolute; top: 8px; left: 8px; width: 30px; height: 30px; border-radius: 50%; background: #fff; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 1px 3px rgba(0,0,0,.28); }
.large-card .lc-logo svg { width: 18px; height: 18px; display: block; }
.large-card .lc-play { position: absolute; inset: 0; margin: auto; width: 52px; height: 52px; border-radius: 50%; background: rgba(17,17,17,.55); display: flex; align-items: center; justify-content: center; transition: background .15s ease, transform .15s ease; }
.large-card:hover .lc-play { background: var(--primary); transform: scale(1.06); }
.large-card .lc-play svg { width: 20px; height: 20px; fill: #fff; margin-left: 2px; }
/* dead/absent image → shared domain tile; compound selector so the gradient outranks .lc-media's muted bg */
.large-card .lc-media.sc-thumb-ph { background: linear-gradient(135deg, var(--primary-container-background), var(--secondary)); }
"""
    )

    # ---- Social embeds (native) ----
    # Markup contract + per-platform embed method: SKILL.md "Social embeds (native)";
    # reference markup: example.html "Social embeds (native)" section.
    parts.append(
        """/* ---- Social embeds (native) — one tile per platform, platform's own embed snippet ---- */
.embed-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; align-items: start; margin: 12px 0; }
.embed-tile { border: 1px solid var(--border); border-radius: var(--radius); background: var(--card); box-shadow: var(--shadow-sm-recipe); overflow: hidden; }
.embed-tile .embed-plat { display: flex; align-items: center; gap: 7px; padding: 10px 14px; border-bottom: 1px solid var(--border); font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: .02em; color: var(--muted-foreground); }
.embed-tile .embed-plat .dot { width: 9px; height: 9px; border-radius: 50%; flex: none; }
.embed-tile .embed-body { padding: 12px; }
.embed-tile .embed-body iframe { width: 100%; border: 0; display: block; }
/* 16:9 responsive wrapper for YouTube (aspect-ratio iframes) */
.embed-tile .yt { position: relative; width: 100%; padding-top: 56.25%; border-radius: var(--radius-sm); overflow: hidden; }
.embed-tile .yt iframe { position: absolute; inset: 0; width: 100%; height: 100%; }
/* script-processed blockquotes centre themselves once the platform widget rehydrates them */
.embed-tile .instagram-media, .embed-tile .tiktok-embed, .embed-tile .twitter-tweet { margin: 0 auto !important; }
/* No max-width. This carried `70ch`, the last reading-measure cap on text in
   the system, and it resolved to 574px against a 930px body column -- 62%, so
   an embed caption ran two-thirds width while everything around it ran full.
   The one other cap, `.hero .lede`, is gone too. Text fills its column here. */
.embed-note { font-size: var(--font-size-13); line-height: var(--font-line-height-13); color: var(--muted-foreground); margin-top: 16px; }
"""
    )

    # ---- Shell (page scaffold / container) ----
    # The full-page container every multi-section brief is built on: a sticky
    # side-nav rail beside the main column (hero + a .brief-body slot of
    # <section> blocks). Catalog components (KPI, charts,
    # posts, embeds, tables) compose INSIDE the .brief-body sections — the shell
    # is the frame, not the content.
    # Markup contract + scroll-spy JS + nav-label rule: SKILL.md "The Shell";
    # full-page reference: shell-modern-example.html.
    parts.append(
        """/* ---- Shell brand tokens (hero gradient + page canvas; overridable per client) ---- */
:root {
  --grad-navy: #0A1B33; --grad-blue: #13315C; --grad-teal: #1A8A8A;
  --hero-gradient: linear-gradient(135deg, var(--grad-navy) 0%, var(--grad-blue) 55%, var(--grad-teal) 130%);
  --hero-overlay: linear-gradient(135deg, rgba(10,27,51,.92) 0%, rgba(19,49,92,.72) 55%, rgba(26,138,138,.45) 130%);
  /* soft tinted canvas the brief cards float over (peach / mint / lavender) */
  --shell-canvas:
    radial-gradient(60% 55% at 14% 16%, rgba(252,227,206,.55) 0%, rgba(252,227,206,0) 60%),
    radial-gradient(55% 45% at 50% 82%, rgba(196,233,228,.55) 0%, rgba(196,233,228,0) 62%),
    radial-gradient(50% 60% at 90% 26%, rgba(228,223,246,.60) 0%, rgba(228,223,246,0) 60%);
}

/* ---- Shell: layout + side-nav ---- */
/* Toggle the whole scaffold with class="with-sidenav" on an ancestor (the brief <body>);
   remove it (and the <aside>) to fall back to a single full-width column. */
html { scroll-behavior: smooth; }   /* smooth-scroll on side-nav anchor clicks (each .section carries scroll-margin-top) */
.body-layout { min-height: 100vh; background-image: var(--shell-canvas); background-attachment: fixed; }
.container-brief { max-width: 1200px; margin: 24px auto 0; padding: 0 32px; }
.main { padding: 0 0 64px; }
.brief-body { min-width: 0; }
.sidenav { display: none; }                 /* hidden by default; the rail is desktop-only */
.with-sidenav .body-layout { display: flex; align-items: flex-start; min-height: 100vh; }
.with-sidenav .main { flex: 1; min-width: 0; }
@media (min-width: 1024px) {
  .with-sidenav .sidenav { display: block; width: 240px; flex-shrink: 0; position: sticky; top: 0; height: 100vh; overflow-y: auto; border-right: 1px solid var(--border); background: var(--card); padding: 26px 14px; }
}
.sidenav-title { font-size: var(--font-size-12); font-weight: var(--font-bold); letter-spacing: 0.02em; color: var(--muted-foreground); margin: 0 0 12px; padding: 0 12px; }
.sidenav nav { display: flex; flex-direction: column; gap: 2px; }
.sidenav a { display: block; padding: 8px 12px; border-left: 2px solid transparent; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: var(--font-size-14); line-height: var(--font-line-height-14); font-weight: var(--font-medium); text-transform: capitalize; color: var(--foreground); text-decoration: none; transition: color .15s, border-color .15s, background-color .15s; }
.sidenav a:hover { color: var(--primary); background: var(--secondary); }
.sidenav a.active { color: var(--primary-container-foreground); border-left-color: var(--primary); font-weight: var(--font-semibold); background: var(--primary-container-background); }

/* ---- Shell: hero / lede ---- */
/* DEFAULT hero is the dark Quid gradient with white text. Add class="has-img" and set
   --hero-img inline to layer a photo behind the dark overlay. Add class="light" for the
   pale primary-container hero instead. */
.hero { padding: 32px 0 0; text-align: left; }
.hero > .container-brief { margin-top: 0; }   /* hero owns its top space (32px); don't stack the container's 24px */
.hero-card { background-color: var(--grad-navy); background-image: var(--hero-gradient); color: #fff; border: 1px solid transparent; border-radius: var(--radius-lg); padding: 36px 32px; display: flex; flex-direction: column; justify-content: center; }
.hero-card h1 { color: #fff; }
.hero-card .lede { color: #fff; opacity: .92; }
/* photo hero: dark overlay multiplied over --hero-img (falls back to the dark gradient) */
.hero-card.has-img { background-image: var(--hero-overlay), var(--hero-img, var(--hero-gradient)); background-size: cover; background-position: center; }
/* light hero variant (opt-in): pale primary-container surface, dark text */
.hero-card.light { background-color: var(--primary-container-background); background-image: none; color: var(--foreground); border-color: var(--border); }
.hero-card.light h1 { color: var(--foreground); }
.hero-card.light .lede { color: var(--foreground); opacity: .82; }
/* eyebrow: translucent light pill by default (on dark); pale card pill on the light hero */
.hero .eyebrow { display: inline-block; align-self: flex-start; border-radius: var(--radius-full); padding: 4px 14px; font-size: var(--font-size-12); font-weight: var(--font-semibold); letter-spacing: 0.02em; margin-bottom: 20px; background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.28); color: #fff; }
.hero-card.light .eyebrow { background: var(--card); border-color: var(--border); color: var(--muted-foreground); }
.hero h1 { margin-bottom: 14px; }
/* No max-width. This carried `680px`, which stopped the lede short of the
   headline above it and the meta row below it, so one masthead had three
   different right edges. The modern shell had been overriding it to `none`
   for exactly that reason; the cap is gone from the source instead, so a
   stock-shell brief gets the same hero the modern one already had. */
.hero .lede { font-size: var(--font-size-16); line-height: var(--font-line-height-16); margin: 0; }

/* ---- Shell: section primitives (structure the .brief-body slot) ---- */
.section { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm-recipe); padding: 32px; margin-bottom: 24px; scroll-margin-top: 24px; }
/* These label <p>s set margin explicitly: a bare <p> otherwise inherits the UA
   margin-block-start of 1em, which stacks on top of .section's 32px padding. */
.section-label { font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: 0.02em; color: var(--primary); margin: 0 0 6px; }
.section > h2 { margin-top: 0; margin-bottom: 6px; }
.section > .section-sub { font-size: var(--font-size-15); line-height: var(--font-line-height-15); color: var(--muted-foreground); margin: 0 0 24px; }
.divider { border: none; border-top: 1px solid var(--border); margin: 40px 0; }
/* section divider band (between parts) */
.section-divider { background: var(--muted); color: var(--foreground); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 28px 32px; margin-bottom: 24px; }
.section-divider .divider-num { font-size: var(--font-size-13); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: 0.02em; color: var(--muted-foreground); margin-bottom: 4px; }
.section-divider h2 { color: var(--foreground); }
.section-divider p { font-size: var(--font-size-15); line-height: var(--font-line-height-15); margin-top: 6px; color: var(--muted-foreground); }
/* free-text prose block inside a section */
.prose p { font-size: var(--font-size-15); line-height: var(--font-line-height-15); color: var(--card-foreground); margin: 0 0 12px; }
.prose p:last-child { margin-bottom: 0; }
.prose ul { margin: 0 0 12px; padding-left: 18px; list-style: disc; }
.prose li { font-size: var(--font-size-15); line-height: var(--font-line-height-15); margin: 0 0 8px; }
.prose strong { font-weight: var(--font-semibold); }
/* plain content links inside a section (classed links keep their own style; side-nav unaffected) */
.section a:not([class]) { color: var(--primary); text-decoration: none; }
.section a:not([class]):hover { text-decoration: underline; }

/* ---- Methodology (standard closing disclosure; collapsed, caption-scale, never in the rail) ---- */
.methodology { margin: 32px 0 8px; border-top: 1px solid var(--border); padding-top: 12px; }
.methodology summary { cursor: pointer; list-style: none; display: inline-flex; align-items: center; gap: 6px; font-size: var(--font-size-13); font-weight: var(--font-semibold); color: var(--muted-foreground); }
.methodology summary::-webkit-details-marker { display: none; }
.methodology summary::before { content: "\\25B8"; color: var(--muted-foreground); font-size: var(--font-size-h3); line-height: 1; transition: transform .15s ease; }
.methodology[open] summary::before { transform: rotate(90deg); }
.methodology summary:hover, .methodology summary:focus-visible { color: var(--foreground); }
.methodology .methodology-body { margin-top: 8px; font-size: var(--font-size-12); line-height: 1.55; color: var(--muted-foreground); }
.methodology .methodology-body ul { margin: 0; padding-left: 18px; list-style: disc; }
.methodology .methodology-body li { margin: 4px 0; }
.methodology .methodology-body b { font-weight: var(--font-semibold); color: var(--foreground); }
"""
    )

    # ---- KPI strip (optional metric cards) ----
    # Per-metric gradient-tint metric cards: bold label over a big value, optional up/down
    # delta with a comparison-window period, and an optional sub-metric note. Colored by
    # WHICH METRIC via a metric-semantic class (--volume/--authors/--engagement/... mapped to
    # --chart-* tokens); one --kpi-tint knob drives both fill and (auto-darkened) label.
    # Markup contract + metric->color standard: SKILL.md "KPI strip"; reference: example.html.
    parts.append(
        r"""/* ---- KPI strip (optional; per-metric gradient-tint metric cards) ---- */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 16px; margin: 24px 0; }
/* One knob per card: --kpi-tint drives BOTH the gradient fill and the (auto-darkened) label color. */
.kpi-card { --kpi-tint: var(--primary); color: var(--card-foreground); border: 1px solid var(--border); border-radius: var(--radius-lg); padding: 20px; text-align: center; background: linear-gradient(155deg, color-mix(in srgb, var(--kpi-tint) 13%, var(--card)) 0%, var(--card) 62%); box-shadow: var(--shadow-sm-recipe); }
.kpi-card .label { font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: 0.02em; color: color-mix(in srgb, var(--kpi-tint) 82%, #000); line-height: 1.35; margin-bottom: 8px; }
.kpi-card .value { font-size: var(--font-size-h1); font-weight: var(--font-bold); line-height: 1.05; font-variant-numeric: tabular-nums; letter-spacing: -0.01em; }
.kpi-card .delta { display: inline-flex; align-items: center; gap: 5px; font-size: var(--font-size-13); font-weight: var(--font-semibold); margin-top: 10px; font-variant-numeric: tabular-nums; }
.kpi-card .delta::before { font-size: 0.78em; line-height: 1; }   /* directional triangle */
.kpi-card .delta.up { color: var(--color-green-700); } .kpi-card .delta.up::before { content: "\25B2"; }   /* up */
.kpi-card .delta.down { color: var(--destructive); } .kpi-card .delta.down::before { content: "\25BC"; }   /* down */
.kpi-card .delta .period { color: var(--muted-foreground); font-weight: var(--font-regular); }   /* optional "vs ..." window, inline after the delta */
.kpi-card .kpi-note { margin-top: 14px; padding-top: 12px; border-top: 1px solid var(--border); font-size: var(--font-size-12); color: var(--muted-foreground); line-height: 1.4; }   /* optional sub-metric; usually omitted */
.kpi-card .kpi-note b { color: var(--card-foreground); font-weight: var(--font-semibold); }
/* metric->color standard: author by METRIC (never re-pick the color); each sets --kpi-tint to a --chart-* token */
.kpi-card--volume     { --kpi-tint: var(--chart-1);  }   /* posts / volume                 */
.kpi-card--mentions   { --kpi-tint: var(--chart-9);  }   /* mentions (2nd volume metric)   */
.kpi-card--authors    { --kpi-tint: var(--chart-4);  }   /* active authors / unique voices */
.kpi-card--engagement { --kpi-tint: var(--chart-7);  }   /* engagements / interactions     */
.kpi-card--reach      { --kpi-tint: var(--chart-14); }   /* potential impressions / reach  */
.kpi-card--sentiment  { --kpi-tint: var(--chart-2);  }   /* net sentiment                  */
.kpi-card--positives  { --kpi-tint: var(--chart-6);  }   /* positives / positive mentions  */
.kpi-card--negatives  { --kpi-tint: var(--chart-11); }   /* negatives / negative mentions  */
.kpi-card--passion    { --kpi-tint: var(--chart-13); }   /* passion intensity              */
.kpi-card--score      { --kpi-tint: var(--chart-5);  }   /* trend score / momentum         */
.kpi-card--video      { --kpi-tint: var(--chart-3);  }   /* video / media volume           */
"""
    )

    # ---- Tag / badge ----
    # Colored pill labels (opportunity/risk/trend/signal/watch/neutral) for tagging a
    # theme, post, or insight. Ported from the Component Gallery.
    # Markup contract + rules: SKILL.md "Tags / badges"; reference: example.html "Tags / badges".
    parts.append(
        """/* ---- Tag / badge (colored pill label) ---- */
.tag { display: inline-flex; align-items: center; border: 1px solid transparent; padding: .125rem .625rem; border-radius: var(--radius-full); font-size: var(--font-size-12); line-height: 1rem; font-weight: var(--font-semibold); margin-bottom: 8px; margin-right: 4px; }
.tag-opportunity { background: var(--color-blue-100); color: var(--color-blue-900); } .tag-risk { background: var(--color-red-100); color: var(--color-red-700); }
.tag-trend { background: var(--color-purple-100); color: var(--color-purple-700); } .tag-signal { background: var(--color-green-100); color: var(--color-green-900); }
.tag-watch { background: var(--color-orange-100); color: var(--color-orange-900); } .tag-neutral { background: var(--muted); color: var(--muted-foreground); }
"""
    )

    # ---- Ranked theme — with quotes ----
    # Boxless ranked list: rank + title + tag badge + Mentions/YoY metrics + description,
    # then inline verbatim quotes. Items separated by a bottom hairline. Ported from the
    # Component Gallery. The badge uses the shared .tag classes (see the Tag / badge block).
    # Markup contract + rules: SKILL.md "Ranked theme — with quotes"; reference: example.html.
    parts.append(
        """/* ---- Ranked theme — with quotes (boxless ranked list, hairline between items) ---- */
.theme-list { display: flex; flex-direction: column; gap: 0; margin: 12px 0; }
.theme-card { border: 0; border-radius: 0; background: transparent; box-shadow: none; padding: 20px 0; border-bottom: 1px solid var(--border); }
.theme-card:last-child { border-bottom: none; }
.theme-head { display: flex; align-items: center; flex-wrap: wrap; gap: 8px 12px; }
/* ONE RANK MARKER FOR BOTH RANKED-THEME PRESENTATIONS. .ci-num renders the
   same thing -- a theme's position in an ordered list -- so it takes this rule
   rather than restating its values. Restating is how the two drifted apart in
   the first place.
   Look only. The flex alignment .ci-num needs inside .ci-card stays on .ci-num
   itself: .theme-head lays its row out with align-items: center, so an
   align-self here would top-align the badge in every brief already using
   .theme-rank. */
.theme-rank, .ci-num { flex: none; width: 26px; height: 26px; border-radius: var(--radius-full); background: var(--primary-container-background); color: var(--primary-container-foreground); font-size: var(--font-size-13); font-weight: var(--font-bold); display: inline-flex; align-items: center; justify-content: center; }
.theme-name { font-size: var(--font-size-h3); line-height: var(--font-line-height-h3); font-weight: var(--font-bold); color: var(--foreground); }
.theme-head .tag { margin: 0; }
.theme-metrics { margin-left: auto; display: flex; gap: 18px; align-items: baseline; }
.theme-metric { font-size: var(--font-size-13); color: var(--muted-foreground); } .theme-metric b { color: var(--foreground); font-weight: var(--font-bold); }
.theme-metric .up { color: var(--color-green-700); font-weight: var(--font-semibold); } .theme-metric .down { color: var(--destructive); font-weight: var(--font-semibold); }
.theme-desc { font-size: var(--font-size-14); line-height: var(--font-line-height-15); color: var(--card-foreground); margin: 10px 0 0; } .theme-desc em { font-style: italic; }
.theme-quote { border-left: 3px solid var(--primary); padding: 2px 0 2px 14px; margin: 12px 0 0; font-size: var(--font-size-14); line-height: var(--font-line-height-15); font-style: italic; color: var(--foreground); }
.theme-quote .q-src { font-style: normal; font-weight: var(--font-semibold); color: var(--primary); text-decoration: none; white-space: nowrap; margin-left: 4px; } .theme-quote .q-src:hover { text-decoration: underline; }
.theme-examples-label { font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: .02em; color: var(--muted-foreground); margin-top: 16px; }
"""
    )

    # ---- Chart palette & convention ----
    # Series-color tokens charts read via getComputedStyle: categorical --chart-1..14,
    # --sentiment-* (pos/neu/neg), and the Citrus set for wordclouds. Ported from the
    # Component Gallery. Overridable per client. Docs: SKILL.md "Chart palette & convention".
    parts.append(
        """/* ---- Chart palette & convention (series-color tokens; overridable per client) ---- */
:root {
  --chart-1: #2F75D7; --chart-2: #6E21BA; --chart-3: #CE42A6; --chart-4: #37A1A5; --chart-5: #E4A709;
  --chart-6: #187B34; --chart-7: #EC6515; --chart-8: #529CE2; --chart-9: #A12B86; --chart-10: #42C366;
  --chart-11: #DD4848; --chart-12: #A91E1E; --chart-13: #A762D9; --chart-14: #AEAEAE;
  --sentiment-positive: #2E964B; --sentiment-neutral: #A0A0A0; --sentiment-negative: #C91616;
  --citrus-1: #158287; --citrus-2: #1B959A; --citrus-3: #37A1A5; --citrus-4: #B88B00; --citrus-5: #CA5010; --citrus-6: #B94103;
}
"""
    )

    # ---- Table ----
    # Metrics / comparison table. .num right-aligns numeric cells (tabular figures);
    # add class="clickable" on .table-wrap for a row-hover state on interactive rows.
    # Ported from the Component Gallery. Markup contract: SKILL.md "Table".
    parts.append(
        """/* ---- Table (metrics / comparisons) ---- */
.table-wrap { background: var(--card); border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); margin: 20px 0; }
.table-wrap table { width: 100%; border-collapse: collapse; font-size: var(--font-size-13); }
.table-wrap thead th { background: var(--muted); color: var(--muted-foreground); padding: 10px 14px; text-align: left; font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: .05em; border-bottom: 1px solid var(--border); }
.table-wrap tbody td { padding: 11px 14px; border-bottom: 1px solid var(--border); color: var(--card-foreground); } .table-wrap tbody tr:last-child td { border-bottom: none; }
.table-wrap.clickable tbody tr { cursor: pointer; } .table-wrap.clickable tbody tr:hover { background: var(--secondary); }
.table-wrap .num { text-align: right; font-variant-numeric: tabular-nums; }
"""
    )

    # ---- Accordion ----
    # Native <details>/<summary> expandable rows for FAQs / per-item comparisons. Add
    # `open` to expand by default; optional .acc-meta right-aligns a label in the summary.
    # Ported from the Component Gallery. Markup contract: SKILL.md "Accordion".
    parts.append(
        r"""/* ---- Accordion (native <details> rows) ---- */
.accordion { border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); background: var(--card); margin: 12px 0; }
.accordion details { border-bottom: 1px solid var(--border); } .accordion details:last-child { border-bottom: none; }
.accordion summary { cursor: pointer; list-style: none; display: flex; align-items: center; gap: 10px; padding: 14px 18px; font-size: var(--font-size-15); font-weight: var(--font-semibold); color: var(--foreground); }
.accordion summary::-webkit-details-marker { display: none; }
.accordion summary::before { content: "\25B8"; color: var(--primary); font-size: var(--font-size-h2); line-height: 1; transition: transform .15s ease; }
.accordion details[open] summary::before { transform: rotate(90deg); }
.accordion summary:hover { background: var(--secondary); }
.accordion details[open] summary { background: var(--muted); }
.accordion summary .acc-meta { margin-left: auto; font-size: var(--font-size-12); font-weight: var(--font-semibold); color: var(--muted-foreground); }
.accordion .acc-body { padding: 2px 18px 18px; color: var(--card-foreground); }
"""
    )

    # ---- Ranked theme — with media ----
    # The .with-media variant of the ranked-theme card: text left, thumbnail top-right,
    # and a full-width example-posts carousel below. Extends the base .theme-* classes
    # (ranked-theme with quotes) and composes .sc-carousel. Ported from the Component
    # Gallery. Markup contract: SKILL.md "Ranked theme — with media".
    parts.append(
        """/* ---- Ranked theme — with media (text left, thumbnail right, carousel below) ---- */
.theme-main { flex: 1; min-width: 0; }
.theme-card.with-media { display: grid; grid-template-columns: minmax(0, 1fr) 200px; grid-template-areas: "text img" "cols cols"; gap: 0 24px; }
.theme-card.with-media .theme-text { grid-area: text; min-width: 0; border-bottom: 1px solid var(--border); padding-bottom: 14px; }
.theme-card.with-media .theme-thumb { grid-area: img; width: 200px; height: 140px; align-self: start; border-radius: var(--radius-md); object-fit: cover; background: var(--muted); }
.theme-card.with-media .theme-cols { grid-area: cols; margin-top: 14px; min-width: 0; }
@media (max-width: 760px) {
  .theme-card.with-media { grid-template-columns: minmax(0, 1fr); grid-template-areas: "text" "img" "cols"; }
  .theme-card.with-media .theme-text { border-bottom: none; padding-bottom: 0; }
  .theme-card.with-media .theme-thumb { width: 100%; height: 160px; margin-top: 14px; }
  .theme-card.with-media .theme-cols { padding-top: 14px; border-top: 1px solid var(--border); }
}
"""
    )

    # ---- Featured posts (2-up rich cards) ----
    # Standout posts in a 2-up grid: optional rank badge on the thumbnail, author,
    # clamped text, and a footer of engagement stats or a category tag. Ported from the
    # Component Gallery (as static cards; the optional post-detail modal is separate).
    # Reuses the shipped .sub-head / .count header. Markup contract: SKILL.md "Featured posts".
    parts.append(
        """/* ---- Featured posts (2-up rich cards) ---- */
.posts-featured { display: grid; grid-template-columns: repeat(2, 1fr); gap: 18px; margin: 12px 0; }
.post { display: flex; gap: 16px; background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px; box-shadow: var(--shadow-sm-recipe); transition: box-shadow .15s, border-color .15s, transform .15s; }
.post:hover { box-shadow: var(--shadow-lg-recipe); border-color: var(--hover-border); transform: translateY(-1px); }
.post-thumb { position: relative; flex: none; width: 92px; height: 120px; border-radius: var(--radius-sm); background: var(--muted); overflow: hidden; }
.post-thumb img { width: 100%; height: 100%; object-fit: cover; display: block; }
.post-rank { position: absolute; top: 6px; left: 6px; background: var(--primary); color: var(--primary-foreground); font-size: var(--font-size-12); font-weight: var(--font-bold); padding: 2px 8px; border-radius: var(--radius-full); }
.post-body { min-width: 0; display: flex; flex-direction: column; flex: 1; }
.post-author { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
.post-author .handle { font-size: var(--font-size-14); font-weight: var(--font-bold); color: var(--foreground); }
.post-author .src { font-size: var(--font-size-12); color: var(--muted-foreground); }
.post-text { font-size: var(--font-size-13); line-height: var(--font-line-height-15); color: var(--card-foreground); margin: 6px 0 auto; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.post-foot { display: flex; align-items: center; gap: 16px; margin-top: 12px; padding-top: 10px; border-top: 1px solid var(--border); font-size: var(--font-size-13); color: var(--muted-foreground); }
.post-foot .stat { display: inline-flex; align-items: center; gap: 5px; font-variant-numeric: tabular-nums; }
.post-foot .stat b { color: var(--foreground); font-weight: var(--font-bold); }
@media (max-width: 760px) { .posts-featured { grid-template-columns: 1fr; } }
"""
    )

    # Platform source tiles. Generated as CSS masks so a brief needs no sprite;
    # see components/platform-tiles.md for the markup contract and the rules
    # about brand colour that the CSS cannot express.
    parts.append(
        """/* ---- Platform source tiles (post-card fallback) ----
   Shows the source platform's mark on its brand colour when a post has no
   image, or when its image fails. See components/platform-tiles.md.

   NO MARKUP BEYOND THE SPAN. The mark is a CSS mask, not an <svg>, so there is
   no sprite to paste into a brief and nothing to forget. A forgotten sprite
   renders an empty box with no error, which is the failure this avoids.

   The mask is painted on ::after and coloured by its background, so the ink is
   one property (--pt-ink) rather than a second copy of every icon. */
.pt-logo { position: absolute; inset: 0; display: grid; place-items: center;
           background: #1A1A1A; --pt-ink: #FFFFFF; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12%202a10%2010%200%201%200%200%2020%2010%2010%200%200%200%200-20zm0%202c1.3%200%202.6%201.9%203.2%204.8H8.8C9.4%205.9%2010.7%204%2012%204zM6.8%208.8H4.3A8%208%200%200%201%208.6%204.7%2012%2012%200%200%200%206.8%208.8zm-3.3%202h3a20%2020%200%200%200%200%202.4h-3a8%208%200%200%201%200-2.4zm1%204.4h2.3a12%2012%200%200%200%201.8%204.1%208%208%200%200%201-4.1-4.1zm3.3-2a18%2018%200%200%201%200-2.4h8.4a18%2018%200%200%201%200%202.4zm3.2%206.8c-1.3%200-2.6-1.9-3.2-4.8h6.4c-.6%202.9-1.9%204.8-3.2%204.8zm3.4-.3a12%2012%200%200%200%201.8-4.1h2.3a8%208%200%200%201-4.1%204.1zm2.3-6.5a20%2020%200%200%200%200-2.4h3a8%208%200%200%201%200%202.4zm-.5-4.4a12%2012%200%200%200-1.8-4.1%208%208%200%200%201%204.1%204.1z'/%3E%3C/svg%3E"); }
.pt-logo::after { content: ""; width: 34px; height: 34px; background: var(--pt-ink);
                  -webkit-mask: var(--pt-mark) center / contain no-repeat;
                          mask: var(--pt-mark) center / contain no-repeat; }
.post-thumb img, .sc-thumb img { position: relative; z-index: 1; }
a.post { text-decoration: none; color: inherit; }
a.post:hover .sc-link { text-decoration: underline; }
.pt-logo[data-plat="facebook"] { background: #1877F2; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M9.101%2023.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085%201.848-5.978%205.858-5.978.401%200%20.955.042%201.468.103a8.68%208.68%200%200%201%201.141.195v3.325a8.623%208.623%200%200%200-.653-.036%2026.805%2026.805%200%200%200-.733-.009c-.707%200-1.259.096-1.675.309a1.686%201.686%200%200%200-.679.622c-.258.42-.374.995-.374%201.752v1.297h3.919l-.386%202.103-.287%201.564h-3.246v8.245C19.396%2023.238%2024%2018.179%2024%2012.044c0-6.627-5.373-12-12-12s-12%205.373-12%2012c0%205.628%203.874%2010.35%209.101%2011.647Z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="instagram"] { background: radial-gradient(circle at 30% 107%, #FDF497 0%, #FD5949 45%, #D6249F 60%, #285AEB 90%); --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12%202.163c3.204%200%203.584.012%204.85.07%203.252.148%204.771%201.691%204.919%204.919.058%201.265.069%201.645.069%204.849%200%203.205-.012%203.584-.069%204.849-.149%203.225-1.664%204.771-4.919%204.919-1.266.058-1.644.07-4.85.07-3.204%200-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849%200-3.204.013-3.583.07-4.849.149-3.227%201.664-4.771%204.919-4.919%201.266-.057%201.645-.069%204.849-.069zm0-2.163c-3.259%200-3.667.014-4.947.072-4.358.2-6.78%202.618-6.98%206.98-.059%201.281-.073%201.689-.073%204.948%200%203.259.014%203.668.072%204.948.2%204.358%202.618%206.78%206.98%206.98%201.281.058%201.689.072%204.948.072%203.259%200%203.668-.014%204.948-.072%204.354-.2%206.782-2.618%206.979-6.98.059-1.28.073-1.689.073-4.948%200-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0%205.838c-3.403%200-6.162%202.759-6.162%206.162s2.759%206.163%206.162%206.163%206.162-2.759%206.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0%2010.162c-2.209%200-4-1.79-4-4%200-2.209%201.791-4%204-4s4%201.791%204%204c0%202.21-1.791%204-4%204zm6.406-11.845c-.796%200-1.441.645-1.441%201.44s.645%201.44%201.441%201.44c.795%200%201.439-.645%201.439-1.44s-.644-1.44-1.439-1.44z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="x"] { background: #000000; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M18.244%202.25h3.308l-7.227%208.26%208.502%2011.24H16.17l-5.214-6.817L4.99%2021.75H1.68l7.73-8.835L1.254%202.25H8.08l4.713%206.231zm-1.161%2017.52h1.833L7.084%204.126H5.117z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="threads"] { background: #000000; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12.186%2024h-.007c-3.581-.024-6.334-1.205-8.184-3.509C2.35%2018.44%201.5%2015.586%201.5%2012.007v-.014c0-3.579.85-6.433%202.495-8.484C5.845%201.205%208.598.024%2012.179%200h.014c2.746.019%205.043.725%206.826%202.098%201.677%201.291%202.858%203.13%203.509%205.467l-2.04.569c-1.104-3.96-3.898-5.984-8.304-6.015-2.91.022-5.11.936-6.54%202.717C4.307%206.504%203.616%208.914%203.616%2012c0%203.086.69%205.496%202.05%207.164%201.43%201.78%203.631%202.695%206.54%202.717%202.623-.02%204.358-.631%205.8-2.045%201.647-1.613%201.617-3.593%201.09-4.798-.31-.71-.873-1.3-1.634-1.75-.192%201.352-.622%202.446-1.284%203.272-.886%201.102-2.14%201.704-3.73%201.79-1.202.065-2.36-.218-3.259-.801-1.063-.689-1.685-1.74-1.752-2.964-.065-1.19.408-2.285%201.33-3.082.88-.76%202.119-1.207%203.583-1.291a13.853%2013.853%200%200%201%203.02.142c-.126-.742-.375-1.332-.75-1.757-.513-.586-1.308-.883-2.359-.89h-.029c-.844%200-1.992.232-2.721%201.32L7.734%207.847c.98-1.454%202.568-2.256%204.478-2.256h.044c3.194.02%205.097%201.975%205.287%205.388.108.046.216.094.321.142%201.49.7%202.58%201.761%203.154%203.07.797%201.82.871%204.79-1.548%207.158-1.85%201.81-4.094%202.628-7.277%202.65h-.007zm1.62-10.65c-.218%200-.44.006-.666.018-1.837.103-2.978.946-2.916%202.143.063%201.156%201.342%201.714%202.571%201.648%201.131-.06%202.606-.5%202.853-3.427a10.342%2010.342%200%200%200-1.842-.382z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="tiktok"] { background: #000000; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12.525.02c1.31-.02%202.61-.01%203.91-.02.08%201.53.63%203.09%201.75%204.17%201.12%201.11%202.7%201.62%204.24%201.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01%202.92.01%205.84-.02%208.75-.08%201.4-.54%202.79-1.35%203.94-1.31%201.92-3.58%203.17-5.91%203.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9%201.12-3.72%202.58-4.96%201.66-1.44%203.98-2.13%206.15-1.72.02%201.48-.04%202.96-.04%204.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11%201.04-1.36%201.75-.21.51-.15%201.07-.14%201.61.24%201.64%201.82%203.02%203.5%202.87%201.12-.01%202.19-.66%202.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="youtube"] { background: #FF0000; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M23.498%206.186a3.016%203.016%200%200%200-2.122-2.136C19.505%203.545%2012%203.545%2012%203.545s-7.505%200-9.377.505A3.017%203.017%200%200%200%20.502%206.186C0%208.07%200%2012%200%2012s0%203.93.502%205.814a3.016%203.016%200%200%200%202.122%202.136c1.871.505%209.376.505%209.376.505s7.505%200%209.377-.505a3.015%203.015%200%200%200%202.122-2.136C24%2015.93%2024%2012%2024%2012s0-3.93-.502-5.814zM9.545%2015.568V8.432L15.818%2012l-6.273%203.568z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="linkedin"] { background: #0A66C2; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M20.447%2020.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853%200-2.136%201.445-2.136%202.939v5.667H9.351V9h3.414v1.561h.046c.477-.9%201.637-1.85%203.37-1.85%203.601%200%204.267%202.37%204.267%205.455v6.286zM5.337%207.433c-1.144%200-2.063-.926-2.063-2.065%200-1.138.92-2.063%202.063-2.063%201.14%200%202.064.925%202.064%202.063%200%201.139-.925%202.065-2.064%202.065zm1.782%2013.019H3.555V9h3.564v11.452zM22.225%200H1.771C.792%200%200%20.774%200%201.729v20.542C0%2023.227.792%2024%201.771%2024h20.451C23.2%2024%2024%2023.227%2024%2022.271V1.729C24%20.774%2023.2%200%2022.222%200h.003z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="reddit"] { background: #FF4500; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12%200A12%2012%200%200%200%200%2012a12%2012%200%200%200%2012%2012%2012%2012%200%200%200%2012-12A12%2012%200%200%200%2012%200zm5.01%204.744c.688%200%201.25.561%201.25%201.249a1.25%201.25%200%200%201-2.498.056l-2.597-.547-.8%203.747c1.824.07%203.48.632%204.674%201.488.308-.309.73-.491%201.207-.491.968%200%201.754.786%201.754%201.754%200%20.716-.435%201.333-1.01%201.614a3.111%203.111%200%200%201%20.042.52c0%202.694-3.13%204.87-7.004%204.87-3.874%200-7.004-2.176-7.004-4.87%200-.183.015-.366.043-.534A1.748%201.748%200%200%201%204.028%2012c0-.968.786-1.754%201.754-1.754.463%200%20.898.196%201.207.49%201.207-.883%202.878-1.43%204.744-1.487l.885-4.182a.342.342%200%200%201%20.14-.197.35.35%200%200%201%20.238-.042l2.906.617a1.214%201.214%200%200%201%201.108-.701zM9.25%2012C8.561%2012%208%2012.562%208%2013.25c0%20.687.561%201.248%201.25%201.248.687%200%201.248-.561%201.248-1.249%200-.688-.561-1.249-1.249-1.249zm5.5%200c-.687%200-1.248.561-1.248%201.25%200%20.687.561%201.248%201.249%201.248.688%200%201.249-.561%201.249-1.249%200-.688-.561-1.249-1.25-1.249zm-5.466%203.99a.327.327%200%200%200-.231.094.33.33%200%200%200%200%20.463c.842.842%202.484.913%202.961.913.477%200%202.105-.056%202.961-.913a.361.361%200%200%200%20.029-.463.33.33%200%200%200-.464%200c-.547.533-1.684.73-2.512.73-.828%200-1.979-.196-2.512-.73a.326.326%200%200%200-.232-.095z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="pinterest"] { background: #BD081C; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12.017%200C5.396%200%20.029%205.367.029%2011.987c0%205.079%203.158%209.417%207.618%2011.162-.105-.949-.199-2.403.041-3.439.219-.937%201.406-5.957%201.406-5.957s-.359-.72-.359-1.781c0-1.663.967-2.911%202.168-2.911%201.024%200%201.518.769%201.518%201.688%200%201.029-.653%202.567-.992%203.992-.285%201.193.6%202.165%201.775%202.165%202.128%200%203.768-2.245%203.768-5.487%200-2.861-2.063-4.869-5.008-4.869-3.41%200-5.409%202.562-5.409%205.199%200%201.033.394%202.143.889%202.741.099.12.112.225.085.345-.09.375-.293%201.199-.334%201.363-.053.225-.172.271-.401.165-1.495-.69-2.433-2.878-2.433-4.646%200-3.776%202.748-7.252%207.92-7.252%204.158%200%207.392%202.967%207.392%206.923%200%204.135-2.607%207.462-6.233%207.462-1.214%200-2.354-.629-2.758-1.379l-.749%202.848c-.269%201.045-1.004%202.352-1.498%203.146%201.123.345%202.306.535%203.55.535%206.607%200%2011.985-5.365%2011.985-11.987C23.97%205.39%2018.592.026%2011.985.026L12.017%200z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="snapchat"] { background: #FFFC00; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12.031%200c-2.4%200-4.56%201.26-5.76%203.3-.6%201.02-.9%202.22-.84%203.42l.06%201.44c-.12.06-.3.12-.48.12-.3%200-.6-.12-.96-.3-.3-.18-.66-.24-.96-.24-.6%200-1.14.36-1.26.84-.12.54.18%201.08.84%201.32l.3.12c.6.24%201.38.54%201.56%201.02.12.3%200%20.72-.24%201.2-.9%201.74-2.4%202.94-3.42%203.18-.36.06-.6.36-.6.72%200%20.18.06.3.12.42.3.54%201.38.9%203.06%201.14.6.06.12.3.18.6.06.24.12.48.18.72.12.36.36.54.72.54.18%200%20.36-.6.6-.12.36-.6.78-.12%201.32-.12.3%200%20.66%200%201.02.06.72.12%201.32.54%202.04%201.02.84.6%201.8%201.26%203.24%201.26h.18c1.44%200%202.4-.66%203.24-1.26.72-.48%201.32-.9%202.04-1.02.36-.6.72-.06%201.02-.6.54%200%20.96.06%201.32.12.24.6.42.12.6.12.42%200%20.6-.24.72-.54.06-.24.12-.48.18-.72.06-.3.12-.54.18-.6%201.68-.24%202.76-.6%203.06-1.14.06-.12.12-.24.12-.42%200-.36-.24-.66-.6-.72-1.02-.24-2.52-1.44-3.42-3.18-.24-.48-.36-.9-.24-1.2.18-.48.96-.78%201.56-1.02l.3-.12c.66-.24.96-.78.84-1.32-.12-.48-.66-.84-1.26-.84-.3%200-.66.06-.96.24-.36.18-.66.3-.96.3-.18%200-.36-.06-.48-.12l.06-1.44c.06-1.2-.24-2.4-.84-3.42C16.591%201.26%2014.431%200%2012.031%200z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="twitch"] { background: #9146FF; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M11.571%204.714h1.715v5.143H11.57zm4.715%200H18v5.143h-1.714zM6%200L1.714%204.286v15.428h5.143V24l4.286-4.286h3.428L22.286%2012V0zm14.571%2011.143l-3.428%203.428h-3.429l-3%203v-3H6.857V1.714h13.714Z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="tumblr"] { background: #36465D; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M14.563%2024c-5.093%200-7.031-3.756-7.031-6.411V9.747H5.116V6.648c3.63-1.313%204.512-4.596%204.71-6.469C9.84.051%209.941%200%209.999%200h3.517v6.114h4.801v3.633h-4.82v7.47c.016%201.001.375%202.371%202.207%202.371h.09c.631-.02%201.486-.205%201.936-.419l1.156%203.425c-.436.636-2.4%201.374-4.156%201.404h-.178l.011.002z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="bluesky"] { background: #0285FF; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M12%2010.8c-1.087-2.114-4.046-6.053-6.798-7.995C2.566.944%201.561%201.266.902%201.565.139%201.908%200%203.08%200%203.768c0%20.69.378%205.65.624%206.479.815%202.736%203.713%203.66%206.383%203.364.136-.02.275-.039.415-.056-.138.022-.276.04-.415.056-3.912.58-7.387%202.005-2.83%207.078%205.013%205.19%206.87-1.113%207.823-4.308.953%203.195%202.05%209.271%207.733%204.308%204.267-4.308%201.172-6.498-2.74-7.078a8.741%208.741%200%200%201-.415-.056c.14.017.279.036.415.056%202.67.297%205.568-.628%206.383-3.364.246-.828.624-5.789.624-6.478%200-.69-.139-1.861-.902-2.206-.659-.298-1.664-.62-4.3%201.24C16.046%204.748%2013.087%208.687%2012%2010.8Z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="discord"] { background: #5865F2; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M20.317%204.3698a19.7913%2019.7913%200%2000-4.8851-1.5152.0741.0741%200%2000-.0785.0371c-.211.3753-.4447.8648-.6083%201.2495-1.8447-.2762-3.68-.2762-5.4868%200-.1636-.3933-.4058-.8742-.6177-1.2495a.077.077%200%2000-.0785-.037%2019.7363%2019.7363%200%2000-4.8852%201.515.0699.0699%200%2000-.0321.0277C.5334%209.0458-.319%2013.5799.0992%2018.0578a.0824.0824%200%2000.0312.0561c2.0528%201.5076%204.0413%202.4228%205.9929%203.0294a.0777.0777%200%2000.0842-.0276c.4616-.6304.8731-1.2952%201.226-1.9942a.076.076%200%2000-.0416-.1057c-.6528-.2476-1.2743-.5495-1.8722-.8923a.077.077%200%2001-.0076-.1277c.1258-.0943.2517-.1923.3718-.2914a.0743.0743%200%2001.0776-.0105c3.9278%201.7933%208.18%201.7933%2012.0614%200a.0739.0739%200%2001.0785.0095c.1202.099.246.1981.3728.2924a.077.077%200%2001-.0066.1276%2012.2986%2012.2986%200%2001-1.873.8914.0766.0766%200%2000-.0407.1067c.3604.698.7719%201.3628%201.225%201.9932a.076.076%200%2000.0842.0286c1.961-.6067%203.9495-1.5219%206.0023-3.0294a.077.077%200%2000.0313-.0552c.5004-5.177-.8382-9.6739-3.5485-13.6604a.061.061%200%2000-.0312-.0286zM8.02%2015.3312c-1.1825%200-2.1569-1.0857-2.1569-2.419%200-1.3332.9555-2.4189%202.157-2.4189%201.2108%200%202.1757%201.0952%202.1568%202.419%200%201.3332-.9555%202.4189-2.1569%202.4189zm7.9748%200c-1.1825%200-2.1569-1.0857-2.1569-2.419%200-1.3332.9554-2.4189%202.1569-2.4189%201.2108%200%202.1757%201.0952%202.1568%202.419%200%201.3332-.946%202.4189-2.1568%202.4189Z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="telegram"] { background: #26A5E4; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M11.944%200A12%2012%200%200%200%200%2012a12%2012%200%200%200%2012%2012%2012%2012%200%200%200%2012-12A12%2012%200%200%200%2012%200a12%2012%200%200%200-.056%200zm4.962%207.224c.1-.002.321.023.465.14a.506.506%200%200%201%20.171.325c.016.093.036.306.02.472-.18%201.898-.962%206.502-1.36%208.627-.168.9-.499%201.201-.82%201.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184%203.247-2.977%203.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793%201.14-5.061%203.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663%203.498-1.524%205.83-2.529%206.998-3.014%203.332-1.386%204.025-1.627%204.476-1.635z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="whatsapp"] { background: #25D366; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M17.472%2014.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94%201.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198%200-.52.074-.792.372-.272.297-1.04%201.016-1.04%202.479%200%201.462%201.065%202.875%201.213%203.074.149.198%202.096%203.2%205.077%204.487.709.306%201.262.489%201.694.625.712.227%201.36.195%201.871.118.571-.085%201.758-.719%202.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421%207.403h-.004a9.87%209.87%200%2001-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86%209.86%200%2001-1.51-5.26c.001-5.45%204.436-9.884%209.888-9.884%202.64%200%205.122%201.03%206.988%202.898a9.825%209.825%200%20012.893%206.994c-.003%205.45-4.437%209.884-9.885%209.884m8.413-18.297A11.815%2011.815%200%200012.05%200C5.495%200%20.16%205.335.157%2011.892c0%202.096.547%204.142%201.588%205.945L.057%2024l6.305-1.654a11.882%2011.882%200%20005.683%201.448h.005c6.554%200%2011.89-5.335%2011.893-11.893A11.821%2011.821%200%200020.885%203.488'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="vimeo"] { background: #1AB7EA; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M23.9765%206.4168c-.105%202.338-1.739%205.5429-4.894%209.6088-3.2679%204.247-6.0258%206.3699-8.2898%206.3699-1.409%200-2.578-1.294-3.553-3.881l-1.9179-7.1138c-.719-2.584-1.488-3.878-2.312-3.878-.179%200-.806.378-1.8809%201.132L0%207.3729c1.19-1.0469%202.366-2.0939%203.521-3.1429%201.588-1.3699%202.78-2.0909%203.578-2.1639%201.882-.1809%203.0389%201.1059%203.4729%203.8599.4679%202.9729.7929%204.8208.9759%205.5428.5469%202.4868%201.1499%203.7288%201.8109%203.7288.5119%200%201.2819-.8109%202.3099-2.4319%201.0259-1.6209%201.5759-2.8549%201.6499-3.7028.1449-1.3879-.3999-2.0829-1.6339-2.0829-.5809%200-1.1799.1329-1.7959.3979%201.1929-3.9099%203.4729-5.8099%206.8379-5.7008%202.4949.0729%203.6709%201.6919%203.5279%204.8569'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="podcast"] { background: #7A3DB8; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M1.5%201.5v3c10.493%200%2019.5%209.007%2019.5%2019.5h3C24%2011.85%2012.15%200%201.5%200zm0%207.5v3c6.351%200%2012%205.649%2012%2012h3c0-8.007-6.993-15-15-15zM4.5%2018a3%203%200%201%200%200%206%203%203%200%200%200%200-6z'/%3E%3C/svg%3E"); }
.pt-logo[data-plat="news"] { background: #334155; --pt-mark: url("data:image/svg+xml,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%3E%3Cpath%20d='M3%204h14v16H5a2%202%200%200%201-2-2V4zm2%202v5h5V6H5zm7%200v1.5h4V6h-4zm0%203.5V11h4V9.5h-4zM5%2013v1.5h11V13H5zm0%203.5V18h11v-1.5H5zM19%208h2v10a2%202%200%200%201-2%202V8z'/%3E%3C/svg%3E"); }
/* Snapchat is the one brand whose ground is too light for a white mark:
   #FFFC00 against #FFFFFF is 1.1:1. Any light brand added later needs this too. */
.pt-logo[data-plat="snapchat"] { --pt-ink: #000000; }"""
    )

    # ---- Post-detail modal + Caption-insight themes ----
    # Caption-insight themes: rank chip + name/tag + a caption read, then a 2-up grid
    # of quote cards that each open the shared post-detail modal. The modal is a page
    # singleton (markup + JS live in the brief, once); this ships its CSS.
    # Ported from the Component Gallery. Contract + snippets: SKILL.md.
    parts.append(
        """/* ---- Post-detail modal (shared singleton; markup + JS go in the brief once) ---- */
.post, .post-tile { cursor: pointer; }
.post:focus-visible, .post-tile:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }
body.modal-open { overflow: hidden; }
.post-modal-overlay { display: none; position: fixed; inset: 0; z-index: 1000; background: rgba(0,0,0,.55); padding: 24px; overflow-y: auto; }
.post-modal-overlay.open { display: flex; align-items: flex-start; justify-content: center; }
.post-modal { background: var(--card); color: var(--card-foreground); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg-recipe); max-width: 900px; width: 100%; margin: auto; display: flex; flex-direction: column; max-height: calc(100vh - 48px); overflow: hidden; }
.post-modal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; padding: 22px 28px; border-bottom: 1px solid var(--border); flex: none; }
.post-modal-head .pm-eyebrow { display: block; font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: .02em; color: var(--primary); margin-bottom: 4px; }
.post-modal-head .handle { font-size: var(--font-size-h2); line-height: var(--font-line-height-h2); font-weight: var(--font-bold); color: var(--foreground); }
.post-modal-close { flex: none; width: 36px; height: 36px; border: 0; background: var(--secondary); color: var(--foreground); font-size: 22px; line-height: 1; cursor: pointer; border-radius: var(--radius); display: inline-flex; align-items: center; justify-content: center; }
.post-modal-close:hover { background: var(--muted); }
.post-modal-body { display: grid; grid-template-columns: 340px 1fr; min-height: 0; overflow: hidden; }
.pm-media { background: var(--muted); border-right: 1px solid var(--border); display: flex; align-items: center; justify-content: center; padding: 24px; }
.pm-media img { width: 100%; border-radius: var(--radius); display: block; }
.pm-media-ph { width: 88px; height: 112px; border: 1px solid var(--border); border-radius: var(--radius-sm); background: var(--card); display: flex; align-items: center; justify-content: center; color: var(--muted-foreground); }
.pm-content { padding: 22px 28px; overflow-y: auto; min-height: 0; }
.pm-tabs { display: flex; gap: 4px; background: var(--muted); padding: 4px; border-radius: var(--radius); margin-bottom: 18px; }
.pm-tab { flex: 1; justify-content: center; border: 0; background: transparent; color: var(--muted-foreground); font: inherit; font-size: var(--font-size-14); font-weight: var(--font-semibold); padding: 7px 14px; border-radius: var(--radius-md); cursor: pointer; display: inline-flex; align-items: center; gap: 7px; }
.pm-tab.active { background: var(--card); color: var(--foreground); box-shadow: var(--shadow-sm-recipe); }
.pm-tab .tab-count { font-size: var(--font-size-12); font-weight: var(--font-semibold); color: var(--muted-foreground); background: var(--background); border-radius: var(--radius-full); padding: 1px 8px; }
.pm-tab.active .tab-count { background: var(--muted); color: var(--foreground); }
.pm-panel { display: none; } .pm-panel.active { display: block; }
.pm-section + .pm-section { margin-top: 18px; }
.pm-section .pm-label { font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: .02em; color: var(--primary); margin-bottom: 6px; }
.pm-section p { font-size: var(--font-size-15); line-height: var(--font-line-height-15); color: var(--card-foreground); }
.pm-highlights { margin: 0; padding-left: 18px; list-style: disc; } .pm-highlights li { font-size: var(--font-size-15); line-height: var(--font-line-height-15); margin-bottom: 10px; color: var(--card-foreground); }
.pm-caption { font-size: var(--font-size-15); line-height: var(--font-line-height-15); color: var(--card-foreground); white-space: pre-wrap; }
.post-modal-foot { display: flex; align-items: center; justify-content: flex-end; gap: 16px; padding: 16px 28px; border-top: 1px solid var(--border); flex: none; }
.post-modal-foot .post-modal-link { color: var(--primary); font-weight: var(--font-semibold); text-decoration: none; font-size: var(--font-size-15); }
.post-modal-foot .post-modal-link:hover { text-decoration: underline; }
@media (max-width: 720px) { .post-modal-body { grid-template-columns: 1fr; } .pm-media { border-right: 0; border-bottom: 1px solid var(--border); } }

/* ---- Caption-insight themes (rank chip + caption read + clickable quote grid) ---- */
/* Boxless, like the other two ranked-theme presentations: items sit on the section
   surface and a bottom hairline carries the ranking. The rank marker is the shared
   .theme-rank chip, hung in a left gutter so the body text aligns down the list. */
.ci-list { display: flex; flex-direction: column; gap: 0; margin: 12px 0; }
.ci-card { display: flex; gap: 20px; border: 0; border-radius: 0; background: transparent; box-shadow: none; padding: 20px 0; border-bottom: 1px solid var(--border); }
.ci-card:last-child { border-bottom: none; }
/* Look comes from .theme-rank above; only what is local to this layout stays
   here. align-self keeps the 26px circle from stretching to the row height as
   a flex child of .ci-card, and the 1px nudge sits it on the heading's optical
   centre. */
.ci-num { line-height: 1; align-self: flex-start; margin-top: 1px; }
.ci-body { flex: 1; min-width: 0; }
.ci-head { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 8px; } .ci-head .tag { margin: 0; }
.ci-name { font-size: var(--font-size-h3); line-height: var(--font-line-height-h3); font-weight: var(--font-bold); color: var(--foreground); }
.ci-text { font-size: var(--font-size-15); line-height: var(--font-line-height-15); color: var(--card-foreground); } .ci-text strong { font-weight: var(--font-bold); color: var(--foreground); }
.ci-quotes { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 18px; }
/* display: flex is for .cq-more below, which pins to the card's floor. */
.ci-quote { display: flex; flex-direction: column; border: 1px solid var(--border); border-left: 3px solid var(--primary); border-radius: var(--radius-sm); padding: 14px 16px; background: var(--card); cursor: pointer; transition: border-color .15s, box-shadow .15s, transform .15s; }
.ci-quote:hover { box-shadow: var(--shadow-sm-hover-recipe); transform: translateY(-1px); }
.ci-quote:focus-visible { outline: 2px solid var(--ring); outline-offset: 2px; }
.ci-quote .cq-handle { display: block; font-size: var(--font-size-13); font-weight: var(--font-bold); color: var(--foreground); margin-bottom: 4px; }
.ci-quote .cq-text { font-size: var(--font-size-14); line-height: var(--font-line-height-15); font-style: italic; color: var(--foreground); }
/* ON THE CARD FLOOR, not under the quote. The grid stretches both cards in a
   row to the taller one, so a short quote left its link floating mid-card with
   dead space beneath while its neighbour's link sat at the bottom. margin-top:
   auto puts every link on the same line across the row, which is what makes
   the stretch read as alignment rather than as a gap. */
.ci-quote .cq-more { display: block; margin-top: auto; padding-top: 8px; font-size: var(--font-size-13); font-weight: var(--font-semibold); color: var(--primary); }
@media (max-width: 760px) { .ci-quotes { grid-template-columns: 1fr; } }
"""
    )

    # ---- Insight / callout ----
    # A bordered callout for a single takeaway: a colored left rule keyed to sentiment
    # (default/accent-2/accent-3/warn/neg), an optional .tag above, one or two short
    # paragraphs. .insight-grid holds a 2-up set of small .insight-card takeaways.
    # Uses the shared .tag badge. Ported from the Component Gallery.
    # Markup contract + rules: SKILL.md "Insight / callout"; reference: example.html.
    parts.append(
        """/* ---- Insight / callout (bordered takeaway; + 2-up insight grid) ---- */
.insight-box { background: var(--card); color: var(--card-foreground); border: 1px solid var(--border); border-left: 4px solid var(--primary); border-radius: 0 var(--radius) var(--radius) 0; padding: 20px 24px; margin: 16px 0; box-shadow: var(--shadow-sm-recipe); }
.insight-box.accent-2 { border-left-color: var(--color-purple-700); } .insight-box.accent-3 { border-left-color: var(--color-green-700); }
.insight-box.warn { border-left-color: var(--color-orange-700); } .insight-box.neg { border-left-color: var(--destructive); }
.insight-box p { font-size: var(--font-size-15); line-height: var(--font-line-height-15); margin: 0; } .insight-box p + p { margin-top: 8px; }
.insight-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; margin: 20px 0; }
.insight-card { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius); padding: 20px; box-shadow: var(--shadow-sm-recipe); }
.insight-card h4 { font-size: var(--font-size-15); font-weight: var(--font-bold); margin: 8px 0 6px; } .insight-card p { font-size: var(--font-size-14); color: var(--muted-foreground); margin: 0; }
@media (max-width: 760px) { .insight-grid { grid-template-columns: 1fr; } }
"""
    )

    # ---- Reduced motion ----
    # LAST BLOCK IN THE STYLESHEET, deliberately. The cascade is not what makes it
    # win -- !important does that -- but anything appended after it would be read
    # by a maintainer as "outside the reduced-motion rules", which is a trap.
    #
    # WHAT IT NEUTRALISES, AND WHAT IT DOES NOT. Durations only. It does not strip
    # `transform`, and that is the whole point of writing this by hand rather than
    # pasting the usual blanket reset:
    #
    #   .methodology[open] summary::before { transform: rotate(90deg); }
    #   .accordion  details[open] summary::before { transform: rotate(90deg); }
    #
    # Those two rotations are not decoration. They are the only thing that tells a
    # reader the disclosure is open -- the caret is a U+25B8 glyph, so with the
    # transform removed an open Methodology section looks exactly like a closed
    # one. A reset that kills `transform` to honour a motion preference would
    # therefore destroy a state indicator for the users asking for the
    # accommodation. Zeroing the duration gets the real win: the caret snaps
    # instead of sweeping, and still points the right way.
    #
    # The hover lifts (`translateY(-2px)` on cards and posts) are kept for the
    # same reason in miniature: a static 2px offset is a hover affordance, not
    # motion. Reduced motion means "don't animate at me", not "remove feedback".
    #
    # scroll-behavior IS reverted, and it is the one that matters most here: a
    # smooth-scrolled jump from a rail click travels the full height of a long
    # brief, which is the classic vestibular trigger. It is also reset on `html`
    # specifically because that is where quid.css sets it, and the `*` rule below
    # cannot reach it with the needed specificity on every engine.
    #
    # .01ms rather than 0s: a zero duration can skip transitionend/animationend
    # in some engines, so script that waits on those events silently stalls.
    # Nothing here listens for them today; the idiom costs nothing and removes
    # the trap for whatever consumes this stylesheet later.
    parts.append(
        """/* ---- Chart card (boxed container for a plotted figure) ---- */
/* For a chart, graph or wordcloud -- anything with a plot area, axis labels or
   a legend. NOT for tables: those use .table-wrap, which is deliberately a
   different treatment (top/bottom hairline, no side borders, no radius, no
   shadow) because a table's header and row rules already bound it. Boxing a
   table puts a second boundary round something already bounded.

   The one surface in the modern shell that KEEPS its box. Sections are boxless
   there and the tinted page canvas is switched off, so a figure sitting loose on
   the page has no edge of its own: its plot area, axis labels and legend read as
   part of the prose around them. The card gives it that edge.

   Same four declarations as .quid-card, not a second card style. Do not swap the
   fill for a hand-picked hex -- in dark mode --card and --background are both
   #212121 and the border carries the whole boundary, which is the intended
   behaviour and the reason the border is not optional.

   .chart-box is the sized wrapper Chart.js needs: a canvas with no positioned
   parent of fixed height grows on every resize. Height is a plain value here,
   so override it inline for a chart that needs more room.

   Colors come from the --chart-* / --sentiment-* tokens, read at runtime --
   see components/chart-palette.md. This block is chrome only; it sets nothing
   about the series. */
.chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin: 20px 0; }
.chart-card {
  background: var(--card);
  color: var(--card-foreground);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm-recipe);
  padding: 20px;
}
.chart-card .chart-title { margin: 0 0 2px; }
.chart-card .chart-sub { margin: 0 0 14px; font-size: var(--font-size-13); line-height: var(--font-line-height-15); color: var(--muted-foreground); }
.chart-card .chart-box { position: relative; height: 260px; }
"""
    )

    parts.append(
        """/* ---- Reduced motion (honours prefers-reduced-motion: reduce) ---- */
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
"""
    )

    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    import sys
    css = build()
    notes = getattr(build, "collision_notes", [])
    OUT.write_text(css)
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")
    if notes:
        print(f"\nWARNING  {len(notes)} token name collision(s) in the Figma source:")
        for n in notes:
            print(f"  - {n}")
        print("  Resolved deterministically, not by emit order. Fix at the source:")
        print("  rename the mismatched leaves in Figma so each leaf is unique.")
        if "--strict" in sys.argv:
            raise SystemExit("FAIL  --strict: refusing to ship with unresolved collisions.")


if __name__ == "__main__":
    main()
