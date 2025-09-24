#!/usr/bin/env python3
"""
Simple script to remove consecutive duplicate speaker names from Shakespeare JSON files.
This script processes the 'play' field and removes speaker names when they appear consecutively.
"""

import json
import os
import re

def process_file(filepath):
    """Process a single JSON file to remove consecutive speaker names."""
    print(f"Processing: {os.path.basename(filepath)}")
    
    try:
        # Read the JSON file
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        changes = 0
        
        # Process each scene
        for scene_key, scene_data in data.items():
            if not isinstance(scene_data, dict):
                continue
            
            last_speaker = None
            scene_changes = 0
            
            # Sort line numbers numerically
            line_keys = sorted(scene_data.keys(), key=lambda x: int(x) if x.isdigit() else 0)
            
            for line_key in line_keys:
                line_data = scene_data[line_key]
                
                if not isinstance(line_data, dict) or 'play' not in line_data:
                    last_speaker = None
                    continue
                    
                play_text = line_data['play']
                if not isinstance(play_text, str):
                    last_speaker = None
                    continue
                
                # Check if line starts with "SPEAKER:" pattern
                speaker_match = re.match(r'^([A-Z][A-Z\s\-\'\.]+):\s*(.*)', play_text)
                
                if speaker_match:
                    speaker = speaker_match.group(1).strip()
                    dialogue = speaker_match.group(2).strip()
                    
                    # Normalize speaker name for comparison
                    normalized_speaker = re.sub(r'[^\w\s]', '', speaker).lower().strip()
                    
                    # If this is the same speaker as the last line, remove the name
                    if last_speaker and normalized_speaker == last_speaker:
                        # Update the play text to remove the speaker name
                        data[scene_key][line_key]['play'] = dialogue
                        changes += 1
                        scene_changes += 1
                        print(f"  Removed '{speaker}:' from line {line_key}")
                    
                    # Update last speaker
                    last_speaker = normalized_speaker
                # If no speaker pattern found, don't reset last_speaker (it's a continuation)
            
            if scene_changes > 0:
                print(f"  Scene {scene_key}: {scene_changes} changes")
        
        # Write the updated data back
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {os.path.basename(filepath)}: {changes} total changes made")
        return changes
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return 0

def main():
    """Find and process all Shakespeare JSON files."""
    data_dir = "Public/Data"
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory not found: {data_dir}")
        return
    
    # Find all JSON files
    json_files = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json') and not any(x in filename.lower() for x in ['bible', 'geneva']):
            json_files.append(os.path.join(data_dir, filename))
    
    if not json_files:
        print("❌ No JSON files found!")
        return
    
    print(f"Found {len(json_files)} files to process")
    print("-" * 50)
    
    total_changes = 0
    for filepath in json_files:
        changes = process_file(filepath)
        total_changes += changes
        print()
    
    print("-" * 50)
    print(f"🎯 COMPLETE: {total_changes} total consecutive speakers removed!")

if __name__ == "__main__":
    main()