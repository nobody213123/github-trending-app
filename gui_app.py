#!/usr/bin/env python3
"""
GitHub Trending 周报生成器 - GUI 版本
Cross-platform GUI application with bilingual support
"""

import sys
import os
from pathlib import Path

# Add app directory to path
APP_DIR = Path(__file__).parent
sys.path.insert(0, str(APP_DIR))

import customtkinter as ctk

from i18n import i18n
from gui_components import MainWindow


class App(ctk.CTk):
    """Main application class"""
    
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title(i18n.t("app_title"))
        self.geometry("900x700")
        self.minsize(800, 600)
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.main_window = MainWindow(self)
        self.main_window.pack(fill="both", expand=True)
    
    def set_title(self, title: str):
        """Update window title"""
        self.title(title)


def main():
    """Application entry point"""
    # Set icon if available
    icon_path = APP_DIR / "assets" / "icon.png"
    
    app = App()
    
    # Set window icon (macOS/Linux)
    if icon_path.exists():
        try:
            app.iconphoto(False, ctk.CTkImage(light_image=None, dark_image=None))
        except:
            pass
    
    # Bind language change to update title
    i18n.on_language_change(lambda: app.set_title(i18n.t("app_title")))
    
    app.mainloop()


if __name__ == "__main__":
    main()
