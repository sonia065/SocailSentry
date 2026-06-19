"""
Utility functions for SocialSentry.
"""

import re
import time
import functools
import requests
from .colors import Colors


def validate_username(username):
    """Validate a social media username format."""
    if not username or len(username) < 2:
        return False
    if len(username) > 30:
        return False
    # Most platforms allow alphanumeric, underscore, dot, hyphen
    if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
        return False
    return True


def validate_email(email):
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone):
    """Validate phone number format (basic)."""
    cleaned = re.sub(r'[\s\-\+\(\)]', '', phone)
    return cleaned.isdigit() and len(cleaned) >= 7


def make_request(url, timeout=15, headers=None):
    """
    Make an HTTP request with error handling.
    
    Args:
        url: Target URL
        timeout: Request timeout in seconds
        headers: Custom HTTP headers
        
    Returns:
        Response object or None on failure
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    if headers:
        default_headers.update(headers)

    try:
        response = requests.get(url, headers=default_headers, timeout=timeout, allow_redirects=True)
        return response
    except requests.exceptions.Timeout:
        print(Colors.status_warn(f"Timeout: {url}"))
        return None
    except requests.exceptions.ConnectionError:
        print(Colors.status_fail(f"Connection error: {url}"))
        return None
    except Exception as e:
        print(Colors.status_fail(f"Request failed: {url} - {str(e)}"))
        return None


def sanitize_output(text):
    """Sanitize output text to avoid terminal issues."""
    if not text:
        return ""
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text.strip()


def timer(func):
    """Decorator to time function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(Colors.status_info(f"Completed in {elapsed:.2f}s"))
        return result
    return wrapper
