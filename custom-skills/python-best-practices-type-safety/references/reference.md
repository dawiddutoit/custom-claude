# Reference - Debug Type Errors

Complete error pattern catalog, advanced configuration, and troubleshooting guide.

## Python Example Scripts

The following utility scripts demonstrate practical usage patterns:

- [parse_pyright_errors.py](../examples/parse_pyright_errors.py) - Parses pyright output to identify and categorize type errors
- [fix_missing_annotations.py](../examples/fix_missing_annotations.py) - Automatically adds missing type annotations to Python functions and variables
- [fix_optional_handling.py](../examples/fix_optional_handling.py) - Detects and fixes improper Optional/None handling patterns

---

## Complete Error Pattern Catalog

### Pattern Group 1: Missing Annotations

| Error Code | Error Message | Fix Template |
|------------|---------------|--------------|
| `reportUnknownReturnType` | `Return type of "func" is unknown` | Add `-> ReturnType` annotation |
| `reportUnknownParameterType` | `Type of parameter "param" is unknown` | Add `param: Type` annotation |
| `reportUnknownVariableType` | `Type of "var" is unknown` | Add `var: Type` annotation or let pyright infer |
| `reportUnknownMemberType` | `Type of member "attr" is unknown` | Add class attribute annotation |
| `reportUnknownLambdaType` | `Type of lambda parameter is unknown` | Add lambda parameter type or use def |

**Fix Template:**
```python
# Missing return type
def func(param: str):  # Error
    return param.upper()

def func(param: str) -> str:  # Fixed
    return param.upper()

# Missing parameter type
def func(param):  # Error
    return param

def func(param: str) -> str:  # Fixed
    return param

# Missing variable type (explicit needed)
result = complex_function()  # Error if type unclear
result: ServiceResult[dict] = complex_function()  # Fixed
```

---

### Pattern Group 2: Type Mismatches

| Error Code | Error Message | Fix Template |
|------------|---------------|--------------|
| `reportAssignmentType` | `Type "X" is not assignable to "Y"` | Change variable type or cast |
| `reportArgumentType` | `Argument of type "X" cannot be assigned to parameter "Y"` | Fix argument type or function signature |
| `reportReturnType` | `Return type "X" is not assignable to declared type "Y"` | Fix return type annotation or return value |
| `reportIncompatibleMethodOverride` | `Override is incompatible with base class` | Match base class signature exactly |

**Fix Template:**
```python
# Assignment mismatch
result: ServiceResult[bool] = get_dict_result()  # Error
result: ServiceResult[dict] = get_dict_result()  # Fixed

# Argument mismatch
def process(data: dict): pass
process("string")  # Error
process({"key": "value"})  # Fixed

# Return type mismatch
def get_data() -> dict:
    return ["list"]  # Error
    return {"key": "value"}  # Fixed

# Method override mismatch
class Base:
    def method(self, x: int) -> str: ...

class Derived(Base):
    def method(self, x: str) -> str: ...  # Error
    def method(self, x: int) -> str: ...  # Fixed
```

---

### Pattern Group 3: Optional/None Handling

| Error Code | Error Message | Fix Template |
|------------|---------------|--------------|
| `reportOptionalMemberAccess` | `Cannot access member for type "X \| None"` | Add None check before access |
| `reportOptionalSubscript` | `Cannot subscript object of type "X \| None"` | Add None check before subscript |
| `reportOptionalCall` | `Cannot call object of type "X \| None"` | Add None check before call |
| `reportOptionalIterable` | `Object of type "None" cannot be used as iterable` | Add None check before iteration |
| `reportOptionalContextManager` | `Object of type "None" cannot be used in with statement` | Add None check before with |

**Fix Template:**
```python
# Optional member access
def get_value(config: Settings | None) -> str:
    return config.value  # Error

def get_value(config: Settings | None) -> str:
    if not config:
        raise ValueError("Config required")
    return config.value  # Fixed

# Optional subscript
def get_item(data: dict | None, key: str) -> Any:
    return data[key]  # Error

def get_item(data: dict | None, key: str) -> Any:
    if not data:
        raise ValueError("Data required")
    return data[key]  # Fixed

# Optional call
def execute(func: Callable | None):
    return func()  # Error

def execute(func: Callable | None):
    if not func:
        raise ValueError("Function required")
    return func()  # Fixed
```

---

### Pattern Group 4: Generic Types

| Error Code | Error Message | Fix Template |
|------------|---------------|--------------|
| `reportMissingTypeArgument` | `Expected N type arguments for "X"` | Add type argument: `X[T]` |
| `reportInvalidTypeArguments` | `Type argument count mismatch` | Match expected argument count |
| `reportGeneralTypeIssues` | `Type "X[Y]" is incompatible with "X[Z]"` | Ensure generic types match |
| `reportInvariantTypeVar` | `Type "Y" cannot be assigned to TypeVar "T"` | Use correct bound/constraint |

**Fix Template:**
```python
# Missing type argument
items: list = []  # Error
items: list[str] = []  # Fixed

data: dict = {}  # Error
data: dict[str, int] = {}  # Fixed

# Type argument mismatch
T = TypeVar("T", bound=str)
value: T = 42  # Error
value: T = "string"  # Fixed

# Generic incompatibility
result: ServiceResult[list[Entity]] = ServiceResult.success(["string"])  # Error
entities = [Entity(name=n) for n in ["string"]]
result: ServiceResult[list[Entity]] = ServiceResult.success(entities)  # Fixed
```

---

### Pattern Group 5: Attribute/Method Access

| Error Code | Error Message | Fix Template |
|------------|---------------|--------------|
| `reportAttributeAccessIssue` | `Cannot access member "X" for type "Y"` | Check attribute exists on type |
| `reportUnknownMemberType` | `"X" is not a known member of "Y"` | Verify attribute name and type |
| `reportCallIssue` | `Cannot call "X"` | Ensure object is callable |
| `reportIndexIssue` | `Cannot subscript "X"` | Ensure object supports indexing |

**Fix Template:**
```python
# Wrong attribute name
result = service.get_data()
items = result.results  # Error: should be 'data'
items = result.data  # Fixed

# Type guard for union
def process(value: str | int):
    return value.strip()  # Error: int has no strip

def process(value: str | int) -> str:
    if isinstance(value, int):
        return str(value)
    return value.strip()  # Fixed

# Method not found
def similarity(vec: list[float], other: list[float]) -> float:
    return vec.cosine_similarity(other)  # Error

import numpy as np
def similarity(vec: list[float], other: list[float]) -> float:
    return float(np.dot(vec, other))  # Fixed
```

---

### Pattern Group 6: Import/Module

| Error Code | Error Message | Fix Template |
|------------|---------------|--------------|
| `reportMissingImports` | `Import "X" could not be resolved` | Fix import path or install package |
| `reportMissingTypeStubs` | `Stub file not found for "X"` | Install types-X or add type: ignore |
| `reportImportCycles` | `Import creates cycle` | Use TYPE_CHECKING guard |
| `reportPrivateImportUsage` | `"X" is not exported from module` | Import from correct public API |

**Fix Template:**
```python
# Missing import path
from src.domain.entities import Entity  # Error
from your_project.domain.entities import Entity  # Fixed

# Missing type stubs
import voyageai  # Error: no stubs
import voyageai  # type: ignore[import-untyped]  # Fixed

# Circular import
# file_a.py
from file_b import ClassB  # Error: creates cycle

# file_a.py (fixed)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from file_b import ClassB

# Private import
from fastapi._compat import PYDANTIC_V2  # Error: private
from fastapi import __version__  # Fixed: public API
```

---

## Pyright Configuration

### Project Configuration (pyrightconfig.json)

```json
{
  "include": ["src"],
  "exclude": [
    "**/__pycache__",
    "**/node_modules",
    ".venv",
    "build",
    "dist"
  ],
  "typeCheckingMode": "strict",
  "strictParameterNoneValue": true,
  "strictDictionaryInference": true,
  "strictListInference": true,
  "strictSetInference": true,
  "reportUnknownMemberType": "error",
  "reportUnknownArgumentType": "error",
  "reportUnknownVariableType": "error",
  "reportUnknownReturnType": "error",
  "reportMissingTypeStubs": "warning",
  "reportPrivateImportUsage": "error",
  "reportConstantRedefinition": "error",
  "reportIncompatibleMethodOverride": "error",
  "reportImportCycles": "error",
  "pythonVersion": "3.11",
  "pythonPlatform": "All"
}
```

### Adjusting Strictness

**Relaxing Specific Rules:**
```json
{
  "reportMissingTypeStubs": "none",  // Ignore missing stubs
  "reportUnknownArgumentType": "warning",  // Downgrade to warning
  "reportPrivateImportUsage": "none"  // Allow private imports
}
```

**File-Specific Overrides:**
```json
{
  "include": ["src"],
  "ignore": ["src/legacy"],  // Skip legacy code
  "typeCheckingMode": "strict"
}
```

---

## Advanced Type Annotations

### TypedDict for Structured Dicts

```python
from typing import TypedDict, NotRequired

# Basic TypedDict
class ChunkData(TypedDict):
    id: str
    content: str
    metadata: dict[str, str]

# With optional fields
class ExtendedChunkData(TypedDict):
    id: str
    content: str
    metadata: NotRequired[dict[str, str]]  # Optional

# Usage
chunk: ChunkData = {
    "id": "123",
    "content": "text",
    "metadata": {}
}
```

### Protocol for Structural Typing

```python
from typing import Protocol, runtime_checkable

# Define protocol
@runtime_checkable
class Repository(Protocol):
    def save(self, data: dict) -> ServiceResult[bool]:
        ...

    def find(self, id: str) -> ServiceResult[dict]:
        ...

# Implement implicitly (no inheritance needed)
class Neo4jRepository:
    def save(self, data: dict) -> ServiceResult[bool]:
        # Implementation
        pass

    def find(self, id: str) -> ServiceResult[dict]:
        # Implementation
        pass

# Type check
repo: Repository = Neo4jRepository()  # ✅ Works
```

### Generic Classes

```python
from typing import Generic, TypeVar

T = TypeVar("T")

class Container(Generic[T]):
    def __init__(self, value: T):
        self._value = value

    def get(self) -> T:
        return self._value

# Usage
str_container: Container[str] = Container("hello")
int_container: Container[int] = Container(42)

result: str = str_container.get()  # ✅ Type is str
```

### Literal Types for Constants

```python
from typing import Literal

# Define literal type
SearchType = Literal["semantic", "keyword", "hybrid"]

def search(query: str, search_type: SearchType) -> list[dict]:
    if search_type == "semantic":
        # Type checker knows search_type is exactly "semantic"
        pass
    elif search_type == "keyword":
        pass
    else:
        # Type checker knows search_type must be "hybrid"
        pass

# Usage
search("test", "semantic")  # ✅
search("test", "invalid")   # ❌ Error
```

### Overload for Multiple Signatures

```python
from typing import overload

@overload
def process(data: str) -> str: ...

@overload
def process(data: int) -> int: ...

@overload
def process(data: list[str]) -> list[str]: ...

def process(data: str | int | list[str]) -> str | int | list[str]:
    if isinstance(data, str):
        return data.upper()
    elif isinstance(data, int):
        return data * 2
    else:
        return [s.upper() for s in data]

# Type checker understands return type based on input
result1: str = process("hello")     # ✅
result2: int = process(42)          # ✅
result3: list[str] = process(["a"]) # ✅
result4: int = process("hello")     # ❌ Error
```

---

## Type Narrowing Techniques

### isinstance() Guards

```python
def process(value: str | int | None) -> str:
    if value is None:
        return "empty"
    elif isinstance(value, int):
        return str(value)
    else:
        # Type narrowed to str
        return value.upper()
```

### hasattr() Checks (Limited)

```python
def get_name(obj: object) -> str:
    if hasattr(obj, "name"):
        # Pyright doesn't always narrow type
        return obj.name  # Error: object has no attribute name
    return "unknown"

# Better: Use Protocol
class HasName(Protocol):
    name: str

def get_name(obj: HasName) -> str:
    return obj.name  # ✅
```

### Type Guards (Custom)

```python
from typing import TypeGuard

def is_entity(obj: object) -> TypeGuard[Entity]:
    return isinstance(obj, Entity) and hasattr(obj, "id")

def process(obj: object) -> str:
    if is_entity(obj):
        # Type narrowed to Entity
        return obj.id
    return "not an entity"
```

### assert for Type Narrowing

```python
def process(value: str | None) -> str:
    assert value is not None, "Value must not be None"
    # Type narrowed to str
    return value.upper()
```

---

## Common Antipatterns and Fixes

### Antipattern 1: Bare Any

```python
# ❌ BAD
def process(data: Any) -> Any:
    return data

# ✅ GOOD
from typing import TypeVar
T = TypeVar("T")

def process(data: T) -> T:
    return data
```

### Antipattern 2: Overusing cast()

```python
from typing import cast

# ❌ BAD - Hides actual type issue
def get_value(data: dict) -> str:
    return cast(str, data.get("key"))  # Might be None!

# ✅ GOOD
def get_value(data: dict) -> str:
    value = data.get("key")
    if not isinstance(value, str):
        raise ValueError("Invalid value type")
    return value
```

### Antipattern 3: Optional Parameters Without Defaults

```python
# ❌ BAD
def func(param: str | None):  # Missing default
    pass

# ✅ GOOD
def func(param: str | None = None):
    if param is None:
        raise ValueError("param required")
    # Use param
```

### Antipattern 4: Ignoring All Errors

```python
# ❌ BAD
# type: ignore  # Ignores all errors on line

# ✅ GOOD
# type: ignore[import-untyped]  # Specific error code
```

---

## Troubleshooting

### Problem: Pyright Reports False Positive

**Solution:** File bug or use specific ignore:
```python
# type: ignore[reportAttributeAccessIssue]  # TODO: pyright bug #1234
```

### Problem: Type Inference Not Working

**Solution:** Add explicit type annotation:
```python
# Before (inference fails)
result = complex_function()

# After
result: ServiceResult[dict] = complex_function()
```

### Problem: Circular Import in Type Annotations

**Solution:** Use TYPE_CHECKING guard:
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from other_module import OtherClass

def process(obj: "OtherClass") -> None:  # Forward reference
    pass
```

### Problem: Third-Party Library No Stubs

**Solution 1:** Install type stubs if available:
```bash
uv pip install types-requests
```

**Solution 2:** Use type: ignore:
```python
import unstubbed_library  # type: ignore[import-untyped]
```

**Solution 3:** Create local stub file:
```python
# stubs/unstubbed_library.pyi
def some_function(arg: str) -> int: ...
```

### Problem: Generic Type Too Complex

**Solution:** Use type alias:
```python
# Before
def process(data: dict[str, list[tuple[str, int]]]) -> dict[str, list[tuple[str, int]]]:
    pass

# After
DataType = dict[str, list[tuple[str, int]]]

def process(data: DataType) -> DataType:
    pass
```

---

## Integration with Quality Gates

### Running Pyright in CI/CD

```bash
#!/bin/bash
# scripts/check_types.sh

echo "Running pyright type checks..."
uv run pyright src/

if [ $? -eq 0 ]; then
    echo "✅ Type checking passed"
    exit 0
else
    echo "❌ Type checking failed"
    exit 1
fi
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pyright
        name: pyright
        entry: uv run pyright
        language: system
        types: [python]
        pass_filenames: false
```

### Quality Gate Integration

```bash
# scripts/check_all.sh
#!/bin/bash

uv run pyright src/ &  # Run in parallel with other checks
uv run ruff check src/ &
uv run pytest tests/ &

wait  # Wait for all checks to complete
```

---

## Project-Specific Type Rules

### Rule 1: No Optional Config Parameters

```python
# ❌ VIOLATION
class Service:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()

# ✅ COMPLIANT
class Service:
    def __init__(self, settings: Settings):
        if not settings:
            raise ValueError("Settings required")
        self.settings = settings
```

### Rule 2: ServiceResult for All Service Methods

```python
# ❌ VIOLATION
def get_data(self) -> dict | None:
    return self._fetch()

# ✅ COMPLIANT
def get_data(self) -> ServiceResult[dict]:
    data = self._fetch()
    if not data:
        return ServiceResult.failure("No data found")
    return ServiceResult.success(data)
```

### Rule 3: Explicit Generic Type Arguments

```python
# ❌ VIOLATION
items: list = []
data: dict = {}

# ✅ COMPLIANT
items: list[str] = []
data: dict[str, Any] = {}
```

### Rule 4: No Bare None Returns

```python
# ❌ VIOLATION
def find(self, id: str) -> Entity | None:
    return self._query(id)

# ✅ COMPLIANT
def find(self, id: str) -> ServiceResult[Entity]:
    entity = self._query(id)
    if not entity:
        return ServiceResult.failure("Entity not found")
    return ServiceResult.success(entity)
```

---

## Quick Reference Table

| Scenario | Pattern | Example |
|----------|---------|---------|
| Unknown return type | Add annotation | `def func() -> str:` |
| Optional parameter | Add None check | `if not param: raise ValueError()` |
| Missing generic arg | Add type parameter | `list[str]` |
| Type mismatch | Fix annotation | `result: ServiceResult[dict]` |
| Union type access | Use type guard | `if isinstance(x, str):` |
| Circular import | TYPE_CHECKING guard | `if TYPE_CHECKING: from ...` |
| Missing stubs | type: ignore | `import lib  # type: ignore` |
| Complex type | Use type alias | `DataType = dict[str, list[int]]` |

---

## Resources

- [Pyright Documentation](https://github.com/microsoft/pyright/blob/main/docs/README.md)
- [PEP 484 - Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [PEP 612 - Parameter Specification Variables](https://www.python.org/dev/peps/pep-0612/)
- [typing module docs](https://docs.python.org/3/library/typing.html)
- [Mypy Type System Reference](https://mypy.readthedocs.io/en/stable/type_system_reference.html)
