"""Value object template for creating immutable domain objects.

This template provides a starting point for creating frozen dataclass value objects
with validation, factory methods, and proper immutability guarantees.

Replace placeholders:
- {{VALUE_OBJECT_NAME}} - Your value object class name (e.g., EmailAddress, UserId)
- {{DOMAIN_CONCEPT}} - What domain concept this represents
- {{ENCAPSULATED_LOGIC}} - What logic/behavior is encapsulated
- {{FIELD_NAME}} - Primary field name (usually 'value')
- {{FIELD_TYPE}} - Type of the primary field
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class {{VALUE_OBJECT_NAME}}:
    """Immutable value object representing {{DOMAIN_CONCEPT}}.

    Encapsulates {{ENCAPSULATED_LOGIC}}.
    """

    {{FIELD_NAME}}: {{FIELD_TYPE}}

    def __post_init__(self) -> None:
        """Validate {{VALUE_OBJECT_NAME}} constraints.

        Raises:
            ValueError: If validation fails
        """
        # Validation: Empty check
        if not self.{{FIELD_NAME}}:
            raise ValueError("{{FIELD_NAME}} cannot be empty")

        # Validation: Format check (customize as needed)
        # Example: if not self.{{FIELD_NAME}}.matches_pattern():
        #     raise ValueError(f"Invalid format: {self.{{FIELD_NAME}}}")

        # Type coercion in frozen context (if needed)
        # Example: if not isinstance(self.{{FIELD_NAME}}, ExpectedType):
        #     object.__setattr__(self, "{{FIELD_NAME}}", ExpectedType(self.{{FIELD_NAME}}))

        # Normalization in frozen context (if needed)
        # Example: object.__setattr__(self, "{{FIELD_NAME}}", self.{{FIELD_NAME}}.lower())

    def __str__(self) -> str:
        """User-friendly string representation.

        Returns:
            The {{FIELD_NAME}} as a string
        """
        return str(self.{{FIELD_NAME}})

    def __repr__(self) -> str:
        """Developer-friendly representation.

        Returns:
            String showing class and {{FIELD_NAME}}
        """
        return f"{{VALUE_OBJECT_NAME}}('{self.{{FIELD_NAME}}}')"

    @classmethod
    def from_string(cls, value_str: str) -> "{{VALUE_OBJECT_NAME}}":
        """Create {{VALUE_OBJECT_NAME}} from string representation.

        Args:
            value_str: String to parse

        Returns:
            {{VALUE_OBJECT_NAME}} instance

        Raises:
            ValueError: If string format is invalid
        """
        return cls({{FIELD_NAME}}=value_str)

    @classmethod
    def from_dict(cls, data: dict) -> "{{VALUE_OBJECT_NAME}}":
        """Create {{VALUE_OBJECT_NAME}} from dictionary representation.

        Args:
            data: Dictionary with value object data

        Returns:
            {{VALUE_OBJECT_NAME}} instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If validation fails
        """
        return cls({{FIELD_NAME}}=data["{{FIELD_NAME}}"])

    def to_dict(self) -> dict:
        """Convert to dictionary representation.

        Returns:
            Dictionary with value object data
        """
        return {
            "{{FIELD_NAME}}": self.{{FIELD_NAME}},
            # Include computed properties or metadata if needed
        }

    # Optional: Add domain-specific methods

    # Example: Computed property
    # @property
    # def display_name(self) -> str:
    #     """Get display-friendly version."""
    #     return self.{{FIELD_NAME}}.title()

    # Example: Pattern matching
    # def matches_pattern(self, pattern: str) -> bool:
    #     """Check if {{FIELD_NAME}} matches a pattern."""
    #     import fnmatch
    #     return fnmatch.fnmatch(self.{{FIELD_NAME}}, pattern)

    # Example: Comparison
    # def is_similar_to(self, other: "{{VALUE_OBJECT_NAME}}") -> bool:
    #     """Check similarity with another instance."""
    #     return self.{{FIELD_NAME}}.lower() == other.{{FIELD_NAME}}.lower()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

# Example 1: Basic construction
# obj = {{VALUE_OBJECT_NAME}}({{FIELD_NAME}}="example")

# Example 2: Factory method construction
# obj = {{VALUE_OBJECT_NAME}}.from_string("example")

# Example 3: Dictionary deserialization
# data = {"{{FIELD_NAME}}": "example"}
# obj = {{VALUE_OBJECT_NAME}}.from_dict(data)

# Example 4: Dictionary serialization
# obj = {{VALUE_OBJECT_NAME}}({{FIELD_NAME}}="example")
# data = obj.to_dict()

# Example 5: Immutability guarantee
# obj = {{VALUE_OBJECT_NAME}}({{FIELD_NAME}}="example")
# obj.{{FIELD_NAME}} = "changed"  # Raises FrozenInstanceError
