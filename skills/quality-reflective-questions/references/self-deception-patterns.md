## Common Self-Deception Patterns

### Pattern 1: "Tests Pass" Syndrome

**Symptom:** Claiming complete because unit tests pass

**Reality Check:**
- "Do the tests import production code or mock it?"
- "Do the tests verify integration or isolated behavior?"
- "Could code exist, tests pass, feature not work?"

**Fix:** Add integration tests, verify in real system

### Pattern 2: "Should Work" Fallacy

**Symptom:** Using words like "should", "probably", "I think"

**Reality Check:**
- "Replace 'should' with 'does' - can you still claim it?"
- "What EVIDENCE do you have, not assumptions?"

**Fix:** Verify explicitly, replace assumptions with proof

### Pattern 3: "No Errors" Confusion

**Symptom:** Equating "no errors" with "works correctly"

**Reality Check:**
- "Could this produce no errors but wrong output?"
- "What positive proof do you have of correct behavior?"

**Fix:** Show correct output, not just absence of errors

### Pattern 4: "File Exists" Completion

**Symptom:** Marking done when artifact created, not integrated

**Reality Check:**
- "Is this file imported anywhere?"
- "Are these functions called anywhere?"
- "Could I delete this and nothing breaks?"

**Fix:** Verify imports, call-sites, integration points

### Pattern 5: "Looks Good" Approval

**Symptom:** Vague assessment instead of specific verification

**Reality Check:**
- "What SPECIFIC evidence supports 'looks good'?"
- "Could you list 5 concrete verification points?"

**Fix:** Replace vague approval with specific checklist

### Pattern 6: "I Remember Doing It" Assumption

**Symptom:** Trusting memory instead of current verification

**Reality Check:**
- "Can you show me RIGHT NOW where this is?"
- "What if your memory is wrong?"

**Fix:** Verify current state, don't trust memory

### Pattern 7: "Later Will Be Fine" Deferral

**Symptom:** Skipping verification steps to finish faster

**Reality Check:**
- "What makes you think later is better than now?"
- "What's the cost if this is wrong and you mark it done?"

**Fix:** Verify now, don't defer to "later"

