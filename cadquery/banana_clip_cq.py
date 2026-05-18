#!/usr/bin/env python3
"""True CAD-kernel banana clip generator using CadQuery/OpenCascade.

This module preserves the design-final profile math from the STL-first
generator, then creates B-rep extrusions and STEP exports through OpenCascade.
The original mesh generator in scripts/ remains the fallback and is not edited
by this file.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import numpy as np
from shapely.geometry import LineString
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
import trimesh

ROOT = Path(__file__).resolve().parent.parent
CADQUERY_DIR = Path(__file__).resolve().parent
SCRIPT_DIR = ROOT / "scripts"
if str(CADQUERY_DIR) not in sys.path:
    sys.path.insert(0, str(CADQUERY_DIR))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import config as C
import banana_clip_design_final as G
import config_cq as CQ

try:
    import cadquery as cq
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by users without CQ.
    raise SystemExit(
        "CadQuery is required for the true CAD-kernel generator.\n"
        "Install it with: python -m pip install cadquery"
    ) from exc

def iter_polygons(poly: Polygon | MultiPolygon) -> Iterable[Polygon]:
    if isinstance(poly, Polygon):
        yield poly
    elif isinstance(poly, MultiPolygon):
        yield from poly.geoms
    else:
        raise TypeError(type(poly))


def _ring_points(ring) -> list[tuple[float, float]]:
    return [(float(x), float(y)) for x, y in list(ring.coords)[:-1]]


def _extrude_ring(points: list[tuple[float, float]], z0: float, z1: float) -> cq.Workplane:
    solid = cq.Workplane("XY").polyline(points).close().extrude(z1 - z0)
    if z0:
        solid = solid.translate((0, 0, z0))
    return solid


def extrude_polygon(poly: Polygon | MultiPolygon, z0: float, z1: float) -> cq.Workplane:
    """Extrude a Shapely polygon into OpenCascade B-rep solids.

    Interiors are cut as real cylindrical/prismatic voids in the resulting
    shape. MultiPolygons become a unioned compound of B-rep extrusions.
    """
    result: cq.Workplane | None = None
    for p in iter_polygons(poly):
        p = p.simplify(C.SIMPLIFY_MM, preserve_topology=True).buffer(0)
        if p.is_empty or p.area <= 1e-6:
            continue
        part = _extrude_ring(_ring_points(p.exterior), z0, z1)
        for interior in p.interiors:
            cutter = _extrude_ring(_ring_points(interior), z0 - 0.25, z1 + 0.25)
            part = part.cut(cutter)
        result = part if result is None else result.union(part)
    if result is None:
        raise ValueError("Cannot extrude an empty polygon")
    return result


def build_arm(side: int) -> cq.Workplane:
    result: cq.Workplane | None = None
    for z0, z1, poly in G.arm_layer_profiles(side):
        if z1 <= z0:
            continue
        part = extrude_polygon(poly, z0, z1)
        result = part if result is None else result.union(part)
    if result is None:
        raise ValueError("No arm layers generated")
    return result


def build_upper_arm() -> cq.Workplane:
    return build_arm(+1)


def build_lower_arm() -> cq.Workplane:
    return build_arm(-1)


def build_pin(radius: float) -> cq.Workplane:
    z0 = -C.PIN_OVERHANG_MM
    height = C.ARM_THICKNESS_MM + 2 * C.PIN_OVERHANG_MM
    shaft = (
        cq.Workplane("XY")
        .center(C.HINGE_X_MM, 0)
        .circle(radius)
        .extrude(height)
        .translate((0, 0, z0))
    )
    head_r = max(C.PIN_HEAD_RADIUS_MM, radius + 1.25)
    lower_head = (
        cq.Workplane("XY")
        .center(C.HINGE_X_MM, 0)
        .circle(head_r)
        .extrude(C.PIN_HEAD_THICKNESS_MM)
        .translate((0, 0, z0 - C.PIN_HEAD_THICKNESS_MM))
    )
    upper_head = (
        cq.Workplane("XY")
        .center(C.HINGE_X_MM, 0)
        .circle(head_r)
        .extrude(C.PIN_HEAD_THICKNESS_MM)
        .translate((0, 0, z0 + height))
    )
    return shaft.union(lower_head).union(upper_head)


def build_tolerance_kit() -> cq.Workplane:
    plate = Polygon([(0, 0), (58, 0), (58, 18), (0, 18)])
    holes = [G.circle_poly(7 + i * 11, 9, r) for i, r in enumerate(C.TOLERANCE_HOLE_RADII_MM)]
    kit = extrude_polygon(G.clean(plate.difference(unary_union(holes))), 0, C.COUPON_THICKNESS_MM)
    for i, r in enumerate(C.TOLERANCE_PIN_RADII_MM):
        pin = (
            cq.Workplane("XY")
            .center(7 + i * 11, 28)
            .circle(r)
            .extrude(C.COUPON_THICKNESS_MM + 2)
        )
        kit = kit.union(pin)
    return kit


def build_elastic_helper() -> cq.Workplane:
    bridge = LineString([(0, 0), (16, 0)]).buffer(1.15, cap_style=2)
    base = unary_union([G.circle_poly(0, 0, 2.1), G.circle_poly(16, 0, 2.1), bridge])
    holes = unary_union([G.circle_poly(0, 0, C.ELASTIC_CHANNEL_RADIUS_MM), G.circle_poly(16, 0, C.ELASTIC_CHANNEL_RADIUS_MM)])
    return extrude_polygon(G.clean(base.difference(holes)), 0, 3.0)


def build_hinge_stress_coupon() -> cq.Workplane:
    base = unary_union([
        G.circle_poly(0, 0, C.HINGE_RADIUS_MM),
        G.circle_poly(10, 4.2, C.HINGE_ATTACH_RADIUS_MM * 0.82),
        G.circle_poly(10, -4.2, C.HINGE_ATTACH_RADIUS_MM * 0.82),
    ]).convex_hull
    hole = G.circle_poly(0, 0, G.PIN_HOLE_RADIUS)
    rib1 = LineString([(1.5, 0), (15.5, 6.0)]).buffer(0.85, cap_style=2)
    rib2 = LineString([(1.5, 0), (15.5, -6.0)]).buffer(0.85, cap_style=2)
    return extrude_polygon(G.clean(unary_union([base, rib1, rib2]).difference(hole)), 0, C.ARM_THICKNESS_MM)


def build_tooth_slot_coupon() -> cq.Workplane:
    """A B-rep version of the quick tooth/slot clearance coupon."""
    upper_base = Polygon([(0, 3.4), (52, 3.4), (52, 9.2), (0, 9.2)])
    lower_base = Polygon([(0, -9.2), (52, -9.2), (52, -3.4), (0, -3.4)])
    pitch = 5.0
    teeth = []
    slots_upper = []
    slots_lower = []
    for i in range(9):
        x = 5 + i * pitch
        w = C.TOOTH_WIDTH_MM * 1.25
        wt = w * C.TOOTH_TIP_TAPER
        teeth.append(Polygon([(x - w / 2, 3.4), (x + w / 2, 3.4), (x + wt / 2, -0.8), (x - wt / 2, -0.8)]).buffer(0.08).buffer(-0.08))
        x2 = x + pitch / 2
        if x2 < 50:
            teeth.append(Polygon([(x2 - w / 2, -3.4), (x2 + w / 2, -3.4), (x2 + wt / 2, 0.8), (x2 - wt / 2, 0.8)]).buffer(0.08).buffer(-0.08))
            slots_upper.append(Polygon([(x2 - 0.95, 3.4), (x2 + 0.95, 3.4), (x2 + 0.55, 1.0), (x2 - 0.55, 1.0)]))
        slots_lower.append(Polygon([(x - 0.95, -3.4), (x + 0.95, -3.4), (x + 0.55, -1.0), (x - 0.55, -1.0)]))
    upper = upper_base.difference(unary_union(slots_upper))
    lower = lower_base.difference(unary_union(slots_lower))
    return extrude_polygon(G.clean(unary_union([upper, lower] + teeth)), 0, min(C.ARM_THICKNESS_MM, 4.0))


def build_snap_latch_coupon() -> cq.Workplane:
    base_a = Polygon([(0, 2), (38, 2), (38, 7), (0, 7)])
    hook = Polygon([(34, 2), (43, 2), (43, 4.0), (38.5, 5.0), (34, 5.0)])
    base_b = Polygon([(0, -7), (38, -7), (38, -2), (0, -2)])
    catch = Polygon([(34, -5.0), (40, -5.0), (40, -2.0), (36.6, -2.0), (36.6, -3.4), (34, -3.4)])
    geom = G.clean(unary_union([base_a, hook, base_b, catch]))
    result: cq.Workplane | None = None
    for i, scale in enumerate([0.85, 1.0, 1.15]):
        sample = extrude_polygon(geom, 0, 3.2 * scale).translate((0, i * 20, 0))
        result = sample if result is None else result.union(sample)
    if result is None:
        raise ValueError("No snap latch samples generated")
    return result


def build_comfort_radius_coupon() -> cq.Workplane:
    result: cq.Workplane | None = None
    for i, r in enumerate([0.04, 0.08, 0.12, 0.18]):
        base = Polygon([(0, 0), (16, 0), (16, 5), (0, 5)])
        tooth = Polygon([(6, 5), (10, 5), (9, 13), (7, 13)])
        geom = G.clean(unary_union([base, tooth.buffer(r).buffer(-r)]))
        item = extrude_polygon(geom, 0, 3.0).translate((i * 20, 0, 0))
        result = item if result is None else result.union(item)
    if result is None:
        raise ValueError("No comfort samples generated")
    return result


def build_fb_hinge_coupon() -> cq.Workplane:
    """Front-back Y-axis hinge coupon matching the fit_demo_head_clip.py dimensions.

    Three B-rep pieces arranged flat on a print plate:
    - outer knuckle: two Y-axis barrels (the outer pair of the interleaved set)
      with a flat arm slab on the +X side.
    - inner knuckle: one Y-axis barrel (the centre of the interleaved set)
      with a flat arm slab on the -X side.
    - test pin: correct radius with small retainer caps at each end.

    Printing and assembling these three pieces tests whether the bore/pin fit
    is achievable before committing the front-back hinge geometry to the main
    arm STEP files.  Dimensions match scripts/fit_demo_head_clip.py constants:
    HINGE_BARREL_RADIUS=1.65, HINGE_PIN_RADIUS=0.72, HINGE_KNUCKLE_CLEARANCE=0.40.
    """
    barrel_r = 1.65
    bore_r = 0.85   # HINGE_PIN_RADIUS (0.72) + 0.13 mm radial slip-fit clearance
    pin_r = 0.72
    pin_head_r = 1.40
    pin_head_h = 0.80
    clearance = 0.40
    slab_x = 8.0
    slab_z = 3.0

    # Y-spans (shifted so the assembly starts at y=0)
    outer1_y0, outer1_y1 = 0.00, 2.95
    inner_y0 = outer1_y1 + clearance           # 3.35
    inner_y1 = inner_y0 + 2.50                 # 5.85
    outer2_y0 = inner_y1 + clearance           # 6.25
    outer2_y1 = outer2_y0 + 2.95              # 9.20
    total_y = outer2_y1

    def cyl_y(y0: float, y1: float, r: float, extra: float = 0.0) -> cq.Workplane:
        """Y-axis cylinder running from y0 to y1, centred at x=0, z=0."""
        h = y1 - y0 + 2 * extra
        return (
            cq.Workplane("XY")
            .circle(r)
            .extrude(h)
            .rotate((0, 0, 0), (1, 0, 0), -90)
            .translate((0, y0 - extra, 0))
        )

    full_bore = cyl_y(-1.0, total_y + 1.0, bore_r)

    # Outer knuckle: two barrels + arm slab on +X side
    b1 = cyl_y(outer1_y0, outer1_y1, barrel_r)
    b3 = cyl_y(outer2_y0, outer2_y1, barrel_r)
    outer_slab = (
        cq.Workplane("XY")
        .box(slab_x, total_y, slab_z)
        .translate((slab_x / 2, total_y / 2, 0))
    )
    outer_knuckle = b1.union(b3).union(outer_slab).cut(full_bore)

    # Inner knuckle: centre barrel + arm slab on -X side
    b2 = cyl_y(inner_y0, inner_y1, barrel_r)
    inner_slab = (
        cq.Workplane("XY")
        .box(slab_x, inner_y1 - inner_y0, slab_z)
        .translate((-slab_x / 2, (inner_y0 + inner_y1) / 2, 0))
    )
    inner_knuckle = b2.union(inner_slab).cut(full_bore)

    # Test pin: functional radius with small retainer caps
    pin_body = cyl_y(-0.30, total_y + 0.30, pin_r)
    head1 = cyl_y(-0.30 - pin_head_h, -0.30, pin_head_r)
    head2 = cyl_y(total_y + 0.30, total_y + 0.30 + pin_head_h, pin_head_r)
    test_pin = pin_body.union(head1).union(head2)

    # Lift everything to z=0 (bottom of barrel) and space out for printing
    lift = barrel_r
    return (
        outer_knuckle.translate((0, 0, lift))
        .union(inner_knuckle.translate((22, 0, lift)))
        .union(test_pin.translate((38, 0, lift)))
    )


def _translated_coupon(poly_builder, x: float, y: float, z: float = 0) -> cq.Workplane:
    return poly_builder().translate((x, y, z))


def build_coupon_plate_first() -> cq.Workplane:
    """First-impression coupon plate matching the mesh workflow intent."""
    parts = [
        _translated_coupon(build_tolerance_kit, 0, 0),
        _translated_coupon(build_elastic_helper, 70, 6),
        _translated_coupon(build_hinge_stress_coupon, 98, 8),
        _translated_coupon(build_tooth_slot_coupon, 0, -34),
        _translated_coupon(build_snap_latch_coupon, 64, -48),
        _translated_coupon(build_comfort_radius_coupon, 0, -70),
    ]
    result = parts[0]
    for part in parts[1:]:
        result = result.union(part)
    return result


def build_all() -> dict[str, cq.Workplane]:
    solids = {
        "upper_arm": build_upper_arm(),
        "lower_arm": build_lower_arm(),
        "tolerance_kit": build_tolerance_kit(),
        "elastic_helper": build_elastic_helper(),
        "hinge_stress_coupon": build_hinge_stress_coupon(),
        "tooth_slot_coupon": build_tooth_slot_coupon(),
        "snap_latch_coupon": build_snap_latch_coupon(),
        "comfort_radius_coupon": build_comfort_radius_coupon(),
        "coupon_plate_first": build_coupon_plate_first(),
        "fb_hinge_coupon": build_fb_hinge_coupon(),
    }
    for name, radius in C.PIN_VARIANTS_MM.items():
        solids[name] = build_pin(radius)
    return solids


def export_part(
    name: str,
    solid: cq.Workplane,
    step_dir: Path = CQ.OUTPUTS_STEP,
    stl_dir: Path = CQ.OUTPUTS_CAD_STL,
) -> None:
    step_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(step_dir / f"{name}.step"))
    vertices, faces = solid.val().tessellate(CQ.STL_TOLERANCE)
    mesh = trimesh.Trimesh(
        vertices=np.array([[v.x, v.y, v.z] for v in vertices]),
        faces=np.array(faces),
        process=True,
    )
    export_ascii_stl(mesh, stl_dir / f"{name}.stl", name)


def export_ascii_stl(mesh: trimesh.Trimesh, path: Path, name: str) -> None:
    """Write STL with enough coordinate precision for validation reloads.

    Binary STL stores float32 coordinates. The normal-following lower arm has a
    few close tessellation vertices that are valid in OpenCascade but can become
    non-manifold after float32 quantization. ASCII STL keeps the CAD-derived
    tessellation precise enough for Trimesh and slicers to reload as watertight.
    """
    normals = mesh.face_normals
    triangles = mesh.triangles
    with path.open("w") as fh:
        fh.write(f"solid {name}\n")
        for normal, tri in zip(normals, triangles):
            fh.write(f"  facet normal {normal[0]:.12g} {normal[1]:.12g} {normal[2]:.12g}\n")
            fh.write("    outer loop\n")
            for vertex in tri:
                fh.write(f"      vertex {vertex[0]:.12g} {vertex[1]:.12g} {vertex[2]:.12g}\n")
            fh.write("    endloop\n")
            fh.write("  endfacet\n")
        fh.write(f"endsolid {name}\n")


def generate(step_dir: Path = CQ.OUTPUTS_STEP, stl_dir: Path = CQ.OUTPUTS_CAD_STL) -> list[Path]:
    written: list[Path] = []
    for name, solid in build_all().items():
        export_part(name, solid, step_dir, stl_dir)
        written.extend([step_dir / f"{name}.step", stl_dir / f"{name}.stl"])
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate true CAD-kernel banana clip STEP/STL files.")
    parser.add_argument("--step-dir", type=Path, default=CQ.OUTPUTS_STEP, help="STEP output directory")
    parser.add_argument("--stl-dir", type=Path, default=CQ.OUTPUTS_CAD_STL, help="CAD-derived STL output directory")
    args = parser.parse_args()
    written = generate(args.step_dir, args.stl_dir)
    for path in written:
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
