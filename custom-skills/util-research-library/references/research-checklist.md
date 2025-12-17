# Library Research Checklist

Use this checklist to ensure comprehensive, systematic research across all 6 dimensions.

---

## Pre-Research Setup

### Context Gathering
- [ ] Check `pyproject.toml [tool.context7]` for existing library ID
- [ ] Review current codebase usage patterns
- [ ] Identify specific use case requirements
- [ ] Determine decision priority (Critical/High/Medium/Low)

### Time Allocation
- [ ] Phase 1 (Gather): 15 minutes budgeted
- [ ] Phase 2 (Synthesize): 10 minutes budgeted
- [ ] Phase 3 (Write): 15 minutes budgeted
- [ ] Total: ~40 minutes

---

## Dimension 1: Official Documentation

**Question:** Does it do what we need?

### Context7 Research
- [ ] Resolve library ID using `mcp__context7__resolve-library-id` (if not in pyproject.toml)
- [ ] Fetch docs with focused topic: `mcp__context7__get-library-docs(id, topic="<use_case>")`
- [ ] Extract capabilities relevant to use case
- [ ] Identify limitations or constraints
- [ ] Note best practices and recommended patterns

### Scoring Criteria
- [ ] **10/10:** Fully supports all requirements, clear documentation
- [ ] **7-9/10:** Supports most requirements, some gaps
- [ ] **4-6/10:** Partial support, workarounds needed
- [ ] **1-3/10:** Major gaps, unclear if viable

### Evidence Collected
```
Score: __/10
Evidence:
- Capability 1: ...
- Capability 2: ...
- Limitation: ...
```

---

## Dimension 2: Recent Developments

**Question:** Is it actively maintained and improving?

### WebSearch Queries
- [ ] `{library} changelog 2025` (use current year from env)
- [ ] `{library} release notes latest`
- [ ] `{library} roadmap 2025`
- [ ] `{library} breaking changes deprecations`

### Analysis
- [ ] Last release date: ___________
- [ ] Release frequency: ___________
- [ ] Breaking changes in last 6 months: Yes/No
- [ ] Active development indicators: Yes/No
- [ ] Future-proofing concerns: Yes/No

### Scoring Criteria
- [ ] **10/10:** Frequent releases, active roadmap, stable API
- [ ] **7-9/10:** Regular releases, responsive maintainers
- [ ] **4-6/10:** Occasional updates, slowing momentum
- [ ] **1-3/10:** Stagnant, deprecated, or abandoned

### Evidence Collected
```
Score: __/10
Evidence:
- Last release: ...
- Release cadence: ...
- Momentum: ...
```

---

## Dimension 3: Alternatives Analysis

**Question:** Is this the best tool for the job?

### WebSearch Queries
- [ ] `best {category} 2025 comparison benchmark`
- [ ] `{library} vs {alternative1} 2025`
- [ ] `{library} vs {alternative2} 2025`
- [ ] `{library} vs {alternative} discussion` (reddit.com, news.ycombinator.com)

### Trusted Comparison Sources
- [ ] db-engines.com (for databases)
- [ ] github.com (stars, forks, activity)
- [ ] benchmarks from independent sources

### Competitive Analysis
| Alternative | Strength | Weakness | When to Use |
|-------------|----------|----------|-------------|
| Alt 1 | | | |
| Alt 2 | | | |

### Scoring Criteria
- [ ] **10/10:** Clear leader, no better alternatives
- [ ] **7-9/10:** Top tier, strong competitive position
- [ ] **4-6/10:** Middle of pack, trade-offs exist
- [ ] **1-3/10:** Inferior to alternatives

### Evidence Collected
```
Score: __/10
Evidence:
- Why this over Alt1: ...
- Trade-offs: ...
- Deal-breakers (if any): ...
```

---

## Dimension 4: Security Assessment

**Question:** Is it safe to use?

### WebSearch Queries
- [ ] `{library} CVE vulnerability 2025` (nvd.nist.gov, snyk.io)
- [ ] `{library} security advisory 2025` (github.com)
- [ ] `{library} security patch history`

### Security Checks
- [ ] Known CVEs: Count: ___ Severity: ___
- [ ] Unpatched vulnerabilities: Yes/No
- [ ] Security response time: Fast/Medium/Slow
- [ ] Security best practices documented: Yes/No

### Scoring Criteria
- [ ] **10/10:** No CVEs, proactive security, good track record
- [ ] **7-9/10:** Minor CVEs patched quickly
- [ ] **4-6/10:** Some CVEs, slow patches
- [ ] **1-3/10:** Critical CVEs, poor security track record

### Evidence Collected
```
Score: __/10
Evidence:
- CVEs: ...
- Security posture: ...
- Risk level: ...
```

---

## Dimension 5: Community Health

**Question:** Will we get support when we need it?

### WebSearch Queries
- [ ] `{library} adoption trends 2025`
- [ ] `{library} experiences 2025` (reddit.com)
- [ ] `{library} discussion 2025` (news.ycombinator.com)
- [ ] `{library} problems issues 2025` (github.com, stackoverflow.com)

### Community Metrics
- [ ] GitHub stars: ___________
- [ ] GitHub issues (open/closed): _____ / _____
- [ ] Average issue response time: ___________
- [ ] StackOverflow questions: ___________
- [ ] Active contributors: ___________

### Community Insights
- [ ] Real user experiences (reddit/HN): ___________
- [ ] Common gotchas or pain points: ___________
- [ ] Community sentiment: Positive/Neutral/Negative

### Scoring Criteria
- [ ] **10/10:** Large community, responsive, positive sentiment
- [ ] **7-9/10:** Active community, good support
- [ ] **4-6/10:** Small but responsive community
- [ ] **1-3/10:** Inactive or negative community

### Evidence Collected
```
Score: __/10
Evidence:
- Community size: ...
- Responsiveness: ...
- Pain points: ...
```

---

## Dimension 6: Current Codebase Usage

**Question:** How does this fit with what we already have?

### Codebase Analysis
- [ ] Semantic search: `{library} usage patterns`
- [ ] Import count: ___________
- [ ] Usage locations: ___________
- [ ] Integration patterns: ___________

### Migration Assessment
- [ ] Files affected: ___________
- [ ] Breaking changes: ___________
- [ ] Test updates needed: ___________
- [ ] Migration effort: Days/Weeks/Months

### Scoring Criteria
- [ ] **10/10:** Seamless integration, minimal changes
- [ ] **7-9/10:** Straightforward integration, manageable effort
- [ ] **4-6/10:** Moderate integration complexity
- [ ] **1-3/10:** High integration complexity, risky migration

### Evidence Collected
```
Score: __/10
Evidence:
- Current usage: ...
- Migration effort: ...
- Integration risk: ...
```

---

## Synthesis Phase

### Overall Scoring
| Dimension | Score | Weight | Weighted Score |
|-----------|-------|--------|----------------|
| Functionality | __/10 | 25% | __ |
| Recent Dev | __/10 | 15% | __ |
| Alternatives | __/10 | 20% | __ |
| Security | __/10 | 20% | __ |
| Community | __/10 | 10% | __ |
| Integration | __/10 | 10% | __ |
| **Total** | | | __/10 |

### Decision Driver
- [ ] What's the ONE thing that matters most? ___________
- [ ] What's the deal-maker? ___________
- [ ] What's the deal-breaker (if any)? ___________

### Recommendation
- [ ] **ADOPT** - Use for new projects/features
- [ ] **MIGRATE** - Switch from current solution
- [ ] **UPGRADE** - Update to newer version
- [ ] **STAY** - Keep current solution
- [ ] **AVOID** - Do not use

### Confidence Level
- [ ] **High (8-10/10):** Strong evidence, clear decision
- [ ] **Medium (5-7/10):** Good evidence, minor uncertainties
- [ ] **Low (1-4/10):** Gaps in evidence, requires more research

---

## Writing Phase

### TL;DR Checklist
- [ ] Recommendation stated clearly (ADOPT/MIGRATE/etc.)
- [ ] Confidence level with numeric score
- [ ] Priority indicated (Critical/High/Medium/Low)
- [ ] Time to adopt estimated
- [ ] One-sentence summary written
- [ ] Key insight identified

### Decision Matrix Checklist
- [ ] All 6 dimensions scored
- [ ] Evidence provided for each score
- [ ] Impact stated (✅/⚠️/🔴)
- [ ] Overall score calculated

### Recommendation Checklist
- [ ] Clear action statement
- [ ] 3 reasons why (prioritized)
- [ ] Why not alternatives (specific reasons)
- [ ] Risks identified with mitigations

### Action Items Checklist
- [ ] Immediate actions (this week) specified
- [ ] Short-term actions (this month) specified
- [ ] Long-term actions (this quarter) specified
- [ ] Actions are specific and assignable

### Supporting Evidence Checklist
- [ ] Strengths documented
- [ ] Limitations documented
- [ ] Deal-breakers noted (if any)
- [ ] Community insights included
- [ ] Alternatives comparison table included

### Quality Checks
- [ ] Can user make decision from TL;DR alone? (30 sec test)
- [ ] Is recommendation clear and confident? (not "it depends")
- [ ] Are scores backed by specific evidence? (not gut feel)
- [ ] Are action items specific? (not vague)
- [ ] Are risks identified with mitigations? (not ignored)
- [ ] Is it scannable? (bullets, tables, sections)
- [ ] Is main content < 2 pages? (not wall of text)
- [ ] Would you read this if someone else wrote it?

---

## Post-Research

### Documentation
- [ ] Add library to `pyproject.toml [tool.context7]` if not present
- [ ] Save research brief to appropriate location
- [ ] Update ADR if architectural decision

### Memory Updates
- [ ] Create entity for library
- [ ] Create relations to related technologies
- [ ] Add observations about decision rationale

### Follow-up
- [ ] Schedule next review date: ___________
- [ ] Set triggers for re-evaluation: ___________
- [ ] Document who to notify of decision: ___________

---

## Common Pitfalls to Avoid

### Research Phase
- [ ] ❌ Dumping all search results without synthesis
- [ ] ❌ Ignoring migration costs
- [ ] ❌ Assuming newer = better
- [ ] ❌ Skipping security checks
- [ ] ❌ Only checking marketing materials

### Writing Phase
- [ ] ❌ Listing features without context
- [ ] ❌ Writing "it depends" recommendations
- [ ] ❌ Using vague language ("might", "could", "possibly")
- [ ] ❌ Creating walls of text
- [ ] ❌ Omitting action items

---

## Time Check

### Phase 1: Gather (Target: 15 min)
- Actual time: _____ minutes
- Over/Under: _____ minutes

### Phase 2: Synthesize (Target: 10 min)
- Actual time: _____ minutes
- Over/Under: _____ minutes

### Phase 3: Write (Target: 15 min)
- Actual time: _____ minutes
- Over/Under: _____ minutes

### Total (Target: 40 min)
- Actual time: _____ minutes
- Efficiency: _____% (40/actual)

---

## Continuous Improvement

### After 6 Months
- [ ] Review decisions made: How many were correct?
- [ ] Identify missed signals: What should we have caught?
- [ ] Update dimension weights: What matters most?
- [ ] Refine sources: Which had best signal/noise?
- [ ] Update templates: What format worked best?

---

**Last Updated:** 2025-10-16
**Version:** 1.0
