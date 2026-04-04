import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
from typing import Dict, List, Tuple, Optional

# Configuration: Play URL path to (Play Name, JSON filename) mapping
PLAYS_CONFIG = {
    "allswell": ("All's Well That Ends Well", "alls_well_that_ends_well"),
    "asyoulikeit": ("As You Like It", "as_you_like_it"),
    "comedy_errors": ("The Comedy of Errors", "comedy_of_errors"),
    "cymbeline": ("Cymbeline", "cymbeline"),
    "lll": ("Love's Labour's Lost", "loves_labours_lost"),
    "measure": ("Measure for Measure", "measure_for_measure"),
    "merry_wives": ("The Merry Wives of Windsor", "merry_wives_of_windsor"),
    "merchant": ("The Merchant of Venice", "merchant_of_venice"),
    "midsummer": ("A Midsummer Night's Dream", "midsummer_nights_dream"),
    "much_ado": ("Much Ado About Nothing", "much_ado_about_nothing"),
    "pericles": ("Pericles, Prince of Tyre", "pericles"),
    "taming_shrew": ("The Taming of the Shrew", "taming_of_the_shrew"),
    "tempest": ("The Tempest", "the_tempest"),
    "troilus_cressida": ("Troilus and Cressida", "troilus_and_cressida"),
    "twelfth_night": ("Twelfth Night", "twelfth_night"),
    "two_gentlemen": ("Two Gentlemen of Verona", "two_gentlemen_of_verona"),
    "winters_tale": ("The Winter's Tale", "the_winters_tale"),
    "1henryiv": ("Henry IV, Part 1", "henry_iv_part1"),
    "2henryiv": ("Henry IV, Part 2", "henry_iv_part2"),
    "henryv": ("Henry V", "henry_v"),
    "1henryvi": ("Henry VI, Part 1", "henry_vi_part1"),
    "2henryvi": ("Henry VI, Part 2", "henry_vi_part2"),
    "3henryvi": ("Henry VI, Part 3", "henry_vi_part3"),
    "henryviii": ("Henry VIII", "henry_viii"),
    "john": ("King John", "king_john"),
    "richardii": ("Richard II", "richard_ii"),
    "richardiii": ("Richard III", "richard_iii"),
    "cleopatra": ("Antony and Cleopatra", "antony_and_cleopatra"),
    "coriolanus": ("Coriolanus", "Coriolanus"),
    "hamlet": ("Hamlet", "hamlet"),
    "julius_caesar": ("Julius Caesar", "julius_caesar"),
    "lear": ("King Lear", "king_lear"),
    "macbeth": ("Macbeth", "macbeth"),
    "othello": ("Othello", "othello"),
    "romeo_juliet": ("Romeo and Juliet", "romeo_and_juliet"),
    "timon": ("Timon of Athens", "timon_of_athens"),
    "titus": ("Titus Andronicus", "titus_andronicus"),
}

def discover_scene_structure(play_path: str) -> Dict[int, List[int]]:
    """Auto-discover the scene structure by parsing the index page"""
    print(f"  Discovering scene structure for {play_path}...")
    scenes_structure = {}
    
    try:
        # Try to get scene structure from the index page
        url = f"https://shakespeare.mit.edu/{play_path}/index.html"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all links that match the pattern play.act.scene.html
        pattern = re.compile(rf"^{re.escape(play_path)}\.(\d+)\.(\d+)\.html$")
        
        found_scenes = set()
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            match = pattern.search(href)
            if match:
                act = int(match.group(1))
                scene = int(match.group(2))
                found_scenes.add((act, scene))
        
        # Organize by act
        for act, scene in sorted(found_scenes):
            if act not in scenes_structure:
                scenes_structure[act] = []
            if scene not in scenes_structure[act]:
                scenes_structure[act].append(scene)
        
        # Sort scenes within each act
        for act in scenes_structure:
            scenes_structure[act].sort()
        
    except Exception as e:
        print(f"    Warning: Could not parse index page, trying fallback method: {e}")
        # Fallback: try to check scenes directly (slower)
        for act in range(1, 6):
            scenes_in_act = []
            for scene in range(1, 11):
                url = f"https://shakespeare.mit.edu/{play_path}/{play_path}.{act}.{scene}.html"
                try:
                    response = requests.head(url, timeout=5, allow_redirects=False)
                    if response.status_code == 200:
                        scenes_in_act.append(scene)
                    else:
                        break  # No more scenes in this act
                except:
                    break
            
            if scenes_in_act:
                scenes_structure[act] = scenes_in_act
            else:
                break
    
    return scenes_structure


def mit_speaker_tag_ok(char_name: str) -> bool:
    """MIT pages use ALL CAPS names; prologues sometimes use 'Chorus' in title case."""
    if not char_name:
        return False
    if char_name.isupper():
        return True
    return char_name.lower() in ("chorus",)


def extract_prologue_numbered_lines_only(body) -> List[str]:
    """
    Prologue pages with no <a name=speechN> header: a single blockquote of
    <A NAME=1>line</A> ... (e.g. Romeo and Juliet Act 1 Prologue on MIT).
    """
    out: List[str] = []
    for blockquote in body.find_all("blockquote"):
        numbered: List[Tuple[int, str]] = []
        for a in blockquote.find_all("a"):
            nm = a.get("name")
            if nm is None:
                continue
            s = str(nm).strip()
            if s.isdigit():
                t = a.get_text(strip=True)
                if t:
                    numbered.append((int(s), t))
        if not numbered:
            continue
        numbered.sort(key=lambda x: x[0])
        texts = [t for _, t in numbered]
        out.append(f"CHORUS: {texts[0]}")
        out.extend(texts[1:])
    return out


def extract_text_from_scene(play_path: str, act: int, scene: int) -> List[str]:
    """Extract text from a specific act and scene"""
    url = f"https://shakespeare.mit.edu/{play_path}/{play_path}.{act}.{scene}.html"
    print(f"    Fetching Act {act}, Scene {scene}...")
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        lines = []
        
        body = soup.find('body')
        if not body:
            print(f"    Warning: Could not find body for Act {act}, Scene {scene}")
            return lines
        
        # Process elements in document order
        # Character names are in <a name="speechX"><b>CHARACTER</b></a>
        # Dialogue is in <blockquote> following character, with <a name="N">dialogue</a> tags
        # Stage directions are in <blockquote><i>direction</i></blockquote>
        
        # Collect all elements with their positions
        elements_with_pos = []
        
        # Find all speech links
        all_speech_links = body.find_all('a', {'name': re.compile(r'^speech')})
        for speech_link in all_speech_links:
            bold = speech_link.find('b')
            if bold:
                char_name = bold.get_text(strip=True)
                if char_name and mit_speaker_tag_ok(char_name):
                    # Find the following blockquote
                    next_elem = speech_link.next_sibling
                    found_blockquote = None
                    
                    while next_elem:
                        if hasattr(next_elem, 'name'):
                            if next_elem.name == 'blockquote':
                                found_blockquote = next_elem
                                break
                            elif next_elem.name == 'a' and next_elem.get('name', '').startswith('speech'):
                                break
                        next_elem = getattr(next_elem, 'next_sibling', None)
                    
                    if not found_blockquote and speech_link.parent:
                        next_parent_sib = speech_link.parent.next_sibling
                        while next_parent_sib:
                            if hasattr(next_parent_sib, 'name') and next_parent_sib.name == 'blockquote':
                                found_blockquote = next_parent_sib
                                break
                            next_parent_sib = getattr(next_parent_sib, 'next_sibling', None)
                    
                    if found_blockquote:
                        dialogue_lines = []
                        for dialogue_a in found_blockquote.find_all('a'):
                            dialogue_text = dialogue_a.get_text(strip=True)
                            if dialogue_text and not dialogue_a.get('name', '').startswith('speech'):
                                dialogue_lines.append(dialogue_text)
                        
                        if dialogue_lines:
                            display_name = (
                                char_name.upper()
                                if char_name.lower() == "chorus"
                                else char_name
                            )
                            # Store with speech link position
                            elements_with_pos.append(
                                ("speech", speech_link.sourceline or 0, display_name, dialogue_lines, found_blockquote)
                            )
        
        # Find all stage direction blockquotes
        all_blockquotes = body.find_all('blockquote')
        processed_blockquotes = {elem[4] for elem in elements_with_pos if len(elem) > 4}
        
        for blockquote in all_blockquotes:
            if blockquote not in processed_blockquotes:
                italic = blockquote.find('i')
                if italic:
                    stage_dir = italic.get_text(strip=True)
                    if stage_dir and re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums)', stage_dir, re.IGNORECASE):
                        elements_with_pos.append(('stage', blockquote.sourceline or 0, stage_dir, None, blockquote))
        
        # Sort by position in document
        elements_with_pos.sort(key=lambda x: x[1])
        
        # Build lines list
        all_lines = []
        for elem_type, pos, content, dialogue_lines, blockquote in elements_with_pos:
            if elem_type == 'speech':
                for dialogue in dialogue_lines:
                    all_lines.append(f"{content}: {dialogue}")
            elif elem_type == 'stage':
                all_lines.append(content)

        if not all_lines:
            all_lines = extract_prologue_numbered_lines_only(body)
        
        # Group consecutive lines from the same speaker
        grouped_lines = []
        current_speaker = None
        
        for line in all_lines:
            if not line or not line.strip():
                continue
                
            # Check if it's a stage direction
            if re.match(r'^(Enter|Exit|Exeunt|Re-enter|Flourish|Alarum|Aside|Alarums)', line, re.IGNORECASE):
                grouped_lines.append(line)
                current_speaker = None
            elif ':' in line:
                # It's a character line
                parts = line.split(':', 1)
                if len(parts) == 2:
                    speaker = parts[0].strip()
                    dialogue = parts[1].strip()
                    
                    if speaker == current_speaker:
                        # Same speaker, just add dialogue without name
                        grouped_lines.append(dialogue)
                    else:
                        # New speaker
                        grouped_lines.append(line)
                        current_speaker = speaker
                else:
                    grouped_lines.append(line)
                    current_speaker = None
            else:
                # Regular line
                grouped_lines.append(line)
                current_speaker = None
        
        return grouped_lines
    
    except Exception as e:
        print(f"    Error fetching Act {act}, Scene {scene}: {e}")
        return []

def extract_dramatis_personae(play_path: str, json_filename: str) -> Optional[Dict]:
    """Extract or create DRAMATIS PERSONAE section"""
    # Try to read from existing file first
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "Public", "Data", f"{json_filename}.json")
    
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if "DRAMATIS PERSONAE" in existing_data:
                    return existing_data["DRAMATIS PERSONAE"]
        except:
            pass
    
    # If not found, create a placeholder
    play_name = PLAYS_CONFIG.get(play_path, (play_path.replace('_', ' ').title(), json_filename))[0]
    return {
        "1": {
            "play": f"DRAMATIS PERSONAE\n{play_name.upper()}",
            "notes": []
        }
    }

def extract_play(play_path: str, play_name: str) -> Dict:
    """Extract all scenes from a play"""
    print(f"\n{'='*70}")
    print(f"Extracting: {play_name}")
    print(f"{'='*70}")
    
    # Discover scene structure
    scenes_structure = discover_scene_structure(play_path)
    
    if not scenes_structure:
        print(f"  Warning: Could not discover scene structure for {play_path}")
        return {}
    
    print(f"  Found structure: {scenes_structure}")
    
    all_scenes = {}
    
    # Extract all scenes
    for act in sorted(scenes_structure.keys()):
        for scene in scenes_structure[act]:
            scene_key = f"ACT {act} SCENE {scene}"
            lines = extract_text_from_scene(play_path, act, scene)
            
            if lines:
                all_scenes[scene_key] = {}
                for idx, line in enumerate(lines, start=1):
                    all_scenes[scene_key][str(idx)] = {
                        "play": line
                    }
                print(f"    Extracted {len(lines)} lines from {scene_key}")
            else:
                print(f"    Warning: No lines extracted from {scene_key}")
            
            # Be polite to the server
            time.sleep(0.5)
    
    return all_scenes

def save_play_json(json_filename: str, all_scenes: Dict, dramatis_personae: Dict):
    """Save play data to JSON file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(script_dir, "Public", "Data", f"{json_filename}.json")
    
    # Combine DRAMATIS PERSONAE and scenes
    output_data = {
        "DRAMATIS PERSONAE": dramatis_personae
    }
    output_data.update(all_scenes)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n  Saved to: {output_file}")
    print(f"  Total scenes: {len(all_scenes)}")
    total_lines = sum(len(scene_data) for scene_data in all_scenes.values())
    print(f"  Total lines: {total_lines}")

def main(batch_number=None, plays_to_extract=None):
    """Extract plays from the MIT Shakespeare website
    
    Args:
        batch_number: Optional batch number (1, 2, or 3) - extracts a subset of plays
        plays_to_extract: Optional list of play paths to extract (overrides batch_number)
    """
    if plays_to_extract is None and batch_number is not None:
        # Divide plays into 3 batches
        all_plays = list(PLAYS_CONFIG.items())
        total = len(all_plays)
        batch_size = total // 3
        
        if batch_number == 1:
            plays_to_extract = [p[0] for p in all_plays[:batch_size + 1]]
            batch_info = f"Batch 1 (plays 1-{len(plays_to_extract)})"
        elif batch_number == 2:
            plays_to_extract = [p[0] for p in all_plays[batch_size + 1:2 * batch_size + 1]]
            batch_info = f"Batch 2 (plays {batch_size + 2}-{batch_size + 1 + len(plays_to_extract)})"
        elif batch_number == 3:
            plays_to_extract = [p[0] for p in all_plays[2 * batch_size + 1:]]
            batch_info = f"Batch 3 (plays {2 * batch_size + 2}-{total})"
        else:
            print(f"Invalid batch number: {batch_number}. Must be 1, 2, or 3.")
            return
    elif plays_to_extract is None:
        plays_to_extract = list(PLAYS_CONFIG.keys())
        batch_info = "All Plays"
    else:
        batch_info = f"Selected Plays ({len(plays_to_extract)})"
    
    print("="*70)
    print(f"Shakespeare Play Extractor - {batch_info}")
    print("="*70)
    print(f"\nExtracting {len(plays_to_extract)} plays from shakespeare.mit.edu")
    print("\nThis may take a while... Please be patient.")
    print("\nStarting extraction...\n")
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "Public", "Data")
    os.makedirs(data_dir, exist_ok=True)
    
    success_count = 0
    failed_plays = []
    
    for play_path in plays_to_extract:
        if play_path not in PLAYS_CONFIG:
            print(f"  Warning: Unknown play path '{play_path}', skipping...")
            continue
            
        play_name, json_filename = PLAYS_CONFIG[play_path]
        try:
            # Extract DRAMATIS PERSONAE
            dramatis_personae = extract_dramatis_personae(play_path, json_filename)
            
            # Extract all scenes
            all_scenes = extract_play(play_path, play_name)
            
            if all_scenes:
                # Save to JSON file
                save_play_json(json_filename, all_scenes, dramatis_personae)
                success_count += 1
            else:
                print(f"  Failed to extract any scenes for {play_name}")
                failed_plays.append(play_name)
            
            # Longer pause between plays to be polite
            print(f"\n  Waiting 2 seconds before next play...")
            time.sleep(2)
            
        except Exception as e:
            print(f"\n  ERROR extracting {play_name}: {e}")
            import traceback
            traceback.print_exc()
            failed_plays.append(play_name)
            time.sleep(2)
    
    # Print summary
    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)
    print(f"Successfully extracted: {success_count}/{len(plays_to_extract)} plays")
    
    if failed_plays:
        print(f"\nFailed plays ({len(failed_plays)}):")
        for play in failed_plays:
            print(f"  - {play}")
    
    print("\nAll JSON files saved to: Public/Data/")
    print("="*70)

if __name__ == "__main__":
    import sys
    batch_num = None
    if len(sys.argv) > 1:
        try:
            batch_num = int(sys.argv[1])
        except ValueError:
            print(f"Invalid batch number: {sys.argv[1]}. Must be 1, 2, or 3.")
            sys.exit(1)
    main(batch_number=batch_num)

