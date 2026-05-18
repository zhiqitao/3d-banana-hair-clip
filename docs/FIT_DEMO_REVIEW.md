# Head/Hair Fit Demo Review

The reference photos show that the previous flat-profile interpretation is misleading. A real banana clip is closer to a curved pair of narrow rails on the head, with short teeth growing from the inner rail surface.

## What the Photos Clarify

- The teeth are arranged along the curved arm, but each tooth projects primarily away from the local inner surface.
- The teeth should not be modeled as long triangular silhouettes in a flat 2D outline.
- The hinge is a transverse mechanism at the arm root, not just a flat circular boss in plan view.
- A fit model with head and hair volume is useful because it exposes whether the clip surrounds hair or merely looks like a comb in isolation.
- The examples split into two related families: hinged banana clips with dense fine comb teeth, and single-piece curved comb/barrettes with larger U-shaped teeth. This project should stay in the hinged banana clip family.
- The outer arm should read as a flattened curved rail or spine, not as a round rod.
- Teeth should emerge from an inner ridge/channel and remain denser, shorter, and more post-like than the older flat triangular teeth.

## Current Fit Demo

Run:

```bash
python scripts/fit_demo_head_clip.py
```

Generated artifacts:

```text
assets/photo_refactored_fit_demo.png         # clip + head, front-facing view
assets/actual_clip_hinge_side.png            # clip only, side view (azim=0)
assets/clip_rear_view.png                    # clip only, rear/outer-spine view (azim=-90, elev=18)
assets/clip_three_quarter.png               # clip only, three-quarter rear (azim=-140, elev=25)
outputs_fit_demo/photo_refactored_fit_demo_clip.stl
outputs_fit_demo/photo_refactored_head_hair_clip_fit.stl
```

The rear and three-quarter renders expose the outer spine and hook geometry
from angles not visible in the side view, which is important for catching
aesthetic issues before printing.

This demo is intentionally separate from the validated design-final model. It is a visual/mechanical direction check for the next CAD rebuild.

## Design Implication

The next production-quality CAD revision should rebuild the arms as swept 3D rails and add teeth as rounded posts normal to the inner rail surface. The earlier 2D profile approach remains useful for validation logic, but it is not the right final architecture for the photographed object.

## Refactor Direction

The photo-informed refactor should use:

- swept flattened rails with rounded ends
- a small inner tooth ridge
- dense rounded comb teeth normal to the inner ridge
- a compact block-like hinge at the root
- curled top latch hooks with bulb tips
- head/hair fit renders as a required design review artifact before STEP/STL release
