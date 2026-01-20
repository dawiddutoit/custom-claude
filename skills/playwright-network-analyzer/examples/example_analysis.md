# Example Network Analyses

Sample network analysis reports for common workflows.

## Example 1: Login Flow Analysis

### Workflow
User navigates to login page, enters credentials, submits form.

### Network Requests (8 total)

```
1. GET /login - 200 OK (150ms)
2. GET /assets/login.css - 200 OK (80ms)
3. GET /assets/login.js - 200 OK (120ms)
4. POST /api/auth/login - 200 OK (250ms)
   Request: {"email": "user@example.com", "password": "***"}
   Response: {"token": "eyJ...", "user": {...}}
5. GET /api/user/profile - 200 OK (100ms)
6. GET /api/user/preferences - 500 Internal Server Error (1100ms)
7. GET /dashboard - 200 OK (200ms)
8. GET /assets/dashboard.css - 200 OK (90ms)
```

### Analysis Report

```markdown
# Network Analysis Report

**Total Requests:** 8
**API Calls:** 3
**Static Resources:** 3
**Failed Requests:** 1
**Slow Requests (>1000ms):** 1

## Failed Requests

- GET `/api/user/preferences` - **500** (1100ms)

## Slow Requests (>1000ms)

- GET `/api/user/preferences` - 500 (1100ms)

## Issues Identified

- ⚠️ Preferences API endpoint failing with server error
- ⚠️ Same endpoint also slow (1.1s response time)
- ℹ️ Login flow otherwise successful (token received)

## Recommendations

1. Fix `/api/user/preferences` backend error (500)
2. Add error handling in frontend (graceful degradation if preferences unavailable)
3. Consider making preferences optional for login flow (non-blocking)
```

---

## Example 2: E-Commerce Checkout Flow

### Workflow
User adds product to cart, proceeds to checkout, enters payment info.

### Network Requests (23 total)

```
1. GET /products/123 - 200 OK (180ms)
2. POST /api/cart/add - 200 OK (120ms)
3. GET /api/cart - 200 OK (150ms)
4. GET /api/cart/1/items - 200 OK (90ms)
5. GET /api/cart/1/items/1/details - 200 OK (85ms)
6. GET /api/cart/1/items/2/details - 200 OK (88ms)
7. GET /api/cart/1/items/3/details - 200 OK (92ms)
... (5 more similar requests)
12. GET /checkout - 200 OK (200ms)
13. GET /api/shipping/rates - 200 OK (1800ms)
14. POST /api/payment/validate - 200 OK (300ms)
15. GET https://cdn.stripe.com/v3/stripe.js - 200 OK (2500ms)
16. POST https://api.stripe.com/v1/tokens - 200 OK (450ms)
17. POST /api/orders/create - 200 OK (600ms)
18. GET /api/orders/456 - 200 OK (150ms)
19. GET /confirmation - 200 OK (180ms)
... (static resources)
```

### Analysis Report

```markdown
# Network Analysis Report

**Total Requests:** 23
**API Calls:** 14
**Static Resources:** 9
**Failed Requests:** 0
**Slow Requests (>1000ms):** 2

## Slow Requests (>1000ms)

- GET `https://cdn.stripe.com/v3/stripe.js` - 200 (2500ms)
- GET `/api/shipping/rates` - 200 (1800ms)

## Detected Patterns

- N+1 Query Pattern: 8 requests to `/api/cart/1/items/*` (consider batch endpoint)

## Issues Identified

- ⚠️ N+1 query for cart item details (8 sequential requests)
- ⚠️ Slow shipping rates API (1.8s)
- ⚠️ Slow Stripe.js load (2.5s from CDN)
- ℹ️ No errors, checkout successful

## Recommendations

1. Create batch endpoint: `GET /api/cart/items?ids=1,2,3` (eliminate N+1)
2. Cache shipping rates (or calculate client-side for standard addresses)
3. Preload Stripe.js on product page (async script tag)
4. Expected improvement: ~4s faster checkout flow
```

---

## Example 3: File Upload Workflow

### Workflow
User selects large file, uploads to server, waits for processing.

### Network Requests (6 total)

```
1. GET /upload - 200 OK (150ms)
2. POST /api/upload/presign - 200 OK (200ms)
   Response: {"uploadUrl": "https://s3.amazonaws.com/...", "key": "abc123"}
3. PUT https://s3.amazonaws.com/bucket/abc123 - 200 OK (8500ms)
   Headers: Content-Type: application/pdf, Content-Length: 15728640
4. POST /api/upload/confirm - 200 OK (300ms)
   Request: {"key": "abc123"}
5. GET /api/upload/abc123/status - 200 OK (100ms)
   Response: {"status": "processing"}
6. GET /api/upload/abc123/status - 200 OK (150ms)
   Response: {"status": "complete", "url": "https://..."}
```

### Analysis Report

```markdown
# Network Analysis Report

**Total Requests:** 6
**API Calls:** 5
**Static Resources:** 1
**Failed Requests:** 0
**Slow Requests (>1000ms):** 1

## Slow Requests (>1000ms)

- PUT `https://s3.amazonaws.com/bucket/abc123` - 200 (8500ms)

## Issues Identified

- ℹ️ Large file upload to S3 (15MB, 8.5s)
- ✅ Presigned URL pattern correctly implemented
- ✅ Polling for processing status (good)
- ℹ️ Direct S3 upload (bypasses app server, good)

## Recommendations

1. Add upload progress indicator (8.5s is noticeable)
2. Consider chunked uploads for files >10MB
3. Show processing status during polling
4. All patterns look correct, no issues detected
```

---

## Example 4: SPA Navigation (Single Page App)

### Workflow
User navigates between routes in React/Vue/Angular app.

### Network Requests (12 total)

```
1. GET / - 200 OK (180ms)
2. GET /assets/app.js - 200 OK (500ms)
3. GET /assets/app.css - 200 OK (200ms)
4. GET /api/user - 200 OK (150ms)
... (initial page load)

# User clicks "Products" link
5. GET /api/products - 200 OK (300ms)
6. GET /assets/chunks/products.chunk.js - 200 OK (180ms)

# User clicks product "123"
7. GET /api/products/123 - 200 OK (200ms)
8. GET /assets/chunks/product-detail.chunk.js - 200 OK (150ms)
9. GET /api/products/123/reviews - 200 OK (2200ms)
10. GET /api/products/123/related - 200 OK (400ms)

# User clicks "Account"
11. GET /api/account - 401 Unauthorized (50ms)
12. GET /login?redirect=/account - 200 OK (180ms)
```

### Analysis Report

```markdown
# Network Analysis Report

**Total Requests:** 12
**API Calls:** 7
**Static Resources:** 5
**Failed Requests:** 1
**Slow Requests (>1000ms):** 1

## Failed Requests

- GET `/api/account` - **401** (50ms)

## Slow Requests (>1000ms)

- GET `/api/products/123/reviews` - 200 (2200ms)

## Issues Identified

- ⚠️ Reviews API very slow (2.2s)
- ⚠️ Session expired (401 on /api/account)
- ✅ Code splitting working well (chunks loaded on demand)
- ✅ Lazy loading routes correctly

## Recommendations

1. Optimize reviews API query (2.2s is too slow)
   - Add pagination (limit reviews to first 10)
   - Cache reviews (low update frequency)
   - Consider lazy loading reviews (load after product details)
2. Fix session expiration handling
   - Implement token refresh
   - Show login modal instead of redirect
3. Preload related products (user likely to navigate)
```

---

## Example 5: Authentication Error Pattern

### Workflow
User attempts to access protected dashboard, redirected to login, logs in.

### Network Requests (15 total)

```
1. GET /dashboard - 302 Found (50ms)
   Location: /login?redirect=/dashboard
2. GET /login?redirect=/dashboard - 200 OK (180ms)
3. POST /api/auth/login - 200 OK (250ms)
   Response: {"token": "eyJ..."}
4. GET /dashboard - 200 OK (200ms)
5. GET /api/dashboard/widgets - 401 Unauthorized (45ms)
6. GET /api/dashboard/stats - 401 Unauthorized (40ms)
7. GET /api/dashboard/activity - 401 Unauthorized (42ms)
8. GET /login?redirect=/dashboard - 200 OK (180ms)
```

### Analysis Report

```markdown
# Network Analysis Report

**Total Requests:** 8
**API Calls:** 5
**Static Resources:** 3
**Failed Requests:** 3
**Slow Requests (>1000ms):** 0

## Failed Requests

- GET `/api/dashboard/widgets` - **401** (45ms)
- GET `/api/dashboard/stats` - **401** (40ms)
- GET `/api/dashboard/activity` - **401** (42ms)

## Detected Patterns

- Authentication Issues: 3 requests failed with 401 (check auth flow)

## Issues Identified

- ❌ Critical: Auth token not persisted after login
- ❌ Subsequent API calls missing Authorization header
- ❌ User stuck in login loop

## Recommendations

1. **Fix token storage** - Token returned by login but not saved
   - Check localStorage/sessionStorage/cookies
   - Verify token saved before redirect
2. **Add Authorization header** - API calls missing `Authorization: Bearer <token>`
   - Check HTTP client interceptor
   - Verify token retrieval from storage
3. **Test auth flow** - End-to-end test needed
   - Login → API call → Verify token included
4. **Expected fix:** Token persistence in client-side storage
```

---

## Example 6: CORS Error Pattern

### Workflow
Frontend app (app.example.com) calls API (api.example.com).

### Network Requests (5 total)

```
1. GET https://app.example.com/ - 200 OK (180ms)
2. GET https://app.example.com/assets/app.js - 200 OK (300ms)
3. OPTIONS https://api.example.com/data - 0 (CORS error)
4. GET https://api.example.com/data - 0 (blocked by CORS)
Console: "Access to fetch at 'https://api.example.com/data' from origin
'https://app.example.com' has been blocked by CORS policy"
```

### Analysis Report

```markdown
# Network Analysis Report

**Total Requests:** 4
**API Calls:** 2
**Static Resources:** 2
**Failed Requests:** 2
**Slow Requests (>1000ms):** 0

## Failed Requests

- OPTIONS `https://api.example.com/data` - **0** (CORS error)
- GET `https://api.example.com/data` - **0** (blocked)

## Console Messages

```
Access to fetch at 'https://api.example.com/data' from origin
'https://app.example.com' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the
requested resource.
```

## Issues Identified

- ❌ Critical: CORS policy blocking API requests
- ❌ Preflight OPTIONS request failing
- ❌ API server not configured for cross-origin requests

## Recommendations

1. **Server-side fix (backend):**
   ```
   Add CORS headers to API responses:
   Access-Control-Allow-Origin: https://app.example.com
   Access-Control-Allow-Methods: GET, POST, PUT, DELETE
   Access-Control-Allow-Headers: Content-Type, Authorization
   ```

2. **If credentials needed:**
   ```
   Access-Control-Allow-Credentials: true
   ```
   And client-side: `fetch(url, {credentials: 'include'})`

3. **Alternative solutions:**
   - Proxy API through same origin (app.example.com/api → api.example.com)
   - Use server-side API calls (no browser CORS)
   - Development: CORS browser extension (NOT for production)

4. **Verify:** Check browser Network tab for response headers after fix
```

---

## Summary of Common Issues

| Issue | Detection | Impact | Fix Complexity |
|-------|-----------|--------|----------------|
| **N+1 Queries** | Multiple similar URLs | High latency | Medium (API change) |
| **CORS Errors** | Status 0, console errors | Feature broken | Low (config) |
| **Auth Issues** | Multiple 401s | Broken features | Medium (token flow) |
| **Slow APIs** | >1s response time | Poor UX | High (optimization) |
| **Missing Resources** | 404s for CSS/JS | Broken UI | Low (fix paths) |
| **Third-party Delays** | External domain slow | Slow page load | Medium (async/defer) |
| **Rate Limiting** | 429 status | Blocked users | Medium (throttle/batch) |
