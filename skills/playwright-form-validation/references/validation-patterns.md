# Form Validation Patterns Reference

Comprehensive reference for testing different field types and validation patterns.

## Table of Contents

1. [Text Field Validation](#text-field-validation)
2. [Email Field Validation](#email-field-validation)
3. [Password Field Validation](#password-field-validation)
4. [Phone Number Validation](#phone-number-validation)
5. [Number Field Validation](#number-field-validation)
6. [Date Field Validation](#date-field-validation)
7. [URL Field Validation](#url-field-validation)
8. [Select/Dropdown Validation](#selectdropdown-validation)
9. [Checkbox/Radio Validation](#checkboxradio-validation)
10. [Cross-Field Validation](#cross-field-validation)
11. [Validation Message Extraction](#validation-message-extraction)

## Text Field Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Empty required | `""` | "This field is required" |
| Too short | `"ab"` (if min=3) | "Minimum 3 characters" |
| Too long | `"a" * 101` (if max=100) | "Maximum 100 characters" |
| Invalid characters | `"test<script>"` | "Invalid characters" |
| Leading/trailing spaces | `"  test  "` | May trim or reject |
| Only whitespace | `"   "` | "This field is required" |

### Common Attributes

```html
<input type="text"
       required
       minlength="3"
       maxlength="100"
       pattern="[A-Za-z ]+" />
```

### Test Sequence

```typescript
// Test 1: Empty value
{ value: "" }

// Test 2: Too short
{ value: "ab" }

// Test 3: Too long
{ value: "a".repeat(101) }

// Test 4: Invalid pattern
{ value: "test123!@#" }

// Test 5: Valid
{ value: "Valid Name" }
```

## Email Field Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Empty required | `""` | "Email is required" |
| No @ symbol | `"invalidemail"` | "Invalid email format" |
| No local part | `"@example.com"` | "Invalid email format" |
| No domain | `"test@"` | "Invalid email format" |
| No TLD | `"test@example"` | "Invalid email format" |
| Spaces | `"test @example.com"` | "Invalid email format" |
| Multiple @ | `"test@@example.com"` | "Invalid email format" |
| Invalid TLD | `"test@example.c"` | "Invalid email format" |
| Special chars | `"test!#$@example.com"` | May allow or reject |

### HTML5 Pattern

```html
<input type="email" required />
```

### Test Sequence

```typescript
const emailTests = [
  { value: "", expected: "required" },
  { value: "invalid-email", expected: "format" },
  { value: "test@", expected: "format" },
  { value: "@example.com", expected: "format" },
  { value: "test @example.com", expected: "format" },
  { value: "test@example", expected: "format" },
  { value: "test@@example.com", expected: "format" },
  { value: "test@example.com", expected: "valid" }
];
```

## Password Field Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Empty required | `""` | "Password is required" |
| Too short | `"abc"` (if min=8) | "Minimum 8 characters" |
| No uppercase | `"password123"` | "Must contain uppercase" |
| No lowercase | `"PASSWORD123"` | "Must contain lowercase" |
| No number | `"Password"` | "Must contain number" |
| No special char | `"Password123"` | "Must contain special character" |
| Common password | `"Password123"` | "Password too common" |
| All valid | `"ValidPass123!"` | (success) |

### Common Requirements

- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*)
- Not in common password list

### Test Sequence

```typescript
const passwordTests = [
  { value: "", expected: "required" },
  { value: "short", expected: "too short" },
  { value: "alllowercase123", expected: "no uppercase" },
  { value: "ALLUPPERCASE123", expected: "no lowercase" },
  { value: "NoNumbers", expected: "no number" },
  { value: "NoSpecial123", expected: "no special char" },
  { value: "password", expected: "too common" },
  { value: "ValidPass123!", expected: "valid" }
];
```

## Phone Number Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Empty required | `""` | "Phone is required" |
| Letters | `"abcdefghij"` | "Invalid phone number" |
| Too short | `"123"` | "Invalid phone number" |
| Too long | `"12345678901234"` | "Invalid phone number" |
| Invalid format | `"12-34-56"` | "Invalid phone number" |
| Valid US | `"(555) 123-4567"` | (success) |
| Valid intl | `"+1-555-123-4567"` | (success) |

### Common Formats

- US: `(555) 123-4567`, `555-123-4567`, `5551234567`
- International: `+1-555-123-4567`, `+44 20 7123 4567`

### Test Sequence

```typescript
const phoneTests = [
  { value: "", expected: "required" },
  { value: "abc123", expected: "format" },
  { value: "123", expected: "too short" },
  { value: "12-34-56", expected: "format" },
  { value: "555-123-4567", expected: "valid" },
  { value: "(555) 123-4567", expected: "valid" }
];
```

## Number Field Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Empty required | `""` | "This field is required" |
| Letters | `"abc"` | "Must be a number" |
| Below min | `"5"` (if min=10) | "Minimum value is 10" |
| Above max | `"200"` (if max=100) | "Maximum value is 100" |
| Decimal not allowed | `"10.5"` (if step=1) | "Must be whole number" |
| Negative not allowed | `"-5"` | "Must be positive" |
| Valid | `"50"` | (success) |

### HTML5 Attributes

```html
<input type="number"
       required
       min="10"
       max="100"
       step="1" />
```

### Test Sequence

```typescript
const numberTests = [
  { value: "", expected: "required" },
  { value: "abc", expected: "not a number" },
  { value: "5", expected: "below min" },
  { value: "200", expected: "above max" },
  { value: "10.5", expected: "not whole" },
  { value: "-5", expected: "negative" },
  { value: "50", expected: "valid" }
];
```

## Date Field Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Empty required | `""` | "Date is required" |
| Invalid format | `"not-a-date"` | "Invalid date format" |
| Invalid date | `"2024-02-30"` | "Invalid date" |
| Before min | `"2020-01-01"` (if min=2024) | "Date too early" |
| After max | `"2030-01-01"` (if max=2025) | "Date too late" |
| Valid | `"2024-06-15"` | (success) |

### HTML5 Attributes

```html
<input type="date"
       required
       min="2024-01-01"
       max="2025-12-31" />
```

### Test Sequence

```typescript
const dateTests = [
  { value: "", expected: "required" },
  { value: "invalid-date", expected: "format" },
  { value: "2024-02-30", expected: "invalid" },
  { value: "2020-01-01", expected: "too early" },
  { value: "2030-01-01", expected: "too late" },
  { value: "2024-06-15", expected: "valid" }
];
```

## URL Field Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Empty required | `""` | "URL is required" |
| No protocol | `"example.com"` | "Invalid URL format" |
| Invalid protocol | `"htp://example.com"` | "Invalid URL format" |
| No domain | `"https://"` | "Invalid URL format" |
| Spaces | `"https://exam ple.com"` | "Invalid URL format" |
| Valid HTTP | `"http://example.com"` | (success) |
| Valid HTTPS | `"https://example.com"` | (success) |

### HTML5 Pattern

```html
<input type="url" required />
```

### Test Sequence

```typescript
const urlTests = [
  { value: "", expected: "required" },
  { value: "example.com", expected: "no protocol" },
  { value: "htp://example.com", expected: "invalid protocol" },
  { value: "https://", expected: "no domain" },
  { value: "https://exam ple.com", expected: "spaces" },
  { value: "https://example.com", expected: "valid" }
];
```

## Select/Dropdown Validation

### Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| No selection | Default placeholder | "Please select an option" |
| Invalid option | Not in list | (prevented by UI) |
| Valid selection | "Option 1" | (success) |

### HTML5 Pattern

```html
<select required>
  <option value="">Select...</option>
  <option value="opt1">Option 1</option>
  <option value="opt2">Option 2</option>
</select>
```

### Test Sequence

```typescript
// Test 1: No selection (leave default)
await browser_fill_form({
  fields: [
    { name: "Dropdown", type: "combobox", ref: "ref_1", value: "" }
  ]
});

// Test 2: Valid selection
await browser_fill_form({
  fields: [
    { name: "Dropdown", type: "combobox", ref: "ref_1", value: "Option 1" }
  ]
});
```

## Checkbox/Radio Validation

### Checkbox Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| Required unchecked | `false` | "You must accept terms" |
| Required checked | `true` | (success) |

### Radio Test Cases

| Test Type | Test Value | Expected Error |
|-----------|------------|----------------|
| No selection | None selected | "Please select an option" |
| Valid selection | One selected | (success) |

### Test Sequence

```typescript
// Checkbox
await browser_fill_form({
  fields: [
    { name: "Terms checkbox", type: "checkbox", ref: "ref_1", value: false }
  ]
});
// Submit and verify error

await browser_fill_form({
  fields: [
    { name: "Terms checkbox", type: "checkbox", ref: "ref_1", value: true }
  ]
});
// Submit and verify success
```

## Cross-Field Validation

### Password Confirmation

**Test Cases:**
- Confirmation empty while password filled
- Confirmation doesn't match password
- Both match (success)

```typescript
// Test mismatch
await browser_fill_form({
  fields: [
    { name: "Password", type: "textbox", ref: "ref_1", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_2", value: "DifferentPass123!" }
  ]
});
// Expected: "Passwords do not match"

// Test match
await browser_fill_form({
  fields: [
    { name: "Password", type: "textbox", ref: "ref_1", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_2", value: "ValidPass123!" }
  ]
});
// Expected: Success
```

### Date Range Validation

**Test Cases:**
- End date before start date
- Start date after end date
- Valid range

```typescript
// Test invalid range
await browser_fill_form({
  fields: [
    { name: "Start Date", type: "textbox", ref: "ref_1", value: "2024-06-15" },
    { name: "End Date", type: "textbox", ref: "ref_2", value: "2024-06-10" }
  ]
});
// Expected: "End date must be after start date"
```

## Validation Message Extraction

### From Browser Snapshot

Validation messages typically appear as:

**Inline field errors:**
```
textbox "Email" (ref_1)
  error: "Please enter a valid email address"
```

**Alert/banner errors:**
```
alert "Error"
  text: "Please fix the following errors:"
  text: "- Email is required"
  text: "- Password must be at least 8 characters"
```

**Aria attributes:**
```
textbox "Email" (ref_1)
  aria-invalid: "true"
  aria-describedby: "email-error"

text "email-error" (ref_2)
  text: "Please enter a valid email address"
```

### Extraction Strategy

1. Look for elements with `aria-invalid="true"`
2. Find associated error messages via `aria-describedby`
3. Check for alert/banner elements with error class
4. Search for text containing validation keywords:
   - "required", "invalid", "must", "minimum", "maximum"
   - "Please enter", "Please select", "Please provide"
   - "Cannot be", "Should be", "Must be"

### Example Parser

```python
import re

def extract_validation_errors(snapshot_content):
    """Extract validation error messages from browser snapshot."""
    errors = []

    # Pattern 1: error: "message"
    pattern1 = r'error:\s*"([^"]+)"'
    errors.extend(re.findall(pattern1, snapshot_content))

    # Pattern 2: aria-describedby with error text
    # More complex parsing needed

    # Pattern 3: alert with error list
    alert_match = re.search(r'alert.*?text:\s*"([^"]+)"', snapshot_content, re.DOTALL)
    if alert_match:
        errors.append(alert_match.group(1))

    return errors
```

## Validation Report Checklist

For each field tested, document:

- [ ] Field name and type
- [ ] Required status
- [ ] Constraints (min/max, pattern, etc.)
- [ ] Test cases executed
- [ ] Validation messages captured
- [ ] Screenshots taken
- [ ] Missing validations identified
- [ ] Accessibility attributes checked (aria-invalid, aria-describedby)
- [ ] Valid submission tested
- [ ] Success confirmation captured

## Common Validation Frameworks

### HTML5 Built-in
- `required` attribute
- `type` attribute (email, url, number, date)
- `pattern` attribute (regex)
- `min`, `max`, `minlength`, `maxlength`
- `:invalid` CSS pseudo-class

### JavaScript Libraries
- **React Hook Form** - `errors.fieldname.message`
- **Formik** - `errors.fieldname`, `touched.fieldname`
- **Yup/Joi** - Schema validation with custom messages
- **Vuelidate** - Vue.js validation
- **Angular Forms** - Template-driven and reactive forms

### Error Display Patterns
- Inline below field
- Tooltip on hover/focus
- Alert banner at top
- Modal dialog
- Summary list
- Field border color change
