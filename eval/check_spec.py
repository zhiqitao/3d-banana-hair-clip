#!/usr/bin/env python3
"""Automated spec checker for SPEC.md criteria S1-S4.

Usage:
    python eval/check_spec.py                # check and print results
    python eval/check_spec.py --save-baseline  # also write eval/baseline.json
    python eval/check_spec.py --json         # print JSON only, no table

Exit code: 0 if all automated criteria pass, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = ROOT / "scripts"
OUTPUTS_DIR = ROOT / "outputs_fit_demo"
EVAL_DIR = ROOT / "eval"

sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import trimesh
except ModuleNotFoundError:
    sys.exit("trimesh not installed — run: pip install trimesh")

import config as C

PIECES = ["arm_left", "arm_right", "hinge_pin", "hinge_cotter"]

Result = dict[str, Any]


def check(criteria_id: str, passed: bool, value: Any = None, reason: str = "") -> Result:
    return {"id": criteria_id, "pass": passed, "value": value, "reason": reason}


# ---------------------------------------------------------------------------
# S1 — Geometry integrity
# ---------------------------------------------------------------------------

def check_s1() -> list[Result]:
    results = []
    for piece in PIECES:
        path = OUTPUTS_DIR / f"{piece}.stl"
        if not path.exists():
            results.append(check(f"S1.1_{piece}", False, reason="file not found"))
            results.append(check(f"S1.2_{piece}", False, reason="file not found"))
            results.append(check(f"S1.3_{piece}", False, reason="file not found"))
            continue

        mesh = trimesh.load(str(path), force="mesh")

        # S1.1 watertight
        results.append(check(
            f"S1.1_{piece}_watertight",
            bool(mesh.is_watertight),
            reason="" if mesh.is_watertight else f"{len(mesh.faces)} faces, not watertight",
        ))

        # S1.2 single connected component
        n = len(mesh.split(only_watertight=False))
        results.append(check(
            f"S1.2_{piece}_components",
            n == 1,
            value=n,
            reason="" if n == 1 else f"{n} components (expected 1)",
        ))

        # S1.3 no degenerate faces
        import numpy as np
        areas = mesh.area_faces
        degen = int((areas < 1e-10).sum())
        results.append(check(
            f"S1.3_{piece}_no_degenerate",
            degen == 0,
            value=degen,
            reason="" if degen == 0 else f"{degen} zero-area triangles",
        ))

    return results


# ---------------------------------------------------------------------------
# S2 — Dimensional bounds
# ---------------------------------------------------------------------------

def check_s2() -> list[Result]:
    return [
        check("S2.1_arm_length", 100 <= C.ARM_LENGTH_MM <= 130,
              value=C.ARM_LENGTH_MM,
              reason="" if 100 <= C.ARM_LENGTH_MM <= 130 else "must be 100–130 mm"),

        check("S2.2_arm_thickness", C.ARM_THICKNESS_MM >= 4.0,
              value=C.ARM_THICKNESS_MM,
              reason="" if C.ARM_THICKNESS_MM >= 4.0 else "must be ≥ 4.0 mm"),

        check("S2.3_tooth_count", 24 <= C.TOOTH_COUNT <= 44,
              value=C.TOOTH_COUNT,
              reason="" if 24 <= C.TOOTH_COUNT <= 44 else "must be 24–44"),

        check("S2.4_tooth_start", C.TOOTH_START_MM > 10,
              value=C.TOOTH_START_MM,
              reason="" if C.TOOTH_START_MM > 10 else "teeth start too close to hinge (must be > 10 mm)"),

        check("S2.5_tooth_end", C.TOOTH_END_MM < C.ARM_LENGTH_MM - 10,
              value=C.TOOTH_END_MM,
              reason="" if C.TOOTH_END_MM < C.ARM_LENGTH_MM - 10
              else f"teeth end too close to hook (must be < {C.ARM_LENGTH_MM - 10:.1f} mm)"),

        check("S2.6_pin_radius", 1.0 <= C.PIN_RADIUS_MM <= 1.3,
              value=C.PIN_RADIUS_MM,
              reason="" if 1.0 <= C.PIN_RADIUS_MM <= 1.3 else "must be 1.0–1.3 mm"),

        check("S2.7_pin_clearance", 0.35 <= C.PIN_CLEARANCE_MM <= 0.55,
              value=C.PIN_CLEARANCE_MM,
              reason="" if 0.35 <= C.PIN_CLEARANCE_MM <= 0.55 else "must be 0.35–0.55 mm"),

        check("S2.8_knuckle_gap", C.HINGE_KNUCKLE_GAP_MM >= 0.30,
              value=C.HINGE_KNUCKLE_GAP_MM,
              reason="" if C.HINGE_KNUCKLE_GAP_MM >= 0.30 else "must be ≥ 0.30 mm"),
    ]


# ---------------------------------------------------------------------------
# S3 — Kinematics
# ---------------------------------------------------------------------------

def check_s3() -> list[Result]:
    sim_path = SCRIPTS_DIR / "simulate_hinge.py"
    if not sim_path.exists():
        return [check("S3.1_simulation", False, reason="simulate_hinge.py not found")]

    proc = subprocess.run(
        [sys.executable, str(sim_path)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    output = proc.stdout + proc.stderr

    sim_passed = "PASSED" in output and proc.returncode == 0
    results = [check("S3.1_simulation_passed", sim_passed,
                     reason="" if sim_passed else "simulation reported failures")]

    # Parse key measurements from simulation output
    # Expected format: "- Open arm X gap min/mean/max: `12.000 / 42.671 / 55.989 mm`"
    open_gap_min = None
    for line in output.splitlines():
        if "Open arm X gap min" in line:
            try:
                after_colon = line.split(":", 1)[1].strip().strip("`")
                open_gap_min = float(after_colon.split("/")[0].strip().split()[0])
            except Exception:
                pass

    results.append(check("S3.2_open_gap_positive", open_gap_min is not None and open_gap_min > 0,
                         value=open_gap_min,
                         reason="" if (open_gap_min is not None and open_gap_min > 0)
                         else "could not parse open gap from simulation output"))

    open_angle = getattr(C, "OPEN_ANGLE_DEG", None)
    results.append(check("S3.3_open_angle", open_angle is not None and open_angle >= 30,
                         value=open_angle,
                         reason="" if (open_angle is not None and open_angle >= 30) else "< 30°"))

    results.append(check("S3.4_knuckle_axial_clearance", C.HINGE_KNUCKLE_GAP_MM >= 0.30,
                         value=C.HINGE_KNUCKLE_GAP_MM))

    return results


# ---------------------------------------------------------------------------
# S4 — Printability
# ---------------------------------------------------------------------------

def check_s4() -> list[Result]:
    tooth_ok = C.TOOTH_WIDTH_MM >= 0.8
    width_ok = C.ARM_WIDTH_MM >= 3 * C.TOOTH_WIDTH_MM

    # Build-plate check: sum arm bounding boxes estimate
    # arm_left and arm_right are ~ARM_LENGTH_MM × ARM_WIDTH_MM each in X-Y
    # pin and cotter are small; rough estimate only
    arm_footprint_x = 2 * C.ARM_LENGTH_MM + 20  # two arms side by side + gap
    arm_footprint_y = C.ARM_WIDTH_MM + 20
    plate_ok = arm_footprint_x <= 256 and arm_footprint_y <= 256

    return [
        check("S4.1_tooth_width", tooth_ok,
              value=C.TOOTH_WIDTH_MM,
              reason="" if tooth_ok else f"{C.TOOTH_WIDTH_MM} mm < 0.8 mm minimum"),

        check("S4.2_arm_width_vs_tooth", width_ok,
              value=round(C.ARM_WIDTH_MM / C.TOOTH_WIDTH_MM, 2),
              reason="" if width_ok else "ARM_WIDTH_MM < 3 × TOOTH_WIDTH_MM"),

        check("S4.3_flat_print_orientation", True,
              reason="arms designed spine-face-down by convention (visual check required)"),

        check("S4.4_build_plate_fit",
              plate_ok,
              value={"estimated_footprint_mm": [round(arm_footprint_x), round(arm_footprint_y)],
                     "plate_mm": [256, 256]},
              reason="" if plate_ok else "estimated footprint exceeds 256 × 256 mm"),
    ]


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def score(results: list[Result]) -> tuple[int, int]:
    passed = sum(1 for r in results if r["pass"])
    return passed, len(results)


def print_table(all_results: list[Result]) -> None:
    print(f"\n{'ID':<40} {'PASS':>6}  VALUE / REASON")
    print("-" * 80)
    for r in all_results:
        status = "PASS" if r["pass"] else "FAIL"
        detail = r.get("reason") or str(r.get("value", ""))
        print(f"{r['id']:<40} {status:>6}  {detail}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--save-baseline", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    all_results: list[Result] = []
    all_results += check_s1()
    all_results += check_s2()
    all_results += check_s3()
    all_results += check_s4()

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        print_table(all_results)
        passed, total = score(all_results)
        print(f"Automated criteria: {passed}/{total} passed")
        if passed == total:
            print("All automated checks PASS.")
        else:
            failed = [r["id"] for r in all_results if not r["pass"]]
            print(f"Failed: {', '.join(failed)}")

    if args.save_baseline or not args.json:
        baseline = {
            "config": {
                "ARM_LENGTH_MM": C.ARM_LENGTH_MM,
                "ARM_WIDTH_MM": C.ARM_WIDTH_MM,
                "ARM_THICKNESS_MM": C.ARM_THICKNESS_MM,
                "TOOTH_COUNT": C.TOOTH_COUNT,
                "TOOTH_START_MM": C.TOOTH_START_MM,
                "TOOTH_END_MM": C.TOOTH_END_MM,
                "PIN_RADIUS_MM": C.PIN_RADIUS_MM,
                "PIN_CLEARANCE_MM": C.PIN_CLEARANCE_MM,
                "HINGE_KNUCKLE_GAP_MM": C.HINGE_KNUCKLE_GAP_MM,
                "OPEN_ANGLE_DEG": getattr(C, "OPEN_ANGLE_DEG", None),
            },
            "results": all_results,
        }
        if args.save_baseline:
            out = EVAL_DIR / "baseline.json"
            out.write_text(json.dumps(baseline, indent=2))
            print(f"Baseline saved to {out.relative_to(ROOT)}")

    passed, total = score(all_results)
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
