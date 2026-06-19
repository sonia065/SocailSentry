# SocialSentry 🔐

**Authorized Social Media Security Assessment Toolkit**

A professional penetration testing tool for assessing the security posture of social media accounts across **YouTube, TikTok, Instagram, Facebook, and WhatsApp**.

> ⚠️ **LEGAL NOTICE:** This tool is designed for **authorized security testing only**. You must have explicit written permission from the account owner or proper legal authorization (e.g., bug bounty program, internal pentest) before using this tool. Unauthorized use is illegal.

## Features

### Platform Coverage
| Platform    | Recon | Auth Testing | Metadata | Public OSINT |
|-------------|-------|--------------|----------|--------------|
| Facebook    | ✅    | ✅           | ✅       | ✅           |
| Instagram   | ✅    | ✅           | ✅       | ✅           |
| YouTube     | ✅    | ✅           | ✅       | ✅           |
| TikTok      | ✅    | ✅           | ✅       | ✅           |
| WhatsApp    | ✅    | ✅           | ✅       | ✅           |

### Modules
- **Username Reconnaissance** - Check if usernames exist across platforms
- **Email-to-Account Mapping** - Find which platforms an email is registered on
- **Password Security Audit** - Test password strength & breach checks (via HaveIBeenPwned)
- **2FA Detection** - Check if accounts have 2FA enabled
- **Metadata Extraction** - Extract public metadata from profiles
- **Session Security Testing** - Analyze session configurations
- **Automated Reporting** - Generate HTML/JSON reports

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/SocialSentry.git
cd SocialSentry

# Install dependencies
pip install -r requirements.txt

# Install the tool
pip install -e .
