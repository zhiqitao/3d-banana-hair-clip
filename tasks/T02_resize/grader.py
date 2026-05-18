#!/usr/bin/env python3
"""Automated grader for T02 — Resize for a Smaller Head.

Run after the agent completes the task:
    python tasks/T02_resize/grader.py

Exit code: 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import config as C

results = []


def check(label: str, passed: bool, detail: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"  {status}  {label}" + (f" — {detail}" if detail else ""))
    results.append(passed)


print("\nT02 Resize Grader\n" + "-" * 40)

TARGET_LENGTH = 100.0
SCALE = TARGET_LENGTH / 116.0  # ratio from original

# 1. Arm length
check("ARM_LENGTH_MM == 100",
      abs(C.ARM_LENGTH_MM - TARGET_LENGTH) < 0.5,
      f"got {C.ARM_LENGTH_MM}")

# 2. Tooth start proportionally scaled (expected ~11.6mm, allow ±3mm)
expected_start = 13.5 * SCALE
check("TOOTH_START_MM proportionally scaled",
      abs(C.TOOTH_START_MM - expected_start) < 3.0 and C.TOOTH_START_MM > 10,
      f"got {C.TOOTH_START_MM:.1f}, expected ~{expected_start:.1f}")

# 3. Tooth end proportionally scaled (expected ~84.5mm, allow ±5mm)
expected_end = 98.0 * SCALE
check("TOOTH_END_MM proportionally scaled",
      abs(C.TOOTH_END_MM - expected_end) < 5.0,
      f"got {C.TOOTH_END_MM:.1f}, expected ~{expected_end:.1f}")

# 4. Tooth end within arm bounds
check("TOOTH_END_MM < ARM_LENGTH_MM - 10",
      C.TOOTH_END_MM < C.ARM_LENGTH_MM - 10,
      f"{C.TOOTH_END_MM:.1f} vs limit {C.ARM_LENGTH_MM - 10:.1f}")

# 5. Elastic hole within arm bounds
check("ELASTIC_HOLE_X_MM < ARM_LENGTH_MM - 5",
      C.ELASTIC_HOLE_X_MM < C.ARM_LENGTH_MM - 5,
      f"got {C.ELASTIC_HOLE_X_MM:.1f}, limit {C.ARM_LENGTH_MM - 5:.1f}")

# 6. STL files exist
import trimesh
outputs = ROOT / "outputs_fit_demo"
all_watertight = True
for piece in ["arm_left", "arm_right", "hinge_pin", "hinge_cotter"]:
    path = outputs / f"{piece}.stl"
    if not path.exists():
        check(f"{piece}.stl exists", False, "file not found")
        all_watertight = False
        continue
    mesh = trimesh.load(str(path), force="mesh")
    wt = bool(mesh.is_watertight)
    check(f"{piece}.stl watertight", wt)
    if not wt:
        all_watertight = False

print()
passed = sum(results)
total = len(results)
print(f"Score: {passed}/{total} checks passed")
sys.exit(0 if passed == total else 1)
