# Decision Matrix Template

Copy and fill out this template for structured library evaluation.

---

## Library Evaluation: {Library Name}

**Date:** {YYYY-MM-DD}
**Researcher:** {Name}
**Use Case:** {Brief description of what we need}

---

## 📋 TL;DR (30-second read)

**Recommendation:** [ADOPT / MIGRATE / UPGRADE / STAY / AVOID]
**Confidence:** [High/Medium/Low] ({X}/10)
**Priority:** [Critical/High/Medium/Low]
**Time to Adopt:** [{X} Days / {X} Weeks / {X} Months]

**One-sentence summary:**
{What the library is and why it matters in one sentence}

**Key insight:**
{The one non-obvious thing that drives the recommendation}

---

## 🎯 Decision Matrix (3-minute read)

| Dimension | Score | Evidence | Impact |
|-----------|-------|----------|--------|
| **Functionality** | ⭐⭐⭐⭐⭐ {X}/10 | {What it does well} | {✅/⚠️/🔴} {Impact statement} |
| **Performance** | ⭐⭐⭐⭐ {X}/10 | {Speed/efficiency metrics} | {✅/⚠️/🔴} {Impact statement} |
| **Security** | ⭐⭐⭐⭐⭐ {X}/10 | {CVE status, security posture} | {✅/⚠️/🔴} {Impact statement} |
| **Community** | ⭐⭐⭐⭐ {X}/10 | {Community size, responsiveness} | {✅/⚠️/🔴} {Impact statement} |
| **Maturity** | ⭐⭐⭐ {X}/10 | {Version, age, stability} | {✅/⚠️/🔴} {Impact statement} |
| **Migration** | ⭐⭐⭐⭐ {X}/10 | {Effort estimate, risk level} | {✅/⚠️/🔴} {Impact statement} |

**Overall:** {X.X}/10 - **{Strong/Moderate/Weak} recommendation**

---

## ✅ Recommendation

**{DECISION}**: {Clear action statement in one sentence}

**Why:**
1. {Primary reason - the deal-maker, the most important factor}
2. {Secondary reason - strong supporting evidence}
3. {Tertiary reason - nice-to-have benefit}

**Why not alternatives:**
- **{Alternative 1}**: {Specific disqualifying reason or trade-off}
- **{Alternative 2}**: {Specific disqualifying reason or trade-off}
- **{Alternative 3}**: {Specific disqualifying reason or trade-off}

**Risks & Mitigations:**
- ⚠️ **{Risk 1}**: {Mitigation strategy or monitoring plan}
- ⚠️ **{Risk 2}**: {Mitigation strategy or monitoring plan}
- ⚠️ **{Risk 3}**: {Mitigation strategy or monitoring plan}

---

## 🚀 Action Items

**Immediate (this week):**
1. [ ] {Specific action with owner, e.g., "John: Create proof-of-concept"}
2. [ ] {Specific action with owner, e.g., "Jane: Review security docs"}
3. [ ] {Specific action with owner}

**Short-term (this month):**
1. [ ] {Specific milestone or task}
2. [ ] {Specific milestone or task}
3. [ ] {Specific milestone or task}

**Long-term (this quarter):**
1. [ ] {Larger initiative or goal}
2. [ ] {Larger initiative or goal}

---

## 📊 Supporting Evidence (10-minute read)

### What We Found

#### ✅ Strengths
- **{Strength 1}**: {Specific evidence and why it matters}
- **{Strength 2}**: {Specific evidence and why it matters}
- **{Strength 3}**: {Specific evidence and why it matters}

#### ⚠️ Limitations
- **{Limitation 1}**: {Specific limitation and workaround if available}
- **{Limitation 2}**: {Specific limitation and impact assessment}
- **{Limitation 3}**: {Specific limitation and when it matters}

#### 🔴 Deal-breakers (if any)
- **{Deal-breaker}**: {What would absolutely disqualify this library}

### Dimension Details

#### 1. Functionality ({X}/10)

**What it does:**
- {Capability 1}
- {Capability 2}
- {Capability 3}

**What it doesn't do:**
- {Gap 1}
- {Gap 2}

**Best practices:**
- {Best practice 1}
- {Best practice 2}

**Evidence sources:**
- Context7: {library_id}
- Official docs: {URL}

---

#### 2. Recent Developments ({X}/10)

**Release cadence:**
- Last release: {Date}
- Frequency: {Weekly/Monthly/Quarterly}
- Version: {Current version}

**Recent changes:**
- {Notable change 1}
- {Notable change 2}
- {Breaking changes if any}

**Roadmap:**
- {Upcoming feature 1}
- {Upcoming feature 2}

**Evidence sources:**
- Changelog: {URL}
- Roadmap: {URL}

---

#### 3. Alternatives Analysis ({X}/10)

**Primary alternatives:**
1. **{Alternative 1}**
   - Strength: {What it does better}
   - Weakness: {What it does worse}
   - When to use: {Specific use case}

2. **{Alternative 2}**
   - Strength: {What it does better}
   - Weakness: {What it does worse}
   - When to use: {Specific use case}

**Competitive positioning:**
- {How this library compares overall}
- {Key differentiator}

**Evidence sources:**
- Comparison: {URL}
- Benchmarks: {URL}

---

#### 4. Security Assessment ({X}/10)

**CVE status:**
- Known CVEs: {Count} (Severity: {Critical/High/Medium/Low/None})
- Unpatched: {Yes/No}
- Last security patch: {Date}

**Security posture:**
- {Security feature 1}
- {Security feature 2}
- Response time: {Fast/Medium/Slow}

**Risk level:** {Low/Medium/High}

**Evidence sources:**
- NVD: {URL}
- Snyk: {URL}
- GitHub advisories: {URL}

---

#### 5. Community Health ({X}/10)

**Community metrics:**
- GitHub stars: {Count}
- Contributors: {Count}
- Open/Closed issues: {Open} / {Closed}
- Avg response time: {Hours/Days}
- StackOverflow questions: {Count}

**Community sentiment:**
- {Positive/Neutral/Negative}
- {Key theme from community}

**Real user experiences:**

**From Reddit:**
- {Key insight or gotcha}
- {Common pain point}

**From Hacker News:**
- {Technical discussion point}
- {Notable concern or praise}

**From GitHub:**
- {Issue responsiveness observation}
- {Active development indicator}

**Evidence sources:**
- Reddit: {URL}
- HN: {URL}
- GitHub: {URL}

---

#### 6. Current Usage ({X}/10)

**Codebase analysis:**
- Current usage: {How we use it now / Not currently used}
- Import count: {X} files
- Integration points: {Where it's used}

**Migration assessment:**
- Files to modify: {Count}
- Tests to update: {Count}
- Breaking changes: {List or "None"}
- Estimated effort: {X Days/Weeks/Months}
- Risk level: {Low/Medium/High}

**Integration complexity:**
- {Easy/Moderate/Complex}
- {Specific challenge 1}
- {Specific challenge 2}

**Evidence sources:**
- Semantic search results
- Import analysis
- Dependency graph

---

### Community Insights

**What users love:**
- {Positive feedback theme 1}
- {Positive feedback theme 2}

**What users complain about:**
- {Common gotcha or pain point 1}
- {Common gotcha or pain point 2}

**War stories:**
- {Interesting real-world experience}
- {Lesson learned from production use}

---

### Alternatives Comparison Table

| Criteria | {This Library} | {Alternative 1} | {Alternative 2} |
|----------|----------------|-----------------|-----------------|
| **Performance** | {Rating/Metric} | {Rating/Metric} | {Rating/Metric} |
| **Features** | {Rating/Count} | {Rating/Count} | {Rating/Count} |
| **Community** | {Stars/Activity} | {Stars/Activity} | {Stars/Activity} |
| **Security** | {CVE count} | {CVE count} | {CVE count} |
| **Maturity** | {Age/Version} | {Age/Version} | {Age/Version} |
| **Migration** | {Effort} | {Effort} | {Effort} |
| **License** | {Type} | {Type} | {Type} |

**Winner:** {This library / Alternative} because {specific reason}

---

### Alternatives Decision Table

| Alternative | Why Not? | When to Reconsider |
|-------------|----------|-------------------|
| **{Alt 1}** | {Specific disqualifying reason} | {Condition that would change decision} |
| **{Alt 2}** | {Specific disqualifying reason} | {Condition that would change decision} |
| **{Alt 3}** | {Specific disqualifying reason} | {Condition that would change decision} |

---

## 📚 References

**Official Resources:**
- Documentation: {Context7 library ID or URL}
- GitHub: {URL}
- Official site: {URL}
- Changelog: {URL}

**Benchmarks & Comparisons:**
- Benchmark 1: {URL}
- Comparison 1: {URL}

**Community Discussions:**
- Reddit thread: {URL}
- HN discussion: {URL}
- GitHub issues: {URL}

**Security:**
- CVE database: {URL}
- Security advisory: {URL}

---

## 🔄 Next Review

**When to revisit:**
- **Trigger 1:** {Specific event, e.g., "v3.0 release"}
- **Trigger 2:** {Time-based, e.g., "6 months from now"}
- **Trigger 3:** {Condition-based, e.g., "if performance degrades"}

**Review date:** {YYYY-MM-DD}
**Owner:** {Name}

---

## 📝 Notes

**Additional context:**
- {Anything that doesn't fit above but matters}
- {Special considerations}
- {Assumptions made}

**Open questions:**
- {Question 1}
- {Question 2}

**Follow-up needed:**
- {Action or research needed}

---

## 📦 Metadata

**Research metadata:**
- Time spent: {X} minutes
- Sources consulted: {Count}
- Confidence factors:
  - Documentation: {Good/Fair/Poor}
  - Community feedback: {Good/Fair/Poor}
  - Benchmark data: {Good/Fair/Poor}
  - Security data: {Good/Fair/Poor}

**Decision metadata:**
- Decision made: {Date}
- Decision by: {Name/Team}
- Approved by: {Name} (if applicable)
- Stakeholders notified: {Yes/No}

---

**Template Version:** 1.0
**Last Updated:** 2025-10-16
