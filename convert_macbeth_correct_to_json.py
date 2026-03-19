#!/usr/bin/env python3
"""
Convert macbeth correct.docx to JSON format matching the structure of macbeth_notes_cleaned_play.json.

Input: macbeth correct.docx with structure:
  - ACT X, SCENE Y
  - ========PLAY TEXT========
  - Numbered lines: 1. text, 2. SPEAKER: text, ...
  - ========SCHOLARLY COMMENTARY========
  - Commentary: 1. phrase] SCHOLAR: note text (line number at start)

Output: JSON with DRAMATIS PERSONAE (empty/minimal) and ACT X SCENE Y scenes.
"""

import json
import os
import re
from docx import Document
from typing import Dict, List, Optional, Tuple


def get_paragraph_text(para) -> str:
    return para.text.strip()


def is_scene_heading(text: str) -> Optional[Tuple[int, int]]:
    match = re.match(r'^ACT\s+(\d+),\s*SCENE\s+(\d+)$', text.strip(), re.IGNORECASE)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    match = re.match(r'^ACT\s+(\d+)\s+SCENE\s+(\d+)$', text.strip(), re.IGNORECASE)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return None


def parse_play_line(text: str) -> Optional[Tuple[int, str]]:
    """Parse '1. text' or '1. SPEAKER: text' -> (line_num, line_text)"""
    match = re.match(r'^(\d+)\.\s+(.*)$', text.strip())
    if match:
        return int(match.group(1)), match.group(2).strip()
    return None


def parse_commentary_line(text: str) -> Optional[Tuple[int, str]]:
    """Parse '1. phrase] SCHOLAR: note' or '3. or] JENNESS: The question...' -> (line_num, full_note_text)"""
    match = re.match(r'^(\d+)\.\s+(.*)$', text.strip())
    if match:
        line_num = int(match.group(1))
        rest = match.group(2).strip()
        if rest:  # Has content after number
            return line_num, f"{match.group(1)}. {rest}"
    return None


def convert_macbeth_correct_to_json(docx_path: str, output_json_path: Optional[str] = None) -> Dict:
    print(f"Reading DOCX: {docx_path}")
    doc = Document(docx_path)

    all_scenes = {}
    current_scene_key = None
    current_scene_lines = {}
    in_play_section = False
    in_commentary_section = False
    current_line_num = None
    current_note_text = None

    for para in doc.paragraphs:
        text = get_paragraph_text(para)
        if not text:
            if in_commentary_section and current_line_num is not None and current_note_text:
                current_note_text += " "
            continue

        # Scene heading
        scene_info = is_scene_heading(text)
        if scene_info:
            # Save pending commentary note before switching scenes
            if current_scene_key and current_line_num is not None and current_note_text:
                line_str = str(current_line_num)
                if line_str in current_scene_lines:
                    current_scene_lines[line_str].setdefault("notes", []).append(current_note_text.strip())
                current_line_num = None
                current_note_text = None

            if current_scene_key and current_scene_lines:
                all_scenes[current_scene_key] = current_scene_lines
                print(f"  Completed {current_scene_key}: {len(current_scene_lines)} lines")

            act_num, scene_num = scene_info
            current_scene_key = f"ACT {act_num} SCENE {scene_num}"
            current_scene_lines = {}  # Reset for new scene
            in_play_section = False
            in_commentary_section = False
            current_line_num = None
            current_note_text = None
            print(f"  Found {current_scene_key}")
            continue

        # Separators
        if "======PLAY TEXT======" in text or text == "======PLAY TEXT======":
            in_play_section = True
            in_commentary_section = False
            continue
        if "======SCHOLARLY COMMENTARY======" in text or "========SCHOLARLY COMMENTARY========" in text:
            in_play_section = False
            in_commentary_section = True
            current_line_num = None
            current_note_text = None
            continue

        # Play text section
        if in_play_section and current_scene_key:
            line_info = parse_play_line(text)
            if line_info:
                line_num, line_text = line_info
                if line_text:
                    line_num_str = str(line_num)
                    if line_num_str not in current_scene_lines:
                        current_scene_lines[line_num_str] = {"play": line_text, "notes": []}
                    else:
                        current_scene_lines[line_num_str]["play"] = line_text
            continue

        # Commentary section
        if in_commentary_section and current_scene_key:
            note_info = parse_commentary_line(text)
            if note_info:
                # Save previous note if exists
                if current_line_num is not None and current_note_text:
                    line_str = str(current_line_num)
                    if line_str in current_scene_lines:
                        if "notes" not in current_scene_lines[line_str]:
                            current_scene_lines[line_str]["notes"] = []
                        current_scene_lines[line_str]["notes"].append(current_note_text.strip())
                    current_note_text = None

                current_line_num, current_note_text = note_info
            elif current_line_num is not None and current_note_text:
                # Continuation of previous note
                current_note_text += " " + text
            continue

    # Save last scene
    if current_scene_key and current_scene_lines:
        if current_line_num is not None and current_note_text and current_scene_key:
            line_str = str(current_line_num)
            if line_str in current_scene_lines:
                if "notes" not in current_scene_lines[line_str]:
                    current_scene_lines[line_str]["notes"] = []
                current_scene_lines[line_str]["notes"].append(current_note_text.strip())
        all_scenes[current_scene_key] = current_scene_lines
        print(f"  Completed {current_scene_key}: {len(current_scene_lines)} lines")

    # Fix: ensure all scene lines have notes array, merge any notes added during commentary
    for scene_key, scene_data in all_scenes.items():
        for line_num, line_data in scene_data.items():
            if "notes" not in line_data:
                line_data["notes"] = []

    # Build output - minimal DRAMATIS PERSONAE (macbeth correct has none)
    output_data = {
        "DRAMATIS PERSONAE": {
            "1": {"play": "Macbeth - Dramatis Personae (see Folger edition)", "notes": []}
        }
    }
    output_data.update(all_scenes)

    # Output path
    if not output_json_path:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_json_path = os.path.join(script_dir, "Public", "Data", "macbeth_correct.json")

    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    print(f"\nWriting JSON: {output_json_path}")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    total_lines = sum(len(s) for s in all_scenes.values())
    total_notes = sum(
        sum(len(d.get("notes", [])) for d in s.values())
        for s in all_scenes.values()
    )
    print(f"  Scenes: {len(all_scenes)}, Lines: {total_lines}, Notes: {total_notes}")
    return output_data


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "macbeth correct.docx")
    if not os.path.isfile(input_path):
        print(f"Error: {input_path} not found")
        return
    convert_macbeth_correct_to_json(input_path)


if __name__ == "__main__":
    main()
