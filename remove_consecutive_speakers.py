#!/usr/bin/env python3
"""
Remove Consecutive Speaker Names Script
This script processes Hamlet, King Lear, and Othello JSON files to remove
consecutive duplicate speaker names, keeping only the first occurrence.
"""

import json
import re
import os
from typing import Dict, Any

def extract_speaker_name(line_text: str) -> str:
    """
    Extract speaker name from a line of text.
    Assumes speaker names are at the beginning followed by a colon.
    """
    if not line_text or not isinstance(line_text, str):
        return ""
    
    # Match speaker name pattern: "Name:" or "Name :" at the start
    match = re.match(r'^([A-Z][A-Z\s\'.,-]+?):\s*', line_text.strip())
    if match:
        return match.group(1).strip()
    return ""

def remove_speaker_from_line(line_text: str) -> str:
    """
    Remove speaker name from the beginning of a line, keeping the rest.
    """
    if not line_text or not isinstance(line_text, str):
        return line_text
    
    # Remove speaker name pattern from the beginning
    cleaned = re.sub(r'^([A-Z][A-Z\s\'.,-]+?):\s*', '', line_text.strip())
    return cleaned

def process_play_data(play_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a play's JSON data to remove consecutive duplicate speaker names.
    """
    processed_data = {}
    
    for scene_key, scene_data in play_data.items():
        if not isinstance(scene_data, dict):
            processed_data[scene_key] = scene_data
            continue
            
        processed_scene = {}
        last_speaker = None
        
        # Sort line numbers to process in order
        line_numbers = sorted(scene_data.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
        
        for line_num in line_numbers:
            line_data = scene_data[line_num]
            
            if isinstance(line_data, dict) and 'play' in line_data:
                line_text = line_data['play']
            elif isinstance(line_data, str):
                line_text = line_data
            else:
                processed_scene[line_num] = line_data
                continue
            
            if not line_text:
                processed_scene[line_num] = line_data
                continue
            
            # Extract current speaker
            current_speaker = extract_speaker_name(line_text)
            
            if current_speaker:
                if current_speaker == last_speaker:
                    # Same speaker as previous line - remove speaker name
                    cleaned_text = remove_speaker_from_line(line_text)
                    if isinstance(line_data, dict):
                        new_line_data = line_data.copy()
                        new_line_data['play'] = cleaned_text
                    else:
                        new_line_data = cleaned_text
                    processed_scene[line_num] = new_line_data
                else:
                    # Different speaker or first occurrence - keep as is
                    processed_scene[line_num] = line_data
                    last_speaker = current_speaker
            else:
                # No speaker detected - keep as is, don't change last_speaker
                processed_scene[line_num] = line_data
        
        processed_data[scene_key] = processed_scene
    
    return processed_data

def process_play_file(file_path: str) -> bool:
    """
    Process a single play JSON file.
    Returns True if successful, False otherwise.
    """
    try:
        print(f"Processing {file_path}...")
        
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            play_data = json.load(f)
        
        # Process the data
        processed_data = process_play_data(play_data)
        
        # Create backup
        backup_path = file_path + '.backup'
        if not os.path.exists(backup_path):
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(play_data, f, indent=2, ensure_ascii=False)
            print(f"  ✅ Backup created: {backup_path}")
        
        # Write the processed data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Successfully processed {file_path}")
        return True
        
    except Exception as e:
        print(f"  ❌ Error processing {file_path}: {e}")
        return False

def main():
    """
    Main function to process Hamlet, King Lear, and Othello JSON files.
    """
    # Define the files to process
    files_to_process = [
        'Public/Data/hamlet_notes (1).json',
        'Public/Data/kinglear_notes.json',
        'Public/Data/othello_notes.json'
    ]
    
    print("🎭 Starting consecutive speaker name removal for Shakespeare plays...")
    print("=" * 60)
    
    success_count = 0
    total_count = len(files_to_process)
    
    for file_path in files_to_process:
        if os.path.exists(file_path):
            if process_play_file(file_path):
                success_count += 1
        else:
            print(f"  ❌ File not found: {file_path}")
    
    print("=" * 60)
    print(f"🎯 Processing complete: {success_count}/{total_count} files successfully processed")
    
    if success_count == total_count:
        print("✅ All files processed successfully!")
    else:
        print("⚠️  Some files had errors. Check the output above for details.")

if __name__ == "__main__":
    main()
