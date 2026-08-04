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
.embed-note { font-size: var(--font-size-13); line-height: var(--font-line-height-15); color: var(--muted-foreground); margin-top: 16px; max-width: 70ch; }
"""
    )

    # ---- Shell (page scaffold / container) ----
    # The full-page container every multi-section brief is built on: a sticky
    # side-nav rail beside the main column (hero + a .brief-body slot of
    # <section> blocks + a methodology footer). Catalog components (KPI, charts,
    # posts, embeds, tables) compose INSIDE the .brief-body sections — the shell
    # is the frame, not the content.
    # Markup contract + scroll-spy JS + nav-label rule: SKILL.md "The Shell";
    # full-page reference: shell-example.html.
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
.sidenav-title { font-size: var(--font-size-12); font-weight: var(--font-bold); letter-spacing: 0.02em; color: var(--muted-foreground); margin-bottom: 12px; padding: 0 12px; }
.sidenav nav { display: flex; flex-direction: column; gap: 2px; }
.sidenav a { display: block; padding: 8px 12px; border-left: 2px solid transparent; border-radius: 0 var(--radius-sm) var(--radius-sm) 0; font-size: var(--font-size-14); line-height: var(--font-line-height-14); font-weight: var(--font-medium); color: var(--foreground); text-decoration: none; transition: color .15s, border-color .15s, background-color .15s; }
.sidenav a:hover { color: var(--primary); background: var(--secondary); }
.sidenav a.active { color: var(--primary-container-foreground); border-left-color: var(--primary); font-weight: var(--font-semibold); background: var(--primary-container-background); }

/* ---- Shell: hero / lede ---- */
/* DEFAULT hero is the dark Quid gradient with white text. Add class="has-img" and set
   --hero-img inline to layer a photo behind the dark overlay. Add class="light" for the
   pale primary-container hero instead. */
.hero { padding: 32px 0 0; text-align: left; }
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
.hero .lede { font-size: var(--font-size-16); line-height: var(--font-line-height-16); max-width: 680px; margin: 0; }

/* ---- Shell: section primitives (structure the .brief-body slot) ---- */
.section { background: var(--card); border: 1px solid var(--border); border-radius: var(--radius-lg); box-shadow: var(--shadow-sm-recipe); padding: 32px; margin-bottom: 24px; scroll-margin-top: 24px; }
.section-label { font-size: var(--font-size-12); font-weight: var(--font-bold); text-transform: uppercase; letter-spacing: 0.02em; color: var(--primary); margin-bottom: 6px; }
.section > h2 { margin-bottom: 6px; }
.section > .section-sub { font-size: var(--font-size-15); color: var(--muted-foreground); margin-bottom: 24px; }
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

/* ---- Shell: methodology footer ---- */
.methodology { max-width: 900px; }
.methodology p { font-size: var(--font-size-13); color: var(--muted-foreground); line-height: var(--font-line-height-15); }
.methodology p + p { margin-top: 8px; }
"""
    )

    # ---- KPI strip (optional metric cards) ----
    # Primary top-accent metric cards: label over big value, optional up/down delta
    # with a comparison-window period. Ported verbatim from the Component Gallery.
    # Markup contract + rules: SKILL.md "KPI strip"; reference: example.html "KPI strip".
    parts.append(
        r"""/* ---- KPI strip (optional; primary top-accent metric cards) ---- */
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px,1fr)); gap: 16px; margin: 24px 0; }
.kpi-card { background: var(--card); color: var(--card-foreground); border: 1px solid var(--border); border-top: 3px solid var(--primary); border-radius: var(--radius); padding: 20px 16px; text-align: center; box-shadow: var(--shadow-sm-recipe); }
.kpi-card .label { font-size: var(--font-size-12); font-weight: var(--font-semibold); text-transform: uppercase; letter-spacing: 0.02em; color: var(--muted-foreground); margin-bottom: 8px; }
.kpi-card .value { font-size: var(--font-size-h1); font-weight: var(--font-bold); line-height: 1.1; }
.kpi-card .delta { display: inline-flex; align-items: center; gap: 4px; font-size: var(--font-size-13); font-weight: var(--font-regular); margin-top: 2px; }
.kpi-card .delta::before { font-size: 0.8em; line-height: 1; }   /* directional triangle */
.kpi-card .delta.up { color: var(--color-green-700); } .kpi-card .delta.up::before { content: "\25B2"; }   /* up */
.kpi-card .delta.down { color: var(--destructive); } .kpi-card .delta.down::before { content: "\25BC"; }   /* down */
.kpi-card .delta .period { color: var(--muted-foreground); }   /* optional "vs ..." window, inline after the delta */
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
.theme-rank { flex: none; width: 26px; height: 26px; border-radius: var(--radius-full); background: var(--primary-container-background); color: var(--primary-container-foreground); font-size: var(--font-size-13); font-weight: var(--font-bold); display: inline-flex; align-items: center; justify-content: center; }
.theme-name { font-size: var(--font-size-h3); font-weight: var(--font-bold); color: var(--foreground); }
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

    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    OUT.write_text(build())
    print(f"Wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
