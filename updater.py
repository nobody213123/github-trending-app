"""
Auto-update module for GitHub Trending App
Checks GitHub releases for updates
"""

import requests
import json
import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple
from dataclasses import dataclass

# Current version
__version__ = "1.0.0"

# GitHub repository info (请替换为你的 GitHub 用户名和仓库名)
REPO_OWNER = "yourusername"  # TODO: 替换为你的 GitHub 用户名
REPO_NAME = "github-trending-app"  # TODO: 替换为你的仓库名


@dataclass
class UpdateInfo:
    """Update information"""
    version: str
    download_url: str
    release_notes: str
    published_at: str


class AutoUpdater:
    """Auto-update checker and downloader"""
    
    def __init__(self, current_version: str = __version__):
        self.current_version = current_version
        self.github_api_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/latest"
    
    def check_for_updates(self) -> Optional[UpdateInfo]:
        """
        Check for updates from GitHub releases
        Returns UpdateInfo if update available, None otherwise
        """
        try:
            response = requests.get(
                self.github_api_url,
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            latest_version = data.get("tag_name", "").lstrip("v")
            
            if not latest_version:
                return None
            
            if self._compare_versions(latest_version, self.current_version) > 0:
                # Find appropriate download for current platform
                download_url = self._get_download_url(data.get("assets", []))
                
                if download_url:
                    return UpdateInfo(
                        version=latest_version,
                        download_url=download_url,
                        release_notes=data.get("body", ""),
                        published_at=data.get("published_at", "")
                    )
            
            return None
            
        except Exception as e:
            print(f"Update check failed: {e}")
            return None
    
    def _compare_versions(self, v1: str, v2: str) -> int:
        """
        Compare two version strings
        Returns: 1 if v1 > v2, -1 if v1 < v2, 0 if equal
        """
        def parse_version(v: str) -> Tuple[int, ...]:
            try:
                return tuple(map(int, v.split(".")))
            except:
                return (0,)
        
        v1_parts = parse_version(v1)
        v2_parts = parse_version(v2)
        
        if v1_parts > v2_parts:
            return 1
        elif v1_parts < v2_parts:
            return -1
        return 0
    
    def _get_download_url(self, assets: list) -> Optional[str]:
        """Get download URL for current platform"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Platform patterns
        patterns = {
            "darwin": [".dmg", ".app", "macos", "darwin"],
            "windows": [".exe", ".msi", "windows", "win"],
            "linux": [".appimage", ".deb", ".rpm", "linux"]
        }
        
        platform_patterns = patterns.get(system, [])
        
        for asset in assets:
            name = asset.get("name", "").lower()
            for pattern in platform_patterns:
                if pattern in name:
                    return asset.get("browser_download_url")
        
        # Fallback: try to find any executable
        for asset in assets:
            name = asset.get("name", "").lower()
            if any(ext in name for ext in [".exe", ".dmg", ".appimage", ".app"]):
                return asset.get("browser_download_url")
        
        return None
    
    def download_update(self, url: str, download_dir: Optional[Path] = None) -> Optional[Path]:
        """
        Download update file
        Returns path to downloaded file
        """
        try:
            if download_dir is None:
                download_dir = Path.home() / "Downloads"
            
            download_dir.mkdir(parents=True, exist_ok=True)
            
            # Get filename from URL
            filename = url.split("/")[-1]
            filepath = download_dir / filename
            
            # Download with progress
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
            
            return filepath
            
        except Exception as e:
            print(f"Download failed: {e}")
            return None
    
    def install_update(self, installer_path: Path) -> bool:
        """
        Install update based on platform
        """
        system = platform.system().lower()
        
        try:
            if system == "darwin":
                # macOS: Open DMG or run installer
                if str(installer_path).endswith(".dmg"):
                    subprocess.run(["open", str(installer_path)], check=True)
                    return True
                elif str(installer_path).endswith(".app"):
                    # Copy to Applications
                    apps_dir = Path.home() / "Applications"
                    apps_dir.mkdir(exist_ok=True)
                    subprocess.run(["cp", "-r", str(installer_path), str(apps_dir)], check=True)
                    return True
            
            elif system == "windows":
                # Windows: Run installer
                subprocess.run([str(installer_path)], check=True)
                return True
            
            elif system == "linux":
                # Linux: Make executable and run
                if str(installer_path).endswith(".AppImage"):
                    os.chmod(str(installer_path), 0o755)
                    subprocess.run([str(installer_path)], check=False)
                    return True
            
            return False
            
        except Exception as e:
            print(f"Installation failed: {e}")
            return False
    
    def get_current_version(self) -> str:
        """Get current application version"""
        return __version__


# Singleton instance
updater = AutoUpdater()


if __name__ == "__main__":
    # Test update check
    print(f"Current version: {updater.get_current_version()}")
    print("Checking for updates...")
    
    update = updater.check_for_updates()
    if update:
        print(f"Update available: {update.version}")
        print(f"Release notes: {update.release_notes}")
        print(f"Download URL: {update.download_url}")
    else:
        print("No updates available")
