#!/bin/bash
# Optimized Mermaid to PNG Converter
# Features: In-place editing, compressed API calls, automatic retry, syntax validation
set -euo pipefail

INPUT_FILE="$1"
OUTPUT_FILE="${2:-output.png}"
MAX_RETRIES=3

# Color output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

usage() {
    echo "Usage: $0 <input.mmd> [output.png]"
    exit 1
}

if [ -z "$INPUT_FILE" ]; then
    usage
fi

if [ ! -f "$INPUT_FILE" ]; then
    echo -e "${RED}Error:${NC} Input file '$INPUT_FILE' not found"
    exit 1
fi

# Create a working copy to avoid modifying original
WORK_FILE="${INPUT_FILE}.$$"
cp "$INPUT_FILE" "$WORK_FILE"

# Optimized syntax fixes using perl (more reliable than sed on macOS)
fix_syntax() {
    local file="$1"
    local original_content
    original_content=$(cat "$file")

    # Use perl for multi-pattern replacement (more reliable across platforms)
    perl -i -pe '
        s/end\(/finish(/g;
        s/end\)/finish)/g;
        s/end\[/finish[/g;
        s/end\]/finish]/g;
        s/end\{/finish{/g;
        s/end\}/finish}/g;
        s/end\>/finish>/g;
        s/--> end /--> finish /g;
        s/--> end$/--> finish/;
        s/^(\s*)end /$1finish /;
        s/^(\s*)end$/$1finish/;
    ' "$file" 2>/dev/null || true

    # Check if anything was changed
    local new_content
    new_content=$(cat "$file")
    if [ "$original_content" = "$new_content" ]; then
        echo -e "${YELLOW}No syntax changes needed${NC}"
        return 1
    else
        echo -e "${GREEN}✓${NC} Applied automatic syntax fixes"
        return 0
    fi
}

# Convert with retry logic
convert_with_retry() {
    local input="$1"
    local output="$2"
    local attempt=1

    while [ $attempt -le $MAX_RETRIES ]; do
        echo -n "Converting (attempt $attempt/$MAX_RETRIES)... "

        # Optimized curl with compression and timeout
        if curl -s --compressed --max-time 30 --connect-timeout 10 \
                -X POST -H "Content-Type: text/plain" \
                --data-binary @"$input" \
                "https://kroki.io/mermaid/png" \
                -o "$output" 2>/dev/null; then

            # Verify PNG header (check magic bytes: 89504e47)
            if head -c 4 "$output" | xxd -p -l 4 | grep -qi "89504e47"; then
                local dimensions
                dimensions=$(sips -g pixelWidth -g pixelHeight "$output" 2>/dev/null | awk '/pixel/ {printf "%s", $2 "x"}' || echo "unknown")
                if [ "$dimensions" = "unknown" ]; then
                    dimensions=$(identify -format "%wx%h" "$output" 2>/dev/null || echo "??x??")
                fi
                echo -e "${GREEN}✓${NC} Saved to $output ($dimensions)"
                return 0
            else
                local error_msg
                error_msg=$(head -c 500 "$output" 2>/dev/null || echo "Unknown error")
                echo -e "${RED}✗${NC} $error_msg"
            fi
        else
            echo -e "${RED}✗${NC} Network error"
        fi

        ((attempt++))
        [ $attempt -le $MAX_RETRIES ] && sleep 1
    done

    return 1
}

echo -e "${YELLOW}Validating Mermaid syntax...${NC}"
fix_syntax "$WORK_FILE" || true

if ! convert_with_retry "$WORK_FILE" "$OUTPUT_FILE"; then
    echo -e "${RED}Error:${NC} Failed to generate PNG after $MAX_RETRIES attempts"
    rm -f "$WORK_FILE"
    exit 1
fi

# Cleanup
rm -f "$WORK_FILE"

# Display file info
if command -v file &> /dev/null; then
    file "$OUTPUT_FILE"
fi
