# Agent Instructions

This repository is an **agentic AI benchmark** built around a real engineering design
problem: produce printable, functional STL files for a 3D-printed banana hair clip.

The design specification is in `SPEC.md`. The benchmark tasks are in `tasks/`.
Success is determined by physical printing and use — not by code appearance alone.

---

## The fundamental goal

Generate four STL files (`arm_left`, `arm_right`, `hinge_pin`, `hinge_cotter`) that:

1. Pass all automated geometry and dimension checks: `python eval/check_spec.py`
2. Slice cleanly in Bambu Studio or PrusaSlicer without unsupported overhangs on the arm faces
3. Assemble by hand without tools
4. Hold hair as a functional clip

A beautiful script that produces a broken mesh is a failure. An ugly script that
produces a watertight, assembleable clip is a success.

---

## Repository layout

```
SPEC.md                   # acceptance criteria — read this first
eval/
  check_spec.py           # automated S1-S4 checker — run after every change
  baseline.json           # known-good geometry metrics
tasks/
  README.md               # benchmark overview and scoring
  T01_audit/              # difficulty 1 — comprehension, no code changes
  T02_resize/             # difficulty 2 — single parameter change
  T03_tooth_density/      # difficulty 3 — multi-constraint parameter change
  T04_physical_iteration/ # difficulty 4 — diagnose and fix from a failure report
  T05_design_extension/   # difficulty 5 — add a new feature to the generator
scripts/
  config.py               # all design parameters — primary change target
  fit_demo_head_clip.py   # main STL generator
  simulate_hinge.py       # kinematic checks
  check_printability.py   # printability analysis
cadquery/                 # OpenCascade B-rep / STEP export (optional workflow)
outputs_fit_demo/         # generated STL files (printable pieces)
outputs_step/             # generated STEP files (CAD handoff)
outputs_cad_stl/          # STL files exported from CadQuery STEP solids
docs/                     # engineering documentation
lesson/                   # learning materials for newcomers to parametric design
```

---

## Regenerating geometry

Primary STL workflow (always usable):

```bash
python scripts/fit_demo_head_clip.py
```

Optional CadQuery/STEP workflow:

```bash
python cadquery/export_all.py
python cadquery/validate_cq.py
```

---

## Validation discipline

Run the spec checker after every geometry change:

```bash
python eval/check_spec.py
```

Run the hinge simulation after any hinge-related change:

```bash
python scripts/simulate_hinge.py
```

Do not claim STL files were regenerated unless `outputs_fit_demo/` timestamps changed.
Do not claim a check passes unless you have quoted the actual output.

---

## Design boundaries

- Preserve the four-piece assembly: left arm, right arm, pin, cotter.
- Keep the barrel-knuckle hinge with real pin bores and real cotter hole.
- Keep `PIN_VARIANTS_MM` (loose / nominal / snug) — they are part of the benchmark.
- Keep `eval/baseline.json` intact — it is used to detect regressions.
- Keep the `lesson/` directory — it is part of the benchmark materials.
- Prefer conservative printability over geometric complexity.
- Do not introduce geometry that requires support on the arm flat face.
