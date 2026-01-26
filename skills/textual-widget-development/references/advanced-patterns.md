# Advanced Textual Widget Patterns

## Complete Widget Composition Patterns

### Complex Container Widget with Multiple Child Types

```python
from textual.app import ComposeResult
from textual.containers import Vertical, Horizontal, Grid
from textual.widgets import Static, Button, Label, Input, DataTable

class DashboardWidget(Vertical):
    """Complex dashboard with multiple widget types."""

    DEFAULT_CSS = """
    DashboardWidget {
        height: 100%;
        border: solid $primary;
    }

    DashboardWidget .header {
        height: 5;
        background: $boost;
        text-style: bold;
        content-align: center middle;
    }

    DashboardWidget .stats-grid {
        height: auto;
        grid-size: 3;
        grid-gutter: 1;
        padding: 1;
    }

    DashboardWidget .stat-card {
        height: 5;
        border: solid $accent;
        padding: 1;
    }

    DashboardWidget .chart-section {
        height: 1fr;
        border-top: solid $primary;
    }

    DashboardWidget .controls {
        height: 3;
        background: $surface;
        border-top: solid $primary;
    }
    """

    def __init__(self, title: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._title = title
        self._stats = {"users": 0, "orders": 0, "revenue": 0}

    def compose(self) -> ComposeResult:
        """Compose dashboard with header, stats, chart, and controls."""
        # Header
        yield Static(self._title, classes="header")

        # Stats grid with cards
        with Grid(classes="stats-grid"):
            yield Static(f"Users: {self._stats['users']}", classes="stat-card", id="stat-users")
            yield Static(f"Orders: {self._stats['orders']}", classes="stat-card", id="stat-orders")
            yield Static(f"Revenue: ${self._stats['revenue']}", classes="stat-card", id="stat-revenue")

        # Chart section with data table
        with Vertical(classes="chart-section"):
            yield Label("Recent Activity")
            yield DataTable(id="activity-table")

        # Control buttons
        with Horizontal(classes="controls"):
            yield Button("Refresh", id="btn-refresh", variant="primary")
            yield Button("Export", id="btn-export")
            yield Button("Settings", id="btn-settings")

    async def on_mount(self) -> None:
        """Initialize data table columns."""
        table = self.query_one("#activity-table", DataTable)
        table.add_column("Time", width=20)
        table.add_column("User", width=20)
        table.add_column("Action", width=40)

    async def update_stats(self, users: int, orders: int, revenue: float) -> None:
        """Update stat cards with new values."""
        self._stats = {"users": users, "orders": orders, "revenue": revenue}

        self.query_one("#stat-users", Static).update(f"Users: {users}")
        self.query_one("#stat-orders", Static).update(f"Orders: {orders}")
        self.query_one("#stat-revenue", Static).update(f"Revenue: ${revenue:.2f}")

    async def add_activity(self, time: str, user: str, action: str) -> None:
        """Add row to activity table."""
        table = self.query_one("#activity-table", DataTable)
        table.add_row(time, user, action)
```

### Dynamic Widget Mounting and Unmounting

```python
from textual.widgets import Static
from textual.containers import Vertical

class DynamicListWidget(Vertical):
    """Widget that dynamically adds/removes child widgets."""

    DEFAULT_CSS = """
    DynamicListWidget {
        height: auto;
        border: solid $primary;
    }

    DynamicListWidget .list-item {
        height: auto;
        padding: 1;
        border-bottom: solid $accent;
    }

    DynamicListWidget .list-item:hover {
        background: $boost;
    }
    """

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._items: dict[str, Static] = {}

    async def add_item(self, item_id: str, content: str) -> None:
        """Add item to list dynamically."""
        if item_id in self._items:
            # Update existing item
            self._items[item_id].update(content)
        else:
            # Create and mount new item
            item_widget = Static(content, classes="list-item", id=f"item-{item_id}")
            await self.mount(item_widget)
            self._items[item_id] = item_widget

    async def remove_item(self, item_id: str) -> None:
        """Remove item from list."""
        if item_id in self._items:
            widget = self._items.pop(item_id)
            await widget.remove()

    async def clear_items(self) -> None:
        """Remove all items."""
        for item_id in list(self._items.keys()):
            await self.remove_item(item_id)

    async def get_item_count(self) -> int:
        """Get number of items."""
        return len(self._items)
```

### Lazy Loading Widget Pattern

```python
import asyncio
from textual.widgets import Static, LoadingIndicator
from textual.containers import Vertical

class LazyLoadWidget(Vertical):
    """Widget that loads data lazily with progress indicator."""

    DEFAULT_CSS = """
    LazyLoadWidget {
        height: 100%;
    }

    LazyLoadWidget .content {
        height: 1fr;
        overflow: auto;
    }

    LazyLoadWidget .loading {
        height: 100%;
        align: center middle;
    }
    """

    def __init__(self, data_loader_func, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._data_loader = data_loader_func
        self._loading = False

    def compose(self) -> ComposeResult:
        """Compose with loading indicator initially."""
        with Vertical(classes="loading", id="loading-container"):
            yield LoadingIndicator()
            yield Static("Loading data...", id="loading-text")

    async def on_mount(self) -> None:
        """Load data after mount."""
        await self.load_data()

    async def load_data(self) -> None:
        """Load data asynchronously."""
        if self._loading:
            return

        self._loading = True

        try:
            # Show loading indicator
            loading_container = self.query_one("#loading-container")
            loading_container.display = True

            # Load data (simulated async operation)
            data = await self._data_loader()

            # Hide loading, show content
            await loading_container.remove()

            # Mount content container
            content_container = Vertical(classes="content", id="content-container")
            await self.mount(content_container)

            # Populate with loaded data
            for i, item in enumerate(data):
                item_widget = Static(item, id=f"item-{i}")
                await content_container.mount(item_widget)

                # Yield to event loop every 10 items for smooth rendering
                if i % 10 == 0:
                    await asyncio.sleep(0)

        except Exception as e:
            # Show error
            error_widget = Static(f"Error loading data: {e}", classes="error")
            await self.mount(error_widget)

        finally:
            self._loading = False
```

## Advanced Reactive Patterns

### Computed Properties with Watchers

```python
from textual.reactive import reactive, var
from textual.widgets import Static
from rich.text import Text

class ReactiveStatusWidget(Static):
    """Widget with reactive properties and computed rendering."""

    # Reactive properties
    status = reactive("idle")  # idle, running, success, error
    progress = reactive(0.0)   # 0.0 to 1.0
    message = reactive("")

    # Computed property
    status_color = var("")

    DEFAULT_CSS = """
    ReactiveStatusWidget {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    ReactiveStatusWidget .status-idle {
        color: $text;
    }

    ReactiveStatusWidget .status-running {
        color: $warning;
        text-style: bold;
    }

    ReactiveStatusWidget .status-success {
        color: $success;
        text-style: bold;
    }

    ReactiveStatusWidget .status-error {
        color: $error;
        text-style: bold;
    }
    """

    def watch_status(self, old_status: str, new_status: str) -> None:
        """React to status changes."""
        # Update computed property
        self.status_color = f"status-{new_status}"

        # Log status change
        self.log(f"Status changed: {old_status} -> {new_status}")

        # Trigger re-render
        self.refresh()

    def watch_progress(self, old_progress: float, new_progress: float) -> None:
        """React to progress changes."""
        # Trigger re-render when progress changes significantly
        if abs(new_progress - old_progress) >= 0.05:
            self.refresh()

    def render(self) -> Text:
        """Render widget with reactive properties."""
        text = Text()

        # Status indicator
        status_icon = {
            "idle": "○",
            "running": "●",
            "success": "✓",
            "error": "✗"
        }.get(self.status, "?")

        text.append(status_icon, style=self.status_color)
        text.append(" ")
        text.append(self.status.upper(), style=self.status_color)

        # Progress bar (if running)
        if self.status == "running":
            text.append("\n")
            bar_width = 40
            filled = int(self.progress * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            text.append(bar)
            text.append(f" {self.progress * 100:.0f}%")

        # Message
        if self.message:
            text.append("\n")
            text.append(self.message, style="dim")

        return text

    async def start_operation(self, message: str = "") -> None:
        """Start an operation."""
        self.status = "running"
        self.progress = 0.0
        self.message = message

    async def update_progress(self, progress: float, message: str = "") -> None:
        """Update operation progress."""
        self.progress = progress
        if message:
            self.message = message

    async def complete_operation(self, success: bool = True, message: str = "") -> None:
        """Complete an operation."""
        self.status = "success" if success else "error"
        self.progress = 1.0
        self.message = message
```

### Custom Message Bubbling Pattern

```python
from textual.message import Message
from textual import on
from textual.widgets import Static, Button
from textual.containers import Vertical, Horizontal

class ItemWidget(Static):
    """Widget that posts custom messages."""

    class ItemClicked(Message):
        """Posted when item is clicked."""

        def __init__(self, item_id: str, item_data: dict) -> None:
            super().__init__()
            self.item_id = item_id
            self.item_data = item_data

    class ItemDeleted(Message):
        """Posted when item delete is requested."""

        def __init__(self, item_id: str) -> None:
            super().__init__()
            self.item_id = item_id

    def __init__(self, item_id: str, label: str, data: dict, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._item_id = item_id
        self._label = label
        self._data = data

    def compose(self) -> ComposeResult:
        """Compose item with label and delete button."""
        with Horizontal():
            yield Static(self._label, classes="item-label")
            yield Button("×", classes="delete-btn", id=f"delete-{self._item_id}")

    @on(Button.Pressed, "#delete-*")
    async def on_delete_button_pressed(self, event: Button.Pressed) -> None:
        """Handle delete button press."""
        self.post_message(self.ItemDeleted(self._item_id))

    def on_click(self) -> None:
        """Handle item click."""
        self.post_message(self.ItemClicked(self._item_id, self._data))


class ItemListWidget(Vertical):
    """Parent widget that handles item messages."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._items: dict[str, ItemWidget] = {}

    async def add_item(self, item_id: str, label: str, data: dict) -> None:
        """Add item to list."""
        item_widget = ItemWidget(item_id, label, data)
        await self.mount(item_widget)
        self._items[item_id] = item_widget

    @on(ItemWidget.ItemClicked)
    async def on_item_clicked(self, message: ItemWidget.ItemClicked) -> None:
        """Handle item click message."""
        self.log(f"Item clicked: {message.item_id}")
        self.notify(f"Selected: {message.item_data.get('name', 'Unknown')}")

        # Can also post a higher-level message for parent containers
        self.post_message(ItemWidget.ItemClicked(message.item_id, message.item_data))

    @on(ItemWidget.ItemDeleted)
    async def on_item_deleted(self, message: ItemWidget.ItemDeleted) -> None:
        """Handle item delete message."""
        self.log(f"Item delete requested: {message.item_id}")

        if message.item_id in self._items:
            item = self._items.pop(message.item_id)
            await item.remove()
            self.notify(f"Deleted: {message.item_id}")
```

## Performance Optimization Patterns

### Virtual Scrolling for Large Lists

```python
from textual.widgets import Static
from textual.containers import VerticalScroll
from textual.geometry import Size

class VirtualListWidget(VerticalScroll):
    """Virtual scrolling list for large datasets."""

    ITEM_HEIGHT = 3  # Height of each item in lines

    def __init__(self, items: list[str], **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._items = items
        self._rendered_items: dict[int, Static] = {}
        self._viewport_start = 0
        self._viewport_end = 0

    def compose(self) -> ComposeResult:
        """Compose with placeholder for virtual items."""
        # Create spacer for unrendered items
        total_height = len(self._items) * self.ITEM_HEIGHT
        yield Static("", id="spacer-top")
        yield Static("", id="container")
        yield Static("", id="spacer-bottom")

    async def on_mount(self) -> None:
        """Initialize viewport."""
        await self.update_viewport()

    async def watch_scroll_y(self, old_y: float, new_y: float) -> None:
        """Update viewport on scroll."""
        await self.update_viewport()

    async def update_viewport(self) -> None:
        """Update visible items based on scroll position."""
        # Calculate visible range
        visible_height = self.size.height
        scroll_offset = self.scroll_y

        start_index = int(scroll_offset / self.ITEM_HEIGHT)
        end_index = min(
            start_index + int(visible_height / self.ITEM_HEIGHT) + 2,
            len(self._items)
        )

        if start_index == self._viewport_start and end_index == self._viewport_end:
            return  # No change

        self._viewport_start = start_index
        self._viewport_end = end_index

        # Update spacers
        spacer_top = self.query_one("#spacer-top", Static)
        spacer_bottom = self.query_one("#spacer-bottom", Static)
        container = self.query_one("#container", Static)

        top_spacer_height = start_index * self.ITEM_HEIGHT
        bottom_spacer_height = (len(self._items) - end_index) * self.ITEM_HEIGHT

        spacer_top.styles.height = top_spacer_height
        spacer_bottom.styles.height = bottom_spacer_height

        # Render visible items
        items_text = "\n".join(
            self._items[i] for i in range(start_index, end_index)
        )
        container.update(items_text)
```

### Debouncing User Input

```python
import asyncio
from textual.widgets import Input, Static
from textual.containers import Vertical

class SearchWidget(Vertical):
    """Search widget with debounced input."""

    def __init__(self, search_func, debounce_ms: int = 300, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._search_func = search_func
        self._debounce_ms = debounce_ms
        self._search_task: asyncio.Task | None = None

    def compose(self) -> ComposeResult:
        """Compose search input and results."""
        yield Input(placeholder="Search...", id="search-input")
        yield Static("", id="results")

    @on(Input.Changed, "#search-input")
    async def on_search_input_changed(self, event: Input.Changed) -> None:
        """Handle input changes with debouncing."""
        # Cancel previous search task if still running
        if self._search_task and not self._search_task.done():
            self._search_task.cancel()

        # Schedule new search after debounce delay
        self._search_task = asyncio.create_task(self._debounced_search(event.value))

    async def _debounced_search(self, query: str) -> None:
        """Execute search after debounce delay."""
        try:
            # Wait for debounce period
            await asyncio.sleep(self._debounce_ms / 1000)

            # Execute search
            results = await self._search_func(query)

            # Update results display
            results_widget = self.query_one("#results", Static)
            results_text = "\n".join(results) if results else "No results"
            results_widget.update(results_text)

        except asyncio.CancelledError:
            # Search was cancelled, ignore
            pass
```

## Testing Patterns

### Widget Unit Testing

```python
import pytest
from textual.app import App, ComposeResult
from textual.widgets import Static

class StatusWidget(Static):
    """Simple status widget."""

    def __init__(self, status: str, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._status = status

    def render(self) -> str:
        return f"Status: {self._status}"


@pytest.fixture
async def app():
    """Create test app."""
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield StatusWidget("active")

    app = TestApp()
    async with app.run_test() as pilot:
        yield pilot


async def test_status_widget_renders(app):
    """Test status widget renders correctly."""
    widget = app.app.query_one(StatusWidget)
    assert widget is not None
    assert "active" in widget.render()


async def test_status_widget_update(app):
    """Test status widget can be updated."""
    widget = app.app.query_one(StatusWidget)
    widget._status = "inactive"
    widget.refresh()
    assert "inactive" in widget.render()
```

### Widget Integration Testing

```python
import pytest
from textual.app import App, ComposeResult
from textual.widgets import Button, Static

class InteractiveWidget(Static):
    """Widget with button interaction."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._count = 0

    def compose(self) -> ComposeResult:
        yield Button("Click Me", id="click-btn")
        yield Static(f"Count: {self._count}", id="count-display")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "click-btn":
            self._count += 1
            count_display = self.query_one("#count-display", Static)
            count_display.update(f"Count: {self._count}")


async def test_button_interaction():
    """Test button click updates count."""
    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield InteractiveWidget()

    app = TestApp()
    async with app.run_test() as pilot:
        # Click button
        await pilot.click("#click-btn")
        await pilot.pause()

        # Verify count updated
        count_display = app.query_one("#count-display", Static)
        assert "Count: 1" in count_display.renderable

        # Click again
        await pilot.click("#click-btn")
        await pilot.pause()

        assert "Count: 2" in count_display.renderable
```
