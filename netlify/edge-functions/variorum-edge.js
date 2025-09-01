// Function to find relevant notes from Macbeth database
function findRelevantNotes(text, macbethNotes) {
  if (!macbethNotes) return []
  
  const relevantNotes = []
  const searchText = text.toLowerCase().trim()
  
  // Search through all scenes and lines
  for (const [sceneKey, sceneData] of Object.entries(macbethNotes)) {
    for (const [lineKey, lineData] of Object.entries(sceneData)) {
      const playText = lineData.play ? lineData.play.toLowerCase() : ''
      
      // Check for exact matches or partial matches
      if (playText.includes(searchText) || searchText.includes(playText) || 
          (playText.length > 10 && searchText.length > 10 && 
           playText.split(' ').some(word => searchText.includes(word)) && 
           searchText.split(' ').some(word => playText.includes(word)))) {
        
        if (lineData.notes && lineData.notes.length > 0) {
          relevantNotes.push({
            scene: sceneKey,
            line: lineKey,
            play: lineData.play,
            notes: lineData.notes
          })
        }
      }
    }
  }
  
  return relevantNotes.slice(0, 5) // Return up to 5 most relevant notes
}

export default async (request, context) => {
  // Handle CORS
  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 200,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS'
      }
    });
  }

  try {
    const CLAUDE_API_KEY = Deno.env.get('CLAUDE_API_KEY');
    
    if (!CLAUDE_API_KEY) {
      return new Response(JSON.stringify({ error: 'Claude API key not configured' }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }

    // Load Macbeth notes database
    let macbethNotes = null;
    try {
      // Try to load from the current site
      const currentUrl = new URL(request.url);
      const notesUrl = `${currentUrl.protocol}//${currentUrl.hostname}/Public/Data/macbeth_notes.json`;
      const notesResponse = await fetch(notesUrl);
      if (notesResponse.ok) {
        macbethNotes = await notesResponse.json();
      }
    } catch (error) {
      console.error('Error loading Macbeth notes:', error);
    }

    if (request.method === 'POST') {
      const { text, playName, sceneName } = await request.json();

      if (!text) {
        return new Response(JSON.stringify({ error: 'Text is required' }), {
          status: 400,
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
          }
        });
      }

      // Set default values for play and scene if not provided
      const currentPlayName = playName || 'Shakespeare';
      const currentSceneName = sceneName || 'scene';

      // Find relevant notes from Macbeth database
      const relevantNotes = findRelevantNotes(text, macbethNotes);

      // Create SSE stream
      const stream = new ReadableStream({
        async start(controller) {
          try {
            // Send initial header
            controller.enqueue(new TextEncoder().encode('data: {"type": "start", "message": "Starting Full Fathom Five analysis..."}\n\n'));

            // Streamlined Full Fathom Five prompt
            let fullPrompt = `You are a Shakespeare scholar providing a comprehensive but concise analysis in the style of the New Variorum editions. Focus on the most important scholarly insights.

CONTEXT: Analyzing "${text}" from ${currentPlayName} (${currentSceneName}).

FORMAT:

## FULL FATHOM FIVE Analysis: "${text}" (${currentPlayName} ${currentSceneName})

### VARIORUM COMMENTARY
Traditional scholarly commentary and historical notes.

### TEXTUAL NOTES
Brief mention of any significant textual variants between early editions (Q1, F1, etc.).

### CRITICAL PERSPECTIVES
3-4 key interpretations from major critics:
**YEAR NAME** (*Work*): Brief insight about this passage.

### PERFORMANCE TRADITION
2-3 notable actor interpretations:
**ACTOR** (period): How they delivered this line.

### SOURCES
Brief mention of any known sources (Holinshed, Plutarch, etc.) or note if Shakespeare invented this.

### WORD STUDY
Brief definitions of key words, preserving original capitalization.

### SHAKESPEAREAN ECHOES
1-2 similar passages from other plays if relevant.

### DRAMATIC PURPOSE
How this passage functions in the scene and play.

### MODERN VIEWS
Brief mention of relevant modern critical approaches.

### CONCLUSION
Concise summary of the passage's significance.

LENGTH: 600-800 words
TONE: Scholarly but clear. Use <em>italics</em> for titles.`;

            // Add Macbeth notes if available
            if (relevantNotes.length > 0) {
              fullPrompt += `\n\nIMPORTANT: You have access to historical variorum notes from the Macbeth database. Use these notes extensively in your analysis, especially in the "VARIORUM COMMENTARY" section. Here are the relevant notes found:`;
              
              relevantNotes.forEach((note, index) => {
                fullPrompt += `\n\nNote ${index + 1} (${note.scene}, Line ${note.line}):\n`;
                fullPrompt += `Text: "${note.play}"\n`;
                fullPrompt += `Historical Notes: ${note.notes.join(' ').substring(0, 1500)}...`;
              });
              
              fullPrompt += `\n\nIntegrate these historical notes into your analysis, particularly in the "VARIORUM COMMENTARY" section. Quote and reference these notes appropriately.`;
            }

            fullPrompt += `\n\nAnalyze: "${text}"`;

            // Send section start
            controller.enqueue(new TextEncoder().encode('data: {"type": "section", "message": "TEXTUAL COLLATION"}\n\n'));

            // Make Claude API call with streaming
            const claudePayload = {
              model: 'claude-sonnet-4-20250514',
              max_tokens: 2000,
              messages: [
                { role: 'user', content: fullPrompt }
              ]
            };

            const claudeResponse = await fetch('https://api.anthropic.com/v1/messages', {
              method: 'POST',
              headers: {
                'x-api-key': `${CLAUDE_API_KEY}`,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
              },
              body: JSON.stringify(claudePayload)
            });

            if (!claudeResponse.ok) {
              throw new Error(`Claude API error: ${claudeResponse.status}`);
            }

            const claudeData = await claudeResponse.json();
            const content = claudeData.content[0].text;

            // Stream the content word by word
            const words = content.split(' ');
            for (let i = 0; i < words.length; i++) {
              const word = words[i];
              const isLastWord = i === words.length - 1;
              
              // Add space after word (except for last word)
              const wordWithSpace = isLastWord ? word : word + ' ';
              
              controller.enqueue(new TextEncoder().encode(`data: {"type": "content", "word": "${wordWithSpace}"}\n\n`));
              
              // Small delay to simulate streaming
              await new Promise(resolve => setTimeout(resolve, 50));
            }

            // Send completion signal
            controller.enqueue(new TextEncoder().encode('data: {"type": "complete"}\n\n'));
            controller.close();

          } catch (error) {
            console.error('Streaming error:', error);
            controller.enqueue(new TextEncoder().encode(`data: {"type": "error", "message": "${error.message}"}\n\n`));
            controller.close();
          }
        }
      });

      return new Response(stream, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Headers': 'Content-Type'
        }
      });
    }

    // Health check
    if (request.method === 'GET') {
      return new Response(JSON.stringify({ 
        status: 'ok', 
        claude: !!CLAUDE_API_KEY
      }), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
    }

  } catch (error) {
    console.error('Edge function error:', error);
    return new Response(JSON.stringify({ error: 'Internal server error' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  }
};
