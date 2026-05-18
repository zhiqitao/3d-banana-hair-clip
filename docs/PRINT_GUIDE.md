# Print Guide

## Suggested material

- PLA or PLA+ for the first educational print.
- PETG may be better for a slightly more flexible prototype.
- Do not start with brittle exotic filament.

## Suggested slicer settings

- Layer height: 0.16–0.20 mm
- Walls/perimeters: 3+
- Infill: 30–50%
- Supports: likely not needed for the flat parts if oriented as generated
- Brim: optional, useful if teeth curl upward at the edges

## Orientation

Print each arm flat. The hinge pin is printed vertically by default in this mesh export. If the pin is weak, reprint it lying down or use a small metal pin/dowel instead.

## Assembly

1. Clean stringing from teeth and slots.
2. Test pin variants using the tolerance kit.
3. Stack the upper/lower hinge knuckles.
4. Insert the loose pin first.
5. Add a small elastic loop through the rear holes or around the curled grips to provide closing force.

## Expected first-try issues

| Symptom | Likely cause | Fix |
|---|---|---|
| Pin too tight | Printer closes holes / elephant foot | Use loose pin, drill hole lightly, or increase `PIN_CLEARANCE_MM` |
| Teeth scrape | Over-extrusion or slot clearance too small | Increase `SLOT_CLEARANCE_MM` by 0.1–0.2 mm |
| Clip too weak | PLA too brittle / low infill | Use PETG, increase walls, increase arm thickness |
| Elastic does not hold | Elastic too loose | Shorter elastic or move hole position in config |
