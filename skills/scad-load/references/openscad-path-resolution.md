# OpenSCAD Path Resolution

## Overview

OpenSCAD uses two syntaxes for file inclusion: angle brackets (`<file.scad>`) and quotes (`"file.scad"`). Each has different search path behavior.

## Angle Bracket Syntax: `<file.scad>`

**Search order:**

1. **Project library directory** (highest priority)
   - Location: `{project_root}/lib/`
   - Example: `<labels.scad>` → `{project}/lib/labels.scad`

2. **User library directory** (macOS)
   - Location: `~/Documents/OpenSCAD/libraries/`
   - Example: `<BOSL2/std.scad>` → `~/Documents/OpenSCAD/libraries/BOSL2/std.scad`

3. **User library directory** (Linux)
   - Location: `~/.local/share/OpenSCAD/libraries/`
   - Example: `<BOSL2/std.scad>` → `~/.local/share/OpenSCAD/libraries/BOSL2/std.scad`

4. **System library directory** (if configured)
   - Platform-specific installation directory
   - Usually not used for user projects

**Examples:**

```openscad
// Project lib
use <labels.scad>
// → searches: lib/labels.scad, then system libraries

// External library
include <BOSL2/std.scad>
// → searches: lib/BOSL2/std.scad, then ~/Documents/OpenSCAD/libraries/BOSL2/std.scad

// Nested library path
use <woodworkers-lib/std.scad>
// → ~/Documents/OpenSCAD/libraries/woodworkers-lib/std.scad
```

## Quote Syntax: `"file.scad"`

**Search behavior:**
- Relative to **current file's directory**
- No library search paths

**Examples:**

```openscad
// In workshop/workbenches/mini-workbench.scad

include "../../lib/assembly-framework.scad"
// → {project_root}/lib/assembly-framework.scad

use "../cabinets/drawer.scad"
// → workshop/cabinets/drawer.scad
```

## Path Resolution Algorithm

```python
def resolve_scad_path(include_statement, current_file_dir, project_root):
    """
    Resolve OpenSCAD include/use path to absolute path.

    Args:
        include_statement: e.g., "<BOSL2/std.scad>" or "../../lib/file.scad"
        current_file_dir: Directory containing the file with include statement
        project_root: Project root directory (where .git/ is located)

    Returns:
        Absolute path to included file, or None if not found
    """
    # Extract path from statement
    if '<' in include_statement:
        # Angle bracket syntax
        path = extract_between('<', '>', include_statement)
        return resolve_library_path(path, project_root)
    else:
        # Quote syntax (relative path)
        path = extract_between('"', '"', include_statement)
        return resolve_relative_path(path, current_file_dir)

def resolve_library_path(path, project_root):
    """Resolve angle bracket path."""
    search_paths = [
        f"{project_root}/lib/{path}",
        f"{os.path.expanduser('~')}/Documents/OpenSCAD/libraries/{path}",
        f"{os.path.expanduser('~')}/.local/share/OpenSCAD/libraries/{path}",
    ]

    for candidate in search_paths:
        if os.path.exists(candidate):
            return os.path.abspath(candidate)

    return None  # Not found

def resolve_relative_path(path, current_file_dir):
    """Resolve quote syntax relative path."""
    candidate = os.path.join(current_file_dir, path)
    if os.path.exists(candidate):
        return os.path.abspath(candidate)
    return None
```

## Common Patterns

### Project Structure with lib/

```
project/
├── lib/
│   ├── assembly-framework.scad
│   ├── labels.scad
│   └── materials.scad
└── workshop/
    └── workbenches/
        └── mini-workbench.scad
```

**In mini-workbench.scad:**

```openscad
// ✅ PREFER: Angle brackets (searches lib/ first)
include <assembly-framework.scad>
use <labels.scad>

// ❌ AVOID: Relative paths (brittle if files move)
include "../../lib/assembly-framework.scad"
use "../../lib/labels.scad"
```

### External Libraries

```openscad
// ✅ CORRECT: Angle brackets for libraries
include <BOSL2/std.scad>
use <woodworkers-lib/std.scad>
use <NopSCADlib/lib.scad>

// ❌ WRONG: Quote syntax doesn't search library paths
include "BOSL2/std.scad"  // Will fail
```

### Relative References (same directory)

```openscad
// In workshop/cabinets/left-cabinet.scad
use "drawer.scad"  // workshop/cabinets/drawer.scad
use "shelf.scad"   // workshop/cabinets/shelf.scad
```

## Platform Differences

| OS | Library Path | Notes |
|----|--------------|-------|
| **macOS** | `~/Documents/OpenSCAD/libraries/` | Default location |
| **Linux** | `~/.local/share/OpenSCAD/libraries/` | XDG standard |
| **Windows** | `%USERPROFILE%\Documents\OpenSCAD\libraries\` | User documents |

## Troubleshooting

### "File not found" errors

**Symptom:**
```
ERROR: Can't open library 'BOSL2/std.scad'
```

**Checks:**

1. **Verify library installation:**
   ```bash
   ls ~/Documents/OpenSCAD/libraries/BOSL2/
   # or
   ls ~/.local/share/OpenSCAD/libraries/BOSL2/
   ```

2. **Check syntax:**
   ```openscad
   // ✅ CORRECT
   include <BOSL2/std.scad>

   // ❌ WRONG (quote syntax doesn't search libraries)
   include "BOSL2/std.scad"
   ```

3. **Verify case sensitivity (Linux):**
   ```openscad
   // Linux is case-sensitive
   include <bosl2/std.scad>  // ❌ WRONG (lowercase)
   include <BOSL2/std.scad>  // ✅ CORRECT
   ```

### Library path detection in skill

**Check multiple locations:**

```bash
# macOS
test -f ~/Documents/OpenSCAD/libraries/BOSL2/std.scad && echo "Found (macOS)"

# Linux
test -f ~/.local/share/OpenSCAD/libraries/BOSL2/std.scad && echo "Found (Linux)"

# Project lib
test -f lib/assembly-framework.scad && echo "Found (project)"
```

## Best Practices

1. **Use angle brackets for all libraries** (project lib/ and external libraries)
2. **Use quotes only for same-directory relative references**
3. **Avoid deep relative paths** (`../../..`) - restructure project instead
4. **Install libraries in standard locations** (don't customize library paths)
5. **Document required libraries** in project README with installation instructions
