"""
Configuration management for SocialSentry.
"""

import json
import os
from pathlib import Path


class Config:
    """Manages tool configuration and settings."""

    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.base_dir / "data"
        self.reports_dir = self.base_dir / "reports"
        self.wordlists_dir = self.data_dir / "wordlists"
        self.signatures_dir = self.data_dir / "signatures"

        # Default settings
        self.settings = {
            "timeout": 15,
            "max_threads": 10,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "output_format": "html",
            "verbose": False,
            "rate_limit_delay": 1.0,
        }

        self._load_endpoints()

    def _load_endpoints(self):
        """Load social media endpoint signatures."""
        endpoints_file = self.signatures_dir / "social_media_endpoints.json"
        self.endpoints = {}
        if endpoints_file.exists():
            with open(endpoints_file) as f:
                self.endpoints = json.load(f)
        else:
            self._generate_default_endpoints()

    def _generate_default_endpoints(self):
        """Generate default endpoint configurations."""
        self.endpoints = {
            "facebook": {
                "base_url": "https://www.facebook.com",
                "username_check": "https://www.facebook.com/{username}",
                "recovery_check": "https://www.facebook.com/login/identify?ctx=recover",
            },
            "instagram": {
                "base_url": "https://www.instagram.com",
                "username_check": "https://www.instagram.com/{username}/",
            },
            "youtube": {
                "base_url": "https://www.youtube.com",
                "username_check": "https://www.youtube.com/@{username}",
            },
            "tiktok": {
                "base_url": "https://www.tiktok.com",
                "username_check": "https://www.tiktok.com/@{username}",
            },
            "whatsapp": {
                "base_url": "https://wa.me",
                "check": "https://wa.me/{phone}",
            },
        }
        self._save_endpoints()

    def _save_endpoints(self):
        """Save endpoints to file."""
        self.signatures_dir.mkdir(parents=True, exist_ok=True)
        with open(self.signatures_dir / "social_media_endpoints.json", "w") as f:
            json.dump(self.endpoints, f, indent=4)

    def get(self, key, default=None):
        """Get a configuration value."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set a configuration value."""
        self.settings[key] = value
