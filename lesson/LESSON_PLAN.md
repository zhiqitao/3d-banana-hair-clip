# Lesson Plan: From Idea to Printable Mechanism

## Session 1 — Analyze the object

- Look at a real banana clip or pictures.
- Identify hinge, arms, teeth, grip hooks, and closing force.
- Draw a simple side sketch.

## Session 2 — Parameters

Open `scripts/config.py` and discuss:

- `ARM_LENGTH_MM`
- `ARM_WIDTH_MM`
- `TOOTH_COUNT`
- `TOOTH_LENGTH_MM`
- `PIN_CLEARANCE_MM`
- `SLOT_CLEARANCE_MM`

Ask: which parameters affect fit, strength, comfort, and printability?

## Session 3 — Validation

Run:

```bash
python scripts/validate_geometry.py
```

Explain why computer validation catches some problems but not all problems.

## Session 4 — First print

Print:

1. tolerance kit
2. elastic helper
3. arms and loose pin

Record results in a table.

## Session 5 — Engineering change order

Change exactly one parameter, regenerate, and explain why.

Example: if teeth scrape, increase `SLOT_CLEARANCE_MM`.
