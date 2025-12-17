# Language-Specific Refactoring Guides

Detailed guidance for common languages and frameworks.

---

## Python

### File Patterns

```bash
Glob: "**/*.py"
Exclude: ".venv/", "venv/", "__pycache__/", "*.pyc", "dist/", "build/"
```

### Common Refactoring Patterns

#### 1. Function/Method Rename

**Discovery:**
```bash
Grep: "def function_name\(|\.function_name\("
```

**Considerations:**
- Check for `@property` decorators (different usage pattern)
- Check for magic methods (`__init__`, `__str__`)
- Update docstrings if they reference the function name

#### 2. Class Rename

**Discovery:**
```bash
Grep: "class OldName|: OldName|OldName\(|\[OldName\]"
```

**Considerations:**
- Check inheritance: `class Child(OldName)`
- Check type hints: `def foo() -> OldName:`
- Check generic types: `List[OldName]`, `Optional[OldName]`
- Check isinstance checks: `isinstance(obj, OldName)`
- Update test class names (often `TestOldName`)

#### 3. Module Refactoring

**Discovery:**
```bash
Grep: "from old_module import|import old_module"
```

**Considerations:**
- Absolute imports: `from package.old_module import X`
- Relative imports: `from .old_module import X`, `from ..old_module import X`
- Star imports: `from old_module import *` (discourage these)
- Check `__init__.py` for re-exports
- Update `__all__` if present

#### 4. Package Restructuring

**Steps:**
```bash
# 1. Create new package structure
bash: "mkdir -p src/new_package"

# 2. Move files
bash: "mv src/old_package/*.py src/new_package/"

# 3. Update imports in moved files (relative imports)
# 4. Update imports in files that use the package (absolute imports)
# 5. Update __init__.py in both old and new packages
# 6. Update setup.py/pyproject.toml if package structure changed
```

### Import Update Patterns

#### Absolute Imports
```python
# Before
from old_package.old_module import OldClass

# After
from new_package.new_module import NewClass
```

#### Relative Imports
```python
# Before (within old_package)
from .old_module import OldClass
from ..parent import ParentClass

# After (within new_package)
from .new_module import NewClass
from ..parent import ParentClass
```

#### Star Imports (Convert to Explicit)
```python
# Before (anti-pattern)
from old_module import *

# After (explicit)
from new_module import Class1, Class2, function1
```

### Quality Gates

```bash
# Type checking
bash: "pyright src/"
# Or: "mypy src/"

# Tests
bash: "pytest tests/ -v"
# With coverage: "pytest tests/ --cov=src --cov-report=term-missing"

# Linting
bash: "ruff check src/"
# Or: "flake8 src/", "pylint src/"

# Dead code
bash: "vulture src/"

# Import sorting
bash: "isort src/ --check-diff"

# Formatting
bash: "black src/ --check"
```

### Common Pitfalls

1. **Forgetting type hints in signatures**
   ```python
   # Don't forget to update type hints
   def process(data: OldType) -> OldType:  # Update both!
   ```

2. **Missing docstring references**
   ```python
   def new_function():
       """Process data using old_function."""  # ← Update this!
   ```

3. **String-based references**
   ```python
   # Dynamic imports or references
   module = importlib.import_module("old.module")  # ← Update this!
   ```

---

## JavaScript / TypeScript

### File Patterns

```bash
Glob: "**/*.{js,jsx,ts,tsx}"
Exclude: "node_modules/", "dist/", "build/", "coverage/", "*.min.js"
```

### Common Refactoring Patterns

#### 1. Function/Class Rename

**Discovery:**
```bash
Grep: "function functionName|const functionName|class ClassName"
Grep: "functionName\(|new ClassName\("
```

**Considerations:**
- Named exports: `export function functionName`
- Default exports: `export default functionName`
- Re-exports: `export { functionName } from './module'`
- Destructured imports: `const { functionName } = require('./module')`

#### 2. Component Rename (React/Vue)

**Discovery:**
```bash
Grep: "function ComponentName|class ComponentName|const ComponentName"
Grep: "<ComponentName|ComponentName\.jsx|ComponentName\.tsx"
```

**Considerations:**
- JSX usage: `<OldComponent />` → `<NewComponent />`
- Display names: `ComponentName.displayName = 'ComponentName'`
- PropTypes: `ComponentName.propTypes = { ... }`
- Lazy loading: `React.lazy(() => import('./OldComponent'))`
- File names: `OldComponent.jsx` → `NewComponent.jsx`
- Test files: `OldComponent.test.js` → `NewComponent.test.js`
- Storybook files: `OldComponent.stories.js`

#### 3. Module Refactoring

**Discovery:**
```bash
Grep: "import.*from ['\"].*old-module|require\(['\"].*old-module"
```

**Import Patterns:**

```javascript
// ES6 Imports
import DefaultExport from './old-module';
import { namedExport } from './old-module';
import * as Module from './old-module';
import { oldName as newName } from './old-module';

// CommonJS
const module = require('./old-module');
const { namedExport } = require('./old-module');

// Dynamic imports
const module = await import('./old-module');
```

### TypeScript-Specific Considerations

#### Type Definitions
```typescript
// Update type references
type Handler = (data: OldType) => void;  // Update OldType
interface Config {
  processor: OldClass;  // Update OldClass
}
```

#### Generic Types
```typescript
Array<OldType>
Promise<OldType>
Map<string, OldType>
Record<string, OldType>
```

#### Type Imports
```typescript
// Update type imports
import type { OldType } from './old-module';
import { type OldType } from './old-module';
```

### Quality Gates

```bash
# TypeScript type checking
bash: "tsc --noEmit"
# Or: "npm run typecheck"

# Tests
bash: "npm run test"
# Or: "yarn test", "jest", "vitest"

# Linting
bash: "eslint src/"
# Or: "npm run lint"

# Formatting
bash: "prettier --check src/"
# Or: "npm run format:check"

# Build
bash: "npm run build"
```

### Common Pitfalls

1. **Forgetting default export vs named export**
   ```javascript
   // Named export
   export function myFunction() { }
   import { myFunction } from './module';

   // Default export
   export default function myFunction() { }
   import myFunction from './module';
   ```

2. **Missing dynamic imports**
   ```javascript
   // String-based imports
   const module = await import(`./components/${componentName}`);
   ```

3. **Forgetting JSX in strings**
   ```javascript
   // Component name in strings (error messages, logs)
   console.log('Rendering OldComponent');  // ← Update this!
   ```

4. **CSS module class names**
   ```css
   .OldComponent { }  /* Update class names if tied to component */
   ```

---

## Java

### File Patterns

```bash
Glob: "**/*.java"
Exclude: "target/", "build/", "*.class", ".gradle/"
```

### Common Refactoring Patterns

#### 1. Class Rename

**Discovery:**
```bash
Grep: "class OldClassName|public class OldClassName"
Grep: "new OldClassName\(|import.*OldClassName"
```

**Considerations:**
- File name MUST match class name: `OldClass.java` → `NewClass.java`
- Package-private classes (multiple classes per file)
- Inner classes: `OuterClass.OldInnerClass`
- Anonymous classes (no rename needed, but check instantiation)

#### 2. Package Restructuring

**Discovery:**
```bash
Grep: "package com.old.package|import com.old.package"
```

**Steps:**
```bash
# 1. Create new package directory
bash: "mkdir -p src/main/java/com/new/package"

# 2. Move files
bash: "mv src/main/java/com/old/package/*.java src/main/java/com/new/package/"

# 3. Update package declarations in moved files
Edit: "package com.old.package;" → "package com.new.package;"

# 4. Update imports in all files
Grep: "import com.old.package" → update to "import com.new.package"

# 5. Update Maven/Gradle configs if needed
```

#### 3. Method Rename

**Discovery:**
```bash
Grep: "public.*methodName\(|private.*methodName\(|\.methodName\("
```

**Considerations:**
- Method overloading (multiple signatures with same name)
- Interface implementations (must match interface)
- Annotation processors (check generated code)
- Reflection usage (string-based method names)

### Import Update Patterns

```java
// Single class import
import com.old.package.OldClass;
→ import com.new.package.NewClass;

// Static import
import static com.old.package.OldClass.METHOD_NAME;
→ import static com.new.package.NewClass.METHOD_NAME;

// Wildcard import (discouraged)
import com.old.package.*;
→ import com.new.package.*;
```

### Quality Gates

```bash
# Maven
bash: "mvn clean compile"
bash: "mvn test"
bash: "mvn checkstyle:check"
bash: "mvn pmd:check"

# Gradle
bash: "./gradlew clean build"
bash: "./gradlew test"
bash: "./gradlew check"
```

### Common Pitfalls

1. **File name must match public class name**
   ```java
   // File: NewClass.java
   public class NewClass { }  // ✅ Correct

   // File: OldClass.java
   public class NewClass { }  // ❌ Wrong! File name must match
   ```

2. **Reflection and string-based class references**
   ```java
   Class.forName("com.old.package.OldClass");  // ← Update this!
   ```

3. **Annotation processor references**
   ```java
   @Entity(name = "old_class")  // May need update
   ```

---

## Go

### File Patterns

```bash
Glob: "**/*.go"
Exclude: "vendor/", "*.pb.go" (generated protobuf)
```

### Common Refactoring Patterns

#### 1. Function/Type Rename

**Discovery:**
```bash
Grep: "func FunctionName|type TypeName"
Grep: "\.FunctionName\(|TypeName\{"
```

**Considerations:**
- Exported vs unexported (capitalization matters)
- Receiver functions: `func (r *Receiver) MethodName()`
- Interface implementations (must match interface)

#### 2. Package Refactoring

**Discovery:**
```bash
Grep: "package oldpkg|import.*oldpkg"
```

**Go-specific rules:**
- Package name should match directory name (by convention)
- All files in directory must have same package declaration
- Import path is directory path, not package name

**Steps:**
```bash
# 1. Create new package directory
bash: "mkdir -p pkg/newpkg"

# 2. Move files
bash: "mv pkg/oldpkg/*.go pkg/newpkg/"

# 3. Update package declarations
Edit: "package oldpkg" → "package newpkg"

# 4. Update imports
Grep: "import.*oldpkg" → update to "newpkg"
```

### Import Update Patterns

```go
// Single import
import "github.com/user/repo/old/package"
→ import "github.com/user/repo/new/package"

// Aliased import
import oldpkg "github.com/user/repo/old/package"
→ import newpkg "github.com/user/repo/new/package"

// Multiple imports
import (
    "github.com/user/repo/old/package"
)
→
import (
    "github.com/user/repo/new/package"
)
```

### Visibility Changes

```go
// Unexported (private) → Exported (public)
type myType struct { }  // Only in package
→ type MyType struct { }  // Accessible outside

// Exported (public) → Unexported (private)
func ExportedFunc() { }  // Accessible outside
→ func unexportedFunc() { }  // Only in package
```

### Quality Gates

```bash
# Build
bash: "go build ./..."

# Tests
bash: "go test ./..."
bash: "go test ./... -v"  # Verbose
bash: "go test ./... -race"  # Race detector

# Vet (static analysis)
bash: "go vet ./..."

# Linting
bash: "golangci-lint run"
# Or: "golint ./..."

# Format check
bash: "gofmt -l ."  # List unformatted files
bash: "gofmt -d ."  # Show diff
bash: "gofmt -w ."  # Write formatted files
```

### Common Pitfalls

1. **Capitalization determines visibility**
   ```go
   type ExportedType struct { }  // Public (exported)
   type unexportedType struct { }  // Private (unexported)
   ```

2. **Package name vs directory name**
   ```go
   // Directory: pkg/mypackage/
   // File: pkg/mypackage/types.go
   package mypackage  // Package name should match directory
   ```

3. **Interface implementation is implicit**
   ```go
   // If you rename a method, check if it implements any interfaces
   type MyInterface interface {
       OldMethod()  // Must update here too!
   }
   ```

---

## Ruby

### File Patterns

```bash
Glob: "**/*.rb"
Exclude: "vendor/", "tmp/"
```

### Common Refactoring Patterns

#### 1. Class/Module Rename

**Discovery:**
```bash
Grep: "class OldName|module OldName"
Grep: "OldName\.new|OldName\:\:"
```

**Considerations:**
- File name convention: `OldClass` → `old_class.rb`
- Namespacing: `Module::OldClass` → `Module::NewClass`
- Autoloading (Rails) expects specific file structure

#### 2. Method Rename

**Discovery:**
```bash
Grep: "def old_method|\.old_method\("
```

**Considerations:**
- Symbol references: `:old_method` (common in Rails)
- String references: `'old_method'`, `"old_method"`
- Dynamic methods: `send(:old_method)`
- Metaprogramming: `define_method :old_method`

### Rails-Specific Considerations

#### Model Rename
```ruby
# 1. Rename class
class OldModel → class NewModel

# 2. Rename file
app/models/old_model.rb → app/models/new_model.rb

# 3. Database migration (rename table)
rails generate migration RenameOldModelsToNewModels

# 4. Update associations in other models
has_many :old_models → has_many :new_models

# 5. Update controllers, views, routes
```

#### Controller Rename
```ruby
# 1. Rename class
class OldController → class NewController

# 2. Rename file
app/controllers/old_controller.rb → new_controller.rb

# 3. Update routes
resources :old → resources :new

# 4. Update views directory
app/views/old/ → app/views/new/

# 5. Update specs/tests
spec/controllers/old_controller_spec.rb → new_controller_spec.rb
```

### Quality Gates

```bash
# Tests
bash: "rspec"
bash: "rake test"  # Rails

# Linting
bash: "rubocop"

# Type checking (if using Sorbet)
bash: "srb tc"

# Rails-specific
bash: "rails test:system"  # System tests
bash: "rails db:migrate"  # Run migrations
```

---

## C# / .NET

### File Patterns

```bash
Glob: "**/*.cs"
Exclude: "bin/", "obj/", "*.Designer.cs"
```

### Common Refactoring Patterns

#### 1. Class/Interface Rename

**Discovery:**
```bash
Grep: "class OldClass|interface IOldInterface"
Grep: "new OldClass\(|: IOldInterface"
```

**Considerations:**
- File name should match type name: `OldClass.cs` → `NewClass.cs`
- Namespace declarations
- Using directives: `using OldNamespace;`

#### 2. Namespace Refactoring

**Discovery:**
```bash
Grep: "namespace OldNamespace|using OldNamespace"
```

**Steps:**
```bash
# 1. Update namespace declaration in all files
Edit: "namespace OldNamespace" → "namespace NewNamespace"

# 2. Update using directives
Edit: "using OldNamespace;" → "using NewNamespace;"

# 3. Update project file if namespace is project root namespace
```

### Quality Gates

```bash
# Build
bash: "dotnet build"

# Tests
bash: "dotnet test"

# Restore packages
bash: "dotnet restore"

# Code analysis
bash: "dotnet format --verify-no-changes"
```

---

## Summary Table: Language-Specific Quick Reference

| Language | File Pattern | Main Refactor Concern | Quality Gate |
|----------|--------------|----------------------|--------------|
| Python | `**/*.py` | Import paths (absolute/relative) | `pytest`, `pyright` |
| JavaScript/TS | `**/*.{js,ts,jsx,tsx}` | Default vs named exports | `npm test`, `tsc` |
| Java | `**/*.java` | File name = class name | `mvn test`, `gradle test` |
| Go | `**/*.go` | Capitalization = visibility | `go test`, `go vet` |
| Ruby | `**/*.rb` | Symbol/string method refs | `rspec`, `rubocop` |
| C# | `**/*.cs` | Namespace + file structure | `dotnet test`, `dotnet build` |

---

## General Best Practices (All Languages)

1. **Read before editing** - Understand context
2. **Use MultiEdit for 2+ changes** - Token efficiency
3. **Update imports/using statements** - Don't forget!
4. **Run tests** - Required, not optional
5. **Check quality gates** - Linting, type checking
6. **Validate completeness** - Grep for missed occurrences
7. **Follow language conventions** - File naming, casing, structure
8. **Update tests and fixtures** - Often forgotten!
9. **Check for string references** - Dynamic imports, reflection
10. **Verify builds succeed** - Compile or bundle without errors
