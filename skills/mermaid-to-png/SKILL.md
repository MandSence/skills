---
name: mermaid-to-png
description: Convert Mermaid diagram code to PNG images using Kroki.io API (no local setup required) with automatic syntax validation, error fixing, and optimized performance
---

# Mermaid to PNG Converter (Optimized)

Convert Mermaid diagram code into high-quality PNG images for use in documents, presentations, and other applications.

## When to use

Use this skill when the user:
- Wants to convert Mermaid code to a PNG image
- Needs raster images instead of vector (SVG) formats
- Wants to insert diagrams into applications that don't support SVG
- Needs to embed diagrams in presentations or documents
- Requires batch conversion of multiple diagrams

## Important: Always Validate Syntax First

**Before converting to PNG, always validate and fix the Mermaid syntax.** This prevents API errors and ensures successful conversion.

### Validation Workflow

1. **Check syntax using Kroki.io validate endpoint** - This returns error details if invalid
2. **Identify and fix common syntax errors (optimized with in-place editing)**
3. **Re-validate until syntax is correct**
4. **Proceed with PNG conversion**

## Performance Optimizations

This optimized version includes:

1. **In-place editing** - Uses `sed -i` to avoid creating temporary files for each fix
2. **Single-pass regex** - Combined patterns reduce file I/O operations
3. **Compressed API calls** - Uses `--compressed` flag to reduce transfer time
4. **Request timeout** - `--max-time 30` prevents hanging on slow connections
5. **Automatic retry** - Built-in retry logic for transient API failures
6. **Batch parallel processing** - Converts multiple diagrams concurrently

## Syntax Validation

### Using Kroki.io for Validation

Kroki.io provides syntax validation. When a diagram has errors, it returns a detailed error message instead of an image.

```bash
# Validate Mermaid syntax - returns error details if invalid (optimized)
curl -s --compressed --max-time 30 \
     -X POST -H "Content-Type: text/plain" \
     --data-binary @diagram.mmd \
     "https://kroki.io/mermaid/png" \
     -o test_output.png

# Check if output is valid PNG
file test_output.png
# If it says "PNG image data", syntax is valid
# If it says "Unicode text, UTF-8", check content for errors
```

## Common Mermaid Syntax Errors and Fixes

### 1. Reserved Keywords as Node IDs

**Error:** `SyntaxError: Parse error on line X: ...got 'end'`

Mermaid reserves certain keywords that cannot be used as node IDs. Common reserved words include:
- `end`
- `graph`
- `subgraph`
- `linkStyle`
- `classDef`
- `class`

**Fix:** Replace reserved keywords with valid identifiers:

| Reserved | Replace With |
|----------|--------------|
| `end` | `finish`, `complete`, `done` |
| `graph` | `diagram`, `chart` |
| `subgraph` | `group`, `cluster` |

**Example:**
```mermaid
# WRONG
flowchart TD
    A --> end(结束)
    end --> B

# FIXED
flowchart TD
    A --> finish(结束)
    finish --> B
```

### 2. Missing Arrows or Connections

**Error:** `SyntaxError: Parse error: expecting ARROW`

**Fix:** Ensure proper arrow syntax:
- `-->` for flowcharts
- `->>` and `-->>` for sequence diagrams

```mermaid
# WRONG
flowchart LR
    A B

# FIXED
flowchart LR
    A --> B
```

### 3. Incorrect Node Shapes

**Error:** `SyntaxError: Parse error: expecting NODE_STRING`

**Fix:** Use correct node shape syntax:

| Shape | Syntax |
|-------|--------|
| Rounded rectangle | `[text]` |
| Stadium shape | `([text])` |
| Subroutine shape | `[[text]]` |
| Cylindrical shape | `[(text)]` |
| Circle | `((text))` |
| Rhombus (decision) | `{text}` |
| Hexagon | `{{text}}` |
| Parallelogram | `[/text/]` |
| Parallelogram (alt) | `[\text\]` |
| Trapezoid | `[/text\]` |
| Trapezoid (alt) | `[\text/]` |
| Asymmetric | `>text]` |

### 4. Line Break Issues in Edge Labels

**Error:** Edge labels must be on a single line or use the correct separator syntax.

**Fix:** For multi-line labels, use the proper syntax or move to a single line:

```mermaid
# WRONG
flowchart LR
    A -->|Line 1
    Line 2| B

# FIXED
flowchart LR
    A -->|Line 1 Line 2| B
```

### 5. Duplicate Node IDs

**Error:** Node IDs must be unique within a diagram.

**Fix:** Ensure each node has a unique identifier:

```mermaid
# WRONG
flowchart LR
    A[Start] --> B[Middle]
    A --> B[Another Middle]

# FIXED
flowchart LR
    A[Start] --> B1[Middle]
    A --> B2[Another Middle]
```

### 6. Missing Diagram Type Declaration

**Error:** First line must declare diagram type.

**Fix:** Start with one of: `flowchart`, `sequenceDiagram`, `classDiagram`, `erDiagram`, etc.

```mermaid
# WRONG
    A --> B

# FIXED
flowchart LR
    A --> B
```

## Instructions

### Method 1: Optimized Conversion Script (Recommended)

This optimized script uses in-place editing, compressed API calls, and automatic retry logic for maximum efficiency.

```bash
cat > mermaid-to-png.sh << 'EOF'
#!/bin/bash
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

# Optimized syntax fixes using single sed command with multiple expressions
fix_syntax() {
    local file="$1"
    local original_content
    original_content=$(cat "$file")

    # Single sed command with all patterns (much faster than multiple calls)
    sed -i '' \
        -e 's/\b\(end\)\s*[(\[{]/finish\1/g' \
        -e 's/\s*-->[[:space:]]*end\b/--> finish/g' \
        -e 's/\b\(end\)\b/finish/g' \
        -e 's/\b\(graph\)\s*[(\[{]/diagram\1/g' \
        -e 's/\b\(subgraph\)\b[^{]/cluster&/g' \
        "$file" 2>/dev/null || true

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

            # Verify PNG header (more efficient than file command)
            if head -c 8 "$output" | grep -q "PNG"; then
                local dimensions
                dimensions=$(identify -format "%wx%h" "$output" 2>/dev/null || echo "unknown")
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
EOF

chmod +x mermaid-to-png.sh
```

**Usage:**

```bash
# Convert a .mmd file to PNG with automatic syntax checking
./scripts/mermaid-to-png.sh diagram.mmd output.png

# Default output filename (output.png)
./scripts/mermaid-to-png.sh diagram.mmd
```

### Method 2: Parallel Batch Conversion

For converting multiple diagrams efficiently in parallel:

```bash
cat > mermaid-batch-convert.sh << 'EOF'
#!/bin/bash
set -euo pipefail

# Parallel batch converter
# Usage: ./scripts/mermaid-batch-convert.sh <pattern> [parallel-jobs]

PATTERN="${1:-*.mmd}"
PARALLEL_JOBS="${2:-4}"
GREEN='\033[0;32m'
RED='\033[0;31m'
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
    echo -n "  Converting $input ... "

    if curl -s --compressed --max-time 30 \
            -X POST -H "Content-Type: text/plain" \
            --data-binary @"$input" \
            "https://kroki.io/mermaid/png" \
            -o "$output" 2>/dev/null; then

        if head -c 8 "$output" | grep -q "PNG"; then
            local size
            size=$(identify -format "%wx%h" "$output" 2>/dev/null || echo "??x??")
            echo -e "${GREEN}✓${NC} ($size)"
            return 0
        fi
    fi

    echo -e "${RED}✗${NC}"
    rm -f "$output"
    return 1
}

export -f convert_file

# Run in parallel
success=0
total=${#FILES[@]}
for i in "${!FILES[@]}"; do
    file="${FILES[$i]}"
    ((jobs_running >= PARALLEL_JOBS)) && wait -n
    convert_file "$file" &
    ((jobs_running++))
    ((success+=$?))
done
wait

echo "Completed: $success/$total successful"
EOF

chmod +x mermaid-batch-convert.sh
```

**Usage:**

```bash
# Convert all .mmd files in current directory (4 parallel jobs)
./scripts/mermaid-batch-convert.sh "*.mmd" 4

# Convert specific files with custom parallelism
./scripts/mermaid-batch-convert.sh "diagram_*.mmd" 8
```

### Method 3: Direct curl command with validation (optimized)

For quick one-off conversions with validation:

```bash
# Optimized single command with validation
curl -s --compressed --max-time 30 \
     -X POST -H "Content-Type: text/plain" \
     --data-binary @diagram.mmd \
     "https://kroki.io/mermaid/png" \
     -o diagram.png && \
  head -c 8 diagram.png | grep -q "PNG" && \
  echo "Conversion successful!" || \
  (echo "Syntax error detected:"; cat diagram.png; rm diagram.png)
```

### Method 4: Using mermaid-cli (Requires Chrome)

This method uses `@mermaid-js/mermaid-cli` (mmdc) which requires Chrome or Chromium to be installed.

**Prerequisites:**
```bash
npm install -g @mermaid-js/mermaid-cli
npx puppeteer browsers install chrome-headless-shell
```

**Convert to PNG:**
```bash
mmdc -i diagram.mmd -o diagram.png
```

**Advanced options:**
```bash
# Set custom dimensions
mmdc -i diagram.mmd -o diagram.png -w 1200 -H 800

# Set scale for higher resolution
mmdc -i diagram.mmd -o diagram.png -s 2

# Set background color
mmdc -i diagram.mmd -o diagram.png -b white
```

**Available themes (mermaid-cli):** `default`, `forest`, `dark`, `neutral`, `base`

## Common Use Cases

### Direct Input Conversion with Validation

When user provides Mermaid code:
1. **Create a `.mmd` file** with the code
2. **Validate syntax** and fix any errors
3. **Run conversion** on the fixed code
4. **Provide the PNG file path** to the user

### Batch Conversion with Parallel Processing

For multiple diagrams (optimized with parallel jobs):
```bash
# Using the batch converter
./scripts/mermaid-batch-convert.sh "*.mmd" 4
```

### Convert from Mermaid Code String

When user provides Mermaid code directly:
```bash
# Create temp file
cat > temp.mmd << 'EOFM'
flowchart TD
    A[Start] --> B[End]
EOFM

# Validate and convert
./scripts/mermaid-to-png.sh temp.mmd output.png
```

## Supported Diagram Types

Kroki.io supports all Mermaid diagram types:
- flowchart - Process flows, algorithms
- sequence - Interactions, message flows
- class - Class diagrams, OOP
- state - State machines
- entity-relationship (er) - Database schemas
- gantt - Project timelines
- pie - Pie charts
- gitGraph - Git branching
- journey - User journeys
- c4 - C4 architecture diagrams

## Performance Tips

1. **Use batch processing** for multiple files - parallel processing reduces total time
2. **Enable compression** with `--compressed` flag for faster API calls
3. **Set appropriate timeouts** - `--max-time 30 --connect-timeout 10` prevents hanging
4. **Cache results** - store converted images to avoid repeated API calls
5. **Use in-place editing** - `sed -i ''` avoids unnecessary file copies

## Troubleshooting

**Error: "SyntaxError: Parse error"**
- Check for reserved keywords as node IDs (e.g., `end`, `graph`)
- Verify arrow syntax (`-->` for flowcharts, `->>` for sequences)
- Ensure all connections have proper syntax

**Error: Input file not found**
- Verify the `.mmd` file path is correct
- Use absolute path if needed

**PNG file is empty or contains text instead of image**
- The API may be temporarily unavailable
- The script will automatically retry up to 3 times
- Check syntax using validation step
- Try again after a moment

**Slow conversion for multiple files**
- Use the parallel batch converter: `./scripts/mermaid-batch-convert.sh "*.mmd" 4`
- Increase parallel jobs based on your network speed: `./scripts/mermaid-batch-convert.sh "*.mmd" 8`

**Error: Command not found: mmdc**
- Install mermaid-cli: `npm install -g @mermaid-js/mermaid-cli`

**Error: Could not find Chrome (mermaid-cli)**
- Install Chrome/Chromium on your system
- Or use Method 1 (Kroki API) instead

## Example Workflow

User: "Convert this Mermaid code to PNG"
```
flowchart TD
    start(开始) --> step1[选择操作类型]
    step1 --> op1{添加商品}
    op1 -- 是 --> add1[输入商品信息]
    add1 --> add2[选择商品分类]
    add2 --> add3[设置商品价格]
    add3 --> add4[设置初始库存]
    add4 --> add5[保存商品信息]
    add5 --> end(结束)
```

Agent actions:
1. **Validate syntax**: Detect `end` is a reserved keyword
2. **Fix the code**: Replace `end` with `finish`
3. **Create `temp.mmd`** with the fixed code
4. **Run `./scripts/mermaid-to-png.sh temp.mmd output.png`**
5. **Return**: "PNG saved to output.png (837x1173px)" and inform user of the fix applied

## Additional Options

### High-resolution output
For larger images, you can scale the output using image tools:
```bash
# Using sips (macOS)
sips -Z 2400 output.png --out output-hires.png

# Using ImageMagick
convert output.png -resize 2400 output-hires.png
```

### Different output formats
Kroki also supports other formats:
```bash
# SVG
curl -X POST -H "Content-Type: text/plain" --compressed \
     --data-binary @diagram.mmd "https://kroki.io/mermaid/svg" -o diagram.svg

# PDF
curl -X POST -H "Content-Type: text/plain" --compressed \
     --data-binary @diagram.mmd "https://kroki.io/mermaid/pdf" -o diagram.pdf
```

## Syntax Quick Reference

### Reserved Keywords to Avoid
Avoid using these as node IDs:
```
end, graph, subgraph, linkStyle, classDef, class, style,
click, callback, direction, alt, else, opt, loop, par,
rect, stroke, fill, opacity, width, height
```

### Flowchart Arrow Types
- `-->` : Standard arrow
- `---` : Line without arrow
- `-.->` : Dotted arrow
- `==> ` : Thick arrow
- `--text-->` : Arrow with label
- `-->|text|` : Arrow with label (alt syntax)

### Node Shape Syntax
- `[text]` : Rectangle
- `([text])` : Stadium/rounded
- `[(text)]` : Database/cylinder
- `((text))` : Circle
- `{text}` : Rhombus (decision)
- `>text]` : Asymmetric (flag)
