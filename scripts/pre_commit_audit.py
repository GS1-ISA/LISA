#!/usr/bin/env python3
"""
Pre-commit audit threshold checker.

This script runs as a pre-commit hook to ensure audit scores meet the minimum
threshold before allowing commits. It integrates with the existing audit
infrastructure and provides clear failure messages with improvement suggestions.
"""

import json
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# Configuration
DEFAULT_THRESHOLD = 70.0
CONFIG_FILE = ".audit_threshold.json"
AUDIT_DIR = Path("docs/audit")
REQUIRED_AUDIT_FILES = ["audit_report.md", "rule_confidence.csv", "remediation_plan.md"]


class AuditThresholdError(Exception):
    """Raised when audit threshold is not met."""

    pass


class AuditChecker:
    """Handles audit threshold checking and reporting."""

    def __init__(self, threshold: Optional[float] = None):
        self.threshold = threshold or self._load_threshold()
        self.audit_dir = AUDIT_DIR
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []

    def _load_threshold(self) -> float:
        """Load threshold from configuration file or use default."""
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    return float(config.get("threshold", DEFAULT_THRESHOLD))
            except (json.JSONDecodeError, ValueError, KeyError):
                print(
                    f"Warning: Invalid config in {CONFIG_FILE}, using default threshold"
                )

        return DEFAULT_THRESHOLD

    def _check_audit_files_exist(self) -> bool:
        """Check if required audit files exist."""
        missing_files = []
        for file_name in REQUIRED_AUDIT_FILES:
            file_path = self.audit_dir / file_name
            if not file_path.exists():
                missing_files.append(file_name)

        if missing_files:
            self.errors.append(f"Missing audit files: {', '.join(missing_files)}")
            self.suggestions.append(
                "Run 'make audit' or 'python scripts/audit_synthesis.py' to generate audit files"
            )
            return False

        return True

    def _extract_current_score(self) -> Optional[float]:
        """Extract current audit score from audit report."""
        audit_report = self.audit_dir / "audit_report.md"
        if not audit_report.exists():
            return None

        try:
            with open(audit_report) as f:
                content = f.read()
                # Look for "Overall Rule Confidence: XX.X %"
                import re

                match = re.search(r"Overall Rule Confidence:\s*([0-9.]+)", content)
                if match:
                    return float(match.group(1))
        except (IOError, ValueError):
            pass

        return None

    def _extract_rule_summary(self) -> Tuple[int, int, int]:
        """Extract rule summary (pass, warn, fail) from audit report."""
        audit_report = self.audit_dir / "audit_report.md"
        if not audit_report.exists():
            return 0, 0, 0

        try:
            with open(audit_report) as f:
                content = f.read()
                # Look for "PASS: X ✅ | WARN: Y ⚠️ | FAIL: Z ❌"
                import re

                match = re.search(
                    r"PASS:\s*(\d+).*WARN:\s*(\d+).*FAIL:\s*(\d+)", content
                )
                if match:
                    return int(match.group(1)), int(match.group(2)), int(match.group(3))
        except IOError:
            pass

        return 0, 0, 0

    def _get_remediation_suggestions(self) -> List[str]:
        """Get remediation suggestions from remediation plan."""
        remediation_plan = self.audit_dir / "remediation_plan.md"
        if not remediation_plan.exists():
            return []

        suggestions = []
        try:
            with open(remediation_plan) as f:
                content = f.read()
                # Extract checklist items
                import re

                items = re.findall(r"- \[[x ]\] (.+)", content)
                # Get incomplete items (not checked)
                incomplete = [item for item in items if not item.startswith("[x]")]
                suggestions.extend(incomplete[:3])  # Top 3 incomplete items
        except IOError:
            pass

        return suggestions

    def _analyze_score_trend(self) -> str:
        """Analyze score trend based on baseline comparison."""
        baseline_file = self.audit_dir / "coverage_baseline.json"
        if not baseline_file.exists():
            return "No baseline available for trend analysis"

        try:
            with open(baseline_file) as f:
                baseline_data = json.load(f)
                baseline_score = float(baseline_data.get("coverage_pct", 0))
        except (json.JSONDecodeError, ValueError, KeyError):
            return "Invalid baseline data"

        current_score = self._extract_current_score()
        if current_score is None:
            return "Unable to determine current score for trend analysis"

        delta = current_score - baseline_score
        if abs(delta) < 1.0:
            return "Score stable (±1%)"
        elif delta > 0:
            return f"Score improving (+{delta:.1f}%)"
        else:
            return f"Score declining ({delta:.1f}%)"

    def run_audit_check(self) -> bool:
        """Run the complete audit threshold check."""
        print("🔍 Running pre-commit audit threshold check...")
        print(f"📊 Threshold: {self.threshold}%")

        # Check if audit files exist
        if not self._check_audit_files_exist():
            return False

        # Extract current score
        current_score = self._extract_current_score()
        if current_score is None:
            self.errors.append("Unable to extract audit score from audit_report.md")
            self.suggestions.append(
                "Ensure audit_report.md contains 'Overall Rule Confidence' score"
            )
            return False

        print(f"📈 Current audit score: {current_score:.1f}%")

        # Extract rule summary
        passes, warns, fails = self._extract_rule_summary()
        print(f"✅ PASS: {passes} | ⚠️ WARN: {warns} | ❌ FAIL: {fails}")

        # Check threshold
        if current_score < self.threshold:
            self.errors.append(
                f"Audit score {current_score:.1f}% is below threshold {self.threshold}%"
            )

            # Get remediation suggestions
            remediation_suggestions = self._get_remediation_suggestions()
            if remediation_suggestions:
                self.suggestions.append("Priority remediation items:")
                self.suggestions.extend(
                    [f"  • {item}" for item in remediation_suggestions]
                )

            # Add general suggestions
            self.suggestions.extend(
                [
                    "Review audit report for specific failure areas",
                    "Check remediation plan for prioritized actions",
                    "Consider running 'make audit' for detailed analysis",
                    "Address failing rules to improve overall score",
                ]
            )

            return False

        # Score meets threshold, but check for warnings
        if warns > 0 or fails > 0:
            self.warnings.append(
                f"Score meets threshold but {warns} warnings and {fails} failures detected"
            )
            self.suggestions.append(
                "Consider addressing warnings and failures for continuous improvement"
            )

        # Show trend analysis
        trend = self._analyze_score_trend()
        print(f"📊 Trend: {trend}")

        print("✅ Audit threshold check passed!")
        return True

    def generate_failure_report(self) -> str:
        """Generate detailed failure report."""
        report = []
        report.append("❌ Audit Threshold Check Failed")
        report.append("=" * 40)
        report.append("")

        if self.errors:
            report.append("🔴 ERRORS:")
            for error in self.errors:
                report.append(f"  • {error}")
            report.append("")

        if self.warnings:
            report.append("⚠️  WARNINGS:")
            for warning in self.warnings:
                report.append(f"  • {warning}")
            report.append("")

        if self.suggestions:
            report.append("💡 SUGGESTIONS:")
            for suggestion in self.suggestions:
                report.append(f"  • {suggestion}")
            report.append("")

        report.append("📋 NEXT STEPS:")
        report.append("  1. Review the audit report: docs/audit/audit_report.md")
        report.append("  2. Check remediation plan: docs/audit/remediation_plan.md")
        report.append("  3. Run detailed audit: make audit")
        report.append("  4. Address identified issues and re-commit")

        return "\n".join(report)


def main():
    """Main entry point for pre-commit audit check."""
    import argparse

    parser = argparse.ArgumentParser(description="Pre-commit audit threshold checker")
    parser.add_argument(
        "--threshold",
        type=float,
        help=f"Audit score threshold (default: {DEFAULT_THRESHOLD})",
        default=None,
    )
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Create checker instance
    checker = AuditChecker(threshold=args.threshold)

    try:
        # Run the audit check
        passed = checker.run_audit_check()

        if not passed:
            # Generate and print failure report
            print(checker.generate_failure_report())
            sys.exit(1)

        # Success case
        if args.verbose:
            print("✅ All audit checks passed!")

        sys.exit(0)

    except Exception as e:
        print(f"❌ Unexpected error during audit check: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
