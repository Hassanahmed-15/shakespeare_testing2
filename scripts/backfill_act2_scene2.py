#!/usr/bin/env python3
"""One-off: backfill ACT 2 SCENE 2 `play` from first note; strip duplicate line;
fix Exit; relocate misfiled notes to ACT 2 SCENE 3."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "Public/Data/ROMEO_notes.json"


def normalize_play_line(s: str) -> str:
    if not s:
        return ""
    s = s.split("\n")[0].strip()
    m = re.match(r"^(Nurse)\s*:\s*(.*)$", s, re.I)
    if m:
        return f"NURSE: {m.group(2)}"
    m = re.match(r"^([A-Z][A-Z\s]+?)\s*:\s*(.*)$", s)
    if m:
        sp = " ".join(m.group(1).split())
        return f"{sp}: {m.group(2)}"
    return s


def main() -> None:
    with open(PATH, encoding="utf-8") as f:
        data = json.load(f)

    s2 = data["ACT 2, SCENE 2"]
    s3 = data["ACT 2, SCENE 3"]

    # Misfiled Variorum glosses (belong to Friar scene)
    if "216" in s2 and s2["216"].get("notes"):
        n0 = s2["216"]["notes"][0]
        s3["4"].setdefault("notes", []).append(n0)
    if "218" in s2 and s2["218"].get("notes"):
        for note in s2["218"]["notes"]:
            s3["2"].setdefault("notes", []).append(note)
    s2["216"] = {"play": "", "notes": []}
    s2["218"] = {"play": "", "notes": []}

    # Keys 1–211: dialogue / stage direction from first note; drop duplicate opener
    for k in range(1, 212):
        kk = str(k)
        ent = s2[kk]
        notes = list(ent.get("notes") or [])
        if not notes:
            ent["play"] = ""
            continue
        play = normalize_play_line(notes[0])
        ent["play"] = play
        if normalize_play_line(notes[0]) == play:
            notes.pop(0)
        ent["notes"] = notes

    # 212: corrupted import — balcony exit
    s2["212"] = {"play": "Exit", "notes": []}

    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print("Wrote", PATH)


if __name__ == "__main__":
    main()
