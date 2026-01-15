"""
Analyze PDF structure to determine:
- Whether it's text-based or scanned (needs OCR)
- Act/Scene structure and formatting
- Page layout patterns
- Text density
"""

import sys
import os
from pdf2image import convert_from_path
import pdfplumber
from PIL import Image
import pytesseract
import re

def analyze_pdf(pdf_path):
    """Analyze a PDF file to determine its structure and type"""
    
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found!")
        return None
    
    print(f"Analyzing PDF: {pdf_path}")
    print("=" * 60)
    
    analysis = {
        'file_path': pdf_path,
        'file_size_mb': os.path.getsize(pdf_path) / (1024 * 1024),
        'is_text_based': False,
        'needs_ocr': False,
        'page_count': 0,
        'has_acts_scenes': False,
        'act_scene_pattern': None,
        'sample_text': [],
        'layout_type': 'unknown',
        'text_density': 'unknown'
    }
    
    # Try to extract text directly (text-based PDF)
    print("\n1. Checking if PDF is text-based...")
    try:
        with pdfplumber.open(pdf_path) as pdf:
            analysis['page_count'] = len(pdf.pages)
            print(f"   Total pages: {analysis['page_count']}")
            
            text_samples = []
            total_text_length = 0
            
            # Check first 3 pages and last page
            pages_to_check = [0, 1, 2] + ([len(pdf.pages) - 1] if len(pdf.pages) > 3 else [])
            
            for page_num in pages_to_check:
                if page_num < len(pdf.pages):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    if text:
                        text_samples.append({
                            'page': page_num + 1,
                            'text_length': len(text),
                            'preview': text[:200].replace('\n', ' ')
                        })
                        total_text_length += len(text)
            
            if total_text_length > 100:  # Has significant text
                analysis['is_text_based'] = True
                analysis['sample_text'] = text_samples
                print(f"   ✓ PDF is text-based")
                if text_samples:
                    print(f"   Sample text from page 1: {text_samples[0]['preview'][:100]}...")
            else:
                print(f"   ✗ PDF appears to be scanned (low text content)")
                analysis['needs_ocr'] = True
                
    except Exception as e:
        print(f"   Warning: Could not extract text directly: {e}")
        analysis['needs_ocr'] = True
    
    # Check for Act/Scene patterns in extracted text
    if analysis['is_text_based'] and analysis['sample_text']:
        print("\n2. Analyzing Act/Scene structure...")
        all_text = ' '.join([s['preview'] for s in analysis['sample_text']])
        
        # Common patterns for acts and scenes (including Latin format)
        act_patterns = [
            r'ACT\s+[IVX0-9]+',
            r'Act\s+[IVX0-9]+',
            r'ACT\s+[IVX0-9]+:',
            r'Act\s+[IVX0-9]+:',
            r'\[Actus\s+\w+\.',  # Latin: [Actus Primus.
        ]
        
        scene_patterns = [
            r'SCENE\s+[IVX0-9]+',
            r'Scene\s+[IVX0-9]+',
            r'SCENE\s+[IVX0-9]+:',
            r'Scene\s+[IVX0-9]+:',
            r'ACT\s+[IVX0-9]+\s+SCENE\s+[IVX0-9]+',
            r'Act\s+[IVX0-9]+\s+Scene\s+[IVX0-9]+',
            r'ACT\s+[IVX0-9]+[,\s]+SC\.?\s*[IVX0-9]+',  # ACT I, SC. i
            r'\[Actus\s+\w+\.\s+Sc[æa]na\s+\w+\]',  # Latin format
        ]
        
        for pattern in act_patterns:
            if re.search(pattern, all_text, re.IGNORECASE):
                analysis['has_acts_scenes'] = True
                analysis['act_scene_pattern'] = pattern
                print(f"   ✓ Found Act/Scene structure")
                print(f"   Pattern: {pattern}")
                break
        
        if not analysis['has_acts_scenes']:
            print("   ✗ Could not detect clear Act/Scene structure")
            print("   (Will attempt to detect during OCR processing)")
    
    # If needs OCR, check first page as image
    if analysis['needs_ocr'] or not analysis['is_text_based']:
        print("\n3. Checking PDF as scanned images...")
        try:
            # Convert first page to image
            images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=150)
            if images:
                print("   ✓ PDF can be converted to images for OCR")
                
                # Quick OCR test on first page
                test_text = pytesseract.image_to_string(images[0])
                if len(test_text.strip()) > 50:
                    print(f"   ✓ OCR test successful (extracted {len(test_text)} chars from first page)")
                    analysis['needs_ocr'] = True
                    
                    # Check for Act/Scene in OCR'd text
                    if re.search(r'ACT\s+[IVX0-9]+|Act\s+[IVX0-9]+', test_text, re.IGNORECASE):
                        analysis['has_acts_scenes'] = True
                        print(f"   ✓ Found Act/Scene structure in scanned text")
                else:
                    print("   ✗ OCR test extracted very little text")
        except Exception as e:
            print(f"   Warning: Could not test OCR: {e}")
            print("   Make sure you have:")
            print("   - Tesseract OCR installed")
            print("   - pdf2image dependencies (poppler)")
    
    # Determine layout type
    print("\n4. Determining layout type...")
    if analysis['is_text_based']:
        if analysis['has_acts_scenes']:
            analysis['layout_type'] = 'structured_play'
            print("   Layout: Structured play text with Acts/Scenes")
        else:
            analysis['layout_type'] = 'plain_text'
            print("   Layout: Plain text (may need manual structuring)")
    else:
        analysis['layout_type'] = 'scanned_document'
        print("   Layout: Scanned document (requires OCR)")
    
    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    print(f"File size: {analysis['file_size_mb']:.2f} MB")
    print(f"Pages: {analysis['page_count']}")
    print(f"Text-based: {analysis['is_text_based']}")
    print(f"Needs OCR: {analysis['needs_ocr']}")
    print(f"Has Acts/Scenes: {analysis['has_acts_scenes']}")
    if analysis['act_scene_pattern']:
        print(f"Act/Scene pattern: {analysis['act_scene_pattern']}")
    print(f"Layout type: {analysis['layout_type']}")
    print("=" * 60)
    
    return analysis

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze.py <pdf_file>")
        print("Example: python analyze.py henry1.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    analysis = analyze_pdf(pdf_path)
    
    if analysis:
        print("\nRecommendation:")
        if analysis['needs_ocr']:
            print("  → Run: python ocr.py <pdf_file> <output_json>")
        elif analysis['is_text_based']:
            print("  → You can use pdfplumber directly, but OCR may still be needed")
            print("  → Run: python ocr.py <pdf_file> <output_json>")
        else:
            print("  → Unable to determine PDF type. Try OCR anyway.")

if __name__ == "__main__":
    main()
