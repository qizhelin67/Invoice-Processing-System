"""
OCR Processing Module
Extracts text from images and PDFs using Tesseract OCR
"""

import os
import re
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from PIL import Image
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class OCRProcessor:
    """Process images and PDFs to extract text using Tesseract OCR"""

    def __init__(self, lang: str = "chi_sim+eng", use_ai: bool = True):
        """
        Initialize OCR processor

        Args:
            lang: Tesseract language(s) - chi_sim+eng for Chinese+English
            use_ai: Whether to use AI for enhanced extraction
        """
        self.lang = lang
        self.use_ai = use_ai and OPENAI_AVAILABLE

        # Configure Tesseract path for Windows - ALWAYS SET IT
        if os.name == 'nt':
            # Set the default installation path directly
            default_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
            if os.path.exists(default_path):
                pytesseract.pytesseract.tesseract_cmd = default_path
                print(f"[INFO] Tesseract found at: {default_path}")
            else:
                # Try alternate paths
                possible_paths = [
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    rf"C:\Users\{os.getenv('USERNAME')}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
                ]
                for path in possible_paths:
                    if os.path.exists(path):
                        pytesseract.pytesseract.tesseract_cmd = path
                        print(f"[INFO] Tesseract found at: {path}")
                        break
                else:
                    print("[WARNING] Tesseract not found in standard locations")
                    print("Please install Tesseract to: C:\\Program Files\\Tesseract-OCR")

        # Initialize OpenAI client if available
        if self.use_ai:
            api_key = os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                self.use_ai = False
                print("[WARNING] OPENAI_API_KEY not found, using rule-based extraction only")

    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image to improve OCR accuracy

        Steps:
        1. Convert to grayscale
        2. Apply adaptive thresholding
        3. Denoise
        4. Enhance contrast
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)

        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(thresh)

        return enhanced

    def extract_text_from_image(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from image file

        Args:
            image_path: Path to image file (JPG, PNG, etc.)

        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")

            # Preprocess
            processed = self.preprocess_image(image)

            # Extract text with Tesseract
            text = pytesseract.image_to_string(
                processed,
                lang=self.lang,
                config='--psm 6'  # Assume uniform block of text
            )

            # Get additional info
            data = pytesseract.image_to_data(
                processed,
                lang=self.lang,
                config='--psm 6',
                output_type=pytesseract.Output.DICT
            )

            return {
                "text": text.strip(),
                "confidence": self._calculate_confidence(data),
                "word_count": len(text.split()),
                "image_path": image_path
            }

        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "image_path": image_path
            }

    def extract_text_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF file

        For text-based PDFs, extracts text directly
        For scanned PDFs, converts to images and uses OCR

        Args:
            pdf_path: Path to PDF file

        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            # First try to extract text directly
            doc = fitz.open(pdf_path)
            text_pages = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                text_pages.append(text)

            full_text = "\n\n".join(text_pages)

            # Check if we got meaningful text
            if len(full_text.strip()) > 100:
                return {
                    "text": full_text.strip(),
                    "method": "direct",
                    "pages": len(doc),
                    "pdf_path": pdf_path
                }

            # If not enough text, try OCR
            doc.close()
            return self._ocr_pdf(pdf_path)

        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "pdf_path": pdf_path
            }

    def _ocr_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Convert PDF to images and apply OCR"""
        try:
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=300,
                fmt='jpg'
            )

            all_text = []

            for i, image in enumerate(images):
                # Convert PIL to OpenCV format
                open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

                # Preprocess
                processed = self.preprocess_image(open_cv_image)

                # Extract text
                text = pytesseract.image_to_string(
                    processed,
                    lang=self.lang,
                    config='--psm 6'
                )

                all_text.append(f"--- Page {i+1} ---\n{text}")

            return {
                "text": "\n\n".join(all_text),
                "method": "ocr",
                "pages": len(images),
                "pdf_path": pdf_path
            }

        except Exception as e:
            return {
                "text": "",
                "error": str(e),
                "pdf_path": pdf_path
            }

    def _calculate_confidence(self, ocr_data: Dict) -> float:
        """Calculate average confidence from OCR data"""
        if 'conf' not in ocr_data:
            return 0.0

        confidences = [int(c) for c in ocr_data['conf'] if str(c).isdigit()]
        if not confidences:
            return 0.0

        return sum(confidences) / len(confidences)

    def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        Extract structured invoice data from OCR text

        Uses rule-based patterns + optional AI enhancement

        Args:
            text: Raw OCR text

        Returns:
            Structured invoice data
        """
        # Rule-based extraction
        data = self._rule_based_extraction(text)

        # AI enhancement if available
        if self.use_ai and len(text) > 50:
            try:
                ai_data = self._ai_extraction(text)
                # Merge AI data with rule-based data (AI takes priority)
                for key, value in ai_data.items():
                    if value:  # Only use AI data if not None/empty
                        data[key] = value
            except Exception as e:
                print(f"[WARNING] AI extraction failed: {e}")

        return data

    def _rule_based_extraction(self, text: str) -> Dict[str, Any]:
        """Extract invoice data using regex patterns"""

        data = {
            "amount": None,
            "date": None,
            "merchant": None,
            "invoice_number": None,
            "tax_id": None,
            "category": "other"
        }

        # Extract amount (Chinese and English formats)
        amount_patterns = [
            r'[¥$€£]\s*([0-9,]+\.?\d*)',  # Currency symbols
            r'([0-9,]+\.?\d*)\s*元',  # Chinese Yuan
            r'总[额计][:：]\s*([0-9,]+\.?\d*)',  # Total amount
            r'合计[:：]\s*([0-9,]+\.?\d*)',
            r'金额[:：]\s*([0-9,]+\.?\d*)',
        ]

        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    data["amount"] = float(amount_str)
                    break
                except ValueError:
                    continue

        # Extract date (multiple formats)
        date_patterns = [
            r'(\d{4})[年\-/](\d{1,2})[月\-/](\d{1,2})[日]?',
            r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',
            r'(\d{4})\-(\d{2})\-(\d{2})',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    if len(match.group(1)) == 4:
                        data["date"] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
                    else:
                        data["date"] = f"{match.group(3)}-{match.group(1)}-{match.group(2)}"
                    break
                except:
                    continue

        # Extract invoice number
        invoice_patterns = [
            r'发票号码[:：]\s*([A-Z0-9]+)',
            r'No\.?\s*([A-Z0-9]+)',
            r'号码[:：]\s*([0-9]+)',
        ]

        for pattern in invoice_patterns:
            match = re.search(pattern, text)
            if match:
                data["invoice_number"] = match.group(1)
                break

        # Extract tax ID
        tax_patterns = [
            r'纳税人识别号[:：]\s*([0-9A-Z]{15,20})',
            r'统一社会信用代码[:：]\s*([0-9A-Z]{15,20})',
        ]

        for pattern in tax_patterns:
            match = re.search(pattern, text)
            if match:
                data["tax_id"] = match.group(1)
                break

        # Extract merchant name (common patterns)
        merchant_patterns = [
            r'名称[:：]\s*([^\n]{5,50})',
            r'收款方[:：]\s*([^\n]{5,50})',
            r'销售方[:：]\s*([^\n]{5,50})',
            r'(滴滴|美团|饿了么|携程|飞猪|如家|汉庭|亚朵)',
        ]

        for pattern in merchant_patterns:
            match = re.search(pattern, text)
            if match:
                data["merchant"] = match.group(1).strip()
                break

        # Classify category
        data["category"] = self._classify_category(text, data.get("merchant", ""))

        return data

    def _ai_extraction(self, text: str) -> Dict[str, Any]:
        """Use OpenAI GPT-4 to extract invoice data"""

        prompt = f"""Extract the following information from this invoice text.
Return ONLY a JSON object with these fields:
- amount: total amount (number)
- date: invoice date (YYYY-MM-DD format)
- merchant: merchant/seller name
- invoice_number: invoice number if present
- tax_id: tax identification number if present
- category: one of (taxi, train, hotel, dining, other)

Invoice text:
{text[:2000]}  # Limit to 2000 chars for API

Return JSON only, no explanation."""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an invoice data extractor. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=500
            )

            import json
            result = response.choices[0].message.content
            return json.loads(result)

        except Exception as e:
            print(f"[ERROR] AI extraction failed: {e}")
            return {}

    def _classify_category(self, text: str, merchant: str) -> str:
        """Classify invoice into category"""

        text_lower = text.lower()
        merchant_lower = merchant.lower() if merchant else ""

        # Taxi keywords
        if any(kw in text_lower or kw in merchant_lower for kw in
               ['滴滴', 'taxi', '出租车', '出行', '打车', 'uber', 'lyft']):
            return 'taxi'

        # Train/plane keywords
        if any(kw in text_lower or kw in merchant_lower for kw in
               ['12306', '火车', '高铁', '动车', 'airline', '航班', '飞机', '携程', '飞猪']):
            return 'train'

        # Hotel keywords
        if any(kw in text_lower or kw in merchant_lower for kw in
               ['酒店', '宾馆', 'hotel', '住宿', '如家', '汉庭', '亚朵', '旅馆']):
            return 'hotel'

        # Dining keywords
        if any(kw in text_lower or kw in merchant_lower for kw in
               ['餐', '饭', '食', 'restaurant', '美团', '饿了么', 'dining']):
            return 'dining'

        return 'other'


def main():
    """Test OCR processor"""
    print("Invoice OCR Processor")
    print("=" * 50)

    processor = OCRProcessor()

    # Check Tesseract availability
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✓ Tesseract version: {version}")
    except:
        print("✗ Tesseract not found!")
        print("  Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return

    # Example usage
    print("\nTo process an invoice:")
    print("  processor = OCRProcessor()")
    print("  result = processor.extract_text_from_image('invoice.jpg')")
    print("  data = processor.extract_invoice_data(result['text'])")


if __name__ == "__main__":
    main()
