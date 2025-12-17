"""Repository interface for {purpose}.

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {Name}: Repository name (e.g., User, Product)
- {name}: Lowercase name (e.g., user, product)
- {Entity}: Entity class name (e.g., User, Product)
- {entity}: Lowercase entity name (e.g., user, product)
- {entities}: Plural entity name (e.g., users, products)

This module defines the {Name}Repository port following Clean Architecture principles.
This is a port (interface) that will be implemented by adapters in the infrastructure layer.
"""

from abc import ABC, abstractmethod

from {{PROJECT_NAME}}.domain.common import ServiceResult
# Import domain models as needed
# from {{PROJECT_NAME}}.domain.models.{model} import {Model}


class {Name}Repository(ABC):
    """Port for {purpose} storage and retrieval.

    This interface defines the contract for {brief description of operations}.
    Concrete implementations will be provided in the infrastructure layer
    (e.g., Neo4j{Name}Repository).
    """

    @abstractmethod
    async def save_{entity}(self, {entity}: {Entity}) -> ServiceResult[None]:
        """Save or update {entity}.

        Args:
            {entity}: {Entity} entity to save

        Returns:
            ServiceResult[None]: Success if saved, Failure on database errors
        """
        pass

    @abstractmethod
    async def get_{entity}(
        self, {entity}_id: str, project_name: str
    ) -> ServiceResult[{Entity} | None]:
        """Retrieve {entity} by ID.

        Args:
            {entity}_id: Unique identifier for the {entity}
            project_name: Name of the project

        Returns:
            ServiceResult[{Entity} | None]: Success with {Entity} if found,
                                            Success with None if not found,
                                            Failure on database errors
        """
        pass

    @abstractmethod
    async def get_{entities}_by_project(
        self, project_name: str
    ) -> ServiceResult[list[{Entity}]]:
        """Retrieve all {entities} for a project.

        Args:
            project_name: Name of the project

        Returns:
            ServiceResult[list[{Entity}]]: Success with list of {Entity} entities
                                           (empty list if none found),
                                           Failure on database errors
        """
        pass

    @abstractmethod
    async def delete_{entity}(
        self, {entity}_id: str, project_name: str
    ) -> ServiceResult[None]:
        """Delete {entity}.

        Args:
            {entity}_id: Unique identifier for the {entity}
            project_name: Name of the project

        Returns:
            ServiceResult[None]: Success if deleted, Failure on database errors
        """
        pass

    @abstractmethod
    async def {entity}_exists(
        self, {entity}_id: str, project_name: str
    ) -> ServiceResult[bool]:
        """Check if {entity} exists.

        Args:
            {entity}_id: Unique identifier for the {entity}
            project_name: Name of the project

        Returns:
            ServiceResult[bool]: Success with True if exists, False otherwise,
                                 Failure on database errors
        """
        pass
