#!/usr/bin/env python3
"""YouTube Transcript Scraper - Desktop GUI"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading, os, json
from pathlib import Path
from scraper_core import TranscriptScraper
from search_optimizer import optimize_search_query
from filters import UPLOAD_DATE_OPTIONS, SORT_BY_OPTIONS, DURATION_OPTIONS, FEATURE_OPTIONS
from config import Config

# Preset configurations for common research tasks
PRESETS = {
    "Custom": {},
    "Quick Overview": {"max_results": 10, "upload_date": "Last 30 days", "sort_by": "Relevance", "duration": "Any duration", "features": ["Subtitles/CC"]},
    "Deep Research": {"max_results": 50, "upload_date": "Any time", "sort_by": "View count", "duration": "Long (> 20 min)", "features": ["Subtitles/CC"]},
    "Recent Updates": {"max_results": 20, "upload_date": "Last 7 days", "sort_by": "Upload date", "duration": "Any duration", "features": ["Subtitles/CC"]},
    "Creator Analysis": {"max_results": 30, "upload_date": "Any time", "sort_by": "View count", "duration": "Any duration", "features": []}
}

class ToolTip:
    def __init__(self, w, t):
        self.w, self.t, self.tw = w, t, None
        w.bind("<Enter>", self.show)
        w.bind("<Leave>", self.hide)
    def show(self, e=None):
        if self.tw or not self.t: return
        x, y = self.w.winfo_rootx() + 25, self.w.winfo_rooty() + 25
        self.tw = tw = tk.Toplevel(self.w)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(tw, text=self.t, justify='left', background="#FFFACD", relief='solid', borderwidth=1, font=('Segoe UI', 9)).pack()
    def hide(self, e=None):
        if self.tw: self.tw.destroy(); self.tw = None

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Your Intelligent YouTube Research Assistant")
        self.root.geometry("800x900")
        self.config = Config()
        self.api_key = self.config.load_api_key()
        self.output_path = str(Path.home())
        self.recent_locations = self.load_recent_locations()
        self.panel_states = {"search": True, "refine": False, "results": False}
        self.current_query = None
        self.result_data = []
        self.setup_styles()
        self.create_widgets()
        self.check_first_run()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # Panel frames with better contrast
        style.configure('TLabelframe', background='#F7F9FC', borderwidth=2, relief='solid')
        style.configure('TLabelframe.Label', background='#F7F9FC', foreground='#2C3E50', font=('Segoe UI', 13, 'bold'))
        # Labels with larger, more readable font
        style.configure('TLabel', background='#F7F9FC', foreground='#2C3E50', font=('Segoe UI', 11))
        style.configure('Heading.TLabel', background='#F7F9FC', foreground='#2C3E50', font=('Segoe UI', 12, 'bold'))
        style.configure('Small.TLabel', background='#F7F9FC', foreground='#5A6C7D', font=('Segoe UI', 9))
        # Buttons with improved spacing
        style.configure('TButton', background='#4A90E2', foreground='white', font=('Segoe UI', 11, 'bold'), borderwidth=0, relief='flat', padding=12)
        style.map('TButton', background=[('active', '#3A7BC8'), ('disabled', '#95A5A6')])
        style.configure('Accent.TButton', background='#50C878', font=('Segoe UI', 12, 'bold'), padding=15)
        style.map('Accent.TButton', background=[('active', '#40B868'), ('disabled', '#95A5A6')])
        style.configure('Secondary.TButton', background='#95A5A6', font=('Segoe UI', 10), padding=8)
        style.map('Secondary.TButton', background=[('active', '#7F8C8D')])
        self.root.configure(background='#F7F9FC')

    def create_widgets(self):
        # Main container with scrollable canvas if needed
        main_container = ttk.Frame(self.root)
        main_container.pack(fill="both", expand=True, padx=15, pady=15)

        # PANEL 1: Define Your Research
        self.panel_search = ttk.LabelFrame(main_container, text="Step 1: Define Your Research", padding=15)
        self.panel_search.pack(fill="x", pady=(0, 10))

        # Preset selector
        preset_frame = ttk.Frame(self.panel_search)
        preset_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(preset_frame, text="Research Type:", style='Heading.TLabel').pack(side="left", padx=(0, 10))
        self.preset_var = tk.StringVar(value="Custom")
        preset_dropdown = ttk.Combobox(preset_frame, textvariable=self.preset_var, values=list(PRESETS.keys()), state="readonly", width=20, font=('Segoe UI', 11))
        preset_dropdown.pack(side="left")
        preset_dropdown.bind("<<ComboboxSelected>>", self.apply_preset)
        ToolTip(preset_dropdown, "Choose a preset configuration for common research tasks")

        # Research question
        ttk.Label(self.panel_search, text="Research Question", style='Heading.TLabel').pack(anchor="w", pady=(10, 5))
        self.query_text = scrolledtext.ScrolledText(self.panel_search, height=5, font=('Segoe UI', 11), wrap='word')
        self.query_text.pack(fill="x", pady=(0, 5))
        self.query_text.insert("1.0", "Example: How to implement BRCGS quality standards in manufacturing")
        self.query_text.bind("<FocusIn>", self.clear_placeholder)
        ttk.Label(self.panel_search, text="Describe what you want to learn. AI will enhance your search with related keywords.", style='Small.TLabel').pack(anchor="w", pady=(0, 10))

        # Controls row
        controls = ttk.Frame(self.panel_search)
        controls.pack(fill="x", pady=(0, 10))

        # AI optimization
        self.optimize_var = tk.BooleanVar(value=False)
        ai_check = ttk.Checkbutton(controls, text="Optimize with AI", variable=self.optimize_var)
        ai_check.pack(side="left", padx=(0, 10))
        ToolTip(ai_check, "Uses GPT-4 to expand your query with semantic keywords for better YouTube search results")

        # Results limit
        ttk.Label(controls, text="Results Limit:").pack(side="left", padx=(20, 5))
        self.max_results = tk.Spinbox(controls, from_=1, to=100, width=6, font=('Segoe UI', 11))
        self.max_results.delete(0, "end")
        self.max_results.insert(0, "20")
        self.max_results.pack(side="left")
        ttk.Label(controls, text="(recommended: 10-20)", style='Small.TLabel').pack(side="left", padx=(5, 0))

        # Next button
        next_btn = ttk.Button(self.panel_search, text="Next: Refine Sources →", command=self.show_refine_panel)
        next_btn.pack(fill="x", pady=(10, 0))

        # PANEL 2: Refine Sources (initially hidden)
        self.panel_refine = ttk.LabelFrame(main_container, text="Step 2: Refine Your Sources", padding=15)

        # Upload date filter
        date_frame = ttk.Frame(self.panel_refine)
        date_frame.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(date_frame, text="📅 Uploaded:", style='Heading.TLabel').pack(side="left", padx=(0, 10))
        self.upload_date = ttk.Combobox(date_frame, values=list(UPLOAD_DATE_OPTIONS.keys()), state="readonly", width=18, font=('Segoe UI', 11))
        self.upload_date.set("Any time")
        self.upload_date.pack(side="left")

        # Sort priority filter
        sort_frame = ttk.Frame(self.panel_refine)
        sort_frame.grid(row=0, column=2, columnspan=2, sticky="w", pady=(0, 10), padx=(20, 0))
        ttk.Label(sort_frame, text="⭐ Sort By:", style='Heading.TLabel').pack(side="left", padx=(0, 10))
        self.sort_by = ttk.Combobox(sort_frame, values=list(SORT_BY_OPTIONS.keys()), state="readonly", width=15, font=('Segoe UI', 11))
        self.sort_by.set("Relevance")
        self.sort_by.pack(side="left")

        # Duration filter
        duration_frame = ttk.Frame(self.panel_refine)
        duration_frame.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 10))
        ttk.Label(duration_frame, text="⏱️ Duration:", style='Heading.TLabel').pack(side="left", padx=(0, 10))
        self.duration = ttk.Combobox(duration_frame, values=list(DURATION_OPTIONS.keys()), state="readonly", width=18, font=('Segoe UI', 11))
        self.duration.set("Any duration")
        self.duration.pack(side="left")

        # Required attributes
        features_frame = ttk.Frame(self.panel_refine)
        features_frame.grid(row=1, column=2, columnspan=2, sticky="w", pady=(0, 10), padx=(20, 0))
        ttk.Label(features_frame, text="✓ Required:", style='Heading.TLabel').pack(anchor="w", pady=(0, 5))
        self.feature_vars = {}
        for feat in FEATURE_OPTIONS:
            var = tk.BooleanVar(value=(feat == "Subtitles/CC"))
            cb = ttk.Checkbutton(features_frame, text=feat, variable=var)
            cb.pack(anchor="w", padx=(10, 0))
            self.feature_vars[feat] = var
            if feat == "Subtitles/CC":
                ToolTip(cb, "Required for transcript extraction - leave enabled")

        # Collection naming
        collection_frame = ttk.Frame(self.panel_refine)
        collection_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(15, 10))
        ttk.Label(collection_frame, text="💾 Collection Name:", style='Heading.TLabel').pack(anchor="w", pady=(0, 5))
        self.topic_entry = ttk.Entry(collection_frame, font=('Segoe UI', 11))
        self.topic_entry.pack(fill="x", pady=(0, 5))
        ttk.Label(collection_frame, text="Leave blank for auto-generated name based on your query", style='Small.TLabel').pack(anchor="w")

        # Save location
        location_frame = ttk.Frame(self.panel_refine)
        location_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(0, 15))
        ttk.Label(location_frame, text="📁 Save Location:", style='Heading.TLabel').pack(anchor="w", pady=(0, 5))
        path_row = ttk.Frame(location_frame)
        path_row.pack(fill="x")
        self.path_label = ttk.Label(path_row, text=self.output_path, relief="sunken", background="white", padding=5)
        self.path_label.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(path_row, text="Browse...", command=self.browse).pack(side="left", padx=(0, 5))
        if self.recent_locations:
            self.recent_btn = ttk.Button(path_row, text="Recent ▼", style='Secondary.TButton', command=self.show_recent_locations)
            self.recent_btn.pack(side="left")

        # Action buttons
        action_frame = ttk.Frame(self.panel_refine)
        action_frame.grid(row=4, column=0, columnspan=4, sticky="ew")
        ttk.Button(action_frame, text="← Back", style='Secondary.TButton', command=self.show_search_panel).pack(side="left", padx=(0, 10))
        self.start_btn = ttk.Button(action_frame, text="🔍 Find & Extract Knowledge", style='Accent.TButton', command=self.start)
        self.start_btn.pack(side="left", fill="x", expand=True)

        # PANEL 3: Results & Progress (initially hidden)
        self.panel_results = ttk.LabelFrame(main_container, text="Step 3: Results & Progress", padding=15)

        # Query echo area
        self.query_echo_frame = ttk.Frame(self.panel_results)
        self.query_echo_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(self.query_echo_frame, text="Your Search:", style='Heading.TLabel').pack(anchor="w", pady=(0, 5))
        self.query_echo = tk.Text(self.query_echo_frame, height=3, font=('Segoe UI', 10), wrap='word', state='disabled', background='#E8F4F8')
        self.query_echo.pack(fill="x", pady=(0, 5))
        self.edit_query_btn = ttk.Button(self.query_echo_frame, text="✏️ Edit Query", style='Secondary.TButton', command=self.edit_query)

        # Progress state indicator
        self.state_frame = ttk.Frame(self.panel_results)
        self.state_frame.pack(fill="x", pady=(0, 10))
        self.state_label = ttk.Label(self.state_frame, text="Idle", style='Heading.TLabel')
        self.state_label.pack(side="left", padx=(0, 10))
        self.state_icon = ttk.Label(self.state_frame, text="⏸️")
        self.state_icon.pack(side="left")

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.panel_results, mode='determinate', length=700)
        self.progress_bar.pack(fill="x", pady=(0, 10))

        # Progress log
        log_frame = ttk.Frame(self.panel_results)
        log_frame.pack(fill="both", expand=True, pady=(0, 10))
        ttk.Label(log_frame, text="Activity Log:", style='Heading.TLabel').pack(anchor="w", pady=(0, 5))
        self.progress = scrolledtext.ScrolledText(log_frame, height=10, state="disabled", font=('Consolas', 10))
        self.progress.pack(fill="both", expand=True)

        # Results display area
        self.results_frame = ttk.Frame(self.panel_results)
        self.results_frame.pack(fill="both", expand=True, pady=(10, 0))
        ttk.Label(self.results_frame, text="Extracted Transcripts:", style='Heading.TLabel').pack(anchor="w", pady=(0, 5))
        self.results_list = tk.Listbox(self.results_frame, height=8, font=('Segoe UI', 10))
        self.results_list.pack(fill="both", expand=True)

        # Bottom actions
        bottom_actions = ttk.Frame(self.panel_results)
        bottom_actions.pack(fill="x", pady=(15, 0))
        ttk.Button(bottom_actions, text="← New Search", style='Secondary.TButton', command=self.new_search).pack(side="left", padx=(0, 10))
        self.export_btn = ttk.Button(bottom_actions, text="📂 Open Collection Folder", command=self.open_collection_folder)
        self.export_btn.pack(side="left")

        # AI Settings (collapsible, at bottom)
        self.ai_settings_frame = ttk.LabelFrame(main_container, text="🔑 AI Search Settings (Optional)", padding=15)
        self.ai_settings_frame.pack(fill="x", pady=(10, 0))
        settings_row = ttk.Frame(self.ai_settings_frame)
        settings_row.pack(fill="x")
        ttk.Label(settings_row, text="OpenAI API Key:").pack(side="left", padx=(0, 10))
        self.api_entry = ttk.Entry(settings_row, show="*", font=('Segoe UI', 11))
        if self.api_key:
            self.api_entry.insert(0, self.api_key)
        self.api_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        ttk.Button(settings_row, text="Save", command=self.save_api_key).pack(side="left")
        ttk.Label(self.ai_settings_frame, text="Required only if you enable AI optimization. Your key is stored locally and encrypted.", style='Small.TLabel').pack(anchor="w", pady=(5, 0))

    def clear_placeholder(self, event):
        if self.query_text.get("1.0", "end").strip() == "Example: How to implement BRCGS quality standards in manufacturing":
            self.query_text.delete("1.0", "end")

    def apply_preset(self, event=None):
        preset_name = self.preset_var.get()
        if preset_name == "Custom":
            return
        preset = PRESETS[preset_name]
        self.max_results.delete(0, "end")
        self.max_results.insert(0, str(preset.get("max_results", 20)))
        self.upload_date.set(preset.get("upload_date", "Any time"))
        self.sort_by.set(preset.get("sort_by", "Relevance"))
        self.duration.set(preset.get("duration", "Any duration"))
        for feat, var in self.feature_vars.items():
            var.set(feat in preset.get("features", []))

    def show_panel(self, panel_name):
        panels = {"search": self.panel_search, "refine": self.panel_refine, "results": self.panel_results}
        for name, panel in panels.items():
            panel.pack_forget()
            self.panel_states[name] = False
        if panel_name == "refine":
            query = self.query_text.get("1.0", "end").strip()
            if not query or query == "Example: How to implement BRCGS quality standards in manufacturing":
                messagebox.showwarning("Missing Information", "Please enter a research question first")
                return
        target = panels[panel_name]
        target.pack(fill="both" if panel_name == "results" else "x", expand=(panel_name == "results"), pady=(0, 10))
        self.panel_states[panel_name] = True
    def show_refine_panel(self): self.show_panel("refine")
    def show_search_panel(self): self.show_panel("search")
    def show_results_panel(self): self.show_panel("results")
    def edit_query(self): self.show_panel("search")

    def new_search(self):
        self.show_panel("search")
        self.query_text.delete("1.0", "end")
        self.progress.config(state="normal")
        self.progress.delete("1.0", "end")
        self.progress.config(state="disabled")
        self.results_list.delete(0, "end")
        self.progress_bar['value'] = 0
        self.set_state("idle")

    def browse(self):
        folder = filedialog.askdirectory(initialdir=self.output_path)
        if folder:
            self.output_path = folder
            self.path_label.config(text=folder)
            self.add_recent_location(folder)

    def load_recent_locations(self):
        try:
            with open(Path.home() / ".youtube_scraper_config.json", 'r') as f:
                return json.load(f).get('recent_locations', [])
        except: return []
    def add_recent_location(self, location):
        if location not in self.recent_locations:
            self.recent_locations.insert(0, location)
            self.recent_locations = self.recent_locations[:5]
            self.save_recent_locations()
    def save_recent_locations(self):
        try:
            cf = Path.home() / ".youtube_scraper_config.json"
            data = json.load(open(cf, 'r')) if cf.exists() else {}
            data['recent_locations'] = self.recent_locations
            json.dump(data, open(cf, 'w'))
        except: pass

    def show_recent_locations(self):
        menu = tk.Menu(self.root, tearoff=0)
        for loc in self.recent_locations: menu.add_command(label=loc, command=lambda l=loc: (setattr(self, 'output_path', l), self.path_label.config(text=l)))
        menu.post(self.recent_btn.winfo_rootx(), self.recent_btn.winfo_rooty() + self.recent_btn.winfo_height())

    def save_api_key(self):
        key = self.api_entry.get().strip()
        if key:
            self.api_key = key
            self.config.save_api_key(key)
            messagebox.showinfo("Saved", "API key saved securely to local configuration")
        else: messagebox.showwarning("Warning", "API key field is empty")
    def set_state(self, state, message=""):
        states = {"idle": ("⏸️ Idle", "#95A5A6"), "optimizing": ("🧠 Optimizing with AI...", "#4A90E2"), "searching": ("🔍 Searching YouTube...", "#4A90E2"), "extracting": ("📥 Extracting transcripts...", "#4A90E2"), "complete": ("✅ Complete", "#50C878"), "failed": ("❌ Failed", "#E74C3C")}
        icon, color = states.get(state, ("⏸️ Idle", "#95A5A6"))
        self.state_label.config(text=message if message else icon.split()[1])
        self.state_icon.config(text=icon.split()[0])

    def log(self, msg):
        self.progress.config(state="normal")
        self.progress.insert("end", f"{msg}\n")
        self.progress.see("end")
        self.progress.config(state="disabled")
        self.root.update_idletasks()
    def start(self):
        query = self.query_text.get("1.0", "end").strip()
        if not query or query == "Example: How to implement BRCGS quality standards in manufacturing":
            messagebox.showerror("Missing Information", "Please enter a research question")
            return
        topic = self.topic_entry.get().strip()
        if not topic:
            topic = self.generate_collection_name(query)
            self.topic_entry.delete(0, "end")
            self.topic_entry.insert(0, topic)
        self.current_query = query
        self.show_results_panel()
        self.start_btn.config(state="disabled")
        self.query_echo.config(state="normal")
        self.query_echo.delete("1.0", "end")
        self.query_echo.insert("1.0", f"Original: {query}\n")
        self.query_echo.config(state="disabled")
        self.progress.config(state="normal")
        self.progress.delete("1.0", "end")
        self.progress.config(state="disabled")
        self.results_list.delete(0, "end")
        threading.Thread(target=self.run, args=(query, topic), daemon=True).start()
    def generate_collection_name(self, query):
        from datetime import datetime
        clean = "".join(c if c.isalnum() or c.isspace() else "" for c in query.lower())
        return "_".join(clean.split()[:5]) + "_" + datetime.now().strftime("%Y%m%d")

    def run(self, query, topic):
        try:
            self.progress_bar['value'] = 0
            self.set_state("idle")

            dur = DURATION_OPTIONS[self.duration.get()]
            feats = [k.lower().replace('subtitles/', '').replace('-', '').replace('/', '') for k, v in self.feature_vars.items() if v.get()]
            upload_days = UPLOAD_DATE_OPTIONS[self.upload_date.get()]

            if self.optimize_var.get() and self.api_key:
                self.progress_bar['value'] = 10
                self.set_state("optimizing")
                self.log("🧠 Optimizing query with AI for semantic keyword expansion...")
                opt = optimize_search_query(query, self.api_key, dur, feats, upload_days)
                self.log(f"✓ Original: {query}")
                self.log(f"✓ Optimized: {opt}")

                # Update query echo
                self.query_echo.config(state="normal")
                self.query_echo.insert("end", f"AI Enhanced: {opt}\n")
                self.query_echo.config(state="disabled")

                query = opt
            elif self.optimize_var.get():
                self.log("⚠ AI optimization enabled but no API key set - using original query")

            self.progress_bar['value'] = 20
            filters = {'upload_date': upload_days, 'sort_by': SORT_BY_OPTIONS[self.sort_by.get()]}

            # Show final query
            final_query = query
            if dur:
                final_query += f", {dur}"
            for feat in feats:
                final_query += f", {feat}"
            self.query_echo.config(state="normal")
            self.query_echo.insert("end", f"YouTube Query: {final_query}")
            self.query_echo.config(state="disabled")

            self.set_state("searching", f"Searching YouTube for {self.max_results.get()} videos...")
            self.log(f"🔍 Searching YouTube with filters: {filters}")
            self.progress_bar['value'] = 30

            scraper = TranscriptScraper(output_dir=os.path.join(self.output_path, topic), callback=lambda msg: (self.log(msg), self.update_progress()))

            self.set_state("extracting", "Extracting transcripts...")
            result = scraper.scrape(query, max_results=int(self.max_results.get()), filters=filters)

            self.progress_bar['value'] = 100
            self.log("=" * 60)

            if result['saved'] == 0 and result['skipped'] == 0:
                self.set_state("failed", "No results found")
                self.log("😕 No videos matched your criteria. Try:")
                self.log("  • Simpler keywords")
                self.log("  • Removing date/duration filters")
                self.log("  • Different sort priority")
            else:
                self.set_state("complete", f"Extracted {result['saved']} transcripts")
                self.log(f"✅ Success! Extracted {result['saved']} transcripts")
                self.log(f"⊘ Skipped {result['skipped']} videos (no transcript available)")
                self.log(f"📁 Saved to: {os.path.join(self.output_path, topic)}")

                # Populate results list
                for i, file_path in enumerate(result['files'], 1):
                    filename = Path(file_path).name
                    self.results_list.insert("end", f"{i}. {filename}")

                self.add_recent_location(os.path.join(self.output_path, topic))

        except Exception as e:
            import traceback
            self.progress_bar['value'] = 0
            self.set_state("failed", "Error occurred")
            self.log(f"❌ Error: {str(e)}")
            self.log("Details:")
            self.log(traceback.format_exc())
        finally:
            self.start_btn.config(state="normal")

    def update_progress(self):
        current = self.progress_bar['value']
        if current < 95:
            self.progress_bar['value'] = min(current + 3, 95)
        self.root.update_idletasks()

    def open_collection_folder(self):
        topic = self.topic_entry.get().strip() or "transcripts"
        folder_path = os.path.join(self.output_path, topic)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showwarning("Not Found", f"Collection folder does not exist:\n{folder_path}")

    def check_first_run(self):
        try:
            cf = Path.home() / ".youtube_scraper_config.json"
            if cf.exists():
                data = json.load(open(cf, 'r'))
                if data.get('first_run', True):
                    self.run_first_time_setup()
                    data['first_run'] = False
                    json.dump(data, open(cf, 'w'))
            else:
                self.run_first_time_setup()
                json.dump({'first_run': False, 'recent_locations': []}, open(cf, 'w'))
        except: pass

    def run_first_time_setup(self):
        self.query_text.delete("1.0", "end")
        self.query_text.insert("1.0", "How to improve manufacturing quality control")
        self.preset_var.set("Quick Overview")
        self.apply_preset()
        w = tk.Toplevel(self.root)
        w.title("Welcome!")
        w.geometry("500x300")
        w.transient(self.root)
        w.grab_set()
        f = ttk.Frame(w, padding=20)
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="Welcome to Your Research Assistant!", font=('Segoe UI', 14, 'bold')).pack(pady=(0, 15))
        ttk.Label(f, text="This tool helps you find and extract YouTube video transcripts for research.", wraplength=450, font=('Segoe UI', 11)).pack(pady=(0, 10))
        ttk.Label(f, text="Quick Start:", font=('Segoe UI', 12, 'bold')).pack(anchor="w", pady=(10, 5))
        for i, txt in enumerate(["1. Enter your research question (example loaded)", "2. Click 'Next' to refine filters (optional)", "3. Click 'Find & Extract' to start", "4. View results in Step 3 panel"], 1):
            ttk.Label(f, text=txt, wraplength=450, font=('Segoe UI', 10)).pack(anchor="w", padx=(10, 0), pady=(0, 15 if i == 4 else 0))
        ttk.Button(f, text="Got it! Let's start", command=w.destroy, style='Accent.TButton').pack(pady=(10, 0))

def main():
    root = tk.Tk()
    ScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
