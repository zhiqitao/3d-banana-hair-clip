#!/usr/bin/env python3
"""Render a head/hair fit demo for the banana clip design.

This is an engineering visualization, not an anatomical sculpture. It creates a
simple head, hair volume, and a banana-clip concept whose teeth project only
along the local inward normal of the curved arm surface. The refactored clip is
based on the supplied photo references: flattened curved rails, dense comb teeth,
compact hinge/latch ends, and a smooth outer spine.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
try:
    import cadquery as cq
except Exception:  # pragma: no cover - optional local CAD kernel
    cq = None

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / "outputs_fit_demo"
ASSETS.mkdir(exist_ok=True)
OUT.mkdir(exist_ok=True)

HINGE_BARREL_RADIUS = 3.70
HINGE_BARREL_BORE_RADIUS = 2.35
HINGE_PIN_RADIUS = 2.00
HINGE_COTTER_RADIUS = 0.90
HINGE_COTTER_HOLE_RADIUS = 1.35
HINGE_KNUCKLE_CLEARANCE = 0.40
HINGE_PIN_RETAINER_RADIUS = 0.95
HINGE_PIN_RETAINER_THICKNESS = 0.35
HINGE_STOP_ANGLE_DEG = 34.0
HINGE_PIN_Y0 = -8.10
HINGE_PIN_Y1 = 9.85
HINGE_SHOW_EXPOSED_PIN = False


def cylinder_between(a: np.ndarray, b: np.ndarray, radius: float, sections: int = 48) -> trimesh.Trimesh:
    vec = b - a
    length = float(np.linalg.norm(vec))
    if length <= 1e-9:
        return trimesh.Trimesh()
    cyl = trimesh.creation.cylinder(radius=radius, height=length, sections=sections)
    cyl.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], vec / length))
    cyl.apply_translation((a + b) / 2.0)
    return cyl


def cq_shape_to_trimesh(shape, tolerance: float = 0.045, angular_tolerance: float = 0.035) -> trimesh.Trimesh:
    """Convert a CadQuery/OpenCascade shape to a Trimesh for STL export/renders."""
    vertices, faces = shape.tessellate(tolerance, angular_tolerance)
    return trimesh.Trimesh(
        vertices=np.array([[v.x, v.y, v.z] for v in vertices], dtype=float),
        faces=np.array(faces, dtype=int),
        process=True,
    )


def hollow_cylinder_between(
    a: np.ndarray,
    b: np.ndarray,
    outer_radius: float,
    inner_radius: float,
    sections: int = 96,
    edge_fillet: float = 0.18,
) -> trimesh.Trimesh:
    """Hollow hinge barrel with a real through-bore.

    This intentionally uses Trimesh's annulus primitive instead of CAD-kernel
    filleting. The OpenCascade fillet produced tiny sliver triangles after STL
    round-tripping; the annulus stays watertight when reloaded by slicer-style
    mesh checks while still giving the arm a true pin bore.
    """
    vec = b - a
    length = float(np.linalg.norm(vec))
    if length <= 1e-9:
        return trimesh.Trimesh()
    axis = vec / length

    barrel = trimesh.creation.annulus(
        r_min=inner_radius,
        r_max=outer_radius,
        height=length,
        sections=sections,
    )
    barrel.apply_transform(trimesh.geometry.align_vectors([0, 0, 1], axis))
    barrel.apply_translation((a + b) / 2.0)
    return barrel


def sphere_at(center: np.ndarray, radius: float) -> trimesh.Trimesh:
    s = trimesh.creation.uv_sphere(segments=48, ring_count=24, radius=radius)
    s.apply_translation(center)
    return s


def ellipsoid_at(center: np.ndarray, radii: tuple[float, float, float]) -> trimesh.Trimesh:
    """High-resolution rounded pad/cap used to hide STL-flat sweep endpoints."""
    s = trimesh.creation.uv_sphere(segments=64, ring_count=32, radius=1.0)
    s.apply_scale(radii)
    s.apply_translation(center)
    return s


def box_at(center: np.ndarray, extents: tuple[float, float, float]) -> trimesh.Trimesh:
    box = trimesh.creation.box(extents=extents)
    box.apply_translation(center)
    return box


def fuse_meshes(meshes: list[trimesh.Trimesh], label: str) -> trimesh.Trimesh:
    """Boolean-union overlapping shells into a single slicer-readable piece."""
    bodies: list[trimesh.Trimesh] = []
    for mesh in meshes:
        bodies.extend(mesh.split(only_watertight=False))
    try:
        fused = trimesh.boolean.union(bodies, engine="manifold")
    except Exception:
        fused = trimesh.util.concatenate(meshes)
    if isinstance(fused, list):
        fused = trimesh.util.concatenate(fused)
    # Remove zero-area triangles left by manifold boolean that cause slicer
    # "floating region" warnings and split the mesh on reload.
    areas = 0.5 * np.linalg.norm(np.cross(
        fused.vertices[fused.faces[:, 1]] - fused.vertices[fused.faces[:, 0]],
        fused.vertices[fused.faces[:, 2]] - fused.vertices[fused.faces[:, 0]],
    ), axis=1)
    fused = trimesh.Trimesh(
        vertices=fused.vertices,
        faces=fused.faces[areas > 1e-10],
        process=True,
    )
    if not fused.is_watertight:
        raise RuntimeError(f"{label} did not export as a watertight mesh")
    return fused


def swept_elliptical_tube(points: np.ndarray, width_radius: float, depth_radius: float, sections: int = 14) -> trimesh.Trimesh:
    """Approximate a flattened curved rail as a watertight swept ellipse."""
    vertices = []
    faces = []
    angles = np.linspace(0, 2 * np.pi, sections, endpoint=False)
    for i, p in enumerate(points):
        if i == 0:
            tangent = points[1] - points[0]
        elif i == len(points) - 1:
            tangent = points[-1] - points[-2]
        else:
            tangent = points[i + 1] - points[i - 1]
        tangent = tangent / np.linalg.norm(tangent)
        depth_axis = np.array([0.0, 1.0, 0.0])
        width_axis = np.cross(depth_axis, tangent)
        if np.linalg.norm(width_axis) < 1e-6:
            width_axis = np.array([1.0, 0.0, 0.0])
        width_axis = width_axis / np.linalg.norm(width_axis)
        depth_axis = np.cross(tangent, width_axis)
        depth_axis = depth_axis / np.linalg.norm(depth_axis)
        for a in angles:
            vertices.append(p + width_axis * (np.cos(a) * width_radius) + depth_axis * (np.sin(a) * depth_radius))
    for i in range(len(points) - 1):
        for j in range(sections):
            a = i * sections + j
            b = i * sections + (j + 1) % sections
            c = (i + 1) * sections + (j + 1) % sections
            d = (i + 1) * sections + j
            faces.append((a, b, c))
            faces.append((a, c, d))
    start_center = len(vertices)
    vertices.append(points[0])
    end_center = len(vertices)
    vertices.append(points[-1])
    for j in range(sections):
        faces.append((start_center, (j + 1) % sections, j))
        a = (len(points) - 1) * sections + j
        b = (len(points) - 1) * sections + (j + 1) % sections
        faces.append((end_center, a, b))
    return trimesh.Trimesh(vertices=np.array(vertices), faces=np.array(faces), process=True)


def swept_flat_strip(points: np.ndarray, width, depth, sections: int = 20) -> trimesh.Trimesh:
    """Rounded flat strip swept along a path.

    width — the broad visible face (seen from behind the head); scalar or 1-D array
    depth — the slim edge dimension (seen from the side); scalar or 1-D array
    The outer (+w_ax) side is the spine; the inner (-w_ax) side is where teeth attach.
    The cross-section is a squircle rather than a sharp rectangle so the printed
    part reads as molded plastic with softened edges.
    """
    n = len(points)
    # Broadcast scalar width/depth to per-point arrays
    widths = np.broadcast_to(np.atleast_1d(np.asarray(width, dtype=float)), (n,)).copy()
    depths = np.broadcast_to(np.atleast_1d(np.asarray(depth, dtype=float)), (n,)).copy()
    verts: list = []
    faces: list = []
    for i, p in enumerate(points):
        if i == 0:
            tang = points[1] - points[0]
        elif i == n - 1:
            tang = points[-1] - points[-2]
        else:
            tang = points[i + 1] - points[i - 1]
        tang = tang / np.linalg.norm(tang)
        d_ax = np.array([0.0, 1.0, 0.0])
        w_ax = np.cross(d_ax, tang)
        if np.linalg.norm(w_ax) < 1e-6:
            w_ax = np.array([1.0, 0.0, 0.0])
        w_ax /= np.linalg.norm(w_ax)
        d_ax = np.cross(tang, w_ax)
        d_ax /= np.linalg.norm(d_ax)
        hw, hd = widths[i] / 2.0, depths[i] / 2.0
        # Superellipse/squircle section: still reads as a flat strip, but the
        # corners are rounded and the side highlights become much more refined.
        angles = np.linspace(0, 2 * np.pi, sections, endpoint=False)
        for a in angles:
            ca, sa = np.cos(a), np.sin(a)
            x = hw * np.sign(ca) * abs(ca) ** 0.48
            z = hd * np.sign(sa) * abs(sa) ** 0.48
            verts.append((p + x * w_ax + z * d_ax).tolist())
    for i in range(n - 1):
        for j in range(sections):
            a = i * sections + j
            b = i * sections + (j + 1) % sections
            c = (i + 1) * sections + (j + 1) % sections
            d2 = (i + 1) * sections + j
            faces += [(a, b, c), (a, c, d2)]
    sc = len(verts)
    verts.append(points[0].tolist())
    ec = len(verts)
    verts.append(points[-1].tolist())
    for j in range(sections):
        faces.append((sc, (j + 1) % sections, j))
        faces.append((ec, (n - 1) * sections + j, (n - 1) * sections + (j + 1) % sections))
    return trimesh.Trimesh(
        vertices=np.array(verts, dtype=float),
        faces=np.array(faces),
        process=True,
    )


def arm_points(side: int, n: int = 36) -> np.ndarray:
    """Back-of-head banana-clip arm path.

    Coordinates are millimeters. The clip sits on the back of a hair volume:
    x spreads left/right, y is back-front depth, z is vertical height.

    Y follows the back-of-hair ellipsoid so the arm wraps around the head
    shape — ends sit closer to the head, middle bows outward over the hair.
    """
    t = np.linspace(0.0, 1.0, n)
    z = 48.0 + 66.0 * t
    x = side * (6.0 + 22.0 * np.sin(np.pi * t) ** 0.68)
    # Follow the back-of-hair ellipsoid to create the side-view wrap visible
    # in real banana clips.
    hair_cy = 5.0
    hair_ry = 39.0
    hair_rx = 45.0
    hair_rz = 63.0
    hair_cz = 86.0
    ellipsoid_term = 1.0 - (x / hair_rx) ** 2 - ((z - hair_cz) / hair_rz) ** 2
    y_surface = hair_cy + hair_ry * np.sqrt(np.clip(ellipsoid_term, 0.035, None))
    offset = 2.0 + 16.0 * np.sin(np.pi * t) ** 1.15
    y = y_surface + offset
    return np.column_stack([x, y, z])


def hinge_origin() -> np.ndarray:
    left = arm_points(-1)
    return np.array([0.0, left[0, 1] - 0.8, left[0, 2]])


def hinge_knuckle_segments() -> list[tuple[float, float, int]]:
    """Y ranges for interleaved hinge barrels.

    Owner side is -1 for the left arm and +1 for the right arm. The gaps between
    adjacent barrels are intentional axial clearance, not modeling error.
    """
    return [
        (-7.00, -2.70, -1),
        (-2.30, 2.30, 1),
        (2.70, 7.00, -1),
    ]


def _smoothstep(t: np.ndarray) -> np.ndarray:
    """Classic smoothstep: 3t^2 - 2t^3, clamped to [0,1]."""
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def convex_prism_on_surface(
    center: np.ndarray,
    across_axis: np.ndarray,
    along_axis: np.ndarray,
    normal_axis: np.ndarray,
    coords: list[tuple[float, float]],
    thickness: float,
) -> trimesh.Trimesh:
    """Small filled relief pad on a curved arm surface."""
    across_axis = across_axis / np.linalg.norm(across_axis)
    along_axis = along_axis / np.linalg.norm(along_axis)
    normal_axis = normal_axis / np.linalg.norm(normal_axis)
    base = [center + across_axis * x + along_axis * y for x, y in coords]
    top = [p + normal_axis * thickness for p in base]
    n = len(coords)
    vertices = np.array(base + top, dtype=float)
    faces: list[tuple[int, int, int]] = []
    for i in range(1, n - 1):
        faces.append((0, i + 1, i))
        faces.append((n, n + i, n + i + 1))
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j))
        faces.append((i, n + j, n + i))
    mesh = trimesh.Trimesh(vertices=vertices, faces=np.array(faces, dtype=int), process=True)
    if mesh.volume < 0:
        mesh.invert()
    return mesh


def make_arm(side: int) -> tuple[trimesh.Trimesh, trimesh.Trimesh]:
    """Rounded flat-section arm with tapered ends, softened comb teeth, and integrated hook.

    Body: swept rounded strip that flows continuously from hinge join point through
    the arm curve and into the hook tip — no separate hook piece, so there is
    no boolean-union seam.
    Teeth: short rounded tapered strips along the inward direction, only in the
    non-tapered zone.
    """
    n_pts = 96
    pts = arm_points(side, n=n_pts)
    t = np.linspace(0.0, 1.0, n_pts)

    # Width profile: taper both ends over first/last 13% using smoothstep
    W_TIP = 3.5
    W_BODY = 11.0
    TAPER_W = 0.13
    left_blend = _smoothstep(t / TAPER_W)
    right_blend = _smoothstep((1.0 - t) / TAPER_W)
    blend_w = np.minimum(left_blend, right_blend)
    widths = W_TIP + (W_BODY - W_TIP) * blend_w

    # Depth profile: constant at 4.5 mm
    depths = np.full(n_pts, 4.5)

    # Compute hinge join point
    l0 = pts[0]
    pivot_y = (l0[1] + arm_points(-side, n=n_pts)[0][1]) / 2.0
    pivot_z = (l0[2] + arm_points(-side, n=n_pts)[0][2]) / 2.0
    pivot = np.array([0.0, pivot_y, pivot_z])
    barrel_r = HINGE_BARREL_RADIUS
    left_join = pivot + np.array([-barrel_r * 0.92 * float(side), 0.0, 0.0])

    # Hook path: starts inside the arm, blends gently out of the spine, then
    # returns inward with a small retaining beak so the two arm tips can hook
    # each other when closed.
    top = pts[-1]
    hook_t = np.linspace(0.0, 1.0, 42)
    hook_path = []
    for u in hook_t:
        ease = _smoothstep(np.array([u]))[0]
        curl = np.sin(np.pi * u)
        hook_path.append(top + np.array([
            side * (
                0.06
                + 2.55 * ease
                - 2.20 * max(u - 0.42, 0.0) ** 1.02
                - 3.10 * max(u - 0.78, 0.0) ** 1.72
            ),
            -0.20 - 2.20 * ease - 0.55 * max(u - 0.72, 0.0) ** 1.10,
            -2.20 + 10.10 * ease - 2.10 * curl - 1.10 * max(u - 0.86, 0.0) ** 1.15,
        ]))
    hook_path = np.array(hook_path)

    hook_widths = 3.55 + 1.10 * np.sin(np.pi * hook_t) ** 0.90
    hook_depths = 4.15 + 0.45 * np.sin(np.pi * hook_t) ** 0.92

    # Full path: hinge join → arm curve → hook extension
    hinge_lead = np.array([
        left_join,
        left_join * 0.55 + pts[0] * 0.45 + np.array([side * 0.15, 0.0, 0.0]),
    ])
    full_path = np.vstack([hinge_lead, pts, hook_path])

    # Width/depth profiles
    hinge_widths = np.array([6.2, 4.8])
    hinge_depths = np.array([7.2, 5.2])
    full_widths = np.concatenate([hinge_widths, widths, hook_widths])
    full_depths = np.concatenate([hinge_depths, depths, hook_depths])

    arm_body = swept_flat_strip(full_path, full_widths, full_depths, sections=80)
    hook_root_fairing = ellipsoid_at(
        top + np.array([side * 0.72, -0.60, 1.35]),
        (2.45, 1.95, 2.40),
    )
    hook_beak_path = np.array([
        hook_path[-5],
        hook_path[-2],
        hook_path[-1] + np.array([-side * 1.30, -0.15, -1.20]),
    ])
    hook_beak = swept_flat_strip(
        hook_beak_path,
        np.array([2.50, 1.90, 1.20]),
        np.array([2.45, 1.85, 1.15]),
        sections=40,
    )
    hook_cap = ellipsoid_at(
        hook_beak_path[-1],
        (
            1.18,
            1.05,
            1.28,
        ),
    )

    # Inward direction: toward clip centre with a slight rearward lean
    inward = np.array([-float(side), -0.10, 0.0])
    inward /= np.linalg.norm(inward)

    # Tooth widths and depths along inward direction
    tooth_widths = np.array([2.5, 2.4, 2.2, 1.9, 1.2])
    tooth_depths = np.array([1.3, 1.2, 1.0, 0.8, 0.4])
    tooth_offsets = np.array([0.0, 2.5, 5.0, 7.5, 9.5])

    tooth_parts = []
    for i in range(n_pts):
        if t[i] < 0.13 or t[i] > 0.87:
            continue
        if (i % 3) != 0:
            continue
        p = pts[i]
        root = p + inward * max(widths[i] / 2.0 - 2.2, 0.8)
        tooth_pts = np.array([root + inward * off for off in tooth_offsets])
        tooth_parts.append(swept_flat_strip(tooth_pts, tooth_widths, tooth_depths, sections=20))

    teeth = trimesh.util.concatenate(tooth_parts)
    return trimesh.util.concatenate([arm_body, hook_root_fairing, hook_beak, hook_cap]), teeth


def make_pin_with_cotter_hole(pivot: np.ndarray, pin_inner_span: float, pin_outer_span: float, cotter_y: float) -> trimesh.Trimesh:
    """Clevis-style pin with a real transverse cotter hole near the outer end."""
    pin_a = pivot - np.array([0.0, pin_inner_span, 0.0])
    pin_b = pivot + np.array([0.0, pin_outer_span, 0.0])

    if cq is None:
        # Fallback keeps the visible pin printable, but cannot subtract the
        # transverse cotter hole without a boolean kernel.
        return trimesh.util.concatenate([
            cylinder_between(pin_a, pin_b, HINGE_PIN_RADIUS, sections=96),
            cylinder_between(
                pin_a - np.array([0.0, 0.72, 0.0]),
                pin_a + np.array([0.0, 0.28, 0.0]),
                3.20,
                sections=96,
            ),
            ellipsoid_at(pin_a - np.array([0.0, 0.18, 0.0]), (3.20, 0.82, 3.20)),
            cylinder_between(
                pin_b - np.array([0.0, 0.08, 0.0]),
                pin_b + np.array([0.0, 0.28, 0.0]),
                HINGE_PIN_RADIUS + 0.10,
                sections=96,
            ),
        ])

    shaft = cq.Solid.makeCylinder(
        HINGE_PIN_RADIUS,
        pin_inner_span + pin_outer_span,
        cq.Vector(*pin_a),
        cq.Vector(0, 1, 0),
    )
    inner_head = cq.Solid.makeCylinder(
        3.20,
        1.00,
        cq.Vector(*(pin_a - np.array([0.0, 0.72, 0.0]))),
        cq.Vector(0, 1, 0),
    )
    comfort_tip = cq.Solid.makeCylinder(
        HINGE_PIN_RADIUS + 0.10,
        0.36,
        cq.Vector(*(pin_b - np.array([0.0, 0.08, 0.0]))),
        cq.Vector(0, 1, 0),
    )
    pin = shaft.fuse(inner_head).fuse(comfort_tip)
    cotter_bore = cq.Solid.makeCylinder(
        HINGE_COTTER_HOLE_RADIUS,
        13.0,
        cq.Vector(pivot[0] - 6.5, cotter_y, pivot[2]),
        cq.Vector(1, 0, 0),
    )
    pin = pin.cut(cotter_bore)
    try:
        pin = pin.fillet(0.24, pin.Edges())
    except Exception:
        pass
    return cq_shape_to_trimesh(pin, tolerance=0.035, angular_tolerance=0.025)


def make_cotter_key(pivot: np.ndarray, cotter_y: float) -> trimesh.Trimesh:
    """Printable cotter key: a straight peg through the pin hole plus a pull loop."""
    z = pivot[2]
    y = cotter_y
    peg = cylinder_between(
        np.array([pivot[0] - 4.25, y, z]),
        np.array([pivot[0] + 5.10, y, z]),
        HINGE_COTTER_RADIUS,
        sections=24,
    )
    pull_loop_path = np.array([
        [pivot[0] + 4.70, y, z],
        [pivot[0] + 7.30, y, z + 0.80],
        [pivot[0] + 8.35, y, z + 3.25],
        [pivot[0] + 7.30, y, z + 5.70],
        [pivot[0] + 4.70, y, z + 6.50],
    ])
    pull_loop = swept_elliptical_tube(
        pull_loop_path,
        width_radius=0.82,
        depth_radius=0.82,
        sections=18,
    )
    insertion_tip = sphere_at(np.array([pivot[0] - 4.25, y, z]), HINGE_COTTER_RADIUS * 0.94)
    return fuse_meshes([peg, pull_loop, insertion_tip], "hinge_cotter")


def make_hinge_and_hooks() -> tuple[trimesh.Trimesh, trimesh.Trimesh, trimesh.Trimesh, trimesh.Trimesh]:
    """Return (left_barrels, right_barrels, pin, cotter) — hinge hardware pieces.

    The arm body sweep now starts at the hinge join point and flows continuously
    through the arm into the hook, so there is no separate knuckle base piece.
    This function only produces the hinge barrels, pin, and cotter.

    Assembly sequence:
      1. Slide arms together — inner barrel nests between the two outer barrels.
      2. Push pin through from the open (no-flange) end until the head flange seats.
      3. Slide the cotter peg through the transverse hole in the pin.
         The pull loop remains outside the hinge for removal.

    Hinge dimensions for daily-use PETG durability:
      - Barrel OD 7.4 mm, pin bore 4.7 mm → 1.35 mm wall (adequate for PETG/nylon)
      - Reduced Y-span keeps the hinge visually tighter while preserving a three-zone load path
      - 4 mm pin diameter: no fatigue fracture under normal opening cycles
      - Cotter cross-bore: 2.7 mm dia transverse hole 3.5 mm from exit face
    """
    left_pts = arm_points(-1, n=96)
    right_pts = arm_points(+1, n=96)

    l0, r0 = left_pts[0], right_pts[0]
    pivot = np.array([0.0, (l0[1] + r0[1]) / 2.0, (l0[2] + r0[2]) / 2.0])

    barrel_r = HINGE_BARREL_RADIUS
    bore_r = HINGE_BARREL_BORE_RADIUS
    pin_half = 7.0
    left_join = pivot + np.array([-barrel_r * 0.92, 0.0, 0.0])
    right_join = pivot + np.array([barrel_r * 0.92, 0.0, 0.0])

    # ---- Left barrels: rounded cheek bridges + outer barrel cylinders ----
    left_parts = []
    for y_anchor in (-5.00, 5.00):
        left_parts.append(swept_flat_strip(
            np.array([
                left_join + np.array([-0.24, 0.0, -0.10]),
                pivot + np.array([-barrel_r * 0.83, y_anchor * 0.56, -0.08]),
                pivot + np.array([-barrel_r * 0.70, y_anchor, -0.06]),
            ]),
            width=np.array([4.35, 3.90, 3.35]),
            depth=np.array([4.00, 3.45, 3.10]),
            sections=48,
        ))
    for y0, y1 in [(-pin_half, -2.70), (2.70, pin_half)]:
        left_parts.append(hollow_cylinder_between(
            pivot + np.array([0.0, y0, 0.0]),
            pivot + np.array([0.0, y1, 0.0]),
            barrel_r,
            bore_r,
        ))

    # ---- Right barrels: rounded cheek bridge + inner barrel cylinder ----
    right_parts = []
    right_parts.append(swept_flat_strip(
        np.array([
            right_join + np.array([0.24, 0.0, -0.10]),
            pivot + np.array([barrel_r * 0.83, 0.0, -0.08]),
            pivot + np.array([barrel_r * 0.70, 0.0, -0.06]),
        ]),
        width=np.array([4.65, 4.25, 3.75]),
        depth=np.array([4.00, 3.55, 3.10]),
        sections=48,
    ))
    right_parts.append(hollow_cylinder_between(
        pivot + np.array([0.0, -2.30, 0.0]),
        pivot + np.array([0.0, +2.30, 0.0]),
        barrel_r,
        bore_r,
    ))

    # ---- Pin piece: low-profile scalp-side head + plain outer end for cotter ----
    # Inner face (negative Y, toward scalp): a short round-edged head keeps the
    # pin from sliding through while staying smooth against the head.
    # Outer face (positive Y, away from head): no large flange; the cotter alone
    # retains the pin and keeps the visible hinge lighter.
    pin_inner_span = pin_half + 0.10
    pin_outer_span = pin_half + 2.85

    # ---- Cotter piece: straight printed peg with pull loop ----
    # Bore stays on the outer side of the clip, clear of the scalp side.
    cotter_y = pivot[1] + pin_outer_span - 2.25
    pin = make_pin_with_cotter_hole(pivot, pin_inner_span, pin_outer_span, cotter_y)
    cotter = make_cotter_key(pivot, cotter_y)

    return (
        trimesh.util.concatenate(left_parts),
        trimesh.util.concatenate(right_parts),
        pin,
        cotter,
    )


def make_tulip_relief(side: int) -> trimesh.Trimesh:
    """Shallow filled tulip relief on the large outward-facing arm face.

    The tulip pads are sunk slightly into the broad flat face visible from the
    back of the head. This makes them visible in Bambu Studio without turning
    them into tall, fragile flower buds.
    """
    n_pts = 96
    pts = arm_points(side, n=n_pts)
    t   = np.linspace(0.0, 1.0, n_pts)

    W_TIP, W_BODY, TAPER_W = 3.5, 11.0, 0.13
    blend_w = np.minimum(_smoothstep(t / TAPER_W), _smoothstep((1.0 - t) / TAPER_W))
    widths  = W_TIP + (W_BODY - W_TIP) * blend_w
    rear_axis = np.array([0.0, -1.0, 0.0])

    relief_path = []
    frames = {}
    for idx, p in enumerate(pts):
        if t[idx] < 0.19 or t[idx] > 0.81:
            continue

        i0 = max(0, idx - 1)
        i1 = min(n_pts - 1, idx + 1)
        tang = pts[i1] - pts[i0]
        tang = tang / np.linalg.norm(tang)
        d_ax = np.array([0.0, 1.0, 0.0])
        w_ax = np.cross(d_ax, tang)
        if np.linalg.norm(w_ax) < 1e-6:
            w_ax = np.array([1.0, 0.0, 0.0])
        w_ax = w_ax / np.linalg.norm(w_ax)

        outward  = float(side) * w_ax
        # Put the pattern on the broad surface visible in the rear/plate view, not on the
        # narrow spine edge. It sits within the central flat field of the arm so
        # Bambu Studio shows actual tulip geometry rather than tiny diamonds.
        surface = p + rear_axis * 1.55 + outward * min(0.75, widths[idx] * 0.10)
        relief_path.append(surface)
        frames[idx] = (surface, outward, tang)

    bud_indices = {
        min(frames.keys(), key=lambda key: abs(key - int(t_pos * (n_pts - 1))))
        for t_pos in [0.26, 0.38, 0.50, 0.62, 0.74]
    }

    relief_parts = []
    tulip_coords = [
        (0.00, -1.65),
        (1.55, -0.95),
        (2.10, -0.05),
        (1.25, 0.85),
        (0.55, 1.45),
        (0.00, 2.35),
        (-0.55, 1.45),
        (-1.25, 0.85),
        (-2.10, -0.05),
        (-1.55, -0.95),
    ]
    for idx in sorted(bud_indices):
        anchor, outward, tang = frames[idx]
        flower_center = anchor + tang * 0.85
        relief_parts.append(convex_prism_on_surface(
            flower_center,
            outward,
            tang,
            rear_axis,
            tulip_coords,
            thickness=0.36,
        ))

    return trimesh.util.concatenate(relief_parts)


def make_decorative_inlay() -> trimesh.Trimesh:
    """Outer spine is the flat face of the strip; no separate inlay needed."""
    return trimesh.Trimesh()


def make_head_and_hair() -> tuple[trimesh.Trimesh, trimesh.Trimesh, trimesh.Trimesh]:
    head = trimesh.creation.uv_sphere(segments=64, ring_count=32, radius=1.0)
    head.apply_scale([40.0, 32.0, 58.0])
    head.apply_translation([0.0, 0.0, 83.0])

    hair = trimesh.creation.uv_sphere(segments=64, ring_count=32, radius=1.0)
    hair.apply_scale([45.0, 39.0, 63.0])
    hair.apply_translation([0.0, 5.0, 86.0])

    neck = trimesh.creation.cylinder(radius=14.0, height=34.0, sections=40)
    neck.apply_translation([0.0, -3.0, 18.0])
    return head, hair, neck


def _glossy_face_colors(mesh: trimesh.Trimesh, face_indices: np.ndarray, color: str, alpha: float) -> np.ndarray:
    """Per-face Phong-like shading for glossy plastic preview renders."""
    base = np.array(mcolors.to_rgb(color), dtype=float)
    vertex_normals = np.zeros_like(mesh.vertices, dtype=float)
    for col in range(3):
        np.add.at(vertex_normals, mesh.faces[:, col], mesh.face_normals)
    vertex_normals /= np.maximum(np.linalg.norm(vertex_normals, axis=1)[:, None], 1e-9)
    face_vertices = mesh.faces[face_indices]
    normals = vertex_normals[face_vertices].mean(axis=1)
    normals /= np.maximum(np.linalg.norm(normals, axis=1)[:, None], 1e-9)
    light = np.array([-0.35, -0.55, 0.76], dtype=float)
    light /= np.linalg.norm(light)
    view = np.array([0.0, -0.18, 0.98], dtype=float)
    view /= np.linalg.norm(view)
    half_vec = light + view
    half_vec /= np.linalg.norm(half_vec)

    diffuse = np.clip(normals @ light, 0.0, 1.0)
    specular = np.clip(normals @ half_vec, 0.0, 1.0) ** 34.0
    rim = np.clip(1.0 - np.abs(normals @ view), 0.0, 1.0) ** 2.0

    shade = 0.32 + 0.58 * diffuse
    rgb = base[None, :] * shade[:, None]
    rgb += 0.42 * specular[:, None]
    rgb += 0.10 * rim[:, None]
    rgb = np.clip(rgb, 0.0, 1.0)
    return np.column_stack([rgb, np.full(len(face_indices), alpha)])


def render(
    meshes,
    colors,
    alphas,
    path: Path,
    elev: float = 12,
    azim: float = -90,
    title: str | None = None,
    auto_fit: bool = False,
    glossy: bool = True,
) -> None:
    fig = plt.figure(figsize=(8, 10), facecolor="white")
    ax = fig.add_subplot(111, projection="3d")
    for mesh, color, alpha in zip(meshes, colors, alphas):
        face_indices = np.arange(len(mesh.faces))
        if len(face_indices) > 120000:
            face_indices = face_indices[np.linspace(0, len(face_indices) - 1, 120000).astype(int)]
        faces = mesh.faces[face_indices]
        tris = mesh.vertices[faces]
        coll = Poly3DCollection(tris, linewidths=0.0, alpha=alpha, antialiaseds=False)
        if glossy:
            coll.set_facecolor(_glossy_face_colors(mesh, face_indices, color, alpha))
        else:
            coll.set_facecolor(color)
        coll.set_edgecolor((0.03, 0.03, 0.03, 0.0 if auto_fit else 0.035))
        ax.add_collection3d(coll)
    ax.view_init(elev=elev, azim=azim)
    aspect = np.array([1.0, 0.52, 1.25])
    if auto_fit:
        bounds = np.array([mesh.bounds for mesh in meshes if len(mesh.vertices)])
        lo = bounds[:, 0, :].min(axis=0)
        hi = bounds[:, 1, :].max(axis=0)
        span = np.maximum(hi - lo, 1.0)
        margin = span * 0.12
        ax.set_xlim(lo[0] - margin[0], hi[0] + margin[0])
        ax.set_ylim(lo[1] - margin[1], hi[1] + margin[1])
        ax.set_zlim(lo[2] - margin[2], hi[2] + margin[2])
        aspect = span
    else:
        ax.set_xlim(-58, 58)
        ax.set_ylim(15, 75)
        ax.set_zlim(10, 152)
    ax.set_box_aspect(aspect)
    ax.set_axis_off()
    ax.set_title(title or "Refactored banana clip fit: flattened rails + normal comb teeth", fontsize=13, pad=10)
    fig.tight_layout(pad=0)
    fig.savefig(path, dpi=180, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)


def orient_for_print(mesh: trimesh.Trimesh, rot_x_deg: float) -> trimesh.Trimesh:
    m = mesh.copy()
    if rot_x_deg:
        transform = trimesh.transformations.rotation_matrix(np.radians(rot_x_deg), [1, 0, 0])
        m.apply_transform(transform)
    bounds = m.bounds
    m.apply_translation(-bounds[0])
    return m


def make_one_color_plate(pieces: list[tuple[str, trimesh.Trimesh, float]]) -> tuple[list[trimesh.Trimesh], trimesh.Trimesh]:
    """Arrange the printable pieces on one 256 x 256 mm build plate."""
    arranged = []
    cursor_x = 10.0
    cursor_y = 12.0
    row_height = 0.0
    plate_limit = 246.0
    spacing = 12.0

    for _name, mesh, rot_x in pieces:
        m = orient_for_print(mesh, rot_x)
        size = m.bounds[1] - m.bounds[0]
        if cursor_x + size[0] > plate_limit:
            cursor_x = 10.0
            cursor_y += row_height + spacing
            row_height = 0.0
        m.apply_translation([cursor_x, cursor_y, 0.0])
        arranged.append(m)
        cursor_x += size[0] + spacing
        row_height = max(row_height, size[1])

    plate = trimesh.creation.box(extents=[256.0, 256.0, 0.6])
    plate.apply_translation([128.0, 128.0, -0.35])
    return arranged, plate


def export_ascii_stl(mesh: trimesh.Trimesh, path: Path, name: str) -> None:
    """Write high-precision ASCII STL for reliable validation reloads."""
    with path.open("w") as fh:
        fh.write(f"solid {name}\n")
        for normal, tri in zip(mesh.face_normals, mesh.triangles):
            fh.write(f"  facet normal {normal[0]:.12g} {normal[1]:.12g} {normal[2]:.12g}\n")
            fh.write("    outer loop\n")
            for vertex in tri:
                fh.write(f"      vertex {vertex[0]:.12g} {vertex[1]:.12g} {vertex[2]:.12g}\n")
            fh.write("    endloop\n")
            fh.write("  endfacet\n")
        fh.write(f"endsolid {name}\n")


def main() -> None:
    head, hair, neck = make_head_and_hair()
    left_rail, left_teeth = make_arm(-1)
    right_rail, right_teeth = make_arm(+1)
    left_barrels, right_barrels, pin, cotter = make_hinge_and_hooks()
    left_flowers  = make_tulip_relief(-1)
    right_flowers = make_tulip_relief(+1)

    # The arm body sweep is now continuous from hinge join through arm to hook.
    # Only the hinge barrels (anchor blocks, cheek blocks, hollow cylinders) are
    # separate pieces that get boolean-unioned with the arm body.
    left_meshes   = [left_rail,  left_teeth,  left_barrels]
    right_meshes  = [right_rail, right_teeth, right_barrels]
    pin_meshes    = [pin]
    cotter_meshes = [cotter]
    flower_meshes = [left_flowers, right_flowers]

    left_colors   = ["#1e3a5f", "#162d4a", "#1e3a5f"]
    right_colors  = ["#2a6b8a", "#1e5070", "#2a6b8a"]
    pin_colors    = ["#8ab0c8"]
    cotter_colors = ["#c8900a"]
    flower_colors = ["#21385a", "#2a6683"]

    left_alphas   = [0.97, 1.0, 0.97]
    right_alphas  = [0.97, 1.0, 0.97]
    pin_alphas    = [1.0]
    cotter_alphas = [1.0]
    flower_alphas = [1.0, 1.0]

    # Export STLs — one per printable piece + combined fit-check assembly
    left_piece  = fuse_meshes(left_meshes + [left_flowers], "arm_left")
    right_piece = fuse_meshes(right_meshes + [right_flowers], "arm_right")
    printable_clip_meshes = [left_piece, right_piece, pin, cotter]
    printable_clip_colors = ["#1e3a5f", "#2a6b8a", "#8ab0c8", "#c8900a"]
    printable_clip_alphas = [1.0, 1.0, 1.0, 1.0]

    export_ascii_stl(orient_for_print(left_piece, -90),  OUT / "arm_left.stl",     "arm_left")
    export_ascii_stl(orient_for_print(right_piece, -90), OUT / "arm_right.stl",    "arm_right")
    export_ascii_stl(orient_for_print(pin, 90),          OUT / "hinge_pin.stl",    "hinge_pin")
    export_ascii_stl(orient_for_print(cotter, 90),       OUT / "hinge_cotter.stl", "hinge_cotter")
    plate_pieces, build_plate = make_one_color_plate([
        ("arm_left", left_piece, -90),
        ("arm_right", right_piece, -90),
        ("hinge_pin", pin, 90),
        ("hinge_cotter", cotter, 90),
    ])
    export_ascii_stl(
        trimesh.util.concatenate(plate_pieces),
        OUT / "print_plate_one_color.stl",
        "print_plate_one_color",
    )
    clip = trimesh.util.concatenate(printable_clip_meshes)
    export_ascii_stl(clip, OUT / "photo_refactored_fit_demo_clip.stl", "photo_refactored_fit_demo_clip")
    export_ascii_stl(
        trimesh.util.concatenate([head, hair, neck, clip]),
        OUT / "photo_refactored_head_hair_clip_fit.stl",
        "photo_refactored_head_hair_clip_fit",
    )
    render(
        [head, neck, hair] + printable_clip_meshes,
        ["#c8906a", "#c8906a", "#3d2010"] + printable_clip_colors,
        [0.28, 0.55, 0.15] + printable_clip_alphas,
        ASSETS / "photo_refactored_fit_demo.png",
        elev=15,
        azim=90,
        title="Banana clip on hair — rear view",
    )
    render(
        printable_clip_meshes,
        printable_clip_colors,
        printable_clip_alphas,
        ASSETS / "actual_clip_hinge_side.png",
        elev=8,
        azim=0,
        title="Clip only: side profile  (navy=left arm · teal=right arm · light=pin)",
        auto_fit=True,
    )
    render(
        printable_clip_meshes,
        printable_clip_colors,
        printable_clip_alphas,
        ASSETS / "clip_rear_view.png",
        elev=18,
        azim=-90,
        title="Clip: rear view — 4 printable pieces + embedded tulip relief",
        auto_fit=True,
    )
    render(
        printable_clip_meshes,
        printable_clip_colors,
        printable_clip_alphas,
        ASSETS / "clip_three_quarter.png",
        elev=25,
        azim=-140,
        title="Clip: three-quarter rear view",
        auto_fit=True,
    )
    render(
        plate_pieces + [build_plate],
        ["#151515"] * len(plate_pieces) + ["#e5e5df"],
        [1.0] * len(plate_pieces) + [0.22],
        ASSETS / "one_color_print_plate.png",
        elev=90,
        azim=-90,
        title="One-colour print plate: all four pieces fit on a 256 x 256 mm bed",
        auto_fit=True,
        glossy=False,
    )
    print(ASSETS / "photo_refactored_fit_demo.png")
    print(ASSETS / "actual_clip_hinge_side.png")
    print(ASSETS / "clip_rear_view.png")
    print(ASSETS / "clip_three_quarter.png")
    print(ASSETS / "one_color_print_plate.png")
    print(OUT / "photo_refactored_head_hair_clip_fit.stl")


if __name__ == "__main__":
    main()
