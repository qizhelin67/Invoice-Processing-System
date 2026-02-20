@echo off
REM Tesseract OCR 自动安装脚本
REM 以管理员身份运行此脚本

echo ============================================
echo Tesseract OCR 自动安装
echo ============================================
echo.

REM 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo [1/4] 检查系统架构...
if defined PROCESSOR_ARCHITEW6432 (
    set ARCH=w64
) else (
    set ARCH=w32
)
echo 检测到架构: %ARCH%

echo.
echo [2/4] 下载 Tesseract 安装程序...
set DOWNLOAD_URL=https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231001.exe
set INSTALLER=%TEMP%\tesseract-installer.exe

echo 正在下载...
powershell -Command "& {Invoke-WebRequest -Uri '%DOWNLOAD_URL%' -OutFile '%INSTALLER%'}"

if not exist %INSTALLER% (
    echo [错误] 下载失败
    echo 请手动下载: https://digi.bib.uni-mannheim.de/tesseract/
    pause
    exit /b 1
)

echo [3/4] 安装 Tesseract...
echo 安装路径: C:\Program Files\Tesseract-OCR
%INSTALLER% /S /D=C:\Program Files\Tesseract-OCR

echo.
echo [4/4] 验证安装...
if exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    echo [成功] Tesseract 已安装!
    echo.
    echo 添加到系统 PATH...
    setx PATH "%PATH%;C:\Program Files\Tesseract-OCR" /M
    echo.
    echo ============================================
    echo 安装完成!
    echo ============================================
    echo.
    echo 请重新启动命令提示符或浏览器
    echo 然后运行: python main.py --web
) else (
    echo [错误] 安装失败
    echo 请检查错误信息
    pause
    exit /b 1
)

echo.
echo 按任意键退出...
pause >nul
