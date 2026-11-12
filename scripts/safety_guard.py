#!/usr/bin/env python3
"""
scripts/safety_guard.py - Safety Gate & Automated Verification for code-unclutter
Handles test detection, execution, atomic commits, and automatic rollbacks on test failure.
Zero external dependencies.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def detect_test_runner():
    """Detects standard test runners present in the project repository."""
    cwd = Path.cwd()
    if (cwd / "package.json").exists():
        # Check if test script exists in package.json
        try:
            with open(cwd / "package.json") as f:
                if '"test"' in f.read():
                    return ["npm", "test"]
        except Exception:
            pass

    if (cwd / "pytest.ini").exists() or (cwd / "pyproject.toml").exists() or any(cwd.glob("tests")):
        return ["pytest"]

    if (cwd / "Cargo.toml").exists():
        return ["cargo", "test"]

    if (cwd / "go.mod").exists():
        return ["go", "test", "./..."]

    if (cwd / "Makefile").exists():
        return ["make", "test"]

    return None


def run_command(cmd, cwd=None):
    try:
        res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0, res.stdout + "\n" + res.stderr
    except Exception as e:
        return False, str(e)


def snapshot():
    """Creates a temporary stash or git commit tag to mark baseline state."""
    ok, diff = run_command(["git", "diff", "HEAD"])
    return diff


def verify_and_commit(message, custom_test_cmd=None, target_files=None):
    test_cmd = custom_test_cmd.split() if custom_test_cmd else detect_test_runner()

    if not test_cmd:
        print("[WARN] No test suite detected. Skipping automated regression testing (Phase 0 Warning).")
        return True

    print(f"[TEST] Running test suite: {' '.join(test_cmd)} ...")
    passed, output = run_command(test_cmd)

    if passed:
        print("[OK] Tests passed successfully!")
        if target_files:
            run_command(["git", "add"] + target_files)
            run_command(["git", "commit", "-m", message])
            print(f"[COMMIT] Created atomic commit: {message}")
        return True
    else:
        print("[NG] Tests failed! Triggering automatic safety rollback...")
        print("--- Failure Output Preview ---")
        print("\n".join(output.strip().splitlines()[-10:]))
        print("-------------------------------")

        # Rollback target files
        if target_files:
            for f in target_files:
                run_command(["git", "checkout", "--", f])
            print(f"[REVERT] Reverted modified files: {target_files}")
        else:
            run_command(["git", "checkout", "--", "."])
            print("[REVERT] Reverted all unstaged changes.")

        return False


def main():
    parser = argparse.ArgumentParser(description="Safety Guard for code-unclutter")
    subparsers = parser.add_subparsers(dest="action")

    verify_p = subparsers.add_parser("verify")
    verify_p.add_argument("--test-cmd", help="Custom test command to run")
    verify_p.add_argument("--message", default="refactor(code-unclutter): safe atomic improvement", help="Commit message on success")
    verify_p.add_argument("--files", nargs="*", help="Specific files to commit or rollback")

    args = parser.parse_args()

    if args.action == "verify":
        success = verify_and_commit(args.message, custom_test_cmd=args.test_cmd, target_files=args.files)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
