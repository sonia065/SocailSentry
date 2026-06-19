"""
Instagram security assessment module.
For authorized pentesting only.
"""

import re
import json
from ..core.utils import make_request, validate_username
from ..core.colors import Colors


class InstagramScanner:
    """Instagram account security assessment scanner."""

    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.instagram.com"
        self.findings = []

    def check_username_exists(self, username):
        """
        Check if an Instagram username exists.
        
        Args:
            username: Instagram username
            
        Returns:
            bool: Whether the profile exists
        """
        if not validate_username(username):
            print(Colors.status_fail("Invalid username format"))
            return False

        url = f"{self.base_url}/{username}/"
        print(Colors.status_info(f"Checking Instagram: {url}"))

        response = make_request(url, timeout=self.config.get("timeout"))
        if response is None:
            return False

        if response.status_code == 200:
            # Instagram embeds profile data in the page source
            if "window.__INITIAL_STATE__" in response.text:
                # Extract JSON data
                match = re.search(
                    r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                    response.text,
                    re.DOTALL
                )
                if match:
                    try:
                        data = json.loads(match.group(1))
                        user_data = data.get("user", {})
                        if user_data:
                            print(Colors.status_ok(f"Instagram profile found: {url}"))
                            self.findings.append({
                                "platform": "instagram",
                                "type": "username_existence",
                                "value": username,
                                "url": url,
                                "status": "found",
                            })
                            return True
                    except json.JSONDecodeError:
                        pass

            # Fallback check
            if f'"username":"{username.lower()}"' in response.text.lower():
                print(Colors.status_ok(f"Instagram profile found: {url}"))
                self.findings.append({
                    "platform": "instagram",
                    "type": "username_existence",
                    "value": username,
                    "url": url,
                    "status": "found",
                })
                return True

        if response.status_code == 404:
            print(Colors.status_fail(f"Instagram profile not found: {username}"))
            return False

        print(Colors.status_warn(f"Instagram check ambiguous for: {username} (HTTP {response.status_code})"))
        return False

    def extract_public_info(self, username):
        """
        Extract publicly available information from an Instagram profile.
        
        Args:
            username: Target username
            
        Returns:
            dict: Extracted public information
        """
        url = f"{self.base_url}/{username}/"
        response = make_request(url)

        info = {
            "username": username,
            "url": url,
            "exists": False,
            "full_name": None,
            "biography": None,
            "is_private": None,
            "follower_count": None,
            "following_count": None,
            "post_count": None,
            "is_verified": None,
        }

        if response and response.status_code == 200:
            info["exists"] = True

            # Try to extract from __INITIAL_STATE__
            match = re.search(
                r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                response.text,
                re.DOTALL
            )
            if match:
                try:
                    data = json.loads(match.group(1))
                    user = data.get("user", {})
                    info["full_name"] = user.get("full_name")
                    info["biography"] = user.get("biography")
                    info["is_private"] = user.get("is_private", False)
                    info["is_verified"] = user.get("is_verified", False)

                    # Edge count
                    edge = user.get("edge_followed_by", {})
                    info["follower_count"] = edge.get("count")

                    edge2 = user.get("edge_follow", {})
                    info["following_count"] = edge2.get("count")

                    edge3 = user.get("edge_owner_to_timeline_media", {})
                    info["post_count"] = edge3.get("count")

                except (json.JSONDecodeError, AttributeError):
                    pass

            # Fallback: try meta tags
            if not info["full_name"]:
                name_match = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', response.text)
                if name_match:
                    info["full_name"] = name_match.group(1)

            # Print results
            print(Colors.BOLD + Colors.C + f"\n[ Instagram Profile: {username} ]" + Colors.N)
            print(f"  Full Name: {info['full_name'] or 'N/A'}")
            print(f"  Biography: {info['biography'] or 'N/A'}")
            print(f"  Private: {info['is_private']}")
            print(f"  Verified: {info['is_verified']}")
            print(f"  Followers: {info['follower_count'] or 'N/A'}")
            print(f"  Following: {info['following_count'] or 'N/A'}")
            print(f"  Posts: {info['post_count'] or 'N/A'}")

            self.findings.append({
                "platform": "instagram",
                "type": "public_info",
                "value": username,
                "details": info,
            })

        return info

    def run_full_audit(self, target):
        """
        Run a complete Instagram security audit.
        
        Args:
            target: Username to audit
            
        Returns:
            list: All findings
        """
        print(Colors.BOLD + Colors.M + "\n[ Instagram Security Audit ]" + Colors.N)
        print("=" * 50)

        self.check_username_exists(target)
        self.extract_public_info(target)

        return self.findings
