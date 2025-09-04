#!/usr/bin/env python3
"""
Play Text Cleaner
Removes repetitive speaker names from consecutive lines in Macbeth play text.
"""

import json
import re
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
    
    def clean_consecutive_speakers(self, scene_data: Dict) -> Dict:
        """Clean up repetitive speaker names in consecutive lines."""
        cleaned_scene = {}
        previous_speaker = ""
        
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
                    'play': cleaned_play_text,
                    'notes': line_data.get('notes', [])
                }
                
                cleaned_scene[line_num] = cleaned_line_data
            else:
                # Keep non-play data as is
                cleaned_scene[line_num] = line_data
        
        return cleaned_scene
    
    def clean_all_scenes(self, notes_data: Dict) -> Dict:
        """Clean up all scenes in the Macbeth data."""
        print("=== CLEANING PLAY TEXT - REMOVING REPETITIVE SPEAKER NAMES ===")
        
        cleaned_data = {}
        total_scenes = len(notes_data)
        
        for i, (act_scene, scene_data) in enumerate(notes_data.items(), 1):
            print(f"Cleaning {act_scene}... ({i}/{total_scenes})")
            
            if isinstance(scene_data, dict):
                cleaned_scene = self.clean_consecutive_speakers(scene_data)
                cleaned_data[act_scene] = cleaned_scene
                
                # Count changes
                original_lines = len(scene_data)
                cleaned_lines = len(cleaned_scene)
                print(f"  ✅ {act_scene}: {original_lines} lines processed")
            else:
                print(f"  ⚠️  {act_scene}: Unexpected structure, keeping as is")
                cleaned_data[act_scene] = scene_data
        
        print(f"\n✅ Play text cleaning complete for {total_scenes} scenes!")
        return cleaned_data
    
    def show_examples(self, original_data: Dict, cleaned_data: Dict, scene_name: str = None):
        """Show examples of the cleaning process."""
        print("\n=== CLEANING EXAMPLES ===")
        
        if scene_name and scene_name in original_data and scene_name in cleaned_data:
            original_scene = original_data[scene_name]
            cleaned_scene = cleaned_data[scene_name]
            
            print(f"\nScene: {scene_name}")
            print("-" * 50)
            
            # Show first few lines as examples
            count = 0
            
            # Handle both string and integer line numbers for sorting
            def sort_key(line_num):
                try:
                    return (0, int(line_num))  # Use tuple with type indicator
                except (ValueError, TypeError):
                    return (1, str(line_num))  # Use tuple with type indicator
            
            for line_num in sorted(original_scene.keys(), key=sort_key):
                if count >= 10:  # Show only first 10 lines
                    break
                    
                if isinstance(original_scene[line_num], dict) and 'play' in original_scene[line_num]:
                    original_text = original_scene[line_num]['play']
                    cleaned_text = cleaned_scene[line_num]['play']
                    
                    if original_text != cleaned_text:
                        print(f"Line {line_num}:")
                        print(f"  BEFORE: {original_text}")
                        print(f"  AFTER:  {cleaned_text}")
                        print()
                    else:
                        print(f"Line {line_num}: {cleaned_text}")
                    
                    count += 1
        else:
            # Show examples from first available scene
            for act_scene in original_data.keys():
                if isinstance(original_data[act_scene], dict):
                    self.show_examples(original_data, cleaned_data, act_scene)
                    break

def main():
    """Main function to clean play text."""
    print("=== PLAY TEXT CLEANER FOR MACBETH ===")
    
    # Load the expanded notes
    print("Step 1: Loading expanded notes...")
    try:
        with open('macbeth_notes_complete_expanded.json', 'r', encoding='utf-8') as f:
            expanded_notes = json.load(f)
        print(f"✅ Loaded expanded notes with {len(expanded_notes)} acts/scenes")
    except FileNotFoundError:
        print("❌ File 'macbeth_notes_complete_expanded.json' not found!")
        print("Please run the bibliography processor first.")
        return
    except Exception as e:
        print(f"❌ Error loading expanded notes: {e}")
        return
    
    # Clean the play text
    print("Step 2: Cleaning play text...")
    cleaner = PlayTextCleaner()
    cleaned_notes = cleaner.clean_all_scenes(expanded_notes)
    
    # Save cleaned notes
    print("Step 3: Saving cleaned notes...")
    try:
        with open('macbeth_notes_cleaned_play.json', 'w', encoding='utf-8') as f:
            json.dump(cleaned_notes, f, indent=2, ensure_ascii=False)
        print("✅ Cleaned notes saved to 'macbeth_notes_cleaned_play.json'")
    except Exception as e:
        print(f"❌ Error saving cleaned notes: {e}")
        return
    
    # Show examples
    print("Step 4: Showing cleaning examples...")
    cleaner.show_examples(expanded_notes, cleaned_notes)
    
    print("\n" + "="*60)
    print("✅ PLAY TEXT CLEANING COMPLETE!")
    print("✅ Repetitive speaker names removed from consecutive lines!")
    print("✅ Output saved to: macbeth_notes_cleaned_play.json")
    print("="*60)

if __name__ == "__main__":
    main()
