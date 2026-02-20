"""
Invoice Processing System - Demo
Demonstrates all features with sample data
"""

import asyncio
from datetime import datetime
from ocr_processor import OCRProcessor
from classifier import Invoice, InvoiceOrganizer
from report_generator import ExcelReportGenerator


def demo_ocr():
    """Demo 1: OCR Processing"""
    print("\n" + "="*60)
    print("DEMO 1: OCR Text Extraction")
    print("="*60)

    processor = OCRProcessor(use_ai=False)  # Use rule-based only for demo

    # Sample invoice text (simulating OCR output)
    sample_text = """
    滴滴出行科技有限公司
    电子发票

    发票号码: 12345678
    开票日期: 2024-01-15

    名称: 出行服务费
    金额: ¥35.50

    纳税人识别号: 91110000MA001234XX
    """

    print("\nOriginal Text:")
    print(sample_text)

    # Extract structured data
    data = processor.extract_invoice_data(sample_text)

    print("\nExtracted Data:")
    print(f"  Amount: {data.get('amount')}")
    print(f"  Date: {data.get('date')}")
    print(f"  Merchant: {data.get('merchant')}")
    print(f"  Invoice Number: {data.get('invoice_number')}")
    print(f"  Category: {data.get('category')}")


def demo_classification():
    """Demo 2: Invoice Classification"""
    print("\n" + "="*60)
    print("DEMO 2: Automatic Classification")
    print("="*60)

    from classifier import InvoiceClassifier

    classifier = InvoiceClassifier()

    # Sample invoices
    invoices = [
        {
            "text": "滴滴出行科技有限公司 出行服务费 ¥35.50",
            "merchant": "滴滴出行"
        },
        {
            "text": "如家酒店管理有限公司 住宿费 ¥350.00",
            "merchant": "如家酒店"
        },
        {
            "text": "美团餐饮 餐费 ¥68.00",
            "merchant": "美团"
        },
        {
            "text": "中国铁路总公司 火车票 ¥245.00",
            "merchant": "12306"
        }
    ]

    print("\nClassification Results:")
    for i, inv in enumerate(invoices, 1):
        category = classifier.classify({}, inv['text'])
        info = classifier.get_category_info(category)
        print(f"  {i}. {inv['merchant'][:20]:20s} → {info['icon']} {info['name']}")


def demo_smart_pairing():
    """Demo 3: Smart Receipt-Invoice Pairing"""
    print("\n" + "="*60)
    print("DEMO 3: Smart Receipt-Invoice Pairing")
    print("="*60)

    from classifier import SmartPairingEngine, Invoice

    # Create sample invoices
    receipt1 = Invoice(
        file_path="/path/to/didi_receipt.pdf",
        file_name="滴滴行程单.pdf",
        category="taxi",
        amount=35.50,
        date="2024-01-15",
        merchant="滴滴出行",
        invoice_number=None,
        confidence=0.95,
        text="滴滴行程单"
    )

    invoice1 = Invoice(
        file_path="/path/to/didi_invoice.jpg",
        file_name="滴滴发票.jpg",
        category="taxi",
        amount=35.50,
        date="2024-01-15",
        merchant="滴滴出行",
        invoice_number="INV001",
        confidence=0.92,
        text="滴滴发票"
    )

    invoice2 = Invoice(
        file_path="/path/to/hotel.pdf",
        file_name="酒店发票.pdf",
        category="hotel",
        amount=350.00,
        date="2024-01-16",
        merchant="如家酒店",
        invoice_number="INV002",
        confidence=0.98,
        text="如家酒店"
    )

    # Pair them
    engine = SmartPairingEngine()
    invoices_list = [receipt1, invoice1, invoice2]

    pairs = engine.find_pairs(invoices_list)

    print(f"\nFound {len(pairs)} pair(s):")

    for pair in pairs:
        print(f"\n  Pair {pairs.index(pair) + 1}:")
        print(f"    Receipt: {pair.receipt.file_name}")
        print(f"    Invoice: {pair.invoice.file_name}")
        print(f"    Score: {pair.match_score:.2f}")
        print(f"    Reason: {pair.match_reason}")


def demo_organization():
    """Demo 4: Complete Organization"""
    print("\n" + "="*60)
    print("DEMO 4: Complete Invoice Organization")
    print("="*60)

    # Create sample invoices
    invoices = [
        Invoice(
            file_path=f"/path/invoice_{i}.pdf",
            file_name=f"发票_{i}.pdf",
            category=cat,
            amount=amt,
            date="2024-01-15",
            merchant=f"商家{cat}",
            invoice_number=f"INV{i:03d}",
            confidence=0.9,
            text=f"Sample {cat} invoice"
        )
        for i, (cat, amt) in enumerate([
            ('taxi', 35.50),
            ('taxi', 28.00),
            ('hotel', 350.00),
            ('dining', 68.00),
            ('train', 245.00),
            ('other', 120.00)
        ], 1)
    ]

    # Organize
    organizer = InvoiceOrganizer()
    result = organizer.organize(invoices)

    # Display statistics
    stats = result['statistics']

    print("\n📊 Statistics:")
    print(f"  Total Invoices: {stats['total_invoices']}")
    print(f"  Grand Total: ¥{stats['grand_total']:,.2f}")

    print("\n📂 By Category:")
    for cat, cat_stat in stats['by_category'].items():
        print(f"  {cat_stat['icon']} {cat_stat['name']}: {cat_stat['count']} items, ¥{cat_stat['total_amount']:,.2f}")


def demo_excel_generation():
    """Demo 5: Excel Report Generation"""
    print("\n" + "="*60)
    print("DEMO 5: Excel Report Generation")
    print("="*60)

    # Create sample organized data
    sample_data = {
        'categorized': {
            'taxi': [],
            'hotel': [],
            'dining': [],
            'train': [],
            'other': []
        },
        'pairs': {},
        'statistics': {
            'total_invoices': 6,
            'total_pairs': 0,
            'grand_total': 846.50,
            'by_category': {
                'taxi': {
                    'name': '打车票',
                    'icon': '🚕',
                    'count': 2,
                    'total_amount': 63.50,
                    'pairs': 0,
                    'unpaired': 2
                },
                'hotel': {
                    'name': '住宿费',
                    'icon': '🏨',
                    'count': 1,
                    'total_amount': 350.00,
                    'pairs': 0,
                    'unpaired': 1
                },
                'dining': {
                    'name': '餐费',
                    'icon': '🍜',
                    'count': 1,
                    'total_amount': 68.00,
                    'pairs': 0,
                    'unpaired': 1
                },
                'train': {
                    'name': '火车飞机票',
                    'icon': '🚄',
                    'count': 1,
                    'total_amount': 245.00,
                    'pairs': 0,
                    'unpaired': 1
                },
                'other': {
                    'name': '其他',
                    'icon': '📦',
                    'count': 1,
                    'total_amount': 120.00,
                    'pairs': 0,
                    'unpaired': 1
                }
            }
        }
    }

    try:
        generator = ExcelReportGenerator()
        output_file = f"demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        generator.generate_report(sample_data, output_file)

        print(f"\n✅ Excel report generated: {output_file}")
        print("\nReport contains:")
        print("  - Summary sheet with category totals")
        print("  - Detail sheet with all invoices")
        print("  - Professional formatting")

    except Exception as e:
        print(f"\n❌ Error generating report: {e}")
        print("   Make sure openpyxl is installed: pip install openpyxl")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" Invoice Processing System - Feature Demonstration")
    print("="*70)

    demo_ocr()
    demo_classification()
    demo_smart_pairing()
    demo_organization()
    demo_excel_generation()

    print("\n" + "="*70)
    print(" All Demos Complete!")
    print("="*70)

    print("\n🚀 To process real invoices:")
    print("   1. Web: python main.py --web")
    print("   2. CLI:  python main.py --cli -i ./invoices -o ./results")
    print()


if __name__ == "__main__":
    main()
