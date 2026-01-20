# Common Network Patterns and Issues

Reference guide for identifying common network issues and their signatures.

## N+1 Query Problem

### Signature
Multiple sequential API calls to similar endpoints with different IDs.

### Example
```
GET /api/products - 200 OK (150ms)
GET /api/products/1/details - 200 OK (80ms)
GET /api/products/2/details - 200 OK (85ms)
GET /api/products/3/details - 200 OK (90ms)
... (repeated 10+ times)
```

### Detection
- Base URL path repeated 5+ times with different IDs
- Sequential timing (one after another, not parallel)
- Total time = sum of individual requests

### Impact
- High latency (each request adds network roundtrip)
- Server load (many small requests vs one batch)
- Poor user experience (visible delay)

### Solutions
1. Batch API endpoint: `GET /api/products/details?ids=1,2,3`
2. Include details in initial response
3. GraphQL (request specific fields)
4. Server-side join/aggregation

## CORS (Cross-Origin Resource Sharing) Issues

### Signature
- Failed OPTIONS preflight requests (status 0 or 4xx)
- Console errors mentioning "CORS policy"
- Request made but response blocked by browser

### Example
```
OPTIONS /api/data - 0 (CORS error)
Console: "Access to fetch at 'https://api.example.com/data' from origin
'https://app.example.com' has been blocked by CORS policy"
```

### Detection
- Status code 0 (network error)
- Console messages contain "CORS"
- OPTIONS requests preceding failed GET/POST

### Impact
- API calls fail silently or with cryptic errors
- Features break in production but work in development
- Authentication cookies not sent

### Solutions
1. Server adds CORS headers: `Access-Control-Allow-Origin`
2. Enable credentials: `Access-Control-Allow-Credentials: true`
3. Proxy API through same origin
4. Use server-side API calls (no browser CORS)

## Authentication Flow Issues

### Signature
- Multiple 401 Unauthorized responses
- Redirects to login page during normal flow
- Missing authentication headers

### Example
```
POST /api/auth/login - 200 OK (200ms)
GET /api/user/profile - 401 Unauthorized (50ms)
GET /api/dashboard - 401 Unauthorized (45ms)
```

### Detection
- 3+ requests with 401 status
- Successful login followed by 401s
- Auth token not in subsequent requests

### Impact
- User sees login prompts unexpectedly
- Features fail after successful login
- Session expires too quickly

### Solutions
1. Check token storage (localStorage/cookies)
2. Verify token included in request headers
3. Refresh token flow implementation
4. Extend session timeout
5. Check cookie SameSite/Secure attributes

## CDN vs Origin Server Patterns

### Signature
- Same resource requested from different hosts
- Initial request slow, subsequent fast
- Cache-Control headers indicate caching strategy

### Example
```
GET /assets/logo.png - origin.example.com - 1200ms (cache miss)
GET /assets/logo.png - cdn.example.com - 50ms (cache hit)
```

### Detection
- Same path, different hostnames
- First request slow, later fast
- Response headers: `X-Cache: HIT` or `X-Cache: MISS`

### Impact
- Slow first page load (origin server)
- Inconsistent performance (cache hit/miss)
- Wasted bandwidth (origin serves static files)

### Solutions
1. Use CDN URLs consistently
2. Set appropriate Cache-Control headers
3. Pre-warm cache for critical resources
4. Use versioned URLs for cache busting

## Rate Limiting

### Signature
- 429 Too Many Requests responses
- Throttling after burst of requests
- Retry-After header in response

### Example
```
GET /api/search?q=test1 - 200 OK (100ms)
GET /api/search?q=test2 - 200 OK (95ms)
... (10 more requests)
GET /api/search?q=test13 - 429 Too Many Requests (50ms)
Headers: Retry-After: 60
```

### Detection
- 429 status codes
- Pattern of success → failures
- Rate limit headers (X-RateLimit-*)

### Impact
- API calls fail after threshold
- User blocked from feature
- Retry storms make it worse

### Solutions
1. Implement exponential backoff
2. Client-side request throttling
3. Request batching
4. Increase rate limits (if possible)
5. Add user feedback ("rate limited, try again in 60s")

## API Versioning Issues

### Signature
- Mixed API versions in same session
- Deprecated endpoint warnings
- Version mismatch errors

### Example
```
GET /api/v1/users - 200 OK (deprecated)
GET /api/v2/users - 200 OK (current)
GET /api/v1/products - 410 Gone (sunset)
```

### Detection
- Different version numbers in URLs
- 410 Gone or 404 for old endpoints
- Deprecation warnings in responses

### Impact
- Inconsistent data formats
- Breaking changes when version sunset
- Technical debt accumulation

### Solutions
1. Standardize on single API version
2. Migrate all endpoints to latest version
3. Version negotiation via headers
4. Monitor deprecation timelines

## Missing Resources (404s)

### Signature
- 404 Not Found for CSS/JS/images
- Broken functionality (missing JS libraries)
- Visual issues (missing CSS/fonts)

### Example
```
GET /assets/app.css - 200 OK
GET /assets/app.js - 404 Not Found
GET /assets/old-lib.js - 404 Not Found
```

### Detection
- 404s for static resources
- Console errors: "Failed to load resource"
- Functionality broken (missing JS)

### Impact
- Broken UI (missing CSS)
- JavaScript errors (missing libraries)
- Poor user experience

### Solutions
1. Fix broken URLs in HTML
2. Update paths after file moves
3. Check build/deployment process
4. Verify CDN/cache invalidation

## Slow Third-Party Resources

### Signature
- Long-running requests to external domains
- Blocking page render (sync scripts)
- Timeout errors for external APIs

### Example
```
GET /api/internal/data - 200 OK (150ms)
GET https://analytics.third-party.com/track - 200 OK (3500ms)
GET https://cdn.third-party.com/widget.js - Timeout (5000ms)
```

### Detection
- External domain requests >2s
- Different hostname than app
- Blocking page load

### Impact
- Slow page load (waiting for third-party)
- Single point of failure
- Privacy concerns (tracking)

### Solutions
1. Load third-party scripts async/defer
2. Use resource hints (dns-prefetch, preconnect)
3. Implement fallback/timeout
4. Self-host critical dependencies
5. Lazy load non-critical widgets

## WebSocket Connection Issues

### Signature
- WebSocket connection failed
- Fallback to polling (many GET requests)
- Connection drops and reconnects

### Example
```
WS wss://app.example.com/socket - 101 Switching Protocols (success)
... connection active ...
WS - Connection closed (network error)
GET /api/polling/messages - 200 OK (fallback to polling)
```

### Detection
- WebSocket upgrade failures
- Repeated short-lived connections
- Fallback to HTTP polling

### Impact
- Real-time features fail
- Excessive polling traffic
- Degraded user experience

### Solutions
1. Check WebSocket proxy configuration
2. Verify wss:// (secure WebSocket) support
3. Implement reconnection logic
4. Graceful fallback to polling
5. Monitor connection health

## Duplicate Requests

### Signature
- Identical requests sent multiple times
- Double form submissions
- Race conditions in client code

### Example
```
POST /api/orders - 200 OK (200ms)
POST /api/orders - 200 OK (205ms)  # Duplicate!
Result: Two orders created instead of one
```

### Detection
- Same URL, method, payload
- Timing close together (<500ms)
- Identical response bodies

### Impact
- Duplicate data (orders, payments, etc.)
- Wasted resources
- Data inconsistency

### Solutions
1. Disable submit button after click
2. Debounce client-side requests
3. Server-side idempotency keys
4. Request deduplication middleware
5. Optimistic locking (version numbers)
