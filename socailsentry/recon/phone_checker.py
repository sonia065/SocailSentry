"""
Phone number reconnaissance module.
"""

from ..core.utils import validate_phone
from ..core.colors import Colors
from ..platforms.whatsapp import WhatsAppScanner


class PhoneChecker:
    """
    Phone number reconnaissance across platforms
    that use phone numbers for identification.
    """

    def __init__(self, config):
        self.config = config

    def check_all(self, phone):
        """
        Check phone number across supported platforms.
        
        Args:
            phone: Phone number with country code
            
        Returns:
            dict: Results per platform
        """
        cleaned = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
        if not validate_phone(cleaned):
            print(Colors.status_fail("Invalid phone number format"))
            return {}

        results = {}
        print(Colors.BOLD + Colors.M + f"\n[ Phone Reconnaissance: {cleaned} ]" + Colors.N)
        print("=" * 60)

        # WhatsApp check
        wa_scanner = WhatsAppScanner(self.config)
        wa_result = wa_scanner.check_phone_number(cleaned)
        results["whatsapp"] = wa_result

        # Note
        print(Colors.status_info(
            "Phone-based social media lookup is limited without API access. "
            "Platforms like Facebook and Instagram don't expose phone-to-account "
            "mapping via public endpoints."
        ))

        return results
