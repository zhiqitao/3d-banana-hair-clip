#!/usr/bin/env python3
"""Banana Clip design-phase final generator.

This generator creates a print-oriented banana hair clip prototype:
- upper_arm.stl
- lower_arm.stl
- pin.stl
- assembly_closed.stl
- assembly_open.stl
- assembly_exploded.stl
- 2D previews

The design uses Shapely for 2D parametric profiles and Trimesh for extrusion.
It intentionally includes validation-friendly geometry helpers so the learning
process is visible instead of hidden inside a black-box CAD file.
"""
from __future__ import annotations

import argparse, math, sys
from pathlib import Path
from typing import Iterable

import numpy as np
from shapely.affinity import rotate as shp_rotate
from shapely.geometry import LineString, Point, Polygon, MultiPolygon
from shapely.ops import triangulate, unary_union
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
ASSETS = ROOT / "assets"
OUT.mkdir(exist_ok=True)
ASSETS.mkdir(exist_ok=True)

T = C.ARM_THICKNESS_MM
K = T / 3.0
PIN_HOLE_RADIUS = C.PIN_RADIUS_MM + C.PIN_CLEARANCE_MM

# ----------------------------- math helpers -----------------------------

def centerline(s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return s, C.CURVE_BOW_MM * np.sin(np.pi * s / C.ARM_LENGTH_MM)


def tangent_at(s: float) -> np.ndarray:
    dy = C.CURVE_BOW_MM * (math.pi / C.ARM_LENGTH_MM) * math.cos(math.pi * s / C.ARM_LENGTH_MM)
    t = np.array([1.0, dy])
    return t / np.linalg.norm(t)


def body_tangent_at(s: float, side: int) -> np.ndarray:
    """Local tangent of the actual upper/lower arm centerline."""
    dy = C.CURVE_BOW_MM * (math.pi / C.ARM_LENGTH_MM) * math.cos(math.pi * s / C.ARM_LENGTH_MM)
    t = np.array([1.0, float(side) * dy])
    return t / np.linalg.norm(t)


def outward_normal_at(s: float, side: int) -> np.ndarray:
    """Normal pointing away from the hair gap for a curved arm."""
    t = body_tangent_at(s, side)
    left = np.array([-t[1], t[0]])
    return left * float(side)


def normal_at(s: float, side: int) -> np.ndarray:
    return outward_normal_at(s, side)


def arm_center_offset() -> float:
    return (C.ARM_GAP_CLOSED_MM + C.ARM_WIDTH_MM) / 2.0


def circle_poly(x: float, y: float, r: float, n: int | None = None) -> Polygon:
    # Shapely resolution is segments per quadrant.
    n = n or C.CIRCLE_SEGMENTS
    return Point(x, y).buffer(r, resolution=max(12, n // 4))


def clean(g):
    return g.buffer(C.BUFFER_EPS_MM).buffer(-C.BUFFER_EPS_MM).buffer(0)

# ----------------------------- 2D profiles -----------------------------

def body_centerline(side: int, steps: int | None = None) -> list[tuple[float, float]]:
    steps = steps or C.CENTERLINE_STEPS
    s = np.linspace(0, C.ARM_LENGTH_MM, steps)
    x, y = centerline(s)
    y = side * (y + arm_center_offset())
    return list(zip(x, y))


def body_polygon_raw(side: int) -> Polygon:
    return LineString(body_centerline(side)).buffer(C.ARM_WIDTH_MM / 2.0, cap_style=2, join_style=2)


def inner_edge_y(side: int, s: float) -> float:
    _, yr = centerline(np.array([s]))
    return side * (float(yr[0]) + C.ARM_GAP_CLOSED_MM / 2.0)


def body_center_point(side: int, s: float) -> np.ndarray:
    x, yr = centerline(np.array([s]))
    return np.array([float(x[0]), side * (float(yr[0]) + arm_center_offset())])


def inner_edge_point(side: int, s: float) -> np.ndarray:
    return body_center_point(side, s) - outward_normal_at(s, side) * (C.ARM_WIDTH_MM / 2.0)


def tooth_positions(side: int) -> list[float]:
    pitch = (C.TOOTH_END_MM - C.TOOTH_START_MM) / (C.TOOTH_COUNT - 1)
    stagger = 0.0 if side > 0 else pitch / 2.0
    xs = []
    for i in range(C.TOOTH_COUNT):
        ss = C.TOOTH_START_MM + i * pitch + stagger
        if C.TOOTH_START_MM <= ss <= C.TOOTH_END_MM:
            xs.append(ss)
    return xs


def tooth_polygon(side: int, s: float) -> Polygon:
    t = body_tangent_at(s, side)
    inward = -outward_normal_at(s, side)
    root = inner_edge_point(side, s) - inward * C.TOOTH_ROOT_INSET_MM
    tip = root + inward * C.TOOTH_LENGTH_MM
    wr = C.TOOTH_WIDTH_MM / 2.0
    wt = wr * C.TOOTH_TIP_TAPER
    p = Polygon([
        tuple(root - t * wr),
        tuple(root + t * wr),
        tuple(tip + t * wt),
        tuple(tip - t * wt),
    ])
    edge_r = getattr(C, "TOOTH_EDGE_RADIUS_MM", C.TOOTH_BASE_FILLET_MM)
    if edge_r > 0:
        # Small global rounding softens the tooth tip and sharp side corners.
        # This is a design-phase comfort improvement; aggressive rounding would
        # reduce grip, so keep it below the slot clearance margin.
        p = p.buffer(edge_r).buffer(-edge_r)
    return p.buffer(0)


def receiving_slot_polygon(receiving_side: int, incoming_tooth_s: float) -> Polygon:
    """Slot in one body for a tooth from the other side.

    It opens at the inner edge and goes outward into the arm by the amount
    the tooth would otherwise penetrate the opposite body, plus clearance.
    """
    t = body_tangent_at(incoming_tooth_s, receiving_side)
    outward = outward_normal_at(incoming_tooth_s, receiving_side)
    inner = inner_edge_point(receiving_side, incoming_tooth_s)
    penetration = max(0.0, C.TOOTH_LENGTH_MM - C.ARM_GAP_CLOSED_MM + C.TOOTH_ROOT_INSET_MM)
    depth = penetration + C.SLOT_EXTRA_DEPTH_MM
    p0 = inner - outward * C.SLOT_MOUTH_MM
    p1 = inner + outward * depth
    wr_mouth = (C.TOOTH_WIDTH_MM + 2.0 * C.SLOT_CLEARANCE_MM) * C.SLOT_TAPER / 2.0
    wr_inner = (C.TOOTH_WIDTH_MM + 2.0 * C.SLOT_CLEARANCE_MM) / 2.0
    return Polygon([
        tuple(p0 - t * wr_mouth), tuple(p0 + t * wr_mouth),
        tuple(p1 + t * wr_inner), tuple(p1 - t * wr_inner),
    ]).buffer(0)


def receiving_slots_for_body(side: int) -> Polygon:
    incoming_side = -side
    slots = [receiving_slot_polygon(side, s) for s in tooth_positions(incoming_side)]
    return unary_union(slots).buffer(0) if slots else Polygon()


def elastic_hole_polygon(side: int) -> Polygon:
    x, yr = centerline(np.array([C.ELASTIC_HOLE_X_MM]))
    # Place the hole near the outer half of the arm, not in the tooth/slot region.
    y = side * (float(yr[0]) + arm_center_offset())
    outward = float(side) * (C.ARM_WIDTH_MM / 2.0 - C.ELASTIC_HOLE_RADIUS_MM - C.ELASTIC_HOLE_EDGE_CLEARANCE_MM)
    return circle_poly(float(x[0]), y + outward, C.ELASTIC_HOLE_RADIUS_MM)


def slotted_body_polygon(side: int, include_elastic_hole: bool = True) -> Polygon:
    body = body_polygon_raw(side)
    cutouts = [receiving_slots_for_body(side)]
    if C.ELASTIC_HOLE_ENABLED and include_elastic_hole:
        cutouts.append(elastic_hole_polygon(side))
    return clean(body.difference(unary_union(cutouts)))


def hook_polygon(side: int) -> Polygon:
    x, yr = centerline(np.array([C.ARM_LENGTH_MM]))
    tip = np.array([float(x[0]), side * (float(yr[0]) + arm_center_offset())])
    t = tangent_at(C.ARM_LENGTH_MM)
    outward = np.array([-t[1], t[0]]) * float(side)
    c = tip + t * (C.HOOK_OUTER_R_MM * 0.25) + outward * (C.HOOK_OUTER_R_MM * 0.48)
    to_tip = tip - c
    start = math.atan2(float(to_tip[1]), float(to_tip[0]))
    sweep = math.radians(C.HOOK_SWEEP_DEG) * float(side)
    angles = np.linspace(start, start + sweep, C.HOOK_STEPS)
    outer, inner = [], []
    for i, a in enumerate(angles):
        k = i / (C.HOOK_STEPS - 1)
        ro = C.HOOK_OUTER_R_MM - 1.1 * k
        ri = C.HOOK_INNER_R_MM - 0.30 * k
        outer.append((float(c[0]) + ro * math.cos(a), float(c[1]) + ro * math.sin(a)))
        inner.append((float(c[0]) + ri * math.cos(a), float(c[1]) + ri * math.sin(a)))
    return clean(Polygon(outer + inner[::-1]))


def teeth_union(side: int) -> Polygon:
    return unary_union([tooth_polygon(side, s) for s in tooth_positions(side)]).buffer(0)


def non_hinge_profile(side: int) -> Polygon:
    return clean(unary_union([slotted_body_polygon(side), hook_polygon(side), teeth_union(side)]))


def hinge_boss_polygon(side: int) -> Polygon:
    attach_y = side * arm_center_offset()
    barrel = circle_poly(C.HINGE_X_MM, 0.0, C.HINGE_RADIUS_MM)
    attach = circle_poly(C.HINGE_ATTACH_X_MM, attach_y, C.HINGE_ATTACH_RADIUS_MM)
    boss = unary_union([barrel, attach]).convex_hull
    hole = circle_poly(C.HINGE_X_MM, 0.0, PIN_HOLE_RADIUS)
    return clean(boss.difference(hole))

# ----------------------------- extrusion -----------------------------

def iter_polygons(poly: Polygon | MultiPolygon) -> Iterable[Polygon]:
    if isinstance(poly, Polygon):
        yield poly
    elif isinstance(poly, MultiPolygon):
        for p in poly.geoms:
            yield p
    else:
        raise TypeError(type(poly))


def extrude_polygon(poly: Polygon | MultiPolygon, z0: float, z1: float) -> trimesh.Trimesh:
    meshes = []
    for p in iter_polygons(poly):
        p = p.simplify(C.SIMPLIFY_MM, preserve_topology=True).buffer(0)
        if p.is_empty or p.area <= 1e-6:
            continue
        try:
            m = trimesh.creation.extrude_polygon(p, height=(z1 - z0))
            m.apply_translation([0, 0, z0])
            meshes.append(m)
            continue
        except Exception:
            pass

        verts = []
        faces = []
        vmap = {}
        def vid(x, y, z):
            key = (round(float(x), 7), round(float(y), 7), round(float(z), 7))
            if key not in vmap:
                vmap[key] = len(verts); verts.append((float(x), float(y), float(z)))
            return vmap[key]

        for tri in triangulate(p):
            rp = tri.representative_point()
            if not p.covers(rp):
                continue
            coords = list(tri.exterior.coords)[:3]
            b = [vid(x,y,z0) for x,y in coords]
            t = [vid(x,y,z1) for x,y in coords]
            faces.append((b[2], b[1], b[0]))
            faces.append((t[0], t[1], t[2]))
        for ring in [p.exterior] + list(p.interiors):
            coords = list(ring.coords)
            for (x0,y0),(x1,y1) in zip(coords[:-1], coords[1:]):
                a=vid(x0,y0,z0); b=vid(x1,y1,z0); c=vid(x1,y1,z1); d=vid(x0,y0,z1)
                faces.append((a,b,c)); faces.append((a,c,d))
        meshes.append(trimesh.Trimesh(vertices=np.array(verts), faces=np.array(faces), process=True))
    if not meshes:
        return trimesh.Trimesh()
    m = trimesh.util.concatenate(meshes)
    m.merge_vertices()
    m.remove_unreferenced_vertices()
    return m


def arm_layer_profiles(side: int):
    """Return non-overlapping Z bands for each arm.

    v7 exported a full-thickness base plus separate overlapping hinge-knuckle
    solids. That was printable in many slicers but not clean engineering. Final
    design_final uses a layered 2.5D approach: each Z band has one unioned 2D profile,
    then bands are stacked. This removes same-part overlapping solids while
    preserving the interleaved hinge knuckles.
    """
    base = non_hinge_profile(side)
    boss = hinge_boss_polygon(side)
    if side > 0:
        return [
            (0.0, K - C.HINGE_KNUCKLE_GAP_MM / 2, clean(unary_union([base, boss]))),
            (K - C.HINGE_KNUCKLE_GAP_MM / 2, 2 * K + C.HINGE_KNUCKLE_GAP_MM / 2, base),
            (2 * K + C.HINGE_KNUCKLE_GAP_MM / 2, T, clean(unary_union([base, boss]))),
        ]
    return [
        (0.0, K + C.HINGE_KNUCKLE_GAP_MM / 2, base),
        (K + C.HINGE_KNUCKLE_GAP_MM / 2, 2 * K - C.HINGE_KNUCKLE_GAP_MM / 2, clean(unary_union([base, boss]))),
        (2 * K - C.HINGE_KNUCKLE_GAP_MM / 2, T, base),
    ]


def layered_arm(side: int) -> trimesh.Trimesh:
    meshes = [extrude_polygon(poly, z0, z1) for z0, z1, poly in arm_layer_profiles(side) if z1 > z0]
    m = trimesh.util.concatenate(meshes)
    m.merge_vertices(); m.remove_unreferenced_vertices()
    return m

def build_upper_arm() -> trimesh.Trimesh:
    return layered_arm(+1)


def build_lower_arm() -> trimesh.Trimesh:
    return layered_arm(-1)


def build_pin(radius: float | None = None) -> trimesh.Trimesh:
    """Build a removable pin.

    design final exports three pin diameters because real FDM holes vary by printer,
    filament, slicer compensation, and orientation. Printing all three pins is
    faster than reprinting the arms.
    """
    r = C.PIN_RADIUS_MM if radius is None else float(radius)
    shaft = extrude_polygon(circle_poly(C.HINGE_X_MM, 0, r), -C.PIN_OVERHANG_MM, T + C.PIN_OVERHANG_MM)
    # Simple flanges make the pin easier to handle; sand if fit is too tight.
    head_r = max(C.PIN_HEAD_RADIUS_MM, r + 1.25)
    lower_head = extrude_polygon(circle_poly(C.HINGE_X_MM, 0, head_r), -C.PIN_OVERHANG_MM - C.PIN_HEAD_THICKNESS_MM, -C.PIN_OVERHANG_MM)
    upper_head = extrude_polygon(circle_poly(C.HINGE_X_MM, 0, head_r), T + C.PIN_OVERHANG_MM, T + C.PIN_OVERHANG_MM + C.PIN_HEAD_THICKNESS_MM)
    m = trimesh.util.concatenate([shaft, lower_head, upper_head])
    m.merge_vertices(); m.remove_unreferenced_vertices()
    return m


def build_tolerance_kit() -> trimesh.Trimesh:
    """Small first-print coupon for fit calibration.

    It includes several holes and several short pins. The student can test what
    actually fits on the target printer before committing to the full clip.
    """
    # plate with labeled-like graduated holes (labels are documented in README)
    plate = Polygon([(0,0),(58,0),(58,18),(0,18)])
    holes = []
    for i, r in enumerate(C.TOLERANCE_HOLE_RADII_MM):
        holes.append(circle_poly(7 + i*11, 9, r))
    plate_mesh = extrude_polygon(clean(plate.difference(unary_union(holes))), 0, C.COUPON_THICKNESS_MM)
    pins = []
    for i, r in enumerate(C.TOLERANCE_PIN_RADII_MM):
        pin = extrude_polygon(circle_poly(7 + i*11, 28, r), 0, C.COUPON_THICKNESS_MM + 2)
        pins.append(pin)
    kit = trimesh.util.concatenate([plate_mesh] + pins)
    kit.merge_vertices(); kit.remove_unreferenced_vertices()
    return kit


def rotated_about_hinge(mesh: trimesh.Trimesh, deg: float) -> trimesh.Trimesh:
    m = mesh.copy()
    T1 = trimesh.transformations.translation_matrix([-C.HINGE_X_MM, 0, 0])
    R = trimesh.transformations.rotation_matrix(math.radians(deg), [0, 0, 1])
    T2 = trimesh.transformations.translation_matrix([C.HINGE_X_MM, 0, 0])
    m.apply_transform(T2 @ R @ T1)
    return m


def translate(mesh: trimesh.Trimesh, xyz) -> trimesh.Trimesh:
    m = mesh.copy(); m.apply_translation(xyz); return m


def export_scad(path: Path):
    path.write_text(f'''// banana_clip_design_final.scad - print/assembly wrapper around generated STLs
// Main mesh source is scripts/banana_clip_design_final.py + scripts/config.py
// CAD/STEP source path is scripts/banana_clip_design_final_cadquery.py

module upper_arm() {{ import("upper_arm.stl"); }}
module lower_arm() {{ import("lower_arm.stl"); }}
module pin()       {{ import("pin.stl"); }}

// closed preview
upper_arm();
lower_arm();
pin();

// open preview example:
// rotate([0,0,{C.OPEN_ANGLE_DEG}]) upper_arm();
// rotate([0,0,{-C.OPEN_ANGLE_DEG}]) lower_arm();
// pin();
''')


def make_previews():
    import matplotlib.pyplot as plt
    for mode in ["closed", "open", "exploded"]:
        fig, ax = plt.subplots(figsize=(10.5, 3.6))
        geoms = [(non_hinge_profile(+1), +1), (non_hinge_profile(-1), -1), (hinge_boss_polygon(+1), +1), (hinge_boss_polygon(-1), -1)]
        for poly, side in geoms:
            p = poly
            if mode == "open":
                p = shp_rotate(p, C.OPEN_ANGLE_DEG * side, origin=(C.HINGE_X_MM, 0), use_radians=False)
            elif mode == "exploded":
                p = shp_rotate(p, 14 * side, origin=(C.HINGE_X_MM, 0), use_radians=False)
                # visual only: shift apart in y
                from shapely.affinity import translate as shp_translate
                p = shp_translate(p, yoff=side * 6.0)
            polys = p.geoms if isinstance(p, MultiPolygon) else [p]
            for q in polys:
                x, y = q.exterior.xy
                ax.fill(x, y, alpha=0.58)
                for interior in q.interiors:
                    xi, yi = interior.xy
                    ax.plot(xi, yi, linewidth=0.6)
        ax.set_aspect("equal", adjustable="box")
        ax.set_title(f"Banana Clip design final - {mode} 2D design review")
        ax.set_xlabel("X mm")
        ax.set_ylabel("Y mm")
        ax.grid(True, linewidth=0.3)
        fig.tight_layout()
        fig.savefig(ASSETS / f"preview_{mode}.png", dpi=170)
        plt.close(fig)


def export_2d_svg(path: Path):
    # Lightweight SVG for classroom/design review. It is not a manufacturing DXF.
    polys = [(non_hinge_profile(+1), "#88aaff"), (non_hinge_profile(-1), "#ffbb88"), (hinge_boss_polygon(+1), "#6688dd"), (hinge_boss_polygon(-1), "#dd8866")]
    minx, miny, maxx, maxy = unary_union([p for p, _ in polys]).bounds
    width = maxx - minx; height = maxy - miny
    def path_for(poly):
        def ring(coords):
            pts = list(coords)
            return "M " + " L ".join(f"{x-minx:.3f},{maxy-y:.3f}" for x,y in pts) + " Z"
        s = ring(poly.exterior.coords)
        for interior in poly.interiors:
            s += " " + ring(interior.coords)
        return s
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}mm" height="{height:.1f}mm" viewBox="0 0 {width:.3f} {height:.3f}">']
    out.append('<rect width="100%" height="100%" fill="white"/>')
    for p, color in polys:
        for q in (p.geoms if isinstance(p, MultiPolygon) else [p]):
            out.append(f'<path d="{path_for(q)}" fill="{color}" fill-opacity="0.55" stroke="black" stroke-width="0.12" fill-rule="evenodd"/>')
    out.append('</svg>')
    path.write_text("\n".join(out))



def build_elastic_helper() -> trimesh.Trimesh:
    """Small first-print elastic-hole tester.

    This lets the family test a rubber band/hair elastic size before printing
    the full clip. It is intentionally tiny and quick to print.
    """
    bridge = LineString([(0, 0), (16, 0)]).buffer(1.15, cap_style=2)
    base = unary_union([circle_poly(0, 0, 2.1), circle_poly(16, 0, 2.1), bridge])
    holes = unary_union([circle_poly(0, 0, C.ELASTIC_CHANNEL_RADIUS_MM), circle_poly(16, 0, C.ELASTIC_CHANNEL_RADIUS_MM)])
    return extrude_polygon(clean(base.difference(holes)), 0, 3.0)




def build_hinge_stress_coupon() -> trimesh.Trimesh:
    """Small coupon that represents the hinge web stress region.

    This is not a replacement for physical fatigue testing. It gives the first
    demo a cheap way to compare hinge boss thickness, pin-hole print quality,
    and layer adhesion before committing to the full arms.
    """
    base = unary_union([
        circle_poly(0, 0, C.HINGE_RADIUS_MM),
        circle_poly(10, 4.2, C.HINGE_ATTACH_RADIUS_MM * 0.82),
        circle_poly(10, -4.2, C.HINGE_ATTACH_RADIUS_MM * 0.82),
    ]).convex_hull
    hole = circle_poly(0, 0, PIN_HOLE_RADIUS)
    rib1 = LineString([(1.5, 0), (15.5, 6.0)]).buffer(0.85, cap_style=2)
    rib2 = LineString([(1.5, 0), (15.5, -6.0)]).buffer(0.85, cap_style=2)
    return extrude_polygon(clean(unary_union([base, rib1, rib2]).difference(hole)), 0, T)


def build_tooth_slot_coupon() -> trimesh.Trimesh:
    """Quick coupon for tooth/slot comfort and clearance.

    It contains a row of tapered teeth facing a row of receiving slots. It is
    intentionally short so it can be printed before the full clip.
    """
    # Use a short local coordinate system; mimic the real tooth width/taper.
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
        teeth.append(Polygon([(x-w/2,3.4),(x+w/2,3.4),(x+wt/2,-0.8),(x-wt/2,-0.8)]).buffer(0.08).buffer(-0.08))
        x2 = x + pitch/2
        if x2 < 50:
            teeth.append(Polygon([(x2-w/2,-3.4),(x2+w/2,-3.4),(x2+wt/2,0.8),(x2-wt/2,0.8)]).buffer(0.08).buffer(-0.08))
        # slots intentionally oversized so clearance is visible in first print
        slots_lower.append(Polygon([(x-0.95,-3.4),(x+0.95,-3.4),(x+0.55,-1.0),(x-0.55,-1.0)]))
        if x2 < 50:
            slots_upper.append(Polygon([(x2-0.95,3.4),(x2+0.95,3.4),(x2+0.55,1.0),(x2-0.55,1.0)]))
    upper = upper_base.difference(unary_union(slots_upper))
    lower = lower_base.difference(unary_union(slots_lower))
    return extrude_polygon(clean(unary_union([upper, lower] + teeth)), 0, min(T, 4.0))


def build_snap_latch_coupon() -> trimesh.Trimesh:
    """Separate snap-latch test, not integrated into the main clip by default.

    A snap latch is a high first-impression risk because FDM flexibility varies
    by material and print orientation. The coupon lets the family test latch
    feel cheaply before making it part of the full clip.
    """
    base_a = Polygon([(0, 2), (38, 2), (38, 7), (0, 7)])
    hook = Polygon([(34, 2), (43, 2), (43, 4.0), (38.5, 5.0), (34, 5.0)])
    base_b = Polygon([(0, -7), (38, -7), (38, -2), (0, -2)])
    catch = Polygon([(34, -5.0), (40, -5.0), (40, -2.0), (36.6, -2.0), (36.6, -3.4), (34, -3.4)])
    # Add three latch stiffness variants as adjacent samples.
    samples = []
    for i, scale in enumerate([0.85, 1.0, 1.15]):
        geom = clean(unary_union([base_a, hook, base_b, catch]))
        m = extrude_polygon(geom, 0, 3.2 * scale)
        m.apply_translation([0, i * 20, 0])
        samples.append(m)
    return trimesh.util.concatenate(samples)


def build_comfort_radius_coupon() -> trimesh.Trimesh:
    """Tiny tactile coupon comparing tooth-tip rounding and edge feel."""
    items = []
    for i, r in enumerate([0.04, 0.08, 0.12, 0.18]):
        base = Polygon([(0,0),(16,0),(16,5),(0,5)])
        tooth = Polygon([(6,5),(10,5),(9,13),(7,13)])
        geom = clean(unary_union([base, tooth.buffer(r).buffer(-r)]))
        m = extrude_polygon(geom, 0, 3.0)
        m.apply_translation([i*20, 0, 0])
        items.append(m)
    return trimesh.util.concatenate(items)


def build_coupon_plate(tolerance_kit, elastic_helper, hinge_coupon, tooth_coupon, snap_coupon, comfort_coupon) -> trimesh.Trimesh:
    """A first-impression-safe plate of small engineering coupons."""
    return trimesh.util.concatenate([
        translate(tolerance_kit, [0, 0, 0]),
        translate(elastic_helper, [70, 6, 0]),
        translate(hinge_coupon, [98, 8, 0]),
        translate(tooth_coupon, [0, -34, 0]),
        translate(snap_coupon, [64, -48, 0]),
        translate(comfort_coupon, [0, -70, 0]),
    ])

def build_print_plate(upper, lower, pin, tolerance_kit, elastic_helper) -> trimesh.Trimesh:
    """Convenience all-parts plate; users may still orient manually in slicer."""
    return trimesh.util.concatenate([
        translate(upper, [0, 18, 0]),
        translate(lower, [0, -18, 0]),
        translate(pin, [136, 0, 0]),
        translate(tolerance_kit, [0, -52, 0]),
        translate(elastic_helper, [88, -52, 0]),
    ])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-previews", action="store_true")
    ap.add_argument("--no-scad", action="store_true")
    args = ap.parse_args()

    upper = build_upper_arm()
    lower = build_lower_arm()
    pin = build_pin(C.PIN_RADIUS_MM)
    closed = trimesh.util.concatenate([upper, lower, pin])
    opened = trimesh.util.concatenate([
        rotated_about_hinge(upper, C.OPEN_ANGLE_DEG),
        rotated_about_hinge(lower, -C.OPEN_ANGLE_DEG),
        pin,
    ])
    exploded = trimesh.util.concatenate([
        translate(rotated_about_hinge(upper, 12), [0, 0, C.EXPLODED_Z_GAP_MM]),
        translate(rotated_about_hinge(lower, -12), [0, 0, -C.EXPLODED_Z_GAP_MM]),
        pin,
    ])
    export_items = [("upper_arm", upper), ("lower_arm", lower), ("pin", pin), ("assembly_closed", closed), ("assembly_open", opened), ("assembly_exploded", exploded)]
    for pname, radius in C.PIN_VARIANTS_MM.items():
        export_items.append((pname, build_pin(radius)))
    if C.TOLERANCE_KIT_ENABLED:
        tolerance_kit = build_tolerance_kit()
        elastic_helper = build_elastic_helper()
        hinge_coupon = build_hinge_stress_coupon()
        tooth_coupon = build_tooth_slot_coupon()
        snap_coupon = build_snap_latch_coupon()
        comfort_coupon = build_comfort_radius_coupon()
        export_items.append(("tolerance_kit", tolerance_kit))
        export_items.append(("elastic_helper", elastic_helper))
        export_items.append(("hinge_stress_coupon", hinge_coupon))
        export_items.append(("tooth_slot_coupon", tooth_coupon))
        export_items.append(("snap_latch_coupon", snap_coupon))
        export_items.append(("comfort_radius_coupon", comfort_coupon))
        export_items.append(("coupon_plate_first", build_coupon_plate(tolerance_kit, elastic_helper, hinge_coupon, tooth_coupon, snap_coupon, comfort_coupon)))
        export_items.append(("print_plate_all_parts", build_print_plate(upper, lower, pin, tolerance_kit, elastic_helper)))
    for name, mesh in export_items:
        mesh.export(OUT / f"{name}.stl")
    if not args.no_scad:
        export_scad(OUT / "banana_clip_design_final.scad")
    export_2d_svg(OUT / "banana_clip_design_final_profiles.svg")
    if not args.no_previews:
        make_previews()

    print("Generated banana_clip_design_final outputs:")
    for p in sorted(OUT.glob("*")):
        print(" -", p.relative_to(ROOT))
    print("\nMesh checks:")
    for name, mesh in [("upper", upper), ("lower", lower), ("pin", pin)]:
        comps = len(mesh.split(only_watertight=False))
        print(f" - {name:5s}: vertices={len(mesh.vertices):6d}, faces={len(mesh.faces):6d}, watertight={mesh.is_watertight}, components={comps}")

if __name__ == "__main__":
    main()
