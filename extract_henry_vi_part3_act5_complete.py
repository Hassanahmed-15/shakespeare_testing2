import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

def extract_text_from_scene(act, scene):
    """Extract text from a specific act and scene - complete extraction"""
    url = f"https://shakespeare.mit.edu/3henryvi/3henryvi.{act}.{scene}.html"
    print(f"Fetching Act {act}, Scene {scene}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        lines = []
        body = soup.find('body')
        if not body:
            return lines
        
        # Process paragraphs in order
        paragraphs = body.find_all('p')
        
        for para in paragraphs:
            char_tag = para.find(['strong', 'b', 'STRONG', 'B'])
            if not char_tag:
                continue
                
            char_name = char_tag.get_text(strip=True)
            blockquote = para.find_next('blockquote')
            
            if not blockquote:
                continue
                
            # Check if stage direction
            em_tag = blockquote.find(['em', 'i', 'EM', 'I'])
            if em_tag:
                stage_dir = em_tag.get_text(separator=' ', strip=True)
                stage_dir = re.sub(r'\s+', ' ', stage_dir)
                if stage_dir:
                    lines.append(stage_dir)
                continue
            
            # Extract dialogue - handle <br> tags to preserve line breaks
            # Get text preserving structure
            dialogue_parts = []
            
            # Process each element in the blockquote
            for elem in blockquote.descendants:
                if elem.name == 'br':
                    if dialogue_parts:
                        line_text = ' '.join(dialogue_parts).strip()
                        if line_text:
                            lines.append(f"{char_name}: {line_text}")
                            dialogue_parts = []
                            current_speaker = None
                elif isinstance(elem, str):
                    text = elem.strip()
                    if text:
                        dialogue_parts.append(text)
            
            # Add remaining text
            if dialogue_parts:
                line_text = ' '.join(dialogue_parts).strip()
                if line_text:
                    lines.append(f"{char_name}: {line_text}")
        
        # Group consecutive lines from same speaker
        grouped = []
        current_speaker = None
        
        for line in lines:
            if not line.strip():
                continue
                
            if re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums|March|Drum)', line, re.IGNORECASE):
                grouped.append(line)
                current_speaker = None
            elif ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    dialogue = parts[1].strip()
                    if speaker == current_speaker:
                        grouped.append(dialogue)
                    else:
                        grouped.append(line)
                        current_speaker = speaker
                else:
                    grouped.append(line)
            else:
                grouped.append(line)
        
        return grouped
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return []

def main():
    print("Extracting complete Act 5 scenes...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, "Public", "Data", "henry_vi_part3.json")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    new_scenes = {}
    for scene in range(1, 8):
        scene_key = f"ACT 5 SCENE {scene}"
        print(f"\nExtracting {scene_key}...")
        lines = extract_text_from_scene(5, scene)
        
        if lines:
            new_scenes[scene_key] = {}
            for idx, line in enumerate(lines, start=1):
                new_scenes[scene_key][str(idx)] = {"play": line}
            print(f"  Extracted {len(lines)} lines")
        time.sleep(0.5)
    
    # Remove old Act 5
    for key in list(data.keys()):
        if key.startswith("ACT 5 SCENE"):
            del data[key]
    
    data.update(new_scenes)
    
    # Sort
    sorted_data = {"DRAMATIS PERSONAE": data["DRAMATIS PERSONAE"]}
    act_keys = sorted([k for k in data.keys() if k.startswith("ACT")], 
                     key=lambda x: (int(re.search(r'ACT (\d+)', x).group(1)),
                                   int(re.search(r'SCENE (\d+)', x).group(1))))
    for key in act_keys:
        sorted_data[key] = data[key]
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(sorted_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nComplete! Added {len(new_scenes)} scenes")

if __name__ == "__main__":
    main()

