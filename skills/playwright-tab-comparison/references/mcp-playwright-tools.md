# Playwright MCP Tools Reference

Quick reference for Playwright MCP browser automation tools used in multi-tab comparison workflows.

## Tab Management

### browser_tabs

List, create, close, or select browser tabs.

**Actions:**
- `list` - Show all open tabs with indices
- `new` - Create a new tab
- `close` - Close tab at index (current if omitted)
- `select` - Switch to tab at index

**Examples:**
```python
# List all tabs
browser_tabs(action="list")

# Create new tab
browser_tabs(action="new")

# Switch to tab 2
browser_tabs(action="select", index=1)  # 0-indexed

# Close tab 3
browser_tabs(action="close", index=2)
```

## Navigation

### browser_navigate

Navigate to URL or go forward/back in history.

**Parameters:**
- `url` - URL to navigate to or "forward"/"back"

**Examples:**
```python
browser_navigate(url="https://example.com")
browser_navigate(url="back")
```

## Content Capture

### browser_snapshot

Capture accessibility snapshot of current page (better than screenshot for content analysis).

**Optional Parameters:**
- `filename` - Save to markdown file instead of returning

**Examples:**
```python
# Return snapshot in response
browser_snapshot()

# Save to file
browser_snapshot(filename="page-snapshot.md")
```

### browser_take_screenshot

Take screenshot of current page or specific element.

**Parameters:**
- `filename` - Output filename (default: page-{timestamp}.png)
- `type` - Image format: "png" or "jpeg" (default: png)
- `fullPage` - Capture full scrollable page (default: false)
- `element` - Human-readable element description (requires ref)
- `ref` - Element reference from snapshot (requires element)

**Examples:**
```python
# Screenshot viewport
browser_take_screenshot(filename="page1.png")

# Screenshot full page
browser_take_screenshot(filename="full-page.png", fullPage=True)

# Screenshot specific element
browser_take_screenshot(
    filename="header.png",
    element="page header",
    ref="ref_1"
)
```

## Data Extraction

### browser_evaluate

Execute JavaScript to extract data from page.

**Parameters:**
- `function` - JavaScript function to execute
- `element` - Human-readable element description (optional)
- `ref` - Element reference from snapshot (optional)

**Examples:**
```python
# Extract page data
browser_evaluate(function="() => { return { title: document.title, url: window.location.href }; }")

# Extract from element
browser_evaluate(
    function="(element) => { return element.textContent; }",
    element="product price",
    ref="ref_5"
)
```

## Network Monitoring

### browser_network_requests

Get all network requests since page load.

**Parameters:**
- `includeStatic` - Include images, fonts, scripts (default: false)

**Examples:**
```python
# Get API calls only
browser_network_requests()

# Include all resources
browser_network_requests(includeStatic=True)
```

## Workflow Pattern

**Standard multi-tab comparison pattern:**

1. List existing tabs
2. Create additional tabs as needed
3. For each tab:
   - Select tab
   - Navigate to URL
   - Wait for page load
   - Capture snapshot
   - Extract data via evaluate
   - Take screenshot
4. Compare results
5. Generate report
