#!/bin/bash
# Packaging script for Linux
# Creates an AppImage and standalone binary

set -e

echo "📦 Building Linux application..."

# Install dependencies
pip3 install pyinstaller

# Clean previous builds
rm -rf build/ dist/

# Build standalone binary
echo "🔨 Creating standalone binary..."
pyinstaller \
    --onefile \
    --name "GitHubTrending" \
    --add-data "assets:assets" \
    --add-data "locales:locales" \
    --hidden-import customtkinter \
    --hidden-import darkdetect \
    gui_app.py

# Create AppImage (optional)
echo "💿 Creating AppImage..."
if command -v appimagetool &> /dev/null; then
    # Create AppDir structure
    mkdir -p AppDir/usr/bin
    mkdir -p AppDir/usr/share/applications
    mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
    
    cp dist/GitHubTrending AppDir/usr/bin/
    cp assets/icon.png AppDir/usr/share/icons/hicolor/256x256/apps/
    
    cat > AppDir/github-trending.desktop << EOF
[Desktop Entry]
Name=GitHub Trending
Exec=GitHubTrending
Icon=github-trending
Type=Application
Categories=Development;
EOF
    
    appimagetool AppDir dist/GitHubTrending-Linux.AppImage
    rm -rf AppDir
    echo "✅ AppImage created: dist/GitHubTrending-Linux.AppImage"
fi

echo "✅ Linux build complete!"
echo "📁 Output: dist/GitHubTrending"
