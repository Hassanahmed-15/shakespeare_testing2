#!/usr/bin/env python3
"""Replace standalone stage-direction play lines in ROMEO_notes.json with Folger TEI text.

Reads Public/Data/folger_sources/Rom.xml (Folger Shakespeare TEI). Skips <stage type="delivery">
(asides) when aligning; matches JSON SD lines to remaining Folger stages in order with
Jaccard overlap (optionally combining two consecutive Folger stages for merged JSON lines).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ROMEO_JSON = ROOT / "Public/Data/ROMEO_notes.json"
FOLGER_XML = ROOT / "Public/Data/folger_sources/Rom.xml"

NS = "{http://www.tei-c.org/ns/1.0}"


def local_name(tag: str) -> str:
    return tag.split("}")[-1] if "}" in tag else tag


def flatten_stage_text(stage_el: Any) -> str:
    t = "".join(stage_el.itertext())
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+([,.;:!?])", r"\1", t)
    return t


def word_set(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9']+", s.lower()))


def jaccard(a: str, b: str) -> float:
    wa, wb = word_set(a), word_set(b)
    if not wa or not wb:
        return 0.0
    inter = len(wa & wb)
    union = len(wa | wb)
    return min(1.0, inter / union if union else 0.0)


def json_sd_kind(play: str) -> str:
    """Rough class for matching Folger stage @type (entrance / exit / business / …)."""
    p = play.strip()
    pl = p.lower()
    if pl.startswith("enter") or pl.startswith("re-enter") or pl.startswith("reenter"):
        return "entrance"
    if p.lstrip().startswith("[") or "exeunt" in pl or pl.startswith("exit "):
        return "exit"
    if pl in ("exit", "exeunt"):
        return "exit"
    if pl.startswith("they fight") or pl.startswith("beats down") or pl.startswith("drawing "):
        return "business"
    if pl.startswith("flourish") or pl.startswith("sennet") or pl.startswith("alarum"):
        return "sound"
    return "any"


def folger_kind(folger_type: str, text: str) -> str:
    t = (folger_type or "").lower()
    if t in ("entrance", "exit", "business", "location"):
        return t
    return "other"


def kinds_compatible(json_play: str, folger_type: str, folger_text: str) -> bool:
    jk = json_sd_kind(json_play)
    fk = folger_kind(folger_type, folger_text)
    if jk == "any":
        return True
    if jk == "entrance":
        return fk == "entrance"
    if jk == "exit":
        return fk == "exit"
    if jk == "business":
        return fk == "business"
    if jk == "sound":
        return fk in ("business", "other")  # rare
    return True


def is_json_stage_direction_line(play: str) -> bool:
    """Lines that are clearly SD in this project's JSON (not speech continuations)."""
    p = play.strip()
    if not p:
        return False
    # Speaker-prefixed dialogue
    if re.match(r"^[A-Za-z][A-Za-z0-9\s\.\'\-\[\]]*:\s", p):
        return False
    pl = p.lower()
    if pl.startswith("enter") or pl.startswith("re-enter") or pl.startswith("reenter"):
        return True
    if pl.startswith("exeunt") or pl.startswith("exit "):
        return True
    if pl in ("exit", "exeunt"):
        return True
    if p.lstrip().startswith("["):
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
    return False


def strip_brackets_for_match(s: str) -> str:
    s = s.strip()
    if s.startswith("[") and s.endswith("]"):
        return s[1:-1].strip()
    return s


def load_folger_scenes(xml_path: Path) -> dict[str, list[tuple[str, str]]]:
    """Map 'ACT n, SCENE m' -> [(type, flattened_text), ...] excluding chorus div2."""
    import xml.etree.ElementTree as ET

    tree = ET.parse(xml_path)
    body = tree.getroot().find(f".//{NS}body")
    if body is None:
        raise RuntimeError("No body in TEI")

    out: dict[str, list[tuple[str, str]]] = {}

    for div1 in body:
        if local_name(div1.tag) != "div1":
            continue
        if div1.get("type") != "act":
            continue
        act = int(div1.get("n", "0"))
        scene_idx = 0
        for div2 in div1:
            if local_name(div2.tag) != "div2":
                continue
            if div2.get("type") == "chorus":
                continue
            scene_idx += 1
            key = f"ACT {act}, SCENE {scene_idx}"
            stages: list[tuple[str, str]] = []
            for st in div2.iter(f"{NS}stage"):
                stages.append((st.get("type") or "", flatten_stage_text(st)))
            out[key] = stages
    return out


def folger_matchable(stages: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Drop delivery asides; keep entrance, exit, business, location, mixed."""
    return [(t, tx) for t, tx in stages if t != "delivery"]


def _head_tokens_after_keyword(line: str, kw: str) -> list[str]:
    """Words after Enter/Exit (lowercase), skipping 'old', 'the', 'a'."""
    low = line.lower()
    idx = low.find(kw)
    if idx < 0:
        return []
    tail = line[idx + len(kw) :]
    words = re.findall(r"[a-zA-Z']+", tail)
    skip = {"old", "the", "a", "an", "and", "with", "his", "her", "my", "your"}
    return [w.lower() for w in words if w.lower() not in skip][:4]


def score_sd_pair(json_line: str, folger_text: str) -> float:
    """Similarity 0..1 with light bonuses for Enter/Exit alignment."""
    jnorm = strip_brackets_for_match(json_line)
    jl, cl = jnorm.lower(), folger_text.lower()
    sc = jaccard(jnorm, folger_text)
    if "enter" in jl and "enter" in cl:
        sc = max(sc, min(1.0, sc + 0.08))
    if ("exeunt" in jl or jl.startswith("exit")) and ("exit" in cl or "exeunt" in cl):
        sc = max(sc, min(1.0, sc + 0.08))
    # Variorum "Beats down their swords" ↔ Folger "Drawing his sword."
    if "beats" in jl and "drawing" in cl and "sword" in cl:
        sc = max(sc, 0.42)

    # Penalize wrong "Enter X" head when both lines look like simple entrance lines.
    if "enter" in jl and "enter" in cl and len(jnorm) < 88:
        jt = _head_tokens_after_keyword(jnorm, "enter")
        ft = _head_tokens_after_keyword(folger_text, "enter")
        if jt and ft:
            def rough_match(a: str, b: str) -> bool:
                if a in b or b in a:
                    return True
                if len(a) >= 4 and len(b) >= 4 and a[:4] == b[:4]:
                    return True
                return False

            if not any(any(rough_match(jw, fw) for fw in ft) for jw in jt):
                sc *= 0.35

    return min(1.0, sc)


def best_pool_match(
    json_line: str,
    pool: list[tuple[str, str]],
    min_score: float,
) -> tuple[int, str, int, float] | tuple[None, None, None, float]:
    """Return (start_index, replacement_text, span, score) or (None,None,None,sc)."""
    if not pool:
        return None, None, None, 0.0

    jnorm = strip_brackets_for_match(json_line)
    jl = jnorm.lower()
    allow_span2 = len(jnorm) > 90 or " then " in jl or ";" in jnorm

    best_i = 0
    best_text = ""
    best_sc = -1.0
    best_span = 1

    for i in range(len(pool)):
        ft, ftxt = pool[i]
        if not kinds_compatible(json_line, ft, ftxt):
            continue
        sc = score_sd_pair(json_line, ftxt)
        if sc > best_sc:
            best_sc = sc
            best_i = i
            best_text = ftxt
            best_span = 1

    if allow_span2:
        for i in range(len(pool) - 1):
            _ft1, t1 = pool[i]
            _ft2, t2 = pool[i + 1]
            chunk = t1 + " " + t2
            sc = score_sd_pair(json_line, chunk)
            if sc > best_sc:
                best_sc = sc
                best_i = i
                best_text = chunk
                best_span = 2

    if best_sc < min_score:
        return None, None, None, best_sc
    return best_i, best_text, best_span, best_sc


def apply_scene(
    scene_data: dict[str, Any],
    folger_stages: list[tuple[str, str]],
    min_score: float = 0.10,
) -> int:
    pool = folger_matchable(folger_stages)
    keys = sorted(scene_data.keys(), key=lambda x: int(x) if str(x).isdigit() else 0)
    n = 0
    for k in keys:
        ent = scene_data[k]
        play = ent.get("play") or ""
        if not is_json_stage_direction_line(play):
            continue
        if not pool:
            break
        got = best_pool_match(play, pool, min_score)
        bi, repl, span, _sc = got
        if bi is None or repl is None or span is None:
            continue
        if span == 2:
            del pool[bi : bi + 2]
        else:
            del pool[bi]
        if repl.strip() != play.strip():
            ent["play"] = repl
            n += 1
    return n


def main() -> None:
    if not FOLGER_XML.is_file():
        raise SystemExit(f"Missing {FOLGER_XML}")

    folger_scenes = load_folger_scenes(FOLGER_XML)
    data = json.loads(ROMEO_JSON.read_text(encoding="utf-8"))

    total = 0
    for sk, scene in data.items():
        if not isinstance(scene, dict) or not sk.startswith("ACT "):
            continue
        if sk not in folger_scenes:
            print("warn: no Folger scene", sk)
            continue
        n = apply_scene(scene, folger_scenes[sk])
        if n:
            print(sk, n, "lines")
        total += n

    ROMEO_JSON.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )
    print("total replacements:", total)


if __name__ == "__main__":
    main()
