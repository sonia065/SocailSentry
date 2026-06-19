"""
Test cases for core modules.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from socialsentry.core.config import Config
from socialsentry.core.colors import Colors, BANNER
from socialsentry.core.reporter import ReportGenerator
from socialsentry.core.utils import (
    validate_username, validate_email, validate_phone,
    sanitize_output, make_request
)


class TestCoreColors(unittest.TestCase):
    """Test colors module."""

    def test_status_ok(self):
        """Test status_ok returns colored OK message."""
        msg = "Test OK"
        result = Colors.status_ok(msg)
        self.assertIn(msg, result)
        self.assertIn("✓", result)

    def test_status_fail(self):
        """Test status_fail returns colored FAIL message."""
        msg = "Test Fail"
        result = Colors.status_fail(msg)
        self.assertIn(msg, result)
        self.assertIn("✗", result)

    def test_status_warn(self):
        """Test status_warn returns colored WARN message."""
        msg = "Test Warn"
        result = Colors.status_warn(msg)
        self.assertIn(msg, result)
        self.assertIn("!", result)

    def test_status_info(self):
        """Test status_info returns colored INFO message."""
        msg = "Test Info"
        result = Colors.status_info(msg)
        self.assertIn(msg, result)
        self.assertIn("i", result)

    def test_banner_exists(self):
        """Test banner string exists."""
        self.assertIsNotNone(BANNER)
        self.assertIn("SocialSentry", BANNER)


class TestCoreConfig(unittest.TestCase):
    """Test config module."""

    def setUp(self):
        self.config = Config()

    def test_default_settings(self):
        """Test default settings exist."""
        self.assertEqual(self.config.get("timeout"), 15)
        self.assertEqual(self.config.get("max_threads"), 10)
        self.assertIsNotNone(self.config.get("user_agent"))

    def test_set_and_get(self):
        """Test setting and getting config values."""
        self.config.set("test_key", "test_value")
        self.assertEqual(self.config.get("test_key"), "test_value")

    def test_get_default(self):
        """Test get returns default for missing key."""
        result = self.config.get("nonexistent_key", "default")
        self.assertEqual(result, "default")

    def test_endpoints_loaded(self):
        """Test endpoints are loaded."""
        self.assertIn("facebook", self.config.endpoints)
        self.assertIn("instagram", self.config.endpoints)
        self.assertIn("youtube", self.config.endpoints)
        self.assertIn("tiktok", self.config.endpoints)
        self.assertIn("whatsapp", self.config.endpoints)

    def test_facebook_endpoint(self):
        """Test Facebook endpoint config."""
        fb = self.config.endpoints["facebook"]
        self.assertEqual(fb["base_url"], "https://www.facebook.com")


class TestCoreReporter(unittest.TestCase):
    """Test reporter module."""

    def setUp(self):
        self.reporter = ReportGenerator()

    def test_set_target(self):
        """Test setting target."""
        self.reporter.set_target("username", "johndoe")
        self.assertEqual(self.reporter.data["target"]["type"], "username")
        self.assertEqual(self.reporter.data["target"]["value"], "johndoe")

    def test_add_finding(self):
        """Test adding a finding."""
        self.reporter.add_finding(
            platform="facebook",
            check_name="test_check",
            severity="high",
            description="Test finding"
        )
        self.assertEqual(len(self.reporter.data["findings"]), 1)
        self.assertEqual(self.reporter.data["summary"]["total_checks"], 1)
        self.assertEqual(self.reporter.data["summary"]["high"], 1)

    def test_add_multiple_findings(self):
        """Test adding multiple findings with different severities."""
        self.reporter.add_finding("fb", "check1", "critical", "Critical issue")
        self.reporter.add_finding("ig", "check2", "medium", "Medium issue")
        self.reporter.add_finding("yt", "check3", "low", "Low issue")
        self.reporter.add_finding("tt", "check4", "info", "Info note")

        self.assertEqual(len(self.reporter.data["findings"]), 4)
        self.assertEqual(self.reporter.data["summary"]["critical"], 1)
        self.assertEqual(self.reporter.data["summary"]["medium"], 1)
        self.assertEqual(self.reporter.data["summary"]["low"], 1)
        self.assertEqual(self.reporter.data["summary"]["info"], 1)

    def test_generate_html(self):
        """Test HTML report generation."""
        self.reporter.set_target("username", "testuser")
        self.reporter.add_finding("test", "check", "info", "Test")
        
        report_path = self.reporter.generate_html("test_report.html")
        self.assertTrue(os.path.exists(report_path))
        self.assertIn("test_report.html", str(report_path))

        # Cleanup
        os.remove(report_path)

    def test_generate_json(self):
        """Test JSON report generation."""
        self.reporter.set_target("username", "testuser")
        self.reporter.add_finding("test", "check", "info", "Test")
        
        report_path = self.reporter.generate_json("test_report.json")
        self.assertTrue(os.path.exists(report_path))

        # Cleanup
        os.remove(report_path)

    def test_summary_counts_match_findings(self):
        """Test summary counts match actual findings."""
        self.reporter.add_finding("a", "c1", "critical", "desc")
        self.reporter.add_finding("b", "c2", "high", "desc")
        self.reporter.add_finding("c", "c3", "medium", "desc")
        self.reporter.add_finding("d", "c4", "low", "desc")
        self.reporter.add_finding("e", "c5", "info", "desc")

        total = sum([
            self.reporter.data["summary"]["critical"],
            self.reporter.data["summary"]["high"],
            self.reporter.data["summary"]["medium"],
            self.reporter.data["summary"]["low"],
            self.reporter.data["summary"]["info"],
        ])
        self.assertEqual(total, 5)


class TestCoreUtils(unittest.TestCase):
    """Test utility functions."""

    # ─── validate_username tests ───

    def test_validate_username_valid(self):
        """Test valid usernames."""
        valid = ["johndoe", "john_doe", "john.doe", "john-doe", "user123", "a_b.c-d"]
        for username in valid:
            self.assertTrue(validate_username(username), f"'{username}' should be valid")

    def test_validate_username_invalid(self):
        """Test invalid usernames."""
        invalid = ["", "a", "ab", "@user", "user name", "user!name", "user#123",
                   "a" * 31, "user@name", "user$name"]
        for username in invalid:
            self.assertFalse(validate_username(username), f"'{username}' should be invalid")

    def test_validate_username_length_boundary(self):
        """Test boundary conditions for length."""
        # Minimum valid (2 chars)
        self.assertTrue(validate_username("jo"))
        # Maximum valid (30 chars)
        self.assertTrue(validate_username("a" * 30))
        # Over max (31 chars)
        self.assertFalse(validate_username("a" * 31))

    # ─── validate_email tests ───

    def test_validate_email_valid(self):
        """Test valid emails."""
        valid = [
            "user@example.com",
            "user.name@example.com",
            "user+tag@example.com",
            "user_name@example.co.uk",
            "user@sub.example.com",
            "123@example.com",
            "a@b.com",
        ]
        for email in valid:
            self.assertTrue(validate_email(email), f"'{email}' should be valid")

    def test_validate_email_invalid(self):
        """Test invalid emails."""
        invalid = [
            "",
            "user",
            "user@",
            "@example.com",
            "user@.com",
            "user@example",
            "user@example.",
            "user name@example.com",
            "user@exam ple.com",
        ]
        for email in invalid:
            self.assertFalse(validate_email(email), f"'{email}' should be invalid")

    # ─── validate_phone tests ───

    def test_validate_phone_valid(self):
        """Test valid phone numbers."""
        valid = ["1234567", "1234567890", "009234567890", "123456789012"]
        for phone in valid:
            self.assertTrue(validate_phone(phone), f"'{phone}' should be valid")

    def test_validate_phone_invalid(self):
        """Test invalid phone numbers."""
        invalid = ["", "123", "abcdefg", "12-34", "phone"]
        for phone in invalid:
            self.assertFalse(validate_phone(phone), f"'{phone}' should be invalid")

    def test_validate_phone_cleaned(self):
        """Test phone with formatting symbols is valid."""
        self.assertTrue(validate_phone("+1 (234) 567-890"))
        self.assertTrue(validate_phone("0092-345-678901"))

    # ─── sanitize_output tests ───

    def test_sanitize_output_removes_control_chars(self):
        """Test control characters are removed."""
        dirty = "Hello\x00World\x1fTest"
        clean = sanitize_output(dirty)
        self.assertEqual(clean, "HelloWorldTest")

    def test_sanitize_output_keeps_normal_text(self):
        """Test normal text remains unchanged."""
        text = "Hello, World! Test 123."
        self.assertEqual(sanitize_output(text), text)

    def test_sanitize_output_strips_whitespace(self):
        """Test whitespace is stripped."""
        self.assertEqual(sanitize_output("  hello  "), "hello")

    def test_sanitize_output_empty(self):
        """Test empty string returns empty."""
        self.assertEqual(sanitize_output(""), "")

    def test_sanitize_output_none(self):
        """Test None returns empty."""
        self.assertEqual(sanitize_output(None), "")

    # ─── make_request tests ───

    @patch('socialsentry.core.utils.requests.get')
    def test_make_request_success(self, mock_get):
        """Test successful request returns response."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = make_request("https://example.com")
        self.assertIsNotNone(result)
        self.assertEqual(result.status_code, 200)

    @patch('socialsentry.core.utils.requests.get')
    def test_make_request_timeout(self, mock_get):
        """Test timeout returns None."""
        mock_get.side_effect = TimeoutError()

        result = make_request("https://example.com")
        self.assertIsNone(result)

    @patch('socialsentry.core.utils.requests.get')
    def test_make_request_connection_error(self, mock_get):
        """Test connection error returns None."""
        mock_get.side_effect = ConnectionError()

        result = make_request("https://example.com")
        self.assertIsNone(result)

    @patch('socialsentry.core.utils.requests.get')
    def test_make_request_custom_headers(self, mock_get):
        """Test custom headers are passed correctly."""
        mock_response = MagicMock()
        mock_get.return_value = mock_response

        custom_headers = {"X-Test": "test-value"}
        make_request("https://example.com", headers=custom_headers)

        # Check that custom headers were passed
        call_kwargs = mock_get.call_args[1]
        self.assertIn("headers", call_kwargs)
        self.assertEqual(call_kwargs["headers"]["X-Test"], "test-value")

    @patch('socialsentry.core.utils.requests.get')
    def test_make_request_with_timeout(self, mock_get):
        """Test timeout parameter is passed."""
        mock_response = MagicMock()
        mock_get.return_value = mock_response

        make_request("https://example.com", timeout=30)

        call_kwargs = mock_get.call_args[1]
        self.assertEqual(call_kwargs["timeout"], 30)


class TestConfigEndpoints(unittest.TestCase):
    """Test endpoint configurations."""

    def setUp(self):
        self.config = Config()

    def test_all_platforms_have_base_url(self):
        """Test all platforms have base_url."""
        for platform, data in self.config.endpoints.items():
            self.assertIn("base_url", data, f"{platform} missing base_url")

    def test_facebook_endpoints(self):
        """Test Facebook endpoints."""
        fb = self.config.endpoints["facebook"]
        self.assertTrue(fb["base_url"].startswith("https://"))
        self.assertIn("username_check", fb)
        self.assertIn("recovery_check", fb)

    def test_instagram_endpoints(self):
        """Test Instagram endpoints."""
        ig = self.config.endpoints["instagram"]
        self.assertIn("{username}", ig.get("username_check", ""))

    def test_youtube_endpoints(self):
        """Test YouTube endpoints."""
        yt = self.config.endpoints["youtube"]
        self.assertIn("@", yt.get("username_check", ""))

    def test_tiktok_endpoints(self):
        """Test TikTok endpoints."""
        tt = self.config.endpoints["tiktok"]
        self.assertIn("@", tt.get("username_check", ""))

    def test_whatsapp_endpoints(self):
        """Test WhatsApp endpoints."""
        wa = self.config.endpoints["whatsapp"]
        self.assertIn("{phone}", wa.get("phone_check", ""))


if __name__ == "__main__":
    unittest.main()
