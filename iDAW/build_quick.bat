@echo off
REM Quick build script for Windows

echo ==========================================
echo   Lariat Bible - Quick Build (Windows)
echo ==========================================

REM Navigate to desktop_app directory
cd /d %~dp0

REM Check for PyInstaller
echo Checking for PyInstaller...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build 2>nul
if exist dist rmdir /s /q dist 2>nul
if exist __pycache__ rmdir /s /q __pycache__ 2>nul
del *.spec 2>nul

REM Build the executable
echo Building standalone executable...
pyinstaller ^
    --name="LariatBible" ^
    --windowed ^
    --onefile ^
    --clean ^
    --noconfirm ^
    main.py

REM Check if build was successful
if exist dist\LariatBible.exe (
    echo Build successful!
    echo Executable location: dist\LariatBible.exe
    echo Run with: dist\LariatBible.exe
) else (
    echo Build failed. Check the output above for errors.
    exit /b 1
)

echo ==========================================
echo   Build Complete!
echo ==========================================
pause
