#!/usr/bin/env python3
"""
Comprehensive audit runner with GitHub issue creation.

This script runs the full audit suite, compares scores with baseline,
and automatically creates GitHub issues if significant changes are detected.
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class AuditRunner:
    """Handles comprehensive audit execution and issue creation."""

    def __init__(self, github_token: Optional[str] = None, repo: Optional[str] = None):
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.repo = repo or os.environ.get("GITHUB_REPOSITORY")
        self.audit_dir = Path("docs/audit")
        self.baseline_file = self.audit_dir / "coverage_baseline.json"
        self.delta_threshold = 5.0  # 5% delta threshold

        # Setup session with retries
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        if self.github_token:
            self.session.headers.update(
                {
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json",
                }
            )

    def run_audit_suite(self) -> Dict[str, float]:
        """Run the complete audit suite and return scores."""
        print("🚀 Running comprehensive audit suite...")

        scores = {}

        # Run audit completeness check
        print("📋 Running audit completeness check...")
        result = subprocess.run(
            [sys.executable, "scripts/audit_completeness.py"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"⚠️  Audit completeness failed: {result.stderr}")

        # Run audit synthesis to generate scores
        print("📊 Running audit synthesis...")
        result = subprocess.run(
            [sys.executable, "scripts/audit_synthesis.py"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print(f"❌ Audit synthesis failed: {result.stderr}")
            raise RuntimeError("Audit synthesis failed")

        # Extract scores from audit report
        scores = self._extract_scores()
        print(f"📈 Current scores: {scores}")

        return scores

    def _extract_scores(self) -> Dict[str, float]:
        """Extract scores from audit report."""
        audit_report = self.audit_dir / "audit_report.md"
        if not audit_report.exists():
            return {"overall": 0.0, "passes": 0, "warns": 0, "fails": 0}

        scores = {}
        try:
            with open(audit_report) as f:
                content = f.read()

                # Extract overall confidence
                import re

                match = re.search(r"Overall Rule Confidence:\s*([0-9.]+)", content)
                if match:
                    scores["overall"] = float(match.group(1))

                # Extract rule summary
                match = re.search(
                    r"PASS:\s*(\d+).*WARN:\s*(\d+).*FAIL:\s*(\d+)", content
                )
                if match:
                    scores["passes"] = int(match.group(1))
                    scores["warns"] = int(match.group(2))
                    scores["fails"] = int(match.group(3))

                # Extract inventory size
                match = re.search(r"Inventory size:\s*(\d+)", content)
                if match:
                    scores["inventory_size"] = int(match.group(1))

                # Extract CI gates
                match = re.search(
                    r"Present\s*(\d+).*Enforced\s*(\d+).*Advisory\s*(\d+)", content
                )
                if match:
                    scores["gates_present"] = int(match.group(1))
                    scores["gates_enforced"] = int(match.group(2))
                    scores["gates_advisory"] = int(match.group(3))

        except (IOError, ValueError) as e:
            print(f"⚠️  Error extracting scores: {e}")
            return {"overall": 0.0, "passes": 0, "warns": 0, "fails": 0}

        return scores

    def load_baseline(self) -> Dict[str, float]:
        """Load baseline scores."""
        if not self.baseline_file.exists():
            return {"coverage_pct": 0.0}

        try:
            with open(self.baseline_file) as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Error loading baseline: {e}")
            return {"coverage_pct": 0.0}

    def calculate_delta(self, current: float, baseline: float) -> float:
        """Calculate percentage delta between current and baseline."""
        if baseline > 0:
            return abs(current - baseline) / baseline * 100
        else:
            return 0 if current == 0 else 100

    def should_create_issue(
        self, delta: float, current_score: float, baseline_score: float
    ) -> bool:
        """Determine if an issue should be created based on delta."""
        return delta > self.delta_threshold

    def create_github_issue(
        self,
        scores: Dict[str, float],
        delta: float,
        current_score: float,
        baseline_score: float,
    ) -> Optional[int]:
        """Create GitHub issue for significant score change."""
        if not self.github_token or not self.repo:
            print(
                "⚠️  GitHub token or repository not configured, skipping issue creation"
            )
            return None

        # Determine issue type and title
        if current_score > baseline_score:
            title = f"🎉 Audit Score Improvement Alert - +{delta:.1f}% delta"
            issue_type = "improvement"
            emoji = "🎉"
        else:
            title = f"🚨 Audit Score Decline Alert - -{delta:.1f}% delta"
            issue_type = "decline"
            emoji = "🚨"

        # Generate detailed issue body
        body = self._generate_issue_body(
            scores, delta, current_score, baseline_score, issue_type
        )

        # Create issue
        url = f"https://api.github.com/repos/{self.repo}/issues"
        data = {
            "title": title,
            "body": body,
            "labels": ["audit", "automated", issue_type, "self-driving"],
        }

        try:
            response = self.session.post(url, json=data)
            response.raise_for_status()

            issue_data = response.json()
            issue_number = issue_data["number"]
            print(f"{emoji} Created GitHub issue #{issue_number}: {title}")
            return issue_number

        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to create GitHub issue: {e}")
            return None

    def _generate_issue_body(
        self,
        scores: Dict[str, float],
        delta: float,
        current_score: float,
        baseline_score: float,
        issue_type: str,
    ) -> str:
        """Generate detailed issue body."""
        body = []

        # Header
        body.append(
            f"## { 'Score Improvement' if issue_type == 'improvement' else 'Score Decline' } Detected"
        )
        body.append("")

        # Score summary
        body.append("### Score Summary")
        body.append(f"- **Current Score:** {current_score:.1f}%")
        body.append(f"- **Previous Baseline:** {baseline_score:.1f}%")
        body.append(
            f"- **Delta:** {delta:.1f}% {'increase' if issue_type == 'improvement' else 'decrease'}"
        )
        body.append(f"- **Threshold:** {self.delta_threshold}%")
        body.append("")

        # Detailed metrics
        body.append("### Detailed Metrics")
        body.append(f"- ✅ Rules Passing: {scores.get('passes', 0)}")
        body.append(f"- ⚠️ Rules Warning: {scores.get('warns', 0)}")
        body.append(f"- ❌ Rules Failing: {scores.get('fails', 0)}")
        body.append(f"- 📋 Inventory Size: {scores.get('inventory_size', 0)} files")
        body.append(
            f"- 🚪 CI Gates: {scores.get('gates_present', 0)} present, {scores.get('gates_enforced', 0)} enforced"
        )
        body.append("")

        # Analysis
        body.append("### Analysis")
        if issue_type == "improvement":
            body.append(
                "This represents a positive improvement in code quality and governance compliance."
            )
            body.append(
                "The automated audit has detected significant improvements in the codebase."
            )
        else:
            body.append(
                "This may indicate degradation in code quality or governance compliance."
            )
            body.append(
                "The automated audit has detected concerning changes that should be reviewed."
            )
        body.append("")

        # Next steps
        body.append("### Next Steps")
        if issue_type == "improvement":
            body.append(
                "- Review the improvements to understand what drove the score increase"
            )
            body.append(
                "- Consider updating quality gates if the improvement is sustained"
            )
            body.append("- Document successful improvement strategies")
        else:
            body.append("- Review recent changes that may have impacted audit scores")
            body.append("- Check audit reports for specific areas of concern")
            body.append("- Consider remediation actions if decline continues")
            body.append("- Prioritize addressing failing rules and warnings")
        body.append("")

        # Audit details
        body.append("### Audit Details")
        body.append(f"- **Timestamp:** {datetime.now().isoformat()}")
        body.append(f"- **Audit Directory:** docs/audit/")
        body.append("- **Related Files:**")
        body.append("  - [Audit Report](docs/audit/audit_report.md)")
        body.append("  - [Remediation Plan](docs/audit/remediation_plan.md)")
        body.append("  - [Rule Confidence](docs/audit/rule_confidence.csv)")
        body.append("")

        # Automation info
        body.append("---")
        body.append(
            "*This issue was automatically created by the self-driving audit mechanism.*"
        )
        body.append(
            "*The audit system continuously monitors code quality and governance compliance.*"
        )

        return "\n".join(body)

    def update_baseline(self, current_score: float) -> None:
        """Update baseline score if current score is higher."""
        baseline = self.load_baseline()
        baseline_score = float(baseline.get("coverage_pct", 0))

        if current_score > baseline_score:
            print(
                f"📈 Updating baseline from {baseline_score:.1f}% to {current_score:.1f}%"
            )
            baseline_data = {
                "coverage_pct": current_score,
                "updated_at": datetime.now().isoformat(),
            }

            with open(self.baseline_file, "w") as f:
                json.dump(baseline_data, f, indent=2)
        else:
            print(f"📊 Keeping existing baseline: {baseline_score:.1f}%")

    def run_comprehensive_audit(self) -> bool:
        """Run the complete audit process with issue creation."""
        try:
            print("🎯 Starting comprehensive audit process...")

            # Run audit suite
            scores = self.run_audit_suite()
            current_score = scores.get("overall", 0.0)

            # Load baseline
            baseline = self.load_baseline()
            baseline_score = float(baseline.get("coverage_pct", 0))

            print(
                f"📊 Score comparison: {current_score:.1f}% (current) vs {baseline_score:.1f}% (baseline)"
            )

            # Calculate delta
            delta = self.calculate_delta(current_score, baseline_score)
            print(f"📈 Score delta: {delta:.1f}%")

            # Check if we should create an issue
            if self.should_create_issue(delta, current_score, baseline_score):
                print(
                    f"🚨 Significant delta detected ({delta:.1f}% > {self.delta_threshold}%)"
                )
                self.create_github_issue(scores, delta, current_score, baseline_score)
            else:
                print(
                    f"✅ Score delta within acceptable range ({delta:.1f}% ≤ {self.delta_threshold}%)"
                )

            # Update baseline if improved
            self.update_baseline(current_score)

            print("✅ Comprehensive audit completed successfully!")
            return True

        except Exception as e:
            print(f"❌ Comprehensive audit failed: {e}")
            return False


def main():
    """Main entry point for comprehensive audit runner."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Comprehensive audit runner with GitHub issue creation"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=5.0,
        help="Delta threshold for issue creation (default: 5.0%)",
    )
    parser.add_argument(
        "--no-issue", action="store_true", help="Skip GitHub issue creation"
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Create runner instance
    runner = AuditRunner()
    runner.delta_threshold = args.threshold

    if args.no_issue:
        runner.github_token = None

    try:
        success = runner.run_comprehensive_audit()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n⚠️  Audit interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
