#!/usr/bin/env bash
#
# iDAWi Repository Import Script
# Usage: ./import-repos.sh
#
# This script imports files from multiple source repositories into iDAWi:
# - sburdges-eng/penta-core (default branch)
# - sburdges-eng/DAiW-Music-Brain (default branch)
# - sburdges-eng/iDAW (default branch)
#
# Additionally, branches matching keywords (voice, synth, synthesizer,
# parrot, parrot-mode, ui, frontend) are imported into imports/<repo>/<branch>/
#
# Conflict handling:
# - Identical files are skipped
# - Conflicting files are copied with .imported-N suffix
#

set -euo pipefail

# Configuration - edit if needed
TARGET_REPO="https://github.com/sburdges-eng/iDAWi.git"
TARGET_DIR="iDAWi-import-work"
TARGET_REPO_SHORT="sburdges-eng/iDAWi"
SOURCE_REPOS=(
  "https://github.com/sburdges-eng/penta-core.git"
  "https://github.com/sburdges-eng/DAiW-Music-Brain.git"
  "https://github.com/sburdges-eng/iDAW.git"
)
KEYWORDS_REGEX="voice|synth|synthesizer|parrot|parrot-mode|ui|frontend"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    local color=$1
    local msg=$2
    echo -e "${color}${msg}${NC}"
}

print_step() {
    print_msg "$BLUE" "===> $1"
}

print_success() {
    print_msg "$GREEN" "[OK] $1"
}

print_warning() {
    print_msg "$YELLOW" "[WARN] $1"
}

print_error() {
    print_msg "$RED" "[ERROR] $1"
}

# Generate timestamp for unique branch name
TS=$(date +%s)
IMPORT_BRANCH="import/penta-daiw-idaw-${TS}"
WORKDIR="$(pwd)/${TARGET_DIR}"
LOGDIR="${WORKDIR}/import-logs"
PR_BODY_FILE="${WORKDIR}/import-pr-body.md"

# Setup working directory
print_step "Setting up working directory..."
mkdir -p "${WORKDIR}"
rm -rf "${WORKDIR:?}/"*
mkdir -p "${LOGDIR}"
print_success "Working in ${WORKDIR}"

# Clone target repo
print_step "Cloning target repo ${TARGET_REPO}..."
git clone --depth 1 "${TARGET_REPO}" "${WORKDIR}/target"
cd "${WORKDIR}/target"
git checkout -b "${IMPORT_BRANCH}"
print_success "Created branch ${IMPORT_BRANCH}"

# Arrays to record changes
ADDED_LIST="${LOGDIR}/added.txt"
SKIPPED_LIST="${LOGDIR}/skipped.txt"
CONFLICTS_LIST="${LOGDIR}/conflicts.txt"
: > "${ADDED_LIST}"
: > "${SKIPPED_LIST}"
: > "${CONFLICTS_LIST}"

# Function to copy files with conflict handling
copy_with_conflict_handling() {
  local srcroot="$1"   # e.g. /tmp/src-repo
  local srcpath="$2"   # path relative to srcroot (usually '.')
  local destroot="$3"  # path in target repo to copy into (relative to target root)

  # Find all files (not .git)
  (cd "${srcroot}/${srcpath}" && \
    find . -type f ! -path './.git/*' -print0) | \
  while IFS= read -r -d '' f; do
    srcfile="${srcroot}/${srcpath}/${f#./}"
    # normalize dest path
    destpath="${WORKDIR}/target/${destroot}/${f#./}"
    destdir="$(dirname "${destpath}")"
    mkdir -p "${destdir}"
    if [ ! -f "${destpath}" ]; then
      cp --preserve=mode,timestamps -- "${srcfile}" "${destpath}"
      echo "${destpath} | ${srcfile}" >> "${ADDED_LIST}"
    else
      # compare content
      if cmp -s "${srcfile}" "${destpath}"; then
        echo "SKIP identical: ${destpath}" >> "${SKIPPED_LIST}"
        continue
      fi
      # find a new name with .imported-N before extension
      base="$(basename "${destpath}")"
      dir="$(dirname "${destpath}")"
      ext=""
      name="${base}"
      if [[ "${base}" == *.* ]]; then
        ext=".${base##*.}"
        name="${base%.*}"
      fi
      n=1
      newpath="${dir}/${name}.imported-${n}${ext}"
      while [ -e "${newpath}" ]; do
        n=$((n+1))
        newpath="${dir}/${name}.imported-${n}${ext}"
      done
      cp --preserve=mode,timestamps -- "${srcfile}" "${newpath}"
      echo "CONFLICT: existing ${destpath} -> imported as ${newpath}" >> "${CONFLICTS_LIST}"
    fi
  done
}

# Process each source repo
for src in "${SOURCE_REPOS[@]}"; do
  print_step "Processing source: ${src}"
  srname="$(basename -s .git "${src}")"
  tmp_src_dir="${WORKDIR}/sources/${srname}"
  git clone --quiet "${src}" "${tmp_src_dir}"
  cd "${tmp_src_dir}"

  # Determine default branch name (fallback to 'main'/'master' if not discovered)
  DEFAULT_BRANCH="$(git symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null || true)"
  if [ -n "${DEFAULT_BRANCH}" ]; then
    DEFAULT_BRANCH="${DEFAULT_BRANCH#refs/remotes/origin/}"
  else
    # try common defaults
    if git show-ref --verify --quiet refs/heads/main; then
      DEFAULT_BRANCH="main"
    elif git show-ref --verify --quiet refs/heads/master; then
      DEFAULT_BRANCH="master"
    else
      DEFAULT_BRANCH="$(git branch --format='%(refname:short)' | head -n1)"
    fi
  fi
  print_success "Default branch for ${srname} -> ${DEFAULT_BRANCH}"

  # 1) Import default branch files into repository root (with conflict handling)
  git checkout --quiet "${DEFAULT_BRANCH}"
  print_step "Copying default branch (${DEFAULT_BRANCH}) files for ${srname}..."
  copy_with_conflict_handling "${tmp_src_dir}" "." "."

  # 2) Find branches matching keywords and import them into imports/<repo>/<branch>/
  print_step "Searching for branches in ${srname} matching keywords..."
  git fetch --all --prune --quiet
  branches_matching=$(git for-each-ref --format='%(refname:short)' refs/remotes/origin | sed 's#^origin/##' | grep -Ei "${KEYWORDS_REGEX}" || true)
  if [ -n "${branches_matching}" ]; then
    while IFS= read -r branch; do
      [ -z "${branch}" ] && continue
      print_msg "$BLUE" "Importing branch ${branch} from ${srname} into imports/${srname}/${branch}/"
      git checkout --quiet "origin/${branch}" || git checkout --quiet "${branch}" || true
      # copy into imports/<repo>/<branch>
      destroot="imports/${srname}/${branch}"
      copy_with_conflict_handling "${tmp_src_dir}" "." "${destroot}"
    done <<< "${branches_matching}"
  else
    print_warning "No matching branches found in ${srname}."
  fi

  # Return to target dir
  cd "${WORKDIR}/target"
done

# Stage everything and create commits (group commits per source for traceability)
print_step "Staging and committing changes..."
git add -A
if git diff --staged --quiet; then
  print_warning "No changes to commit."
else
  # Commit message summarizing sources
  COMMIT_MSG="Import files from sburdges-eng/penta-core, sburdges-eng/DAiW-Music-Brain, sburdges-eng/iDAW (default branches + matching voice/parrot/ui branches)"
  git commit -m "${COMMIT_MSG}"
  print_success "Committed changes on branch ${IMPORT_BRANCH}."
fi

# Push branch
print_step "Pushing branch to origin..."
git push origin "${IMPORT_BRANCH}"

COMPARE_URL="https://github.com/${TARGET_REPO_SHORT}/compare/${IMPORT_BRANCH}?expand=1"
print_success "Branch pushed."

# Generate PR body markdown
cat > "${PR_BODY_FILE}" <<EOF
# Import files from sburdges-eng/penta-core, sburdges-eng/DAiW-Music-Brain, sburdges-eng/iDAW

This PR was generated by an automated import script.

## Imported sources
- sburdges-eng/penta-core (default branch)
- sburdges-eng/DAiW-Music-Brain (default branch)
- sburdges-eng/iDAW (default branch)

Also imported any branches whose names matched: \`${KEYWORDS_REGEX}\`

## Added files
\`\`\`
$(sed 's/^/ - /;' "${ADDED_LIST}" | sed '/^ - $/d' || echo "None")
\`\`\`

## Skipped identical files
\`\`\`
$(sed 's/^/ - /;' "${SKIPPED_LIST}" | sed '/^ - $/d' || echo "None")
\`\`\`

## Conflicts (kept existing file, added imported copy)
\`\`\`
$(sed 's/^/ - /;' "${CONFLICTS_LIST}" | sed '/^ - $/d' || echo "None")
\`\`\`

## Notes
- Files from non-default branches were placed under \`imports/<repo>/<branch>/\` to avoid overwriting.
- Identical files were skipped to avoid redundant commits.
- Conflicting files were copied alongside with a \`.imported-N\` suffix.
- Please review binary files and large assets manually.
- Default behavior: original git history is not preserved; files are copied.
EOF

print_success "PR body generated at: ${PR_BODY_FILE}"
echo ""
print_msg "$GREEN" "=========================================="
print_msg "$GREEN" "  Import Complete!"
print_msg "$GREEN" "=========================================="
echo ""
echo "Next steps:"
echo "1) Review the branch locally under ${WORKDIR}/target"
echo "2) Open the PR in the web UI: ${COMPARE_URL}"
echo "   or use your preferred authenticated GitHub command-line tool to open a PR"
echo "   and use the file ${PR_BODY_FILE} as the PR body."
echo "3) After PR review, you can merge via the web UI."
echo ""
print_success "Done."
