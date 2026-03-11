#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path

FILE_EXTENSIONS = {
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript',
    '.jsx': 'javascript',
    '.vue': 'vue',
    '.java': 'java',
    '.go': 'go',
    '.rs': 'rust',
    '.c': 'c',
    '.cpp': 'cpp',
    '.h': 'cpp',
    '.hpp': 'cpp',
    '.php': 'php',
    '.rb': 'ruby',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.kts': 'kotlin',
    '.cs': 'csharp',
    '.sql': 'sql',
    '.sh': 'shell',
    '.bash': 'shell',
    '.html': 'html',
    '.htm': 'html',
    '.css': 'css',
    '.scss': 'css',
    '.sass': 'css',
    '.less': 'css'
}

# Backend extensions (server-side code)
BACKEND_EXTENSIONS = {
    '.py', '.java', '.go', '.rs', '.c', '.cpp', '.h', '.hpp',
    '.php', '.rb', '.swift', '.kt', '.kts', '.cs', '.sql'
}

# Frontend extensions (client-side code)
FRONTEND_EXTENSIONS = {
    '.js', '.ts', '.tsx', '.jsx', '.vue', '.html', '.htm',
    '.css', '.scss', '.sass', '.less'
}

# Other extensions (shell scripts, etc.)
OTHER_EXTENSIONS = {'.sh', '.bash'}

EXCLUDE_DIRS = {
    'test', 'spec', '__tests__', '__test__',
    'target', 'build', 'dist', 'out',
    'node_modules', 'vendor', '.venv', 'venv',
    'env', '.env', 'envs',
    '__pycache__', '.pytest_cache',
    '.git', '.hg', '.svn',
    '.idea', '.vscode', '*.iml',
    'backups', 'logs', 'staticfiles', 'media'
}

def remove_c_style_comments(content):
    """
    Remove C-style multi-line comments (/* ... */) and Javadoc (/** ... */)
    Also removes C-style single-line comments (//)
    Preserves string literals
    """
    result = []
    i = 0
    n = len(content)
    in_string = False
    in_comment = False
    in_multiline_comment = False
    string_char = None

    while i < n:
        char = content[i]

        if in_multiline_comment:
            if i + 1 < n and content[i:i+2] == '*/':
                in_multiline_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_comment:
            if char == '\n':
                in_comment = False
                result.append(char)
                i += 1
                continue
            i += 1
            continue

        if in_string:
            if char == '\\' and i + 1 < n:
                result.append(char)
                result.append(content[i+1])
                i += 2
                continue
            if char == string_char:
                in_string = False
                result.append(char)
                i += 1
                continue
            result.append(char)
            i += 1
            continue

        # Check for string start
        if char in ('"', "'"):
            # Check if it's a raw string (Python)
            if i > 0 and content[i-1] in ('r', 'R', 'f', 'F', 'b', 'B', 'u', 'U'):
                in_string = True
                string_char = char
                result.append(char)
                i += 1
                continue
            in_string = True
            string_char = char
            result.append(char)
            i += 1
            continue

        # Check for multi-line comment start
        if i + 1 < n and content[i:i+2] in ('/*', '/**'):
            # Check if it's inside a string
            if i > 0 and content[i-1] == string_char and in_string:
                result.append(char)
                i += 1
                continue
            in_multiline_comment = True
            i += 2
            continue

        # Check for single-line comment start (but not inside a string)
        if i + 1 < n and content[i:i+2] == '//':
            # Check if it's inside a string
            if i > 0 and content[i-1] == string_char and in_string:
                result.append(char)
                i += 1
                continue
            in_comment = True
            i += 2
            continue

        result.append(char)
        i += 1

    return ''.join(result)

def remove_python_comments(content):
    """
    Remove Python comments (#) and docstrings (triple-quoted strings)
    """
    result = []
    i = 0
    n = len(content)
    in_string = False
    in_comment = False
    in_triple_string = False
    string_char = None

    while i < n:
        char = content[i]

        if in_triple_string:
            triple_char = string_char * 3
            if i + 2 < n and content[i:i+3] == triple_char:
                in_triple_string = False
                in_string = False
                string_char = None
                i += 3
                continue
            i += 1
            continue

        if in_comment:
            if char == '\n':
                in_comment = False
            i += 1
            continue

        if in_string:
            if char == '\\' and i + 1 < n:
                result.append(char)
                result.append(content[i+1])
                i += 2
                continue
            if char == string_char:
                in_string = False
                string_char = None
                result.append(char)
                i += 1
                continue
            result.append(char)
            i += 1
            continue

        # Check for triple-quoted string start
        if i + 2 < n and content[i:i+3] in ('"""', "'''"):
            in_triple_string = True
            in_string = True
            string_char = content[i]
            i += 3
            continue

        # Check for string start
        if char in ('"', "'"):
            in_string = True
            string_char = char
            result.append(char)
            i += 1
            continue

        # Check for comment start
        if char == '#':
            in_comment = True
            i += 1
            continue

        result.append(char)
        i += 1

    return ''.join(result)

def remove_html_comments(content):
    """Remove HTML comments <!-- -->"""
    return re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

def remove_blank_lines(content):
    """Remove all blank lines"""
    lines = content.splitlines()
    non_empty = [line for line in lines if line.strip()]
    return chr(10).join(non_empty)

class CodeCleaner:
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.ext = self.filepath.suffix.lower()
        self.lang = FILE_EXTENSIONS.get(self.ext, 'unknown')

    def clean(self, content):
        if content is None:
            return ''
        self.lang = FILE_EXTENSIONS.get(self.ext, 'unknown')

        if self.lang == 'python':
            content = remove_python_comments(content)
            return remove_blank_lines(content)
        elif self.lang in ('javascript', 'typescript', 'jsx', 'vue'):
            content = remove_c_style_comments(content)
            content = remove_html_comments(content)
            return remove_blank_lines(content)
        elif self.lang in ('css', 'scss', 'sass', 'less'):
            # Remove multi-line /* */ comments
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # For SCSS/SASS/Less, also remove // comments (line-based, but careful with URLs)
            lines = []
            for line in content.splitlines():
                line_content = line.rstrip()
                if not line_content:
                    continue
                # Check for // comment but not in a URL (http://, https://, //)
                if '//' in line_content:
                    # Find if // is part of a URL pattern
                    # URLs in CSS: url(//...), url(http://...), url(https://...)
                    # Or as property values: background-image: url(https://...);
                    # The // comment in SCSS must be outside quotes and URLs
                    # We need to find // that's not inside quotes or url()
                    idx = -1
                    i = 0
                    in_quote = False
                    quote_char = None
                    in_url = False
                    while i < len(line_content):
                        char = line_content[i]
                        if char in ('"', "'"):
                            if not in_quote:
                                in_quote = True
                                quote_char = char
                            elif char == quote_char:
                                in_quote = False
                        elif char == 'u' and i + 2 < len(line_content) and line_content[i:i+3] == 'url(':
                            in_url = True
                        elif char == ')' and in_url:
                            in_url = False
                        elif not in_quote and not in_url and i + 1 < len(line_content) and line_content[i:i+2] == '//':
                            idx = i
                            break
                        i += 1
                    if idx != -1:
                        line_content = line_content[:idx].rstrip()
                if line_content.strip():
                    lines.append(line_content)
            return chr(10).join(lines)
        elif self.lang == 'sql':
            # Remove SQL comments (--)
            lines = []
            for line in content.splitlines():
                if '--' in line:
                    idx = line.find('--')
                    line = line[:idx]
                if line.strip():
                    lines.append(line.rstrip())
            return chr(10).join(lines)
        elif self.lang == 'html':
            content = remove_html_comments(content)
            return remove_blank_lines(content)
        elif self.lang in ('java', 'c', 'cpp', 'go', 'rs', 'php', 'csharp', 'kotlin', 'swift', 'ruby'):
            content = remove_c_style_comments(content)
            return remove_blank_lines(content)
        elif self.lang in ('shell', 'bash'):
            lines = []
            for line in content.splitlines():
                line_content = line.rstrip()
                if not line_content:
                    continue
                if line_content.lstrip().startswith('#'):
                    continue
                if '#' in line_content:
                    idx = line_content.find('#')
                    line_content = line_content[:idx].rstrip()
                if line_content.strip():
                    lines.append(line_content)
            return chr(10).join(lines)
        else:
            content = remove_c_style_comments(content)
            return remove_blank_lines(content)

def is_excluded_dir(filepath):
    path = Path(filepath)
    parts = path.parts
    for part in parts:
        if part.lower() in EXCLUDE_DIRS:
            return True
    return False

def should_extract(filepath):
    path = Path(filepath)
    if path.is_dir():
        return False

    if path.suffix.lower() not in FILE_EXTENSIONS:
        return False

    if is_excluded_dir(filepath):
        return False

    return True

def get_file_priority(filepath):
    """Get priority for sorting files: backend (1), frontend (2), other (3)"""
    ext = filepath.suffix.lower()
    if ext in BACKEND_EXTENSIONS:
        return 1
    elif ext in FRONTEND_EXTENSIONS:
        return 2
    else:
        return 3

def extract_project(project_path, output_file=None):
    project_path = Path(project_path).resolve()
    if not project_path.exists():
        print(f'Error: Project path {project_path} does not exist', file=sys.stderr)
        return False

    if output_file is None:
        output_file = Path.cwd() / 'code_extraction.md'
    else:
        output_file = Path(output_file)

    print(f'Scanning project: {project_path}')
    print(f'Output file: {output_file}')

    all_files = []
    for ext in FILE_EXTENSIONS.keys():
        pattern = f'**/*{ext}'
        matches = list(project_path.glob(pattern))
        all_files.extend(matches)

    print(f'Found {len(all_files)} code files')

    # Sort files: first by category (backend, frontend, other), then by filepath
    all_files.sort(key=lambda f: (get_file_priority(f), str(f)))

    # Count files by category
    backend_count = sum(1 for f in all_files if get_file_priority(f) == 1)
    frontend_count = sum(1 for f in all_files if get_file_priority(f) == 2)
    other_count = sum(1 for f in all_files if get_file_priority(f) == 3)
    print(f'  Backend: {backend_count}, Frontend: {frontend_count}, Other: {other_count}')

    extracted_count = 0
    output_lines = ['# Code Extraction Document', '']

    for filepath in all_files:
        if not should_extract(filepath):
            continue

        try:
            rel_path = filepath.relative_to(project_path)

            cleaner = CodeCleaner(filepath)

            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError) as e:
                content = ''

            if not content or not content.strip():
                continue

            cleaned = cleaner.clean(content)

            if cleaned and cleaned.strip():
                output_lines.append(cleaned)
                extracted_count += 1

                if extracted_count % 50 == 0:
                    print(f'Processed {extracted_count}/{len(all_files)} files...')

        except Exception as e:
            print(f'Error processing {filepath}: {e}', file=sys.stderr)

    print(f'Extracted {extracted_count} files')
    print(f'Writing to {output_file}...')

    output_content = chr(10).join(output_lines)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_content)

    print(f'Done! Extracted {extracted_count} files')
    return True

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Extract and clean code from a project')
    parser.add_argument('project', help='Path to project directory')
    parser.add_argument('-o', '--output', help='Output file path (default: code_extraction.md)')
    args = parser.parse_args()

    if args.project:
        extract_project(args.project, args.output)
    else:
        print('Usage: python extractor.py <project_path> [-o output_file]')
