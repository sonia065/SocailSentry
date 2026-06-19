"""
Web scraping module for social media public page analysis.
For authorized pentesting only.
"""

import re
from urllib.parse import urlparse
from ..core.utils import make_request
from ..core.colors import Colors


class WebScraper:
    """
    Scrapes publicly available information from social media pages
    for security assessment purposes.
    """

    def __init__(self, config):
        self.config = config

    def scrape_profile_page(self, url):
        """
        Scrape a social media profile page for public data.
        
        Args:
            url: Full profile URL
            
        Returns:
            dict: Scraped data
        """
        print(Colors.status_info(f"Scraping: {url}"))
        response = make_request(url, timeout=self.config.get("timeout"))

        data = {
            "url": url,
            "status_code": None,
            "page_title": None,
            "meta_description": None,
            "social_links": [],
            "external_links": [],
            "has_redirect": False,
            "redirect_url": None,
        }

        if response is None:
            return data

        data["status_code"] = response.status_code

        # Check redirects
        if response.history:
            data["has_redirect"] = True
            data["redirect_url"] = response.url

        # Extract title
        title_match = re.search(r'<title>([^<]*)</title>', response.text)
        if title_match:
            data["page_title"] = title_match.group(1).strip()

        # Extract meta description
        desc_match = re.search(
            r'<meta\s+name="description"\s+content="([^"]*)"', response.text
        )
        if desc_match:
            data["meta_description"] = desc_match.group(1)

        # Extract links
        hrefs = re.findall(r'href="(https?://[^"]*)"', response.text)
        domain = urlparse(url).netloc

        for link in hrefs:
            link_domain = urlparse(link).netloc
            if link_domain != domain:
                data["external_links"].append(link)
            else:
                # Social links within same domain
                if any(p in link for p in ["/about", "/contact", "/privacy", "/security"]):
                    data["social_links"].append(link)

        # Remove duplicates
        data["social_links"] = list(set(data["social_links"]))[:20]
        data["external_links"] = list(set(data["external_links"]))[:20]

        # Summary
        print(Colors.status_ok(f"Page loaded (HTTP {response.status_code})"))
        if data["page_title"]:
            print(Colors.status_info(f"Title: {data['page_title'][:80]}"))
        print(Colors.status_info(f"Social links found: {len(data['social_links'])}"))
        print(Colors.status_info(f"External links found: {len(data['external_links'])}"))

        return data

    def analyze_security_headers(self, url):
        """
        Analyze HTTP security headers of a social media page.
        
        Args:
            url: Target URL
            
        Returns:
            dict: Security header analysis
        """
        response = make_request(url, timeout=self.config.get("timeout"))
        
        headers_analysis = {
            "url": url,
            "headers": {},
            "missing_headers": [],
            "present_headers": [],
        }

        if response is None:
            return headers_analysis

        # Important security headers
        security_headers = {
            "Strict-Transport-Security": "HSTS - Protects against SSL stripping",
            "Content-Security-Policy": "CSP - Prevents XSS attacks",
            "X-Content-Type-Options": "Prevents MIME type sniffing",
            "X-Frame-Options": "Prevents clickjacking",
            "X-XSS-Protection": "Cross-site scripting filter",
            "Referrer-Policy": "Controls referrer information leakage",
            "Permissions-Policy": "Controls browser API access",
            "Set-Cookie": "Cookie security flags (HttpOnly, Secure, SameSite)",
        }

        # Analyze cookies if present
        if "Set-Cookie" in response.headers:
            cookie_header = response.headers["Set-Cookie"]
            cookie_analysis = {
                "has_httponly": "httponly" in cookie_header.lower(),
                "has_secure": "secure" in cookie_header.lower(),
                "has_samesite": "samesite" in cookie_header.lower(),
            }
            headers_analysis["cookie_analysis"] = cookie_analysis

        # Check each security header
        for header, description in security_headers.items():
            if header in response.headers:
                headers_analysis["present_headers"].append({
                    "header": header,
                    "value": response.headers[header][:100],
                    "purpose": description,
                })
            else:
                headers_analysis["missing_headers"].append({
                    "header": header,
                    "purpose": description,
                })

        # Store all response headers
        headers_analysis["headers"] = dict(response.headers)

        return headers_analysis
