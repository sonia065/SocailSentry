"""
Metadata extraction module.
Extracts and analyzes public metadata from social media profiles.
"""

import re
from ..core.utils import make_request
from ..core.colors import Colors


class MetadataExtractor:
    """
    Extracts publicly available metadata from social media profiles
    for security assessment purposes.
    """

    def __init__(self, config):
        self.config = config

    def extract_meta_tags(self, url):
        """
        Extract HTML meta tags and OpenGraph data from a URL.
        
        Args:
            url: Target profile URL
            
        Returns:
            dict: Extracted metadata
        """
        response = make_request(url, timeout=self.config.get("timeout"))
        metadata = {
            "url": url,
            "title": None,
            "description": None,
            "image": None,
            "site_name": None,
            "meta_tags": {},
        }

        if response and response.status_code == 200:
            content = response.text

            # OpenGraph tags
            og_patterns = {
                "title": r'<meta\s+property="og:title"\s+content="([^"]*)"',
                "description": r'<meta\s+property="og:description"\s+content="([^"]*)"',
                "image": r'<meta\s+property="og:image"\s+content="([^"]*)"',
                "site_name": r'<meta\s+property="og:site_name"\s+content="([^"]*)"',
                "url": r'<meta\s+property="og:url"\s+content="([^"]*)"',
            }

            for key, pattern in og_patterns.items():
                match = re.search(pattern, content)
                if match:
                    metadata[key] = match.group(1)

            # Twitter card tags
            twitter_patterns = {
                "twitter_title": r'<meta\s+name="twitter:title"\s+content="([^"]*)"',
                "twitter_desc": r'<meta\s+name="twitter:description"\s+content="([^"]*)"',
                "twitter_image": r'<meta\s+name="twitter:image"\s+content="([^"]*)"',
            }

            for key, pattern in twitter_patterns.items():
                match = re.search(pattern, content)
                if match:
                    metadata[key] = match.group(1)

            # All meta tags
            all_meta = re.findall(r'<meta\s+([^>]*)>', content)
            for meta in all_meta:
                name_match = re.search(r'name="([^"]*)"', meta)
                content_match = re.search(r'content="([^"]*)"', meta)
                if name_match and content_match:
                    metadata["meta_tags"][name_match.group(1)] = content_match.group(1)

            # Title tag
            title_match = re.search(r'<title>([^<]*)</title>', content)
            if title_match:
                metadata["title"] = metadata.get("title") or title_match.group(1)

        return metadata

    def extract_links(self, url):
        """
        Extract all links from a social media page.
        
        Args:
            url: Target URL
            
        Returns:
            list: Extracted links
        """
        response = make_request(url, timeout=self.config.get("timeout"))
        links = []

        if response and response.status_code == 200:
            hrefs = re.findall(r'href="([^"]*)"', response.text)
            unique_links = set()

            for href in hrefs:
                if href.startswith("http") or href.startswith("/"):
                    if href.startswith("/"):
                        from urllib.parse import urlparse
                        parsed = urlparse(url)
                        href = f"{parsed.scheme}://{parsed.netloc}{href}"

                    if href not in unique_links:
                        unique_links.add(href)
                        links.append(href)

        return links[:50]  # Limit to 50 links
