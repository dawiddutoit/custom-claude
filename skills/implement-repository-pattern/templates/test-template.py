"""Unit tests for Neo4j{Name}Repository.

TEMPLATE VARIABLES:
- {{PROJECT_NAME}}: Your project package name (e.g., my_project, acme_system)
- {Name}: Repository name (e.g., User, Product)
- {name}: Lowercase name (e.g., user, product)
- {Entity}: Entity class name (e.g., User, Product)
- {entity}: Lowercase entity name (e.g., user, product)
- {entities}: Plural entity name (e.g., users, products)
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from {{PROJECT_NAME}}.infrastructure.neo4j.{name}_repository import (
    Neo4j{Name}Repository,
)
# Import domain models as needed
# from {{PROJECT_NAME}}.domain.models.{model} import {Model}


@pytest.fixture
def mock_driver():
    """Create mock Neo4j driver."""
    driver = AsyncMock()
    driver.execute_query = AsyncMock()
    return driver


@pytest.fixture
def settings(mock_settings):
    """Create settings fixture."""
    return mock_settings


@pytest.mark.asyncio
async def test_save_{entity}_success(mock_driver, settings):
    """Test successful {entity} save operation."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.return_value = ([], None, None)

    # Create test {entity}
    # {entity} = {Entity}(...)

    # Act
    result = await repo.save_{entity}({entity})

    # Assert
    assert result.is_success
    assert result.data is None
    mock_driver.execute_query.assert_called_once()


@pytest.mark.asyncio
async def test_save_{entity}_database_error(mock_driver, settings):
    """Test {entity} save with database error."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.side_effect = Exception("Connection failed")

    # Create test {entity}
    # {entity} = {Entity}(...)

    # Act
    result = await repo.save_{entity}({entity})

    # Assert
    assert result.is_failure
    assert "Connection failed" in result.error


@pytest.mark.asyncio
async def test_get_{entity}_success(mock_driver, settings):
    """Test retrieving {entity} by ID."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_record = {
        "e": {
            "id": "test-id",
            "project_name": "test-project",
            # Add other properties
        }
    }
    mock_driver.execute_query.return_value = (
        [MagicMock(**mock_record)],
        None,
        None,
    )

    # Act
    result = await repo.get_{entity}("test-id", "test-project")

    # Assert
    assert result.is_success
    assert result.data is not None
    # Add specific assertions about the {entity}


@pytest.mark.asyncio
async def test_get_{entity}_not_found(mock_driver, settings):
    """Test retrieving {entity} that doesn't exist."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.return_value = ([], None, None)

    # Act
    result = await repo.get_{entity}("nonexistent-id", "test-project")

    # Assert
    assert result.is_success
    assert result.data is None


@pytest.mark.asyncio
async def test_get_{entity}_database_error(mock_driver, settings):
    """Test {entity} retrieval with database error."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.side_effect = Exception("Database error")

    # Act
    result = await repo.get_{entity}("test-id", "test-project")

    # Assert
    assert result.is_failure
    assert "Database error" in result.error


@pytest.mark.asyncio
async def test_get_{entities}_by_project_success(mock_driver, settings):
    """Test retrieving all {entities} for a project."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_records = [
        {"e": {"id": "entity-1", "project_name": "test-project"}},
        {"e": {"id": "entity-2", "project_name": "test-project"}},
    ]
    mock_driver.execute_query.return_value = (
        [MagicMock(**record) for record in mock_records],
        None,
        None,
    )

    # Act
    result = await repo.get_{entities}_by_project("test-project")

    # Assert
    assert result.is_success
    assert len(result.data) == 2


@pytest.mark.asyncio
async def test_get_{entities}_by_project_empty(mock_driver, settings):
    """Test retrieving {entities} for project with no {entities}."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.return_value = ([], None, None)

    # Act
    result = await repo.get_{entities}_by_project("empty-project")

    # Assert
    assert result.is_success
    assert len(result.data) == 0


@pytest.mark.asyncio
async def test_delete_{entity}_success(mock_driver, settings):
    """Test successful {entity} deletion."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.return_value = ([], None, None)

    # Act
    result = await repo.delete_{entity}("test-id", "test-project")

    # Assert
    assert result.is_success
    mock_driver.execute_query.assert_called_once()


@pytest.mark.asyncio
async def test_delete_{entity}_database_error(mock_driver, settings):
    """Test {entity} deletion with database error."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.side_effect = Exception("Delete failed")

    # Act
    result = await repo.delete_{entity}("test-id", "test-project")

    # Assert
    assert result.is_failure
    assert "Delete failed" in result.error


@pytest.mark.asyncio
async def test_{entity}_exists_true(mock_driver, settings):
    """Test {entity} exists check returns True."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.return_value = (
        [{"exists": True}],
        None,
        None,
    )

    # Act
    result = await repo.{entity}_exists("test-id", "test-project")

    # Assert
    assert result.is_success
    assert result.data is True


@pytest.mark.asyncio
async def test_{entity}_exists_false(mock_driver, settings):
    """Test {entity} exists check returns False."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)
    mock_driver.execute_query.return_value = (
        [{"exists": False}],
        None,
        None,
    )

    # Act
    result = await repo.{entity}_exists("nonexistent-id", "test-project")

    # Assert
    assert result.is_success
    assert result.data is False


@pytest.mark.asyncio
async def test_constructor_validates_driver():
    """Test constructor rejects None driver."""
    # Arrange
    from {{PROJECT_NAME}}.config.settings import Settings

    settings = Settings()

    # Act & Assert
    with pytest.raises(ValueError, match="Neo4j driver is required"):
        Neo4j{Name}Repository(None, settings)


@pytest.mark.asyncio
async def test_constructor_validates_settings(mock_driver):
    """Test constructor rejects None settings."""
    # Act & Assert
    with pytest.raises(ValueError, match="Settings is required"):
        Neo4j{Name}Repository(mock_driver, None)


@pytest.mark.asyncio
async def test_close_succeeds(mock_driver, settings):
    """Test repository cleanup succeeds."""
    # Arrange
    repo = Neo4j{Name}Repository(mock_driver, settings)

    # Act & Assert (should not raise)
    await repo.close()
