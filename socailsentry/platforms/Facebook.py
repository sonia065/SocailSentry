"""
Facebook security assessment module.
For authorized pentesting only.
"""

import re
import json
from ..core.utils import make_request, validate_username, validate_email
from ..core.colors import Colors


class FacebookScanner:
    """Facebook account security assessment scanner."""

    def __init__(self, config):
        self.config = config
        self.base_url = "https://www.facebook.com"
        self.findings = []

    def check_username_exists(self, username):
        """
        Check if a Facebook username/profile exists.
        
        Args:
            username: Facebook username or profile ID
            
        Returns:
            bool: Whether the profile exists
        """
        if not validate_username(username):
            print(Colors.status_fail("Invalid username format"))
            return False

        url = f"{self.base_url}/{username}"
        print(Colors.status_info(f"Checking Facebook: {url}"))

        response = make_request(url, timeout=self.config.get("timeout"))
        if response is None:
            return False

        # Check response indicators
        if response.status_code == 200:
            # Profile page indicators
            indicators = [
                "profile_browser",
                "user-content",
                "fb_profile",
                '"name"',
                "timeline",
                "ProfilePage",
            ]
            content = response.text.lower()
            matched = [i for i in indicators if i.lower() in content]

            if matched:
                print(Colors.status_ok(f"Facebook profile found: {url}"))
                self.findings.append({
                    "platform": "facebook",
                    "type": "username_existence",
                    "value": username,
                    "url": url,
                    "status": "found",
                })
                return True

        print(Colors.status_fail(f"Facebook profile not found: {username}"))
        return False

    def check_email_registration(self, email):
        """
        Check if an email is registered on Facebook
        using the forgot password flow.
        
        Args:
            email: Email address to check
            
        Returns:
            dict: Registration status and details
        """
        if not validate_email(email):
            print(Colors.status_fail("Invalid email format"))
            return {"registered": False}

        print(Colors.status_info(f"Checking if email is registered on Facebook: {email}"))

        # Use Facebook's identify endpoint
        identify_url = "https://www.facebook.com/login/identify?ctx=recover"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        session = requests.Session()
        try:
            # Get initial cookies
            session.get(self.base_url, timeout=self.config.get("timeout"))

            # Submit email to recovery flow
            data = {"email": email}
            response = session.post(
                "https://www.facebook.com/recover/initiate",
                data=data,
                headers=headers,
                timeout=self.config.get("timeout"),
                allow_redirects=False,
            )

            # Check response for indicators
            if response.status_code in [302, 200]:
                # Facebook typically redirects to a page asking for
                # more verification if account exists
                print(Colors.status_info(f"Facebook response code: {response.status_code}"))

                result = {
                    "registered": True,
                    "platform": "facebook",
                    "email": email,
                    "note": "Email may be registered. Verify through official recovery flow.",
                }
                self.findings.append(result)
                return result

        except Exception as e:
            print(Colors.status_fail(f"Error checking Facebook email: {str(e)}"))

        return {"registered": False, "platform": "facebook", "email": email}

    def analyze_profile_visibility(self, username):
        """
        Analyze the visibility of a Facebook profile.
        
        Args:
            username: Target username
            
        Returns:
            dict: Visibility analysis
        """
        url = f"{self.base_url}/{username}"
        response = make_request(url)

        visibility = {
            "username": username,
            "url": url,
            "profile_found": False,
            "visible_info": [],
            "restricted": False,
        }

        if response and response.status_code == 200:
            content = response.text
            visibility["profile_found"] = True

            # Check for restricted/private indicators
            restricted_indicators = [
                "content is unavailable",
                "this content isn't available",
                "page isn't available",
                "you must log in",
            ]
            for indicator in restricted_indicators:
                if indicator.lower() in content.lower():
                    visibility["restricted"] = True
                    break

            # Extract public info patterns
            info_patterns = {
                "name": r'<title>([^<]*)</title>',
                "about": r'"about"[^:]*:"([^"]*)"',
            }

            for info_type, pattern in info_patterns.items():
                match = re.search(pattern, content)
                if match:
                    visibility["visible_info"].append({
                        "type": info_type,
                        "value": match.group(1)[:100],
                    })

        return visibility

    def run_full_audit(self, target):
        """
        Run a complete Facebook security audit.
        
        Args:
            target: Username or email to audit
            
        Returns:
            list: All findings
        """
        print(Colors.BOLD + Colors.B + "\n[ Facebook Security Audit ]" + Colors.N)
        print("=" * 50)

        if "@" in target:
            self.check_email_registration(target)
        else:
            self.check_username_exists(target)
            vis = self.analyze_profile_visibility(target)
            if vis.get("visible_info"):
                for info in vis["visible_info"]:
                    print(Colors.status_info(f"Public info - {info['type']}: {info['value']}"))

        return self.findings
