"""
Two-Factor Authentication detection module.
Checks if 2FA options are available on target platforms.
"""

from ..core.colors import Colors


class TwoFAChecker:
    """
    Analyzes 2FA availability and security configurations
    for social media platforms.
    """

    def __init__(self, config):
        self.config = config

    def check_platform_2fa(self, platform):
        """
        Check 2FA options available for a specific platform.
        
        Args:
            platform: Platform name
            
        Returns:
            dict: 2FA information
        """
        # Known 2FA support information for each platform
        platform_2fa = {
            "facebook": {
                "supports_2fa": True,
                "methods": ["SMS", "Authenticator App", "Security Key", "Recovery Codes"],
                "recommended": "Authenticator App or Security Key",
                "notes": "Facebook also supports login alerts and trusted contacts",
            },
            "instagram": {
                "supports_2fa": True,
                "methods": ["SMS", "Authenticator App", "Recovery Codes"],
                "recommended": "Authenticator App",
                "notes": "Instagram 2FA prevents account takeover even if password is compromised",
            },
            "youtube": {
                "supports_2fa": True,
                "methods": ["SMS", "Authenticator App", "Security Key", "Recovery Codes"],
                "recommended": "Security Key or Authenticator App",
                "notes": "YouTube uses Google account 2FA - enable Advanced Protection for highest security",
            },
            "tiktok": {
                "supports_2fa": True,
                "methods": ["SMS", "Authenticator App", "Recovery Codes"],
                "recommended": "Authenticator App",
                "notes": "TikTok also supports login verification through trusted devices",
            },
            "whatsapp": {
                "supports_2fa": True,
                "methods": ["SMS", "Authenticator App (via Google/Apple)"],
                "recommended": "Two-step verification in settings",
                "notes": "WhatsApp 2FA prevents SIM swap attacks on
