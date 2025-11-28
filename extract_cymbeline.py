import requests
from bs4 import BeautifulSoup
import json
import re
import time

def extract_text_from_scene(act, scene):
    """Extract text from a specific act and scene"""
    url = f"https://shakespeare.mit.edu/cymbeline/cymbeline.{act}.{scene}.html"
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
        
        # Group consecutive lines from the same speaker
        grouped_lines = []
        current_speaker = None
        
        for line in all_lines:
            if not line or not line.strip():
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
    """Extract all text from Cymbeline"""
    all_scenes = {}
    
    # Cymbeline structure:
    # Act 1: 6 scenes
    # Act 2: 5 scenes (scene 3 missing in some editions)
    # Act 3: 7 scenes
    # Act 4: 4 scenes
    # Act 5: 5 scenes
    
    scenes_structure = {
        1: [1, 2, 3, 4, 5, 6],
        2: [1, 2, 4, 5],  # Scene 3 might not exist
        3: [1, 2, 3, 4, 5, 6, 7],
        4: [1, 2, 3, 4],
        5: [1, 2, 3, 4, 5]
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
    print("Extracting Cymbeline from MIT Shakespeare website...")
    print("=" * 60)
    
    # Read existing file to preserve DRAMATIS PERSONAE
    existing_file = "Public/Data/cymbeline.json"
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
                    "play": "DRAMATIS PERSONAE\nCYMBELINE\n\nCAIUS LUCIUS\nFirst Brother\nFirst Captain\nFirst Gaoler\nFirst Gentleman\nFirst Lady\nFirst Lord\nFirst Senator\nFirst Tribune\nIn France\nPOSTHUMUS LEONATUS\nPosthumus Leonatus\nQUEEN\nSecond Brother\nSecond Captain\nSecond Gaoler\nSecond Gentleman\nSecond Lord\nSecond Senator\nSicilius Leonatus\n\nARVIRAGUS\nBELARIUS\nCLOTEN\nCORNELIUS\nCYMBELINE\nGUIDERIUS\nIACHIMO\nIMOGEN\nPHILARIO\nPISANIO",
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
    output_file = "Public/Data/cymbeline.json"
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





