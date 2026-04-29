#!/bin/bash
#
# AI Development Course - Diagnostic Script
#
# Collects environment, configuration, and setup information
# to help debug issues with Claude Code and course materials.
#
# Usage: ./diagnose.sh [--verbose]
#

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
NC='\033[0m' # No Color

VERBOSE=false
if [[ "$1" == "--verbose" || "$1" == "-v" ]]; then
    VERBOSE=true
fi

section() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
}

subsection() {
    echo -e "${CYAN}── $1 ──${NC}"
}

ok() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
}

info() {
    echo -e "${DIM}  $1${NC}"
}

# Header
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  AI Development Course - Diagnostic Report${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${DIM}  Generated: $(date)${NC}"
echo ""

#############################################
section "System Information"
#############################################

subsection "Operating System"
if [[ "$OSTYPE" == "darwin"* ]]; then
    ok "macOS detected"
    sw_vers 2>/dev/null | sed 's/^/  /'
    echo ""
    info "Architecture: $(uname -m)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    ok "Linux detected"
    if [ -f /etc/os-release ]; then
        grep -E "^(NAME|VERSION)=" /etc/os-release | sed 's/^/  /'
    fi
    info "Architecture: $(uname -m)"
else
    warn "Unknown OS: $OSTYPE"
fi
echo ""

subsection "Shell Environment"
echo "  SHELL: $SHELL"
echo "  Terminal: ${TERM:-not set}"
echo ""

subsection "User & Home"
echo "  USER: $USER"
echo "  HOME: $HOME"
if [ -w "$HOME" ]; then
    ok "Home directory is writable"
else
    fail "Home directory is NOT writable"
fi
echo ""

#############################################
section "Claude Code"
#############################################

subsection "Installation"
if command -v claude &> /dev/null; then
    CLAUDE_PATH=$(which claude)
    CLAUDE_VERSION=$(claude --version 2>&1 | head -1)
    ok "Claude Code installed"
    echo "  Path: $CLAUDE_PATH"
    echo "  Version: $CLAUDE_VERSION"
else
    fail "Claude Code NOT found in PATH"
    echo ""
    info "Install from: https://claude.ai/code"
fi
echo ""

subsection "Configuration Directory (~/.claude)"
CLAUDE_DIR="$HOME/.claude"
if [ -d "$CLAUDE_DIR" ]; then
    ok "~/.claude directory exists"

    # Permissions
    PERMS=$(ls -ld "$CLAUDE_DIR" | awk '{print $1}')
    echo "  Permissions: $PERMS"

    if [ -w "$CLAUDE_DIR" ]; then
        ok "Directory is writable"
    else
        fail "Directory is NOT writable"
    fi

    # Size
    SIZE=$(du -sh "$CLAUDE_DIR" 2>/dev/null | cut -f1)
    echo "  Size: $SIZE"

    # Contents summary
    echo ""
    echo "  Contents:"
    ls -la "$CLAUDE_DIR" 2>/dev/null | tail -n +2 | head -20 | sed 's/^/    /'

    FILE_COUNT=$(find "$CLAUDE_DIR" -type f 2>/dev/null | wc -l | tr -d ' ')
    DIR_COUNT=$(find "$CLAUDE_DIR" -type d 2>/dev/null | wc -l | tr -d ' ')
    echo ""
    info "$FILE_COUNT files, $DIR_COUNT directories"
else
    warn "~/.claude directory does not exist"
    info "Will be created when Claude Code first runs"
fi
echo ""

subsection "Global Config (~/.claude.json)"
if [ -f "$HOME/.claude.json" ]; then
    ok "~/.claude.json exists"
    SIZE=$(ls -lh "$HOME/.claude.json" | awk '{print $5}')
    echo "  Size: $SIZE"
    if $VERBOSE; then
        echo ""
        echo "  Contents:"
        cat "$HOME/.claude.json" 2>/dev/null | head -50 | sed 's/^/    /'
    fi
else
    info "~/.claude.json does not exist (optional)"
fi
echo ""

subsection "Settings File"
SETTINGS_FILE="$HOME/.claude/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    ok "settings.json exists"
    if $VERBOSE; then
        echo ""
        echo "  Contents:"
        cat "$SETTINGS_FILE" 2>/dev/null | head -100 | sed 's/^/    /'
    else
        # Just show MCP server names
        if command -v jq &> /dev/null; then
            MCP_SERVERS=$(jq -r '.mcpServers // {} | keys[]' "$SETTINGS_FILE" 2>/dev/null)
            if [ -n "$MCP_SERVERS" ]; then
                echo "  MCP Servers configured:"
                echo "$MCP_SERVERS" | sed 's/^/    - /'
            else
                info "No MCP servers configured"
            fi
        else
            info "Install jq to see MCP server details"
        fi
    fi
else
    warn "settings.json does not exist"
fi
echo ""

subsection "Projects Directory"
PROJECTS_DIR="$HOME/.claude/projects"
if [ -d "$PROJECTS_DIR" ]; then
    ok "Projects directory exists"
    PROJECT_COUNT=$(ls -1 "$PROJECTS_DIR" 2>/dev/null | wc -l | tr -d ' ')
    echo "  Projects: $PROJECT_COUNT"
    if $VERBOSE && [ "$PROJECT_COUNT" -gt 0 ]; then
        echo ""
        ls -1 "$PROJECTS_DIR" 2>/dev/null | head -10 | sed 's/^/    /'
        [ "$PROJECT_COUNT" -gt 10 ] && info "... and $((PROJECT_COUNT - 10)) more"
    fi
else
    info "No projects directory yet"
fi
echo ""

subsection "Installed Plugins"
PLUGINS_FILE="$HOME/.claude/plugins/installed_plugins.json"
if [ -f "$PLUGINS_FILE" ]; then
    ok "Plugins configuration exists"
    if command -v jq &> /dev/null; then
        # Format: { "plugins": { "name@marketplace": [{ "version": "x.y.z", ... }] } }
        PLUGINS=$(jq -r '.plugins // {} | to_entries[] | "\(.key) v\(.value[0].version // "unknown")"' "$PLUGINS_FILE" 2>/dev/null)
        if [ -n "$PLUGINS" ]; then
            PLUGIN_COUNT=$(echo "$PLUGINS" | wc -l | tr -d ' ')
            echo "  Installed: $PLUGIN_COUNT plugin(s)"
            echo ""
            echo "$PLUGINS" | sed 's/^/    - /'
        else
            info "No plugins installed"
        fi
    else
        info "Install jq to see plugin details"
    fi
else
    info "No plugins installed yet"
fi
echo ""

#############################################
section "Dependencies"
#############################################

subsection "Package Manager"
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        ok "Homebrew: $(brew --version | head -1)"
    else
        fail "Homebrew not installed"
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command -v apt &> /dev/null; then
        ok "apt available"
    elif command -v brew &> /dev/null; then
        ok "Homebrew (Linuxbrew): $(brew --version | head -1)"
    else
        warn "No supported package manager found"
    fi
fi
echo ""

subsection "Node.js & npm"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NODE_PATH=$(which node)
    ok "Node.js: $NODE_VERSION"
    info "Path: $NODE_PATH"

    # Check version
    MAJOR=$(echo "$NODE_VERSION" | sed 's/v//' | cut -d. -f1)
    if [ "$MAJOR" -ge 18 ]; then
        ok "Version OK (need v18+)"
    else
        fail "Version too old (need v18+)"
    fi
else
    fail "Node.js not installed"
fi
echo ""

if command -v npm &> /dev/null; then
    ok "npm: $(npm --version)"
else
    fail "npm not found"
fi

if command -v npx &> /dev/null; then
    ok "npx: $(npx --version)"
else
    fail "npx not found"
fi
echo ""

subsection "Python & uv"
if command -v uvx &> /dev/null; then
    ok "uvx: $(uvx --version 2>&1 | head -1)"

    # Check Python 3.13
    if uvx --python 3.13 python --version &> /dev/null 2>&1; then
        PYVER=$(uvx --python 3.13 python --version 2>&1)
        ok "Python 3.13 available: $PYVER"
    else
        warn "Python 3.13 not yet cached (will install on first use)"
    fi
else
    fail "uvx not installed"
    info "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
fi
echo ""

if command -v python3 &> /dev/null; then
    info "System Python: $(python3 --version 2>&1)"
fi
echo ""

subsection "Other Tools"
for tool in git jq curl; do
    if command -v $tool &> /dev/null; then
        ok "$tool: $($tool --version 2>&1 | head -1)"
    else
        warn "$tool not found"
    fi
done
echo ""

#############################################
section "Environment Variables"
#############################################

subsection "PATH"
echo "$PATH" | tr ':' '\n' | head -15 | sed 's/^/  /'
PATH_COUNT=$(echo "$PATH" | tr ':' '\n' | wc -l | tr -d ' ')
[ "$PATH_COUNT" -gt 15 ] && info "... and $((PATH_COUNT - 15)) more entries"
echo ""

subsection "Relevant Variables"
for var in ANTHROPIC_API_KEY CLAUDE_CODE_API_KEY OPENAI_API_KEY TMPDIR EDITOR VISUAL; do
    VALUE="${!var}"
    if [ -n "$VALUE" ]; then
        if [[ "$var" == *"KEY"* || "$var" == *"SECRET"* || "$var" == *"TOKEN"* ]]; then
            ok "$var: [SET - hidden]"
        else
            ok "$var: $VALUE"
        fi
    else
        info "$var: (not set)"
    fi
done
echo ""

#############################################
section "Course Materials"
#############################################

COURSE_DIR="$HOME/ai-development-course"
if [ -d "$COURSE_DIR" ]; then
    ok "Course directory exists: $COURSE_DIR"
    echo ""

    # Check key files
    for file in PRE_COURSE_SETUP.md preflight.sh backup-claude-config.sh QUICK_REFERENCE.md; do
        if [ -f "$COURSE_DIR/$file" ]; then
            ok "$file present"
        else
            warn "$file missing"
        fi
    done
    echo ""

    # Check key directories
    for dir in plugins course exercises configs examples; do
        if [ -d "$COURSE_DIR/$dir" ]; then
            COUNT=$(ls -1 "$COURSE_DIR/$dir" 2>/dev/null | wc -l | tr -d ' ')
            ok "$dir/ ($COUNT items)"
        else
            warn "$dir/ missing"
        fi
    done
else
    warn "Course directory not found at $COURSE_DIR"
    info "Extract course materials to ~/ai-development-course"
fi
echo ""

#############################################
section "Beads CLI"
#############################################

if command -v bd &> /dev/null; then
    ok "Beads CLI installed"
    BD_VERSION=$(bd version 2>&1 | head -1)
    echo "  Version: $BD_VERSION"
    BD_PATH=$(which bd)
    echo "  Path: $BD_PATH"
else
    warn "Beads CLI (bd) not found"
    info "Install via: /plugin install beads (in Claude Code)"
fi
echo ""

#############################################
section "Disk Space"
#############################################

if [[ "$OSTYPE" == "darwin"* ]]; then
    df -h "$HOME" | tail -1 | awk '{print "  Available: " $4 " of " $2 " (" $5 " used)"}'
else
    df -h "$HOME" | tail -1 | awk '{print "  Available: " $4 " of " $2 " (" $5 " used)"}'
fi
echo ""

#############################################
section "Recent Claude Logs"
#############################################

LOG_DIR="$HOME/.claude/logs"
if [ -d "$LOG_DIR" ]; then
    LOG_COUNT=$(ls -1 "$LOG_DIR" 2>/dev/null | wc -l | tr -d ' ')
    ok "Logs directory exists ($LOG_COUNT files)"

    # Show recent logs
    RECENT=$(ls -t "$LOG_DIR" 2>/dev/null | head -5)
    if [ -n "$RECENT" ]; then
        echo ""
        echo "  Most recent:"
        echo "$RECENT" | while read f; do
            SIZE=$(ls -lh "$LOG_DIR/$f" 2>/dev/null | awk '{print $5}')
            MOD=$(ls -lh "$LOG_DIR/$f" 2>/dev/null | awk '{print $6, $7, $8}')
            echo "    $f ($SIZE, $MOD)"
        done
    fi

    if $VERBOSE; then
        # Show last few lines of most recent log
        LATEST=$(ls -t "$LOG_DIR" 2>/dev/null | head -1)
        if [ -n "$LATEST" ] && [ -f "$LOG_DIR/$LATEST" ]; then
            echo ""
            echo "  Last 10 lines of $LATEST:"
            tail -10 "$LOG_DIR/$LATEST" 2>/dev/null | sed 's/^/    /'
        fi
    fi
else
    info "No logs directory yet"
fi
echo ""

#############################################
section "Summary"
#############################################

echo "Diagnostic report complete."
echo ""
echo "If you need help, share this output (remove any sensitive info first)."
echo ""
if ! $VERBOSE; then
    info "Run with --verbose for more details: ./diagnose.sh --verbose"
fi
echo ""
