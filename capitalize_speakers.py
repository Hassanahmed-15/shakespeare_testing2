#!/usr/bin/env python3
"""
Script to capitalize speaker names in Shakespeare play JSON files.
This script processes all JSON files in the Public/Data directory and 
capitalizes speaker names that appear before colons in the dialogue.
"""

import json
import os
import re
import glob
from pathlib import Path

def capitalize_speaker_names(text):
    """
    Capitalize speaker names that appear before colons in dialogue text.
    
    Args:
        text (str): The dialogue text to process
        
    Returns:
        str: Text with capitalized speaker names
    """
    if not text:
        return text
    
    # Pattern to match speaker names followed by colon
    # This matches words (letters, spaces, apostrophes, periods) followed by a colon and space
    # Updated to handle abbreviated names like "Rodo." and "Iago."
    pattern = r'^([A-Za-z\s\'\.]+):\s'
    
    # Check if the line starts with a speaker name pattern
    match = re.match(pattern, text)
    if match:
        speaker_name = match.group(1).strip()
        # Capitalize the speaker name
        capitalized_speaker = speaker_name.upper()
        # Replace the original speaker name with the capitalized version
        return text.replace(speaker_name + ':', capitalized_speaker + ':', 1)
    
    return text

def process_json_file(file_path):
    """
    Process a single JSON file to capitalize speaker names.
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        bool: True if file was modified, False otherwise
    """
    try:
        # Read the JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # Process each section in the JSON
        for section_key, section_data in data.items():
            if isinstance(section_data, dict):
                for item_key, item_data in section_data.items():
                    if isinstance(item_data, dict) and 'play' in item_data:
                        original_text = item_data['play']
                        if original_text:
                            new_text = capitalize_speaker_names(original_text)
                            if new_text != original_text:
                                item_data['play'] = new_text
                                modified = True
        
        # Write back to file if modified
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Updated: {file_path}")
            return True
        else:
            print(f"- No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f"✗ Error processing {file_path}: {str(e)}")
        return False

def main():
    """
    Main function to process all JSON files in the Public/Data directory.
    """
    # Get the directory containing the JSON files
    data_dir = Path("Public/Data")
    
    if not data_dir.exists():
        print(f"Error: Directory {data_dir} does not exist!")
        return
    
    # Find all JSON files
    json_files = list(data_dir.glob("*.json"))
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return
    
    print(f"Found {len(json_files)} JSON files to process:")
    for file_path in json_files:
        print(f"  - {file_path.name}")
    
    print("\nProcessing files...")
    
    modified_count = 0
    total_count = len(json_files)
    
    for file_path in json_files:
        if process_json_file(file_path):
            modified_count += 1
    
    print(f"\nProcessing complete!")
    print(f"Files processed: {total_count}")
    print(f"Files modified: {modified_count}")
    print(f"Files unchanged: {total_count - modified_count}")

if __name__ == "__main__":
    main()
