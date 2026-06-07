"""
Main window component for GitHub Trending App
"""

import customtkinter as ctk
from tkinter import messagebox
import threading
import os
import subprocess
from pathlib import Path
from datetime import datetime

from i18n import i18n
from scraper import GitHubTrendingScraper
from ai_summarizer import AISummarizer
from report_generator import ReportGenerator
from config import DEFAULT_TIME_RANGE, MAX_REPOS, OUTPUT_DIR
from updater import updater
from scheduler import scheduler, ScheduleType
from cache import cache


class MainWindow(ctk.CTkFrame):
    """Main application window"""
    
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.is_running = False
        self.current_report_path = None
        
        self.setup_ui()
        self.setup_callbacks()
    
    def setup_ui(self):
        """Setup the UI layout"""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Title bar
        self.title_frame = ctk.CTkFrame(self, height=60)
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.title_frame.grid_columnconfigure(1, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.title_frame,
            text=i18n.t("app_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title_label.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # Language switcher
        self.lang_var = ctk.StringVar(value=i18n.get_language().upper())
        self.lang_switch = ctk.CTkSegmentedButton(
            self.title_frame,
            values=["ZH", "EN"],
            variable=self.lang_var,
            command=self.on_language_change
        )
        self.lang_switch.grid(row=0, column=2, padx=20, pady=15, sticky="e")
        
        # Main content (tabview)
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Setup tabs
        self.setup_generate_tab()
        self.setup_report_tab()
        self.setup_settings_tab()
        self.setup_schedule_tab()
        self.setup_about_tab()
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self, height=40)
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text=i18n.t("status_ready"),
            anchor="w"
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        self.version_label = ctk.CTkLabel(
            self.status_frame,
            text=f"{i18n.t('version')}: {updater.get_current_version()}",
            anchor="e"
        )
        self.version_label.pack(side="right", padx=20, pady=10)
    
    def setup_generate_tab(self):
        """Setup the generate report tab"""
        self.generate_tab = self.tabview.add(i18n.t("generate_report"))
        self.generate_tab.grid_columnconfigure(0, weight=1)
        self.generate_tab.grid_rowconfigure(2, weight=1)
        
        # Settings frame
        self.settings_frame = ctk.CTkFrame(self.generate_tab)
        self.settings_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        self.settings_frame.grid_columnconfigure(1, weight=1)
        
        # Time range
        ctk.CTkLabel(self.settings_frame, text=i18n.t("time_range")).grid(
            row=0, column=0, padx=20, pady=10, sticky="w"
        )
        self.time_var = ctk.StringVar(value=DEFAULT_TIME_RANGE)
        self.time_menu = ctk.CTkOptionMenu(
            self.settings_frame,
            variable=self.time_var,
            values=["daily", "weekly", "monthly"]
        )
        self.time_menu.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        
        # Language filter
        ctk.CTkLabel(self.settings_frame, text=i18n.t("language")).grid(
            row=1, column=0, padx=20, pady=10, sticky="w"
        )
        self.lang_filter_var = ctk.StringVar(value="")
        self.lang_filter_entry = ctk.CTkEntry(
            self.settings_frame,
            placeholder_text=i18n.t("all_languages")
        )
        self.lang_filter_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        # Max repos
        ctk.CTkLabel(self.settings_frame, text=i18n.t("max_repos")).grid(
            row=2, column=0, padx=20, pady=10, sticky="w"
        )
        self.max_slider_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.max_slider_frame.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.max_slider_frame.grid_columnconfigure(0, weight=1)
        
        self.max_var = ctk.IntVar(value=MAX_REPOS)
        self.max_slider = ctk.CTkSlider(
            self.max_slider_frame,
            from_=5,
            to=50,
            variable=self.max_var,
            number_of_steps=9,
            command=self.on_slider_change
        )
        self.max_slider.grid(row=0, column=0, sticky="ew")
        
        self.max_value_label = ctk.CTkLabel(
            self.max_slider_frame,
            text=str(MAX_REPOS),
            width=40,
            font=ctk.CTkFont(weight="bold")
        )
        self.max_value_label.grid(row=0, column=1, padx=(10, 0))
        
        # Buttons frame
        self.buttons_frame = ctk.CTkFrame(self.generate_tab, fg_color="transparent")
        self.buttons_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        self.generate_btn = ctk.CTkButton(
            self.buttons_frame,
            text=i18n.t("generate_report"),
            command=self.start_generation,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.generate_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.stop_btn = ctk.CTkButton(
            self.buttons_frame,
            text=i18n.t("stop"),
            command=self.stop_generation,
            height=50,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            state="disabled"
        )
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
        
        # Log area
        self.log_frame = ctk.CTkFrame(self.generate_tab)
        self.log_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(10, 20))
        self.log_frame.grid_columnconfigure(0, weight=1)
        self.log_frame.grid_rowconfigure(1, weight=1)
        
        self.log_title_label = ctk.CTkLabel(
            self.log_frame,
            text=i18n.t("log_title"),
            font=ctk.CTkFont(weight="bold")
        )
        self.log_title_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.log_text = ctk.CTkTextbox(self.log_frame, state="disabled")
        self.log_text.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
    
    def setup_report_tab(self):
        """Setup the report preview tab"""
        self.report_tab = self.tabview.add(i18n.t("report_tab"))
        self.report_tab.grid_columnconfigure(0, weight=1)
        self.report_tab.grid_rowconfigure(0, weight=1)
        
        # Report preview
        self.report_text = ctk.CTkTextbox(self.report_tab, state="disabled")
        self.report_text.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        # Buttons
        self.report_buttons = ctk.CTkFrame(self.report_tab, fg_color="transparent")
        self.report_buttons.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.open_report_btn = ctk.CTkButton(
            self.report_buttons,
            text=i18n.t("open_report"),
            command=self.open_report,
            state="disabled"
        )
        self.open_report_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.open_folder_btn = ctk.CTkButton(
            self.report_buttons,
            text=i18n.t("open_folder"),
            command=self.open_folder,
            state="disabled"
        )
        self.open_folder_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))
    
    def setup_settings_tab(self):
        """Setup the settings tab"""
        self.settings_tab = self.tabview.add(i18n.t("settings"))
        self.settings_tab.grid_columnconfigure(1, weight=1)
        
        # AI Provider
        ctk.CTkLabel(self.settings_tab, text=i18n.t("ai_provider")).grid(
            row=0, column=0, padx=20, pady=15, sticky="w"
        )
        self.ai_var = ctk.StringVar(value="none")
        self.ai_menu = ctk.CTkOptionMenu(
            self.settings_tab,
            variable=self.ai_var,
            values=["none", "openai", "local"]
        )
        self.ai_menu.grid(row=0, column=1, padx=20, pady=15, sticky="ew")
        
        # API Key
        ctk.CTkLabel(self.settings_tab, text=i18n.t("api_key")).grid(
            row=1, column=0, padx=20, pady=15, sticky="w"
        )
        self.api_key_entry = ctk.CTkEntry(
            self.settings_tab,
            placeholder_text="sk-...",
            show="*"
        )
        self.api_key_entry.grid(row=1, column=1, padx=20, pady=15, sticky="ew")
        
        # Output directory
        ctk.CTkLabel(self.settings_tab, text=i18n.t("output_dir")).grid(
            row=2, column=0, padx=20, pady=15, sticky="w"
        )
        self.output_frame = ctk.CTkFrame(self.settings_tab, fg_color="transparent")
        self.output_frame.grid(row=2, column=1, padx=20, pady=15, sticky="ew")
        self.output_frame.grid_columnconfigure(0, weight=1)
        
        self.output_var = ctk.StringVar(value=str(OUTPUT_DIR))
        self.output_entry = ctk.CTkEntry(
            self.output_frame,
            textvariable=self.output_var
        )
        self.output_entry.grid(row=0, column=0, sticky="ew")
        
        self.browse_btn = ctk.CTkButton(
            self.output_frame,
            text=i18n.t("browse"),
            command=self.browse_output,
            width=100
        )
        self.browse_btn.grid(row=0, column=1, padx=(10, 0))
        
        # Check for updates button
        self.update_frame = ctk.CTkFrame(self.settings_tab, fg_color="transparent")
        self.update_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        self.check_update_btn = ctk.CTkButton(
            self.update_frame,
            text=i18n.t("check_update"),
            command=self.check_for_update
        )
        self.check_update_btn.pack(side="left")
    
    def setup_schedule_tab(self):
        """Setup the schedule tab"""
        self.schedule_tab = self.tabview.add(i18n.t("schedule"))
        self.schedule_tab.grid_columnconfigure(0, weight=1)
        self.schedule_tab.grid_rowconfigure(1, weight=1)
        
        # Schedule controls
        self.schedule_controls = ctk.CTkFrame(self.schedule_tab)
        self.schedule_controls.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        # Enable/disable scheduler
        self.schedule_enabled_var = ctk.BooleanVar(value=False)
        self.schedule_switch = ctk.CTkSwitch(
            self.schedule_controls,
            text=i18n.t("enable_schedule"),
            variable=self.schedule_enabled_var,
            command=self.toggle_scheduler
        )
        self.schedule_switch.pack(side="left", padx=20, pady=10)
        
        # Schedule type
        ctk.CTkLabel(self.schedule_controls, text=i18n.t("schedule_type")).pack(side="left", padx=10)
        self.schedule_type_var = ctk.StringVar(value="weekly")
        self.schedule_type_menu = ctk.CTkOptionMenu(
            self.schedule_controls,
            variable=self.schedule_type_var,
            values=["daily", "weekly", "monthly"],
            command=self.on_schedule_type_change
        )
        self.schedule_type_menu.pack(side="left", padx=10)
        
        # Time
        ctk.CTkLabel(self.schedule_controls, text=i18n.t("schedule_time")).pack(side="left", padx=10)
        self.schedule_time_var = ctk.StringVar(value="09:00")
        self.schedule_time_entry = ctk.CTkEntry(
            self.schedule_controls,
            textvariable=self.schedule_time_var,
            width=80
        )
        self.schedule_time_entry.pack(side="left", padx=10)
        
        # Day of week (for weekly)
        self.day_frame = ctk.CTkFrame(self.schedule_controls, fg_color="transparent")
        self.day_frame.pack(side="left", padx=10)
        
        ctk.CTkLabel(self.day_frame, text=i18n.t("schedule_day")).pack(side="left")
        self.schedule_day_var = ctk.StringVar(value="monday")
        self.schedule_day_menu = ctk.CTkOptionMenu(
            self.day_frame,
            variable=self.schedule_day_var,
            values=["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        )
        self.schedule_day_menu.pack(side="left", padx=5)
        
        # Task list
        self.task_list_frame = ctk.CTkFrame(self.schedule_tab)
        self.task_list_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.task_list_frame.grid_columnconfigure(0, weight=1)
        self.task_list_frame.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            self.task_list_frame,
            text=i18n.t("scheduled_tasks"),
            font=ctk.CTkFont(weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        
        self.task_list = ctk.CTkTextbox(self.task_list_frame, state="disabled")
        self.task_list.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Cache info
        self.cache_frame = ctk.CTkFrame(self.schedule_tab)
        self.cache_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        ctk.CTkLabel(
            self.cache_frame,
            text=i18n.t("cache_info"),
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=20, pady=10)
        
        self.clear_cache_btn = ctk.CTkButton(
            self.cache_frame,
            text=i18n.t("clear_cache"),
            command=self.clear_cache
        )
        self.clear_cache_btn.pack(side="right", padx=20, pady=10)
    
    def setup_about_tab(self):
        """Setup the about tab"""
        self.about_tab = self.tabview.add(i18n.t("about"))
        self.about_tab.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            self.about_tab,
            text=i18n.t("about_text"),
            font=ctk.CTkFont(size=14),
            justify="center"
        ).grid(row=0, column=0, padx=40, pady=40)
    
    def setup_callbacks(self):
        """Setup i18n callbacks"""
        i18n.on_language_change(self.update_ui_texts)
    
    def update_ui_texts(self):
        """Update all UI texts when language changes - rebuilds tabs"""
        # Update title
        self.title_label.configure(text=i18n.t("app_title"))
        
        # Store current state
        current_time = self.time_var.get() if hasattr(self, 'time_var') else DEFAULT_TIME_RANGE
        current_lang_filter = self.lang_filter_entry.get() if hasattr(self, 'lang_filter_entry') else ""
        current_max = self.max_var.get() if hasattr(self, 'max_var') else MAX_REPOS
        current_ai = self.ai_var.get() if hasattr(self, 'ai_var') else "none"
        current_output = self.output_var.get() if hasattr(self, 'output_var') else str(OUTPUT_DIR)
        
        # Destroy old tabview
        if hasattr(self, 'tabview'):
            self.tabview.destroy()
        
        # Create new tabview with updated language
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Rebuild all tabs
        self.setup_generate_tab()
        self.setup_report_tab()
        self.setup_settings_tab()
        self.setup_schedule_tab()
        self.setup_about_tab()
        
        # Restore state
        self.time_var.set(current_time)
        self.lang_filter_entry.insert(0, current_lang_filter)
        self.max_var.set(current_max)
        self.max_value_label.configure(text=str(int(current_max)))
        self.ai_var.set(current_ai)
        self.output_var.set(current_output)
        
        # Update status
        if not self.is_running:
            self.status_label.configure(text=i18n.t("status_ready"))
    
    def on_language_change(self, value):
        """Handle language change"""
        lang = value.lower()
        i18n.set_language(lang)
    
    def on_slider_change(self, value):
        """Handle slider value change"""
        self.max_value_label.configure(text=str(int(value)))
    
    def log(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.configure(state="normal")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def start_generation(self):
        """Start report generation in background thread"""
        if self.is_running:
            return
        
        self.is_running = True
        self.generate_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text=i18n.t("status_scraping"))
        
        # Clear log
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        
        # Start thread
        self.generation_thread = threading.Thread(target=self.run_generation, daemon=True)
        self.generation_thread.start()
    
    def run_generation(self):
        """Run the generation process"""
        try:
            # Get settings
            time_range = self.time_var.get()
            lang_filter = self.lang_filter_entry.get().strip() or None
            max_repos = int(float(self.max_var.get()))
            ai_provider = self.ai_var.get()
            
            # 1. Scrape
            self.log(i18n.t("status_scraping"))
            scraper = GitHubTrendingScraper()
            repos = scraper.scrape_trending(
                time_range=time_range,
                language=lang_filter,
                max_repos=max_repos
            )
            
            if not repos:
                self.log(i18n.t("msg_no_repos"))
                self.finish_generation(False)
                return
            
            self.log(f"✓ {len(repos)} repositories found")
            
            # 2. AI Summary
            self.log(i18n.t("status_summarizing"))
            summarizer = AISummarizer(provider=ai_provider)
            repos = summarizer.batch_summarize(repos, max_summary=10)
            self.log("✓ Summaries complete")
            
            # 3. Generate report
            self.log(i18n.t("status_generating"))
            generator = ReportGenerator()
            generator.output_dir = Path(self.output_var.get())
            generator.output_dir.mkdir(parents=True, exist_ok=True)
            
            md_path = generator.generate_markdown(repos, time_range=time_range)
            html_path = generator.generate_html(repos, time_range=time_range)
            
            self.current_report_path = md_path
            self.log(f"✓ {i18n.t('status_done')}")
            
            # Show in preview
            self.show_report_preview(md_path)
            
            self.finish_generation(True)
            
        except Exception as e:
            self.log(f"✗ {i18n.t('msg_error')}: {str(e)}")
            self.finish_generation(False)
    
    def finish_generation(self, success: bool):
        """Finish generation and reset UI"""
        self.is_running = False
        self.generate_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        
        if success:
            self.status_label.configure(text=i18n.t("msg_success"))
            self.open_report_btn.configure(state="normal")
            self.open_folder_btn.configure(state="normal")
        else:
            self.status_label.configure(text=i18n.t("status_error"))
    
    def stop_generation(self):
        """Stop the generation process"""
        # Note: This is a simplified stop mechanism
        # For a real app, you'd need to implement cooperative cancellation
        self.is_running = False
        self.generate_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text=i18n.t("status_stopped"))
        self.log(i18n.t("status_stopped"))
    
    def show_report_preview(self, path: Path):
        """Show report preview in the report tab"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.report_text.configure(state="normal")
            self.report_text.delete("1.0", "end")
            self.report_text.insert("1.0", content)
            self.report_text.configure(state="disabled")
        except Exception as e:
            self.log(f"Error reading report: {e}")
    
    def open_report(self):
        """Open the generated report"""
        if self.current_report_path:
            try:
                path = Path(self.current_report_path)
                if path.exists():
                    # Open HTML version if available
                    html_path = path.with_suffix('.html')
                    if html_path.exists():
                        subprocess.run(['open', str(html_path)], check=False)
                    else:
                        subprocess.run(['open', str(path)], check=False)
            except Exception as e:
                self.log(f"Error opening report: {e}")
    
    def open_folder(self):
        """Open the output folder"""
        output_dir = Path(self.output_var.get())
        if output_dir.exists():
            try:
                subprocess.run(['open', str(output_dir)], check=False)
            except Exception as e:
                self.log(f"Error opening folder: {e}")
    
    def browse_output(self):
        """Browse for output directory"""
        from tkinter import filedialog
        folder = filedialog.askdirectory()
        if folder:
            self.output_var.set(folder)
    
    def check_for_update(self):
        """Check for application updates"""
        def check_thread():
            try:
                update = updater.check_for_updates()
                if update:
                    # Show update dialog
                    result = messagebox.askyesno(
                        i18n.t("update_available"),
                        f"{i18n.t('version')}: {update.version}\n\n"
                        f"{update.release_notes[:200]}...\n\n"
                        f"{i18n.t('update_now')}?"
                    )
                    if result:
                        self.status_label.configure(text="Downloading update...")
                        filepath = updater.download_update(update.download_url)
                        if filepath:
                            self.status_label.configure(text="Installing update...")
                            updater.install_update(filepath)
                else:
                    messagebox.showinfo(
                        i18n.t("check_update"),
                        i18n.t("up_to_date")
                    )
            except Exception as e:
                self.log(f"Update check failed: {e}")
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def toggle_scheduler(self):
        """Toggle scheduler on/off"""
        if self.schedule_enabled_var.get():
            scheduler.start()
            self.log(i18n.t("scheduler_started"))
        else:
            scheduler.stop()
            self.log(i18n.t("scheduler_stopped"))
    
    def on_schedule_type_change(self, value):
        """Handle schedule type change"""
        # Show/hide day of week selector
        if value == "weekly":
            self.day_frame.pack(side="left", padx=10)
        else:
            self.day_frame.pack_forget()
    
    def add_scheduled_task(self):
        """Add a scheduled task"""
        schedule_type = self.schedule_type_var.get()
        time_str = self.schedule_time_var.get()
        
        type_map = {
            "daily": ScheduleType.DAILY,
            "weekly": ScheduleType.WEEKLY,
            "monthly": ScheduleType.MONTHLY
        }
        
        kwargs = {
            "name": f"auto_report_{schedule_type}",
            "func": self.run_generation,
            "schedule_type": type_map[schedule_type],
            "time": time_str
        }
        
        if schedule_type == "weekly":
            kwargs["day_of_week"] = self.schedule_day_var.get()
        
        task_id = scheduler.add_task(**kwargs)
        self.update_task_list()
        self.log(f"Added scheduled task: {schedule_type} at {time_str}")
    
    def update_task_list(self):
        """Update the task list display"""
        tasks = scheduler.get_tasks()
        
        self.task_list.configure(state="normal")
        self.task_list.delete("1.0", "end")
        
        if not tasks:
            self.task_list.insert("1.0", i18n.t("no_scheduled_tasks"))
        else:
            for task in tasks:
                status = "✅" if task["enabled"] else "❌"
                self.task_list.insert("end", 
                    f"{status} {task['name']} ({task['type']} at {task['time']})\n"
                )
        
        self.task_list.configure(state="disabled")
    
    def clear_cache(self):
        """Clear all cached data"""
        count = cache.clear()
        self.log(f"Cleared {count} cache files")
        messagebox.showinfo(i18n.t("clear_cache"), f"Cleared {count} cache files")
