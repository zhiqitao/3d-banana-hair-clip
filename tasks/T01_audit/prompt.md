# T01 — Spec Audit

**Difficulty:** 1 / 5
**Type:** Comprehension — no code changes allowed
**Time budget:** 15 minutes

---

## Your task

Run `python eval/check_spec.py` and produce a written audit report.

Do not modify any code or configuration. Your job is only to read, run, and report.

---

## What to deliver

A structured report covering all of the following:

### 1. Automated check results

List every criterion that passes and every criterion that fails, with the reported value.

### 2. Root cause for each failure

For each failing criterion, identify:
- Which file contains the relevant parameter or code
- The exact line or value that causes the failure
- Whether the failure is a real design problem or a spec boundary issue

### 3. Geometry assessment

For each of the 4 STL files (`arm_left`, `arm_right`, `hinge_pin`, `hinge_cotter`):
- Is it watertight?
- How many components does it have?

### 4. Gap analysis — what the automated checks cannot catch

List at least 3 things that `eval/check_spec.py` does NOT check that would affect
whether the clip actually works in real life. Explain why each one matters.

### 5. Your recommendation

Given the audit findings, what single change would most improve the design's readiness
for a first physical print? Give a specific parameter name or file location.

---

## Scoring rubric

| Criterion | Points |
|---|---|
| Ran `eval/check_spec.py` and quoted actual output | 20 |
| Correct pass/fail list with values | 20 |
| Accurate root-cause identification for each failure | 20 |
| 3+ valid automated-check gaps with clear rationale | 25 |
| Specific, actionable recommendation grounded in the code | 15 |
| **Total** | **100** |

No points for answers that could be written without running the script or reading the code.
