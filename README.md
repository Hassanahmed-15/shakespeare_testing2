# Shakespeare Variorum Digital Edition

A comprehensive digital platform for exploring Shakespeare's plays with integrated New Variorum commentary and analysis tools.

## Overview

This project provides an interactive web application that combines Shakespeare's original texts with scholarly commentary from the New Variorum editions. Users can navigate through plays, access detailed character lists (Dramatis Personae), and explore extensive critical analysis from centuries of Shakespeare scholarship.

## Features

### 📚 Complete Play Library
- **21 Shakespeare Plays** including major works like Hamlet, Macbeth, King Lear, Romeo and Juliet, and Othello
- **Dramatis Personae** for each play with properly formatted character lists
- **Scene-by-scene navigation** with easy access to any act or scene

### 🔍 Advanced Analysis Tools
- **Three Analysis Modes:**
  - **Basic**: Simple AI-powered text analysis
  - **Expert**: Advanced literary analysis with contextual insights
  - **Full Fathom Five**: Traditional New Variorum commentary integration

### 📖 New Variorum Integration
- **Five Core Plays** with full New Variorum Analysis:
  - Hamlet (analysis only, no critics list)
  - Macbeth (with critics bibliography)
  - King Lear (with German critics list)
  - Romeo and Juliet (with English works, editions & translations, French & German criticism)
  - Othello (with comprehensive critics list)

### 🎭 Critics & Authorities
- **Extensive Bibliography** of Shakespeare scholars and critics
- **Multi-language Sources** including German, French, Italian, and other European scholarship
- **Historical Context** spanning from 18th-century pioneers to modern critics

## Technical Architecture

### Frontend
- **Pure HTML/CSS/JavaScript** - No external frameworks required
- **Responsive Design** - Works on desktop, tablet, and mobile devices
- **Modern UI** - Clean, accessible interface with dark/light theme support

### Data Structure
- **JSON-based Play Data** - Each play stored as structured JSON with scenes, characters, and notes
- **Modular Design** - Easy to add new plays or update existing ones
- **Optimized Loading** - Efficient parsing and display of large text files

### File Organization
```
├── index.html              # Main application file
├── styles/                 # CSS styling
│   ├── modern-ui.css      # Main stylesheet
│   └── tokens.css         # Design tokens
├── Public/Data/           # Play data files
│   ├── *.json            # Individual play files
│   ├── app.js            # Legacy application logic
│   └── notes-integration.js # Notes processing
└── functions/             # Serverless functions (Netlify)
```

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Local web server (for development)

### Installation
1. Clone or download the repository
2. Open `index.html` in a web browser, or
3. Serve the files using a local web server:
   ```bash
   # Using Python
   python -m http.server 8000
   
   # Using Node.js
   npx serve .
   ```

### Usage
1. **Select a Play**: Choose from the dropdown in the sidebar
2. **Navigate**: Click on scenes in the left navigation panel
3. **Analyze Text**: Select text and choose an analysis mode
4. **Explore Commentary**: Access New Variorum critics lists for supported plays

## Supported Plays

### Full New Variorum Integration
- **Hamlet** - Complete analysis with character studies
- **Macbeth** - Full commentary with critics bibliography
- **King Lear** - German scholarship integration
- **Romeo and Juliet** - Multi-language editions and criticism
- **Othello** - Comprehensive critics database

### Standard Plays
- As You Like It
- Coriolanus
- Cymbeline
- Henry IV (Parts 1 & 2)
- Julius Caesar
- King John
- Love's Labour's Lost
- Merchant of Venice
- Midsummer Night's Dream
- Much Ado About Nothing
- Richard II & III
- The Tempest
- The Winter's Tale
- Troilus and Cressida
- Twelfth Night

## Development

### Adding New Plays
1. Create a JSON file in `Public/Data/`
2. Follow the existing structure with scenes and Dramatis Personae
3. Update the play loading logic in `index.html`

### Customizing Analysis
- Modify the analysis modes in the JavaScript functions
- Add new critics lists for additional plays
- Extend the New Variorum integration

## Browser Compatibility

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## Contributing

This project welcomes contributions for:
- Adding new plays or improving existing ones
- Enhancing the analysis tools
- Expanding the critics database
- Improving accessibility and usability

## License

This project is part of the Shakespeare Variorum digital initiative, designed for educational and scholarly purposes.

## Acknowledgments

- New Variorum Shakespeare series
- Historical Shakespeare scholars and critics
- Modern digital humanities community
- Open source web technologies

---

**Version**: 2.0  
**Last Updated**: 2024  
**Maintainer**: Shakespeare Variorum Digital Project
