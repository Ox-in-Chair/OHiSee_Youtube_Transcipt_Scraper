#!/usr/bin/env python3
"""YouTube Transcript Scraper - Desktop GUI"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading, os
from pathlib import Path
from scraper_core import TranscriptScraper
from search_optimizer import optimize_search_query
from filters import UPLOAD_DATE_OPTIONS, SORT_BY_OPTIONS, DURATION_OPTIONS, FEATURE_OPTIONS
from config import Config

class ScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Your Intelligent YouTube Research Assistant")
        self.root.geometry("650x600")
        self.config = Config()
        self.api_key = self.config.load_api_key()
        self.output_path = str(Path.home())
        self.create_widgets()
    def create_widgets(self):
        f = ttk.LabelFrame(self.root, text="💭 Search", padding=10)
        f.pack(fill="x", padx=10, pady=5)
        ttk.Label(f, text="What are you researching?").pack(anchor="w")
        self.query_text = scrolledtext.ScrolledText(f, height=3)
        self.query_text.pack(fill="x", pady=5)
        cf = ttk.Frame(f)
        cf.pack(fill="x")
        self.optimize_var = tk.BooleanVar()
        ttk.Checkbutton(cf, text="Use AI to find better results", variable=self.optimize_var).pack(side="left")
        ttk.Label(cf, text="Find up to:").pack(side="left", padx=(20, 5))
        self.max_results = tk.Spinbox(cf, from_=1, to=50, width=5)
        self.max_results.insert(0, "10")
        self.max_results.pack(side="left")
        f = ttk.LabelFrame(self.root, text="🎯 Refine Your Search", padding=10)
        f.pack(fill="x", padx=10, pady=5)
        ttk.Label(f, text="Show me:").grid(row=0, column=0, sticky="w", padx=5)
        self.upload_date = ttk.Combobox(f, values=list(UPLOAD_DATE_OPTIONS.keys()), state="readonly", width=15)
        self.upload_date.set("Any time")
        self.upload_date.grid(row=0, column=1, padx=5)
        ttk.Label(f, text="Prioritize:").grid(row=0, column=2, sticky="w", padx=5)
        self.sort_by = ttk.Combobox(f, values=list(SORT_BY_OPTIONS.keys()), state="readonly", width=12)
        self.sort_by.set("Relevance")
        self.sort_by.grid(row=0, column=3, padx=5)
        ttk.Label(f, text="Video length:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.duration = ttk.Combobox(f, values=list(DURATION_OPTIONS.keys()), state="readonly", width=15)
        self.duration.set("Any duration")
        self.duration.grid(row=1, column=1, padx=5, pady=5)
        ttk.Label(f, text="Must have:").grid(row=1, column=2, sticky="w", padx=5)
        ff = ttk.Frame(f)
        ff.grid(row=1, column=3, sticky="w", padx=5)
        self.feature_vars = {}
        for i, feat in enumerate(FEATURE_OPTIONS):
            var = tk.BooleanVar()
            ttk.Checkbutton(ff, text=feat, variable=var).pack(side="left", padx=2)
            self.feature_vars[feat] = var
        f = ttk.LabelFrame(self.root, text="💾 Save Results", padding=10)
        f.pack(fill="x", padx=10, pady=5)
        ttk.Label(f, text="Save to collection:").pack(anchor="w")
        self.topic_entry = ttk.Entry(f)
        self.topic_entry.pack(fill="x", pady=5)
        pf = ttk.Frame(f)
        pf.pack(fill="x")
        ttk.Label(pf, text="Location:").pack(side="left")
        self.path_label = ttk.Label(pf, text=self.output_path, relief="sunken", width=35)
        self.path_label.pack(side="left", padx=5, fill="x", expand=True)
        ttk.Button(pf, text="Browse", command=self.browse).pack(side="left")
        f = ttk.LabelFrame(self.root, text="🔑 AI Search Settings (Optional)", padding=10)
        f.pack(fill="x", padx=10, pady=5)
        self.api_entry = ttk.Entry(f, show="*", width=40)
        if self.api_key:
            self.api_entry.insert(0, self.api_key)
        self.api_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(f, text="Save Key", command=self.save_api_key).pack(side="left")
        bf = ttk.Frame(self.root)
        bf.pack(fill="x", padx=10, pady=10)
        self.start_btn = ttk.Button(bf, text="Find & Extract Knowledge", command=self.start)
        self.start_btn.pack(side="left", padx=5)
        f = ttk.LabelFrame(self.root, text="⏳ Working on it...", padding=10)
        f.pack(fill="both", expand=True, padx=10, pady=5)
        self.progress = scrolledtext.ScrolledText(f, height=8, state="disabled")
        self.progress.pack(fill="both", expand=True)

    def browse(self):
        folder = filedialog.askdirectory(initialdir=self.output_path)
        if folder:
            self.output_path = folder
            self.path_label.config(text=folder)
    def save_api_key(self):
        key = self.api_entry.get().strip()
        if key:
            self.api_key = key
            self.config.save_api_key(key)
            messagebox.showinfo("Saved", "API key saved permanently!")
        else:
            messagebox.showwarning("Warning", "API key is empty")
    def log(self, msg):
        self.progress.config(state="normal")
        self.progress.insert("end", f"{msg}\n")
        self.progress.see("end")
        self.progress.config(state="disabled")
        self.root.update_idletasks()
    def start(self):
        query = self.query_text.get("1.0", "end").strip()
        if not query:
            messagebox.showerror("Error", "Enter search query")
            return
        topic = self.topic_entry.get().strip() or "transcripts"
        self.start_btn.config(state="disabled")
        self.progress.config(state="normal")
        self.progress.delete("1.0", "end")
        self.progress.config(state="disabled")
        threading.Thread(target=self.run, args=(query, topic), daemon=True).start()
    def run(self, query, topic):
        try:
            dur = DURATION_OPTIONS[self.duration.get()]
            feats = [k.lower().replace('subtitles/', '').replace('-', '').replace('/', '') for k, v in self.feature_vars.items() if v.get()]
            upload_days = UPLOAD_DATE_OPTIONS[self.upload_date.get()]
            if self.optimize_var.get() and self.api_key:
                self.log("🧠 Making search smarter with AI...")
                opt = optimize_search_query(query, self.api_key, dur, feats, upload_days)
                self.log(f"Original: {query}\nOptimized: {opt}")
                query = opt
            elif self.optimize_var.get():
                self.log("⚠ No API key set - using your query as-is")
            filters = {'upload_date': upload_days, 'sort_by': SORT_BY_OPTIONS[self.sort_by.get()]}
            self.log("🔍 Finding perfect videos for you...")
            scraper = TranscriptScraper(output_dir=os.path.join(self.output_path, topic), callback=self.log)
            result = scraper.scrape(query, max_results=int(self.max_results.get()), filters=filters)
            self.log("="*40)
            if result['saved'] == 0 and result['skipped'] == 0:
                self.log("😕 No matches found. Try simpler keywords or remove filters.")
            else:
                self.log(f"🎉 Success! Extracted {result['saved']} transcripts ({result['skipped']} skipped)\nSaved to: {os.path.join(self.output_path, topic)}")
        except Exception as e:
            import traceback
            self.log(f"✗ Error: {e}\nDetails: {traceback.format_exc()}")
        finally:
            self.start_btn.config(state="normal")


def main():
    root = tk.Tk()
    ScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
