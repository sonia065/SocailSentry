"""
Password security assessment module.
Tests password strength and checks against known breaches.
"""

import re
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
        self.common_passwords = [
            "123456", "password", "123456789", "12345678", "12345",
            "1234567", "qwerty123", "abc123", "football", "monkey",
            "iloveyou", "trustno1", "sunshine", "master", "welcome",
            "shadow", "ashley", "footbal", "jesus", "michael",
            "ninja", "mustang", "password1", "admin", "letmein",
        ]

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
        suggestions = []

        # Length check
        if len(password) < 8:
            feedback.append("❌ Too short (minimum 8 characters required)")
            suggestions.append("Use at least 12-16 characters")
        elif len(password) >= 16:
            score += 3
            feedback.append("✅ Excellent length")
        elif len(password) >= 12:
            score += 2
            feedback.append("✅ Good length")
        else:
            score += 1
            feedback.append("⚠️ Adequate length, could be longer")

        # Character type checks
        has_lower = bool(re.search(r'[a-z]', password))
        has_upper = bool(re.search(r'[A-Z]', password))
        has_digit = bool(re.search(r'[0-9]', password))
        has_special = bool(re.search(r'[^a-zA-Z0-9]', password))

        if has_lower:
            score += 1
        else:
            feedback.append("❌ Missing lowercase letters")
            suggestions.append("Add lowercase letters (a-z)")

        if has_upper:
            score += 1
        else:
            feedback.append("❌ Missing uppercase letters")
            suggestions.append("Add uppercase letters (A-Z)")

        if has_digit:
            score += 1
        else:
            feedback.append("❌ Missing numbers")
            suggestions.append("Add numbers (0-9)")

        if has_special:
            score += 1
        else:
            feedback.append("❌ Missing special characters (!@#$% etc)")
            suggestions.append("Add special characters like !@#$%^&*")

        # Check for common patterns
        if password.lower() in self.common_passwords:
            score = max(0, score - 3)
            feedback.append("❌ This is a VERY common password!")
            suggestions.append("Use a unique, random password")

        if re.search(r'(.)\1{2,}', password):
            score = max(0, score - 1)
            feedback.append("⚠️ Contains repeated characters (e.g., 'aaa')")

        if re.search(r'(123|abc|qwerty|asdf|zxcv)', password.lower()):
            score = max(0, score - 1)
            feedback.append("⚠️ Contains common keyboard pattern")

        # Rating
        if score >= 7:
            strength = "Strong 💪"
            color = Colors.G
        elif score >= 4:
            strength = "Medium ⚡"
            color = Colors.Y
        else:
            strength = "Weak ❌"
            color = Colors.R

        result = {
            "password_length": len(password),
            "score": score,
            "max_score": 8,
            "strength": strength,
            "feedback": feedback,
            "suggestions": suggestions,
        }

        print(f"\n{Colors.BOLD}{Colors.B}[ Password Strength Check ]{Colors.N}")
        print(f"{'='*50}")
        print(f"  Length: {len(password)} characters")
        print(f"  Strength: {color}{strength}{Colors.N} (Score: {score}/8)")
        print(f"\n  {Colors.BOLD}Analysis:{Colors.N}")
        for fb in feedback:
            print(f"    {fb}")
        if suggestions:
            print(f"\n  {Colors.BOLD}Suggestions:{Colors.N}")
            for s in suggestions:
                print(f"    → {s}")

        return result

    def check_pwned(self, password):
        """
        Check if password has been exposed in data breaches
        using HaveIBeenPwned API (k-anonymity model).
        
        Args:
            password: Password to check
            
        Returns:
            dict: Breach check results
        """
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        print(f"\n{Colors.BOLD}{Colors.B}[ Breach Database Check ]{Colors.N}")
        print(f"{'='*50}")
        print(f"  Checking HaveIBeenPwned (k-anonymity)...")

        try:
            response = requests.get(
                self.pwned_api + prefix,
                timeout=10,
                headers={"User-Agent": "SocialSentry-Pentest-Tool v1.0"}
            )

            if response.status_code == 200:
                hashes = response.text.splitlines()
                for line in hashes:
                    if line.startswith(suffix):
                        count = int(line.split(":")[1].strip())
                        result = {
                            "exposed": True,
                            "exposure_count": count,
                            "message": f"Password found in {count:,} data breaches!"
                        }
                        print(f"  {Colors.R}⚠️  PASSWORD COMPROMISED!{Colors.N}")
                        print(f"  Found in {Colors.BOLD}{count:,}{Colors.N} known data breaches!")
                        print(f"  {Colors.Y}IMMEDIATELY change this password on all sites!{Colors.N}")
                        return result

                print(f"  {Colors.G}✅ Password not found in any known breaches.{Colors.N}")
                return {
                    "exposed": False,
                    "exposure_count": 0,
                    "message": "Password not found in known breaches"
                }

        except requests.exceptions.Timeout:
            print(f"  {Colors.Y}⚠️  Breach database check timed out{Colors.N}")
        except requests.exceptions.ConnectionError:
            print(f"  {Colors.Y}⚠️  Could not connect to breach database{Colors.N}")
        except Exception as e:
            print(f"  {Colors.Y}⚠️  Breach check error: {str(e)}{Colors.N}")

        return {
            "exposed": False,
            "exposure_count": 0,
            "message": "Breach check unavailable"
        }

    def full_check(self, password):
        """
        Complete password security assessment.
        
        Args:
            password: Password to assess
            
        Returns:
            dict: Complete assessment
        """
        print(f"\n{Colors.BOLD}{Colors.M}{'='*50}{Colors.N}")
        print(f"{Colors.BOLD}{Colors.M}   COMPLETE PASSWORD SECURITY ASSESSMENT{Colors.N}")
        print(f"{Colors.BOLD}{Colors.M}{'='*50}{Colors.N}")

        strength = self.check_strength(password)
        breach = self.check_pwned(password)

        # Final verdict
        print(f"\n{Colors.BOLD}{Colors.B}[ FINAL VERDICT ]{Colors.N}")
        print(f"{'='*50}")
        
        if breach.get("exposed"):
            print(f"  {Colors.R}⚠️  CRITICAL: Password is COMPROMISED!{Colors.N}")
            print(f"  {Colors.R}   Change it immediately everywhere you use it!{Colors.N}")
        elif strength["score"] >= 7:
            print(f"  {Colors.G}✅ GOOD: Strong password not found in breaches{Colors.N}")
        elif strength["score"] >= 4:
            print(f"  {Colors.Y}⚠️  WARNING: Password strength could be improved{Colors.N}")
        else:
            print(f"  {Colors.R}❌ WEAK: Password needs significant improvement{Colors.N}")

        return {
            "strength": strength,
            "breach_check": breach,
        }
