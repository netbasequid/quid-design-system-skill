#!/usr/bin/env python3
"""Generate example-modern.html: the component catalog inside the modern shell.

    python3 build_example_modern.py

WHY THIS EXISTS. example.html demonstrates every component in a flat gallery of
`<section class="quid-card">` blocks — no .body-layout, no rail, no hero. That
shows what a component looks like on its own, and nothing about how it behaves
in a page. With one shell that was a small gap. With two it is a real one: the
modern shell makes sections BOXLESS, and every component was designed sitting
inside a card. Whether they still read without one is a question the catalog
could not answer, and a question each author would otherwise answer alone, by
building a page and looking at it.

WHY GENERATED RATHER THAN HAND-WRITTEN. A second catalog with the components
copied into it would drift from the first the moment anyone edited a demo, and
the drift would be silent. This reads example.html at build time, so there is
one source for the component markup and a guaranteed-identical second view of
it. Same arrangement as quid.css and build_tokens.py: edit the source, re-run
the script, commit the output.

WHAT IT DOES. Lifts the inner markup of each `<section class="quid-card">` out
of its card and drops it into a `<section class="section">` inside a full
modern shell — masthead, right-hand rail with a working scroll-spy, boxless
sections, the .brief-modern gate on <body>. Nothing about the demos is edited;
only the wrapper around them changes.

IT ALSO LIFTS THE PAGE-LEVEL MACHINERY, and that is not an afterthought. Half
the components in this catalog are inert without something that lives OUTSIDE
the tiles: .post, .ci-quote and .large-card open the post-detail modal, which
is a single overlay at the end of <body> plus a delegated click handler, and
the Twitter/TikTok/Reddit embeds only become embeds once their widget scripts
run. An earlier version of this script copied the tiles and nothing else, so
the generated catalog had seventeen clickable elements that silently did
nothing and three embeds that stayed blockquotes. Everything between </main>
and </body> is therefore copied verbatim, as a region rather than as a list of
known pieces — so machinery added to example.html later arrives here without
anyone remembering to update this script.

RE-RUN IT AFTER: adding or renaming a component demo in example.html, adding
page-level script or markup to it, or changing quid-modern-shell.css in a way
that affects .section.
"""
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).parent
SRC = HERE / "example.html"
SHELL_SRC = HERE / "shell-modern-example.html"
OUT = HERE / "example-modern.html"


def demo_blocks(html):
    """(name, inner markup) for each `<section class="quid-card">`.

    Balanced-tag scan rather than a lazy regex: several demos nest their own
    <section> elements, and taking the first </section> would truncate them
    mid-component. An earlier version of this assumed <div> and silently
    extracted nothing, which is why the count is asserted below.
    """
    out = []
    for m in re.finditer(r'<section class="quid-card"[^>]*>', html):
        start, depth, i = m.end(), 1, m.end()
        tag = re.compile(r"<(/?)section\b")
        while depth and i < len(html):
            k = tag.search(html, i)
            if not k:
                break
            depth += -1 if k.group(1) else 1
            i = k.end()
        inner = html[start:i - len("</section>")]
        h = re.search(r"<h[23][^>]*>(.*?)</h[23]>", inner, re.S)
        name = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", h.group(1))).strip() if h else "Component"
        out.append((name, inner))
    return out


def grab(pattern, text, what):
    m = re.search(pattern, text, re.S)
    if not m:
        print(f"FAIL  could not find {what}", file=sys.stderr)
        sys.exit(1)
    return m.group(1)


def main():
    src = SRC.read_text(encoding="utf-8")
    blocks = demo_blocks(src)
    if len(blocks) < 10:
        print(f"FAIL  extracted only {len(blocks)} demos from example.html; "
              f"the markup shape has changed and this script needs updating",
              file=sys.stderr)
        return 1

    # The demo markup leans on a few scaffolding classes example.html defines
    # inline (.row, .swatch, .grid). Carry them over or several demos collapse.
    helpers = grab(r"<style>(.*?)</style>", src, "example.html's helper styles")
    # Drop .page: it centres a narrow column, which fights the shell's own layout.
    helpers = re.sub(r"\.page\s*\{[^}]*\}\s*", "", helpers)

    spy = grab(r"<script\b[^>]*>(.*?)</script>", SHELL_SRC.read_text(encoding="utf-8"),
               "the scroll-spy script in shell-modern-example.html")

    # Everything after the content and before </body>: embed widget loaders, the
    # post-detail modal overlay, and the modal's delegated click handler. Taken
    # as one region on purpose -- see the module docstring.
    machinery = grab(r"</main>(.*?)</body>", src, "the page-level region between </main> and </body>")

    # The modal is the reason this region matters, so prove it came across
    # rather than trusting the slice. A silent miss here looks exactly like a
    # working catalog until someone clicks a post.
    for needle, what in [('id="postModal"', "the modal overlay markup"),
                         ("getElementById('postModal')", "the modal's open/close script"),
                         ("script.post-data", "the modal's per-post data reader")]:
        if needle not in machinery:
            print(f"FAIL  {what} is missing from the lifted region; "
                  f"example.html's structure has changed", file=sys.stderr)
            return 1

    nav, secs = [], []
    for n, (name, inner) in enumerate(blocks, 1):
        sid = "sec-%d" % n
        active = ' class="active"' if n == 1 else ""
        nav.append('        <a href="#%s"%s>%s</a>' % (sid, active, name))
        secs.append(
            '            <section class="section" id="%s">\n'
            '              <p class="section-label">%s</p>\n'
            "%s\n"
            "            </section>" % (sid, name, inner.rstrip()))

    doc = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Quid Design System — components in the modern shell</title>
    <link rel="preconnect" href="https://rsms.me/" />
    <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
    <link rel="stylesheet" href="./quid.css" />
    <link rel="stylesheet" href="./quid-fonts.css" />
    <link rel="stylesheet" href="./quid-modern-shell.css" />
    <!--
      GENERATED by build_example_modern.py from example.html. Do not hand-edit;
      re-run the script.

      Every component from the catalog, shown where it actually lives: inside a
      boxless `section.section` in the modern shell. example.html shows the same
      components bare, in a card, which answers what they look like but not how
      they behave in a page.

      This file LINKS its stylesheets because it is opened from the repo. A
      DELIVERED brief must inline them instead — see "How to apply" in SKILL.md.
    -->
    <style>
%s    </style>
  </head>

  <body class="with-sidenav brief-modern">
    <div class="body-layout">
      <header class="hero">
        <div class="container-brief">
          <div class="hero-card">
            <div class="bb-text">
              <h1 class="quid-hero">Components In The Modern Shell</h1>
              <p class="lede">Every demo from example.html, lifted out of its card and placed in a boxless section. Same markup, different container.</p>
              <dl class="hero-meta">
                <div class="hm-item"><dt>Shell</dt><dd>Modern</dd></div>
                <div class="hm-item"><dt>Components</dt><dd>%d</dd></div>
              </dl>
            </div>
          </div>
        </div>
      </header>

      <div class="page-row">
        <nav class="sidenav" aria-label="On this page">
          <p class="sidenav-title">On this page</p>
%s
        </nav>

        <div class="main">
          <div class="container-brief">
            <div class="brief-body">
%s
            </div>
          </div>
        </div>
      </div>
    </div>
%s
    <script>
%s
    </script>
  </body>
</html>
""" % (helpers, len(blocks), "\n".join(nav), "\n".join(secs), machinery.rstrip(), spy)

    OUT.write_text(doc, encoding="utf-8")
    print("PASS  wrote %s: %d components in boxless sections, %s bytes"
          % (OUT.name, len(blocks), format(len(doc), ",")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
