#!/bin/bash
# iDAW Quick Setup Script
# Usage: curl -sSL https://raw.githubusercontent.com/sburdges-eng/iDAWi/main/setup-idaw.sh | bash -s [full|dev|minimal]
#
# Options:
#   full    - Complete setup with all dependencies
#   dev     - Development setup (npm + pip)
#   minimal - Just create directory structure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default mode
MODE="${1:-full}"

echo -e "${BLUE}=========================================="
echo -e "  iDAW Quick Setup"
echo -e "  Mode: ${MODE}"
echo -e "==========================================${NC}"

# Change to script directory if running locally
if [ -d ".git" ]; then
    echo -e "${GREEN}Running in existing repository...${NC}"
    REPO_DIR="$(pwd)"
else
    # Clone if not already in repo
    echo -e "${YELLOW}Cloning iDAWi repository...${NC}"
    if ! git clone https://github.com/sburdges-eng/iDAWi.git; then
        echo -e "${RED}Failed to clone repository. Check your network connection.${NC}"
        exit 1
    fi
    cd iDAWi
    REPO_DIR="$(pwd)"
fi

echo -e "${BLUE}Creating directory structure...${NC}"

# Create config directories
mkdir -p .claude
mkdir -p .devcontainer
mkdir -p .github/workflows

# Create Tauri application directories
mkdir -p iDAW/iDAWi/src-tauri/src/audio
mkdir -p iDAW/iDAWi/src-tauri/src/commands
mkdir -p iDAW/iDAWi/src-tauri/src/python

# Create React/TypeScript directories
mkdir -p iDAW/iDAWi/src/components
mkdir -p iDAW/iDAWi/src/emotion
mkdir -p iDAW/iDAWi/src/hooks
mkdir -p iDAW/iDAWi/src/stores

# Create Python generator directory
mkdir -p python/idaw_generator

echo -e "${GREEN}Directory structure created!${NC}"

# Install dependencies based on mode
case "$MODE" in
    full)
        echo -e "${BLUE}Installing full dependencies...${NC}"
        
        # Check for npm
        if command -v npm &> /dev/null; then
            echo "Installing npm dependencies..."
            cd "${REPO_DIR}/iDAW/iDAWi"
            if ! npm install; then
                echo -e "${YELLOW}npm install failed. You may need to run it manually.${NC}"
            fi
            cd "${REPO_DIR}"
        else
            echo -e "${YELLOW}npm not found. Skipping npm dependencies.${NC}"
        fi
        
        # Check for pip
        if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
            echo "Installing Python dependencies..."
            if ! pip install numpy midiutil black mypy 2>&1 && ! pip3 install numpy midiutil black mypy 2>&1; then
                echo -e "${YELLOW}pip install failed. You may need to run it manually.${NC}"
            fi
        else
            echo -e "${YELLOW}pip not found. Skipping Python dependencies.${NC}"
        fi
        
        # Check for Rust/Cargo
        if command -v cargo &> /dev/null; then
            echo -e "${GREEN}Rust is installed. Tauri dev ready!${NC}"
        else
            echo -e "${YELLOW}Rust not found. Install from: https://rustup.rs${NC}"
        fi
        ;;
        
    dev)
        echo -e "${BLUE}Installing development dependencies...${NC}"
        
        if command -v npm &> /dev/null; then
            cd "${REPO_DIR}/iDAW/iDAWi"
            if ! npm install; then
                echo -e "${YELLOW}npm install failed${NC}"
            fi
            cd "${REPO_DIR}"
        fi
        
        if command -v pip &> /dev/null || command -v pip3 &> /dev/null; then
            if ! pip install numpy midiutil black mypy pytest 2>&1 && ! pip3 install numpy midiutil black mypy pytest 2>&1; then
                echo -e "${YELLOW}pip install failed${NC}"
            fi
        fi
        ;;
        
    minimal)
        echo -e "${YELLOW}Minimal setup - directories only${NC}"
        ;;
        
    *)
        echo -e "${RED}Unknown mode: ${MODE}${NC}"
        echo "Usage: setup-idaw.sh [full|dev|minimal]"
        exit 1
        ;;
esac

echo -e "${GREEN}=========================================="
echo -e "  Setup Complete!"
echo -e "==========================================${NC}"
echo ""
echo -e "Next steps:"
echo -e "  ${BLUE}cd ${REPO_DIR}/iDAW/iDAWi${NC}"
echo -e "  ${BLUE}npm run tauri dev${NC}  (start development)"
echo ""
echo -e "Documentation:"
echo -e "  ${BLUE}cat docs/AGENT_PROMPTS.md${NC}  (AI assistant prompts)"
echo ""
