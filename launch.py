#!/usr/bin/env python3
"""
YouTube Research Platform Launcher

Simple launcher script for the integrated application.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Launch main application
from main_app import main

if __name__ == "__main__":
    main()
