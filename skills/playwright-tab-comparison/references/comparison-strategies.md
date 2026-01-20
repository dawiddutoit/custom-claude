# Comparison Strategies

Different strategies for comparing pages depending on the use case.

## Visual Comparison

Compare visual appearance using screenshots.

**Use when:**
- Testing responsive design across breakpoints
- Comparing styling changes
- Verifying cross-browser rendering
- A/B testing visual variants

**Approach:**
1. Capture full-page screenshots from each tab
2. Use same viewport size for consistency
3. Compare side-by-side in HTML report
4. Note visual differences manually or programmatically

**Limitations:**
- Cannot detect functional differences
- Timing-dependent (animations, loading states)
- Requires consistent viewport and state

## Content Comparison

Compare page content and structure using snapshots.

**Use when:**
- Verifying content parity across environments
- Checking data consistency
- Testing content updates
- Comparing localized versions

**Approach:**
1. Capture accessibility snapshots
2. Extract text content via evaluate
3. Compare element counts and structure
4. Identify missing/added content

**Key metrics:**
- Element count differences
- Text content changes
- Heading hierarchy
- Link counts and targets

## Behavioral Comparison

Compare page behavior and interactions.

**Use when:**
- Testing feature flags
- Comparing staging vs production functionality
- Validating form behavior
- Testing interactive elements

**Approach:**
1. Execute same interaction sequence on each tab
2. Capture network requests during interaction
3. Compare API responses
4. Verify expected outcomes

**What to compare:**
- Network request patterns
- API response data
- Console messages
- State changes

## Performance Comparison

Compare page performance metrics.

**Use when:**
- Testing optimization changes
- Comparing different implementations
- Measuring CDN impact
- Evaluating third-party scripts

**Approach:**
1. Capture network requests with timing
2. Measure page load events via evaluate
3. Compare resource counts and sizes
4. Identify performance bottlenecks

**Key metrics:**
- Total resource size
- Request count
- Load time (DOMContentLoaded, load events)
- Largest Contentful Paint (LCP)

## Data Extraction Comparison

Compare structured data extracted from pages.

**Use when:**
- Verifying product catalogs
- Comparing pricing across regions
- Testing search results
- Validating data migrations

**Approach:**
1. Define extraction script (evaluate function)
2. Run same script on each tab
3. Save extracted JSON data
4. Compare data structures and values

**Example extraction:**
```javascript
() => {
    return {
        products: Array.from(document.querySelectorAll('.product')).map(p => ({
            name: p.querySelector('.name')?.textContent,
            price: p.querySelector('.price')?.textContent,
            inStock: p.querySelector('.stock')?.textContent
        }))
    };
}
```

## Hybrid Comparison

Combine multiple strategies for comprehensive comparison.

**Example workflow:**
1. Visual: Capture screenshots for reference
2. Content: Snapshot for structure comparison
3. Data: Extract specific metrics via evaluate
4. Behavioral: Compare network patterns

**Report includes:**
- Side-by-side screenshots
- Structural differences
- Data comparison tables
- Network request analysis

## Choosing a Strategy

| Use Case | Strategy | Tools |
|----------|----------|-------|
| Design consistency | Visual | Screenshots |
| Content updates | Content | Snapshots |
| Feature testing | Behavioral | Network + evaluate |
| Performance optimization | Performance | Network timing |
| Data validation | Data extraction | Evaluate |
| Comprehensive QA | Hybrid | All tools |
