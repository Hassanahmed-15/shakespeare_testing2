import requests
from bs4 import BeautifulSoup
import json
import time
import os

def extract_text_from_scene(act, scene):
    """Extract all text (dialogue and stage directions) from a scene"""
    url = f"https://shakespeare.mit.edu/macbeth/macbeth.{act}.{scene}.html"
    print(f"Fetching Act {act}, Scene {scene}...")
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 404:
            print(f"  Warning: Page not found for Act {act}, Scene {scene}")
            return []
            
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        body = soup.find('body')
        if not body:
            return []

        scene_elements = []

        # REMOVED recursive=False so it finds blockquotes even if they are hidden inside <p> tags
        for element in body.find_all(['a', 'blockquote']):
            
            # 1. Handle Speaker Names
            name_attr = element.get('name', '')
            if element.name == 'a' and name_attr.startswith('speech'):
                speaker_bold = element.find('b')
                if speaker_bold:
                    scene_elements.append({
                        'type': 'speaker',
                        'text': speaker_bold.get_text(strip=True)
                    })
            
            # 2. Handle Dialogue and Stage Directions
            elif element.name == 'blockquote':
                # If it contains <i>, it's usually a stage direction
                if element.find('i'):
                    scene_elements.append({
                        'type': 'stage',
                        'text': element.get_text(strip=True)
                    })
                else:
                    # It's dialogue. Get all lines within the blockquote
                    lines = list(element.stripped_strings)
                    for line in lines:
                        scene_elements.append({
                            'type': 'line',
                            'text': line
                        })

        # Format into the final list
        final_lines = []
        current_speaker = ""
        
        for item in scene_elements:
            if item['type'] == 'speaker':
                current_speaker = item['text']
            elif item['type'] == 'line':
                if current_speaker:
                    final_lines.append(f"{current_speaker}: {item['text']}")
                    current_speaker = "" # Clear so we don't repeat the name on the next line
                else:
                    final_lines.append(item['text'])
            elif item['type'] == 'stage':
                final_lines.append(item['text'])
                current_speaker = "" # Clear speaker after a stage direction

        return final_lines
    
    except Exception as e:
        print(f"  Error fetching Act {act}, Scene {scene}: {e}")
        return []

def extract_play_text():
    """Extract all text from Macbeth"""
    all_scenes = {}
    
    # Macbeth structure:
    scenes_structure = {
        1: 7, # Act 1: 7 scenes
        2: 4, # Act 2: 4 scenes
        3: 6, # Act 3: 6 scenes
        4: 3, # Act 4: 3 scenes
        5: 8  # Act 5: 8 scenes
    }
    
    for act, num_scenes in scenes_structure.items():
        for scene in range(1, num_scenes + 1):
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
    print("Extracting Macbeth from MIT Shakespeare website...")
    print("=" * 60)
    
    output_dir = "Public/Data"
    output_file = f"{output_dir}/macbeth.json"
    
    # Ensure the directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract all scenes
    all_scenes = extract_play_text()
    
    # Write to file directly (no Dramatis Personae logic)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_scenes, f, indent=2, ensure_ascii=False)
    
    print("=" * 60)
    print(f"Extraction complete! Data saved to {output_file}")
    print(f"Total scenes extracted: {len(all_scenes)}")
    
    # Print summary
    total_lines = sum(len(scene_data) for scene_data in all_scenes.values())
    print(f"Total lines extracted: {total_lines}")

if __name__ == "__main__":
    main()