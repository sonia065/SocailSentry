"""
Test suite for SocialSentry modules.
Run all tests: python -m pytest tests/
Run specific: python -m pytest tests/test_facebook.py -v
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))
