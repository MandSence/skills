#!/bin/bash
# Parallel Batch Mermaid to PNG Converter
# Converts multiple .mmd files concurrently for maximum efficiency
set -euo pipefail

PATTERN="${1:-*.mmd}"
PARALLEL_JOBS="${2:-4}"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Find all .mmd files
FILES=($(ls $PATTERN 2>/dev/null)) || true

if [ ${#FILES[@]} -eq 0 ]; then
    echo -e "${RED}No files matching '$PATTERN'${NC}"
    exit 1
fi

echo "Found ${#FILES[@]} file(s) to convert"
echo "Using $PARALLEL_JOBS parallel jobs"

# Function to convert a single file
convert_file() {
    local input="$1"
    local output="${input%.mmd}.png"
    local work_file="${input}.$$"
    local max_retries=3
    local attempt=1

    echo -n "  Converting $input ... "

    # Create working copy
    cp "$input" "$work_file"

    # Apply syntax fixes using perl (more reliable than sed on macOS)
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
    ' "$work_file" 2>/dev/null || true

    # Try conversion with retry
    while [ $attempt -le $max_retries ]; do
        if curl -s --compressed --max-time 30 --connect-timeout 10 \
                -X POST -H "Content-Type: text/plain" \
                --data-binary @"$work_file" \
                "https://kroki.io/mermaid/png" \
                -o "$output" 2>/dev/null; then

            if head -c 4 "$output" | xxd -p -l 4 | grep -qi "89504e47"; then
                local size
                size=$(sips -g pixelWidth -g pixelHeight "$output" 2>/dev/null | awk '/pixel/ {printf "%s", $2 "x"}' || echo "??")
                if [ "$size" = "??" ]; then
                    size=$(identify -format "%wx%h" "$output" 2>/dev/null || echo "??x??")
                fi
                echo -e "${GREEN}✓${NC} ($size)"
                rm -f "$work_file"
                return 0
            fi
        fi

        ((attempt++))
        [ $attempt -le $max_retries ] && sleep 1
    done

    echo -e "${RED}✗${NC}"
    rm -f "$output" "$work_file"
    return 1
}

export -f convert_file

# Run conversions in parallel (compatible with macOS bash 3.2)
success=0
total=${#FILES[@]}
pids=()

for i in "${!FILES[@]}"; do
    file="${FILES[$i]}"
    convert_file "$file" &
    pids+=($!)

    # Limit concurrent jobs
    if [ ${#pids[@]} -ge $PARALLEL_JOBS ]; then
        for pid in "${pids[@]}"; do
            wait $pid 2>/dev/null || true
        done
        pids=()
    fi
done

# Wait for any remaining jobs
for pid in "${pids[@]}"; do
    wait $pid 2>/dev/null || true
done

# Count successful conversions
actual_success=0
for file in "${FILES[@]}"; do
    png_file="${file%.mmd}.png"
    if [ -f "$png_file" ]; then
        ((actual_success++))
    fi
done

echo ""
echo "Completed: $actual_success/$total successful"
