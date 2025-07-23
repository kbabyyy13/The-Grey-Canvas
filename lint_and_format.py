#!/usr/bin/env python3
"""
Automated linting and formatting script for The Grey Canvas
Run this before committing code changes
"""

import os
import subprocess
import sys


def run_command(command, description):
    """Run a command and return success status"""
    print(f"\n🔍 {description}...")

    # Whitelist of allowed commands for security
    allowed_commands = {
        "black .": ["black", "."],
        "isort .": ["isort", "."],
        "black --check --diff .": ["black", "--check", "--diff", "."],
        "isort --check-only --diff .": ["isort", "--check-only", "--diff", "."],
        "flake8 .": ["flake8", "."],
        "mypy app.py models.py routes.py forms.py --ignore-missing-imports": [
            "mypy",
            "app.py",
            "models.py",
            "routes.py",
            "forms.py",
            "--ignore-missing-imports",
        ],
    }

    if command not in allowed_commands:
        print(f"❌ Command not allowed: {command}")
        return False

    try:
        # Use pre-defined static command list
        cmd_list = allowed_commands[command]
        result = subprocess.run(cmd_list, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} passed")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(result.stderr)
            if result.stdout:
                print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Error running {description}: {e}")
        return False


def main():
    """Main function to run all code quality checks"""
    print("🤖 Starting automated code quality checks for The Grey Canvas")
    print("=" * 60)

    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)

    all_passed = True

    # Format code first
    print("\n📝 FORMATTING CODE")
    print("-" * 30)

    if not run_command("black .", "Black code formatting"):
        all_passed = False

    if not run_command("isort .", "Import sorting"):
        all_passed = False

    # Then run checks
    print("\n🔍 RUNNING CHECKS")
    print("-" * 30)

    if not run_command("black --check --diff .", "Black format check"):
        all_passed = False

    if not run_command("isort --check-only --diff .", "Import order check"):
        all_passed = False

    if not run_command("flake8 .", "Flake8 linting"):
        all_passed = False

    # Type checking (allow failures for now)
    print("\n🏷️  TYPE CHECKING")
    print("-" * 30)
    run_command(
        "mypy app.py models.py routes.py forms.py --ignore-missing-imports",
        "MyPy type checking",
    )

    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All code quality checks passed!")
        print("✅ Your code is ready for deployment")
    else:
        print("⚠️  Some checks failed. Please fix the issues above.")
        print("💡 Run 'python lint_and_format.py' again after fixing")

    print("=" * 60)
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
