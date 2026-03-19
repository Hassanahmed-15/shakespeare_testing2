# Prompt: Correct Scholarly Commentary Line Numbers

## Task
Match scholarly commentary line-number references to the actual line numbers in the play text by finding where each quoted/annotated phrase appears exactly in the play.

## Instructions
You will receive:
1. **Play text** – A scene with numbered lines (1. 2. 3. …) in format like:
   ```
   1. FIRST WITCH: When shall we three meet again
   2. In thunder, lightning, or in rain?
   3. SECOND WITCH: When the hurly-burly's done,
   ...
   ```

2. **Scholarly commentary** – Notes referencing line numbers and often quoting phrases, e.g.:
   ```
   5. WARBURTON: The phrase "hurly-burly" refers to...
   10. JOHNSON: "fair is foul" – this inversion...
   ```

**Your job:** For each scholarly commentary entry, identify the phrase or line being discussed. Search the play text for that **exact phrase**. Replace the commentary’s line number with the play-text line number where that phrase actually appears. Leave all other text unchanged.

## Rules
- Preserve all commentary text exactly; only change the line number.
- Match by exact phrase. If the commentary quotes part of a line, find that exact substring in the play text.
- If the phrase appears more than once, use the first occurrence in that scene.
- If no match is found, keep the original line number but add a flag: `[unverified]`.
- Speaker names and stage directions in `[brackets]` are part of the play text; include them when matching.
- Ignore minor punctuation differences (e.g., smart quotes vs straight quotes) when matching.
- Line numbers in the play text restart per scene; match within the correct scene only.

## Output Format
Return the scholarly commentary **exactly as given**, with only the line numbers corrected. No extra explanation unless you flag an entry as `[unverified]`.

## Example

**Play text (excerpt):**
```
1. FIRST WITCH: When shall we three meet again
2. In thunder, lightning, or in rain?
3. SECOND WITCH: When the hurly-burly's done,
4. When the battle's lost and won.
5. THIRD WITCH: That will be ere the set of sun.
...
11. ALL: Fair is foul, and foul is fair;
```

**Input commentary:**
```
5. WARBURTON: "hurly-burly" derives from the French "hurluberlu."
10. JOHNSON: The chiasmus "fair is foul, and foul is fair"...
```

**Output (corrected):**
```
3. WARBURTON: "hurly-burly" derives from the French "hurluberlu."
11. JOHNSON: The chiasmus "fair is foul, and foul is fair"...
```

---

## Usage
Provide the play text for one scene and the scholarly commentary for that scene. Process scene by scene to keep line-number context correct.
