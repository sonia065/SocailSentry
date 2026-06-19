"""
Email-to-account mapping module.
Checks if an email is registered on various social platforms.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.utils import validate_email
from ..core.colors import Colors
from ..platforms.facebook import FacebookScanner


class EmailChecker:
    """
    Maps email addresses to social media accounts
    using password recovery flows and public checks.
    """

    def __init__(self, config):
        self.config = config

    def check_all(self, email):
        """
        Check if an email is registered on supported platforms.
        
        Args:
            email: Email address to check
            
        Returns:
            dict: Registration status per platform
        """
        if not validate_email(email):
            print(Colors.status_fail("Invalid email format"))
            return {}

        results = {}
        print(Colors.BOLD + Colors.M + f"\n[ Email Reconnaissance: {email} ]" + Colors.N)
        print("=" * 60)

        # Facebook check
        fb_scanner = FacebookScanner(self.config)
        fb_result = fb_scanner.check_email_registration(email)
        results["facebook"] = fb_result

        # Note about other platforms
        print(Colors.status_info(
            "Checking email registration across platforms typically requires "
            "API access or password recovery flow testing."
        ))
        print(Colors.status_warn(
            "Many platforms rate-limit or block automated email checks. "
            "Manual verification via 'forgot password' is more reliable."
        ))

        print(Colors.BOLD + Colors.G + "\n[ Email Check Complete ]" + Colors.N)
        return results
