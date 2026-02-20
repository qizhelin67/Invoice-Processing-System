"""
Simplified test server with detailed error logging
"""
import sys
import os
import shutil
import tempfile
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Test Server is Running"}

@app.post("/test-upload")
async def test_upload(file: UploadFile = File(...)):
    """Test file upload with detailed logging"""
    print("="*60)
    print("File Upload Test")
    print("="*60)

    try:
        print(f"1. Filename: {file.filename}")
        print(f"2. Content-Type: {file.content_type}")

        # Save file
        temp_dir = Path("uploads/test")
        temp_dir.mkdir(parents=True, exist_ok=True)
        file_path = temp_dir / file.filename

        print(f"3. Saving to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"   File saved: {file_path.exists()}")

        # Test OCR
        print("\n4. Testing OCR...")
        from ocr_processor import OCRProcessor
        processor = OCRProcessor(use_ai=False)
        print("   OCRProcessor created")

        # Check file extension
        file_ext = file_path.suffix.lower()
        print(f"   File extension: {file_ext}")

        if file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            print("   Processing image...")
            result = processor.extract_text_from_image(str(file_path))
            print(f"   Text length: {len(result.get('text', ''))}")
            print(f"   Confidence: {result.get('confidence', 0)}")

            # Extract data
            data = processor.extract_invoice_data(result.get('text', ''))
            print(f"   Category: {data.get('category')}")
            print(f"   Amount: {data.get('amount')}")
            print(f"   Date: {data.get('date')}")
            print(f"   Merchant: {data.get('merchant')}")

        elif file_ext == '.pdf':
            print("   Processing PDF...")
            result = processor.extract_text_from_pdf(str(file_path))
            print(f"   Text length: {len(result.get('text', ''))}")
            print(f"   Method: {result.get('method')}")

            # Extract data
            data = processor.extract_invoice_data(result.get('text', ''))
            print(f"   Category: {data.get('category')}")
            print(f"   Amount: {data.get('amount')}")

        else:
            print(f"   Unsupported format: {file_ext}")
            return JSONResponse({
                "success": False,
                "error": f"Unsupported file format: {file_ext}"
            })

        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)

        return JSONResponse({
            "success": True,
            "filename": file.filename,
            "category": data.get('category'),
            "amount": data.get('amount'),
            "date": data.get('date'),
            "merchant": data.get('merchant')
        })

    except Exception as e:
        print("\n" + "="*60)
        print("ERROR!")
        print("="*60)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*60)

        return JSONResponse({
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        })

if __name__ == "__main__":
    print("\nStarting test server...")
    print("Open: http://127.0.0.1:8000")
    print("Upload endpoint: POST /test-upload")
    print("\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)
