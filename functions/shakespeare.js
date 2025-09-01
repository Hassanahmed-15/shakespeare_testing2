const { OpenAI } = require('openai')

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Function to find relevant notes from Macbeth database
async function findRelevantNotes(text, scene = null) {
  try {
    // Load Macbeth notes from the public URL
    const response = await fetch('https://shakespeare-variorum.netlify.app/Public/Data/macbeth_notes.json')
    if (!response.ok) {
      console.error('Failed to load Macbeth notes:', response.status)
      return []
    }
    
    const macbethNotes = await response.json()
    const relevantNotes = []
    const searchText = text.toLowerCase().trim()
    
    // Search through all scenes and lines
    for (const [sceneKey, sceneData] of Object.entries(macbethNotes)) {
      for (const [lineKey, lineData] of Object.entries(sceneData)) {
        const playText = lineData.play ? lineData.play.toLowerCase() : ''
        
        // More precise matching - look for exact line matches first
        if (playText === searchText) {
          // Exact match - highest priority
          if (lineData.notes && lineData.notes.length > 0) {
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
        'Analysis',
        'New Variorum Analysis'
      ]
    }

    const structure = analysisStructure[analysisMode] || analysisStructure.basic

    // Check if text contains multiple lines
    const lines = text.split('\n').filter(line => line.trim().length > 0)
    const isMultipleLines = lines.length >= 2 && lines.length <= 5

    // Find relevant notes from Macbeth database (only for Full Fathom Five)
    const relevantNotes = analysisMode === 'fullfathomfive' ? await findRelevantNotes(text) : []
    
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
      systemPrompt = `You are an expert Shakespearean critic giving the deepest possible analysis.

IMPORTANT CONTEXT: You are analyzing "${currentPlayName}" (${currentSceneName}).

CRITICAL: You MUST include these two sub-sections in exactly this order:

**Analysis:**
Provide a very deep, holistic analysis of the entire passage. Discuss language, imagery, symbolism, rhythm, structure, and interpretive depth in flowing scholarly paragraphs. Do not include historical reception or external plays — focus entirely on the passage itself.

**New Variorum Analysis:**
Provide line-by-line commentary ONLY for the line numbers passed in from macbeth-notes.json. Each note should show the exact commentary from the JSON, without additions or speculation. Format:
[Line X] [Commentary from notes]

FORMAT REQUIREMENTS:
- Use EXACT headers ("Analysis:" and "New Variorum Analysis:")
- Write in complete, flowing paragraphs
- Keep strictly to the notes JSON for the Variorum section (no invented material)
- Always reference "${currentPlayName}" and "${currentSceneName}"`
       
      // Add Macbeth notes if available
      if (relevantNotes.length > 0) {
        systemPrompt += `\n\nIMPORTANT: You have access to historical variorum notes from the Macbeth database. Here are the relevant notes found:`
        
        relevantNotes.forEach((note, index) => {
          systemPrompt += `\n\n[Line ${note.line}] ${note.notes.join(' ')}`
        })
        
        systemPrompt += `\n\nUse these exact notes in your "New Variorum Analysis" section without additions or speculation.`
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
