import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

def extract_text_from_scene(act, scene):
    """Extract text from a specific act and scene"""
    url = f"https://shakespeare.mit.edu/3henryvi/3henryvi.{act}.{scene}.html"
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
        
        # Process all elements in order by walking through the body
        elements_with_pos = []
        
        # Find all paragraphs with STRONG tags (character names)
        all_paragraphs = body.find_all('p')
        
        for para in all_paragraphs:
            # Find STRONG or B tag for character name
            char_tag = para.find(['strong', 'b', 'STRONG', 'B'])
            
            if char_tag:
                char_name = char_tag.get_text(strip=True)
                
                # Find the following blockquote
                blockquote = para.find_next('blockquote')
                
                if blockquote:
                    # Check if it's a stage direction (contains EM or I tag)
                    em_tag = blockquote.find(['em', 'i', 'EM', 'I'])
                    
                    if em_tag:
                        stage_dir = em_tag.get_text(strip=True)
                        # Clean up stage direction but preserve structure
                        stage_dir = ' '.join(stage_dir.split())
                        if stage_dir:
                            elements_with_pos.append(('stage', para.sourceline or 0, stage_dir))
                    else:
                        # It's dialogue - extract each line separately
                        # Each <a> tag or <br> indicates a potential line break
                        blockquote_text = blockquote.get_text(separator='\n', strip=False)
                        
                        # Split by <br> tags to get individual lines
                        br_tags = blockquote.find_all('br')
                        if br_tags:
                            # Get text segments between <br> tags
                            parts = []
                            current_text = []
                            
                            for element in blockquote.descendants:
                                if element.name == 'br':
                                    if current_text:
                                        text = ' '.join(current_text).strip()
                                        if text:
                                            parts.append(text)
                                        current_text = []
                                elif isinstance(element, str) and element.strip():
                                    current_text.append(element.strip())
                            
                            # Add remaining text
                            if current_text:
                                text = ' '.join(current_text).strip()
                                if text:
                                    parts.append(text)
                            
                            # If we didn't get parts from <br>, try getting all <a> tags
                            if not parts:
                                for link in blockquote.find_all('a'):
                                    link_text = link.get_text(strip=True)
                                    if link_text:
                                        parts.append(link_text)
                        else:
                            # No <br> tags, extract all <a> tags individually
                            parts = []
                            for link in blockquote.find_all('a'):
                                link_text = link.get_text(strip=True)
                                if link_text:
                                    parts.append(link_text)
                        
                        # If still no parts, get all text
                        if not parts:
                            full_text = blockquote.get_text(separator=' ', strip=True)
                            if full_text:
                                parts = [full_text]
                        
                        # Add each part as a separate line with character name
                        for part in parts:
                            part = part.strip()
                            if part:
                                elements_with_pos.append(('speech', para.sourceline or 0, char_name, part))
        
        # Also find standalone stage directions
        all_blockquotes = body.find_all('blockquote')
        for blockquote in all_blockquotes:
            em_tag = blockquote.find(['em', 'i', 'EM', 'I'])
            if em_tag:
                stage_dir = em_tag.get_text(strip=True)
                stage_dir = ' '.join(stage_dir.split())
                if stage_dir and not any(elem[2] == stage_dir for elem in elements_with_pos if elem[0] == 'stage'):
                    elements_with_pos.append(('stage', blockquote.sourceline or 0, stage_dir))
        
        # Sort by position
        elements_with_pos.sort(key=lambda x: x[1])
        
        # Build the lines list
        all_lines = []
        for elem in elements_with_pos:
            if elem[0] == 'stage':
                all_lines.append(elem[2])
            elif elem[0] == 'speech':
                char_name = elem[2]
                dialogue = elem[3]
                all_lines.append(f"{char_name}: {dialogue}")
        
        # Group consecutive lines from the same speaker
        grouped_lines = []
        current_speaker = None
        
        for line in all_lines:
            if not line or not line.strip():
                continue
                
            # Check if it's a stage direction
            if re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums|March|Drum|DUMB SHOW)', line, re.IGNORECASE):
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
    print("Extracting Act 5 scenes from Henry VI Part 3...")
    print("=" * 60)
    
    # Get the script directory and construct the path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, "Public", "Data", "henry_vi_part3.json")
    
    # Read existing file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Read existing file: {json_file}")
    
    # Extract all 7 scenes of Act 5
    scenes_to_extract = [
        (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)
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
    
    # Remove any existing Act 5 scenes if they exist
    keys_to_remove = [k for k in data.keys() if k.startswith("ACT 5 SCENE")]
    for key in keys_to_remove:
        del data[key]
        print(f"  Removed existing {key}")
    
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
    print(f"Added {len(new_scenes)} scenes from Act 5")
    total_lines = sum(len(scene_data) for scene_data in new_scenes.values())
    print(f"Total lines extracted: {total_lines}")

if __name__ == "__main__":
    main()
