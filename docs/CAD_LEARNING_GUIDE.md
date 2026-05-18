# Real-Life CAD Design Process Lesson

This project is designed as a hands-on CAD lesson, not just a hair clip.

## 1. Observe the real object

Questions to ask:

- Where is the hinge axis?
- Which parts need to rotate?
- Where do the teeth interleave?
- What prevents the clip from opening by itself?
- Which features are cosmetic, and which are structural?

## 2. Turn observation into requirements

Example requirements:

- Two arms must not overlap when closed.
- Teeth must grip hair but not collide with the other arm.
- Hinge pin must fit with clearance.
- Print must be possible on a normal FDM printer.
- The model must be adjustable with parameters.

## 3. Build a simple model first

The early versions looked good but had hidden problems:

- floating hinge barrels
- arm body overlap
- missing pin hole
- teeth colliding with the opposite arm

This is a normal engineering lesson: a pretty model is not automatically a working design.

## 4. Validate before printing

Run:

```bash
python scripts/validate_geometry.py
```

The validation is not a replacement for a real print, but it catches obvious mistakes.

## 5. Print small tests first

Print the tolerance kit and elastic helper first. This teaches that CAD dimensions are ideal, but printed dimensions are real.

## 6. Iterate after the first physical test

Measure:

- pin fit
- hinge smoothness
- tooth scraping
- closing force
- comfort in hand
- whether hair actually stays in place

Then change one parameter at a time.
