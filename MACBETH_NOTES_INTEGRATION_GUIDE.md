# Macbeth Notes Integration Guide

## Overview

This guide explains how your `macbeth_notes_cleaned_play.json` database has been successfully connected to your Shakespeare Variorum website. Users can now select lines from Macbeth and see historical scholarly commentary alongside AI analysis.

## What Was Implemented

### 1. **Database Connector** (`MacbethNotesConnector` class)
- **Location**: Integrated directly into `index.html`
- **Purpose**: Loads and searches the `macbeth_notes_cleaned_play.json` file
- **Features**:
  - Automatic loading from multiple possible file paths
  - Smart text matching (exact, partial, word-based)
  - Line number extraction from selected text
  - Comprehensive error handling

### 2. **Enhanced Analyze Text Functionality**
- **Function**: `explainHighlightedWithCommentary()`
- **Integration**: Replaces the original `explainHighlighted()` function
- **Features**:
  - Searches for relevant commentary when text is selected
  - Displays results in the "New Variorum Analysis" section
  - Works seamlessly with existing AI analysis

### 3. **User Interface Enhancements**
- **New Section**: Enhanced "New Variorum Analysis" display
- **Styling**: Custom CSS for commentary display
- **Features**:
  - Formatted scholarly notes with proper attribution
  - Line information and location context
  - Scrollable content for long commentary
  - Helpful messages when no commentary is found

## How It Works

### For Users:

1. **Load a Macbeth Scene**: Navigate to any scene in Macbeth
2. **Select Text**: Click on a line or highlight text containing line numbers
3. **Switch to Full Fathom Five**: Click the "Full Fathom Five" analysis tab
4. **Click "Analyze Text"**: The enhanced button will:
   - Search the Macbeth database for matching commentary
   - Display historical notes in the "New Variorum Analysis" section
   - Continue with regular AI analysis

### Behind the Scenes:

1. **Database Loading**: The system automatically loads `macbeth_notes_cleaned_play.json` when the page loads
2. **Text Analysis**: When "Analyze Text" is clicked:
   - Extracts line numbers from selected text (e.g., "5. When shall we three meet again")
   - Searches the database using multiple matching strategies:
     - Exact line number matches
     - Exact text matches
     - Partial text matches
     - Word-based similarity matching
3. **Result Display**: Shows the best matching commentary with:
   - Original line text
   - Scene and line number
   - Complete scholarly notes
   - Proper formatting and styling

## Database Structure

The system expects your JSON file to have this structure:

```json
{
  "ACT 1, SCENE 1": {
    "1": {
      "play": "First Witch: When shall we three meet again",
      "notes": [
        "Historical commentary text here..."
      ]
    },
    "2": {
      "play": "In thunder, lightning, or in rain?",
      "notes": [
        "More commentary..."
      ]
    }
  }
}
```

## File Locations

The system will automatically search for your JSON file in these locations:
- `/Public/Data/macbeth_notes_cleaned_play.json`
- `./Public/Data/macbeth_notes_cleaned_play.json`
- `Public/Data/macbeth_notes_cleaned_play.json`
- `/macbeth_notes_cleaned_play.json`
- `./macbeth_notes_cleaned_play.json`
- `macbeth_notes_cleaned_play.json`

**Recommended**: Place the file at `Public/Data/macbeth_notes_cleaned_play.json`

## Testing the Integration

### Test Case 1: Line Number Selection
1. Load Act 1, Scene 1 of Macbeth
2. Select text like "1. First Witch: When shall we three meet again"
3. Switch to "Full Fathom Five" tab
4. Click "Analyze Text"
5. **Expected**: Commentary appears in "New Variorum Analysis" section

### Test Case 2: Text-Only Selection
1. Select text without line numbers, like "When shall we three meet again"
2. Click "Analyze Text"
3. **Expected**: System finds matching line and displays commentary

### Test Case 3: No Commentary Available
1. Select text that doesn't exist in the database
2. Click "Analyze Text"
3. **Expected**: Helpful message explaining no commentary was found

## Debugging

### Check Browser Console
Open browser developer tools (F12) and look for these messages:
- `🔄 Loading Macbeth notes database...`
- `✅ Successfully loaded Macbeth notes database`
- `🎭 Macbeth Notes Connector ready!`
- `✅ Analyze button enhanced with Macbeth commentary`

### Common Issues and Solutions

**Issue**: "Could not load macbeth_notes_cleaned_play.json"
- **Solution**: Ensure the JSON file is in the `Public/Data/` directory
- **Check**: File name is exactly `macbeth_notes_cleaned_play.json`

**Issue**: "No commentary found"
- **Solution**: Verify the selected text matches entries in your JSON file
- **Check**: Scene names match the format "ACT X, SCENE Y"

**Issue**: Commentary not displaying
- **Solution**: Make sure you're using the "Full Fathom Five" analysis level
- **Check**: The "New Variorum Analysis" section should be visible

## Customization

### Adding More Plays
To extend this system to other plays:
1. Create similar JSON files for other plays
2. Modify the `loadNotesData()` function to load multiple databases
3. Update the search logic to determine which database to use

### Modifying Display Format
Edit the `formatCommentary()` function in the `MacbethNotesConnector` class to change how commentary is displayed.

### Changing Search Behavior
Modify the matching algorithms in `findCommentaryByText()` to adjust how text matches are found and scored.

## Code Architecture

### Main Components:

1. **MacbethNotesConnector**: Core database interface
2. **explainHighlightedWithCommentary()**: Enhanced analysis function
3. **CSS Styles**: Commentary display formatting
4. **Integration Logic**: Connects to existing "Analyze Text" button

### Key Functions:

- `loadNotesData()`: Loads the JSON database
- `findCommentaryByText()`: Searches for relevant commentary
- `formatCommentary()`: Formats commentary for display
- `extractLineNumbers()`: Finds line numbers in selected text
- `calculateWordMatch()`: Computes text similarity scores

## Success Metrics

The integration is working correctly when:
- ✅ Database loads automatically on page load
- ✅ "Analyze Text" button searches the database
- ✅ Commentary appears in "New Variorum Analysis" section
- ✅ No commentary message appears for non-matching text
- ✅ System gracefully handles missing files or errors

## Support

If you encounter issues:
1. Check the browser console for error messages
2. Verify file paths and names match exactly
3. Test with known lines from Act 1, Scene 1
4. Ensure the JSON file is valid and accessible

The system is designed to be robust - if the Macbeth database fails to load, the regular analysis will continue to work normally.
