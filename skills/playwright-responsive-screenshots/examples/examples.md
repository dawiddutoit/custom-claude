# Responsive Screenshot Examples

Comprehensive examples demonstrating various screenshot capture scenarios.

## Example 1: Standard Breakpoints - Single Page

**User Request:**
```
Capture responsive screenshots of https://example.com
```

**Workflow:**
1. Navigate to https://example.com
2. Resize to 375×667 (mobile), wait 1s, screenshot → `example-mobile.png`
3. Resize to 768×1024 (tablet), wait 1s, screenshot → `example-tablet.png`
4. Resize to 1920×1080 (desktop), wait 1s, screenshot → `example-desktop.png`

**Tool Calls:**
```
browser_navigate({ url: "https://example.com" })
browser_resize({ width: 375, height: 667 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "example-mobile.png", fullPage: true })
browser_resize({ width: 768, height: 1024 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "example-tablet.png", fullPage: true })
browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "example-desktop.png", fullPage: true })
```

**Output:**
```
✅ Captured 3 screenshots:
  - example-mobile.png (375×667)
  - example-tablet.png (768×1024)
  - example-desktop.png (1920×1080)
```

---

## Example 2: Custom Breakpoints - Specific Devices

**User Request:**
```
Screenshot https://app.dev at iPhone 14 Pro (393×852) and Samsung Galaxy S23 (360×780)
```

**Workflow:**
1. Navigate to https://app.dev
2. Resize to 393×852, wait 1s, screenshot → `app-iphone14pro.png`
3. Resize to 360×780, wait 1s, screenshot → `app-galaxys23.png`

**Tool Calls:**
```
browser_navigate({ url: "https://app.dev" })
browser_resize({ width: 393, height: 852 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "app-iphone14pro.png", fullPage: true })
browser_resize({ width: 360, height: 780 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "app-galaxys23.png", fullPage: true })
```

**Output:**
```
✅ Captured 2 screenshots:
  - app-iphone14pro.png (393×852)
  - app-galaxys23.png (360×780)
```

---

## Example 3: Multiple Pages - Standard Breakpoints

**User Request:**
```
Capture responsive screenshots for /home, /products, and /checkout on https://shop.com
```

**Workflow:**
For each page:
1. Navigate to page
2. Capture at mobile, tablet, desktop breakpoints

**Tool Calls:**
```
# Page 1: /home
browser_navigate({ url: "https://shop.com/home" })
browser_resize({ width: 375, height: 667 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "home-mobile.png", fullPage: true })
browser_resize({ width: 768, height: 1024 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "home-tablet.png", fullPage: true })
browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "home-desktop.png", fullPage: true })

# Page 2: /products
browser_navigate({ url: "https://shop.com/products" })
browser_resize({ width: 375, height: 667 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "products-mobile.png", fullPage: true })
browser_resize({ width: 768, height: 1024 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "products-tablet.png", fullPage: true })
browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "products-desktop.png", fullPage: true })

# Page 3: /checkout
browser_navigate({ url: "https://shop.com/checkout" })
browser_resize({ width: 375, height: 667 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "checkout-mobile.png", fullPage: true })
browser_resize({ width: 768, height: 1024 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "checkout-tablet.png", fullPage: true })
browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "checkout-desktop.png", fullPage: true })
```

**Output:**
```
✅ Captured 9 screenshots (3 pages × 3 breakpoints):
  - home-mobile.png, home-tablet.png, home-desktop.png
  - products-mobile.png, products-tablet.png, products-desktop.png
  - checkout-mobile.png, checkout-tablet.png, checkout-desktop.png
```

---

## Example 4: With Comparison Report

**User Request:**
```
Screenshot https://portfolio.dev at mobile and desktop, then create a comparison report
```

**Workflow:**
1. Capture screenshots at breakpoints
2. Generate markdown report with embedded images

**Report Content (report.md):**
```markdown
# Responsive Screenshot Report

**Date:** 2025-12-20 14:23:15
**URL:** https://portfolio.dev
**Breakpoints:** mobile (375×667), desktop (1920×1080)

## Screenshot Comparison

| Breakpoint | Screenshot | Dimensions |
|------------|------------|------------|
| Mobile | ![Mobile view](portfolio-mobile.png) | 375 × 667 |
| Desktop | ![Desktop view](portfolio-desktop.png) | 1920 × 1080 |

## Notes
- Mobile navigation collapses to hamburger menu
- Desktop shows full navigation bar
- Hero image scales appropriately across breakpoints
```

**Output:**
```
✅ Captured 2 screenshots with comparison report:
  - portfolio-mobile.png (375×667)
  - portfolio-desktop.png (1920×1080)
  - report.md

View report.md for side-by-side comparison.
```

---

## Example 5: Edge Case - Ultra-Wide Desktop

**User Request:**
```
Test https://dashboard.app at ultra-wide resolution (3440×1440)
```

**Workflow:**
1. Navigate to https://dashboard.app
2. Resize to 3440×1440 (21:9 ultra-wide)
3. Wait 1s for layout reflow
4. Capture full-page screenshot

**Tool Calls:**
```
browser_navigate({ url: "https://dashboard.app" })
browser_resize({ width: 3440, height: 1440 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "dashboard-ultrawide.png", fullPage: true })
```

**Output:**
```
✅ Captured 1 screenshot:
  - dashboard-ultrawide.png (3440×1440, ultra-wide 21:9)
```

---

## Example 6: Mobile Landscape Orientation

**User Request:**
```
Capture https://game.io in mobile landscape (667×375)
```

**Workflow:**
1. Navigate to https://game.io
2. Resize to landscape dimensions (width > height)
3. Screenshot landscape view

**Tool Calls:**
```
browser_navigate({ url: "https://game.io" })
browser_resize({ width: 667, height: 375 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "game-mobile-landscape.png", fullPage: true })
```

**Output:**
```
✅ Captured 1 screenshot:
  - game-mobile-landscape.png (667×375, mobile landscape)
```

---

## Example 7: SPA with Animation - Extended Wait

**User Request:**
```
Screenshot https://animated-spa.com - page has loading animations
```

**Workflow:**
1. Navigate and wait for initial page load
2. Resize to breakpoint
3. **Extended wait (2-3s)** for animations to complete
4. Capture screenshot

**Tool Calls:**
```
browser_navigate({ url: "https://animated-spa.com" })
browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 3 })  # Extended wait for animations
browser_take_screenshot({ filename: "spa-desktop.png", fullPage: true })
```

**Note:** Adjust wait time based on page complexity:
- Static sites: 500ms-1s
- Standard SPAs: 1-2s
- Heavy animations: 2-3s

---

## Example 8: Validation Failure - Invalid Dimensions

**User Request:**
```
Screenshot https://example.com at 50×50
```

**Response:**
```
❌ Invalid viewport dimensions: 50×50

Viewport dimensions must be:
  - Width: 200-3840 pixels
  - Height: 200-2160 pixels

Requested: 50×50 (too small)
Recommendation: Use minimum 200×200 or standard mobile breakpoint (375×667)
```

**Action:** Reject invalid dimensions, suggest valid alternatives.

---

## Example 9: Batch Capture - Design System Validation

**User Request:**
```
Validate our design system components at all standard breakpoints:
- https://design.system/buttons
- https://design.system/forms
- https://design.system/navigation
```

**Workflow:**
Nested loops: pages × breakpoints

**Output:**
```
✅ Captured 9 screenshots for design system validation:

Buttons:
  - buttons-mobile.png (375×667)
  - buttons-tablet.png (768×1024)
  - buttons-desktop.png (1920×1080)

Forms:
  - forms-mobile.png (375×667)
  - forms-tablet.png (768×1024)
  - forms-desktop.png (1920×1080)

Navigation:
  - navigation-mobile.png (375×667)
  - navigation-tablet.png (768×1024)
  - navigation-desktop.png (1920×1080)

All components validated across breakpoints.
```

---

## Example 10: Viewport-Only Screenshot (Not Full Page)

**User Request:**
```
Capture just the visible viewport of https://longpage.com at desktop size (no scrolling)
```

**Workflow:**
1. Navigate to page
2. Resize to desktop
3. Capture with `fullPage: false` (viewport only)

**Tool Calls:**
```
browser_navigate({ url: "https://longpage.com" })
browser_resize({ width: 1920, height: 1080 })
browser_wait_for({ time: 1 })
browser_take_screenshot({ filename: "longpage-viewport-only.png", fullPage: false })
```

**Note:** Default is `fullPage: true`. Use `fullPage: false` only when specifically requested.

---

## Summary of Patterns

| Pattern | Use Case | Key Considerations |
|---------|----------|-------------------|
| **Standard breakpoints** | General responsive testing | Use 375×667, 768×1024, 1920×1080 |
| **Custom devices** | Specific device validation | Validate dimensions, use descriptive names |
| **Multiple pages** | Site-wide testing | Nested loops, consistent naming |
| **Comparison report** | Design review documentation | Markdown tables with embedded images |
| **Ultra-wide** | Edge case testing | Up to 3840×2160 maximum |
| **Landscape** | Mobile games/video apps | Width > height orientation |
| **Extended wait** | SPAs with animations | 2-3s wait for complex pages |
| **Viewport-only** | Above-fold testing | `fullPage: false` parameter |
