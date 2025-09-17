#!/usr/bin/env python3
"""
Validation script for the three self-driving audit mechanisms.

This script validates that all three audit mechanisms are properly configured
and functional.
"""

import json
import os
import subprocess
import sys
from pathlib import Path


class AuditMechanismValidator:
    """Validates the three self-driving audit mechanisms."""

    def __init__(self):
        self.results: list[tuple[str, bool, str]] = []
        self.github_action_file = Path(".github/workflows/nightly_audit.yml")
        self.pre_commit_config = Path(".pre-commit-config.yaml")
        self.makefile = Path("Makefile")
        self.pre_commit_script = Path("scripts/pre_commit_audit.py")
        self.audit_with_issue_script = Path("scripts/audit_with_issue.py")
        self.audit_threshold_config = Path(".audit_threshold.json")
        self.readme = Path("README.md")

    def _run_command(self, cmd: list[str], description: str) -> tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return True, result.stdout.strip()
            else:
                return False, result.stderr.strip() or result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return False, str(e)

    def validate_github_action(self) -> bool:
        """Validate GitHub Action configuration."""
        print("🔍 Validating GitHub Action...")

        # Check file exists
        if not self.github_action_file.exists():
            self.results.append(("GitHub Action File", False, "File not found"))
            return False

        # Check YAML syntax
        try:
            import yaml

            with open(self.github_action_file) as f:
                yaml.safe_load(f)
            self.results.append(("GitHub Action YAML", True, "Valid YAML syntax"))
        except yaml.YAMLError as e:
            self.results.append(("GitHub Action YAML", False, f"Invalid YAML: {e}"))
            return False

        # Check required components
        content = self.github_action_file.read_text()
        required_components = [
            "schedule:",
            "cron:",
            "nightly_audit.yml",
            "python scripts/audit_completeness.py",
            "python scripts/audit_synthesis.py",
            "audit-badge.svg",
            "GITHUB_TOKEN",
            "issues: write",
        ]

        missing_components = []
        for component in required_components:
            if component not in content:
                missing_components.append(component)

        if missing_components:
            self.results.append(
                ("GitHub Action Components", False, f"Missing: {missing_components}")
            )
            return False

        self.results.append(("GitHub Action", True, "All components present"))
        return True

    def validate_pre_commit_hook(self) -> bool:
        """Validate pre-commit hook configuration."""
        print("🔍 Validating pre-commit hook...")

        # Check pre-commit config exists
        if not self.pre_commit_config.exists():
            self.results.append(("Pre-commit Config", False, "File not found"))
            return False

        # Check YAML syntax
        try:
            import yaml

            with open(self.pre_commit_config) as f:
                config = yaml.safe_load(f)
            self.results.append(("Pre-commit YAML", True, "Valid YAML syntax"))
        except yaml.YAMLError as e:
            self.results.append(("Pre-commit YAML", False, f"Invalid YAML: {e}"))
            return False

        # Check audit threshold hook is configured
        hooks = config.get("repos", [])
        audit_hook_found = False
        for repo in hooks:
            if repo.get("repo") == "local":
                for hook in repo.get("hooks", []):
                    if hook.get("id") == "audit-threshold":
                        audit_hook_found = True
                        break

        if not audit_hook_found:
            self.results.append(
                ("Pre-commit Hook", False, "Audit threshold hook not found")
            )
            return False

        # Check script exists and is executable
        if not self.pre_commit_script.exists():
            self.results.append(("Pre-commit Script", False, "Script not found"))
            return False

        if not os.access(self.pre_commit_script, os.X_OK):
            self.results.append(("Pre-commit Script", False, "Script not executable"))
            return False

        # Check threshold config exists
        if not self.audit_threshold_config.exists():
            self.results.append(("Threshold Config", False, "Config file not found"))
            return False

        try:
            with open(self.audit_threshold_config) as f:
                config_data = json.load(f)
                threshold = float(config_data.get("threshold", 0))
                if threshold <= 0:
                    raise ValueError("Invalid threshold")
            self.results.append(("Threshold Config", True, f"Threshold: {threshold}%"))
        except (json.JSONDecodeError, ValueError) as e:
            self.results.append(("Threshold Config", False, f"Invalid config: {e}"))
            return False

        self.results.append(("Pre-commit Hook", True, "Configuration valid"))
        return True

    def validate_makefile_target(self) -> bool:
        """Validate Makefile audit target."""
        print("🔍 Validating Makefile audit target...")

        # Check Makefile exists
        if not self.makefile.exists():
            self.results.append(("Makefile", False, "File not found"))
            return False

        content = self.makefile.read_text()

        # Check audit target exists
        if "audit:" not in content:
            self.results.append(
                ("Makefile Audit Target", False, "Audit target not found")
            )
            return False

        # Check audit script exists and is executable
        if not self.audit_with_issue_script.exists():
            self.results.append(("Audit Script", False, "Script not found"))
            return False

        if not os.access(self.audit_with_issue_script, os.X_OK):
            self.results.append(("Audit Script", False, "Script not executable"))
            return False

        # Check required commands in audit target
        required_commands = [
            "python scripts/audit_completeness.py",
            "python scripts/audit_synthesis.py",
            "python scripts/audit_with_issue.py",
        ]

        missing_commands = []
        for cmd in required_commands:
            if cmd not in content:
                missing_commands.append(cmd)

        if missing_commands:
            self.results.append(
                ("Makefile Commands", False, f"Missing: {missing_commands}")
            )
            return False

        self.results.append(("Makefile Audit Target", True, "All components present"))
        return True

    def validate_readme_integration(self) -> bool:
        """Validate README.md integration."""
        print("🔍 Validating README integration...")

        if not self.readme.exists():
            self.results.append(("README", False, "File not found"))
            return False

        content = self.readme.read_text()

        # Check audit badge is present
        if "![Audit Score](audit-badge.svg)" not in content:
            self.results.append(("README Badge", False, "Audit badge not found"))
            return False

        # Check self-driving audit section exists
        if "## 🤖 Self-Driving Audit Mechanisms" not in content:
            self.results.append(
                ("README Section", False, "Audit mechanisms section not found")
            )
            return False

        # Check all three mechanisms are documented
        mechanisms = ["Nightly Audit", "Pre-commit Audit", "Makefile Audit"]
        missing_mechanisms = []
        for mechanism in mechanisms:
            if mechanism not in content:
                missing_mechanisms.append(mechanism)

        if missing_mechanisms:
            self.results.append(
                ("README Documentation", False, f"Missing: {missing_mechanisms}")
            )
            return False

        self.results.append(("README Integration", True, "All integrations present"))
        return True

    def validate_script_functionality(self) -> bool:
        """Validate script functionality with basic tests."""
        print("🔍 Validating script functionality...")

        # Test pre-commit script help
        success, output = self._run_command(
            [sys.executable, str(self.pre_commit_script), "--help"],
            "Pre-commit script help",
        )

        if not success or "Audit score threshold" not in output:
            self.results.append(
                ("Pre-commit Script Help", False, "Help command failed")
            )
            return False

        self.results.append(("Pre-commit Script Help", True, "Help command works"))

        # Test audit with issue script help
        success, output = self._run_command(
            [sys.executable, str(self.audit_with_issue_script), "--help"],
            "Audit with issue script help",
        )

        if not success or "Comprehensive audit runner" not in output:
            self.results.append(("Audit Script Help", False, "Help command failed"))
            return False

        self.results.append(("Audit Script Help", True, "Help command works"))

        # Test audit threshold config
        try:
            with open(self.audit_threshold_config) as f:
                config = json.load(f)
                if config.get("threshold") != 70.0:
                    raise ValueError("Wrong threshold value")
            self.results.append(
                ("Threshold Config Value", True, "Default threshold: 70.0%")
            )
        except (json.JSONDecodeError, ValueError) as e:
            self.results.append(("Threshold Config Value", False, f"Config error: {e}"))
            return False

        return True

    def run_validation(self) -> bool:
        """Run complete validation of all mechanisms."""
        print("🚀 Starting validation of self-driving audit mechanisms...")
        print("=" * 60)

        # Run all validations
        validations = [
            self.validate_github_action,
            self.validate_pre_commit_hook,
            self.validate_makefile_target,
            self.validate_readme_integration,
            self.validate_script_functionality,
        ]

        all_passed = True
        for validation in validations:
            try:
                if not validation():
                    all_passed = False
            except Exception as e:
                print(f"❌ Validation error: {e}")
                all_passed = False

        print("=" * 60)
        print("📊 Validation Results Summary:")
        print("=" * 60)

        passed = 0
        total = len(self.results)

        for test_name, success, message in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {test_name}: {message}")
            if success:
                passed += 1

        print("=" * 60)
        print(f"Overall: {passed}/{total} tests passed")

        if all_passed:
            print("🎉 All validations passed! Self-driving audit mechanisms are ready.")
        else:
            print("⚠️  Some validations failed. Please review the issues above.")

        return all_passed


def main():
    """Main entry point for validation."""
    validator = AuditMechanismValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
