---
name: pytest-type-safety
description: |
  Enforce type safety in all tests: type annotations for test functions and fixtures, mock autospec patterns, mypy configuration for tests, type-safe assertions, generic type handling in mocks. Includes protocol-based typing and cast patterns for complex scenarios.

  Use when: Writing type-safe tests, configuring mypy for test files, using protocols for mocks, enforcing type checking in CI/CD, or debugging type-related test issues.
allowed-tools: Read, Bash, Write
---

# Pytest Type Safety

## Purpose

Type safety in tests catches errors early and improves code quality. This skill provides patterns for enforcing strict types throughout your test suite.

## Quick Start

Add type annotations to every test function and fixture:

```python
from __future__ import annotations

from typing import Any, AsyncGenerator, Optional
from unittest.mock import AsyncMock
import pytest

from app.extraction.domain.entities import Order
from app.extraction.application.use_cases import ExtractOrdersUseCase

# ✅ GOOD: Type annotations on fixture
@pytest.fixture
def create_test_order() -> Any:  # Return type of factory function
    """Factory fixture with type hints."""
    def _create(order_id: str = "123") -> Order:
        return Order(...)
    return _create

# ✅ GOOD: Type annotations on test function
@pytest.mark.asyncio
async def test_extract_orders(
    create_test_order: Any,
    mock_gateway: AsyncMock,
) -> None:
    """Test function with full type safety."""
    use_case = ExtractOrdersUseCase(gateway=mock_gateway)
    result = await use_case.execute()
    assert result is not None
```

## Instructions

### Step 1: Add Type Annotations to All Test Functions

```python
from __future__ import annotations

import pytest
from app.extraction.domain.value_objects import ProductTitle


# ❌ BAD: No type annotations
def test_product_title():
    title = ProductTitle("Laptop")
    assert title.value == "Laptop"


# ✅ GOOD: Complete type annotations
def test_product_title() -> None:
    """Test product title creation."""
    title: ProductTitle = ProductTitle("Laptop")
    assert title.value == "Laptop"


# ✅ GOOD: Parametrized with type annotations
@pytest.mark.parametrize(
    "input_title,expected",
    [("Laptop", "Laptop"), ("Mouse", "Mouse")],
    ids=["laptop", "mouse"]
)
def test_valid_titles(input_title: str, expected: str) -> None:
    """Test title parametrization."""
    title = ProductTitle(input_title)
    assert title.value == expected
```

### Step 2: Type Annotate All Fixtures

```python
from __future__ import annotations

from typing import Any, AsyncGenerator, Callable
from unittest.mock import AsyncMock
import pytest

from app.extraction.domain.entities import Order, LineItem
from app.extraction.domain.value_objects import OrderId, ProductId, ProductTitle, Money


# ✅ GOOD: Factory fixture with return type
@pytest.fixture
def create_test_line_item() -> Callable[..., LineItem]:
    """Factory for creating line items."""
    def _create(
        product_id: str = "prod_1",
        title: str = "Test Product",
        quantity: int = 1,
        price: float = 99.99,
    ) -> LineItem:
        return LineItem(
            product_id=ProductId(product_id),
            product_title=ProductTitle(title),
            quantity=quantity,
            price=Money.from_float(price),
        )

    return _create


# ✅ GOOD: Async fixture with proper return type
@pytest.fixture
async def async_http_client() -> AsyncGenerator[AsyncClient, None]:
    """Async HTTP client fixture."""
    from httpx import AsyncClient
    from app.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# ✅ GOOD: Mock fixture with return type
@pytest.fixture
def mock_gateway() -> AsyncMock:
    """Mock gateway with proper type."""
    mock = AsyncMock()
    mock.fetch_orders.return_value = []
    return mock


# ✅ GOOD: Parametrized fixture with type
@pytest.fixture(params=["http://api1.com", "http://api2.com"])
def api_endpoint(request: pytest.FixtureRequest) -> str:
    """Parametrized endpoint fixture."""
    return request.param
```

### Step 3: Use Create_Autospec for Type-Safe Mocks

```python
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, create_autospec
import pytest

from app.extraction.application.ports import ShopifyPort


# ❌ BAD: Mock without autospec (allows typos)
def test_bad_mock(mocker: Any) -> None:
    """Mock without autospec allows invalid calls."""
    mock = mocker.Mock()
    mock.typo_method()  # No error! Dangerous!


# ✅ GOOD: Mock with autospec enforces interface
def test_with_autospec() -> None:
    """Mock with autospec catches typos."""
    mock = create_autospec(ShopifyPort, instance=True)
    # mock.typo_method() raises AttributeError (good!)
    mock.fetch_orders.return_value = []


# ✅ GOOD: Async autospec with proper type
@pytest.fixture
def typed_mock_gateway() -> AsyncMock:
    """Type-safe mock gateway."""
    mock = create_autospec(ShopifyPort, instance=True)
    mock.fetch_orders = AsyncMock(return_value=[])
    return mock
```

### Step 4: Configure Mypy for Test Files

```toml
# pyproject.toml

[tool.mypy]
python_version = "3.11"
strict = true
disallow_untyped_defs = true
disallow_any_unimported = true
disallow_untyped_calls = true
warn_unused_ignores = true
warn_redundant_casts = true
warn_unused_configs = true
show_error_codes = true

# Type check test files
[[tool.mypy.overrides]]
module = "tests.*"
# Still enforce type checking
disallow_untyped_defs = true
# But allow Any from pytest fixtures
disallow_any_unimported = false

# Allow Any for mocker fixture
[[tool.mypy.overrides]]
module = "pytest_mock"
ignore_missing_imports = true
```

### Step 5: Type-Safe Assertions

```python
from __future__ import annotations

from typing import Any
import pytest

from app.extraction.domain.entities import Order


def test_order_type_safe(create_test_order: Any) -> None:
    """Type-safe assertions with explicit types."""
    order: Order = create_test_order()

    # ✅ GOOD: Explicit type check
    assert isinstance(order, Order)
    assert len(order.line_items) > 0

    # ✅ GOOD: Type is known from variable
    assert order.customer_name is not None
    assert isinstance(order.customer_name, str)

    # ✅ GOOD: Compare with typed variables
    expected_id: str = "order_123"
    assert order.order_id.value == expected_id


def test_list_items_typed() -> None:
    """Type-safe list assertions."""
    items: list[str] = ["laptop", "mouse", "keyboard"]

    # ✅ GOOD: Check type and content
    assert isinstance(items, list)
    assert len(items) == 3
    assert all(isinstance(item, str) for item in items)
```

### Step 6: Use Typing.Cast for Complex Mocks

```python
from __future__ import annotations

from typing import cast, Any
from unittest.mock import AsyncMock
import pytest

from app.extraction.application.ports import ShopifyPort


def test_with_cast() -> None:
    """Use cast when mock type doesn't match interface."""
    # Create mock
    mock = AsyncMock()

    # Cast to interface type for type checker
    gateway: ShopifyPort = cast(ShopifyPort, mock)

    # Now type checker knows gateway has ShopifyPort interface
    # But we still have mock's flexibility at runtime
    gateway.fetch_orders.return_value = []
```

### Step 7: Use Protocols for Type-Safe Mocking

```python
from __future__ import annotations

from typing import Protocol, Any
from unittest.mock import AsyncMock, create_autospec
import pytest


class OrderRepository(Protocol):
    """Protocol defining repository interface."""

    async def create(self, data: dict[str, Any]) -> Order:
        """Create order."""
        ...

    async def get_by_id(self, order_id: str) -> Order | None:
        """Get order by ID."""
        ...


# ✅ GOOD: Mock respects protocol
@pytest.fixture
def mock_repository() -> AsyncMock:
    """Type-safe mock using protocol."""
    mock = create_autospec(OrderRepository, instance=True)
    mock.create = AsyncMock(return_value=Order(...))
    mock.get_by_id = AsyncMock(return_value=None)
    return mock


def test_with_typed_mock(mock_repository: AsyncMock) -> None:
    """Test using typed mock."""
    use_case = CreateOrderUseCase(repository=mock_repository)
    # Type checker knows mock_repository conforms to OrderRepository
```

### Step 8: Type Safe Parametrization

```python
from __future__ import annotations

from typing import NamedTuple
import pytest


class OrderTestCase(NamedTuple):
    """Type-safe parametrization data."""

    order_id: str
    customer_name: str
    total: float


# ✅ GOOD: Parametrize with typed data
ORDER_TEST_CASES: list[OrderTestCase] = [
    OrderTestCase(order_id="1", customer_name="Alice", total=100.0),
    OrderTestCase(order_id="2", customer_name="Bob", total=200.0),
]


@pytest.mark.parametrize(
    "test_case",
    ORDER_TEST_CASES,
    ids=[tc.customer_name for tc in ORDER_TEST_CASES]
)
def test_orders_typed(test_case: OrderTestCase) -> None:
    """Parametrized test with type safety."""
    order = create_test_order(
        order_id=test_case.order_id,
        customer_name=test_case.customer_name,
        total=test_case.total,
    )

    assert order.order_id.value == test_case.order_id
```

### Step 9: Type Check Test Files in CI/CD

```yaml
# GitHub Actions
name: Type Check

on: [push, pull_request]

jobs:
  type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Type check with mypy
        run: uv run mypy tests/

      - name: Type check with pyright
        run: uv run pyright tests/
```

### Step 10: Use Typing.Assert_Type for Verification

```python
from __future__ import annotations

from typing import assert_type
import pytest

from app.extraction.domain.entities import Order


def test_return_type_is_correct(create_test_order: Any) -> None:
    """Verify return types are correct."""
    order = create_test_order()

    # Compile-time check that order is Order
    assert_type(order, Order)

    # Runtime check
    assert isinstance(order, Order)
```

## Examples

### Example 1: Complete Type-Safe Test File

```python
from __future__ import annotations

from typing import Any, AsyncGenerator, Callable
from unittest.mock import AsyncMock, create_autospec
import pytest
from httpx import AsyncClient, ASGITransport

from app.extraction.domain.entities import Order, LineItem
from app.extraction.domain.value_objects import OrderId, ProductId, ProductTitle, Money
from app.extraction.application.use_cases import ExtractOrdersUseCase
from app.extraction.application.ports import ShopifyPort, PublisherPort
from app.main import app


# Fixtures
@pytest.fixture
def create_test_line_item() -> Callable[..., LineItem]:
    """Factory for line items."""
    def _create(
        product_id: str = "prod_1",
        title: str = "Product",
        quantity: int = 1,
        price: float = 99.99,
    ) -> LineItem:
        return LineItem(
            product_id=ProductId(product_id),
            product_title=ProductTitle(title),
            quantity=quantity,
            price=Money.from_float(price),
        )

    return _create


@pytest.fixture
def create_test_order(create_test_line_item: Callable[..., LineItem]) -> Callable[..., Order]:
    """Factory for orders."""
    def _create(
        order_id: str = "order_123",
        customer_name: str = "Test User",
    ) -> Order:
        items: list[LineItem] = [create_test_line_item()]
        total: float = sum(
            float(item.price.amount) * item.quantity for item in items
        )

        return Order(
            order_id=OrderId(order_id),
            created_at=datetime.now(),
            customer_name=customer_name,
            line_items=items,
            total_price=Money.from_float(total),
        )

    return _create


@pytest.fixture
def mock_shopify_gateway() -> AsyncMock:
    """Type-safe mock gateway."""
    mock = create_autospec(ShopifyPort, instance=True)
    mock.fetch_orders = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_event_publisher() -> AsyncMock:
    """Type-safe mock publisher."""
    mock = create_autospec(PublisherPort, instance=True)
    mock.publish_order = AsyncMock(return_value=None)
    mock.close = AsyncMock(return_value=None)
    return mock


@pytest.fixture
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    """Typed async HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# Tests
class TestExtractOrdersUseCase:
    """Type-safe test class."""

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        mock_shopify_gateway: AsyncMock,
        mock_event_publisher: AsyncMock,
    ) -> None:
        """Test with full type safety."""
        use_case: ExtractOrdersUseCase = ExtractOrdersUseCase(
            gateway=mock_shopify_gateway,
            publisher=mock_event_publisher,
        )

        result = await use_case.execute()

        assert result is not None
        assert isinstance(result.orders_count, int)
        assert result.orders_count >= 0
```

### Example 2: Type-Safe Test Data

```python
from dataclasses import dataclass
from typing import Any


@dataclass
class MockOrderData:
    """Typed mock order data."""

    order_id: str
    customer_name: str
    total: float
    line_count: int


MOCK_ORDERS: list[MockOrderData] = [
    MockOrderData(order_id="1", customer_name="Alice", total=100.0, line_count=1),
    MockOrderData(order_id="2", customer_name="Bob", total=200.0, line_count=2),
]


@pytest.mark.parametrize("order_data", MOCK_ORDERS)
def test_with_typed_data(order_data: MockOrderData) -> None:
    """Type-safe parametrized test."""
    order = create_test_order(
        order_id=order_data.order_id,
        customer_name=order_data.customer_name,
    )

    assert order.order_id.value == order_data.order_id
```

## Requirements

- Python 3.11+
- pytest >= 7.0
- mypy >= 1.7.0
- pyright >= 1.1.0 (optional)
- Unit test code with type annotations

## See Also

- [pytest-configuration](../pytest-configuration/SKILL.md) - mypy configuration
- [pytest-mocking-strategy](../pytest-mocking-strategy/SKILL.md) - create_autospec patterns
- [pytest-test-data-factories](../pytest-test-data-factories/SKILL.md) - Type-safe factories
- [PYTHON_UNIT_TESTING_BEST_PRACTICES.md](../../artifacts/2025-11-09/testing-research/PYTHON_UNIT_TESTING_BEST_PRACTICES.md) - Section: "Type Safety in Tests"
