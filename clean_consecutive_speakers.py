#!/usr/bin/env python3
"""
Shakespeare Play JSON Cleaner - Remove Consecutive Speaker Names

This script processes all Shakespeare play JSON files and removes redundant speaker names
when the same speaker appears on consecutive lines. This makes the play text look cleaner
and more natural when displayed.

The script modifies the existing JSON files directly (no new files created).
"""

import json
import os
import re
import glob
from datetime import datetime

def clean_consecutive_speakers(file_path):
    """
    Remove consecutive duplicate speaker names from a Shakespeare play JSON file.
    
    Args:
        file_path (str): Path to the JSON file to process
    
    Returns:
        bool: True if successful, False if error occurred
    """
    print(f"🎭 Processing {os.path.basename(file_path)}...")
    
    try:
        # Load the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        changes_made = 0
        
        # Process each scene in the play
        for scene_key, scene_data in data.items():
            if not isinstance(scene_data, dict):
                continue
                
            print(f"  📑 Processing scene: {scene_key}")
            scene_changes = 0
            last_speaker = None
            
            # Get all line numbers and sort them numerically
            line_numbers = sorted(scene_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
            
            # Process each line in the scene
            for line_num in line_numbers:
                line_data = scene_data[line_num]
                
                if not line_data or not isinstance(line_data, dict) or 'play' not in line_data:
                    last_speaker = None
                    continue
                
                play_content = line_data['play']
                if not isinstance(play_content, str):
                    last_speaker = None
                    continue
                
                # Check if this line has a speaker name
                match = re.match(r'^([A-Z][A-Z\s\-\']+):\s*(.*)', play_content)
                if match:
                    speaker = match.group(1).strip()
                    dialogue = match.group(2).strip()
                    
                    # Normalize speaker name for comparison
                    normalized_speaker = re.sub(r'[^\w\s]', '', speaker.lower().strip())
                    
                    # If this is the same speaker as the previous line, remove the name
                    if last_speaker and normalized_speaker == last_speaker:
                        # Remove the speaker name, keep only the dialogue
                        data[scene_key][line_num]['play'] = dialogue
                        changes_made += 1
                        scene_changes += 1
                        print(f"    🔄 Line {line_num}: Removed '{speaker}:' (consecutive)")
                    else:
                        # New speaker, update our tracking
                        last_speaker = normalized_speaker
                else:
                    # No speaker in this line, it's a continuation - don't reset last_speaker
                    pass
            
            if scene_changes > 0:
                print(f"    ✅ {scene_changes} consecutive speakers removed from {scene_key}")
        
        # Save the cleaned data back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  🎯 Total changes: {changes_made} consecutive speakers removed")
        print(f"  ✅ Successfully cleaned {os.path.basename(file_path)}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"  ❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def find_shakespeare_json_files():
    """
    Find all JSON files in the Public/Data directory that contain Shakespeare plays.
    
    Returns:
        list: List of file paths to process
    """
    data_dir = "Public/Data"
    if not os.path.exists(data_dir):
        print(f"❌ Data directory not found: {data_dir}")
        return []
    
    # Find all JSON files
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    
    # Filter out non-play files (like bible files, etc.)
    shakespeare_files = []
    exclude_patterns = [
        'bible', 'geneva', 'notes-integration', 'bibleSearch'
    ]
    
    for file_path in json_files:
        filename = os.path.basename(file_path).lower()
        if not any(pattern in filename for pattern in exclude_patterns):
            shakespeare_files.append(file_path)
    
    return shakespeare_files

def main():
    """Main function to process all Shakespeare JSON files."""
    print("🎭 Shakespeare Play Cleaner - Remove Consecutive Speaker Names")
    print("=" * 70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Find all Shakespeare JSON files
    json_files = find_shakespeare_json_files()
    
    if not json_files:
        print("❌ No Shakespeare JSON files found!")
        return
    
    print(f"📁 Found {len(json_files)} JSON files to process:")
    for file_path in json_files:
        print(f"  - {os.path.basename(file_path)}")
    print()
    
    # Process each file
    successful = 0
    failed = 0
    
    for file_path in json_files:
        if clean_consecutive_speakers(file_path):
            successful += 1
        else:
            failed += 1
        print()  # Add spacing between files
    
    # Summary
    print("=" * 70)
    print(f"🎯 Processing Complete!")
    print(f"✅ Successfully processed: {successful} files")
    if failed > 0:
        print(f"❌ Failed to process: {failed} files")
    print(f"📅 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("🎭 Your Shakespeare plays now have cleaner consecutive speaker formatting!")
    print("💾 Original files have been modified directly (no backups created)")

if __name__ == "__main__":
    main()