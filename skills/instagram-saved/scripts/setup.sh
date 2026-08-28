#!/usr/bin/env bash
# One-command setup. Creates a virtualenv, installs everything, downloads a
# browser, and runs the environment check.
#
#   ./setup.sh               everything
#   ./setup.sh --no-whisper  skip reel transcription (largest download)
#   ./setup.sh --no-ocr      skip on-screen text extraction
#   ./setup.sh --minimal     browser + database only
#
# Safe to re-run.

set -euo pipefail
cd "$(dirname "$0")"

WHISPER=1
OCR=1
for arg in "$@"; do
    case "$arg" in
        --no-whisper) WHISPER=0 ;;
        --no-ocr)     OCR=0 ;;
        --minimal)    WHISPER=0; OCR=0 ;;
        -h|--help)
            sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
            exit 0 ;;
        *) echo "Unknown option: $arg" >&2; exit 2 ;;
    esac
done

say() { printf '\n\033[1m%s\033[0m\n' "$*"; }

# --- python ----------------------------------------------------------------

PY=""
for candidate in python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
            PY="$candidate"
            break
        fi
    fi
done

if [ -z "$PY" ]; then
    echo "Python 3.10+ is required but was not found." >&2
    echo "  macOS:  brew install python@3.12" >&2
    echo "  Ubuntu: sudo apt install python3 python3-venv" >&2
    exit 1
fi
say "Using $($PY --version)"

# --- venv ------------------------------------------------------------------

if [ ! -d .venv ]; then
    say "Creating virtualenv (.venv)"
    "$PY" -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --quiet --upgrade pip

# --- dependencies ----------------------------------------------------------

# Driven from requirements.txt so a new dependency is never silently missed —
# this drifted once already and shipped an install with no OCR engine.
EXCLUDE=""
[ "$WHISPER" = "0" ] && EXCLUDE="$EXCLUDE faster-whisper"
[ "$OCR" = "0" ] && EXCLUDE="$EXCLUDE rapidocr-onnxruntime"

PACKAGES=$(
    grep -vE '^\s*(#|$)' requirements.txt |
    while read -r line; do
        name=$(printf '%s' "$line" | sed 's/[<>=!].*//' | tr -d '[:space:]')
        skip=0
        for bad in $EXCLUDE; do [ "$name" = "$bad" ] && skip=1; done
        [ "$skip" = "0" ] && printf '%s\n' "$line"
    done
)

say "Installing dependencies"
printf '%s\n' "$PACKAGES" | sed 's/^/    /'

# Install one at a time: a single unavailable wheel should not take the whole
# environment down, and the doctor check below reports whatever is missing.
FAILED=""
while read -r package; do
    [ -z "$package" ] && continue
    python -m pip install --quiet "$package" || FAILED="$FAILED $package"
done <<EOF
$PACKAGES
EOF

if [ -n "$FAILED" ]; then
    echo "" >&2
    echo "These did not install:$FAILED" >&2
    echo "The stages that need them will be reported by 'doctor' below." >&2
fi

# --- browser ---------------------------------------------------------------

say "Installing Chromium for Playwright"
if ! python -m playwright install chromium; then
    echo "Browser download failed." >&2
    echo "If you already have Chrome, point at it instead:" >&2
    echo "  export IG_SAVED_CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'" >&2
fi

# --- verify ----------------------------------------------------------------

say "Checking the environment"
python -m ig_saved.cli doctor || true

cat <<'EOF'

────────────────────────────────────────────────────────────
Setup done. From this directory, activate the venv each time:

    source .venv/bin/activate

Then:

    python -m ig_saved.cli login          # sign in by hand, once
    python -m ig_saved.cli collections    # list your collections

To archive one collection (start small to confirm it works):

    python -m ig_saved.cli index --source browser --max-pages 1 \
        --collection 'https://www.instagram.com/<you>/saved/<name>/<id>/'
    python -m ig_saved.cli stats

Then the full run:

    python -m ig_saved.cli sync --source browser
    python -m ig_saved.cli search 'ramen'
────────────────────────────────────────────────────────────
EOF
