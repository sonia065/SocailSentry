"""
TikTok security assessment module.
For authorized pentesting only.
"""

import re
import json
from ..core.utils import make_request, validate_username
from ..core.colors import Colors


class TikTokScanner:
    """TikTok account security assessment scanner."""

    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.tiktok.com"
        self.findings = []

    def check_username_exists(self, username):
        """
        Check if a TikTok username exists.
        
        Args:
            username: TikTok username (with or without @)
            
        Returns:
            bool: Whether the profile exists
        """
        if not validate_username(username.replace("@", "")):
            print(Colors.status_fail("Invalid username format"))
            return False

        clean_username = username.lstrip("@")
        url = f"{self.base_url}/@{clean_username}"
        print(Colors.status_info(f"Checking TikTok: {url}"))

        response = make_request(url, timeout=self.config.get("timeout"))
        if response is None:
            return False

        if response.status_code == 200:
            # Check for profile data in page source
            indicators = [
                '"userInfo"',
                '"uniqueId"',
                '"nickname"',
                "SIGI_STATE",
            ]
            content = response.text
            matched = [i for i in indicators if i in content]

            if matched:
                print(Colors.status_ok(f"TikTok profile found: {url}"))
                self.findings.append({
                    "platform": "tiktok",
                    "type": "username_existence",
                    "value": username,
                    "url": url,
                    "status": "found",
                })
                return True

        if response.status_code == 404:
            print(Colors.status_fail(f"TikTok profile not found: {username}"))
            return False

        print(Colors.status_warn(f"TikTok check ambiguous for: {username} (HTTP {response.status_code})"))
        return False

    def extract_public_info(self, username):
        """
        Extract publicly available TikTok profile information.
        
        Args:
            username: Target username
            
        Returns:
            dict: Profile information
        """
        clean_username = username.lstrip("@")
        url = f"{self.base_url}/@{clean_username}"
        response = make_request(url)

        info = {
            "username": clean_username,
            "url": url,
            "exists": False,
            "display_name": None,
            "bio": None,
            "follower_count": None,
            "following_count": None,
            "like_count": None,
            "is_verified": None,
        }

        if response and response.status_code == 200:
            info["exists"] = True

            # Try to extract from SIGI_STATE or other embedded data
            sigi_match = re.search(
                r'window\.SIGI_STATE\s*=\s*({.*?});',
                response.text,
                re.DOTALL
            )
            if sigi_match:
                try:
                    data = json.loads(sigi_match.group(1))
                    user_module = data.get("UserModule", {})
                    users = user_module.get("users", {})
                    user_data = users.get(clean_username, {})

                    info["display_name"] = user_data.get("nickname")
                    info["bio"] = user_data.get("signature")
                    info["follower_count"] = user_data.get("followerCount")
                    info["following_count"] = user_data.get("followingCount")
                    info["like_count"] = user_data.get("heartCount")
                    info["is_verified"] = user_data.get("verified", False)

                except (json.JSONDecodeError, AttributeError):
                    pass

            # Fallback extraction from HTML
            if not info["display_name"]:
                name_match = re.search(r'<title>([^<]*)</title>', response.text)
                if name_match:
                    title = name_match.group(1).replace(" (@", "|").split("|")[0]
                    info["display_name"] = title.strip()

            print(Colors.BOLD + Colors.C + f"\n[ TikTok Profile: {clean_username} ]" + Colors.N)
            print(f"  Display Name: {info['display_name'] or 'N/A'}")
            print(f"  Bio: {info['bio'] or 'N/A'}")
            print(f"  Followers: {info['follower_count'] or 'N/A'}")
            print(f"  Following: {info['following_count'] or 'N/A'}")
            print(f"  Likes: {info['like_count'] or 'N/A'}")
            print(f"  Verified: {info['is_verified']}")

            self.findings.append({
                "platform": "tiktok",
                "type": "public_info",
                "value": clean_username,
                "details": info,
            })

        return info

    def run_full_audit(self, target):
        """
        Run a complete TikTok account security audit.
        
        Args:
            target: Username to audit
            
        Returns:
            list: All findings
        """
        print(Colors.BOLD + Colors.C + "\n[ TikTok Security Audit ]" + Colors.N)
        print("=" * 50)

        self.check_username_exists(target)
        self.extract_public_info(target)

        return self.findings
