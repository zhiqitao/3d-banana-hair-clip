# Changelog

## Hook interlock + slimmer hinge comfort pass

- Smoothed the arm-to-hook transition with an added root fairing so the hook no
  longer stands off the arm like a separate lump.
- Added a small inward retaining beak at each hook tip so the two arms have a
  better chance of catching each other when clamped shut.
- Shortened the hinge Y-span and narrowed the cheek bridges to reduce the thick,
  overbuilt look around the hinge block.
- Moved the fixed pin head to the scalp side and reshaped it as a lower-profile
  round-edged head, while keeping the cotter hole and cotter retention on the
  outer side.
- Regenerated fit-demo STLs, renders, and the hinge simulation report. The
  updated printable parts remain watertight and the hinge sanity check still
  passes; slicer support/orientation review is still required for the arms.

## Smoother hook, hinge, and actual-STL preview

- Reworked the top hook curl with a smaller continuous path and a rounded
  high-resolution cap, so the latch end no longer presents as a chopped flat
  polygonal surface in slicer previews.
- Increased arm, tooth, hinge-bridge, hinge-barrel, and rounded-cap tessellation
  to reduce the faceted/cheap-looking STL surface in Bambu Studio.
- Replaced rectangular hinge anchor blocks with rounded swept cheek bridges,
  keeping the interleaved barrel hinge and real pin bore while making the hinge
  area less blocky against the head.
- Updated the render pipeline to use the fused printable STL pieces rather than
  pre-boolean construction shells, so demo images match what is loaded into
  Bambu Studio.
- Regenerated fit-demo STLs and preview renders. Validation confirms each
  individual printable STL is watertight and one connected component; slicer
  checks still recommend support/orientation review for the curved arms.

## Fused printable arm shells

- Fixed the Bambu Studio floating-shell problem by boolean-unioning each arm
  from its body, teeth, hinge leaves, hook, and tulip relief before STL export.
- Embedded tooth roots deeper into the arm body and rebuilt the top hooks so
  they overlap into the arm instead of sitting beside it.
- Added hinge cheek geometry so the barrel leaves are physically connected to
  the arm bodies while preserving the pin bore.
- Added `manifold3d` as the local mesh-union dependency for the fit-demo STL
  export path.
- Updated printability validation to report disconnected component count; each
  individual printable STL now reloads as one watertight component.
- Changed the four individual printable STL exports to be pre-oriented for
  Bambu Studio import. The assembled orientation is now kept only in the visual
  fit/demo STL outputs.

## Printable hinge bores + visible tulip face relief

- Replaced the visual-only hinge barrels in the fit-demo STL generator with
  hollow annular barrels, so both arms now have real pin bores.
- Rebuilt the hinge pin as a smooth clevis-style pin with a real transverse
  cotter hole near the outward flange.
- Replaced the decorative cotter concept with a straight printed cotter peg and
  pull loop that aligns with the hole through the pin.
- Moved the tulip decoration off the narrow spine edge and onto the broad flat
  arm face. The motif is now shallow filled tulip relief pads so Bambu Studio
  shows recognizable geometry instead of tiny diamond marks.
- Regenerated fit-demo STLs, preview renders, hinge simulation image/report,
  and the one-colour build-plate STL.
- Re-ran validation: all fit-demo printable STLs reload as watertight, hinge
  simulation passes, CadQuery STEP validation passes, and printability still
  warns that support/slicer review is required.

## Hinge comfort + wider embedded tulip relief

- Reduced the scalp-facing hinge pin protrusion by replacing the round inner
  head with a low-profile tip that stays close to the barrel face.
- Widened the hinge to a 16 mm Y-span and moved the larger retaining flange to
  the outward-facing side, keeping stability while moving bulk away from the
  head-contact side.
- Made the embedded tulip-vine relief slightly wider and more visible while
  keeping it shallow, connected, and same-colour for a molded-plastic look.
- Regenerated the fit-demo STLs and preview renders.
- Re-ran hinge simulation, per-piece watertight STL checks, and the no-slicer
  printability check. The geometry is watertight, but slicer review is still
  required because overhang/support warnings remain.

## Connected tulip relief + restored STEP workflow

- Replaced separate raised rose-bead decorations with a continuous tulip-vine
  relief embedded into each arm spine. Each side's decoration is now one
  watertight connected relief body instead of many isolated spheres.
- Rounded the fit-demo arm and tooth sweep sections so edges read more like
  molded plastic and less like sharp rectangular prototype bars.
- Made the tulip relief subtle and same-colour in renders, closer to an
  embedded pattern than stand-out flower buds.
- Regenerated the fit-demo STLs and renders, including a clearer top-down
  one-colour build-plate preview.
- Restored the design-final STL fallback generator required by the CadQuery
  workflow and regenerated `outputs_step/` plus matching `outputs_cad_stl/`
  files for Onshape/CAD handoff.
- Re-ran CadQuery validation: STEP files exist, are non-empty, and matching
  CAD-derived STLs are watertight.

## Robust barrel-knuckle hinge + cotter pin retention + repo cleanup

- Redesigned hinge from thin webs (1.5 mm dia, failure-prone) to a solid
  bridge block + three interleaved barrel cylinders (7 mm OD, 14 mm Y-span).
- Arm depth is now constant at 4.5 mm throughout — no taper at the hinge end,
  which would crack under PLA/PETG in daily use.
- Split hinge into four distinct printable pieces: left arm (outer barrels),
  right arm (inner barrel), pin, and cotter. Each piece rendered in a distinct
  colour in all preview images.
- Replaced dual symmetric pin caps (uninsertable) with a proper retention
  design: fixed head flange on entry side + printed U-shaped hairpin cotter
  through a transverse bore near the exit tip.
- Exported per-piece STLs: `arm_left.stl`, `arm_right.stl`, `hinge_pin.stl`,
  `hinge_cotter.stl` in `outputs_fit_demo/`.
- Removed obsolete generators (`banana_clip_design_final.py`,
  `banana_clip_v8_final.py`, `validate_geometry.py`), old output directories
  (`outputs/`, `outputs_cad_stl/`, `outputs_step/`), stale docs, and old
  render assets.
- Rewrote README to describe the four-piece print-and-assemble workflow.

## Fit-demo redesign: flat strip arms + clean pin hinge

- Rewrote `scripts/fit_demo_head_clip.py` arm geometry from round elliptical tubes to
  flat rectangular-section strips (11 mm wide face, 4.5 mm deep), matching the
  proportions of real banana clips in the reference photos.
- Replaced cylindrical post teeth attached to a ridge with direct cylindrical posts
  (r=1.35 mm, 10.5 mm long) projecting from the inner face of the flat strip,
  spaced ~6 mm — matching the dense-comb appearance in the reference photos.
- Replaced the exposed barrel-knuckle hinge with a minimal clean-plastic hinge:
  a small sphere at the pivot, Y-axis pin-head discs (the only visible hardware),
  and thin webs to each arm root.  No external knuckles or barrel hardware shown.
- Replaced the previous large wire hooks with proportional curled J-hooks (r≈2 mm)
  that taper and curl inward — matching the latch hooks in the reference photos.
- Removed the decorative inlay (the flat strip spine is already clean).
- Updated render color list to remove the inlay layer; all four renders regenerated.
- Hinge kinematic simulation still passes all checks.

## Front-back hinge coupon + additional renders

- Added `cadquery/banana_clip_cq.py: build_fb_hinge_coupon()` — a CadQuery B-rep
  solid with three printable pieces: outer knuckle (two Y-axis barrels), inner
  knuckle (one Y-axis barrel), and a test pin. Dimensions match the kinematically
  validated front-back hinge in `scripts/fit_demo_head_clip.py` (barrel_r=1.65,
  bore_r=0.85, pin_r=0.72, clearance=0.40). All three pieces export as one watertight
  STEP and STL for print testing before modifying the main arm geometry.
- Added `fb_hinge_coupon` to `cadquery/config_cq.py COUPON_PARTS`, so
  `cadquery/validate_cq.py` checks the STEP and STL automatically.
- Added two new clip-only renders to `scripts/fit_demo_head_clip.py`:
  `assets/clip_rear_view.png` (looking at the outer spine face) and
  `assets/clip_three_quarter.png` (diagonal back view), both with auto-fit framing.
- All 70 CadQuery validation checks pass; hinge simulation still passes.

## Curved-arm normal tooth correction

- Corrected tooth orientation so teeth grow along each curved arm's local inward normal instead of a global up/down direction.
- Updated receiving slots to follow the matching local arm tangent/normal frame.
- Regenerated mesh fallback outputs, CAD STEP files, CAD-derived STLs, previews, and validation reports.
- Changed CAD-derived STL export to high-precision ASCII tessellation from the OpenCascade solid so validation reloads remain watertight after the normal-following geometry change.

## True CAD-kernel CadQuery version

- Added `cadquery/banana_clip_cq.py` to generate OpenCascade B-rep solids.
- Added explicit CadQuery workflow files: `config_cq.py`, `export_all.py`, and `validate_cq.py`.
- Added STEP exports under `outputs_step/` and matching CAD-derived STL exports under `outputs_cad_stl/`.
- Preserved the design-final profile math while keeping the STL-first generator as a fallback.
- Added CadQuery tests for generated files, non-empty STEP files, watertight STL exports, pin clearance, and tooth/slot 2D collision checks.
- Added `docs/CADQUERY_VALIDATION_REPORT.md` generation.
- Added `docs/TRUE_CAD_KERNEL_VERSION.md` with STL-vs-STEP notes, Onshape import guidance, and physical validation boundaries.

## Design-Phase Final

- Added `scripts/banana_clip_design_final.py` as the final design-phase generator.
- Added softened tooth-tip geometry via `TOOTH_EDGE_RADIUS_MM`.
- Added first-impression coupon plate: `coupon_plate_first.stl`.
- Added new engineering coupons:
  - `hinge_stress_coupon.stl`
  - `tooth_slot_coupon.stl`
  - `snap_latch_coupon.stl`
  - `comfort_radius_coupon.stl`
- Added material profile guidance in `scripts/config.py`.
- Added GitHub Actions geometry validation workflow.
- Added final design-phase docs:
  - `docs/DESIGN_PHASE_FINAL_REVIEW.md`
  - `docs/FIRST_IMPRESSION_DEMO_PLAN.md`
  - `docs/MATERIAL_PROFILES.md`
  - `docs/FAILURE_MODES_AND_EFFECTS.md`
  - `docs/VALIDATION_STRATEGY.md`
  - `docs/SNAP_LATCH_DECISION.md`
- Updated README to describe the final design workflow.

## Final v8 annotated package

- Added detailed engineering iteration history from v3 through Final v8.
- Added debug log covering arm overlap, floating hinge barrels, pin clearance, tooth collision, tolerance uncertainty, and STL editability limits.
- Added design-decision document explaining major tradeoffs.
- Added version-by-version review notes for teaching and future revision.
- Added engineering notebook with next physical test plan and likely first failures.

## Final v8

- Rebuilt arm export as layered Z-band profiles instead of same-part overlapping hinge solids.
- Increased tooth root embedding so teeth are structurally connected to the arm body.
- Preserved long tapered teeth and receiving slots.
- Added elastic helper test coupon.
- Added all-parts print plate as a convenience preview/plate file.
- Expanded validation and teaching documents.

## v7 baseline

- Added tolerance kit and pin variants.
- Added print guide and CAD migration docs.
