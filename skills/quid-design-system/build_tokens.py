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
    return part.lower().replace(" ", "-").replace(":", "-").replace("/", "-")


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
    radius_lines: list[str] = []
    for path, tok in walk(primitives):
        if tok["$type"] != "number":
            continue
        # primitives.tokens.json contains both radius (px) and state (opacity %).
        if path[0].startswith("radius"):
            name = f"--{slug(path[1:] or path)}"
            val = tok["$value"]
            if isinstance(val, float) and not val.is_integer():
                val_str = f"{round(val, 4)}px"
            elif val >= 1000:
                val_str = f"{int(val)}px"
            else:
                val_str = f"{int(val)}px"
            radius_lines.append(f"  {name}: {val_str};")
        elif path[0] == "state":
            radius_lines.append(f"  --opacity-{slug(path[1:])}: {tok['$value']}%;")
    root.append(section("radius & state primitives", radius_lines))

    # Typography (desktop). Emit using only the leaf token name — the Figma leaves
    # already carry the prefix (font-sans, font-size-14, font-line-height-h1, font-bold, ...).
    type_lines: list[str] = []
    for path, tok in walk(type_desktop["font-family"]):
        if tok["$type"] == "string":
            type_lines.append(
                f"  --{_clean(path[-1])}: {tok['$value']}, ui-sans-serif, system-ui, sans-serif;"
            )
    for cat in ("font-size", "line-height"):
        for path, tok in walk(type_desktop[cat]):
            type_lines.append(f"  --{_clean(path[-1])}: {int(tok['$value'])}px;")
    for path, tok in walk(type_desktop["font-weight"]):
        type_lines.append(f"  --{_clean(path[-1])}: {int(tok['$value'])};")
    root.append(section("typography (desktop default)", type_lines))

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

    css = ":root {\n" + "\n\n".join(root) + "\n}\n"
    parts.append(css)

    # ---- .dark / [data-theme=\"dark\"] override ----
    dark_lines: list[str] = []
    dark_lines.append(section("semantic colors (dark)", color_vars(sys_dark, "")))
    dark_lines.append(section("shadow rgba (dark)", color_vars(shadow_dark, "")))
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
  font-feature-settings: "cv11", "ss03";
}

h1, h2, h3, h4, h5, h6 { margin: 0; font-weight: var(--font-headings); color: var(--foreground); }

.quid-hero,
.quid-h0   { font-size: var(--font-size-h0); line-height: var(--font-line-height-h0); font-weight: var(--font-h0); letter-spacing: -0.02em; }
.quid-h1   { font-size: var(--font-size-h1); line-height: var(--font-line-height-h1); font-weight: var(--font-headings); letter-spacing: -0.015em; }
.quid-h2,
.quid-subtitle,
.quid-pull-quote { font-size: var(--font-size-h2); line-height: var(--font-line-height-h2); font-weight: var(--font-headings); letter-spacing: -0.01em; }
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

    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    OUT.write_text(build())
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
