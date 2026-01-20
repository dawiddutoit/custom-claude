# Playwright E2E Testing Examples

Complete test scenarios demonstrating the workflow pattern.

## Table of Contents

1. Basic Login Flow
2. Registration Form with Validation
3. Shopping Cart Checkout
4. Search and Filter
5. File Upload
6. Multi-Tab Navigation
7. API-Driven Dashboard
8. Error Handling Test
9. Performance Monitoring
10. Mobile Responsive Test

---

## 1. Basic Login Flow

**Scenario:** Test user authentication with valid credentials

**Test Steps:**

```
1. Navigate to login page
   browser_navigate(url="http://localhost:3000/login")

2. Wait for page load
   browser_wait_for(time=2)

3. Capture initial state
   browser_snapshot() → Save output
   browser_take_screenshot(filename="login-initial.png")

4. Fill login form
   browser_snapshot() → Identify form refs
   browser_fill_form(fields=[
     {name: "Email", ref: "ref_3", type: "textbox", value: "test@example.com"},
     {name: "Password", ref: "ref_4", type: "textbox", value: "password123"}
   ])

5. Submit form
   browser_click(element="Login Button", ref: "ref_5")

6. Wait for success
   browser_wait_for(text="Welcome")

7. Check console
   browser_console_messages(level="error") → Expect: []

8. Verify network
   browser_network_requests() → Check POST /api/login returns 200

9. Capture final state
   browser_snapshot() → Save output
   browser_take_screenshot(filename="login-success.png")

10. Generate report
    python scripts/generate_test_report.py \
      --test-name "Login Flow" \
      --url "http://localhost:3000/login" \
      --screenshots "login-initial.png,login-success.png" \
      --status "passed" \
      --output "reports/login-test.md"
```

**Expected Outcome:**
- ✅ "Welcome" text visible
- ✅ No console errors
- ✅ Authentication API call succeeded
- ✅ User redirected to dashboard

---

## 2. Registration Form with Validation

**Scenario:** Test form validation and submission

**Test Steps:**

```
1. Navigate to signup page
   browser_navigate(url="http://localhost:3000/signup")

2. Capture initial state
   browser_snapshot()
   browser_take_screenshot(filename="signup-initial.png")

3. Fill form with invalid email
   browser_fill_form(fields=[
     {name: "Email", ref: "ref_5", type: "textbox", value: "invalid-email"},
     {name: "Password", ref: "ref_6", type: "textbox", value: "pass123"}
   ])

4. Submit form
   browser_click(element="Sign Up", ref: "ref_7")

5. Wait for validation error
   browser_wait_for(text="Invalid email")

6. Capture validation state
   browser_take_screenshot(filename="signup-validation-error.png")

7. Fix email and resubmit
   browser_fill_form(fields=[
     {name: "Email", ref: "ref_5", type: "textbox", value: "valid@example.com"}
   ])
   browser_click(element="Sign Up", ref: "ref_7")

8. Wait for success
   browser_wait_for(text="Account created")

9. Check console and network
   browser_console_messages(level="error")
   browser_network_requests()

10. Capture final state
    browser_snapshot()
    browser_take_screenshot(filename="signup-success.png")
```

**Expected Outcome:**
- ✅ Validation error shown for invalid email
- ✅ Form accepts valid email
- ✅ POST /api/signup returns 201
- ✅ Success message displayed

---

## 3. Shopping Cart Checkout

**Scenario:** Multi-step checkout process

**Test Steps:**

```
1. Navigate to product page
   browser_navigate(url="http://localhost:3000/products/123")

2. Capture initial state
   browser_snapshot()
   browser_take_screenshot(filename="product-page.png")

3. Add to cart
   browser_click(element="Add to Cart", ref: "ref_8")
   browser_wait_for(text="Added to cart")

4. Navigate to cart
   browser_click(element="Cart Icon", ref: "ref_2")
   browser_wait_for(text="Shopping Cart")

5. Capture cart state
   browser_snapshot()
   browser_take_screenshot(filename="cart-page.png")

6. Proceed to checkout
   browser_click(element="Checkout", ref: "ref_10")

7. Fill shipping info
   browser_fill_form(fields=[
     {name: "Name", ref: "ref_12", type: "textbox", value: "John Doe"},
     {name: "Address", ref: "ref_13", type: "textbox", value: "123 Main St"},
     {name: "City", ref: "ref_14", type: "textbox", value: "Boston"}
   ])
   browser_click(element: "Continue", ref: "ref_15")

8. Capture shipping state
   browser_take_screenshot(filename="checkout-shipping.png")

9. Fill payment info (test mode)
   browser_fill_form(fields=[
     {name: "Card Number", ref: "ref_17", type: "textbox", value: "4242424242424242"},
     {name: "Expiry", ref: "ref_18", type: "textbox", value: "12/25"}
   ])

10. Place order
    browser_click(element: "Place Order", ref: "ref_19")
    browser_wait_for(text="Order Confirmed")

11. Check all API calls
    browser_network_requests()
    → Verify: POST /api/cart, POST /api/orders

12. Capture final state
    browser_snapshot()
    browser_take_screenshot(filename="order-confirmation.png")

13. Check console
    browser_console_messages(level="error") → Expect: []
```

**Expected Outcome:**
- ✅ Product added to cart
- ✅ All form steps completed
- ✅ Order submitted successfully
- ✅ No console errors throughout flow

---

## 4. Search and Filter

**Scenario:** Test search functionality and filters

**Test Steps:**

```
1. Navigate to search page
   browser_navigate(url="http://localhost:3000/search")

2. Capture initial state
   browser_snapshot()
   browser_take_screenshot(filename="search-initial.png")

3. Enter search query
   browser_fill_form(fields=[
     {name: "Search", ref: "ref_5", type: "textbox", value: "laptop"}
   ])
   browser_key(key="Enter")

4. Wait for results
   browser_wait_for(text="results found")

5. Capture search results
   browser_snapshot()
   browser_take_screenshot(filename="search-results.png")

6. Apply price filter
   browser_fill_form(fields=[
     {name: "Min Price", ref: "ref_10", type: "textbox", value: "500"},
     {name: "Max Price", ref: "ref_11", type: "textbox", value: "1500"}
   ])
   browser_click(element: "Apply Filters", ref: "ref_12")

7. Wait for filtered results
   browser_wait_for(time=1)

8. Verify network requests
   browser_network_requests()
   → Check: GET /api/search?q=laptop&min=500&max=1500

9. Capture filtered state
   browser_snapshot()
   browser_take_screenshot(filename="search-filtered.png")

10. Check console
    browser_console_messages(level="error")
```

**Expected Outcome:**
- ✅ Search returns results
- ✅ Filters update results
- ✅ API called with correct parameters
- ✅ No console errors

---

## 5. File Upload

**Scenario:** Test file upload functionality

**Test Steps:**

```
1. Navigate to upload page
   browser_navigate(url="http://localhost:3000/upload")

2. Capture initial state
   browser_snapshot()
   browser_take_screenshot(filename="upload-initial.png")

3. Trigger file chooser
   browser_click(element: "Choose File", ref: "ref_5")

4. Upload file
   browser_file_upload(paths=["/path/to/test-document.pdf"])

5. Wait for upload indicator
   browser_wait_for(text="Uploaded")

6. Verify network request
   browser_network_requests()
   → Check: POST /api/upload (multipart/form-data)

7. Capture upload success state
   browser_snapshot()
   browser_take_screenshot(filename="upload-success.png")

8. Check console
   browser_console_messages(level="error")
```

**Expected Outcome:**
- ✅ File selected successfully
- ✅ Upload completed
- ✅ Server acknowledged upload (200/201)
- ✅ No console errors

---

## 6. Multi-Tab Navigation

**Scenario:** Test SPA navigation between tabs

**Test Steps:**

```
1. Navigate to dashboard
   browser_navigate(url="http://localhost:3000/dashboard")

2. Capture dashboard state
   browser_snapshot()
   browser_take_screenshot(filename="tab-dashboard.png")

3. Click Profile tab
   browser_click(element: "Profile Tab", ref: "ref_7")
   browser_wait_for(text="User Profile")

4. Capture profile state
   browser_snapshot()
   browser_take_screenshot(filename="tab-profile.png")

5. Click Settings tab
   browser_click(element: "Settings Tab", ref: "ref_8")
   browser_wait_for(text="Account Settings")

6. Capture settings state
   browser_snapshot()
   browser_take_screenshot(filename="tab-settings.png")

7. Verify console (no errors during navigation)
   browser_console_messages(level="error")

8. Check network (minimal requests for SPA)
   browser_network_requests()
```

**Expected Outcome:**
- ✅ All tabs load correctly
- ✅ Content updates without full page reload
- ✅ No console errors during navigation
- ✅ Minimal network requests (SPA behavior)

---

## 7. API-Driven Dashboard

**Scenario:** Test dashboard with live data

**Test Steps:**

```
1. Navigate to dashboard
   browser_navigate(url="http://localhost:3000/dashboard")

2. Wait for data load
   browser_wait_for(time=3)

3. Capture loading state
   browser_take_screenshot(filename="dashboard-loading.png")

4. Wait for data display
   browser_wait_for(text="Total Sales")

5. Capture loaded state
   browser_snapshot()
   browser_take_screenshot(filename="dashboard-loaded.png")

6. Verify API calls
   browser_network_requests()
   → Check: GET /api/dashboard/stats, GET /api/dashboard/charts

7. Refresh data
   browser_click(element: "Refresh", ref: "ref_5")
   browser_wait_for(time=2)

8. Verify refresh API call
   browser_network_requests()
   → Check: New GET requests made

9. Check console
   browser_console_messages(level="error")
```

**Expected Outcome:**
- ✅ Dashboard loads with data
- ✅ All API calls succeed (200 status)
- ✅ Refresh triggers new API calls
- ✅ No console errors

---

## 8. Error Handling Test

**Scenario:** Test application behavior with API failures

**Test Steps:**

```
1. Navigate to page that makes API calls
   browser_navigate(url="http://localhost:3000/users")

2. Wait for initial load
   browser_wait_for(time=2)

3. Simulate network failure (if app has test mode)
   [Configure app to return 500 for next request]

4. Trigger action that calls API
   browser_click(element: "Load More", ref: "ref_8")

5. Wait for error message
   browser_wait_for(text="Failed to load")

6. Capture error state
   browser_snapshot()
   browser_take_screenshot(filename="error-state.png")

7. Check console for errors
   browser_console_messages(level="error")
   → Expect: Error message logged

8. Verify network failure
   browser_network_requests()
   → Check: 500 status code

9. Test retry
   browser_click(element: "Retry", ref: "ref_10")
   browser_wait_for(text="Loaded successfully")
```

**Expected Outcome:**
- ✅ Error message displayed to user
- ✅ Console logs error appropriately
- ✅ Retry functionality works
- ✅ App doesn't crash on error

---

## 9. Performance Monitoring

**Scenario:** Track page load performance

**Test Steps:**

```
1. Navigate to page
   browser_navigate(url="http://localhost:3000/products")

2. Wait for complete load
   browser_wait_for(time=5)

3. Capture loaded state
   browser_snapshot()
   browser_take_screenshot(filename="products-loaded.png")

4. Check all network requests
   browser_network_requests()
   → Analyze: Response times, resource sizes

5. Check console for performance warnings
   browser_console_messages(level="warning")
   → Look for: "Slow script execution", "Large bundle size"

6. Generate performance report
   [Extract timing data from network requests]
   - Initial page load: < 2s
   - API calls: < 500ms
   - Image loads: < 1s
```

**Expected Outcome:**
- ✅ Page loads within acceptable time
- ✅ No performance warnings
- ✅ All resources load successfully
- ✅ API calls respond quickly

---

## 10. Mobile Responsive Test

**Scenario:** Test mobile viewport behavior

**Test Steps:**

```
1. Resize browser to mobile
   browser_resize(width=375, height=667)

2. Navigate to page
   browser_navigate(url="http://localhost:3000")

3. Capture mobile initial state
   browser_snapshot()
   browser_take_screenshot(filename="mobile-home.png")

4. Open mobile menu
   browser_click(element: "Hamburger Menu", ref: "ref_3")
   browser_wait_for(text="Navigation Menu")

5. Capture menu state
   browser_take_screenshot(filename="mobile-menu.png")

6. Navigate to page
   browser_click(element: "Products Link", ref: "ref_5")
   browser_wait_for(text="Products")

7. Capture products mobile view
   browser_snapshot()
   browser_take_screenshot(filename="mobile-products.png")

8. Check console
   browser_console_messages(level="error")

9. Resize to desktop
   browser_resize(width=1920, height=1080)

10. Verify desktop layout
    browser_snapshot()
    browser_take_screenshot(filename="desktop-products.png")
```

**Expected Outcome:**
- ✅ Mobile menu functions correctly
- ✅ Layout adapts to viewport
- ✅ All interactions work on mobile
- ✅ No console errors on resize

---

## Common Patterns

### Pattern 1: State Capture
Always capture state before and after actions:
```
browser_snapshot()
browser_take_screenshot(filename="before-action.png")
[Perform action]
browser_snapshot()
browser_take_screenshot(filename="after-action.png")
```

### Pattern 2: Error Verification
Check console after every significant action:
```
browser_click(...)
browser_console_messages(level="error")
```

### Pattern 3: Network Verification
Verify API calls succeeded:
```
browser_network_requests()
→ Check for 2xx status codes
```

### Pattern 4: Wait Strategies
Prefer text-based waits over fixed time:
```
# Good
browser_wait_for(text="Success")

# Avoid (unless necessary)
browser_wait_for(time=5)
```

### Pattern 5: Report Generation
Always generate reports with all evidence:
```
python scripts/generate_test_report.py \
  --test-name "..." \
  --url "..." \
  --screenshots "..." \
  --console-logs console.json \
  --network-requests network.json \
  --status "passed" \
  --output "reports/test.md"
```
