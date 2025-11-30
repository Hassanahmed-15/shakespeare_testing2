const { OpenAI } = require('openai');

exports.handler = async (event, context) => {
    // Handle CORS preflight requests
    if (event.httpMethod === 'OPTIONS') {
        return {
            statusCode: 200,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            body: ''
        };
    }

    // Only allow POST requests
    if (event.httpMethod !== 'POST') {
        return {
            statusCode: 405,
            headers: {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ error: 'Method not allowed' })
        };
    }

    try {
        // Parse the request body
        const { text, level, model } = JSON.parse(event.body);

        if (!text) {
            return {
                statusCode: 400,
                body: JSON.stringify({ error: 'Text is required' })
            };
        }

        // Get API key from environment variable
        const apiKey = process.env.OPENAI_API_KEY;
        if (!apiKey) {
            return {
                statusCode: 500,
                body: JSON.stringify({ error: 'OpenAI API key not configured' })
            };
        }

        // Initialize OpenAI client
        const openai = new OpenAI({
            apiKey: apiKey
        });

        // Create analysis prompt based on level
        let systemPrompt = '';
        let userPrompt = '';

        switch (level) {
            case 'basic':
                systemPrompt = 'You are a Shakespeare scholar providing basic analysis of Shakespearean text. Explain the meaning in simple, clear terms.';
                userPrompt = `Analyze this Shakespeare text and explain its meaning:\n\n${text}`;
                break;
            case 'detailed':
                systemPrompt = 'You are a Shakespeare scholar providing detailed analysis. Include themes, literary devices, historical context, and character motivations.';
                userPrompt = `Provide a detailed analysis of this Shakespeare text:\n\n${text}\n\nInclude themes, literary devices, historical context, and character analysis.`;
                break;
            case 'expert':
                systemPrompt = 'You are an expert Shakespeare scholar providing comprehensive analysis. Include critical interpretations, textual variants, performance history, and scholarly commentary.';
                userPrompt = `Provide an expert-level analysis of this Shakespeare text:\n\n${text}\n\nInclude critical interpretations, textual variants, performance history, scholarly commentary, and multiple perspectives.`;
                break;
            default:
                systemPrompt = 'You are a Shakespeare scholar providing analysis of Shakespearean text.';
                userPrompt = `Analyze this Shakespeare text:\n\n${text}`;
        }

        // Call OpenAI API
        const completion = await openai.chat.completions.create({
            model: model || 'gpt-4o-mini',
            messages: [
                { role: 'system', content: systemPrompt },
                { role: 'user', content: userPrompt }
            ],
            temperature: 0.7,
            max_tokens: 2000
        });

        // Return the response
        return {
            statusCode: 200,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST, OPTIONS'
            },
            body: JSON.stringify(completion)
        };

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            headers: {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            body: JSON.stringify({ 
                error: error.message || 'Internal server error',
                details: process.env.NODE_ENV === 'development' ? error.stack : undefined
            })
        };
    }
};

