import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

def extract_text_from_scene(act, scene):
    """Extract text from a specific act and scene"""
    url = f"https://shakespeare.mit.edu/pericles/pericles.{act}.{scene}.html"
    print(f"Fetching Act {act}, Scene {scene} from {url}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        lines = []
        
        body = soup.find('body')
        if not body:
            print(f"Warning: Could not find body for Act {act}, Scene {scene}")
            return lines
        
        # Process elements in document order
        elements_with_pos = []
        
        # Find all speech links
        all_speech_links = body.find_all('a', {'name': re.compile(r'^speech')})
        for speech_link in all_speech_links:
            bold = speech_link.find('b')
            if bold:
                char_name = bold.get_text(strip=True)
                if char_name and char_name.isupper():
                    # Find the following blockquote
                    next_elem = speech_link.next_sibling
                    found_blockquote = None
                    
                    while next_elem:
                        if hasattr(next_elem, 'name'):
                            if next_elem.name == 'blockquote':
                                found_blockquote = next_elem
                                break
                            elif next_elem.name == 'a' and next_elem.get('name', '').startswith('speech'):
                                break
                        next_elem = getattr(next_elem, 'next_sibling', None)
                    
                    if not found_blockquote and speech_link.parent:
                        next_parent_sib = speech_link.parent.next_sibling
                        while next_parent_sib:
                            if hasattr(next_parent_sib, 'name') and next_parent_sib.name == 'blockquote':
                                found_blockquote = next_parent_sib
                                break
                            next_parent_sib = getattr(next_parent_sib, 'next_sibling', None)
                    
                    if found_blockquote:
                        dialogue_lines = []
                        for dialogue_a in found_blockquote.find_all('a'):
                            dialogue_text = dialogue_a.get_text(strip=True)
                            if dialogue_text and not dialogue_a.get('name', '').startswith('speech'):
                                dialogue_lines.append(dialogue_text)
                        
                        if dialogue_lines:
                            elements_with_pos.append(('speech', speech_link.sourceline or 0, char_name, dialogue_lines, found_blockquote))
        
        # Find all stage direction blockquotes
        all_blockquotes = body.find_all('blockquote')
        processed_blockquotes = {elem[4] for elem in elements_with_pos if len(elem) > 4}
        
        for blockquote in all_blockquotes:
            if blockquote not in processed_blockquotes:
                italic = blockquote.find('i')
                if italic:
                    stage_dir = italic.get_text(strip=True)
                    if stage_dir and re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums)', stage_dir, re.IGNORECASE):
                        elements_with_pos.append(('stage', blockquote.sourceline or 0, stage_dir, None, blockquote))
        
        # Sort by position in document
        elements_with_pos.sort(key=lambda x: x[1])
        
        # Build lines list
        all_lines = []
        for elem_type, pos, content, dialogue_lines, blockquote in elements_with_pos:
            if elem_type == 'speech':
                for dialogue in dialogue_lines:
                    all_lines.append(f"{content}: {dialogue}")
            elif elem_type == 'stage':
                all_lines.append(content)
        
        # Group consecutive lines from the same speaker
        grouped_lines = []
        current_speaker = None
        
        for line in all_lines:
            if not line or not line.strip():
                continue
                
            # Check if it's a stage direction
            if re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums)', line, re.IGNORECASE):
                grouped_lines.append(line)
                current_speaker = None
            elif ':' in line:
                # It's a character line
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    dialogue = parts[1].strip()
                    
                    if speaker == current_speaker:
                        # Same speaker, just add dialogue without name
                        grouped_lines.append(dialogue)
                    else:
                        # New speaker
                        grouped_lines.append(line)
                        current_speaker = speaker
                else:
                    grouped_lines.append(line)
                    current_speaker = None
            else:
                # Regular line
                grouped_lines.append(line)
                current_speaker = None
        
        return grouped_lines
    
    except Exception as e:
        print(f"Error fetching Act {act}, Scene {scene}: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("Extracting missing scenes from Pericles...")
    print("=" * 60)
    
    # Get the script directory and construct the path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, "Public", "Data", "pericles.json")
    
    # Read existing file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Read existing file: {json_file}")
    
    # Remove ACT 1 SCENE 0 if it exists
    if "ACT 1 SCENE 0" in data:
        print("\nRemoving ACT 1 SCENE 0...")
        del data["ACT 1 SCENE 0"]
        print("  Removed ACT 1 SCENE 0")
    
    # Extract missing scenes
    scenes_to_extract = [
        (3, 1),
        (4, 4),
        (5, 2)
    ]
    
    new_scenes = {}
    for act, scene in scenes_to_extract:
        scene_key = f"ACT {act} SCENE {scene}"
        print(f"\nExtracting {scene_key}...")
        lines = extract_text_from_scene(act, scene)
        
        if lines:
            new_scenes[scene_key] = {}
            for idx, line in enumerate(lines, start=1):
                new_scenes[scene_key][str(idx)] = {
                    "play": line
                }
            print(f"  Extracted {len(lines)} lines from {scene_key}")
        else:
            print(f"  Warning: No lines extracted from {scene_key}")
        
        time.sleep(0.5)
    
    # Add new scenes to data
    data.update(new_scenes)
    
    # Sort the keys to ensure proper order
    sorted_data = {}
    sorted_data["DRAMATIS PERSONAE"] = data["DRAMATIS PERSONAE"]
    
    # Sort all ACT/SCENE keys
    act_scene_keys = [k for k in data.keys() if k.startswith("ACT")]
    act_scene_keys.sort(key=lambda x: (
        int(re.search(r'ACT (\d+)', x).group(1)),
        int(re.search(r'SCENE (\d+)', x).group(1))
    ))
    
    for key in act_scene_keys:
        sorted_data[key] = data[key]
    
    # Write back to file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print(f"Extraction complete! Data saved to {json_file}")
    print(f"Removed: ACT 1 SCENE 0")
    print(f"Added {len(new_scenes)} scenes: {', '.join(new_scenes.keys())}")

if __name__ == "__main__":
    main()

