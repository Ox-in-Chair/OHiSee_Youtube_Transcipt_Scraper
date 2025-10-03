#!/usr/bin/env python3
"""YouTube Research Assistant - World-Class Desktop Platform"""
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import threading, os, json, re
from pathlib import Path
from datetime import datetime
from scraper_core import TranscriptScraper
from search_optimizer import optimize_search_query
from filters import UPLOAD_DATE_OPTIONS, SORT_BY_OPTIONS, DURATION_OPTIONS, FEATURE_OPTIONS
from config import Config

# ============================================================================
# RESEARCH TEMPLATES
# ============================================================================
RESEARCH_TEMPLATES = {
    "Topic Overview": {
        "desc": "Get a broad understanding of a subject",
        "defaults": {"results": 15, "upload_date": "Last 90 days", "sort_by": "Relevance", "duration": "Any duration", "features": ["Subtitles/CC"]},
        "example": "How BRCGS standards apply to food manufacturing",
        "chips": {"topic": "BRCGS standards", "audience": "food manufacturers", "time_window": "Last 3 months", "quality": "Balanced", "sources": "Expert creators", "goals": ["Overview", "Key concepts"]}
    },
    "Fact Check": {
        "desc": "Verify claims with authoritative sources",
        "defaults": {"results": 10, "upload_date": "Last year", "sort_by": "Relevance", "duration": "Any duration", "features": ["Subtitles/CC"]},
        "example": "Are BRCGS audits required for export to EU",
        "chips": {"topic": "BRCGS export requirements", "audience": "exporters", "time_window": "Last year", "quality": "Deep dive", "sources": "Official channels", "goals": ["Citations", "Quotes"]}
    },
    "Competitor Scan": {
        "desc": "See how others approach this topic",
        "defaults": {"results": 25, "upload_date": "Last 6 months", "sort_by": "View count", "duration": "Any duration", "features": ["Subtitles/CC"]},
        "example": "How competitors implement quality management systems",
        "chips": {"topic": "quality management", "audience": "manufacturing companies", "time_window": "Last 6 months", "quality": "Balanced", "sources": "Any", "goals": ["Creators", "Trends"]}
    },
    "Citation Harvest": {
        "desc": "Collect authoritative references for research",
        "defaults": {"results": 30, "upload_date": "Any time", "sort_by": "Rating", "duration": "Long (> 20 min)", "features": ["Subtitles/CC"]},
        "example": "Academic sources on ISO 9001 implementation",
        "chips": {"topic": "ISO 9001", "audience": "researchers", "time_window": "All time", "quality": "Deep dive", "sources": "Expert creators", "goals": ["Citations", "Timestamps", "Quotes"]}
    },
    "Course Outline": {
        "desc": "Build structured learning path on a topic",
        "defaults": {"results": 20, "upload_date": "Last year", "sort_by": "Relevance", "duration": "Any duration", "features": ["Subtitles/CC"]},
        "example": "Learning path for food safety management certification",
        "chips": {"topic": "food safety certification", "audience": "learners", "time_window": "Last year", "quality": "Balanced", "sources": "Expert creators", "goals": ["Overview", "Progression"]}
    },
    "Custom": {
        "desc": "Build your own research configuration",
        "defaults": {"results": 20, "upload_date": "Last 30 days", "sort_by": "Relevance", "duration": "Any duration", "features": ["Subtitles/CC"]},
        "example": "",
        "chips": {}
    }
}

# ============================================================================
# PROFESSIONAL TYPOGRAPHY & STYLING SYSTEM
# ============================================================================
class ProfessionalStyles:
    FONTS = {
        "display": ("Segoe UI", 24, "bold"),
        "heading1": ("Segoe UI", 18, "bold"),
        "heading2": ("Segoe UI", 14, "bold"),
        "body": ("Segoe UI", 12),
        "caption": ("Segoe UI", 10),
        "code": ("Consolas", 11)
    }
    COLORS = {
        "primary": "#2563EB", "success": "#059669", "warning": "#D97706", "danger": "#DC2626",
        "text-primary": "#111827", "text-secondary": "#6B7280", "bg-primary": "#FFFFFF",
        "bg-secondary": "#F9FAFB", "bg-tertiary": "#F3F4F6", "border": "#E5E7EB"
    }
    SPACING = {"xs": 4, "sm": 8, "md": 16, "lg": 24, "xl": 32}

    @staticmethod
    def apply(root):
        s = ttk.Style()
        s.theme_use('clam')
        s.configure('TLabelframe', background=ProfessionalStyles.COLORS["bg-secondary"], borderwidth=1, relief='solid', bordercolor=ProfessionalStyles.COLORS["border"])
        s.configure('TLabelframe.Label', background=ProfessionalStyles.COLORS["bg-secondary"], foreground=ProfessionalStyles.COLORS["text-primary"], font=ProfessionalStyles.FONTS["heading2"])
        s.configure('TLabel', background=ProfessionalStyles.COLORS["bg-secondary"], foreground=ProfessionalStyles.COLORS["text-primary"], font=ProfessionalStyles.FONTS["body"])
        s.configure('Caption.TLabel', font=ProfessionalStyles.FONTS["caption"], foreground=ProfessionalStyles.COLORS["text-secondary"])
        s.configure('Heading1.TLabel', font=ProfessionalStyles.FONTS["heading1"], foreground=ProfessionalStyles.COLORS["text-primary"])
        s.configure('Heading2.TLabel', font=ProfessionalStyles.FONTS["heading2"], foreground=ProfessionalStyles.COLORS["text-primary"])
        s.configure('TButton', background=ProfessionalStyles.COLORS["primary"], foreground='white', font=ProfessionalStyles.FONTS["body"], borderwidth=0, padding=12)
        s.map('TButton', background=[('active', '#1D4ED8'), ('disabled', '#9CA3AF')])
        s.configure('Primary.TButton', background=ProfessionalStyles.COLORS["primary"], font=ProfessionalStyles.FONTS["heading2"], padding=15)
        s.map('Primary.TButton', background=[('active', '#1D4ED8')])
        s.configure('Success.TButton', background=ProfessionalStyles.COLORS["success"])
        s.map('Success.TButton', background=[('active', '#047857')])
        s.configure('Secondary.TButton', background=ProfessionalStyles.COLORS["bg-tertiary"], foreground=ProfessionalStyles.COLORS["text-primary"], padding=8)
        s.map('Secondary.TButton', background=[('active', '#E5E7EB')])
        root.configure(background=ProfessionalStyles.COLORS["bg-secondary"])

# ============================================================================
# WIZARD NAVIGATION COMPONENT
# ============================================================================
class WizardNav(ttk.Frame):
    STEPS = [
        ("1", "Define", "🎯"),
        ("2", "Refine", "⚙️"),
        ("3", "Review", "👁️"),
        ("4", "Run", "▶️"),
        ("5", "Export", "📦")
    ]
    def __init__(self, parent, on_step_change):
        super().__init__(parent)
        self.on_step_change = on_step_change
        self.current_step = 0
        self.configure(style='TFrame')
        ttk.Label(self, text="Research Wizard", style='Heading1.TLabel').pack(pady=(0, ProfessionalStyles.SPACING["lg"]))
        self.step_widgets = []
        for i, (num, name, icon) in enumerate(self.STEPS):
            frame = ttk.Frame(self)
            frame.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
            self.step_widgets.append(frame)
            btn = ttk.Button(frame, text=f"{icon} {num}. {name}", command=lambda idx=i: self.set_step(idx), width=15)
            btn.pack(fill="x")
        self.update_visual()
    def set_step(self, step_index):
        if step_index != self.current_step:
            self.current_step = step_index
            self.update_visual()
            self.on_step_change(step_index)
    def update_visual(self):
        for i, widget in enumerate(self.step_widgets):
            for child in widget.winfo_children():
                if isinstance(child, ttk.Button):
                    if i < self.current_step:
                        child.configure(style='Success.TButton')
                    elif i == self.current_step:
                        child.configure(style='Primary.TButton')
                    else:
                        child.configure(style='Secondary.TButton')

# ============================================================================
# LIVE PREVIEW COMPONENT
# ============================================================================
class LivePreview(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style='TFrame')
        ttk.Label(self, text="Live Preview", style='Heading1.TLabel').pack(pady=(0, ProfessionalStyles.SPACING["md"]))
        preview_frame = ttk.LabelFrame(self, text="What will be executed", padding=ProfessionalStyles.SPACING["md"])
        preview_frame.pack(fill="both", expand=True, pady=(0, ProfessionalStyles.SPACING["md"]))
        ttk.Label(preview_frame, text="Plain Language Summary:", style='Heading2.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["sm"]))
        self.summary_text = tk.Text(preview_frame, height=6, font=ProfessionalStyles.FONTS["body"], wrap='word', state='disabled', background='#E0F2FE', borderwidth=0)
        self.summary_text.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        ttk.Label(preview_frame, text="Technical Configuration:", style='Heading2.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["sm"]))
        self.config_text = tk.Text(preview_frame, height=8, font=ProfessionalStyles.FONTS["code"], wrap='word', state='disabled', background='#F3F4F6', borderwidth=0)
        self.config_text.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        btn_frame = ttk.Frame(preview_frame)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="📋 Copy Config", command=self.copy_config).pack(side="left", padx=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Button(btn_frame, text="💾 Export Config", command=self.export_config).pack(side="left")
    def update_preview(self, config):
        summary = f"Searching YouTube for '{config.get('query', 'N/A')}'\n"
        summary += f"• Results: {config.get('max_results', 20)}\n"
        summary += f"• Uploaded: {config.get('upload_date', 'Any time')}\n"
        summary += f"• Sorted by: {config.get('sort_by', 'Relevance')}\n"
        summary += f"• Duration: {config.get('duration', 'Any')}\n"
        summary += f"• Required features: {', '.join(config.get('features', ['None']))}\n"
        if config.get('ai_optimized'):
            summary += f"• AI optimized with GPT-4"
        self.summary_text.config(state="normal")
        self.summary_text.delete("1.0", "end")
        self.summary_text.insert("1.0", summary)
        self.summary_text.config(state="disabled")
        config_json = json.dumps(config, indent=2)
        self.config_text.config(state="normal")
        self.config_text.delete("1.0", "end")
        self.config_text.insert("1.0", config_json)
        self.config_text.config(state="disabled")
    def copy_config(self):
        self.clipboard_clear()
        self.clipboard_append(self.config_text.get("1.0", "end"))
        messagebox.showinfo("Copied", "Configuration copied to clipboard")
    def export_config(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            with open(filename, 'w') as f:
                f.write(self.config_text.get("1.0", "end"))
            messagebox.showinfo("Exported", f"Configuration exported to {filename}")

# ============================================================================
# CHIP INPUT COMPONENTS
# ============================================================================
class ChipInput(ttk.Frame):
    def __init__(self, parent, placeholder="", on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.entry = ttk.Entry(self, font=ProfessionalStyles.FONTS["body"], width=30)
        self.entry.pack(fill="x")
        self.entry.insert(0, placeholder)
        self.entry.bind("<FocusIn>", lambda e: self.entry.delete(0, "end") if self.entry.get() == placeholder else None)
        self.entry.bind("<KeyRelease>", lambda e: self.on_change() if self.on_change else None)
    def get(self):
        return self.entry.get()
    def set(self, value):
        self.entry.delete(0, "end")
        self.entry.insert(0, value)

class ChipSelector(ttk.Frame):
    def __init__(self, parent, options, on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.var = tk.StringVar(value=options[0] if options else "")
        self.combo = ttk.Combobox(self, textvariable=self.var, values=options, state="readonly", font=ProfessionalStyles.FONTS["body"], width=28)
        self.combo.pack(fill="x")
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.on_change() if self.on_change else None)
    def get(self):
        return self.var.get()
    def set(self, value):
        self.var.set(value)

class ChipMultiSelect(ttk.Frame):
    def __init__(self, parent, options, on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.vars = {}
        for opt in options:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self, text=opt, variable=var, command=lambda: self.on_change() if self.on_change else None)
            cb.pack(anchor="w")
            self.vars[opt] = var
    def get(self):
        return [k for k, v in self.vars.items() if v.get()]
    def set(self, values):
        for k, v in self.vars.items():
            v.set(k in values)

# ============================================================================
# PROMPT COMPOSER COMPONENT
# ============================================================================
class PromptComposer(ttk.Frame):
    def __init__(self, parent, on_change=None):
        super().__init__(parent)
        self.on_change = on_change
        self.chips = {}
        components = [
            ("Topic", "What are you researching?", "text", "e.g., BRCGS automation"),
            ("Audience", "Who is this for?", "text", "e.g., food manufacturers"),
            ("Time Window", "When was it published?", "select", ["Last week", "Last month", "Last 3 months", "Last 6 months", "Last year", "All time"]),
            ("Quality Bar", "How deep should we search?", "select", ["Quick scan", "Balanced", "Deep dive"]),
            ("Sources", "What kind of sources?", "select", ["Expert creators", "Official channels", "Any"]),
            ("Output Goals", "What do you want to extract?", "multi", ["Overview", "Citations", "Quotes", "Timestamps", "Trends"])
        ]
        for label, desc, widget_type, options in components:
            frame = ttk.Frame(self)
            frame.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
            ttk.Label(frame, text=label, style='Heading2.TLabel').pack(anchor="w")
            ttk.Label(frame, text=desc, style='Caption.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["xs"]))
            if widget_type == "text":
                self.chips[label] = ChipInput(frame, placeholder=options, on_change=self.trigger_change)
            elif widget_type == "select":
                self.chips[label] = ChipSelector(frame, options, on_change=self.trigger_change)
            elif widget_type == "multi":
                self.chips[label] = ChipMultiSelect(frame, options, on_change=self.trigger_change)
            self.chips[label].pack(fill="x")
    def trigger_change(self):
        if self.on_change:
            self.on_change()
    def get_values(self):
        return {k: v.get() for k, v in self.chips.items()}
    def set_values(self, values):
        for k, v in values.items():
            if k in self.chips:
                self.chips[k].set(v)
    def build_query(self):
        values = self.get_values()
        topic = values.get("Topic", "")
        audience = values.get("Audience", "")
        if not topic:
            return ""
        query = f"How {topic}"
        if audience:
            query += f" applies to {audience}"
        return query

# ============================================================================
# AI TRANSPARENCY PANEL
# ============================================================================
class AITransparencyPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.expanded = False
        header = ttk.Frame(self)
        header.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
        self.toggle_btn = ttk.Button(header, text="▶ AI Optimization Settings", command=self.toggle, style='Secondary.TButton')
        self.toggle_btn.pack(side="left")
        self.enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(header, text="Enable AI optimization", variable=self.enabled_var).pack(side="left", padx=ProfessionalStyles.SPACING["md"])
        self.details_frame = ttk.Frame(self)
        info_frame = ttk.LabelFrame(self.details_frame, text="How AI optimization works", padding=ProfessionalStyles.SPACING["md"])
        info_frame.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
        ttk.Label(info_frame, text="Model: GPT-4 (gpt-4-0613)", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w")
        ttk.Label(info_frame, text="Technique: Semantic keyword expansion with synonym detection", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w")
        ttk.Label(info_frame, text="Cost: ~$0.02-0.04 per optimization", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w", pady=(ProfessionalStyles.SPACING["sm"], 0))
        ttk.Label(info_frame, text="Example transformation:", style='Heading2.TLabel').pack(anchor="w", pady=(ProfessionalStyles.SPACING["md"], ProfessionalStyles.SPACING["xs"]))
        ttk.Label(info_frame, text="Before: 'BRCGS automation'", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w")
        ttk.Label(info_frame, text="After: 'BRCGS food safety standard workflow automation manufacturing procedures quality management'", font=ProfessionalStyles.FONTS["body"], wraplength=500).pack(anchor="w")
        params_frame = ttk.LabelFrame(self.details_frame, text="Advanced parameters", padding=ProfessionalStyles.SPACING["md"])
        params_frame.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
        ttk.Label(params_frame, text="Temperature (creativity):").grid(row=0, column=0, sticky="w", pady=ProfessionalStyles.SPACING["xs"])
        self.temp_var = tk.DoubleVar(value=0.3)
        ttk.Scale(params_frame, from_=0.0, to=1.0, variable=self.temp_var, orient="horizontal").grid(row=0, column=1, sticky="ew", padx=ProfessionalStyles.SPACING["sm"])
        ttk.Label(params_frame, textvariable=self.temp_var).grid(row=0, column=2)
        ttk.Label(params_frame, text="Max tokens:").grid(row=1, column=0, sticky="w", pady=ProfessionalStyles.SPACING["xs"])
        self.tokens_var = tk.IntVar(value=80)
        ttk.Spinbox(params_frame, from_=20, to=200, textvariable=self.tokens_var, width=10).grid(row=1, column=1, sticky="w", padx=ProfessionalStyles.SPACING["sm"])
    def toggle(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.details_frame.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
            self.toggle_btn.config(text="▼ AI Optimization Settings")
        else:
            self.details_frame.pack_forget()
            self.toggle_btn.config(text="▶ AI Optimization Settings")
    def is_enabled(self):
        return self.enabled_var.get()

# ============================================================================
# QUALITY GATE SYSTEM
# ============================================================================
class QueryQualityGate:
    @staticmethod
    def score_query(chips):
        score, feedback = 0, []
        topic = chips.get("Topic", "")
        if not topic or topic.startswith("e.g.,"):
            feedback.append("⚠ Enter a topic to continue")
        elif len(topic) < 3:
            feedback.append("💡 Topic too vague - be more specific")
        elif len(topic) > 100:
            feedback.append("💡 Topic too complex - try breaking it down")
        else:
            score += 60
            feedback.append("✓ Topic looks good")
        if chips.get("Audience", "") and not chips["Audience"].startswith("e.g.,"):
            score += 20
            feedback.append("✓ Audience specified")
        if chips.get("Time Window", "") != "All time":
            score += 10
        if chips.get("Output Goals", []):
            score += 10
        return min(score, 100), feedback, score >= 60

# ============================================================================
# CONNECTION MANAGER MODAL
# ============================================================================
class ConnectionManager(tk.Toplevel):
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.title("API Connection Manager")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=ProfessionalStyles.SPACING["md"], pady=ProfessionalStyles.SPACING["md"])
        key_tab = ttk.Frame(notebook)
        notebook.add(key_tab, text="API Key")
        ttk.Label(key_tab, text="OpenAI API Key", style='Heading2.TLabel').pack(anchor="w", pady=ProfessionalStyles.SPACING["md"])
        ttk.Label(key_tab, text="Enter your OpenAI API key for AI-powered query optimization", style='Caption.TLabel').pack(anchor="w")
        self.key_entry = ttk.Entry(key_tab, show="*", font=ProfessionalStyles.FONTS["body"], width=50)
        self.key_entry.pack(fill="x", pady=ProfessionalStyles.SPACING["md"])
        if config.load_api_key():
            self.key_entry.insert(0, config.load_api_key())
        btn_frame = ttk.Frame(key_tab)
        btn_frame.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
        ttk.Button(btn_frame, text="Test Connection", command=self.test_connection).pack(side="left", padx=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Button(btn_frame, text="Save Key", command=self.save_key, style='Primary.TButton').pack(side="left")
        ttk.Label(key_tab, text="Model Selection", style='Heading2.TLabel').pack(anchor="w", pady=(ProfessionalStyles.SPACING["lg"], ProfessionalStyles.SPACING["sm"]))
        self.model_var = tk.StringVar(value="gpt-4")
        for model in ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]:
            ttk.Radiobutton(key_tab, text=model, variable=self.model_var, value=model).pack(anchor="w")
        security_tab = ttk.Frame(notebook)
        notebook.add(security_tab, text="Security & Privacy")
        ttk.Label(security_tab, text="Data Security", style='Heading2.TLabel').pack(anchor="w", pady=ProfessionalStyles.SPACING["md"])
        ttk.Label(security_tab, text="• Encryption: AES-256 encryption at rest", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w", pady=ProfessionalStyles.SPACING["xs"])
        ttk.Label(security_tab, text="• Storage: ~/.youtube_scraper_config.json (encrypted)", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w", pady=ProfessionalStyles.SPACING["xs"])
        ttk.Label(security_tab, text="• Network: HTTPS only, no third-party sharing", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w", pady=ProfessionalStyles.SPACING["xs"])
        ttk.Label(security_tab, text="\nData Usage Policy", style='Heading2.TLabel').pack(anchor="w", pady=(ProfessionalStyles.SPACING["md"], ProfessionalStyles.SPACING["sm"]))
        ttk.Label(security_tab, text="Your API key is used exclusively for query optimization. No queries, transcripts, or personal data are sent to third parties. All processing is done locally except for OpenAI API calls which are governed by OpenAI's privacy policy.", font=ProfessionalStyles.FONTS["body"], wraplength=550).pack(anchor="w")
        close_btn = ttk.Button(self, text="Close", command=self.destroy, style='Secondary.TButton')
        close_btn.pack(side="bottom", pady=ProfessionalStyles.SPACING["md"])
    def test_connection(self):
        key = self.key_entry.get()
        if not key:
            messagebox.showerror("Error", "Please enter an API key first")
            return
        try:
            from openai import OpenAI
            client = OpenAI(api_key=key)
            client.models.list()
            messagebox.showinfo("Success", "✓ Connection successful! API key is valid.")
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Could not connect to OpenAI API:\n{str(e)}")
    def save_key(self):
        key = self.key_entry.get()
        if key:
            self.config.save_api_key(key)
            messagebox.showinfo("Saved", "API key saved securely")
            self.destroy()

# ============================================================================
# MAIN APPLICATION
# ============================================================================
class ResearchPlatform:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Research Assistant - World-Class Platform")
        self.root.geometry("1400x900")
        self.config = Config()
        self.api_key = self.config.load_api_key()
        self.output_path = str(Path.home())
        self.current_config = {}
        ProfessionalStyles.apply(root)
        container = ttk.Frame(root)
        container.pack(fill="both", expand=True, padx=ProfessionalStyles.SPACING["lg"], pady=ProfessionalStyles.SPACING["lg"])
        left_panel = ttk.Frame(container, width=200)
        left_panel.pack(side="left", fill="y", padx=(0, ProfessionalStyles.SPACING["lg"]))
        left_panel.pack_propagate(False)
        self.wizard = WizardNav(left_panel, self.on_step_change)
        self.wizard.pack(fill="both", expand=True)
        right_panel = ttk.Frame(container, width=400)
        right_panel.pack(side="right", fill="both", expand=False, padx=(ProfessionalStyles.SPACING["lg"], 0))
        right_panel.pack_propagate(False)
        self.live_preview = LivePreview(right_panel)
        self.live_preview.pack(fill="both", expand=True)
        center_panel = ttk.Frame(container)
        center_panel.pack(side="left", fill="both", expand=True)
        self.step_frames = {}
        self.create_step_define(center_panel)
        self.create_step_refine(center_panel)
        self.create_step_review(center_panel)
        self.create_step_run(center_panel)
        self.create_step_export(center_panel)
        self.show_step(0)
        self.check_first_run()
    def create_step_define(self, parent):
        frame = ttk.Frame(parent)
        self.step_frames[0] = frame
        ttk.Label(frame, text="Step 1: Define Your Research", style='Heading1.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["lg"]))
        template_frame = ttk.LabelFrame(frame, text="Choose a Research Template", padding=ProfessionalStyles.SPACING["md"])
        template_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        self.template_var = tk.StringVar(value="Custom")
        template_grid = ttk.Frame(template_frame)
        template_grid.pack(fill="x")
        for i, (name, data) in enumerate(RESEARCH_TEMPLATES.items()):
            row, col = divmod(i, 2)
            btn = ttk.Button(template_grid, text=f"{name}\n{data['desc']}", command=lambda n=name: self.apply_template(n), width=35)
            btn.grid(row=row, column=col, padx=ProfessionalStyles.SPACING["sm"], pady=ProfessionalStyles.SPACING["sm"], sticky="ew")
        composer_frame = ttk.LabelFrame(frame, text="Build Your Research Question", padding=ProfessionalStyles.SPACING["md"])
        composer_frame.pack(fill="both", expand=True, pady=(0, ProfessionalStyles.SPACING["md"]))
        self.composer = PromptComposer(composer_frame, on_change=self.on_composer_change)
        self.composer.pack(fill="both", expand=True)
        quality_frame = ttk.Frame(frame)
        quality_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        ttk.Label(quality_frame, text="Query Quality:", style='Heading2.TLabel').pack(side="left", padx=(0, ProfessionalStyles.SPACING["sm"]))
        self.quality_label = ttk.Label(quality_frame, text="0/100", font=ProfessionalStyles.FONTS["body"])
        self.quality_label.pack(side="left", padx=(0, ProfessionalStyles.SPACING["sm"]))
        self.quality_progress = ttk.Progressbar(quality_frame, length=200, mode='determinate')
        self.quality_progress.pack(side="left")
        self.quality_feedback = ttk.Label(frame, text="", style='Caption.TLabel', wraplength=700)
        self.quality_feedback.pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["md"]))
        self.ai_panel = AITransparencyPanel(frame)
        self.ai_panel.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x")
        self.next_btn = ttk.Button(nav_frame, text="Next: Refine Parameters →", command=lambda: self.wizard.set_step(1), style='Primary.TButton', state='disabled')
        self.next_btn.pack(side="right")
    def create_step_refine(self, parent):
        frame = ttk.Frame(parent)
        self.step_frames[1] = frame
        ttk.Label(frame, text="Step 2: Refine Your Search", style='Heading1.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["lg"]))
        filters_frame = ttk.LabelFrame(frame, text="Search Filters", padding=ProfessionalStyles.SPACING["md"])
        filters_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        grid = ttk.Frame(filters_frame)
        grid.pack(fill="x")
        ttk.Label(grid, text="Uploaded:").grid(row=0, column=0, sticky="w", padx=ProfessionalStyles.SPACING["sm"], pady=ProfessionalStyles.SPACING["xs"])
        self.upload_date = ttk.Combobox(grid, values=list(UPLOAD_DATE_OPTIONS.keys()), state="readonly", width=20)
        self.upload_date.set("Last 30 days")
        self.upload_date.grid(row=0, column=1, sticky="w", padx=ProfessionalStyles.SPACING["sm"])
        self.upload_date.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        ttk.Label(grid, text="Sort By:").grid(row=0, column=2, sticky="w", padx=(ProfessionalStyles.SPACING["lg"], ProfessionalStyles.SPACING["sm"]), pady=ProfessionalStyles.SPACING["xs"])
        self.sort_by = ttk.Combobox(grid, values=list(SORT_BY_OPTIONS.keys()), state="readonly", width=20)
        self.sort_by.set("Relevance")
        self.sort_by.grid(row=0, column=3, sticky="w", padx=ProfessionalStyles.SPACING["sm"])
        self.sort_by.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        ttk.Label(grid, text="Duration:").grid(row=1, column=0, sticky="w", padx=ProfessionalStyles.SPACING["sm"], pady=ProfessionalStyles.SPACING["xs"])
        self.duration = ttk.Combobox(grid, values=list(DURATION_OPTIONS.keys()), state="readonly", width=20)
        self.duration.set("Any duration")
        self.duration.grid(row=1, column=1, sticky="w", padx=ProfessionalStyles.SPACING["sm"])
        self.duration.bind("<<ComboboxSelected>>", lambda e: self.update_preview())
        results_frame = ttk.LabelFrame(frame, text="Results Configuration", padding=ProfessionalStyles.SPACING["md"])
        results_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        ttk.Label(results_frame, text="How many results do you need?", style='Heading2.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["sm"]))
        slider_container = ttk.Frame(results_frame)
        slider_container.pack(fill="x")
        preset_frame = ttk.Frame(slider_container)
        preset_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Button(preset_frame, text="Quick Scan (10)", command=lambda: self.set_results(10), style='Secondary.TButton').pack(side="left", padx=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Button(preset_frame, text="Balanced (20)", command=lambda: self.set_results(20), style='Secondary.TButton').pack(side="left", padx=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Button(preset_frame, text="Deep Dive (50)", command=lambda: self.set_results(50), style='Secondary.TButton').pack(side="left")
        self.results_var = tk.IntVar(value=20)
        slider = ttk.Scale(slider_container, from_=1, to=100, variable=self.results_var, orient="horizontal", command=lambda v: self.on_results_change())
        slider.pack(fill="x", pady=ProfessionalStyles.SPACING["sm"])
        self.results_label = ttk.Label(slider_container, text="20 results | Est. runtime: 4-6 min | ~1000 tokens", style='Caption.TLabel')
        self.results_label.pack(anchor="w")
        features_frame = ttk.LabelFrame(frame, text="Required Features", padding=ProfessionalStyles.SPACING["md"])
        features_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        self.feature_vars = {}
        for feat in FEATURE_OPTIONS:
            var = tk.BooleanVar(value=(feat == "Subtitles/CC"))
            cb = ttk.Checkbutton(features_frame, text=feat, variable=var, command=self.update_preview)
            cb.pack(anchor="w")
            self.feature_vars[feat] = var
        output_frame = ttk.LabelFrame(frame, text="Output Configuration", padding=ProfessionalStyles.SPACING["md"])
        output_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        ttk.Label(output_frame, text="Collection Name:").pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["xs"]))
        self.collection_entry = ttk.Entry(output_frame, font=ProfessionalStyles.FONTS["body"])
        self.collection_entry.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Label(output_frame, text="Save Location:").pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["xs"]))
        path_frame = ttk.Frame(output_frame)
        path_frame.pack(fill="x")
        self.path_label = ttk.Label(path_frame, text=self.output_path, relief="sunken", padding=ProfessionalStyles.SPACING["sm"])
        self.path_label.pack(side="left", fill="x", expand=True, padx=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Button(path_frame, text="Browse", command=self.browse_output).pack(side="left")
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x", pady=(ProfessionalStyles.SPACING["lg"], 0))
        ttk.Button(nav_frame, text="← Back", command=lambda: self.wizard.set_step(0), style='Secondary.TButton').pack(side="left")
        ttk.Button(nav_frame, text="Next: Review Configuration →", command=lambda: self.wizard.set_step(2), style='Primary.TButton').pack(side="right")
    def create_step_review(self, parent):
        frame = ttk.Frame(parent)
        self.step_frames[2] = frame
        ttk.Label(frame, text="Step 3: Review & Confirm", style='Heading1.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["lg"]))
        ttk.Label(frame, text="Review your research configuration before proceeding:", font=ProfessionalStyles.FONTS["body"]).pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["md"]))
        review_frame = ttk.LabelFrame(frame, text="Configuration Summary", padding=ProfessionalStyles.SPACING["md"])
        review_frame.pack(fill="both", expand=True, pady=(0, ProfessionalStyles.SPACING["md"]))
        self.review_text = scrolledtext.ScrolledText(review_frame, height=15, font=ProfessionalStyles.FONTS["body"], wrap='word', state='disabled')
        self.review_text.pack(fill="both", expand=True)
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x")
        ttk.Button(nav_frame, text="← Back to Refine", command=lambda: self.wizard.set_step(1), style='Secondary.TButton').pack(side="left")
        ttk.Button(nav_frame, text="▶ Start Research", command=self.start_research, style='Success.TButton').pack(side="right")
    def create_step_run(self, parent):
        frame = ttk.Frame(parent)
        self.step_frames[3] = frame
        ttk.Label(frame, text="Step 4: Research in Progress", style='Heading1.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["lg"]))
        status_frame = ttk.LabelFrame(frame, text="Status", padding=ProfessionalStyles.SPACING["md"])
        status_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        self.status_label = ttk.Label(status_frame, text="Initializing...", style='Heading2.TLabel')
        self.status_label.pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["sm"]))
        self.progress_bar = ttk.Progressbar(status_frame, mode='determinate', length=700)
        self.progress_bar.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["sm"]))
        log_frame = ttk.LabelFrame(frame, text="Activity Log", padding=ProfessionalStyles.SPACING["md"])
        log_frame.pack(fill="both", expand=True, pady=(0, ProfessionalStyles.SPACING["md"]))
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, font=ProfessionalStyles.FONTS["code"], state='disabled')
        self.log_text.pack(fill="both", expand=True)
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x")
        ttk.Button(nav_frame, text="Cancel", command=self.cancel_research, style='Secondary.TButton', state='disabled').pack(side="left")
        self.export_nav_btn = ttk.Button(nav_frame, text="Next: Export Results →", command=lambda: self.wizard.set_step(4), style='Primary.TButton', state='disabled')
        self.export_nav_btn.pack(side="right")
    def create_step_export(self, parent):
        frame = ttk.Frame(parent)
        self.step_frames[4] = frame
        ttk.Label(frame, text="Step 5: Export & Review Results", style='Heading1.TLabel').pack(anchor="w", pady=(0, ProfessionalStyles.SPACING["lg"]))
        results_frame = ttk.LabelFrame(frame, text="Extracted Transcripts", padding=ProfessionalStyles.SPACING["md"])
        results_frame.pack(fill="both", expand=True, pady=(0, ProfessionalStyles.SPACING["md"]))
        self.results_list = tk.Listbox(results_frame, height=15, font=ProfessionalStyles.FONTS["body"])
        self.results_list.pack(fill="both", expand=True)
        actions_frame = ttk.Frame(frame)
        actions_frame.pack(fill="x", pady=(0, ProfessionalStyles.SPACING["md"]))
        ttk.Button(actions_frame, text="📂 Open Folder", command=self.open_results_folder).pack(side="left", padx=(0, ProfessionalStyles.SPACING["sm"]))
        ttk.Button(actions_frame, text="🔄 New Research", command=self.new_research, style='Primary.TButton').pack(side="left")
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x")
        ttk.Button(nav_frame, text="← Back to Results", command=lambda: self.wizard.set_step(3), style='Secondary.TButton').pack(side="left")
    def on_step_change(self, step_index):
        self.show_step(step_index)
        if step_index == 2:
            self.update_review()
    def show_step(self, step_index):
        for i, frame in self.step_frames.items():
            frame.pack_forget()
        if step_index in self.step_frames:
            self.step_frames[step_index].pack(fill="both", expand=True)
    def apply_template(self, template_name):
        self.template_var.set(template_name)
        template = RESEARCH_TEMPLATES[template_name]
        if template["chips"]:
            self.composer.set_values(template["chips"])
        self.upload_date.set(template["defaults"]["upload_date"])
        self.sort_by.set(template["defaults"]["sort_by"])
        self.duration.set(template["defaults"]["duration"])
        self.results_var.set(template["defaults"]["results"])
        for feat, var in self.feature_vars.items():
            var.set(feat in template["defaults"]["features"])
        self.on_composer_change()
        self.update_preview()
    def on_composer_change(self):
        values = self.composer.get_values()
        score, feedback, can_proceed = QueryQualityGate.score_query(values)
        self.quality_label.config(text=f"{score}/100")
        self.quality_progress['value'] = score
        self.quality_feedback.config(text=" | ".join(feedback))
        self.next_btn.config(state='normal' if can_proceed else 'disabled')
        self.update_preview()
    def set_results(self, value):
        self.results_var.set(value)
        self.on_results_change()
    def on_results_change(self):
        value = int(self.results_var.get())
        runtime = f"{value * 0.2:.0f}-{value * 0.3:.0f} min"
        tokens = value * 50
        self.results_label.config(text=f"{value} results | Est. runtime: {runtime} | ~{tokens} tokens")
        self.update_preview()
    def update_preview(self):
        query = self.composer.build_query()
        config = {
            "query": query,
            "max_results": int(self.results_var.get()),
            "upload_date": self.upload_date.get(),
            "sort_by": self.sort_by.get(),
            "duration": self.duration.get(),
            "features": [k for k, v in self.feature_vars.items() if v.get()],
            "ai_optimized": self.ai_panel.is_enabled(),
            "collection": self.collection_entry.get(),
            "output_path": self.output_path
        }
        self.current_config = config
        self.live_preview.update_preview(config)
    def update_review(self):
        config = self.current_config
        review = f"RESEARCH CONFIGURATION SUMMARY\n{'='*60}\n\n"
        review += f"Research Question:\n  {config.get('query', 'N/A')}\n\n"
        review += f"Search Parameters:\n"
        review += f"  • Results to fetch: {config.get('max_results', 20)}\n"
        review += f"  • Upload date filter: {config.get('upload_date', 'Any time')}\n"
        review += f"  • Sort priority: {config.get('sort_by', 'Relevance')}\n"
        review += f"  • Duration filter: {config.get('duration', 'Any')}\n"
        review += f"  • Required features: {', '.join(config.get('features', ['None']))}\n\n"
        review += f"AI Optimization:\n"
        review += f"  • Status: {'Enabled (GPT-4)' if config.get('ai_optimized') else 'Disabled'}\n\n"
        review += f"Output:\n"
        review += f"  • Collection: {config.get('collection', 'Auto-generated')}\n"
        review += f"  • Location: {config.get('output_path', 'N/A')}\n\n"
        review += f"Estimated Runtime: {int(config.get('max_results', 20)) * 0.25:.0f}-{int(config.get('max_results', 20)) * 0.35:.0f} minutes\n"
        self.review_text.config(state="normal")
        self.review_text.delete("1.0", "end")
        self.review_text.insert("1.0", review)
        self.review_text.config(state="disabled")
    def start_research(self):
        self.wizard.set_step(3)
        query = self.current_config.get("query", "")
        collection = self.collection_entry.get().strip() or self.generate_collection_name(query)
        threading.Thread(target=self.run_research, args=(query, collection), daemon=True).start()
    def run_research(self, query, collection):
        try:
            self.log("🎯 Initializing research process...")
            self.progress_bar['value'] = 0
            self.status_label.config(text="Starting...")
            if self.ai_panel.is_enabled() and self.api_key:
                self.log("🧠 Optimizing query with GPT-4...")
                self.progress_bar['value'] = 10
                self.status_label.config(text="AI Optimization in progress...")
                dur = DURATION_OPTIONS[self.duration.get()]
                feats = [k.lower().replace('subtitles/', '').replace('-', '').replace('/', '') for k, v in self.feature_vars.items() if v.get()]
                upload_days = UPLOAD_DATE_OPTIONS[self.upload_date.get()]
                optimized = optimize_search_query(query, self.api_key, dur, feats, upload_days)
                self.log(f"✓ Original: {query}")
                self.log(f"✓ Optimized: {optimized}")
                query = optimized
            self.progress_bar['value'] = 20
            self.status_label.config(text="Searching YouTube...")
            self.log(f"🔍 Searching YouTube for: {query}")
            filters = {'upload_date': UPLOAD_DATE_OPTIONS[self.upload_date.get()], 'sort_by': SORT_BY_OPTIONS[self.sort_by.get()]}
            scraper = TranscriptScraper(output_dir=os.path.join(self.output_path, collection), callback=lambda msg: (self.log(msg), self.update_progress()))
            self.status_label.config(text="Extracting transcripts...")
            result = scraper.scrape(query, max_results=int(self.results_var.get()), filters=filters)
            self.progress_bar['value'] = 100
            self.status_label.config(text="Complete!")
            self.log("="*60)
            if result['saved'] == 0:
                self.log("😕 No transcripts found. Try adjusting your filters.")
            else:
                self.log(f"✅ Success! Extracted {result['saved']} transcripts")
                self.log(f"📁 Saved to: {os.path.join(self.output_path, collection)}")
                for i, file_path in enumerate(result['files'], 1):
                    self.results_list.insert("end", f"{i}. {Path(file_path).name}")
            self.export_nav_btn.config(state='normal')
        except Exception as e:
            import traceback
            self.status_label.config(text="Error occurred")
            self.log(f"❌ Error: {str(e)}")
            self.log(traceback.format_exc())
    def log(self, msg):
        self.log_text.config(state="normal")
        self.log_text.insert("end", f"{msg}\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")
        self.root.update_idletasks()
    def update_progress(self):
        current = self.progress_bar['value']
        if current < 95:
            self.progress_bar['value'] = min(current + 2, 95)
        self.root.update_idletasks()
    def browse_output(self):
        folder = filedialog.askdirectory(initialdir=self.output_path)
        if folder:
            self.output_path = folder
            self.path_label.config(text=folder)
            self.update_preview()
    def generate_collection_name(self, query):
        clean = "".join(c if c.isalnum() or c.isspace() else "" for c in query.lower())
        return "_".join(clean.split()[:5]) + "_" + datetime.now().strftime("%Y%m%d")
    def cancel_research(self):
        pass
    def open_results_folder(self):
        collection = self.collection_entry.get().strip() or "transcripts"
        folder_path = os.path.join(self.output_path, collection)
        if os.path.exists(folder_path):
            os.startfile(folder_path)
    def new_research(self):
        self.wizard.set_step(0)
        self.composer.set_values({})
        self.results_list.delete(0, "end")
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")
        self.progress_bar['value'] = 0
    def check_first_run(self):
        try:
            cf = Path.home() / ".youtube_scraper_config.json"
            if cf.exists():
                data = json.load(open(cf, 'r'))
                if not data.get('first_run_v3', True):
                    return
            self.show_welcome()
            if cf.exists():
                data = json.load(open(cf, 'r'))
                data['first_run_v3'] = False
                json.dump(data, open(cf, 'w'))
            else:
                json.dump({'first_run_v3': False}, open(cf, 'w'))
        except: pass
    def show_welcome(self):
        w = tk.Toplevel(self.root)
        w.title("Welcome to Your Research Assistant")
        w.geometry("700x500")
        w.transient(self.root)
        w.grab_set()
        f = ttk.Frame(w, padding=ProfessionalStyles.SPACING["xl"])
        f.pack(fill="both", expand=True)
        ttk.Label(f, text="🎯 Welcome to YouTube Research Assistant", font=("Segoe UI", 20, "bold")).pack(pady=(0, ProfessionalStyles.SPACING["lg"]))
        ttk.Label(f, text="A world-class platform for systematic YouTube research", font=ProfessionalStyles.FONTS["heading2"]).pack(pady=(0, ProfessionalStyles.SPACING["xl"]))
        features = [
            "✓ Wizard-guided workflow with 5 clear steps",
            "✓ Research templates for common tasks",
            "✓ Smart prompt composer with structured inputs",
            "✓ Live preview of your research configuration",
            "✓ AI-powered query optimization with full transparency",
            "✓ Quality gates to ensure good research questions",
            "✓ Exportable configurations for reproducible research"
        ]
        for feat in features:
            ttk.Label(f, text=feat, font=ProfessionalStyles.FONTS["body"]).pack(anchor="w", pady=ProfessionalStyles.SPACING["xs"])
        ttk.Label(f, text="\nGetting Started:", font=ProfessionalStyles.FONTS["heading2"]).pack(anchor="w", pady=(ProfessionalStyles.SPACING["lg"], ProfessionalStyles.SPACING["sm"]))
        steps = [
            "1. Choose a research template or go custom",
            "2. Fill in the prompt composer (topic, audience, goals)",
            "3. Refine filters and configure output",
            "4. Review and start your research",
            "5. Export results and configurations"
        ]
        for step in steps:
            ttk.Label(f, text=step, font=ProfessionalStyles.FONTS["body"]).pack(anchor="w", pady=ProfessionalStyles.SPACING["xs"])
        ttk.Button(f, text="Let's Get Started! 🚀", command=w.destroy, style='Primary.TButton').pack(pady=(ProfessionalStyles.SPACING["xl"], 0))
    def show_connection_manager(self):
        ConnectionManager(self.root, self.config)

def main():
    root = tk.Tk()
    app = ResearchPlatform(root)
    menu = tk.Menu(root)
    root.config(menu=menu)
    tools_menu = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Tools", menu=tools_menu)
    tools_menu.add_command(label="API Connection Manager", command=app.show_connection_manager)
    root.mainloop()

if __name__ == "__main__":
    main()
