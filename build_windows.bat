@echo off
REM Packaging script for Windows
REM Creates a .exe executable

echo 📦 Building Windows application...

REM Install dependencies
pip install pyinstaller

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

REM Build .exe
echo 🔨 Creating .exe executable...
pyinstaller ^
    --windowed ^
    --name "GitHubTrending" ^
    --icon "assets/icon.ico" ^
    --add-data "assets;assets" ^
    --add-data "locales;locales" ^
    --hidden-import customtkinter ^
    --hidden-import darkdetect ^
    gui_app.py

echo ✅ Windows build complete!
echo 📁 Output: dist\GitHubTrending.exe
echo.
echo To create an installer, use Inno Setup or NSIS
