#!/usr/bin/env python3
"""
Parse Folger Shakespeare TEI (Folger Digital Texts XML) into a linear spine:
  - Stage directions (tei:stage) with stable n= (e.g. SD 1.1.0)
  - Speech lines keyed by Folger through-line number (milestone @unit='ftln', @n like 1.1.1)

Output anchors use the ftln @n attribute (e.g. "1.1.1") and stage @n (e.g. "SD 1.1.0").

License: Folger Digital Texts XML is CC BY-NC; see teiHeader in each file.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"


def _local(tag: str) -> str:
    if tag.startswith("{"):
        return tag.split("}", 1)[-1]
    return tag


def _q(local: str) -> str:
    return f"{{{TEI_NS}}}{local}"


def scene_key_from_divs(act_n: str, scene_n: str) -> str:
    """Normalize to match index.html normalizeSceneKey: ACT 1, SCENE 1."""
    return f"ACT {int(act_n)}, SCENE {int(scene_n)}"


def _text_from_stage(stage: ET.Element) -> str:
    t = re.sub(r"\s+", " ", "".join(stage.itertext())).strip()
    t = re.sub(r"\s+([.,;:!?])", r"\1", t)
    return t


def _collect_line_after_ftln(
    ab_children: list[ET.Element], start_idx: int
) -> tuple[str, int]:
    """Collect text for the ftln milestone at start_idx; return (text, next_index)."""
    parts: list[str] = []
    i = start_idx + 1
    while i < len(ab_children):
        ch = ab_children[i]
        loc = _local(ch.tag)
        if loc == "milestone" and ch.get("unit") == "ftln":
            break
        if loc == "milestone":
            i += 1
            continue
        if loc == "lb":
            parts.append(" ")
            i += 1
            continue
        if loc in ("w", "c", "pc", "name", "title", "hi", "foreign"):
            parts.append("".join(ch.itertext()))
            i += 1
            continue
        i += 1
    text = re.sub(r"\s+", " ", "".join(parts)).strip()
    return text, i


def _speaker_text(sp: ET.Element) -> str:
    spk = sp.find(_q("speaker"))
    if spk is None:
        return ""
    return re.sub(r"\s+", " ", "".join(spk.itertext())).strip()


def _iter_ab_ftln_lines(ab: ET.Element) -> Iterator[tuple[str, str]]:
    children = list(ab)
    i = 0
    while i < len(children):
        ch = children[i]
        if _local(ch.tag) == "milestone" and ch.get("unit") == "ftln":
            n = ch.get("n") or ""
            text, next_i = _collect_line_after_ftln(children, i)
            yield n, text
            i = next_i
        else:
            i += 1


def _process_ab_blocks(sp: ET.Element, speaker: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for ab in sp.findall(_q("ab")):
        for ftln, line_text in _iter_ab_ftln_lines(ab):
            if not ftln:
                continue
            play = f"{speaker}: {line_text}" if speaker else line_text
            out.append(
                {
                    "kind": "speech",
                    "anchor": ftln,
                    "speaker": speaker,
                    "text": line_text,
                    "play": play,
                }
            )
    return out


def _process_sp(sp: ET.Element) -> list[dict[str, Any]]:
    speaker = _speaker_text(sp)
    return _process_ab_blocks(sp, speaker)


def iter_div2_scene_units(div2: ET.Element) -> Iterator[dict[str, Any]]:
    """Yield ordered units: stages and speech lines for one scene div2."""
    for child in div2:
        loc = _local(child.tag)
        if loc == "head":
            continue
        if loc == "stage":
            n = child.get("n") or ""
            xml_id = child.get(f"{{{XML_NS}}}id") or ""
            text = _text_from_stage(child)
            yield {
                "kind": "stage",
                "anchor": n,
                "xml_id": xml_id,
                "text": text,
                "play": f"[{text}]",
            }
        elif loc == "sp":
            for row in _process_sp(child):
                yield row


def parse_folger_play(path: Path) -> dict[str, Any]:
    tree = ET.parse(path)
    root = tree.getroot()
    body = root.find(_q("body"))
    if body is None:
        text_el = root.find(_q("text"))
        if text_el is not None:
            body = text_el.find(_q("body"))
    if body is None:
        raise ValueError("No body in TEI (expected TEI/body or TEI/text/body)")

    title_el = root.find(f".//{{{TEI_NS}}}fileDesc/{{{TEI_NS}}}titleStmt/{{{TEI_NS}}}title")
    title = (title_el.text or "Play").strip() if title_el is not None else "Play"
    idno_el = root.find(f".//{{{TEI_NS}}}fileDesc/{{{TEI_NS}}}publicationStmt/{{{TEI_NS}}}idno")
    play_id = (idno_el.text or "").strip() if idno_el is not None else path.stem

    scenes: dict[str, list[dict[str, Any]]] = {}

    for div1 in body.findall(_q("div1")):
        if div1.get("type") != "act":
            continue
        act_n = div1.get("n") or ""
        for div2 in div1.findall(_q("div2")):
            if div2.get("type") != "scene":
                continue
            scene_n = div2.get("n") or ""
            key = scene_key_from_divs(act_n, scene_n)
            units = list(iter_div2_scene_units(div2))
            scenes[key] = units

    return {
        "title": title,
        "play_id": play_id,
        "source_file": path.name,
        "scenes": scenes,
    }


def spine_to_scene_json(spine: dict[str, Any]) -> dict[str, Any]:
    """
    Build Variorum-style scene objects: line_key -> { play, notes, folgerAnchor, kind }.
    Line keys are anchor strings (ftln or stage SD n).
    """
    out: dict[str, Any] = {}
    dramatis: dict[str, Any] | None = None

    for scene_key, units in spine["scenes"].items():
        scene_obj: dict[str, Any] = {}
        for u in units:
            anchor = u.get("anchor") or ""
            if not anchor:
                continue
            # Use anchor as key; stage SDs have "SD 1.1.0" style n
            line_key = anchor.replace(" ", "_") if anchor.startswith("SD") else anchor
            line_key = re.sub(r"[^\w.]", "_", line_key) if not anchor[0].isdigit() else anchor

            # Prefer stable key: for "SD 1.1.0" -> use full anchor as key with underscores
            if anchor.startswith("SD"):
                line_key = anchor.replace(" ", "_")

            scene_obj[line_key] = {
                "play": u.get("play") or "",
                "notes": [],
                "folgerAnchor": anchor,
                "kind": u.get("kind", "speech"),
            }
        out[scene_key] = scene_obj

    return out


def main() -> None:
    import argparse
    import json
    import sys

    ap = argparse.ArgumentParser(description="Parse Folger TEI to JSON spine")
    ap.add_argument("tei_file", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    spine = parse_folger_play(args.tei_file)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(spine, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {args.output} ({len(spine['scenes'])} scenes)", file=sys.stderr)


if __name__ == "__main__":
    main()
