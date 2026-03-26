"""
Apply PDF Redaction to Specified Pages

This script applies redaction to specified coordinates on specific page ranges of a PDF.

Usage:
    1. Run: python apply_redaction_at_coordinates_globally.py
    2. Select your PDF file from the file picker dialog
    3. Update REDACTION_AREAS with coordinates and page ranges (below)
    4. The output file will be automatically named redacted_{input_filename}

Configuration:
    - REDACT_COLOR: RGB tuple for redaction color (default: black)
    - REDACTION_AREAS: List of dicts with 'coords' and 'pages'

Example:
    REDACTION_AREAS = [
        {"coords": (496.5, 21.0, 526.5, 34.0), "pages": "1-4"},
        {"coords": (100.0, 200.0, 300.0, 250.0), "pages": "2-9"},
        {"coords": (50.0, 50.0, 200.0, 100.0), "pages": "8"},
    ]

Author: PDF Redaction Tool
License: MIT
"""

import fitz
import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox


# ============================================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================================

# Input and Output PDF files will be selected at runtime
INPUT_PDF = None  # Selected via file picker
OUTPUT_PDF = None  # Auto-generated from input filename

# Redaction color (RGB tuple)
# Common options:
#   (0, 0, 0)       - Black (default)
#   (255, 0, 0)     - Red
#   (128, 128, 128) - Gray
#   (255, 255, 255) - White
REDACT_COLOR = (0, 0, 0)

# Redaction areas - List of dicts with 'coords' and 'pages'
# 'coords': (x0, y0, x1, y1) tuple
# 'pages': string like "1-4" for pages 1 to 4, or "8" for page 8
REDACTION_AREAS = [
     {'coords': (68.7, 197.3, 329.3, 225.3), 'pages': '1' },     
    {'coords': (175.3, 296.0, 256.7, 306.0), 'pages': '1' },    
    {'coords': (69.0, 555.0, 148.0, 572.0), 'pages': '1' },     
    {'coords': (68.0, 413.3, 169.3, 432.0), 'pages': '3' },     
    {'coords': (340.0, 626.7, 393.3, 640.0), 'pages': '3' },    
    {'coords': (70.7, 214.7, 150.7, 232.0), 'pages': '3' },     
    {'coords': (414.7, 128.0, 434.7, 240.0), 'pages': '4' }, 
    
    # Add more as needed:
    # {"coords": (100.0, 200.0, 300.0, 250.0), "pages": "2-9"},  # Example: redact on pages 5-20
    # {"coords": (50.0, 50.0, 200.0, 100.0), "pages": "8"},
]


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def parse_page_ranges(page_str):
    """Parse page range string into 0-indexed list.
    
    Examples:
        "1-4" -> [0, 1, 2, 3]
        "8" -> [7]
    """
    try:
        if '-' in page_str:
            start, end = map(int, page_str.split('-'))
            return list(range(start-1, end))
        else:
            return [int(page_str)-1]
    except ValueError:
        raise ValueError(f"Invalid page range format: '{page_str}'. Use '1-4' or '8'.")


# ============================================================================
# EXECUTION
# ============================================================================

def validate_inputs():
    """Validate input before processing."""
    if not os.path.exists(INPUT_PDF):
        print(f"✗ Error: Input PDF not found: {INPUT_PDF}")
        print(f"  Current directory: {os.getcwd()}")
        print(f"  Files in directory: {os.listdir('.')}")
        return False
    
    if not REDACTION_AREAS:
        print("✗ Error: No redaction areas defined")
        
    # Validate each redaction area
    for i, area in enumerate(REDACTION_AREAS):
        if not isinstance(area, dict) or 'coords' not in area or 'pages' not in area:
            print(f"✗ Error: Redaction area {i+1} must be a dict with 'coords' and 'pages' keys")
            return False
        coords = area['coords']
        if not (isinstance(coords, tuple) and len(coords) == 4 and all(isinstance(c, (int, float)) for c in coords)):
            print(f"✗ Error: Redaction area {i+1} 'coords' must be a tuple of 4 numbers")
            return False
        try:
            parse_page_ranges(area['pages'])
        except ValueError as e:
            print(f"✗ Error in redaction area {i+1}: {e}")
            return False
    
    return True


def apply_redaction():
    """Apply redaction to PDF."""
    global INPUT_PDF, OUTPUT_PDF
    
    try:
        # Open file picker to select input PDF
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        INPUT_PDF = filedialog.askopenfilename(
            title="Select PDF file to redact",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not INPUT_PDF:
            print("⚠ No file selected. Exiting.")
            root.destroy()
            return False
        
        root.destroy()
        
        # Auto-generate output filename
        input_path = Path(INPUT_PDF)
        OUTPUT_PDF = str(input_path.parent / f"redacted_{input_path.name}")
        
        # Validate inputs
        if not validate_inputs():
            return False
        
        print("=" * 60)
        print("PDF REDACTION TOOL")
        print("=" * 60)
        print(f"Input file:  {INPUT_PDF}")
        print(f"Output file: {OUTPUT_PDF}")
        print(f"Redaction color: RGB{REDACT_COLOR}")
        print(f"Total redaction areas: {len(REDACTION_AREAS)}")
        for i, area in enumerate(REDACTION_AREAS):
            pages = parse_page_ranges(area['pages'])
            print(f"  Area {i+1}: {area['coords']} on pages {area['pages']} (0-indexed: {pages})")
        print("=" * 60)
        print()
        
        # Open PDF
        print("📄 Opening PDF...")
        pdf = fitz.open(INPUT_PDF)
        total_pages = len(pdf)
        print(f"   ✓ Loaded {total_pages} pages")
        
        # Apply redaction
        print(f"\n🔒 Applying redaction...")
        
        redacted_pages = set()
        for page_num in range(total_pages):
            page = pdf[page_num]
            page_redacted = False
            
            # Check each redaction area
            for area in REDACTION_AREAS:
                pages = parse_page_ranges(area['pages'])
                if page_num in pages:
                    redact_area = fitz.Rect(*area['coords'])
                    page.add_redact_annot(redact_area, fill=REDACT_COLOR)
                    page_redacted = True
            
            # Apply redactions if any were added
            if page_redacted:
                page.apply_redactions()
                redacted_pages.add(page_num)
        
        print(f"   ✓ Redacted {len(redacted_pages)} page(s): {sorted(redacted_pages)}")
        
        # Save redacted PDF
        print(f"\n💾 Saving redacted PDF...")
        pdf.save(OUTPUT_PDF)
        pdf.close()
        
        # Verify output
        if os.path.exists(OUTPUT_PDF):
            file_size = os.path.getsize(OUTPUT_PDF)
            print(f"   ✓ Saved to {OUTPUT_PDF}")
            print(f"   ✓ File size: {file_size / 1024:.1f} KB")
        
        print("\n" + "=" * 60)
        print("✓ SUCCESS - Redaction completed!")
        print("=" * 60)
        print(f"\nNext steps:")
        print(f"  1. Open {OUTPUT_PDF} to verify redaction")
        print(f"  2. Check that all sensitive data is obscured")
        print(f"  3. Keep your original file as backup")
        print()
        
        return True
    
    except FileNotFoundError as e:
        print(f"✗ File Error: {str(e)}")
        return False
    
    except fitz.FileError as e:
        print(f"✗ PDF Error: Invalid or corrupted PDF file")
        print(f"  {str(e)}")
        return False
    
    except Exception as e:
        print(f"✗ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    try:
        success = apply_redaction()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠ Process cancelled by user")
        sys.exit(1)