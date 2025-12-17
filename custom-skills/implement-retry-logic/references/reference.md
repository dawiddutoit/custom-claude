# Reference - Implement Retry Logic

## Python Example Scripts

The following utility scripts demonstrate practical usage:

- [add_retry_logic.py](../examples/add_retry_logic.py) - Adds retry logic to async service methods with exponential backoff
- [analyze_retryable_operations.py](../examples/analyze_retryable_operations.py) - Analyzes codebase for operations needing retry logic
- [validate_retry_patterns.py](../examples/validate_retry_patterns.py) - Validates retry logic implementations against best practices

---

## Retry Patterns

### Exponential Backoff Formula

**Standard Formula**:
```
delay = min(base_delay * 2^attempt, max_delay)
```

**With Jitter (Recommended)**:
```
delay = min(base_delay * 2^attempt, max_delay)
jitter = delay * 0.2 * (2 * random() - 1)  # ±20%
final_delay = max(min_delay, delay + jitter)
```

**Parameters**:
- `base_delay`: Initial delay (typically 1.0s)
- `attempt`: Current retry attempt (0-based)
- `max_delay`: Maximum delay cap (typically 30s)
- `min_delay`: Minimum delay floor (typically 0.1s)

**Example Progression**:
```
Attempt 0: 1.0s  ± 0.2s  = 0.8-1.2s
Attempt 1: 2.0s  ± 0.4s  = 1.6-2.4s
Attempt 2: 4.0s  ± 0.8s  = 3.2-4.8s
Attempt 3: 8.0s  ± 1.6s  = 6.4-9.6s
Attempt 4: 16.0s ± 3.2s  = 12.8-19.2s
Attempt 5: 30.0s ± 6.0s  = 24.0-30.0s (capped)
```

---

### Why Jitter?

**Problem**: Without jitter, all clients retry at same time (thundering herd).

**Scenario**:
```
Service crashes at 10:00:00
1000 clients all fail simultaneously
Without jitter: All retry at 10:00:01, 10:00:03, 10:00:07...
Result: Synchronized retry storm overwhelms recovering service
```

**Solution**: Add randomness (jitter)
```
With ±20% jitter:
Client 1 retries: 0.9s, 1.8s, 3.5s, 7.2s...
Client 2 retries: 1.1s, 2.3s, 4.1s, 8.4s...
Client 3 retries: 0.8s, 2.0s, 3.9s, 7.8s...
Result: Retries spread over time, service recovers gracefully
```

**Implementation**:
```python
import time

def _calculate_backoff_delay(self, attempt: int) -> float:
    """Calculate exponential backoff with jitter."""
    base_delay = self.settings.retry_delay

    # Exponential backoff
    delay = min(base_delay * (2 ** attempt), 30.0)

    # Jitter using fractional seconds from time.time()
    # time.time() % 1 gives 0.0-1.0 range
    # 2 * (time.time() % 1) - 1 gives -1.0 to +1.0 range
    jitter = delay * 0.2 * (2 * (time.time() % 1) - 1)

    # Ensure minimum 0.1s delay
    return max(0.1, delay + jitter)
```

**Why use `time.time()` for jitter?**
- Available in Python standard library
- Provides sufficient randomness for jitter
- No need for `random` module import
- Fractional seconds are effectively random

---

## Error Classification

### HTTP Status Codes

**Retriable (5xx, 429, 408)**:
```python
retriable_status_codes = {
    408,  # Request Timeout
    429,  # Too Many Requests (rate limit)
    500,  # Internal Server Error
    502,  # Bad Gateway
    503,  # Service Unavailable
    504,  # Gateway Timeout
}
```

**Non-Retriable (4xx except 429, 408)**:
```python
permanent_status_codes = {
    400,  # Bad Request (malformed)
    401,  # Unauthorized (bad credentials)
    403,  # Forbidden (insufficient permissions)
    404,  # Not Found (resource doesn't exist)
    405,  # Method Not Allowed
    409,  # Conflict (version mismatch)
    422,  # Unprocessable Entity (validation failed)
}
```

**Special Cases**:
- **429 Rate Limited**: Use `Retry-After` header if available
- **503 Service Unavailable**: May include `Retry-After` header
- **408 Request Timeout**: Retriable but consider increasing timeout

---

### Exception Types

**Retriable Exceptions**:
```python
retriable_exceptions = (
    # Network errors
    aiohttp.ClientConnectionError,
    aiohttp.ServerDisconnectedError,
    ConnectionError,
    ConnectionRefusedError,
    ConnectionResetError,

    # Timeouts
    asyncio.TimeoutError,
    TimeoutError,
    aiohttp.ServerTimeoutError,

    # DNS errors
    aiohttp.ClientConnectorError,
)
```

**Non-Retriable Exceptions**:
```python
permanent_exceptions = (
    # Validation errors
    ValueError,
    TypeError,
    KeyError,
    AttributeError,

    # Syntax errors
    SyntaxError,

    # JSON errors
    json.JSONDecodeError,

    # Authentication errors
    aiohttp.ClientResponseError,  # If 4xx (except 429)
)
```

**Classification Function**:
```python
def _is_retriable_error(
    self,
    error: Exception,
    status_code: int | None = None
) -> bool:
    """Classify error as retriable or permanent."""

    # Check HTTP status first
    if status_code:
        if status_code == 429 or status_code == 408:
            return True
        if 500 <= status_code < 600:
            return True
        if 400 <= status_code < 500:
            return False

    # Check exception type
    if isinstance(error, retriable_exceptions):
        return True

    if isinstance(error, permanent_exceptions):
        return False

    # Default: fail fast (not retriable)
    return False
```

---

## Configuration Patterns

### Settings Structure

**Neo4j Retry Configuration**:
```python
@dataclass
class Neo4jSettings:
    """Neo4j connection and retry settings."""

    # Connection settings
    uri: str
    username: str
    password: str
    database: str

    # Retry configuration
    max_retries: int = 3
    initial_retry_delay: float = 1.0
    retry_delay_multiplier: float = 2.0
    max_retry_delay: float = 30.0

    @classmethod
    def from_env(cls) -> "Neo4jSettings":
        return cls(
            uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            username=os.getenv("NEO4J_USERNAME", "neo4j"),
            password=os.getenv("NEO4J_PASSWORD", ""),
            database=os.getenv("NEO4J_DATABASE", "neo4j"),
            max_retries=int(float(os.getenv("NEO4J_MAX_RETRIES", "3"))),
            initial_retry_delay=float(os.getenv("NEO4J_INITIAL_RETRY_DELAY", "1.0")),
            retry_delay_multiplier=float(os.getenv("NEO4J_RETRY_DELAY_MULTIPLIER", "2.0")),
            max_retry_delay=float(os.getenv("NEO4J_MAX_RETRY_DELAY", "30.0")),
        )
```

**Embedding Service Retry Configuration**:
```python
@dataclass
class EmbeddingSettings:
    """Embedding service settings."""

    # Service settings
    api_url: str
    model: str

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0

    @classmethod
    def from_env(cls) -> "EmbeddingSettings":
        return cls(
            api_url=os.getenv("EMBEDDING_API_URL", "http://localhost:7997"),
            model=os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
            max_retries=int(os.getenv("EMBEDDING_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("EMBEDDING_RETRY_DELAY", "1.0")),
        )
```

**Generic Retry Configuration**:
```python
@dataclass
class RetrySettings:
    """Generic retry configuration."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    min_delay: float = 0.1
    jitter_factor: float = 0.2  # ±20%

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter = delay * self.jitter_factor * (2 * (time.time() % 1) - 1)
        return max(self.min_delay, delay + jitter)
```

---

## Advanced Patterns

### Circuit Breaker

**Purpose**: Prevent cascading failures by temporarily blocking requests to failing service.

**States**:
1. **CLOSED**: Normal operation, requests allowed
2. **OPEN**: Too many failures, requests blocked
3. **HALF_OPEN**: Testing if service recovered

**Implementation**:
```python
from enum import Enum
from typing import Optional

class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        success_threshold: int = 2
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            timeout: Seconds before attempting recovery
            success_threshold: Successes needed to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        self.failures = 0
        self.successes = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def record_success(self) -> None:
        """Record successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                # Service recovered, close circuit
                self.state = CircuitState.CLOSED
                self.failures = 0
                self.successes = 0
        else:
            # Normal operation
            self.failures = 0

    def record_failure(self) -> None:
        """Record failed operation."""
        self.failures += 1
        self.last_failure_time = time.time()
        self.successes = 0

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN

    def is_available(self) -> bool:
        """Check if circuit allows requests."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            # Check if timeout has passed
            if self.last_failure_time:
                elapsed = time.time() - self.last_failure_time
                if elapsed > self.timeout:
                    # Try recovery
                    self.state = CircuitState.HALF_OPEN
                    return True
            return False

        # HALF_OPEN - allow request to test recovery
        return True

    def get_state(self) -> dict:
        """Get circuit breaker state for monitoring."""
        return {
            "state": self.state.value,
            "failures": self.failures,
            "successes": self.successes,
            "time_since_last_failure": (
                time.time() - self.last_failure_time
                if self.last_failure_time
                else None
            )
        }
```

**Usage with Retry**:
```python
class ResilientService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            timeout=60.0
        )

    async def call_with_circuit_breaker(self) -> ServiceResult[T]:
        """Call with retry + circuit breaker."""

        # Check circuit breaker first
        if not self.circuit_breaker.is_available():
            return ServiceResult.fail(
                "Circuit breaker is OPEN - service unavailable",
                error_type="CircuitOpen",
                recoverable=True
            )

        # Retry loop
        for attempt in range(self.settings.max_retries):
            try:
                result = await self._perform_operation()
                self.circuit_breaker.record_success()
                return ServiceResult.ok(result)

            except Exception as e:
                if not self._is_retriable_error(e):
                    self.circuit_breaker.record_failure()
                    return ServiceResult.fail(str(e))

                if attempt < self.settings.max_retries - 1:
                    delay = self._calculate_backoff_delay(attempt)
                    await asyncio.sleep(delay)

        # All retries failed
        self.circuit_breaker.record_failure()
        return ServiceResult.fail("Failed after retries")
```

---

### Rate Limiting

**Problem**: API has rate limits (e.g., 100 requests/minute).

**Solution**: Respect `Retry-After` header and implement token bucket.

**Token Bucket**:
```python
import time

class TokenBucket:
    """Token bucket for rate limiting."""

    def __init__(self, rate: float, capacity: int):
        """Initialize token bucket.

        Args:
            rate: Tokens added per second
            capacity: Maximum tokens
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now

    async def acquire(self, tokens: int = 1) -> None:
        """Acquire tokens, waiting if necessary."""
        while True:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return

            # Wait for tokens to refill
            wait_time = (tokens - self.tokens) / self.rate
            await asyncio.sleep(wait_time)
```

**Usage**:
```python
class RateLimitedService:
    def __init__(self, settings: Settings):
        self.settings = settings
        # 100 requests/minute = 100/60 = 1.67 tokens/second
        self.rate_limiter = TokenBucket(rate=1.67, capacity=100)

    async def call_api(self) -> ServiceResult[T]:
        """Call API with rate limiting."""

        # Acquire token before making request
        await self.rate_limiter.acquire()

        # Make request with retry
        return await self._call_with_retry()
```

**Respect Retry-After Header**:
```python
async def _handle_rate_limit(self, response: aiohttp.ClientResponse) -> float:
    """Extract delay from Retry-After header.

    Args:
        response: HTTP response with 429 status

    Returns:
        Delay in seconds (capped at 30s)
    """
    retry_after = response.headers.get("Retry-After")

    if retry_after:
        try:
            # Retry-After can be seconds or HTTP date
            delay = float(retry_after)
        except ValueError:
            # HTTP date format - parse it
            from email.utils import parsedate_to_datetime
            retry_time = parsedate_to_datetime(retry_after)
            delay = (retry_time - datetime.now()).total_seconds()

        # Cap at 30s
        return min(delay, 30.0)

    # No header, use default
    return 2.0
```

---

## Troubleshooting

### Common Issues

**Issue 1: Retries Don't Stop**

**Symptom**: Infinite retry loop.

**Cause**: Loop condition incorrect.

**Fix**:
```python
# ❌ WRONG - infinite loop
while True:
    try:
        result = await operation()
        return result
    except Exception:
        await asyncio.sleep(1)

# ✅ CORRECT - bounded retries
for attempt in range(max_retries):
    try:
        result = await operation()
        return result
    except Exception as e:
        if attempt < max_retries - 1:
            await asyncio.sleep(delay)
        else:
            return ServiceResult.fail(f"Failed: {e}")
```

---

**Issue 2: Non-Idempotent Operation Retried**

**Symptom**: Duplicate entities created.

**Cause**: Retrying create/update without idempotency check.

**Fix**:
```python
# ✅ CORRECT - check before retry
async def create_with_idempotency(entity_id: str) -> ServiceResult[Entity]:
    for attempt in range(max_retries):
        try:
            # Check if already exists
            exists = await self._entity_exists(entity_id)
            if exists:
                return ServiceResult.ok(exists, already_existed=True)

            # Create new
            entity = await self._create_entity(entity_id)
            return ServiceResult.ok(entity, was_created=True)

        except Exception as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
```

---

**Issue 3: All Clients Retry Simultaneously**

**Symptom**: Service crashes again after recovery.

**Cause**: No jitter - thundering herd problem.

**Fix**:
```python
# ❌ WRONG - no jitter
delay = base_delay * (2 ** attempt)

# ✅ CORRECT - add jitter
delay = base_delay * (2 ** attempt)
jitter = delay * 0.2 * (2 * (time.time() % 1) - 1)
final_delay = delay + jitter
```

---

**Issue 4: Retrying Permanent Errors**

**Symptom**: Retrying 400 Bad Request errors.

**Cause**: Not classifying errors correctly.

**Fix**:
```python
# ✅ CORRECT - classify errors
def _is_retriable_error(self, error: Exception, status_code: int | None) -> bool:
    # 4xx client errors are NOT retriable (except 429)
    if status_code and 400 <= status_code < 500:
        return status_code == 429  # Only 429 is retriable

    # 5xx server errors ARE retriable
    if status_code and 500 <= status_code < 600:
        return True

    # Validation errors are NOT retriable
    if isinstance(error, (ValueError, TypeError)):
        return False

    # Network errors ARE retriable
    if isinstance(error, (ConnectionError, TimeoutError)):
        return True

    return False
```

---

**Issue 5: Circuit Breaker Never Closes**

**Symptom**: Circuit stays OPEN forever.

**Cause**: Not implementing HALF_OPEN state.

**Fix**:
```python
# ✅ CORRECT - implement HALF_OPEN
def is_available(self) -> bool:
    if self.state == CircuitState.OPEN:
        # Check if timeout passed
        if time.time() - self.last_failure_time > self.timeout:
            self.state = CircuitState.HALF_OPEN  # Try recovery
            return True
        return False

    return True  # CLOSED or HALF_OPEN
```

---

## Performance Considerations

### Total Retry Time

**Formula**:
```
total_time = Σ(base_delay * 2^i) for i in [0, max_retries-1]
```

**Example (base_delay=1s, max_retries=5)**:
```
Attempt 0: 0s (immediate)
Attempt 1: 1s delay
Attempt 2: 2s delay
Attempt 3: 4s delay
Attempt 4: 8s delay
Total: 0 + 1 + 2 + 4 + 8 = 15s
```

**With max_delay cap (30s)**:
```
Attempt 0: 0s
Attempt 1: 1s
Attempt 2: 2s
Attempt 3: 4s
Attempt 4: 8s
Attempt 5: 16s
Attempt 6: 30s (capped)
Attempt 7: 30s (capped)
Total: ~91s for 8 retries
```

**Recommendation**: For user-facing operations, limit max_retries to 3-5 to keep total time under 15-30s.

---

### Memory Impact

**Problem**: Retrying large payloads consumes memory.

**Solution**: Stream large data instead of loading into memory.

```python
# ❌ WRONG - loads entire file into memory
async def upload_file_with_retry(file_path: str) -> ServiceResult[None]:
    data = open(file_path, 'rb').read()  # Entire file in memory

    for attempt in range(max_retries):
        try:
            await self._upload(data)
            return ServiceResult.ok(None)
        except Exception:
            await asyncio.sleep(delay)

# ✅ CORRECT - stream file
async def upload_file_with_retry(file_path: str) -> ServiceResult[None]:
    for attempt in range(max_retries):
        try:
            # Reopen file for each attempt (streaming)
            async with aiofiles.open(file_path, 'rb') as f:
                await self._upload_stream(f)
            return ServiceResult.ok(None)
        except Exception:
            await asyncio.sleep(delay)
```

---

### Logging Overhead

**Problem**: Excessive logging during retries.

**Solution**: Log warnings only, not debug messages.

```python
# ❌ WRONG - too verbose
logger.debug(f"Attempt {attempt}")
logger.debug(f"Calling API: {url}")
logger.warning(f"Failed: {error}")
logger.debug(f"Retrying in {delay}s")

# ✅ CORRECT - concise
if attempt < max_retries - 1:
    logger.warning(
        f"Transient error: {error}. Retrying in {delay:.1f}s "
        f"(attempt {attempt + 1}/{max_retries})"
    )
else:
    logger.error(f"Failed after {max_retries} retries: {error}")
```

---

## Testing Strategies

### Mock Failures

**Pattern**: Use `side_effect` to simulate retry scenarios.

```python
from unittest.mock import AsyncMock

async def test_retry_then_success():
    mock_op = AsyncMock()
    mock_op.side_effect = [
        TimeoutError("timeout"),
        TimeoutError("timeout"),
        {"status": "success"}  # Third attempt succeeds
    ]

    result = await service.call_with_retry()

    assert result.is_success
    assert mock_op.call_count == 3
```

---

### Verify Delays

**Pattern**: Mock `asyncio.sleep` to verify backoff behavior.

```python
async def test_exponential_backoff():
    delays = []

    async def mock_sleep(delay: float):
        delays.append(delay)

    with patch("asyncio.sleep", side_effect=mock_sleep):
        await service.call_with_retry()

    # Verify exponential increase
    assert delays[0] < delays[1]
    assert delays[1] < delays[2]
```

---

### Test Error Classification

**Pattern**: Test all error types are classified correctly.

```python
@pytest.mark.parametrize("error,status,expected", [
    (TimeoutError(), None, True),           # Retriable
    (ConnectionError(), None, True),        # Retriable
    (ValueError(), None, False),            # Not retriable
    (Exception(), 429, True),               # Rate limit - retriable
    (Exception(), 500, True),               # Server error - retriable
    (Exception(), 400, False),              # Client error - not retriable
])
async def test_error_classification(error, status, expected):
    result = service._is_retriable_error(error, status)
    assert result == expected
```

---

## Best Practices Summary

1. **Always use exponential backoff** - Prevents overwhelming recovering service
2. **Add jitter** - Prevents thundering herd
3. **Classify errors** - Retry only transient failures
4. **Cap max delay** - Typically 30s
5. **Limit max retries** - Typically 3-5 attempts
6. **Log appropriately** - Warning on retry, error on failure
7. **Use ServiceResult** - Never raise exceptions from retry logic
8. **Test thoroughly** - Mock failures, verify delays, test error classification
9. **Consider circuit breaker** - For critical dependencies
10. **Respect rate limits** - Use token bucket or Retry-After header
