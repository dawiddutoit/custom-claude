# Playwright Console Monitor Examples

This file contains real-world examples of console monitoring during browser automation workflows.

## Table of Contents

1. E-Commerce Checkout Monitoring
2. Form Submission Validation
3. SPA Navigation Tracking
4. Authentication Flow Monitoring
5. Third-Party Integration Validation
6. Multi-Step Wizard Monitoring
7. Real-Time Data Updates

---

## 1. E-Commerce Checkout Monitoring

**Scenario:** Monitor console errors during complete checkout process

**Workflow:**
```
1. Navigate to product page
2. Add item to cart
3. Proceed to checkout
4. Enter shipping information
5. Apply discount code
6. Enter payment details
7. Submit order
```

**Console Checkpoints:**
- After adding to cart (check for cart calculation errors)
- After proceeding to checkout (check for session/auth errors)
- After applying discount code (check for pricing errors)
- After payment submission (CRITICAL - check for transaction errors)

**Example Error Detected:**
```
Critical Error at Step 5 (Apply Discount Code):
[14:32:15] Uncaught TypeError: Cannot read property 'discountAmount' of null
  at applyDiscount (checkout.js:245)
  at HTMLButtonElement.onclick (checkout.html:89)

Context: User clicked "Apply" button for discount code "SAVE20"
Screenshot: checkout-discount-error.png
Page URL: https://example.com/checkout/payment

Debugging Recommendation:
- Check if discount validation API returned null instead of discount object
- Verify discount code "SAVE20" exists and is active
- Review error handling in applyDiscount function
```

---

## 2. Form Submission Validation

**Scenario:** Monitor form validation and submission for contact form

**Workflow:**
```
1. Navigate to contact page
2. Fill in name, email, message
3. Click submit
4. Wait for success message
```

**Console Checkpoints:**
- After form load (check for validation library errors)
- After clicking submit (check for validation and AJAX errors)
- After success message appears (verify no delayed errors)

**Example Warning Detected:**
```
Warning at Step 3 (Submit Form):
[10:15:42] [Deprecation] Synchronous XMLHttpRequest on the main thread is deprecated
  at sendFormData (contact.js:156)

Context: Form submitted via synchronous XHR instead of fetch/async
Screenshot: contact-form-warning.png

Debugging Recommendation:
- Modernize form submission to use fetch() API
- This will eventually break in newer browsers
- Consider progressive enhancement pattern
```

---

## 3. SPA Navigation Tracking

**Scenario:** Monitor console during single-page application navigation

**Workflow:**
```
1. Navigate to dashboard
2. Click "Projects" tab
3. Click "Team Members" tab
4. Click "Settings" tab
5. Click back to "Dashboard"
```

**Console Checkpoints:**
- After each tab change (check for routing errors)
- Before navigation (clear previous tab's messages)
- After navigation complete (check for data loading errors)

**Example Error Detected:**
```
Critical Error at Step 4 (Settings Tab):
[16:22:33] Error: Failed to fetch user preferences
  GET https://api.example.com/v1/preferences 401 Unauthorized
  at fetchPreferences (settings.js:78)

Context: Navigation to Settings tab triggered API call with expired token
Screenshot: settings-error.png
Network: GET /v1/preferences returned 401

Debugging Recommendation:
- Token refresh logic may not be working during SPA navigation
- Check if auth interceptor is properly configured for all routes
- Consider implementing token validation before protected route navigation
```

---

## 4. Authentication Flow Monitoring

**Scenario:** Monitor OAuth/SSO login flow

**Workflow:**
```
1. Navigate to login page
2. Click "Sign in with Google"
3. Redirected to Google OAuth
4. Authorize application
5. Redirected back to application
6. Dashboard loads
```

**Console Checkpoints:**
- After clicking "Sign in with Google" (check for popup/redirect errors)
- After OAuth redirect back (CRITICAL - check for token exchange errors)
- After dashboard loads (verify authentication state)

**Example Error Detected:**
```
Critical Error at Step 5 (OAuth Callback):
[11:45:18] Uncaught ReferenceError: oauth is not defined
  at handleOAuthCallback (auth.js:203)

[11:45:18] Error: OAuth state mismatch
  Expected: a7f3k2m9...
  Received: undefined

Context: OAuth redirect callback failed due to missing OAuth library
Screenshot: oauth-error.png
URL: https://example.com/auth/callback?code=xyz&state=undefined

Debugging Recommendation:
- OAuth library script may not be loading before callback executes
- Check script loading order in auth flow
- Verify state parameter is properly stored in sessionStorage
- Consider adding loading state during OAuth redirect
```

---

## 5. Third-Party Integration Validation

**Scenario:** Monitor integration with analytics, chat widget, payment processor

**Workflow:**
```
1. Navigate to page with integrations
2. Wait for all third-party scripts to load
3. Trigger analytics event
4. Open chat widget
5. Attempt test payment
```

**Console Checkpoints:**
- After page load (check for script loading errors)
- After each third-party interaction (check for integration errors)
- After 5 seconds (check for delayed initialization errors)

**Example Errors Detected:**
```
Warning at Step 1 (Page Load):
[09:30:12] [Intercom] No app_id found
  at intercom.js:45

Critical Error at Step 3 (Analytics Event):
[09:30:25] ga is not defined
  at trackEvent (analytics.js:12)

Warning at Step 5 (Payment):
[09:31:15] Stripe: Card element not mounted
  at stripe-v3.js:892

Context: Multiple third-party integration failures
Screenshots: integration-errors-*.png

Debugging Recommendations:
- Intercom widget missing app_id configuration
- Google Analytics script blocked or failed to load (check Content Security Policy)
- Stripe Elements not properly initialized before payment attempt
- Consider adding integration health checks on page load
- Implement fallback UI for missing third-party services
```

---

## 6. Multi-Step Wizard Monitoring

**Scenario:** Monitor insurance quote wizard (5 steps)

**Workflow:**
```
Step 1: Personal Information
Step 2: Coverage Details
Step 3: Beneficiaries
Step 4: Medical Questions
Step 5: Review and Submit
```

**Console Checkpoints:**
- After completing each step (check for validation errors)
- Before proceeding to next step (verify data persistence)
- After final submission (CRITICAL - check for submission errors)

**Example Pattern:**
```javascript
// Checkpoint after each step
for (step = 1; step <= 5; step++) {
  // Fill in step fields
  // Click "Continue"
  // Wait for next step to appear

  // Check console
  const errors = await browser_console_messages({ level: "error" });
  if (errors.length > 0) {
    // Capture context
    await browser_take_screenshot({ filename: `wizard-step-${step}-error.png` });
    // Record errors with step context
  }
}
```

**Example Error Detected:**
```
Critical Error at Step 3 (Beneficiaries):
[13:15:44] Uncaught TypeError: beneficiaries.map is not a function
  at validateBeneficiaries (wizard.js:445)

Context: User added 2 beneficiaries, clicked Continue
Data State: beneficiaries stored as object instead of array
Screenshot: wizard-step3-error.png

Debugging Recommendation:
- Data persistence layer storing beneficiaries incorrectly
- Check sessionStorage/localStorage schema
- Verify API response format for beneficiaries
- Add runtime type checking for critical data structures
```

---

## 7. Real-Time Data Updates

**Scenario:** Monitor WebSocket/SSE real-time dashboard

**Workflow:**
```
1. Navigate to live dashboard
2. Wait for initial data load
3. Monitor for 30 seconds (real-time updates)
4. Trigger manual refresh
5. Check for any accumulated errors
```

**Console Checkpoints:**
- After initial load (check for WebSocket connection errors)
- Every 10 seconds during monitoring (check for update errors)
- After manual refresh (check for data sync errors)

**Example Errors Detected:**
```
Warning at 00:15 (Real-time Update):
[14:50:15] WebSocket connection to 'wss://live.example.com' failed
  Error: Connection timeout after 30000ms

Info at 00:18 (Fallback):
[14:50:18] Falling back to polling mode (30s interval)

Warning at 00:25 (Data Update):
[14:50:25] Received malformed data packet
  Expected: { type: 'update', data: {...} }
  Received: { type: 'update', data: null }

Context: Real-time updates experiencing connection and data issues
Screenshot: dashboard-realtime-errors.png

Debugging Recommendations:
- WebSocket connection timing out - check network/firewall rules
- Application properly falling back to polling (good error handling)
- Data validation needed for incoming real-time messages
- Consider adding connection status indicator in UI
- Implement data validation before state updates
```

---

## Common Patterns Summary

### Pattern 1: Critical Operation Monitoring
```
Execute critical operation
  ↓
Wait for completion
  ↓
Check console (level: "error")
  ↓
If errors: Capture context + screenshot
  ↓
Report or halt workflow
```

### Pattern 2: Multi-Step Form Monitoring
```
For each form step:
  Fill fields
    ↓
  Submit/Continue
    ↓
  Wait for next step
    ↓
  Check console (level: "warning")
    ↓
  Log any issues with step number
```

### Pattern 3: Third-Party Integration Validation
```
Page load
  ↓
Wait for all scripts
  ↓
Check console (level: "warning")
  ↓
Categorize by integration (GA, Stripe, etc.)
  ↓
Report integration health status
```

### Pattern 4: Real-Time Application Monitoring
```
Initial load
  ↓
Baseline console check
  ↓
Monitor period (30-60s)
  ↓
Periodic console checks (every 10s)
  ↓
Aggregate errors by type/severity
  ↓
Report patterns and trends
```
