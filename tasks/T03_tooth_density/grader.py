#!/usr/bin/env python3
"""Automated grader for T03 — Increase Tooth Density.

Run after the agent completes the task:
    python tasks/T03_tooth_density/grader.py

Exit code: 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import subprocess
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


print("\nT03 Tooth Density Grader\n" + "-" * 40)

ORIGINAL_TOOTH_START = 13.5
ORIGINAL_TOOTH_END = 98.0

# 1. Tooth count
check("TOOTH_COUNT == 40",
      C.TOOTH_COUNT == 40,
      f"got {C.TOOTH_COUNT}")

# 2. Tooth bounds not shrunk significantly
check("TOOTH_START_MM within 1mm of original",
      abs(C.TOOTH_START_MM - ORIGINAL_TOOTH_START) <= 1.0,
      f"got {C.TOOTH_START_MM:.2f}, original {ORIGINAL_TOOTH_START}")

check("TOOTH_END_MM within 1mm of original",
      abs(C.TOOTH_END_MM - ORIGINAL_TOOTH_END) <= 1.0,
      f"got {C.TOOTH_END_MM:.2f}, original {ORIGINAL_TOOTH_END}")

# 3. Printability: tooth width
check("TOOTH_WIDTH_MM >= 0.8 mm",
      C.TOOTH_WIDTH_MM >= 0.8,
      f"got {C.TOOTH_WIDTH_MM:.3f}")

# 4. Tooth bounds within arm
check("TOOTH_END_MM < ARM_LENGTH_MM - 10",
      C.TOOTH_END_MM < C.ARM_LENGTH_MM - 10,
      f"{C.TOOTH_END_MM:.1f} vs limit {C.ARM_LENGTH_MM - 10:.1f}")

# 5. STL geometry
try:
    import trimesh
    outputs = ROOT / "outputs_fit_demo"
    for piece in ["arm_left", "arm_right", "hinge_pin", "hinge_cotter"]:
        path = outputs / f"{piece}.stl"
        if not path.exists():
            check(f"{piece}.stl watertight", False, "file not found")
            continue
        mesh = trimesh.load(str(path), force="mesh")
        check(f"{piece}.stl watertight", bool(mesh.is_watertight))
except ModuleNotFoundError:
    print("  SKIP  trimesh not installed — geometry checks skipped")

# 6. Hinge simulation
proc = subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "simulate_hinge.py")],
    capture_output=True, text=True, cwd=str(ROOT),
)
sim_ok = "PASSED" in (proc.stdout + proc.stderr) and proc.returncode == 0
check("Hinge simulation PASSED", sim_ok,
      "" if sim_ok else "simulation reported failures — see simulate_hinge.py output")

print()
passed = sum(results)
total = len(results)
print(f"Score: {passed}/{total} checks passed")
sys.exit(0 if passed == total else 1)
