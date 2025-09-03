// Variorum Integration - Connects Macbeth Notes to Analyze Text functionality
// This file integrates the macbeth-notes-connector.js with the existing website functionality

class VariorumIntegration {
    constructor() {
        this.isInitialized = false;
    }

    // Initialize the integration
    async initialize() {
        if (this.isInitialized) return;

        try {
            // Ensure the notes connector is loaded
            if (!window.macbethNotesConnector) {
                throw new Error('Macbeth Notes Connector not found');
            }

            await window.macbethNotesConnector.loadNotesData();
            this.isInitialized = true;
            console.log('✅ Variorum Integration initialized');
        } catch (error) {
            console.error('❌ Failed to initialize Variorum Integration:', error);
            throw error;
        }
    }

    // Enhanced analyze text function that includes Macbeth commentary
    async analyzeTextWithCommentary(selectedText, currentScene = null) {
        try {
            await this.initialize();
            
            console.log('🔍 Analyzing text with commentary:', selectedText);
            console.log('🎭 Current scene:', currentScene);

            // Try to find commentary from the Macbeth database
            const commentary = this.findRelevantCommentary(selectedText, currentScene);
            
            // Get the existing analysis (if any)
            const existingAnalysis = await this.getExistingAnalysis(selectedText);
            
            // Combine analysis with commentary
            return this.combineAnalysisWithCommentary(existingAnalysis, commentary, selectedText);
            
        } catch (error) {
            console.error('❌ Error in analyzeTextWithCommentary:', error);
            return {
                success: false,
                error: error.message,
                selectedText: selectedText
            };
        }
    }

    // Find relevant commentary for the selected text
    findRelevantCommentary(selectedText, currentScene) {
        if (!window.macbethNotesConnector || !window.macbethNotesConnector.isLoaded) {
            console.log('⚠️ Notes connector not available');
            return null;
        }

        // Try different strategies to find commentary
        let commentary = null;

        // Strategy 1: If we can determine act/scene/line from context
        const lineInfo = this.extractLineInfo(selectedText, currentScene);
        if (lineInfo) {
            commentary = window.macbethNotesConnector.findCommentaryByLine(
                lineInfo.act, 
                lineInfo.scene, 
                lineInfo.line
            );
        }

        // Strategy 2: Search by text content
        if (!commentary) {
            const results = window.macbethNotesConnector.findCommentaryByText(selectedText);
            if (results && results.length > 0) {
                // Take the best match
                commentary = results[0];
            }
        }

        return commentary;
    }

    // Extract act, scene, and line information from text and context
    extractLineInfo(selectedText, currentScene) {
        // Try to extract line number from the selected text
        const lineMatch = selectedText.match(/^(\d+)\.?\s/);
        if (!lineMatch) {
            return null;
        }

        const lineNumber = parseInt(lineMatch[1]);

        // Try to extract act and scene from current scene context
        if (currentScene) {
            const actMatch = currentScene.match(/ACT\s+(\d+|[IVX]+)/i);
            const sceneMatch = currentScene.match(/SCENE\s+(\d+|[IVX]+)/i);
            
            if (actMatch && sceneMatch) {
                return {
                    act: actMatch[1],
                    scene: sceneMatch[1],
                    line: lineNumber
                };
            }
        }

        // Default to Act 1, Scene 1 if we can't determine from context
        return {
            act: '1',
            scene: '1',
            line: lineNumber
        };
    }

    // Get existing analysis from the current system
    async getExistingAnalysis(selectedText) {
        // This would call the existing analysis function
        // For now, return a placeholder
        return {
            hasExistingAnalysis: false,
            analysis: null
        };
    }

    // Combine AI analysis with historical commentary
    combineAnalysisWithCommentary(existingAnalysis, commentary, selectedText) {
        const result = {
            success: true,
            selectedText: selectedText,
            hasCommentary: commentary && commentary.hasNotes,
            commentary: commentary,
            existingAnalysis: existingAnalysis,
            displayContent: this.generateDisplayContent(existingAnalysis, commentary, selectedText)
        };

        return result;
    }

    // Generate the HTML content to display
    generateDisplayContent(existingAnalysis, commentary, selectedText) {
        let html = '';

        // Add commentary section if available
        if (commentary && commentary.hasNotes) {
            html += window.macbethNotesConnector.formatCommentary(commentary);
        } else {
            // Show that we searched but found nothing
            html += `
                <div class="variorum-commentary">
                    <h3>📚 New Variorum Analysis</h3>
                    <p class="no-notes">No historical commentary found for the selected text.</p>
                    <div class="search-info">
                        <strong>Searched text:</strong> "${selectedText}"
                        <br><em>The database contains extensive commentary for Macbeth. Try selecting a different line or ensure you're viewing Act 1.</em>
                    </div>
                </div>
            `;
        }

        // Add existing analysis if available
        if (existingAnalysis && existingAnalysis.hasExistingAnalysis) {
            html += `
                <div class="ai-analysis">
                    <h3>🤖 AI Analysis</h3>
                    <div class="analysis-content">
                        ${existingAnalysis.analysis}
                    </div>
                </div>
            `;
        }

        return html;
    }

    // Update the New Variorum Analysis section
    updateVariorumSection(commentary) {
        const variorumSection = document.getElementById('variorumSection');
        const variorumContent = document.getElementById('variorumContent');
        
        if (!variorumSection || !variorumContent) {
            console.log('⚠️ Variorum section elements not found');
            return;
        }

        // Show the section
        variorumSection.style.display = 'block';

        // Update content
        if (commentary && commentary.hasNotes) {
            variorumContent.innerHTML = window.macbethNotesConnector.formatCommentary(commentary);
        } else {
            variorumContent.innerHTML = `
                <div class="no-commentary">
                    <p>No historical commentary available for the selected text.</p>
                    <p class="help-text">Try selecting a line from Act 1 of Macbeth to see scholarly notes.</p>
                </div>
            `;
        }
    }

    // Enhanced version of the existing explainHighlighted function
    async enhancedExplainHighlighted() {
        console.log('🔍 Enhanced explainHighlighted called');
        
        // Get selected text (this should work with the existing selection system)
        const selectedText = this.getSelectedText();
        const currentScene = this.getCurrentScene();
        
        if (!selectedText) {
            alert('Please select text in the play first.');
            return;
        }

        console.log('📖 Selected text:', selectedText);
        console.log('🎭 Current scene:', currentScene);

        // Analyze with commentary
        const result = await this.analyzeTextWithCommentary(selectedText, currentScene);
        
        if (result.success) {
            // Update the variorum section with commentary
            this.updateVariorumSection(result.commentary);
            
            // Log results
            if (result.hasCommentary) {
                console.log('✅ Found commentary:', result.commentary);
            } else {
                console.log('⚠️ No commentary found for selected text');
            }
        } else {
            console.error('❌ Analysis failed:', result.error);
        }
    }

    // Get currently selected text from the page
    getSelectedText() {
        // Try to get from global selectedLines variable (if it exists)
        if (typeof selectedLines !== 'undefined' && selectedLines.length > 0) {
            return selectedLines.join('\n');
        }

        // Try to get from browser selection
        const selection = window.getSelection();
        if (selection.toString().trim()) {
            return selection.toString().trim();
        }

        // Try to get from selectedText variable (if it exists)
        if (typeof selectedText !== 'undefined' && selectedText) {
            return selectedText;
        }

        return null;
    }

    // Get current scene context
    getCurrentScene() {
        // Try to get from global currentScene variable (if it exists)
        if (typeof currentScene !== 'undefined' && currentScene) {
            return currentScene;
        }

        // Try to extract from page title or headers
        const sceneTitle = document.querySelector('.scene-title');
        if (sceneTitle) {
            return sceneTitle.textContent.trim();
        }

        // Default fallback
        return 'ACT 1, SCENE 1';
    }
}

// Create global instance
window.variorumIntegration = new VariorumIntegration();

// Enhanced function to replace or augment the existing explainHighlighted
window.enhancedExplainHighlighted = async function() {
    await window.variorumIntegration.enhancedExplainHighlighted();
};

// Function to integrate with existing Analyze Text button
window.integrateWithAnalyzeButton = function() {
    const analyzeButton = document.getElementById('analyzeButton');
    if (analyzeButton) {
        // Store the original onclick handler
        const originalOnClick = analyzeButton.onclick;
        
        // Replace with enhanced version
        analyzeButton.onclick = async function() {
            // Call the enhanced function
            await window.enhancedExplainHighlighted();
            
            // Also call the original function if it exists
            if (originalOnClick && typeof originalOnClick === 'function') {
                originalOnClick.call(this);
            }
        };
        
        console.log('✅ Analyze button enhanced with Macbeth commentary');
    } else {
        console.log('⚠️ Analyze button not found');
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async function() {
    try {
        await window.variorumIntegration.initialize();
        
        // Integrate with the analyze button after a short delay to ensure it exists
        setTimeout(() => {
            window.integrateWithAnalyzeButton();
        }, 1000);
        
        console.log('🎭 Variorum Integration ready!');
    } catch (error) {
        console.error('❌ Failed to initialize Variorum Integration:', error);
    }
});
