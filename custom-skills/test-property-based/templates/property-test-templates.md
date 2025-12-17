# Property Test Templates

Copy-paste ready templates for common property testing scenarios.

## Table of Contents

1. [Basic Property Test](#basic-property-test)
2. [Async Property Test](#async-property-test)
3. [Pydantic Model Property Test](#pydantic-model-property-test)
4. [Custom Strategy](#custom-strategy)
5. [State Machine Test](#state-machine-test)
6. [conftest.py Configuration](#conftestpy-configuration)
7. [Roundtrip Test](#roundtrip-test)
8. [Invariant Test](#invariant-test)

---

## Basic Property Test

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_property_name(input_data):
    """Property: Describe what property should always hold.

    This test verifies that [PROPERTY] holds for all valid inputs.
    """
    # Arrange
    # (Optional setup - usually not needed with property tests)

    # Act
    result = function_under_test(input_data)

    # Assert - Check the property
    assert result satisfies_property
    # Or multiple assertions for complex properties
    assert condition_1
    assert condition_2
```

**Example:**

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_idempotent(lst):
    """Property: Sorting twice gives same result as once.

    This test verifies that sorting is idempotent - applying it
    multiple times has the same effect as applying it once.
    """
    once_sorted = sorted(lst)
    twice_sorted = sorted(once_sorted)

    assert once_sorted == twice_sorted
```

---

## Async Property Test

```python
import pytest
from hypothesis import given, strategies as st

@pytest.mark.asyncio  # IMPORTANT: Must be innermost decorator
@given(st.text())
async def test_async_property_name(input_data):
    """Property: Describe async property.

    Tests async function with property-based inputs.
    """
    # Act
    result = await async_function_under_test(input_data)

    # Assert
    assert result satisfies_property
```

**Example:**

```python
import pytest
from hypothesis import given, strategies as st

@pytest.mark.asyncio
@given(
    command=st.sampled_from(["execute", "status", "cancel"]),
    correlation_id=st.uuids().map(str)
)
async def test_ipc_command_response(command, correlation_id):
    """Property: All IPC commands should get responses.

    Tests that every valid command receives a response with
    matching correlation ID.
    """
    response = await send_ipc_command(command, correlation_id)

    assert response is not None
    assert response["correlation_id"] == correlation_id
    assert response["status"] in ["success", "error"]
```

---

## Pydantic Model Property Test

```python
from hypothesis import given
from hypothesis.strategies import builds
from pydantic import BaseModel

class YourModel(BaseModel):
    field1: str
    field2: int
    field3: bool

@given(builds(YourModel))
def test_model_property_name(model_instance):
    """Property: All valid model instances should satisfy constraints.

    Tests that Hypothesis-generated model instances meet all
    validation requirements.
    """
    # Assert properties that should hold for all valid instances
    assert model_instance.field2 >= 0  # If you have constraints
    assert len(model_instance.field1) > 0
    # ... more property checks
```

**Example:**

```python
from hypothesis import given
from hypothesis.strategies import builds
from pydantic import BaseModel, PositiveInt, EmailStr

class UserConfig(BaseModel):
    username: str
    age: PositiveInt
    email: EmailStr
    active: bool = True

@given(builds(UserConfig))
def test_user_config_json_roundtrip(config):
    """Property: UserConfig instances roundtrip through JSON.

    Tests that all valid UserConfig instances can be serialized
    to JSON and deserialized back without data loss.
    """
    # Serialize to JSON
    json_str = config.model_dump_json()

    # Deserialize back
    restored = UserConfig.model_validate_json(json_str)

    # Property: Should equal original
    assert restored == config
    assert restored.age > 0  # Pydantic constraint
    assert '@' in restored.email  # Email format
```

**With Custom Field Strategies:**

```python
@given(builds(
    UserConfig,
    username=st.text(alphabet=st.characters(whitelist_categories=('Ll',)), min_size=3, max_size=20),
    age=st.integers(min_value=18, max_value=120)
))
def test_user_config_adult_users(config):
    """Property: Adult user configs have specific constraints."""
    assert config.age >= 18
    assert 3 <= len(config.username) <= 20
    assert config.username.islower()
```

---

## Custom Strategy

```python
from hypothesis import strategies as st
from hypothesis.strategies import composite

@composite
def your_custom_strategy(draw):
    """Generate custom domain objects.

    This strategy creates [DESCRIPTION OF OBJECTS] with valid
    combinations of fields that satisfy domain constraints.
    """
    # Draw from primitive strategies
    field1 = draw(st.text(min_size=1, max_size=20))
    field2 = draw(st.integers(min_value=0, max_value=100))

    # Conditional logic based on drawn values
    if field2 > 50:
        field3 = draw(st.sampled_from(['option_a', 'option_b']))
    else:
        field3 = draw(st.sampled_from(['option_c']))

    # Return the constructed object
    return {
        'field1': field1,
        'field2': field2,
        'field3': field3,
    }

@given(your_custom_strategy())
def test_with_custom_strategy(custom_object):
    """Test using custom strategy."""
    assert custom_object['field2'] >= 0
    # ... more tests
```

**Example: IPC Command Request Strategy**

```python
from hypothesis import strategies as st
from hypothesis.strategies import composite
import uuid

@composite
def command_requests(draw):
    """Generate valid IPC CommandRequest messages.

    Creates command request messages with realistic field combinations
    that match the IPC protocol specification.
    """
    # Command type determines available fields
    command = draw(st.sampled_from(["execute", "status", "cancel", "disconnect"]))

    # All commands have correlation ID
    correlation_id = draw(st.uuids().map(str))

    # Context is optional
    context = draw(st.dictionaries(st.text(), st.text(), max_size=5))

    # Execute command requires prompt
    if command == "execute":
        prompt = draw(st.text(min_size=1, max_size=500))
    else:
        prompt = ""

    return {
        "type": "command_request",
        "command": command,
        "prompt": prompt,
        "correlation_id": correlation_id,
        "context": context
    }

@given(command_requests())
def test_command_request_structure(request):
    """Property: All generated command requests are valid."""
    assert request["type"] == "command_request"
    assert request["command"] in ["execute", "status", "cancel", "disconnect"]
    assert "correlation_id" in request

    if request["command"] == "execute":
        assert len(request["prompt"]) > 0
```

---

## State Machine Test

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, precondition
from hypothesis import strategies as st

class YourStateMachine(RuleBasedStateMachine):
    """Test stateful system with sequences of operations.

    This state machine tests [DESCRIPTION OF SYSTEM] by generating
    random sequences of operations and checking invariants hold.
    """

    def __init__(self):
        super().__init__()
        # Initialize state variables
        self.state_variable_1 = initial_value
        self.state_variable_2 = initial_value

    @rule()
    def operation_without_precondition(self):
        """Operation that can always be performed."""
        # Perform operation
        self.state_variable_1 = new_value

    @precondition(lambda self: self.state_variable_1 > 0)
    @rule(param=st.integers())
    def operation_with_precondition(self, param):
        """Operation that requires certain state.

        Only runs when precondition is satisfied.
        """
        # Perform operation using param
        self.state_variable_2 = param

    @invariant()
    def check_invariant_1(self):
        """Invariant: [DESCRIPTION].

        This property should hold after every operation.
        """
        assert self.state_variable_1 >= 0

    @invariant()
    def check_invariant_2(self):
        """Invariant: [DESCRIPTION]."""
        # Check relationship between state variables
        assert condition_holds

# Convert to pytest test case
TestYourSystem = YourStateMachine.TestCase
```

**Example: Connection State Machine**

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, precondition
from hypothesis import strategies as st

class ConnectionStateMachine(RuleBasedStateMachine):
    """Test connection lifecycle state transitions.

    Generates random sequences of connect/disconnect/send operations
    and verifies connection state invariants always hold.
    """

    def __init__(self):
        super().__init__()
        self.connected = False
        self.messages_sent = 0
        self.messages_received = 0

    @rule()
    def connect(self):
        """Connect to service if not already connected."""
        if not self.connected:
            self.connected = True

    @precondition(lambda self: self.connected)
    @rule(message=st.text(min_size=1, max_size=100))
    def send_message(self, message):
        """Send message when connected."""
        self.messages_sent += 1
        # Simulate receiving response
        self.messages_received += 1

    @precondition(lambda self: self.connected)
    @rule()
    def disconnect(self):
        """Disconnect from service."""
        self.connected = False

    @invariant()
    def messages_consistent(self):
        """Invariant: Received messages <= sent messages."""
        assert self.messages_received <= self.messages_sent

    @invariant()
    def connection_state_valid(self):
        """Invariant: Connection state is boolean."""
        assert isinstance(self.connected, bool)

TestConnection = ConnectionStateMachine.TestCase
```

---

## conftest.py Configuration

```python
# tests/conftest.py
from hypothesis import settings, HealthCheck

# Configure Hypothesis profiles for different environments

# Development profile - fast iteration
settings.register_profile(
    "dev",
    max_examples=50,        # Fewer examples for speed
    deadline=None,          # No time limit
    print_blob=False,       # Don't print blob on failure
)

# CI profile - balanced
settings.register_profile(
    "ci",
    max_examples=200,       # More examples for confidence
    deadline=1000,          # 1 second per test
    print_blob=True,        # Print blob for reproduction
)

# Thorough profile - comprehensive testing
settings.register_profile(
    "thorough",
    max_examples=1000,      # Extensive testing
    deadline=None,          # No time limit
    suppress_health_check=[HealthCheck.too_slow],  # Allow slow tests
    print_blob=True,
)

# Debug profile - for investigating failures
settings.register_profile(
    "debug",
    max_examples=10,        # Few examples for debugging
    verbosity=st.Verbosity.debug,  # Maximum verbosity
    deadline=None,
    print_blob=True,
)

# Activate profile based on environment variable
# Default to "dev" if not specified
import os
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "dev"))
```

**Usage:**

```bash
# Use default (dev) profile
pytest tests/

# Use CI profile
HYPOTHESIS_PROFILE=ci pytest tests/

# Or via command line
pytest --hypothesis-profile=thorough tests/

# Debug mode
pytest --hypothesis-profile=debug tests/test_specific.py::test_function
```

---

## Roundtrip Test

```python
from hypothesis import given, strategies as st

@given(st.YOUR_DATA_TYPE())
def test_roundtrip_OPERATION(data):
    """Property: Data should roundtrip through SERIALIZE/DESERIALIZE.

    Tests that serialization and deserialization are inverse operations.
    """
    # Serialize
    serialized = serialize(data)

    # Deserialize
    deserialized = deserialize(serialized)

    # Property: Should equal original
    assert deserialized == data
```

**Example: JSON Roundtrip**

```python
from hypothesis import given, strategies as st
import json

@given(st.dictionaries(st.text(), st.one_of(st.text(), st.integers(), st.booleans())))
def test_json_roundtrip(data):
    """Property: Dicts roundtrip through JSON serialization.

    Tests that any valid dict can be serialized to JSON and
    deserialized back to the original structure.
    """
    # Serialize to JSON string
    json_str = json.dumps(data)

    # Deserialize back to dict
    parsed = json.loads(json_str)

    # Property: Should equal original
    assert parsed == data
```

**Example: Base64 Roundtrip**

```python
from hypothesis import given, strategies as st
import base64

@given(st.binary())
def test_base64_roundtrip(data):
    """Property: Binary data roundtrips through base64 encoding.

    Tests that encoding and decoding are inverse operations.
    """
    # Encode
    encoded = base64.b64encode(data)

    # Decode
    decoded = base64.b64decode(encoded)

    # Property: Should equal original
    assert decoded == data
```

---

## Invariant Test

```python
from hypothesis import given, strategies as st

@given(st.YOUR_INPUT_TYPE())
def test_invariant_PROPERTY(input_data):
    """Property: INVARIANT should always hold.

    Tests that regardless of input, the specified invariant
    property is maintained.
    """
    # Act
    result = function_under_test(input_data)

    # Assert invariant
    assert invariant_condition(result)
```

**Example: Absolute Value Invariant**

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_abs_non_negative(n):
    """Property: Absolute value is always non-negative.

    Tests the mathematical invariant that |n| >= 0 for all integers.
    """
    result = abs(n)

    # Invariant: Always non-negative
    assert result >= 0

    # Additional invariants
    assert abs(-n) == result  # abs(-n) == abs(n)
    assert result == max(n, -n)  # abs(n) == max(n, -n)
```

**Example: Sorted List Invariant**

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sorted_list_ordered(lst):
    """Property: Sorted list is always in ascending order.

    Tests the fundamental invariant of sorting - that resulting
    list has elements in non-decreasing order.
    """
    sorted_lst = sorted(lst)

    # Invariant: Each element <= next element
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]

    # Additional invariants
    assert len(sorted_lst) == len(lst)  # Preserves length
```

---

## Quick Template Selection Guide

| Need | Use Template |
|------|--------------|
| Simple property test | [Basic Property Test](#basic-property-test) |
| Testing async function | [Async Property Test](#async-property-test) |
| Testing Pydantic model | [Pydantic Model Property Test](#pydantic-model-property-test) |
| Complex domain data | [Custom Strategy](#custom-strategy) |
| Stateful behavior | [State Machine Test](#state-machine-test) |
| Project configuration | [conftest.py Configuration](#conftestpy-configuration) |
| Serialization | [Roundtrip Test](#roundtrip-test) |
| Mathematical property | [Invariant Test](#invariant-test) |

## Tips for Using Templates

1. **Replace placeholders:**
   - `YOUR_DATA_TYPE` → Actual strategy (e.g., `st.integers()`)
   - `function_under_test` → Your actual function name
   - `PROPERTY` → Description of property being tested

2. **Customize strategies:**
   - Add constraints: `st.integers(min_value=0, max_value=100)`
   - Combine strategies: `st.one_of(st.integers(), st.text())`
   - Use `min_size`/`max_size` for collections

3. **Add meaningful docstrings:**
   - Describe what property is being tested
   - Explain why this property should hold
   - Document any assumptions or constraints

4. **Start simple:**
   - Begin with basic property test
   - Add complexity as needed
   - Don't over-engineer initially

5. **Run and iterate:**
   - Run test to see what Hypothesis generates
   - Refine strategy if invalid inputs generated
   - Add constraints or use `assume()` sparingly

## Further Reading

- Hypothesis documentation: https://hypothesis.readthedocs.io/
- Example-based vs property-based testing: https://hypothesis.works/articles/what-is-property-based-testing/
- Writing good properties: https://fsharpforfunandprofit.com/posts/property-based-testing-2/
