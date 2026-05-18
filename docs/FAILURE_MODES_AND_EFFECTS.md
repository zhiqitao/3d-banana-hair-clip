# Failure Modes and Effects Review

| Failure mode | Likely cause | Design-phase mitigation | Physical-test action |
|---|---|---|---|
| Pin too tight | Hole shrinkage, elephant foot, slicer compensation | Three pin sizes + tolerance kit | Start with loose pin; sand or reprint pin |
| Pin too loose | Oversized hole or undersized pin | Nominal and snug pins included | Try snug pin or reduce clearance |
| Hinge snaps | Layer orientation, brittle material, thin web | Larger hinge boss + hinge stress coupon | Print in PETG; increase boss radius |
| Teeth break | Teeth too thin, wrong material, layer direction | Tapered teeth + softened edges | Increase tooth width/root inset |
| Teeth scratch | Sharp tips or edges | Tooth edge rounding + comfort coupon | Increase `TOOTH_EDGE_RADIUS_MM` |
| Clip does not hold hair | Weak closing force | Elastic retention holes | Stronger/smaller elastic; later integrate latch |
| Snap latch fails | Material sensitivity | Snap latch coupon kept separate | Tune latch geometry after coupon test |
| Arms collide when closing | Bad gap/slot math | Validation checks body and tooth collisions | Increase gap or slot clearance |
| Slots print poorly | Slots too narrow or stringing | Oversized slot clearance | Reduce speed, tune retraction, or widen slots |
| Model looks toy-like | Lack of polish or explanation | Preview assets + docs + Git history | Present as engineering kit, not just object |
