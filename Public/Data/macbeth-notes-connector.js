// Macbeth Notes Database Connector
// Connects macbeth_notes_cleaned_play.json to the Shakespeare Variorum website

class MacbethNotesConnector {
    constructor() {
        this.notesData = null;
        this.isLoaded = false;
        this.loadingPromise = null;
    }

    // Load and parse the macbeth_notes_cleaned_play.json file
    async loadNotesData() {
        if (this.loadingPromise) {
            return this.loadingPromise;
        }

        this.loadingPromise = this._loadNotesData();
        return this.loadingPromise;
    }

    async _loadNotesData() {
        if (this.isLoaded && this.notesData) {
            return this.notesData;
        }

        try {
            console.log('🔄 Loading Macbeth notes database...');
            
            // Try multiple possible paths for the JSON file
            const possiblePaths = [
                '/Public/Data/macbeth_notes_cleaned_play.json',
                './Public/Data/macbeth_notes_cleaned_play.json',
                'Public/Data/macbeth_notes_cleaned_play.json',
                '/macbeth_notes_cleaned_play.json',
                './macbeth_notes_cleaned_play.json',
                'macbeth_notes_cleaned_play.json'
            ];

            for (const path of possiblePaths) {
                try {
                    console.log(`🔍 Trying to load from: ${path}`);
                    const response = await fetch(path);
                    
                    if (response.ok) {
                        const text = await response.text();
                        this.notesData = JSON.parse(text);
                        this.isLoaded = true;
                        
                        console.log('✅ Successfully loaded Macbeth notes database');
                        console.log(`📊 Database contains ${Object.keys(this.notesData).length} scenes`);
                        
                        // Log scene summary
                        let totalLines = 0;
                        let totalNotes = 0;
                        for (const [sceneName, sceneData] of Object.entries(this.notesData)) {
                            const sceneLines = Object.keys(sceneData).length;
                            totalLines += sceneLines;
                            
                            for (const [lineNumber, lineData] of Object.entries(sceneData)) {
                                if (lineData.notes && lineData.notes.length > 0) {
                                    totalNotes += lineData.notes.length;
                                }
                            }
                        }
                        console.log(`📈 Total lines: ${totalLines}, Total notes: ${totalNotes}`);
                        
                        return this.notesData;
                    }
                } catch (error) {
                    console.log(`❌ Failed to load from ${path}: ${error.message}`);
                }
            }
            
            throw new Error('Could not load macbeth_notes_cleaned_play.json from any location');
            
        } catch (error) {
            console.error('❌ Error loading Macbeth notes:', error);
            this.isLoaded = false;
            throw error;
        }
    }

    // Search for commentary by act, scene, and line number
    findCommentaryByLine(act, scene, lineNumber) {
        if (!this.isLoaded || !this.notesData) {
            console.warn('⚠️ Notes database not loaded');
            return null;
        }

        // Create scene key in the format used by the JSON file
        const sceneKey = `ACT ${act}, SCENE ${scene}`;
        
        console.log(`🔍 Searching for: ${sceneKey}, Line ${lineNumber}`);
        
        if (!this.notesData[sceneKey]) {
            console.log(`❌ Scene not found: ${sceneKey}`);
            return null;
        }

        const sceneData = this.notesData[sceneKey];
        const lineData = sceneData[lineNumber.toString()];
        
        if (!lineData) {
            console.log(`❌ Line not found: ${lineNumber} in ${sceneKey}`);
            return null;
        }

        console.log(`✅ Found line data for ${sceneKey}, Line ${lineNumber}`);
        
        return {
            act: act,
            scene: scene,
            lineNumber: lineNumber,
            sceneKey: sceneKey,
            playText: lineData.play,
            notes: lineData.notes || [],
            hasNotes: lineData.notes && lineData.notes.length > 0
        };
    }

    // Search for commentary by text content (when act/scene/line not known)
    findCommentaryByText(searchText) {
        if (!this.isLoaded || !this.notesData) {
            console.warn('⚠️ Notes database not loaded');
            return [];
        }

        const results = [];
        const searchLower = searchText.toLowerCase().trim();
        
        console.log(`🔍 Searching for text: "${searchText}"`);

        // Extract line numbers from the search text if present
        const lineNumbers = this.extractLineNumbers(searchText);
        
        // Search through all scenes
        for (const [sceneKey, sceneData] of Object.entries(this.notesData)) {
            for (const [lineNumber, lineData] of Object.entries(sceneData)) {
                if (!lineData.play) continue;
                
                const playText = lineData.play.toLowerCase().trim();
                let matchScore = 0;
                let matchType = 'none';

                // If we found line numbers in the search text, prioritize exact line matches
                if (lineNumbers.length > 0 && lineNumbers.includes(parseInt(lineNumber))) {
                    matchScore = 100;
                    matchType = 'line_number';
                } 
                // Exact text match
                else if (playText === searchLower) {
                    matchScore = 95;
                    matchType = 'exact';
                }
                // Search text contains the play line
                else if (searchLower.includes(playText) && playText.length > 5) {
                    matchScore = 85;
                    matchType = 'contains_play';
                }
                // Play line contains the search text
                else if (playText.includes(searchLower) && searchLower.length > 5) {
                    matchScore = 80;
                    matchType = 'contains_search';
                }
                // Word-based matching
                else {
                    const wordMatch = this.calculateWordMatch(playText, searchLower);
                    if (wordMatch > 0.4) { // 40% word match threshold
                        matchScore = Math.floor(wordMatch * 70);
                        matchType = 'word_match';
                    }
                }

                if (matchScore > 0) {
                    const [act, scene] = this.parseSceneKey(sceneKey);
                    results.push({
                        act: act,
                        scene: scene,
                        lineNumber: parseInt(lineNumber),
                        sceneKey: sceneKey,
                        playText: lineData.play,
                        notes: lineData.notes || [],
                        hasNotes: lineData.notes && lineData.notes.length > 0,
                        matchScore: matchScore,
                        matchType: matchType
                    });
                }
            }
        }

        // Sort by match score (highest first)
        results.sort((a, b) => b.matchScore - a.matchScore);
        
        console.log(`✅ Found ${results.length} matches for "${searchText}"`);
        return results;
    }

    // Extract line numbers from text (e.g., "5. When shall we three meet again" -> [5])
    extractLineNumbers(text) {
        const lineNumbers = [];
        const matches = text.match(/\b(\d+)\.?\s/g);
        
        if (matches) {
            for (const match of matches) {
                const num = parseInt(match.replace(/[^\d]/g, ''));
                if (num > 0 && num < 1000) { // Reasonable line number range
                    lineNumbers.push(num);
                }
            }
        }
        
        return lineNumbers;
    }

    // Calculate word match percentage between two texts
    calculateWordMatch(text1, text2) {
        const words1 = text1.split(/\s+/).filter(word => word.length > 2);
        const words2 = text2.split(/\s+/).filter(word => word.length > 2);
        
        if (words1.length === 0 || words2.length === 0) return 0;
        
        const matchingWords = words1.filter(word => 
            words2.some(searchWord => 
                word.includes(searchWord) || searchWord.includes(word)
            )
        );
        
        return matchingWords.length / Math.min(words1.length, words2.length);
    }

    // Parse scene key to extract act and scene numbers
    parseSceneKey(sceneKey) {
        const actMatch = sceneKey.match(/ACT (\d+|[IVX]+)/i);
        const sceneMatch = sceneKey.match(/SCENE (\d+|[IVX]+)/i);
        
        const act = actMatch ? actMatch[1] : '1';
        const scene = sceneMatch ? sceneMatch[1] : '1';
        
        return [act, scene];
    }

    // Format commentary for display
    formatCommentary(commentaryData) {
        if (!commentaryData || !commentaryData.hasNotes) {
            return `
                <div class="variorum-commentary">
                    <h3>📚 New Variorum Analysis</h3>
                    <p class="no-notes">No historical commentary available for this line.</p>
                    <div class="line-info">
                        <strong>Line:</strong> ${commentaryData ? commentaryData.playText : 'Unknown'}
                        <br><strong>Location:</strong> ${commentaryData ? commentaryData.sceneKey + ', Line ' + commentaryData.lineNumber : 'Unknown'}
                    </div>
                </div>
            `;
        }

        let html = `
            <div class="variorum-commentary">
                <h3>📚 New Variorum Analysis</h3>
                <div class="line-info">
                    <strong>Line ${commentaryData.lineNumber}:</strong> "${commentaryData.playText}"
                    <br><strong>Location:</strong> ${commentaryData.sceneKey}
                </div>
                <div class="commentary-content">
        `;

        commentaryData.notes.forEach((note, index) => {
            html += `
                <div class="note-entry">
                    <div class="note-text">${this.formatNoteText(note)}</div>
                </div>
            `;
        });

        html += `
                </div>
            </div>
        `;

        return html;
    }

    // Format individual note text with basic markup
    formatNoteText(note) {
        return note
            .replace(/\n/g, '<br>')
            .replace(/\[([^\]]+)\]/g, '<em>$1</em>')
            .replace(/—([^—]+)—/g, '<strong>$1</strong>')
            .replace(/\.\.\./g, '…');
    }

    // Get all available scenes
    getAvailableScenes() {
        if (!this.isLoaded || !this.notesData) {
            return [];
        }
        
        return Object.keys(this.notesData).sort();
    }

    // Get statistics about the database
    getDatabaseStats() {
        if (!this.isLoaded || !this.notesData) {
            return null;
        }

        let totalLines = 0;
        let totalNotes = 0;
        let scenesWithNotes = 0;

        for (const [sceneKey, sceneData] of Object.entries(this.notesData)) {
            const sceneLines = Object.keys(sceneData).length;
            totalLines += sceneLines;
            
            let sceneHasNotes = false;
            for (const [lineNumber, lineData] of Object.entries(sceneData)) {
                if (lineData.notes && lineData.notes.length > 0) {
                    totalNotes += lineData.notes.length;
                    sceneHasNotes = true;
                }
            }
            
            if (sceneHasNotes) scenesWithNotes++;
        }

        return {
            totalScenes: Object.keys(this.notesData).length,
            totalLines: totalLines,
            totalNotes: totalNotes,
            scenesWithNotes: scenesWithNotes
        };
    }
}

// Create global instance
window.macbethNotesConnector = new MacbethNotesConnector();

// Auto-load when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    try {
        await window.macbethNotesConnector.loadNotesData();
        console.log('🎭 Macbeth Notes Connector ready!');
    } catch (error) {
        console.error('❌ Failed to initialize Macbeth Notes Connector:', error);
    }
});
