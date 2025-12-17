# Common Quality Gate Failures and Fixes

Comprehensive guide to the most common quality gate failures and their solutions.

## Python - Type Checking Failures

### 1. Type "None" Cannot Be Assigned to Type "str"

**Error:**
```
src/services/search.py:45 - error: Type "None" cannot be assigned to type "str"
```

**Common causes:**
```python
# Cause 1: Function can return None
def get_name(user_id: int) -> str:
    user = find_user(user_id)
    if user is None:
        return None  # ❌ Returns None, declared as str
    return user.name

# Cause 2: Variable initialized as None
name: str = None  # ❌ None assigned to str
```

**Fixes:**

**Fix 1: Use Optional type**
```python
from typing import Optional

def get_name(user_id: int) -> Optional[str]:
    user = find_user(user_id)
    if user is None:
        return None  # ✅ None is valid for Optional[str]
    return user.name
```

**Fix 2: Provide default value**
```python
def get_name(user_id: int) -> str:
    user = find_user(user_id)
    if user is None:
        return ""  # ✅ Return empty string instead of None
    return user.name
```

**Fix 3: Raise error instead of returning None**
```python
def get_name(user_id: int) -> str:
    user = find_user(user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")  # ✅ Fail fast
    return user.name
```

---

### 2. Argument Type Mismatch

**Error:**
```
src/utils/helper.py:12 - error: Argument of type "int" cannot be assigned to parameter of type "str"
```

**Common cause:**
```python
def process_value(value: str) -> None:
    print(value)

user_id = 123
process_value(user_id)  # ❌ Passing int to str parameter
```

**Fixes:**

**Fix 1: Convert type**
```python
user_id = 123
process_value(str(user_id))  # ✅ Convert int to str
```

**Fix 2: Change parameter type**
```python
def process_value(value: str | int) -> None:
    print(str(value))  # ✅ Accept both types
```

**Fix 3: Overload function**
```python
from typing import overload

@overload
def process_value(value: str) -> None: ...

@overload
def process_value(value: int) -> None: ...

def process_value(value: str | int) -> None:
    print(str(value))  # ✅ Type-safe overloading
```

---

### 3. Return Type Mismatch

**Error:**
```
src/models/result.py:8 - error: Return type "dict[str, Any]" is incompatible with declared return type "SearchResult"
```

**Common cause:**
```python
def create_result() -> SearchResult:
    return {"results": [], "count": 0}  # ❌ Returning dict, not SearchResult
```

**Fixes:**

**Fix 1: Return proper instance**
```python
def create_result() -> SearchResult:
    return SearchResult(results=[], count=0)  # ✅ Return SearchResult instance
```

**Fix 2: Change return type**
```python
def create_result() -> dict[str, Any]:
    return {"results": [], "count": 0}  # ✅ Update type annotation
```

**Fix 3: Use TypedDict**
```python
from typing import TypedDict

class SearchResultDict(TypedDict):
    results: list
    count: int

def create_result() -> SearchResultDict:
    return {"results": [], "count": 0}  # ✅ Type-safe dict
```

---

### 4. Missing Type Annotation

**Error:**
```
src/services/search.py:23 - error: Missing type annotation for variable
```

**Common cause:**
```python
results = []  # ❌ Type inferred as list[Unknown]
```

**Fix:**
```python
results: list[SearchResult] = []  # ✅ Explicit type annotation
```

---

### 5. Attribute Not Defined

**Error:**
```
src/models/user.py:45 - error: "User" has no attribute "profile"
```

**Common causes:**
```python
# Cause 1: Typo
user.proflie  # ❌ Typo in attribute name

# Cause 2: Attribute added dynamically
user.profile = Profile()  # ❌ Not defined in __init__

# Cause 3: Optional attribute not checked
def get_profile_name(user: User) -> str:
    return user.profile.name  # ❌ profile might be None
```

**Fixes:**

**Fix 1: Correct typo**
```python
user.profile  # ✅ Fixed spelling
```

**Fix 2: Define in class**
```python
class User:
    def __init__(self):
        self.profile: Optional[Profile] = None  # ✅ Define attribute
```

**Fix 3: Check for None**
```python
def get_profile_name(user: User) -> str:
    if user.profile is None:
        return "No profile"
    return user.profile.name  # ✅ Checked for None
```

---

## Python - Linting Failures

### 6. Unused Import (F401)

**Error:**
```
src/services/search.py:23 - F401 [*] `logging` imported but unused
```

**Cause:**
```python
import logging  # ❌ Imported but never used

def search(query: str):
    return []
```

**Fixes:**

**Fix 1: Remove import**
```python
# ✅ Import removed

def search(query: str):
    return []
```

**Fix 2: Use import**
```python
import logging

logger = logging.getLogger(__name__)  # ✅ Now used

def search(query: str):
    logger.info(f"Searching for: {query}")
    return []
```

---

### 7. Unused Variable (F841)

**Error:**
```
src/utils/helper.py:45 - F841 local variable 'temp' is assigned to but never used
```

**Cause:**
```python
def process_data(data: list):
    temp = calculate_intermediate(data)  # ❌ Assigned but not used
    return format_result(data)
```

**Fixes:**

**Fix 1: Remove unused variable**
```python
def process_data(data: list):
    # ✅ Removed temp variable
    return format_result(data)
```

**Fix 2: Use variable**
```python
def process_data(data: list):
    temp = calculate_intermediate(data)  # ✅ Now used
    return format_result(temp)
```

**Fix 3: Prefix with underscore (intentionally unused)**
```python
def process_data(data: list):
    _temp = calculate_intermediate(data)  # ✅ Prefix indicates intentionally unused
    return format_result(data)
```

---

### 8. Line Too Long (E501)

**Error:**
```
src/services/search.py:78 - E501 line too long (125 > 100 characters)
```

**Cause:**
```python
result = SearchResult(query=query, results=results, count=len(results), metadata={"timestamp": datetime.now(), "user": current_user})
```

**Fixes:**

**Fix 1: Break into multiple lines**
```python
result = SearchResult(
    query=query,
    results=results,
    count=len(results),
    metadata={"timestamp": datetime.now(), "user": current_user}
)
```

**Fix 2: Extract to variables**
```python
metadata = {"timestamp": datetime.now(), "user": current_user}
result = SearchResult(
    query=query,
    results=results,
    count=len(results),
    metadata=metadata
)
```

---

### 9. Undefined Name (F821)

**Error:**
```
src/models/user.py:15 - F821 undefined name 'Profile'
```

**Cause:**
```python
class User:
    def __init__(self):
        self.profile: Profile = None  # ❌ Profile not imported
```

**Fix:**
```python
from models.profile import Profile  # ✅ Import Profile

class User:
    def __init__(self):
        self.profile: Optional[Profile] = None
```

---

## Python - Test Failures

### 10. AssertionError: assert X == Y

**Error:**
```
tests/unit/test_search.py::test_search_empty - AssertionError: assert None == []
```

**Cause:**
```python
def test_search_empty():
    result = search_service.search("")
    assert result == []  # ❌ Expects empty list, gets None
```

**Fixes:**

**Fix 1: Fix the service to return []**
```python
# In search_service.py
def search(query: str) -> list[SearchResult]:
    if not query:
        return []  # ✅ Return empty list instead of None
    ...
```

**Fix 2: Update test to handle None**
```python
def test_search_empty():
    result = search_service.search("")
    assert result == [] or result is None  # ✅ Accept both
```

**Fix 3: Use ServiceResult pattern (preferred)**
```python
# In search_service.py
def search(query: str) -> ServiceResult[list[SearchResult]]:
    if not query:
        return ServiceResult.success([])  # ✅ Always return ServiceResult
    ...

# In test
def test_search_empty():
    result = search_service.search("")
    assert result.success
    assert result.value == []  # ✅ Access value from ServiceResult
```

---

### 11. AttributeError: 'NoneType' object has no attribute

**Error:**
```
tests/unit/test_search.py::test_search_invalid - AttributeError: 'NoneType' object has no attribute 'results'
```

**Cause:**
```python
def test_search_invalid():
    result = search_service.search("invalid")
    assert result.results == []  # ❌ result is None
```

**Fixes:**

**Fix 1: Check for None first**
```python
def test_search_invalid():
    result = search_service.search("invalid")
    assert result is not None, "Expected SearchResult, got None"
    assert result.results == []  # ✅ Checked for None
```

**Fix 2: Fix service to never return None**
```python
# In search_service.py
def search(query: str) -> SearchResult:
    if not is_valid(query):
        return SearchResult(results=[], count=0)  # ✅ Return empty result, not None
    ...
```

---

### 12. Mock Not Called

**Error:**
```
tests/unit/test_search.py::test_search_calls_database - AssertionError: Expected 'fetch_data' to be called once. Called 0 times.
```

**Cause:**
```python
def test_search_calls_database(mock_db):
    search_service.search("test")
    mock_db.fetch_data.assert_called_once()  # ❌ fetch_data not called
```

**Common reasons:**
1. Function uses different method name
2. Mock not properly patched
3. Function not reaching the mocked code path

**Fixes:**

**Fix 1: Check method name**
```python
def test_search_calls_database(mock_db):
    search_service.search("test")
    mock_db.query.assert_called_once()  # ✅ Correct method name
```

**Fix 2: Verify patch path**
```python
@patch("services.search.database")  # ❌ Wrong path
def test_search_calls_database(mock_db):
    ...

@patch("search_service.database")  # ✅ Correct path
def test_search_calls_database(mock_db):
    ...
```

**Fix 3: Check code path**
```python
def test_search_calls_database(mock_db):
    mock_db.is_connected.return_value = True  # ✅ Ensure code path reached
    search_service.search("test")
    mock_db.query.assert_called_once()
```

---

### 13. Test Timeout

**Error:**
```
tests/integration/test_api.py::test_large_query - TIMEOUT after 30s
```

**Causes:**
1. Infinite loop
2. Waiting for network/database
3. Missing mock/fixture

**Fixes:**

**Fix 1: Add timeout to test**
```python
@pytest.mark.timeout(5)  # ✅ Fail after 5s
def test_large_query():
    ...
```

**Fix 2: Mock slow operations**
```python
@patch("search_service.slow_operation")
def test_large_query(mock_slow):
    mock_slow.return_value = "fast result"  # ✅ Mock slow operation
    ...
```

**Fix 3: Use async properly**
```python
@pytest.mark.asyncio
async def test_large_query():
    result = await search_service.search("large")  # ✅ Await async call
    ...
```

---

## Python - Dead Code Failures

### 14. Unused Function

**Error:**
```
src/utils/helper.py:45 - unused function 'calculate_temp' (80% confidence)
```

**Cause:**
```python
def calculate_temp(value: int) -> float:  # ❌ Never called
    return value * 1.8 + 32
```

**Fixes:**

**Fix 1: Remove if truly unused**
```python
# ✅ Function removed (confirmed unused)
```

**Fix 2: Add to whitelist if intentionally unused**
```python
# In pyproject.toml or vulture.txt
calculate_temp  # Used via string import or external API
```

**Fix 3: Use the function**
```python
def process_temperature(celsius: int) -> str:
    fahrenheit = calculate_temp(celsius)  # ✅ Now used
    return f"{fahrenheit}°F"
```

---

## JavaScript/TypeScript - Type Checking Failures

### 15. Property Does Not Exist on Type

**Error:**
```
src/components/Button.tsx:23:5 - error TS2339: Property 'onClick' does not exist on type 'ButtonProps'
```

**Cause:**
```typescript
interface ButtonProps {
  label: string;
}

function Button(props: ButtonProps) {
  return <button onClick={props.onClick}>  // ❌ onClick not in ButtonProps
    {props.label}
  </button>;
}
```

**Fix:**
```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;  // ✅ Add onClick to interface
}

function Button(props: ButtonProps) {
  return <button onClick={props.onClick}>
    {props.label}
  </button>;
}
```

---

### 16. Type 'undefined' Is Not Assignable

**Error:**
```
src/utils/helper.ts:12:5 - error TS2322: Type 'string | undefined' is not assignable to type 'string'
```

**Cause:**
```typescript
const value: string = getValue();  // ❌ getValue() returns string | undefined
```

**Fixes:**

**Fix 1: Handle undefined**
```typescript
const value: string = getValue() ?? "";  // ✅ Provide default
```

**Fix 2: Change type**
```typescript
const value: string | undefined = getValue();  // ✅ Accept undefined
if (value !== undefined) {
  // Use value
}
```

**Fix 3: Non-null assertion (use cautiously)**
```typescript
const value: string = getValue()!;  // ✅ Assert non-null (dangerous if wrong)
```

---

## JavaScript/TypeScript - Linting Failures

### 17. Variable Assigned but Never Used

**Error:**
```
src/components/Button.tsx:23:7 - error: 'handleClick' is assigned a value but never used
```

**Cause:**
```typescript
const handleClick = () => {  // ❌ Defined but not used
  console.log("clicked");
};

return <button>Click me</button>;
```

**Fix:**
```typescript
const handleClick = () => {
  console.log("clicked");
};

return <button onClick={handleClick}>Click me</button>;  // ✅ Now used
```

---

### 18. Missing Dependency in useEffect

**Error:**
```
src/hooks/useSearch.ts:15:6 - warning: React Hook useEffect has a missing dependency: 'query'
```

**Cause:**
```typescript
useEffect(() => {
  fetchResults(query);  // ❌ query not in dependency array
}, []);
```

**Fixes:**

**Fix 1: Add to dependencies**
```typescript
useEffect(() => {
  fetchResults(query);
}, [query]);  // ✅ Add query to dependencies
```

**Fix 2: Use callback**
```typescript
const fetchResultsCallback = useCallback(() => {
  fetchResults(query);
}, [query]);

useEffect(() => {
  fetchResultsCallback();
}, [fetchResultsCallback]);
```

---

## JavaScript/TypeScript - Test Failures

### 19. Cannot Find Element

**Error:**
```
src/components/Button.test.tsx - error: Unable to find element with text: Click me
```

**Cause:**
```typescript
test("renders button", () => {
  render(<Button />);
  expect(screen.getByText("Click me")).toBeInTheDocument();  // ❌ Button doesn't render this text
});
```

**Fixes:**

**Fix 1: Fix test query**
```typescript
test("renders button", () => {
  render(<Button label="Submit" />);
  expect(screen.getByText("Submit")).toBeInTheDocument();  // ✅ Correct text
});
```

**Fix 2: Fix component**
```typescript
function Button() {
  return <button>Click me</button>;  // ✅ Component renders expected text
}
```

---

## Formatting Failures

### 20. Code Not Formatted

**Error:**
```
src/services/search.py - would reformat
```

**Cause:**
```python
def search(query:str)->list:  # ❌ Missing spaces
    return []
```

**Fix:**
```bash
# Run formatter
uv run ruff format src/services/search.py

# Or auto-fix all
uv run ruff format src/
```

**Result:**
```python
def search(query: str) -> list:  # ✅ Properly formatted
    return []
```

---

## Summary: Quick Reference

| Error Type | Quick Fix | Priority |
|------------|-----------|----------|
| Type "None" cannot be assigned | Use Optional or provide default | HIGH |
| Argument type mismatch | Convert type or change parameter | HIGH |
| Return type mismatch | Return correct type | HIGH |
| Unused import | Remove or use import | MEDIUM |
| Unused variable | Remove or use variable | MEDIUM |
| assert X == Y failed | Fix logic or update test | HIGH |
| AttributeError on None | Check for None first | HIGH |
| Mock not called | Fix mock path or method name | HIGH |
| Property does not exist | Add to interface | HIGH |
| Type 'undefined' not assignable | Handle undefined case | HIGH |
| Variable never used | Use variable or remove | MEDIUM |
| Missing useEffect dependency | Add to dependency array | MEDIUM |
| Code not formatted | Run formatter | LOW |

