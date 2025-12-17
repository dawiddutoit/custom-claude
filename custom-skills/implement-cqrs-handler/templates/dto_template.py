"""Template for Data Transfer Object (DTO).

TEMPLATE VARIABLES:
- {{DTO_NAME}}: Your DTO class name (e.g., SearchResult, UserProfile)

USAGE:
1. Copy this template to application/dto/your_dto.py
2. Replace {{DTO_NAME}} with your DTO name (e.g., SearchResult)
3. Add your data fields
4. Implement to_dict() for serialization
5. Implement from_entity() for conversion from domain entities
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class {{DTO_NAME}}DTO:
    """Data transfer object for {{DTO_NAME}}.

    Carries data from application layer to interface layer.
    Contains only data, no business logic.
    DTOs are immutable and should be created from domain entities.
    """

    # Add your fields here
    # id: str
    # name: str
    # value: int
    # metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            # Add your fields here
            # "id": self.id,
            # "name": self.name,
            # "value": self.value,
            # "metadata": self.metadata,
        }

    @classmethod
    def from_entity(cls, entity) -> "{{DTO_NAME}}DTO":
        """Create DTO from domain entity.

        Args:
            entity: Domain entity to convert

        Returns:
            DTO instance populated from entity data
        """
        return cls(
            # Map entity attributes to DTO fields
            # id=entity.identity.value,
            # name=entity.name,
            # value=entity.value,
            # metadata=entity.metadata,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "{{DTO_NAME}}DTO":
        """Create DTO from dictionary.

        Args:
            data: Dictionary containing DTO data

        Returns:
            DTO instance populated from dictionary
        """
        return cls(
            # Extract fields from dictionary
            # id=data["id"],
            # name=data["name"],
            # value=data["value"],
            # metadata=data.get("metadata", {}),
        )
