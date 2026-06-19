"""
YouTube security assessment module.
For authorized pentesting only.
"""

import re
import json
from ..core.utils import make_request, validate_username
from ..core.colors import Colors


class YouTubeScanner:
    """YouTube channel security assessment scanner."""

    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.youtube.com"
        self.findings = []

    def check_username_exists(self, username):
        """
        Check if a YouTube channel exists by username/handle.
        
        Args:
            username: YouTube handle (with or without @)
            
        Returns:
            bool: Whether the channel exists
        """
        if not validate_username(username.replace("@", "")):
            print(Colors.status_fail("Invalid username format"))
            return False

        # Remove @ if present for checking both formats
        clean_username = username.lstrip("@")

        # Try @handle format (modern YouTube handles)
        urls_to_try = [
            f"{self.base_url}/@{clean_username}",
            f"{self.base_url}/c/{clean_username}",
            f"{self.base_url}/user/{clean_username}",
            f"{self.base_url}/channel/{clean_username}",
        ]

        for url in urls_to_try:
            print(Colors.status_info(f"Checking YouTube: {url}"))

            response = make_request(url, timeout=self.config.get("timeout"))
            if response is None:
                continue

            if response.status_code == 200:
                # Check for channel indicators
                indicators = [
                    '"channelId"',
                    '"title"',
                    'channel-header',
                    'browse_id',
                    'subscriberCount',
                ]
                content = response.text
                matched = [i for i in indicators if i in content]

                if matched:
                    print(Colors.status_ok(f"YouTube channel found: {url}"))
                    self.findings.append({
                        "platform": "youtube",
                        "type": "username_existence",
                        "value": username,
                        "url": url,
                        "status": "found",
                    })
                    return True

        print(Colors.status_fail(f"YouTube channel not found: {username}"))
        return False

    def extract_channel_info(self, username):
        """
        Extract publicly available YouTube channel information.
        
        Args:
            username: Channel handle
            
        Returns:
            dict: Channel information
        """
        clean_username = username.lstrip("@")
        url = f"{self.base_url}/@{clean_username}"
        response = make_request(url)

        info = {
            "handle": clean_username,
            "url": url,
            "exists": False,
            "channel_name": None,
            "subscriber_count": None,
            "is_verified": None,
        }

        if response and response.status_code == 200:
            info["exists"] = True

            # Extract channel name from title
            title_match = re.search(r'<title>([^<]*)</title>', response.text)
            if title_match:
                title = title_match.group(1).replace(" - YouTube", "")
                info["channel_name"] = title.strip()

            # Extract subscriber count
            sub_match = re.search(r'"subscriberCountText":\s*\{[^}]*"simpleText":\s*"([^"]+)"', response.text)
            if sub_match:
                info["subscriber_count"] = sub_match.group(1)

            # Check verification badge
            if '"badges"' in response.text and '"verified"' in response.text.lower():
                info["is_verified"] = True

            print(Colors.BOLD + Colors.C + f"\n[ YouTube Channel: {clean_username} ]" + Colors.N)
            print(f"  Channel Name: {info['channel_name'] or 'N/A'}")
            print(f"  Subscribers: {info['subscriber_count'] or 'N/A'}")
            print(f"  Verified: {info['is_verified']}")

            self.findings.append({
                "platform": "youtube",
                "type": "public_info",
                "value": clean_username,
                "details": info,
            })

        return info

    def run_full_audit(self, target):
        """
        Run a complete YouTube channel security audit.
        
        Args:
            target: Channel handle to audit
            
        Returns:
            list: All findings
        """
        print(Colors.BOLD + Colors.R + "\n[ YouTube Security Audit ]" + Colors.N)
        print("=" * 50)

        self.check_username_exists(target)
        self.extract_channel_info(target)

        return self.findings
