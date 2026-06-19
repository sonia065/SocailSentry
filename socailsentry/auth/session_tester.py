"""
Session security testing module.
Analyzes session configurations and security settings.
"""

import re
from ..core.utils import make_request
from ..core.colors import Colors


class SessionTester:
    """
    Tests session security configurations for social media platforms.
    """

    def __init__(self, config):
        self.config = config

    def analyze_cookies(self, url):
        """
        Analyze cookie security settings from HTTP response.
        
        Args:
            url: Target URL
            
        Returns:
            dict: Cookie security analysis
        """
        response = make_request(url, timeout=self.config.get("timeout"))
        
        cookie_analysis = {
            "url": url,
            "total_cookies": 0,
            "secure_cookies": 0,
            "httponly_cookies": 0,
            "samesite_cookies": 0,
            "insecure_cookies": [],
            "recommendations": [],
        }

        if response is None or "Set-Cookie" not in response.headers:
            cookie_analysis["note"] = "No cookies set by this endpoint"
            return cookie_analysis

        # Parse multiple Set-Cookie headers
        cookie_headers = response.headers.get_all("Set-Cookie") if hasattr(
            response.headers, "get_all"
        ) else [response.headers.get("Set-Cookie")]

        for cookie_str in cookie_headers:
            if not cookie_str:
                continue

            cookie_analysis["total_cookies"] += 1
            cookie_info = {
                "raw": cookie_str[:100],
                "has_secure": "secure" in cookie_str.lower().split(";"),
                "has_httponly": "httponly" in cookie_str.lower().split(";"),
                "has_samesite": "samesite" in cookie_str.lower(),
            }

            # Extract cookie name
            name_match = re.match(r'^([^=]+)=', cookie_str)
            if name_match:
                cookie_info["name"] = name_match.group(1)

            if cookie_info["has_secure"]:
                cookie_analysis["secure_cookies"] += 1
            else:
                cookie_analysis["insecure_cookies"].append(cookie_info)
                cookie_analysis["recommendations"].append(
                    f"Cookie '{cookie_info.get('name', 'unknown')}' missing 'Secure' flag"
                )

            if cookie_info["has_httponly"]:
                cookie_analysis["httponly_cookies"] += 1
            else:
                if cookie_info.get("name") and cookie_info["name"] not in ["lang", "locale"]:
                    cookie_analysis["recommendations"].append(
                        f"Cookie '{cookie_info['name']}' missing 'HttpOnly' flag"
                    )

            if cookie_info["has_samesite"]:
                cookie_analysis["samesite_cookies"] += 1

        # Generate summary
        print(f"\n{Colors.BOLD}{Colors.B}[ Cookie Security Analysis ]{Colors.N}")
        print(f"{'='*50}")
        print(f"  Total Cookies: {cookie_analysis['total_cookies']}")
        print(f"  Secure Flag:   {cookie_analysis['secure_cookies']}/{cookie_analysis['total_cookies']}")
        print(f"  HttpOnly Flag: {cookie_analysis['httponly_cookies']}/{cookie_analysis['total_cookies']}")
        print(f"  SameSite Flag: {cookie_analysis['samesite_cookies']}/{cookie_analysis['total_cookies']}")

        if cookie_analysis["recommendations"]:
            print(f"\n  {Colors.Y}Recommendations:{Colors.N}")
            for rec in cookie_analysis["recommendations"]:
                print(f"    → {rec}")

        return cookie_analysis

    def test_login_endpoint_security(self, login_url):
        """
        Test basic security of a login endpoint.
        
        Args:
            login_url: Login page URL
            
        Returns:
            dict: Security analysis
        """
        print(f"\n{Colors.BOLD}{Colors.B}[ Login Endpoint Security Check ]{Colors.N}")
        print(f"{'='*50}")
        print(f"  Testing: {login_url}")

        response = make_request(login_url, timeout=self.config.get("timeout"))
        
        security_check = {
            "url": login_url,
            "uses_https": login_url.startswith("https://"),
            "has_form": False,
            "form_action_secure": None,
            "notes": [],
        }

        if response is None:
            security_check["notes"].append("Could not access login page")
            return security_check

        # Check HTTPS
        if not security_check["uses_https"]:
            security_check["notes"].append("❌ Login page not using HTTPS!")

        # Check for login form
        form_match = re.search(
            r'<form[^>]*action=["\']([^"\']*)["\']',
            response.text,
            re.IGNORECASE
        )
        if form_match:
            security_check["has_form"] = True
            form_action = form_match.group(1)
            security_check["form_action_secure"] = form_action.startswith("https://") if form_action.startswith("http") else True
            
            if not security_check["form_action_secure"]:
                security_check["notes"].append("❌ Form action does not use HTTPS!")

        # Check for password input
        if re.search(r'<input[^>]*type=["\']password["\']', response.text, re.IGNORECASE):
            security_check["has_password_field"] = True

        # Print results
        print(f"  HTTPS: {'✅' if security_check['uses_https'] else '❌'}")
        print(f"  Login Form: {'✅ Found' if security_check.get('has_form') else '❌ Not found'}")
        if security_check.get("form_action_secure") is not None:
            print(f"  Form Action Secure: {'✅' if security_check['form_action_secure'] else '❌'}")
        if security_check.get("has_password_field"):
            print(f"  Password Field: ✅ Present")

        for note in security_check["notes"]:
            print(f"  {Colors.Y}{note}{Colors.N}")

        return security_check
