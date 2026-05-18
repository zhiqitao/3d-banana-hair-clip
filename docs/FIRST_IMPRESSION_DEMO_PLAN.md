# First-Impression Demo Plan

The first impression should communicate discipline, not gambling.

## What to show first

1. `assets/preview_closed.png` — shows the intended closed geometry.
2. `assets/preview_open.png` — shows the hinge/opening concept.
3. `assets/preview_exploded.png` — shows that it is made of separate parts.
4. `docs/DESIGN_PHASE_FINAL_REVIEW.md` — shows engineering tradeoffs.
5. Git history — shows progressive improvement rather than a one-shot model.

## Best first physical print

Print:

```text
outputs/coupon_plate_first.stl
```

This plate demonstrates:

- tolerance testing
- elastic hole testing
- hinge boss testing
- tooth/slot testing
- snap latch exploration
- comfort-radius comparison

It is faster, cheaper, and less risky than printing the entire clip first.

## Best first full clip print

After the coupon plate looks good:

```text
outputs/upper_arm.stl
outputs/lower_arm.stl
outputs/pin_loose.stl
```

Use a small elastic/hair band through the rear elastic holes for closing force.

## What not to do

Do not print `assembly_closed.stl` as one piece. It is a visual preview only.

Do not start with the snap latch as the primary retention method. Snap latches are material-sensitive and should be coupon-tested first.

## Suggested explanation

> This is not about making a cheap hair clip. This is about teaching design review, tolerance testing, mechanical iteration, and evidence-based engineering before we spend time and money on the full print.
