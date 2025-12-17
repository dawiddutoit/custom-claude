# Reference - Instrument with OpenTelemetry

> **Note:** This reference uses generic placeholders for project-specific names. Replace `your_project` with your actual project package name in all import statements and configurations.

## Utility Scripts

For automated instrumentation, see these Python examples in the `examples/` directory:
- [add_tracing.py](../examples/add_tracing.py) - Auto-add OTEL instrumentation to Python service files
- [analyze_traces.py](../examples/analyze_traces.py) - Analyze trace coverage in your codebase
- [validate_instrumentation.py](../examples/validate_instrumentation.py) - Validate OTEL instrumentation patterns and find gaps

## OpenTelemetry Architecture

### Core Components

**OpenTelemetry (OTEL)** provides observability primitives for distributed systems:

1. **Tracing**: Tracks requests across service boundaries with trace_id and span_id
2. **Logging**: Structured logs with correlation IDs and contextual metadata
3. **Metrics**: (Not yet implemented in your_project)

### Trace Propagation

**Trace Context Format:**
```
trace_id: 128-bit identifier (hex: 32 characters)
span_id:  64-bit identifier (hex: 16 characters)
```

**Example:**
```
trace_id: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
span_id:  q7r8s9t0u1v2w3x4
```

**Logs display shortened IDs:**
```
[trace:a1b2c3d4 | span:q7r8s9t0]
```

---

## API Reference

### Core Functions

#### `initialize_otel_logger()`
Initialize OpenTelemetry logging system (call once at application startup).

```python
from your_project.core.monitoring import initialize_otel_logger

initialize_otel_logger(
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_otlp: bool = False,
    otlp_endpoint: str | None = None,
)
```

**Note:** Replace `your_project` with your actual project package name.

**Parameters:**
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `enable_console`: Enable console output (default: True)
- `enable_otlp`: Enable OTLP export for centralized logging (default: False)
- `otlp_endpoint`: OTLP collector endpoint (e.g., "http://localhost:4317")

**Raises:**
- `ValueError`: If configuration is invalid
- `RuntimeError`: If initialization fails

**Example:**
```python
# Development mode
initialize_otel_logger(log_level="DEBUG", enable_console=True)

# Production mode with OTLP
initialize_otel_logger(
    log_level="INFO",
    enable_console=False,
    enable_otlp=True,
    otlp_endpoint="http://otel-collector:4317"
)
```

---

#### `get_logger()`
Get a logger instance for a module.

```python
from your_project.core.monitoring import get_logger

logger = get_logger(name: str) -> logging.Logger
```

**Parameters:**
- `name`: Logger name (typically `__name__`)

**Returns:**
- Configured logger instance with OTEL integration

**Example:**
```python
logger = get_logger(__name__)
logger.info("Application started")
```

---

#### `@traced` Decorator
Automatically add OpenTelemetry tracing to functions/methods.

```python
from your_project.core.monitoring import traced

@traced
async def my_function(param: str) -> ServiceResult[Data]:
    # Function implementation
    pass
```

**Behavior:**
- Creates span with function's qualified name (e.g., `MyClass.my_method`)
- Captures function arguments as span attributes (primitives only)
- Works with both sync and async functions
- Propagates trace context to child operations

**Captured Attributes:**
- Primitive types (str, int, float, bool): Value
- None: String "None"
- Complex types: Type name (e.g., "Settings", "File")

**Example:**
```python
@traced
async def search_code(query: str, limit: int = 10) -> ServiceResult[list[Result]]:
    # Span attributes: query="async def", limit=10
    pass
```

---

#### `trace_span()` Context Manager
Create manual span for fine-grained tracing within a method.

```python
from your_project.core.monitoring import trace_span

with trace_span(span_name: str, **attributes) as span:
    # Operation to trace
    span.set_attribute(key: str, value: str | int | float | bool)
```

**Parameters:**
- `span_name`: Descriptive name for the operation
- `**attributes`: Initial span attributes (key-value pairs)

**Returns:**
- OpenTelemetry span object

**Span Methods:**
- `span.set_attribute(key, value)`: Add attribute to span
- `span.is_recording()`: Check if span is active
- `span.get_span_context()`: Get trace/span IDs

**Example:**
```python
with trace_span("database_query", operation="SELECT", table="files") as span:
    results = await db.query(sql)
    span.set_attribute("row_count", len(results))
    span.set_attribute("query_time_ms", elapsed)
```

---

#### `correlation_context()` Context Manager
Create correlation context for tracking related operations.

```python
from your_project.core.monitoring import correlation_context

with correlation_context(correlation_id: str | None = None) as cid:
    # All logs within this context include same correlation_id
    pass
```

**Parameters:**
- `correlation_id`: Optional custom ID (auto-generated UUID4 if not provided)

**Returns:**
- Correlation ID being used

**Behavior:**
- Adds `correlation_id` to all logs within context
- Automatically cleaned up when context exits
- Propagated to child operations

**Example:**
```python
with correlation_context() as cid:
    logger.info(f"Starting batch processing (correlation_id: {cid})")
    for item in items:
        await process_item(item)  # All logs include same cid
    logger.info("Batch processing complete")
```

---

#### `add_context()` / `clear_context()`
Manually manage baggage context.

```python
from your_project.core.monitoring import add_context, clear_context

add_context(key: str, value: str) -> None
clear_context(key: str | None = None) -> None
```

**Parameters:**
- `key`: Context key (e.g., "user_id", "operation_id")
- `value`: Context value (string)

**Behavior:**
- `add_context()`: Add key-value to all subsequent logs
- `clear_context(key)`: Remove specific key
- `clear_context()`: Remove all context

**Example:**
```python
add_context("user_id", "user-123")
add_context("session_id", "sess-456")

logger.info("User action")
# Output: [...] [user_id=user-123 | session_id=sess-456] - User action

clear_context("session_id")  # Remove session_id
clear_context()  # Remove all context
```

---

### Advanced Configuration

#### `OTELConfiguration` Class
Configuration object for OTEL initialization.

```python
from your_project.core.monitoring.otel_configuration import OTELConfiguration

config = OTELConfiguration(
    service_name: str = "your_project",
    service_version: str = "1.0.0",
    log_level: str = "INFO",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_otlp: bool = False,
    otlp_endpoint: str | None = None,
    log_dir: Path = Path("logs"),
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
)
```

**File Rotation:**
- Default: 10MB per file, 5 backup files
- Total storage: ~50MB logs retained

---

## Log Formatting

### Standard Log Format

```
%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s
```

**With OTEL Context:**
```
2025-10-18 14:30:45 - [trace:a1b2c3d4 | span:e5f6g7h8] - module.name - INFO ℹ️  - [file.py:42] - method() - Log message
```

**Components:**
1. `2025-10-18 14:30:45`: Timestamp (local timezone)
2. `[trace:a1b2c3d4 | span:e5f6g7h8]`: Correlation context (optional)
3. `module.name`: Logger name
4. `INFO ℹ️ `: Log level with emoji
5. `[file.py:42]`: Source location
6. `method()`: Function name
7. `Log message`: Actual message

---

### Emoji Enhancement

**Log Level Emojis:**
- 🔴 CRITICAL/ERROR
- ⚠️  WARNING
- ℹ️  INFO
- 🔍 DEBUG

**Operation Emojis:**
- 🚀 Initialization
- ▶️  Starting
- ⚙️  Processing/Configuration
- 📄 File/Parsing
- 💾 Database/Neo4j
- 🔎 Query
- 🎯 Embedding
- ✅ Success/Complete
- ❌ Failure
- 📍 Monitoring/Tracking

**Example:**
```
INFO ℹ️  🚀 - Initializing service
DEBUG 🔍 📄 - Parsing file structure
INFO ℹ️  💾 - Storing in Neo4j
INFO ℹ️  ✅ - Operation complete
```

---

## Performance Considerations

### Trace Span Overhead

**Minimal overhead per span:**
- Span creation: ~0.1-0.5ms
- Attribute setting: ~0.01ms per attribute
- Context propagation: ~0.05ms

**Best Practices:**
1. Use `@traced` on public methods (Commands, Queries, Services)
2. Add manual spans for expensive operations (>10ms)
3. Avoid spans in tight loops (use batch operations instead)

**Good:**
```python
@traced
async def batch_process(self, items: list[str]) -> ServiceResult[None]:
    with trace_span("batch_operation", item_count=len(items)) as span:
        results = await self._process_all(items)  # Single span for batch
        span.set_attribute("processed", len(results))
```

**Bad:**
```python
async def batch_process(self, items: list[str]) -> ServiceResult[None]:
    for item in items:  # DON'T do this
        with trace_span("process_item", item=item):
            await self._process(item)  # Creates 1000s of spans
```

---

### Log Volume Management

**Log Levels:**
- `DEBUG`: Very verbose, development only (~1000+ logs/operation)
- `INFO`: Milestones and significant events (~10-50 logs/operation)
- `WARNING`: Degraded conditions (~1-5 logs/operation)
- `ERROR`: Failures requiring attention (~0-2 logs/operation)

**Production Recommendation:**
- Default: `INFO`
- Debugging: `DEBUG` (temporarily)
- High-traffic: `WARNING` (reduce volume)

---

## Distributed Tracing

### Trace Propagation Across Services

**Automatic Propagation:**
The `@traced` decorator automatically propagates trace context to:
1. Nested function calls within same service
2. Database queries (via instrumented drivers)
3. HTTP requests (if instrumented)

**Manual Propagation:**
For external service calls, use OTEL context:
```python
from opentelemetry import context, trace

current_context = context.get_current()
span = trace.get_current_span()

# Extract trace headers for HTTP request
headers = {
    "traceparent": f"00-{span.trace_id}-{span.span_id}-01"
}

response = await http_client.post(url, headers=headers)
```

---

### OTLP Export (Optional)

**Enable OTLP for centralized logging:**
```python
initialize_otel_logger(
    enable_otlp=True,
    otlp_endpoint="http://localhost:4317"
)
```

**Compatible Backends:**
- Jaeger (distributed tracing UI)
- Zipkin (distributed tracing UI)
- Prometheus (metrics)
- Grafana Loki (log aggregation)
- OpenTelemetry Collector (vendor-neutral)

**Docker Compose Example:**
```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # UI
      - "4317:4317"    # OTLP gRPC
      - "4318:4318"    # OTLP HTTP
```

**Access Jaeger UI:**
```
http://localhost:16686
```

---

## Testing with OTEL

### Unit Testing with Mocked OTEL

```python
from unittest.mock import patch
import pytest

@pytest.mark.asyncio
async def test_service_with_tracing():
    with patch("your_project.core.monitoring.trace.get_tracer"):
        service = MyService()
        result = await service.operation()
        assert result.success
```

### Integration Testing with OTEL Enabled

```python
from your_project.core.monitoring import initialize_otel_logger

@pytest.fixture(scope="session", autouse=True)
def setup_otel():
    initialize_otel_logger(log_level="DEBUG")

@pytest.mark.asyncio
async def test_full_stack_tracing():
    # OTEL is initialized, traces will be captured
    result = await mcp_tool.search_code(query="async def")
    assert result["success"]
```

---

## Troubleshooting

### Issue: Logs Missing Trace IDs

**Symptoms:**
Logs don't show `[trace:... | span:...]`

**Diagnosis:**
1. Check if OTEL initialized: `logger.handlers` should include `LoggingHandler`
2. Verify `@traced` decorator applied to method
3. Ensure operation runs within traced context

**Solution:**
```python
# Ensure initialization before any logging
from your_project.core.monitoring import initialize_otel_logger
initialize_otel_logger()

# Apply @traced to method
@traced
async def my_method(self):
    logger.info("This will have trace IDs")
```

---

### Issue: Span Attributes Not Visible

**Symptoms:**
Custom attributes don't appear in traces

**Diagnosis:**
Attributes must be set within span context, and OTLP must be enabled

**Solution:**
```python
with trace_span("operation") as span:
    span.set_attribute("key", "value")  # Must be inside context

# Enable OTLP to export spans
initialize_otel_logger(enable_otlp=True, otlp_endpoint="http://localhost:4317")
```

---

### Issue: High Log Volume in Production

**Symptoms:**
Log files grow too large, disk space issues

**Diagnosis:**
Log level too verbose (DEBUG) or too many INFO logs

**Solution:**
```python
# Reduce log level in production
initialize_otel_logger(log_level="WARNING")

# Or dynamically adjust
from your_project.core.monitoring import set_log_level
set_log_level("WARNING")

# Increase file rotation settings
config = OTELConfiguration(
    max_bytes=50 * 1024 * 1024,  # 50MB per file
    backup_count=10,  # Keep 10 backups
)
```

---

## Advanced Patterns

### Pattern 1: Custom Trace Samplers
Control which traces are recorded (reduce overhead):

```python
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatio

# Sample 10% of traces
sampler = ParentBasedTraceIdRatio(0.1)
tracer_provider = TracerProvider(sampler=sampler)
```

---

### Pattern 2: Structured Logging with Extra Fields
Add custom fields to log records:

```python
logger.info(
    "Processing completed",
    extra={
        "duration_ms": 123,
        "item_count": 50,
        "cache_hit": True,
    }
)
```

**Note:** OTEL automatically includes trace_id, span_id as extra fields.

---

### Pattern 3: Exception Tracking in Spans
Capture exceptions within spans:

```python
with trace_span("risky_operation") as span:
    try:
        result = await self._risky_call()
    except Exception as e:
        span.set_attribute("error", True)
        span.set_attribute("error_message", str(e))
        logger.error(f"Operation failed: {str(e)}")
        raise
```

---

## Project-Specific Guidelines

### Clean Architecture Layer Guidelines

**Domain Layer:**
- ❌ No OTEL imports in domain models/values
- ❌ No logging in domain entities
- ✅ Domain remains pure business logic

**Application Layer:**
- ✅ `@traced` on all Command/Query handlers
- ✅ Logger at module level
- ✅ Manual spans for multi-step operations

**Infrastructure Layer:**
- ✅ `@traced` on repository methods
- ✅ Manual spans for database operations
- ✅ Span attributes for query performance

**Interface Layer:**
- ✅ `@traced` on all MCP tools
- ✅ Request/response logging
- ✅ Correlation context for request tracking

---

### ServiceResult Pattern Integration

Always log before returning ServiceResult:

```python
@traced
async def operation(self) -> ServiceResult[Data]:
    try:
        result = await self._execute()
        logger.info("Operation completed successfully")
        return ServiceResult.ok(result)
    except Exception as e:
        logger.error(f"Operation failed: {str(e)}")
        return ServiceResult.fail(str(e))
```

---

### Fail-Fast Principle

All OTEL imports at module top (no try/except ImportError):

```python
# ✅ CORRECT
from your_project.core.monitoring import get_logger, traced

logger = get_logger(__name__)

# ❌ WRONG
try:
    from your_project.core.monitoring import get_logger
except ImportError:
    logger = logging.getLogger(__name__)
```

---

## See Also

- [SKILL.md](../SKILL.md) - Main skill documentation
- [examples/examples.md](../examples/examples.md) - Comprehensive examples
- [ARCHITECTURE.md](${PROJECT_ROOT}/ARCHITECTURE.md) - Clean Architecture
- OpenTelemetry Python Docs: https://opentelemetry.io/docs/languages/python/
- Core monitoring module: `src/your_project/core/monitoring/`
