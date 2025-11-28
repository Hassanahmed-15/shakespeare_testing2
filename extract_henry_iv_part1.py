import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os


BASE_URL = "https://shakespeare.mit.edu/1henryiv/1henryiv.{act}.{scene}.html"


def extract_text_from_scene(act, scene):
    """Extract text from a specific act and scene"""
    url = BASE_URL.format(act=act, scene=scene)
    print(f"Fetching Act {act}, Scene {scene} from {url}...")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        body = soup.find("body")
        if not body:
            print(f"Warning: Could not find body for Act {act}, Scene {scene}")
            return []

        elements_with_pos = []

        # Capture speeches
        all_speech_links = body.find_all("a", {"name": re.compile(r"^speech")})
        for speech_link in all_speech_links:
            bold = speech_link.find("b")
            if not bold:
                continue

            char_name = bold.get_text(strip=True)
            if not char_name or not char_name.isupper():
                continue

            next_elem = speech_link.next_sibling
            found_blockquote = None
            while next_elem:
                if hasattr(next_elem, "name"):
                    if next_elem.name == "blockquote":
                        found_blockquote = next_elem
                        break
                    if next_elem.name == "a" and next_elem.get("name", "").startswith("speech"):
                        break
                next_elem = getattr(next_elem, "next_sibling", None)

            if not found_blockquote and speech_link.parent:
                next_parent_sib = speech_link.parent.next_sibling
                while next_parent_sib:
                    if hasattr(next_parent_sib, "name") and next_parent_sib.name == "blockquote":
                        found_blockquote = next_parent_sib
                        break
                    next_parent_sib = getattr(next_parent_sib, "next_sibling", None)

            if not found_blockquote:
                continue

            dialogue_lines = []
            for dialogue_a in found_blockquote.find_all("a"):
                dialogue_text = dialogue_a.get_text(strip=True)
                if dialogue_text and not dialogue_a.get("name", "").startswith("speech"):
                    dialogue_lines.append(dialogue_text)

            if dialogue_lines:
                elements_with_pos.append(
                    ("speech", speech_link.sourceline or 0, char_name, dialogue_lines, found_blockquote)
                )

        # Capture stage directions
        all_blockquotes = body.find_all("blockquote")
        processed_blockquotes = {elem[4] for elem in elements_with_pos if len(elem) > 4}
        for blockquote in all_blockquotes:
            if blockquote in processed_blockquotes:
                continue
            italic = blockquote.find("i")
            if not italic:
                continue
            stage_dir = italic.get_text(strip=True)
            if stage_dir and re.match(r"^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums)", stage_dir, re.IGNORECASE):
                elements_with_pos.append(("stage", blockquote.sourceline or 0, stage_dir, None, blockquote))

        elements_with_pos.sort(key=lambda x: x[1])

        all_lines = []
        for elem_type, _pos, content, dialogue_lines, _blockquote in elements_with_pos:
            if elem_type == "speech":
                for dialogue in dialogue_lines:
                    all_lines.append(f"{content}: {dialogue}")
            else:
                all_lines.append(content)

        grouped_lines = []
        current_speaker = None

        for line in all_lines:
            if re.match(r"^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums)", line, re.IGNORECASE):
                grouped_lines.append(line)
                current_speaker = None
                continue

            if ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    dialogue = parts[1].strip()
                    if speaker == current_speaker:
                        grouped_lines.append(dialogue)
                    else:
                        grouped_lines.append(line)
                        current_speaker = speaker
                    continue

            grouped_lines.append(line)
            current_speaker = None

        return grouped_lines

    except Exception as exc:
        print(f"Error fetching Act {act}, Scene {scene}: {exc}")
        import traceback

        traceback.print_exc()
        return []


def extract_play_text():
    """Extract all text from Henry IV Part 1"""
    all_scenes = {}

    scenes_structure = {
        1: [1, 2, 3],
        2: [1, 2, 3, 4],
        3: [1, 2],
        4: [1, 2, 3, 4],
        5: [1, 2, 3, 4, 5],
    }

    for act in range(1, 6):
        for scene in scenes_structure[act]:
            scene_key = f"ACT {act} SCENE {scene}"
            lines = extract_text_from_scene(act, scene)

            if lines:
                all_scenes[scene_key] = {}
                for idx, line in enumerate(lines, start=1):
                    all_scenes[scene_key][str(idx)] = {"play": line}
                print(f"  Extracted {len(lines)} lines from {scene_key}")
            else:
                print(f"  Warning: No lines extracted from {scene_key}")

            time.sleep(0.2)

    return all_scenes


def main():
    print("Extracting Henry IV Part 1 from MIT Shakespeare website...")
    print("=" * 60)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, "Public", "Data", "henry_iv_part1.json")

    existing_data = {}
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        print(f"Read existing file: {json_file}")
    except Exception as exc:
        print(f"Could not read existing file ({exc}), creating new structure")
        existing_data = {
            "DRAMATIS PERSONAE": {
                "1": {
                    "play": "DRAMATIS PERSONAE\nHENRY IV PART 1",
                    "notes": [],
                }
            }
        }

    all_scenes = extract_play_text()

    output_data = {"DRAMATIS PERSONAE": existing_data.get("DRAMATIS PERSONAE", {})}
    output_data.update(all_scenes)

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"Extraction complete! Data saved to {json_file}")
    print(f"Total scenes extracted: {len(all_scenes)}")
    total_lines = sum(len(scene_data) for scene_data in all_scenes.values())
    print(f"Total lines extracted: {total_lines}")

    expected_scenes = [
        "ACT 1 SCENE 1",
        "ACT 1 SCENE 2",
        "ACT 1 SCENE 3",
        "ACT 2 SCENE 1",
        "ACT 2 SCENE 2",
        "ACT 2 SCENE 3",
        "ACT 2 SCENE 4",
        "ACT 3 SCENE 1",
        "ACT 3 SCENE 2",
        "ACT 4 SCENE 1",
        "ACT 4 SCENE 2",
        "ACT 4 SCENE 3",
        "ACT 4 SCENE 4",
        "ACT 5 SCENE 1",
        "ACT 5 SCENE 2",
        "ACT 5 SCENE 3",
        "ACT 5 SCENE 4",
        "ACT 5 SCENE 5",
    ]

    missing_scenes = [scene for scene in expected_scenes if scene not in all_scenes]
    if missing_scenes:
        print(f"\nWARNING: Missing scenes: {missing_scenes}")
    else:
        print("\nAll expected scenes are present!")


if __name__ == "__main__":
    main()



