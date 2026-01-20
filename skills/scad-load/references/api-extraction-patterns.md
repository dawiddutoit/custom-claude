# API Extraction Patterns

## Overview

Regex patterns and parsing strategies for extracting OpenSCAD API surface (modules, functions, variables, customizer parameters).

## Module Definitions

**Pattern:**
```regex
^\s*module\s+(\w+)\s*\((.*?)\)\s*[{;]
```

**Matches:**
- `module drawer_stack(width, x_start, drawer_start=0) {`
- `module cabinet_shell() {`
- `module _helper() {`  (private convention)

**Grep command:**
```bash
grep -E '^\s*module\s+\w+\s*\(' file.scad
```

**Example output:**
```
module mini_workbench() {
module drawer_stack(width, x_start, drawer_start=0) {
module _internal_helper(x) {
```

**Parsing:**
```python
import re

pattern = r'^\s*module\s+(\w+)\s*\((.*?)\)\s*[{;]'

for line in file_lines:
    match = re.match(pattern, line)
    if match:
        name = match.group(1)
        params = match.group(2)
        is_private = name.startswith('_')

        print(f"Module: {name}, Params: {params}, Private: {is_private}")
```

## Function Definitions

**Pattern:**
```regex
^\s*function\s+(\w+)\s*\((.*?)\)\s*=
```

**Matches:**
- `function asmfw_section_internal_width(section_id) = ...`
- `function calc_total(a, b, c=10) = a + b + c;`
- `function _private_calc() = 42;`

**Grep command:**
```bash
grep -E '^\s*function\s+\w+\s*\(' file.scad
```

**Example output:**
```
function asmfw_section_internal_width(section_id) =
function asmfw_section_x_start(section_id) =
function _calc_offset(base) = base + PANEL_THICKNESS;
```

## Customizer Parameters

**Section markers:**
```regex
/\*\s*\[([^\]]+)\]\s*\*/
```

**Matches:**
- `/* [Dimensions] */`
- `/* [Display Options] */`
- `/* [Advanced Settings] */`

**Parameter pattern (after section marker):**
```regex
^(\w+)\s*=\s*([^;]+);\s*(//\s*(.*))?
```

**Matches:**
- `show_cabinet = true;  // Show cabinet shell`
- `wall_thickness = 18;`
- `drawer_heights = [140, 140, 92];  // Heights in mm`

**Grep commands:**
```bash
# Find customizer sections
grep -E '/\*\s*\[.*\]\s*\*/' file.scad

# Find parameters (with comments)
grep -E '^\w+\s*=.*;\s*//' file.scad
```

**Parsing example:**
```python
import re

# Extract customizer sections
section_pattern = r'/\*\s*\[([^\]]+)\]\s*\*/'
param_pattern = r'^(\w+)\s*=\s*([^;]+);(?:\s*//\s*(.*))?'

current_section = None
customizer_params = {}

for line in file_lines:
    # Check for section marker
    section_match = re.search(section_pattern, line)
    if section_match:
        current_section = section_match.group(1)
        customizer_params[current_section] = []
        continue

    # Check for parameter
    if current_section:
        param_match = re.match(param_pattern, line)
        if param_match:
            name = param_match.group(1)
            value = param_match.group(2).strip()
            comment = param_match.group(3) if param_match.group(3) else ""

            customizer_params[current_section].append({
                'name': name,
                'value': value,
                'comment': comment
            })
```

## Variable Assignments

**Pattern:**
```regex
^(\w+)\s*=\s*(.+);
```

**Matches:**
- `ASMFW_SECTION_IDS = ["A", "B", "C"];`
- `panel_thickness = 18;`
- `room_ew = 6440;  // East-West dimension`

**Grep command:**
```bash
# Get first 30 variable assignments
grep -E '^\w+\s*=' file.scad | head -30
```

**Distinguish from customizer params:**
- Variables outside `/* [Section] */` blocks are config variables
- Variables inside customizer sections are parameters

## Use/Include Statements

**Pattern:**
```regex
^\s*(use|include)\s*<([^>]+)>
```

**Also supports quote syntax:**
```regex
^\s*(use|include)\s*"([^"]+)"
```

**Matches:**
- `use <BOSL2/std.scad>`
- `include <../../lib/assembly-framework.scad>`
- `use "drawer.scad"`

**Grep command:**
```bash
# Angle bracket syntax
grep -E '^\s*(use|include)\s*<' file.scad

# Quote syntax
grep -E '^\s*(use|include)\s*"' file.scad

# Both
grep -E '^\s*(use|include)\s*[<"]' file.scad
```

**Parsing:**
```python
import re

pattern_angle = r'^\s*(use|include)\s*<([^>]+)>'
pattern_quote = r'^\s*(use|include)\s*"([^"]+)"'

dependencies = []

for line in file_lines:
    # Try angle bracket syntax
    match = re.match(pattern_angle, line)
    if match:
        keyword = match.group(1)  # "use" or "include"
        path = match.group(2)
        dependencies.append({
            'type': keyword,
            'path': path,
            'syntax': 'angle'
        })
        continue

    # Try quote syntax
    match = re.match(pattern_quote, line)
    if match:
        keyword = match.group(1)
        path = match.group(2)
        dependencies.append({
            'type': keyword,
            'path': path,
            'syntax': 'quote'
        })
```

## Comments and Documentation

**Single-line comments:**
```regex
//\s*(.*)
```

**Multi-line comments:**
```regex
/\*[\s\S]*?\*/
```

**Module/function documentation (preceding definition):**
```python
def extract_doc_comment(lines, index):
    """Extract comment block before module/function definition."""
    docs = []
    i = index - 1

    # Walk backwards collecting comments
    while i >= 0 and (lines[i].strip().startswith('//') or lines[i].strip() == ''):
        if lines[i].strip().startswith('//'):
            docs.insert(0, lines[i].strip()[2:].strip())
        i -= 1

    return '\n'.join(docs) if docs else None
```

## Complete API Extraction Example

```python
import re

def extract_openscad_api(file_path):
    """Extract complete API surface from OpenSCAD file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()

    api = {
        'modules': [],
        'functions': [],
        'customizer': {},
        'variables': [],
        'dependencies': []
    }

    current_customizer_section = None

    for i, line in enumerate(lines):
        # Customizer section
        section_match = re.search(r'/\*\s*\[([^\]]+)\]\s*\*/', line)
        if section_match:
            current_customizer_section = section_match.group(1)
            api['customizer'][current_customizer_section] = []
            continue

        # Module definition
        module_match = re.match(r'^\s*module\s+(\w+)\s*\((.*?)\)', line)
        if module_match:
            api['modules'].append({
                'name': module_match.group(1),
                'params': module_match.group(2),
                'private': module_match.group(1).startswith('_'),
                'line': i + 1
            })
            continue

        # Function definition
        func_match = re.match(r'^\s*function\s+(\w+)\s*\((.*?)\)\s*=', line)
        if func_match:
            api['functions'].append({
                'name': func_match.group(1),
                'params': func_match.group(2),
                'private': func_match.group(1).startswith('_'),
                'line': i + 1
            })
            continue

        # Variable assignment
        var_match = re.match(r'^(\w+)\s*=\s*([^;]+);', line)
        if var_match:
            name = var_match.group(1)
            value = var_match.group(2).strip()

            if current_customizer_section:
                # Customizer parameter
                api['customizer'][current_customizer_section].append({
                    'name': name,
                    'value': value,
                    'line': i + 1
                })
            else:
                # Configuration variable
                api['variables'].append({
                    'name': name,
                    'value': value,
                    'line': i + 1
                })
            continue

        # Dependencies
        dep_match = re.match(r'^\s*(use|include)\s*[<"]([^>"]+)[>"]', line)
        if dep_match:
            api['dependencies'].append({
                'type': dep_match.group(1),
                'path': dep_match.group(2),
                'line': i + 1
            })

    return api
```

## Edge Cases

### Multi-line Definitions

**Module with parameters split across lines:**
```openscad
module complex_module(
    width,
    height,
    depth,
    show_debug=false
) {
    // ...
}
```

**Handling:** Use `-A` flag in grep to get context lines:
```bash
grep -A 5 '^\s*module\s+\w+' file.scad
```

### Inline Comments

**Parameter with inline comment:**
```openscad
module drawer(
    width,     // Drawer width in mm
    height,    // Drawer height
    depth      // Drawer depth
) { }
```

**Handling:** Strip inline comments when parsing parameters:
```python
params = re.sub(r'//.*', '', params_string)
```

### Special Characters in Strings

**Variable with string value:**
```openscad
label_text = "Cabinet /* note */";  // Special chars in string
```

**Handling:** Be cautious with comment detection - strings can contain `//` and `/*`

## Performance Optimization

**For large files:**
1. Use grep to filter lines before parsing (much faster than reading entire file)
2. Stop parsing after finding what you need (early exit)
3. Use simple regex (avoid lookbehinds/lookaheads)
4. Cache parsed results

**Example efficient extraction:**
```bash
# Extract just module names (fast)
grep -oP '^\s*module\s+\K\w+' file.scad

# Extract just function names
grep -oP '^\s*function\s+\K\w+' file.scad

# Count modules (no parsing needed)
grep -c '^\s*module\s+' file.scad
```
