"""Configuration management for YouTube Transcript Scraper"""

import json
from pathlib import Path


class Config:
    """Manages persistent configuration (API keys, settings)"""

    def __init__(self):
        self.config_file = Path.home() / ".youtube_scraper_config.json"

    def save_api_key(self, key):
        """Save OpenAI API key to config file"""
        config = self.load_config()
        config["openai_api_key"] = key
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def load_api_key(self):
        """Load OpenAI API key from config"""
        config = self.load_config()
        return config.get("openai_api_key", "")

    def load_config(self):
        """Load full config or return empty dict"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except:
                return {}
        return {}
