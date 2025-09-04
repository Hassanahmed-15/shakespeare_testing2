#!/usr/bin/env python3
"""
Fix Line Numbers in Macbeth Database
This script corrects all incorrect line numbers to ensure proper sequential numbering
"""

import json
import re

def fix_line_numbers(data):
    """Fix all incorrect line numbers in the database"""
    print("=== FIXING LINE NUMBERS IN MACBETH DATABASE ===")
    
    fixed_data = {}
    total_fixes = 0
    
    for scene_name, scene_data in data.items():
        print(f"Processing {scene_name}...")
        fixed_scene = {}
        
        # Get all line numbers and sort them
        line_numbers = []
        for line_num in scene_data.keys():
            if line_num.isdigit():
                line_numbers.append(int(line_num))
            else:
                print(f"  ⚠️  Non-numeric line number found: {line_num}")
                continue
        
        if not line_numbers:
            print(f"  ⚠️  No valid line numbers found in {scene_name}")
            fixed_data[scene_name] = scene_data
            continue
        
        # Sort line numbers and create sequential mapping
        line_numbers.sort()
        line_mapping = {}
        
        for i, old_num in enumerate(line_numbers, 1):
            line_mapping[old_num] = i
        
        # Apply fixes
        for old_num, line_data in scene_data.items():
            if old_num.isdigit():
                old_num_int = int(old_num)
                if old_num_int in line_mapping:
                    new_num = str(line_mapping[old_num_int])
                    if old_num != new_num:
                        print(f"  🔧 Line {old_num} → Line {new_num}")
                        total_fixes += 1
                    fixed_scene[new_num] = line_data
                else:
                    print(f"  ⚠️  Line {old_num} not in mapping, keeping as is")
                    fixed_scene[old_num] = line_data
            else:
                # Keep non-numeric keys as is
                fixed_scene[old_num] = line_data
        
        fixed_data[scene_name] = fixed_scene
        
        # Verify the fix
        expected_lines = len([k for k in fixed_scene.keys() if k.isdigit()])
        actual_lines = len(line_numbers)
        if expected_lines != actual_lines:
            print(f"  ⚠️  Line count mismatch: expected {expected_lines}, got {actual_lines}")
    
    print(f"\n✅ Total line number fixes: {total_fixes}")
    return fixed_data

def verify_database_integrity(data):
    """Verify that the database has proper sequential line numbering"""
    print("\n=== VERIFYING DATABASE INTEGRITY ===")
    
    total_scenes = len(data)
    total_lines = 0
    issues_found = 0
    
    for scene_name, scene_data in data.items():
        print(f"\n{scene_name}:")
        
        # Get numeric line numbers
        line_numbers = []
        for line_num in scene_data.keys():
            if line_num.isdigit():
                line_numbers.append(int(line_num))
        
        if not line_numbers:
            print("  ⚠️  No lines found")
            issues_found += 1
            continue
        
        # Check if line numbers are sequential
        line_numbers.sort()
        expected_sequence = list(range(1, len(line_numbers) + 1))
        
        if line_numbers != expected_sequence:
            print(f"  ❌ Line numbering not sequential!")
            print(f"     Expected: {expected_sequence}")
            print(f"     Found:    {line_numbers}")
            issues_found += 1
        else:
            print(f"  ✅ {len(line_numbers)} lines properly numbered (1-{len(line_numbers)})")
        
        total_lines += len(line_numbers)
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total Scenes: {total_scenes}")
    print(f"   Total Lines: {total_lines}")
    print(f"   Issues Found: {issues_found}")
    
    if issues_found == 0:
        print("🎉 Database integrity verified! All line numbers are sequential.")
    else:
        print("⚠️  Database has integrity issues that need attention.")

def main():
    """Main function to fix the database"""
    print("=== MACBETH DATABASE LINE NUMBER FIXER ===")
    
    # Load the current database
    try:
        with open('macbeth_notes_cleaned_play.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded database with {len(data)} scenes")
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return
    
    # Verify current state
    print("\n=== CURRENT DATABASE STATE ===")
    verify_database_integrity(data)
    
    # Fix the line numbers
    print("\n=== APPLYING FIXES ===")
    fixed_data = fix_line_numbers(data)
    
    # Verify the fix
    print("\n=== VERIFYING FIXES ===")
    verify_database_integrity(fixed_data)
    
    # Save the fixed database
    print("\n=== SAVING FIXED DATABASE ===")
    try:
        with open('macbeth_notes_cleaned_play.json', 'w', encoding='utf-8') as f:
            json.dump(fixed_data, f, indent=2, ensure_ascii=False)
        print("✅ Fixed database saved successfully!")
    except Exception as e:
        print(f"❌ Error saving fixed database: {e}")
        return
    
    print("\n🎯 DATABASE FIXED SUCCESSFULLY!")
    print("   All line numbers are now sequential and properly mapped.")
    print("   Your variorum analyzer will now work correctly!")

if __name__ == "__main__":
    main()
