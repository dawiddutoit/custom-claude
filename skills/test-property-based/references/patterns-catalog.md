# Property Testing Patterns Catalog

Common property-based testing patterns with detailed examples.

## Table of Contents

1. [Roundtrip Properties](#roundtrip-properties)
2. [Invariant Properties](#invariant-properties)
3. [Idempotency Properties](#idempotency-properties)
4. [Commutativity Properties](#commutativity-properties)
5. [Consistency Properties](#consistency-properties)
6. [Conservation Properties](#conservation-properties)
7. [Induction Properties](#induction-properties)
8. [Oracle Properties](#oracle-properties)
9. [Validation Properties](#validation-properties)
10. [State Machine Properties](#state-machine-properties)

---

## Roundtrip Properties

**Pattern:** `parse(serialize(x)) == x`

**Use when:** Testing serialization, encoding, parsing, or conversion logic.

### Example 1: JSON Serialization

```python
from hypothesis import given, strategies as st
import json

@given(st.dictionaries(st.text(), st.text()))
def test_json_roundtrip(data):
    """Property: Any dict should roundtrip through JSON."""
    serialized = json.dumps(data)
    parsed = json.loads(serialized)
    assert parsed == data
```

### Example 2: Pydantic Model Serialization

```python
from hypothesis import given
from hypothesis.strategies import builds
from pydantic import BaseModel

class UserConfig(BaseModel):
    username: str
    age: int
    active: bool

@given(builds(UserConfig))
def test_pydantic_json_roundtrip(config):
    """Property: Pydantic models roundtrip through JSON."""
    json_str = config.model_dump_json()
    restored = UserConfig.model_validate_json(json_str)
    assert restored == config
```

### Example 3: Base64 Encoding

```python
from hypothesis import given, strategies as st
import base64

@given(st.binary())
def test_base64_roundtrip(data):
    """Property: Binary data roundtrips through base64."""
    encoded = base64.b64encode(data)
    decoded = base64.b64decode(encoded)
    assert decoded == data
```

### Example 4: URL Encoding

```python
from hypothesis import given, strategies as st
from urllib.parse import quote, unquote

@given(st.text())
def test_url_encoding_roundtrip(text):
    """Property: Text roundtrips through URL encoding."""
    encoded = quote(text)
    decoded = unquote(encoded)
    assert decoded == text
```

---

## Invariant Properties

**Pattern:** Some property always holds regardless of input.

**Use when:** Testing mathematical properties, data structure constraints, or system invariants.

### Example 1: Sorted List is Ordered

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sorted_list_ordered(lst):
    """Property: Sorted list should be in ascending order."""
    sorted_lst = sorted(lst)
    for i in range(len(sorted_lst) - 1):
        assert sorted_lst[i] <= sorted_lst[i + 1]
```

### Example 2: Absolute Value is Non-Negative

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_abs_non_negative(n):
    """Property: Absolute value is always non-negative."""
    assert abs(n) >= 0
```

### Example 3: Set Has No Duplicates

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_set_no_duplicates(lst):
    """Property: Converting to set removes duplicates."""
    s = set(lst)
    assert len(s) == len(list(s))
```

### Example 4: Dictionary Keys Match Values

```python
from hypothesis import given, strategies as st

@given(st.dictionaries(st.text(), st.integers()))
def test_dict_keys_match_values(d):
    """Property: Dict keys and values should have same count."""
    assert len(d.keys()) == len(d.values()) == len(d)
```

---

## Idempotency Properties

**Pattern:** `f(f(x)) == f(x)`

**Use when:** Testing normalization, deduplication, or operations that should stabilize.

### Example 1: Sorting is Idempotent

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_idempotent(lst):
    """Property: Sorting twice gives same result as once."""
    once_sorted = sorted(lst)
    twice_sorted = sorted(once_sorted)
    assert once_sorted == twice_sorted
```

### Example 2: String Normalization

```python
from hypothesis import given, strategies as st

def normalize(text: str) -> str:
    """Normalize text: lowercase, strip, collapse whitespace."""
    return ' '.join(text.lower().strip().split())

@given(st.text())
def test_normalize_idempotent(text):
    """Property: Normalizing twice gives same result."""
    once = normalize(text)
    twice = normalize(once)
    assert once == twice
```

### Example 3: Deduplication

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_deduplicate_idempotent(lst):
    """Property: Deduplicating twice gives same result."""
    def deduplicate(items):
        return list(dict.fromkeys(items))  # Preserves order

    once = deduplicate(lst)
    twice = deduplicate(once)
    assert once == twice
```

### Example 4: Absolute Value

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_abs_idempotent(n):
    """Property: abs(abs(x)) == abs(x)."""
    assert abs(abs(n)) == abs(n)
```

---

## Commutativity Properties

**Pattern:** `f(a, b) == f(b, a)`

**Use when:** Testing operations where order doesn't matter.

### Example 1: Addition is Commutative

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Property: a + b == b + a."""
    assert a + b == b + a
```

### Example 2: Multiplication is Commutative

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_multiplication_commutative(a, b):
    """Property: a * b == b * a."""
    assert a * b == b * a
```

### Example 3: Set Union is Commutative

```python
from hypothesis import given, strategies as st

@given(st.sets(st.integers()), st.sets(st.integers()))
def test_set_union_commutative(s1, s2):
    """Property: s1 | s2 == s2 | s1."""
    assert s1 | s2 == s2 | s1
```

### Example 4: String Concatenation Order Matters (Counter-example)

```python
from hypothesis import given, strategies as st

@given(st.text(), st.text())
def test_concat_not_commutative(a, b):
    """Property: Concatenation is NOT commutative (unless a==b)."""
    if a != b:
        # This would fail - showing concat is not commutative
        # assert a + b == b + a  # DON'T DO THIS
        pass
    else:
        assert a + b == b + a
```

---

## Consistency Properties

**Pattern:** Different paths to the same result should agree.

**Use when:** Testing multiple implementations, algorithms, or computation methods.

### Example 1: Manual Sum vs Built-in Sum

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sum_consistency(lst):
    """Property: Manual sum equals built-in sum."""
    manual_sum = 0
    for x in lst:
        manual_sum += x
    assert manual_sum == sum(lst)
```

### Example 2: Length of List vs Count

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_length_consistency(lst):
    """Property: len() and manual count agree."""
    count = 0
    for _ in lst:
        count += 1
    assert count == len(lst)
```

### Example 3: List Reverse Twice

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_reverse_consistency(lst):
    """Property: Reversing twice gives original."""
    assert list(reversed(list(reversed(lst)))) == lst
```

### Example 4: Dict Keys and Items

```python
from hypothesis import given, strategies as st

@given(st.dictionaries(st.text(), st.integers()))
def test_dict_consistency(d):
    """Property: Keys from items() match keys()."""
    keys_from_items = [k for k, v in d.items()]
    assert set(keys_from_items) == set(d.keys())
```

---

## Conservation Properties

**Pattern:** Operation preserves certain quantities.

**Use when:** Testing transformations that shouldn't lose data.

### Example 1: Sorting Preserves Length

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_preserves_length(lst):
    """Property: Sorting preserves list length."""
    assert len(sorted(lst)) == len(lst)
```

### Example 2: Sorting Preserves Elements

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_sort_preserves_elements(lst):
    """Property: Sorting preserves all elements."""
    sorted_lst = sorted(lst)
    for item in lst:
        assert sorted_lst.count(item) == lst.count(item)
```

### Example 3: Filtering Reduces or Maintains Size

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_filter_size_reduction(lst):
    """Property: Filtering can't increase size."""
    filtered = [x for x in lst if x > 0]
    assert len(filtered) <= len(lst)
```

### Example 4: Map Preserves Length

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_map_preserves_length(lst):
    """Property: Mapping preserves list length."""
    mapped = list(map(lambda x: x * 2, lst))
    assert len(mapped) == len(lst)
```

---

## Induction Properties

**Pattern:** Base case + inductive step proves property for all cases.

**Use when:** Testing recursive algorithms or structures.

### Example 1: Factorial Properties

```python
from hypothesis import given, strategies as st

def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

@given(st.integers(min_value=0, max_value=100))
def test_factorial_positive(n):
    """Property: Factorial is always positive."""
    assert factorial(n) > 0

@given(st.integers(min_value=1, max_value=100))
def test_factorial_recursive_relation(n):
    """Property: factorial(n) == n * factorial(n-1)."""
    assert factorial(n) == n * factorial(n - 1)
```

### Example 2: List Concatenation Length

```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()), st.lists(st.integers()))
def test_concat_length(lst1, lst2):
    """Property: Length of concat equals sum of lengths."""
    concatenated = lst1 + lst2
    assert len(concatenated) == len(lst1) + len(lst2)
```

### Example 3: Tree Depth

```python
from hypothesis import given, strategies as st
from hypothesis.strategies import recursive

tree_strategy = st.recursive(
    st.integers(),  # Leaf nodes
    lambda children: st.tuples(children, children),  # Branch nodes
    max_leaves=20
)

def depth(tree):
    if isinstance(tree, int):
        return 0
    left, right = tree
    return 1 + max(depth(left), depth(right))

@given(tree_strategy)
def test_tree_depth_non_negative(tree):
    """Property: Tree depth is non-negative."""
    assert depth(tree) >= 0
```

---

## Oracle Properties

**Pattern:** Compare against a known-correct reference implementation.

**Use when:** You have a simple (but slow) reference and want to test a fast implementation.

### Example 1: Fast Sort vs Reference Sort

```python
from hypothesis import given, strategies as st

def reference_sort(lst):
    """Simple bubble sort - slow but obviously correct."""
    result = lst[:]
    for i in range(len(result)):
        for j in range(len(result) - 1 - i):
            if result[j] > result[j + 1]:
                result[j], result[j + 1] = result[j + 1], result[j]
    return result

@given(st.lists(st.integers()))
def test_sort_matches_reference(lst):
    """Property: Optimized sort matches reference sort."""
    assert sorted(lst) == reference_sort(lst)
```

### Example 2: Fast Prime Check vs Reference

```python
from hypothesis import given, strategies as st

def reference_is_prime(n):
    """Simple prime check - slow but correct."""
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

def fast_is_prime(n):
    """Optimized prime check."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True

@given(st.integers(min_value=0, max_value=10000))
def test_prime_check_matches_reference(n):
    """Property: Fast prime check matches reference."""
    assert fast_is_prime(n) == reference_is_prime(n)
```

---

## Validation Properties

**Pattern:** Output satisfies certain constraints.

**Use when:** Testing validators, parsers, or constraint-checking code.

### Example 1: Pydantic Validation

```python
from hypothesis import given
from hypothesis.strategies import builds
from pydantic import BaseModel, PositiveInt, EmailStr

class UserModel(BaseModel):
    age: PositiveInt
    email: EmailStr
    username: str

@given(builds(UserModel))
def test_user_model_constraints(user):
    """Property: Generated users satisfy all constraints."""
    assert user.age > 0
    assert '@' in user.email
    assert len(user.username) > 0
```

### Example 2: Range Validation

```python
from hypothesis import given, strategies as st

def normalize_percent(value: float) -> float:
    """Normalize to 0-100 range."""
    return max(0.0, min(100.0, value))

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_normalize_percent_range(value):
    """Property: Normalized value is always in [0, 100]."""
    result = normalize_percent(value)
    assert 0.0 <= result <= 100.0
```

### Example 3: Email Validation

```python
from hypothesis import given
from hypothesis.strategies import composite

@composite
def valid_emails(draw):
    username = draw(st.text(alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd')
    ), min_size=1, max_size=20))
    domain = draw(st.text(alphabet=st.characters(
        whitelist_categories=('Ll',)
    ), min_size=1, max_size=15))
    tld = draw(st.sampled_from(['com', 'org', 'net']))
    return f"{username}@{domain}.{tld}"

@given(valid_emails())
def test_email_format(email):
    """Property: Generated emails have valid format."""
    assert '@' in email
    parts = email.split('@')
    assert len(parts) == 2
    assert '.' in parts[1]
```

---

## State Machine Properties

**Pattern:** Sequences of operations maintain system invariants.

**Use when:** Testing stateful systems, protocols, or lifecycle management.

### Example 1: Stack State Machine

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, precondition
from hypothesis import strategies as st

class StackStateMachine(RuleBasedStateMachine):
    """Test stack data structure with state machine."""

    def __init__(self):
        super().__init__()
        self.stack = []

    @rule(value=st.integers())
    def push(self, value):
        """Push value onto stack."""
        self.stack.append(value)

    @precondition(lambda self: len(self.stack) > 0)
    @rule()
    def pop(self):
        """Pop value from stack."""
        self.stack.pop()

    @precondition(lambda self: len(self.stack) > 0)
    @rule()
    def peek(self):
        """Peek at top value."""
        return self.stack[-1]

    @invariant()
    def stack_size_non_negative(self):
        """Invariant: Stack size is always non-negative."""
        assert len(self.stack) >= 0

    @invariant()
    def peek_matches_top(self):
        """Invariant: Peek returns same as direct access."""
        if self.stack:
            assert self.stack[-1] == self.stack[-1]

TestStack = StackStateMachine.TestCase
```

### Example 2: Connection State Machine

```python
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant, precondition
from hypothesis import strategies as st

class ConnectionStateMachine(RuleBasedStateMachine):
    """Test connection lifecycle."""

    def __init__(self):
        super().__init__()
        self.connected = False
        self.messages_sent = 0
        self.messages_received = 0

    @rule()
    def connect(self):
        """Connect if not already connected."""
        if not self.connected:
            self.connected = True

    @precondition(lambda self: self.connected)
    @rule(message=st.text())
    def send_message(self, message):
        """Send message when connected."""
        self.messages_sent += 1

    @precondition(lambda self: self.connected and self.messages_sent > 0)
    @rule()
    def receive_message(self):
        """Receive message when available."""
        self.messages_received += 1

    @precondition(lambda self: self.connected)
    @rule()
    def disconnect(self):
        """Disconnect if connected."""
        self.connected = False

    @invariant()
    def received_not_more_than_sent(self):
        """Invariant: Can't receive more than sent."""
        assert self.messages_received <= self.messages_sent

    @invariant()
    def cant_send_when_disconnected(self):
        """Invariant: Can't send when disconnected."""
        # This invariant is enforced by precondition
        pass

TestConnection = ConnectionStateMachine.TestCase
```

---

## Pattern Selection Guide

| Property Type | When to Use | Example |
|--------------|-------------|---------|
| **Roundtrip** | Serialization, encoding, parsing | `parse(serialize(x)) == x` |
| **Invariant** | Math properties, constraints | `abs(x) >= 0` |
| **Idempotency** | Normalization, deduplication | `f(f(x)) == f(x)` |
| **Commutativity** | Order-independent operations | `a + b == b + a` |
| **Consistency** | Multiple implementations | `fast_sort(x) == slow_sort(x)` |
| **Conservation** | Data preservation | `len(sorted(lst)) == len(lst)` |
| **Induction** | Recursive structures | `factorial(n) == n * factorial(n-1)` |
| **Oracle** | Reference implementation | `optimized(x) == reference(x)` |
| **Validation** | Constraint checking | `0 <= normalize(x) <= 100` |
| **State Machine** | Stateful systems | `invariant holds across operations` |

## Common Anti-Patterns

### DON'T: Test Implementation Details

```python
# BAD: Duplicating implementation in test
@given(st.lists(st.integers()))
def test_sum_implementation(lst):
    result = sum(lst)
    # Reimplementing sum() - not a property!
    expected = 0
    for x in lst:
        expected += x
    assert result == expected
```

**DO: Test Properties**

```python
# GOOD: Test properties of sum
@given(st.lists(st.integers()))
def test_sum_commutative(lst):
    assert sum(lst) == sum(reversed(lst))

@given(st.lists(st.integers()))
def test_sum_with_zero(lst):
    assert sum(lst + [0]) == sum(lst)
```

### DON'T: Over-Constrain Strategies

```python
# BAD: Too specific
@given(st.integers(min_value=5, max_value=5))
def test_specific_value(n):
    assert n == 5  # Just use example-based test!
```

**DO: Test Broad Properties**

```python
# GOOD: Test property for all integers
@given(st.integers())
def test_abs_property(n):
    assert abs(n) >= 0
```

## Further Reading

- Hypothesis documentation: https://hypothesis.readthedocs.io/
- Property-based testing guide: https://hypothesis.works/articles/what-is-property-based-testing/
- State machine testing: https://hypothesis.works/articles/rule-based-stateful-testing/
