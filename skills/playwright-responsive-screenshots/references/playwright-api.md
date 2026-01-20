# Playwright MCP Tool Reference

Quick reference for Playwright MCP tools used in responsive screenshot workflows.

## Core Tools for Screenshot Workflows

### browser_navigate

Navigate to a URL and wait for page load.

**Signature:**
```typescript
browser_navigate({
  url: string  // The URL to navigate to (required)
})
```

**Examples:**
```typescript
browser_navigate({ url: "https://example.com" })
browser_navigate({ url: "https://shop.com/products" })
browser_navigate({ url: "http://localhost:3000/dashboard" })
```

**Success Response:**
- Page loads successfully
- DOM ready for interaction

**Error Scenarios:**
- Network timeout (default 30s)
- DNS resolution failure
- Server error (404, 500, etc.)
- SSL certificate issues

**Best Practices:**
- Always verify navigation success before proceeding
- Handle errors gracefully (don't attempt screenshots on failed navigation)
- Use full URLs with protocol (https:// or http://)

---

### browser_resize

Resize the browser window to specified viewport dimensions.

**Signature:**
```typescript
browser_resize({
  width: number,   // Viewport width in pixels (required)
  height: number   // Viewport height in pixels (required)
})
```

**Examples:**
```typescript
// Mobile
browser_resize({ width: 375, height: 667 })

// Tablet
browser_resize({ width: 768, height: 1024 })

// Desktop
browser_resize({ width: 1920, height: 1080 })

// Custom ultra-wide
browser_resize({ width: 3440, height: 1440 })
```

**Valid Ranges:**
- Width: 200-3840 pixels
- Height: 200-2160 pixels

**Important Notes:**
- Resizing triggers layout reflow
- **Always wait after resize** before screenshot (minimum 1s)
- Viewport dimensions ≠ window dimensions (no browser chrome included)
- Retina displays use device pixel ratio (2x on MacBook)

**Common Mistakes:**
- Not waiting after resize (captures mid-reflow)
- Using unreasonable dimensions (50×50 or 10000×10000)
- Forgetting height parameter

---

### browser_wait_for

Wait for a specified time or condition before proceeding.

**Signature:**
```typescript
browser_wait_for({
  time?: number,      // Wait duration in seconds
  text?: string,      // Wait for text to appear
  textGone?: string   // Wait for text to disappear
})
```

**Examples:**
```typescript
// Time-based wait (most common for layout settling)
browser_wait_for({ time: 1 })      // 1 second
browser_wait_for({ time: 2.5 })    // 2.5 seconds

// Condition-based wait
browser_wait_for({ text: "Loading complete" })
browser_wait_for({ textGone: "Loading..." })
```

**Wait Time Guidelines:**

| Page Type | Recommended Wait |
|-----------|------------------|
| Static HTML | 500ms - 1s |
| Standard SPA | 1-2s |
| Heavy animations | 2-3s |
| Complex dashboards | 3-5s |

**Best Practices:**
- **Always wait after resize** (minimum 1s)
- Use condition-based waits for dynamic content
- Avoid excessive waits (>5s) - indicates page issues
- Consider page complexity when setting wait time

**Common Scenarios:**
```typescript
// After navigation
browser_navigate({ url: "https://example.com" })
browser_wait_for({ time: 1 })  // Initial page load

// After resize (critical for screenshots)
browser_resize({ width: 375, height: 667 })
browser_wait_for({ time: 1 })  // Layout reflow

// For SPAs with loading states
browser_navigate({ url: "https://spa.app" })
browser_wait_for({ textGone: "Loading..." })  // Wait for spinner
```

---

### browser_take_screenshot

Capture a screenshot of the current page.

**Signature:**
```typescript
browser_take_screenshot({
  filename?: string,     // Output filename (optional)
  fullPage?: boolean,    // Capture full scrollable page (default: false)
  type?: "png" | "jpeg"  // Image format (default: "png")
})
```

**Examples:**
```typescript
// Full-page PNG (recommended for UI testing)
browser_take_screenshot({
  filename: "homepage-mobile.png",
  fullPage: true
})

// Viewport-only screenshot
browser_take_screenshot({
  filename: "above-fold.png",
  fullPage: false
})

// JPEG format (smaller file size)
browser_take_screenshot({
  filename: "photo-gallery.jpg",
  fullPage: true,
  type: "jpeg"
})

// Auto-generated filename
browser_take_screenshot({ fullPage: true })
// → page-1734712345.png
```

**Parameters:**

**filename (optional):**
- Defaults to `page-{timestamp}.{ext}` if omitted
- Can be absolute or relative path
- Extension determined by `type` parameter

**fullPage (boolean):**
- `true`: Captures entire scrollable page (recommended for responsive testing)
- `false`: Captures only visible viewport (useful for above-fold testing)
- Default: `false`

**type ("png" | "jpeg"):**
- `"png"`: Lossless, good for UI (recommended)
- `"jpeg"`: Lossy compression, smaller file size (good for photo-heavy pages)
- Default: `"png"`

**File Sizes (approximate):**
- Mobile PNG: 100-300KB
- Tablet PNG: 300-700KB
- Desktop PNG: 800KB-2MB
- JPEG: ~50% smaller than PNG

**Best Practices:**
- **Always use `fullPage: true`** for responsive testing (unless specifically testing above-fold)
- Use descriptive filenames: `{page-name}-{breakpoint}.png`
- PNG for UI screenshots, JPEG for photo-heavy pages
- Wait after resize before screenshot

**Common Mistakes:**
- Forgetting `fullPage: true` (captures only viewport)
- Not waiting after resize (captures mid-animation)
- Inconsistent file naming (hard to identify screenshots)

---

## Complete Responsive Screenshot Workflow

**Standard pattern for single page, standard breakpoints:**

```typescript
// 1. Navigate to page
browser_navigate({ url: "https://example.com" })

// 2. Mobile breakpoint
browser_resize({ width: 375, height: 667 })
browser_wait_for({ time: 1 })
browser_take_screenshot({
  filename: "example-mobile.png",
  fullPage: true
})

// 3. Tablet breakpoint
browser_resize({ width: 768, height: 1024 })
browser_wait_for({ time: 1 })
browser_take_screenshot({
  filename: "example-tablet.png",
  fullPage: true
})

// 4. Desktop breakpoint
browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 1 })
browser_take_screenshot({
  filename: "example-desktop.png",
  fullPage: true
})
```

**Result:** 3 screenshots at standard breakpoints with proper layout settling.

---

## Error Handling Patterns

### Navigation Failure

```typescript
try {
  browser_navigate({ url: "https://broken-site.com" })
} catch (error) {
  // Report: Navigation failed, cannot proceed with screenshots
  // Do not attempt resize/screenshot
}
```

### Invalid Viewport Dimensions

```typescript
// Validate before calling browser_resize
function validateDimensions(width: number, height: number): boolean {
  const valid =
    width >= 200 && width <= 3840 &&
    height >= 200 && height <= 2160;

  if (!valid) {
    console.error(`Invalid dimensions: ${width}×${height}`);
    console.error("Valid range: 200-3840 width, 200-2160 height");
  }

  return valid;
}
```

### Screenshot Capture Failure

```typescript
// If screenshot fails, report which breakpoint failed
browser_take_screenshot({ filename: "page-mobile.png", fullPage: true })
  .catch(error => {
    console.error("Mobile screenshot failed:", error);
    // Continue with other breakpoints or abort
  });
```

---

## Performance Optimization

### Minimize Navigation

**Bad (inefficient):**
```typescript
// Re-navigates for each breakpoint (wasteful)
browser_navigate({ url: "https://example.com" })
browser_resize({ width: 375, height: 667 })
browser_take_screenshot({ filename: "mobile.png", fullPage: true })

browser_navigate({ url: "https://example.com" })  // ❌ Unnecessary
browser_resize({ width: 1920, height: 1080 })
browser_take_screenshot({ filename: "desktop.png", fullPage: true })
```

**Good (efficient):**
```typescript
// Navigate once, resize multiple times
browser_navigate({ url: "https://example.com" })

browser_resize({ width: 375, height: 667 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "mobile.png", fullPage: true })

browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "desktop.png", fullPage: true })
```

### Adjust Wait Times

**Static pages:**
```typescript
browser_wait_for({ time: 0.5 })  // 500ms sufficient
```

**Standard SPAs:**
```typescript
browser_wait_for({ time: 1 })  // 1s recommended
```

**Heavy animations:**
```typescript
browser_wait_for({ time: 3 })  // 3s for complex transitions
```

---

## Additional Playwright MCP Tools

These tools may be useful for advanced screenshot workflows:

### browser_snapshot

Capture accessibility tree snapshot (alternative to visual screenshot).

```typescript
browser_snapshot({
  filename?: string  // Save to markdown file
})
```

**Use case:** Testing accessibility structure across breakpoints.

### browser_console_messages

Read console logs for debugging layout issues.

```typescript
browser_console_messages({
  pattern?: string,     // Regex filter
  onlyErrors?: boolean  // Only show errors
})
```

**Use case:** Detect CSS warnings or JavaScript errors at specific breakpoints.

### browser_network_requests

Monitor network requests during screenshot capture.

```typescript
browser_network_requests({
  urlPattern?: string  // Filter requests
})
```

**Use case:** Verify responsive images load correctly at different viewport sizes.

---

## Summary Checklist

For each screenshot capture:

- [ ] Navigate to target URL
- [ ] Resize to target viewport
- [ ] **Wait minimum 1 second** after resize
- [ ] Capture with `fullPage: true`
- [ ] Use descriptive filename with breakpoint identifier
- [ ] Handle errors gracefully
- [ ] Report file paths to user

For multiple breakpoints:

- [ ] Navigate **once** per page
- [ ] Loop through breakpoints (resize/wait/capture)
- [ ] Organize files with consistent naming
- [ ] Validate all screenshots captured successfully
