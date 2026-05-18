# Validation Strategy

## Software validation

The script checks what can be checked without a physical print:

- 2D arm body overlap
- tooth collision against slotted body
- full closed non-hinge overlap
- hinge boss contact area
- layer validity
- pin clearance
- STL watertightness

Run:

```bash
python scripts/banana_clip_design_final.py
python scripts/validate_geometry.py
```

## Coupon validation

The final package includes small coupons to reduce first-print risk:

| Coupon | Purpose |
|---|---|
| `tolerance_kit.stl` | pin/hole fit calibration |
| `elastic_helper.stl` | elastic/hair-band fit |
| `hinge_stress_coupon.stl` | hinge boss print quality and layer adhesion |
| `tooth_slot_coupon.stl` | tooth and slot geometry |
| `snap_latch_coupon.stl` | latch feel without risking full clip |
| `comfort_radius_coupon.stl` | tooth-tip comfort comparison |

## Physical validation

Physical validation should be treated as data collection, not pass/fail ego.

Record:

- material
- nozzle size
- layer height
- walls/perimeters
- infill
- orientation
- pin fit
- hinge motion
- tooth comfort
- closing force
- visible failure mode

Use `lesson/TEST_LOG_TEMPLATE.md`.
