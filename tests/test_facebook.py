"""
Test cases for Facebook scanner module.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from socialsentry.core.config import Config
from socialsentry.platforms.facebook import FacebookScanner
from socialsentry.core.utils import validate_username, validate_email


class TestFacebookScanner(unittest.TestCase):
    """Test Facebook scanner functionality."""

    @classmethod
    def setUpClass(cls):
        """Setup test resources once."""
        cls.config = Config()
        cls.scanner = FacebookScanner(cls.config)

    def setUp(self):
        """Setup before each test."""
        self.valid_username = "johndoe"
        self.invalid_username = "ab"  # Too short
        self.valid_email = "user@example.com"
        self.invalid_email = "notanemail"

    # ─── Username Validation Tests ───

    def test_validate_username_valid(self):
        """Test valid username passes validation."""
        result = validate_username(self.valid_username)
        self.assertTrue(result, f"Valid username '{self.valid_username}' should pass validation")

    def test_validate_username_too_short(self):
        """Test username too short fails validation."""
        result = validate_username(self.invalid_username)
        self.assertFalse(result, f"Username '{self.invalid_username}' (too short) should fail")

    def test_validate_username_special_chars(self):
        """Test username with invalid special chars fails."""
        result = validate_username("user@name!")
        self.assertFalse(result, "Username with @ and ! should fail")

    def test_validate_username_underscore_allowed(self):
        """Test username with underscore passes."""
        result = validate_username("john_doe")
        self.assertTrue(result, "Username with underscore should pass")

    def test_validate_username_dot_allowed(self):
        """Test username with dot passes."""
        result = validate_username("john.doe")
        self.assertTrue(result, "Username with dot should pass")

    def test_validate_username_hyphen_allowed(self):
        """Test username with hyphen passes."""
        result = validate_username("john-doe")
        self.assertTrue(result, "Username with hyphen should pass")

    def test_validate_username_too_long(self):
        """Test username too long fails."""
        result = validate_username("a" * 31)
        self.assertFalse(result, "Username over 30 chars should fail")

    def test_validate_username_empty(self):
        """Test empty username fails."""
        result = validate_username("")
        self.assertFalse(result, "Empty username should fail")

    # ─── Email Validation Tests ───

    def test_validate_email_valid(self):
        """Test valid email passes validation."""
        result = validate_email(self.valid_email)
        self.assertTrue(result, f"Valid email '{self.valid_email}' should pass")

    def test_validate_email_no_at(self):
        """Test email without @ fails."""
        result = validate_email("userexample.com")
        self.assertFalse(result, "Email without @ should fail")

    def test_validate_email_no_domain(self):
        """Test email without domain fails."""
        result = validate_email("user@.com")
        self.assertFalse(result, "Email without domain should fail")

    def test_validate_email_no_tld(self):
        """Test email without TLD fails."""
        result = validate_email("user@example")
        self.assertFalse(result, "Email without TLD should fail")

    def test_validate_email_subdomain(self):
        """Test email with subdomain passes."""
        result = validate_email("user@sub.example.com")
        self.assertTrue(result, "Email with subdomain should pass")

    def test_validate_email_plus_addressing(self):
        """Test email with plus addressing passes."""
        result = validate_email("user+tag@example.com")
        self.assertTrue(result, "Email with +tag should pass")

    # ─── Username Existence Check Tests ───

    @patch('socialsentry.platforms.facebook.make_request')
    def test_check_username_exists_found(self, mock_request):
        """Test username found returns True."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<title>John Doe</title><script>profile_browser</script>'
        mock_request.return_value = mock_response

        result = self.scanner.check_username_exists(self.valid_username)
        self.assertTrue(result, "Should return True when profile exists")

    @patch('socialsentry.platforms.facebook.make_request')
    def test_check_username_exists_not_found(self, mock_request):
        """Test username not found returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = self.scanner.check_username_exists("nonexistent_user_12345")
        self.assertFalse(result, "Should return False when profile not found")

    @patch('socialsentry.platforms.facebook.make_request')
    def test_check_username_exists_request_error(self, mock_request):
        """Test request error returns False."""
        mock_request.return_value = None

        result = self.scanner.check_username_exists(self.valid_username)
        self.assertFalse(result, "Should return False on request error")

    @patch('socialsentry.platforms.facebook.make_request')
    def test_check_username_exists_private_profile(self, mock_request):
        """Test private profile detection."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'This content is unavailable right now'
        mock_request.return_value = mock_response

        result = self.scanner.check_username_exists(self.valid_username)
        self.assertFalse(result, "Should return False for restricted content")

    # ─── Email Registration Check Tests ───

    @patch('socialsentry.platforms.facebook.requests.Session')
    def test_check_email_registration_found(self, mock_session):
        """Test email registered returns registered=True."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.get.return_value = MagicMock()
        
        mock_response = MagicMock()
        mock_response.status_code = 302
        mock_session_instance.post.return_value = mock_response

        result = self.scanner.check_email_registration(self.valid_email)
        self.assertTrue(result.get("registered"), "Should detect registered email")

    @patch('socialsentry.platforms.facebook.requests.Session')
    def test_check_email_registration_not_found(self, mock_session):
        """Test email not registered returns registered=False."""
        mock_session_instance = MagicMock()
        mock_session.return_value = mock_session_instance
        mock_session_instance.get.return_value = MagicMock()
        
        mock_response = MagicMock()
        mock_response.status_code = 200  # No redirect = not found
        mock_session_instance.post.return_value = mock_response

        result = self.scanner.check_email_registration("newuser@example.com")
        self.assertFalse(result.get("registered"), "Should return not registered")

    # ─── Profile Visibility Tests ───

    @patch('socialsentry.platforms.facebook.make_request')
    def test_analyze_profile_visibility_public(self, mock_request):
        """Test public profile visibility analysis."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<title>John Doe</title><meta property="og:title" content="John Doe">'
        mock_request.return_value = mock_response

        result = self.scanner.analyze_profile_visibility(self.valid_username)
        self.assertTrue(result.get("profile_found"), "Public profile should be found")
        self.assertFalse(result.get("restricted", True), "Public profile should not be restricted")

    @patch('socialsentry.platforms.facebook.make_request')
    def test_analyze_profile_visibility_restricted(self, mock_request):
        """Test restricted profile visibility analysis."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'This content is currently unavailable'
        mock_request.return_value = mock_response

        result = self.scanner.analyze_profile_visibility(self.valid_username)
        self.assertTrue(result.get("restricted"), "Restricted profile should be detected")

    # ─── Full Audit Tests ───

    @patch.object(FacebookScanner, 'check_username_exists')
    @patch.object(FacebookScanner, 'analyze_profile_visibility')
    def test_run_full_audit_username(self, mock_vis, mock_exists):
        """Test full audit with username returns findings."""
        mock_exists.return_value = True
        mock_vis.return_value = {"profile_found": True, "visible_info": []}

        findings = self.scanner.run_full_audit(self.valid_username)
        self.assertIsInstance(findings, list, "Audit should return a list of findings")

    @patch.object(FacebookScanner, 'check_email_registration')
    def test_run_full_audit_email(self, mock_email):
        """Test full audit with email returns findings."""
        mock_email.return_value = {"registered": True}

        findings = self.scanner.run_full_audit(self.valid_email)
        self.assertIsInstance(findings, list, "Email audit should return a list of findings")


if __name__ == "__main__":
    unittest.main()
