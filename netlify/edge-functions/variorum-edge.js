// Function to find relevant notes from Macbeth database
function findRelevantNotes(text, macbethNotes) {
  if (!macbethNotes) return []
  
  const relevantNotes = []
  const searchText = text.toLowerCase().trim()
  
  console.log(`🔍 Searching for notes matching: "${text}"`)
  console.log(`📚 Database contains ${Object.keys(macbethNotes).length} scenes`)
  
  // Search through all scenes and lines
  for (const [sceneKey, sceneData] of Object.entries(macbethNotes)) {
    const sceneLineCount = Object.keys(sceneData).length
    console.log(`🎭 Scene ${sceneKey}: ${sceneLineCount} lines`)
    
    for (const [lineKey, lineData] of Object.entries(sceneData)) {
      const playText = lineData.play ? lineData.play.toLowerCase() : ''
      
      // Improved matching algorithm with priority scoring
      let matchScore = 0
      let matchType = 'none'
      
      // Exact match gets highest priority
      if (playText === searchText) {
        matchScore = 100
        matchType = 'exact'
      }
      // Contains match (search text is part of play line)
      else if (playText.includes(searchText) && searchText.length > 3) {
        matchScore = 80
        matchType = 'contains'
      }
      // Play line is part of search text
      else if (searchText.includes(playText) && playText.length > 3) {
        matchScore = 70
        matchType = 'contained'
      }
      // Word-by-word matching for longer texts
      else if (playText.length > 10 && searchText.length > 10) {
        const playWords = playText.split(/\s+/).filter(word => word.length > 2)
        const searchWords = searchText.split(/\s+/).filter(word => word.length > 2)
        
        if (playWords.length > 0 && searchWords.length > 0) {
          const matchingWords = playWords.filter(word => 
            searchWords.some(searchWord => 
              word.includes(searchWord) || searchWord.includes(word)
            )
          )
          
          // If more than 50% of words match, consider it a match
          const matchPercentage = matchingWords.length / Math.min(playWords.length, searchWords.length)
          if (matchPercentage >= 0.5) {
            matchScore = Math.floor(matchPercentage * 60)
            matchType = 'word-match'
          }
        }
      }
      
      // If we have a match, add to relevant notes
      if (matchScore > 0) {
        if (lineData.notes && lineData.notes.length > 0) {
          relevantNotes.push({
            scene: sceneKey,
            line: lineKey,
            play: lineData.play,
            notes: lineData.notes,
            matchScore: matchScore,
            matchType: matchType
          })
          console.log(`✅ Found match in ${sceneKey}, Line ${lineKey}: ${matchType} (score: ${matchScore})`)
        } else {
          console.log(`⚠️ Match found but no notes: ${sceneKey}, Line ${lineKey}`)
        }
      }
    }
  }
  
  // Sort by match score (highest first) and return ALL relevant notes
  relevantNotes.sort((a, b) => b.matchScore - a.matchScore)
  
  console.log(`🎯 Total relevant notes found: ${relevantNotes.length}`)
  console.log(`📊 Match distribution:`, relevantNotes.reduce((acc, note) => {
    acc[note.matchType] = (acc[note.matchType] || 0) + 1
    return acc
  }, {}))
  
  // Return ALL notes, not limited to 5
  return relevantNotes
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

    // Load Macbeth notes database with multiple fallback URLs
    let macbethNotes = null;
    const notesUrls = [
      // Primary: Current site
      `${new URL(request.url).protocol}//${new URL(request.url).hostname}/Public/Data/macbeth_notes.json`,
      // Fallback 1: Netlify deployment
      'https://shakespeare-variorum.netlify.app/Public/Data/macbeth_notes.json',
      // Fallback 2: GitHub raw
      'https://raw.githubusercontent.com/Hassanahmed-15/Shakespeare-Variorum/main/Public/Data/macbeth_notes.json'
    ];
    
    for (const notesUrl of notesUrls) {
      try {
        console.log(`🔄 Attempting to load Macbeth notes from: ${notesUrl}`);
        const notesResponse = await fetch(notesUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          }
        });
        
        if (notesResponse.ok) {
          const responseText = await notesResponse.text();
          console.log(`✅ Successfully loaded from: ${notesUrl}`);
          console.log(`📊 Response size: ${responseText.length} characters`);
          
          macbethNotes = JSON.parse(responseText);
          console.log(`🎭 Database loaded: ${Object.keys(macbethNotes).length} scenes`);
          
          // Log total line count across all scenes
          let totalLines = 0;
          let totalNotes = 0;
          for (const [sceneKey, sceneData] of Object.entries(macbethNotes)) {
            const sceneLines = Object.keys(sceneData).length;
            totalLines += sceneLines;
            
            for (const [lineKey, lineData] of Object.entries(sceneData)) {
              if (lineData.notes && lineData.notes.length > 0) {
                totalNotes += lineData.notes.length;
              }
            }
          }
          console.log(`📈 Total lines in database: ${totalLines}`);
          console.log(`📚 Total note entries: ${totalNotes}`);
          
          break; // Successfully loaded, exit loop
        } else {
          console.log(`❌ Failed to load from ${notesUrl}: Status ${notesResponse.status}`);
        }
      } catch (error) {
        console.error(`❌ Error loading from ${notesUrl}:`, error.message);
      }
    }
    
    if (!macbethNotes) {
      console.error('❌ CRITICAL: Could not load Macbeth notes from any source!');
      return new Response(JSON.stringify({ error: 'Macbeth database unavailable' }), {
        status: 500,
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*'
        }
      });
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
            // Send initial header with database info
            const dbInfo = relevantNotes.length > 0 
              ? `Starting Full Fathom Five analysis with ${relevantNotes.length} historical notes from Macbeth database...`
              : 'Starting Full Fathom Five analysis...';
            
            controller.enqueue(new TextEncoder().encode(`data: {"type": "start", "message": "${dbInfo}"}\n\n`));
            
            // Log database utilization
            console.log(`🎯 Analysis starting with ${relevantNotes.length} relevant notes`);
            if (relevantNotes.length > 0) {
              console.log(`📊 Database utilization: ${relevantNotes.length} notes will be integrated`);
              console.log(`🏆 Top matches:`, relevantNotes.slice(0, 3).map(n => `${n.scene} Line ${n.line} (${n.matchType}: ${n.matchScore})`));
            }

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
              fullPrompt += `\n\nIMPORTANT: You have access to ${relevantNotes.length} historical variorum notes from the Macbeth database. Use these notes extensively in your analysis, especially in the "VARIORUM COMMENTARY" section. Here are the relevant notes found:`;
              
              relevantNotes.forEach((note, index) => {
                fullPrompt += `\n\nNote ${index + 1} (${note.scene}, Line ${note.line}, Match: ${note.matchType}, Score: ${note.matchScore}):\n`;
                fullPrompt += `Text: "${note.play}"\n`;
                fullPrompt += `Historical Notes: ${note.notes.join(' ')}`;
              });
              
              fullPrompt += `\n\nCRITICAL REQUIREMENTS:`;
              fullPrompt += `\n1. Use ALL ${relevantNotes.length} notes in your analysis - do not skip any`;
              fullPrompt += `\n2. Integrate these historical notes extensively in the "VARIORUM COMMENTARY" section`;
              fullPrompt += `\n3. Quote and reference these notes appropriately with proper attribution`;
              fullPrompt += `\n4. Ensure every single note contributes to your analysis`;
              fullPrompt += `\n5. The database contains the complete scholarly archive - use it completely`;
            } else {
              fullPrompt += `\n\nNOTE: No specific historical notes were found in the Macbeth database for this text.`;
              fullPrompt += `\nHowever, you should still provide comprehensive variorum-style analysis based on your knowledge of Shakespearean scholarship.`;
            }

            fullPrompt += `\n\nAnalyze: "${text}"`;

            // Send section start
            controller.enqueue(new TextEncoder().encode('data: {"type": "section", "message": "TEXTUAL COLLATION"}\n\n'));

            // Make Claude API call with streaming
            const claudePayload = {
              model: 'claude-sonnet-4-20250514',
              max_tokens: 8000,
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

            // Send completion signal with database summary
            const completionMessage = relevantNotes.length > 0 
              ? `Analysis complete! Successfully integrated ${relevantNotes.length} historical notes from the complete Macbeth database.`
              : 'Analysis complete!';
            
            controller.enqueue(new TextEncoder().encode(`data: {"type": "complete", "message": "${completionMessage}"}\n\n`));
            controller.close();
            
            // Log completion
            console.log(`✅ Analysis completed successfully`);
            if (relevantNotes.length > 0) {
              console.log(`🎯 Database utilization: ${relevantNotes.length} notes fully integrated`);
              console.log(`📚 Complete scholarly archive utilized`);
            }

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
