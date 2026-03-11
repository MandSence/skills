---
name: code-extractor
description: Extract pure code content from project source code and output to a markdown document. Use this skill whenever user asks to extract code from a project, clean code by removing comments and blank lines, get pure runnable code without any documentation, create a code extraction document, strip out comments from source code, or summarize code files into a single document.
---

# Code Extractor Skill (Optimized v2.1)

This skill extracts clean code content from project source code, removing all comments, blank lines, and documentation. The output is a markdown document containing ONLY executable code in plain text format.

**Sorting Feature**: Files are extracted in order - backend code first (.py, .java, .go, .rs, .c, .cpp, .php, .rb, .swift, .kt, .cs, .sql), then frontend code (.js, .ts, .tsx, .jsx, .vue, .html, .css, .scss), then other files (.sh, .bash). Within each category, files are sorted by path.

## When to Use

Use this skill when user requests any of:
- Extract code from a project directory
- Clean code by removing comments and blank lines
- Create a code extraction document
- Summarize all code files into one document
- Strip comments and documentation from source code
- Export pure runnable code without any comments

## Input Requirements

The skill accepts:
- Project path: The root directory of project to extract code from (required)
- Output file path: Where to save .md extraction document (optional, defaults to code_extraction.md in current working directory root)

## File Types to Extract

Extract files with these common code extensions:

Programming Languages:
- Python: .py
- JavaScript: .js
- TypeScript: .ts, .tsx
- Java: .java
- Go: .go
- Rust: .rs
- C/C++: .c, .cpp, .h, .hpp
- Shell: .sh, .bash
- SQL: .sql
- HTML: .html, .htm
- CSS: .css, .scss, .sass, .less
- Kotlin: .kt, .kts
- Swift: .swift
- PHP: .php
- Ruby: .rb
- C#: .cs
- Vue: .vue
- React: .jsx

## Files to Exclude

Do NOT include:
- Test files (files/directories containing test, spec, __tests__, __test__)
- Build output directories (target/, build/, dist/, out/, node_modules/, vendor/, .venv, venv)
- Documentation files (.md, README, LICENSE, CHANGELOG)
- Version control files (.git/, .hg/, .svn/)
- IDE configuration files (.idea/, .vscode/, *.iml)
- Environment files (.env, .env.*, envs)
- Configuration and data files (.json, .yml, .yaml, .xml, .toml, .ini, .cfg, .conf)
- Compiled files (.class, .o, .so, .dll, .exe)
- Asset files (images, fonts, media)
- Cache and log directories (backups/, logs/, staticfiles/, media/, __pycache__, .pytest_cache/)

## Cleaning Rules

### What to Remove Completely

Remove ALL of the following from the output:

1. Blank Lines:
   - All empty lines (lines containing only whitespace)
   - Lines with only spaces or tabs
   - Multiple consecutive blank lines

2. Single-line Comments (remove entire line):
   - // comment (C, C++, Java, JavaScript, TypeScript, JSX, Go, C#, PHP)
   - # comment (Python, Ruby, Shell, YAML, TOML)
   - -- comment (SQL, Haskell, Lua)
   - ; comment (INI files, Lisp)
   - :: comment (Batch files)
   - REM comment (Batch files)

3. Multi-line Comments:
   - /* comment */ (C, C++, Java, JavaScript, TypeScript, JSX, Go, C#, PHP, CSS)
   - <!-- comment --> (HTML, XML, SGML, Vue templates)
   - (* comment *) (Pascal, OCaml, F#, Mathematica)
   - {- comment -} (Haskell)
   - (*| comment |*) (Mathematica)
   - --[[ comment ]] (Lua)
   - """ comment """ (Python docstrings - multiline)
   - ''' comment ''' (Python docstrings - multiline)

4. Documentation Content:
   - All docstrings (Python triple quotes)
   - Javadoc comments (slash star star ... star slash)
   - XML documentation comments
   - License headers and copyright notices
   - File header comments
   - Inline documentation comments

### What to Keep

Keep ONLY executable code:
- Code statements and expressions
- Import/include statements
- Variable declarations
- Function/class/interface definitions
- String literals (even if they contain comment-like characters)
- Code operators and punctuation
- Control structures (if, for, while, etc.)

### Special Handling for Vue Files

For .vue files:
- Template section: Remove HTML comments (<!-- -->), keep Vue syntax
- Script section: Remove JS comments (// and /* */), keep code
- Style section: Remove CSS comments (/* */), keep styles

## Execution Method (Optimized)

The skill uses a high-performance Python script (`extractor.py`) for fast code extraction:

### Performance Features

1. **Single-Pass File Discovery**: Batch glob pattern matching for all extensions
2. **Efficient Content Reading**: Direct file I/O with UTF-8 encoding
3. **Regex-Based Cleaning**: Compiled regex patterns for fast comment removal
4. **Stream Output**: Minimized I/O operations with progress reporting
5. **Smart Sorting**: Files are extracted in priority order (backend → frontend → other) with path-based sorting within categories

### Sorting Order

The extractor automatically sorts files into three categories:

1. **Backend Code** (Priority 1):
   - .py (Python)
   - .java (Java)
   - .go (Go)
   - .rs (Rust)
   - .c, .cpp, .h, .hpp (C/C++)
   - .php (PHP)
   - .rb (Ruby)
   - .swift (Swift)
   - .kt, .kts (Kotlin)
   - .cs (C#)
   - .sql (SQL)

2. **Frontend Code** (Priority 2):
   - .js (JavaScript)
   - .ts, .tsx (TypeScript)
   - .jsx (React JSX)
   - .vue (Vue)
   - .html, .htm (HTML)
   - .css, .scss, .sass, .less (Stylesheets)

3. **Other Files** (Priority 3):
   - .sh, .bash (Shell scripts)

Within each category, files are sorted alphabetically by their full path.

### Python Script Commands

Run the extractor directly:

```bash
python3 /path/to/.claude/skills/code-extractor/scripts/extractor.py <project_path> [-o output_file]
```

Parameters:
- `project_path`: Path to the project directory (required)
- `-o output_file`: Output file path (optional, defaults to code_extraction.md in CWD)

### Cleaning Implementation

The optimized cleaner uses:
- String literal detection to preserve code strings
- Multi-pass regex for comment removal
- Efficient line-by-line processing
- Language-specific cleaning rules
- Vue file handling (template/script/style sections)

## Output Format

The output follows these strict rules:

1. Start with only `# Code Extraction Document` as the title
2. After the title, a single blank line
3. Then the cleaned code from each file
4. Separate code from different files with a single blank line
5. NEVER use backticks or code block syntax
6. NEVER include file paths or file names
7. NEVER use section headers like ### or ##
8. NEVER add any descriptive text or comments

Output example (correct format):

Start with title: # Code Extraction Document

Then add Python code:
import os
import sys
from pathlib import Path
def greet(name):
    return f"Hello, {name}!"
def main():
    print(greet("World"))
if __name__ == "__main__":
    main()

Then add JavaScript code:
const express = require('express');
const app = express();
const PORT = 3000;
app.get('/', (req, res) => {
    res.send('Hello');
});
app.listen(PORT);

## Edge Cases and Special Handling

### String Literals

Do NOT remove content that looks like comments but is inside string literals:
- Strings containing //, #, /* should be preserved
- Example: const message = "This is not // a comment"; - keep string intact

### Nested Comments

Handle nested comment structures carefully:
- Most languages do not support true nested comments
- For languages that do, handle appropriately
- Remove all comment content regardless of nesting

### Mixed Content

For files with mixed content (e.g., HTML with embedded CSS/JS):
- Remove HTML comments (<!-- -->)
- Remove CSS comments (/* */)
- Remove JS comments (// and /* */)
- For Vue files (.vue): Remove template HTML comments (<!-- -->) and script comments (//, /* */)
- For JSX files (.jsx): Remove JavaScript comments (//, /* */) while preserving JSX syntax (className, etc.)

## Performance Notes

The optimized extractor processes files significantly faster than tool-based extraction:
- Single-pass directory scanning instead of multiple Glob calls
- Direct file I/O bypassing tool overhead
- Compiled regex patterns for fast pattern matching
- Progress reporting during large file processing
