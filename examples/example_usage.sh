#!/bin/bash
#
# Example usage of SocialSentry toolkit
#

echo "=========================================="
echo "  SocialSentry - Example Usage"
echo "=========================================="
echo ""

# 1. Check username across all platforms
echo "1] Checking username across platforms:"
python socialsentry/main.py username johndoe
echo ""

# 2. Check specific platforms only
echo "2] Checking username on specific platforms:"
python socialsentry/main.py username johndoe --platforms instagram tiktok
echo ""

# 3. Email reconnaissance
echo "3] Checking email registration:"
python socialsentry/main.py email user@example.com
echo ""

# 4. Full platform audit
echo "4] Running full Instagram audit:"
python socialsentry/main.py audit instagram --target johndoe
echo ""

# 5. Password security check
echo "5] Checking password strength:"
python socialsentry/main.py check-password "MySecureP@ss123"
echo ""

# 6. Generate report
echo "6] Generating HTML report:"
python socialsentry/main.py report --format html
echo ""

echo "=========================================="
echo "  Reports saved in reports/ directory"
echo "=========================================="
