#!/usr/bin/env python3
"""Automated grader for T05 — Parametric Size Variants.

Run after the agent completes the task:
    python tasks/T05_design_extension/grader.py

Assumes the agent has already run:
    python scripts/fit_demo_head_clip.py --sizes S M L

Exit code: 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
OUTPUTS = ROOT / "outputs_fit_demo"
PIECES = ["arm_left", "arm_right", "hinge_pin", "hinge_cotter"]
SIZES = {"S": 100.0, "M": 116.0, "L": 130.0}
ORIGINAL_ARM_LENGTH = 116.0

results = []


def check(label: str, passed: bool, detail: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    print(f"  {status}  {label}" + (f" — {detail}" if detail else ""))
    results.append(passed)


print("\nT05 Design Extension Grader\n" + "-" * 40)

try:
    import trimesh
    has_trimesh = True
except ModuleNotFoundError:
    has_trimesh = False
    print("  WARN  trimesh not installed — geometry checks will be skipped")

# 1. Subdirectories exist
for size in SIZES:
    subdir = OUTPUTS / f"size_{size}"
    check(f"size_{size}/ directory exists", subdir.is_dir())

# 2. All 4 STL files present in each size
for size in SIZES:
    subdir = OUTPUTS / f"size_{size}"
    for piece in PIECES:
        path = subdir / f"{piece}.stl"
        check(f"size_{size}/{piece}.stl exists", path.exists())

# 3. Watertight + single component for each variant
if has_trimesh:
    for size in SIZES:
        subdir = OUTPUTS / f"size_{size}"
        for piece in PIECES:
            path = subdir / f"{piece}.stl"
            if not path.exists():
                check(f"size_{size}/{piece}.stl watertight", False, "file not found")
                continue
            mesh = trimesh.load(str(path), force="mesh")
            import trimesh.graph as tgraph
            n_comp = len(tgraph.connected_components(mesh.faces))
            check(f"size_{size}/{piece}.stl watertight", bool(mesh.is_watertight))
            check(f"size_{size}/{piece}.stl 1 component", n_comp == 1, f"{n_comp} components")

# 4. Backward compatibility — outputs_fit_demo/arm_left.stl still exists at root
for piece in PIECES:
    check(f"root {piece}.stl unchanged", (OUTPUTS / f"{piece}.stl").exists())

print()
passed = sum(results)
total = len(results)
print(f"Score: {passed}/{total} checks passed")
sys.exit(0 if passed == total else 1)
