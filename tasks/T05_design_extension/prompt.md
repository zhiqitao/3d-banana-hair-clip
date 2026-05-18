# T05 — Add Parametric Size Variants

**Difficulty:** 5 / 5
**Type:** Generator code modification — new feature
**Time budget:** 90 minutes

---

## Context

The current design targets a single arm length (defined by `ARM_LENGTH_MM`).
A common request from users is to have Small / Medium / Large size variants
printed simultaneously from one configuration run, so they can choose the best
fit after printing.

---

## Your task

Add a **size variant system** to the generator. When the user runs:

```bash
python scripts/fit_demo_head_clip.py --sizes S M L
```

The script should generate three complete sets of STL files — one per size — in
separate subdirectories:

```
outputs_fit_demo/
  size_S/   arm_left.stl, arm_right.stl, hinge_pin.stl, hinge_cotter.stl
  size_M/   arm_left.stl, arm_right.stl, hinge_pin.stl, hinge_cotter.stl
  size_L/   arm_left.stl, arm_right.stl, hinge_pin.stl, hinge_cotter.stl
```

With the existing output (no `--sizes` flag) continuing to work exactly as before
and writing to `outputs_fit_demo/` directly.

---

## Size definitions

| Size | ARM_LENGTH_MM | Head circumference target |
|---|---|---|
| S | 100 mm | ~510 mm |
| M | 116 mm (current) | ~555 mm (unchanged) |
| L | 130 mm | ~590 mm |

All other parameters (`TOOTH_COUNT`, `PIN_RADIUS_MM`, `PIN_CLEARANCE_MM`, etc.)
stay at their `config.py` values. Only the following scale proportionally with arm length:

- `TOOTH_START_MM` — scale by `arm_length / ARM_LENGTH_MM`
- `TOOTH_END_MM` — scale by `arm_length / ARM_LENGTH_MM`
- `ELASTIC_HOLE_X_MM` — scale by `arm_length / ARM_LENGTH_MM`

---

## Requirements

1. `--sizes` flag is optional; no flag = current behaviour, no subdirectories
2. Each size subdirectory contains exactly the 4 printable STL files
3. All 4 STL files in each size variant are watertight and 1 component
4. Running `python eval/check_spec.py` on any size variant's config values passes S2
5. No changes to `scripts/config.py` — size scaling happens inside the script
6. The modification must be backward-compatible: existing tests and CI must still pass

---

## Steps

1. Read `scripts/fit_demo_head_clip.py` thoroughly before making changes.
2. Identify where arm length and proportional parameters are used.
3. Add argument parsing for `--sizes`.
4. Loop over requested sizes, scale the proportional parameters, write to subdirectory.
5. Verify each size variant:
   ```bash
   python scripts/fit_demo_head_clip.py --sizes S M L
   ```
6. Verify backward compatibility:
   ```bash
   python scripts/fit_demo_head_clip.py
   python eval/check_spec.py
   ```
7. Check watertightness across all variants.

---

## What to deliver

- The modified `scripts/fit_demo_head_clip.py` (show a diff or the changed sections)
- Directory listing of `outputs_fit_demo/` showing all three size subdirectories
- Watertight check output for all 12 STL files (S + M + L × 4 pieces)
- Confirmation that the no-`--sizes` run still writes to `outputs_fit_demo/` directly
- Full output of `python eval/check_spec.py` (still passes)

---

## Automated grader

```bash
python tasks/T05_design_extension/grader.py
```

---

## Scoring rubric

| Criterion | Points |
|---|---|
| `--sizes` flag accepted without error | 10 |
| Three subdirectories (size_S, size_M, size_L) created | 10 |
| Each subdirectory contains all 4 STL files | 10 |
| All 12 STL files watertight and single component | 25 |
| Proportional parameters (TOOTH_START, TOOTH_END, ELASTIC_HOLE) scaled correctly | 15 |
| No-flag run unaffected (backward compatible) | 15 |
| `eval/check_spec.py` still passes | 15 |
| **Total** | **100** |
