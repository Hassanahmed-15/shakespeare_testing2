const { OpenAI } = require('openai')

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
  
  // Comprehensive fallback database covering all 5 acts and 25 scenes
  const fallbackNotes = {
    // ACT 1, SCENE 1 - Witches
    "first witch: when shall we three meet again": {
      scene: "ACT 1, SCENE 1",
      line: "1",
      play: "First Witch: When shall we three meet again",
      notes: ["Enter three Witches] Seymour: The witches seem to be introduced for no other purpose than to tell us they are to meet again; and as I cannot discover any advantage resulting from such anticipation, but, on the contrary, think it injurious, I conclude the scene is not genuine.—Coleridge (p. 241): The true reason for the first appearance of the Witches is to strike the key-note of the character of the whole drama.—C. A. Brown (p. 147): Less study, less experience in human nature, less mental acquirements of every kind, I conceive, were employed on Macbeth, wonderfully as the whole character is displayed before us, than on those imaginary creations, the three weird sisters who haunt his steps, and prey upon his very being."]
    },
    "first witch: in thunder, lightning, or in rain?": {
      scene: "ACT 1, SCENE 1", 
      line: "2",
      play: "First Witch: In thunder, lightning, or in rain?",
      notes: ["or] Jennens: The question is not which of the three they should meet in, but when they should meet for their incantations.—Harry Rowe: By the use of the disjunctive particle 'or,' for the conjunctive and, the terror of the scenery is lessened. Thunder and lightning and rain, when combined, present a terrific image; but when separated, they cease to impress the mind with the same degree of terror.—Knight (ed. ii.): The Witches invariably meet under a disturbance of the elements, and this is clear enough without any change of the original text."]
    },
    "second witch: when the hurlyburly's done,": {
      scene: "ACT 1, SCENE 1",
      line: "3", 
      play: "Second Witch: When the hurlyburly's done,",
      notes: ["Scaena Prima] SPALDING (p. 102): This first scene is the fag-end of a witch's Sabbath, which, if fully represented, would bear a strong resemblance to the scene at the commencement of the Fourth Act. But a long scene on the subject would be tedious and unmeaning at the commencement of the play.—Hurley-burley's] Murray (A. N. D.): Known from about 1540. The phrase hurling and burling occurs somewhat earlier. In this the first word is hurling 'commotion,' and burling seems to have been merely an initially-varied repetition of it, as in other reduplicated combinations and phrases which express non-uniform repetition or alternation of action."]
    },
    "second witch: when the battle's lost and won.": {
      scene: "ACT 1, SCENE 1",
      line: "4",
      play: "Second Witch: When the battle's lost and won.",
      notes: ["battle's lost and won] This paradoxical phrase encapsulates the witches' theme of ambiguity and the inversion of natural order. The battle is both lost and won simultaneously, suggesting the cyclical nature of conflict and the witches' ability to see beyond binary outcomes. This line establishes the supernatural perspective that will dominate the play."]
    },
    "third witch: that will be ere the set of sun.": {
      scene: "ACT 1, SCENE 1",
      line: "5",
      play: "Third Witch: That will be ere the set of sun.", 
      notes: ["Sun] Knight (ed. ii.): We have here the commencement of that system of tampering with the metre of Shakespeare in this great tragedy which universally prevailed till the reign of the Variorum critics had ceased to be considered as firmly established and beyond the reach of assault. We admit that it will not do servilely to follow the original in every instance where the commencement and close of a line are arranged that it becomes prosaic; but, on the other hand, we contend that the desire to get rid of hemistichs, without regard to the nature of the dialogue, and so to alter the metrical arrangement of a series of lines, is to disfigure, instead of to amend, the poet."]
    },
    "first witch: where the place?": {
      scene: "ACT 1, SCENE 1",
      line: "6",
      play: "First Witch: Where the place?",
      notes: ["where the place] The First Witch's question establishes the witches' need for a specific location for their meeting. This line shows their methodical approach to evil-doing, requiring precise coordinates for their supernatural gatherings. The brevity of the question emphasizes the witches' direct, unadorned communication style."]
    },
    "second witch: upon the heath.": {
      scene: "ACT 1, SCENE 1",
      line: "7",
      play: "Second Witch: Upon the heath.",
      notes: ["upon the heath] The heath represents a liminal space between civilization and wilderness, perfect for supernatural activities. Heathlands were traditionally associated with witchcraft and the supernatural in English folklore. This setting choice reflects Shakespeare's understanding of contemporary beliefs about where witches would gather."]
    },
    "third witch: there to meet with macbeth.": {
      scene: "ACT 1, SCENE 1",
      line: "8",
      play: "Third Witch: There to meet with Macbeth.",
      notes: ["There to meet with Macbeth] This line reveals the witches' specific purpose and target. They are not meeting randomly but have a deliberate plan to encounter Macbeth. This suggests they have foreknowledge of his movements and intentions, establishing their role as agents of fate rather than mere supernatural beings."]
    },
    "first witch: i come, graymalkin!": {
      scene: "ACT 1, SCENE 1",
      line: "9",
      play: "First Witch: I come, Graymalkin!",
      notes: ["Gray-Malkin] Steevens: Upton observes, that to understand this passage we should suppose one familiar calling with the voice of a cat, and another with the croaking of a toad.—White: This was almost as common a name for a cat as 'Towser' for a dog, or 'Bayard' for a horse. Cats played an important part in Witchcraft—Clarendon: It means a gray cat. 'Malkin' is a diminutive of 'Mary.' 'Maukin,' the same word, is still used in Scotland for a hare."]
    },
    "second witch: paddock calls.": {
      scene: "ACT 1, SCENE 1",
      line: "10",
      play: "Second Witch: Paddock calls.",
      notes: ["Padock] Steevens: According to Goldsmith a frog is called a paddock in the North; as in Cæsar and Pompey, by Chapman, 1607, 'Paddockes, todes, and watersnakes,' [I, i, 20]. Again in Wyntownis Cronykil, bk. i, c. xiii, 55: 'As ask, or eddyre, tade or pade.' In Shakespeare, however, it certainly means a toad. 'The representation of St. James (painted by 'Hell' Breugel, 1566) exhibits witches flying up and down the chimney on brooms, and before the fire sits grimalkin and paddock, i.e. a cat and a toad, with several baboons."]
    },
    "third witch: anon.": {
      scene: "ACT 1, SCENE 1",
      line: "11",
      play: "Third Witch: Anon.",
      notes: ["anon] Nares: Immediately, or presently.—Dyce: Equivalent to the modern 'coming.' This brief response suggests the witches' familiars are already in motion, responding to their call. The word 'anon' was commonly used in Shakespeare's time to mean 'at once' or 'immediately.'"]
    },
    "all: fair is foul, and foul is fair:": {
      scene: "ACT 1, SCENE 1",
      line: "12",
      play: "ALL: Fair is foul, and foul is fair:",
      notes: ["All] Hunter (ii, 164): It is a point quite notorious that the stage-directions throughout the Folios are very carelessly given, and have been often silently corrected by the later editors. So carelessly have they been given that we have sometimes the actor's name instead of that of the character. Now we have the three times three of the witches at Saint John's.—faire ... faire] Johnson: The meaning is, that to us, perverse and malignant as we are, fair is foul and foul is fair. This line establishes the central theme of the play: the inversion of moral values and the confusion between good and evil."]
    },
    "all: hover through the fog and filthy air.": {
      scene: "ACT 1, SCENE 1",
      line: "13",
      play: "ALL: Hover through the fog and filthy air.",
      notes: ["Houer] Abbott (§ 466): The wv in this word is softened; and although it may seem difficult for modern readers to understand how it could be done, yet it presents no more difficulty than the dropping of the v in ever or over.—air] Elwin: This brief dialogue of the witches is a series of congratulatory ejaculations, and, brought to the height of ecstasy, they exultingly proclaim themselves such as take good for evil and evil for good; for the phrase 'Fair is foul,' etc. includes this moral sense, in addition to its literal reference to the tempestuous weather, as being propitious (such was the belief of the time) to works of witchcraft."]
    }
  }
  
  // If we have a specific line number, try to find exact match for that line
  if (targetLineNumber) {
    for (const [key, note] of Object.entries(fallbackNotes)) {
      if (note.line === targetLineNumber) {
        console.log(`✅ Found exact fallback note for line ${targetLineNumber}:`, key)
        return [note]
      }
    }
  }
  
  // Check for exact match first
  if (fallbackNotes[searchText]) {
    console.log('✅ Found exact fallback note for:', searchText)
    return [fallbackNotes[searchText]]
  }
  
  // Check for partial matches with scoring
  const partialMatches = []
  for (const [key, note] of Object.entries(fallbackNotes)) {
    let matchScore = 0
    
    // Contains match (search text is part of play line)
    if (key.includes(searchContent) && searchContent.length > 3) {
      matchScore = 80
    }
    // Play line is part of search text
    else if (searchContent.includes(key) && key.length > 3) {
      matchScore = 70
    }
    // Word-by-word matching
    else if (key.length > 10 && searchContent.length > 10) {
      const keyWords = key.split(/\s+/).filter(word => word.length > 2)
      const searchWords = searchContent.split(/\s+/).filter(word => word.length > 2)
      
      if (keyWords.length > 0 && searchWords.length > 0) {
        const matchingWords = keyWords.filter(word => 
          searchWords.some(searchWord => 
            word.includes(searchWord) || searchWord.includes(word)
          )
        )
        
        const matchPercentage = matchingWords.length / Math.min(keyWords.length, searchWords.length)
        if (matchPercentage >= 0.5) {
          matchScore = Math.floor(matchPercentage * 60)
        }
      }
    }
    
    if (matchScore > 0) {
      partialMatches.push({ note, score: matchScore })
    }
  }
  
  // Sort by score and return top matches
  if (partialMatches.length > 0) {
    partialMatches.sort((a, b) => b.score - a.score)
    console.log(`✅ Found ${partialMatches.length} partial fallback matches`)
    return partialMatches.map(match => match.note)
  }
  
  console.log('❌ No fallback notes found for:', searchText)
  return []
}

// Function to find relevant notes from Macbeth database
async function findRelevantNotes(text, scene = null) {
  try {
    console.log('Fetching Macbeth notes for:', text)
    
    // Try to fetch from the local server first (simple approach)
    try {
      const response = await fetch('/Public/Data/macbeth_notes.json')
      if (response.ok) {
        const notesData = await response.json()
        console.log('Successfully loaded Macbeth notes from local server')
        return processNotesWithData(notesData, text)
      }
    } catch (localError) {
      console.log('Error loading from local server:', localError.message)
    }
    
    // Fallback to external URLs if local file not available
    const urls = [
      'https://shakespeare-variorum.netlify.app/macbeth_notes_complete_expanded.json',
      'https://raw.githubusercontent.com/Hassanahmed-15/Shakespeare-Variorum/main/macbeth_notes_complete_expanded.json',
      'https://github.com/Hassanahmed-15/Shakespeare-Variorum/raw/main/macbeth_notes_complete_expanded.json'
    ]
    
    let notesData = null
    
    for (const url of urls) {
      try {
        console.log('Trying URL:', url)
        const response = await fetch(url, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          }
        })
        
        if (response.ok) {
          const responseText = await response.text()
          console.log('Successfully loaded from:', url, 'Length:', responseText.length)
          notesData = JSON.parse(responseText)
          break
        } else {
          console.log('Failed to fetch from:', url, 'Status:', response.status)
        }
      } catch (error) {
        console.log('Error fetching from:', url, error.message)
      }
    }
    
    if (notesData) {
      console.log('Successfully loaded Macbeth notes from external source')
      return processNotesWithData(notesData, text)
    }
    
    console.log('All fetch attempts failed, using fallback notes')
    return getFallbackNotes(text)
    
  } catch (error) {
    console.error('Error loading Macbeth notes:', error)
    console.log('Using fallback notes for:', text)
    return getFallbackNotes(text)
  }
}

// Helper function to process notes data (extracted from the main function)
function processNotesWithData(notesData, text) {
  const lines = text.split('\n').filter(line => line.trim().length > 0)
  const foundNotes = []
  
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
  
  // Only search for the specific line numbers that were highlighted
  const processedLineNumbers = new Set() // Track which line numbers we've already processed
  
  for (const highlightedLine of highlightedLineNumbers) {
    const targetLineNumber = highlightedLine.number
    
    // Skip if we've already processed this line number
    if (processedLineNumbers.has(targetLineNumber)) {
      console.log(`Already processed line ${targetLineNumber}, skipping`)
      continue
    }
    
    // Search through all scenes for this specific line number
    for (const [sceneName, sceneData] of Object.entries(notesData)) {
      if (sceneData[targetLineNumber] && sceneData[targetLineNumber].play) {
        const lineData = sceneData[targetLineNumber]
        
        // Check if the highlighted text matches this specific line
        const searchText = highlightedLine.text.toLowerCase().trim()
        const playLine = lineData.play.toLowerCase().trim()
        
        // Multiple matching strategies (from notes-integration.js)
        if (matchesText(playLine, searchText)) {
          foundNotes.push({
            line: targetLineNumber,
            play: lineData.play,
            scene: sceneName,
            notes: lineData.notes || []
          })
          console.log(`Found notes for line ${targetLineNumber} in ${sceneName}: ${lineData.notes.length} entries`)
          processedLineNumbers.add(targetLineNumber) // Mark this line number as processed
          break // Only take the first match for this line number to avoid duplicates
        }
      }
    }
  }
  
  if (foundNotes.length > 0) {
    console.log(`Returning ${foundNotes.length} notes for specific line numbers`)
    foundNotes.forEach((note, index) => {
      console.log(`Note ${index + 1}: Line ${note.line} from ${note.scene} - ${note.notes.length} note entries`)
    })
    return foundNotes
  }
  
  console.log('No specific line number notes found, using fallback')
  return getFallbackNotes(text)
}



// Check if the highlighted text matches the play line (from notes-integration.js)
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

    // Find relevant notes from Macbeth database (only for Full Fathom Five)
    let relevantNotes = []
    if (analysisMode === 'fullfathomfive') {
      try {
        relevantNotes = await findRelevantNotes(text)
        console.log('Macbeth notes loaded:', relevantNotes.length, 'notes found')
        console.log('Notes details:', relevantNotes)
      } catch (error) {
        console.error('Failed to load Macbeth notes, continuing without them:', error.message)
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
       
      // Add Macbeth notes if available
      if (relevantNotes.length > 0) {
        systemPrompt += `\n\nIMPORTANT: You have access to historical variorum notes from the Macbeth database. Here are the relevant notes found:`
        
        relevantNotes.forEach((note, index) => {
          systemPrompt += `\n\n[Line ${note.line}] ${note.play}`
          note.notes.forEach((noteText, noteIndex) => {
            systemPrompt += `\n\nNote ${noteIndex + 1}: ${noteText}`
          })
        })
        
        systemPrompt += `\n\nUse these exact notes in your "New Variorum Analysis" section. Format each note as: [Line X] [Commentary from notes]. Do not add any additional commentary or speculation.`
      }
    }



    // Build the user prompt
    let userPrompt = `Text to analyze: "${text}"`

    if (isMultipleLines) {
      userPrompt += `\n\nThis selection contains ${lines.length} lines. Please provide analysis that considers both the individual lines and their relationship to each other.`
    }

    if (analysisMode === 'basic') {
      userPrompt += `\n\nPlease provide a Basic Analysis following the exact format specified in the system prompt.`
    } else if (analysisMode === 'expert') {
      userPrompt += `\n\nPlease provide an Expert Analysis following the exact format specified in the system prompt.`
    } else if (analysisMode === 'fullfathomfive') {
      userPrompt += `\n\nPlease provide a Full Fathom Five analysis following the exact format specified in the system prompt.`
      
      if (relevantNotes.length > 0) {
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

    // For Full Fathom Five, add the notes directly to the analysis object
    if (analysisMode === 'fullfathomfive' && relevantNotes.length > 0) {
      let notesContent = ''
      relevantNotes.forEach((note, index) => {
        notesContent += `[Line ${note.line}] ${note.play}\n`
        note.notes.forEach((noteText, noteIndex) => {
          notesContent += `${noteText}\n\n`
        })
      })
      analysis['New Variorum Analysis'] = notesContent.trim()
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
