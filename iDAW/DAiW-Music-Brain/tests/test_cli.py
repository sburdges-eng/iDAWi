"""Tests for CLI tool."""

import pytest
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_cli_exists():
    """Test CLI tool is executable."""
    cli_path = Path(__file__).parent.parent / "bin" / "daiw-logic"
    assert cli_path.exists()
    assert cli_path.stat().st_mode & 0o111  # Executable


def test_cli_help():
    """Test CLI help command."""
    result = subprocess.run(
        ["python", "bin/daiw-logic", "--help"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0
    assert "DAiW Logic Pro" in result.stdout


def test_cli_analyze():
    """Test CLI analyze command."""
    result = subprocess.run(
        ["python", "bin/daiw-logic", "analyze", "bereaved heartbroken grief"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0
    assert "Detected Emotions" in result.stdout or "Primary Emotion" in result.stdout


def test_cli_generate():
    """Test CLI generate command."""
    result = subprocess.run(
        ["python", "bin/daiw-logic", "generate", "grief", "-o", "test_cli_output"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0
    assert "Created" in result.stdout

    # Cleanup
    output_file = Path(__file__).parent.parent / "test_cli_output_automation.json"
    if output_file.exists():
        output_file.unlink()


def test_cli_list_emotions():
    """Test CLI list-emotions command."""
    result = subprocess.run(
        ["python", "bin/daiw-logic", "list-emotions"],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).parent.parent)
    )
    assert result.returncode == 0
    assert "AVAILABLE EMOTIONS" in result.stdout
    assert "SAD" in result.stdout.upper()
    assert "JOY" in result.stdout.upper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
