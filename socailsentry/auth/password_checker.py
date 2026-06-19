"""
Password security assessment module.
Tests password strength and checks against known breaches.
"""

import hashlib
import requests
from ..core.colors import Colors


class PasswordChecker:
    """
    Password security checking module.
    - Password strength analysis
    - HaveIBeenPwned breach check (k-anonymity model)
    - Common password detection
    """

    def __init__(self, config):
        self.config = config
        self.pwned_api = "https://api.pwnedpasswords.com/range/"

    def check_strength(self, password):
        """
        Analyze password strength.
        
        Args:
            password: Password to analyze
            
        Returns:
            dict: Strength analysis
        """
        score = 0
        feedback = []

        # Length check
        if len(password) < 8:
            feedback.append("Too short (min 8 characters)")
        elif len(password) >= 12:
            score += 2
            feedback.append("Good length")
        else:
            score += 1
            feedback.append("Adequate length")

        # Complexity checks
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Missing uppercase letters")

        if re.search(r'[0-9]', password):
            score += 1
        else:
            feedback.append("Missing numbers")

        if re.search(r'[^a-zA-Z0-9]', password):
            score += 1
        else:
            feedback.append("Missing special characters")

        # Rating
        if score >= 6:
            strength = "Strong"
        elif score >= 4:
            strength = "Medium"
        else:
            strength = "Weak"

        result = {
            "password_length": len(password),
            "score": score,
            "strength": strength,
            "feedback": feedback,
        }

        print(Colors.BOLD + Colors.G + "\n[ Password Strength Check ]" + Colors.N)
        print(f"  Length: {len(password)} characters")
        print(f"  Strength: {strength} (Score: {score}/6)")
        for fb in feedback:
            print(f"  {'✓' if 'Missing' not in fb else '✗'} {fb}")

        return result

    def check_pwned(self, password):
        """
        Check if password has been exposed in data breaches
        using HaveIBeenPwned API (k-anonymity).
        
        Args:
            password: Password to check
            
        Returns:
            dict: Breach check results
        """
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        try:
            response = requests.get(
                self.pwned_api + prefix,
                timeout=10,
                headers={"User-Agent": "SocialSentry-Pentest-Tool"}
            )

            if response.status_code == 200:
                hashes = response.text.splitlines()
                for line in hashes:
                    if line.startswith(suffix):
                        count = int(line.split(":")[1])
                        result = {
                            "exposed": True,
                            "exposure_count": count,
                            "message": f"Password found in {count:,} breaches!"
                        }
                        print(Colors.status_fail(f"⚠ PASSWORD COMPROMISED: Found in {count:,} data breaches!"))
                        return result

                print(Colors.status_ok("Password not found in known breaches."))
                return {"exposed": False, "exposure_count": 0, "message": "Password not found in known breaches"}

        except Exception as e:
            print(Colors.status_warn(f"Could not check breach database: {str(e)}"))

        return {"exposed": False, "exposure_count": 0, "message": "Breach check unavailable"}

    def full_check(self, password):
        """
        Complete password security assessment.
        
        Args:
            password: Password to assess
            
        Returns:
            dict: Complete assessment
        """
        strength = self.check_strength(password)
        breach = self.check_pwned(password)

        return {
            "strength": strength,
            "breach_check": breach,
        }


import re
