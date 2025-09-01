const { OpenAI } = require('openai')

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Fallback notes function for when external fetch fails
function getFallbackNotes(text) {
  const searchText = text.toLowerCase().trim()
  const fallbackNotes = {
    "first witch: when shall we three meet again": {
      scene: "ACT 1, SCENE 1",
      line: "1",
      play: "First Witch: When shall we three meet again",
      notes: ["Enter three Witches] Seymour: The witches seem to be introduced for no other purpose than to tell us they are to meet again; and as I cannot discover any advantage resulting from such anticipation, but, on the contrary, think it injurious, I conclude the scene is not genuine.—Coleridge (p. 241): The true reason for the first appearance of the Witches is to strike the key-note of the character of the whole drama."]
    },
    "first witch: in thunder, lightning, or in rain?": {
      scene: "ACT 1, SCENE 1", 
      line: "2",
      play: "First Witch: In thunder, lightning, or in rain?",
      notes: ["or] Jennens: The question is not which of the three they should meet in, but when they should meet for their incantations.—Harry Rowe: By the use of the disjunctive particle 'or,' for the conjunctive and, the terror of the scenery is lessened. Thunder and lightning and rain, when combined, present a terrific image; but when separated, they cease to impress the mind with the same degree of terror."]
    },
    "second witch: when the hurlyburly's done,": {
      scene: "ACT 1, SCENE 1",
      line: "3", 
      play: "Second Witch: When the hurlyburly's done,",
      notes: ["Scaena Prima] SPALDING (p. 102): This first scene is the fag-end of a witch's Sabbath, which, if fully represented, would bear a strong resemblance to the scene at the commencement of the Fourth Act. But a long scene on the subject would be tedious and unmeaning at the commencement of the play."]
    },
    "third witch: that will be ere the set of sun.": {
      scene: "ACT 1, SCENE 1",
      line: "5",
      play: "Third Witch: That will be ere the set of sun.", 
      notes: ["Sun] Knight (ed. ii.): We have here the commencement of that system of tampering with the metre of Shakespeare in this great tragedy which universally prevailed till the reign of the Variorum critics had ceased to be considered as firmly established and beyond the reach of assault."]
    }
  }
  
  // Check for exact match
  if (fallbackNotes[searchText]) {
    console.log('Found fallback note for:', searchText)
    return [fallbackNotes[searchText]]
  }
  
  // Check for partial matches
  for (const [key, note] of Object.entries(fallbackNotes)) {
    if (key.includes(searchText) || searchText.includes(key)) {
      console.log('Found partial fallback match for:', searchText)
      return [note]
    }
  }
  
  console.log('No fallback notes found for:', searchText)
  return []
}

// Function to find relevant notes from Macbeth database
async function findRelevantNotes(text, scene = null) {
  try {
    // Load Macbeth notes from the public URL with timeout
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 5000) // 5 second timeout
    
    // Try multiple URLs to find the notes
    const urls = [
      'https://shakespeare-variorum.netlify.app/Public/Data/macbeth_notes.json',
      'https://raw.githubusercontent.com/Hassanahmed-15/Shakespeare-Variorum/main/Public/Data/macbeth_notes.json',
      'https://github.com/Hassanahmed-15/Shakespeare-Variorum/raw/main/Public/Data/macbeth_notes.json'
    ]
    
    let response = null
    for (const url of urls) {
      try {
        console.log('Trying to fetch from:', url)
        response = await fetch(url, { signal: controller.signal })
        if (response.ok) {
          console.log('Successfully fetched from:', url)
          break
        }
      } catch (error) {
        console.log('Failed to fetch from:', url, error.message)
        continue
      }
    }
    
    clearTimeout(timeoutId)
    
    if (!response || !response.ok) {
      console.error('Failed to load Macbeth notes from any URL, using fallback notes')
      // Return fallback notes for testing
      return getFallbackNotes(text)
    }
    
    const macbethNotes = await response.json()
    const relevantNotes = []
    const searchText = text.toLowerCase().trim()
    
    console.log('Searching for text:', searchText)
    console.log('Available scenes:', Object.keys(macbethNotes))
    
    // Search through all scenes and lines
    for (const [sceneKey, sceneData] of Object.entries(macbethNotes)) {
      for (const [lineKey, lineData] of Object.entries(sceneData)) {
        const playText = lineData.play ? lineData.play.toLowerCase() : ''
        
        // More precise matching - look for exact line matches first
        if (playText === searchText) {
          // Exact match - highest priority
          if (lineData.notes && lineData.notes.length > 0) {
            console.log('Found exact match:', lineKey, lineData.play)
            relevantNotes.push({
              scene: sceneKey,
              line: lineKey,
              play: lineData.play,
              notes: lineData.notes,
              matchType: 'exact'
            })
          }
        } else if (playText.includes(searchText) || searchText.includes(playText)) {
          // Partial match - medium priority
          if (lineData.notes && lineData.notes.length > 0) {
            relevantNotes.push({
              scene: sceneKey,
              line: lineKey,
              play: lineData.play,
              notes: lineData.notes,
              matchType: 'partial'
            })
          }
        } else {
          // Word-level matching for similar content
          const searchWords = searchText.split(' ').filter(word => word.length > 3)
          const playWords = playText.split(' ').filter(word => word.length > 3)
          const matchingWords = searchWords.filter(word => playWords.includes(word))
          
          if (matchingWords.length >= Math.min(2, searchWords.length)) {
            if (lineData.notes && lineData.notes.length > 0) {
              relevantNotes.push({
                scene: sceneKey,
                line: lineKey,
                play: lineData.play,
                notes: lineData.notes,
                matchType: 'word'
              })
            }
          }
        }
      }
    }
    
    // Sort by match quality (exact > partial > word) and return top 5
    relevantNotes.sort((a, b) => {
      const matchOrder = { 'exact': 3, 'partial': 2, 'word': 1 }
      return matchOrder[b.matchType] - matchOrder[a.matchType]
    })
    
    return relevantNotes.slice(0, 5) // Return up to 5 most relevant notes
  } catch (error) {
    console.error('Error loading Macbeth notes:', error)
    return []
  }
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

  // Set a timeout for the entire function (20 seconds to stay under Netlify's 30s limit)
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Function timeout')), 20000)
  })

  try {
    const mainPromise = (async () => {
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
        'Analysis',
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
        // Set a quick timeout for notes loading
        const notesPromise = findRelevantNotes(text)
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Notes timeout')), 3000)
        )
        
        relevantNotes = await Promise.race([notesPromise, timeoutPromise])
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
      systemPrompt = `You are an expert Shakespearean scholar giving the deepest possible analysis.

IMPORTANT CONTEXT: You are analyzing text from "${currentPlayName}" (${currentSceneName}). Always refer to this specific play and scene in your analysis.

CRITICAL: You MUST produce exactly TWO sections in this order:

**Analysis:**
Provide a very deep, holistic analysis of the entire passage. This section should go line-by-line or thematically through the passage, connecting language, imagery, rhythm, symbolism, and dramatic function. Use essay-style paragraphs. Do not add historical reception, performance history, or comparisons to other plays. Stay focused on the passage itself in "${currentPlayName}" (${currentSceneName}).

**New Variorum Analysis:**
For this section, fetch commentary from macbeth_notes.json.  
- Only display the exact notes linked to the line numbers passed in.  
- Do not invent or expand commentary beyond what is in the JSON.  
- Format each entry as:

[Line X] Commentary text from macbeth_notes.json

- If no note exists for a line, output: [Line X] No commentary available.
- Notes must appear in the same order as the selected line numbers.
- Do not include notes for lines that are not explicitly selected.`
       
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
        userPrompt += `\n\nNote: Historical variorum notes have been found for this text. Use these exact notes in your "New Variorum Analysis" section without additions or speculation.`
      }
    } else {
      userPrompt += `\n\nPlease provide a comprehensive ${analysisMode} analysis of this text.`
    }

    // Get max_tokens from request or use default
    const maxTokens = event.body.max_tokens || (analysisMode === 'fullfathomfive' ? 8000 : 3000)

    // Make the API call
    const completion = await openai.chat.completions.create({
      model: model,
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

    // If parsing failed, return the raw response
    if (Object.keys(analysis).length === 0) {
      analysis = { 'Analysis': response }
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
    })()

    // Race between main function and timeout
    return await Promise.race([mainPromise, timeoutPromise])

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
