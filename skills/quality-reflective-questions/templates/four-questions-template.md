# Four Questions Self-Review Template

**Feature/Task:** ___________________________
**Date:** ___________________________
**Reviewer:** ___________________________

---

## The Four Mandatory Questions

### Question 1: How do I trigger this?

**Initial Answer:**


**Follow-up: Is this SPECIFIC enough?**
- [ ] Can I paste the exact command right now?
- [ ] Could someone else trigger this without asking me?
- [ ] Does this include all required arguments/parameters?

**Revised Answer (if needed):**


**Evidence:**
```bash
# Paste the EXACT command here

```

---

### Question 2: What connects it to the system?

**Initial Answer:**


**Follow-up: Is this SPECIFIC enough?**
- [ ] Can I show the file and line number?
- [ ] Can I paste the import/registration statement?
- [ ] Could I find this in 60 seconds with grep?

**Revised Answer (if needed):**


**Evidence:**
```bash
# Paste grep output showing the connection

```

---

### Question 3: What evidence proves it runs?

**Initial Answer:**


**Follow-up: Is this SPECIFIC enough?**
- [ ] Can I show timestamped log output?
- [ ] Did I actually trigger this and observe it?
- [ ] Am I showing execution proof vs assuming it runs?

**Revised Answer (if needed):**


**Evidence:**
```bash
# Paste actual logs showing execution

```

---

### Question 4: What shows it works correctly?

**Initial Answer:**


**Follow-up: Is this SPECIFIC enough?**
- [ ] Can I show the exact output/state change?
- [ ] Am I showing correct behavior vs just "no errors"?
- [ ] Can I demonstrate this matches the specification?

**Revised Answer (if needed):**


**Evidence:**
```bash
# Paste actual output or state showing correct behavior

```

---

## Honesty Checklist

Answer honestly:

- [ ] All four questions answered with SPECIFIC details (not vague)
- [ ] All evidence is ACTUAL output (not "should" or "probably")
- [ ] I have PERSONALLY triggered and observed this
- [ ] I could demonstrate this working RIGHT NOW to someone else
- [ ] I would bet $1000 this works end-to-end
- [ ] No "should", "probably", "I think" language in answers
- [ ] All connection points verified with grep/inspection
- [ ] All execution verified with logs/output

**If ANY box unchecked:** Work is NOT complete. Fix gaps before claiming "done".

---

## Self-Deception Check

Answer honestly (these are WARNING signs):

- [ ] Am I rushing to mark this done?
- [ ] Do I have doubts I'm ignoring?
- [ ] Am I relying on "tests pass" alone?
- [ ] Did I skip actually triggering this manually?
- [ ] Am I assuming connection without verifying?
- [ ] Am I using vague language to avoid specifics?
- [ ] Would I be embarrassed to demo this right now?

**If ANY box checked:** STOP. Investigate the concern before proceeding.

---

## Red Flag Questions

Answer YES or NO:

1. **Did I only test this in isolation?** ☐ YES ☐ NO
   - If YES: Add integration test, verify in real system

2. **Am I assuming something is connected without verifying?** ☐ YES ☐ NO
   - If YES: Verify with grep, show evidence

3. **Did I only run unit tests, not integration tests?** ☐ YES ☐ NO
   - If YES: Create/run integration tests

4. **Am I relying on 'should' or 'probably' language?** ☐ YES ☐ NO
   - If YES: Replace assumptions with evidence

5. **Could this code exist and never execute?** ☐ YES ☐ NO
   - If YES: Verify call-sites exist in production

6. **Have I not actually triggered this feature?** ☐ YES ☐ NO
   - If YES: Trigger it, observe execution

7. **Am I claiming it works based on 'no errors' vs positive proof?** ☐ YES ☐ NO
   - If YES: Show positive evidence of correct behavior

8. **Did I forget to check logs after running?** ☐ YES ☐ NO
   - If YES: Run again, capture logs

9. **Am I trusting tests alone without manual verification?** ☐ YES ☐ NO
   - If YES: Manual E2E test required

10. **Could this be wired but the conditional never triggers?** ☐ YES ☐ NO
    - If YES: Verify the condition is reachable

**If ANY answer is YES:** Address the issue before claiming complete.

---

## Final Decision

**Based on honest answers above:**

☐ **COMPLETE** - All four questions answered specifically, all evidence present, all checks passed

☐ **NOT COMPLETE** - Gaps found, need to:
  - [ ] Fix connection issues (import/registration)
  - [ ] Verify execution (trigger and capture logs)
  - [ ] Verify outcome (show correct behavior)
  - [ ] Other: _______________________________

**Signature/Date:** ___________________________

**Next Action:**
- If COMPLETE: Proceed to mark task/ADR as done
- If NOT COMPLETE: Address gaps listed above, then re-run this review

---

## Template Usage

**When to use:**
- Before marking any task complete
- Before moving ADR to completed
- During self-review
- When claiming "feature works"

**How to use:**
1. Copy this template
2. Answer all questions honestly
3. Paste actual evidence (don't write "it's imported" - paste grep output)
4. Check all checklists
5. Make final decision
6. Act on decision (fix or complete)

**Remember:** The person you're most likely to deceive is yourself. Be honest.
