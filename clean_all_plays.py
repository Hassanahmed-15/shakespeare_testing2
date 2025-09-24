#!/usr/bin/env python3
"""
Play Text Cleaner for All Shakespeare Plays
Removes repetitive speaker names from consecutive lines in all Shakespeare play JSON files.
"""

import json
import re
import os
import glob
from typing import Dict, List, Tuple

class PlayTextCleaner:
    """Cleans up repetitive speaker names in play text."""
    
    def __init__(self):
        # Fix regex to capture speaker names like "First Witch", "Second Witch", "DUNCAN", etc.
        self.speaker_pattern = re.compile(r'^([A-Z][a-zA-Z\s]+):\s*(.*)$')
    
    def extract_speaker_and_text(self, line: str) -> Tuple[str, str]:
        """Extract speaker name and text from a line."""
        match = self.speaker_pattern.match(line)
        if match:
            speaker = match.group(1).strip()
            text = match.group(2).strip()
            return speaker, text
        return "", line
    
    def clean_consecutive_speakers(self, scene_data: Dict) -> Tuple[Dict, int]:
        """Clean up repetitive speaker names in consecutive lines."""
        cleaned_scene = {}
        previous_speaker = ""
        changes_made = 0
        
        # Sort lines by line number to ensure proper order
        # Handle both string and integer line numbers
        def sort_key(item):
            line_num = item[0]
            try:
                # Try to convert to int for numeric sorting
                return (0, int(line_num))  # Use tuple with type indicator
            except (ValueError, TypeError):
                # If not numeric, keep as string
                return (1, str(line_num))  # Use tuple with type indicator
        
        sorted_lines = sorted(scene_data.items(), key=sort_key)
        
        for line_num, line_data in sorted_lines:
            if isinstance(line_data, dict) and 'play' in line_data:
                play_text = line_data['play']
                speaker, text = self.extract_speaker_and_text(play_text)
                
                if speaker and speaker == previous_speaker:
                    # Same speaker as previous line - remove speaker name
                    cleaned_play_text = text
                    changes_made += 1
                    print(f"    Removed '{speaker}:' from line {line_num}")
                elif speaker:
                    # New speaker - keep speaker name
                    cleaned_play_text = f"{speaker}: {text}"
                    previous_speaker = speaker
                else:
                    # No speaker pattern found - keep as is
                    cleaned_play_text = play_text
                    previous_speaker = ""
                
                # Create cleaned line data
                cleaned_line_data = {
                    'play': cleaned_play_text
                }
                
                # Preserve notes if they exist
                if 'notes' in line_data:
                    cleaned_line_data['notes'] = line_data['notes']
                
                cleaned_scene[line_num] = cleaned_line_data
            else:
                # Keep non-play data as is
                cleaned_scene[line_num] = line_data
        
        return cleaned_scene, changes_made
    
    def clean_all_scenes(self, notes_data: Dict, filename: str) -> Tuple[Dict, int]:
        """Clean up all scenes in the play data."""
        print(f"=== CLEANING {filename} - REMOVING REPETITIVE SPEAKER NAMES ===")
        
        cleaned_data = {}
        total_scenes = len(notes_data)
        total_changes = 0
        
        for i, (act_scene, scene_data) in enumerate(notes_data.items(), 1):
            print(f"  Cleaning {act_scene}... ({i}/{total_scenes})")
            
            if isinstance(scene_data, dict):
                cleaned_scene, scene_changes = self.clean_consecutive_speakers(scene_data)
                cleaned_data[act_scene] = cleaned_scene
                total_changes += scene_changes
                
                # Count changes
                original_lines = len(scene_data)
                print(f"    ✅ {act_scene}: {original_lines} lines processed, {scene_changes} changes")
            else:
                print(f"    ⚠️  {act_scene}: Unexpected structure, keeping as is")
                cleaned_data[act_scene] = scene_data
        
        print(f"  🎯 {filename}: {total_changes} total consecutive speakers removed!")
        return cleaned_data, total_changes

def process_file(filepath: str, cleaner: PlayTextCleaner) -> int:
    """Process a single Shakespeare play file."""
    filename = os.path.basename(filepath)
    
    try:
        # Load the play data
        print(f"\n📖 Loading {filename}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            play_data = json.load(f)
        
        # Clean the play text
        cleaned_data, changes_made = cleaner.clean_all_scenes(play_data, filename)
        
        # Save back to the same file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {filename}: Successfully cleaned and saved with {changes_made} changes")
        return changes_made
        
    except Exception as e:
        print(f"❌ Error processing {filename}: {e}")
        return 0

def main():
    """Main function to clean all play texts."""
    print("🎭 SHAKESPEARE PLAY TEXT CLEANER - ALL PLAYS 🎭")
    print("=" * 60)
    
    # Find all Shakespeare JSON files
    data_dir = "Public/Data"
    if not os.path.exists(data_dir):
        print(f"❌ Directory not found: {data_dir}")
        return
    
    # Find all JSON files, exclude non-play files
    json_files = []
    exclude_patterns = ['bible', 'geneva', 'notes-integration', 'bibleSearch']
    
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            if not any(pattern in filename.lower() for pattern in exclude_patterns):
                json_files.append(os.path.join(data_dir, filename))
    
    if not json_files:
        print("❌ No Shakespeare play JSON files found!")
        return
    
    print(f"📁 Found {len(json_files)} Shakespeare play files:")
    for filepath in json_files:
        print(f"  - {os.path.basename(filepath)}")
    
    print("\n🔄 Starting processing...")
    
    # Initialize cleaner
    cleaner = PlayTextCleaner()
    
    # Process each file
    total_changes = 0
    successful = 0
    failed = 0
    
    for filepath in json_files:
        changes = process_file(filepath, cleaner)
        if changes >= 0:  # Even 0 changes is successful processing
            total_changes += changes
            successful += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("🎯 PROCESSING COMPLETE!")
    print(f"✅ Successfully processed: {successful} files")
    if failed > 0:
        print(f"❌ Failed to process: {failed} files")
    print(f"🎭 Total consecutive speakers removed: {total_changes}")
    print("✅ All Shakespeare plays now have cleaner text formatting!")
    print("=" * 60)

if __name__ == "__main__":
    main()
