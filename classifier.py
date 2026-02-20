"""
Invoice Classifier and Smart Pairing Module
Categorizes invoices and pairs receipts with invoices
"""

import os
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class Invoice:
    """Invoice data structure"""
    file_path: str
    file_name: str
    category: str
    amount: Optional[float]
    date: Optional[str]
    merchant: Optional[str]
    invoice_number: Optional[str]
    confidence: float
    text: str

    def __hash__(self):
        return hash(self.file_path)


@dataclass
class InvoicePair:
    """Paired receipt and invoice"""
    receipt: Invoice
    invoice: Invoice
    match_score: float
    match_reason: str


class InvoiceClassifier:
    """Classify invoices into categories"""

    CATEGORIES = {
        'taxi': {
            'keywords': ['滴滴', 'taxi', '出租车', '出行', '打车', 'uber', 'lyft',
                        '美团打车', '高德打车', '曹操出行', '首汽'],
            'icon': '🚕',
            'name': '打车票'
        },
        'train': {
            'keywords': ['12306', '火车', '高铁', '动车', 'railway', 'ticket',
                        '携程', '飞猪', '航空', '航班', '飞机', 'airline'],
            'icon': '🚄 ✈️',
            'name': '火车飞机票'
        },
        'hotel': {
            'keywords': ['酒店', '宾馆', 'hotel', '住宿', '如家', '汉庭', '亚朵',
                        '旅馆', '招待所', '香格里拉', '希尔顿', '万豪'],
            'icon': '🏨',
            'name': '住宿费'
        },
        'dining': {
            'keywords': ['餐', '饭', '食', 'restaurant', '美团', '饿了么',
                        'dining', '食堂', '餐厅', '美食'],
            'icon': '🍜',
            'name': '餐费'
        },
        'other': {
            'keywords': [],
            'icon': '📦',
            'name': '其他'
        }
    }

    def classify(self, invoice_data: Dict[str, Any], text: str) -> str:
        """
        Classify invoice into category

        Args:
            invoice_data: Extracted invoice data
            text: Raw OCR text

        Returns:
            Category string
        """
        # If already classified by OCR, use that
        if 'category' in invoice_data and invoice_data['category']:
            return invoice_data['category']

        # Classify based on merchant and text
        merchant = invoice_data.get('merchant', '').lower()
        text_lower = text.lower()

        # Check each category
        for category, info in self.CATEGORIES.items():
            if category == 'other':
                continue

            for keyword in info['keywords']:
                if keyword.lower() in text_lower or keyword.lower() in merchant:
                    return category

        return 'other'

    def get_category_info(self, category: str) -> Dict[str, str]:
        """Get category display info"""
        return self.CATEGORIES.get(category, self.CATEGORIES['other'])


class SmartPairingEngine:
    """
    Intelligently pair receipts with invoices

    Matching criteria:
    - Same platform/merchant
    - Close dates (±1 day)
    - Similar amounts (±5%)
    """

    def __init__(self,
                 date_tolerance_days: int = 1,
                 amount_tolerance_percent: float = 5.0):
        """
        Initialize pairing engine

        Args:
            date_tolerance_days: Max days between receipt and invoice
            amount_tolerance_percent: Max amount difference percentage
        """
        self.date_tolerance = timedelta(days=date_tolerance_days)
        self.amount_tolerance = amount_tolerance_percent / 100.0

    def find_pairs(self, invoices: List[Invoice]) -> List[InvoicePair]:
        """
        Find receipt-invoice pairs

        Args:
            invoices: List of all invoices (including receipts and invoices)

        Returns:
            List of paired invoices
        """
        # Separate receipts and invoices
        receipts = []
        formal_invoices = []

        for inv in invoices:
            # Check if file name indicates it's a receipt
            if self._is_receipt(inv):
                receipts.append(inv)
            else:
                formal_invoices.append(inv)

        pairs = []
        paired_invoices = set()

        # Try to pair each receipt
        for receipt in receipts:
            best_match = None
            best_score = 0.0
            best_reason = ""

            for invoice in formal_invoices:
                if invoice in paired_invoices:
                    continue

                score, reason = self._calculate_match_score(receipt, invoice)

                if score > best_score:
                    best_score = score
                    best_match = invoice
                    best_reason = reason

            # If match is good enough, create pair
            if best_match and best_score >= 0.5:
                pair = InvoicePair(
                    receipt=receipt,
                    invoice=best_match,
                    match_score=best_score,
                    match_reason=best_reason
                )
                pairs.append(pair)
                paired_invoices.add(best_match)

        return pairs

    def _is_receipt(self, invoice: Invoice) -> bool:
        """Check if file is likely a receipt (行程单/凭证)"""
        receipt_keywords = ['凭证', '行程单', 'receipt', '凭证单']
        file_name_lower = invoice.file_name.lower()

        return any(kw in file_name_lower for kw in receipt_keywords)

    def _calculate_match_score(self, receipt: Invoice, invoice: Invoice) -> Tuple[float, str]:
        """
        Calculate match score between receipt and invoice

        Returns:
            (score: 0-1, reason: string)
        """
        score = 0.0
        reasons = []

        # Check merchant/platform match (highest priority)
        if receipt.merchant and invoice.merchant:
            if self._merchants_match(receipt.merchant, invoice.merchant):
                score += 0.5
                reasons.append("同一平台")

        # Check date match
        if receipt.date and invoice.date:
            if self._dates_match(receipt.date, invoice.date):
                score += 0.3
                reasons.append("日期相近")
            elif self._dates_within_tolerance(receipt.date, invoice.date):
                score += 0.15
                reasons.append("日期接近")

        # Check amount match
        if receipt.amount and invoice.amount:
            if self._amounts_match(receipt.amount, invoice.amount):
                score += 0.2
                reasons.append("金额一致")
            elif self._amounts_within_tolerance(receipt.amount, invoice.amount):
                score += 0.1
                reasons.append("金额接近")

        return score, ", ".join(reasons) if reasons else "匹配度低"

    def _merchants_match(self, merchant1: str, merchant2: str) -> bool:
        """Check if two merchants are from the same platform"""
        # Normalize
        m1 = merchant1.lower().strip()
        m2 = merchant2.lower().strip()

        if m1 == m2:
            return True

        # Check for common platform keywords
        platforms = ['滴滴', '美团', '携程', '飞猪', '如家', '汉庭', '亚朵']

        for platform in platforms:
            if platform in m1 and platform in m2:
                return True

        return False

    def _dates_match(self, date1: str, date2: str) -> bool:
        """Check if dates are exactly the same"""
        return date1 == date2

    def _dates_within_tolerance(self, date1: str, date2: str) -> bool:
        """Check if dates are within tolerance"""
        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")
            d2 = datetime.strptime(date2, "%Y-%m-%d")

            return abs(d1 - d2) <= self.date_tolerance

        except:
            return False

    def _amounts_match(self, amount1: float, amount2: float) -> bool:
        """Check if amounts are exactly the same"""
        return abs(amount1 - amount2) < 0.01  # Within 1 cent

    def _amounts_within_tolerance(self, amount1: float, amount2: float) -> bool:
        """Check if amounts are within tolerance percentage"""
        if amount1 == 0 or amount2 == 0:
            return False

        diff = abs(amount1 - amount2)
        avg = (amount1 + amount2) / 2

        return (diff / avg) <= self.amount_tolerance


class InvoiceOrganizer:
    """Organize invoices into folder structure"""

    def __init__(self):
        self.classifier = InvoiceClassifier()
        self.pairing_engine = SmartPairingEngine()

    def organize(self, invoices: List[Invoice]) -> Dict[str, Any]:
        """
        Organize invoices into categories and pairs

        Args:
            invoices: List of processed invoices

        Returns:
            Organized structure with categories, pairs, and unpaired items
        """
        # Classify all invoices
        categorized = defaultdict(list)
        for invoice in invoices:
            category = invoice.category
            categorized[category].append(invoice)

        # Find pairs within each category
        pairs_by_category = {}
        unpaired_by_category = defaultdict(list)

        for category, category_invoices in categorized.items():
            pairs = self.pairing_engine.find_pairs(category_invoices)

            # Track paired invoices
            paired_file_paths = set()
            for pair in pairs:
                paired_file_paths.add(pair.receipt.file_path)
                paired_file_paths.add(pair.invoice.file_path)

            # Separate unpaired
            unpaired = [
                inv for inv in category_invoices
                if inv.file_path not in paired_file_paths
            ]

            pairs_by_category[category] = pairs
            unpaired_by_category[category] = unpaired

        # Calculate statistics
        stats = self._calculate_stats(categorized, pairs_by_category)

        return {
            'categorized': dict(categorized),
            'pairs': pairs_by_category,
            'unpaired': dict(unpaired_by_category),
            'statistics': stats
        }

    def _calculate_stats(self,
                        categorized: Dict[str, List[Invoice]],
                        pairs: Dict[str, List[InvoicePair]]) -> Dict[str, Any]:
        """Calculate organization statistics"""

        total_invoices = sum(len(invoices) for invoices in categorized.values())

        total_pairs = sum(len(pair_list) for pair_list in pairs.values())

        # Calculate totals by category
        category_totals = {}
        for category, invoices in categorized.items():
            total = sum(inv.amount or 0 for inv in invoices)
            count = len(invoices)
            category_info = self.classifier.get_category_info(category)

            category_totals[category] = {
                'name': category_info['name'],
                'icon': category_info['icon'],
                'count': count,
                'total_amount': total,
                'pairs': len(pairs.get(category, [])),
                'unpaired': count - (len(pairs.get(category, [])) * 2)
            }

        grand_total = sum(ct['total_amount'] for ct in category_totals.values())

        return {
            'total_invoices': total_invoices,
            'total_pairs': total_pairs,
            'grand_total': grand_total,
            'by_category': category_totals
        }


def main():
    """Test classifier and pairing"""
    print("Invoice Classifier & Smart Pairing")
    print("=" * 50)

    # Create sample invoices
    invoices = [
        Invoice(
            file_path="/path/to/didi_receipt.pdf",
            file_name="滴滴行程单.pdf",
            category="taxi",
            amount=35.50,
            date="2024-01-15",
            merchant="滴滴出行",
            invoice_number=None,
            confidence=0.95,
            text="滴滴行程单 35.50元"
        ),
        Invoice(
            file_path="/path/to/didi_invoice.jpg",
            file_name="滴滴发票.jpg",
            category="taxi",
            amount=35.50,
            date="2024-01-15",
            merchant="滴滴出行",
            invoice_number="INV001",
            confidence=0.92,
            text="滴滴发票 35.50元"
        ),
        Invoice(
            file_path="/path/to/hotel_invoice.pdf",
            file_name="酒店发票.pdf",
            category="hotel",
            amount=350.00,
            date="2024-01-16",
            merchant="如家酒店",
            invoice_number="INV002",
            confidence=0.98,
            text="如家酒店 350元"
        ),
    ]

    # Organize
    organizer = InvoiceOrganizer()
    result = organizer.organize(invoices)

    print("\nStatistics:")
    print(f"  Total invoices: {result['statistics']['total_invoices']}")
    print(f"  Total pairs: {result['statistics']['total_pairs']}")
    print(f"  Grand total: ¥{result['statistics']['grand_total']:.2f}")

    print("\nBy Category:")
    for cat, stat in result['statistics']['by_category'].items():
        print(f"  {stat['icon']} {stat['name']}: {stat['count']} items, ¥{stat['total_amount']:.2f}")

    print("\nPairs Found:")
    for category, pairs in result['pairs'].items():
        if pairs:
            print(f"\n  {category}:")
            for pair in pairs:
                print(f"    - {pair.receipt.file_name} + {pair.invoice.file_name}")
                print(f"      Score: {pair.match_score:.2f} ({pair.match_reason})")


if __name__ == "__main__":
    main()
