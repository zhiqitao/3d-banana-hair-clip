# T02 — Resize for a Smaller Head

**Difficulty:** 2 / 5
**Type:** Single-parameter change with proportional scaling
**Time budget:** 30 minutes

---

## Context

The current design (arm length 116 mm) is calibrated for a head circumference of
roughly 560 mm. A user with a smaller head (~510 mm circumference) reports that
the clip extends past their ear uncomfortably.

Target arm length: **100 mm**.

---

## Your task

Shorten the clip to 100 mm arm length. The following must all be true when you are done:

1. `ARM_LENGTH_MM` = 100 in `scripts/config.py`
2. Tooth span scaled proportionally — same tooth density, still within arm bounds:
   - `TOOTH_START_MM` proportional to new arm length
   - `TOOTH_END_MM` proportional to new arm length
   - Both within S2.4 and S2.5 bounds
3. Elastic hole position (`ELASTIC_HOLE_X_MM`) scaled to remain within arm bounds
4. STL files regenerated
5. All S1–S4 criteria in `SPEC.md` pass

---

## Steps

1. Update `scripts/config.py`.
2. Regenerate STLs:
   ```bash
   python scripts/fit_demo_head_clip.py
   ```
3. Verify:
   ```bash
   python eval/check_spec.py
   ```
4. Report the check output.

---

## What to deliver

- The modified `scripts/config.py` (show the changed lines)
- The full output of `python eval/check_spec.py`
- Confirmation that `outputs_fit_demo/` files were regenerated (file timestamps or sizes)
- One sentence explaining why proportional scaling is the right approach here

---

## Automated grader

```bash
python tasks/T02_resize/grader.py
```

The grader checks:
- `ARM_LENGTH_MM` == 100
- `TOOTH_START_MM` and `TOOTH_END_MM` scaled within bounds
- `ELASTIC_HOLE_X_MM` < ARM_LENGTH_MM - 5
- All S1 STL geometry checks pass

---

## Scoring rubric

| Criterion | Points |
|---|---|
| `ARM_LENGTH_MM` == 100 | 20 |
| Tooth bounds proportionally scaled and within spec | 25 |
| Elastic hole within arm bounds | 10 |
| All S1–S4 automated checks pass | 30 |
| Delivered check output (not just claimed success) | 15 |
| **Total** | **100** |
