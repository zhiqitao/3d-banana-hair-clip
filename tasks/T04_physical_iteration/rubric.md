# T04 Evaluator Rubric

Use this to score the human-evaluation components of T04.

## Expected diagnoses and fixes

These are the correct answers. Do not share with agents before evaluation.

### Problem 1 — Pin cannot insert

**Root cause:** `PIN_CLEARANCE_MM` is 0.46 mm for the nominal pin in the current
PETG profile. FDM printers typically under-size holes by 0.1–0.2 mm due to
material expansion and elephant foot. The effective bore is smaller than designed.

**Correct fix:** Increase `PIN_CLEARANCE_MM` by 0.08–0.15 mm (e.g., 0.54–0.58 mm
for PETG) **or** direct the user to use the `pin_loose` variant (PIN_RADIUS_MM=1.02).
A config change to `PIN_CLEARANCE_MM` = 0.54 is the most direct solution.

**Acceptable alternative:** Add a new PETG-specific pin clearance value to
`MATERIAL_PROFILES` and document how to apply it.

**Not acceptable:** Suggesting to drill out the bore manually (not a design fix).

---

### Problem 2 — Teeth scrape on close

**Root cause:** `SLOT_CLEARANCE_MM` = 0.54 mm is insufficient for PETG stringing
and elephant-foot effects. The slot mouth (`SLOT_MOUTH_MM` = 0.82 mm) is nearly
the same as the tooth width (`TOOTH_WIDTH_MM` = 0.82 mm) — zero clearance at entry.

**Correct fix:** Increase `SLOT_CLEARANCE_MM` by 0.08–0.15 mm (e.g., 0.62–0.68 mm)
**and/or** increase `SLOT_MOUTH_MM` by 0.1–0.2 mm to widen the entry chamfer.

**Not acceptable:** Suggesting to file the teeth manually.

---

### Problem 3 — Hinge wobble after 20 cycles

**Root cause:** `HINGE_KNUCKLE_GAP_MM` = 0.48 mm. For PETG, this gap may be tight
enough to create initial friction and wear. A slightly larger gap (0.55–0.65 mm)
would reduce wear while still maintaining alignment.

**Correct fix:** Increase `HINGE_KNUCKLE_GAP_MM` to 0.55–0.65 mm.

**Note:** This is in tension with Problem 1 (more clearance = more wobble). The
agent should acknowledge this and choose a balanced value.

---

### Problem 4 — Hook does not latch reliably

**Root cause:** `HOOK_SWEEP_DEG` = 275° and `HOOK_INNER_R_MM` = 2.8 mm. A larger
sweep angle (285–300°) would curl the hook tip further inward, making it more
likely to catch. Alternatively, reducing `HOOK_INNER_R_MM` makes the hook curl
tighter.

**Correct fix:** Increase `HOOK_SWEEP_DEG` to 285–295° **or** decrease
`HOOK_INNER_R_MM` to 2.2–2.5 mm.

**Note:** Changing `HOOK_INNER_R_MM` also affects hook clearance — must regenerate
and verify arms don't collide.

---

## Scoring guidance for evaluators

Award full diagnosis points (12/problem) if the agent:
- Identifies the correct config parameter
- Gives a direction of change (increase/decrease) that is correct
- Gives a magnitude that is physically reasonable

Award partial diagnosis points (6/problem) if the agent:
- Identifies the right general area (e.g., "pin clearance") but not the exact parameter
- Gets the direction right but the magnitude unreasonably large or small

Award 0 diagnosis points if the agent:
- Blames the printer (not the design)
- Recommends post-print manual fixes without any design change
- Identifies the wrong parameter
