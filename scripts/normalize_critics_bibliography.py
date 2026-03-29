#!/usr/bin/env python3
"""
Normalize all <div class="critics-list"> bibliography <p> entries in index.html
to match the Macbeth Variorum convention:

  "Surname, Given: Title detail. Place, year."
  "[Anonymous]: ..."
  Article titles use straight double quotes, stored as &quot; inside HTML.

Preserves:
  - <p><strong>...</strong></p> section headings
  - NOT FOUND placeholders
  - Entries that cannot be parsed safely (left unchanged with a warning)

Usage:
  python scripts/normalize_critics_bibliography.py              # writes index.html
  python scripts/normalize_critics_bibliography.py --dry-run   # print stats only
  python scripts/normalize_critics_bibliography.py --backup    # write .bak first

Requires Python 3.8+ (stdlib only).
"""

from __future__ import annotations

import argparse
import html
import re
import shutil
import sys
from pathlib import Path
from typing import Callable, List, Optional, Tuple

# --- Macbeth-style heuristics (aligned with site JS) ------------------------

SURNAME_PREFIXES = frozenset(
    {"de", "von", "van", "di", "du", "la", "le", "del", "delle", "des", "da", "ten", "ter", "den"}
)

TITLE_START_WORDS = frozenset(
    {
        "new", "notes", "few", "die", "der", "das", "seven", "eight", "nine", "ten",
        "introduction", "ethics", "criticism", "antidote", "theatrical", "memorials",
        "strictures", "critical", "remarks", "observations", "history", "life", "works",
        "letters", "lectures", "studies", "inquiry", "text", "glossary", "canons", "essays",
        "supplemental", "old", "some", "shakespeare", "miscellaneous", "more", "prose",
        "index", "account", "notices", "caledonia", "specimens", "memoirs", "illustrations",
        "supplement", "chronicle", "register", "annals", "anecdotes", "literary", "dramatic",
        "philosophical", "variorum", "general", "translation", "treatise", "dissertation",
        "extracts", "outlines", "select", "poems", "collection", "dictionary", "grammar",
        "manual", "handbook", "correspondence", "diary", "journal", "magazine", "review",
        "gazette", "record", "report", "survey", "abstract", "summary", "catalogue",
        "calendar", "selections", "the", "second", "third", "fourth", "fifth",
        "cooper", "cotgrave", "capell", "second", "third", "critical", "review",
    }
)


def _words(s: str) -> List[str]:
    return s.split()


def _is_multi_author_and_safe(parts: List[str]) -> bool:
    """Avoid splitting 'Macbeth and Richard the Third' into fake co-authors."""
    for p in parts:
        pt = p.strip()
        if re.search(r"\bthe (first|second|third|fourth)\b", pt, re.I):
            return False
        if len(_words(pt)) >= 5:
            return False
    return True


def flip_name(name: str) -> str:
    name = name.strip()
    if not name:
        return name
    if re.match(r"^(anonymous|\[anonymous\])$", name, re.I):
        return "[Anonymous]"

    # W. and R. Chambers
    if re.match(r"^W\.\s+and\s+R\.\s+Chambers\b", name, re.I):
        return "Chambers, W. and R."

    if re.search(r"\b(and|et)\b", name, re.I):
        parts = re.split(r"\s+(?:and|et)\s+", name, flags=re.I)
        if _is_multi_author_and_safe(parts):
            out = []
            for p in parts:
                p = p.strip()
                w = p.split()
                if len(w) < 2:
                    out.append(p)
                else:
                    sn = w[-1]
                    if len(w) >= 2 and w[-2].lower() in SURNAME_PREFIXES:
                        sn = w[-2] + " " + sn
                        given = " ".join(w[:-2])
                    else:
                        given = " ".join(w[:-1])
                    out.append(f"{sn}, {given}" if given else sn)
            joiner = ", and " if re.search(r"\band\b", name, re.I) else ", et "
            return joiner.join(out)
        # unsafe: return whole string (caller may treat as title fragment)
        return name

    w = name.split()
    if len(w) < 2:
        return name
    if len(w) >= 2 and w[-2].lower() in SURNAME_PREFIXES:
        surname = w[-2] + " " + w[-1]
        given = " ".join(w[:-2])
    else:
        surname = w[-1]
        given = " ".join(w[:-1])
    return f"{surname}, {given}" if given else surname


def has_author_comma(text: str) -> bool:
    ci = text.find(",")
    if ci == -1:
        return False
    seg = text[:ci].strip()

    if re.search(r"\b[A-Z]\.\s*[A-Z]", seg):
        return True
    if re.search(r"\b[A-Z]\.\s*$", seg):
        return True
    if re.search(r"^[A-Z]\.\s", seg):
        return True
    if re.search(
        r"^(anonymous|\[anonymous\]|lord |sir |prof\.|miss |mrs |dr\.|chevalier |dame |mme |madame |rev\.|bishop |st\.\s)",
        seg,
        re.I,
    ):
        return True
    if re.search(r"\b(and|et)\b", seg, re.I) and seg[:1].isupper() and len(seg) < 50:
        return True

    words = seg.split()
    if 2 <= len(words) <= 4:
        first_w = words[0].rstrip("'s").lower()
        if first_w in TITLE_START_WORDS:
            return False
        all_cap = all(
            (len(x) > 0 and x[0].isupper()) or x.lower() in SURNAME_PREFIXES for x in words
        )
        if all_cap and len(seg) < 40:
            return True
    return False


def normalize_publication_detail(rest: str, active: bool) -> str:
    """
    Prefer Macbeth-like detail: use '.' before common place names when the fragment
    still uses comma after title only. Conservative — only when active.
    """
    if not active:
        return rest.strip()
    r = rest.strip()
    if not r:
        return r
    # 'Title, London, 1870' -> 'Title. London, 1870' when Title has no period
    m = re.match(
        r"^([^.,]{3,80}?),\s*((?:London|Paris|Oxford|Cambridge|Edinburgh|Boston|New York|Philadelphia|Leipzig|Berlin|Wien|Stuttgart|Dublin)[^,]*),(\s*\d{4}|.*)$",
        r,
        re.I,
    )
    if m and "." not in m.group(1):
        title, place, tail = m.group(1), m.group(2), m.group(3)
        return f"{title.strip()}. {place.strip()},{tail}"
    return r


def colon_split(raw: str) -> Tuple[str, str]:
    ci = raw.find(":")
    if ci <= 0:
        return "", raw
    author = raw[:ci].strip()
    rest = raw[ci + 1 :].strip()
    return author, rest


def to_macbeth_colon_line(
    raw: str,
    last_author: Optional[str],
    *,
    enrich_places: bool = False,
    ascii_quotes: bool = False,
) -> Tuple[str, Optional[str], bool]:
    """
    Returns (p_inner_quoted_and_escaped, new_last_author, did_change_logical).
    """
    text = raw.replace("\u201c", '"').replace("\u201d", '"').strip()
    text = html.unescape(text)

    if not text or re.match(r"^not found$", text, re.I):
        return format_p_content(text) if text else '""', last_author, False

    if len(text) >= 2 and text[0] == text[-1] == '"':
        text = text[1:-1].strip()

    logical_in = text
    is_colon = 0 < text.find(":") < len(text) - 1

    if is_colon:
        author_raw, rest = colon_split(text)
        if not author_raw:
            return format_p_content(logical_in), last_author, False
        if re.match(r"^(anonymous|\[anonymous\])$", author_raw, re.I):
            disp = "[Anonymous]"
        elif "," in author_raw:
            disp = author_raw.strip()
        else:
            disp = flip_name(author_raw)
        rest_n = normalize_publication_detail(rest, enrich_places)
        if ascii_quotes:
            rest_n = re.sub(r"'([^']{2,120})'", r'"\1"', rest_n)
        out = f"{disp}: {rest_n}".strip()
        last_author = "[Anonymous]" if re.match(r"^\[anonymous\]$", disp, re.I) else disp
    else:
        if has_author_comma(text):
            ci = text.find(",")
            author_raw = text[:ci].strip()
            rest = text[ci + 1 :].strip()
            disp = flip_name(author_raw)
            rest_n = normalize_publication_detail(rest, enrich_places)
            if ascii_quotes:
                rest_n = re.sub(r"'([^']{2,120})'", r'"\1"', rest_n)
            out = f"{disp}: {rest_n}".strip()
            last_author = "[Anonymous]" if re.match(r"^\[anonymous\]$", disp, re.I) else disp
        else:
            auth = last_author if last_author else "[Anonymous]"
            rest_n = normalize_publication_detail(text, enrich_places)
            if ascii_quotes:
                rest_n = re.sub(r"'([^']{2,120})'", r'"\1"', rest_n)
            out = f"{auth}: {rest_n}".strip()

    changed = out != logical_in
    return format_p_content(out), last_author, changed


def format_p_content(logical: str) -> str:
    """Wrap logical citation; escape for HTML attribute-safe text inside <p>...</p>."""
    esc = (
        logical.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f'"{esc}"'


def process_inner_html(
    inner: str,
    *,
    enrich_places: bool = False,
    ascii_quotes: bool = False,
) -> Tuple[str, int, int]:
    """
    Process one critics-list inner <div> body. Returns (new_inner, changed, total_ps).
    """
    p_re = re.compile(r"<p(\s[^>]*)?>([\s\S]*?)</p>", re.I)
    out_parts: List[str] = []
    last = 0
    changed = 0
    total = 0
    last_author: Optional[str] = None

    for m in p_re.finditer(inner):
        out_parts.append(inner[last : m.start()])
        last = m.end()
        attrs, body = m.group(1) or "", m.group(2)
        total += 1
        low = body.lower()

        if "<strong" in low:
            out_parts.append(m.group(0))
            last_author = None
            continue
        if "not found" in low and len(re.sub(r"\s+", "", body)) < 40:
            out_parts.append(m.group(0))
            last_author = None
            continue

        # visible text (strip tags inside p, rare)
        plain = re.sub(r"<[^>]+>", "", body)
        logical = html.unescape(plain.strip())
        if logical.startswith('"') and logical.endswith('"'):
            logical = logical[1:-1].strip()

        if not logical:
            out_parts.append(m.group(0))
            continue

        new_inner, last_author, did_change = to_macbeth_colon_line(
            logical,
            last_author,
            enrich_places=enrich_places,
            ascii_quotes=ascii_quotes,
        )
        if not did_change:
            out_parts.append(m.group(0))
            continue
        new_line = f"<p{attrs}>{new_inner}</p>"
        changed += 1
        out_parts.append(new_line)

    out_parts.append(inner[last:])
    return "".join(out_parts), changed, total


CRITICS_OPEN = re.compile(
    r'<div\s+class="critics-list"[^>]*>\s*<div\s*>', re.I
)


def iter_critics_sections(html: str) -> List[Tuple[int, int]]:
    """Return list of (inner_start, inner_end) character spans for inner <div> of each critics-list."""
    spans: List[Tuple[int, int]] = []
    pos = 0
    while True:
        m = CRITICS_OPEN.search(html, pos)
        if not m:
            break
        inner_start = m.end()
        depth = 1
        i = inner_start
        while i < len(html) and depth > 0:
            if html.startswith("<div", i):
                depth += 1
                i = html.find(">", i)
                if i == -1:
                    return spans
                i += 1
            elif html.startswith("</div>", i, i + 6):
                depth -= 1
                i += 6
            else:
                i += 1
        inner_end = i - 6
        spans.append((inner_start, inner_end))
        pos = inner_end
    return spans


def normalize_file(
    path: Path,
    dry_run: bool,
    backup: bool,
    *,
    enrich_places: bool,
    ascii_quotes: bool,
) -> int:
    text = path.read_text(encoding="utf-8")
    spans = iter_critics_sections(text)
    if not spans:
        print("No critics-list blocks found.", file=sys.stderr)
        return 1

    total_changed = 0
    total_ps = 0
    new_chunks: List[str] = []
    prev = 0
    for start, end in spans:
        new_chunks.append(text[prev:start])
        block = text[start:end]
        new_block, ch, tp = process_inner_html(
            block,
            enrich_places=enrich_places,
            ascii_quotes=ascii_quotes,
        )
        total_changed += ch
        total_ps += tp
        new_chunks.append(new_block)
        prev = end
    new_chunks.append(text[prev:])
    new_text = "".join(new_chunks)

    print(f"Critics lists processed: {len(spans)}")
    print(f"<p> entries seen: {total_ps}")
    print(f"<p> entries rewritten: {total_changed}")

    if dry_run:
        return 0

    if backup:
        bak = path.with_suffix(path.suffix + ".bak")
        shutil.copy2(path, bak)
        print(f"Backup: {bak}")

    path.write_text(new_text, encoding="utf-8")
    print(f"Wrote: {path}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "index_html",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "index.html",
        help="Path to index.html (default: repo root)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Show stats only")
    ap.add_argument("--backup", action="store_true", help="Keep .bak copy before write")
    ap.add_argument(
        "--enrich-places",
        action="store_true",
        help="Normalize 'Title, London, 1870' → 'Title. London, 1870' (conservative)",
    )
    ap.add_argument(
        "--ascii-quotes",
        action="store_true",
        help="Convert inner single-quoted snippets to double quotes in the citation",
    )
    args = ap.parse_args()
    path: Path = args.index_html
    if not path.is_file():
        print(f"Not found: {path}", file=sys.stderr)
        sys.exit(1)
    sys.exit(
        normalize_file(
            path,
            args.dry_run,
            args.backup,
            enrich_places=args.enrich_places,
            ascii_quotes=args.ascii_quotes,
        )
    )


if __name__ == "__main__":
    main()
