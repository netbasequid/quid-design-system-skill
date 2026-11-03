#!/usr/bin/env python3
"""Check that a brief is safe to deliver as a single file.

    python3 check_delivery.py brief.html

A delivered brief is one HTML file. Readers open it from an inbox, a download
folder, or Terminal, never from the directory it was authored in, so any
reference to a sibling file resolves on the author's machine and nowhere else.
The brief looks correct to the person who made it and wrong to everybody else,
with nothing in the console a reader would notice.

WHY THIS IS A SCRIPT AND NOT A grep. The check this replaces was:

    grep -nE '(href|src)="(?!https?://|data:|#)' brief.html

`(?!...)` is a negative lookahead, which is PCRE, not POSIX ERE. BSD grep on
macOS rejects it, and so does ugrep, which is what `grep` resolves to on many
macOS setups. `grep -P` is not a portable fallback: stock BSD grep has no -P at
all.

The failure is silent in the worst way. grep exits 2 and prints the error on
stderr, while a clean brief exits 1 and prints nothing on stdout. An author who
runs the documented command, sees no filenames listed, and concludes "no
relative references" gets the same impression from a check that never ran. That
is a false pass on the single most common way a delivered brief breaks.

This script instead:
  - parses the HTML rather than pattern-matching it, so an attribute containing
    an escaped quote or an entity cannot slip past;
  - states PASS or FAIL in words, so a successful check never looks like a
    failed one;
  - exits 0 on pass, 1 on findings, 2 on its own failure, so the three outcomes
    are distinguishable in CI.

Exit codes:
  0  PASS, every reference is self-contained or absolute
  1  FAIL, at least one reference would break off the author's machine
  2  the check could not run (bad arguments, unreadable file, parse error)
"""
import sys
from html.parser import HTMLParser

# Where a broken reference actually costs something. href/src on these elements
# is fetched at render time; a relative one silently yields an unstyled or
# image-less brief.
WATCHED = {
    "link":   ("href", "stylesheet or icon"),
    "script": ("src",  "JavaScript"),
    "img":    ("src",  "image"),
    "iframe": ("src",  "embed"),
    "source": ("src",  "media source"),
    "video":  ("src",  "video"),
    "audio":  ("src",  "audio"),
}

# Allowed: absolute URLs, inline data, in-page anchors, and protocol-relative
# URLs (which still resolve against a real host, not the filesystem).
ALLOWED_PREFIXES = ("http://", "https://", "data:", "#", "//", "mailto:", "tel:")


class RefCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.findings = []
        self.checked = 0

    def handle_starttag(self, tag, attrs):
        if tag not in WATCHED:
            return
        attr, kind = WATCHED[tag]
        for name, value in attrs:
            if name != attr or not value:
                continue
            self.checked += 1
            v = value.strip()
            if v.lower().startswith(ALLOWED_PREFIXES):
                continue
            self.findings.append((self.getpos()[0], tag, attr, v, kind))


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        print("usage: python3 check_delivery.py brief.html", file=sys.stderr)
        return 2
    path = argv[1]
    try:
        html = open(path, encoding="utf-8", errors="replace").read()
    except OSError as e:
        print(f"ERROR  could not read {path}: {e}", file=sys.stderr)
        return 2

    p = RefCollector()
    try:
        p.feed(html)
        p.close()
    except Exception as e:                                  # noqa: BLE001
        print(f"ERROR  could not parse {path}: {e}", file=sys.stderr)
        return 2

    if p.findings:
        print(f"FAIL  {len(p.findings)} relative reference(s) in {path}.")
        print("      A delivered brief is one file; these resolve only on this machine.\n")
        for line, tag, attr, value, kind in p.findings:
            print(f"      line {line}: <{tag} {attr}=\"{value}\">   ({kind})")
        print("\n      Fix: inline the stylesheet or script, or use an absolute https:// URL.")
        return 1

    print(f"PASS  {path}: {p.checked} reference(s) checked, all self-contained or absolute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
