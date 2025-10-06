"""Settings Panel Component

Provides configuration interface for all v2.0 modules:
- CORE-001 settings (analysis mode, summary depth)
- INTEL-001 settings (ROI weights, learning path goals)
- VISUAL-001 settings (diagram types, complexity)
- EXEC-001 settings (playbook format, checklist type)
- KNOWLEDGE-001 settings (database, deduplication)
- API key management
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Optional, Callable
import json


class SettingsPanel:
    """Module configuration settings panel"""

    def __init__(self, parent, callback: Optional[Callable] = None):
        """Initialize settings panel

        Args:
            parent: Parent tkinter widget
            callback: Optional logging callback function
        """
        self.parent = parent
        self.callback = callback or (lambda x: None)
        self.settings = self._load_default_settings()

        # Create main container
        self.container = ttk.Frame(parent)

        # Build UI
        self._build_header()
        self._build_tabs()
        self._build_actions()

    def _build_header(self):
        """Build header section"""
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(header_frame, text="Module Settings", font=("Segoe UI", 14, "bold")).pack(
            anchor="w"
        )

        ttk.Label(
            header_frame,
            text="Configure intelligence modules and preferences",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(anchor="w")

        ttk.Separator(self.container, orient="horizontal").pack(fill="x", padx=20, pady=10)

    def _build_tabs(self):
        """Build tabbed settings interface"""
        # Create notebook
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        # Create tabs
        self.core_tab = ttk.Frame(self.notebook)
        self.intel_tab = ttk.Frame(self.notebook)
        self.visual_tab = ttk.Frame(self.notebook)
        self.exec_tab = ttk.Frame(self.notebook)
        self.knowledge_tab = ttk.Frame(self.notebook)
        self.api_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.core_tab, text="CORE-001")
        self.notebook.add(self.intel_tab, text="INTEL-001")
        self.notebook.add(self.visual_tab, text="VISUAL-001")
        self.notebook.add(self.exec_tab, text="EXEC-001")
        self.notebook.add(self.knowledge_tab, text="KNOWLEDGE-001")
        self.notebook.add(self.api_tab, text="API Keys")

        # Build each tab
        self._build_core_tab()
        self._build_intel_tab()
        self._build_visual_tab()
        self._build_exec_tab()
        self._build_knowledge_tab()
        self._build_api_tab()

    def _build_core_tab(self):
        """Build CORE-001 settings tab"""
        frame = ttk.LabelFrame(self.core_tab, text="Summary Engine Settings", padding=20)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Analysis mode
        ttk.Label(frame, text="Analysis Mode:", font=("Segoe UI", 10)).pack(anchor="w", pady=5)

        self.core_mode_var = tk.StringVar(value=self.settings["core"]["mode"])
        modes = [
            ("Quick (10-15 items, ~$0.15)", "quick"),
            ("Developer (50-100 items, ~$0.30)", "developer"),
            ("Research (75-150 items, ~$0.50)", "research"),
        ]

        for text, value in modes:
            ttk.Radiobutton(frame, text=text, variable=self.core_mode_var, value=value).pack(
                anchor="w", padx=20, pady=2
            )

        # Summary depth
        ttk.Label(frame, text="Summary Depth (items):", font=("Segoe UI", 10)).pack(
            anchor="w", pady=(10, 5)
        )

        depth_frame = ttk.Frame(frame)
        depth_frame.pack(anchor="w", padx=20)

        self.core_depth_var = tk.IntVar(value=self.settings["core"]["depth"])
        self.core_depth_scale = ttk.Scale(
            depth_frame,
            from_=10,
            to=150,
            orient="horizontal",
            variable=self.core_depth_var,
            length=300,
        )
        self.core_depth_scale.pack(side="left", padx=5)

        self.core_depth_label = ttk.Label(depth_frame, text=f"{self.core_depth_var.get()}")
        self.core_depth_label.pack(side="left", padx=5)

        self.core_depth_var.trace_add(
            "write", lambda *args: self.core_depth_label.config(text=f"{self.core_depth_var.get()}")
        )

        # Synthesis enabled
        self.core_synthesis_var = tk.BooleanVar(value=self.settings["core"]["synthesis_enabled"])
        ttk.Checkbutton(
            frame,
            text="Enable cross-video synthesis",
            variable=self.core_synthesis_var,
        ).pack(anchor="w", pady=10)

    def _build_intel_tab(self):
        """Build INTEL-001 settings tab"""
        frame = ttk.LabelFrame(self.intel_tab, text="Intelligence Layer Settings", padding=20)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # ROI weights
        ttk.Label(frame, text="ROI Scoring Weights:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=5
        )

        weights_frame = ttk.Frame(frame)
        weights_frame.pack(fill="x", padx=20, pady=5)

        # Implementation time weight
        ttk.Label(weights_frame, text="Implementation Time:").grid(
            row=0, column=0, sticky="w", pady=2
        )
        self.intel_time_weight = tk.DoubleVar(value=self.settings["intel"]["roi_weights"]["time"])
        ttk.Scale(
            weights_frame,
            from_=0,
            to=1,
            orient="horizontal",
            variable=self.intel_time_weight,
        ).grid(row=0, column=1, padx=10, pady=2)
        ttk.Label(weights_frame, textvariable=self.intel_time_weight).grid(row=0, column=2, pady=2)

        # Complexity weight
        ttk.Label(weights_frame, text="Complexity:").grid(row=1, column=0, sticky="w", pady=2)
        self.intel_complexity_weight = tk.DoubleVar(
            value=self.settings["intel"]["roi_weights"]["complexity"]
        )
        ttk.Scale(
            weights_frame,
            from_=0,
            to=1,
            orient="horizontal",
            variable=self.intel_complexity_weight,
        ).grid(row=1, column=1, padx=10, pady=2)
        ttk.Label(weights_frame, textvariable=self.intel_complexity_weight).grid(
            row=1, column=2, pady=2
        )

        # Readiness weight
        ttk.Label(weights_frame, text="Readiness:").grid(row=2, column=0, sticky="w", pady=2)
        self.intel_readiness_weight = tk.DoubleVar(
            value=self.settings["intel"]["roi_weights"]["readiness"]
        )
        ttk.Scale(
            weights_frame,
            from_=0,
            to=1,
            orient="horizontal",
            variable=self.intel_readiness_weight,
        ).grid(row=2, column=1, padx=10, pady=2)
        ttk.Label(weights_frame, textvariable=self.intel_readiness_weight).grid(
            row=2, column=2, pady=2
        )

        # Learning path goal
        ttk.Label(frame, text="Learning Path Goal:", font=("Segoe UI", 10)).pack(
            anchor="w", pady=(10, 5)
        )

        self.intel_goal_var = tk.StringVar(value=self.settings["intel"]["learning_goal"])
        goals = [
            ("Comprehensive", "comprehensive"),
            ("Quick Start", "quick"),
            ("Deep Dive", "deep"),
        ]

        for text, value in goals:
            ttk.Radiobutton(frame, text=text, variable=self.intel_goal_var, value=value).pack(
                anchor="w", padx=20, pady=2
            )

    def _build_visual_tab(self):
        """Build VISUAL-001 settings tab"""
        frame = ttk.LabelFrame(self.visual_tab, text="Visualization Settings", padding=20)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Diagram types to generate
        ttk.Label(frame, text="Generate Diagrams:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=5
        )

        self.visual_timeline_var = tk.BooleanVar(value=self.settings["visual"]["types"]["timeline"])
        self.visual_architecture_var = tk.BooleanVar(
            value=self.settings["visual"]["types"]["architecture"]
        )
        self.visual_comparison_var = tk.BooleanVar(
            value=self.settings["visual"]["types"]["comparison"]
        )
        self.visual_flowchart_var = tk.BooleanVar(
            value=self.settings["visual"]["types"]["flowchart"]
        )

        ttk.Checkbutton(frame, text="Timeline Diagram", variable=self.visual_timeline_var).pack(
            anchor="w", padx=20, pady=2
        )
        ttk.Checkbutton(
            frame, text="Architecture Diagram", variable=self.visual_architecture_var
        ).pack(anchor="w", padx=20, pady=2)
        ttk.Checkbutton(frame, text="Comparison Matrix", variable=self.visual_comparison_var).pack(
            anchor="w", padx=20, pady=2
        )
        ttk.Checkbutton(frame, text="Flowchart", variable=self.visual_flowchart_var).pack(
            anchor="w", padx=20, pady=2
        )

        # Complexity level
        ttk.Label(frame, text="Diagram Complexity:", font=("Segoe UI", 10)).pack(
            anchor="w", pady=(10, 5)
        )

        self.visual_complexity_var = tk.StringVar(value=self.settings["visual"]["complexity"])
        complexities = [
            ("Simple", "simple"),
            ("Detailed", "detailed"),
            ("Comprehensive", "comprehensive"),
        ]

        for text, value in complexities:
            ttk.Radiobutton(
                frame, text=text, variable=self.visual_complexity_var, value=value
            ).pack(anchor="w", padx=20, pady=2)

    def _build_exec_tab(self):
        """Build EXEC-001 settings tab"""
        frame = ttk.LabelFrame(self.exec_tab, text="Execution Layer Settings", padding=20)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Playbook format
        ttk.Label(frame, text="Playbook Format:", font=("Segoe UI", 10)).pack(anchor="w", pady=5)

        self.exec_format_var = tk.StringVar(value=self.settings["exec"]["format"])
        formats = [
            ("Markdown", "markdown"),
            ("JSON", "json"),
            ("HTML", "html"),
        ]

        for text, value in formats:
            ttk.Radiobutton(frame, text=text, variable=self.exec_format_var, value=value).pack(
                anchor="w", padx=20, pady=2
            )

        # Checklist type
        ttk.Label(frame, text="Checklist Type:", font=("Segoe UI", 10)).pack(
            anchor="w", pady=(10, 5)
        )

        self.exec_checklist_var = tk.StringVar(value=self.settings["exec"]["checklist_type"])
        checklist_types = [
            ("Simple", "simple"),
            ("Interactive", "interactive"),
            ("Detailed", "detailed"),
        ]

        for text, value in checklist_types:
            ttk.Radiobutton(frame, text=text, variable=self.exec_checklist_var, value=value).pack(
                anchor="w", padx=20, pady=2
            )

        # Include troubleshooting
        self.exec_troubleshoot_var = tk.BooleanVar(
            value=self.settings["exec"]["include_troubleshooting"]
        )
        ttk.Checkbutton(
            frame,
            text="Include troubleshooting tips",
            variable=self.exec_troubleshoot_var,
        ).pack(anchor="w", pady=10)

    def _build_knowledge_tab(self):
        """Build KNOWLEDGE-001 settings tab"""
        frame = ttk.LabelFrame(self.knowledge_tab, text="Knowledge Base Settings", padding=20)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Deduplication threshold
        ttk.Label(frame, text="Deduplication Threshold:", font=("Segoe UI", 10)).pack(
            anchor="w", pady=5
        )

        threshold_frame = ttk.Frame(frame)
        threshold_frame.pack(anchor="w", padx=20)

        self.knowledge_threshold_var = tk.DoubleVar(
            value=self.settings["knowledge"]["dedup_threshold"]
        )
        ttk.Scale(
            threshold_frame,
            from_=0.5,
            to=1.0,
            orient="horizontal",
            variable=self.knowledge_threshold_var,
            length=300,
        ).pack(side="left", padx=5)

        ttk.Label(threshold_frame, textvariable=self.knowledge_threshold_var).pack(
            side="left", padx=5
        )

        # Auto-save interval
        ttk.Label(frame, text="Auto-save interval (minutes):", font=("Segoe UI", 10)).pack(
            anchor="w", pady=(10, 5)
        )

        self.knowledge_autosave_var = tk.IntVar(
            value=self.settings["knowledge"]["autosave_minutes"]
        )
        ttk.Spinbox(frame, from_=1, to=60, textvariable=self.knowledge_autosave_var, width=10).pack(
            anchor="w", padx=20, pady=2
        )

        # Enable journal
        self.knowledge_journal_var = tk.BooleanVar(
            value=self.settings["knowledge"]["enable_journal"]
        )
        ttk.Checkbutton(
            frame,
            text="Enable implementation journal",
            variable=self.knowledge_journal_var,
        ).pack(anchor="w", pady=10)

    def _build_api_tab(self):
        """Build API keys tab"""
        frame = ttk.LabelFrame(self.api_tab, text="API Configuration", padding=20)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # OpenAI API key
        ttk.Label(frame, text="OpenAI API Key:", font=("Segoe UI", 10)).pack(anchor="w", pady=5)

        key_frame = ttk.Frame(frame)
        key_frame.pack(fill="x", padx=20, pady=5)

        self.api_key_var = tk.StringVar(value=self.settings["api"]["openai_key"])
        self.api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            key_frame,
            text="Show",
            variable=self.show_key_var,
            command=self._toggle_key_visibility,
        ).pack(side="left")

        # Test API button
        ttk.Button(frame, text="Test API Connection", command=self._test_api).pack(
            anchor="w", padx=20, pady=10
        )

        # API status
        self.api_status_label = ttk.Label(
            frame, text="API status: Not tested", foreground="#6B7280"
        )
        self.api_status_label.pack(anchor="w", padx=20, pady=5)

    def _build_actions(self):
        """Build action buttons"""
        action_frame = ttk.Frame(self.container)
        action_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(action_frame, text="Save Settings", command=self._save_settings).pack(
            side="left", padx=5
        )

        ttk.Button(action_frame, text="Reset to Defaults", command=self._reset_defaults).pack(
            side="left", padx=5
        )

        ttk.Button(action_frame, text="Export Settings", command=self._export_settings).pack(
            side="left", padx=5
        )

    def _load_default_settings(self) -> Dict:
        """Load default settings configuration"""
        return {
            "core": {"mode": "developer", "depth": 50, "synthesis_enabled": True},
            "intel": {
                "roi_weights": {"time": 0.4, "complexity": 0.3, "readiness": 0.3},
                "learning_goal": "comprehensive",
            },
            "visual": {
                "types": {
                    "timeline": True,
                    "architecture": True,
                    "comparison": True,
                    "flowchart": True,
                },
                "complexity": "detailed",
            },
            "exec": {
                "format": "markdown",
                "checklist_type": "interactive",
                "include_troubleshooting": True,
            },
            "knowledge": {
                "dedup_threshold": 0.85,
                "autosave_minutes": 5,
                "enable_journal": True,
            },
            "api": {"openai_key": ""},
        }

    def _toggle_key_visibility(self):
        """Toggle API key visibility"""
        if self.show_key_var.get():
            self.api_key_entry.config(show="")
        else:
            self.api_key_entry.config(show="*")

    def _test_api(self):
        """Test API connection"""
        api_key = self.api_key_var.get()
        if not api_key:
            self.api_status_label.config(text="API status: No key provided", foreground="#EF4444")
            return

        self.api_status_label.config(text="API status: Testing...", foreground="#F59E0B")
        self.callback("Testing API connection...")

        # Placeholder - actual implementation would test OpenAI API
        # For now, just validate format
        if api_key.startswith("sk-"):
            self.api_status_label.config(
                text="API status: Key format valid ✓", foreground="#10B981"
            )
        else:
            self.api_status_label.config(
                text="API status: Invalid key format", foreground="#EF4444"
            )

    def _save_settings(self):
        """Save current settings"""
        # Update settings dict
        self.settings["core"]["mode"] = self.core_mode_var.get()
        self.settings["core"]["depth"] = self.core_depth_var.get()
        self.settings["core"]["synthesis_enabled"] = self.core_synthesis_var.get()

        self.settings["intel"]["roi_weights"]["time"] = self.intel_time_weight.get()
        self.settings["intel"]["roi_weights"]["complexity"] = self.intel_complexity_weight.get()
        self.settings["intel"]["roi_weights"]["readiness"] = self.intel_readiness_weight.get()
        self.settings["intel"]["learning_goal"] = self.intel_goal_var.get()

        self.settings["visual"]["types"]["timeline"] = self.visual_timeline_var.get()
        self.settings["visual"]["types"]["architecture"] = self.visual_architecture_var.get()
        self.settings["visual"]["types"]["comparison"] = self.visual_comparison_var.get()
        self.settings["visual"]["types"]["flowchart"] = self.visual_flowchart_var.get()
        self.settings["visual"]["complexity"] = self.visual_complexity_var.get()

        self.settings["exec"]["format"] = self.exec_format_var.get()
        self.settings["exec"]["checklist_type"] = self.exec_checklist_var.get()
        self.settings["exec"]["include_troubleshooting"] = self.exec_troubleshoot_var.get()

        self.settings["knowledge"]["dedup_threshold"] = self.knowledge_threshold_var.get()
        self.settings["knowledge"]["autosave_minutes"] = self.knowledge_autosave_var.get()
        self.settings["knowledge"]["enable_journal"] = self.knowledge_journal_var.get()

        self.settings["api"]["openai_key"] = self.api_key_var.get()

        messagebox.showinfo("Settings Saved", "All settings have been saved successfully")
        self.callback("Settings saved successfully")

    def _reset_defaults(self):
        """Reset all settings to defaults"""
        if messagebox.askyesno(
            "Reset Settings", "Are you sure you want to reset all settings to defaults?"
        ):
            self.settings = self._load_default_settings()
            self._update_ui_from_settings()
            self.callback("Settings reset to defaults")

    def _update_ui_from_settings(self):
        """Update UI elements from settings dict"""
        # Update all variables from settings
        self.core_mode_var.set(self.settings["core"]["mode"])
        self.core_depth_var.set(self.settings["core"]["depth"])
        self.core_synthesis_var.set(self.settings["core"]["synthesis_enabled"])

        self.intel_time_weight.set(self.settings["intel"]["roi_weights"]["time"])
        self.intel_complexity_weight.set(self.settings["intel"]["roi_weights"]["complexity"])
        self.intel_readiness_weight.set(self.settings["intel"]["roi_weights"]["readiness"])
        self.intel_goal_var.set(self.settings["intel"]["learning_goal"])

        self.visual_timeline_var.set(self.settings["visual"]["types"]["timeline"])
        self.visual_architecture_var.set(self.settings["visual"]["types"]["architecture"])
        self.visual_comparison_var.set(self.settings["visual"]["types"]["comparison"])
        self.visual_flowchart_var.set(self.settings["visual"]["types"]["flowchart"])
        self.visual_complexity_var.set(self.settings["visual"]["complexity"])

        self.exec_format_var.set(self.settings["exec"]["format"])
        self.exec_checklist_var.set(self.settings["exec"]["checklist_type"])
        self.exec_troubleshoot_var.set(self.settings["exec"]["include_troubleshooting"])

        self.knowledge_threshold_var.set(self.settings["knowledge"]["dedup_threshold"])
        self.knowledge_autosave_var.set(self.settings["knowledge"]["autosave_minutes"])
        self.knowledge_journal_var.set(self.settings["knowledge"]["enable_journal"])

        self.api_key_var.set(self.settings["api"]["openai_key"])

    def _export_settings(self):
        """Export settings to JSON file"""
        from tkinter import filedialog

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="youtube_scraper_settings.json",
        )

        if not filepath:
            return

        # Save current settings first
        self._save_settings()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2)

        messagebox.showinfo("Export Success", f"Settings exported to:\n{filepath}")
        self.callback(f"Settings exported to: {filepath}")

    def get_settings(self) -> Dict:
        """Get current settings dictionary

        Returns:
            Current settings configuration
        """
        return self.settings

    def pack(self, **kwargs):
        """Pack the panel container"""
        self.container.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the panel container"""
        self.container.grid(**kwargs)
