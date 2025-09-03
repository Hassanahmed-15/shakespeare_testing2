const { OpenAI } = require('openai')

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
})

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

    console.log('Analysis mode:', analysisMode)
    console.log('Text:', text)

    // Simple system prompt for testing
    let systemPrompt = ''
    if (analysisMode === 'fullfathomfive') {
      systemPrompt = `You are an expert Shakespearean scholar giving the deepest possible analysis.

IMPORTANT CONTEXT: You are analyzing text from "Macbeth" (ACT 1, SCENE 1). Always refer to this specific play and scene in your analysis.

CRITICAL: You MUST produce exactly TWO sections in this order:

**Analysis:**
Provide a very deep, holistic analysis of the entire passage. This section should go line-by-line or thematically through the passage, connecting language, imagery, rhythm, symbolism, and dramatic function. Use essay-style paragraphs. Do not add historical reception, performance history, or comparisons to other plays. Stay focused on the passage itself in "Macbeth" (ACT 1, SCENE 1).

**New Variorum Analysis:**
For this section, provide historical commentary on the selected text. Format each entry as:

[Line 1] Historical commentary on the selected text

If no specific historical note exists for a line, output: [Line 1] No commentary available.`
    } else {
      systemPrompt = `You are a Shakespeare scholar. Analyze the text: "${text}"`
    }

    // Build the user prompt
    let userPrompt = `Text to analyze: "${text}"`
    if (analysisMode === 'fullfathomfive') {
      userPrompt += `\n\nPlease provide a Full Fathom Five analysis following the exact format specified in the system prompt.`
    }

    console.log('Making API call...')

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
      max_tokens: analysisMode === 'fullfathomfive' ? 8000 : 3000
    })

    const response = completion.choices[0].message.content

    console.log('API call successful')

    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        choices: [{
          message: {
            content: response
          }
        }],
        analysis: { 'Analysis': response },
        mode: analysisMode,
        text: text,
        relevantNotes: []
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
