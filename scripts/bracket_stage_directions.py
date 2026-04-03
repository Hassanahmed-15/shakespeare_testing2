#!/usr/bin/env python3
"""Wrap standalone stage-direction `play` lines in [brackets] across Variorum JSON play files.

Does not modify speaker lines (NAME: dialogue). Skips lines already fully wrapped in [...].
Uses the same SD heuristics as scripts/apply_folger_stage_directions.py, plus common extras.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "Public/Data"

# Same set as index.html plays metadata (fileName values)
PLAY_FILES = [
    "macbeth_notes_cleaned_play.json",
    "hamlet_notes (1).json",
    "ROMEO_notes.json",
    "othello_notes.json",
    "kinglear_notes.json",
    "as_you_like_it.json",
    "Coriolanus.json",
    "cymbeline.json",
    "henry_iv_part1.json",
    "henry_iv_part2.json",
    "julius_caesar.json",
    "king_john.json",
    "loves_labours_lost.json",
    "merchant_of_venice.json",
    "midsummer_nights_dream.json",
    "much_ado_about_nothing.json",
    "richard_ii.json",
    "richard_iii.json",
    "the_tempest.json",
    "the_winters_tale.json",
    "troilus_and_cressida.json",
    "twelfth_night.json",
    "alls_well_that_ends_well.json",
    "antony_and_cleopatra.json",
    "comedy_of_errors.json",
    "henry_v.json",
    "henry_vi_part1.json",
    "henry_vi_part2.json",
    "henry_vi_part3.json",
    "henry_viii.json",
    "measure_for_measure.json",
    "merry_wives_of_windsor.json",
    "pericles.json",
    "taming_of_the_shrew.json",
    "timon_of_athens.json",
    "titus_andronicus.json",
    "two_gentlemen_of_verona.json",
]


def is_speaker_line(p: str) -> bool:
    return bool(re.match(r"^[A-Za-z][A-Za-z0-9\s.'\-\[\]]*:\s", p))


def is_fully_bracketed(p: str) -> bool:
    s = p.strip()
    return len(s) >= 2 and s[0] == "[" and s[-1] == "]"


def is_standalone_stage_direction(play: str) -> bool:
    """True if the whole line is a stage direction (not NAME: speech), unbracketed or partial."""
    p = play.strip()
    if not p:
        return False
    if is_speaker_line(p):
        return False
    if is_fully_bracketed(p):
        return False

    pl = p.lower().strip()

    # Canonical entrances / exits / sounds (matches apply_folger_stage_directions)
    if pl.startswith("enter") or pl.startswith("re-enter") or pl.startswith("reenter"):
        return True
    if pl.startswith("exeunt") or pl.startswith("exit "):
        return True
    if pl in ("exit", "exeunt"):
        return True
    if pl in ("they fight", "they fight."):
        return True
    if pl.startswith("beats down"):
        return True
    if pl.startswith("drawing his sword") or pl.startswith("drawing her sword"):
        return True
    if pl.startswith("he bites his thumb"):
        return True
    if pl.startswith("flourish") or pl.startswith("sennet") or pl.startswith("alarum"):
        return True

    # Danish march + flourish + entrance (e.g. Hamlet 3.2)
    if pl.startswith("danish march"):
        return True

    # "To CHARACTER" as standalone SD (short; comma usually means dialogue, e.g. "To Norway, uncle")
    if (
        re.match(r"^To [A-Z][A-Z\s']+$", p)
        and len(p) < 48
        and "," not in p
    ):
        return True

    # Mime / dumb-show (e.g. Hamlet 3.2)
    if pl.startswith("lying down"):
        return True
    if pl == "sleeps":
        return True
    if pl.startswith("pours the poison"):
        return True

    # Latin / early print
    if re.match(r"^(manet|manent|manet\.|manent\.|omnes|omnes\.)\b", pl):
        return True

    # Music / noise / location cues (line-start only)
    if re.match(
        r"^(hautboys|cornets|trumpets|dead march|a march|march\.|thunder|lightning|"
        r"alarums|alarum\.|drum|drums|within\.|above\.|below\.|knocking|"
        r"noise|music|song\.|sings\.|speaks from|she speaks|he speaks)\b",
        pl,
    ):
        return True

    # Short location / prop lines (very common as standalone SD)
    if re.match(r"^(the |a |an )?(tomb|bed|chair|throne|altar|gates?|door)\b", pl):
        if len(p) < 120:
            return True

    # "They fight" variants
    if "fight" in pl and len(p) < 80 and not pl.startswith("i "):
        if pl.startswith("here they") or pl.startswith("then they"):
            return True

    return False


def bracket_play_field(play: str) -> tuple[str, bool]:
    if not is_standalone_stage_direction(play):
        return play, False
    p = play.strip()
    return f"[{p}]", True


def process_obj(o: object, stats: dict[str, int]) -> None:
    if isinstance(o, dict):
        if "play" in o and isinstance(o["play"], str):
            new_p, changed = bracket_play_field(o["play"])
            if changed:
                o["play"] = new_p
                stats["lines"] = stats.get("lines", 0) + 1
        for k, v in o.items():
            if str(k).startswith("_"):
                continue
            process_obj(v, stats)
    elif isinstance(o, list):
        for item in o:
            process_obj(item, stats)


def main() -> None:
    dry = "--dry-run" in sys.argv
    paths = [DATA / name for name in PLAY_FILES]
    missing = [p for p in paths if not p.is_file()]
    if missing:
        print("Missing files:", *[m.name for m in missing], file=sys.stderr)

    total_lines = 0
    for path in paths:
        if not path.is_file():
            continue
        stats: dict[str, int] = {}
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        process_obj(data, stats)
        n = stats.get("lines", 0)
        total_lines += n
        if n:
            print(f"{path.name}: {n} play lines bracketed")
        if n and not dry:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        elif dry and n:
            print(f"  (dry-run: would write {path.name})")

    print(f"Done. Total lines updated: {total_lines}" + (" (dry-run)" if dry else ""))


if __name__ == "__main__":
    main()
