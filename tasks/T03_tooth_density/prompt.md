# T03 — Increase Tooth Density for Fine Hair

**Difficulty:** 3 / 5
**Type:** Multi-constraint parameter change
**Time budget:** 45 minutes

---

## Context

Users with fine or silky hair report that the current 32-tooth design lets hair slip
out under light tension. More teeth, spaced closer together, would improve grip.

Target tooth count: **40 teeth**.

---

## Your task

Increase tooth count from 32 to 40. This is harder than it sounds — the following
constraints must all hold simultaneously:

1. `TOOTH_COUNT` = 40 in `scripts/config.py`
2. All teeth remain within arm bounds (TOOTH_START_MM and TOOTH_END_MM unchanged)
3. Individual tooth width and slot clearance may need adjustment to prevent:
   - Tooth-to-slot collision at the closed position
   - Feature width below the 0.8 mm printability minimum (S4.1)
4. All S1–S4 SPEC criteria pass
5. Hinge simulation still passes (S3.1)

---

## What you need to understand first

The tooth pitch is determined by how many teeth fit between `TOOTH_START_MM` and
`TOOTH_END_MM`. With 40 teeth over the same span, pitch decreases from ~2.64 mm to
~2.11 mm. Consider whether `TOOTH_WIDTH_MM` needs to decrease and whether `SLOT_CLEARANCE_MM`
needs to be re-evaluated to maintain clearance.

Read `scripts/fit_demo_head_clip.py` to understand how tooth geometry is generated
before making changes.

---

## Steps

1. Analyze the current tooth pitch and identify what parameters must change.
2. Update `scripts/config.py` with the new tooth count and any dependent parameters.
3. Regenerate:
   ```bash
   python scripts/fit_demo_head_clip.py
   ```
4. Verify:
   ```bash
   python eval/check_spec.py
   ```
5. If any check fails, iterate — do not submit a failing result.

---

## What to deliver

- Modified `scripts/config.py` with all changed lines highlighted
- Explanation of your reasoning: which parameters changed and why
- Full output of `python eval/check_spec.py` (all pass)
- Full output of `python scripts/simulate_hinge.py` (PASSED)

---

## Automated grader

```bash
python tasks/T03_tooth_density/grader.py
```

---

## Scoring rubric

| Criterion | Points |
|---|---|
| `TOOTH_COUNT` == 40 | 15 |
| Tooth bounds unchanged (TOOTH_START, TOOTH_END within ±1mm of original) | 10 |
| `TOOTH_WIDTH_MM` ≥ 0.8 mm (printable) | 15 |
| All S1 geometry checks pass | 25 |
| Hinge simulation passes (S3.1) | 15 |
| Reasoning clearly explains the pitch / width trade-off | 20 |
| **Total** | **100** |

Partial credit: if 35–39 teeth with all other criteria met, award 8/15 for tooth count.
