"""Configuration for the CadQuery/OpenCascade export workflow."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_STEP = ROOT / "outputs_step"
OUTPUTS_CAD_STL = ROOT / "outputs_cad_stl"
DOCS = ROOT / "docs"

MAIN_PARTS = [
    "upper_arm",
    "lower_arm",
    "pin_loose",
    "pin_nominal",
    "pin_snug",
]

COUPON_PARTS = [
    "tolerance_kit",
    "elastic_helper",
    "hinge_stress_coupon",
    "tooth_slot_coupon",
    "snap_latch_coupon",
    "comfort_radius_coupon",
    "coupon_plate_first",
    "fb_hinge_coupon",
]

ALL_PARTS = MAIN_PARTS + COUPON_PARTS

STEP_SUFFIX = ".step"
STL_SUFFIX = ".stl"

STL_TOLERANCE = 0.04
STL_ANGULAR_TOLERANCE = 0.12
