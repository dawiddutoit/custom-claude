# Date-Aware WebSearch Patterns

Strategies for finding recent, relevant information using WebSearch with proper date awareness.

---

## Core Principle: Use Current Year from Environment

**CRITICAL:** Always check `<env>` for "Today's date" and use that year in searches.

**Example:**
- If `<env>` shows "Today's date: 2025-10-16"
- Use `2025` in search queries, NOT `2024` or older years

**Why this matters:**
- Ensures you get the most recent information
- Avoids outdated comparisons and benchmarks
- Captures latest security issues and releases

---

## Date-Aware Search Patterns

### Pattern 1: Explicit Year in Query

**Format:** `{topic} {CURRENT_YEAR}`

**Examples:**
```
neo4j vs memgraph 2025
pydantic v2 performance 2025
fastapi best practices 2025
python type hints 2025
```

**When to use:**
- Always, for any library research
- Especially for fast-moving technologies
- When looking for current best practices

**What you'll find:**
- Most recent articles, blog posts, discussions
- Latest benchmarks and comparisons
- Current community sentiment

---

### Pattern 2: "Latest" or "Recent" Modifiers

**Format:** `{topic} latest` or `{topic} recent`

**Examples:**
```
neo4j latest release
pydantic recent changes
fastapi latest version features
python typing recent improvements
```

**When to use:**
- When looking for release information
- When you want cutting-edge updates
- When year alone might not be specific enough

**What you'll find:**
- Recent release notes
- Latest changelog entries
- Breaking changes announcements

---

### Pattern 3: Time Window Searches

**Format:** `{topic} last {N} months`

**Examples:**
```
neo4j updates last 6 months
pydantic breaking changes last 3 months
fastapi security issues last year
python asyncio improvements last 12 months
```

**When to use:**
- When you need a specific time window
- For release cadence analysis
- For security vulnerability tracking

**What you'll find:**
- Time-bounded updates
- Recent trends and patterns
- Activity level indicators

---

## Search Patterns by Research Dimension

### Dimension 1: Official Documentation
**Goal:** Current API, features, capabilities

```
{library} documentation {YEAR}
{library} official guide {YEAR}
{library} api reference {YEAR}
{library} getting started {YEAR}
```

**Date strategy:** Use current year to find latest docs versions

---

### Dimension 2: Recent Developments
**Goal:** Release history, momentum, roadmap

```
{library} changelog {YEAR}
{library} release notes {YEAR}
{library} roadmap {YEAR}
{library} latest release
{library} breaking changes {YEAR}
{library} deprecations {YEAR}
{library} updates last 6 months
```

**Date strategy:**
- Use current year for releases
- Use "last 6 months" for activity window

---

### Dimension 3: Alternatives & Comparisons
**Goal:** Current competitive landscape

```
best {category} {YEAR}
{library} vs {alternative} {YEAR}
{library} vs {alternative} benchmark {YEAR}
{library} vs {alternative} comparison {YEAR}
{library} alternatives {YEAR}
{category} comparison {YEAR}
```

**Date strategy:** ALWAYS use current year for comparisons

**Why:** Technology landscape changes rapidly. A 2023 comparison is outdated in 2025.

**Trusted sources to prioritize:**
- db-engines.com (database rankings)
- github.com (activity, stars, forks)
- Independent benchmarks (not vendor marketing)

---

### Dimension 4: Security
**Goal:** Recent vulnerabilities, patches, security posture

```
{library} CVE {YEAR}
{library} vulnerability {YEAR}
{library} security advisory {YEAR}
{library} security patch {YEAR}
{library} CVE site:nvd.nist.gov
{library} security site:snyk.io
{library} advisory site:github.com
```

**Date strategy:**
- Use current year to find recent CVEs
- Use "last 12 months" for security trends
- Check both current year and previous year

**Critical sources:**
- nvd.nist.gov (official CVE database)
- snyk.io (vulnerability tracking)
- github.com/advisories (GitHub security advisories)

---

### Dimension 5: Community Health
**Goal:** Recent experiences, current sentiment, active discussions

```
{library} experiences {YEAR} site:reddit.com
{library} discussion {YEAR} site:news.ycombinator.com
{library} problems {YEAR} site:stackoverflow.com
{library} issues {YEAR} site:github.com
{library} adoption trends {YEAR}
{library} production experience {YEAR}
```

**Date strategy:** Use current year to capture recent sentiment

**Trusted community sources:**
- reddit.com/r/programming, /r/python, /r/webdev, etc.
- news.ycombinator.com (HN)
- stackoverflow.com
- github.com (issues, discussions)

**What to look for:**
- Common gotchas and pain points
- Real production experiences
- Response time to issues
- Community sentiment (positive/negative/neutral)

---

### Dimension 6: Adoption & Trends
**Goal:** Current usage patterns, growing/declining

```
{library} adoption {YEAR}
{library} popularity {YEAR}
{library} usage stats {YEAR}
{library} trends {YEAR}
{library} market share {YEAR}
```

**Date strategy:** Use current year for adoption data

**What to look for:**
- GitHub star growth rate
- Package download statistics
- Job posting trends
- Conference talk mentions

---

## Advanced Search Techniques

### Site-Specific Searches

Use `site:` to target trusted sources:

```
{library} site:github.com
{library} CVE site:nvd.nist.gov
{library} vulnerability site:snyk.io
{library} discussion site:news.ycombinator.com
{library} experience site:reddit.com
```

### Excluding Marketing Fluff

Use `-site:` to exclude marketing:

```
{library} comparison 2025 -site:vendor.com
{library} vs {alternative} 2025 -site:marketing.com
```

### Finding Benchmarks

```
{library} benchmark {YEAR}
{library} performance {YEAR}
{library} speed test {YEAR}
{library} vs {alternative} benchmark {YEAR}
```

Look for:
- Independent benchmarks (not vendor-run)
- Reproducible methodology
- Recent data (use current year)

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Using Outdated Years
```
neo4j vs memgraph 2023  // BAD if we're in 2025
```

**Fix:** Always use current year from `<env>`
```
neo4j vs memgraph 2025  // GOOD
```

---

### ❌ Mistake 2: No Date Qualifier
```
python asyncio best practices  // Might return 2018 results
```

**Fix:** Add current year
```
python asyncio best practices 2025  // Gets recent content
```

---

### ❌ Mistake 3: Trusting Vendor Marketing
```
{library} best features  // Finds marketing pages
```

**Fix:** Search for community experiences
```
{library} experiences 2025 site:reddit.com  // Real user feedback
```

---

### ❌ Mistake 4: Ignoring Security Recency
```
{library} security  // Might miss recent CVEs
```

**Fix:** Add time constraint
```
{library} CVE 2025
{library} security advisory last 12 months
```

---

## Date Strategy by Content Type

### Blog Posts & Articles
- **Strategy:** Use current year
- **Example:** `fastapi tutorial 2025`
- **Why:** Technologies evolve, old tutorials become outdated

### Release Notes
- **Strategy:** "latest release" or current year
- **Example:** `pydantic latest release` or `pydantic release notes 2025`
- **Why:** Need most recent version information

### Benchmarks
- **Strategy:** ALWAYS use current year
- **Example:** `neo4j vs memgraph benchmark 2025`
- **Why:** Performance characteristics change with versions

### Security
- **Strategy:** Current year + previous year
- **Example:** `fastapi CVE 2025`, `fastapi CVE 2024`
- **Why:** CVEs are time-sensitive, need recent data

### Community Discussion
- **Strategy:** Use current year, optionally "last 6 months"
- **Example:** `react vs vue 2025 site:reddit.com`
- **Why:** Community sentiment shifts over time

---

## WebSearch Quality Checklist

Before trusting search results:

- [ ] Used current year from `<env>` in search query?
- [ ] Checked multiple sources (not just vendor sites)?
- [ ] Verified publication date of articles/posts?
- [ ] Cross-referenced community discussions?
- [ ] Looked for independent benchmarks?
- [ ] Checked security sources (NVD, Snyk, GitHub)?
- [ ] Avoided pure marketing content?
- [ ] Found real user experiences (Reddit, HN)?

---

## Example Research Flow

### Researching "Pydantic v2" in 2025

**Step 1: Get Current Year from `<env>`**
```
Check <env> → Today's date: 2025-10-16 → Use 2025
```

**Step 2: Official Documentation**
```
pydantic v2 documentation 2025
pydantic v2 migration guide 2025
```

**Step 3: Recent Developments**
```
pydantic v2 latest release
pydantic v2 changelog 2025
pydantic v2 breaking changes 2025
```

**Step 4: Comparisons**
```
pydantic v2 vs v1 benchmark 2025
pydantic v2 vs marshmallow 2025
data validation libraries python 2025
```

**Step 5: Security**
```
pydantic CVE 2025
pydantic security advisory 2025 site:github.com
pydantic vulnerability 2024
```

**Step 6: Community**
```
pydantic v2 experiences 2025 site:reddit.com
pydantic v2 discussion 2025 site:news.ycombinator.com
pydantic v2 issues 2025 site:github.com
```

**Result:** Comprehensive, up-to-date research using current year

---

## Pro Tips

### Tip 1: Check Result Dates
After getting search results, verify the publish date of articles. Discard anything older than 12-18 months for fast-moving tech.

### Tip 2: Look for "Updated" Timestamps
Some articles are updated over time. Look for "Last updated: {date}" indicators.

### Tip 3: Use GitHub for Freshness
GitHub activity (commits, releases, issues) is always dated. Use it to verify recency.

### Tip 4: Cross-Reference Community
If official docs say one thing but Reddit/HN say another, investigate further. Community often reveals gotchas.

### Tip 5: Prioritize Primary Sources
Official docs > Independent benchmarks > Community discussion > Marketing

---

## Environment Date Extraction

When the skill is invoked, always:

1. Check `<env>` tag for "Today's date"
2. Extract current year
3. Use that year in ALL WebSearch queries
4. Document what year was used in research report

**Example `<env>` tag:**
```
<env>
Today's date: 2025-10-16
</env>
```

**Extracted year:** `2025`
**Use in searches:** `{library} {topic} 2025`

---

## Time-Sensitivity by Topic

| Topic | Time Sensitivity | Recommended Strategy |
|-------|------------------|---------------------|
| API Documentation | Medium | Current year |
| Release Notes | High | "latest" or current year |
| Benchmarks | High | ALWAYS current year |
| Security (CVEs) | Critical | Current + previous year |
| Community Sentiment | High | Current year + "last 6 months" |
| Architecture Patterns | Low-Medium | Current year preferred |
| Best Practices | Medium | Current year |
| Tool Comparisons | High | ALWAYS current year |

---

## Validation

After completing research, verify:

- [ ] All WebSearch queries used current year from `<env>`
- [ ] No outdated comparisons (>18 months old)
- [ ] Security data is from last 12-24 months
- [ ] Community feedback is recent (last 12 months)
- [ ] Benchmarks are from current year
- [ ] Documentation is latest version

---

**Last Updated:** 2025-10-16
**Version:** 1.0
