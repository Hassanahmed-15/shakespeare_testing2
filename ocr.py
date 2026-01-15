"""
Extract text from PDF using OCR (Tesseract) and format into JSON structure
matching the format of much_ado_about_nothing.json
"""

import sys
import os
import json
import re
import shutil
from pdf2image import convert_from_path
import pytesseract
import pdfplumber
from collections import OrderedDict

def check_tesseract_installed():
    """Check if Tesseract OCR is installed and accessible"""
    tesseract_path = shutil.which('tesseract')
    if tesseract_path:
        try:
            # Try to get version to verify it works
            version = pytesseract.get_tesseract_version()
            return True, tesseract_path, version
        except Exception as e:
            return False, None, None
    return False, None, None

def check_dependencies():
    """Check all required dependencies"""
    issues = []
    
    # Check Tesseract
    tesseract_ok, tesseract_path, version = check_tesseract_installed()
    if not tesseract_ok:
        issues.append({
            'dependency': 'Tesseract OCR',
            'status': 'NOT INSTALLED',
            'install_macos': 'brew install tesseract',
            'install_ubuntu': 'sudo apt-get install tesseract-ocr',
            'install_windows': 'Download from: https://github.com/UB-Mannheim/tesseract/wiki'
        })
    else:
        print(f"✓ Tesseract OCR found: {tesseract_path} (version: {version})")
    
    # Check poppler (for pdf2image)
    poppler_path = shutil.which('pdftoppm') or shutil.which('pdftocairo')
    if not poppler_path:
        issues.append({
            'dependency': 'Poppler (pdf2image)',
            'status': 'NOT INSTALLED',
            'install_macos': 'brew install poppler',
            'install_ubuntu': 'sudo apt-get install poppler-utils',
            'install_windows': 'Download from: https://github.com/oschwartz10612/poppler-windows/releases/'
        })
    else:
        print(f"✓ Poppler found: {poppler_path}")
    
    return issues

def extract_text_with_pdfplumber(pdf_path):
    """Try to extract text directly from PDF (for text-based PDFs)"""
    text_by_page = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_by_page.append((page_num, text))
        return text_by_page
    except Exception as e:
        print(f"Warning: Could not extract text with pdfplumber: {e}")
        return []

def extract_text_with_ocr(pdf_path, dpi=300):
    """Extract text from PDF using OCR"""
    # Check if Tesseract is installed
    tesseract_ok, tesseract_path, version = check_tesseract_installed()
    if not tesseract_ok:
        print("\n" + "=" * 60)
        print("ERROR: Tesseract OCR is not installed!")
        print("=" * 60)
        print("\nPlease install Tesseract OCR:")
        print("\n  macOS:")
        print("    brew install tesseract")
        print("\n  Ubuntu/Debian:")
        print("    sudo apt-get install tesseract-ocr")
        print("\n  Windows:")
        print("    Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("    Then add it to your PATH")
        print("\n" + "=" * 60)
        return []
    
    print(f"Converting PDF to images (DPI: {dpi})...")
    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        print(f"Converted {len(images)} pages to images")
        
        text_by_page = []
        for page_num, image in enumerate(images, 1):
            print(f"Processing page {page_num}/{len(images)}...", end='\r')
            text = pytesseract.image_to_string(image)
            if text.strip():
                text_by_page.append((page_num, text))
        
        print(f"\nExtracted text from {len(text_by_page)} pages")
        return text_by_page
    except Exception as e:
        print(f"\nError during OCR: {e}")
        if "tesseract" in str(e).lower() or "not found" in str(e).lower():
            print("\nTesseract OCR may not be properly installed or in your PATH.")
            print("Run: python ocr.py --check-deps  to verify dependencies")
        return []

def parse_play_structure(text_content):
    """
    Parse the extracted text into Act/Scene structure
    Returns a dictionary matching the JSON format
    """
    all_lines = text_content.split('\n')
    
    # Clean up lines
    cleaned_lines = []
    for line in all_lines:
        line = line.strip()
        if line:  # Only non-empty lines
            cleaned_lines.append(line)
    
    # Initialize output structure
    output = OrderedDict()
    
    # Try to detect DRAMATIS PERSONAE
    dramatis_start = None
    dramatis_end = None
    for i, line in enumerate(cleaned_lines):
        if re.match(r'^DRAMATIS\s+PERSONAE', line, re.IGNORECASE):
            dramatis_start = i
        elif dramatis_start is not None and (
            re.match(r'^ACT\s+[IVX0-9]+', line, re.IGNORECASE) or
            re.match(r'^SCENE\s+[IVX0-9]+', line, re.IGNORECASE)
        ):
            dramatis_end = i
            break
    
    # Extract DRAMATIS PERSONAE if found
    if dramatis_start is not None:
        if dramatis_end is None:
            dramatis_end = min(dramatis_start + 50, len(cleaned_lines))  # Take first 50 lines
        
        dramatis_text = '\n'.join(cleaned_lines[dramatis_start:dramatis_end])
        output["DRAMATIS PERSONAE"] = {
            "1": {
                "play": dramatis_text,
                "notes": []
            }
        }
        cleaned_lines = cleaned_lines[dramatis_end:]
    
    # Helper function to fix common OCR errors in Roman numerals
    def fix_ocr_roman_errors(num_str):
        """Fix common OCR errors that misread Roman numerals"""
        num_str = num_str.strip()
        
        # Common OCR errors for Roman numerals:
        # "111" is often "iii" (3) - but could also be "11" + "1" or actual 111
        # "11" could be "ii" (2) or actual 11
        # "1v" or "lv" could be "iv" (4)
        # "1x" or "lx" could be "ix" (9)
        
        # If it's all digits and looks like a misread Roman numeral
        if num_str.isdigit():
            # Check if it's a common misread pattern
            if num_str == "111":  # Very likely "iii" (3) in scene numbers
                return "iii"
            elif num_str == "11":  # Could be "ii" (2) but less certain
                # Keep as is for now, but we'll validate later
                return num_str
            elif len(num_str) == 1:
                return num_str  # Single digit, probably correct
        
        # Fix common character misreads
        num_str = num_str.replace('1', 'I').replace('0', 'O')  # But be careful with this
        # Actually, let's be more specific
        num_str = re.sub(r'1+', lambda m: 'I' * len(m.group()), num_str)  # Replace sequences of 1s with Is
        
        return num_str.upper()
    
    # Helper function to convert Roman numerals to Arabic
    def roman_to_arabic(roman):
        """Convert Roman numeral to Arabic number"""
        roman_map = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
        roman = roman.upper().strip()
        
        # If it's already a digit, return it
        if roman.isdigit():
            # But check for common OCR errors first
            if roman == "111" and len(roman) == 3:  # Likely "iii" misread
                return 3
            elif roman == "11" and len(roman) == 2:  # Could be "ii" but less certain
                return 2  # Assume it's "ii" for scene numbers (usually small)
            return int(roman)
        
        # Clean up common OCR errors
        roman = roman.replace('1', 'I').replace('0', 'O')
        
        result = 0
        prev_value = 0
        for char in reversed(roman):
            value = roman_map.get(char, 0)
            if value == 0:
                # Invalid character, try to continue
                continue
            if value < prev_value:
                result -= value
            else:
                result += value
            prev_value = value
        
        return result if result > 0 else None
    
    # Helper function to normalize act/scene numbers
    def normalize_number(num_str):
        """Convert Roman numeral or number string to standard format"""
        num_str = num_str.strip()
        
        # If it's a pure digit string
        if num_str.isdigit():
            # Check for common OCR misreads
            if num_str == "111":  # Almost certainly "iii" (3) misread
                return "3"
            elif num_str == "11":  # Could be "ii" (2) - but validate context
                return "2"  # Assume "ii" for scene numbers
            elif int(num_str) > 20:  # Scene numbers rarely > 20, probably OCR error
                # Try to interpret as Roman numeral
                fixed = fix_ocr_roman_errors(num_str)
                try:
                    arabic = roman_to_arabic(fixed)
                    if arabic and arabic <= 20:
                        return str(arabic)
                except:
                    pass
            return num_str
        
        # Try to convert Roman numeral
        try:
            arabic = roman_to_arabic(num_str)
            if arabic:
                return str(arabic)
        except:
            pass
        
        # Last resort: try fixing OCR errors
        fixed = fix_ocr_roman_errors(num_str)
        try:
            arabic = roman_to_arabic(fixed)
            if arabic:
                return str(arabic)
        except:
            pass
        
        return num_str
    
    # Parse Acts and Scenes
    current_act = None
    current_scene = None
    current_scene_lines = []
    scene_key = None
    
    for line in cleaned_lines:
        # Check for Latin format: [Actus Primus. Scæna Prima.] or [Actus Secundus. Scæna Secunda.]
        latin_act_scene = re.search(r'\[Actus\s+(\w+)\.\s+Sc[æa]na\s+(\w+)\]', line, re.IGNORECASE)
        if latin_act_scene:
            # Save previous scene if exists
            if scene_key and current_scene_lines:
                output[scene_key] = OrderedDict()
                for idx, scene_line in enumerate(current_scene_lines, start=1):
                    output[scene_key][str(idx)] = {
                        "play": scene_line
                    }
                current_scene_lines = []
            
            # Convert Latin ordinals to numbers
            latin_ordinals = {
                'primus': '1', 'prima': '1',
                'secundus': '2', 'secunda': '2',
                'tertius': '3', 'tertia': '3',
                'quartus': '4', 'quarta': '4',
                'quintus': '5', 'quinta': '5'
            }
            act_latin = latin_act_scene.group(1).lower()
            scene_latin = latin_act_scene.group(2).lower()
            current_act = latin_ordinals.get(act_latin, '1')
            current_scene = latin_ordinals.get(scene_latin, '1')
            scene_key = f"ACT {current_act} SCENE {current_scene}"
            continue
        
        # Check for Act header (various formats)
        act_match = re.search(r'ACT\s+([IVX0-9]+)', line, re.IGNORECASE)
        if act_match and not re.search(r'SCENE|SC\.', line, re.IGNORECASE):
            # Save previous scene if exists
            if scene_key and current_scene_lines:
                output[scene_key] = OrderedDict()
                for idx, scene_line in enumerate(current_scene_lines, start=1):
                    output[scene_key][str(idx)] = {
                        "play": scene_line
                    }
                current_scene_lines = []
            
            current_act = normalize_number(act_match.group(1))
            current_scene = None
            scene_key = None
            continue
        
        # Check for Scene header (various formats)
        scene_match = re.search(r'SCENE\s+([IVX0-9]+)', line, re.IGNORECASE)
        if scene_match:
            # Save previous scene if exists
            if scene_key and current_scene_lines:
                output[scene_key] = OrderedDict()
                for idx, scene_line in enumerate(current_scene_lines, start=1):
                    output[scene_key][str(idx)] = {
                        "play": scene_line
                    }
                current_scene_lines = []
            
            current_scene = normalize_number(scene_match.group(1))
            if current_act:
                scene_key = f"ACT {current_act} SCENE {current_scene}"
            else:
                scene_key = f"SCENE {current_scene}"
            continue
        
        # Check for combined ACT X SCENE Y format (various patterns)
        # Pattern: "ACT I, SC. i]", "ACT I, SC. i.]", "ACT I, SC i]", "ACT I SCENE 1"
        combined_patterns = [
            r'ACT\s+([IVX0-9]+)[,\s]+SC\.?\s*([IVX0-9]+)',
            r'ACT\s+([IVX0-9]+)\s+SCENE\s+([IVX0-9]+)',
            r'\[ACT\s+([IVX0-9]+)[,\s]+SC\.?\s*([IVX0-9]+)\]',
        ]
        
        for pattern in combined_patterns:
            combined_match = re.search(pattern, line, re.IGNORECASE)
            if combined_match:
                # Save previous scene if exists
                if scene_key and current_scene_lines:
                    output[scene_key] = OrderedDict()
                    for idx, scene_line in enumerate(current_scene_lines, start=1):
                        output[scene_key][str(idx)] = {
                            "play": scene_line
                        }
                    current_scene_lines = []
                
                current_act = normalize_number(combined_match.group(1))
                current_scene = normalize_number(combined_match.group(2))
                scene_key = f"ACT {current_act} SCENE {current_scene}"
                break
        
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in combined_patterns):
            continue
        
        # If we're in a scene, add line to current scene
        if current_act and current_scene:
            # Clean up line
            line = line.strip()
            # Skip empty lines, dashes/spaces, and standalone line numbers
            if (line and 
                not re.match(r'^[-\s]+$', line) and  # Not just dashes/spaces
                not re.match(r'^\d+$', line) and  # Not standalone numbers (line numbers)
                not re.match(r'^THE HISTORIE OF|^HENRY THE FOURTH', line, re.IGNORECASE) and  # Skip headers
                not re.match(r'^\[ACT\s+[IVX0-9]+', line, re.IGNORECASE)):  # Skip repeated act headers
                current_scene_lines.append(line)
        elif scene_key:  # Scene without act number
            line = line.strip()
            if (line and 
                not re.match(r'^[-\s]+$', line) and
                not re.match(r'^\d+$', line) and
                not re.match(r'^THE HISTORIE OF|^HENRY THE FOURTH', line, re.IGNORECASE) and
                not re.match(r'^\[ACT\s+[IVX0-9]+', line, re.IGNORECASE)):
                current_scene_lines.append(line)
    
    # Save last scene
    if scene_key and current_scene_lines:
        output[scene_key] = OrderedDict()
        for idx, scene_line in enumerate(current_scene_lines, start=1):
            output[scene_key][str(idx)] = {
                "play": scene_line
            }
    
    # Post-process: Fix scene numbers that are clearly OCR errors
    # Common issues: "111" should be "3" (iii), "9" might be "3" (iii), etc.
    fixed_output = OrderedDict()
    act_scenes_map = {}  # Track (act, scene) -> original_key mapping
    
    # First pass: collect all scenes and fix obvious errors
    for key, value in output.items():
        if key == "DRAMATIS PERSONAE":
            fixed_output[key] = value
            continue
        
        # Parse act and scene from key
        act_scene_match = re.match(r'ACT\s+(\d+)\s+SCENE\s+(\d+)', key)
        if act_scene_match:
            act_num = int(act_scene_match.group(1))
            scene_num = int(act_scene_match.group(2))
            
            # Fix obvious OCR errors
            if scene_num == 111:  # Almost certainly "iii" (3) misread
                scene_num = 3
            elif scene_num == 11:  # Could be "ii" (2) misread
                scene_num = 2
            elif scene_num == 9 and act_num == 1:  # "9" in Act 1 is suspicious, likely "3" (iii)
                # Check context - if we have scene 2 and scene 3 already, this might be wrong
                scene_num = 3  # Assume it's scene 3
            elif scene_num > 20:  # Scene numbers rarely exceed 20 in Shakespeare
                # Try common misreads
                if scene_num == 111:
                    scene_num = 3
                elif scene_num == 11:
                    scene_num = 2
                # For other large numbers, try to guess or keep as is
            
            # Track scenes per act
            if act_num not in act_scenes_map:
                act_scenes_map[act_num] = {}
            act_scenes_map[act_num][scene_num] = (key, value)
        else:
            fixed_output[key] = value
    
    # Second pass: ensure sequential scene numbering within each act
    final_output = OrderedDict()
    if "DRAMATIS PERSONAE" in fixed_output:
        final_output["DRAMATIS PERSONAE"] = fixed_output["DRAMATIS PERSONAE"]
    
    # Process each act
    for act_num in sorted(act_scenes_map.keys()):
        scenes = act_scenes_map[act_num]
        scene_nums = sorted(scenes.keys())
        
        # If scenes are not sequential, try to fix
        expected_scene = 1
        for scene_num in scene_nums:
            # If scene number is way off, assume it should be the next expected
            if scene_num > expected_scene + 2:  # More than 2 off
                # This is likely an OCR error, use expected number
                corrected_scene = expected_scene
            else:
                corrected_scene = scene_num
                expected_scene = max(expected_scene, scene_num + 1)
            
            original_key, value = scenes[scene_num]
            new_key = f"ACT {act_num} SCENE {corrected_scene}"
            final_output[new_key] = value
    
    return final_output

def merge_character_lines(scene_data):
    """
    Merge consecutive lines from the same character
    This handles cases where dialogue is split across multiple lines
    """
    if not scene_data:
        return scene_data
    
    merged_data = OrderedDict()
    line_idx = 1
    
    i = 0
    while i < len(scene_data):
        current_line = scene_data[i]["play"]
        
        # Check if it's a character name followed by dialogue
        if ':' in current_line:
            parts = current_line.split(':', 1)
            character = parts[0].strip()
            dialogue = parts[1].strip() if len(parts) > 1 else ""
            
            # Look ahead for continuation lines (same character or no colon)
            merged_dialogue = [dialogue] if dialogue else []
            j = i + 1
            
            while j < len(scene_data):
                next_line = scene_data[j]["play"]
                
                # Stop if we hit a stage direction or new character
                if (next_line.startswith('Enter') or 
                    next_line.startswith('Exit') or 
                    next_line.startswith('Exeunt') or
                    (':' in next_line and not next_line.startswith(character + ':'))):
                    break
                
                # Continue if it's the same character or no character indicator
                if ':' in next_line:
                    next_parts = next_line.split(':', 1)
                    if next_parts[0].strip() == character:
                        merged_dialogue.append(next_parts[1].strip() if len(next_parts) > 1 else "")
                        j += 1
                    else:
                        break
                else:
                    # Continuation line (no character name)
                    merged_dialogue.append(next_line)
                    j += 1
            
            # Combine dialogue
            if merged_dialogue:
                final_dialogue = ' '.join([d for d in merged_dialogue if d])
                if final_dialogue:
                    merged_data[str(line_idx)] = {
                        "play": f"{character}: {final_dialogue}"
                    }
                    line_idx += 1
            else:
                merged_data[str(line_idx)] = {"play": current_line}
                line_idx += 1
            
            i = j
        else:
            # Stage direction or other line
            merged_data[str(line_idx)] = {"play": current_line}
            line_idx += 1
            i += 1
    
    return merged_data

def extract_and_parse_pdf(pdf_path, use_ocr=True, dpi=300):
    """Main extraction function"""
    print(f"Extracting text from: {pdf_path}")
    print("=" * 60)
    
    # Try direct text extraction first
    text_by_page = extract_text_with_pdfplumber(pdf_path)
    
    # If no text extracted or very little, use OCR
    total_text = ''.join([text for _, text in text_by_page])
    if len(total_text.strip()) < 100 or use_ocr:
        print("\nUsing OCR for text extraction...")
        text_by_page = extract_text_with_ocr(pdf_path, dpi=dpi)
    
    if not text_by_page:
        print("Error: No text extracted from PDF!")
        return None
    
    # Combine all pages
    full_text = '\n'.join([text for _, text in text_by_page])
    
    print("\nParsing play structure...")
    parsed_data = parse_play_structure(full_text)
    
    print(f"\nExtracted {len(parsed_data)} sections:")
    for key in parsed_data.keys():
        if key != "DRAMATIS PERSONAE":
            line_count = len(parsed_data[key])
            print(f"  {key}: {line_count} lines")
    
    return parsed_data

def main():
    # Check for dependency check flag
    if '--check-deps' in sys.argv or '--check-dependencies' in sys.argv:
        print("Checking dependencies...")
        print("=" * 60)
        issues = check_dependencies()
        if issues:
            print("\n" + "=" * 60)
            print("MISSING DEPENDENCIES:")
            print("=" * 60)
            for issue in issues:
                print(f"\n{issue['dependency']}: {issue['status']}")
                print(f"  macOS:   {issue['install_macos']}")
                print(f"  Ubuntu:  {issue['install_ubuntu']}")
                print(f"  Windows: {issue['install_windows']}")
            sys.exit(1)
        else:
            print("\n✓ All dependencies are installed!")
            sys.exit(0)
    
    if len(sys.argv) < 2:
        print("Usage: python ocr.py <pdf_file> [output_json] [--dpi=300]")
        print("       python ocr.py --check-deps  (check dependencies)")
        print("\nExample:")
        print("  python ocr.py henry1.pdf")
        print("  python ocr.py henry1.pdf henry1.json")
        print("  python ocr.py henry1.pdf henry1.json --dpi=400")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # Determine output file
    if len(sys.argv) >= 3 and not sys.argv[2].startswith('--'):
        output_file = sys.argv[2]
    else:
        # Generate output filename from PDF name
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_file = f"Public/Data/{base_name.lower()}.json"
    
    # Check for DPI argument
    dpi = 300
    for arg in sys.argv:
        if arg.startswith('--dpi='):
            dpi = int(arg.split('=')[1])
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found!")
        sys.exit(1)
    
    # Extract and parse
    result = extract_and_parse_pdf(pdf_path, use_ocr=True, dpi=dpi)
    
    if result:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to JSON file
        print(f"\nWriting output to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print("SUCCESS!")
        print("=" * 60)
        print(f"Output saved to: {output_file}")
        
        # Count total lines
        total_lines = sum(len(scene) for scene in result.values() if isinstance(scene, dict))
        print(f"Total lines extracted: {total_lines}")
    else:
        print("\nError: Failed to extract text from PDF")
        sys.exit(1)

if __name__ == "__main__":
    main()
