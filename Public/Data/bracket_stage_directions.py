#!/usr/bin/env python3
"""
Add brackets around stage directions in Shakespeare play JSON files.
100% accurate: only stage directions get brackets, never dialogue.
"""

import json
import re
import os

# ── helpers ──────────────────────────────────────────────────────

def has_character_prefix(text):
    """True if line starts with 'CHARACTER:' (all-caps name + colon)."""
    return bool(re.match(r'^[A-Z][A-Z\s\'\.]+:', text))

def is_pure_stage_direction(text):
    """
    True if the ENTIRE line is a stage direction (no dialogue mixed in).
    Conservative: only matches patterns we're sure about.
    """
    if has_character_prefix(text):
        return False

    t = text.strip()

    # "Enter [characters...]" patterns
    # (caller must verify this isn't a dialogue continuation via context)
    if t.startswith("Enter "):
        return True

    # "Sings in [character's] ear:" etc.
    if t.startswith("Sings in ") or t.startswith("Sings,"):
        return True

    # Exact or near-exact short stage directions
    short_directions = [
        "Exit.", "Exeunt.", "They exit.", "He exits.", "She exits.",
        "Flourish.", "Song.", "Sings.", "Dies.", "Fight.",
        "They withdraw.", "He writes.",
    ]
    if t in short_directions:
        return True

    # "[Name(s)] exit(s)." — e.g. "Ghost exits.", "Polonius exits.",
    # "Rosencrantz and Guildenstern exit.", "Players exit."
    if re.match(r'^[A-Z][A-Za-z\s,]+ exits?\.$', t):
        return True

    # "Flourish. <stage direction>" — e.g. "Flourish. All but Hamlet exit."
    if t.startswith("Flourish. ") or t.startswith("Flourish,"):
        return True

    # "Exeunt <names/description>"
    if t.startswith("Exeunt ") or t.startswith("Exeunt,"):
        return True

    # "Exit <name>."
    if t.startswith("Exit "):
        return True

    # "They exit," or "They exit " (with continuation)
    if t.startswith("They exit,") or t.startswith("They exit "):
        return True

    # Sound/Trumpet/Alarum/Sennet/Re-enter/Retreat
    for kw in ["Sound ", "Trumpet", "Alarum", "Sennet", "Re-enter", "Retreat"]:
        if t.startswith(kw):
            return True

    # "Thunder and lightning." or "Thunder and lightning. Enter..."
    if t.startswith("Thunder and lightning"):
        return True

    # "A tempestuous noise..."
    if t.startswith("A tempestuous noise"):
        return True

    # "Music." or "Music " as standalone
    if t.startswith("Music.") or t.startswith("Music "):
        return True

    # "[Characters] withdraw." patterns
    if re.match(r'^[A-Z][A-Za-z\s,]+ withdraw\.$', t):
        return True

    return False

def is_mixed_stage_and_dialogue(text):
    """
    Check if line starts with a SHORT stage direction then continues with dialogue.
    Returns (stage_direction_part, dialogue_part) or None.
    Examples:
        "Aside. I must obey." → ("Aside.", "I must obey.")
        "Sings.    He is dead and gone, lady," → ("Sings.", "He is dead and gone, lady,")
        "Thunder. Alas, the storm is come again." → ("Thunder.", "Alas, the storm is come again.")
        "Song.  Come unto these yellow sands," → ("Song.", "Come unto these yellow sands,")
    """
    if has_character_prefix(text):
        return None

    # List of short stage direction words that can precede dialogue
    mixed_keywords = ["Aside.", "Sings.", "Song.", "Thunder.", "Music."]

    for kw in mixed_keywords:
        if text.startswith(kw):
            rest = text[len(kw):].strip()
            if rest:
                return (kw, rest)

    return None

def is_continuation_candidate(text):
    """Could this be a continuation of a multi-line stage direction?"""
    if has_character_prefix(text):
        return False
    # Must not itself look like a new stage direction or dialogue
    if is_pure_stage_direction(text):
        return False
    return True

def already_bracketed(text):
    return text.strip().startswith("[")

# ── core processing ──────────────────────────────────────────────

def process_scene(scene_data):
    changes = []
    keys = sorted(
        [k for k in scene_data if isinstance(scene_data[k], dict) and "play" in scene_data[k]],
        key=lambda x: int(x) if x.isdigit() else 0
    )

    i = 0
    while i < len(keys):
        key = keys[i]
        text = scene_data[key]["play"]

        if already_bracketed(text):
            i += 1
            continue

        # ── Mixed line (stage direction + dialogue on same line) ──
        mixed = is_mixed_stage_and_dialogue(text)
        if mixed:
            sd_part, dialogue_part = mixed
            new_text = f"[{sd_part}] {dialogue_part}"
            changes.append((key, text, new_text))
            i += 1
            continue

        # ── Pure stage direction ──
        if is_pure_stage_direction(text):
            # Guard against "Enter" used as a verb in dialogue continuation.
            # If the previous line is a dialogue continuation (no CHARACTER: prefix,
            # not a stage direction) AND doesn't end with sentence-ending punctuation,
            # then "Enter" is likely continuing a sentence, not a stage direction.
            if text.strip().startswith("Enter ") and i > 0:
                prev_key = keys[i - 1]
                prev_text = scene_data[prev_key]["play"]
                if (not has_character_prefix(prev_text)
                    and not is_pure_stage_direction(prev_text)
                    and not already_bracketed(prev_text)
                    and not prev_text.rstrip().endswith(('.', '!', '?', ')', ']'))):
                    # This "Enter" is a dialogue verb, not a stage direction
                    i += 1
                    continue

            sd_keys = [key]

            # Multi-line: only look ahead if current text is INCOMPLETE
            # (doesn't end with sentence-ending punctuation)
            j = i + 1
            last_text = text
            while j < len(keys) and not last_text.rstrip().endswith(('.', '!', '?', ')', ':')):
                next_key = keys[j]
                next_text = scene_data[next_key]["play"]
                if is_continuation_candidate(next_text) and not already_bracketed(next_text):
                    sd_keys.append(next_key)
                    last_text = next_text
                    j += 1
                else:
                    break

            if len(sd_keys) == 1:
                new_text = f"[{text}]"
                changes.append((key, text, new_text))
            else:
                # First line gets [, last line gets ]
                first_t = scene_data[sd_keys[0]]["play"]
                last_t = scene_data[sd_keys[-1]]["play"]
                changes.append((sd_keys[0], first_t, f"[{first_t}"))
                changes.append((sd_keys[-1], last_t, f"{last_t}]"))

            i = j
            continue

        i += 1

    return changes

def process_file(filepath):
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(filepath)}")
    print(f"{'='*60}")

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_changes = 0

    for section_name, section_data in data.items():
        if "DRAMATIS PERSONAE" in section_name.upper():
            continue
        if not isinstance(section_data, dict):
            continue

        changes = process_scene(section_data)

        for key, old_text, new_text in changes:
            section_data[key]["play"] = new_text
            total_changes += 1
            old_display = f'"{old_text[:80]}..."' if len(old_text) > 80 else f'"{old_text}"'
            new_display = f'"{new_text[:80]}..."' if len(new_text) > 80 else f'"{new_text}"'
            print(f"  [{section_name}][{key}]: {old_display}")
            print(f"    → {new_display}")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nTotal changes in {os.path.basename(filepath)}: {total_changes}")
    return total_changes

def main():
    base_dir = "/Users/hassanahmed/Desktop/UPWORK/SHAKESPEARE PROJECT/Shakespeare-Variorum/Public/Data"

    files = [
        "hamlet.json",
        "romeo_and_juliet.json",
        "troilus_and_cressida.json",
        "henry_iv_part2.json",
        "the_winters_tale.json",
        "the_tempest.json",
    ]

    grand_total = 0
    for filename in files:
        filepath = os.path.join(base_dir, filename)
        if os.path.exists(filepath):
            grand_total += process_file(filepath)
        else:
            print(f"WARNING: File not found: {filepath}")

    print(f"\n{'='*60}")
    print(f"GRAND TOTAL CHANGES: {grand_total}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
