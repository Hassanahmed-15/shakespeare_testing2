#!/usr/bin/env python3
"""
Debug script to see the exact format and find consecutive speaker patterns
"""

import json
import re

def debug_file(filename):
    """Debug a specific file to see the format."""
    print(f"\n🔍 DEBUGGING: {filename}")
    
    with open(f"Public/Data/{filename}", 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Look at first scene
    first_scene = list(data.keys())[0]
    scene_data = data[first_scene]
    
    print(f"Scene: {first_scene}")
    
    # Get first 30 lines to analyze
    lines = []
    for line_num in scene_data.keys():
        try:
            num = int(line_num)
            lines.append((num, line_num))
        except:
            lines.append((999999, line_num))
    lines.sort()
    
    print("First 30 lines:")
    speakers_found = []
    
    for i, (_, line_num) in enumerate(lines[:30]):
        line_data = scene_data[line_num]
        if isinstance(line_data, dict) and 'play' in line_data:
            text = line_data['play']
            
            # Check for speaker pattern
            match = re.match(r'^([A-Z][A-Z\s\-\'\.]+):\s*(.*)$', text.strip())
            
            if match:
                speaker = match.group(1).strip()
                dialogue = match.group(2).strip()
                speakers_found.append(speaker)
                print(f"  Line {line_num}: SPEAKER='{speaker}' TEXT='{dialogue[:40]}...'")
            else:
                print(f"  Line {line_num}: NO SPEAKER - '{text[:50]}...'")
    
    print(f"\nSpeakers found: {speakers_found}")
    
    # Look for consecutive patterns
    consecutive = []
    for i in range(1, len(speakers_found)):
        if speakers_found[i] == speakers_found[i-1]:
            consecutive.append(f"{speakers_found[i]} appears consecutively")
    
    if consecutive:
        print(f"🎯 CONSECUTIVE SPEAKERS FOUND: {consecutive}")
    else:
        print("❌ NO CONSECUTIVE SPEAKERS FOUND")

# Test a few files
files_to_test = ["As_You_Like_It.json", "hamlet_notes (1).json"]

for filename in files_to_test:
    try:
        debug_file(filename)
    except Exception as e:
        print(f"Error with {filename}: {e}")

print("\n" + "="*50)
print("This will help us understand the exact format!")
