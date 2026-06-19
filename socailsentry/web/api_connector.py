"""
API connector module for interacting with social media platform APIs.
Note: Most platforms require authentication tokens.
"""

import json
import time
from ..core.utils import make_request
from ..core.colors import Colors


class APIConnector:
    """
    Handles API interactions with social media platforms.
    For authorized assessment with valid API credentials only.
    """

    def __init__(self, config):
        self.config = config
        self.rate_limit_delay = config.get("rate_limit_delay", 1.0)

    def test_endpoint(self, base_url, endpoint, method="GET", headers=None, params=None):
        """
        Test a social media API endpoint.
        
        Args:
            base_url: API base URL
            endpoint: API endpoint path
            method: HTTP method
            headers: Request headers
            params: Query parameters
            
        Returns:
            dict: API response analysis
        """
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        print(Colors.status_info(f"Testing API endpoint: {url}"))

        result = {
            "url": url,
            "method": method,
            "status_code": None,
            "response_size": 0,
            "content_type": None,
            "has_rate_limit": False,
            "rate_limit_remaining": None,
        }

        # Add rate limiting delay
        time.sleep(self.rate_limit_delay)

        response = make_request(url, timeout=self.config.get("timeout"), headers=headers)
        
        if response is None:
            return result

        result["status_code"] = response.status_code
        result["response_size"] = len(response.content)
        result["content_type"] = response.headers.get("Content-Type", "")

        # Check for rate limiting
        if response.status_code == 429:
            result["has_rate_limit"] = True
            print(Colors.status_warn("Rate limited!"))

        # Check rate limit headers
        for header in ["X-RateLimit-Remaining", "RateLimit-Remaining", "X-Rate-Limit-Remaining"]:
            if header in response.headers:
                result["rate_limit_remaining"] = response.headers[header]
                break

        # Try to parse JSON response
        try:
            result["json_response"] = response.json()
        except (json.JSONDecodeError, ValueError):
            result["text_preview"] = response.text[:500]

        return result

    def check_public_api_accessibility(self, platform):
        """
        Check public API accessibility for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            dict: API accessibility info
        """
        public_apis = {
            "youtube": {
                "name": "YouTube Data API v3",
                "endpoint": "https://www.googleapis.com/youtube/v3",
                "requires_auth": True,
                "public_endpoints": ["/v3/videos", "/v3/channels", "/v3/search"],
            },
            "facebook": {
                "name": "Facebook Graph API",
                "endpoint": "https://graph.facebook.com/v19.0",
                "requires_auth": True,
                "public_endpoints": ["/me", "/v19.0/user"],
            },
            "instagram": {
                "name": "Instagram Basic Display API",
                "endpoint": "https://graph.instagram.com/v19.0",
                "requires_auth": True,
                "public_endpoints": ["/me", "/refresh_access_token"],
            },
            "tiktok": {
                "name": "TikTok API",
                "endpoint": "https://open-api.tiktok.com",
                "requires_auth": True,
                "public_endpoints": ["/oauth/access_token/", "/user/info/"],
            },
            "whatsapp": {
                "name": "WhatsApp Business API",
                "endpoint": "https://graph.facebook.com/v19.0",
                "requires_auth": True,
                "public_endpoints": ["/v19.0/messages"],
            },
        }

        info = public_apis.get(platform.lower(), {
            "name": "Unknown",
            "endpoint": "N/A",
            "requires_auth": True,
            "note": "No public API documentation found",
        })

        print(Colors.BOLD + Colors.C + f"\n[ API Info: {platform.title()} ]" + Colors.N)
        print(f"  API Name: {info['name']}")
        print(f"  Base URL: {info['endpoint']}")
        print(f"  Requires Auth: {info.get('requires_auth', 'Unknown')}")
        
        if "public_endpoints" in info:
            print(f"  Public Endpoints:")
            for ep in info["public_endpoints"]:
                print(f"    - {ep}")

        return info
