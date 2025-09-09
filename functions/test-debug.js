exports.handler = async (event, context) => {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Content-Type': 'application/json'
  }

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' }
  }

  try {
    console.log('=== DEBUG FUNCTION CALLED ===')
    console.log('Environment check:')
    console.log('OPENAI_API_KEY exists:', !!process.env.OPENAI_API_KEY)
    console.log('OPENAI_API_KEY length:', process.env.OPENAI_API_KEY ? process.env.OPENAI_API_KEY.length : 0)
    
    return {
      statusCode: 200,
      headers,
      body: JSON.stringify({
        message: 'Debug function working',
        hasApiKey: !!process.env.OPENAI_API_KEY,
        nodeVersion: process.version,
        timestamp: new Date().toISOString()
      })
    }
  } catch (error) {
    console.error('Debug function error:', error)
    return {
      statusCode: 500,
      headers,
      body: JSON.stringify({ 
        error: 'Debug function error',
        details: error.message 
      })
    }
  }
}
