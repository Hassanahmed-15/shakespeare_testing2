import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os

def extract_from_project_gutenberg():
    """Extract Two Noble Kinsmen from Project Gutenberg"""
    url = "https://www.gutenberg.org/files/1506/1506-h/1506-h.htm"
    print(f"Fetching from Project Gutenberg: {url}")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main content
        lines = []
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Find the play content (usually in body or specific div)
        body = soup.find('body')
        if not body:
            return lines
        
        # Extract text structure
        # Look for act/scene markers
        text_content = body.get_text(separator='\n')
        
        # Split by ACT and SCENE markers
        acts = re.split(r'ACT\s+([IVX]+)', text_content, flags=re.IGNORECASE)
        
        scenes_dict = {}
        current_act = None
        current_scene = None
        
        for i, section in enumerate(acts):
            if i == 0:
                continue  # Skip content before first ACT
            
            if i % 2 == 1:
                # This is an act number
                act_num = section
                # Convert Roman to Arabic
                act_num_arabic = roman_to_arabic(act_num)
                current_act = act_num_arabic
                scenes_dict[current_act] = {}
            else:
                # This is act content, split by scenes
                scenes = re.split(r'SCENE\s+([IVX]+)', section, flags=re.IGNORECASE)
                
                for j, scene_content in enumerate(scenes):
                    if j == 0:
                        continue  # Skip content before first SCENE
                    
                    if j % 2 == 1:
                        # This is a scene number
                        scene_num = section if isinstance(section, str) else scene_content
                        scene_num_arabic = roman_to_arabic(scene_num)
                        current_scene = scene_num_arabic
                        if current_act:
                            scenes_dict[current_act][current_scene] = []
                    else:
                        # This is scene content
                        if current_act and current_scene:
                            scene_lines = parse_scene_content(scene_content)
                            scenes_dict[current_act][current_scene] = scene_lines
        
        return scenes_dict
        
    except Exception as e:
        print(f"Error fetching from Project Gutenberg: {e}")
        import traceback
        traceback.print_exc()
        return {}

def roman_to_arabic(roman):
    """Convert Roman numeral to Arabic"""
    roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    result = 0
    prev_value = 0
    
    for char in roman[::-1]:
        value = roman_map.get(char.upper(), 0)
        if value < prev_value:
            result -= value
        else:
            result += value
        prev_value = value
    
    return result

def parse_scene_content(content):
    """Parse scene content into structured lines"""
    lines = []
    
    # Split by lines
    raw_lines = content.split('\n')
    
    current_speaker = None
    
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if it's a stage direction (all caps or in brackets)
        if re.match(r'^\[.*\]$', line) or (line.isupper() and len(line) > 10):
            lines.append(line)
            current_speaker = None
        # Check if it's a character name (often all caps or followed by period)
        elif re.match(r'^[A-Z][A-Z\s]+\s*\.?\s*$', line) and len(line) < 40:
            current_speaker = line.rstrip('. ').strip()
        # Check if line starts with character name followed by period or colon
        elif re.match(r'^[A-Z][A-Z\s]+[.:]\s+', line):
            parts = re.split(r'([A-Z][A-Z\s]+)[.:]\s+', line, 1)
            if len(parts) >= 3:
                speaker = parts[1].strip()
                dialogue = parts[2].strip()
                if speaker == current_speaker:
                    lines.append(dialogue)
                else:
                    lines.append(f"{speaker}: {dialogue}")
                    current_speaker = speaker
            else:
                if current_speaker:
                    lines.append(line)
                else:
                    lines.append(line)
        else:
            # Regular dialogue line
            if current_speaker:
                lines.append(line)
            else:
                lines.append(line)
    
    return lines

def extract_from_mit_alternative():
    """Try alternative MIT URL patterns"""
    # Try different URL patterns
    url_patterns = [
        "https://shakespeare.mit.edu/twokinsmen/twokinsmen.{act}.{scene}.html",
        "https://shakespeare.mit.edu/noblekingsmen/noblekingsmen.{act}.{scene}.html",
    ]
    
    # Known structure for Two Noble Kinsmen: 5 acts
    scenes_structure = {
        1: [1, 2, 3, 4, 5],
        2: [1, 2, 3, 4, 5, 6],
        3: [1, 2, 3, 4, 5, 6],
        4: [1, 2, 3],
        5: [1, 2, 3, 4, 5, 6]
    }
    
    for pattern in url_patterns:
        print(f"Trying pattern: {pattern}")
        # Test first scene
        test_url = pattern.format(act=1, scene=1)
        try:
            response = requests.get(test_url, timeout=10)
            if response.status_code == 200:
                print(f"Found working URL pattern: {pattern}")
                # Extract using this pattern
                return extract_from_mit_with_pattern(pattern, scenes_structure)
        except:
            continue
    
    return {}

def extract_from_mit_with_pattern(url_pattern, scenes_structure):
    """Extract using a working MIT URL pattern"""
    all_scenes = {}
    
    for act in sorted(scenes_structure.keys()):
        for scene in scenes_structure[act]:
            url = url_pattern.format(act=act, scene=scene)
            print(f"Fetching Act {act}, Scene {scene}...")
            
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                lines = []
                body = soup.find('body')
                if not body:
                    continue
                
                # Process paragraphs
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
                        if stage_dir:
                            lines.append(stage_dir)
                        continue
                    
                    # Extract dialogue
                    dialogue_text = blockquote.get_text(separator=' ', strip=True)
                    if dialogue_text:
                        lines.append(f"{char_name}: {dialogue_text}")
                
                if lines:
                    scene_key = f"ACT {act} SCENE {scene}"
                    all_scenes[scene_key] = {}
                    for idx, line in enumerate(lines, start=1):
                        all_scenes[scene_key][str(idx)] = {"play": line}
                    print(f"  Extracted {len(lines)} lines")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"  Error: {e}")
                continue
    
    return all_scenes

def main():
    print("Extracting Two Noble Kinsmen...")
    print("=" * 60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(script_dir, "Public", "Data", "two_noble_kinsmen.json")
    
    # Try MIT first (unlikely to work)
    print("\nAttempting to extract from MIT Shakespeare website...")
    all_scenes = extract_from_mit_alternative()
    
    if not all_scenes:
        print("\nMIT website not available. Trying Project Gutenberg...")
        scenes_dict = extract_from_project_gutenberg()
        
        # Convert to our format
        all_scenes = {}
        for act in sorted(scenes_dict.keys()):
            for scene in sorted(scenes_dict[act].keys()):
                scene_key = f"ACT {act} SCENE {scene}"
                all_scenes[scene_key] = {}
                for idx, line in enumerate(scenes_dict[act][scene], start=1):
                    all_scenes[scene_key][str(idx)] = {"play": line}
    
    if not all_scenes:
        print("\nERROR: Could not extract play from any source!")
        print("Please provide the URL or source you'd like me to extract from.")
        return
    
    # Read existing file
    existing_data = {}
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        print(f"\nRead existing file: {json_file}")
    except:
        existing_data = {
            "DRAMATIS PERSONAE": {
                "1": {
                    "play": "DRAMATIS PERSONAE\nTWO NOBLE KINSMEN",
                    "notes": []
                }
            }
        }
    
    # Remove existing scenes
    keys_to_remove = [key for key in existing_data.keys() if key.startswith("ACT")]
    for key in keys_to_remove:
        del existing_data[key]
    
    # Combine
    output_data = {}
    output_data["DRAMATIS PERSONAE"] = existing_data.get("DRAMATIS PERSONAE", {})
    
    # Add scenes in order
    for act_num in sorted(set(int(k.split(' ')[1]) for k in all_scenes.keys() if k.startswith('ACT'))):
        for scene_num in sorted(set(int(k.split(' ')[3]) for k in all_scenes.keys() if k.startswith(f'ACT {act_num}'))):
            scene_key = f"ACT {act_num} SCENE {scene_num}"
            if scene_key in all_scenes:
                output_data[scene_key] = all_scenes[scene_key]
    
    # Write to file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print(f"Extraction complete! Data saved to {json_file}")
    print(f"Total scenes extracted: {len(all_scenes)}")
    total_lines = sum(len(scene_data) for scene_data in all_scenes.values())
    print(f"Total lines extracted: {total_lines}")

if __name__ == "__main__":
    main()
