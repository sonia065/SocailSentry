"""
WhatsApp security assessment module.
For authorized pentesting only.
"""

import re
import json
from ..core.utils import make_request, validate_phone
from ..core.colors import Colors


class WhatsAppScanner:
    """WhatsApp account security assessment scanner."""

    def __init__(self, config):
        self.config = config
        self.base_url = "https://wa.me"
        self.findings = []

    def check_phone_number(self, phone):
        """
        Check if a phone number is associated with WhatsApp.
        
        Note: WhatsApp doesn't expose account existence via web.
        This checks the wa.me link format and basic validation.
        
        Args:
            phone: Phone number with country code
            
        Returns:
            dict: Check results
        """
        cleaned = re.sub(r'[\s\-\+\(\)]', '', phone)
        if not validate_phone(cleaned):
            print(Colors.status_fail("Invalid phone number format. Use format: 1234567890"))
            return {"valid": False}

        url = f"{self.base_url}/{cleaned}"
        print(Colors.status_info(f"Checking WhatsApp link: {url}"))

        # wa.me redirects to whatsapp:// or web.whatsapp.com
        # We can only verify the URL format is valid
        print(Colors.status_info(f"You can verify WhatsApp account by sending a message to: {url}"))
        print(Colors.status_warn("WhatsApp does not provide a public API to check account existence."))

        self.findings.append({
            "platform": "whatsapp",
            "type": "phone_check",
            "value": phone,
            "url": url,
            "note": "Manual verification required - send a message to confirm",
        })

        return {
            "platform": "whatsapp",
            "phone": cleaned,
            "url": url,
            "format_valid": True,
            "note": "WhatsApp account verification requires sending a message via the app",
        }

    def analyze_whatsapp_web_security(self):
        """
        Analyze WhatsApp Web security considerations.
        Returns security recommendations for WhatsApp Web usage.
        """
        recommendations = [
            {
                "area": "WhatsApp Web Sessions",
                "risk": "Medium",
                "description": "WhatsApp Web sessions can be hijacked if QR code is intercepted",
                "recommendation": "Always verify QR codes before scanning. Log out of unused sessions.",
            },
            {
                "area": "End-to-End Encryption",
                "risk": "Info",
                "description": "WhatsApp uses E2E encryption but metadata is still visible",
                "recommendation": "Be aware that sender/recipient metadata is logged",
            },
            {
                "area": "Two-Step Verification",
                "risk": "Info",
                "description": "WhatsApp 2FA prevents SIM swap attacks",
                "recommendation": "Enable two-step verification in WhatsApp settings",
            },
        ]

        print(Colors.BOLD + Colors.G + "\n[ WhatsApp Security Recommendations ]" + Colors.N)
        print("=" * 50)
        for rec in recommendations:
            print(f"  [{rec['area']}] ({rec['risk']})")
            print(f"  {rec['description']}")
            print(f"  → {rec['recommendation']}\n")

        self.findings.extend(recommendations)
        return recommendations

    def run_full_audit(self, target):
        """
        Run a WhatsApp security audit.
        
        Args:
            target: Phone number to check
            
        Returns:
            list: All findings
        """
        print(Colors.BOLD + Colors.G + "\n[ WhatsApp Security Audit ]" + Colors.N)
        print("=" * 50)

        self.check_phone_number(target)
        self.analyze_whatsapp_web_security()

        return self.findings
