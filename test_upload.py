"""Test file upload and OCR processing"""
import sys
import os
from pathlib import Path

print("="*60)
print("Testing Invoice Processing Components")
print("="*60)

# Test 1: Check Tesseract
print("\n[Test 1] Tesseract OCR Check")
try:
    import pytesseract
    version = pytesseract.get_tesseract_version()
    print(f"[OK] Tesseract version: {version}")
except Exception as e:
    print(f"[ERROR] Tesseract: {e}")
    sys.exit(1)

# Test 2: Import modules
print("\n[Test 2] Import Modules")
try:
    from ocr_processor import OCRProcessor
    print("[OK] OCRProcessor imported")

    from classifier import Invoice, InvoiceOrganizer
    print("[OK] Classifier imported")

    from report_generator import ExcelReportGenerator
    print("[OK] ReportGenerator imported")

    import uvicorn
    print("[OK] Uvicorn imported")
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Create processor
print("\n[Test 3] Create OCR Processor")
try:
    processor = OCRProcessor(use_ai=False)
    print("[OK] OCRProcessor created successfully")
except Exception as e:
    print(f"[ERROR] Failed to create processor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Test text extraction with dummy image
print("\n[Test 4] Test Image Processing")
try:
    from PIL import Image
    import numpy as np

    # Create a simple test image
    test_image = Image.new('RGB', (100, 50), color='white')
    test_path = Path('test_image.jpg')
    test_image.save(test_path)

    # Try OCR
    result = processor.extract_text_from_image(str(test_path))
    print(f"[OK] Image processed")
    print(f"     Text extracted: {result['text'][:50]}...")

    # Clean up
    test_path.unlink()

except Exception as e:
    print(f"[ERROR] Image processing failed: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check directories
print("\n[Test 5] Check Directories")
dirs_to_check = ['uploads', 'results', 'templates']
for dir_name in dirs_to_check:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"[OK] {dir_name}/ exists")
    else:
        print(f"[WARNING] {dir_name}/ does not exist")

# Test 6: Check templates
print("\n[Test 6] Check Templates")
templates = ['index.html', 'results.html']
for template in templates:
    template_path = Path('templates') / template
    if template_path.exists():
        print(f"[OK] {template} exists")
    else:
        print(f"[ERROR] {template} not found!")

print("\n" + "="*60)
print("Test Complete")
print("="*60)

print("\nIf all tests passed, the issue might be in the web server.")
print("Try running: python main.py --web")
print("And check the terminal for detailed error messages.")
