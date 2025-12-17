# Hypothesis Strategies Reference

Complete catalog of built-in Hypothesis strategies with examples.

## Table of Contents

1. [Basic Types](#basic-types)
2. [Numeric Strategies](#numeric-strategies)
3. [Text and String Strategies](#text-and-string-strategies)
4. [Collection Strategies](#collection-strategies)
5. [Date and Time Strategies](#date-and-time-strategies)
6. [Special Types](#special-types)
7. [Combinators](#combinators)
8. [Advanced Strategies](#advanced-strategies)

## Basic Types

### Booleans

```python
from hypothesis import strategies as st

st.booleans()  # True or False
```

### None

```python
st.none()  # Always generates None
```

### Sampled From

```python
# Pick from a list of values
st.sampled_from(['execute', 'status', 'cancel', 'disconnect'])
st.sampled_from([1, 2, 3, 5, 8, 13, 21])
st.sampled_from(MyEnum)  # Works with enums
```

## Numeric Strategies

### Integers

```python
st.integers()                      # All integers (including negative)
st.integers(min_value=0)          # Non-negative integers
st.integers(max_value=100)        # Integers up to 100
st.integers(min_value=0, max_value=100)  # 0 to 100 inclusive
```

**Examples:**
```python
@given(st.integers())
def test_abs_non_negative(n):
    assert abs(n) >= 0

@given(st.integers(min_value=1, max_value=10))
def test_single_digit_positive(n):
    assert 1 <= n <= 10
```

### Floats

```python
st.floats()                           # All floats (including inf, -inf, nan)
st.floats(allow_nan=False)            # Exclude NaN
st.floats(allow_infinity=False)       # Exclude inf/-inf
st.floats(min_value=0.0, max_value=1.0)  # Range [0.0, 1.0]
st.floats(allow_nan=False, allow_infinity=False)  # Normal floats only
```

**Examples:**
```python
@given(st.floats(min_value=0.0, allow_nan=False, allow_infinity=False))
def test_non_negative_float(x):
    assert x >= 0.0

@given(st.floats(allow_nan=False, allow_infinity=False))
def test_float_add_commutative(x, y):
    assert abs((x + y) - (y + x)) < 1e-10  # Account for floating point error
```

### Decimals

```python
from decimal import Decimal

st.decimals()                         # Decimal numbers
st.decimals(min_value=0, max_value=100)
st.decimals(allow_nan=False, allow_infinity=False)
```

### Fractions

```python
from fractions import Fraction

st.fractions()                        # Fraction objects
st.fractions(min_value=0, max_value=1)
```

## Text and String Strategies

### Text

```python
st.text()                             # Any unicode string
st.text(min_size=1)                   # Non-empty strings
st.text(max_size=100)                 # Up to 100 characters
st.text(min_size=1, max_size=20)      # 1-20 characters

# Limited alphabet
st.text(alphabet='abc')               # Only 'a', 'b', 'c'
st.text(alphabet=st.characters(min_codepoint=ord('a'), max_codepoint=ord('z')))

# Specific character categories
st.text(alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll'),  # Upper and lowercase letters
    min_codepoint=ord('a')
))
```

**Examples:**
```python
@given(st.text())
def test_len_non_negative(s):
    assert len(s) >= 0

@given(st.text(alphabet='abc', min_size=1))
def test_only_abc(s):
    assert all(c in 'abc' for c in s)
```

### Binary

```python
st.binary()                           # Bytes objects
st.binary(min_size=1, max_size=100)   # 1-100 bytes
```

### Characters

```python
st.characters()                       # Single unicode characters
st.characters(min_codepoint=ord('a'), max_codepoint=ord('z'))  # a-z
st.characters(whitelist_categories=('Ll',))  # Lowercase letters
st.characters(blacklist_categories=('Cs',))  # Exclude surrogates
```

## Collection Strategies

### Lists

```python
st.lists(st.integers())               # Lists of integers
st.lists(st.text(), min_size=1)       # Non-empty lists of strings
st.lists(st.integers(), max_size=10)  # Up to 10 integers
st.lists(st.integers(), min_size=1, max_size=5)  # 1-5 integers
st.lists(st.integers(), unique=True)  # No duplicate elements
```

**Examples:**
```python
@given(st.lists(st.integers()))
def test_sort_preserves_length(lst):
    assert len(sorted(lst)) == len(lst)

@given(st.lists(st.integers(), min_size=1))
def test_max_in_list(lst):
    assert max(lst) in lst
```

### Sets

```python
st.sets(st.integers())                # Sets of integers
st.sets(st.text(), min_size=1)        # Non-empty sets
st.sets(st.integers(), max_size=10)   # Up to 10 elements
```

**Examples:**
```python
@given(st.sets(st.integers()))
def test_set_no_duplicates(s):
    # Sets automatically deduplicate
    assert len(s) == len(list(s))
```

### Dictionaries

```python
st.dictionaries(st.text(), st.integers())  # Dict[str, int]
st.dictionaries(st.text(), st.integers(), min_size=1)  # Non-empty
st.dictionaries(st.text(), st.integers(), max_size=10)  # Up to 10 keys
```

**Examples:**
```python
@given(st.dictionaries(st.text(), st.integers()))
def test_dict_keys_match_len(d):
    assert len(d.keys()) == len(d)

@given(st.dictionaries(st.text(), st.text()))
def test_json_roundtrip(d):
    import json
    assert json.loads(json.dumps(d)) == d
```

### Tuples

```python
# Fixed-length tuples with specific types
st.tuples(st.integers(), st.text())   # (int, str)
st.tuples(st.text(), st.integers(), st.booleans())  # (str, int, bool)
```

**Examples:**
```python
@given(st.tuples(st.integers(), st.integers()))
def test_tuple_addition(t):
    a, b = t
    assert (a, b) == t
```

## Date and Time Strategies

### Datetimes

```python
from datetime import datetime, timezone

st.datetimes()                        # All datetimes
st.datetimes(min_value=datetime(2020, 1, 1), max_value=datetime(2025, 12, 31))
st.datetimes(timezones=st.just(timezone.utc))  # UTC only
st.datetimes(timezones=st.none())     # Naive datetimes
```

**Examples:**
```python
@given(st.datetimes())
def test_datetime_iso_roundtrip(dt):
    iso_str = dt.isoformat()
    # Can parse back (may lose some precision)
    assert isinstance(iso_str, str)
```

### Dates

```python
from datetime import date

st.dates()                            # All dates
st.dates(min_value=date(2020, 1, 1), max_value=date(2025, 12, 31))
```

### Times

```python
from datetime import time

st.times()                            # All times
st.times(min_value=time(9, 0), max_value=time(17, 0))  # 9am-5pm
```

### Timedeltas

```python
from datetime import timedelta

st.timedeltas()                       # All timedeltas
st.timedeltas(min_value=timedelta(seconds=0), max_value=timedelta(days=1))
```

## Special Types

### UUIDs

```python
import uuid

st.uuids()                            # UUID objects
st.uuids().map(str)                   # UUID strings
```

**Examples:**
```python
@given(st.uuids())
def test_uuid_version(u):
    # Most generated UUIDs will be version 4
    assert isinstance(u, uuid.UUID)

@given(st.uuids().map(str))
def test_uuid_string_format(s):
    assert len(s) == 36  # Standard UUID string length
    assert s.count('-') == 4
```

### Email Addresses

```python
# Requires hypothesis[cli] or manual implementation
# Using email strategy (if available)
st.emails()  # Valid email addresses

# Manual email generation
@composite
def emails(draw):
    local = draw(st.text(alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd'),
        min_codepoint=ord('a')
    ), min_size=1, max_size=20))
    domain = draw(st.text(alphabet=st.characters(
        whitelist_categories=('Ll',),
        min_codepoint=ord('a')
    ), min_size=1, max_size=15))
    tld = draw(st.sampled_from(['com', 'org', 'net', 'io', 'edu']))
    return f"{local}@{domain}.{tld}"
```

## Combinators

### one_of

```python
# Generate from multiple strategies
st.one_of(st.integers(), st.text())   # Either int or str
st.one_of(st.none(), st.text())       # Optional[str]
```

**Examples:**
```python
@given(st.one_of(st.integers(), st.text()))
def test_handles_union_types(value):
    assert isinstance(value, (int, str))
```

### builds

```python
# Build instances of classes
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

st.builds(Point)                      # Point instances with random x, y
st.builds(Point, x=st.integers(0, 100), y=st.integers(0, 100))  # Custom ranges
```

**Examples:**
```python
@given(st.builds(Point))
def test_point_creation(p):
    assert isinstance(p, Point)
    assert isinstance(p.x, int)
    assert isinstance(p.y, int)
```

### fixed_dictionaries

```python
# Dictionaries with specific keys
st.fixed_dictionaries({
    'name': st.text(),
    'age': st.integers(0, 120),
    'active': st.booleans()
})
```

**Examples:**
```python
@given(st.fixed_dictionaries({
    'type': st.just('command_request'),
    'command': st.sampled_from(['execute', 'status']),
    'correlation_id': st.uuids().map(str)
}))
def test_command_request_structure(req):
    assert req['type'] == 'command_request'
    assert req['command'] in ['execute', 'status']
```

### just

```python
# Always generate the same value
st.just(42)                           # Always 42
st.just("constant")                   # Always "constant"
st.just(None)                         # Always None (equivalent to st.none())
```

### recursive

```python
# Generate recursive structures (trees, nested lists)
json_values = st.recursive(
    st.one_of(st.none(), st.booleans(), st.floats(), st.text()),
    lambda children: st.lists(children) | st.dictionaries(st.text(), children),
    max_leaves=10
)
```

**Examples:**
```python
@given(json_values)
def test_json_serializable(value):
    import json
    # Should be able to serialize any generated value
    serialized = json.dumps(value)
    assert isinstance(serialized, str)
```

## Advanced Strategies

### @composite

Build custom strategies by composing other strategies:

```python
from hypothesis.strategies import composite

@composite
def valid_user_records(draw):
    """Generate valid user records."""
    age = draw(st.integers(min_value=18, max_value=120))

    # Email format
    username = draw(st.text(alphabet=st.characters(
        whitelist_categories=('Ll', 'Lu', 'Nd')
    ), min_size=1, max_size=20))
    domain = draw(st.sampled_from(['example.com', 'test.org', 'demo.net']))

    return {
        'age': age,
        'email': f"{username}@{domain}",
        'active': draw(st.booleans()),
        'created_at': draw(st.datetimes())
    }

@given(valid_user_records())
def test_user_record(user):
    assert user['age'] >= 18
    assert '@' in user['email']
```

### data()

Draw from strategies dynamically within tests:

```python
from hypothesis import given
from hypothesis.strategies import data

@given(data())
def test_dynamic_strategy(data):
    # Draw from strategies during test execution
    x = data.draw(st.integers())
    y = data.draw(st.integers(min_value=x))  # y >= x
    assert y >= x
```

### shared()

Share generated values across strategies:

```python
shared_int = st.shared(st.integers(), key="my_int")

@given(shared_int, shared_int)
def test_shared_values(a, b):
    assert a == b  # Both use same generated value
```

## Strategy Selection Guide

| Data Type | Strategy | Example |
|-----------|----------|---------|
| `int` | `st.integers()` | `st.integers(min_value=0)` |
| `float` | `st.floats()` | `st.floats(allow_nan=False)` |
| `str` | `st.text()` | `st.text(min_size=1)` |
| `bool` | `st.booleans()` | `st.booleans()` |
| `bytes` | `st.binary()` | `st.binary(min_size=1)` |
| `List[int]` | `st.lists(st.integers())` | `st.lists(st.integers(), min_size=1)` |
| `Dict[str, int]` | `st.dictionaries(st.text(), st.integers())` | `st.dictionaries(...)` |
| `Set[str]` | `st.sets(st.text())` | `st.sets(st.text(), min_size=1)` |
| `Tuple[int, str]` | `st.tuples(st.integers(), st.text())` | `st.tuples(...)` |
| `Optional[str]` | `st.one_of(st.text(), st.none())` | `st.one_of(...)` |
| `UUID` | `st.uuids()` | `st.uuids().map(str)` |
| `datetime` | `st.datetimes()` | `st.datetimes(timezones=st.just(UTC))` |
| `Enum` | `st.sampled_from(MyEnum)` | `st.sampled_from(...)` |
| Pydantic model | `builds(MyModel)` | `builds(MyModel, field=st.integers())` |
| Custom class | `builds(MyClass)` | `builds(MyClass, arg=st.text())` |

## Performance Tips

1. **Constrain strategies appropriately:**
   - `st.text(max_size=100)` faster than `st.text()`
   - `st.integers(0, 1000)` faster than `st.integers()`

2. **Avoid over-filtering with `assume()`:**
   - Prefer constrained strategies over `assume()` filtering
   - Too many `assume()` calls slow down generation

3. **Use `@composite` for complex objects:**
   - More efficient than chaining many `.map()` calls
   - Better shrinking behavior

4. **Profile-specific settings:**
   - Use fewer examples in dev (`max_examples=50`)
   - More examples in CI (`max_examples=200`)
   - Thorough testing (`max_examples=1000+`)

## Common Patterns

### Generate Valid Identifiers

```python
identifiers = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'), min_codepoint=ord('a')),
    min_size=1,
    max_size=20
).filter(lambda s: s[0].isalpha())  # Must start with letter
```

### Generate File Paths

```python
from pathlib import Path

@composite
def file_paths(draw):
    parts = draw(st.lists(
        st.text(alphabet=st.characters(whitelist_categories=('Ll',)), min_size=1, max_size=10),
        min_size=1,
        max_size=5
    ))
    return Path('/'.join(parts))
```

### Generate JSON-Compatible Values

```python
json_primitives = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.text()
)

json_values = st.recursive(
    json_primitives,
    lambda children: st.lists(children) | st.dictionaries(st.text(), children),
    max_leaves=20
)
```

## Further Reading

- Official Hypothesis documentation: https://hypothesis.readthedocs.io/en/latest/data.html
- Hypothesis strategies cookbook: https://hypothesis.readthedocs.io/en/latest/strategies.html
- Custom strategies guide: https://hypothesis.readthedocs.io/en/latest/strategies.html#composite-strategies
