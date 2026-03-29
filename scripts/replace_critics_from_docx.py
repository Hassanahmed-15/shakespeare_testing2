#!/usr/bin/env python3
"""
Replace critics-list content in index.html with the exact content
from the NV Critics docx files for each play.
"""

import zipfile
import xml.etree.ElementTree as ET
import re
import html as html_mod
import os
import shutil
import sys

WS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCX_DIR = os.path.join(WS, "Public", "Data", "NV_Critics_All (1)")
INDEX_HTML = os.path.join(WS, "index.html")

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

DOCX_TO_MODAL = {
    "Variorum_Macbeth_Critics.docx": ["criticsModalLegacy", "criticsModal"],
    "Variorum_King_Lear_Critics.docx": ["kingLearCriticsModal"],
    "Variorum_Hamlet_Critics.docx": ["hamletCriticsModal"],
    "Variorum_Romeo_and_Juliet_Critics.docx": ["romeoJulietCriticsModal"],
    "Variorum_Othello_Critics.docx": ["othelloCriticsModal"],
    "Variorum_Henry_IV_Part_1_Critics.docx": ["henryiv1CriticsModal"],
    "Variorum_Midsummer_Nights_Dream_Critics.docx": ["midsummerCriticsModal"],
    "Variorum_As_You_Like_It_Critics.docx": ["asyoulikeitCriticsModal"],
    "Variorum_Julius_Caesar_Critics.docx": ["juliuscaesarCriticsModal"],
    "Variorum_King_John_Critics.docx": ["kingjohnCriticsModal"],
    "Variorum_Loves_Labours_Lost_Critics.docx": ["loveslabourslostCriticsModal"],
    "Variorum_Much_Ado_About_Nothing_Critics.docx": ["muchadoCriticsModal"],
    "Variorum_Richard_III_Critics.docx": ["richardiiiCriticsModal"],
    "Variorum_Merchant_of_Venice_Critics.docx": ["merchantofveniceCriticsModal"],
    "Variorum_The_Tempest_Critics.docx": ["tempestCriticsModal"],
    "Variorum_Winters_Tale_Critics.docx": ["winterstaleCriticsModal"],
    "Variorum_Twelfth_Night_Critics.docx": ["twelfthnightCriticsModal"],
    "Variorum_Antony_and_Cleopatra_Critics.docx": ["antonyCriticsModal"],
    "Variorum_Coriolanus_Critics.docx": ["coriolanusCriticsModal"],
    "Variorum_Cymbeline_Critics.docx": ["cymbelineCriticsModal"],
}

DOCX_TO_PLAY_NAME = {
    "Variorum_Macbeth_Critics.docx": "Macbeth",
    "Variorum_King_Lear_Critics.docx": "King Lear",
    "Variorum_Hamlet_Critics.docx": "Hamlet",
    "Variorum_Romeo_and_Juliet_Critics.docx": "Romeo and Juliet",
    "Variorum_Othello_Critics.docx": "Othello",
    "Variorum_Henry_IV_Part_1_Critics.docx": "Henry IV Part 1",
    "Variorum_Midsummer_Nights_Dream_Critics.docx": "A Midsummer Night's Dream",
    "Variorum_As_You_Like_It_Critics.docx": "As You Like It",
    "Variorum_Julius_Caesar_Critics.docx": "Julius Caesar",
    "Variorum_King_John_Critics.docx": "King John",
    "Variorum_Loves_Labours_Lost_Critics.docx": "Love's Labour's Lost",
    "Variorum_Much_Ado_About_Nothing_Critics.docx": "Much Ado About Nothing",
    "Variorum_Richard_III_Critics.docx": "Richard III",
    "Variorum_Merchant_of_Venice_Critics.docx": "The Merchant of Venice",
    "Variorum_The_Tempest_Critics.docx": "The Tempest",
    "Variorum_Winters_Tale_Critics.docx": "The Winter's Tale",
    "Variorum_Twelfth_Night_Critics.docx": "Twelfth Night",
    "Variorum_Antony_and_Cleopatra_Critics.docx": "Antony and Cleopatra",
    "Variorum_Coriolanus_Critics.docx": "Coriolanus",
    "Variorum_Cymbeline_Critics.docx": "Cymbeline",
}


def get_para_style(p):
    ppr = p.find('w:pPr', NS)
    if ppr is None:
        return ''
    s = ppr.find('w:pStyle', NS)
    if s is None:
        return ''
    return s.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '')


def extract_runs(p):
    """Return list of (text, bold, italic) tuples for a paragraph's runs."""
    runs = []
    for r in p.findall('.//w:r', NS):
        rpr = r.find('w:rPr', NS)
        bold = False
        italic = False
        if rpr is not None:
            if rpr.find('w:b', NS) is not None:
                bold = True
            if rpr.find('w:i', NS) is not None:
                italic = True
        t = r.find('w:t', NS)
        txt = t.text if t is not None and t.text else ''
        if txt:
            runs.append((txt, bold, italic))
    return runs


def runs_to_html(runs):
    """Convert a list of (text, bold, italic) tuples to HTML string."""
    parts = []
    for text, bold, italic in runs:
        escaped = html_mod.escape(text)
        if bold and italic:
            parts.append(f'<strong><em>{escaped}</em></strong>')
        elif bold:
            parts.append(f'<strong>{escaped}</strong>')
        elif italic:
            parts.append(f'<em>{escaped}</em>')
        else:
            parts.append(escaped)
    return ''.join(parts)


def plain_text(runs):
    return ''.join(t for t, b, i in runs)


def extract_table_html(tbl):
    """Convert a docx table to an HTML table."""
    rows = tbl.findall('.//w:tr', NS)
    html_parts = []
    html_parts.append('<table class="nvs-table" style="width:100%; border-collapse:collapse; margin: 15px 0; font-size: 0.95em;">')

    for ri, row in enumerate(rows):
        cells = row.findall('.//w:tc', NS)
        tag = 'th' if ri == 0 else 'td'
        html_parts.append('  <tr>')
        for cell in cells:
            cell_runs = []
            for p in cell.findall('.//w:p', NS):
                cell_runs.extend(extract_runs(p))
            cell_html = runs_to_html(cell_runs) if cell_runs else '&nbsp;'
            style = 'padding: 6px 10px; border-bottom: 1px solid #ddd; text-align: left;'
            if ri == 0:
                style += ' font-weight: 600; background: #f0f0f0;'
            html_parts.append(f'    <{tag} style="{style}">{cell_html}</{tag}>')
        html_parts.append('  </tr>')

    html_parts.append('</table>')
    return '\n'.join(html_parts)


def parse_docx(docx_path):
    """
    Parse a docx file and return a list of 'blocks'.
    Each block is a dict with:
      - type: 'title', 'heading1', 'heading2', 'paragraph', 'list_bullet', 'table'
      - html: the HTML string for this block
      - text: plain text (for debugging)
    """
    with zipfile.ZipFile(docx_path) as z:
        tree = ET.parse(z.open('word/document.xml'))

    body = tree.find('.//w:body', NS)
    blocks = []

    for child in body:
        tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag

        if tag == 'tbl':
            blocks.append({
                'type': 'table',
                'html': extract_table_html(child),
                'text': '[TABLE]',
            })
        elif tag == 'p':
            style = get_para_style(child)
            runs = extract_runs(child)
            if not runs:
                continue
            txt = plain_text(runs)
            h = runs_to_html(runs)

            if style == 'Title':
                blocks.append({'type': 'title', 'html': h, 'text': txt})
            elif style == 'Heading1':
                blocks.append({'type': 'heading1', 'html': h, 'text': txt})
            elif style == 'Heading2':
                blocks.append({'type': 'heading2', 'html': h, 'text': txt})
            elif style == 'ListBullet':
                blocks.append({'type': 'list_bullet', 'html': h, 'text': txt})
            else:
                blocks.append({'type': 'paragraph', 'html': h, 'text': txt})

    return blocks


def blocks_to_modal_body_html(blocks, play_name):
    """
    Convert parsed blocks into the full HTML for a modal-body div.
    """
    indent = '                '
    lines = []

    for block in blocks:
        btype = block['type']
        h = block['html']

        if btype == 'title':
            lines.append(f'{indent}<h3 style="text-align: center; color: #2c3e50; margin-bottom: 5px;">{h}</h3>')
        elif btype == 'heading1':
            lines.append(f'{indent}<div class="critics-separator" style="margin: 25px 0 15px 0; padding: 15px 0; border-top: 2px solid #e5e7eb; border-bottom: 2px solid #e5e7eb;">')
            lines.append(f'{indent}    <h4 style="text-align: center; color: #666; font-weight: 600;">{h}</h4>')
            lines.append(f'{indent}</div>')
        elif btype == 'heading2':
            lines.append(f'{indent}<h5 style="color: #555; font-weight: 600; margin: 20px 0 10px 0; border-bottom: 1px solid #ddd; padding-bottom: 5px;">{h}</h5>')
        elif btype == 'table':
            lines.append(f'{indent}{h}')
        elif btype == 'list_bullet':
            lines.append(f'{indent}<p style="margin: 4px 0; padding-left: 20px;">{h}</p>')
        elif btype == 'paragraph':
            lines.append(f'{indent}<p style="margin: 6px 0; line-height: 1.6;">{h}</p>')

    return '\n'.join(lines)


def build_full_modal_html(modal_id, play_name, body_content, close_fn_name):
    """Build the complete modal div HTML."""
    return f'''    <div id="{modal_id}" class="modal" role="dialog" aria-modal="true" aria-labelledby="{modal_id}-title">
        <div class="modal-content">
            <div class="modal-header">
                <div class="modal-title" id="{modal_id}-title">Who are the NV Critics for {play_name}?</div>
                <button class="modal-close" onclick="{close_fn_name}()">&times;</button>
            </div>
            <div class="modal-body" style="max-height: 75vh; overflow-y: auto;">
{body_content}
            </div>
        </div>
    </div>'''


def find_modal_body_span(html_text, modal_id):
    """
    Find the start and end positions of the modal-body content
    for a given modal id. Returns (start, end) of the content
    between the modal-body opening tag and its closing tag,
    or None if not found.
    """
    modal_start = html_text.find(f'id="{modal_id}"')
    if modal_start < 0:
        return None

    search_from = modal_start
    body_tag = re.search(r'<div[^>]*class="modal-body"[^>]*>', html_text[search_from:search_from + 2000])
    if not body_tag:
        return None

    content_start = search_from + body_tag.end()

    depth = 1
    pos = content_start
    while depth > 0 and pos < len(html_text):
        next_open = html_text.find('<div', pos)
        next_close = html_text.find('</div>', pos)
        if next_close < 0:
            break
        if next_open >= 0 and next_open < next_close:
            depth += 1
            pos = next_open + 4
        else:
            depth -= 1
            if depth == 0:
                return (content_start, next_close)
            pos = next_close + 6

    return None


def main():
    dry_run = '--dry-run' in sys.argv

    if not os.path.isfile(INDEX_HTML):
        print(f"ERROR: {INDEX_HTML} not found")
        sys.exit(1)

    if not dry_run:
        backup = INDEX_HTML + '.bak_critics'
        shutil.copy2(INDEX_HTML, backup)
        print(f"Backup created: {backup}")

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html_text = f.read()

    new_modals_to_insert = []
    stats = {}

    for docx_name, modal_ids in DOCX_TO_MODAL.items():
        docx_path = os.path.join(DOCX_DIR, docx_name)
        play_name = DOCX_TO_PLAY_NAME[docx_name]

        if not os.path.isfile(docx_path):
            print(f"WARNING: {docx_path} not found, skipping {play_name}")
            continue

        print(f"\nProcessing {play_name} ({docx_name})...")
        blocks = parse_docx(docx_path)
        body_html = blocks_to_modal_body_html(blocks, play_name)
        block_count = len(blocks)

        for modal_id in modal_ids:
            span = find_modal_body_span(html_text, modal_id)
            if span:
                start, end = span
                old_content = html_text[start:end]
                html_text = html_text[:start] + '\n' + body_html + '\n            ' + html_text[end:]
                print(f"  ✓ Replaced content in {modal_id} ({block_count} blocks)")
                stats[modal_id] = block_count
            else:
                print(f"  ✗ Modal {modal_id} not found in HTML — will create new modal")
                close_fn = f"close{modal_id.replace('CriticsModal', '').capitalize()}CriticsModal"
                full_modal = build_full_modal_html(modal_id, play_name, body_html, f"close{modal_id[0].upper()}{modal_id[1:].replace('Modal', '')}")
                new_modals_to_insert.append((modal_id, play_name, full_modal, close_fn))
                stats[modal_id] = block_count

    if new_modals_to_insert:
        insert_pos = html_text.find('<!-- Critics Modal -->')
        if insert_pos < 0:
            insert_pos = html_text.find('<div id="criticsModal"')
        if insert_pos > 0:
            new_html = '\n\n'.join(modal_html for _, _, modal_html, _ in new_modals_to_insert)
            html_text = html_text[:insert_pos] + new_html + '\n\n    ' + html_text[insert_pos:]
            print(f"\n  ✓ Inserted {len(new_modals_to_insert)} new modals")

    if not dry_run:
        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(html_text)
        print(f"\n✅ index.html updated successfully")
    else:
        print(f"\n[DRY RUN] Would update index.html")

    print(f"\nSummary: {len(stats)} modals processed")
    for mid, count in stats.items():
        print(f"  {mid}: {count} blocks")

    # Also handle the JavaScript template critics-list and the second openCriticsModal function
    if not dry_run:
        update_js_functions(html_text, new_modals_to_insert)


def update_js_functions(html_text, new_modals):
    """Update JS functions to handle new play modals."""
    if not new_modals:
        return

    with open(INDEX_HTML, 'r', encoding='utf-8') as f:
        html_text = f.read()

    play_key_to_modal = {
        'antonyCriticsModal': ('antony', 'antonyCriticsModal'),
        'coriolanusCriticsModal': ('coriolanus', 'coriolanusCriticsModal'),
        'cymbelineCriticsModal': ('cymbeline', 'cymbelineCriticsModal'),
    }

    additions_open = []
    additions_close = []
    for modal_id, play_name, _, _ in new_modals:
        if modal_id in play_key_to_modal:
            key, mid = play_key_to_modal[modal_id]
            additions_open.append(f"            }} else if (currentPlay === '{key}') {{\n                document.getElementById('{mid}').style.display = 'flex';")
            additions_close.append(f"            try {{ document.getElementById('{mid}').style.display = 'none'; }} catch(e) {{}}")

    if additions_open:
        open_additions = '\n'.join(additions_open)
        close_additions = '\n'.join(additions_close)

        marker = "} else {\n                document.getElementById('criticsModal').style.display = 'flex';\n            }"
        count = 0
        pos = 0
        while True:
            idx = html_text.find(marker, pos)
            if idx < 0:
                break
            replacement = open_additions + '\n            ' + marker
            html_text = html_text[:idx] + replacement + html_text[idx + len(marker):]
            count += 1
            pos = idx + len(replacement)

        if count > 0:
            print(f"  ✓ Updated {count} openCriticsModal() function(s) with new plays")

        close_marker = "document.getElementById('twelfthnightCriticsModal').style.display = 'none';"
        idx = 0
        count = 0
        while True:
            pos = html_text.find(close_marker, idx)
            if pos < 0:
                break
            insert_at = pos + len(close_marker)
            html_text = html_text[:insert_at] + '\n' + close_additions + html_text[insert_at:]
            count += 1
            idx = insert_at + len(close_additions) + 10

        if count > 0:
            print(f"  ✓ Updated {count} closeCriticsModal() function(s) with new plays")

        with open(INDEX_HTML, 'w', encoding='utf-8') as f:
            f.write(html_text)
        print("  ✓ JS functions updated")


if __name__ == '__main__':
    main()
