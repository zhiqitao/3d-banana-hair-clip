# True CAD-Kernel Version

The original design-final generator remains the print-first fallback in `scripts/banana_clip_design_final.py`. The CadQuery version in `cadquery/banana_clip_cq.py` uses the same profile math, then asks OpenCascade to create B-rep solids and STEP files.

## STL vs STEP

STL is a triangle mesh. It is excellent for slicers and quick printing, but it does not preserve design intent such as analytic holes, faces, edges, or editable features.

STEP is a CAD exchange format. It carries boundary-representation geometry that CAD systems can inspect, measure, repair, and remodel more cleanly than a mesh. For this project, STEP is the better handoff format for Onshape or another CAD package.

## Why CadQuery/OpenCascade

CadQuery is a Python CAD layer over OpenCascade. OpenCascade is a real CAD kernel, so the arms, pins, hinge holes, receiving slots, and coupons are exported as CAD solids rather than triangle mesh assemblies. The design still starts from the validated 2D parametric profiles so the CadQuery path stays aligned with the STL-first path.

The current CadQuery outputs are written to:

```text
outputs_step/
  upper_arm.step
  lower_arm.step
  pin_loose.step
  pin_nominal.step
  pin_snug.step
  tolerance_kit.step
  tooth_slot_coupon.step

outputs_cad_stl/
  upper_arm.stl
  lower_arm.stl
  pin_loose.stl
  pin_nominal.stl
  pin_snug.stl
  tooth_slot_coupon.stl
```

Each STEP file has a matching STL export in `outputs_cad_stl/` for slicer checks.

## Reproduction

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-cadquery.txt
python cadquery/export_all.py
python cadquery/validate_cq.py
python -m unittest tests/test_cadquery_generator.py
```

## Importing STEP Into Onshape

1. Open an Onshape document.
2. Click the `+` tab button and choose `Import`.
3. Upload the desired file from `outputs_step/`, such as `upper_arm.step`.
4. Choose import into the current document.
5. Open the imported Part Studio and inspect the solids.
6. If you want an editable production model, rebuild the successful printed dimensions as native Onshape sketches/features after physical validation.

## What Becomes Editable

STEP import gives Onshape real CAD faces, edges, holes, and solids to measure and reference. It is much better than importing STL mesh triangles.

It does not recreate the Python parameters or a native Onshape feature tree. For teaching, this is still valuable: the student can inspect true CAD solids, measure design features, and then rebuild selected dimensions as sketches after the printed prototype proves what should change.

## What Still Requires Physical Validation

The CAD kernel can prove cleaner geometry, but it cannot prove product behavior. These still require printing, assembly, and measurement:

- hinge feel and wear
- pin friction on the target printer
- elastic force and user feel
- tooth comfort in hair
- material flexibility and layer adhesion
- long-term durability
- whether the conservative elastic-assisted closure should become an integrated snap latch
