# Anti-Patterns Catalog

**Comprehensive database of code anti-patterns across languages and frameworks.**

---

## Universal Anti-Patterns

### Configuration Anti-Patterns

#### Optional Config Parameters
**Pattern:** Making configuration optional with default creation

**Detection:**
```python
# Python
grep -rn "def.*config.*Optional\|config.*None.*=" src/

# TypeScript
grep -rn "config\?:" src/
```

**Examples:**

```python
# ❌ WRONG
class Service:
    def __init__(self, config: Config | None = None):
        if not config:
            config = Config()  # Creates default
        self.config = config

# ✅ CORRECT
class Service:
    def __init__(self, config: Config):
        if not config:
            raise ValueError("Config is required")
        self.config = config
```

```typescript
// ❌ WRONG
class Service {
    constructor(config?: Config) {
        this.config = config || new Config();  // Creates default
    }
}

// ✅ CORRECT
class Service {
    constructor(config: Config) {
        if (!config) throw new Error("Config required");
        this.config = config;
    }
}
```

**Why it's wrong:**
- Violates fail-fast principle
- Hides configuration errors
- Makes testing harder (can't inject mocks)
- Unclear precedence (CLI args vs ENV vs defaults)

**Fix:**
- Make config required parameter
- Validate config in constructor
- Force caller to provide config
- Create config only at application entry point

---

#### Optional Dependencies (try/except ImportError)
**Pattern:** Making imports optional with try/except fallbacks

**Detection:**
```bash
grep -rn "try:.*import" src/ -A 3 | grep "except ImportError"
```

**Examples:**

```python
# ❌ WRONG
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

def cache_data(key, value):
    if REDIS_AVAILABLE:
        redis.set(key, value)
    # Silently fails if Redis unavailable

# ✅ CORRECT
import redis  # Fails fast if missing

def cache_data(key, value):
    redis.set(key, value)  # Caller handles errors
```

**Why it's wrong:**
- Silent failures
- Code paths untested (if optional dep missing)
- Hides missing dependencies until runtime
- Makes dependency requirements unclear

**Fix:**
- All imports at top of file
- Fail fast if dependency missing
- Document all required dependencies
- Use `requirements.txt` or `package.json`

---

### Single Responsibility Anti-Patterns

#### Methods with "and" in Name
**Pattern:** Methods doing multiple things

**Detection:**
```bash
grep -rn "def.*_and_.*\|function.*And" src/
```

**Examples:**

```python
# ❌ WRONG (violates SRP)
def validate_and_save_user(user_data: dict):
    # Validation (responsibility 1)
    if not user_data.get("email"):
        raise ValueError("Email required")
    if not user_data.get("name"):
        raise ValueError("Name required")

    # Saving (responsibility 2)
    db.execute("INSERT INTO users ...", user_data)

    # Sending email (responsibility 3)
    send_welcome_email(user_data["email"])

# ✅ CORRECT (split responsibilities)
def validate_user(user_data: dict) -> ValidationResult:
    errors = []
    if not user_data.get("email"):
        errors.append("Email required")
    if not user_data.get("name"):
        errors.append("Name required")
    return ValidationResult(errors)

def save_user(user_data: dict) -> ServiceResult[User]:
    return db.execute("INSERT INTO users ...", user_data)

def send_welcome_email(email: str) -> ServiceResult[None]:
    return email_service.send(email, "Welcome!")
```

**Why it's wrong:**
- Hard to test (multiple responsibilities)
- Hard to reuse (coupled logic)
- Hard to understand (cognitive overload)
- Violates Single Responsibility Principle

**Fix:**
- Split into separate methods
- Each method does ONE thing
- Compose methods in caller
- Use orchestrator/coordinator pattern

---

#### God Objects/Classes
**Pattern:** Classes with too many responsibilities

**Detection:**
```bash
# Count methods per class
grep -A 200 "^class " src/ | grep "def " | wc -l
```

**Examples:**

```python
# ❌ WRONG (God Object - 500 lines)
class UserManager:
    def create_user(self): ...
    def update_user(self): ...
    def delete_user(self): ...
    def authenticate_user(self): ...
    def send_email(self): ...
    def log_activity(self): ...
    def validate_input(self): ...
    def format_output(self): ...
    # ... 20+ more methods

# ✅ CORRECT (split responsibilities)
class UserRepository:
    def create(self, user: User): ...
    def update(self, user: User): ...
    def delete(self, user_id: int): ...

class AuthenticationService:
    def authenticate(self, credentials: Credentials): ...

class EmailService:
    def send(self, email: Email): ...

class UserValidator:
    def validate(self, user_data: dict): ...
```

**Why it's wrong:**
- Impossible to understand entire class
- Changes affect unrelated functionality
- Testing requires massive setup
- Tight coupling to everything

**Fix:**
- Extract cohesive responsibilities into separate classes
- Use composition over inheritance
- Follow Single Responsibility Principle
- Keep classes <200 lines ideally

---

### Error Handling Anti-Patterns

#### Returning None on Error
**Pattern:** Returning None instead of proper error handling

**Detection:**
```bash
grep -rn "except.*:.*return None" src/
```

**Examples:**

```python
# ❌ WRONG (silent failure)
def get_user(user_id: int) -> User | None:
    try:
        return db.query(User).filter_by(id=user_id).first()
    except Exception as e:
        logger.error(f"Error: {e}")
        return None  # Lost error context

# Caller doesn't know WHY it failed
user = get_user(123)
if user is None:
    # Database error? User not found? Permission denied?
    print("User not found")  # Wrong assumption!

# ✅ CORRECT (ServiceResult pattern)
def get_user(user_id: int) -> ServiceResult[User]:
    try:
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            return ServiceResult.failure(f"User {user_id} not found")
        return ServiceResult.success(user)
    except Exception as e:
        return ServiceResult.failure(f"Database error: {e}")

# Caller can distinguish between error types
result = get_user(123)
if result.is_failure:
    print(f"Error: {result.error_message}")
```

**Why it's wrong:**
- Lost error context
- Caller can't distinguish error types
- Silent failures hard to debug
- No way to propagate errors up

**Fix:**
- Use Result/Option types
- Return ServiceResult[T] (success/failure)
- Include error messages
- Let caller decide how to handle

---

#### Bare try/except
**Pattern:** Catching all exceptions without handling

**Detection:**
```bash
grep -rn "except:" src/
grep -rn "catch ()" src/
```

**Examples:**

```python
# ❌ WRONG (catches everything)
try:
    result = process_data(data)
    save_result(result)
except:  # Catches KeyboardInterrupt, SystemExit, everything!
    logger.error("Something went wrong")
    return None

# ✅ CORRECT (specific exceptions)
try:
    result = process_data(data)
    save_result(result)
except ValidationError as e:
    logger.error(f"Invalid data: {e}")
    return ServiceResult.failure(f"Validation failed: {e}")
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    return ServiceResult.failure(f"Storage failed: {e}")
# Let other exceptions propagate (KeyboardInterrupt, etc.)
```

**Why it's wrong:**
- Catches system exceptions (KeyboardInterrupt)
- Hides programming errors (AttributeError, etc.)
- Makes debugging impossible
- Violates fail-fast principle

**Fix:**
- Catch specific exception types only
- Let unexpected exceptions propagate
- Log exceptions with context
- Use exception hierarchies

---

### Performance Anti-Patterns

#### N+1 Queries
**Pattern:** Querying database in loops

**Detection:**
```bash
# Python
grep -rn "for.*in.*:" src/ -A 5 | grep "query\|execute"

# JavaScript
grep -rn "\.map\|\.forEach" src/ -A 3 | grep "query\|fetch"
```

**Examples:**

```python
# ❌ WRONG (N+1 queries - 1 + 100 queries)
users = db.query("SELECT * FROM users")
for user in users:
    orders = db.query(f"SELECT * FROM orders WHERE user_id = {user.id}")
    user.orders = orders

# ✅ CORRECT (2 queries with JOIN or eager loading)
users = db.query("""
    SELECT users.*, orders.*
    FROM users
    LEFT JOIN orders ON orders.user_id = users.id
""")
```

```typescript
// ❌ WRONG (N+1 queries)
const users = await db.query("SELECT * FROM users");
for (const user of users) {
    user.orders = await db.query(
        "SELECT * FROM orders WHERE user_id = ?",
        [user.id]
    );
}

// ✅ CORRECT (single query with JOIN)
const users = await db.query(`
    SELECT users.*,
           JSON_AGG(orders.*) as orders
    FROM users
    LEFT JOIN orders ON orders.user_id = users.id
    GROUP BY users.id
`);
```

**Why it's wrong:**
- Scales poorly (100 users = 101 queries)
- Database roundtrip overhead
- Locks database for extended time
- Can cause timeouts/performance issues

**Fix:**
- Use JOINs to fetch related data
- Use eager loading (ORM feature)
- Batch queries with WHERE IN
- Use DataLoader pattern (GraphQL)

---

#### Repeated Expensive Operations
**Pattern:** Calling expensive functions in loops

**Detection:**
```bash
grep -rn "for.*in.*:" src/ -A 5 | grep -E "(json.loads|compile|parse)"
```

**Examples:**

```python
# ❌ WRONG (compiles regex 1000 times)
for item in items:
    if re.match(r"\d{3}-\d{2}-\d{4}", item):
        process(item)

# ✅ CORRECT (compile once, use many times)
pattern = re.compile(r"\d{3}-\d{2}-\d{4}")
for item in items:
    if pattern.match(item):
        process(item)
```

```javascript
// ❌ WRONG (parses JSON 1000 times)
for (const item of items) {
    const config = JSON.parse(configString);  // Same string!
    process(item, config);
}

// ✅ CORRECT (parse once)
const config = JSON.parse(configString);
for (const item of items) {
    process(item, config);
}
```

**Why it's wrong:**
- Wasteful computation
- Slows down entire loop
- Easy to miss in code reviews
- Compounds with large datasets

**Fix:**
- Hoist invariant computations outside loop
- Cache expensive results
- Use memoization for pure functions
- Profile to find hotspots

---

### Security Anti-Patterns

#### Hardcoded Secrets
**Pattern:** Credentials in source code

**Detection:**
```bash
grep -rn "password\|api_key\|secret\|token" src/ | grep "="
```

**Examples:**

```python
# ❌ WRONG (hardcoded secret)
API_KEY = "sk-1234567890abcdef"
db_password = "mysecretpassword123"

# ✅ CORRECT (environment variables)
API_KEY = os.environ["API_KEY"]
db_password = os.environ["DB_PASSWORD"]
```

```javascript
// ❌ WRONG (hardcoded secret)
const apiKey = "sk-1234567890abcdef";

// ✅ CORRECT (environment variables)
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error("API_KEY not set");
```

**Why it's wrong:**
- Secrets committed to git history
- Anyone with repo access has secrets
- Cannot rotate secrets without code change
- Security audit nightmare

**Fix:**
- Use environment variables
- Use secret management (Vault, AWS Secrets Manager)
- Add .env to .gitignore
- Scan commits for secrets (pre-commit hook)

---

#### SQL Injection
**Pattern:** String concatenation for SQL queries

**Detection:**
```bash
grep -rn "execute.*f\".*SELECT\|execute.*\".*\+.*" src/
```

**Examples:**

```python
# ❌ WRONG (SQL injection vulnerable)
user_id = request.GET.get("id")
query = f"SELECT * FROM users WHERE id = {user_id}"
db.execute(query)
# Attacker sends: id = "1 OR 1=1" → returns all users!

# ✅ CORRECT (parameterized query)
user_id = request.GET.get("id")
query = "SELECT * FROM users WHERE id = ?"
db.execute(query, [user_id])
```

```javascript
// ❌ WRONG (SQL injection vulnerable)
const userId = req.query.id;
const query = `SELECT * FROM users WHERE id = ${userId}`;
db.execute(query);

// ✅ CORRECT (parameterized query)
const userId = req.query.id;
const query = "SELECT * FROM users WHERE id = ?";
db.execute(query, [userId]);
```

**Why it's wrong:**
- Allows arbitrary SQL execution
- Can leak entire database
- Can delete all data
- Critical security vulnerability

**Fix:**
- Always use parameterized queries
- Never concatenate user input into SQL
- Use ORM with parameterization
- Validate input types (integers, UUIDs)

---

## Language-Specific Anti-Patterns

### Python Anti-Patterns

#### Mutable Default Arguments
**Pattern:** Using lists/dicts as default arguments

```python
# ❌ WRONG (shared state between calls)
def add_item(item, items=[]):
    items.append(item)
    return items

add_item(1)  # [1]
add_item(2)  # [1, 2] - Oops! Shared list

# ✅ CORRECT (create new list each call)
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items
```

#### Catching Exception Instead of Specific Exceptions
```python
# ❌ WRONG
try:
    data = json.loads(string)
except Exception:  # Too broad
    return None

# ✅ CORRECT
try:
    data = json.loads(string)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return ServiceResult.failure(f"Invalid JSON: {e}")
```

#### Not Using Context Managers
```python
# ❌ WRONG (file not closed if exception)
f = open("file.txt")
data = f.read()
process(data)
f.close()  # Never reached if exception!

# ✅ CORRECT (always closed)
with open("file.txt") as f:
    data = f.read()
    process(data)
```

---

### JavaScript/TypeScript Anti-Patterns

#### Unhandled Promise Rejections
```typescript
// ❌ WRONG (unhandled rejection)
fetchData()
    .then(data => process(data));
// If fetchData rejects, error silently ignored

// ✅ CORRECT (handle rejection)
fetchData()
    .then(data => process(data))
    .catch(error => logger.error("Fetch failed", error));

// ✅ EVEN BETTER (async/await)
try {
    const data = await fetchData();
    process(data);
} catch (error) {
    logger.error("Fetch failed", error);
}
```

#### Using `any` Type
```typescript
// ❌ WRONG (defeats TypeScript)
function process(data: any): any {
    return data.foo.bar.baz;  // No type checking!
}

// ✅ CORRECT (proper types)
interface Data {
    foo: { bar: { baz: string } };
}

function process(data: Data): string {
    return data.foo.bar.baz;
}
```

#### Callback Hell
```javascript
// ❌ WRONG (nested callbacks)
fetchUser((user) => {
    fetchOrders(user.id, (orders) => {
        fetchDetails(orders[0].id, (details) => {
            process(details);
        });
    });
});

// ✅ CORRECT (async/await)
async function processUser() {
    const user = await fetchUser();
    const orders = await fetchOrders(user.id);
    const details = await fetchDetails(orders[0].id);
    process(details);
}
```

---

### Go Anti-Patterns

#### Ignoring Errors
```go
// ❌ WRONG (ignored error)
data, _ := fetchData()
process(data)

// ✅ CORRECT (handle error)
data, err := fetchData()
if err != nil {
    return fmt.Errorf("fetch failed: %w", err)
}
process(data)
```

#### Not Using defer for Cleanup
```go
// ❌ WRONG (file not closed if panic)
f, err := os.Open("file.txt")
if err != nil {
    return err
}
data, err := io.ReadAll(f)
f.Close()  // Never reached if ReadAll panics!

// ✅ CORRECT (always closed)
f, err := os.Open("file.txt")
if err != nil {
    return err
}
defer f.Close()
data, err := io.ReadAll(f)
```

---

### Rust Anti-Patterns

#### Excessive `unwrap()`
```rust
// ❌ WRONG (panics on error)
let data = fetch_data().unwrap();
let result = process(data).unwrap();

// ✅ CORRECT (proper error handling)
let data = fetch_data()?;
let result = process(data)?;
Ok(result)
```

#### Clone Instead of Borrow
```rust
// ❌ WRONG (unnecessary clone)
fn process(data: String) {
    let copy = data.clone();  // Expensive!
    println!("{}", copy);
}

// ✅ CORRECT (borrow)
fn process(data: &str) {
    println!("{}", data);
}
```

---

## Detection Automation

### Pre-Commit Hook Detection
```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Detecting anti-patterns..."

# Optional config parameters
if git diff --cached | grep -q "config.*Optional\|config.*None.*="; then
    echo "❌ Optional config parameter detected"
    exit 1
fi

# try/except ImportError
if git diff --cached | grep -q "except ImportError"; then
    echo "❌ Optional dependency pattern detected"
    exit 1
fi

# Methods with "and"
if git diff --cached | grep -q "def.*_and_"; then
    echo "⚠️ Method with 'and' in name (possible SRP violation)"
    exit 1
fi

echo "✅ No anti-patterns detected"
```

### CI/CD Pipeline Detection
```yaml
# .github/workflows/quality.yml
- name: Detect Anti-Patterns
  run: |
    python .claude/scripts/detect_anti_patterns.py src/
    if [ $? -ne 0 ]; then
      echo "Anti-patterns detected"
      exit 1
    fi
```

---

## References

- **CLAUDE.md** - Project-specific anti-patterns
- **.claude/refactor-marker-guide.md** - Refactor tracking
- **Clean Code** (Robert C. Martin) - General principles
- **Refactoring** (Martin Fowler) - Pattern catalog
- **OWASP Top 10** - Security anti-patterns

---

**Last Updated:** 2025-10-17
**Version:** 1.0.0
