"""Configuration module with settings dialog.

Wraps utils.config.Config and provides a settings dialog UI for
managing API keys and output directory.

Target: ~100 lines
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import json

# Re-export Config class from utils
from utils.config import Config


def open_settings_dialog(parent, config_manager: Config):
    """Open settings dialog for API key and output directory.

    Args:
        parent: Parent tkinter window
        config_manager: Config instance for persisting settings
    """
    dialog = tk.Toplevel(parent)
    dialog.title("Settings")
    dialog.geometry("500x300")
    dialog.transient(parent)
    dialog.grab_set()

    # API Key section
    api_frame = tk.LabelFrame(dialog, text="OpenAI API Key", padx=10, pady=10)
    api_frame.pack(fill='x', padx=15, pady=10)

    ttk.Label(
        api_frame,
        text="Required for AI-powered query optimization (GPT-4):"
    ).pack(anchor='w')

    api_key_entry = ttk.Entry(api_frame, width=50, show='*')
    current_key = config_manager.load_api_key()
    if current_key:
        api_key_entry.insert(0, current_key)
    api_key_entry.pack(pady=5, fill='x')

    # Output directory section
    output_frame = tk.LabelFrame(
        dialog,
        text="Output Directory",
        padx=10,
        pady=10
    )
    output_frame.pack(fill='x', padx=15, pady=10)

    ttk.Label(
        output_frame,
        text="Transcripts will be saved to:"
    ).pack(anchor='w')

    output_row = tk.Frame(output_frame)
    output_row.pack(fill='x', pady=5)

    output_entry = ttk.Entry(output_row)
    current_config = config_manager.load_config()
    output_entry.insert(0, current_config.get('output_dir', 'transcripts'))
    output_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))

    def browse_dir():
        """Browse for output directory."""
        dir_path = filedialog.askdirectory()
        if dir_path:
            output_entry.delete(0, 'end')
            output_entry.insert(0, dir_path)

    ttk.Button(
        output_row,
        text="Browse",
        command=browse_dir
    ).pack(side='right')

    # Save button
    def save_settings():
        """Save settings to config file."""
        api_key = api_key_entry.get().strip()
        output_dir = output_entry.get().strip()

        # Save API key
        if api_key:
            config_manager.save_api_key(api_key)

        # Save output directory
        config = config_manager.load_config()
        config['output_dir'] = output_dir

        config_file = Path.home() / ".youtube_scraper_config.json"
        with open(config_file, "w") as f:
            json.dump(config, f, indent=2)

        dialog.destroy()
        messagebox.showinfo("Settings", "Settings saved successfully!")

    ttk.Button(
        dialog,
        text="Save Settings",
        command=save_settings
    ).pack(pady=10)
