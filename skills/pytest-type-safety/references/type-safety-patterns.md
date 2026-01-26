# Type Safety Patterns Reference

Comprehensive patterns for type-safe testing with pytest.

## Complete Type-Safe Test File Pattern

```python
from __future__ import annotations

from typing import Any, AsyncGenerator, Callable
from unittest.mock import AsyncMock, create_autospec
import pytest
from httpx import AsyncClient, ASGITransport

from app.domain.entities import Order, LineItem
from app.domain.value_objects import OrderId, ProductId, ProductTitle, Money
from app.application.use_cases import ExtractOrdersUseCase
from app.application.ports import ShopifyPort, PublisherPort
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
async def http_client() -> AsyncGenerator[AsyncClient, None]:
    """Typed async HTTP client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# Tests
class TestExtractOrdersUseCase:

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
```

## Type-Safe Parametrization

```python
from typing import NamedTuple

class OrderTestCase(NamedTuple):
    """Type-safe parametrization data."""
    order_id: str
    customer_name: str
    total: float


ORDER_TEST_CASES: list[OrderTestCase] = [
    OrderTestCase(order_id="1", customer_name="Alice", total=100.0),
    OrderTestCase(order_id="2", customer_name="Bob", total=200.0),
]


@pytest.mark.parametrize("test_case", ORDER_TEST_CASES)
def test_orders_typed(test_case: OrderTestCase) -> None:
    """Parametrized test with type safety."""
    order = create_test_order(
        order_id=test_case.order_id,
        customer_name=test_case.customer_name,
    )
    assert order.order_id.value == test_case.order_id
```

## Protocol-Based Mocking

```python
from typing import Protocol

class OrderRepository(Protocol):
    """Protocol defining repository interface."""
    
    async def create(self, data: dict[str, Any]) -> Order: ...
    async def get_by_id(self, order_id: str) -> Order | None: ...


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Type-safe mock using protocol."""
    mock = create_autospec(OrderRepository, instance=True)
    mock.create = AsyncMock(return_value=Order(...))
    mock.get_by_id = AsyncMock(return_value=None)
    return mock
```

## CI/CD Integration

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
