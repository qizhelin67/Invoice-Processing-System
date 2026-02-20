"""
Invoice Processing System - Main Application
FastAPI web service for invoice OCR, classification, and report generation
"""

import os
import sys
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import uvicorn

# Import our modules
from ocr_processor import OCRProcessor
from classifier import Invoice, InvoiceOrganizer
from report_generator import ExcelReportGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Invoice Processing System",
    description="AI-powered invoice recognition and reimbursement organization",
    version="1.0.0"
)

# Get base directory
BASE_DIR = Path(__file__).parent

# Create directories for uploads and results
UPLOAD_DIR = BASE_DIR / "uploads"
RESULTS_DIR = BASE_DIR / "results"
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Setup templates and static files
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
if (BASE_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Initialize processors
ocr_processor = OCRProcessor(use_ai=True)
organizer = InvoiceOrganizer()
report_generator = ExcelReportGenerator()


# =============================================================================
# Web Routes
# =============================================================================

@app.get("/")
async def index(request: Request):
    """Render main page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload")
async def upload_invoices(
    request: Request,
    files: List[UploadFile] = File(...)
):
    """
    Upload and process invoice files

    Args:
        files: List of uploaded files (images or PDFs)

    Returns:
        JSON response with processing results
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")

    # Create unique session directory
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    # Save uploaded files
    saved_files = []
    for file in files:
        file_path = session_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(str(file_path))

    # Process invoices
    try:
        result = await process_invoices(saved_files, session_id)

        return templates.TemplateResponse(
            "results.html",
            {
                "request": request,
                "session_id": session_id,
                "result": result
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{session_id}")
async def download_results(session_id: str):
    """
    Download processed results as ZIP file

    Args:
        session_id: Session identifier

    Returns:
        ZIP file with organized invoices and Excel report
    """
    zip_path = RESULTS_DIR / f"报销结果_{session_id}.zip"

    if not zip_path.exists():
        raise HTTPException(status_code=404, detail="Results not found")

    return FileResponse(
        path=zip_path,
        filename=f"报销结果_{session_id}.zip",
        media_type="application/zip"
    )


@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "status": "running",
        "ocr_available": True,
        "ai_available": ocr_processor.use_ai,
        "version": "1.0.0"
    }


# =============================================================================
# Processing Logic
# =============================================================================

async def process_invoices(file_paths: List[str], session_id: str) -> Dict[str, Any]:
    """
    Process list of invoice files

    Args:
        file_paths: List of file paths to process
        session_id: Session identifier for this batch

    Returns:
        Processing results with organized invoices
    """
    print(f"\n[DEBUG] Processing {len(file_paths)} files, session: {session_id}")
    invoices = []

    for idx, file_path in enumerate(file_paths):
        print(f"\n[DEBUG] Processing file {idx+1}/{len(file_paths)}: {file_path}")

        try:
            # Extract text based on file type
            file_ext = Path(file_path).suffix.lower()
            print(f"[DEBUG] File extension: {file_ext}")

            if file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                print(f"[DEBUG] Processing as image...")
                ocr_result = ocr_processor.extract_text_from_image(file_path)
                print(f"[DEBUG] OCR result keys: {list(ocr_result.keys())}")
                if 'error' in ocr_result:
                    print(f"[ERROR] OCR failed: {ocr_result['error']}")
            elif file_ext == '.pdf':
                print(f"[DEBUG] Processing as PDF...")
                ocr_result = ocr_processor.extract_text_from_pdf(file_path)
                print(f"[DEBUG] OCR result keys: {list(ocr_result.keys())}")
                if 'error' in ocr_result:
                    print(f"[ERROR] OCR failed: {ocr_result['error']}")
            else:
                print(f"[WARNING] Unsupported file type: {file_ext}")
                continue

            # Extract structured data
            invoice_data = ocr_processor.extract_invoice_data(ocr_result.get('text', ''))
            print(f"[DEBUG] Invoice data extracted: category={invoice_data.get('category')}, amount={invoice_data.get('amount')}")

        except Exception as e:
            print(f"[ERROR] Failed to process {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            continue

        # Create Invoice object
        invoice = Invoice(
            file_path=file_path,
            file_name=Path(file_path).name,
            category=invoice_data.get('category', 'other'),
            amount=invoice_data.get('amount'),
            date=invoice_data.get('date'),
            merchant=invoice_data.get('merchant'),
            invoice_number=invoice_data.get('invoice_number'),
            confidence=ocr_result.get('confidence', 0.0),
            text=ocr_result.get('text', '')
        )

        invoices.append(invoice)

    # Organize invoices
    print(f"\n[DEBUG] Organizing {len(invoices)} invoices...")
    try:
        organized = organizer.organize(invoices)
        print(f"[DEBUG] Organization complete")
    except Exception as e:
        print(f"[ERROR] Organization failed: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Generate Excel report
    print(f"[DEBUG] Generating Excel report...")
    try:
        result_dir = RESULTS_DIR / session_id
        result_dir.mkdir(exist_ok=True)

        report_path = result_dir / f"报销统计_{datetime.now().strftime('%Y%m%d')}.xlsx"
        report_generator.generate_report(organized, str(report_path))
        print(f"[DEBUG] Excel report generated: {report_path}")
    except Exception as e:
        print(f"[ERROR] Excel generation failed: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Organize files into folders
    print(f"[DEBUG] Organizing files into folders...")
    try:
        await organize_files(invoices, organized, result_dir)
        print(f"[DEBUG] File organization complete")
    except Exception as e:
        print(f"[ERROR] File organization failed: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Create ZIP archive
    print(f"[DEBUG] Creating ZIP archive...")
    try:
        zip_path = RESULTS_DIR / f"报销结果_{session_id}.zip"
        create_zip_archive(result_dir, zip_path)
        print(f"[DEBUG] ZIP created: {zip_path}")
    except Exception as e:
        print(f"[ERROR] ZIP creation failed: {e}")
        import traceback
        traceback.print_exc()
        raise

    # Prepare result for display
    print(f"[DEBUG] Preparing result data for display...")

    # Get category info
    from classifier import InvoiceClassifier
    classifier_obj = InvoiceClassifier()

    categories_data = {}
    for cat, org in organized['categorized'].items():
        info = classifier_obj.get_category_info(cat)
        categories_data[cat] = {
            'name': info['name'],
            'icon': info['icon'],
            'count': len(org),
            'items': [
                {
                    'file_name': inv.file_name,
                    'date': inv.date,
                    'amount': inv.amount,
                    'merchant': inv.merchant
                }
                for inv in org
            ][:5]  # Show first 5 items
        }

    print(f"[DEBUG] Result data prepared successfully")
    return {
        'statistics': organized['statistics'],
        'categories': categories_data,
        'zip_url': f"/download/{session_id}",
        'report_path': str(report_path)
    }


async def organize_files(invoices: List[Invoice],
                        organized: Dict[str, Any],
                        result_dir: Path):
    """Organize invoice files into category folders"""

    category_map = {
        'taxi': '打车票',
        'train': '火车飞机票',
        'hotel': '住宿费',
        'dining': '餐费',
        'other': '其他'
    }

    # Copy files to category folders
    for invoice in invoices:
        category_name = category_map.get(invoice.category, '其他')
        category_dir = result_dir / category_name
        category_dir.mkdir(exist_ok=True)

        # Copy file
        dest_path = category_dir / invoice.file_name
        shutil.copy2(invoice.file_path, dest_path)

        # Handle pairs
        for category, pairs in organized['pairs'].items():
            for pair in pairs:
                if pair.receipt == invoice or pair.invoice == invoice:
                    # Create paired folder
                    pair_dir = category_dir / f"{invoice.date}_{invoice.merchant}_{invoice.amount}元"
                    pair_dir.mkdir(exist_ok=True)

                    # Move both files to paired folder
                    shutil.copy2(pair.receipt.file_path, pair_dir / f"01_凭证_{pair.receipt.file_name}")
                    shutil.copy2(pair.invoice.file_path, pair_dir / f"02_发票_{pair.invoice.file_name}")


def create_zip_archive(source_dir: Path, zip_path: Path):
    """Create ZIP archive from directory"""

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in source_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(source_dir)
                zipf.write(file, arcname)


# =============================================================================
# CLI Interface
# =============================================================================

def process_cli(input_dir: str, output_dir: str):
    """
    Process invoices from command line

    Args:
        input_dir: Directory containing invoice files
        output_dir: Directory to save results
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    if not input_path.exists():
        print(f"[ERROR] Input directory not found: {input_dir}")
        sys.exit(1)

    output_path.mkdir(parents=True, exist_ok=True)

    # Collect all invoice files
    file_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.pdf']
    invoice_files = []

    for ext in file_extensions:
        invoice_files.extend(input_path.glob(f'*{ext}'))
        invoice_files.extend(input_path.glob(f'*{ext.upper()}'))

    if not invoice_files:
        print(f"[WARNING] No invoice files found in {input_dir}")
        return

    print(f"Found {len(invoice_files)} invoice files")

    # Process files
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_paths = [str(f) for f in invoice_files]

    print("Processing invoices...")
    result = asyncio.run(process_invoices(file_paths, session_id))

    print("\n" + "="*50)
    print("Processing Complete!")
    print("="*50)
    print(f"Total invoices: {result['statistics']['total_invoices']}")
    print(f"Total pairs: {result['statistics']['total_pairs']}")
    print(f"Grand total: ¥{result['statistics']['grand_total']:,.2f}")

    print("\nBy Category:")
    for cat, stat in result['statistics']['by_category'].items():
        print(f"  {stat['icon']} {stat['name']}: {stat['count']} items, ¥{stat['total_amount']:,.2f}")

    print(f"\nResults saved to: {output_path}")
    print(f"ZIP archive: {RESULTS_DIR / f'报销结果_{session_id}.zip'}")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description="Invoice Processing System")
    parser.add_argument('--web', action='store_true', help='Run web server')
    parser.add_argument('--cli', action='store_true', help='Run in CLI mode')
    parser.add_argument('-i', '--input', help='Input directory with invoices')
    parser.add_argument('-o', '--output', help='Output directory for results')
    parser.add_argument('--host', default='127.0.0.1', help='Web server host')
    parser.add_argument('--port', type=int, default=8000, help='Web server port')

    args = parser.parse_args()

    if args.web:
        print("="*60)
        print("Invoice Processing System - Web Server")
        print("="*60)
        print(f"Starting server at http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop")
        print("="*60)

        uvicorn.run(app, host=args.host, port=args.port)

    elif args.cli:
        if not args.input or not args.output:
            print("[ERROR] CLI mode requires --input and --output")
            sys.exit(1)

        process_cli(args.input, args.output)

    else:
        # Default: run web server
        print("\nStarting web server...")
        print("Open http://127.0.0.1:8000 in your browser\n")
        uvicorn.run(app, host="127.0.0.1", port=8000)
