#!/usr/bin/env python3
"""
match_macbeth_critics.py
========================
Make every critics/bibliography list in index.html match Macbeth's exact
structure, styling, and entry format.

Macbeth gold-standard pattern
-----------------------------
Container:
    <div class="critics-list" style="max-height: 50vh; overflow-y: auto;
         background: #f9f9f9; padding: 20px; border-radius: 8px;
         border: 1px solid #e5e7eb;">
        <div>
            <p>"Author, Last: Title. Place, Year"</p>
            ...
        </div>
    </div>

Rules enforced:
1. Container style → exact Macbeth style (50vh scroll).
2. No <p><strong>…</strong></p> section headings — flat list only.
3. Every <p> entry wrapped in outer quotes: <p>"…"</p>
4. Author in "Last, First" or "Last, Initials:" colon format.
5. Inner article titles use &quot;…&quot;
6. HTML entities correct (&amp; &lt; &gt; &quot;).

Usage:
    python3 scripts/match_macbeth_critics.py                 # dry-run
    python3 scripts/match_macbeth_critics.py --apply          # write changes
    python3 scripts/match_macbeth_critics.py --apply --backup # write + .bak
"""
from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# ---------------------------------------------------------------------------
# Macbeth's exact container style
# ---------------------------------------------------------------------------
MACBETH_STYLE = (
    'max-height: 50vh; overflow-y: auto; background: #f9f9f9; '
    'padding: 20px; border-radius: 8px; border: 1px solid #e5e7eb;'
)

# ---------------------------------------------------------------------------
# Regex to find every critics-list div with its style attribute
# ---------------------------------------------------------------------------
CRITICS_DIV_RE = re.compile(
    r'(<div\s+class="critics-list"\s+style=")([^"]*?)(")',
    re.I,
)

# ---------------------------------------------------------------------------
# Author normalisation helpers (from the earlier script, refined)
# ---------------------------------------------------------------------------
SKIP_FLIP = re.compile(
    r'(?:^(?:Mrs|Miss|Sir|Lord|Lady|Rev|Dr|Prof|The|St|De|Von|Van)\b'
    r'|and\s|,|\[|\]|Anonymous)',
    re.I,
)

def flip_name(name: str) -> str:
    """Turn 'First Last' into 'Last, First' when safe."""
    name = name.strip()
    if not name or SKIP_FLIP.search(name):
        return name
    parts = name.split()
    if len(parts) == 2:
        return f"{parts[1]}, {parts[0]}"
    return name


def has_author_colon(text: str) -> bool:
    idx = text.find(":")
    return 0 < idx < len(text) - 1


def normalise_entry(raw: str) -> str:
    """
    Normalise a single bibliography entry to Macbeth style.
    Returns the inner text (without outer quotes — caller adds those).
    """
    text = raw.strip()
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = html.unescape(text)

    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1].strip()

    if not text:
        return text

    if has_author_colon(text):
        ci = text.index(":")
        author = text[:ci].strip()
        rest = text[ci + 1:].strip()

        if re.match(r'^(anonymous|\[anonymous\])$', author, re.I):
            author = "[Anonymous]"
        elif "," not in author:
            author = flip_name(author)

        out = f"{author}: {rest}"
    else:
        out = text

    return escape_for_p(out)


def escape_for_p(logical: str) -> str:
    """Escape for safe HTML inside <p>"…"</p>."""
    return (
        logical
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# ---------------------------------------------------------------------------
# Process inner HTML of a critics-list <div><div>…</div></div>
# ---------------------------------------------------------------------------
P_RE = re.compile(r'<p(\s[^>]*)?>(.+?)</p>', re.I | re.S)
STRONG_RE = re.compile(r'^\s*<strong[^>]*>.*?</strong>\s*$', re.I | re.S)
NOTFOUND_RE = re.compile(r'^\s*NOT\s*FOUND\s*$', re.I)


def process_critics_block(inner_html: str) -> Tuple[str, int, int, int]:
    """
    Process the content inside a critics-list inner <div>.
    Returns (new_html, total_entries, changed_entries, removed_headings).
    """
    parts: List[str] = []
    last_end = 0
    total = 0
    changed = 0
    removed = 0

    for m in P_RE.finditer(inner_html):
        parts.append(inner_html[last_end:m.start()])
        last_end = m.end()

        attrs = m.group(1) or ""
        body = m.group(2)

        if STRONG_RE.match(body):
            removed += 1
            continue

        if NOTFOUND_RE.match(re.sub(r'<[^>]+>', '', body)):
            parts.append(m.group(0))
            total += 1
            continue

        total += 1
        plain = re.sub(r'<[^>]+>', '', body)
        plain = html.unescape(plain.strip())

        if plain.startswith('"') and plain.endswith('"'):
            plain = plain[1:-1].strip()

        if not plain:
            parts.append(m.group(0))
            continue

        normalised = normalise_entry(plain)
        new_p = f'<p>"{normalised}"</p>'

        if new_p != m.group(0):
            changed += 1

        parts.append(new_p)

    parts.append(inner_html[last_end:])
    return "".join(parts), total, changed, removed


# ---------------------------------------------------------------------------
# Find critics-list blocks via nesting
# ---------------------------------------------------------------------------
CRITICS_OPEN_RE = re.compile(
    r'<div\s+class="critics-list"[^>]*>\s*<div[^>]*>', re.I
)


def find_inner_div_spans(text: str) -> List[Tuple[int, int]]:
    """Return (start, end) spans for the inner <div> content of each critics-list."""
    spans = []
    pos = 0
    while True:
        m = CRITICS_OPEN_RE.search(text, pos)
        if not m:
            break
        inner_start = m.end()
        depth = 1
        i = inner_start
        while i < len(text) and depth > 0:
            if text[i:i+4] == '<div':
                depth += 1
                close = text.find('>', i)
                i = close + 1 if close != -1 else len(text)
            elif text[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    spans.append((inner_start, i))
                i += 6
            else:
                i += 1
        pos = i
    return spans


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run(path: Path, apply: bool, backup: bool) -> int:
    text = path.read_text(encoding='utf-8')
    original = text

    # ------------------------------------------------------------------
    # Step 1: Fix all critics-list container styles to match Macbeth
    # ------------------------------------------------------------------
    style_fixes = 0
    def replace_style(m: re.Match) -> str:
        nonlocal style_fixes
        old_style = m.group(2)
        if old_style.strip().rstrip(';') != MACBETH_STYLE.rstrip(';'):
            style_fixes += 1
        return m.group(1) + MACBETH_STYLE + m.group(3)

    text = CRITICS_DIV_RE.sub(replace_style, text)

    # ------------------------------------------------------------------
    # Step 2: Process each inner block — remove headings, normalise entries
    # ------------------------------------------------------------------
    spans = find_inner_div_spans(text)
    total_entries = 0
    total_changed = 0
    total_headings_removed = 0

    chunks: List[str] = []
    prev = 0
    for start, end in spans:
        chunks.append(text[prev:start])
        block = text[start:end]
        new_block, entries, ch, rm = process_critics_block(block)
        total_entries += entries
        total_changed += ch
        total_headings_removed += rm
        chunks.append(new_block)
        prev = end
    chunks.append(text[prev:])
    text = "".join(chunks)

    # ------------------------------------------------------------------
    # Step 3: Fix the JS template block style too (line ~15701)
    # ------------------------------------------------------------------
    js_pattern = re.compile(
        r'(<div\s+class="critics-list"\s+style=")([^"]*?)(")',
        re.I,
    )
    text = js_pattern.sub(
        lambda m: m.group(1) + MACBETH_STYLE + m.group(3),
        text,
    )

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------
    print(f"Critics-list blocks found:    {len(spans)}")
    print(f"Container styles fixed:       {style_fixes}")
    print(f"Section headings removed:     {total_headings_removed}")
    print(f"Total <p> entries:            {total_entries}")
    print(f"Entries normalised/changed:   {total_changed}")

    if text == original:
        print("\nNo changes needed — file already matches Macbeth style.")
        return 0

    if not apply:
        print("\n[DRY RUN] No changes written. Use --apply to write.")
        return 0

    if backup:
        bak = path.with_suffix(path.suffix + '.bak2')
        shutil.copy2(path, bak)
        print(f"\nBackup: {bak}")

    path.write_text(text, encoding='utf-8')
    print(f"Wrote: {path}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('index_html', nargs='?', type=Path,
                    default=Path(__file__).resolve().parents[1] / 'index.html',
                    help='Path to index.html (default: repo root)')
    ap.add_argument('--apply', action='store_true',
                    help='Actually write changes (default is dry-run)')
    ap.add_argument('--backup', action='store_true',
                    help='Save .bak2 before writing')
    args = ap.parse_args()

    if not args.index_html.is_file():
        print(f"Not found: {args.index_html}", file=sys.stderr)
        return 1
    return run(args.index_html, args.apply, args.backup)


if __name__ == '__main__':
    sys.exit(main())
