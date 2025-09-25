#!/usr/bin/env python3
"""
Script to extract Dramatis Personae (character lists) from Shakespeare plays
and add them as separate entries above ACT 1 in the JSON structure.
"""

import json
import os
import re
from collections import defaultdict
from pathlib import Path

class DramatisPersonaeExtractor:
    def __init__(self, data_dir="Public/Data"):
        self.data_dir = Path(data_dir)
        self.character_patterns = [
            r'^([A-Z][A-Z\s\-\']+):',  # Character names in caps followed by colon
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+):',  # Two-word character names
            r'^([A-Z][A-Z]+):',  # Single word character names in caps
        ]
        
        # Common non-character patterns to exclude
        self.exclude_patterns = [
            r'^(ACT|SCENE|Enter|Exit|Stage Direction)',
            r'^\[.*\]',  # Stage directions in brackets
            r'^\d+$',  # Just numbers
            r'^[^A-Z]',  # Doesn't start with capital
        ]
    
    def extract_characters_from_play(self, play_data):
        """Extract unique characters from a play's dialogue."""
        characters = set()
        
        for scene_name, scene_data in play_data.items():
            if not isinstance(scene_data, dict):
                continue
                
            for line_num, line_data in scene_data.items():
                if not isinstance(line_data, dict) or 'play' not in line_data:
                    continue
                    
                play_text = line_data['play']
                if not play_text:
                    continue
                
                # Check if line contains character dialogue
                for pattern in self.character_patterns:
                    match = re.match(pattern, play_text.strip())
                    if match:
                        character_name = match.group(1).strip()
                        
                        # Filter out non-character patterns
                        if not any(re.match(exclude_pattern, character_name) for exclude_pattern in self.exclude_patterns):
                            # Clean up character name
                            character_name = self.clean_character_name(character_name)
                            if character_name:
                                characters.add(character_name)
        
        return sorted(list(characters))
    
    def clean_character_name(self, name):
        """Clean and standardize character names."""
        # Remove extra whitespace
        name = ' '.join(name.split())
        
        # Skip if too short or contains numbers
        if len(name) < 2 or re.search(r'\d', name):
            return None
            
        # Skip common non-character words
        skip_words = ['THE', 'AND', 'OR', 'OF', 'TO', 'IN', 'ON', 'AT', 'BY', 'FOR', 'WITH']
        if name.upper() in skip_words:
            return None
            
        return name
    
    def create_dramatis_personae_entry(self, characters, play_title):
        """Create a Dramatis Personae entry structure."""
        if not characters:
            return None
            
        # Create the character list text
        character_list = []
        character_list.append(f"DRAMATIS PERSONAE")
        character_list.append(f"{play_title.upper()}")
        character_list.append("")
        
        # Group characters by type (main characters, servants, etc.)
        main_characters = []
        other_characters = []
        
        for char in characters:
            # Simple heuristic: characters with longer names or common main character patterns
            if (len(char.split()) >= 2 or 
                char in ['KING', 'QUEEN', 'PRINCE', 'DUKE', 'LORD', 'LADY'] or
                any(title in char for title in ['KING', 'QUEEN', 'PRINCE', 'DUKE'])):
                main_characters.append(char)
            else:
                other_characters.append(char)
        
        # Add main characters first
        if main_characters:
            character_list.extend(main_characters)
            if other_characters:
                character_list.append("")
        
        # Add other characters
        if other_characters:
            character_list.extend(other_characters)
        
        # Create the entry structure
        entry = {
            "1": {
                "play": "\n".join(character_list),
                "notes": []
            }
        }
        
        return entry
    
    def process_play_file(self, file_path):
        """Process a single play file and add Dramatis Personae."""
        print(f"Processing {file_path.name}...")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                play_data = json.load(f)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return False
        
        # Extract play title from filename
        play_title = file_path.stem.replace('_notes', '').replace('_cleaned_play', '').replace('_', ' ').title()
        
        # Extract characters
        characters = self.extract_characters_from_play(play_data)
        print(f"Found {len(characters)} characters: {characters[:10]}{'...' if len(characters) > 10 else ''}")
        
        if not characters:
            print(f"No characters found in {file_path.name}")
            return False
        
        # Create Dramatis Personae entry
        dramatis_entry = self.create_dramatis_personae_entry(characters, play_title)
        if not dramatis_entry:
            print(f"Could not create Dramatis Personae for {file_path.name}")
            return False
        
        # Check if Dramatis Personae already exists
        if "DRAMATIS PERSONAE" in play_data:
            print(f"Dramatis Personae already exists in {file_path.name}")
            return True
        
        # Create new structure with Dramatis Personae at the top
        new_play_data = {}
        
        # Add Dramatis Personae first
        new_play_data["DRAMATIS PERSONAE"] = dramatis_entry
        
        # Add all existing scenes
        for scene_name, scene_data in play_data.items():
            new_play_data[scene_name] = scene_data
        
        # Write back to file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(new_play_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Added Dramatis Personae to {file_path.name}")
            return True
        except Exception as e:
            print(f"Error writing {file_path}: {e}")
            return False
    
    def process_all_plays(self):
        """Process all play files in the data directory."""
        json_files = list(self.data_dir.glob("*.json"))
        
        # Filter out non-play files
        play_files = []
        for file_path in json_files:
            filename = file_path.name.lower()
            # Skip app.js and other non-play files
            if (filename.endswith('.json') and 
                'app' not in filename and 
                'bible' not in filename and
                'notes-integration' not in filename):
                play_files.append(file_path)
        
        print(f"Found {len(play_files)} play files to process")
        
        success_count = 0
        for file_path in play_files:
            if self.process_play_file(file_path):
                success_count += 1
            print()  # Add spacing between files
        
        print(f"✅ Successfully processed {success_count}/{len(play_files)} play files")
        return success_count

def main():
    """Main function to run the script."""
    print("🎭 Shakespeare Dramatis Personae Extractor")
    print("=" * 50)
    
    extractor = DramatisPersonaeExtractor()
    success_count = extractor.process_all_plays()
    
    print(f"\n🎉 Processing complete! {success_count} plays updated with Dramatis Personae.")
    print("\nNext steps:")
    print("1. Update the JavaScript navigation to include Dramatis Personae")
    print("2. Test the implementation in the web interface")

if __name__ == "__main__":
    main()
