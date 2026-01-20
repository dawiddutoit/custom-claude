# Detailed Validation Testing Workflow

Complete step-by-step workflow for form validation testing with code examples.

## Navigation and Initial State

```typescript
// Navigate to form
await browser_navigate({ url: "https://example.com/form" });

// Wait for form to load
await browser_wait_for({ time: 2 });

// Capture initial snapshot
await browser_snapshot({ filename: "form-initial-state.md" });
```

**What to extract from initial snapshot:**
- Field names and types (text, email, password, number, etc.)
- Required vs optional fields
- Placeholder text or hints
- Existing validation attributes (pattern, min, max, etc.)

## Empty Field Validation Testing

For each required field, submit with empty value:

```typescript
// Example: Test empty email field
await browser_fill_form({
  fields: [
    { name: "Email field", type: "textbox", ref: "ref_1", value: "" },
    { name: "Password field", type: "textbox", ref: "ref_2", value: "ValidPassword123!" }
  ]
});

await browser_click({ element: "Submit button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });

// Capture error state
await browser_take_screenshot({
  filename: "validation-empty-email.png"
});

// Capture updated snapshot with error messages
await browser_snapshot({ filename: "validation-empty-email.md" });
```

**After each test:**
1. Take screenshot showing error state
2. Capture snapshot with error messages
3. Parse validation message from snapshot
4. Reset form for next test (navigate back or clear fields)

## Invalid Format Validation Testing

Test common invalid patterns for each field type:

### Email Field Tests

```typescript
const emailTests = [
  "invalid-email",      // No @ symbol
  "test@",             // No domain
  "@example.com",      // No local part
  "test @example.com", // Spaces
  "test@@example.com", // Multiple @
  "test@example",      // No TLD
];

for (const invalidEmail of emailTests) {
  await browser_navigate({ url: formUrl }); // Reset form

  await browser_fill_form({
    fields: [
      { name: "Email field", type: "textbox", ref: "ref_1", value: invalidEmail },
      { name: "Password field", type: "textbox", ref: "ref_2", value: "ValidPassword123!" }
    ]
  });

  await browser_click({ element: "Submit button", ref: "ref_submit" });
  await browser_wait_for({ time: 1 });

  await browser_take_screenshot({
    filename: `validation-email-${invalidEmail.replace(/[^a-z0-9]/gi, '-')}.png`
  });
  await browser_snapshot({ filename: `validation-email-${invalidEmail}.md` });
}
```

### Phone Field Tests

```typescript
const phoneTests = [
  "abc123",        // Letters
  "123",          // Too short
  "12-34-56",     // Invalid format
];

for (const invalidPhone of phoneTests) {
  // Same pattern as email tests
}
```

### Password Field Tests

```typescript
const passwordTests = [
  "short",              // Too short
  "alllowercase123",    // No uppercase
  "ALLUPPERCASE123",    // No lowercase
  "NoNumbers",          // No numbers
  "NoSpecial123",       // No special chars
];

for (const invalidPassword of passwordTests) {
  await browser_navigate({ url: formUrl });

  await browser_fill_form({
    fields: [
      { name: "Email field", type: "textbox", ref: "ref_1", value: "test@example.com" },
      { name: "Password field", type: "textbox", ref: "ref_2", value: invalidPassword }
    ]
  });

  await browser_click({ element: "Submit button", ref: "ref_submit" });
  await browser_wait_for({ time: 1 });

  await browser_take_screenshot({
    filename: `validation-password-${invalidPassword}.png`
  });
}
```

## Boundary Value Testing

For fields with min/max constraints:

```typescript
// Test password too short (if min length = 8)
await browser_fill_form({
  fields: [
    { name: "Email field", type: "textbox", ref: "ref_1", value: "test@example.com" },
    { name: "Password field", type: "textbox", ref: "ref_2", value: "short" }
  ]
});

await browser_click({ element: "Submit button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "validation-password-too-short.png" });

// Test number below minimum
await browser_fill_form({
  fields: [
    { name: "Age field", type: "textbox", ref: "ref_age", value: "5" } // If min = 10
  ]
});

// Test number above maximum
await browser_fill_form({
  fields: [
    { name: "Quantity field", type: "textbox", ref: "ref_qty", value: "200" } // If max = 100
  ]
});

// Test text too long
const longText = "a".repeat(101); // If max = 100
await browser_fill_form({
  fields: [
    { name: "Bio field", type: "textbox", ref: "ref_bio", value: longText }
  ]
});
```

## Cross-Field Validation Testing

### Password Confirmation

```typescript
// Test password mismatch
await browser_fill_form({
  fields: [
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "DifferentPass123!" }
  ]
});

await browser_click({ element: "Submit button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "validation-password-mismatch.png" });

// Test password match (should succeed)
await browser_navigate({ url: formUrl });
await browser_fill_form({
  fields: [
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "ValidPass123!" }
  ]
});
```

### Date Range Validation

```typescript
// Test end date before start date
await browser_fill_form({
  fields: [
    { name: "Start Date", type: "textbox", ref: "ref_start", value: "2024-06-15" },
    { name: "End Date", type: "textbox", ref: "ref_end", value: "2024-06-10" }
  ]
});

await browser_click({ element: "Submit button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "validation-invalid-date-range.png" });
```

## Valid Submission Testing

Submit form with all valid data to verify success path:

```typescript
await browser_navigate({ url: formUrl }); // Fresh start

await browser_fill_form({
  fields: [
    { name: "Email field", type: "textbox", ref: "ref_1", value: "test@example.com" },
    { name: "Password field", type: "textbox", ref: "ref_2", value: "ValidPassword123!" },
    { name: "Name field", type: "textbox", ref: "ref_3", value: "John Doe" },
    { name: "Age field", type: "textbox", ref: "ref_4", value: "25" },
    { name: "Terms checkbox", type: "checkbox", ref: "ref_5", value: true }
  ]
});

await browser_click({ element: "Submit button", ref: "ref_submit" });
await browser_wait_for({ time: 2 }); // Wait longer for submission

// Check for success indicators
await browser_snapshot({ filename: "validation-success.md" });
await browser_take_screenshot({ filename: "validation-success.png" });
```

**Success indicators to look for in snapshot:**
- Redirect to different URL (e.g., dashboard, confirmation page)
- Success message displayed
- Form cleared or hidden
- No validation errors present

## Validation Message Extraction

Parse snapshots to extract validation messages:

### Using parse_validation_errors.py script

```bash
# Extract all errors from snapshot
python scripts/parse_validation_errors.py validation-empty-email.md

# Get JSON output
python scripts/parse_validation_errors.py validation-empty-email.md --json

# Filter by specific field
python scripts/parse_validation_errors.py validation-empty-email.md --field "Email"
```

### Manual extraction patterns

**Pattern 1: Inline error attribute**
```
textbox "Email" (ref_1)
  error: "Please enter a valid email address"
```

**Pattern 2: ARIA attributes**
```
textbox "Email" (ref_1)
  aria-invalid: "true"
  aria-describedby: "email-error"

text "email-error" (ref_2)
  text: "Please enter a valid email address"
```

**Pattern 3: Alert banner**
```
alert "Error"
  text: "Please fix the following errors:"
  text: "- Email is required"
  text: "- Password must be at least 8 characters"
```

## Report Generation

Compile all findings into structured report using template:

```bash
# Use validation report template
cp templates/validation-report-template.md .claude/artifacts/$(date +%Y-%m-%d)/validation-report-login-form.md
```

**Fill in report sections:**

1. **Executive Summary** - Total fields, validations found, status
2. **Field-by-Field Results** - For each field: tests run, errors found, screenshots
3. **Cross-Field Validation** - Password match, date ranges, etc.
4. **Valid Submission** - Success state verification
5. **Missing Validations** - Fields without proper validation
6. **Recommendations** - Prioritized list of improvements

## Testing Patterns by Form Type

### Simple Form (Login)
1. Test each field empty
2. Test invalid formats (email)
3. Test valid submission
4. 5-10 total tests

### Medium Form (Contact)
1. Test required fields empty
2. Test format validations (email, phone)
3. Test length constraints (min/max)
4. Test dropdown/select required
5. Test valid submission
6. 15-20 total tests

### Complex Form (Registration)
1. Test all required fields empty
2. Test all format validations
3. Test password complexity rules
4. Test password confirmation match
5. Test username uniqueness/format
6. Test age/number constraints
7. Test terms acceptance
8. Test valid submission
9. 25-35 total tests

### Multi-Step Form
1. Test each step independently
2. Test navigation between steps
3. Test data persistence across steps
4. Test final submission
5. 30-50+ total tests

## Optimization Strategies

### Reduce Test Time

1. **Batch similar tests** - Test all email formats in one browser session
2. **Skip redundant resets** - Only navigate when necessary
3. **Parallelize when possible** - Test independent fields in separate sessions
4. **Use snapshots strategically** - Only capture when error messages change

### Handle Dynamic Forms

1. **Wait for elements to appear** - Use `browser_wait_for` with text matching
2. **Handle conditional fields** - Test show/hide behavior
3. **Test AJAX validation** - Wait for async validation to complete
4. **Test real-time validation** - Capture on blur events

### Handle Complex Validation

1. **Test in logical order** - Basic to complex validations
2. **Document dependencies** - Note which validations depend on others
3. **Test edge cases** - Boundary values, special characters
4. **Test localization** - Multiple language error messages if applicable
