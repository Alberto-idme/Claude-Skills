#!/bin/bash
#
# AI Development Course - Preflight Check
#
# This script verifies all dependencies are installed before
# proceeding with the course setup.
#
# Exit codes:
#   0 = All checks passed
#   1 = One or more checks failed
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

ERRORS=0

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AI Development Course - Preflight Check${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Function to check if a command exists
check_command() {
    local cmd=$1
    local name=$2
    local install_hint=$3

    if command -v "$cmd" &> /dev/null; then
        local version=$($cmd --version 2>&1 | head -1)
        echo -e "${GREEN}✓${NC} $name found: $version"
        return 0
    else
        echo -e "${RED}✗${NC} $name NOT FOUND"
        echo ""
        echo -e "  ${YELLOW}How to install:${NC}"
        echo -e "  $install_hint"
        echo ""
        ERRORS=$((ERRORS + 1))
        return 1
    fi
}

# Function to check Node.js version
check_node_version() {
    if command -v node &> /dev/null; then
        local version=$(node --version | sed 's/v//')
        local major=$(echo "$version" | cut -d. -f1)
        if [ "$major" -ge 18 ]; then
            echo -e "${GREEN}✓${NC} Node.js version OK: v$version (need v18+)"
            return 0
        else
            echo -e "${RED}✗${NC} Node.js version TOO OLD: v$version (need v18+)"
            echo ""
            echo -e "  ${YELLOW}How to upgrade:${NC}"
            echo -e "  brew upgrade node"
            echo -e "  # or visit https://nodejs.org/"
            echo ""
            ERRORS=$((ERRORS + 1))
            return 1
        fi
    fi
    return 1
}

# Function to check Python 3.13 availability via uvx
check_python_313() {
    if command -v uvx &> /dev/null; then
        # Try to check if Python 3.13 is available
        if uvx --python 3.13 python --version &> /dev/null 2>&1; then
            echo -e "${GREEN}✓${NC} Python 3.13 available via uvx"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} Python 3.13 not yet installed (uvx will install it automatically)"
            echo -e "  ChromaDB MCP server will install Python 3.13 on first use."
            return 0
        fi
    fi
    return 1
}

echo -e "${BLUE}Checking Claude Code...${NC}"
echo ""

# Check if Claude Code is already installed
if command -v claude &> /dev/null; then
    local_version=$(claude --version 2>&1 | head -1)
    echo -e "${GREEN}✓${NC} Claude Code already installed: $local_version"
    echo ""
    echo -e "  ${YELLOW}Important:${NC} Run ./backup-claude-config.sh to backup your"
    echo -e "  existing configuration before installing course plugins."
    echo ""
    CLAUDE_INSTALLED=true
else
    echo -e "${YELLOW}⚠${NC} Claude Code not yet installed"
    echo ""
    echo -e "  ${YELLOW}How to install:${NC}"
    echo -e "  Visit https://claude.ai/code and follow the instructions."
    echo -e "  Then re-run this preflight check."
    echo ""
    CLAUDE_INSTALLED=false
fi

echo -e "${BLUE}Checking other dependencies...${NC}"
echo ""

# 1. Check Homebrew (macOS) or apt (Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    check_command "brew" "Homebrew" \
        '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt &> /dev/null; then
        echo -e "${GREEN}✓${NC} apt package manager found"
    elif command -v brew &> /dev/null; then
        echo -e "${GREEN}✓${NC} Homebrew (Linuxbrew) found"
    else
        echo -e "${YELLOW}⚠${NC} No supported package manager found (apt or brew)"
    fi
fi

# 2. Check Node.js
if ! check_command "node" "Node.js" \
    "brew install node\n  # or visit https://nodejs.org/"; then
    :
else
    check_node_version
fi

# 3. Check npx
check_command "npx" "npx" \
    "Comes with Node.js. Reinstall Node.js if missing."

# 4. Check uv/uvx (needed for ChromaDB)
check_command "uvx" "uvx (uv package manager)" \
    'curl -LsSf https://astral.sh/uv/install.sh | sh\n  # Then restart your terminal'

# 5. Check Python 3.13 availability
check_python_313

# 6. Check that required directories can be created
echo ""
echo -e "${BLUE}Checking directory access...${NC}"
echo ""

CLAUDE_DIR="$HOME/.claude"
if [ -d "$CLAUDE_DIR" ]; then
    if [ -w "$CLAUDE_DIR" ]; then
        echo -e "${GREEN}✓${NC} ~/.claude directory exists and is writable"
    else
        echo -e "${RED}✗${NC} ~/.claude directory exists but is NOT writable"
        echo ""
        echo -e "  ${YELLOW}How to fix:${NC}"
        echo -e "  chmod u+w ~/.claude"
        echo ""
        ERRORS=$((ERRORS + 1))
    fi
else
    # Try to create it
    if mkdir -p "$CLAUDE_DIR" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} ~/.claude directory created successfully"
    else
        echo -e "${RED}✗${NC} Cannot create ~/.claude directory"
        echo ""
        echo -e "  ${YELLOW}How to fix:${NC}"
        echo -e "  mkdir -p ~/.claude"
        echo -e "  # Check permissions on your home directory"
        echo ""
        ERRORS=$((ERRORS + 1))
    fi
fi

# Summary
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}  ✓ All preflight checks passed!${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    if [ "$CLAUDE_INSTALLED" = true ]; then
        echo "Claude Code is installed. Next steps:"
        echo "  1. Run ./backup-claude-config.sh (if you haven't already)"
        echo "  2. Start Claude Code: claude"
        echo "  3. Install plugins (see PRE_COURSE_SETUP.md Step 5)"
    else
        echo "Next steps:"
        echo "  1. Install Claude Code from https://claude.ai/code"
        echo "  2. Re-run ./preflight.sh to verify"
        echo "  3. Then continue with PRE_COURSE_SETUP.md"
    fi
    echo ""
    exit 0
else
    echo -e "${RED}  ✗ $ERRORS check(s) failed${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Please fix the issues above before proceeding.${NC}"
    echo ""
    echo "After fixing, you can re-run this check with:"
    echo "  ./preflight.sh"
    echo ""
    exit 1
fi
