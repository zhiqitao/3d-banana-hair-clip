# Onshape Migration Guide

The current model is STL-first because this environment does not have a full CAD kernel. For Onshape, the clean path is to rebuild the design from the parameter logic, not to edit STL triangles.

## Practical path

1. Open `outputs/banana_clip_v8_final_profiles.svg` as a visual reference.
2. Recreate one arm centerline sketch in Onshape.
3. Offset the centerline to create the arm body.
4. Add tooth pattern with linear pattern along the arm.
5. Add receiving slots as a matching staggered pattern.
6. Add hinge boss using circles and tangent/convex-hull-like sketch lines.
7. Extrude the Z layers:
   - upper arm: lower knuckle, middle body, upper knuckle
   - lower arm: lower body, middle knuckle, upper body
8. Add pin hole using a remove-extrude through the hinge axis.
9. Add fillets/chamfers.
10. Export STEP and STL.

## Teaching point

This is exactly how real CAD often works: use a script prototype to discover geometry, then rebuild the final version in a parametric CAD system once the layout is understood.
