#!/usr/bin/env python3
"""Printability check for the banana hair clip STL pieces.

Two-tier analysis:
  1. Trimesh geometric checks: watertightness, minimum edge length (thin features),
     overhang angle distribution, and wall-thickness proxy.
  2. Bambu Studio P2S CLI slice: parses result.json for print time, overhang-wall
     fraction, support need, and any warning messages.

Usage:
    python scripts/check_printability.py           # full check including slicer
    python scripts/check_printability.py --no-slicer  # geometry only
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = ROOT / "outputs_fit_demo"

BAMBU = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
BBL = Path.home() / "Library/Application Support/BambuStudio/system/BBL"
MACHINE  = BBL / "machine/Bambu Lab P2S 0.4 nozzle.json"
PROCESS  = BBL / "process/0.20mm Standard @BBL P2S.json"
FILAMENT = BBL / "filament/Bambu PETG Basic @BBL P2S 0.4 nozzle.json"

# Recommended print orientation (rotation degrees around X) for each piece.
# Rotating the geometry before overhang analysis gives accurate results.
PRINT_ROTATIONS_X = {
    "arm_left.stl":       0,   # exported pre-oriented for print
    "arm_right.stl":      0,
    "hinge_pin.stl":      0,
    "hinge_cotter.stl":   0,
}

PIECES = list(PRINT_ROTATIONS_X.keys())


# ── geometry helpers ────────────────────────────────────────────────────────

def min_edge_mm(mesh: trimesh.Trimesh) -> float:
    edges = mesh.vertices[mesh.edges_unique]
    lengths = np.linalg.norm(edges[:, 1] - edges[:, 0], axis=1)
    return float(lengths.min())


def overhang_fraction(mesh: trimesh.Trimesh, rot_x_deg: float,
                      threshold_deg: float = 45.0) -> float:
    """Fraction of faces that overhang more than threshold_deg from vertical.

    Applies the recommended print rotation first so the analysis matches the
    actual build orientation.
    """
    m = mesh.copy()
    if rot_x_deg:
        R = trimesh.transformations.rotation_matrix(
            np.radians(rot_x_deg), [1, 0, 0])
        m.apply_transform(R)
    normals = m.face_normals          # unit vectors
    cos_thresh = np.cos(np.radians(90 - threshold_deg))
    # Downward-facing normals have negative Z component. Overhang if angle
    # between normal and -Z is less than threshold from vertical.
    overhang_mask = normals[:, 2] < -cos_thresh
    return float(overhang_mask.sum()) / max(len(normals), 1)


def run_geometry_check(stl: Path, rot_x: float) -> dict:
    mesh = trimesh.load(stl, force="mesh")
    result = {
        "watertight": bool(mesh.is_watertight),
        "components": len(mesh.split(only_watertight=False)),
        "volume_mm3": round(float(mesh.volume), 1) if mesh.is_watertight else None,
        "min_edge_mm": round(min_edge_mm(mesh), 3),
        "faces": len(mesh.faces),
        "overhang_fraction": round(overhang_fraction(mesh, rot_x), 3),
    }
    result["issues"] = _geometry_issues(result)
    return result


def _geometry_issues(r: dict) -> list[str]:
    issues = []
    if not r["watertight"]:
        issues.append("NOT watertight — slicer may misread geometry")
    if r["components"] != 1:
        issues.append(f"{r['components']} disconnected mesh components — part may import with floating shells")
    if r["min_edge_mm"] < 0.4:
        issues.append(
            f"Min edge {r['min_edge_mm']} mm < 0.4 mm nozzle — feature may not print")
    elif r["min_edge_mm"] < 1.0:
        issues.append(
            f"Min edge {r['min_edge_mm']} mm is thin — use 2+ perimeters, PETG")
    if r["overhang_fraction"] > 0.10:
        issues.append(
            f"{r['overhang_fraction']*100:.1f}% of faces overhang >45° — supports recommended")
    elif r["overhang_fraction"] > 0.03:
        issues.append(
            f"{r['overhang_fraction']*100:.1f}% of faces overhang >45° — check orientation")
    return issues


# ── Bambu Studio slicer ─────────────────────────────────────────────────────

def run_bambu_slice(stl: Path, rot_x: float = 0) -> dict | None:
    if not BAMBU.exists():
        return None
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [
            str(BAMBU),
            "--slice", "0",
            "--load-settings", f"{MACHINE};{PROCESS}",
            "--load-filaments", str(FILAMENT),
            "--outputdir", tmp,
            "--ensure-on-bed",
        ]
        if rot_x:
            cmd += ["--rotate-x", str(rot_x)]
        cmd.append(str(stl))
        subprocess.run(cmd, capture_output=True, timeout=180)
        result_path = Path(tmp) / "result.json"
        if not result_path.exists():
            return {"error": "no result.json — slicer may have failed"}
        with result_path.open() as f:
            data = json.load(f)

    plates = data.get("sliced_plates", [])
    if not plates:
        return {"error": data.get("error_string", "unknown")}

    plate = plates[0]
    feat = plate.get("feature_type_times", {})
    total_move = sum(feat.values()) or 1
    overhang_pct = feat.get("Overhang wall", 0) / total_move * 100
    support_time = plate.get("generate_support_material_time", 0)
    print_sec = int(plate.get("total_predication", 0))
    warnings = plate.get("warning_message", "")

    issues = []
    if warnings:
        for w in warnings.split(". "):
            w = w.strip()
            if w:
                issues.append(w)
    if overhang_pct > 5:
        issues.append(
            f"Overhang wall is {overhang_pct:.1f}% of total move time — may need support")
    if support_time > 30:
        issues.append(
            f"Slicer spent {support_time}s generating supports — supports were added")

    return {
        "print_time_min": round(print_sec / 60, 1),
        "overhang_wall_pct": round(overhang_pct, 1),
        "support_gen_s": support_time,
        "return_code": data.get("return_code", -1),
        "issues": issues,
    }


# ── report ──────────────────────────────────────────────────────────────────

def fmt_issues(issues: list[str]) -> str:
    if not issues:
        return "  ✓  no issues"
    return "\n".join(f"  ✗  {i}" for i in issues)


def run_all(use_slicer: bool) -> None:
    print("=" * 70)
    print("Banana Hair Clip — Printability Check")
    print(f"Printer: Bambu Lab P2S  |  Nozzle: 0.4 mm  |  Material: PETG")
    print("=" * 70)

    all_ok = True
    for name in PIECES:
        stl = OUTPUTS / name
        rot_x = PRINT_ROTATIONS_X[name]
        print(f"\n── {name} ──")

        if not stl.exists():
            print("  STL not found — run fit_demo_head_clip.py first")
            all_ok = False
            continue

        geo = run_geometry_check(stl, rot_x)
        print(f"  Watertight:   {geo['watertight']}")
        print(f"  Components:   {geo['components']}")
        print(f"  Faces:        {geo['faces']}")
        print(f"  Volume:       {geo['volume_mm3']} mm³" if geo["volume_mm3"] else "  Volume:       n/a (not watertight)")
        print(f"  Min edge:     {geo['min_edge_mm']} mm")
        print(f"  Overhang:     {geo['overhang_fraction']*100:.1f}% of faces >45°  (at recommended print orientation)")
        if geo["issues"]:
            print("  Geometry issues:")
            print(fmt_issues(geo["issues"]))
            all_ok = False

        if use_slicer:
            sr = run_bambu_slice(stl, rot_x=rot_x)
            if sr and "error" not in sr:
                print(f"  Print time:   ~{sr['print_time_min']} min")
                print(f"  Overhang wall:{sr['overhang_wall_pct']}% of move time")
                if sr["issues"]:
                    print("  Slicer issues:")
                    print(fmt_issues(sr["issues"]))
                    all_ok = False
            elif sr:
                print(f"  Slicer:       {sr['error']}")

    print("\n" + "=" * 70)
    if all_ok:
        print("RESULT: All pieces passed — safe to print.")
    else:
        print("RESULT: Issues found — review above before printing.")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-slicer", action="store_true",
                        help="Skip Bambu Studio slice (geometry checks only)")
    args = parser.parse_args()
    run_all(use_slicer=not args.no_slicer)
