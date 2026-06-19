"""
Report generation engine for SocialSentry.
Generates HTML and JSON reports from assessment data.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from .colors import Colors


class ReportGenerator:
    """Generates assessment reports in multiple formats."""

    def __init__(self, output_dir=None):
        self.base_dir = Path(__file__).parent.parent.parent
        self.output_dir = Path(output_dir) if output_dir else (self.base_dir / "reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.data = {
            "tool": "SocialSentry v1.0.0",
            "timestamp": datetime.now().isoformat(),
            "target": {},
            "findings": [],
            "summary": {
                "total_checks": 0,
                "findings_count": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            },
        }

    def set_target(self, target_type, target_value):
        """Set the target information."""
        self.data["target"] = {
            "type": target_type,
            "value": target_value,
        }

    def add_finding(self, platform, check_name, severity, description, detail=""):
        """
        Add a security finding.

        Severity levels: critical, high, medium, low, info
        """
        finding = {
            "platform": platform,
            "check": check_name,
            "severity": severity.lower(),
            "description": description,
            "detail": detail,
            "timestamp": datetime.now().isoformat(),
        }
        self.data["findings"].append(finding)
        self.data["summary"]["total_checks"] += 1
        self.data["summary"]["findings_count"] += 1
        self.data["summary"][severity.lower()] += 1

    def generate_html(self, filename=None):
        """Generate an HTML report."""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        filepath = self.output_dir / filename

        # Build severity-colored HTML
        severity_colors = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#28a745",
            "info": "#17a2b8",
        }

        findings_html = ""
        for f in self.data["findings"]:
            color = severity_colors.get(f["severity"], "#6c757d")
            findings_html += f"""
            <tr>
                <td>{f['platform']}</td>
                <td>{f['check']}</td>
                <td><span style="color:{color};font-weight:bold;">{f['severity'].upper()}</span></td>
                <td>{f['description']}</td>
                <td>{f['detail']}</td>
            </tr>
            """

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SocialSentry Report - {self.data['target'].get('value', 'Unknown')}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background: #1a1a2e; color: #e0e0e0; }}
        .container {{ max-width: 1200px; margin: auto; background: #16213e; padding: 30px; border-radius: 10px; }}
        h1 {{ color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }}
        h2 {{ color: #0f3460; }}
        .summary {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin: 20px 0; }}
        .stat {{ background: #0f3460; padding: 15px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 28px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #333; }}
        th {{ background: #0f3460; color: #e94560; }}
        tr:hover {{ background: #1a1a3e; }}
        .footer {{ margin-top: 30px; text-align: center; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 SocialSentry Security Assessment Report</h1>
        <p><strong>Target:</strong> {self.data['target'].get('type', 'N/A')}: {self.data['target'].get('value', 'N/A')}</p>
        <p><strong>Date:</strong> {self.data['timestamp']}</p>

        <h2>Summary</h2>
        <div class="summary">
            <div class="stat"><div class="stat-number" style="color:#dc3545;">{self.data['summary']['critical']}</div>Critical</div>
            <div class="stat"><div class="stat-number" style="color:#fd7e14;">{self.data['summary']['high']}</div>High</div>
            <div class="stat"><div class="stat-number" style="color:#ffc107;">{self.data['summary']['medium']}</div>Medium</div>
            <div class="stat"><div class="stat-number" style="color:#28a745;">{self.data['summary']['low']}</div>Low</div>
            <div class="stat"><div class="stat-number" style="color:#17a2b8;">{self.data['summary']['info']}</div>Info</div>
        </div>
        <p>Total Checks: {self.data['summary']['total_checks']} | Total Findings: {self.data['summary']['findings_count']}</p>

        <h2>Detailed Findings</h2>
        <table>
            <tr><th>Platform</th><th>Check</th><th>Severity</th><th>Description</th><th>Details</th></tr>
            {findings_html if findings_html else '<tr><td colspan="5" style="text-align:center;">No findings recorded.</td></tr>'}
        </table>

        <div class="footer">
            <p>Generated by SocialSentry v1.0.0 | For authorized security testing only</p>
        </div>
    </div>
</body>
</html>"""

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)

        print(Colors.status_ok(f"HTML report saved: {filepath}"))
        return filepath

    def generate_json(self, filename=None):
        """Generate a JSON report."""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.output_dir / filename
        with open(filepath, "w") as f:
            json.dump(self.data, f, indent=4)

        print(Colors.status_ok(f"JSON report saved: {filepath}"))
        return filepath
