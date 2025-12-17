# Minimal Abstractions - Practical Examples

This document provides comprehensive examples of applying the minimal-abstractions principle across different scenarios.

## Table of Contents

1. Real-World Refactoring Examples
2. Code Review Scenarios
3. Architecture Decision Examples
4. Common Pitfalls and Fixes
5. Language-Specific Examples

## 1. Real-World Refactoring Examples

### Example 1: Authentication System Simplification

**Before (Over-Engineered):**
```python
# domain/auth/interfaces.py
class AuthenticationService(Protocol):
    def authenticate(self, credentials: Credentials) -> Result[User, AuthError]: ...

class PasswordValidator(Protocol):
    def validate(self, password: str) -> bool: ...

class TokenGenerator(Protocol):
    def generate(self, user: User) -> str: ...

# application/auth/services.py
class AuthenticationServiceImpl:
    def __init__(
        self,
        user_repo: UserRepository,
        password_validator: PasswordValidator,
        token_generator: TokenGenerator,
    ):
        self.user_repo = user_repo
        self.password_validator = password_validator
        self.token_generator = token_generator

    def authenticate(self, credentials: Credentials) -> Result[User, AuthError]:
        # Just coordinates - no real business logic unique to "service"
        user = self.user_repo.get_by_email(credentials.email)
        if not user:
            return Err(AuthError.USER_NOT_FOUND)
        if not self.password_validator.validate(credentials.password):
            return Err(AuthError.INVALID_PASSWORD)
        return Ok(user)

# infrastructure/auth/password.py
class BcryptPasswordValidator:  # Only implementation
    def validate(self, password: str) -> bool:
        return bcrypt.checkpw(password, stored_hash)

# infrastructure/auth/tokens.py
class JwtTokenGenerator:  # Only implementation
    def generate(self, user: User) -> str:
        return jwt.encode({"user_id": user.id}, secret)
```

**Problem Analysis:**
- 3 interfaces with only 1 implementation each (lonely interfaces)
- AuthenticationServiceImpl just forwards calls (no unique business logic)
- Password validation and token generation are simple operations wrapped unnecessarily

**After (Right-Sized):**
```python
# domain/auth/repositories.py (reuse existing pattern)
class UserRepository(Protocol):  # Already exists in project
    def get_by_email(self, email: str) -> User | None: ...

# application/auth/handlers.py
class AuthenticateUserHandler:
    """Handle user authentication with password verification."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def handle(self, email: str, password: str) -> Result[AuthToken, AuthError]:
        """Authenticate user and return token.

        Business logic lives here - no unnecessary service layer.
        """
        user = self.user_repo.get_by_email(email)
        if not user:
            return Err(AuthError.USER_NOT_FOUND)

        # Direct use of libraries - no wrapper needed
        if not bcrypt.checkpw(password.encode(), user.password_hash):
            return Err(AuthError.INVALID_PASSWORD)

        # Generate token directly
        token = jwt.encode(
            {"user_id": user.id, "exp": datetime.utcnow() + timedelta(hours=24)},
            settings.SECRET_KEY,
        )

        return Ok(AuthToken(value=token, user_id=user.id))
```

**Improvements:**
- Removed 3 unnecessary interfaces
- Removed service layer that added no value
- Direct use of bcrypt and jwt libraries (well-tested, no need to wrap)
- Business logic clearly visible in handler
- Fewer files, less indirection, same functionality

---

### Example 2: Repository Pattern Over-Abstraction

**Before (Over-Engineered):**
```python
# domain/common/repository.py
class Repository(Protocol, Generic[T, ID]):
    """Generic repository interface."""
    def get_by_id(self, id: ID) -> T | None: ...
    def save(self, entity: T) -> None: ...
    def delete(self, id: ID) -> None: ...
    def list_all(self) -> list[T]: ...

# domain/common/base_repository.py
class BaseRepository(ABC, Generic[T, ID]):
    """Abstract base repository with common logic."""

    @abstractmethod
    def _get_table_name(self) -> str: ...

    def get_by_id(self, id: ID) -> T | None:
        # Common SQL logic
        pass

    def save(self, entity: T) -> None:
        # Common SQL logic
        pass

# infrastructure/repositories/user_repository.py
class SqlUserRepository(BaseRepository[User, int]):
    """User repository implementation."""

    def _get_table_name(self) -> str:
        return "users"

    # Inherits all methods from BaseRepository
```

**Problem Analysis:**
- Generic Repository interface assumes all entities have same operations
- BaseRepository forces inheritance (not composition)
- Common logic assumption may not hold (different entities have different needs)
- Premature generalization before knowing actual requirements

**After (Right-Sized):**
```python
# domain/repositories.py
class UserRepository(Protocol):
    """User-specific repository interface.

    Protocol in domain for dependency inversion.
    Implementation in infrastructure.
    """
    def get_user(self, user_id: int) -> User | None: ...
    def get_user_by_email(self, email: str) -> User | None: ...
    def save_user(self, user: User) -> None: ...
    def list_active_users(self) -> list[User]: ...

class ProductRepository(Protocol):
    """Product-specific repository interface.

    Different operations than UserRepository - no forced commonality.
    """
    def get_product(self, product_id: int) -> Product | None: ...
    def search_products(self, query: str, filters: ProductFilters) -> list[Product]: ...
    def save_product(self, product: Product) -> None: ...
    def get_products_by_category(self, category: str) -> list[Product]: ...

# infrastructure/repositories.py
class SqlUserRepository:
    """SQL implementation of UserRepository."""

    def __init__(self, db: Database):
        self.db = db

    def get_user(self, user_id: int) -> User | None:
        row = self.db.query_one("SELECT * FROM users WHERE id = ?", user_id)
        return User.from_row(row) if row else None

    def get_user_by_email(self, email: str) -> User | None:
        row = self.db.query_one("SELECT * FROM users WHERE email = ?", email)
        return User.from_row(row) if row else None

    # ... other methods specific to User needs

class SqlProductRepository:
    """SQL implementation of ProductRepository."""

    def __init__(self, db: Database):
        self.db = db

    # Completely different implementation details
    # No forced commonality with UserRepository
```

**Improvements:**
- Removed generic abstraction that forced commonality
- Each repository has operations specific to its entity
- No inheritance - composition via dependency injection
- Easier to add entity-specific methods
- Clearer intent - UserRepository methods are user-centric

---

## 2. Code Review Scenarios

### Scenario 1: PR Introduces New Interface

**PR Description:** "Add ConfigurationService for environment variable management"

**Code Submitted:**
```python
# domain/config/service.py
class ConfigurationService(Protocol):
    def get_config(self, key: str) -> str: ...
    def set_config(self, key: str, value: str) -> None: ...

# infrastructure/config/env_service.py
class EnvironmentConfigService:
    def get_config(self, key: str) -> str:
        return os.getenv(key, "")

    def set_config(self, key: str, value: str) -> None:
        os.environ[key] = value
```

**Review Using Minimal-Abstractions:**

Run checklist:
1. Does this abstraction already exist? → Check codebase... No similar config abstraction found.
2. Are there 2+ implementations? → NO - only EnvironmentConfigService
3. Is there a concrete requirement? → PR says "for future database config support" (speculative!)
4. Complexity cost? → +2 files, +30 LOC, interface indirection
5. Simpler solution? → YES - Use pydantic-settings directly (project standard)

**Review Comment:**
```
❌ Unnecessary Abstraction

This PR introduces ConfigurationService interface with only one implementation.
The justification "for future database config support" is speculative (YAGNI).

This project already uses pydantic-settings for configuration (see src/config/settings.py).

**Recommendation:**
Use existing Settings class instead:

# config/settings.py (already exists)
class Settings(BaseSettings):
    database_url: str
    api_key: str
    # ... existing config

    class Config:
        env_file = ".env"

# Usage
settings = Settings()
db_url = settings.database_url

**Benefits:**
- No new abstraction
- Type-safe configuration (mypy validation)
- Validation built-in (pydantic)
- Follows project conventions

Please update the PR to use Settings instead of introducing ConfigurationService.
```

---

### Scenario 2: Factory Pattern Misuse

**PR Description:** "Add UserFactory for user creation"

**Code Submitted:**
```python
class UserFactory:
    @staticmethod
    def create_standard_user(email: str, name: str) -> User:
        return User(
            id=None,
            email=email,
            name=name,
            role=UserRole.STANDARD,
            created_at=datetime.utcnow(),
        )

    @staticmethod
    def create_admin_user(email: str, name: str) -> User:
        return User(
            id=None,
            email=email,
            name=name,
            role=UserRole.ADMIN,
            created_at=datetime.utcnow(),
        )
```

**Review Using Minimal-Abstractions:**

Run checklist:
1. Is Factory pattern needed? → Check if complex construction logic exists... NO
2. Are there variants that justify factory? → Just role difference
3. Simpler solution? → YES - Use dataclass with default values

**Review Comment:**
```
❌ Unnecessary Factory Pattern

UserFactory adds no value - it's just forwarding to User constructor with
different role values. Factory pattern is appropriate when:
- Complex object assembly is required
- Object creation logic is complex
- Multiple interdependent objects need coordination

None of these apply here.

**Recommendation:**
Use User dataclass directly with sensible defaults:

@dataclass
class User:
    email: str
    name: str
    role: UserRole = UserRole.STANDARD
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: int | None = None

# Usage
standard_user = User(email="alice@example.com", name="Alice")
admin_user = User(email="bob@example.com", name="Bob", role=UserRole.ADMIN)

**Benefits:**
- Direct construction (no indirection)
- Type-safe (mypy validates)
- Fewer files (no factory.py)
- Clear and explicit
```

---

## 3. Architecture Decision Examples

### Decision 1: Should We Add a Service Layer?

**Context:** Team proposes adding service layer between handlers and repositories.

**Proposal:**
```
src/
├── domain/
│   ├── repositories.py (interfaces)
├── application/
│   ├── handlers.py (CQRS handlers)
│   ├── services.py (NEW - proposed)
├── infrastructure/
│   ├── repositories.py (implementations)
```

**Evaluation Using Minimal-Abstractions:**

**Checklist:**
1. Does service layer abstraction exist? → NO
2. Is there business logic that needs orchestration? → Check handlers... they're simple CRUD
3. Is complexity justified? → Adds +1 layer, indirection cost
4. Simpler solution? → Keep business logic in handlers

**Decision: REJECT Service Layer**

**Rationale:**
```
Current handlers are simple CRUD operations:
- CreateUserHandler: validates input → saves to repo
- GetUserHandler: fetches from repo → returns result

Adding a service layer would just forward calls:

# This adds no value:
class UserService:
    def create_user(self, data: CreateUserData) -> User:
        return self.repo.save_user(User(...))  # Just forwarding

# Current approach is simpler:
class CreateUserHandler:
    def handle(self, data: CreateUserData) -> Result[User, Error]:
        user = User(...)
        self.user_repo.save_user(user)
        return Ok(user)

**When to revisit:**
Add service layer IF:
- Multi-step business logic emerges
- Transactions span multiple repositories
- Complex orchestration is needed

Current state: No service layer needed.
```

---

### Decision 2: Generic Error Handling Abstraction

**Proposal:** Create generic Result wrapper with error handling DSL

**Proposed Code:**
```python
class Result(Generic[T, E]):
    def map(self, fn: Callable[[T], U]) -> Result[U, E]: ...
    def map_err(self, fn: Callable[[E], F]) -> Result[T, F]: ...
    def and_then(self, fn: Callable[[T], Result[U, E]]) -> Result[U, E]: ...
    def or_else(self, fn: Callable[[E], Result[T, F]]) -> Result[T, F]: ...
    def unwrap(self) -> T: ...
    def unwrap_or(self, default: T) -> T: ...
    def unwrap_or_else(self, fn: Callable[[E], T]) -> T: ...
    # ... 15 more methods
```

**Evaluation Using Minimal-Abstractions:**

**Checklist:**
1. Does error handling exist? → YES - project uses simple Result[T, E] with Ok/Err
2. Are all these methods needed? → Check usage... only Ok/Err/match used
3. Complexity cost? → +200 LOC, learning curve for team
4. Simpler solution? → Keep current simple Result

**Decision: REJECT Generic Error DSL**

**Rationale:**
```
Current Result pattern is simple and sufficient:

# Current usage (works well):
def get_user(id: int) -> Result[User, UserError]:
    if user := self.repo.get(id):
        return Ok(user)
    return Err(UserError.NOT_FOUND)

# Calling code:
result = get_user(123)
match result:
    case Ok(user):
        print(user.name)
    case Err(error):
        print(f"Error: {error}")

The proposed 15+ methods (map, and_then, unwrap_or_else, etc.) are:
- Not currently used in codebase
- Add complexity without clear benefit
- Require team training (cognitive load)
- Solve problems we don't have

**When to revisit:**
Add functional methods IF:
- We see repeated patterns that map/and_then would eliminate
- Team specifically requests functional error handling

Current state: Simple Result with match is sufficient.
```

---

## 4. Common Pitfalls and Fixes

### Pitfall 1: "Best Practice" Cargo Culting

**Symptom:** Adding patterns because "that's what the books say"

**Example:**
```python
# Developer adds Specification pattern after reading Domain-Driven Design
class Specification(ABC, Generic[T]):
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool: ...

    def and_(self, other: Specification[T]) -> Specification[T]: ...
    def or_(self, other: Specification[T]) -> Specification[T]: ...
    def not_(self) -> Specification[T]: ...

class ActiveUserSpecification(Specification[User]):
    def is_satisfied_by(self, user: User) -> bool:
        return user.is_active

# Usage (overcomplicated):
spec = ActiveUserSpecification().and_(EmailVerifiedSpecification())
matching_users = [u for u in users if spec.is_satisfied_by(u)]
```

**Fix: Use Simple Predicates**
```python
# Simple, clear, Pythonic
def is_active_user(user: User) -> bool:
    return user.is_active

def is_email_verified(user: User) -> bool:
    return user.email_verified

# Usage (simple):
active_verified_users = [
    u for u in users
    if is_active_user(u) and is_email_verified(u)
]

# Or if reusable filtering is needed:
def filter_users(
    users: list[User],
    *predicates: Callable[[User], bool]
) -> list[User]:
    return [u for u in users if all(p(u) for p in predicates)]

# Usage:
filtered = filter_users(users, is_active_user, is_email_verified)
```

---

### Pitfall 2: Premature Interface Extraction

**Symptom:** Creating interface "in case we need it later"

**Example:**
```python
# Developer extracts interface immediately
class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

class SmtpEmailSender:  # Only implementation
    def send(self, to: str, subject: str, body: str) -> None:
        # SMTP logic
        pass
```

**Fix: Wait for Second Implementation**
```python
# Start with concrete class
class EmailSender:
    """Send emails via SMTP.

    When we need a second implementation (e.g., SES, SendGrid),
    THEN extract Protocol interface.
    """
    def send(self, to: str, subject: str, body: str) -> None:
        # SMTP logic
        pass

# When second implementation is actually needed:
# 1. Extract Protocol
class EmailSender(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...

# 2. Rename original
class SmtpEmailSender:
    def send(self, to: str, subject: str, body: str) -> None: ...

# 3. Add second implementation
class SesEmailSender:
    def send(self, to: str, subject: str, body: str) -> None: ...
```

---

### Pitfall 3: Layer Tunneling

**Symptom:** Data passes through layers unchanged

**Example:**
```python
# Over-layered: Each layer just forwards
class UserController:
    def get_user(self, id: int) -> User:
        return self.service.get_user(id)

class UserService:
    def get_user(self, id: int) -> User:
        return self.repository.get_user(id)

class UserRepository:
    def get_user(self, id: int) -> User:
        return self.db.query_one("SELECT * FROM users WHERE id = ?", id)
```

**Fix: Collapse Unnecessary Layers**
```python
# Right-sized: Handler uses repository directly
class GetUserHandler:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def handle(self, id: int) -> Result[User, UserError]:
        if user := self.user_repo.get_user(id):
            return Ok(user)
        return Err(UserError.NOT_FOUND)

# Repository does actual data access
class SqlUserRepository:
    def get_user(self, id: int) -> User | None:
        row = self.db.query_one("SELECT * FROM users WHERE id = ?", id)
        return User.from_row(row) if row else None
```

---

## 5. Language-Specific Examples

### Python: When to Use Protocol vs Concrete Class

**Over-Abstracted:**
```python
# Protocol with single implementation
class JsonParser(Protocol):
    def parse(self, text: str) -> dict: ...

class StandardJsonParser:
    def parse(self, text: str) -> dict:
        return json.loads(text)
```

**Right-Sized:**
```python
# Direct use of standard library
import json

# No wrapper needed - json.loads is clear and well-tested
data = json.loads(text)

# If validation is needed, add it directly:
def parse_config(text: str) -> Config:
    """Parse and validate JSON config."""
    data = json.loads(text)
    return Config(**data)  # Pydantic validation
```

---

### TypeScript: When to Use Interface vs Type

**Over-Abstracted:**
```typescript
// Unnecessary interface hierarchy
interface Entity {
  id: number;
}

interface User extends Entity {
  email: string;
  name: string;
}

interface Product extends Entity {
  sku: string;
  price: number;
}
```

**Right-Sized:**
```typescript
// Simple types - no forced commonality
type User = {
  id: number;
  email: string;
  name: string;
};

type Product = {
  id: number;
  sku: string;
  price: number;
};

// Add commonality only when actually needed:
type WithId<T> = T & { id: number };
```

---

### Go: When to Use Interface

**Over-Abstracted:**
```go
// Interface with single implementation
type UserService interface {
    GetUser(id int) (*User, error)
    CreateUser(user *User) error
}

type userServiceImpl struct {
    repo UserRepository
}

func (s *userServiceImpl) GetUser(id int) (*User, error) {
    return s.repo.GetUser(id)  // Just forwarding
}
```

**Right-Sized:**
```go
// Accept interfaces, return concrete types
type UserRepository interface {
    GetUser(id int) (*User, error)
    SaveUser(user *User) error
}

// Concrete service
type UserService struct {
    repo UserRepository
}

func (s *UserService) GetUser(id int) (*User, error) {
    return s.repo.GetUser(id)
}

// Interface extracted only at boundaries (dependency injection)
```

---

## Summary Checklist

Before adding ANY abstraction, check:

- [ ] Does similar abstraction exist in project?
- [ ] Are there 2+ concrete implementations RIGHT NOW?
- [ ] Is there a concrete (not speculative) requirement?
- [ ] Is complexity cost justified?
- [ ] Is there a simpler solution?

If ANY answer is "no" → Don't add the abstraction.
