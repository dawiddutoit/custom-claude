# Form Validation Testing Examples

Complete examples demonstrating validation testing for common form types.

## Table of Contents

1. [Login Form Validation](#login-form-validation)
2. [Signup/Registration Form](#signupregistration-form)
3. [Contact Form](#contact-form)
4. [Checkout Form](#checkout-form)
5. [Profile Update Form](#profile-update-form)
6. [Search Form](#search-form)
7. [Multi-Step Form](#multi-step-form)
8. [Complex Business Form](#complex-business-form)

## Login Form Validation

### Form Structure
- Email field (required, email format)
- Password field (required, min 8 chars)
- Remember me checkbox (optional)
- Submit button

### Complete Test Sequence

```typescript
// Step 1: Navigate and capture initial state
await browser_navigate({ url: "https://example.com/login" });
await browser_wait_for({ time: 2 });
await browser_snapshot({ filename: "login-form-initial.md" });

// Step 2: Test empty email
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" }
  ]
});
await browser_click({ element: "Login button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "login-validation-empty-email.png" });
await browser_snapshot({ filename: "login-validation-empty-email.md" });

// Step 3: Test invalid email format
await browser_navigate({ url: "https://example.com/login" }); // Reset form
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "invalid-email" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" }
  ]
});
await browser_click({ element: "Login button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "login-validation-invalid-email.png" });
await browser_snapshot({ filename: "login-validation-invalid-email.md" });

// Step 4: Test empty password
await browser_navigate({ url: "https://example.com/login" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "" }
  ]
});
await browser_click({ element: "Login button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "login-validation-empty-password.png" });
await browser_snapshot({ filename: "login-validation-empty-password.md" });

// Step 5: Test password too short
await browser_navigate({ url: "https://example.com/login" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "short" }
  ]
});
await browser_click({ element: "Login button", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "login-validation-password-too-short.png" });
await browser_snapshot({ filename: "login-validation-password-too-short.md" });

// Step 6: Test valid submission
await browser_navigate({ url: "https://example.com/login" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" }
  ]
});
await browser_click({ element: "Login button", ref: "ref_submit" });
await browser_wait_for({ time: 2 });
await browser_take_screenshot({ filename: "login-validation-success.png" });
await browser_snapshot({ filename: "login-validation-success.md" });
```

### Expected Results

**Test 1: Empty email**
- Error message: "Email is required" or "Please enter your email"
- Email field highlighted/marked invalid
- Form not submitted

**Test 2: Invalid email format**
- Error message: "Please enter a valid email address"
- Email field highlighted
- Form not submitted

**Test 3: Empty password**
- Error message: "Password is required"
- Password field highlighted
- Form not submitted

**Test 4: Password too short**
- Error message: "Password must be at least 8 characters"
- Password field highlighted
- Form not submitted

**Test 5: Valid submission**
- No error messages
- Redirect to dashboard or success message
- User logged in

### Validation Report

```markdown
# Login Form Validation Report

**Form URL:** https://example.com/login
**Test Date:** 2025-12-20
**Fields Tested:** 2 (Email, Password)

## Summary

- ✅ Total validations found: 4
- ✅ Missing validations: 0
- ✅ Valid submission: Success

## Email Field

| Test Case | Input | Expected Error | Actual Error | Status |
|-----------|-------|----------------|--------------|--------|
| Empty value | `""` | "Email is required" | "Email is required" | ✅ Pass |
| Invalid format | `"invalid-email"` | "Invalid email" | "Please enter a valid email address" | ✅ Pass |
| Valid | `"test@example.com"` | None | None | ✅ Pass |

**Screenshots:**
- [Empty email error](login-validation-empty-email.png)
- [Invalid email error](login-validation-invalid-email.png)

## Password Field

| Test Case | Input | Expected Error | Actual Error | Status |
|-----------|-------|----------------|--------------|--------|
| Empty value | `""` | "Password is required" | "Password is required" | ✅ Pass |
| Too short | `"short"` | "Min 8 characters" | "Password must be at least 8 characters" | ✅ Pass |
| Valid | `"ValidPass123!"` | None | None | ✅ Pass |

**Screenshots:**
- [Empty password error](login-validation-empty-password.png)
- [Short password error](login-validation-password-too-short.png)

## Valid Submission

- ✅ Form submitted successfully
- ✅ Redirected to dashboard
- Screenshot: [Success state](login-validation-success.png)

## Recommendations

None - all validations working as expected.
```

## Signup/Registration Form

### Form Structure
- Email field (required, email format)
- Password field (required, min 8 chars, complexity rules)
- Confirm password field (required, must match password)
- Username field (required, alphanumeric only)
- Age field (optional, number, min 13)
- Terms checkbox (required)

### Test Sequence Highlights

```typescript
// Test password complexity
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "lowercase123" }, // No uppercase
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "lowercase123" },
    { name: "Username", type: "textbox", ref: "ref_username", value: "testuser" }
  ]
});
await browser_click({ element: "Sign Up", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "signup-password-no-uppercase.png" });

// Test password mismatch
await browser_navigate({ url: "https://example.com/signup" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "DifferentPass123!" },
    { name: "Username", type: "textbox", ref: "ref_username", value: "testuser" }
  ]
});
await browser_click({ element: "Sign Up", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "signup-password-mismatch.png" });

// Test invalid username (special chars)
await browser_navigate({ url: "https://example.com/signup" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "ValidPass123!" },
    { name: "Username", type: "textbox", ref: "ref_username", value: "test@user!" }
  ]
});
await browser_click({ element: "Sign Up", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "signup-invalid-username.png" });

// Test age below minimum
await browser_navigate({ url: "https://example.com/signup" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "ValidPass123!" },
    { name: "Username", type: "textbox", ref: "ref_username", value: "testuser" },
    { name: "Age", type: "textbox", ref: "ref_age", value: "10" }
  ]
});
await browser_click({ element: "Sign Up", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "signup-age-too-young.png" });

// Test terms not accepted
await browser_navigate({ url: "https://example.com/signup" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "ValidPass123!" },
    { name: "Username", type: "textbox", ref: "ref_username", value: "testuser" },
    { name: "Terms", type: "checkbox", ref: "ref_terms", value: false }
  ]
});
await browser_click({ element: "Sign Up", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "signup-terms-not-accepted.png" });

// Test valid submission
await browser_navigate({ url: "https://example.com/signup" });
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Password", type: "textbox", ref: "ref_password", value: "ValidPass123!" },
    { name: "Confirm Password", type: "textbox", ref: "ref_confirm", value: "ValidPass123!" },
    { name: "Username", type: "textbox", ref: "ref_username", value: "testuser" },
    { name: "Age", type: "textbox", ref: "ref_age", value: "25" },
    { name: "Terms", type: "checkbox", ref: "ref_terms", value: true }
  ]
});
await browser_click({ element: "Sign Up", ref: "ref_submit" });
await browser_wait_for({ time: 2 });
await browser_take_screenshot({ filename: "signup-success.png" });
```

### Expected Validation Messages

- Password no uppercase: "Password must contain at least one uppercase letter"
- Password mismatch: "Passwords do not match"
- Invalid username: "Username can only contain letters and numbers"
- Age too young: "You must be at least 13 years old"
- Terms not accepted: "You must accept the terms and conditions"

## Contact Form

### Form Structure
- Name field (required, min 2 chars)
- Email field (required, email format)
- Phone field (optional, phone format)
- Subject dropdown (required)
- Message textarea (required, min 10 chars, max 500 chars)

### Key Test Cases

```typescript
// Test message too short
await browser_fill_form({
  fields: [
    { name: "Name", type: "textbox", ref: "ref_name", value: "John Doe" },
    { name: "Email", type: "textbox", ref: "ref_email", value: "john@example.com" },
    { name: "Subject", type: "combobox", ref: "ref_subject", value: "General Inquiry" },
    { name: "Message", type: "textbox", ref: "ref_message", value: "Too short" }
  ]
});
await browser_click({ element: "Send", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "contact-message-too-short.png" });

// Test message too long
const longMessage = "a".repeat(501);
await browser_navigate({ url: "https://example.com/contact" });
await browser_fill_form({
  fields: [
    { name: "Name", type: "textbox", ref: "ref_name", value: "John Doe" },
    { name: "Email", type: "textbox", ref: "ref_email", value: "john@example.com" },
    { name: "Subject", type: "combobox", ref: "ref_subject", value: "General Inquiry" },
    { name: "Message", type: "textbox", ref: "ref_message", value: longMessage }
  ]
});
await browser_click({ element: "Send", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "contact-message-too-long.png" });

// Test invalid phone format (if provided)
await browser_navigate({ url: "https://example.com/contact" });
await browser_fill_form({
  fields: [
    { name: "Name", type: "textbox", ref: "ref_name", value: "John Doe" },
    { name: "Email", type: "textbox", ref: "ref_email", value: "john@example.com" },
    { name: "Phone", type: "textbox", ref: "ref_phone", value: "123-abc" },
    { name: "Subject", type: "combobox", ref: "ref_subject", value: "General Inquiry" },
    { name: "Message", type: "textbox", ref: "ref_message", value: "This is a valid message with enough characters." }
  ]
});
await browser_click({ element: "Send", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "contact-invalid-phone.png" });

// Test no subject selected
await browser_navigate({ url: "https://example.com/contact" });
await browser_fill_form({
  fields: [
    { name: "Name", type: "textbox", ref: "ref_name", value: "John Doe" },
    { name: "Email", type: "textbox", ref: "ref_email", value: "john@example.com" },
    { name: "Subject", type: "combobox", ref: "ref_subject", value: "" },
    { name: "Message", type: "textbox", ref: "ref_message", value: "This is a valid message." }
  ]
});
await browser_click({ element: "Send", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "contact-no-subject.png" });
```

## Checkout Form

### Form Structure
- Email (required, email format)
- Shipping Address:
  - Full Name (required)
  - Street Address (required)
  - City (required)
  - State/Province dropdown (required)
  - ZIP/Postal Code (required, format validation)
  - Country dropdown (required)
- Phone (required, phone format)
- Card Number (required, credit card format)
- Expiry Date (required, MM/YY format, future date)
- CVV (required, 3-4 digits)

### Complex Validation Tests

```typescript
// Test invalid ZIP code format
await browser_fill_form({
  fields: [
    { name: "Email", type: "textbox", ref: "ref_email", value: "test@example.com" },
    { name: "Full Name", type: "textbox", ref: "ref_name", value: "John Doe" },
    { name: "Street Address", type: "textbox", ref: "ref_address", value: "123 Main St" },
    { name: "City", type: "textbox", ref: "ref_city", value: "New York" },
    { name: "State", type: "combobox", ref: "ref_state", value: "NY" },
    { name: "ZIP", type: "textbox", ref: "ref_zip", value: "123" }, // Too short
    { name: "Country", type: "combobox", ref: "ref_country", value: "US" }
  ]
});
await browser_click({ element: "Continue", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "checkout-invalid-zip.png" });

// Test expired card
await browser_navigate({ url: "https://example.com/checkout" });
await browser_fill_form({
  fields: [
    // ... (all shipping fields valid)
    { name: "Card Number", type: "textbox", ref: "ref_card", value: "4111111111111111" },
    { name: "Expiry", type: "textbox", ref: "ref_expiry", value: "01/20" }, // Expired
    { name: "CVV", type: "textbox", ref: "ref_cvv", value: "123" }
  ]
});
await browser_click({ element: "Place Order", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "checkout-expired-card.png" });

// Test invalid CVV
await browser_navigate({ url: "https://example.com/checkout" });
await browser_fill_form({
  fields: [
    // ... (all other fields valid)
    { name: "Card Number", type: "textbox", ref: "ref_card", value: "4111111111111111" },
    { name: "Expiry", type: "textbox", ref: "ref_expiry", value: "12/25" },
    { name: "CVV", type: "textbox", ref: "ref_cvv", value: "12" } // Too short
  ]
});
await browser_click({ element: "Place Order", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "checkout-invalid-cvv.png" });
```

## Profile Update Form

### Form Structure
- Current Password (required to update)
- New Password (optional, but if provided, must meet complexity)
- Confirm New Password (required if new password provided)
- Display Name (required, min 2 chars)
- Bio (optional, max 200 chars)
- Website URL (optional, URL format)

### Conditional Validation Tests

```typescript
// Test new password without current password
await browser_fill_form({
  fields: [
    { name: "Current Password", type: "textbox", ref: "ref_current", value: "" },
    { name: "New Password", type: "textbox", ref: "ref_new", value: "NewPass123!" },
    { name: "Confirm New Password", type: "textbox", ref: "ref_confirm", value: "NewPass123!" }
  ]
});
await browser_click({ element: "Update Profile", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "profile-new-password-no-current.png" });

// Test bio exceeds max length
const longBio = "a".repeat(201);
await browser_navigate({ url: "https://example.com/profile" });
await browser_fill_form({
  fields: [
    { name: "Display Name", type: "textbox", ref: "ref_name", value: "John Doe" },
    { name: "Bio", type: "textbox", ref: "ref_bio", value: longBio }
  ]
});
await browser_click({ element: "Update Profile", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "profile-bio-too-long.png" });

// Test invalid website URL
await browser_navigate({ url: "https://example.com/profile" });
await browser_fill_form({
  fields: [
    { name: "Display Name", type: "textbox", ref: "ref_name", value: "John Doe" },
    { name: "Website", type: "textbox", ref: "ref_website", value: "not-a-url" }
  ]
});
await browser_click({ element: "Update Profile", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "profile-invalid-url.png" });
```

## Search Form

### Form Structure
- Search query (required, min 3 chars)
- Category filter (optional dropdown)
- Date range (optional, start/end dates)

### Edge Cases

```typescript
// Test query too short
await browser_fill_form({
  fields: [
    { name: "Search", type: "textbox", ref: "ref_search", value: "ab" }
  ]
});
await browser_click({ element: "Search", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "search-query-too-short.png" });

// Test invalid date range (end before start)
await browser_navigate({ url: "https://example.com/search" });
await browser_fill_form({
  fields: [
    { name: "Search", type: "textbox", ref: "ref_search", value: "keyword" },
    { name: "Start Date", type: "textbox", ref: "ref_start", value: "2024-06-15" },
    { name: "End Date", type: "textbox", ref: "ref_end", value: "2024-06-10" }
  ]
});
await browser_click({ element: "Search", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "search-invalid-date-range.png" });
```

## Multi-Step Form

### Form Structure (3 steps)

**Step 1: Personal Info**
- First Name (required)
- Last Name (required)
- Email (required, email format)

**Step 2: Address**
- Street (required)
- City (required)
- ZIP (required, format)

**Step 3: Payment**
- Card details (required, format)

### Testing Strategy

Test each step independently, then test navigation:

```typescript
// Step 1: Test and proceed
await browser_fill_form({
  fields: [
    { name: "First Name", type: "textbox", ref: "ref_first", value: "" }
  ]
});
await browser_click({ element: "Next", ref: "ref_next" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "multistep-step1-empty-name.png" });

// Fill valid and proceed
await browser_fill_form({
  fields: [
    { name: "First Name", type: "textbox", ref: "ref_first", value: "John" },
    { name: "Last Name", type: "textbox", ref: "ref_last", value: "Doe" },
    { name: "Email", type: "textbox", ref: "ref_email", value: "john@example.com" }
  ]
});
await browser_click({ element: "Next", ref: "ref_next" });
await browser_wait_for({ time: 1 });

// Step 2: Test ZIP validation
await browser_fill_form({
  fields: [
    { name: "Street", type: "textbox", ref: "ref_street", value: "123 Main St" },
    { name: "City", type: "textbox", ref: "ref_city", value: "New York" },
    { name: "ZIP", type: "textbox", ref: "ref_zip", value: "123" }
  ]
});
await browser_click({ element: "Next", ref: "ref_next" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "multistep-step2-invalid-zip.png" });
```

## Complex Business Form

### Scenario: Event Registration
- Event Type (required dropdown)
- Number of Attendees (required, min 1, max 100)
- Attendee details (dynamic, one set per attendee):
  - Full Name (required)
  - Email (required, unique)
  - Dietary restrictions (optional)
- Billing same as first attendee (checkbox)
- If not checked:
  - Billing Name (required)
  - Billing Email (required)

### Dynamic Validation

```typescript
// Test number of attendees validation
await browser_fill_form({
  fields: [
    { name: "Event Type", type: "combobox", ref: "ref_event", value: "Conference" },
    { name: "Number of Attendees", type: "textbox", ref: "ref_count", value: "0" }
  ]
});
await browser_click({ element: "Continue", ref: "ref_next" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "event-zero-attendees.png" });

// Test duplicate email addresses
await browser_fill_form({
  fields: [
    { name: "Attendee 1 Email", type: "textbox", ref: "ref_att1_email", value: "john@example.com" },
    { name: "Attendee 2 Email", type: "textbox", ref: "ref_att2_email", value: "john@example.com" }
  ]
});
await browser_click({ element: "Submit", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "event-duplicate-emails.png" });

// Test conditional billing validation
await browser_fill_form({
  fields: [
    { name: "Billing same as first attendee", type: "checkbox", ref: "ref_same", value: false },
    { name: "Billing Name", type: "textbox", ref: "ref_billing_name", value: "" }
  ]
});
await browser_click({ element: "Submit", ref: "ref_submit" });
await browser_wait_for({ time: 1 });
await browser_take_screenshot({ filename: "event-missing-billing-name.png" });
```

## Testing Checklist

For each example, verify:

- [ ] All required fields tested with empty values
- [ ] All format validations tested (email, phone, URL, etc.)
- [ ] All boundary conditions tested (min/max length/value)
- [ ] All cross-field validations tested (password match, date ranges)
- [ ] All conditional validations tested (show/hide based on other fields)
- [ ] Valid submission tested and confirmed
- [ ] All error messages captured and documented
- [ ] All screenshots saved with descriptive names
- [ ] Validation report generated with all findings
