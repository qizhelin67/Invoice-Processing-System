"""
Invoice Processing System - Setup Script
Quick setup and configuration
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")


def run_command(cmd, description):
    """Run shell command and display output"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ {description} - SUCCESS\n")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"   Error: {e.stderr}\n")
        return False


def setup_python_dependencies():
    """Install Python dependencies"""
    print_header("Installing Python Dependencies")

    requirements_files = [
        "requirements.txt"
    ]

    for req_file in requirements_files:
        if os.path.exists(req_file):
            success = run_command(
                f"pip install -r {req_file}",
                f"Installing from {req_file}"
            )
            if not success:
                print("⚠️  Some packages may have failed. Continuing...\n")
        else:
            print(f"⚠️  {req_file} not found. Skipping.\n")


def check_tesseract():
    """Check if Tesseract OCR is installed"""
    print_header("Checking Tesseract OCR")

    try:
        result = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ Tesseract found: {version}\n")
            return True
    except FileNotFoundError:
        pass

    print("❌ Tesseract OCR not found!\n")
    print("📥 Install Instructions:\n")

    system = platform.system()

    if system == "Windows":
        print("1. Download from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("2. Install to: C:\\Program Files\\Tesseract-OCR")
        print("3. Add to PATH (optional - script auto-detects)\n")

    elif system == "Darwin":  # macOS
        print("Run: brew install tesseract tesseract-lang\n")

    elif system == "Linux":
        print("Run: sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim\n")

    return False


def setup_env_file():
    """Create .env file if not exists"""
    print_header("Configuration Setup")

    env_file = Path(".env")
    env_example = Path(".env.example")

    if env_file.exists():
        print("✅ .env file already exists\n")
        return

    print("Creating .env file...")

    env_content = """# OpenAI API Configuration (Optional)
# Get your API key from: https://platform.openai.com/api-keys
# Leave empty to use rule-based extraction only

OPENAI_API_KEY=

# Optional: Custom OpenAI endpoint
# OPENAI_BASE_URL=https://api.openai.com/v1
"""

    with open(env_file, 'w') as f:
        f.write(env_content)

    print("✅ Created .env file\n")
    print("⚠️  To enable AI features:")
    print("   1. Get API key from: https://platform.openai.com/api-keys")
    print("   2. Add to .env: OPENAI_API_KEY=sk-...\n")


def create_directories():
    """Create necessary directories"""
    print_header("Creating Directories")

    directories = [
        "uploads",
        "results",
        "templates",
        "static"
    ]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created/verified: {directory}/")

    print()


def test_installation():
    """Test if installation is working"""
    print_header("Testing Installation")

    try:
        # Test imports
        print("Testing Python imports...")
        from ocr_processor import OCRProcessor
        from classifier import InvoiceOrganizer
        from report_generator import ExcelReportGenerator
        print("✅ All imports successful\n")

        # Test Tesseract
        print("Testing Tesseract...")
        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            print(f"✅ Tesseract version: {version}\n")
        except:
            print("⚠️  Tesseract not installed (see instructions above)\n")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}\n")
        print("Run: pip install -r requirements.txt\n")
        return False


def print_next_steps():
    """Print next steps"""
    print_header("Setup Complete!")

    print("🚀 Quick Start:\n")
    print("1. Web Interface:")
    print("   python main.py --web")
    print("   Then open: http://127.0.0.1:8000\n")

    print("2. Command Line:")
    print("   python main.py --cli -i ./invoices -o ./results\n")

    print("3. Python API:")
    print("   from ocr_processor import OCRProcessor")
    print("   processor = OCRProcessor()\n")

    print("📚 Documentation:")
    print("   See README.md for full documentation\n")


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print(" Invoice Processing System - Setup")
    print("="*60)

    # Step 1: Create directories
    create_directories()

    # Step 2: Install Python dependencies
    setup_python_dependencies()

    # Step 3: Check Tesseract
    tesseract_ok = check_tesseract()

    # Step 4: Setup environment file
    setup_env_file()

    # Step 5: Test installation
    test_ok = test_installation()

    # Print next steps
    print_next_steps()

    # Summary
    print("="*60)
    print(" Setup Summary")
    print("="*60)
    print(f"Python Dependencies: {'✅ OK' if test_ok else '❌ FAILED'}")
    print(f"Tesseract OCR: {'✅ OK' if tesseract_ok else '❌ NOT INSTALLED'}")
    print(f"Directories: ✅ Created")
    print(f"Config file: ✅ Created")
    print("="*60 + "\n")

    if not tesseract_ok:
        print("⚠️  IMPORTANT: Install Tesseract OCR for full functionality")
        print("   See instructions above\n")


if __name__ == "__main__":
    main()
