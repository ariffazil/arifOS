# arifosd Patch String-Literal Bug Fix

## Problem
When `write_file` or multi-line patches insert long strings containing `\n` or `\t` escape sequences, they can break across lines in the output. Python treats a literal newline inside a string literal as a syntax error. The bug appears as:

```
SyntaxError: unterminated string literal (detected at line X)
>>> Line N: '        for line in out.strip().split("\n'
>>> Line N+1: '")[1:]:'
```

## Root Cause
Strings with `\n`, `\t`, `\x`, or other escape sequences can get line-broken by the output writer. Python then sees an unclosed `"` at the end of line N and an orphaned `")` at the start of line N+1.

## Fix Method

```python
with open("/path/to/file.py") as f:
    lines = f.readlines()

# Find the broken pair: line ends with just '"' 
# 0-index the line number from the error message
lines[broken_0index] = 'correct merged line content\n'
del lines[broken_0index + 1]  # Remove orphaned continuation

with open("/path/to/file.py", "w") as f:
    f.writelines(lines)
```

## Automation Script
```python
with open("file.py") as f:
    lines = f.readlines()

import ast
fixes = 0
while True:
    try:
        ast.parse("".join(lines)); break
    except SyntaxError as e:
        lineno = e.lineno
        line_cur  = lines[lineno-1]
        line_next = lines[lineno] if lineno < len(lines) else ""
        merged = line_cur.rstrip() + line_next.lstrip(' "\t')
        lines[lineno-1] = merged + "\n"
        del lines[lineno]
        fixes += 1
        print(f"  Fixed merge at old line {lineno}")

with open("file.py", "w") as f:
    f.writelines(lines)
```

## Prevention
- In `write_file`, avoid inserting strings containing `\n` or similar escapes across lines
- For multi-line strings, use `\n` as explicit escape sequences rather than literal newlines
- After any large patch, always run `python3 -m py_compile file.py` to check syntax before proceeding

## Affected Files (May 2025 session)
- `/workspace/arifOS/arifosd.py` — 5 broken string literal pairs fixed manually