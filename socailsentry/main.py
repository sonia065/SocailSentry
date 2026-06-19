#!/usr/bin/env python3
"""
SocialSentry - Authorized Social Media Security Assessment Toolkit
Main entry point with CLI interface.

Usage:
    python socialsentry/main.py username <username>
    python socialsentry/main.py email <email>
    python socialsentry/main.py audit <platform> --target <target>
    python socialsentry/main.py check-password <password>
    python socialsentry/main.py report
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.colors import Colors, BANNER
from core.config import Config
from core.reporter import ReportGenerator
from recon.username_checker import UsernameChecker
from recon.email_checker import EmailChecker
from recon.phone_checker import PhoneChecker
from auth.password_checker import PasswordChecker
from platforms import (
    YouTubeScanner,
    TikTokScanner,
    InstagramScanner,
    FacebookScanner,
    WhatsAppScanner,
)


def setup_argparse():
    """Setup command line argument parser."""
    parser = argparse.ArgumentParser(
        description="SocialSentry - Authorized Social Media Security Assessment Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python socialsentry/main.py username johndoe
  python socialsentry/main.py email user@example.com
  python socialsentry/main.py phone +1234567890
  python socialsentry/main.py audit instagram --target username
  python socialsentry/main.py check-password "MyP@ssw0rd"
  python socialsentry/main.py report --format html
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Username command
    username_parser = subparsers.add_parser("username", help="Check username across platforms")
    username_parser.add_argument("username", help="Username to search for")
    username_parser.add_argument(
        "--platforms", nargs="+",
        choices=["facebook", "instagram", "youtube", "tiktok", "all"],
        default=["all"],
        help="Platforms to check (default: all)"
    )

    # Email command
    email_parser = subparsers.add_parser("email", help="Check email registration across platforms")
    email_parser.add_argument("email", help="Email address to check")

    # Phone command
    phone_parser = subparsers.add_parser("phone", help="Check phone number across platforms")
    phone_parser.add_argument("phone", help="Phone number with country code")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Run full audit on a platform")
    audit_parser.add_argument(
        "platform",
        choices=["facebook", "instagram", "youtube", "tiktok", "whatsapp"],
        help="Platform to audit"
    )
    audit_parser.add_argument("--target", required=True, help="Target username/email/phone")
    audit_parser.add_argument("--output", choices=["html", "json", "both"], default="html",
                            help="Report output format")

    # Password check command
    password_parser = subparsers.add_parser("check-password", help="Check password strength and breaches")
    password_parser.add_argument("password", help="Password to analyze")

    # Report command
    report_parser = subparsers.add_parser("report", help="View or generate reports")
    report_parser.add_argument("--format", choices=["html", "json"], default="html",
                             help="Report format (default: html)")
    report_parser.add_argument("--filename", help="Custom report filename")

    return parser


def handle_username(args, config):
    """Handle username reconnaissance command."""
    print(Colors.BOLD + Colors.M + f"\n  Username Reconnaissance: {args.username}" + Colors.N)
    print("=" * 60)

    checker = UsernameChecker(config)
    
    platforms = args.platforms
    if "all" in platforms:
        platforms = None  # Will check all platforms
    
    results = checker.check_all(args.username, platforms)
    
    # Generate report
    reporter = ReportGenerator()
    reporter.set_target("username", args.username)
    for platform, found in results.items():
        severity = "info" if found else "low"
        reporter.add_finding(
            platform=platform,
            check_name="username_existence",
            severity=severity,
            description=f"Username '{args.username}' {'found' if found else 'not found'} on {platform}",
            detail=f"Platform: {platform}, Status: {'Found' if found else 'Not Found'}"
        )
    
    reporter.generate_html()
    return results


def handle_email(args, config):
    """Handle email reconnaissance command."""
    print(Colors.BOLD + Colors.M + f"\n  Email Reconnaissance: {args.email}" + Colors.N)
    print("=" * 60)

    checker = EmailChecker(config)
    results = checker.check_all(args.email)
    
    # Generate report
    reporter = ReportGenerator()
    reporter.set_target("email", args.email)
    reporter.generate_html()
    
    return results


def handle_phone(args, config):
    """Handle phone number check command."""
    print(Colors.BOLD + Colors.M + f"\n  Phone Check: {args.phone}" + Colors.N)
    print("=" * 60)

    checker = PhoneChecker(config)
    results = checker.check_all(args.phone)
    
    reporter = ReportGenerator()
    reporter.set_target("phone", args.phone)
    reporter.generate_html()
    
    return results


def handle_audit(args, config):
    """Handle platform audit command."""
    scanner_map = {
        "facebook": FacebookScanner,
        "instagram": InstagramScanner,
        "youtube": YouTubeScanner,
        "tiktok": TikTokScanner,
        "whatsapp": WhatsAppScanner,
    }

    if args.platform not in scanner_map:
        print(Colors.status_fail(f"Unknown platform: {args.platform}"))
        return

    scanner = scanner_map[args.platform](config)
    findings = scanner.run_full_audit(args.target)
    
    # Generate report
    reporter = ReportGenerator()
    reporter.set_target(f"{args.platform}_account", args.target)
    for finding in findings:
        reporter.add_finding(
            platform=finding.get("platform", args.platform),
            check_name=finding.get("type", "general_check"),
            severity=finding.get("severity", "info"),
            description=str(finding.get("description", finding.get("note", "Audit finding"))),
            detail=str(finding)
        )
    
    reporter.generate_html()
    if args.output in ["json", "both"]:
        reporter.generate_json()
    
    return findings


def handle_password(args, config):
    """Handle password check command."""
    checker = PasswordChecker(config)
    results = checker.full_check(args.password)
    
    reporter = ReportGenerator()
    reporter.set_target("password", "***hidden***")
    reporter.add_finding(
        platform="general",
        check_name="password_strength",
        severity="high" if results["strength"]["score"] < 4 else "medium" if results["strength"]["score"] < 7 else "info",
        description=f"Password strength: {results['strength']['strength']}",
        detail=f"Score: {results['strength']['score']}/8 | Breached: {results['breach_check'].get('exposed', False)}"
    )
    reporter.generate_html()
    
    return results


def handle_report(args, config):
    """Handle report generation command."""
    reporter = ReportGenerator()
    
    if args.format == "html":
        reporter.generate_html(args.filename)
    else:
        reporter.generate_json(args.filename)


def main():
    """Main entry point."""
    print(BANNER)
    
    config = Config()
    parser = setup_argparse()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        print(f"\n{Colors.Y}[!]{Colors.N} Use 'python socialsentry/main.py <command> --help' for help with a specific command.")
        print(f"\n{Colors.G}Quick Start:{Colors.N}")
        print(f"  python socialsentry/main.py username johndoe")
        print(f"  python socialsentry/main.py email user@example.com")
        print(f"  python socialsentry/main.py audit instagram --target username")
        print(f"  python socialsentry/main.py check-password \"MyP@ssw0rd\"")
        return

    # Command routing
    command_map = {
        "username": handle_username,
        "email": handle_email,
        "phone": handle_phone,
        "audit": handle_audit,
        "check-password": handle_password,
        "report": handle_report,
    }

    handler = command_map.get(args.command)
    if handler:
        handler(args, config)
    else:
        print(Colors.status_fail(f"Unknown command: {args.command}"))


if __name__ == "__main__":
    main()
