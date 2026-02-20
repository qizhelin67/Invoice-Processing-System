@echo off
echo ========================================
echo Invoice Processing System - Quick Deploy
echo ========================================
echo.

cd /d "%~dp0"

echo [Step 1/5] Initializing Git repository...
git init
echo.

echo [Step 2/5] Adding all files...
git add .
echo.

echo [Step 3/5] Creating commit...
git commit -m "Initial commit: Invoice Processing System - AI-powered OCR and classification"
echo.

echo ========================================
echo READY FOR GITHUB!
echo ========================================
echo.
echo Next Steps:
echo.
echo 1. Create GitHub Repository:
echo    - Go to https://github.com/new
echo    - Repository name: invoice-processor
echo    - Select PUBLIC
echo    - Click "Create repository"
echo.
echo 2. Push to GitHub (AFTER creating repo):
echo    git remote add origin https://github.com/YOUR_USERNAME/invoice-processor.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo 3. Deploy to Railway (EASIEST):
echo    - Go to https://railway.app
echo    - Click "Sign in with GitHub"
echo    - Click "New Project" -> "Deploy from GitHub repo"
echo    - Select your invoice-processor repository
echo    - Click "Deploy"
echo    - Wait 3-5 minutes
echo    - Get your URL: https://invoice-processor.up.railway.app
echo.
echo ========================================
pause
