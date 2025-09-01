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
        'Basic Analysis'
      ],
      expert: [
        'Expert Analysis'
      ],
      fullfathomfive: [
        'Analysis (Very Deep)',
        'New Variorum Analysis (Selected Lines Commentary)'
      ]
    }

    const structure = analysisStructure[analysisMode] || analysisStructure.basic

    // Check if text contains multiple lines
    const lines = text.split('\n').filter(line => line.trim().length > 0)
    const isMultipleLines = lines.length >= 2 && lines.length <= 5

    // Find relevant notes from Macbeth database (only for Full Fathom Five)
    const relevantNotes = analysisMode === 'fullfathomfive' ? await findRelevantNotes(text) : []
    
    // Build the system prompt
    let systemPrompt = `You are a Shakespeare scholar providing ${analysisMode} analysis.`

    if (isMultipleLines) {
      systemPrompt += `\n\nYou are analyzing ${lines.length} selected lines from Shakespeare's work. Provide a comprehensive analysis that considers the relationship between these lines and their combined meaning.`
    }

    if (analysisMode === 'expert') {
      systemPrompt += `\n\nIn Expert mode, provide a detailed, scholarly interpretation that explores:

- Themes and symbols
- Historical/cultural context  
- Stylistic and literary devices
- Critical/theoretical perspectives

This should be significantly more advanced than basic analysis, suitable for graduate students and scholars.`
    }

    if (analysisMode === 'fullfathomfive') {
      systemPrompt += `\n\nIn Full Fathom Five mode, provide two distinct sections:

1. ANALYSIS (VERY DEEP): A comprehensive, line-aware, holistic reading of the entire passage. This must go deeper than Basic/Expert — connecting imagery, sound, rhythm, myth, and intertextual echoes.

2. NEW VARIORUM ANALYSIS (SELECTED LINES COMMENTARY): Commentary only on the selected lines. For each line or group of lines:
   - Quote the text
   - Give focused commentary (wordplay, meaning, allusion, critical notes)

This should be the most comprehensive analysis possible - think doctoral-level scholarship.`
       
      // Add Macbeth notes if available
      if (relevantNotes.length > 0) {
        systemPrompt += `\n\nIMPORTANT: You have access to historical variorum notes from the Macbeth database. Use these notes extensively in your analysis, especially in the "Historical Variorum Notes" section. Here are the relevant notes found:`
        
        relevantNotes.forEach((note, index) => {
          systemPrompt += `\n\nNote ${index + 1} (${note.scene}, Line ${note.line}):\n`
          systemPrompt += `Text: "${note.play}"\n`
          systemPrompt += `Historical Notes: ${note.notes.join(' ').substring(0, 2000)}...`
        })
        
        systemPrompt += `\n\nIntegrate these historical notes into your analysis, particularly in the "Historical Variorum Notes" section. Quote and reference these notes appropriately.`
      }
    }

    systemPrompt += `\n\nProvide analysis in the following structure:\n${structure.map(section => `- ${section}`).join('\n')}`

    systemPrompt += `\n\nFormat your response as structured sections. For each section, provide comprehensive analysis that would be appropriate for ${analysisMode === 'basic' ? 'undergraduate students' : analysisMode === 'expert' ? 'graduate students and scholars' : 'advanced scholars and researchers'}.

Use proper scholarly language and provide specific examples from Shakespeare's works when relevant. Include citations and references where appropriate.

For the "New Variorum Analysis (Selected Lines Commentary)" section (in Full Fathom Five mode), provide line-by-line commentary with quoted text and focused analysis.`

    // Build the user prompt
    let userPrompt = `Text to analyze: "${text}"`

    if (isMultipleLines) {
      userPrompt += `\n\nThis selection contains ${lines.length} lines. Please provide analysis that considers both the individual lines and their relationship to each other.`
    }

    if (analysisMode === 'basic') {
      userPrompt += `\n\nPlease provide a Basic Analysis: A simple, straightforward explanation of the passage's surface meaning and imagery.`
    } else if (analysisMode === 'expert') {
      userPrompt += `\n\nPlease provide an Expert Analysis: A detailed, scholarly interpretation that explores themes and symbols, historical/cultural context, stylistic and literary devices, and critical/theoretical perspectives.`
    } else if (analysisMode === 'fullfathomfive') {
      userPrompt += `\n\nPlease provide a Full Fathom Five analysis with two sections:

1. ANALYSIS (VERY DEEP): A comprehensive, line-aware, holistic reading of the entire passage. This must go deeper than Basic/Expert — connecting imagery, sound, rhythm, myth, and intertextual echoes.

2. NEW VARIORUM ANALYSIS (SELECTED LINES COMMENTARY): Commentary only on the selected lines. For each line or group of lines:
   - Quote the text
   - Give focused commentary (wordplay, meaning, allusion, critical notes)`
      
      if (relevantNotes.length > 0) {
        userPrompt += `\n\nNote: Historical variorum notes have been found for this text. Please integrate these notes extensively into your analysis, particularly in the "New Variorum Analysis" section.`
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
