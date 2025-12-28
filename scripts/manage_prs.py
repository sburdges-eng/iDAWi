#!/usr/bin/env python3
"""
Wrapper script for PR management that fetches PR data from GitHub.

This script uses the GitHub API to fetch open PRs and then processes them
using the PR manager.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Add parent directory to path to import pr_manager
sys.path.insert(0, str(Path(__file__).parent))
from pr_manager import PRManager


def get_github_prs(owner: str, repo: str):
    """Get open PRs using gh CLI.
    
    Args:
        owner: Repository owner
        repo: Repository name
        
    Returns:
        List of PR data dictionaries
    """
    try:
        # Try using gh CLI
        result = subprocess.run(
            ["gh", "pr", "list", "--json", "number,title,headRefName,baseRefName,state", 
             "--state", "open", "--repo", f"{owner}/{repo}"],
            capture_output=True,
            text=True,
            check=True
        )
        return json.loads(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  'gh' CLI not found or failed. Install with: brew install gh")
        print("   Or use --branches to specify branches manually")
        return []


def get_default_repo_info():
    """Get default repository owner and name from git remote.
    
    Returns:
        Tuple of (owner, repo) or (None, None) if not found
    """
    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            capture_output=True,
            text=True,
            check=True
        )
        url = result.stdout.strip()
        
        # Parse GitHub URL (supports both HTTPS and SSH formats)
        # https://github.com/owner/repo.git or git@github.com:owner/repo.git
        if "github.com" in url:
            # Remove .git suffix if present
            url = url.rstrip(".git")
            
            if url.startswith("git@"):
                # SSH format: git@github.com:owner/repo
                parts = url.split(":")[-1].split("/")
            else:
                # HTTPS format: https://github.com/owner/repo
                parts = url.split("github.com/")[-1].split("/")
            
            if len(parts) >= 2:
                return parts[0], parts[1]
    except subprocess.CalledProcessError:
        pass
    
    return None, None


def main():
    """Main entry point."""
    import argparse
    
    # Get default repo info from git remote
    default_owner, default_repo = get_default_repo_info()
    
    parser = argparse.ArgumentParser(
        description="Manage open PRs - merge or create conflict branches"
    )
    parser.add_argument(
        "--owner",
        default=default_owner or "sburdges-eng",
        help=f"GitHub repository owner (default: {default_owner or 'sburdges-eng'})"
    )
    parser.add_argument(
        "--repo",
        default=default_repo or "iDAWi",
        help=f"GitHub repository name (default: {default_repo or 'iDAWi'})"
    )
    parser.add_argument(
        "--branches",
        nargs="+",
        help="Specific branches to process (bypasses GitHub API)"
    )
    parser.add_argument(
        "--exclude-current",
        action="store_true",
        help="Exclude the current working branch"
    )
    
    args = parser.parse_args()
    
    # Get current branch to potentially exclude it
    current_branch = None
    if args.exclude_current:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            current_branch = result.stdout.strip()
            print(f"ℹ️  Current branch: {current_branch} (will be excluded)")
    
    # Get PRs
    if args.branches:
        # Use specified branches
        prs = []
        for branch in args.branches:
            if current_branch and branch == current_branch:
                print(f"⏭️  Skipping current branch: {branch}")
                continue
            prs.append({
                "headRefName": branch,
                "branch": branch
            })
    else:
        # Fetch from GitHub
        print(f"📡 Fetching open PRs from {args.owner}/{args.repo}...")
        gh_prs = get_github_prs(args.owner, args.repo)
        
        if not gh_prs:
            print("\n⚠️  No PRs found or GitHub API access failed.")
            print("   Use --branches to specify branches manually")
            return 1
        
        # Convert to expected format
        prs = []
        for pr in gh_prs:
            branch = pr.get("headRefName")
            if current_branch and branch == current_branch:
                print(f"⏭️  Skipping current PR branch: {branch} (PR #{pr.get('number')})")
                continue
            prs.append({
                "number": pr.get("number"),
                "title": pr.get("title"),
                "branch": branch,
                "head": {"ref": branch},
                "base": {"ref": pr.get("baseRefName", "main")}
            })
        
        print(f"✓ Found {len(prs)} open PR(s) to process\n")
    
    if not prs:
        print("ℹ️  No PRs to process.")
        return 0
    
    # Initialize and run manager
    manager = PRManager()
    
    # Process PRs
    manager.process_all_prs(prs)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
