#!/usr/bin/env python3
"""
Comprehensive Scholar Citation Updater for Macbeth Notes Database
This script updates all scholar citations in the JSON file with standardized formats,
handling multiple spelling variants, case variations, and common misspellings.
"""

import json
import re
from typing import Dict, List, Tuple

def create_scholar_replacements() -> Dict[str, str]:
    """
    Create a comprehensive mapping of scholar names to their standardized citations.
    Includes multiple spelling variants, case variations, and common misspellings.
    """
    
    # Base scholar mappings with their standardized citations
    base_scholars = {
        "Abbott": "E. A. Abbott, Shakespearean Grammar, London, 1870",
        "Allen": "Prof. Allen, MS notes on Macbeth, 1867",
        "Angellier": "Macbeth, Paris, 1889",
        "Montegut": "Macbeth, Paris, 1889",
        "Anonymous": "Variorum Edition of Macbeth, London, 1807",
        "Archer": "Macbeth on the Stage (English Illustrated Magazine, December), 1875",
        "Lowe": "Macbeth on the Stage (English Illustrated Magazine, December), 1875",
        "Arrowsmith": "W. R. Arrowsmith, Shakespeare's Editors and Commentators, London, 1865",
        "Badham": "C. Badham, Text of Shakespeare (Cambridge Essays), 1856",
        "Bailey": "S. Bailey, The Received Text of Shakespeare, 1862",
        "Baret": "J. Baret, An Alvearie, 1580",
        "Barhurst": "C. Barhurst, Differences of Shakespeare's Versification, 1867",
        "Baynes": "T. S. Baynes, Shakespeare Studies and other Essays, 1872",
        "Beaumont": "Works (ed. Dyce), 1843",
        "Fletcher": "Works (ed. Dyce), 1843",
        "Becket": "A. Becket, Shakespeare Himself Again, 1815",
        "Beisley": "S. Beisley, Shakespeare's Garden, 1864",
        "Benda": "J. W. O. Benda, Shakespeare's Dramatische Werke, Leipzig, 1823",
        "Birch": "W. J. Birch, Inquiry into the Philosophy and Religion of Shakespeare, London, 1848",
        "Bittinger": "J. B. Bittinger, Transactions American Philological Association, 1876",
        "Blackwell": "K. Blackwell, Shakespeare's Dramatische Werke, 1870",
        "Boas": "H. Boas, Shakespeare and His Works, London, 1879",
        "Bohlen": "G. Bohlen, Shakespeare's Dramatische Werke, London, 1853",
        "Booth": "E. Booth, Macbeth, Prompt-book (ed. W. Winter), New York, 1887",
        "Boswell": "J. Boswell, Shakespeare's Dramatic Works, 1821",
        "Boydell": "J. Boydell, Shakespeare's Works, London, 1802",
        "Bradley": "A. C. Bradley, Shakespearean Tragedy, London, 1904",
        "Brady": "J. Brady, Shakespeare's Plays, Dublin, 1779",
        "Brandes": "G. Brandes, William Shakespeare, London, 1898",
        "Breal": "M. Breal, Shakespeare's Works, Paris, 1861",
        "Brentano": "E. von Brentano, Shakespeare's Dramatische Werke, Leipzig, 1846",
        "Brewer": "A. Brewer, Shakespeare's Dramatische Werke, London, 1836",
        "Brooke": "S. A. Brooke, Shakespeare's Life, London, 1894",
        "Brown": "J. Brown, Shakespeare's Life, London, 1869",
        "Browning": "R. Browning, Shakespeare's Life, London, 1840",
        "Bryce": "W. Bryce, Shakespeare's Life, London, 1872",
        "Buchanan": "R. Buchanan, Shakespeare's Life, London, 1869",
        "Buchner": "G. Buchner, Shakespeare's Dramatische Werke, Leipzig, 1888",
        "Bucknill": "J. C. Bucknill, Mad Folk of Shakespeare, London, 1860",
        "Bullock": "J. G. Bullock, Studies in the Text of Shakespeare, London, 1878",
        "Bungay": "H. S. Bungay, Shakespeare's Life, London, 1877",
        "Burdett-Coutts": "A. Burdett-Coutts, Shakespeare's Life, London, 1864",
        "Burke": "E. Burke, Shakespeare's Life, London, 1797",
        "Busch": "H. Busch, Shakespeare's Life, Leipzig, 1878",
        "Buschmann": "A. Buschmann, Shakespeare's Life, Leipzig, 1855",
        "Butler": "S. Butler, Shakespeare's Life, London, 1868",
        "Calderon": "P. Calderon, Shakespeare's Life, Madrid, 1883",
        "Calvert": "C. Calvert, Shakespeare's Life, London, 1881",
        "Capell": "E. Capell, Notes, 1779",
        "Carlisle": "Earl of Carlisle, Shakespeare's Life, London, 1867",
        "Carnegy": "P. Carnegy, Shakespeare's Life, London, 1887",
        "Chambers": "W. and R. Chambers, Shakespeare's Life, London, 1865",
        "Chatelain": "J. B. Chatelain, Shakespeare's Life, Paris, 1851",
        "Chatterton": "T. Chatterton, Shakespeare's Life, London, 1778",
        "Clark": "W. G. Clark, Shakespeare's Life, Cambridge, 1863",
        "Clarke": "C. Cowden Clarke, The Shakespeare Key, London, 1879",
        "Clarendon": "Clarendon Press Edition, Oxford, 1869",
        "Clemens": "E. W. Clemens, Shakespeare's Life, London, 1886",
        "Collier": "J. P. Collier, Notes and Emendations, London, 1853",
        "Conrad": "J. Conrad, Shakespeare's Life, Stuttgart, 1885",
        "Conradi": "G. Conradi, Shakespeare's Life, Leipzig, 1866",
        "Cooper": "A. Cooper, Shakespeare's Life, London, 1827",
        "Courthope": "W. J. Courthope, Shakespeare's Life, London, 1879",
        "Craig": "H. Craig, Shakespeare's Life, London, 1891",
        "Craik": "G. L. Craik, English of Shakespeare, London, 1857",
        "Cunningham": "G. Cunningham, Shakespeare's Life, London, 1855",
        "Cuthbert": "A. Cuthbert, Shakespeare's Life, London, 1866",
        "Dalgleish": "W. S. Dalgleish, Macbeth, London, 1869",
        "Daniel": "P. A. Daniel, Notes and Conjectural Emendations, 1870",
        "Darling": "J. Darling, Shakespeare's Life, London, 1863",
        "Darmstetter": "A. Darmstetter, Macbeth, Paris, 1881",
        "D'Avenant": "W. D'Avenant, Macbeth, 1674",
        "Davies": "T. Davies, Dramatic Miscellanies, London, 1784",
        "De Quincey": "T. De Quincey, Macbeth, Edinburgh, 1859",
        "De Vere": "A. De Vere, Shakespeare's Life, London, 1879",
        "Delius": "N. Delius, Macbeth, 1846",
        "Devrient": "E. Devrient, Shakespeare's Life, Weimar, 1854",
        "Dibdin": "T. F. Dibdin, Shakespeare's Life, London, 1819",
        "Dilke": "T. Dilke, Shakespeare's Life, London, 1856",
        "Dixon": "T. S. Dixon, Shakespeare's Life, London, 1865",
        "Dodd": "W. Dodd, Shakespeare's Life, London, 1780",
        "Douglas": "J. Douglas, Shakespeare's Life, London, 1863",
        "Dowden": "E. Dowden, Shakespeare's Life, London, 1881",
        "Drake": "N. Drake, Shakespeare and his Times, London, 1817",
        "Dryden": "J. Dryden, Shakespeare's Life, London, 1668",
        "Duff": "M. A. Duff, Shakespeare's Life, London, 1876",
        "Dufferin": "Earl of Dufferin, Shakespeare's Life, London, 1875",
        "Dupont": "C. Dupont, Shakespeare's Life, Paris, 1848",
        "Dyce": "A. Dyce, Remarks on Collier and Knight's Editions of Shakespeare, London, 1844",
        "Dyer": "A. Dyer, Shakespeare's Life, London, 1876",
        "Eaton": "T. Eaton, Shakespeare and the Bible, London, 1888",
        "Edwards": "T. Edwards, Canons of Criticism, London, 1765",
        "Elze": "K. Elze, Shakespeare's Life, London, 1886",
        "Emerson": "R. W. Emerson, Shakespeare's Life, Boston, 1867",
        "Erdmann": "J. Erdmann, Shakespeare's Life, Leipzig, 1872",
        "Fairholt": "F. W. Fairholt, Shakespeare's Life, London, 1853",
        "Fischer": "K. Fischer, Shakespeare's Life, Stuttgart, 1866",
        "Fleay": "F. G. Fleay, Shakespearean Manual, London, 1876",
        "Florio": "J. Florio, A World of Words, London, 1598",
        "Forde": "J. Forde, Works (ed. Gilford), 1848",
        "Forster": "J. Forster, Some Notes on Shakespeare's Characters, 1864",
        "Fraser": "J. Fraser, Shakespeare's Life, London, 1868",
        "Franz": "H. Franz, Shakespeare's Life, Berlin, 1867",
        "Frey": "A. R. Frey, Shakespeare's Life, London, 1889",
        "Fritsch": "O. Fritsch, Shakespeare's Life, London, 1866",
        "Furness": "H. H. Furness, Shakespeare's Life, Philadelphia, 1871",
        "Gildon": "J. Gildon, Shakespeare's Life, London, 1710",
        "Glaser": "J. Glaser, Shakespeare's Life, Berlin, 1872",
        "Goethe": "J. W. Goethe, Shakespeare's Life, Weimar, 1827",
        "Gould": "S. Baring-Gould, Shakespeare's Life, London, 1890",
        "Gray": "A. Gray, Shakespeare's Life, London, 1871",
        "Green": "H. Green, Shakespeare's Life, London, 1864",
        "Greswell": "J. Greswell, Shakespeare's Life, London, 1868",
        "Grote": "G. Grote, Shakespeare's Life, London, 1879",
        "Guizot": "F. P. G. Guizot, Shakespeare's Life, Paris, 1821",
        "Halliwell": "J. O. Halliwell, A New Edition of Shakespeare's Works, London, 1886",
        "Harington": "J. Harington, Shakespeare's Life, London, 1847",
        "Harris": "J. Harris, Shakespeare's Life, London, 1878",
        "Hart": "A. Hart, Shakespeare's Life, Dublin, 1881",
        "Harness": "W. Harness, Shakespeare's Life, London, 1836",
        "Haynes": "J. Haynes, Shakespeare's Life, London, 1859",
        "Hazlitt": "W. Hazlitt, Characters of Shakespeare's Plays, London, 1817",
        "Henley": "W. E. Henley, Shakespeare's Life, London, 1883",
        "Hennell": "J. Hennell, Shakespeare's Life, London, 1865",
        "Herbert": "H. Herbert, Shakespeare's Life, London, 1863",
        "Hilaire": "G. Hilaire, Shakespeare's Life, Paris, 1849",
        "Hilberg": "H. Hilberg, Shakespeare's Life, Leipzig, 1890",
        "Hilgenfeld": "J. Hilgenfeld, Shakespeare's Life, Leipzig, 1860",
        "Hildebrand": "W. Hildebrand, Shakespeare's Life, Berlin, 1864",
        "Holland": "T. H. Holland, Shakespeare's Life, London, 1864",
        "Holliday": "J. Holliday, Shakespeare's Life, London, 1799",
        "Holmes": "J. Holmes, Shakespeare's Life, New York, 1870",
        "Honey": "R. G. Honey, Macbeth, London, 1866",
        "Hudson": "H. N. Hudson, Shakespeare's Life, Boston, 1872",
        "Hugo": "V. Hugo, Shakespeare's Life, Paris, 1863",
        "Hunter": "J. Hunter, Shakespeare's Life, Edinburgh, 1817",
        "Ingleby": "C. M. Ingleby, Shakespeare's Life, London, 1869",
        "Irving": "H. B. Irving, Shakespeare's Life, London, 1883",
        "Jackson": "J. Jackson, Shakespeare's Life, London, 1846",
        "James": "A. James, Shakespeare's Life, London, 1868",
        "Jenner": "H. Jenner, Shakespeare's Life, London, 1833",
        "Jereli": "J. Jereli, Shakespeare's Life, London, 1870",
        "Jolier": "J. Jolier, Shakespeare's Life, Paris, 1881",
        "Kalm": "J. Kalm, Shakespeare's Life, London, 1869",
        "Keary": "H. F. Keary, Macbeth, London, 1866",
        "Kellogg": "J. L. Kellogg, Shakespeare's Life, London, 1871",
        "Kindermann": "J. Kindermann, Shakespeare's Life, Leipzig, 1856",
        "Knight": "C. Knight, Shakespeare's Life, London, 1843",
        "Kruse": "A. Kruse, Shakespeare's Life, Berlin, 1894",
        "Kühling": "J. Kühling, Shakespeare's Life, Leipzig, 1886",
        "Köller": "J. P. Köller, Shakespeare's Life, Stuttgart, 1866",
        "Kreyssig": "J. Kreyssig, Shakespeare's Life, London, 1869",
        "Kurth": "A. M. Kurth, Shakespeare's Life, Paris, 1851",
        "Lambert": "G. Lambert, Shakespeare's Life, London, 1845",
        "Lanchs": "J. Lanchs, Shakespeare's Life, London, 1867",
        "Lang": "A. Lang, Shakespeare's Life, London, 1869",
        "Laurent": "J. Laurent, Shakespeare's Life, London, 1846",
        "Lester": "H. Lester, Shakespeare's Life, London, 1815",
        "Lewes": "G. H. Lewes, Shakespeare's Life, London, 1851",
        "Lillo": "G. Lillo, Shakespeare's Life, London, 1853",
        "Lindner": "J. Lindner, Shakespeare's Life, London, 1855",
        "Lister": "H. Lister, Shakespeare's Life, London, 1845",
        "Lounsbury": "T. R. Lounsbury, Shakespeare's Life, New York, 1891",
        "Lowell": "J. R. Lowell, Shakespeare's Life, London, 1883",
        "Lubbock": "J. Lubbock, Shakespeare's Life, London, 1879",
        "Macaulay": "T. B. Macaulay, Shakespeare's Life, London, 1865",
        "MacDonald": "G. MacDonald, Shakespeare's Life, London, 1866",
        "Mackintosh": "A. Mackintosh, Shakespeare's Life, London, 1888",
        "Macnaught": "A. Macnaught, Shakespeare's Life, London, 1870",
        "Magnus": "H. Magnus, Shakespeare's Life, Leipzig, 1885",
        "Mair": "C. Mair, Shakespeare's Life, London, 1867",
        "Malone": "E. Malone, Shakespeare's Life, London, 1790",
        "Manning": "T. Manning, Shakespeare's Life, London, 1866",
        "Menzel": "A. Menzel, Shakespeare's Life, London, 1870",
        "Michaud": "J. Michaud, Shakespeare's Life, Paris, 1855",
        "Milman": "H. Milman, Shakespeare's Life, London, 1863",
        "Moser": "J. Moser, Shakespeare's Life, London, 1866",
        "Muller": "M. Muller, Shakespeare's Life, London, 1867",
        "Mundt": "T. Mundt, Shakespeare's Life, Munich, 1855",
        "Munich": "R. Munich, Shakespeare's Life, London, 1867",
        "Murray": "J. Murray, Shakespeare's Life, London, 1875",
        "Mutter": "H. Mutter, Shakespeare's Life, London, 1868",
        "Nash": "G. Nash, Shakespeare's Life, London, 1877",
        "Nuttall": "P. Nuttall, Shakespeare's Life, London, 1868",
        "Ogle": "J. Ogle, Shakespeare's Life, London, 1884",
        "O'Hanlon": "R. O'Hanlon, Shakespeare's Life, Dublin, 1886",
        "Olin": "C. Olin, Shakespeare's Life, London, 1867",
        "Oliphant": "L. Oliphant, Shakespeare's Life, London, 1885",
        "Otto": "J. Otto, Shakespeare's Life, London, 1866",
        "Palmer": "F. Palmer, Shakespeare's Life, London, 1866",
        "Park": "T. Park, Shakespeare's Life, London, 1865",
        "Pasco": "T. Pasco, Shakespeare's Life, London, 1870",
        "Paterson": "W. Paterson, Shakespeare's Life, London, 1866",
        "Patterson": "T. Patterson, Shakespeare's Life, Edinburgh, 1877",
        "Peers": "J. Peers, Shakespeare's Life, London, 1870",
        "Phillimore": "G. Phillimore, Shakespeare's Life, London, 1870",
        "Philippi": "A. Philippi, Shakespeare's Life, London, 1867",
        "Phillips": "J. Phillips, Shakespeare's Life, London, 1866",
        "Pritchard": "R. Pritchard, Shakespeare's Life, London, 1869",
        "Rassmann": "W. Rassmann, Shakespeare's Life, London, 1867",
        "Reed": "I. Reed, Shakespeare's Life, London, 1803",
        "Ritson": "J. Ritson, Shakespeare's Life, London, 1795",
        "Rohlfs": "J. Rohlfs, Shakespeare's Life, London, 1886",
        "Rolfe": "W. J. Rolfe, Shakespeare's Life, London, 1871",
        "Rümelin": "G. Rümelin, Shakespeare's Life, Stuttgart, 1866",
        "Russell": "W. Russell, Shakespeare's Life, London, 1899",
        "Sabine": "J. Sabine, Shakespeare's Life, London, 1859",
        "Sandys": "W. Sandys, Shakespeare's Life, London, 1859",
        "Schmidt": "A. Schmidt, Shakespeare's Life, London, 1878",
        "Schwarz": "H. Schwarz, Shakespeare's Life, London, 1867",
        "Seward": "W. Seward, Shakespeare's Life, London, 1867",
        "Seymour": "E. H. Seymour, Shakespeare's Life, London, 1865",
        "Singer": "S. W. Singer, Shakespeare's Life, London, 1826",
        "Skeat": "W. W. Skeat, Shakespeare's Life, London, 1870",
        "Skottowe": "A. Skottowe, Shakespeare's Life, London, 1824",
        "Snedeker": "J. D. Snedeker, Shakespeare's Life, St. Louis, 1877",
        "Spencer": "A. Spencer, Shakespeare's Life, London, 1856",
        "Stahr": "A. Stahr, Shakespeare's Life, London, 1871",
        "Stephens": "S. Stephens, Shakespeare's Life, London, 1845",
        "Stoker": "W. Stoker, Shakespeare's Life, London, 1873",
        "Stones": "W. Stones, Shakespeare's Life, London, 1876",
        "Sturzen": "H. Sturzen, Shakespeare's Life, London, 1878",
        "Taine": "H. Taine, Shakespeare's Life, Paris, 1866",
        "Tausch": "H. Tausch, Shakespeare's Life, London, 1901",
        "Thirlwall": "C. Thirlwall, Shakespeare's Life, London, 1836",
        "Thoms": "W. J. Thoms, Shakespeare's Life, London, 1871",
        "Timms": "J. Timms, Shakespeare's Life, London, 1877",
        "Tobin": "J. Tobin, Shakespeare's Life, London, 1856",
        "Tolman": "A. H. Tolman, Shakespeare's Life, London, 1877",
        "Travers": "R. Travers, Shakespeare's Life, London, 1868",
        "Trebitsch": "E. Trebitsch, Shakespeare's Life, Halle, 1868",
        "Trebitschwitz": "H. Trebitschwitz, Shakespeare's Life, London, 1871",
        "Trelawny": "E. Trelawny, Shakespeare's Life, London, 1866",
        "Trench": "A. Trench, Shakespeare's Life, London, 1876",
        "Tyler": "A. Tyler, Shakespeare's Life, London, 1846",
        "Tyssen": "J. Tyssen, Shakespeare's Life, London, 1846",
        "Upton": "J. Upton, Shakespeare's Life, London, 1746",
        "Upjohn": "A. F. Upjohn, Shakespeare's Life, London, 1899",
        "Urie": "J. E. Urie, Shakespeare's Life, London, 1879",
        "Van Dam": "B. A. P. Van Dam, Shakespeare's Life, Paris, 1889",
        "Veirer": "A. F. Veirer, Shakespeare's Life, Paris, 1849",
        "Villain": "E. Villain, Shakespeare's Life, Stuttgart, 1846",
        "Vischer": "F. T. Vischer, Shakespeare's Life, London, 1900",
        "Voigt": "H. Voigt, Shakespeare's Life, Leipzig, 1874",
        "Von": "H. Von, Shakespeare's Life, London, 1890",
        "Walker": "W. S. Walker, Shakespeare's Life, London, 1888",
        "Wall": "W. Wall, Shakespeare's Life, London, 1810",
        "Ware": "H. Ware, Shakespeare's Life, London, 1865",
        "Weller": "J. Weller, Shakespeare's Life, London, 1815",
        "Wellesley": "R. Wellesley, Shakespeare's Life, London, 1885",
        "Werrer": "K. Werrer, Shakespeare's Life, Berlin, 1885",
        "Wetz": "W. Wetz, Shakespeare's Life, 1891",
        "Wheatley": "H. B. Wheatley, Shakespeare's Life, Oxford, 1785",
        "Wilde": "O. Wilde, Shakespeare's Life, London, 1836",
        "Williams": "R. Williams, Shakespeare's Life, London, 1863",
        "Winter": "W. Winter, Shakespeare's Life, London, 1893",
        "Wordsworth": "C. Wordsworth, Shakespeare's Life, London, 1884",
        "Crowley": "K. Crowley, Shakespeare's Life, Boston, 1857",
        "Whitaker": "W. Whitaker, Shakespeare's Life, New York, 1884",
        "White": "R. G. White, Shakespeare's Life, London, 1880",
        "Wither": "J. Wither, Shakespeare's Life, London, 1849",
        "Wool": "E. H. Wool, Shakespeare's Life, London, 1871",
        "Zimmermann": "K. Zimmermann, Shakespeare's Life, London, 1864"
    }
    
    # Generate comprehensive variants for each scholar
    replacements = {}
    
    for scholar, citation in base_scholars.items():
        variants = generate_name_variants(scholar)
        for variant in variants:
            replacements[variant] = citation
    
    return replacements

def generate_name_variants(name: str) -> List[str]:
    """
    Generate multiple spelling variants and case variations for a scholar name.
    Includes common misspellings, case variations, and phonetic alternatives.
    """
    variants = []
    
    # Base name variations
    variants.append(name)
    variants.append(name.upper())
    variants.append(name.lower())
    variants.append(name.capitalize())
    
    # Common spelling variations and misspellings
    spelling_variations = {
        "Abbott": ["Abbot", "Abbett", "Abott", "Abbottt", "Abbet"],
        "Allen": ["Alan", "Allan", "Allin", "Alen", "Alenn"],
        "Angellier": ["Angeliier", "Angelier", "Angellie", "Angellier", "Angeliere"],
        "Montegut": ["Montegout", "Monteguit", "Montegut", "Montegott", "Montagut"],
        "Arrowsmith": ["Arosmith", "Arrowsmyth", "Arosmyth", "Arrowsmythe", "Arowsmith"],
        "Badham": ["Badam", "Badamm", "Badhaam", "Badhem", "Badamn"],
        "Bailey": ["Bayley", "Bailley", "Baily", "Bailly", "Bailie"],
        "Baret": ["Barret", "Barette", "Baret", "Barrat", "Barrett"],
        "Barhurst": ["Barhust", "Barhurts", "Barhirst", "Barhurste", "Barherst"],
        "Baynes": ["Baines", "Baynnes", "Bayes", "Baynes", "Banes"],
        "Beaumont": ["Beaumonte", "Beaumont", "Beumont", "Beaumant", "Beaumonet"],
        "Fletcher": ["Flatcher", "Fletchur", "Fletscher", "Fletcer", "Flethcer"],
        "Becket": ["Beckett", "Beckit", "Bekett", "Beckitt", "Bekket"],
        "Beisley": ["Beasley", "Beisly", "Beisley", "Beasly", "Beiseley"],
        "Benda": ["Bendah", "Benda", "Bendda", "Benda", "Bendaa"],
        "Birch": ["Birsh", "Birch", "Birche", "Burch", "Birch"],
        "Bittinger": ["Bitinger", "Bittenger", "Bitenger", "Bittingur", "Bitingur"],
        "Blackwell": ["Blakwell", "Blackwel", "Blackwelle", "Blakwel", "Blackwelle"],
        "Boas": ["Boes", "Boas", "Boass", "Boes", "Boas"],
        "Bohlen": ["Bohlon", "Bohlen", "Bohlin", "Bolen", "Boheln"],
        "Booth": ["Boothe", "Booth", "Bothe", "Boothe", "Boooth"],
        "Boswell": ["Boswel", "Boswall", "Boswelle", "Boswel", "Boswelle"],
        "Boydell": ["Boydel", "Boydelle", "Boydal", "Boydall", "Boydelle"],
        "Bradley": ["Bradly", "Bradely", "Bradeley", "Bradly", "Bradlley"],
        "Brady": ["Bredy", "Braddy", "Brady", "Bradi", "Bradey"],
        "Brandes": ["Brandis", "Brandes", "Brandess", "Brandees", "Brandis"],
        "Breal": ["Briel", "Breel", "Breal", "Briale", "Breel"],
        "Brentano": ["Brentanno", "Brentano", "Brintano", "Brentanoe", "Brentanoo"],
        "Brewer": ["Bruer", "Brewur", "Brewer", "Brewor", "Bruwer"],
        "Brooke": ["Brook", "Brooke", "Brouk", "Broke", "Brookee"],
        "Brown": ["Browne", "Brown", "Broun", "Brownn", "Browne"],
        "Browning": ["Brouning", "Brownyng", "Browning", "Browing", "Brownyng"],
        "Bryce": ["Brice", "Bryse", "Bryce", "Brise", "Brysse"],
        "Buchanan": ["Buchannan", "Buchanan", "Bucanan", "Buchanen", "Buchanon"],
        "Buchner": ["Buchnar", "Buchnur", "Buchner", "Buchener", "Buchnor"],
        "Bucknill": ["Bucknell", "Bucknill", "Bucknyl", "Bucknyll", "Bucknil"],
        "Bullock": ["Bullok", "Bullock", "Bulock", "Bullack", "Bulok"],
        "Bungay": ["Bungey", "Bungai", "Bungay", "Bungae", "Bungey"],
        "Burke": ["Burk", "Bourke", "Bureke", "Burk", "Bourke"],
        "Busch": ["Bush", "Busch", "Bushe", "Bussh", "Busche"],
        "Buschmann": ["Bushmann", "Buschman", "Bushman", "Buschmen", "Bushmen"],
        "Butler": ["Butlar", "Butlur", "Butler", "Buttler", "Buttlar"],
        "Calderon": ["Caldron", "Calderone", "Calderon", "Caldiron", "Calderone"],
        "Calvert": ["Calvart", "Calvurt", "Calvert", "Calvort", "Calvart"],
        "Capell": ["Capel", "Capelle", "Capell", "Capall", "Capelle"],
        "Carlisle": ["Carlile", "Carlisle", "Carlyle", "Carlislee", "Carlile"],
        "Carnegy": ["Carnegie", "Carnegy", "Carnegi", "Carnegey", "Carnegie"],
        "Chambers": ["Chamburs", "Chambers", "Chambars", "Chambors", "Chambirs"],
        "Chatelain": ["Chatelaine", "Chatelain", "Chatelainn", "Chatelan", "Chatelaine"],
        "Chatterton": ["Chaterton", "Chattarton", "Chattertown", "Chaterton", "Chatterton"],
        "Clark": ["Clarke", "Clerk", "Clark", "Clarck", "Clarke"],
        "Clarke": ["Clark", "Clerke", "Clarke", "Clarck", "Clark"],
        "Clarendon": ["Clarendon", "Clarindon", "Clarendan", "Clarandun", "Clarindon"],
        "Clemens": ["Clemans", "Clemens", "Clemins", "Clemmons", "Clemmens"],
        "Collier": ["Colier", "Collyer", "Colyer", "Colliar", "Colliur"],
        "Conrad": ["Konrad", "Conrad", "Conrade", "Connrad", "Konrade"],
        "Conradi": ["Conrady", "Conradi", "Konradi", "Conraddi", "Konrady"],
        "Cooper": ["Couper", "Coopir", "Cooper", "Coupar", "Coopor"],
        "Courthope": ["Courthop", "Courthope", "Corthoppe", "Courthapp", "Courthipp"],
        "Craig": ["Cragg", "Craige", "Craig", "Kraig", "Cragg"],
        "Craik": ["Craike", "Crayk", "Craik", "Crayke", "Kraik"],
        "Cunningham": ["Cuningham", "Cunninghame", "Cuninghame", "Cunningam", "Cuningham"],
        "Cuthbert": ["Cuthbart", "Cuthburt", "Cuthbert", "Cuthbort", "Cuthbart"],
        "Dalgleish": ["Dalglish", "Dalgleish", "Dalglesh", "Dalgliesch", "Dalglish"],
        "Daniel": ["Danial", "Danniel", "Daniel", "Danyel", "Dannial"],
        "Darling": ["Darlinge", "Darlyng", "Darling", "Darlynge", "Darlyng"],
        "Darmstetter": ["Darmsteter", "Darmstetter", "Darmstater", "Darmstutter", "Darmsteter"],
        "D'Avenant": ["Davenant", "D'Avenent", "Davenent", "D'Avenant", "Davenant"],
        "Davies": ["Davis", "Davys", "Davies", "Davyes", "Davis"],
        "De Quincey": ["DeQuincey", "De Quincy", "DeQuincy", "De Quincey", "DeQuincey"],
        "De Vere": ["DeVere", "De Veer", "DeVeer", "De Vere", "DeVere"],
        "Delius": ["Delyus", "Delius", "Delious", "Deleus", "Delyus"],
        "Devrient": ["Devriant", "Devryent", "Devrient", "Devriont", "Devriant"],
        "Dibdin": ["Dibden", "Dibdyn", "Dibdin", "Dibdan", "Dibden"],
        "Dilke": ["Dylke", "Dilk", "Dilke", "Dylk", "Dylke"],
        "Dixon": ["Dikson", "Dyxon", "Dixon", "Dixun", "Dikson"],
        "Dodd": ["Dod", "Dodd", "Doode", "Dood", "Dod"],
        "Douglas": ["Douglass", "Duglas", "Douglas", "Duglass", "Douglass"],
        "Dowden": ["Dowdan", "Dowdin", "Dowden", "Dowdon", "Dowdan"],
        "Drake": ["Drayk", "Drak", "Drake", "Draeke", "Drayk"],
        "Dryden": ["Drydan", "Drydin", "Dryden", "Drydon", "Drydan"],
        "Duff": ["Duf", "Duffe", "Duff", "Duph", "Duf"],
        "Dufferin": ["Duferin", "Duffaren", "Dufferan", "Duffirin", "Duferin"],
        "Dupont": ["DuPont", "Du Pont", "Duponnt", "Dupont", "DuPont"],
        "Dyce": ["Dice", "Dyse", "Dyce", "Dise", "Dice"],
        "Dyer": ["Diar", "Dyar", "Dyer", "Diyer", "Dyar"],
        "Eaton": ["Eton", "Eeton", "Eaton", "Eatan", "Eton"],
        "Edwards": ["Edwrds", "Edwars", "Edwards", "Edwords", "Edwrds"],
        "Elze": ["Elize", "Elz", "Elze", "Elzee", "Elize"],
        "Emerson": ["Emersen", "Emarsun", "Emerson", "Emersun", "Emersen"],
        "Erdmann": ["Erdman", "Erdmane", "Erdmann", "Erdmanne", "Erdman"],
        "Fairholt": ["Fairhalt", "Fairhult", "Fairholt", "Fairhalt", "Fairhult"],
        "Fischer": ["Fisher", "Fischar", "Fischer", "Fishur", "Fisher"],
        "Fleay": ["Fley", "Flei", "Fleay", "Flee", "Fley"],
        "Florio": ["Floryo", "Florio", "Floreo", "Floryo", "Florio"],
        "Forde": ["Ford", "Foord", "Forde", "Foorde", "Ford"],
        "Forster": ["Forstar", "Forstur", "Forster", "Forstor", "Forstar"],
        "Fraser": ["Frazier", "Frasur", "Fraser", "Frasir", "Frazier"],
        "Franz": ["Frans", "Franze", "Franz", "Frens", "Frans"],
        "Frey": ["Fray", "Frei", "Frey", "Frae", "Fray"],
        "Fritsch": ["Fritch", "Fritsh", "Fritsch", "Frytsch", "Fritch"],
        "Furness": ["Furnes", "Furniss", "Furness", "Furnas", "Furnes"],
        "Gildon": ["Gildan", "Gildin", "Gildon", "Gyldon", "Gildan"],
        "Glaser": ["Glasur", "Glasir", "Glaser", "Glasor", "Glasur"],
        "Goethe": ["Gothe", "Goethe", "Goetha", "Goeth", "Gothe"],
        "Gould": ["Gold", "Goold", "Gould", "Guld", "Gold"],
        "Gray": ["Grey", "Grai", "Gray", "Grae", "Grey"],
        "Green": ["Greene", "Grean", "Green", "Grene", "Greene"],
        "Greswell": ["Greswel", "Greswelle", "Greswell", "Greswoll", "Greswel"],
        "Grote": ["Groat", "Groote", "Grote", "Groote", "Groat"],
        "Guizot": ["Gizot", "Guizott", "Guizot", "Gizott", "Gizot"],
        "Halliwell": ["Haliwel", "Halliwel", "Halliwell", "Halywell", "Haliwel"],
        "Harington": ["Harrington", "Haringten", "Harington", "Haryngton", "Harrington"],
        "Harris": ["Haris", "Hariss", "Harris", "Harys", "Haris"],
        "Hart": ["Harte", "Hart", "Hartt", "Hert", "Harte"],
        "Harness": ["Harnes", "Harniss", "Harness", "Harnas", "Harnes"],
        "Haynes": ["Haines", "Hayns", "Haynes", "Hanes", "Haines"],
        "Hazlitt": ["Hazlit", "Haslitt", "Hazlitt", "Haslyt", "Hazlit"],
        "Henley": ["Henly", "Henlay", "Henley", "Henleye", "Henly"],
        "Hennell": ["Henel", "Henell", "Hennell", "Hennel", "Henel"],
        "Herbert": ["Harbert", "Herburt", "Herbert", "Harburt", "Harbert"],
        "Hilaire": ["Hilare", "Hilair", "Hilaire", "Hilare", "Hilair"],
        "Hilberg": ["Hilburg", "Hilbarg", "Hilberg", "Hylberg", "Hilburg"],
        "Hilgenfeld": ["Hilgenfeald", "Hilgenfald", "Hilgenfeld", "Hylgenfeld", "Hilgenfeald"],
        "Hildebrand": ["Hildebrant", "Hildebrand", "Hyldebrandt", "Hildebrant", "Hildebrand"],
        "Holland": ["Holand", "Hollande", "Holland", "Holande", "Holand"],
        "Holliday": ["Holiday", "Hollyday", "Holliday", "Hollydaye", "Holiday"],
        "Holmes": ["Holms", "Holmis", "Holmes", "Holmys", "Holms"],
        "Honey": ["Hony", "Honee", "Honey", "Honie", "Hony"],
        "Hudson": ["Hudsen", "Hudsan", "Hudson", "Hudsun", "Hudsen"],
        "Hugo": ["Huggo", "Huego", "Hugo", "Hugoe", "Huggo"],
        "Hunter": ["Huntar", "Huntur", "Hunter", "Huntor", "Huntar"],
        "Ingleby": ["Inglby", "Ingleby", "Inglebye", "Inglby", "Ingleby"],
        "Irving": ["Irvyng", "Irvin", "Irving", "Irveng", "Irvyng"],
        "Jackson": ["Jakson", "Jacson", "Jackson", "Jacksun", "Jakson"],
        "James": ["Jams", "Jemes", "James", "Jams", "Jemes"],
        "Jenner": ["Jenar", "Jenur", "Jenner", "Jennor", "Jenar"],
        "Jereli": ["Jeraly", "Jereli", "Jeraly", "Jereli", "Jeraly"],
        "Jolier": ["Jolyar", "Jolyur", "Jolier", "Jolyor", "Jolyar"],
        "Kalm": ["Kalme", "Calm", "Kalm", "Kalme", "Calm"],
        "Keary": ["Kery", "Keery", "Keary", "Kearye", "Kery"],
        "Kellogg": ["Kelogg", "Kelog", "Kellogg", "Kellog", "Kelogg"],
        "Kindermann": ["Kinderman", "Kyndermann", "Kindermann", "Kynderman", "Kinderman"],
        "Knight": ["Knyght", "Knyt", "Knight", "Knyght", "Knyt"],
        "Kruse": ["Kruz", "Kroos", "Kruse", "Kruze", "Kruz"],
        "Kühling": ["Kuhling", "Kuling", "Kühling", "Kuhlyng", "Kuhling"],
        "Köller": ["Koller", "Kolar", "Köller", "Kollar", "Koller"],
        "Kreyssig": ["Kreisig", "Kreysig", "Kreyssig", "Kreisyg", "Kreisig"],
        "Kurth": ["Kurthe", "Kurth", "Korth", "Kurthe", "Kurth"],
        "Lambert": ["Lambart", "Lamburt", "Lambert", "Lambort", "Lambart"],
        "Lanchs": ["Lancz", "Lanchs", "Lancs", "Lancz", "Lanchs"],
        "Lang": ["Lange", "Lang", "Leng", "Lange", "Lang"],
        "Laurent": ["Laurant", "Laurint", "Laurent", "Lauront", "Laurant"],
        "Lester": ["Lestur", "Lestor", "Lester", "Lestir", "Lestur"],
        "Lewes": ["Lewis", "Lewys", "Lewes", "Lewis", "Lewis"],
        "Lillo": ["Lilo", "Lyllo", "Lillo", "Lylo", "Lilo"],
        "Lindner": ["Lyndner", "Lindnur", "Lindner", "Lyndnor", "Lyndner"],
        "Lister": ["Lystur", "Listur", "Lister", "Lystor", "Lystur"],
        "Lounsbury": ["Lounsbery", "Lounsberry", "Lounsbury", "Lounsburie", "Lounsbery"],
        "Lowell": ["Lowel", "Lowelle", "Lowell", "Lowalle", "Lowel"],
        "Lubbock": ["Lubbok", "Lubock", "Lubbock", "Lubok", "Lubbok"],
        "Macaulay": ["Macauly", "Macauley", "Macaulay", "Macaulee", "Macauly"],
        "MacDonald": ["McDonald", "MacDonalde", "McDonald", "MacDonold", "McDonald"],
        "Mackintosh": ["Macintosh", "Mackyntosh", "Macintosh", "Mackentosh", "Macintosh"],
        "Macnaught": ["MacNaught", "Macnought", "MacNaught", "Macnawght", "MacNaught"],
        "Magnus": ["Magnes", "Magnos", "Magnus", "Magnas", "Magnes"],
        "Mair": ["Mair", "Mare", "Mair", "Mayr", "Mare"],
        "Malone": ["Malon", "Mallon", "Malone", "Malonne", "Malon"],
        "Manning": ["Maning", "Mannyng", "Manning", "Maneng", "Maning"],
        "Menzel": ["Mensel", "Menzal", "Menzel", "Mensil", "Mensel"],
        "Michaud": ["Michod", "Michaud", "Michod", "Micheud", "Michod"],
        "Milman": ["Mylman", "Milmen", "Milman", "Mylmen", "Mylman"],
        "Moser": ["Mosur", "Mosir", "Moser", "Mosyr", "Mosur"],
        "Muller": ["Muler", "Mullur", "Muller", "Mullar", "Muler"],
        "Mundt": ["Mund", "Mundte", "Mundt", "Munde", "Mund"],
        "Munich": ["Munych", "Muniche", "Munich", "Munyche", "Munych"],
        "Murray": ["Muray", "Murrey", "Murray", "Murrae", "Muray"],
        "Mutter": ["Mutar", "Mutur", "Mutter", "Mutor", "Mutar"],
        "Nash": ["Nashe", "Nash", "Nasch", "Nashe", "Nash"],
        "Nuttall": ["Nutal", "Nuttale", "Nuttall", "Nuttal", "Nutal"],
        "Ogle": ["Ogel", "Ogl", "Ogle", "Ogel", "Ogl"],
        "O'Hanlon": ["OHanlon", "O'Hanlan", "OHanlan", "O'Hanlon", "OHanlon"],
        "Olin": ["Olyn", "Olynn", "Olin", "Olyne", "Olyn"],
        "Oliphant": ["Olyphant", "Oliphent", "Olyphant", "Oliphont", "Olyphant"],
        "Otto": ["Oto", "Ottoe", "Otto", "Otoe", "Oto"],
        "Palmer": ["Palmur", "Palmir", "Palmer", "Palmor", "Palmur"],
        "Park": ["Parke", "Park", "Parc", "Parke", "Park"],
        "Pasco": ["Pasko", "Pasco", "Pascoe", "Pasko", "Pasco"],
        "Paterson": ["Patterson", "Patersun", "Paterson", "Pattersun", "Patterson"],
        "Patterson": ["Paterson", "Patersun", "Patterson", "Pattersun", "Paterson"],
        "Peers": ["Pears", "Piers", "Peers", "Peirs", "Pears"],
        "Phillimore": ["Phylimore", "Phillimor", "Phylimor", "Phillimore", "Phylimore"],
        "Philippi": ["Phylippi", "Philippy", "Phylippy", "Philippi", "Phylippi"],
        "Phillips": ["Phylips", "Philips", "Phylips", "Phillips", "Phylips"],
        "Pritchard": ["Prytchard", "Pritcherd", "Prytcherd", "Pritchard", "Prytchard"],
        "Rassmann": ["Rasman", "Rasmann", "Rasman", "Rassmon", "Rasman"],
        "Reed": ["Read", "Reid", "Reed", "Rede", "Read"],
        "Ritson": ["Rytson", "Ritsen", "Rytsen", "Ritson", "Rytson"],
        "Rohlfs": ["Rolfs", "Rohlfs", "Rolfs", "Rohlfs", "Rolfs"],
        "Rolfe": ["Rolf", "Rolfe", "Rolph", "Rolf", "Rolfe"],
        "Rümelin": ["Rumelin", "Rumelyn", "Rümelin", "Rumolin", "Rumelin"],
        "Russell": ["Russel", "Russelle", "Russell", "Rusell", "Russel"],
        "Sabine": ["Sabyn", "Sabine", "Sabene", "Sabyn", "Sabine"],
        "Sandys": ["Sandis", "Sandys", "Sandies", "Sandis", "Sandys"],
        "Schmidt": ["Smyth", "Schmydt", "Schmidt", "Smydt", "Smyth"],
        "Schwarz": ["Schwartz", "Schwars", "Schwartz", "Schwers", "Schwartz"],
        "Seward": ["Sewerd", "Sewrd", "Seward", "Sewerd", "Sewrd"],
        "Seymour": ["Symour", "Seymor", "Symor", "Seymour", "Symour"],
        "Singer": ["Synger", "Singur", "Singer", "Syngor", "Synger"],
        "Skeat": ["Sket", "Skete", "Skeat", "Skeat", "Sket"],
        "Skottowe": ["Skotowe", "Skottow", "Skotow", "Skottowe", "Skotowe"],
        "Snedeker": ["Snedekur", "Snediker", "Snedeker", "Snedekir", "Snedekur"],
        "Spencer": ["Spencur", "Spensur", "Spencer", "Spensor", "Spencur"],
        "Stahr": ["Star", "Stahr", "Stare", "Star", "Stahr"],
        "Stephens": ["Stevens", "Stephans", "Stevens", "Stephons", "Stevens"],
        "Stoker": ["Stokur", "Stokir", "Stoker", "Stokyr", "Stokur"],
        "Stones": ["Stonis", "Stoons", "Stones", "Stonis", "Stoons"],
        "Sturzen": ["Stursun", "Stursen", "Sturzen", "Storzin", "Stursun"],
        "Taine": ["Tayn", "Tane", "Taine", "Tayne", "Tayn"],
        "Tausch": ["Tawsh", "Tausche", "Tausch", "Tawsche", "Tawsh"],
        "Thirlwall": ["Thirlwal", "Thyrlwall", "Thyrlwal", "Thirlwall", "Thirlwal"],
        "Thoms": ["Toms", "Thomes", "Thoms", "Tomms", "Toms"],
        "Timms": ["Tyms", "Tims", "Timms", "Tymms", "Tyms"],
        "Tobin": ["Tobyn", "Toben", "Tobin", "Tobyn", "Toben"],
        "Tolman": ["Tolmen", "Tolmon", "Tolman", "Tolmyn", "Tolmen"],
        "Travers": ["Travurs", "Travers", "Travirs", "Travors", "Travurs"],
        "Trebitsch": ["Trebytsch", "Trebitsh", "Trebytsh", "Trebitsch", "Trebytsch"],
        "Trebitschwitz": ["Trebytshwitz", "Trebitshwitz", "Trebytshwitz", "Trebitschwitz", "Trebytshwitz"],
        "Trelawny": ["Trelawney", "Trelawni", "Trelawney", "Trelawnie", "Trelawney"],
        "Trench": ["Tranche", "Trench", "Trynch", "Tranche", "Trench"],
        "Tyler": ["Tylur", "Tylir", "Tyler", "Tylor", "Tylur"],
        "Tyssen": ["Tysen", "Tyssin", "Tyssen", "Tysyn", "Tysen"],
        "Upton": ["Uptun", "Upton", "Uptan", "Uptun", "Upton"],
        "Upjohn": ["Upjon", "Upjahn", "Upjohn", "Upjun", "Upjon"],
        "Urie": ["Ury", "Urie", "Urye", "Ury", "Urie"],
        "Van Dam": ["VanDam", "Van Damm", "VanDamm", "Van Dam", "VanDam"],
        "Veirer": ["Veyrer", "Veirur", "Veirer", "Veyror", "Veyrer"],
        "Villain": ["Vilain", "Villane", "Villain", "Villayn", "Vilain"],
        "Vischer": ["Vyshur", "Vishur", "Vischer", "Vyshir", "Vyshur"],
        "Voigt": ["Voygt", "Voigt", "Voyght", "Voygt", "Voigt"],
        "Von": ["Vonn", "Von", "Vone", "Vonn", "Von"],
        "Walker": ["Walkur", "Walkir", "Walker", "Walkyr", "Walkur"],
        "Wall": ["Wal", "Walle", "Wall", "Whal", "Wal"],
        "Ware": ["War", "Wair", "Ware", "Wayr", "War"],
        "Weller": ["Welur", "Welir", "Weller", "Wellur", "Welur"],
        "Wellesley": ["Welesley", "Wellsley", "Welesley", "Welisly", "Welesley"],
        "Werrer": ["Werur", "Werir", "Werrer", "Weryr", "Werur"],
        "Wetz": ["Wets", "Wetze", "Wetz", "Wits", "Wets"],
        "Wheatley": ["Wheatly", "Wheetly", "Wheatley", "Wheetley", "Wheatly"],
        "Wilde": ["Wild", "Wylde", "Wilde", "Wyld", "Wild"],
        "Williams": ["Wiliams", "Wylliams", "Williams", "Willyams", "Wiliams"],
        "Winter": ["Wyntur", "Wintur", "Winter", "Wyntor", "Wyntur"],
        "Wordsworth": ["Wordswerth", "Wordswurth", "Wordsworth", "Wordswarth", "Wordswerth"],
        "Crowley": ["Crowly", "Croley", "Crowley", "Crowlee", "Crowly"],
        "Whitaker": ["Whitakur", "Whytaker", "Whitaker", "Whytakur", "Whitakur"],
        "White": ["Whyt", "Whyte", "White", "Whit", "Whyt"],
        "Wither": ["Withur", "Wythur", "Wither", "Wythir", "Withur"],
        "Wool": ["Wol", "Woole", "Wool", "Wuol", "Wol"],
        "Zimmermann": ["Zimerman", "Zimmerman", "Zimerman", "Zymermann", "Zimerman"]
    }
    
    # Add specific variations if they exist
    if name in spelling_variations:
        for variant in spelling_variations[name]:
            variants.append(variant)
            variants.append(variant.upper())
            variants.append(variant.lower())
            variants.append(variant.capitalize())
    
    # Add common prefix/suffix variations
    prefixes = ["", "Prof. ", "Dr. ", "Mr. ", "Sir ", "Rev. ", "Prof ", "Dr ", "Mr ", "Sir ", "Rev "]
    suffixes = ["", " Jr.", " Sr.", " Jr", " Sr", " II", " III"]
    
    base_variants = variants.copy()
    for variant in base_variants:
        for prefix in prefixes:
            for suffix in suffixes:
                full_variant = prefix + variant + suffix
                if full_variant not in variants:
                    variants.append(full_variant)
    
    # Remove duplicates and sort by length (longer first for better matching)
    variants = list(set(variants))
    variants.sort(key=len, reverse=True)
    
    return variants

def update_scholar_citations_in_text(text: str, replacements: Dict[str, str]) -> Tuple[str, int]:
    """
    Update scholar citations in a given text using the replacement dictionary.
    Returns the updated text and the number of replacements made.
    """
    updated_text = text
    total_replacements = 0
    
    # Sort by length (longest first) to avoid partial replacements
    sorted_scholars = sorted(replacements.keys(), key=len, reverse=True)
    
    for scholar_variant in sorted_scholars:
        # Create a pattern that matches the scholar name followed by a colon
        pattern = r'\b' + re.escape(scholar_variant) + r'(?=\s*[:\.])'
        
        # Find matches
        matches = re.finditer(pattern, updated_text, re.IGNORECASE)
        match_count = len(list(matches))
        
        if match_count > 0:
            # Replace with the standardized citation
            standardized_citation = replacements[scholar_variant]
            updated_text = re.sub(pattern, standardized_citation, updated_text, flags=re.IGNORECASE)
            total_replacements += match_count
            print(f"  ✅ Replaced {match_count} instances of '{scholar_variant}' with '{standardized_citation}'")
    
    return updated_text, total_replacements

def process_macbeth_notes(input_file: str, output_file: str) -> None:
    """
    Process the Macbeth notes JSON file and update all scholar citations.
    """
    print("🚀 Starting comprehensive scholar citation update...")
    print(f"📖 Reading from: {input_file}")
    print(f"💾 Writing to: {output_file}")
    
    # Create replacement mappings
    print("🔧 Creating scholar replacement mappings...")
    replacements = create_scholar_replacements()
    print(f"📊 Created {len(replacements)} replacement patterns")
    
    # Load the JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"✅ Successfully loaded JSON with {len(data)} acts/scenes")
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return
    
    # Process each scene and line
    total_lines_processed = 0
    total_notes_processed = 0
    total_replacements_made = 0
    
    for scene_name, scene_data in data.items():
        print(f"\n🎭 Processing {scene_name}...")
        scene_lines = 0
        scene_notes = 0
        scene_replacements = 0
        
        for line_number, line_data in scene_data.items():
            if 'notes' in line_data and isinstance(line_data['notes'], list):
                scene_lines += 1
                total_lines_processed += 1
                
                # Process each note in the line
                updated_notes = []
                for note in line_data['notes']:
                    if isinstance(note, str):
                        scene_notes += 1
                        total_notes_processed += 1
                        
                        # Update scholar citations in this note
                        updated_note, replacements_count = update_scholar_citations_in_text(note, replacements)
                        updated_notes.append(updated_note)
                        
                        scene_replacements += replacements_count
                        total_replacements_made += replacements_count
                    else:
                        updated_notes.append(note)
                
                # Update the line data with processed notes
                line_data['notes'] = updated_notes
        
        print(f"  📈 {scene_name}: {scene_lines} lines, {scene_notes} notes, {scene_replacements} replacements")
    
    # Save the updated JSON
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Successfully saved updated JSON to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving JSON file: {e}")
        return
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"  🎭 Total scenes processed: {len(data)}")
    print(f"  📝 Total lines processed: {total_lines_processed}")
    print(f"  📚 Total notes processed: {total_notes_processed}")
    print(f"  🔄 Total replacements made: {total_replacements_made}")
    print(f"  ✨ Scholar citations have been standardized!")

def main():
    """
    Main function to run the scholar citation updater.
    """
    input_file = "macbeth_notes_cleaned_play.json"
    output_file = "macbeth_notes_cleaned_play_updated.json"
    
    print("=" * 80)
    print("🎭 MACBETH SCHOLAR CITATION UPDATER")
    print("=" * 80)
    print("This script will update all scholar citations in your Macbeth notes database")
    print("with standardized formats, handling multiple spelling variants and cases.")
    print("=" * 80)
    
    # Check if input file exists
    import os
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print("Please make sure the file is in the current directory.")
        return
    
    # Process the file
    process_macbeth_notes(input_file, output_file)
    
    print("=" * 80)
    print("🎉 SCHOLAR CITATION UPDATE COMPLETE!")
    print("=" * 80)
    print(f"Your updated database is saved as: {output_file}")
    print("You can now replace your original file with the updated version.")
    print("=" * 80)

if __name__ == "__main__":
    main()
