# Banana Hair Clip — Design Specification

This file defines the acceptance criteria for a 3D-printed banana hair clip produced
by this repository. An AI agent that generates STL files meeting all criteria has
demonstrated the ability to translate physical product requirements into valid,
printable, functional geometry.

Run automated checks at any time:

```bash
python eval/check_spec.py
```

---

## Target use case

| Attribute | Value |
|---|---|
| Wearer | Adult, gathered hair (bun or ponytail) |
| Head circumference | 520–580 mm |
| Hair volume at clip | ~50 mm wide, ~35 mm deep |
| Intended wear duration | Up to 12 hours/day |
| Print method | FDM — PETG preferred, PLA acceptable for first demo |
| Minimum build volume | 200 × 200 × 200 mm (Bambu P1/X1, Prusa MK4, Ender 3 V2) |

---

## Part list

Four separate STL files, assembled without tools or metal hardware:

| File | Role |
|---|---|
| `outputs_fit_demo/arm_left.stl` | Left arm — outer hinge barrels + hook |
| `outputs_fit_demo/arm_right.stl` | Right arm — inner hinge barrel + hook |
| `outputs_fit_demo/hinge_pin.stl` | Retention pin (3 size variants available) |
| `outputs_fit_demo/hinge_cotter.stl` | Cotter peg — locks pin in place |

---

## Acceptance criteria

### S1 — Geometry integrity (automated)

| ID | Criterion |
|---|---|
| S1.1 | All 4 STL files are watertight (manifold — no open edges or holes) |
| S1.2 | Each STL file is exactly 1 connected component |
| S1.3 | No degenerate (zero-area) triangles in any STL |

**Why S1 matters:** A non-manifold mesh cannot be sliced. Disconnected components cause Bambu Studio to treat pieces as separate floating bodies, breaking assembly.

---

### S2 — Dimensional bounds (automated, from `scripts/config.py`)

| ID | Criterion | Rationale |
|---|---|---|
| S2.1 | `ARM_LENGTH_MM` ∈ [100, 130] mm | Fits head circumference range; below 100 too short to grip hair, above 130 protrudes past ear |
| S2.2 | `ARM_THICKNESS_MM` ≥ 4.0 mm | Thinner arms crack at hinge under PETG/PLA cycling |
| S2.3 | `TOOTH_COUNT` ∈ [24, 44] | <24 insufficient grip, >44 makes slots too narrow for FDM |
| S2.4 | `TOOTH_START_MM` > 10 mm | Prevents teeth in the hinge zone |
| S2.5 | `TOOTH_END_MM` < `ARM_LENGTH_MM` − 10 mm | Preserves hook attachment zone |
| S2.6 | `PIN_RADIUS_MM` ∈ [1.0, 1.3] mm | 2.0–2.6 mm total diameter; below 1.0 snaps, above 1.3 resists insertion |
| S2.7 | `PIN_CLEARANCE_MM` ∈ [0.35, 0.55] mm | Below 0.35 cannot insert pin; above 0.55 hinge wobbles immediately |
| S2.8 | `HINGE_KNUCKLE_GAP_MM` ≥ 0.30 mm | Barrel axial clearance; tighter binds, looser rattles |

---

### S3 — Kinematics (automated, via `scripts/simulate_hinge.py`)

| ID | Criterion |
|---|---|
| S3.1 | Hinge simulation reports PASSED with no failures |
| S3.2 | Arms open to ≥ 30° without arm-body collision |
| S3.3 | Minimum arm gap at open position > 0 mm |
| S3.4 | No tooth-to-slot collision at the closed position |

---

### S4 — Printability (automated, via `scripts/check_printability.py`)

| ID | Criterion |
|---|---|
| S4.1 | `TOOTH_WIDTH_MM` ≥ 0.8 mm (2× standard 0.4 mm nozzle diameter) |
| S4.2 | `ARM_WIDTH_MM` ≥ 3× `TOOTH_WIDTH_MM` (arm wide enough for tooth roots) |
| S4.3 | Arms designed to print flat — spine face down — without supports on the main body face |
| S4.4 | All 4 pieces fit simultaneously on a 256 × 256 mm build plate |

---

### S5 — Assembly (human evaluation, first print)

| ID | Criterion |
|---|---|
| S5.1 | All 4 pieces assemble following README instructions in < 10 minutes without tools |
| S5.2 | At least one pin size variant (loose/nominal/snug) inserts through hinge barrels by hand |
| S5.3 | Cotter peg passes through the transverse hole in the pin and retains it |
| S5.4 | Assembled clip opens and closes through full range of motion without binding |

---

### S6 — Functional (human evaluation, 30-minute wear test)

| ID | Criterion |
|---|---|
| S6.1 | Clip holds gathered hair (bun or ponytail) for ≥ 10 continuous minutes without slipping |
| S6.2 | Arms close with one-handed force (no tools, no two-handed squeeze required) |
| S6.3 | No part of the clip causes skin discomfort after 30 minutes of wear |
| S6.4 | Hook ends engage each other reliably — clip does not spring open under light tension |

---

### S7 — Durability (human evaluation, cycle test)

| ID | Criterion |
|---|---|
| S7.1 | Hinge completes ≥ 50 open/close cycles in PETG without visible cracking or fracture |
| S7.2 | Pin does not back out or become loose after 50 cycles |
| S7.3 | Cotter peg remains in place after 50 cycles |

---

## Scoring

| Category | Criteria | Max points |
|---|---|---|
| S1 Geometry | 12 checks (4 files × 3) | 24 |
| S2 Dimensions | 8 criteria | 16 |
| S3 Kinematics | 4 criteria | 12 |
| S4 Printability | 4 criteria | 8 |
| **Automated total** | | **60** |
| S5 Assembly | 4 criteria | 10 |
| S6 Functional | 4 criteria | 15 |
| S7 Durability | 3 criteria | 15 |
| **Human total** | | **40** |
| **Grand total** | | **100** |

**Minimum passing threshold:** 55 / 100, with all S1 criteria passing.

An agent that scores well on S1–S4 but has never been printed should be treated as
**unverified**. Physical S5–S7 evaluation is required before claiming the design works.

---

## Evaluation protocol

### Automated (S1–S4)

```bash
python eval/check_spec.py
```

Outputs `eval/results.json` — one entry per criterion, each with `pass`, `value`, and
`reason` fields. Exit code 0 if all automated criteria pass; 1 otherwise.

### Human (S5–S7)

Print `outputs_fit_demo/` STL files using the settings in `docs/PRINT_GUIDE.md`.
Record results in `lesson/REVISION_PROMPT_TEMPLATE.md` and score each S5–S7 criterion.

---

## Baseline

The current baseline (unmodified repo) should pass all S1–S4 criteria.
Run `python eval/check_spec.py --save-baseline` to capture geometry metrics
after any validated regeneration.

Saved to `eval/baseline.json`.
