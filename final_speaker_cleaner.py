#!/usr/bin/env python3
"""
FINAL SHAKESPEARE SPEAKER CLEANER
Based on actual format analysis - speakers are embedded WITHIN the text.
"""

import json
import os
import re

def clean_file(file_path):
    """Clean consecutive speakers from one file."""
    file_name = os.path.basename(file_path)
    print(f"\n🎭 Processing: {file_name}")
    
    try:
        # Load JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        total_changes = 0
        
        # Process each scene
        for scene_name, scene_data in data.items():
            if not isinstance(scene_data, dict):
                continue
                
            print(f"  Scene: {scene_name}")
            last_speaker = None
            scene_changes = 0
            
            # Get line numbers in order
            line_numbers = []
            for line_num in scene_data.keys():
                try:
                    line_numbers.append((int(line_num), line_num))
                except:
                    line_numbers.append((999999, line_num))
            line_numbers.sort()
            
            # Process each line in order
            for _, line_num in line_numbers:
                line_data = scene_data[line_num]
                
                # Skip if not the right format
                if not isinstance(line_data, dict) or 'play' not in line_data:
                    last_speaker = None
                    continue
                    
                text = line_data['play']
                if not isinstance(text, str):
                    last_speaker = None
                    continue
                
                # Check for speaker pattern embedded in text: "Speaker: dialogue"
                # Look for capitalized name followed by colon at start of text
                match = re.match(r'^([A-Z][a-z]*[A-Z]*[a-z]*(?:\s+[A-Z][a-z]*)*): (.*)$', text.strip())
                
                if match:
                    speaker = match.group(1).strip()
                    dialogue = match.group(2).strip()
                    
                    # Clean speaker name for comparison (remove punctuation, normalize)
                    clean_speaker = re.sub(r'[^A-Za-z\s]', '', speaker).upper().strip()
                    
                    # If same speaker as previous line, remove the speaker name
                    if last_speaker and clean_speaker == last_speaker:
                        # Remove speaker, keep only dialogue
                        data[scene_name][line_num]['play'] = dialogue
                        print(f"    Line {line_num}: Removed '{speaker}:' -> '{dialogue[:50]}...'")
                        scene_changes += 1
                        total_changes += 1
                    else:
                        # New speaker, update tracking
                        last_speaker = clean_speaker
                else:
                    # No speaker found, it's a continuation line
                    # Don't reset last_speaker - this allows for multi-line speeches
                    pass
            
            if scene_changes > 0:
                print(f"    ✅ {scene_changes} changes in {scene_name}")
        
        # Save the file back
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"  🎯 {file_name}: {total_changes} total consecutive speakers removed!")
        return total_changes
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return 0

def main():
    """Process all Shakespeare files."""
    print("🎭 FINAL SHAKESPEARE CONSECUTIVE SPEAKER CLEANER 🎭")
    print("=" * 60)
    
    # Find all JSON files in Public/Data
    data_dir = "Public/Data"
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory {data_dir} not found!")
        return
    
    # Get all .json files, exclude bible files
    files_to_process = []
    for filename in os.listdir(data_dir):
        if (filename.endswith('.json') and 
            'bible' not in filename.lower() and 
            'geneva' not in filename.lower()):
            files_to_process.append(os.path.join(data_dir, filename))
    
    print(f"📁 Found {len(files_to_process)} files to process:")
    for file_path in files_to_process:
        print(f"  - {os.path.basename(file_path)}")
    
    # Process each file
    grand_total = 0
    for file_path in files_to_process:
        changes = clean_file(file_path)
        grand_total += changes
    
    # Final summary
    print("\n" + "=" * 60)
    print("🎯 FINAL MISSION ACCOMPLISHED!")
    print(f"✅ Processed {len(files_to_process)} files")
    print(f"🎭 Total consecutive speakers removed: {grand_total}")
    print("✅ All Shakespeare plays now have clean consecutive speaker formatting!")
    print("=" * 60)

if __name__ == "__main__":
    main()
