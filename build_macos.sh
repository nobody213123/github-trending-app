#!/bin/bash
# Packaging script for macOS
# Creates a .app bundle and .dmg installer

set -e

echo "📦 Building macOS application..."

# Install dependencies
pip3 install pyinstaller

# Clean previous builds
rm -rf build/ dist/

# Build .app bundle
echo "🔨 Creating .app bundle..."
pyinstaller \
    --windowed \
    --name "GitHubTrending" \
    --icon "assets/icon.icns" \
    --add-data "assets:assets" \
    --add-data "locales:locales" \
    --hidden-import customtkinter \
    --hidden-import darkdetect \
    gui_app.py

# Create DMG (optional)
echo "💿 Creating DMG installer..."
if command -v hdiutil &> /dev/null; then
    # Create a temporary folder for DMG contents
    mkdir -p dist/dmg
    cp -r dist/GitHubTrending.app dist/dmg/
    
    # Create symlink to Applications
    ln -s /Applications dist/dmg/Applications
    
    # Create DMG
    hdiutil create \
        -volname "GitHubTrending" \
        -srcfolder dist/dmg \
        -ov \
        -format UDZO \
        dist/GitHubTrending-macOS.dmg
    
    rm -rf dist/dmg
    echo "✅ DMG created: dist/GitHubTrending-macOS.dmg"
fi

echo "✅ macOS build complete!"
echo "📁 Output: dist/GitHubTrending.app"
