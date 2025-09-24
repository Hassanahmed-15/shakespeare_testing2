#!/usr/bin/env python3
"""
Debug script to find consecutive speaker patterns in Shakespeare JSON files.
"""

import json
import os
import re

def analyze_file(filepath):
    """Analyze a file to find consecutive speaker patterns."""
    print(f"\n🔍 Analyzing: {os.path.basename(filepath)}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        consecutive_found = 0
        
        # Process first scene only for debugging
        scene_keys = list(data.keys())
        if not scene_keys:
            return 0
            
        first_scene = scene_keys[0]
        scene_data = data[first_scene]
        
        if not isinstance(scene_data, dict):
            return 0
        
        print(f"  Checking scene: {first_scene}")
        
        last_speaker = None
        line_keys = sorted(scene_data.keys(), key=lambda x: int(x) if x.isdigit() else 0)
        
        # Check first 20 lines for patterns
        for i, line_key in enumerate(line_keys[:20]):
            line_data = scene_data[line_key]
            
            if not isinstance(line_data, dict) or 'play' not in line_data:
                continue
                
            play_text = line_data['play']
            if not isinstance(play_text, str):
                continue
            
            print(f"    Line {line_key}: {play_text[:80]}...")
            
            # Check for speaker pattern
            speaker_match = re.match(r'^([A-Z][A-Z\s\-\'\.]+):\s*(.*)', play_text)
            
            if speaker_match:
                speaker = speaker_match.group(1).strip()
                dialogue = speaker_match.group(2).strip()
                
                print(f"      → Found speaker: '{speaker}'")
                
                # Normalize for comparison
                normalized_speaker = re.sub(r'[^\w\s]', '', speaker).lower().strip()
                
                if last_speaker and normalized_speaker == last_speaker:
                    print(f"      🎯 CONSECUTIVE! Same as previous: '{speaker}'")
                    consecutive_found += 1
                
                last_speaker = normalized_speaker
            else:
                print(f"      → No speaker found (continuation line)")
        
        return consecutive_found
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 0

def main():
    """Find consecutive patterns in Shakespeare files."""
    data_dir = "Public/Data"
    
    # Test with just a few files first
    test_files = [
        "As_You_Like_It.json",
        "hamlet_notes (1).json", 
        "macbeth_notes_cleaned_play.json"
    ]
    
    total_consecutive = 0
    
    for filename in test_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            consecutive = analyze_file(filepath)
            total_consecutive += consecutive
        else:
            print(f"❌ File not found: {filename}")
    
    print(f"\n🎯 Total consecutive speakers found: {total_consecutive}")

if __name__ == "__main__":
    main()
