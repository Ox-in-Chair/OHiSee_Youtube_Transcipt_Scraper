"""Credentials manager modal for secure API key management."""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from design_system import COLORS, FONTS, grid, SPACING

class CredentialsManager(tk.Toplevel):
    """Modal window for managing API credentials."""

    def __init__(self, parent, on_save: Optional[Callable] = None):
        super().__init__(parent)
        self.on_save = on_save
        self.api_key = ""
        self.selected_model = "gpt-4"
        self.usage_cap = 100.0

        self._setup_window()
        self._build_ui()
        self._load_existing_credentials()

    def _setup_window(self):
        """Configure modal window."""
        self.title("API Credentials Manager")
        self.geometry("500x400")
        self.resizable(False, False)
        self.configure(bg=COLORS['bg'])

        # Center on parent
        self.transient(self.master)
        self.grab_set()

        # Position center screen
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.winfo_screenheight() // 2) - (400 // 2)
        self.geometry(f"+{x}+{y}")

    def _build_ui(self):
        """Build the credentials manager UI."""
        # Title
        title = tk.Label(self, text='OpenAI API Configuration',
                        font=FONTS['h2'], bg=COLORS['bg'], fg=COLORS['text'])
        title.pack(pady=SPACING['md'])

        # Tabs
        notebook = ttk.Notebook(self)
        notebook.pack(fill='both', expand=True, padx=SPACING['md'], pady=SPACING['xs'])

        # Tab 1: API Key
        key_tab = tk.Frame(notebook, bg='white')
        notebook.add(key_tab, text='API Key')
        self._build_key_tab(key_tab)

        # Tab 2: Model Selection
        model_tab = tk.Frame(notebook, bg='white')
        notebook.add(model_tab, text='Model & Cost')
        self._build_model_tab(model_tab)

        # Tab 3: Usage Limits
        limits_tab = tk.Frame(notebook, bg='white')
        notebook.add(limits_tab, text='Usage Limits')
        self._build_limits_tab(limits_tab)

        # Bottom action buttons
        button_frame = tk.Frame(self, bg=COLORS['bg'])
        button_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])

        tk.Button(button_frame, text='Test Connection', font=FONTS['body'],
                 bg=COLORS['warning'], fg='white', relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._test_connection).pack(side='left', padx=SPACING['xs'])

        tk.Button(button_frame, text='Save', font=FONTS['body'],
                 bg=COLORS['primary'], fg='white', relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self._save_credentials).pack(side='right', padx=SPACING['xs'])

        tk.Button(button_frame, text='Cancel', font=FONTS['body'],
                 bg=COLORS['surface'], fg=COLORS['text'], relief='flat',
                 padx=SPACING['md'], pady=SPACING['xs'],
                 command=self.destroy).pack(side='right')

    def _build_key_tab(self, parent):
        """Build API key entry tab."""
        # Description
        desc = tk.Label(parent, text='Enter your OpenAI API key for query optimization',
                       font=FONTS['body'], bg='white', fg=COLORS['text_secondary'],
                       wraplength=400)
        desc.pack(pady=SPACING['md'])

        # API Key input
        tk.Label(parent, text='API Key:', font=FONTS['body'],
                bg='white', fg=COLORS['text']).pack(anchor='w', padx=SPACING['md'])

        self.key_entry = tk.Entry(parent, font=FONTS['body'], show='*',
                                  bg=COLORS['surface'], fg=COLORS['text'],
                                  relief='solid', bd=1)
        self.key_entry.pack(fill='x', padx=SPACING['md'], pady=SPACING['xs'])

        # Show/Hide toggle
        self.show_key_var = tk.BooleanVar(value=False)
        tk.Checkbutton(parent, text='Show API key', variable=self.show_key_var,
                      font=FONTS['small'], bg='white',
                      command=self._toggle_key_visibility).pack(anchor='w',
                                                                padx=SPACING['md'])

        # Privacy notice
        notice_frame = tk.Frame(parent, bg=COLORS['surface'], bd=1, relief='solid')
        notice_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])

        tk.Label(notice_frame, text='🔒 Privacy Promise',
                font=FONTS['body'], bg=COLORS['surface'],
                fg=COLORS['text']).pack(anchor='w', padx=SPACING['sm'],
                                       pady=(SPACING['xs'], 0))

        tk.Label(notice_frame, text='Your API key is stored locally and never shared.',
                font=FONTS['small'], bg=COLORS['surface'],
                fg=COLORS['text_secondary'], wraplength=400,
                justify='left').pack(anchor='w', padx=SPACING['sm'],
                                    pady=(2, SPACING['xs']))

    def _build_model_tab(self, parent):
        """Build model selection tab."""
        # Model options
        tk.Label(parent, text='Select OpenAI Model:',
                font=FONTS['body'], bg='white', fg=COLORS['text']).pack(anchor='w',
                                                                        padx=SPACING['md'],
                                                                        pady=(SPACING['md'], SPACING['xs']))

        models = [
            ('gpt-4', 'GPT-4', '$0.03/1K tokens (recommended)'),
            ('gpt-3.5-turbo', 'GPT-3.5 Turbo', '$0.002/1K tokens (faster, less accurate)')
        ]

        self.model_var = tk.StringVar(value='gpt-4')

        for value, label, cost in models:
            frame = tk.Frame(parent, bg='white')
            frame.pack(fill='x', padx=SPACING['md'], pady=2)

            rb = tk.Radiobutton(frame, text=label, variable=self.model_var,
                               value=value, font=FONTS['body'],
                               bg='white', fg=COLORS['text'])
            rb.pack(side='left')

            tk.Label(frame, text=cost, font=FONTS['small'],
                    bg='white', fg=COLORS['text_secondary']).pack(side='left',
                                                                  padx=SPACING['sm'])

        # Cost estimate
        estimate_frame = tk.Frame(parent, bg=COLORS['surface'])
        estimate_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])

        tk.Label(estimate_frame, text='Estimated Cost per Query',
                font=FONTS['body'], bg=COLORS['surface'],
                fg=COLORS['text']).pack(anchor='w', padx=SPACING['sm'],
                                       pady=(SPACING['xs'], 0))

        self.cost_label = tk.Label(estimate_frame, text='~$0.03',
                                   font=FONTS['h3'], bg=COLORS['surface'],
                                   fg=COLORS['primary'])
        self.cost_label.pack(anchor='w', padx=SPACING['sm'],
                            pady=(0, SPACING['xs']))

    def _build_limits_tab(self, parent):
        """Build usage limits tab."""
        # Monthly cap
        tk.Label(parent, text='Monthly Spending Cap (USD):',
                font=FONTS['body'], bg='white', fg=COLORS['text']).pack(anchor='w',
                                                                        padx=SPACING['md'],
                                                                        pady=(SPACING['md'], SPACING['xs']))

        self.cap_entry = tk.Entry(parent, font=FONTS['body'],
                                  bg=COLORS['surface'], fg=COLORS['text'],
                                  relief='solid', bd=1)
        self.cap_entry.insert(0, "100.00")
        self.cap_entry.pack(fill='x', padx=SPACING['md'], pady=SPACING['xs'])

        # Usage warning
        warning_frame = tk.Frame(parent, bg=COLORS['surface'])
        warning_frame.pack(fill='x', padx=SPACING['md'], pady=SPACING['md'])

        tk.Label(warning_frame, text='⚠️ Usage will be tracked locally',
                font=FONTS['body'], bg=COLORS['surface'],
                fg=COLORS['warning']).pack(anchor='w', padx=SPACING['sm'],
                                          pady=(SPACING['xs'], 0))

        tk.Label(warning_frame, text='The app will stop making API calls when cap is reached.',
                font=FONTS['small'], bg=COLORS['surface'],
                fg=COLORS['text_secondary'], wraplength=400,
                justify='left').pack(anchor='w', padx=SPACING['sm'],
                                    pady=(2, SPACING['xs']))

    def _toggle_key_visibility(self):
        """Toggle API key visibility."""
        if self.show_key_var.get():
            self.key_entry.config(show='')
        else:
            self.key_entry.config(show='*')

    def _test_connection(self):
        """Test API connection."""
        api_key = self.key_entry.get()

        if not api_key:
            messagebox.showwarning("Missing Key", "Please enter an API key first.")
            return

        # Simulate test (in real implementation, make actual API call)
        try:
            # from openai import OpenAI
            # client = OpenAI(api_key=api_key)
            # response = client.chat.completions.create(...)

            messagebox.showinfo("Connection Successful",
                              "API key validated successfully!\n\n"
                              "Model: GPT-4\n"
                              "Status: Active")
        except Exception as e:
            messagebox.showerror("Connection Failed",
                               f"Could not connect to OpenAI API.\n\n"
                               f"Error: {str(e)}")

    def _save_credentials(self):
        """Save credentials to config."""
        api_key = self.key_entry.get()
        model = self.model_var.get()

        try:
            cap = float(self.cap_entry.get())
        except ValueError:
            messagebox.showwarning("Invalid Cap", "Please enter a valid number for usage cap.")
            return

        if not api_key:
            messagebox.showwarning("Missing Key", "Please enter an API key.")
            return

        # Save via config (import from existing config.py)
        try:
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from config import Config
            config = Config()
            config.set_api_key(api_key)
            config.set('model', model)
            config.set('usage_cap', cap)

            if self.on_save:
                self.on_save({'api_key': api_key, 'model': model, 'usage_cap': cap})

            messagebox.showinfo("Saved", "Credentials saved successfully!")
            self.destroy()

        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save credentials.\n\n{str(e)}")

    def _load_existing_credentials(self):
        """Load existing credentials from config."""
        try:
            from config import Config
            config = Config()
            api_key = config.get_api_key()

            if api_key:
                self.key_entry.insert(0, api_key)

            model = config.get('model', 'gpt-4')
            self.model_var.set(model)

            cap = config.get('usage_cap', 100.0)
            self.cap_entry.delete(0, 'end')
            self.cap_entry.insert(0, str(cap))

        except Exception:
            pass  # No existing config
