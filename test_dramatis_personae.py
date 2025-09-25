#!/usr/bin/env python3
"""
Test script to verify that Dramatis Personae was added correctly to the plays.
"""

import json
import os
from pathlib import Path

def test_dramatis_personae():
    """Test that Dramatis Personae was added to all play files."""
    data_dir = Path("Public/Data")
    json_files = list(data_dir.glob("*.json"))
    
    # Filter out non-play files
    play_files = []
    for file_path in json_files:
        filename = file_path.name.lower()
        if (filename.endswith('.json') and 
            'app' not in filename and 
            'bible' not in filename and
            'notes-integration' not in filename):
            play_files.append(file_path)
    
    print(f"🎭 Testing Dramatis Personae in {len(play_files)} play files")
    print("=" * 60)
    
    success_count = 0
    total_plays = len(play_files)
    
    for file_path in play_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                play_data = json.load(f)
            
            if "DRAMATIS PERSONAE" in play_data:
                dramatis_data = play_data["DRAMATIS PERSONAE"]
                if isinstance(dramatis_data, dict) and "1" in dramatis_data:
                    character_text = dramatis_data["1"]["play"]
                    lines = character_text.split('\n')
                    
                    # Count non-empty lines
                    character_count = len([line for line in lines if line.strip()])
                    
                    print(f"✅ {file_path.name:30} - {character_count:2} characters found")
                    success_count += 1
                else:
                    print(f"❌ {file_path.name:30} - Invalid Dramatis Personae structure")
            else:
                print(f"❌ {file_path.name:30} - No Dramatis Personae found")
                
        except Exception as e:
            print(f"❌ {file_path.name:30} - Error: {e}")
    
    print("=" * 60)
    print(f"📊 Results: {success_count}/{total_plays} plays have Dramatis Personae")
    
    if success_count == total_plays:
        print("🎉 All plays successfully updated with Dramatis Personae!")
        return True
    else:
        print(f"⚠️  {total_plays - success_count} plays still need Dramatis Personae")
        return False

def show_sample_dramatis_personae():
    """Show a sample of Dramatis Personae from one play."""
    data_dir = Path("Public/Data")
    sample_file = data_dir / "as_you_like_it.json"
    
    if sample_file.exists():
        with open(sample_file, 'r', encoding='utf-8') as f:
            play_data = json.load(f)
        
        if "DRAMATIS PERSONAE" in play_data:
            print("\n📖 Sample Dramatis Personae from As You Like It:")
            print("-" * 50)
            character_text = play_data["DRAMATIS PERSONAE"]["1"]["play"]
            print(character_text)
            print("-" * 50)

if __name__ == "__main__":
    success = test_dramatis_personae()
    show_sample_dramatis_personae()
    
    if success:
        print("\n🚀 Ready to test in the web interface!")
        print("1. Open index.html in a web browser")
        print("2. Select a play from the dropdown")
        print("3. Look for 'Dramatis Personae' in the left navigation")
        print("4. Click on it to view the character list")
    else:
        print("\n🔧 Some issues found - check the errors above")
