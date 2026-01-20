# Playwright Console API Reference

Detailed reference for `mcp__playwright__browser_console_messages` and console monitoring patterns.

## Table of Contents

1. API Signature
2. Console Message Levels
3. Message Format
4. Message Persistence
5. Advanced Patterns
6. Error Categorization
7. Performance Considerations
8. Integration with Other Tools

---

## 1. API Signature

```typescript
mcp__playwright__browser_console_messages({
  level?: "error" | "warning" | "info" | "debug"
})
```

### Parameters

**level** (optional)
- Type: `"error" | "warning" | "info" | "debug"`
- Default: `"info"`
- Behavior: Returns messages at specified level AND more severe levels

**Level Hierarchy:**
```
debug     ← Least severe (includes ALL messages)
  ↓
info      ← Includes info + warning + error
  ↓
warning   ← Includes warning + error
  ↓
error     ← Most severe (errors only)
```

### Return Value

Returns array of console message objects:

```javascript
[
  {
    type: "error" | "warning" | "info" | "log" | "debug",
    text: "Error message text",
    timestamp: "2025-12-20T14:32:15.123Z",
    location: {
      url: "https://example.com/app.js",
      lineNumber: 245,
      columnNumber: 12
    },
    args: [...],  // Original console arguments
    stackTrace: [...] // Stack trace for errors
  },
  // ... more messages
]
```

---

## 2. Console Message Levels

### error

**Browser Sources:**
- `console.error()`
- Uncaught exceptions
- Unhandled promise rejections
- Network request failures (shown in console)
- Missing resource errors (404s for scripts/styles)
- CORS errors

**Example Messages:**
```
Uncaught TypeError: Cannot read property 'x' of undefined
Uncaught (in promise) Error: API request failed
Failed to load resource: net::ERR_CONNECTION_REFUSED
Access to fetch at 'https://api.example.com' from origin 'https://example.com' has been blocked by CORS policy
```

**When to Use:** After critical operations that MUST succeed (payments, submissions, authentication)

### warning

**Browser Sources:**
- `console.warn()`
- Deprecation warnings
- Resource load warnings
- Security warnings
- Performance warnings

**Example Messages:**
```
[Deprecation] Synchronous XMLHttpRequest on the main thread is deprecated
[Violation] 'requestAnimationFrame' handler took 245ms
Mixed Content: The page at 'https://example.com' was loaded over HTTPS, but requested an insecure image 'http://...'
Cookie "session" will be soon rejected because it has the "SameSite" attribute set to "None"
```

**When to Use:** General monitoring, form workflows, feature usage

### info

**Browser Sources:**
- `console.info()`
- `console.log()` (also captured at info level)
- Application lifecycle events
- Navigation events
- Custom application logging

**Example Messages:**
```
Application initialized
User logged in: user@example.com
Route changed: /dashboard → /settings
API request successful: GET /api/users
```

**When to Use:** Understanding application flow, debugging workflows, regression testing

### debug

**Browser Sources:**
- `console.debug()`
- Verbose framework output
- Detailed timing information
- Development-only messages

**Example Messages:**
```
[Vue DevTools] Ready
[React DevTools] Initialized
[Redux] Action: USER_LOGIN
[Performance] Component render: 12ms
```

**When to Use:** Deep debugging, framework-level investigation, performance analysis

---

## 3. Message Format

### Standard Message Object

```javascript
{
  type: "error",
  text: "Uncaught TypeError: Cannot read property 'total' of undefined",
  timestamp: "2025-12-20T14:32:15.123Z",
  location: {
    url: "https://example.com/checkout.js",
    lineNumber: 245,
    columnNumber: 12
  },
  args: [
    "Uncaught TypeError: Cannot read property 'total' of undefined"
  ],
  stackTrace: [
    "at calculateTotal (checkout.js:245:12)",
    "at applyDiscount (checkout.js:189:5)",
    "at HTMLButtonElement.onclick (checkout.html:89:10)"
  ]
}
```

### Message Properties

**type**
- Console method used: "error", "warning", "info", "log", "debug"
- Determines severity and filtering behavior

**text**
- Human-readable error message
- Concatenation of all console arguments
- Use for error reporting and display

**timestamp**
- ISO 8601 format timestamp
- When message was logged
- Use for temporal correlation with user actions

**location**
- Source file URL where console message originated
- Line and column numbers for debugging
- May be missing for native browser errors

**args**
- Raw console arguments
- Useful for structured logging (if app uses JSON logging)
- May include objects, not just strings

**stackTrace**
- Array of stack frames (for errors)
- Most recent call first
- Use for identifying error source in minified code

---

## 4. Message Persistence

### Persistence Rules

**Within Page Lifetime:**
- Console messages accumulate during page lifetime
- Repeated calls to `browser_console_messages` return ALL messages since page load
- Messages are NOT cleared after reading

**Page Navigation:**
- Navigation to new page (document) clears console
- SPA route changes do NOT clear console (same document)
- iframe navigation clears iframe console only

**Tab State:**
- Console messages persist even if tab is hidden
- Background tabs continue accumulating messages
- Tab reload clears all messages

### Managing Message Accumulation

**Pattern 1: Baseline + Delta**
```javascript
// Get baseline after page load
const baseline = await browser_console_messages({ level: "error" });
const baselineCount = baseline.length;

// Execute workflow...

// Get new messages
const current = await browser_console_messages({ level: "error" });
const newMessages = current.slice(baselineCount);
```

**Pattern 2: Manual Tracking**
```javascript
let lastCheckedIndex = 0;

async function checkNewErrors() {
  const all = await browser_console_messages({ level: "error" });
  const newErrors = all.slice(lastCheckedIndex);
  lastCheckedIndex = all.length;
  return newErrors;
}
```

**Pattern 3: Page Reload for Clean Slate**
```javascript
// Reload page to clear console
await browser_navigate({ url: currentUrl });

// Now console is empty - execute workflow with clean baseline
```

---

## 5. Advanced Patterns

### Pattern 1: Error-First Monitoring

Monitor only for errors during critical operations:

```javascript
async function criticalOperationWithMonitoring(operation, context) {
  // Get baseline
  const before = await browser_console_messages({ level: "error" });

  // Execute operation
  await operation();

  // Check for new errors
  const after = await browser_console_messages({ level: "error" });
  const newErrors = after.slice(before.length);

  if (newErrors.length > 0) {
    // Capture context
    await browser_take_screenshot({
      filename: `error-${context}-${Date.now()}.png`
    });

    // Return error report
    return {
      success: false,
      errors: newErrors,
      context: context
    };
  }

  return { success: true };
}
```

### Pattern 2: Multi-Level Monitoring

Different monitoring levels for different operations:

```javascript
async function multiLevelMonitoring(workflow) {
  const results = [];

  for (const step of workflow.steps) {
    const level = step.critical ? "error" : "warning";
    const before = await browser_console_messages({ level });

    await step.execute();

    const after = await browser_console_messages({ level });
    const newMessages = after.slice(before.length);

    results.push({
      step: step.name,
      level: level,
      messages: newMessages,
      critical: step.critical && newMessages.length > 0
    });
  }

  return results;
}
```

### Pattern 3: Error Categorization

Categorize errors by type for better reporting:

```javascript
function categorizeErrors(errors) {
  return {
    network: errors.filter(e =>
      e.text.includes('Failed to load') ||
      e.text.includes('net::ERR') ||
      e.text.includes('fetch')
    ),

    runtime: errors.filter(e =>
      e.text.includes('TypeError') ||
      e.text.includes('ReferenceError') ||
      e.text.includes('Uncaught')
    ),

    cors: errors.filter(e =>
      e.text.includes('CORS') ||
      e.text.includes('Access-Control')
    ),

    thirdParty: errors.filter(e =>
      e.location?.url && !e.location.url.includes(appDomain)
    ),

    other: errors.filter(e => /* not categorized above */)
  };
}
```

### Pattern 4: Timeout-Based Monitoring

Monitor for errors within time window:

```javascript
async function monitorForDuration(durationMs, level = "error") {
  const startTime = Date.now();
  const startCount = (await browser_console_messages({ level })).length;
  const errors = [];

  while (Date.now() - startTime < durationMs) {
    const current = await browser_console_messages({ level });
    const newErrors = current.slice(startCount);

    for (const error of newErrors) {
      if (!errors.find(e => e.text === error.text)) {
        errors.push(error);
      }
    }

    await new Promise(resolve => setTimeout(resolve, 1000));
  }

  return errors;
}
```

### Pattern 5: Error Correlation with Network

Correlate console errors with network failures:

```javascript
async function correlateErrorsWithNetwork() {
  const errors = await browser_console_messages({ level: "error" });
  const networkRequests = await browser_network_requests();

  const failedRequests = networkRequests.filter(r => r.status >= 400);

  const correlatedErrors = errors.map(error => {
    const relatedRequest = failedRequests.find(req =>
      error.text.includes(req.url) ||
      Math.abs(new Date(error.timestamp) - new Date(req.timestamp)) < 1000
    );

    return {
      error,
      networkRequest: relatedRequest || null
    };
  });

  return correlatedErrors;
}
```

---

## 6. Error Categorization

### By Severity

**Critical (Workflow-Breaking):**
- Payment failures
- Authentication errors
- Data submission errors
- Required API failures
- State corruption errors

**High (Feature-Breaking):**
- Form validation failures
- Optional API failures
- Third-party integration failures
- UI component errors

**Medium (Degraded Experience):**
- Performance warnings
- Deprecation warnings
- Missing optional resources
- Analytics failures

**Low (Informational):**
- Development mode warnings
- Debug messages
- Info logging
- Performance metrics

### By Source

**Application Errors:**
- Custom JavaScript errors
- React/Vue/Angular errors
- Business logic failures

**Third-Party Errors:**
- Analytics script failures
- Chat widget errors
- Payment processor errors
- CDN resource failures

**Browser/Platform Errors:**
- CORS violations
- Mixed content warnings
- Security policy violations
- Browser API errors

### By Impact

**User-Facing:**
- Errors that prevent user action
- Visible UI failures
- Data loss risks

**Behind-the-Scenes:**
- Silent failures
- Analytics failures
- Non-critical API failures
- Background sync errors

---

## 7. Performance Considerations

### API Call Overhead

**Console Check Cost:**
- ~100-200ms per call
- Negligible for most workflows
- Consider batching for high-frequency checks

**Screenshot Cost:**
- ~500ms-1s per screenshot
- Significant for many captures
- Only capture on actual errors

### Optimization Strategies

**Strategy 1: Selective Monitoring**
```javascript
// DON'T monitor every action
for (const item of items) {
  await click(item);
  // ❌ await checkConsole();  // Too frequent
}

// DO monitor critical checkpoints
await selectAllItems();
await submitBatch();
await checkConsole();  // ✅ Strategic checkpoint
```

**Strategy 2: Level-Appropriate Monitoring**
```javascript
// Use strictest level appropriate for operation
await login();
await checkConsole({ level: "error" });  // ✅ Critical - errors only

await fillOptionalField();
await checkConsole({ level: "warning" }); // ✅ Non-critical - warnings OK
```

**Strategy 3: Deferred Context Capture**
```javascript
// Capture context only when errors detected
const errors = await browser_console_messages({ level: "error" });

if (errors.length > 0) {
  // NOW capture expensive context
  await browser_take_screenshot();
  await browser_snapshot();
}
```

---

## 8. Integration with Other Tools

### With Network Monitoring

```javascript
async function fullDiagnostics() {
  const errors = await browser_console_messages({ level: "error" });
  const network = await browser_network_requests({
    includeStatic: false
  });

  return {
    consoleErrors: errors,
    failedRequests: network.filter(r => r.status >= 400),
    correlation: correlateErrorsWithNetwork(errors, network)
  };
}
```

### With Snapshots

```javascript
async function errorWithContext() {
  const errors = await browser_console_messages({ level: "error" });

  if (errors.length > 0) {
    const snapshot = await browser_snapshot();
    const screenshot = await browser_take_screenshot();

    return {
      errors,
      visualState: screenshot,
      domState: snapshot,
      timestamp: new Date().toISOString()
    };
  }
}
```

### With Wait Conditions

```javascript
async function waitForErrorFreeState(timeout = 5000) {
  const startTime = Date.now();

  while (Date.now() - startTime < timeout) {
    const errors = await browser_console_messages({ level: "error" });

    if (errors.length === 0) {
      return { success: true };
    }

    await new Promise(resolve => setTimeout(resolve, 500));
  }

  return {
    success: false,
    reason: "Errors persisted after timeout",
    errors: await browser_console_messages({ level: "error" })
  };
}
```

### With Custom Assertions

```javascript
async function assertNoConsoleErrors(context) {
  const errors = await browser_console_messages({ level: "error" });

  if (errors.length > 0) {
    await browser_take_screenshot({
      filename: `assertion-failed-${context}.png`
    });

    throw new Error(`
      Assertion Failed: Expected no console errors during ${context}
      Found ${errors.length} error(s):
      ${errors.map(e => `  - ${e.text}`).join('\n')}
    `);
  }
}
```

---

## Browser-Specific Behaviors

### Chrome/Chromium
- Full stack traces for errors
- Detailed CORS error messages
- Deprecation warnings for modern APIs
- Performance violation warnings

### Firefox
- Different error message formatting
- Security warnings formatted differently
- Network errors may have different text

### Safari
- More conservative error reporting
- Some warnings not exposed to console API
- Different CORS error format

**Recommendation:** Test console monitoring patterns across browsers if multi-browser support required. Use substring matching rather than exact message matching for cross-browser compatibility.
