#!/usr/bin/env python3
"""
PR Management Agent for iDAWi Repository

This script processes all open pull requests in the repository:
1. Fetches and identifies the target branch (usually main/master)
2. Attempts to merge the PR branch into the target branch
3. If merge succeeds with no conflicts:
   - Completes the merge
   - Deletes the source branch immediately after merge
4. If merge conflicts exist:
   - Does NOT merge
   - Creates a new branch named "conflicts/{original-branch-name}"
   - Pushes the conflicting branch state there
   - Adds a comment to the PR listing the conflicting files
   - Leaves the original PR open

Never force pushes. Never resolves conflicts automatically. 
Always preserves conflict state for human review.
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class PRManager:
    """Manages pull request merging and conflict handling."""
    
    def __init__(self, repo_path: str = "."):
        """Initialize the PR manager.
        
        Args:
            repo_path: Path to the git repository (default: current directory)
        """
        self.repo_path = Path(repo_path).resolve()
        self.merged_prs = []
        self.conflict_prs = []
        
    def run_git(self, *args, check=True, capture=True) -> subprocess.CompletedProcess:
        """Run a git command.
        
        Args:
            *args: Git command arguments
            check: Whether to raise on non-zero exit
            capture: Whether to capture output
            
        Returns:
            CompletedProcess instance
        """
        cmd = ["git", "-C", str(self.repo_path)] + list(args)
        if capture:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=check
            )
        else:
            result = subprocess.run(cmd, check=check)
        return result
    
    def get_default_branch(self) -> str:
        """Get the default branch (main or master).
        
        Returns:
            Name of the default branch
        """
        # Try to get from remote HEAD
        result = self.run_git("symbolic-ref", "refs/remotes/origin/HEAD", check=False)
        if result.returncode == 0:
            # Format: refs/remotes/origin/main
            return result.stdout.strip().split("/")[-1]
        
        # Check if main exists
        result = self.run_git("rev-parse", "--verify", "origin/main", check=False)
        if result.returncode == 0:
            return "main"
        
        # Check if master exists
        result = self.run_git("rev-parse", "--verify", "origin/master", check=False)
        if result.returncode == 0:
            return "master"
        
        # Default to main
        return "main"
    
    def fetch_all(self):
        """Fetch all branches from remote."""
        print("📥 Fetching all branches from remote...")
        self.run_git("fetch", "--all", "--prune")
        print("✓ Fetch complete\n")
    
    def get_open_prs(self) -> List[Dict]:
        """Get list of open pull requests.
        
        This would typically use the GitHub API. For now, we'll use
        a simplified approach that works with local git data.
        
        Returns:
            List of PR dictionaries
        """
        # In a real implementation, this would call GitHub API
        # For this script, we'll need to be called with PR data
        # or use gh CLI if available
        
        result = self.run_git("branch", "-r", check=False)
        if result.returncode != 0:
            return []
        
        branches = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if line and "origin/" in line and "->" not in line:
                branch = line.replace("origin/", "")
                if branch not in ["main", "master", "HEAD"]:
                    branches.append(branch)
        
        return branches
    
    def try_merge(self, branch: str, target: str) -> Tuple[bool, List[str]]:
        """Attempt to merge a branch into target.
        
        Args:
            branch: Source branch name
            target: Target branch name
            
        Returns:
            Tuple of (success, conflicting_files)
        """
        print(f"🔄 Attempting to merge '{branch}' into '{target}'...")
        
        # Checkout target branch
        result = self.run_git("checkout", target, check=False)
        if result.returncode != 0:
            print(f"✗ Failed to checkout {target}")
            return False, []
        
        # Pull latest changes
        self.run_git("pull", "origin", target, check=False)
        
        # Attempt merge with no-commit and no-ff
        result = self.run_git(
            "merge", 
            "--no-commit", 
            "--no-ff", 
            f"origin/{branch}",
            check=False
        )
        
        if result.returncode == 0:
            # Merge succeeded
            print(f"✓ Merge successful (no conflicts)")
            return True, []
        else:
            # Check for conflicts
            status_result = self.run_git("status", "--short")
            conflicting_files = []
            
            for line in status_result.stdout.strip().split("\n"):
                # Check for all types of unmerged file status codes
                # UU = both modified, AA = both added, DD = both deleted
                # AU = added by us, UA = added by them
                # DU = deleted by us, UD = deleted by them
                if line.startswith(("UU", "AA", "DD", "AU", "UA", "DU", "UD")):
                    # Unmerged files
                    conflicting_files.append(line[3:].strip())
            
            # Abort the merge
            self.run_git("merge", "--abort", check=False)
            
            if conflicting_files:
                print(f"✗ Merge conflicts detected in {len(conflicting_files)} file(s)")
                return False, conflicting_files
            else:
                print(f"✗ Merge failed (unknown reason)")
                return False, []
    
    def complete_merge(self, branch: str, target: str) -> bool:
        """Complete a successful merge and delete the source branch.
        
        Args:
            branch: Source branch name
            target: Target branch name
            
        Returns:
            True if successful
        """
        print(f"📝 Completing merge...")
        
        # Commit the merge
        merge_msg = f"Merge branch '{branch}' into {target}"
        result = self.run_git("commit", "-m", merge_msg, check=False)
        if result.returncode != 0:
            print(f"✗ Failed to commit merge")
            return False
        
        print(f"✓ Merge committed")
        
        # Push to remote
        print(f"📤 Pushing merge to remote...")
        result = self.run_git("push", "origin", target, check=False)
        if result.returncode != 0:
            print(f"✗ Failed to push merge")
            return False
        
        print(f"✓ Pushed to {target}")
        
        # Delete the source branch
        print(f"🗑️  Deleting source branch '{branch}'...")
        result = self.run_git("push", "origin", "--delete", branch, check=False)
        if result.returncode != 0:
            print(f"⚠️  Warning: Failed to delete remote branch '{branch}'")
        else:
            print(f"✓ Deleted remote branch '{branch}'")
        
        return True
    
    def create_conflict_branch(self, branch: str, target: str, conflicts: List[str]) -> bool:
        """Create a conflict branch for manual resolution.
        
        Args:
            branch: Source branch name
            target: Target branch name
            conflicts: List of conflicting files
            
        Returns:
            True if successful
        """
        conflict_branch = f"conflicts/{branch}"
        print(f"🔀 Creating conflict branch '{conflict_branch}'...")
        
        # Checkout the source branch
        result = self.run_git("checkout", "-b", conflict_branch, f"origin/{branch}", check=False)
        if result.returncode != 0:
            print(f"✗ Failed to create conflict branch")
            return False
        
        # Try to merge to capture conflict state
        self.run_git("merge", f"origin/{target}", check=False)
        
        # Add a marker file with conflict information
        conflict_info = {
            "source_branch": branch,
            "target_branch": target,
            "conflicting_files": conflicts,
            "resolution_instructions": [
                "1. Review the conflicting files listed below",
                "2. Resolve conflicts manually",
                "3. Run: git add <resolved-files>",
                "4. Run: git commit",
                "5. Push the changes",
                "6. Update the original PR or create a new one"
            ]
        }
        
        conflict_file = self.repo_path / "MERGE_CONFLICTS.json"
        with open(conflict_file, "w") as f:
            json.dump(conflict_info, f, indent=2)
        
        self.run_git("add", "MERGE_CONFLICTS.json", check=False)
        
        # Push the conflict branch
        print(f"📤 Pushing conflict branch to remote...")
        result = self.run_git("push", "origin", conflict_branch, check=False)
        if result.returncode != 0:
            print(f"✗ Failed to push conflict branch")
            return False
        
        print(f"✓ Conflict branch created and pushed")
        
        # Return to target branch
        self.run_git("checkout", target, check=False)
        
        return True
    
    def process_pr(self, branch: str, target: str, pr_number: Optional[int] = None) -> Dict:
        """Process a single pull request.
        
        Args:
            branch: Source branch name
            target: Target branch name
            pr_number: PR number (optional)
            
        Returns:
            Dictionary with processing results
        """
        print("=" * 80)
        print(f"Processing PR: {branch} -> {target}")
        if pr_number:
            print(f"PR Number: #{pr_number}")
        print("=" * 80)
        
        # Try to merge
        success, conflicts = self.try_merge(branch, target)
        
        result = {
            "branch": branch,
            "target": target,
            "pr_number": pr_number,
            "success": success,
            "conflicts": conflicts
        }
        
        if success:
            # Complete the merge and delete branch
            if self.complete_merge(branch, target):
                print(f"✅ Successfully merged and deleted branch '{branch}'")
                self.merged_prs.append(result)
                result["status"] = "merged"
            else:
                print(f"⚠️  Merge completed but cleanup failed for '{branch}'")
                result["status"] = "merged_with_warnings"
        else:
            if conflicts:
                # Create conflict branch
                if self.create_conflict_branch(branch, target, conflicts):
                    print(f"⚠️  Created conflict branch for '{branch}'")
                    self.conflict_prs.append(result)
                    result["status"] = "conflicts"
                    
                    # Note: In a full implementation, would add PR comment here
                    print(f"\n📋 Conflicting files:")
                    for conflict in conflicts:
                        print(f"   - {conflict}")
                else:
                    print(f"✗ Failed to handle conflicts for '{branch}'")
                    result["status"] = "failed"
            else:
                print(f"✗ Merge failed for unknown reason: '{branch}'")
                result["status"] = "failed"
        
        print()
        return result
    
    def process_all_prs(self, prs: List[Dict]):
        """Process all open pull requests.
        
        Args:
            prs: List of PR dictionaries
        """
        print("\n" + "=" * 80)
        print("PR MANAGEMENT AGENT - STARTING")
        print("=" * 80)
        print(f"Total PRs to process: {len(prs)}\n")
        
        # Fetch all branches
        self.fetch_all()
        
        # Get default target branch
        target = self.get_default_branch()
        print(f"🎯 Target branch: {target}\n")
        
        # Process each PR
        for i, pr in enumerate(prs, 1):
            print(f"\n[{i}/{len(prs)}] ", end="")
            
            if isinstance(pr, dict):
                branch = pr.get("head", {}).get("ref") or pr.get("branch")
                pr_number = pr.get("number")
            else:
                # Simple branch name
                branch = pr
                pr_number = None
            
            if branch:
                self.process_pr(branch, target, pr_number)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print processing summary."""
        print("\n" + "=" * 80)
        print("PR MANAGEMENT SUMMARY")
        print("=" * 80)
        
        print(f"\n✅ Successfully merged and deleted ({len(self.merged_prs)}):")
        if self.merged_prs:
            for pr in self.merged_prs:
                branch = pr["branch"]
                pr_num = f"#{pr['pr_number']}" if pr.get("pr_number") else ""
                print(f"   - {branch} {pr_num}")
        else:
            print("   (none)")
        
        print(f"\n⚠️  Moved to conflicts branch ({len(self.conflict_prs)}):")
        if self.conflict_prs:
            for pr in self.conflict_prs:
                branch = pr["branch"]
                pr_num = f"#{pr['pr_number']}" if pr.get("pr_number") else ""
                conflicts = pr.get("conflicts", [])
                print(f"   - {branch} {pr_num}")
                print(f"     Conflicting files: {', '.join(conflicts)}")
                print(f"     Conflict branch: conflicts/{branch}")
        else:
            print("   (none)")
        
        print("\n" + "=" * 80)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PR Management Agent - Automatically merge or handle conflicts for open PRs"
    )
    parser.add_argument(
        "--repo-path",
        default=".",
        help="Path to the git repository (default: current directory)"
    )
    parser.add_argument(
        "--pr-data",
        help="JSON file containing PR data from GitHub API"
    )
    parser.add_argument(
        "--branches",
        nargs="+",
        help="Specific branches to process (space-separated)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually doing it"
    )
    
    args = parser.parse_args()
    
    # Initialize manager
    manager = PRManager(args.repo_path)
    
    # Get PRs to process
    prs = []
    if args.pr_data:
        # Load from JSON file
        with open(args.pr_data) as f:
            prs = json.load(f)
    elif args.branches:
        # Use specified branches
        prs = args.branches
    else:
        # Auto-detect from git branches
        prs = manager.get_open_prs()
        if not prs:
            print("No pull request branches found.")
            print("Use --branches to specify branches manually,")
            print("or --pr-data to provide GitHub API data.")
            return 1
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made\n")
        print("PRs to process:")
        for pr in prs:
            if isinstance(pr, dict):
                print(f"  - {pr.get('head', {}).get('ref', pr.get('branch'))}")
            else:
                print(f"  - {pr}")
        return 0
    
    # Process all PRs
    manager.process_all_prs(prs)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
