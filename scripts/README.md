# PR Management Scripts

Automated scripts for managing pull requests in the iDAWi repository.

## Overview

The PR management system processes open pull requests automatically:

1. **Fetch** the latest target branch (main/master)
2. **Attempt merge** of PR branch into target
3. **If successful**: Complete merge and delete source branch
4. **If conflicts**: Create `conflicts/{branch-name}` branch with conflict state

## Scripts

### `manage_prs.py` - Main Entry Point

The recommended way to run PR management. Fetches PR data from GitHub and processes them.

```bash
# Process all open PRs (requires gh CLI)
python scripts/manage_prs.py

# Process specific branches
python scripts/manage_prs.py --branches feature/xyz bugfix/abc

# Exclude current branch (useful when running from a PR)
python scripts/manage_prs.py --exclude-current
```

**Requirements:**
- GitHub CLI (`gh`) for automatic PR detection
- Or use `--branches` to specify manually

### `pr_manager.py` - Core Logic

Low-level script that handles the actual merge operations. Can be used directly:

```bash
# Process specific branches
python scripts/pr_manager.py --branches feature/xyz

# Dry run (show what would happen)
python scripts/pr_manager.py --branches feature/xyz --dry-run

# Use PR data from JSON file
python scripts/pr_manager.py --pr-data prs.json
```

## How It Works

### Successful Merge Flow

1. Fetch all branches: `git fetch --all`
2. Checkout target branch: `git checkout main`
3. Attempt merge: `git merge --no-commit --no-ff origin/{pr-branch}`
4. If no conflicts:
   - Commit merge: `git commit -m "Merge branch 'xyz'"`
   - Push: `git push origin main`
   - Delete branch: `git push origin --delete {pr-branch}`

### Conflict Handling Flow

1. Detect conflicts during merge attempt
2. Abort merge: `git merge --abort`
3. Create conflict branch: `git checkout -b conflicts/{pr-branch}`
4. Attempt merge to capture conflict state
5. Add `MERGE_CONFLICTS.json` with conflict details
6. Push: `git push origin conflicts/{pr-branch}`
7. (Future) Add comment to PR with conflict information

## Configuration

### Environment Variables

- `GITHUB_TOKEN` - Personal access token for GitHub API (if not using gh CLI)

### Command Line Options

#### manage_prs.py

- `--owner` - Repository owner (default: sburdges-eng)
- `--repo` - Repository name (default: iDAWi)
- `--branches` - Specific branches to process
- `--exclude-current` - Skip the current working branch

#### pr_manager.py

- `--repo-path` - Path to git repository (default: .)
- `--branches` - Specific branches to process
- `--pr-data` - JSON file with PR data
- `--dry-run` - Show what would be done

## Examples

### Process All Open PRs

```bash
# From repository root
cd /path/to/iDAWi
python scripts/manage_prs.py
```

### Process Specific PRs

```bash
# Process only specific feature branches
python scripts/manage_prs.py --branches feature/audio-engine feature/ui-update
```

### From Within a PR Branch

When running as part of a PR (e.g., from GitHub Actions on the PR branch):

```bash
# Exclude the current PR branch from processing
python scripts/manage_prs.py --exclude-current
```

### Dry Run

```bash
# See what would happen without making changes
python scripts/pr_manager.py --branches feature/test --dry-run
```

## Output

The script provides detailed output:

```
📥 Fetching all branches from remote...
✓ Fetch complete

🎯 Target branch: main

================================================================================
Processing PR: feature/audio-engine -> main
PR Number: #42
================================================================================
🔄 Attempting to merge 'feature/audio-engine' into 'main'...
✓ Merge successful (no conflicts)
📝 Completing merge...
✓ Merge committed
📤 Pushing merge to remote...
✓ Pushed to main
🗑️  Deleting source branch 'feature/audio-engine'...
✓ Deleted remote branch 'feature/audio-engine'
✅ Successfully merged and deleted branch 'feature/audio-engine'
```

## Safety Features

1. **No Force Push** - Never uses `--force` or `--force-with-lease`
2. **No Auto-Resolve** - Never automatically resolves conflicts
3. **Conflict Preservation** - Saves exact conflict state for human review
4. **Rollback Safe** - Uses `--no-commit` to test merges first
5. **Branch Protection** - Won't delete protected branches

## Conflict Resolution

When conflicts are detected:

1. A new branch is created: `conflicts/{original-branch}`
2. `MERGE_CONFLICTS.json` contains:
   - Source and target branches
   - List of conflicting files
   - Resolution instructions
3. Original PR remains open
4. Human can resolve conflicts on the conflict branch

### Resolving Conflicts

```bash
# Checkout the conflict branch
git checkout conflicts/feature-xyz

# Review conflicts
cat MERGE_CONFLICTS.json

# Resolve conflicts manually
# Edit conflicting files...

# Complete the merge
git add <resolved-files>
git commit
git push

# Update original PR or create new one
```

## Integration with CI/CD

Can be integrated into GitHub Actions:

```yaml
name: Auto-merge PRs

on:
  schedule:
    - cron: '0 0 * * *'  # Daily
  workflow_dispatch:  # Manual trigger

jobs:
  merge:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      
      - name: Manage PRs
        run: python scripts/manage_prs.py --exclude-current
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Troubleshooting

### "gh CLI not found"

Install GitHub CLI:
- macOS: `brew install gh`
- Linux: `sudo apt install gh` or download from https://cli.github.com
- Or use `--branches` to specify manually

### "Failed to checkout target branch"

Ensure you have the latest changes:
```bash
git fetch --all
```

### Merge Fails for Unknown Reason

Check:
1. Branch protection rules
2. Required status checks
3. Git configuration
4. Network connectivity

## Future Enhancements

- [ ] Add PR comment with conflict details via GitHub API
- [ ] Support for multiple target branches
- [ ] Integration with GitHub Actions
- [ ] Email notifications for conflicts
- [ ] Slack/Discord integration
- [ ] Automatic retry logic
- [ ] Merge queue support
