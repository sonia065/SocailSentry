"""
Multi-platform username reconnaissance module.
Checks if a username exists across all supported platforms.
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.colors import Colors
from ..platforms import (
    YouTubeScanner,
    TikTokScanner,
    InstagramScanner,
    FacebookScanner,
)


class UsernameChecker:
    """
    Checks username existence across multiple social media platforms
    simultaneously.
    """

    def __init__(self, config):
        self.config = config
        self.scanners = {
            "facebook": FacebookScanner(config),
            "instagram": InstagramScanner(config),
            "youtube": YouTubeScanner(config),
            "tiktok": TikTokScanner(config),
        }

    def check_all(self, username, platforms=None):
        """
        Check a username across all or specified platforms.
        
        Args:
            username: Username to search for
            platforms: List of platforms to check (None = all)
            
        Returns:
            dict: Results per platform
        """
        if platforms is None:
            platforms = list(self.scanners.keys())

        results = {}
        print(Colors.BOLD + Colors.M + f"\n[ Username Reconnaissance: {username} ]" + Colors.N)
        print("=" * 60)

        max_workers = min(self.config.get("max_threads", 5), len(platforms))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_map = {}

            for platform in platforms:
                if platform in self.scanners:
                    scanner = self.scanners[platform]
                    future = executor.submit(scanner.check_username_exists, username)
                    future_map[future] = platform

            for future in as_completed(future_map):
                platform = future_map[future]
                try:
                    results[platform] = future.result()
                except Exception as e:
                    print(Colors.status_fail(f"{platform}: Error - {str(e)}"))
                    results[platform] = False

        # Summary
        print(Colors.BOLD + Colors.G + "\n[ Results Summary ]" + Colors.N)
        found = [p for p, r in results.items() if r]
        not_found = [p for p, r in results.items() if not r]

        if found:
            print(Colors.status_ok(f"Found on: {', '.join(found)}"))
        if not_found:
            print(Colors.status_fail(f"Not found on: {', '.join(not_found)}"))

        return results
