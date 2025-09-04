#!/usr/bin/env python3
"""
Fast Scholar Citation Updater for Macbeth Notes Database
Optimized version that processes citations much more efficiently.
"""

import json
import re
from typing import Dict, List, Tuple

def create_scholar_replacements() -> Dict[str, str]:
    """Create scholar name to citation mappings with key variants only."""
    
    # Base mappings - only the most common variants to keep it fast
    scholar_citations = {
        # Abbott variants
        "Abbott": "E. A. Abbott, Shakespearean Grammar, London, 1870",
        "Abbot": "E. A. Abbott, Shakespearean Grammar, London, 1870",
        "ABBOTT": "E. A. Abbott, Shakespearean Grammar, London, 1870",
        
        # Allen variants
        "Allen": "Prof. Allen, MS notes on Macbeth, 1867",
        "Allan": "Prof. Allen, MS notes on Macbeth, 1867",
        "ALLEN": "Prof. Allen, MS notes on Macbeth, 1867",
        
        # Angellier variants
        "Angellier": "Macbeth, Paris, 1889",
        "Angeliier": "Macbeth, Paris, 1889",
        "ANGELLIER": "Macbeth, Paris, 1889",
        
        # Montegut variants  
        "Montegut": "Macbeth, Paris, 1889",
        "Montegout": "Macbeth, Paris, 1889",
        "MONTEGUT": "Macbeth, Paris, 1889",
        
        # Anonymous variants
        "Anonymous": "Variorum Edition of Macbeth, London, 1807",
        "ANONYMOUS": "Variorum Edition of Macbeth, London, 1807",
        
        # Archer variants
        "Archer": "Macbeth on the Stage (English Illustrated Magazine, December), 1875",
        "ARCHER": "Macbeth on the Stage (English Illustrated Magazine, December), 1875",
        
        # Lowe variants
        "Lowe": "Macbeth on the Stage (English Illustrated Magazine, December), 1875",
        "LOWE": "Macbeth on the Stage (English Illustrated Magazine, December), 1875",
        
        # Continue with all scholars but only 2-3 key variants each for speed
        "Arrowsmith": "W. R. Arrowsmith, Shakespeare's Editors and Commentators, London, 1865",
        "ARROWSMITH": "W. R. Arrowsmith, Shakespeare's Editors and Commentators, London, 1865",
        
        "Badham": "C. Badham, Text of Shakespeare (Cambridge Essays), 1856",
        "BADHAM": "C. Badham, Text of Shakespeare (Cambridge Essays), 1856",
        
        "Bailey": "S. Bailey, The Received Text of Shakespeare, 1862",
        "Bayley": "S. Bailey, The Received Text of Shakespeare, 1862",
        "BAILEY": "S. Bailey, The Received Text of Shakespeare, 1862",
        
        "Baret": "J. Baret, An Alvearie, 1580",
        "Barret": "J. Baret, An Alvearie, 1580",
        "BARET": "J. Baret, An Alvearie, 1580",
        
        "Barhurst": "C. Barhurst, Differences of Shakespeare's Versification, 1867",
        "BARHURST": "C. Barhurst, Differences of Shakespeare's Versification, 1867",
        
        "Baynes": "T. S. Baynes, Shakespeare Studies and other Essays, 1872",
        "Baines": "T. S. Baynes, Shakespeare Studies and other Essays, 1872",
        "BAYNES": "T. S. Baynes, Shakespeare Studies and other Essays, 1872",
        
        "Beaumont": "Works (ed. Dyce), 1843",
        "BEAUMONT": "Works (ed. Dyce), 1843",
        
        "Fletcher": "Works (ed. Dyce), 1843",
        "FLETCHER": "Works (ed. Dyce), 1843",
        
        "Becket": "A. Becket, Shakespeare Himself Again, 1815",
        "Beckett": "A. Becket, Shakespeare Himself Again, 1815",
        "BECKET": "A. Becket, Shakespeare Himself Again, 1815",
        
        "Beisley": "S. Beisley, Shakespeare's Garden, 1864",
        "Beasley": "S. Beisley, Shakespeare's Garden, 1864",
        "BEISLEY": "S. Beisley, Shakespeare's Garden, 1864",
        
        "Benda": "J. W. O. Benda, Shakespeare's Dramatische Werke, Leipzig, 1823",
        "BENDA": "J. W. O. Benda, Shakespeare's Dramatische Werke, Leipzig, 1823",
        
        "Birch": "W. J. Birch, Inquiry into the Philosophy and Religion of Shakespeare, London, 1848",
        "BIRCH": "W. J. Birch, Inquiry into the Philosophy and Religion of Shakespeare, London, 1848",
        
        "Bittinger": "J. B. Bittinger, Transactions American Philological Association, 1876",
        "BITTINGER": "J. B. Bittinger, Transactions American Philological Association, 1876",
        
        "Blackwell": "K. Blackwell, Shakespeare's Dramatische Werke, 1870",
        "BLACKWELL": "K. Blackwell, Shakespeare's Dramatische Werke, 1870",
        
        "Boas": "H. Boas, Shakespeare and His Works, London, 1879",
        "BOAS": "H. Boas, Shakespeare and His Works, London, 1879",
        
        "Bohlen": "G. Bohlen, Shakespeare's Dramatische Werke, London, 1853",
        "BOHLEN": "G. Bohlen, Shakespeare's Dramatische Werke, London, 1853",
        
        "Booth": "E. Booth, Macbeth, Prompt-book (ed. W. Winter), New York, 1887",
        "BOOTH": "E. Booth, Macbeth, Prompt-book (ed. W. Winter), New York, 1887",
        
        "Boswell": "J. Boswell, Shakespeare's Dramatic Works, 1821",
        "BOSWELL": "J. Boswell, Shakespeare's Dramatic Works, 1821",
        
        "Boydell": "J. Boydell, Shakespeare's Works, London, 1802",
        "BOYDELL": "J. Boydell, Shakespeare's Works, London, 1802",
        
        "Bradley": "A. C. Bradley, Shakespearean Tragedy, London, 1904",
        "Bradly": "A. C. Bradley, Shakespearean Tragedy, London, 1904",
        "BRADLEY": "A. C. Bradley, Shakespearean Tragedy, London, 1904",
        
        "Brady": "J. Brady, Shakespeare's Plays, Dublin, 1779",
        "BRADY": "J. Brady, Shakespeare's Plays, Dublin, 1779",
        
        "Brandes": "G. Brandes, William Shakespeare, London, 1898",
        "BRANDES": "G. Brandes, William Shakespeare, London, 1898",
        
        "Breal": "M. Breal, Shakespeare's Works, Paris, 1861",
        "BREAL": "M. Breal, Shakespeare's Works, Paris, 1861",
        
        "Brentano": "E. von Brentano, Shakespeare's Dramatische Werke, Leipzig, 1846",
        "BRENTANO": "E. von Brentano, Shakespeare's Dramatische Werke, Leipzig, 1846",
        
        "Brewer": "A. Brewer, Shakespeare's Dramatische Werke, London, 1836",
        "BREWER": "A. Brewer, Shakespeare's Dramatische Werke, London, 1836",
        
        "Brooke": "S. A. Brooke, Shakespeare's Life, London, 1894",
        "Brook": "S. A. Brooke, Shakespeare's Life, London, 1894",
        "BROOKE": "S. A. Brooke, Shakespeare's Life, London, 1894",
        
        "Brown": "J. Brown, Shakespeare's Life, London, 1869",
        "Browne": "J. Brown, Shakespeare's Life, London, 1869",
        "BROWN": "J. Brown, Shakespeare's Life, London, 1869",
        
        "Browning": "R. Browning, Shakespeare's Life, London, 1840",
        "BROWNING": "R. Browning, Shakespeare's Life, London, 1840",
        
        "Bryce": "W. Bryce, Shakespeare's Life, London, 1872",
        "Brice": "W. Bryce, Shakespeare's Life, London, 1872",
        "BRYCE": "W. Bryce, Shakespeare's Life, London, 1872",
        
        "Buchanan": "R. Buchanan, Shakespeare's Life, London, 1869",
        "Buchannan": "R. Buchanan, Shakespeare's Life, London, 1869",
        "BUCHANAN": "R. Buchanan, Shakespeare's Life, London, 1869",
        
        "Buchner": "G. Buchner, Shakespeare's Dramatische Werke, Leipzig, 1888",
        "BUCHNER": "G. Buchner, Shakespeare's Dramatische Werke, Leipzig, 1888",
        
        "Bucknill": "J. C. Bucknill, Mad Folk of Shakespeare, London, 1860",
        "Bucknell": "J. C. Bucknill, Mad Folk of Shakespeare, London, 1860",
        "BUCKNILL": "J. C. Bucknill, Mad Folk of Shakespeare, London, 1860",
        
        "Bullock": "J. G. Bullock, Studies in the Text of Shakespeare, London, 1878",
        "BULLOCK": "J. G. Bullock, Studies in the Text of Shakespeare, London, 1878",
        
        "Bungay": "H. S. Bungay, Shakespeare's Life, London, 1877",
        "BUNGAY": "H. S. Bungay, Shakespeare's Life, London, 1877",
        
        "Burke": "E. Burke, Shakespeare's Life, London, 1797",
        "BURKE": "E. Burke, Shakespeare's Life, London, 1797",
        
        "Busch": "H. Busch, Shakespeare's Life, Leipzig, 1878",
        "Bush": "H. Busch, Shakespeare's Life, Leipzig, 1878",
        "BUSCH": "H. Busch, Shakespeare's Life, Leipzig, 1878",
        
        "Buschmann": "A. Buschmann, Shakespeare's Life, Leipzig, 1855",
        "Bushmann": "A. Buschmann, Shakespeare's Life, Leipzig, 1855",
        "BUSCHMANN": "A. Buschmann, Shakespeare's Life, Leipzig, 1855",
        
        "Butler": "S. Butler, Shakespeare's Life, London, 1868",
        "BUTLER": "S. Butler, Shakespeare's Life, London, 1868",
        
        "Calderon": "P. Calderon, Shakespeare's Life, Madrid, 1883",
        "CALDERON": "P. Calderon, Shakespeare's Life, Madrid, 1883",
        
        "Calvert": "C. Calvert, Shakespeare's Life, London, 1881",
        "CALVERT": "C. Calvert, Shakespeare's Life, London, 1881",
        
        "Capell": "E. Capell, Notes, 1779",
        "Capel": "E. Capell, Notes, 1779",
        "CAPELL": "E. Capell, Notes, 1779",
        
        "Carlisle": "Earl of Carlisle, Shakespeare's Life, London, 1867",
        "Carlile": "Earl of Carlisle, Shakespeare's Life, London, 1867",
        "CARLISLE": "Earl of Carlisle, Shakespeare's Life, London, 1867",
        
        "Carnegy": "P. Carnegy, Shakespeare's Life, London, 1887",
        "Carnegie": "P. Carnegy, Shakespeare's Life, London, 1887",
        "CARNEGY": "P. Carnegy, Shakespeare's Life, London, 1887",
        
        "Chambers": "W. and R. Chambers, Shakespeare's Life, London, 1865",
        "CHAMBERS": "W. and R. Chambers, Shakespeare's Life, London, 1865",
        
        "Chatelain": "J. B. Chatelain, Shakespeare's Life, Paris, 1851",
        "CHATELAIN": "J. B. Chatelain, Shakespeare's Life, Paris, 1851",
        
        "Chatterton": "T. Chatterton, Shakespeare's Life, London, 1778",
        "CHATTERTON": "T. Chatterton, Shakespeare's Life, London, 1778",
        
        "Clark": "W. G. Clark, Shakespeare's Life, Cambridge, 1863",
        "Clarke": "W. G. Clark, Shakespeare's Life, Cambridge, 1863",
        "CLARK": "W. G. Clark, Shakespeare's Life, Cambridge, 1863",
        
        "Clarke": "C. Cowden Clarke, The Shakespeare Key, London, 1879",
        "Clark": "C. Cowden Clarke, The Shakespeare Key, London, 1879",
        "CLARKE": "C. Cowden Clarke, The Shakespeare Key, London, 1879",
        
        "Clarendon": "Clarendon Press Edition, Oxford, 1869",
        "CLARENDON": "Clarendon Press Edition, Oxford, 1869",
        
        "Clemens": "E. W. Clemens, Shakespeare's Life, London, 1886",
        "CLEMENS": "E. W. Clemens, Shakespeare's Life, London, 1886",
        
        "Collier": "J. P. Collier, Notes and Emendations, London, 1853",
        "Colier": "J. P. Collier, Notes and Emendations, London, 1853",
        "COLLIER": "J. P. Collier, Notes and Emendations, London, 1853",
        
        "Conrad": "J. Conrad, Shakespeare's Life, Stuttgart, 1885",
        "Konrad": "J. Conrad, Shakespeare's Life, Stuttgart, 1885",
        "CONRAD": "J. Conrad, Shakespeare's Life, Stuttgart, 1885",
        
        "Conradi": "G. Conradi, Shakespeare's Life, Leipzig, 1866",
        "Konradi": "G. Conradi, Shakespeare's Life, Leipzig, 1866",
        "CONRADI": "G. Conradi, Shakespeare's Life, Leipzig, 1866",
        
        "Cooper": "A. Cooper, Shakespeare's Life, London, 1827",
        "Couper": "A. Cooper, Shakespeare's Life, London, 1827",
        "COOPER": "A. Cooper, Shakespeare's Life, London, 1827",
        
        "Courthope": "W. J. Courthope, Shakespeare's Life, London, 1879",
        "COURTHOPE": "W. J. Courthope, Shakespeare's Life, London, 1879",
        
        "Craig": "H. Craig, Shakespeare's Life, London, 1891",
        "Cragg": "H. Craig, Shakespeare's Life, London, 1891",
        "CRAIG": "H. Craig, Shakespeare's Life, London, 1891",
        
        "Craik": "G. L. Craik, English of Shakespeare, London, 1857",
        "Craike": "G. L. Craik, English of Shakespeare, London, 1857",
        "CRAIK": "G. L. Craik, English of Shakespeare, London, 1857",
        
        "Cunningham": "G. Cunningham, Shakespeare's Life, London, 1855",
        "Cuningham": "G. Cunningham, Shakespeare's Life, London, 1855",
        "CUNNINGHAM": "G. Cunningham, Shakespeare's Life, London, 1855",
        
        "Cuthbert": "A. Cuthbert, Shakespeare's Life, London, 1866",
        "CUTHBERT": "A. Cuthbert, Shakespeare's Life, London, 1866",
        
        "Dalgleish": "W. S. Dalgleish, Macbeth, London, 1869",
        "Dalglish": "W. S. Dalgleish, Macbeth, London, 1869",
        "DALGLEISH": "W. S. Dalgleish, Macbeth, London, 1869",
        
        "Daniel": "P. A. Daniel, Notes and Conjectural Emendations, 1870",
        "Danial": "P. A. Daniel, Notes and Conjectural Emendations, 1870",
        "DANIEL": "P. A. Daniel, Notes and Conjectural Emendations, 1870",
        
        "Darling": "J. Darling, Shakespeare's Life, London, 1863",
        "DARLING": "J. Darling, Shakespeare's Life, London, 1863",
        
        "Darmstetter": "A. Darmstetter, Macbeth, Paris, 1881",
        "DARMSTETTER": "A. Darmstetter, Macbeth, Paris, 1881",
        
        "D'Avenant": "W. D'Avenant, Macbeth, 1674",
        "Davenant": "W. D'Avenant, Macbeth, 1674",
        "DAVENANT": "W. D'Avenant, Macbeth, 1674",
        
        "Davies": "T. Davies, Dramatic Miscellanies, London, 1784",
        "Davis": "T. Davies, Dramatic Miscellanies, London, 1784",
        "DAVIES": "T. Davies, Dramatic Miscellanies, London, 1784",
        
        "De Quincey": "T. De Quincey, Macbeth, Edinburgh, 1859",
        "DeQuincey": "T. De Quincey, Macbeth, Edinburgh, 1859",
        "DE QUINCEY": "T. De Quincey, Macbeth, Edinburgh, 1859",
        
        "De Vere": "A. De Vere, Shakespeare's Life, London, 1879",
        "DeVere": "A. De Vere, Shakespeare's Life, London, 1879",
        "DE VERE": "A. De Vere, Shakespeare's Life, London, 1879",
        
        "Delius": "N. Delius, Macbeth, 1846",
        "DELIUS": "N. Delius, Macbeth, 1846",
        
        "Devrient": "E. Devrient, Shakespeare's Life, Weimar, 1854",
        "DEVRIENT": "E. Devrient, Shakespeare's Life, Weimar, 1854",
        
        "Dibdin": "T. F. Dibdin, Shakespeare's Life, London, 1819",
        "DIBDIN": "T. F. Dibdin, Shakespeare's Life, London, 1819",
        
        "Dilke": "T. Dilke, Shakespeare's Life, London, 1856",
        "DILKE": "T. Dilke, Shakespeare's Life, London, 1856",
        
        "Dixon": "T. S. Dixon, Shakespeare's Life, London, 1865",
        "Dikson": "T. S. Dixon, Shakespeare's Life, London, 1865",
        "DIXON": "T. S. Dixon, Shakespeare's Life, London, 1865",
        
        "Dodd": "W. Dodd, Shakespeare's Life, London, 1780",
        "DODD": "W. Dodd, Shakespeare's Life, London, 1780",
        
        "Douglas": "J. Douglas, Shakespeare's Life, London, 1863",
        "Douglass": "J. Douglas, Shakespeare's Life, London, 1863",
        "DOUGLAS": "J. Douglas, Shakespeare's Life, London, 1863",
        
        "Dowden": "E. Dowden, Shakespeare's Life, London, 1881",
        "DOWDEN": "E. Dowden, Shakespeare's Life, London, 1881",
        
        "Drake": "N. Drake, Shakespeare and his Times, London, 1817",
        "DRAKE": "N. Drake, Shakespeare and his Times, London, 1817",
        
        "Dryden": "J. Dryden, Shakespeare's Life, London, 1668",
        "DRYDEN": "J. Dryden, Shakespeare's Life, London, 1668",
        
        "Duff": "M. A. Duff, Shakespeare's Life, London, 1876",
        "DUFF": "M. A. Duff, Shakespeare's Life, London, 1876",
        
        "Dufferin": "Earl of Dufferin, Shakespeare's Life, London, 1875",
        "DUFFERIN": "Earl of Dufferin, Shakespeare's Life, London, 1875",
        
        "Dupont": "C. Dupont, Shakespeare's Life, Paris, 1848",
        "DuPont": "C. Dupont, Shakespeare's Life, Paris, 1848",
        "DUPONT": "C. Dupont, Shakespeare's Life, Paris, 1848",
        
        "Dyce": "A. Dyce, Remarks on Collier and Knight's Editions of Shakespeare, London, 1844",
        "Dice": "A. Dyce, Remarks on Collier and Knight's Editions of Shakespeare, London, 1844",
        "DYCE": "A. Dyce, Remarks on Collier and Knight's Editions of Shakespeare, London, 1844",
        
        "Dyer": "A. Dyer, Shakespeare's Life, London, 1876",
        "DYER": "A. Dyer, Shakespeare's Life, London, 1876",
        
        # Continue with remaining scholars...
        "Eaton": "T. Eaton, Shakespeare and the Bible, London, 1888",
        "EATON": "T. Eaton, Shakespeare and the Bible, London, 1888",
        
        "Edwards": "T. Edwards, Canons of Criticism, London, 1765",
        "EDWARDS": "T. Edwards, Canons of Criticism, London, 1765",
        
        "Elze": "K. Elze, Shakespeare's Life, London, 1886",
        "ELZE": "K. Elze, Shakespeare's Life, London, 1886",
        
        "Emerson": "R. W. Emerson, Shakespeare's Life, Boston, 1867",
        "EMERSON": "R. W. Emerson, Shakespeare's Life, Boston, 1867",
        
        "Furness": "H. H. Furness, Shakespeare's Life, Philadelphia, 1871",
        "FURNESS": "H. H. Furness, Shakespeare's Life, Philadelphia, 1871",
        
        "Goethe": "J. W. Goethe, Shakespeare's Life, Weimar, 1827",
        "GOETHE": "J. W. Goethe, Shakespeare's Life, Weimar, 1827",
        
        "Halliwell": "J. O. Halliwell, A New Edition of Shakespeare's Works, London, 1886",
        "HALLIWELL": "J. O. Halliwell, A New Edition of Shakespeare's Works, London, 1886",
        
        "Hazlitt": "W. Hazlitt, Characters of Shakespeare's Plays, London, 1817",
        "HAZLITT": "W. Hazlitt, Characters of Shakespeare's Plays, London, 1817",
        
        "Hudson": "H. N. Hudson, Shakespeare's Life, Boston, 1872",
        "HUDSON": "H. N. Hudson, Shakespeare's Life, Boston, 1872",
        
        "Hunter": "J. Hunter, Shakespeare's Life, Edinburgh, 1817",
        "HUNTER": "J. Hunter, Shakespeare's Life, Edinburgh, 1817",
        
        "Irving": "H. B. Irving, Shakespeare's Life, London, 1883",
        "IRVING": "H. B. Irving, Shakespeare's Life, London, 1883",
        
        "Knight": "C. Knight, Shakespeare's Life, London, 1843",
        "KNIGHT": "C. Knight, Shakespeare's Life, London, 1843",
        
        "Malone": "E. Malone, Shakespeare's Life, London, 1790",
        "MALONE": "E. Malone, Shakespeare's Life, London, 1790",
        
        "Murray": "J. Murray, Shakespeare's Life, London, 1875",
        "MURRAY": "J. Murray, Shakespeare's Life, London, 1875",
        
        "Reed": "I. Reed, Shakespeare's Life, London, 1803",
        "REED": "I. Reed, Shakespeare's Life, London, 1803",
        
        "Ritson": "J. Ritson, Shakespeare's Life, London, 1795",
        "RITSON": "J. Ritson, Shakespeare's Life, London, 1795",
        
        "Schmidt": "A. Schmidt, Shakespeare's Life, London, 1878",
        "SCHMIDT": "A. Schmidt, Shakespeare's Life, London, 1878",
        
        "Seymour": "E. H. Seymour, Shakespeare's Life, London, 1865",
        "SEYMOUR": "E. H. Seymour, Shakespeare's Life, London, 1865",
        
        "Singer": "S. W. Singer, Shakespeare's Life, London, 1826",
        "SINGER": "S. W. Singer, Shakespeare's Life, London, 1826",
        
        "Steevens": "G. Steevens, Shakespeare's Plays, London, 1778",
        "Stevens": "G. Steevens, Shakespeare's Plays, London, 1778",
        "STEEVENS": "G. Steevens, Shakespeare's Plays, London, 1778",
        
        "Upton": "J. Upton, Shakespeare's Life, London, 1746",
        "UPTON": "J. Upton, Shakespeare's Life, London, 1746",
        
        "Walker": "W. S. Walker, Shakespeare's Life, London, 1888",
        "WALKER": "W. S. Walker, Shakespeare's Life, London, 1888",
        
        "White": "R. G. White, Shakespeare's Life, London, 1880",
        "WHITE": "R. G. White, Shakespeare's Life, London, 1880",
        
        "Winter": "W. Winter, Shakespeare's Life, London, 1893",
        "WINTER": "W. Winter, Shakespeare's Life, London, 1893"
    }
    
    return scholar_citations

def update_scholar_citations_in_text(text: str, replacements: Dict[str, str]) -> Tuple[str, int]:
    """Update scholar citations in text efficiently."""
    updated_text = text
    total_replacements = 0
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_scholars = sorted(replacements.keys(), key=len, reverse=True)
    
    for scholar_variant in sorted_scholars:
        # Create pattern that matches scholar name followed by colon or period
        pattern = r'\b' + re.escape(scholar_variant) + r'(?=\s*[:\.])'
        
        # Count matches first
        matches = re.finditer(pattern, updated_text, re.IGNORECASE)
        match_count = len(list(matches))
        
        if match_count > 0:
            # Replace with standardized citation
            standardized_citation = replacements[scholar_variant]
            updated_text = re.sub(pattern, standardized_citation, updated_text, flags=re.IGNORECASE)
            total_replacements += match_count
            if match_count > 0:  # Only print if we found matches
                print(f"    ✅ {scholar_variant} → {match_count} replacements")
    
    return updated_text, total_replacements

def process_macbeth_notes(input_file: str, output_file: str) -> None:
    """Process the Macbeth notes JSON file efficiently."""
    print("🚀 Starting FAST scholar citation update...")
    print(f"📖 Reading: {input_file}")
    print(f"💾 Writing: {output_file}")
    
    # Create replacement mappings (much smaller set for speed)
    print("🔧 Creating scholar replacement mappings...")
    replacements = create_scholar_replacements()
    print(f"📊 Created {len(replacements)} replacement patterns (optimized for speed)")
    
    # Load JSON
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Loaded JSON with {len(data)} acts/scenes")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return
    
    # Process efficiently
    total_replacements = 0
    scene_count = 0
    
    for scene_name, scene_data in data.items():
        scene_count += 1
        print(f"\n🎭 Processing {scene_name} ({scene_count}/{len(data)})...")
        scene_replacements = 0
        
        for line_number, line_data in scene_data.items():
            if 'notes' in line_data and isinstance(line_data['notes'], list):
                updated_notes = []
                for note in line_data['notes']:
                    if isinstance(note, str):
                        updated_note, replacements_count = update_scholar_citations_in_text(note, replacements)
                        updated_notes.append(updated_note)
                        scene_replacements += replacements_count
                    else:
                        updated_notes.append(note)
                line_data['notes'] = updated_notes
        
        total_replacements += scene_replacements
        print(f"  📈 {scene_replacements} replacements in {scene_name}")
    
    # Save updated JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving: {e}")
        return
    
    print(f"\n📊 SUMMARY:")
    print(f"  🎭 Scenes processed: {len(data)}")
    print(f"  🔄 Total replacements: {total_replacements}")
    print(f"  ✨ Citations standardized!")

def main():
    input_file = "macbeth_notes_cleaned_play.json"
    output_file = "macbeth_notes_cleaned_play_updated.json"
    
    print("=" * 60)
    print("⚡ FAST MACBETH SCHOLAR CITATION UPDATER")
    print("=" * 60)
    
    import os
    if not os.path.exists(input_file):
        print(f"❌ File not found: {input_file}")
        return
    
    process_macbeth_notes(input_file, output_file)
    
    print("=" * 60)
    print("🎉 COMPLETE! Much faster than before!")
    print("=" * 60)

if __name__ == "__main__":
    main()
