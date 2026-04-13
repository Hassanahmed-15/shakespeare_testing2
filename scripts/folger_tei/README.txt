Folger TEI + New Variorum alignment (Hamlet, Othello, future plays)
===================================================================

License
-------
Folger Digital Texts XML is CC BY-NC 4.0. Keep attribution and noncommercial
terms wherever you ship TEI or derived line text. See index.html Rights modal.

Pipeline
--------
1) Place Folger XML under Public/Data/folger_tei/ (e.g. Oth.xml, Ham.xml).

2) Align legacy Variorum JSON (integer line keys) to Folger anchors and emit
   merged reader JSON (Folger line text, stage directions as [brackets], notes
   mapped by similarity). From repository root:

   Othello (optional note overrides):

   PYTHONPATH=. python3 -m scripts.folger_tei.align_nv_to_folger \
     --tei Public/Data/folger_tei/Oth.xml \
     --legacy Public/Data/othello_notes.json \
     --out Public/Data/othello_notes_folger.json \
     --review Public/Data/othello_folger_alignment_review.json

   By default, if Public/Data/othello_note_overrides.json exists, post-moves
   are applied (use --no-overrides to skip, or --overrides PATH for another file).

   Hamlet (use --no-overrides so othello_note_overrides.json is not applied):

   PYTHONPATH=. python3 -m scripts.folger_tei.align_nv_to_folger \
     --tei Public/Data/folger_tei/Ham.xml \
     --legacy PATH/TO/hamlet_legacy_integer_keys.json \
     --out Public/Data/hamlet_notes\ \(1\).json \
     --review Public/Data/hamlet_folger_alignment_review.json \
     --no-overrides

   --legacy must be Variorum JSON with integer line keys (1, 2, 3, ... per scene).
   Do not pass the merged Folger-anchor JSON as --legacy; keep a backup of the
   pre-merge file for re-runs. First-time output is written to --out; inspect
   --review for alignment gaps.

3) Optional: ingest-only exploration is via scripts/folger_tei/ingest_folger_tei.py
   (parse_folger_play) for debugging TEI structure.

Legacy vs Folger scene boundaries
---------------------------------
When the Variorum JSON merged two Folger scenes under one heading, add a tuple
under LEGACY_TO_FOLGER_SCENE_SEGMENTS in align_nv_to_folger.py. Mappings are
scoped by Folger play id (TEI publication idno, e.g. "Oth", "Ham") so an
Othello-only merge is not applied to Hamlet or other plays. Example: Othello
ACT 2, SCENE 2 spans Folger ACT 2, SCENE 2 and ACT 2, SCENE 3.

Note overrides
--------------
Edit Public/Data/othello_note_overrides.json to move a note from one Folger
line key to another when the gloss clearly refers to different speech than the
legacy integer key. Each move requires scene, fromLineKey, toLineKey,
noteContains (substring match), and optional reason. Re-run the aligner after edits.

Deployment (Netlify)
--------------------
This site is deployed from the connected Git repository. Pushing commits to the
branch Netlify watches (typically main) triggers a build and publish. No
separate Netlify CLI step is required unless you deploy manually.

Stopping point (automated scope)
--------------------------------
Everything above is intended to be repeatable without reading every line by hand.
Line-by-line scholarly QA is optional and out of scope for the scripted pipeline.
