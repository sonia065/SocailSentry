"""
Terminal color codes and banners for SocialSentry.
"""

import sys
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform support
init(autoreset=True)


class Colors:
    """ANSI color codes for terminal output."""
    R = Fore.RED
    G = Fore.GREEN
    Y = Fore.YELLOW
    B = Fore.BLUE
    M = Fore.MAGENTA
    C = Fore.CYAN
    W = Fore.WHITE
    N = Style.RESET_ALL
    BOLD = Style.BRIGHT

    @staticmethod
    def status_ok(msg):
        return f"{Colors.G}[✓]{Colors.N} {msg}"

    @staticmethod
    def status_fail(msg):
        return f"{Colors.R}[✗]{Colors.N} {msg}"

    @staticmethod
    def status_warn(msg):
        return f"{Colors.Y}[!]{Colors.N} {msg}"

    @staticmethod
    def status_info(msg):
        return f"{Colors.C}[i]{Colors.N} {msg}"


BANNER = f"""
{Colors.M}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                    SocialSentry v1.0.0                           ║
║         Authorized Social Media Security Assessment              ║
║          YouTube · TikTok · Instagram · Facebook · WhatsApp      ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.N}
{Colors.Y}[!]{Colors.N} For authorized security testing ONLY.
{Colors.Y}[!]{Colors.N} You must have explicit permission to test target accounts.
{Colors.N}
"""
