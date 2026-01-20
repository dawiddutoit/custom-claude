# Console Error Report Template

Use this template for structured error reporting during console monitoring workflows.

---

## Console Error Report

**Workflow:** [Workflow name - e.g., "E-Commerce Checkout"]
**Executed:** [Timestamp - e.g., "2025-12-20 14:32:15 UTC"]
**Duration:** [Workflow duration - e.g., "45 seconds"]
**Total Operations:** [Number of operations monitored]
**Monitoring Level:** [error | warning | info | debug]

---

## Summary

| Metric | Count |
|--------|-------|
| **Critical Errors** | [count] |
| **Warnings** | [count] |
| **Info Messages** | [count] |
| **Total Messages** | [count] |

**Result:** [✅ Success - No Errors | ⚠️ Warnings Detected | ❌ Critical Errors Detected]

---

## Critical Errors (level: error)

### Error 1

**Timestamp:** [e.g., "14:32:15.123"]
**Context:** [Operation that triggered - e.g., "After clicking 'Apply Discount Code'"]
**Type:** [Error category - e.g., "Runtime Error / Network Error / CORS Error"]

**Message:**
```
[Full error message from console]
```

**Stack Trace:**
```
[Stack trace if available]
```

**Location:**
- File: [e.g., "checkout.js"]
- Line: [e.g., "245"]
- Column: [e.g., "12"]
- URL: [Full URL to source file]

**Visual Context:**
- Screenshot: [filename.png]
- Page URL: [URL at time of error]
- DOM Snapshot: [filename.md or inline]

**Debugging Recommendations:**
- [Specific suggestion 1]
- [Specific suggestion 2]
- [Specific suggestion 3]

---

### Error 2

[Repeat structure above for each critical error]

---

## Warnings (level: warning)

### Warning 1

**Timestamp:** [e.g., "14:30:45.678"]
**Context:** [Operation - e.g., "During address validation"]
**Type:** [Warning category - e.g., "Deprecation / Performance / Security"]

**Message:**
```
[Warning message]
```

**Impact:** [Description of potential impact - e.g., "Will break in future browser versions"]

**Recommendations:**
- [Specific suggestion to address warning]

---

### Warning 2

[Repeat for each warning]

---

## Info Messages

[Summarize info-level messages if relevant to debugging, otherwise omit this section]

**Notable Messages:**
- [Timestamp] [Message summary]
- [Timestamp] [Message summary]

---

## Network Correlation

[If network monitoring was used alongside console monitoring]

| Console Error | Related Network Request | Status | Timing Correlation |
|---------------|------------------------|--------|-------------------|
| [Error summary] | [Request URL] | [Status code] | [Time difference] |

**Analysis:** [Description of how network failures relate to console errors]

---

## Debugging Context

### Application State
- **URL at time of error:** [Full URL with query params]
- **User action:** [What user/automation was doing]
- **Expected outcome:** [What should have happened]
- **Actual outcome:** [What actually happened]

### Browser State
- **Browser:** [Chrome/Firefox/Safari + version]
- **Viewport:** [Width x Height]
- **Device:** [Desktop/Mobile/Tablet]

### Environment
- **Environment:** [Production/Staging/Development]
- **User session:** [Logged in/out, user role if relevant]
- **Feature flags:** [Any relevant feature flags enabled]

---

## Error Categories

### By Severity
- **Workflow-Breaking:** [count] - [list error numbers]
- **Feature-Breaking:** [count] - [list error numbers]
- **Degraded Experience:** [count] - [list warning numbers]
- **Informational:** [count]

### By Source
- **Application Code:** [count] - [list error numbers]
- **Third-Party Scripts:** [count] - [list error numbers]
- **Browser/Platform:** [count] - [list error numbers]

### By Type
- **Runtime Errors:** [count]
- **Network Errors:** [count]
- **CORS Errors:** [count]
- **Resource Loading Errors:** [count]
- **Deprecation Warnings:** [count]
- **Performance Warnings:** [count]

---

## Recommendations

### Immediate Actions
1. [Most critical fix - e.g., "Fix null reference in discount calculation"]
2. [Second priority - e.g., "Add error handling for payment API failures"]
3. [Third priority]

### Short-Term Improvements
- [Preventive measure - e.g., "Add runtime type checking for cart data"]
- [Monitoring improvement - e.g., "Implement error boundary for checkout flow"]
- [Testing enhancement - e.g., "Add integration test for discount code edge cases"]

### Long-Term Considerations
- [Architectural improvement - e.g., "Modernize AJAX calls to fetch() API"]
- [Infrastructure - e.g., "Implement proper error logging/monitoring"]
- [Process - e.g., "Add console error checking to CI/CD pipeline"]

---

## Attachments

### Screenshots
- [filename-1.png] - [Description of what screenshot shows]
- [filename-2.png] - [Description]

### Snapshots
- [snapshot-1.md] - [DOM state at Error 1]
- [snapshot-2.md] - [DOM state at Error 2]

### Raw Data
- [console-messages-raw.json] - [Full console messages JSON]
- [network-requests-raw.json] - [Network requests if captured]

---

## Next Steps

- [ ] [Specific action item 1]
- [ ] [Specific action item 2]
- [ ] [Specific action item 3]
- [ ] Re-run workflow after fixes to validate resolution
- [ ] Update monitoring strategy based on findings

---

**Report Generated:** [Timestamp]
**Generated By:** [Playwright Console Monitor skill]
**Report Version:** 1.0
