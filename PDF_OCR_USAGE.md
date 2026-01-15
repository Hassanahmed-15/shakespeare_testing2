# PDF OCR Processing Guide

## Overview

Two scripts for processing PDF files of Shakespeare plays:
1. **analyze.py** - Analyzes PDF structure to determine type and format
2. **ocr.py** - Extracts text using OCR and converts to JSON format

## Installation

### 1. Install Python dependencies:
```bash
pip install -r requirements_ocr.txt
```

### 2. Install system dependencies:

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
- Download and install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
- Download and install Poppler: https://github.com/oschwartz10612/poppler-windows/releases/

## Usage

### Step 1: Analyze the PDF
```bash
python analyze.py henry1.pdf
```

This will:
- Determine if the PDF is text-based or scanned
- Detect Act/Scene structure
- Check if OCR is needed
- Provide recommendations

### Step 2: Extract text and convert to JSON
```bash
python ocr.py henry1.pdf henry1.json
```

Or let it auto-generate the output filename:
```bash
python ocr.py henry1.pdf
# Outputs to: Public/Data/henry1.json
```

**Optional: Adjust OCR quality (higher DPI = better quality but slower):**
```bash
python ocr.py henry1.pdf henry1.json --dpi=400
```

## Output Format

The JSON output matches the format of `much_ado_about_nothing.json`:
```json
{
  "DRAMATIS PERSONAE": {
    "1": {
      "play": "...",
      "notes": []
    }
  },
  "ACT 1 SCENE 1": {
    "1": {
      "play": "Enter LEONATO, HERO, and BEATRICE, with a Messenger"
    },
    "2": {
      "play": "LEONATO: I learn in this letter..."
    },
    ...
  },
  ...
}
```

## Notes

- The scripts automatically detect Act/Scene headers (various formats supported)
- Character names and stage directions are preserved
- Consecutive lines from the same character are merged
- DRAMATIS PERSONAE is detected if present

