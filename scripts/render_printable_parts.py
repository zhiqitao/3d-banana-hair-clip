#!/usr/bin/env python3
"""Render the 4 printable STL files as a single layout image for the README.

Loads the actual STL geometry — no reproduction, no idealized matplotlib —
and lays the pieces out the way they would appear on a Bambu Studio build plate.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).parent.parent
OUT_DIR = ROOT / "outputs_fit_demo"
ASSETS = ROOT / "assets"
TARGET = ASSETS / "printable_parts.png"

PIECES = [
    ("arm_left",     "Left arm",      "#1f3a93"),
    ("arm_right",    "Right arm",     "#16a085"),
    ("hinge_pin",    "Hinge pin",     "#5dade2"),
    ("hinge_cotter", "Hinge cotter",  "#e67e22"),
]


def render_mesh(ax, mesh: trimesh.Trimesh, color: str, label: str) -> None:
    faces = mesh.vertices[mesh.faces]
    poly = Poly3DCollection(
        faces,
        facecolors=color,
        edgecolors=(0, 0, 0, 0.08),
        linewidths=0.15,
        alpha=1.0,
    )
    ax.add_collection3d(poly)

    bounds = mesh.bounds
    center = (bounds[0] + bounds[1]) / 2.0
    extents = bounds[1] - bounds[0]
    size = extents.max() * 0.52
    ax.set_xlim(center[0] - size, center[0] + size)
    ax.set_ylim(center[1] - size, center[1] + size)
    ax.set_zlim(center[2] - size, center[2] + size)

    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=24, azim=-62)
    ax.set_axis_off()
    ax.text2D(0.5, 0.92, label, transform=ax.transAxes,
              fontsize=12, fontweight="medium",
              ha="center", va="bottom")


def main() -> None:
    fig = plt.figure(figsize=(10, 3.5), dpi=160)
    fig.patch.set_facecolor("white")

    for i, (stem, label, color) in enumerate(PIECES):
        path = OUT_DIR / f"{stem}.stl"
        mesh = trimesh.load(str(path), force="mesh")
        ax = fig.add_subplot(1, 4, i + 1, projection="3d")
        ax.set_facecolor("white")
        render_mesh(ax, mesh, color, label)

    fig.suptitle(
        "The four pieces an agent must produce",
        fontsize=13, fontweight="bold", y=0.97,
    )
    fig.subplots_adjust(left=-0.05, right=1.05, top=0.95, bottom=-0.05, wspace=-0.15)

    ASSETS.mkdir(exist_ok=True)
    fig.savefig(TARGET, dpi=140, bbox_inches="tight", facecolor="white")
    print(f"Wrote {TARGET.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
