import requests
from bs4 import BeautifulSoup
import json
import re
import time

def extract_text_from_scene(act, scene):
    """Extract text from a specific act and scene"""
    url = f"https://shakespeare.mit.edu/midsummer/midsummer.{act}.{scene}.html"
    print(f"Fetching Act {act}, Scene {scene}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        lines = []
        
        body = soup.find('body')
        if not body:
            print(f"Warning: Could not find body for Act {act}, Scene {scene}")
            return lines
        
        # Define starting lines and target line numbers for each scene
        start_configs = {
            (1, 1): {"marker": "THESEUS: Now, fair Hippolyta, our nuptial hour", "line": 4},
            (1, 2): {"marker": "QUINCE: Is all our company here?", "line": 4},
            (2, 1): {"marker": "PUCK: How now, spirit! whither wander you?", "line": 4},
            (2, 2): {"marker": "TITANIA: Come, now a roundel and a fairy song;", "line": 2},
            (3, 1): {"marker": "BOTTOM: Are we all met?", "line": 4},
            (3, 2): {"marker": "OBERON: I wonder if Titania be awaked;", "line": 2},
            (4, 1): {"marker": "THESEUS: Have you sent to Bottom's house ? is he come home yet?", "line": 3},
            (5, 1): {"marker": "HIPPOLYTA: 'Tis strange my Theseus, that these lovers speak of", "line": 3}
        }
        
        start_config = start_configs.get((act, scene), {"marker": None, "line": 1})
        start_marker = start_config.get("marker")
        target_line = start_config.get("line", 1)
        
        # Process elements in document order
        # Character names are in <a name="speechX"><b>CHARACTER</b></a>
        # Dialogue is in <blockquote> following character, with <a name="N">dialogue</a> tags
        # Stage directions are in <blockquote><i>direction</i></blockquote>
        
        # Collect all elements with their positions
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
                            # Store with speech link position
                            elements_with_pos.append(('speech', speech_link.sourceline or 0, char_name, dialogue_lines, found_blockquote))
        
        # Find all stage direction blockquotes
        all_blockquotes = body.find_all('blockquote')
        processed_blockquotes = {elem[4] for elem in elements_with_pos if len(elem) > 4}
        
        for blockquote in all_blockquotes:
            if blockquote not in processed_blockquotes:
                italic = blockquote.find('i')
                if italic:
                    stage_dir = italic.get_text(strip=True)
                    if stage_dir and re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside)', stage_dir, re.IGNORECASE):
                        elements_with_pos.append(('stage', blockquote.sourceline or 0, stage_dir, None, blockquote))
        
        # Sort by position in document
        elements_with_pos.sort(key=lambda x: x[1])
        
        # Build lines list (without scene headings)
        all_lines = []
        for elem_type, pos, content, dialogue_lines, blockquote in elements_with_pos:
            if elem_type == 'speech':
                for dialogue in dialogue_lines:
                    all_lines.append(f"{content}: {dialogue}")
            elif elem_type == 'stage':
                all_lines.append(content)
        
        # Find the starting point
        start_index = 0
        if start_marker:
            for i, line in enumerate(all_lines):
                if start_marker.lower() in line.lower():
                    start_index = i
                    break
        
        # Get stage directions before the start
        stage_directions = []
        for i in range(start_index):
            if all_lines[i].startswith(('Enter', 'Exit', 'Exeunt', 'Re-enter', 'Flourish', 'Alarum', 'Aside')):
                stage_directions.append(all_lines[i])
        
        # Get lines from start_index onwards
        play_lines = all_lines[start_index:]
        
        # Calculate padding needed: target_line - 1 (for stage directions) - number of stage directions
        # We want the starting dialogue at target_line, so we need (target_line - 1) total lines before it
        # If we have N stage directions, we need (target_line - 1 - N) empty lines
        padding_needed = max(0, target_line - 1 - len(stage_directions))
        
        # Combine: stage directions, padding (empty lines), then play lines
        final_lines = stage_directions + ([''] * padding_needed) + play_lines
        
        # Group consecutive lines from the same speaker
        # Keep empty lines for padding, but process them separately
        grouped_lines = []
        current_speaker = None
        
        for line in final_lines:
            # Keep empty lines as-is (for padding to reach target line)
            if not line or not line.strip():
                grouped_lines.append('')
                current_speaker = None
                continue
                
            # Check if it's a stage direction
            if re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside)', line, re.IGNORECASE):
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

def extract_play_text():
    """Extract all text from A Midsummer Night's Dream"""
    all_scenes = {}
    
    # A Midsummer Night's Dream structure:
    # Act 1: 1 scene
    # Act 2: 2 scenes
    # Act 3: 2 scenes
    # Act 4: 1 scene
    # Act 5: 1 scene
    
    scenes_structure = {
        1: [1],
        2: [1, 2],
        3: [1, 2],
        4: [1],
        5: [1]
    }
    
    for act in range(1, 6):
        for scene in scenes_structure[act]:
            scene_key = f"ACT {act} SCENE {scene}"
            lines = extract_text_from_scene(act, scene)
            
            if lines:
                all_scenes[scene_key] = {}
                for idx, line in enumerate(lines, start=1):
                    all_scenes[scene_key][str(idx)] = {
                        "play": line
                    }
                print(f"  Extracted {len(lines)} lines from {scene_key}")
            else:
                print(f"  Warning: No lines extracted from {scene_key}")
            
            # Be polite to the server
            time.sleep(0.5)
    
    return all_scenes

def main():
    print("Extracting A Midsummer Night's Dream from MIT Shakespeare website...")
    print("=" * 60)
    
    # Read existing file to preserve DRAMATIS PERSONAE
    existing_file = "Public/Data/midsummer_nights_dream.json"
    existing_data = {}
    
    try:
        with open(existing_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        print(f"Read existing file: {existing_file}")
    except Exception as e:
        print(f"Could not read existing file ({e}), creating new structure")
        existing_data = {
            "DRAMATIS PERSONAE": {
                "1": {
                    "play": "DRAMATIS PERSONAE\nMIDSUMMER NIGHTS DREAM\n\nALL\nBOTTOM\nCOBWEB\nDEMETRIUS\nEGEUS\nFLUTE\nHELENA\nHERMIA\nHERNIA\nHIPPOLYTA\nLYSANDER\nMOTH\nMUSTARDSEED\nOBERON\nPEASEBLOSSOM\nPHILOSTRATE\nPUCK\nQUINCE\nSNOUT\nSNUG\nSTARVELING\nTHESEUS\nTITANIA",
                    "notes": []
                }
            }
        }
    
    # Extract all scenes
    all_scenes = extract_play_text()
    
    # Combine with existing data
    output_data = {
        "DRAMATIS PERSONAE": existing_data.get("DRAMATIS PERSONAE", {})
    }
    output_data.update(all_scenes)
    
    # Write to file
    output_file = "Public/Data/midsummer_nights_dream.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print(f"Extraction complete! Data saved to {output_file}")
    print(f"Total scenes extracted: {len(all_scenes)}")
    
    # Print summary
    total_lines = sum(len(scene_data) for scene_data in all_scenes.values())
    print(f"Total lines extracted: {total_lines}")

if __name__ == "__main__":
    main()
