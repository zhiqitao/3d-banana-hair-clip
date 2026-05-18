# T04 — Physical Iteration from Print Failure

**Difficulty:** 4 / 5
**Type:** Diagnose a real failure report, propose fixes, implement, validate
**Time budget:** 60 minutes

---

## Context

A first print was completed. The clip assembles but has four problems that make it
unusable as a daily hair clip. The full failure report is in `failure_report.md`
in this directory.

---

## Your task

Read `failure_report.md` carefully. For each reported problem:

1. **Diagnose** — identify the root cause in the codebase (file and parameter/line)
2. **Propose** — state the specific change you will make and why
3. **Implement** — make the change in `scripts/config.py` or the generator script
4. **Validate** — run `python eval/check_spec.py` and confirm the change does not
   break any automated criteria

You must address all four reported problems. If fixing one problem conflicts with
fixing another, explain the trade-off and resolve it.

---

## Constraints

- Do not change `TOOTH_COUNT` (leave it at the current value)
- Do not change `ARM_LENGTH_MM` (leave it at the current value)
- All S1 geometry checks must still pass after your changes
- At least two of the four problems must be addressed with a parameter change in
  `scripts/config.py` (not just a comment or documentation change)

---

## What to deliver

A structured response with four sections — one per problem:

```
### Problem 1: [Name from failure report]
Diagnosis: [root cause — specific file, parameter, line]
Change: [exact parameter name and new value]
Rationale: [why this value]
```

Then: the full output of `python eval/check_spec.py` after all changes are applied.

---

## Automated grader

```bash
python eval/check_spec.py
```

All S1–S4 checks must still pass. No dedicated task grader — the spec checker
is the gate.

---

## Scoring rubric

| Criterion | Points |
|---|---|
| Problem 1 diagnosed correctly with code location | 12 |
| Problem 2 diagnosed correctly with code location | 12 |
| Problem 3 diagnosed correctly with code location | 12 |
| Problem 4 diagnosed correctly with code location | 12 |
| At least 2 fixes implemented in config.py | 15 |
| All S1–S4 spec checks still pass | 20 |
| Trade-off explanation if any fixes conflict | 10 |
| Check output quoted (not just claimed) | 7 |
| **Total** | **100** |
