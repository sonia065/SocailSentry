"""
Test cases for Instagram scanner module.
"""

import sys
import json
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from socialsentry.core.config import Config
from socialsentry.platforms.instagram import InstagramScanner


class TestInstagramScanner(unittest.TestCase):
    """Test Instagram scanner functionality."""

    @classmethod
    def setUpClass(cls):
        """Setup test resources once."""
        cls.config = Config()
        cls.scanner = InstagramScanner(cls.config)

    def setUp(self):
        """Setup before each test."""
        self.valid_username = "johndoe"
        self.mock_init_state = json.dumps({
            "user": {
                "full_name": "John Doe",
                "biography": "Test bio",
                "is_private": False,
                "is_verified": True,
                "edge_followed_by": {"count": 1000},
                "edge_follow": {"count": 500},
                "edge_owner_to_timeline_media": {"count": 50}
            }
        })

    # ─── Username Existence Tests ───

    @patch('socialsentry.platforms.instagram.make_request')
    def test_check_username_exists_found(self, mock_request):
        """Test username found returns True."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = f'window.__INITIAL_STATE__ = {self.mock_init_state};'
        mock_request.return_value = mock_response

        result = self.scanner.check_username_exists(self.valid_username)
        self.assertTrue(result, "Should return True when profile exists")

    @patch('socialsentry.platforms.instagram.make_request')
    def test_check_username_exists_not_found(self, mock_request):
        """Test username not found returns False."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        result = self.scanner.check_username_exists("nonexistent_user")
        self.assertFalse(result, "Should return False when profile not found")

    @patch('socialsentry.platforms.instagram.make_request')
    def test_check_username_exists_request_error(self, mock_request):
        """Test request error returns False."""
        mock_request.return_value = None

        result = self.scanner.check_username_exists(self.valid_username)
        self.assertFalse(result, "Should return False on request error")

    @patch('socialsentry.platforms.instagram.make_request')
    def test_check_username_exists_fallback(self, mock_request):
        """Test fallback detection via username string."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '"username":"johndoe"'
        mock_request.return_value = mock_response

        result = self.scanner.check_username_exists(self.valid_username)
        self.assertTrue(result, "Should detect username via fallback string match")

    # ─── Public Info Extraction Tests ───

    @patch('socialsentry.platforms.instagram.make_request')
    def test_extract_public_info_found(self, mock_request):
        """Test extract public info returns correct data."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = f'window.__INITIAL_STATE__ = {self.mock_init_state};'
        mock_request.return_value = mock_response

        info = self.scanner.extract_public_info(self.valid_username)
        self.assertTrue(info.get("exists"), "Profile should exist")
        self.assertEqual(info.get("full_name"), "John Doe")
        self.assertEqual(info.get("biography"), "Test bio")
        self.assertEqual(info.get("follower_count"), 1000)
        self.assertEqual(info.get("following_count"), 500)
        self.assertEqual(info.get("post_count"), 50)
        self.assertTrue(info.get("is_verified"))
        self.assertFalse(info.get("is_private"))

    @patch('socialsentry.platforms.instagram.make_request')
    def test_extract_public_info_not_found(self, mock_request):
        """Test extract public info returns empty for non-existent profile."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        info = self.scanner.extract_public_info("nonexistent_user")
        self.assertFalse(info.get("exists"), "Non-existent profile should not exist")

    @patch('socialsentry.platforms.instagram.make_request')
    def test_extract_public_info_og_title_fallback(self, mock_request):
        """Test fallback extraction via OG title."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '<meta property="og:title" content="John Doe (@johndoe)">'
        mock_request.return_value = mock_response

        info = self.scanner.extract_public_info(self.valid_username)
        self.assertEqual(info.get("full_name"), "John Doe (@johndoe)")

    # ─── Full Audit Tests ───

    @patch.object(InstagramScanner, 'check_username_exists')
    @patch.object(InstagramScanner, 'extract_public_info')
    def test_run_full_audit(self, mock_info, mock_exists):
        """Test full audit returns findings list."""
        mock_exists.return_value = True
        mock_info.return_value = {"exists": True, "full_name": "John"}

        findings = self.scanner.run_full_audit(self.valid_username)
        self.assertIsInstance(findings, list, "Audit should return list")


if __name__ == "__main__":
    unittest.main()
