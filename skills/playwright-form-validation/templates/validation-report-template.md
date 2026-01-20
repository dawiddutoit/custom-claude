# Form Validation Test Report

**Form Name:** [Form Name]
**Form URL:** [URL]
**Test Date:** [YYYY-MM-DD]
**Tester:** Claude Code (playwright-form-validation skill)

---

## Executive Summary

| Metric | Value |
|--------|-------|
| **Total Fields** | [N] |
| **Fields Tested** | [N] |
| **Validations Found** | [N] |
| **Missing Validations** | [N] |
| **Valid Submission** | ✅ Success / ❌ Failed |
| **Overall Status** | ✅ Pass / ⚠️ Issues Found / ❌ Critical Issues |

### Key Findings

- [Finding 1]
- [Finding 2]
- [Finding 3]

---

## Test Coverage

### Fields Tested

| Field Name | Type | Required | Constraints | Tests Run | Status |
|------------|------|----------|-------------|-----------|--------|
| [Field 1] | [text/email/etc] | Yes/No | [min/max/pattern] | [N] | ✅/⚠️/❌ |
| [Field 2] | [text/email/etc] | Yes/No | [min/max/pattern] | [N] | ✅/⚠️/❌ |

### Test Summary

- **Empty Value Tests:** [N passed / N failed]
- **Format Validation Tests:** [N passed / N failed]
- **Boundary Tests:** [N passed / N failed]
- **Cross-Field Tests:** [N passed / N failed]
- **Valid Submission:** [Pass/Fail]

---

## Detailed Results

### Field 1: [Field Name]

**Field Details:**
- Type: [textbox/email/number/etc]
- Required: Yes/No
- Constraints: [min/max length, pattern, etc]
- Accessibility: [aria-invalid, aria-describedby, etc]

**Test Cases:**

| Test Case | Input Value | Expected Result | Actual Result | Status |
|-----------|-------------|-----------------|---------------|--------|
| Empty value | `""` | "Field is required" | "[Actual message]" | ✅/❌ |
| Invalid format | `"[test value]"` | "[Expected error]" | "[Actual message]" | ✅/❌ |
| Below minimum | `"[value]"` | "[Expected error]" | "[Actual message]" | ✅/❌ |
| Above maximum | `"[value]"` | "[Expected error]" | "[Actual message]" | ✅/❌ |
| Valid value | `"[value]"` | No error | No error | ✅/❌ |

**Screenshots:**
- [Empty value error](path/to/screenshot1.png)
- [Invalid format error](path/to/screenshot2.png)
- [Boundary error](path/to/screenshot3.png)

**Notes:**
- [Any additional observations about this field]

---

### Field 2: [Field Name]

[Repeat structure from Field 1]

---

## Cross-Field Validation

### [Cross-Field Test Name] (e.g., Password Confirmation)

**Fields Involved:** [Field A], [Field B]

**Test Cases:**

| Test Case | Field A | Field B | Expected Result | Actual Result | Status |
|-----------|---------|---------|-----------------|---------------|--------|
| [Test 1] | `"[value]"` | `"[value]"` | "[Expected]" | "[Actual]" | ✅/❌ |
| [Test 2] | `"[value]"` | `"[value]"` | "[Expected]" | "[Actual]" | ✅/❌ |

**Screenshots:**
- [Cross-field error](path/to/screenshot.png)

---

## Valid Submission Test

**Test Details:**
- All fields filled with valid values
- No validation errors expected

**Input Values:**

| Field | Value |
|-------|-------|
| [Field 1] | `"[value]"` |
| [Field 2] | `"[value]"` |
| [Field 3] | `"[value]"` |

**Expected Outcome:**
- Form submits successfully
- [Redirect to success page / Show success message / etc]

**Actual Outcome:**
- ✅ Form submitted successfully
- ✅ Redirected to [URL]
- ✅ Success message displayed: "[message]"

OR

- ❌ Form submission failed
- ❌ Error: [error description]

**Screenshot:**
- [Success state](path/to/screenshot.png)

---

## Missing Validations

### Critical Issues

| Field | Issue | Impact | Recommendation |
|-------|-------|--------|----------------|
| [Field name] | [Missing validation] | [High/Medium/Low] | [Suggested fix] |

### Warnings

| Field | Issue | Impact | Recommendation |
|-------|-------|--------|----------------|
| [Field name] | [Weak validation] | [Medium/Low] | [Suggested improvement] |

---

## Accessibility Findings

### Positive Findings

- ✅ [Accessibility feature found]
- ✅ [Accessibility feature found]

### Issues

- ❌ [Accessibility issue]
- ⚠️ [Accessibility concern]

### Recommendations

1. [Recommendation 1]
2. [Recommendation 2]

---

## Validation Message Analysis

### Messages Found

| Field | Message | Clarity | Helpfulness |
|-------|---------|---------|-------------|
| [Field] | "[Message]" | ✅ Clear / ⚠️ Unclear | ✅ Helpful / ⚠️ Not helpful |

### Consistency

- ✅ Consistent error message formatting
- ⚠️ Inconsistent message style across fields
- ❌ No validation messages shown

### Tone

- ✅ Friendly and helpful
- ⚠️ Technical/confusing
- ❌ Harsh or blaming

---

## Recommendations

### High Priority

1. **[Recommendation Title]**
   - Issue: [Description]
   - Impact: [User impact]
   - Suggested Fix: [How to fix]
   - Effort: [Low/Medium/High]

### Medium Priority

1. **[Recommendation Title]**
   - Issue: [Description]
   - Impact: [User impact]
   - Suggested Fix: [How to fix]
   - Effort: [Low/Medium/High]

### Low Priority / Nice to Have

1. **[Recommendation Title]**
   - Issue: [Description]
   - Impact: [User impact]
   - Suggested Fix: [How to fix]
   - Effort: [Low/Medium/High]

---

## Best Practices Compliance

| Best Practice | Status | Notes |
|--------------|--------|-------|
| All required fields validated | ✅/❌ | [Notes] |
| Format validation on typed fields | ✅/❌ | [Notes] |
| Clear error messages | ✅/❌ | [Notes] |
| Inline error display | ✅/❌ | [Notes] |
| Error prevention (pattern attr) | ✅/❌ | [Notes] |
| Accessible error association | ✅/❌ | [Notes] |
| Valid submission confirmed | ✅/❌ | [Notes] |

---

## Appendix

### Screenshots Index

All screenshots saved to: `[directory path]`

1. **Initial State:** [filename.png]
2. **Field Validations:**
   - [field-validation-1.png] - [Description]
   - [field-validation-2.png] - [Description]
   - [field-validation-N.png] - [Description]
3. **Cross-Field Validations:**
   - [cross-field-1.png] - [Description]
4. **Success State:**
   - [success.png] - [Description]

### Snapshots Index

All snapshots saved to: `[directory path]`

1. [initial-state.md] - Initial form structure
2. [validation-state-1.md] - [Description]
3. [validation-state-N.md] - [Description]
4. [success-state.md] - Successful submission

### Test Environment

- Browser: [Browser name and version]
- Viewport: [Width x Height]
- Date/Time: [Timestamp]
- Network: [Online/Offline]

### Raw Data

[Optional: Include raw validation message data, DOM structure excerpts, etc.]

---

## Conclusion

[Summary of overall validation test results, key takeaways, and next steps]

**Overall Assessment:** ✅ Pass / ⚠️ Pass with Issues / ❌ Fail

**Next Steps:**
1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

---

*Generated by playwright-form-validation skill*
*Report Date: [YYYY-MM-DD HH:MM]*
