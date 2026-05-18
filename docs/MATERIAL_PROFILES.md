# Material Profiles

The geometry defaults are conservative for a first demo. Material choice still matters.

## PLA first demo

Best for:

- clean first print
- easiest slicing
- low warping
- good dimensional accuracy

Weakness:

- brittle hinge and teeth
- poor long-term flex

Recommendation:

Use PLA for coupon plate and first visual prototype, not for the final functional clip.

## PETG functional prototype

Best for:

- better toughness than PLA
- more forgiving flex
- practical home printing

Weakness:

- stringing
- slightly worse dimensional crispness
- needs cleaner tuning

Recommendation:

Use PETG for the first serious functional banana clip.

## Nylon / PA advanced prototype

Best for:

- toughness
- flex
- durability

Weakness:

- moisture sensitivity
- harder print setup
- often needs drying and enclosure

Recommendation:

Use only after the geometry is proven in PLA/PETG.

## Why material profiles are not auto-applied

The repo documents material profiles instead of silently changing geometry because printer, slicer, nozzle, filament, humidity, and orientation all interact. Automatic material scaling without physical measurements can make the first print worse.
