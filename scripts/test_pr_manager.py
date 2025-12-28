#!/usr/bin/env python3
"""
Integration tests for PR management scripts.

These tests validate the core functionality of the PR manager without
actually making changes to the repository.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from pr_manager import PRManager


def test_initialization():
    """Test PR manager initialization."""
    print("Testing initialization...")
    
    manager = PRManager()
    assert manager.repo_path is not None
    assert isinstance(manager.merged_prs, list)
    assert isinstance(manager.conflict_prs, list)
    
    print("✓ Initialization test passed")


def test_get_default_branch():
    """Test getting default branch."""
    print("Testing default branch detection...")
    
    manager = PRManager()
    default = manager.get_default_branch()
    assert default in ["main", "master"], f"Expected main or master, got {default}"
    
    print(f"✓ Default branch test passed (found: {default})")


def test_git_command():
    """Test git command execution."""
    print("Testing git command execution...")
    
    manager = PRManager()
    result = manager.run_git("status", "--short")
    assert result.returncode == 0, "Git status command failed"
    
    print("✓ Git command test passed")


def test_dry_run():
    """Test dry run functionality."""
    print("Testing dry run functionality...")
    
    # Create test script in temp directory
    test_script = Path(__file__).parent.parent / "scripts" / "pr_manager.py"
    assert test_script.exists(), "pr_manager.py not found"
    
    # Run with dry-run flag
    result = subprocess.run(
        [sys.executable, str(test_script), "--dry-run"],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"Dry run failed: {result.stderr}"
    assert "DRY RUN MODE" in result.stdout, "Dry run mode not detected"
    
    print("✓ Dry run test passed")


def test_help_output():
    """Test help output."""
    print("Testing help output...")
    
    scripts = [
        Path(__file__).parent.parent / "scripts" / "pr_manager.py",
        Path(__file__).parent.parent / "scripts" / "manage_prs.py"
    ]
    
    for script in scripts:
        result = subprocess.run(
            [sys.executable, str(script), "--help"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"Help failed for {script.name}"
        assert "usage:" in result.stdout.lower(), f"No usage info in {script.name}"
    
    print("✓ Help output test passed")


def test_branch_detection():
    """Test branch detection."""
    print("Testing branch detection...")
    
    manager = PRManager()
    branches = manager.get_open_prs()
    
    # Should return a list (may be empty or contain branches)
    assert isinstance(branches, list), "Branch detection should return a list"
    
    print(f"✓ Branch detection test passed (found {len(branches)} branches)")


def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("PR MANAGEMENT INTEGRATION TESTS")
    print("=" * 70)
    print()
    
    tests = [
        test_initialization,
        test_get_default_branch,
        test_git_command,
        test_dry_run,
        test_help_output,
        test_branch_detection,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} ERROR: {e}")
            failed += 1
        print()
    
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
