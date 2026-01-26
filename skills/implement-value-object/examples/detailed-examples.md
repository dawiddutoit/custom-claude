# Value Object Implementation Examples

Comprehensive examples demonstrating frozen dataclass patterns, validation, factory methods, and advanced techniques.

## Example 1: Simple String Value Object

Basic validation pattern for simple string-based value objects.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ProjectName:
    """Immutable project name value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate project name."""
        if not self.value:
            raise ValueError("Project name cannot be empty")
        if not self.value.isidentifier():
            raise ValueError(f"Invalid project name: {self.value}")

    def __str__(self) -> str:
        return self.value
```

**Usage:**
```python
# Valid creation
name = ProjectName(value="my_project")
print(name)  # "my_project"

# Invalid creation
try:
    ProjectName(value="")  # ValueError: Project name cannot be empty
except ValueError as e:
    print(f"Error: {e}")
```

## Example 2: Path Value Object with Normalization

Type coercion and normalization in frozen context using `object.__setattr__()`.

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class FilePath:
    """Immutable file path value object."""

    value: Path

    def __post_init__(self) -> None:
        """Validate and normalize path."""
        # Type coercion in frozen context
        if not isinstance(self.value, Path):
            object.__setattr__(self, "value", Path(self.value))

        # Normalization in frozen context
        object.__setattr__(self, "value", self.value.resolve())

    @classmethod
    def from_string(cls, path_str: str) -> "FilePath":
        """Create FilePath from string."""
        return cls(value=Path(path_str))

    @property
    def name(self) -> str:
        """Get file name."""
        return self.value.name
```

**Usage:**
```python
# Create from string
path1 = FilePath.from_string("/tmp/../home/file.txt")
print(path1.value)  # Normalized: /home/file.txt

# Create from Path
path2 = FilePath(value=Path("./file.txt"))
print(path2.name)  # "file.txt"
```

## Example 3: Hash Value Object with Factory

Computing values from content using factory methods.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class FileHash:
    """Immutable file hash value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate hash format."""
        if not self.value:
            raise ValueError("File hash cannot be empty")

        # Validate hexadecimal format
        try:
            int(self.value, 16)
        except ValueError:
            raise ValueError(f"Invalid hash format: {self.value}") from None

    @classmethod
    def from_content(cls, content: str) -> "FileHash":
        """Compute hash from content."""
        import xxhash
        hash_value = xxhash.xxh64(content.encode("utf-8")).hexdigest()
        return cls(value=hash_value)

    def short_hash(self, length: int = 8) -> str:
        """Get shortened hash for display."""
        return self.value[:length]
```

**Usage:**
```python
# Compute from content
content = "def hello(): return 'world'"
file_hash = FileHash.from_content(content)
print(file_hash.short_hash())  # "a1b2c3d4"

# Create directly
hash2 = FileHash(value="deadbeef123456789abcdef")
print(hash2.short_hash(12))  # "deadbeef1234"
```

## Example 4: Multi-Field Value Object with Validation

Complex constraints across multiple fields.

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Identity:
    """Immutable identity value object with multiple components."""

    value: str
    entity_type: str
    project_name: str
    file_path: Path | None = None

    def __post_init__(self) -> None:
        """Validate identity components."""
        if not self.value:
            raise ValueError("Identity value cannot be empty")
        if not self.entity_type:
            raise ValueError("Entity type cannot be empty")
        if not self.project_name:
            raise ValueError("Project name cannot be empty")

        # Validate entity_type format
        valid_types = ["file", "directory", "symbol", "dependency"]
        if self.entity_type not in valid_types:
            raise ValueError(f"Invalid entity type: {self.entity_type}")

        # Validate value format (colon-separated)
        parts = self.value.split(":")
        if len(parts) < 3:
            raise ValueError(f"Invalid identity format: {self.value}")

    @classmethod
    def from_components(
        cls,
        project_name: str,
        entity_type: str,
        name: str,
        file_path: Path | None = None,
    ) -> "Identity":
        """Create Identity from components."""
        components = [project_name, entity_type, name]
        if file_path:
            components.append(str(file_path))

        identity_value = ":".join(components)
        return cls(
            value=identity_value,
            entity_type=entity_type,
            project_name=project_name,
            file_path=file_path,
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        result = {
            "value": self.value,
            "entity_type": self.entity_type,
            "project_name": self.project_name,
        }
        if self.file_path:
            result["file_path"] = str(self.file_path)
        return result
```

**Usage:**
```python
# Create from components
identity = Identity.from_components(
    project_name="my_project",
    entity_type="file",
    name="main.py",
    file_path=Path("/src/main.py")
)
print(identity.value)  # "my_project:file:main.py:/src/main.py"

# Serialize
data = identity.to_dict()
print(data)  # {"value": "...", "entity_type": "file", ...}

# Invalid creation
try:
    Identity.from_components(
        project_name="my_project",
        entity_type="invalid_type",  # Not in valid_types
        name="test"
    )
except ValueError as e:
    print(f"Error: {e}")  # "Invalid entity type: invalid_type"
```

## Common Patterns

### Pattern: Computed Properties

Use `@property` for derived values that don't need to be stored:

```python
@dataclass(frozen=True)
class Identity:
    value: str

    @property
    def short_id(self) -> str:
        """Get shortened version of identity."""
        parts = self.value.split(":")
        return parts[-1] if parts else self.value
```

### Pattern: Type Coercion in Frozen Context

When you need to ensure type consistency:

```python
def __post_init__(self) -> None:
    """Ensure value is correct type."""
    if not isinstance(self.value, Path):
        object.__setattr__(self, "value", Path(self.value))
```

### Pattern: Validation with Custom Errors

Provide clear, actionable error messages:

```python
def __post_init__(self) -> None:
    """Validate with descriptive errors."""
    if not self.value:
        raise ValueError(f"{self.__class__.__name__} value cannot be empty")
    if len(self.value) < 3:
        raise ValueError(f"{self.__class__.__name__} must be at least 3 characters")
```

### Pattern: Serialization Support

Support dictionary conversion for persistence:

```python
def to_dict(self) -> dict:
    """Convert to dictionary for serialization."""
    return {
        "value": self.value,
        # Include any metadata or computed properties
    }

@classmethod
def from_dict(cls, data: dict) -> "YourValueObject":
    """Deserialize from dictionary."""
    return cls(value=data["value"])
```

## Testing Value Objects

Value objects should be tested for:

1. **Validation**: Ensure invalid inputs raise `ValueError`
2. **Immutability**: Verify frozen behavior
3. **Equality**: Test value-based equality (automatic with dataclass)
4. **Factory methods**: Test all construction paths
5. **Serialization**: Test to_dict/from_dict round-trip

```python
import pytest
from dataclasses import FrozenInstanceError

def test_value_object_validation():
    """Test validation raises on invalid input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        YourValueObject(value="")

def test_value_object_immutability():
    """Test frozen behavior."""
    obj = YourValueObject(value="test")
    with pytest.raises(FrozenInstanceError):
        obj.value = "changed"

def test_value_object_equality():
    """Test value-based equality."""
    obj1 = YourValueObject(value="test")
    obj2 = YourValueObject(value="test")
    assert obj1 == obj2
    assert obj1 is not obj2  # Different instances

def test_factory_method():
    """Test factory method construction."""
    obj = YourValueObject.from_string("test")
    assert obj.value == "test"

def test_serialization_round_trip():
    """Test to_dict/from_dict round-trip."""
    obj = YourValueObject(value="test")
    data = obj.to_dict()
    restored = YourValueObject.from_dict(data)
    assert restored == obj
```

## Advanced Patterns

### Multi-Step Validation

For complex validation logic:

```python
def __post_init__(self) -> None:
    """Multi-step validation."""
    self._validate_not_empty()
    self._validate_format()
    self._validate_business_rules()

def _validate_not_empty(self) -> None:
    """Validate value is not empty."""
    if not self.value:
        raise ValueError(f"{self.__class__.__name__} cannot be empty")

def _validate_format(self) -> None:
    """Validate value format."""
    if not self.value.startswith("prefix_"):
        raise ValueError(f"Invalid format: {self.value}")

def _validate_business_rules(self) -> None:
    """Validate business rules."""
    if len(self.value) > 100:
        raise ValueError("Value too long (max 100 characters)")
```

### Value Object Collections

Creating collections of value objects:

```python
@dataclass(frozen=True)
class Tags:
    """Immutable collection of tag values."""

    values: tuple[str, ...]

    def __post_init__(self) -> None:
        """Validate tags."""
        if not self.values:
            raise ValueError("Tags cannot be empty")

        # Ensure tuple (immutable)
        if not isinstance(self.values, tuple):
            object.__setattr__(self, "values", tuple(self.values))

        # Validate each tag
        for tag in self.values:
            if not tag or not tag.isidentifier():
                raise ValueError(f"Invalid tag: {tag}")

    @classmethod
    def from_list(cls, tags: list[str]) -> "Tags":
        """Create from list."""
        return cls(values=tuple(tags))

    def __contains__(self, tag: str) -> bool:
        """Check if tag exists."""
        return tag in self.values
```

### Nested Value Objects

Value objects containing other value objects:

```python
@dataclass(frozen=True)
class FullName:
    """Person's full name."""
    first: str
    last: str

@dataclass(frozen=True)
class Person:
    """Person entity with value object composition."""
    name: FullName
    email: EmailAddress

    @classmethod
    def create(cls, first: str, last: str, email: str) -> "Person":
        """Create person from primitives."""
        return cls(
            name=FullName(first=first, last=last),
            email=EmailAddress(value=email)
        )
```
