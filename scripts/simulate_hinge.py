#!/usr/bin/env python3
"""Kinematic sanity checks for the banana clip fit-demo hinge.

This is intentionally simple. Before a full finite-element or contact
simulation, the hinge has to pass basic mechanism checks:

- the hinge housing must be coaxial with the arm roots
- the hinge axis must be oriented so the arms can close
- rotating around the claimed axis must reduce the arm-to-arm gap
"""
from __future__ import annotations

from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
ASSETS = ROOT / "assets"
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import fit_demo_head_clip as F


def rotate_about_axis(points: np.ndarray, origin: np.ndarray, axis: np.ndarray, angle_deg: float) -> np.ndarray:
    axis = axis / np.linalg.norm(axis)
    theta = np.radians(angle_deg)
    p = points - origin
    return (
        p * np.cos(theta)
        + np.cross(axis, p) * np.sin(theta)
        + axis * np.dot(p, axis)[:, None] * (1.0 - np.cos(theta))
        + origin
    )


def gap_stats(left: np.ndarray, right: np.ndarray) -> tuple[float, float, float]:
    gaps = right[:, 0] - left[:, 0]
    return float(gaps.min()), float(gaps.mean()), float(gaps.max())


def main() -> None:
    DOCS.mkdir(exist_ok=True)
    ASSETS.mkdir(exist_ok=True)

    left = F.arm_points(-1, n=60)
    right = F.arm_points(+1, n=60)

    current_origin = F.hinge_origin()
    current_axis = np.array([0.0, 1.0, 0.0])

    hinge_center = current_origin
    barrel_segments = F.hinge_knuckle_segments()
    hinge_y_half = max(abs(barrel_segments[0][0]), abs(barrel_segments[-1][1]))
    hinge_half = np.array([F.HINGE_BARREL_RADIUS, hinge_y_half, F.HINGE_BARREL_RADIUS])
    pin_inside_block_z = (hinge_center[2] - hinge_half[2]) <= current_origin[2] <= (hinge_center[2] + hinge_half[2])
    pin_to_block_z_delta = current_origin[2] - hinge_center[2]
    barrel_gaps = [barrel_segments[i + 1][0] - barrel_segments[i][1] for i in range(len(barrel_segments) - 1)]
    min_barrel_gap = min(barrel_gaps)
    owner_pattern = [seg[2] for seg in barrel_segments]
    pin_radial_clearance = F.HINGE_BARREL_BORE_RADIUS - F.HINGE_PIN_RADIUS
    cotter_radial_clearance = F.HINGE_COTTER_HOLE_RADIUS - F.HINGE_COTTER_RADIUS
    pin_y_span = F.HINGE_PIN_Y1 - F.HINGE_PIN_Y0
    barrel_y_span = barrel_segments[-1][1] - barrel_segments[0][0]
    pin_end_capture = (pin_y_span - barrel_y_span) / 2.0

    open_gap = gap_stats(left, right)
    left_current_axis_rot = rotate_about_axis(left, current_origin, current_axis, 5.0)
    right_current_axis_rot = rotate_about_axis(right, current_origin, current_axis, -5.0)
    current_axis_gap = gap_stats(left_current_axis_rot, right_current_axis_rot)

    gap_reduction_current = open_gap[1] - current_axis_gap[1]

    failures = []
    if not pin_inside_block_z:
        failures.append("Current pin axis is not inside the visible hinge Z range.")
    if gap_reduction_current < 5.0:
        failures.append("Rotation about the current front-back hinge axis does not close the arm gap enough.")
    if min_barrel_gap < 0.35:
        failures.append("Interleaved hinge barrels do not have enough axial clearance for a first print.")
    if owner_pattern != [-1, 1, -1]:
        failures.append("Hinge barrels are not interleaved left/right/left.")
    if pin_radial_clearance < 0.25:
        failures.append("Pin-to-barrel radial clearance is too small for a first PETG print.")
    if cotter_radial_clearance < 0.25:
        failures.append("Cotter-to-pin-hole radial clearance is too small for a first PETG print.")
    if pin_end_capture < F.HINGE_PIN_RETAINER_THICKNESS * 0.45:
        failures.append("Hidden pin capture does not extend far enough beyond the outer barrels.")
    if not (25.0 <= F.HINGE_STOP_ANGLE_DEG <= 45.0):
        failures.append("Configured stop angle is outside the conservative first-print range.")

    fig, ax = plt.subplots(figsize=(7.5, 7.5), facecolor="white")
    ax.plot(left[:, 0], left[:, 2], color="black", linewidth=4, label="open left arm")
    ax.plot(right[:, 0], right[:, 2], color="black", linewidth=4, label="open right arm")
    ax.plot(left_current_axis_rot[:, 0], left_current_axis_rot[:, 2], color="#2d6cdf", linestyle=":", linewidth=2.5, label="current front-back axis rotation")
    ax.plot(right_current_axis_rot[:, 0], right_current_axis_rot[:, 2], color="#2d6cdf", linestyle=":", linewidth=2.5)
    ax.scatter([current_origin[0]], [current_origin[2]], color="orange", s=80, zorder=5, label="current pin axis center")
    ax.axhspan(hinge_center[2] - hinge_half[2], hinge_center[2] + hinge_half[2], color="orange", alpha=0.12, label="hinge Z band")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("X left/right mm")
    ax.set_ylabel("Z vertical mm")
    ax.set_title("Hinge sanity simulation: front-back axis closes the arms")
    ax.grid(True, linewidth=0.3)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(ASSETS / "hinge_simulation.png", dpi=180)
    plt.close(fig)

    lines = [
        "# Hinge Simulation Report",
        "",
        "Generated by `python scripts/simulate_hinge.py`.",
        "",
        "## Result",
        "",
        "FAILED - current fit-demo hinge is not mechanically credible." if failures else "PASSED - front-back hinge axis is kinematically plausible.",
        "",
        "## Key Measurements",
        "",
        f"- Current pin axis center: `{current_origin.round(3).tolist()}`",
        f"- Visible hinge center: `{hinge_center.round(3).tolist()}`",
        f"- Pin-to-block Z offset: `{pin_to_block_z_delta:.3f} mm`",
        f"- Pin inside visible hinge block Z range: `{pin_inside_block_z}`",
        f"- Interleaved barrel owner pattern: `{owner_pattern}`",
        f"- Barrel axial clearance min: `{min_barrel_gap:.3f} mm`",
        f"- Pin-to-barrel radial allowance: `{pin_radial_clearance:.3f} mm`",
        f"- Cotter-to-pin-hole radial allowance: `{cotter_radial_clearance:.3f} mm`",
        f"- Hidden pin capture beyond outer barrels: `{pin_end_capture:.3f} mm per side`",
        f"- Exposed bolt/pin geometry shown in render: `{F.HINGE_SHOW_EXPOSED_PIN}`",
        f"- Configured conservative stop angle: `{F.HINGE_STOP_ANGLE_DEG:.1f} deg`",
        f"- Open arm X gap min/mean/max: `{open_gap[0]:.3f} / {open_gap[1]:.3f} / {open_gap[2]:.3f} mm`",
        f"- After current front-back axis rotation gap min/mean/max: `{current_axis_gap[0]:.3f} / {current_axis_gap[1]:.3f} / {current_axis_gap[2]:.3f} mm`",
        f"- Current-axis mean gap reduction: `{gap_reduction_current:.3f} mm`",
        "",
        "## Failures",
        "",
    ]
    lines.extend(f"- {failure}" for failure in failures)
    lines.extend([
        "",
        "## Design Implication",
        "",
        "The hinge now keeps the pin as hidden functional intent instead of exposed bolt-like hardware. The visible form is interleaved molded barrels with intentional axial gaps and rounded stop nubs near the arm roots. This is still a kinematic sanity check, not a fatigue/contact simulation. The next CAD step is to transfer these dimensions into the CadQuery STEP model as editable hinge leaves with real bores.",
        "",
        "![Hinge simulation](../assets/hinge_simulation.png)",
    ])
    (DOCS / "HINGE_SIMULATION_REPORT.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:22]))
    if failures:
        sys.exit(1)


if __name__ == "__main__":
    main()
