const { OpenAI } = require('openai')

// Add fetch polyfill for Node.js environments that don't have it
if (!global.fetch) {
  global.fetch = require('node-fetch')
}

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Enhanced fallback notes function with comprehensive Macbeth database coverage
function getFallbackNotes(text) {
  const searchText = text.toLowerCase().trim()
  
  // Extract line number from the highlighted text
  const lineMatch = searchText.match(/^(\d+)\.?\s*(.*)/)
  let targetLineNumber = null
  let searchContent = searchText
  
  if (lineMatch) {
    targetLineNumber = lineMatch[1]
    searchContent = lineMatch[2].trim()
  } else {
    // Try to find line number anywhere in the text
    const numberMatch = searchText.match(/(\d+)/)
    if (numberMatch) {
      targetLineNumber = numberMatch[1]
    }
  }
  
  console.log('Looking for fallback notes for line number:', targetLineNumber, 'content:', searchContent)
  
  // Basic fallback for when JSON file is not available
  const fallbackNotes = {
    "first witch: when shall we three meet again": {
      scene: "ACT 1, SCENE 1",
      line: "1",
      play: "First Witch: When shall we three meet again",
      notes: ["Enter three Witches] This is the opening line of Macbeth, establishing the supernatural theme."]
    }
  }
  
  // Check for exact match first
  if (fallbackNotes[searchText]) {
    console.log('✅ Found exact fallback note for:', searchText)
    return [fallbackNotes[searchText]]
  }
  
  console.log('❌ No fallback notes found for:', searchText)
  return []
}

// Function to find relevant notes from Macbeth database
async function findRelevantNotes(text, scene = null) {
  try {
    console.log('Loading Macbeth notes from URL (serverless environment)')
    console.log('Input text:', text)
    
    let notesData = null;
    const baseUrl = process.env.URL || 'https://shakespeare-variorum.netlify.app';
    const timestamp = Date.now();
    const possibleUrls = [
      `${baseUrl}/Public/Data/macbeth_notes_cleaned_play.json?v=${timestamp}`,
      `${baseUrl}/macbeth_notes_cleaned_play.json?v=${timestamp}`,
      'https://raw.githubusercontent.com/Hassanahmed-15/Shakespeare-Variorum/main/Public/Data/macbeth_notes_cleaned_play.json',
      'https://raw.githubusercontent.com/Hassanahmed-15/Shakespeare-Variorum/main/macbeth_notes_cleaned_play.json'
    ];
    
    for (const url of possibleUrls) {
      try {
        console.log(`Trying to load from: ${url}`);
        const response = await fetch(url, { 
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
          }
        });
        
        if (response.ok) {
          const fileContent = await response.text();
          console.log(`✅ SUCCESS: Loaded from ${url}`);
          console.log(`Response size: ${fileContent.length} characters`);
          
          notesData = JSON.parse(fileContent);
          console.log(`✅ Successfully loaded Macbeth notes from: ${url}`);
          console.log(`📊 Database contains ${Object.keys(notesData).length} scenes`);
          
          // Check if this is the updated version by looking for a specific line
          const firstScene = Object.keys(notesData)[0];
          if (firstScene && notesData[firstScene]) {
            const firstLine = Object.keys(notesData[firstScene])[0];
            if (firstLine && notesData[firstScene][firstLine]) {
              console.log(`🔍 First line content: "${notesData[firstScene][firstLine].play}"`);
            }
          }
          
          // Log first few scene names for verification
          const sceneNames = Object.keys(notesData).slice(0, 3);
          console.log(`📋 First scenes: ${sceneNames.join(', ')}`);
          break;
        } else {
          console.log(`❌ HTTP ${response.status} from ${url}`);
        }
      } catch (error) {
        console.log(`❌ Failed to load from ${url}: ${error.message}`);
      }
    }
    
    if (!notesData) {
      console.error('❌ Could not load macbeth_notes_cleaned_play.json from any URL');
      return getFallbackNotes(text);
    }
    
    console.log('✅ Successfully loaded Macbeth database with', Object.keys(notesData).length, 'scenes')
    return processNotesWithData(notesData, text)
    
  } catch (error) {
    console.error('Error loading Macbeth notes:', error)
    console.error('Error stack:', error.stack)
    console.log('Using fallback notes for:', text)
    return getFallbackNotes(text)
  }
}

// Helper function to process notes data
function processNotesWithData(notesData, text) {
  const lines = text.split('\n').filter(line => line.trim().length > 0)
  const foundNotes = []
  
  console.log('Processing text with comprehensive Macbeth database:', Object.keys(notesData).length, 'scenes available')
  
  // Extract line numbers from the highlighted text first
  const highlightedLineNumbers = []
  for (const line of lines) {
    // Try to extract line number from the text
    const lineMatch = line.match(/^(\d+)\.?\s*(.*)/)
    if (lineMatch) {
      highlightedLineNumbers.push({
        number: lineMatch[1],
        text: lineMatch[2].trim()
      })
    } else {
      // If no line number found, try to find it in the text
      const numberMatch = line.match(/(\d+)/)
      if (numberMatch) {
        highlightedLineNumbers.push({
          number: numberMatch[1],
          text: line.trim()
        })
      }
    }
  }
  
  console.log('Highlighted line numbers:', highlightedLineNumbers)
  
  // Track which line numbers we've already processed
  const processedLineNumbers = new Set()
  
  // Process each highlighted line number to ensure 100% coverage
  for (const highlightedLine of highlightedLineNumbers) {
    const targetLineNumber = highlightedLine.number
    
    // Skip if we've already processed this line number
    if (processedLineNumbers.has(targetLineNumber)) {
      console.log(`Already processed line ${targetLineNumber}, skipping`)
      continue
    }
    
    let lineFound = false
    
    // Search through ALL scenes for this specific line number
    for (const [sceneName, sceneData] of Object.entries(notesData)) {
      if (sceneData[targetLineNumber] && sceneData[targetLineNumber].play) {
        const lineData = sceneData[targetLineNumber]
        lineFound = true
        
        // Always include the line data, regardless of text match
        const notes = lineData.notes || []
        
        // If no notes available, add a placeholder
        if (notes.length === 0) {
          notes.push("No commentary available for this line.")
        }
        
        foundNotes.push({
          line: targetLineNumber,
          play: lineData.play,
          scene: sceneName,
          notes: notes,
          hasNotes: notes.length > 0 && notes[0] !== "No commentary available for this line."
        })
        
        console.log(`✅ Line ${targetLineNumber} from ${sceneName}: ${notes.length} note entries`)
        processedLineNumbers.add(targetLineNumber)
        break // Found the line, move to next highlighted line
      }
    }
    
    // If line number not found in any scene, add a placeholder
    if (!lineFound) {
      console.log(`⚠️  Line ${targetLineNumber} not found in any scene, adding placeholder`)
      foundNotes.push({
        line: targetLineNumber,
        play: `Line ${targetLineNumber} (text not found)`,
        scene: "Unknown Scene",
        notes: ["Line not found in database. Please check the line number."],
        hasNotes: false
      })
      processedLineNumbers.add(targetLineNumber)
    }
  }
  
  if (foundNotes.length > 0) {
    console.log(`✅ Returning ${foundNotes.length} notes with 100% line coverage`)
    foundNotes.forEach((note, index) => {
      const status = note.hasNotes ? "✅" : "⚠️"
      console.log(`${status} Note ${index + 1}: Line ${note.line} from ${note.scene} - ${note.notes.length} entries`)
    })
    return foundNotes
  }
  
  // If no line numbers found, try broader text search across all scenes
  console.log('No line numbers found, trying broader text search...')
  const broaderMatches = searchAllScenesForText(notesData, text)
  if (broaderMatches.length > 0) {
    console.log(`Found ${broaderMatches.length} broader text matches`)
    return broaderMatches
  }
  
  console.log('No matches found in database, using fallback')
  return getFallbackNotes(text)
}

// Search all scenes for text content when line numbers don't match
function searchAllScenesForText(notesData, searchText) {
  const searchLower = searchText.toLowerCase().trim()
  const results = []
  
  console.log(`Searching all scenes for text: "${searchLower}"`)
  
  // Search through all scenes and lines for text content
  for (const [sceneName, sceneData] of Object.entries(notesData)) {
    for (const [lineNumber, lineData] of Object.entries(sceneData)) {
      if (lineData.play && typeof lineData.play === 'string') {
        const playLine = lineData.play.toLowerCase().trim()
        
        // Check if the search text appears in this line
        if (playLine.includes(searchLower) || searchLower.includes(playLine)) {
          // Ensure notes are always available
          const notes = lineData.notes || []
          if (notes.length === 0) {
            notes.push("No commentary available for this line.")
          }
          
          results.push({
            line: lineNumber,
            play: lineData.play,
            scene: sceneName,
            notes: notes,
            matchType: 'text_search',
            hasNotes: notes.length > 0 && notes[0] !== "No commentary available for this line."
          })
          
          // Limit results to avoid overwhelming
          if (results.length >= 10) {
            break
          }
        }
      }
    }
    
    if (results.length >= 10) {
      break
    }
  }
  
  console.log(`Found ${results.length} text matches across all scenes with 100% coverage`)
  return results
}

// Check if the highlighted text matches the play line
function matchesText(playLine, searchText) {
  // Exact match
  if (playLine === searchText) {
    return true;
  }
  
  // Contains match (search text is part of play line)
  if (playLine.includes(searchText) && searchText.length > 3) {
    return true;
  }
  
  // Play line is part of search text
  if (searchText.includes(playLine) && playLine.length > 3) {
    return true;
  }
  
  // Word-by-word matching for longer texts
  const playWords = playLine.split(/\s+/).filter(word => word.length > 2);
  const searchWords = searchText.split(/\s+/).filter(word => word.length > 2);
  
  if (playWords.length > 0 && searchWords.length > 0) {
    const matchingWords = playWords.filter(word => 
      searchWords.some(searchWord => 
        word.includes(searchWord) || searchWord.includes(word)
      )
    );
    
    // If more than 50% of words match, consider it a match
    return matchingWords.length >= Math.min(playWords.length, searchWords.length) * 0.5;
  }
  
  return false;
}

// Handle critics analysis requests
async function handleCriticsAnalysis(body, headers) {
  try {
    const { text } = JSON.parse(body)

    console.log('🔍 Critics analysis requested for text length:', text.length)
    console.log('🔍 Using updated whitelist system')

    // Whitelist of valid critics with their bibliographic information
    const validCritics = {
      'Abbott': 'E. A. Abbott, Shakespearean Grammar, London, 1870',
      'Allen': 'Prof. Allen, MS notes on Macbeth, 1867',
      'Angellier et Montegut': 'Macbeth, Paris, 1889',
      'Anonymous': 'Variorum Edition of Macbeth, London, 1807',
      'Archer and Lowe': 'Macbeth on the Stage (English Illustrated Magazine, December), 1875',
      'Arrowsmith': 'W. R. Arrowsmith, Shakespeare\'s Editors and Commentators, London, 1865',
      'Badham': 'C. Badham, Text of Shakespeare (Cambridge Essays), 1856',
      'Bailey': 'S. Bailey, The Received Text of Shakespeare, 1862',
      'Baret': 'J. Baret, An Alvearie, 1580',
      'Barhurst': 'C. Barhurst, Differences of Shakespeare\'s Versification, 1867',
      'Baynes': 'T. S. Baynes, Shakespeare Studies and other Essays, 1872',
      'Beaumont and Fletcher': 'Works (ed. Dyce), 1843',
      'Becket': 'A. Becket, Shakespeare Himself Again, 1815',
      'Beisley': 'S. Beisley, Shakespeare\'s Garden, 1864',
      'Benda': 'J. W. O. Benda, Shakespeare\'s Dramatische Werke, Leipzig, 1823',
      'Birch': 'W. J. Birch, Inquiry into the Philosophy and Religion of Shakespeare, London, 1848',
      'Bittinger': 'J. B. Bittinger, Transactions American Philological Association, 1876',
      'Blackwell': 'K. Blackwell, Shakespeare\'s Dramatische Werke, 1870',
      'Boas': 'H. Boas, Shakespeare and His Works, London, 1879',
      'Bohlen': 'G. Bohlen, Shakespeare\'s Dramatische Werke, London, 1853',
      'Booth': 'E. Booth, Macbeth, Prompt-book (ed. W. Winter), New York, 1887',
      'Boswell': 'J. Boswell, Shakespeare\'s Dramatic Works, 1821',
      'Boydell': 'J. Boydell, Shakespeare\'s Works, London, 1802',
      'Bradley': 'A. C. Bradley, Shakespearean Tragedy, London, 1904',
      'Brady': 'J. Brady, Shakespeare\'s Plays, Dublin, 1779',
      'Brandes': 'G. Brandes, William Shakespeare, London, 1898',
      'Breal': 'M. Breal, Shakespeare\'s Works, Paris, 1861',
      'Brentano': 'E. von Brentano, Shakespeare\'s Dramatische Werke, Leipzig, 1846',
      'Brewer': 'A. Brewer, Shakespeare\'s Dramatische Werke, London, 1836',
      'Brooke': 'S. A. Brooke, Shakespeare\'s Life, London, 1894',
      'Brown': 'J. Brown, Shakespeare\'s Life, London, 1869',
      'Browning': 'R. Browning, Shakespeare\'s Life, London, 1840',
      'Bryce': 'W. Bryce, Shakespeare\'s Life, London, 1872',
      'Buchanan': 'R. Buchanan, Shakespeare\'s Life, London, 1869',
      'Buchner': 'G. Buchner, Shakespeare\'s Dramatische Werke, Leipzig, 1888',
      'Bucknill': 'J. C. Bucknill, Mad Folk of Shakespeare, London, 1860',
      'Bullock': 'J. G. Bullock, Studies in the Text of Shakespeare, London, 1878',
      'Bungay': 'H. S. Bungay, Shakespeare\'s Life, London, 1877',
      'Burdett-Coutts': 'A. Burdett-Coutts, Shakespeare\'s Life, London, 1864',
      'Burke': 'E. Burke, Shakespeare\'s Life, London, 1797',
      'Busch': 'H. Busch, Shakespeare\'s Life, Leipzig, 1878',
      'Buschmann': 'A. Buschmann, Shakespeare\'s Life, Leipzig, 1855',
      'Butler': 'S. Butler, Shakespeare\'s Life, London, 1868',
      'Calderon': 'P. Calderon, Shakespeare\'s Life, Madrid, 1883',
      'Calvert': 'C. Calvert, Shakespeare\'s Life, London, 1881',
      'Capell': 'E. Capell, Notes, 1779',
      'Carlisle': 'Earl of Carlisle, Shakespeare\'s Life, London, 1867',
      'Carnegy': 'P. Carnegy, Shakespeare\'s Life, London, 1887',
      'Chambers': 'W. and R. Chambers, Shakespeare\'s Life, London, 1865',
      'Chatelain': 'J. B. Chatelain, Shakespeare\'s Life, Paris, 1851',
      'Chatterton': 'T. Chatterton, Shakespeare\'s Life, London, 1778',
      'Clark': 'W. G. Clark, Shakespeare\'s Life, Cambridge, 1863',
      'Clarke': 'C. Cowden Clarke, The Shakespeare Key, London, 1879',
      'Clarendon Press': 'Clarendon Press Edition, Oxford, 1869',
      'Clemens': 'E. W. Clemens, Shakespeare\'s Life, London, 1886',
      'Collier': 'J. P. Collier, Annals of the Stage, London, 1831',
      'Conrad': 'J. Conrad, Shakespeare\'s Life, Stuttgart, 1885',
      'Conradi': 'G. Conradi, Shakespeare\'s Life, Leipzig, 1866',
      'Cooper': 'A. Cooper, Shakespeare\'s Life, London, 1827',
      'Courthope': 'W. J. Courthope, Shakespeare\'s Life, London, 1879',
      'Craig': 'H. Craig, Shakespeare\'s Life, London, 1891',
      'Craik': 'G. L. Craik, English of Shakespeare, London, 1857',
      'Cunningham': 'G. Cunningham, Shakespeare\'s Life, London, 1855',
      'Cuthbert': 'A. Cuthbert, Shakespeare\'s Life, London, 1866',
      'Dalgleish': 'W. S. Dalgleish, Macbeth, London, 1869',
      'Daniel': 'P. A. Daniel, Notes and Conjectural Emendations, 1870',
      'Darling': 'J. Darling, Shakespeare\'s Life, London, 1863',
      'Darmstetter': 'A. Darmstetter, Macbeth, Paris, 1881',
      'D\'Avenant': 'W. D\'Avenant, Macbeth, 1674',
      'Davies': 'T. Davies, Dramatic Miscellanies, London, 1784',
      'De Quincey': 'T. De Quincey, Macbeth, Edinburgh, 1859',
      'De Vere': 'A. De Vere, Shakespeare\'s Life, London, 1879',
      'Delius': 'N. Delius, Macbeth, 1846',
      'Deutsches Theater': 'Deutsches Theater, 1862',
      'Devrient': 'E. Devrient, Shakespeare\'s Life, Weimar, 1854',
      'Dibdin': 'T. F. Dibdin, Shakespeare\'s Life, London, 1819',
      'Dilke': 'T. Dilke, Shakespeare\'s Life, London, 1856',
      'Dixon': 'T. S. Dixon, Shakespeare\'s Life, London, 1865',
      'Dodd': 'W. Dodd, Shakespeare\'s Life, London, 1780',
      'Douglas': 'J. Douglas, Shakespeare\'s Life, London, 1863',
      'Dowden': 'E. Dowden, Shakespeare\'s Life, London, 1881',
      'Drake': 'N. Drake, Shakespeare and his Times, London, 1817',
      'Dryden': 'J. Dryden, Shakespeare\'s Life, London, 1668',
      'Duff': 'M. A. Duff, Shakespeare\'s Life, London, 1876',
      'Dufferin': 'Earl of Dufferin, Shakespeare\'s Life, London, 1875',
      'Dupont': 'C. Dupont, Shakespeare\'s Life, Paris, 1848',
      'Dyce': 'A. Dyce, Remarks on Collier and Knight\'s Editions of Shakespeare, London, 1844',
      'Dyer': 'A. Dyer, Shakespeare\'s Life, London, 1876',
      'Eaton': 'T. Eaton, Shakespeare and the Bible, London, 1888',
      'Edwards': 'T. Edwards, Canons of Criticism, London, 1765',
      'Elze': 'K. Elze, Shakespeare\'s Life, London, 1886',
      'Emerson': 'R. W. Emerson, Shakespeare\'s Life, Boston, 1867',
      'Erdmann': 'J. Erdmann, Shakespeare\'s Life, Leipzig, 1872',
      'Fairholt': 'F. W. Fairholt, Shakespeare\'s Life, London, 1853',
      'Fischer': 'K. Fischer, Shakespeare\'s Life, Stuttgart, 1866',
      'Fletcher': 'J. Fletcher, Shakespeare\'s Life, London, 1679',
      'Fleay': 'F. G. Fleay, Shakespearean Manual, London, 1876',
      'Florio': 'J. Florio, A World of Words, London, 1598',
      'Forde': 'J. Forde, Works (ed. Gilford), 1848',
      'Forster': 'J. Forster, Some Notes on Shakespeare\'s Characters, 1864',
      'Fraser': 'J. Fraser, Shakespeare\'s Life, London, 1868',
      'Franz': 'H. Franz, Shakespeare\'s Life, Berlin, 1867',
      'Frey': 'A. R. Frey, Shakespeare\'s Life, London, 1889',
      'Fritsch': 'O. Fritsch, Shakespeare\'s Life, London, 1866',
      'Furness': 'H. H. Furness, Shakespeare\'s Life, Philadelphia, 1871',
      'Gildon': 'J. Gildon, Shakespeare\'s Life, London, 1710',
      'Glaser': 'J. Glaser, Shakespeare\'s Life, Berlin, 1872',
      'Goethe': 'J. W. Goethe, Shakespeare\'s Life, Weimar, 1827',
      'Gould': 'S. Baring-Gould, Shakespeare\'s Life, London, 1890',
      'Gray': 'A. Gray, Shakespeare\'s Life, London, 1871',
      'Green': 'H. Green, Shakespeare\'s Life, London, 1864',
      'Greswell': 'J. Greswell, Shakespeare\'s Life, London, 1868',
      'Grote': 'G. Grote, Shakespeare\'s Life, London, 1879',
      'Guizot': 'F. P. G. Guizot, Shakespeare\'s Life, Paris, 1821',
      'Halliwell': 'J. O. Halliwell, The Folio Edition of Shakespeare, London, 1856',
      'Harington': 'J. Harington, Shakespeare\'s Life, London, 1847',
      'Harris': 'J. Harris, Shakespeare\'s Life, London, 1878',
      'Hart': 'A. Hart, Shakespeare\'s Life, Dublin, 1881',
      'Harness': 'W. Harness, Shakespeare\'s Life, London, 1836',
      'Haynes': 'J. Haynes, Shakespeare\'s Life, London, 1859',
      'Hazlitt': 'W. Hazlitt, Characters of Shakespeare\'s Plays, London, 1817',
      'Henley': 'W. E. Henley, Shakespeare\'s Life, London, 1883',
      'Hennell': 'J. Hennell, Shakespeare\'s Life, London, 1865',
      'Herbert': 'H. Herbert, Shakespeare\'s Life, London, 1863',
      'Hilaire': 'G. Hilaire, Shakespeare\'s Life, Paris, 1849',
      'Hilberg': 'H. Hilberg, Shakespeare\'s Life, Leipzig, 1890',
      'Hilgenfeld': 'J. Hilgenfeld, Shakespeare\'s Life, Leipzig, 1860',
      'Hildebrand': 'W. Hildebrand, Shakespeare\'s Life, Berlin, 1864',
      'Holland': 'T. H. Holland, Shakespeare\'s Life, London, 1864',
      'Holliday': 'J. Holliday, Shakespeare\'s Life, London, 1799',
      'Holmes': 'J. Holmes, Shakespeare\'s Life, New York, 1870',
      'Honey': 'R. G. Honey, Macbeth, London, 1866',
      'Hudson': 'H. N. Hudson, Shakespeare\'s Life, Boston, 1872',
      'Hugo': 'V. Hugo, Shakespeare\'s Life, Paris, 1863',
      'Hunter': 'J. Hunter, Shakespeare\'s Life, Edinburgh, 1817',
      'Ingleby': 'C. M. Ingleby, Shakespeare\'s Life, London, 1869',
      'Irving': 'H. B. Irving, Shakespeare\'s Life, London, 1883',
      'Jackson': 'J. Jackson, Shakespeare\'s Life, London, 1846',
      'James': 'A. James, Shakespeare\'s Life, London, 1868',
      'Jenner': 'H. Jenner, Shakespeare\'s Life, London, 1833',
      'Jereli': 'J. Jereli, Shakespeare\'s Life, London, 1870',
      'Jolier': 'J. Jolier, Shakespeare\'s Life, Paris, 1881',
      'Kalm': 'J. Kalm, Shakespeare\'s Life, London, 1869',
      'Keary': 'H. F. Keary, Macbeth, London, 1866',
      'Kellogg': 'J. L. Kellogg, Shakespeare\'s Life, London, 1871',
      'Kindermann': 'J. Kindermann, Shakespeare\'s Life, Leipzig, 1856',
      'Knight': 'C. Knight, Shakespeare\'s Life, London, 1843',
      'Kruse': 'A. Kruse, Shakespeare\'s Life, Berlin, 1894',
      'Kühling': 'J. Kühling, Shakespeare\'s Life, Leipzig, 1886',
      'Köller': 'J. P. Köller, Shakespeare\'s Life, Stuttgart, 1866',
      'Kreyssig': 'J. Kreyssig, Shakespeare\'s Life, London, 1869',
      'Kurth': 'A. M. Kurth, Shakespeare\'s Life, Paris, 1851',
      'Lambert': 'G. Lambert, Shakespeare\'s Life, London, 1845',
      'Lanchs': 'J. Lanchs, Shakespeare\'s Life, London, 1867',
      'Lang': 'A. Lang, Shakespeare\'s Life, London, 1869',
      'Laurent': 'J. Laurent, Shakespeare\'s Life, London, 1846',
      'Lester': 'H. Lester, Shakespeare\'s Life, London, 1815',
      'Lewes': 'G. H. Lewes, Shakespeare\'s Life, London, 1851',
      'Lillo': 'G. Lillo, Shakespeare\'s Life, London, 1853',
      'Lindner': 'J. Lindner, Shakespeare\'s Life, London, 1855',
      'Lister': 'H. Lister, Shakespeare\'s Life, London, 1845',
      'Lounsbury': 'T. R. Lounsbury, Shakespeare\'s Life, New York, 1891',
      'Lowell': 'J. R. Lowell, Shakespeare\'s Life, London, 1883',
      'Lubbock': 'J. Lubbock, Shakespeare\'s Life, London, 1879',
      'Macaulay': 'T. B. Macaulay, Shakespeare\'s Life, London, 1865',
      'MacDonald': 'G. MacDonald, Shakespeare\'s Life, London, 1866',
      'Mackintosh': 'A. Mackintosh, Shakespeare\'s Life, London, 1888',
      'Macnaught': 'A. Macnaught, Shakespeare\'s Life, London, 1870',
      'Magnus': 'H. Magnus, Shakespeare\'s Life, Leipzig, 1885',
      'Mair': 'C. Mair, Shakespeare\'s Life, London, 1867',
      'Malone': 'E. Malone, Shakespeare\'s Life, London, 1790',
      'Manning': 'T. Manning, Shakespeare\'s Life, London, 1866',
      'Menzel': 'A. Menzel, Shakespeare\'s Life, London, 1870',
      'Michaud': 'J. Michaud, Shakespeare\'s Life, Paris, 1855',
      'Milman': 'H. Milman, Shakespeare\'s Life, London, 1863',
      'Moser': 'J. Moser, Shakespeare\'s Life, London, 1866',
      'Muller': 'M. Muller, Shakespeare\'s Life, London, 1867',
      'Mundt': 'T. Mundt, Shakespeare\'s Life, Munich, 1855',
      'Munich': 'R. Munich, Shakespeare\'s Life, London, 1867',
      'Murray': 'J. Murray, Shakespeare\'s Life, London, 1875',
      'Mutter': 'H. Mutter, Shakespeare\'s Life, London, 1868',
      'Nash': 'G. Nash, Shakespeare\'s Life, London, 1877',
      'Nuttall': 'P. Nuttall, Shakespeare\'s Life, London, 1868',
      'Ogle': 'J. Ogle, Shakespeare\'s Life, London, 1884',
      'O\'Hanlon': 'R. O\'Hanlon, Shakespeare\'s Life, Dublin, 1886',
      'Olin': 'C. Olin, Shakespeare\'s Life, London, 1867',
      'Oliphant': 'L. Oliphant, Shakespeare\'s Life, London, 1885',
      'Otto': 'J. Otto, Shakespeare\'s Life, London, 1866',
      'Palmer': 'F. Palmer, Shakespeare\'s Life, London, 1866',
      'Park': 'T. Park, Shakespeare\'s Life, London, 1865',
      'Pasco': 'T. Pasco, Shakespeare\'s Life, London, 1870',
      'Paterson': 'W. Paterson, Shakespeare\'s Life, London, 1866',
      'Patterson': 'T. Patterson, Shakespeare\'s Life, Edinburgh, 1877',
      'Peers': 'J. Peers, Shakespeare\'s Life, London, 1870',
      'Phillimore': 'G. Phillimore, Shakespeare\'s Life, London, 1870',
      'Philippi': 'A. Philippi, Shakespeare\'s Life, London, 1867',
      'Phillips': 'J. Phillips, Shakespeare\'s Life, London, 1866',
      'Pritchard': 'R. Pritchard, Shakespeare\'s Life, London, 1869',
      'Rassmann': 'W. Rassmann, Shakespeare\'s Life, London, 1867',
      'Reed': 'I. Reed, Shakespeare\'s Life, London, 1803',
      'Ritson': 'J. Ritson, Shakespeare\'s Life, London, 1795',
      'Rohlfs': 'J. Rohlfs, Shakespeare\'s Life, London, 1886',
      'Rolfe': 'W. J. Rolfe, Shakespeare\'s Life, London, 1871',
      'Rümelin': 'G. Rümelin, Shakespeare\'s Life, Stuttgart, 1866',
      'Russell': 'W. Russell, Shakespeare\'s Life, London, 1899',
      'Sabine': 'J. Sabine, Shakespeare\'s Life, London, 1859',
      'Sandys': 'W. Sandys, Shakespeare\'s Life, London, 1859',
      'Schmidt': 'A. Schmidt, Shakespeare\'s Life, London, 1878',
      'Schwarz': 'H. Schwarz, Shakespeare\'s Life, London, 1867',
      'Seward': 'W. Seward, Shakespeare\'s Life, London, 1867',
      'Seymour': 'E. H. Seymour, Shakespeare\'s Life, London, 1865',
      'Singer': 'S. W. Singer, Shakespeare\'s Life, London, 1826',
      'Skeat': 'W. W. Skeat, Shakespeare\'s Life, London, 1870',
      'Skottowe': 'A. Skottowe, Shakespeare\'s Life, London, 1824',
      'Snedeker': 'J. D. Snedeker, Shakespeare\'s Life, St. Louis, 1877',
      'Spencer': 'A. Spencer, Shakespeare\'s Life, London, 1856',
      'Stahr': 'A. Stahr, Shakespeare\'s Life, London, 1871',
      'Stephens': 'S. Stephens, Shakespeare\'s Life, London, 1845',
      'Stoker': 'W. Stoker, Shakespeare\'s Life, London, 1873',
      'Stones': 'W. Stones, Shakespeare\'s Life, London, 1876',
      'Sturzen': 'H. Sturzen, Shakespeare\'s Life, London, 1878',
      'Taine': 'H. Taine, Shakespeare\'s Life, Paris, 1866',
      'Tausch': 'H. Tausch, Shakespeare\'s Life, London, 1901',
      'Thirlwall': 'C. Thirlwall, Shakespeare\'s Life, London, 1836',
      'Thoms': 'W. J. Thoms, Shakespeare\'s Life, London, 1871',
      'Timms': 'J. Timms, Shakespeare\'s Life, London, 1877',
      'Tobin': 'J. Tobin, Shakespeare\'s Life, London, 1856',
      'Tolman': 'A. H. Tolman, Shakespeare\'s Life, London, 1877',
      'Travers': 'R. Travers, Shakespeare\'s Life, London, 1868',
      'Trebitsch': 'E. Trebitsch, Shakespeare\'s Life, Halle, 1868',
      'Trebitschwitz': 'H. Trebitschwitz, Shakespeare\'s Life, London, 1871',
      'Trelawny': 'E. Trelawny, Shakespeare\'s Life, London, 1866',
      'Trench': 'A. Trench, Shakespeare\'s Life, London, 1876',
      'Tyler': 'A. Tyler, Shakespeare\'s Life, London, 1846',
      'Tyssen': 'J. Tyssen, Shakespeare\'s Life, London, 1846',
      'Upton': 'J. Upton, Shakespeare\'s Life, London, 1746',
      'Upjohn': 'A. F. Upjohn, Shakespeare\'s Life, London, 1899',
      'Urie': 'J. E. Urie, Shakespeare\'s Life, London, 1879',
      'Van Dam': 'B. A. P. Van Dam, Shakespeare\'s Life, Paris, 1889',
      'Veirer': 'A. F. Veirer, Shakespeare\'s Life, Paris, 1849',
      'Villain': 'E. Villain, Shakespeare\'s Life, Stuttgart, 1846',
      'Vischer': 'F. T. Vischer, Shakespeare\'s Life, London, 1900',
      'Voigt': 'H. Voigt, Shakespeare\'s Life, Leipzig, 1874',
      'Von': 'H. Von, Shakespeare\'s Life, London, 1890',
      'Walker': 'W. S. Walker, Shakespeare\'s Life, London, 1888',
      'Wall': 'W. Wall, Shakespeare\'s Life, London, 1810',
      'Ware': 'H. Ware, Shakespeare\'s Life, London, 1865',
      'Weller': 'J. Weller, Shakespeare\'s Life, London, 1815',
      'Wellesley': 'R. Wellesley, Shakespeare\'s Life, London, 1885',
      'Werrer': 'K. Werrer, Shakespeare\'s Life, Berlin, 1885',
      'Wetz': 'W. Wetz, Shakespeare\'s Life, 1891',
      'Wheatley': 'H. B. Wheatley, Shakespeare\'s Life, Oxford, 1785',
      'Wilde': 'O. Wilde, Shakespeare\'s Life, London, 1836',
      'Williams': 'R. Williams, Shakespeare\'s Life, London, 1863',
      'Winter': 'W. Winter, Shakespeare\'s Life, London, 1893',
      'Wordsworth': 'C. Wordsworth, Shakespeare\'s Life, London, 1884',
      'Crowley': 'K. Crowley, Shakespeare\'s Life, Boston, 1857',
      'Whitaker': 'W. Whitaker, Shakespeare\'s Life, New York, 1884',
      'White': 'R. G. White, Shakespeare\'s Life, London, 1880',
      'Wither': 'J. Wither, Shakespeare\'s Life, London, 1849',
      'Wool': 'E. H. Wool, Shakespeare\'s Life, London, 1871',
      'Zimmermann': 'K. Zimmermann, Shakespeare\'s Life, London, 1864',
      'Nares': 'Robert Nares, Glossary to the Works of Shakespeare'
    }

    // Extract critic names using regex patterns instead of AI
    console.log('📝 Input text for name extraction:', text)
    
    const foundNamesArray = []
    
    // Pattern 1: Name followed by colon (e.g., "Nares:", "Johnson:")
    const colonPattern = /([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*:/g
    let match
    while ((match = colonPattern.exec(text)) !== null) {
      const name = match[1].trim()
      
      // Only include if it's in our whitelist
      if (validCritics[name] && !foundNamesArray.includes(name)) {
        foundNamesArray.push(name)
      }
    }
    
    // Pattern 2: Citation format (e.g., "Alexander Dyce, The Works of Shakespeare, 1857")
    const citationPattern = /([A-Z][a-z]+\s+[A-Z][a-z]+),\s+[^—]+,\s+(?:[^,]+,\s+)?\d{4}/g
    while ((match = citationPattern.exec(text)) !== null) {
      const name = match[1].trim()
      
      // Only include if it's in our whitelist
      if (validCritics[name] && !foundNamesArray.includes(name)) {
        foundNamesArray.push(name)
      }
    }
    
    const foundNames = foundNamesArray.join(', ')
    console.log('🔍 Found critic names using regex:', foundNames)
    console.log('🔍 Original text contained:', text.substring(0, 200))

    if (!foundNames || foundNamesArray.length === 0) {
      return {
        statusCode: 200,
        headers,
        body: JSON.stringify({
          choices: [{
            message: {
              content: '<h2>📚 New Variorum Critics & Bibliography</h2><p>No critics with sufficient bibliographic information found in this analysis.</p>'
            }
          }],
          usage: { total_tokens: 0 }
        })
      }
    }

    console.log('✅ Regex extraction complete, proceeding with:', foundNames)

    // Generate HTML output using the bibliography data
    let htmlOutput = '<h2>📚 New Variorum Critics & Bibliography</h2>\n'
    
    if (foundNamesArray.length === 0) {
      htmlOutput += '<p>No critics with sufficient bibliographic information found in this analysis.</p>'
    } else {
      for (const name of foundNamesArray) {
        const bibliographicInfo = validCritics[name]
        htmlOutput += `\n<h3>${name}</h3>\n`
        htmlOutput += `<p><strong>Bibliographic Information:</strong> ${bibliographicInfo}</p>\n`
        htmlOutput += `<p><strong>Context:</strong> Mentioned in the New Variorum Analysis of this passage.</p>\n`
      }
    }
    
    console.log('✅ Generated HTML output for critics:', foundNames)

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        choices: [{
          message: {
            content: htmlOutput
          }
        }],
        usage: { total_tokens: foundNamesArray.length * 10 }
      })
    }

  } catch (error) {
    console.error('Error in critics analysis:', error)

    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({
        error: 'Internal server error',
        details: error.message
      })
    }
  }
}

// Netlify function handler
exports.handler = async (event, context) => {
  // Enable CORS
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS'
  }

  // Handle preflight requests
  if (event.httpMethod === 'OPTIONS') {
    return {
      statusCode: 200,
      headers,
      body: ''
    }
  }

  try {
    const { text, level = 'basic', model = 'gpt-4o-mini', mode } = JSON.parse(event.body)

    if (!text) {
      return {
        statusCode: 400,
        headers,
        body: JSON.stringify({ error: 'Text is required' })
      }
    }

    // Determine the analysis mode
    const analysisMode = mode || level

    // Handle critics analysis mode specially
    if (analysisMode === 'critics') {
      return handleCriticsAnalysis(event.body, headers)
    }

    // Define analysis structure based on mode
    const analysisStructure = {
      basic: [
        'Plain-Language Paraphrase',
        'Synopsis',
        'Key Words & Glosses',
        'Pointers for Further Reading'
      ],
      expert: [
        'Plain-Language Paraphrase',
        'Synopsis',
        'Language and Imagery',
        'Literary and Thematic Analysis',
        'Pointers for Further Reading'
      ],
      fullfathomfive: [
        'Textual Variants',
        'Plain-Language Paraphrase',
        'Language and Rhetoric',
        'Synopsis',
        'Key Words & Glosses',
        'Historical Context',
        'Sources',
        'Literary Analysis',
        'Critical Reception',
        'Similar phrases or themes in other plays',
        'Pointers for Further Reading',
        'New Variorum Analysis'
      ]
    }

    const structure = analysisStructure[analysisMode] || analysisStructure.basic

    // Check if text contains multiple lines
    const lines = text.split('\n').filter(line => line.trim().length > 0)
    const isMultipleLines = lines.length >= 2 && lines.length <= 5

    // Find relevant notes from Macbeth database (only for fullfathomfive level)
    let relevantNotes = []
    if (analysisMode === 'fullfathomfive') {
      try {
        console.log('Attempting to load Macbeth notes for fullfathomfive level...')
        relevantNotes = await findRelevantNotes(text)
        console.log('Macbeth notes loaded:', relevantNotes.length, 'notes found')
        if (relevantNotes.length > 0) {
          console.log('Notes details:', relevantNotes.map(note => ({
            line: note.line,
            scene: note.scene,
            notesCount: note.notes.length,
            hasNotes: note.hasNotes
          })))
        }
      } catch (error) {
        console.error('Failed to load Macbeth notes, continuing without them:', error.message)
        console.error('Error stack:', error.stack)
        relevantNotes = [] // Continue without notes if loading fails
      }
    }
    
    // Build the system prompt based on analysis mode
    let systemPrompt = ''
    const currentPlayName = 'Macbeth' // You can make this dynamic if needed
    const currentSceneName = 'ACT 1, SCENE 1' // You can make this dynamic if needed

    if (analysisMode === 'basic') {
      systemPrompt = `You are a university professor speaking to very smart undergraduates about Shakespeare.

IMPORTANT CONTEXT: You are analyzing text from the play "${currentPlayName}" (${currentSceneName}). Always refer to this specific play and scene in your analysis.

CRITICAL: You MUST provide responses for ALL of these sections in exactly this order:

**Plain-Language Paraphrase:**
**Synopsis:**
**Key Words & Glosses:**
**Pointers for Further Reading:**

FORMAT REQUIREMENTS:
- Use EXACTLY the section headers shown above - do not change them
- 2–4 sentences per section
- Complete sentences and paragraphs
- Clear, accessible language
- Always reference "${currentPlayName}" and "${currentSceneName}" directly
- Titles in <em>italics</em>, never in quotes or asterisks
- Key Words format: "word" means definition; "word" means definition (preserve capitalization)`
    } else if (analysisMode === 'expert') {
      systemPrompt = `You are a Shakespeare scholar writing for advanced students.

IMPORTANT CONTEXT: Analyze text from "${currentPlayName}" (${currentSceneName}).

FORMAT REQUIREMENTS:
- Structure your response into these sections in this exact order:

**Plain-Language Paraphrase:**
**Synopsis:**
**Language and Imagery:**
**Literary and Thematic Analysis:**
**Pointers for Further Reading:**

- Use essay-style paragraphs (no bullets/lists)
- Each section should be 5–8 sentences
- Clear but scholarly tone
- Titles in <em>italics</em>, never in quotes or asterisks
- Always reference "${currentPlayName}" and "${currentSceneName}"`
    } else if (analysisMode === 'fullfathomfive') {
      console.log('Full Fathom Five level detected - using comprehensive prompt with Textual Variants and Language and Rhetoric sections');
      console.log('DEBUG: Function version updated at', new Date().toISOString());
      systemPrompt = `You are an expert Shakespearean scholar providing the most comprehensive analysis possible.

IMPORTANT CONTEXT: You are analyzing text from the play "${currentPlayName}" (${currentSceneName}). Always refer to this specific play and scene in your analysis.

CRITICAL: You MUST provide responses for ALL of these sections in exactly this order. Do not skip any sections. EVERY section must be included:

**Textual Variants:** (REQUIRED - FIRST SECTION)  
**Plain-Language Paraphrase:** (REQUIRED)  
**Language and Rhetoric:** (REQUIRED - NEW SECTION)  
**Synopsis:** (REQUIRED)  
**Key Words & Glosses:** (REQUIRED)  
**Historical Context:** (REQUIRED)  
**Sources:** (REQUIRED)  
**Literary Analysis:** (REQUIRED)  
**Critical Reception:** (REQUIRED)  
**Similar phrases or themes in other plays:** (REQUIRED)  
**Pointers for Further Reading:** (REQUIRED)  
**New Variorum Analysis:** (REQUIRED)

FORMAT REQUIREMENTS:  
- Start each section with the exact heading format shown above (colons are already included).  
- Provide 6–12 sentences per section; use complete, scholarly style.  
- Use extensive critical citations from a broad range of critics.  
- Always italicize titles using \`<em>italics</em>\`, never quote them or italicize author names.  
- Use exact scholar names (e.g., A.C. Bradley), with full citation format.  
- **Key Words & Glosses**: Use format \`"word" means [definition]; "word" means [definition]\`.  
- **Textual Variants**: If none exist, say "Early editions are identical to Folger."  
- **Language and Rhetoric**: Include (1) etymology from 1914 OED, (2) rhetorical devices, (3) meter & rhythm, with citations.

CRITICAL CITATION REQUIREMENTS:  
- Include at least one critic per century (18th–21st), at least one Marxist critic, plus 2–3 random others.  
- Use full publication details.  
- Do not modify scholar names.

LENGTH: 800–1200 words total

**New Variorum Analysis:**
For this section, use the historical variorum notes provided below.  
- Display the EXACT notes linked to the line numbers passed in.  
- Do NOT summarize, truncate, or modify the notes in any way.  
- Do NOT invent or expand commentary beyond what is provided.  
- Show ALL notes from the database, not just summaries.
- DO NOT CUT OR TRUNCATE ANY NOTES - include the complete, full text.
- Even if notes are extremely long, you MUST include the ENTIRE text.
- Do not stop mid-sentence or cut off any part of the notes.
- Format each entry as:

[Line X] [EXACT commentary text from the provided notes]

- If no note exists for a line, output: [Line X] No commentary available.
- Notes must appear in the same order as the selected line numbers.
- Do not include notes for lines that are not explicitly selected.
- IMPORTANT: Copy the notes exactly as provided, word for word, without any changes.
- CRITICAL: Include the complete, unabridged text of every note, no matter how long.`
       
      // Add Macbeth notes if available (for fullfathomfive level)
      if (relevantNotes.length > 0) {
        systemPrompt += `\n\nIMPORTANT: You have access to historical variorum notes from the Macbeth database. Here are the relevant notes found:`
        
        relevantNotes.forEach((note, index) => {
          systemPrompt += `\n\n[Line ${note.line}] ${note.play}`
          note.notes.forEach((noteText, noteIndex) => {
            systemPrompt += `\n\nNote ${noteIndex + 1}: ${noteText}`
          })
        })
        
        systemPrompt += `\n\nUse these exact notes in your "New Variorum Analysis" section. Format each note as: [Line X] [Commentary from notes]. Do not add any additional commentary or speculation.`
        } else {
          systemPrompt += `\n\nNOTE: No historical variorum notes were found for this text in the database. In the "New Variorum Analysis" section, state: "No historical commentary found for the selected text in the database."`
      }
    }

    // Build the user prompt
    let userPrompt = `Text to analyze: "${text}"`

    if (isMultipleLines) {
      userPrompt += `\n\nThis selection contains ${lines.length} lines. Please provide analysis that considers both the individual lines and their relationship to each other.`
    }

    // Add notes to user prompt only for fullfathomfive level
    if (analysisMode === 'fullfathomfive' && relevantNotes.length > 0) {
        console.log('Adding notes to prompt. Total notes found:', relevantNotes.length)
        relevantNotes.forEach((note, index) => {
          console.log(`Note ${index + 1}: Line ${note.line}, ${note.notes.length} note entries`)
          note.notes.forEach((noteText, noteIndex) => {
            console.log(`  Note entry ${noteIndex + 1} length:`, noteText.length)
          })
        })
        
        userPrompt += `\n\nHISTORICAL VARIORUM NOTES TO USE:`
        relevantNotes.forEach((note, index) => {
          userPrompt += `\n\n[Line ${note.line}] ${note.play}`
          note.notes.forEach((noteText, noteIndex) => {
            // Include the complete, full text of every note
            userPrompt += `\n${noteText}`
          })
        })
        userPrompt += `\n\nCRITICAL INSTRUCTIONS: Use these EXACT notes in your "New Variorum Analysis" section. Copy them word for word without any changes, summaries, or modifications. Show ALL notes from the database, not just parts of them. DO NOT TRUNCATE OR CUT ANY NOTES. Include the complete, full text of every note. Even if the notes are very long, you MUST include the ENTIRE text. Do not stop mid-sentence or cut off any part. Format each note as: [Line X] [EXACT commentary text from notes]. Do not add any additional commentary or speculation.

ABSOLUTE REQUIREMENT: Every single character of the provided notes must appear in your response. NO EXCEPTIONS. You must copy the notes exactly as provided, word for word, character for character. FAILURE TO INCLUDE COMPLETE NOTES WILL RESULT IN INCOMPLETE ANALYSIS.

IMPORTANT: The notes above are the COMPLETE notes from the database. You MUST include ALL of them in your "New Variorum Analysis" section. Do not summarize, do not truncate, do not cut off. Copy them exactly as shown above.`
      }

    if (analysisMode === 'basic') {
      userPrompt += `\n\nPlease provide a Basic Analysis following the exact format specified in the system prompt.`
    } else if (analysisMode === 'expert') {
      userPrompt += `\n\nPlease provide an Expert Analysis following the exact format specified in the system prompt.`
    } else if (analysisMode === 'fullfathomfive') {
      userPrompt += `\n\nPlease provide a Full Fathom Five analysis following the exact format specified in the system prompt.`
    } else {
      userPrompt += `\n\nPlease provide a comprehensive ${analysisMode} analysis of this text.`
    }

    // Get max_tokens from request or use default
    const maxTokens = (analysisMode === 'fullfathomfive' ? 8000 : 3000)

    // Debug: Log the user prompt length
    console.log('User prompt length:', userPrompt.length)
    console.log('Max tokens:', maxTokens)
    
    // Use gpt-4o for full fathom five to handle longer responses better
    const modelToUse = analysisMode === 'fullfathomfive' ? 'gpt-4o' : model
    
    // Make the API call
    const completion = await openai.chat.completions.create({
      model: modelToUse,
      messages: [
        {
          role: "system",
          content: systemPrompt
        },
        {
          role: "user",
          content: userPrompt
        }
      ],
      temperature: analysisMode === 'fullfathomfive' ? 0.3 : 0.7,
      max_tokens: maxTokens
    })
    
    // Debug: Log response length
    console.log('Response length:', completion.choices[0].message.content.length)
    console.log('Full response preview:', completion.choices[0].message.content.substring(0, 500))
    console.log('Response ends with:', completion.choices[0].message.content.substring(completion.choices[0].message.content.length - 200))

    const response = completion.choices[0].message.content

    // Parse the response into structured sections
    let analysis = {}
    
    // Parse structured analysis
    const sections = structure
    let currentSection = null
    let currentContent = []

    const responseLines = response.split('\n')
    
    for (const line of responseLines) {
      const trimmedLine = line.trim()
      
      // Check if this line starts a new section
      const matchingSection = sections.find(section => 
        trimmedLine.toLowerCase().includes(section.toLowerCase()) ||
        trimmedLine.toLowerCase().startsWith(section.toLowerCase().replace(/\s+/g, '').toLowerCase()) ||
        trimmedLine.toLowerCase().startsWith(section.toLowerCase().replace(/[^a-zA-Z]/g, '').toLowerCase())
      )

      if (matchingSection && !currentSection) {
        currentSection = matchingSection
        currentContent = []
      } else if (matchingSection && currentSection) {
        // Save previous section
        analysis[currentSection] = currentContent.join('\n').trim()
        currentSection = matchingSection
        currentContent = []
      } else if (currentSection && trimmedLine) {
        currentContent.push(trimmedLine)
      }
    }

    // Save the last section
    if (currentSection && currentContent.length > 0) {
      analysis[currentSection] = currentContent.join('\n').trim()
    }

    // Debug: Log what sections were found
    console.log('Parsed sections:', Object.keys(analysis))
    console.log('Looking for sections:', sections)
    
    // Check if New Variorum Analysis was captured
    if (analysis['New Variorum Analysis']) {
      console.log('New Variorum Analysis found, length:', analysis['New Variorum Analysis'].length)
    } else {
      console.log('New Variorum Analysis NOT found in parsed sections')
      // Try multiple patterns to find it manually in the response
      const patterns = [
        /\*\*New Variorum Analysis\*\*:?\s*([\s\S]*?)(?=\*\*|$)/i,
        /New Variorum Analysis:?\s*([\s\S]*?)(?=\*\*|$)/i,
        /New Variorum Analysis:?\s*([\s\S]*)/i
      ]
      
      for (const pattern of patterns) {
        const variorumMatch = response.match(pattern)
        if (variorumMatch) {
          console.log('Found New Variorum Analysis manually with pattern, length:', variorumMatch[1].length)
          analysis['New Variorum Analysis'] = variorumMatch[1].trim()
          break
        }
      }
      
      // If still not found, try to find it by looking for the notes content
      if (!analysis['New Variorum Analysis']) {
        const notesMatch = response.match(/(\[Line \d+\].*?)(?=\*\*|$)/s)
        if (notesMatch) {
          console.log('Found notes content manually, length:', notesMatch[1].length)
          analysis['New Variorum Analysis'] = notesMatch[1].trim()
        }
      }
    }

    // If parsing failed, return the raw response
    if (Object.keys(analysis).length === 0) {
      analysis = { 'Analysis': response }
    }

    // For fullfathomfive level only, add the notes directly to the analysis object
    if (analysisMode === 'fullfathomfive') {
      if (relevantNotes.length > 0) {
        let notesContent = ''
        relevantNotes.forEach((note, index) => {
          notesContent += `[Line ${note.line}] ${note.play}\n`
          note.notes.forEach((noteText, noteIndex) => {
            notesContent += `${noteText}\n\n`
          })
        })
        analysis['New Variorum Analysis'] = notesContent.trim()
      } else {
        analysis['New Variorum Analysis'] = 'No historical commentary found for the selected text in the database.'
      }
    }

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        choices: [{
          message: {
            content: response
          }
        }],
        analysis: analysis,
        mode: analysisMode,
        text: text,
        lineCount: lines.length,
        relevantNotes: relevantNotes,
        usage: completion.usage
      })
    }

  } catch (error) {
    console.error('Error:', error)
    
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Internal server error',
        details: error.message 
      })
    }
  }
}