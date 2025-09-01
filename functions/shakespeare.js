const { OpenAI } = require('openai')

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

// Function to find relevant notes from Macbeth database
// For now, return empty array to avoid errors
function findRelevantNotes(text, scene = null) {
  return []
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
      detailed: [
        'Plain-Language Paraphrase',
        'Language and Rhetoric',
        'Synopsis',
        'Key Words & Glosses',
        'Historical Context',
        'Literary Analysis',
        'Pointers for Further Reading'
      ],
      expert: [
        'Advanced Textual Analysis',
        'Metrical and Prosodic Analysis',
        'Rhetorical Devices and Figures',
        'Intertextual Connections',
        'Critical Interpretations',
        'Performance History',
        'Editorial Commentary',
        'Scholarly Debates',
        'Thematic Analysis',
        'Cultural Context',
        'Further Research Directions'
      ],
      fullfathomfive: [
        'Variorum Commentary',
        'Textual Variants and Collation',
        'Historical Variorum Notes',
        'Critical Reception Through Time',
        'Performance Traditions',
        'Editorial History',
        'Source Materials',
        'Linguistic Analysis',
        'Metrical Analysis',
        'Rhetorical Analysis',
        'Thematic and Symbolic Analysis',
        'Intertextual Echoes',
        'Modern Critical Approaches',
        'Scholarly Bibliography'
      ]
    }

    const structure = analysisStructure[analysisMode] || analysisStructure.basic

    // Check if text contains multiple lines
    const lines = text.split('\n').filter(line => line.trim().length > 0)
    const isMultipleLines = lines.length >= 2 && lines.length <= 5

    // Find relevant notes from Macbeth database
    const relevantNotes = findRelevantNotes(text)
    
    // Build the system prompt
    let systemPrompt = `You are a Shakespeare scholar providing ${analysisMode} analysis.`

    if (isMultipleLines) {
      systemPrompt += `\n\nYou are analyzing ${lines.length} selected lines from Shakespeare's work. Provide a comprehensive analysis that considers the relationship between these lines and their combined meaning.`
    }

    if (analysisMode === 'expert') {
      systemPrompt += `\n\nIn Expert mode, you should provide ADVANCED SCHOLARLY analysis that goes significantly beyond basic analysis. This is graduate-level scholarship that includes:

1. Sophisticated textual analysis with attention to editorial issues
2. Detailed metrical and prosodic analysis
3. Advanced rhetorical analysis identifying complex figures of speech
4. Intertextual connections to other Shakespeare works and classical sources
5. Critical interpretations from major scholars
6. Performance history and theatrical traditions
7. Editorial commentary and textual variants
8. Scholarly debates and controversies
9. Thematic analysis with cultural and historical context
10. Directions for further research

This should be significantly more advanced than basic analysis, suitable for graduate students and scholars.`
    }

    if (analysisMode === 'fullfathomfive') {
      systemPrompt += `\n\nIn Full Fathom Five mode, you should provide INSANELY DETAILED and COMPREHENSIVE analysis in the style of traditional variorum editions. This is the highest level of scholarly analysis available. You must:

1. Provide EXTREMELY detailed analysis for each section
2. Include extensive historical context and background
3. Reference multiple scholarly sources and interpretations
4. Analyze every word, phrase, and literary device in depth
5. Compare with similar passages across Shakespeare's works
6. Include critical reception from multiple time periods
7. Provide detailed textual variants and editorial history
8. Analyze meter, rhythm, and poetic techniques extensively
9. Include cultural, political, and social context
10. Reference contemporary scholarship and modern interpretations

This should be the most comprehensive analysis possible - think doctoral-level scholarship. Each section should be extensive and thorough.`
      

    }

    systemPrompt += `\n\nProvide analysis in the following structure:\n${structure.map(section => `- ${section}`).join('\n')}`

    systemPrompt += `\n\nFormat your response as structured sections. For each section, provide comprehensive analysis that would be appropriate for ${analysisMode === 'basic' ? 'undergraduate students' : analysisMode === 'detailed' ? 'advanced students' : analysisMode === 'expert' ? 'graduate students and scholars' : 'advanced scholars and researchers'}.

Use proper scholarly language and provide specific examples from Shakespeare's works when relevant. Include citations and references where appropriate.

For the Commentary section (in Full Fathom Five mode), provide traditional scholarly commentary if available, or clearly state "No traditional commentary available for this text" and proceed with modern analysis.`

    // Build the user prompt
    let userPrompt = `Text to analyze: "${text}"`

    if (isMultipleLines) {
      userPrompt += `\n\nThis selection contains ${lines.length} lines. Please provide analysis that considers both the individual lines and their relationship to each other.`
    }

    if (analysisMode === 'expert') {
      userPrompt += `\n\nPlease provide an ADVANCED EXPERT analysis of this text. This should be significantly more sophisticated than basic analysis, suitable for graduate students and scholars. Focus on advanced textual analysis, metrical patterns, rhetorical devices, intertextual connections, and scholarly interpretations.`
    } else if (analysisMode === 'fullfathomfive') {
      userPrompt += `\n\nPlease provide an INSANELY DETAILED and COMPREHENSIVE Full Fathom Five analysis of this text. This should be the most thorough scholarly analysis possible - equivalent to doctoral-level research. Be extremely detailed in every section, providing extensive context, multiple interpretations, and thorough scholarly analysis.`
      

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
