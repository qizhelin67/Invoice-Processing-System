"""Diagnostic Script - Check System Dependencies"""
import sys
import os
from pathlib import Path

print("="*60)
print("Invoice Processing System - Diagnostic Tool")
print("="*60)

# Check Python version
print(f"\n1. Python version: {sys.version}")

# Check packages
print("\n2. Checking packages:")
packages = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'pytesseract': 'pytesseract',
    'PIL': 'Pillow',
    'cv2': 'opencv-python',
    'fitz': 'PyMuPDF',
    'openpyxl': 'openpyxl',
    'pandas': 'pandas',
    'openai': 'openai'
}

for pkg_name, install_name in packages.items():
    try:
        if pkg_name == 'PIL':
            import PIL
            print(f"   [OK] Pillow: {PIL.__version__}")
        elif pkg_name == 'cv2':
            import cv2
            print(f"   [OK] opencv-python: {cv2.__version__}")
        elif pkg_name == 'fitz':
            import fitz
            print(f"   [OK] PyMuPDF: {fitz.version}")
        else:
            mod = __import__(pkg_name)
            version = getattr(mod, '__version__', 'installed')
            print(f"   [OK] {pkg_name}: {version}")
    except ImportError:
        print(f"   [MISSING] {pkg_name}")

# Check Tesseract OCR
print("\n3. Checking Tesseract OCR:")
try:
    import pytesseract
    try:
        version = pytesseract.get_tesseract_version()
        print(f"   [OK] Tesseract installed: {version}")
    except Exception as e:
        print(f"   [ERROR] Tesseract not installed")
        print(f"   Error: {e}")
        print(f"\n   Solution:")
        print(f"   1. Download: https://github.com/UB-Mannheim/tesseract/wiki")
        print(f"   2. Install to: C:\\Program Files\\Tesseract-OCR")
        print(f"   3. Restart server")
except ImportError:
    print(f"   [ERROR] pytesseract package not installed")

# Check .env file
print("\n4. Checking configuration:")
env_file = Path(".env")
if env_file.exists():
    print(f"   [OK] .env file exists")
    with open('.env', encoding='utf-8') as f:
        content = f.read()
        if 'OPENAI_API_KEY' in content and len(content.split('OPENAI_API_KEY=')[1].strip()) > 0:
            print(f"   [OK] OPENAI_API_KEY configured")
        else:
            print(f"   [INFO] OPENAI_API_KEY not set (using rule-based extraction)")
else:
    print(f"   [INFO] .env file not found (optional)")

# Test basic functionality
print("\n5. Testing basic functionality:")
try:
    from ocr_processor import OCRProcessor
    processor = OCRProcessor(use_ai=False)
    print(f"   [OK] OCRProcessor created")

    # Test rule-based extraction
    test_text = "Test Invoice Amount: 100.00 Date: 2024-01-15"
    result = processor.extract_invoice_data(test_text)
    print(f"   [OK] Rule extraction test passed")
    print(f"      Category: {result.get('category')}")
    print(f"      Amount: {result.get('amount')}")

except Exception as e:
    print(f"   [ERROR] Function test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("Diagnostic Complete")
print("="*60)

print("\nSUMMARY:")
print("If Tesseract shows [ERROR], you need to install it.")
print("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
print("\nAll other packages should show [OK].")
