"""Banana Clip design-phase final configuration. Units: millimeters/degrees."""
ARM_LENGTH_MM = 116.0
ARM_WIDTH_MM = 7.8
ARM_THICKNESS_MM = 4.5
ARM_GAP_CLOSED_MM = 4.8
CURVE_BOW_MM = 13.2
CENTERLINE_STEPS = 260
TOOTH_COUNT = 32
TOOTH_WIDTH_MM = 0.82
TOOTH_LENGTH_MM = 5.20
TOOTH_START_MM = 13.5
TOOTH_END_MM = 98.0
TOOTH_ROOT_INSET_MM = 0.85
TOOTH_TIP_TAPER = 0.38
TOOTH_BASE_FILLET_MM = 0.06
TOOTH_EDGE_RADIUS_MM = 0.10
SLOT_CLEARANCE_MM = 0.54
SLOT_EXTRA_DEPTH_MM = 1.15
SLOT_MOUTH_MM = 0.82
SLOT_TAPER = 1.7
HINGE_X_MM = -3.0
HINGE_RADIUS_MM = 4.6
HINGE_ATTACH_X_MM = 3.8
HINGE_ATTACH_RADIUS_MM = 4.45
PIN_RADIUS_MM = 1.12
PIN_CLEARANCE_MM = 0.46
HINGE_KNUCKLE_GAP_MM = 0.48
PIN_OVERHANG_MM = 1.35
PIN_HEAD_RADIUS_MM = 2.75
PIN_HEAD_THICKNESS_MM = 0.9
PIN_VARIANTS_MM = {'pin_loose': 1.02, 'pin_nominal': PIN_RADIUS_MM, 'pin_snug': 1.20}
HOOK_OUTER_R_MM = 6.8
HOOK_INNER_R_MM = 2.8
HOOK_SWEEP_DEG = 275
HOOK_STEPS = 72
ELASTIC_HOLE_ENABLED = True
ELASTIC_HOLE_X_MM = 104.5
ELASTIC_HOLE_RADIUS_MM = 1.65
ELASTIC_HOLE_EDGE_CLEARANCE_MM = 1.40
ELASTIC_CHANNEL_RADIUS_MM = 1.10
OPEN_ANGLE_DEG = 36
EXPLODED_Z_GAP_MM = 5.0
CIRCLE_SEGMENTS = 160
BUFFER_EPS_MM = 0.008
SIMPLIFY_MM = 0.002
TOLERANCE_PIN_RADII_MM = [1.02, 1.06, 1.10, 1.14, 1.18, 1.22]
TOLERANCE_HOLE_RADII_MM = [1.46, 1.52, 1.58, 1.64, 1.70, 1.76]
COUPON_THICKNESS_MM = 4.0
TOLERANCE_KIT_ENABLED = True


# Design-phase guidance profiles. The default geometry is conservative for PLA/PETG.
# These are documented rather than automatically applied because material, printer,
# slicer, nozzle, and orientation interact; changing geometry without test data can
# make the first full print worse.
MATERIAL_PROFILES = {
    "PLA_FIRST_DEMO": {"pin_clearance_mm": 0.46, "slot_clearance_mm": 0.54, "note": "safe first demo; easiest print"},
    "PETG_FUNCTIONAL": {"pin_clearance_mm": 0.40, "slot_clearance_mm": 0.50, "note": "better flex and toughness; can string"},
    "NYLON_ADVANCED": {"pin_clearance_mm": 0.35, "slot_clearance_mm": 0.46, "note": "best toughness; harder printing/drying"},
}
