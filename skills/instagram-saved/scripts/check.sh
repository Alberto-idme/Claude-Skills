#!/usr/bin/env bash
# Run the whole verification suite. This is "the build".
#
#   ./check.sh            everything
#   ./check.sh --quick    skip the two slow suites (browser, OCR)
#
# Exits non-zero if anything fails.

set -uo pipefail
cd "$(dirname "$0")"

[ -d .venv ] && source .venv/bin/activate

QUICK=0
[ "${1:-}" = "--quick" ] && QUICK=1

SUITES=("test_ig_saved.py:offline unit tests")
if [ "$QUICK" = "0" ]; then
    SUITES+=("test_browser_e2e.py:browser against mock Instagram"
             "test_ocr_e2e.py:OCR and vision on real video"
             "test_pipeline_smoke.py:whole chain, mock in -> report out")
fi

printf '\n%s\n' "$(python -V) · $(pwd)"
printf '%s\n\n' "────────────────────────────────────────────────────────────"

FAILED=0
for entry in "${SUITES[@]}"; do
    file="${entry%%:*}"; label="${entry#*:}"
    printf '%-24s %-42s ' "$file" "$label"
    if output=$(timeout 900 python "$file" 2>&1); then
        # The suites print "N/N passed"; the smoke test prints stages instead.
        printf '%s\n' "$(printf '%s' "$output" | grep -Eo '[0-9]+/[0-9]+ passed' | tail -1 || echo ok)"
    else
        printf 'FAILED\n'
        printf '%s\n' "$output" | grep -E 'FAIL|Error|error|Traceback' | head -10 | sed 's/^/    /'
        FAILED=1
    fi
done

printf '\n'
if [ "$FAILED" = "0" ]; then
    printf 'All suites passed.\n'
else
    printf 'Something failed — see above.\n' >&2
fi
exit "$FAILED"
