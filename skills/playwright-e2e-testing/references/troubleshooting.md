# Playwright E2E Testing Troubleshooting

Common issues and solutions for E2E testing.

## Table of Contents

1. Element Not Found
2. Timing Issues
3. Network Request Failures
4. Console Errors
5. Screenshot Issues
6. Form Interaction Problems
7. Navigation Issues
8. Browser State Problems

---

## 1. Element Not Found

### Symptom
```
Error: Element with ref "ref_5" not found
```

### Causes
- Element not rendered yet (async loading)
- Wrong ref from outdated snapshot
- Element removed from DOM
- Element hidden by CSS

### Solutions

**Solution 1: Take fresh snapshot**
```
# Always snapshot before interacting
browser_snapshot()
→ Get latest refs from output
browser_click(element="Button", ref="ref_X")
```

**Solution 2: Wait for element**
```
# Wait for text to appear first
browser_wait_for(text="Submit")
→ Then snapshot to get ref
browser_snapshot()
browser_click(element="Submit", ref="ref_X")
```

**Solution 3: Check element visibility**
```
# Use snapshot to verify element is visible
browser_snapshot()
→ Look for element in output
→ Check it's not hidden or disabled
```

### Prevention
- Always take fresh snapshot before interactions
- Don't reuse refs from previous snapshots
- Verify element visibility in snapshot output

---

## 2. Timing Issues

### Symptom
```
Test fails intermittently
Expected text "Success" not found
```

### Causes
- Fixed waits too short
- Async operations not complete
- Network delays
- Animation/transition timing

### Solutions

**Solution 1: Use text-based waits**
```
# ❌ AVOID: Fixed time waits
browser_wait_for(time=2)

# ✅ PREFER: Wait for specific text
browser_wait_for(text="Loading complete")
```

**Solution 2: Increase wait time for slow operations**
```
# For known slow operations
browser_click(element="Submit", ref="ref_5")
browser_wait_for(time=5)  # Wait for processing
browser_wait_for(text="Success")
```

**Solution 3: Check network requests**
```
# Verify async operations completed
browser_click(element="Save", ref="ref_5")
browser_wait_for(time=2)
browser_network_requests()
→ Check if POST completed (200 status)
```

### Prevention
- Use text-based waits whenever possible
- Add extra time for known slow operations
- Monitor network requests for completion
- Don't rely solely on fixed time waits

---

## 3. Network Request Failures

### Symptom
```
API call returned 404/500
Expected 200, got 401
```

### Causes
- API endpoint changed
- Authentication expired
- Server error
- CORS issues
- Request payload invalid

### Solutions

**Solution 1: Check network requests**
```
browser_network_requests()
→ Review all requests
→ Check status codes
→ Verify request URLs
```

**Solution 2: Verify authentication**
```
# For authenticated endpoints
browser_navigate(url="http://localhost:3000/login")
[Complete login flow]
→ Obtain auth token
browser_navigate(url="http://localhost:3000/protected")
```

**Solution 3: Check console for errors**
```
browser_console_messages(level="error")
→ Look for CORS errors
→ Check for authentication errors
→ Verify payload validation errors
```

**Solution 4: Verify API availability**
```
# Test API endpoint directly first
curl http://localhost:3000/api/users
→ Confirm endpoint exists
→ Verify expected response
```

### Prevention
- Verify API endpoints before testing
- Include authentication in test setup
- Monitor console for network errors
- Check network requests after actions

---

## 4. Console Errors

### Symptom
```
Console shows: "Uncaught TypeError: Cannot read property 'x' of undefined"
Test passes but errors logged
```

### Causes
- JavaScript errors in application
- Missing error handling
- Race conditions
- Invalid state

### Solutions

**Solution 1: Check console after every action**
```
browser_click(element="Button", ref="ref_5")
browser_console_messages(level="error")
→ Verify no errors logged
→ Fail test if errors present
```

**Solution 2: Capture full console log**
```
# At end of test
browser_console_messages(level="info")
→ Review all messages
→ Look for warnings that might indicate issues
```

**Solution 3: Debug with screenshots**
```
# When error occurs
browser_console_messages(level="error")
browser_take_screenshot(filename="error-state.png")
browser_snapshot()
→ Correlate error with UI state
```

### Prevention
- Check console after every significant action
- Fail tests on console errors
- Include console logs in test reports
- Fix application errors, don't ignore them

---

## 5. Screenshot Issues

### Symptom
```
Screenshot file not found
Screenshot shows wrong state
```

### Causes
- File path incorrect
- Screenshot taken before render
- File overwritten
- Insufficient permissions

### Solutions

**Solution 1: Use absolute paths**
```
# Use full paths for screenshots
browser_take_screenshot(filename="/path/to/test-artifacts/screenshots/initial.png")
```

**Solution 2: Wait before screenshot**
```
browser_click(element="Button", ref="ref_5")
browser_wait_for(time=1)  # Wait for render
browser_take_screenshot(filename="after-click.png")
```

**Solution 3: Unique filenames**
```
# Use timestamps to avoid overwrites
import datetime
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
browser_take_screenshot(filename=f"screenshot-{timestamp}.png")
```

**Solution 4: Verify directory exists**
```
# Create screenshots directory first
mkdir -p test-artifacts/screenshots/
```

### Prevention
- Create output directories before testing
- Use unique filenames
- Wait for UI updates before screenshots
- Use absolute paths

---

## 6. Form Interaction Problems

### Symptom
```
Form field not filled
Checkbox not checked
Dropdown not selected
```

### Causes
- Wrong element ref
- Wrong input type specified
- Element disabled
- JavaScript interference

### Solutions

**Solution 1: Verify element type in snapshot**
```
browser_snapshot()
→ Check element type (textbox, checkbox, combobox, etc.)
→ Use correct type in fill_form
```

**Solution 2: Check element state**
```
browser_snapshot()
→ Verify element is not disabled
→ Check if element is readonly
```

**Solution 3: Use correct value format**
```
# Checkbox - use boolean
{name: "Terms", ref: "ref_5", type: "checkbox", value: true}

# Textbox - use string
{name: "Email", ref: "ref_6", type: "textbox", value: "test@example.com"}

# Select - use option value or text
{name: "Country", ref: "ref_7", type: "combobox", value: "USA"}
```

**Solution 4: Fill one field at a time**
```
# Instead of batch filling
browser_fill_form(fields=[
  {name: "Field1", ref: "ref_5", type: "textbox", value: "value1"}
])
browser_fill_form(fields=[
  {name: "Field2", ref: "ref_6", type: "textbox", value: "value2"}
])
```

### Prevention
- Always snapshot before filling forms
- Use correct input types
- Verify element state in snapshot
- Test form interactions manually first

---

## 7. Navigation Issues

### Symptom
```
Page not loading
Unexpected redirect
Wrong URL
```

### Causes
- Server not running
- URL typo
- Application redirect logic
- Authentication required

### Solutions

**Solution 1: Verify server is running**
```
# Test URL manually
curl http://localhost:3000
→ Confirm server responds
```

**Solution 2: Check for redirects**
```
browser_navigate(url="http://localhost:3000/protected")
browser_wait_for(time=2)
browser_snapshot()
→ Check if redirected to login
```

**Solution 3: Handle authentication**
```
# Complete login first
browser_navigate(url="http://localhost:3000/login")
[Login flow]
→ Then navigate to protected page
browser_navigate(url="http://localhost:3000/protected")
```

**Solution 4: Wait after navigation**
```
browser_navigate(url="http://localhost:3000")
browser_wait_for(time=2)  # Wait for page load
browser_wait_for(text="Expected content")
```

### Prevention
- Verify application is running
- Handle authentication in test setup
- Wait for page load after navigation
- Check for unexpected redirects

---

## 8. Browser State Problems

### Symptom
```
Test works in isolation but fails in suite
Unexpected data from previous test
Session state persists
```

### Causes
- Cookies/localStorage not cleared
- Previous test didn't clean up
- Shared browser state
- Race conditions

### Solutions

**Solution 1: Clear state between tests**
```
# Use browser_run_code to clear storage
browser_run_code(code=`
  async (page) => {
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  }
`)
```

**Solution 2: Use fresh browser context**
```
# Close and reopen browser
browser_close()
browser_navigate(url="http://localhost:3000")
```

**Solution 3: Logout between tests**
```
# Explicit logout
browser_navigate(url="http://localhost:3000/logout")
browser_wait_for(text="Logged out")
```

### Prevention
- Clear state between independent tests
- Use isolated browser contexts
- Don't assume clean state
- Implement proper test teardown

---

## Debugging Checklist

When test fails, check in this order:

1. **Verify Application Running**
   - [ ] Server is accessible
   - [ ] Correct URL
   - [ ] No deployment issues

2. **Check Element Selection**
   - [ ] Fresh snapshot taken
   - [ ] Correct ref used
   - [ ] Element visible in snapshot

3. **Verify Timing**
   - [ ] Waited for async operations
   - [ ] Used text-based waits
   - [ ] Allowed for animations

4. **Check Network**
   - [ ] API calls succeeded
   - [ ] Correct status codes
   - [ ] Authentication valid

5. **Review Console**
   - [ ] No JavaScript errors
   - [ ] No warnings
   - [ ] Expected logs present

6. **Examine Evidence**
   - [ ] Screenshots show expected state
   - [ ] Snapshots include target elements
   - [ ] Network logs show API calls

7. **Verify Test Logic**
   - [ ] Correct test steps
   - [ ] Valid test data
   - [ ] Proper assertions

---

## Getting Help

If issues persist:

1. **Capture Full Evidence**
   - Initial state snapshot
   - All screenshots
   - Console logs
   - Network requests
   - Error messages

2. **Create Minimal Reproduction**
   - Isolate failing test
   - Remove unrelated steps
   - Test manually first

3. **Review Similar Tests**
   - Check examples.md for patterns
   - Compare with working tests
   - Verify approach matches examples

4. **Document Issue**
   - What was expected
   - What actually happened
   - Steps to reproduce
   - Evidence files
