"""Intelligence Dashboard Component

Provides the main dashboard interface for displaying:
- ROI scoring and prioritization
- Learning path visualization
- Knowledge search interface
- Implementation progress tracking
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional, Callable


class IntelligenceDashboard:
    """Main intelligence dashboard widget for v2.0 features"""

    def __init__(self, parent, callback: Optional[Callable] = None):
        """Initialize intelligence dashboard

        Args:
            parent: Parent tkinter widget
            callback: Optional logging callback function
        """
        self.parent = parent
        self.callback = callback or (lambda x: None)
        self.data = {}

        # Create main container
        self.container = ttk.Frame(parent)

        # Create tabbed interface for different intelligence features
        self.notebook = ttk.Notebook(self.container)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        # Create tabs
        self.roi_tab = ttk.Frame(self.notebook)
        self.learning_tab = ttk.Frame(self.notebook)
        self.knowledge_tab = ttk.Frame(self.notebook)
        self.progress_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.roi_tab, text="ROI Scoring")
        self.notebook.add(self.learning_tab, text="Learning Paths")
        self.notebook.add(self.knowledge_tab, text="Knowledge Base")
        self.notebook.add(self.progress_tab, text="Progress Tracker")

        # Build each tab
        self._build_roi_tab()
        self._build_learning_tab()
        self._build_knowledge_tab()
        self._build_progress_tab()

    def _build_roi_tab(self):
        """Build ROI scoring tab with prioritization matrix"""
        # Header
        header_frame = ttk.Frame(self.roi_tab)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            header_frame,
            text="ROI Analysis & Prioritization",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="Score and prioritize insights by implementation value",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(anchor="w")

        # Separator
        ttk.Separator(self.roi_tab, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # Filter controls
        filter_frame = ttk.Frame(self.roi_tab)
        filter_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(filter_frame, text="Filter by:").pack(side="left", padx=5)

        self.roi_filter_var = tk.StringVar(value="all")
        filters = [
            ("All Items", "all"),
            ("High ROI (>7)", "high"),
            ("Medium ROI (4-7)", "medium"),
            ("Low ROI (<4)", "low"),
        ]

        for text, value in filters:
            ttk.Radiobutton(
                filter_frame, text=text, variable=self.roi_filter_var, value=value
            ).pack(side="left", padx=5)

        # Sort controls
        sort_frame = ttk.Frame(self.roi_tab)
        sort_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(sort_frame, text="Sort by:").pack(side="left", padx=5)

        self.roi_sort_var = tk.StringVar(value="score_desc")
        sorts = [
            ("ROI Score (High→Low)", "score_desc"),
            ("ROI Score (Low→High)", "score_asc"),
            ("Implementation Time", "time"),
            ("Readiness", "ready"),
        ]

        for text, value in sorts:
            ttk.Radiobutton(sort_frame, text=text, variable=self.roi_sort_var, value=value).pack(
                side="left", padx=5
            )

        # ROI items list with scrollbar
        list_frame = ttk.Frame(self.roi_tab)
        list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        # Canvas for scrolling
        self.roi_canvas = tk.Canvas(list_frame, yscrollcommand=scrollbar.set, highlightthickness=0)
        self.roi_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.roi_canvas.yview)

        # Inner frame for items
        self.roi_items_frame = ttk.Frame(self.roi_canvas)
        self.roi_canvas.create_window((0, 0), window=self.roi_items_frame, anchor="nw")

        # Bind resize
        self.roi_items_frame.bind(
            "<Configure>",
            lambda e: self.roi_canvas.configure(scrollregion=self.roi_canvas.bbox("all")),
        )

        # Action buttons
        action_frame = ttk.Frame(self.roi_tab)
        action_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(action_frame, text="Export ROI Report", command=self._export_roi).pack(
            side="left", padx=5
        )
        ttk.Button(action_frame, text="Refresh Scores", command=self._refresh_roi).pack(
            side="left", padx=5
        )

    def _build_learning_tab(self):
        """Build learning paths tab with sequential recommendations"""
        # Header
        header_frame = ttk.Frame(self.learning_tab)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            header_frame,
            text="Learning Path Generator",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="AI-recommended sequence for optimal learning",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(anchor="w")

        # Separator
        ttk.Separator(self.learning_tab, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # Path options
        options_frame = ttk.Frame(self.learning_tab)
        options_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(options_frame, text="Learning Goal:").pack(side="left", padx=5)

        self.learning_goal_var = tk.StringVar(value="comprehensive")
        goals = [
            ("Comprehensive", "comprehensive"),
            ("Quick Start", "quick"),
            ("Deep Dive", "deep"),
        ]

        for text, value in goals:
            ttk.Radiobutton(
                options_frame, text=text, variable=self.learning_goal_var, value=value
            ).pack(side="left", padx=5)

        # Path visualization
        path_frame = ttk.Frame(self.learning_tab)
        path_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollable canvas
        scrollbar = ttk.Scrollbar(path_frame)
        scrollbar.pack(side="right", fill="y")

        self.path_canvas = tk.Canvas(path_frame, yscrollcommand=scrollbar.set, highlightthickness=0)
        self.path_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.path_canvas.yview)

        self.path_items_frame = ttk.Frame(self.path_canvas)
        self.path_canvas.create_window((0, 0), window=self.path_items_frame, anchor="nw")

        self.path_items_frame.bind(
            "<Configure>",
            lambda e: self.path_canvas.configure(scrollregion=self.path_canvas.bbox("all")),
        )

        # Action buttons
        action_frame = ttk.Frame(self.learning_tab)
        action_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(action_frame, text="Generate Path", command=self._generate_path).pack(
            side="left", padx=5
        )
        ttk.Button(action_frame, text="Export Path", command=self._export_path).pack(
            side="left", padx=5
        )

    def _build_knowledge_tab(self):
        """Build knowledge base search tab"""
        # Header
        header_frame = ttk.Frame(self.knowledge_tab)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(header_frame, text="Knowledge Base Search", font=("Segoe UI", 14, "bold")).pack(
            anchor="w"
        )

        ttk.Label(
            header_frame,
            text="Search across all processed videos and insights",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(anchor="w")

        # Separator
        ttk.Separator(self.knowledge_tab, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # Search controls
        search_frame = ttk.Frame(self.knowledge_tab)
        search_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(search_frame, text="Search Query:").pack(anchor="w", pady=5)

        search_entry_frame = ttk.Frame(search_frame)
        search_entry_frame.pack(fill="x", pady=5)

        self.kb_search_var = tk.StringVar()
        self.kb_search_entry = ttk.Entry(
            search_entry_frame, textvariable=self.kb_search_var, font=("Segoe UI", 11)
        )
        self.kb_search_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        ttk.Button(search_entry_frame, text="Search", command=self._search_knowledge).pack(
            side="left"
        )

        # Search type options
        type_frame = ttk.Frame(self.knowledge_tab)
        type_frame.pack(fill="x", padx=20, pady=5)

        ttk.Label(type_frame, text="Search in:").pack(side="left", padx=5)

        self.kb_search_type = tk.StringVar(value="all")
        search_types = [
            ("All", "all"),
            ("Commands", "commands"),
            ("Prompts", "prompts"),
            ("Tools", "tools"),
            ("Insights", "insights"),
        ]

        for text, value in search_types:
            ttk.Radiobutton(type_frame, text=text, variable=self.kb_search_type, value=value).pack(
                side="left", padx=5
            )

        # Results area
        results_frame = ttk.Frame(self.knowledge_tab)
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        ttk.Label(results_frame, text="Search Results:", font=("Segoe UI", 10)).pack(
            anchor="w", pady=5
        )

        # Scrollable results
        scrollbar = ttk.Scrollbar(results_frame)
        scrollbar.pack(side="right", fill="y")

        self.kb_results_text = tk.Text(
            results_frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("Consolas", 9),
        )
        self.kb_results_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.kb_results_text.yview)

        # Stats label
        self.kb_stats_label = ttk.Label(
            self.knowledge_tab, text="Ready to search", foreground="#6B7280"
        )
        self.kb_stats_label.pack(anchor="w", padx=20, pady=5)

    def _build_progress_tab(self):
        """Build implementation progress tracker tab"""
        # Header
        header_frame = ttk.Frame(self.progress_tab)
        header_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(
            header_frame,
            text="Implementation Progress Tracker",
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor="w")

        ttk.Label(
            header_frame,
            text="Track your implementation journey",
            font=("Segoe UI", 9),
            foreground="#6B7280",
        ).pack(anchor="w")

        # Separator
        ttk.Separator(self.progress_tab, orient="horizontal").pack(fill="x", padx=20, pady=10)

        # Progress summary
        summary_frame = ttk.LabelFrame(self.progress_tab, text="Overall Progress", padding=10)
        summary_frame.pack(fill="x", padx=20, pady=10)

        self.total_items_label = ttk.Label(
            summary_frame, text="Total Items: 0", font=("Segoe UI", 10)
        )
        self.total_items_label.pack(anchor="w", pady=2)

        self.completed_items_label = ttk.Label(
            summary_frame, text="Completed: 0", font=("Segoe UI", 10)
        )
        self.completed_items_label.pack(anchor="w", pady=2)

        self.in_progress_label = ttk.Label(
            summary_frame, text="In Progress: 0", font=("Segoe UI", 10)
        )
        self.in_progress_label.pack(anchor="w", pady=2)

        # Progress bar
        self.progress_bar = ttk.Progressbar(summary_frame, mode="determinate", length=400)
        self.progress_bar.pack(fill="x", pady=10)

        self.progress_percent_label = ttk.Label(
            summary_frame, text="0% Complete", font=("Segoe UI", 10, "bold")
        )
        self.progress_percent_label.pack(anchor="w", pady=2)

        # Item list
        items_frame = ttk.LabelFrame(self.progress_tab, text="Implementation Items", padding=10)
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Scrollable list
        scrollbar = ttk.Scrollbar(items_frame)
        scrollbar.pack(side="right", fill="y")

        self.progress_canvas = tk.Canvas(
            items_frame, yscrollcommand=scrollbar.set, highlightthickness=0
        )
        self.progress_canvas.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.progress_canvas.yview)

        self.progress_items_frame = ttk.Frame(self.progress_canvas)
        self.progress_canvas.create_window((0, 0), window=self.progress_items_frame, anchor="nw")

        self.progress_items_frame.bind(
            "<Configure>",
            lambda e: self.progress_canvas.configure(scrollregion=self.progress_canvas.bbox("all")),
        )

        # Action buttons
        action_frame = ttk.Frame(self.progress_tab)
        action_frame.pack(fill="x", padx=20, pady=10)

        ttk.Button(action_frame, text="Mark Selected Complete", command=self._mark_complete).pack(
            side="left", padx=5
        )
        ttk.Button(action_frame, text="Export Progress Report", command=self._export_progress).pack(
            side="left", padx=5
        )

    def update_data(self, data: Dict):
        """Update dashboard with new intelligence data

        Args:
            data: Dictionary containing ROI scores, learning paths, knowledge base
        """
        self.data = data
        self._refresh_all_tabs()

    def _refresh_all_tabs(self):
        """Refresh all tab contents with current data"""
        self._refresh_roi()
        self._refresh_learning_paths()
        self._refresh_knowledge_stats()
        self._refresh_progress()

    def _refresh_roi(self):
        """Refresh ROI scoring tab with current data"""
        # Clear existing items
        for widget in self.roi_items_frame.winfo_children():
            widget.destroy()

        if not self.data.get("roi_scores"):
            ttk.Label(
                self.roi_items_frame, text="No ROI data available", foreground="#6B7280"
            ).pack(pady=20)
            return

        # Get filter and sort settings
        filter_mode = self.roi_filter_var.get()
        sort_mode = self.roi_sort_var.get()

        # Filter items
        items = self.data["roi_scores"]
        if filter_mode == "high":
            items = [i for i in items if i.get("score", 0) > 7]
        elif filter_mode == "medium":
            items = [i for i in items if 4 <= i.get("score", 0) <= 7]
        elif filter_mode == "low":
            items = [i for i in items if i.get("score", 0) < 4]

        # Sort items
        if sort_mode == "score_desc":
            items = sorted(items, key=lambda x: x.get("score", 0), reverse=True)
        elif sort_mode == "score_asc":
            items = sorted(items, key=lambda x: x.get("score", 0))
        elif sort_mode == "time":
            items = sorted(items, key=lambda x: x.get("time_minutes", 999))
        elif sort_mode == "ready":
            items = sorted(items, key=lambda x: x.get("readiness", ""))

        # Display items
        for idx, item in enumerate(items):
            self._create_roi_item(idx, item)

    def _create_roi_item(self, idx: int, item: Dict):
        """Create ROI item widget

        Args:
            idx: Item index
            item: ROI item data
        """
        frame = ttk.Frame(self.roi_items_frame, relief="solid", borderwidth=1)
        frame.pack(fill="x", padx=5, pady=5)

        # Header with score
        header = ttk.Frame(frame)
        header.pack(fill="x", padx=10, pady=5)

        score = item.get("score", 0)
        score_color = "#10B981" if score > 7 else "#F59E0B" if score >= 4 else "#EF4444"

        ttk.Label(
            header,
            text=f"ROI: {score:.1f}",
            font=("Segoe UI", 12, "bold"),
            foreground=score_color,
        ).pack(side="left", padx=5)

        ttk.Label(header, text=item.get("title", "Unknown"), font=("Segoe UI", 11)).pack(
            side="left", padx=10
        )

        # Metadata
        meta = ttk.Frame(frame)
        meta.pack(fill="x", padx=10, pady=2)

        ttk.Label(meta, text=f"⏱ {item.get('time_minutes', '?')} min", foreground="#6B7280").pack(
            side="left", padx=5
        )
        ttk.Label(meta, text=f"📊 {item.get('readiness', 'Unknown')}", foreground="#6B7280").pack(
            side="left", padx=5
        )
        ttk.Label(meta, text=f"🏷 {item.get('category', 'General')}", foreground="#6B7280").pack(
            side="left", padx=5
        )

    def _refresh_learning_paths(self):
        """Refresh learning paths tab"""
        for widget in self.path_items_frame.winfo_children():
            widget.destroy()

        if not self.data.get("learning_path"):
            ttk.Label(
                self.path_items_frame,
                text="No learning path generated",
                foreground="#6B7280",
            ).pack(pady=20)
            return

        path = self.data["learning_path"]
        for idx, step in enumerate(path, 1):
            self._create_path_step(idx, step)

    def _create_path_step(self, idx: int, step: Dict):
        """Create learning path step widget"""
        frame = ttk.Frame(self.path_items_frame, relief="solid", borderwidth=1)
        frame.pack(fill="x", padx=5, pady=5)

        # Step number
        header = ttk.Frame(frame)
        header.pack(fill="x", padx=10, pady=5)

        ttk.Label(
            header, text=f"Step {idx}", font=("Segoe UI", 11, "bold"), foreground="#1E40AF"
        ).pack(side="left", padx=5)

        ttk.Label(header, text=step.get("title", "Unknown"), font=("Segoe UI", 10)).pack(
            side="left", padx=10
        )

        # Description
        ttk.Label(
            frame,
            text=step.get("description", ""),
            wraplength=600,
            foreground="#4B5563",
        ).pack(anchor="w", padx=10, pady=5)

    def _refresh_knowledge_stats(self):
        """Update knowledge base statistics"""
        total = len(self.data.get("knowledge_base", []))
        self.kb_stats_label.config(text=f"Knowledge base contains {total} entries")

    def _refresh_progress(self):
        """Refresh progress tracker tab"""
        for widget in self.progress_items_frame.winfo_children():
            widget.destroy()

        items = self.data.get("progress_items", [])
        total = len(items)
        completed = len([i for i in items if i.get("status") == "completed"])

        self.total_items_label.config(text=f"Total Items: {total}")
        self.completed_items_label.config(text=f"Completed: {completed}")
        self.in_progress_label.config(
            text=f"In Progress: {len([i for i in items if i.get('status') == 'in_progress'])}"
        )

        if total > 0:
            percent = (completed / total) * 100
            self.progress_bar["value"] = percent
            self.progress_percent_label.config(text=f"{percent:.0f}% Complete")
        else:
            self.progress_bar["value"] = 0
            self.progress_percent_label.config(text="No items to track")

    def _export_roi(self):
        """Export ROI report"""
        self.callback("ROI export functionality - to be implemented")

    def _generate_path(self):
        """Generate learning path"""
        self.callback("Learning path generation - to be implemented")

    def _export_path(self):
        """Export learning path"""
        self.callback("Learning path export - to be implemented")

    def _search_knowledge(self):
        """Search knowledge base"""
        query = self.kb_search_var.get()
        if not query:
            self.kb_results_text.delete("1.0", "end")
            self.kb_results_text.insert("1.0", "Enter a search query")
            return

        self.callback(f"Searching knowledge base for: {query}")
        # Placeholder implementation
        self.kb_results_text.delete("1.0", "end")
        self.kb_results_text.insert("1.0", f"Search results for '{query}':\n\n(To be implemented)")

    def _mark_complete(self):
        """Mark selected items as complete"""
        self.callback("Mark complete functionality - to be implemented")

    def _export_progress(self):
        """Export progress report"""
        self.callback("Progress export functionality - to be implemented")

    def pack(self, **kwargs):
        """Pack the dashboard container"""
        self.container.pack(**kwargs)

    def grid(self, **kwargs):
        """Grid the dashboard container"""
        self.container.grid(**kwargs)
