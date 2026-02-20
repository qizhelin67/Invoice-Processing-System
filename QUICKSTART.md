# Quick Start Guide

## 5 Minutes to Your First Invoice Processing

### Step 1: Install Python Dependencies (1 minute)

```bash
cd invoice_processor
pip install -r requirements.txt
```

### Step 2: Install Tesseract OCR (2 minutes)

**Windows:**
1. Download: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Done!

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Linux:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim
```

### Step 3: (Optional) Add OpenAI API Key (1 minute)

Create `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
```

Without API key, system still works using rule-based extraction!

### Step 4: Run the Application (30 seconds)

**Option A: Web Interface**
```bash
python main.py --web
```

Open browser: http://127.0.0.1:8000

**Option B: Command Line**
```bash
python main.py --cli -i ./test_invoices -o ./results
```

### Step 5: Process Invoices (30 seconds)

**Web:**
1. Drag invoice images/PDFs to upload zone
2. Click "Start Processing"
3. Download ZIP with organized files + Excel report

**CLI:**
- Put invoices in `./test_invoices/` folder
- Run command above
- Find results in `./results/`

## That's It! 🎉

Your invoices are now:
✅ OCR processed
✅ AI analyzed
✅ Auto-categorized
✅ Smart paired
✅ Excel report generated

## Sample Output

```
Processing invoices...
Found 15 invoice files
Total invoices: 15
Total pairs: 3
Grand total: ¥2,580.00

By Category:
  🚕 打车票: 5 items, ¥350.00
  🏨 住宿费: 3 items, ¥1,200.00
  🍜 餐费: 4 items, ¥380.00
  🚄 火车飞机票: 2 items, ¥500.00
  📦 其他: 1 item, ¥150.00

Results saved to: ./results
ZIP archive: ./results/报销结果_20240115_123456.zip
```

## Troubleshooting

**Tesseract not found?**
- Download and install (see Step 2)

**Import errors?**
- Run: `pip install -r requirements.txt`

**Low accuracy?**
- Use high-resolution images (300 DPI+)
- Enable OpenAI API (add to .env)
- Ensure good lighting for photos

**Need help?**
- Check README.md
- Review troubleshooting section
- Open GitHub issue

## Next Steps

- Process your real invoices
- Customize categories
- Deploy to cloud
- Integrate with your workflow

Happy processing! 📊
