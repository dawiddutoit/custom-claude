---
name: data-migration-versioning
description: |
  Systematic data format migration and versioning for backward-compatible
  schema changes. Use when adding version field, migrating data formats (JSON,
  YAML, SQLite), supporting multiple schema versions, or upgrading file formats.
  Covers version numbering strategies, backward compatibility patterns, auto-upgrade
  timing, testing checklists, and common pitfalls like partial data preservation.
  Works with JSON, YAML, database schemas, and configuration files.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Grep
  - Glob
---

# Data Migration & Versioning

## Table of Contents

### Core Sections
- [When to Use This Skill](#when-to-use-this-skill) - Trigger phrases and situations
- [What This Skill Does](#what-this-skill-does) - Migration workflow and outcomes
- [Quick Start](#quick-start) - Immediate examples
  - [Example 1: JSON Format Migration](#example-1-json-format-migration) - v1.0 → v2.0 upgrade
  - [Example 2: Auto-Upgrade on Load](#example-2-auto-upgrade-on-load) - Transparent migration

### Migration Process
- [Version Numbering Strategies](#version-numbering-strategies) - Semantic, dotted, integer versioning
- [Backward Compatibility Patterns](#backward-compatibility-patterns) - Load old formats
- [Auto-Upgrade Timing](#auto-upgrade-timing) - When to migrate (load, save, update)
- [Field Deprecation Workflow](#field-deprecation-workflow) - Remove old fields safely
- [Testing Checklist](#testing-checklist) - Comprehensive migration validation

### Implementation
- [Migration Workflow](#migration-workflow) - 7-step process
- [Common Pitfalls](#common-pitfalls) - Anti-patterns to avoid
- [Language-Specific Patterns](#language-specific-patterns) - Python, JavaScript, Go, Rust

### Supporting Resources
- [Supporting Files](#supporting-files) - References, examples, templates, scripts
- [Examples](#examples) - Real-world migration patterns
- [Troubleshooting](#troubleshooting) - Common issues and solutions

## Purpose

Provides systematic guidance for migrating data formats (JSON, YAML, SQLite, config files) with version numbering and backward compatibility. Prevents data loss during migrations by enforcing testing checklists and detecting common anti-patterns like partial preservation. Essential when evolving file formats, adding features that require schema changes, or supporting multiple versions of data structures.

## When to Use This Skill

**Use when:**
- Adding version field to existing data format
- Migrating from v1.0 to v2.0 (or any version change)
- Adding new fields that change data structure
- Supporting multiple schema versions simultaneously
- Upgrading file formats (JSON, YAML, config files)
- Migrating database schemas with backward compatibility

**User trigger phrases:**
- "add data versioning"
- "migrate data format"
- "backward compatible file format"
- "upgrade v1 to v2"
- "schema migration"
- "support old file format"
- "migrate JSON structure"

**NOT for:**
- Breaking changes without backward compatibility
- Database migrations with ORM tools (use Alembic, Flyway, etc.)
- API versioning (different concern)

## What This Skill Does

Guides you through a systematic data migration process:

1. **Version Numbering** - Choose appropriate versioning scheme
2. **Backward Compatibility Design** - Load old formats transparently
3. **Auto-Upgrade Strategy** - Decide when to migrate data
4. **Migration Implementation** - Write conversion code
5. **Field Cleanup** - Remove deprecated fields
6. **Testing** - Validate all migration paths
7. **Documentation** - Record format changes

**Result:** ✅ Safe migration with zero data loss and backward compatibility

## Quick Start

### Example 1: JSON Format Migration

**Scenario:** Adding multi-material support to layout optimizer

**Before (v1.0):**
```json
{
  "version": "1.0",
  "material": "18mm Plywood",
  "result": { ... }
}
```

**After (v2.0):**
```json
{
  "version": "2.0",
  "materials": {
    "18mm Plywood": { "result": { ... } },
    "6mm MDF": { "result": { ... } }
  }
}
```

**Migration code:**
```python
def load_layout(path):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        # Auto-convert to v2.0 structure
        material = data.get("material", "Unknown")
        result = PackingResult.from_dict(data["result"])
        return {material: result}, config  # Return as dict

    elif version == "2.0":
        # Load v2.0 format
        results = {}
        for mat_name, mat_data in data["materials"].items():
            results[mat_name] = PackingResult.from_dict(mat_data["result"])
        return results, config
```

**Outcome:** Old v1.0 files load seamlessly, returned in v2.0 structure

### Example 2: Auto-Upgrade on Load

**User workflow:**
```
1. User has old v1.0 file: layout-old.json
2. Loads file via load_layout()
3. Adds new material
4. Saves via update_layout()
5. File automatically upgraded to v2.0
6. Both old and new materials preserved ✅
```

**Critical anti-pattern detected by this skill:**
```python
# ❌ BAD: Only saves original material during upgrade
materials_data = {
    original_material: {"result": results[original_material].to_dict()}
}
# RESULT: New materials LOST! 💥

# ✅ GOOD: Iterate through ALL materials
materials_data = {}
for mat_name, result in results.items():
    materials_data[mat_name] = {"result": result.to_dict()}
# RESULT: All materials preserved ✅
```

## Version Numbering Strategies

### Strategy 1: Semantic Versioning (Recommended for Libraries)

**Format:** `MAJOR.MINOR.PATCH`

**Rules:**
- MAJOR: Breaking changes (incompatible)
- MINOR: New features (backward compatible)
- PATCH: Bug fixes

**Example:**
```json
{"version": "2.1.0"}
```

**When to use:** Libraries, APIs, public data formats

### Strategy 2: Dotted Versioning (Recommended for Applications)

**Format:** `MAJOR.MINOR`

**Rules:**
- MAJOR: Structural changes (may need migration)
- MINOR: Field additions (backward compatible)

**Example:**
```json
{"version": "2.0"}
```

**When to use:** Application data files, configuration files (used in Stream A work)

### Strategy 3: Integer Versioning

**Format:** `1`, `2`, `3`

**Example:**
```json
{"version": 2}
```

**When to use:** Internal formats, simple migrations

### Strategy 4: Date-Based Versioning

**Format:** `YYYY-MM-DD` or `YYYYMMDD`

**Example:**
```json
{"version": "2025-12-21"}
```

**When to use:** Configuration files, data exports, snapshots

## Backward Compatibility Patterns

### Pattern 1: Auto-Convert on Load (Recommended)

**Advantages:**
- Transparent to caller
- No user intervention needed
- Works with read-only files

**Implementation:**
```python
def load_data(path):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        # Convert v1.0 to v2.0 structure in memory
        return convert_v1_to_v2(data)
    elif version == "2.0":
        return load_v2(data)
    else:
        raise ValueError(f"Unsupported version: {version}")
```

**When to use:** Most applications (Stream A used this)

### Pattern 2: Explicit Migration Script

**Advantages:**
- One-time operation
- Clear migration event
- User controls timing

**Implementation:**
```bash
# migrate_v1_to_v2.py
for file in *.json:
    data = load_v1(file)
    converted = convert_to_v2(data)
    save_v2(file, converted)
```

**When to use:** Large datasets, breaking changes, user needs notification

### Pattern 3: Dual-Format Support

**Advantages:**
- Supports both versions simultaneously
- Gradual migration
- Rollback possible

**Implementation:**
```python
def save_data(data, path, version="2.0"):
    if version == "1.0":
        save_v1_format(data, path)
    elif version == "2.0":
        save_v2_format(data, path)
```

**When to use:** Transitional periods, multiple clients with different versions

## Auto-Upgrade Timing

### Option 1: On Load (Recommended)

**When:** During `load_layout()` / `load_config()`

**Advantages:**
- Immediate compatibility
- Works with read-only files
- No user action needed

**Disadvantages:**
- File stays in old format until saved

**Example:** Stream A implementation

### Option 2: On First Save

**When:** During first `save()` or `update()` after load

**Advantages:**
- File updated to new format on disk
- Clear migration point

**Disadvantages:**
- File remains old format if never saved

**Example:**
```python
def update_layout(path, results):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        # Auto-upgrade to v2.0 on first save
        data["version"] = "2.0"
        data["materials"] = convert_to_v2_materials(results)
        data.pop("material", None)  # Remove old field
        data.pop("result", None)
```

### Option 3: On First Update (Hybrid - Used in Stream A)

**When:** During `update_layout()` (not on load, not on save)

**Advantages:**
- File loads in any format
- Upgrades only when modified
- Preserves original file if read-only

**Disadvantages:**
- More complex logic

**Example:** See `update_multi_material_layout()` in Stream A

### Option 4: Manual Migration Tool

**When:** User runs `migrate.py` script

**Advantages:**
- User controls timing
- Can handle large batches
- Clear migration event

**Disadvantages:**
- Requires user action

## Field Deprecation Workflow

### Step 1: Add Version Field (if missing)

```python
# Before
data = {"material": "18mm", "result": {...}}

# After
data = {"version": "1.0", "material": "18mm", "result": {...}}
```

### Step 2: Add New Fields (v1.1)

```python
# Backward compatible - keep old fields
data = {
    "version": "1.1",
    "material": "18mm",  # Old field - deprecated
    "materials": {"18mm": {...}},  # New field
    "result": {...}  # Old field - deprecated
}
```

### Step 3: Mark Fields as Deprecated (Documentation)

```python
# In code comments or docs
"""
version 1.1: 'material' and 'result' fields deprecated, use 'materials' instead
"""
```

### Step 4: Remove Old Fields (v2.0)

```python
# Breaking change - new major version
data = {
    "version": "2.0",
    "materials": {"18mm": {...}}
}
# 'material' and 'result' fields removed
```

### Step 5: Update Load Function

```python
def load(path):
    version = data.get("version", "1.0")

    if version in ["1.0", "1.1"]:
        # Support both old versions
        return load_legacy(data)
    elif version == "2.0":
        return load_v2(data)
```

## Testing Checklist

### Essential Tests

- [ ] **Load v1.0 file** - Verify old format loads without errors
- [ ] **Load v2.0 file** - Verify new format loads correctly
- [ ] **Round-trip v2.0** (save → load) - Data preserved
- [ ] **Upgrade v1.0 → v2.0** (load v1 → save → load) - Verify upgrade works
- [ ] **Data preservation** - ALL entities/materials preserved during upgrade ← CRITICAL
- [ ] **Field cleanup** - Old fields removed after upgrade
- [ ] **Version detection** - Correct version identified
- [ ] **Error handling** - Unsupported versions rejected with clear error

### Additional Tests

- [ ] **Multiple entity preservation** - When upgrading, all items preserved (not just first)
- [ ] **Metadata preservation** - Created dates, user info, etc. preserved
- [ ] **Concurrent loads** - Multiple files loaded simultaneously
- [ ] **Large files** - Performance with 1000+ entities
- [ ] **Edge cases** - Empty files, missing fields, corrupted data

### Test Template

```python
def test_v1_to_v2_upgrade():
    """Test v1.0 file auto-upgrades to v2.0 with all data preserved."""
    # Create v1.0 file
    v1_data = {
        "version": "1.0",
        "material": "18mm Plywood",
        "result": {"sheets_used": 2}
    }

    # Load v1.0 (auto-converts)
    results, config = load_layout(v1_path)
    assert len(results) == 1
    assert "18mm Plywood" in results

    # Add new material
    results["6mm MDF"] = create_result(sheets_used=1)

    # Update (triggers v1→v2 upgrade)
    update_layout(v1_path, results)

    # Verify upgrade
    with open(v1_path) as f:
        upgraded = json.load(f)

    assert upgraded["version"] == "2.0"
    assert "materials" in upgraded
    assert len(upgraded["materials"]) == 2  # Both materials!
    assert "18mm Plywood" in upgraded["materials"]
    assert "6mm MDF" in upgraded["materials"]
    assert "material" not in upgraded  # Old field removed
    assert "result" not in upgraded  # Old field removed
```

## Migration Workflow

### Step 1: Assess Current Format

```bash
# Identify all data files
find . -name "*.json" -o -name "*.yaml"

# Check current structure
cat example.json
```

### Step 2: Design New Format

```python
# Document changes
"""
v1.0 → v2.0 Migration Plan

Changes:
- Add "version" field (if missing)
- Convert "material" (string) → "materials" (dict)
- Convert "result" (object) → materials[name]["result"]

Backward compatibility: Yes (auto-convert on load)
Upgrade timing: On first update
"""
```

### Step 3: Implement Load Function

```python
def load_multi_version(path):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        return load_v1(data)  # Auto-convert
    elif version == "2.0":
        return load_v2(data)
    else:
        raise ValueError(f"Unsupported version: {version}")
```

### Step 4: Implement Save/Update Functions

```python
def save_v2(path, results):
    """Save in v2.0 format only."""
    data = {
        "version": "2.0",
        "materials": {
            mat_name: {"result": result.to_dict()}
            for mat_name, result in results.items()
        }
    }
    path.write_text(json.dumps(data, indent=2))

def update_layout(path, results):
    """Update existing file, auto-upgrade if v1.0."""
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        # Upgrade to v2.0 - save ALL materials
        data["version"] = "2.0"
        data["materials"] = {
            mat_name: {"result": result.to_dict()}
            for mat_name, result in results.items()
        }
        data.pop("material", None)
        data.pop("result", None)

    elif version == "2.0":
        # Update existing v2.0 structure
        for mat_name, result in results.items():
            data["materials"][mat_name] = {"result": result.to_dict()}

    path.write_text(json.dumps(data, indent=2))
```

### Step 5: Write Tests

See [Testing Checklist](#testing-checklist)

### Step 6: Update Documentation

```markdown
# File Format

## Version 2.0 (Current)

```json
{
  "version": "2.0",
  "materials": {
    "18mm": { "result": {...} }
  }
}
```

## Version 1.0 (Deprecated, still supported)

```json
{
  "version": "1.0",
  "material": "18mm",
  "result": {...}
}
```

## Migration

v1.0 files auto-convert on load. On first update, files upgrade to v2.0 format.
```

### Step 7: Deploy and Monitor

```bash
# Test with real files
python test_migration.py

# Monitor for issues
tail -f logs/migrations.log
```

## Common Pitfalls

### ❌ Pitfall 1: Partial Data Preservation (CRITICAL)

**Problem:** Only saving original entity during migration

```python
# ❌ BAD: Only saves the material from v1.0 file
materials_data = {
    original_material: {"result": results[original_material].to_dict()}
}
# RESULT: If user added new materials, they're LOST! 💥
```

**Fix:**
```python
# ✅ GOOD: Iterate through ALL materials
materials_data = {}
for mat_name, result in results.items():
    materials_data[mat_name] = {"result": result.to_dict()}
# RESULT: All materials preserved ✅
```

**Real-world impact:** This exact bug was found during Stream A testing. Would have caused DATA LOSS.

### ❌ Pitfall 2: Missing Version Field

**Problem:** No version field in original format

```python
# ❌ BAD: No version field
data = {"material": "18mm", "result": {...}}
```

**Fix:**
```python
# ✅ GOOD: Always include version, default to "1.0" if missing
version = data.get("version", "1.0")
```

### ❌ Pitfall 3: Breaking Changes Without Backward Compatibility

**Problem:** New code can't load old files

```python
# ❌ BAD: Only supports new format
def load_layout(path):
    data = json.loads(path.read_text())
    # Assumes v2.0 format, crashes on v1.0
    return data["materials"]
```

**Fix:**
```python
# ✅ GOOD: Support both versions
def load_layout(path):
    data = json.loads(path.read_text())
    version = data.get("version", "1.0")

    if version == "1.0":
        # Convert to v2.0 structure
        material = data["material"]
        return {material: data["result"]}
    elif version == "2.0":
        return data["materials"]
```

### ❌ Pitfall 4: Orphaned Fields After Migration

**Problem:** Old fields remain in upgraded files

```python
# ❌ BAD: Old fields remain
data["version"] = "2.0"
data["materials"] = {...}
# "material" and "result" still present! (orphaned)
```

**Fix:**
```python
# ✅ GOOD: Remove old fields
data["version"] = "2.0"
data["materials"] = {...}
data.pop("material", None)
data.pop("result", None)
```

### ❌ Pitfall 5: Untested Migration Paths

**Problem:** No tests for v1→v2 upgrade

**Fix:** See [Testing Checklist](#testing-checklist)

### ❌ Pitfall 6: Unclear Version Errors

**Problem:** Generic error for unsupported versions

```python
# ❌ BAD
raise ValueError("Bad version")
```

**Fix:**
```python
# ✅ GOOD
raise ValueError(
    f"Unsupported layout version: {version} "
    f"(expected 1.0 or 2.0)"
)
```

## Language-Specific Patterns

### Python

**Using dataclasses:**
```python
from dataclasses import dataclass, asdict

@dataclass
class LayoutV2:
    version: str = "2.0"
    materials: dict[str, Any]

    def to_dict(self):
        return asdict(self)
```

**Using Pydantic:**
```python
from pydantic import BaseModel

class LayoutV2(BaseModel):
    version: str = "2.0"
    materials: dict[str, Any]

    def to_dict(self):
        return self.model_dump()
```

### JavaScript/TypeScript

```typescript
interface LayoutV1 {
  version: "1.0";
  material: string;
  result: Result;
}

interface LayoutV2 {
  version: "2.0";
  materials: Record<string, { result: Result }>;
}

function loadLayout(path: string): LayoutV2 {
  const data = JSON.parse(fs.readFileSync(path, 'utf8'));

  if (data.version === "1.0") {
    // Auto-convert
    return {
      version: "2.0",
      materials: {
        [data.material]: { result: data.result }
      }
    };
  }

  return data as LayoutV2;
}
```

### Go

```go
type LayoutV1 struct {
    Version  string `json:"version"`
    Material string `json:"material"`
    Result   Result `json:"result"`
}

type LayoutV2 struct {
    Version   string              `json:"version"`
    Materials map[string]Material `json:"materials"`
}

func LoadLayout(path string) (*LayoutV2, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }

    // Try v2 first
    var v2 LayoutV2
    if err := json.Unmarshal(data, &v2); err == nil && v2.Version == "2.0" {
        return &v2, nil
    }

    // Fall back to v1
    var v1 LayoutV1
    if err := json.Unmarshal(data, &v1); err != nil {
        return nil, err
    }

    // Convert v1 → v2
    return &LayoutV2{
        Version: "2.0",
        Materials: map[string]Material{
            v1.Material: {Result: v1.Result},
        },
    }, nil
}
```

## Supporting Files

- [references/migration-patterns.md](references/migration-patterns.md) - Design patterns catalog
- [references/version-strategies.md](references/version-strategies.md) - Detailed versioning guide
- [examples/json-v1-to-v2.md](examples/json-v1-to-v2.md) - Real-world JSON migration (Stream A)
- [examples/yaml-migration.md](examples/yaml-migration.md) - YAML configuration migration
- [templates/migration-test-suite.py](templates/migration-test-suite.py) - Complete test template
- [templates/load-save-template.py](templates/load-save-template.py) - Load/save function templates
- [scripts/detect-version.sh](scripts/detect-version.sh) - Version detection utility

## Examples

### Example 1: JSON Layout Migration (Real Stream A Work)

See [examples/json-v1-to-v2.md](examples/json-v1-to-v2.md) for complete implementation

### Example 2: Configuration File Migration

```yaml
# Before (no version)
database:
  host: localhost
  port: 5432

# After (versioned)
version: "1.0"
database:
  host: localhost
  port: 5432
  pool_size: 10  # New field
```

### Example 3: Database Schema Migration

```sql
-- Migration: v1 → v2
ALTER TABLE users ADD COLUMN created_at TIMESTAMP;
UPDATE metadata SET version = '2.0';
```

## Troubleshooting

### Issue: "Old files won't load after migration"

**Solution:** Ensure backward compatibility in load function

```python
# Always support old versions
if version == "1.0":
    return load_v1(data)
```

### Issue: "Data lost during migration"

**Solution:** Check for partial preservation bug

```python
# Iterate through ALL items, not just original
for item in all_items:
    migrated_data[item.name] = convert(item)
```

### Issue: "Don't know which version strategy to use"

**Solution:**
- Application data files: Dotted versioning (2.0, 2.1)
- Library formats: Semantic versioning (2.1.0)
- Simple cases: Integer versioning (1, 2, 3)

### Issue: "When to remove old fields?"

**Solution:**
- v1.1: Keep both (deprecated + new)
- v2.0: Remove old fields (major version change)

## Requirements

**No external dependencies** - Works with standard library JSON/YAML parsing

**Minimum requirements:**
- Read/Write access to data files
- JSON or YAML parser
- Unit testing framework (for validation)

**Optional:**
- Schema validation library (JSON Schema, Pydantic)
- Migration tracking system (database or log file)
