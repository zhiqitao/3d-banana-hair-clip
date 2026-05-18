from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import trimesh

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import config as C
import banana_clip_design_final as G


def load_cq_generator():
    path = ROOT / "cadquery" / "banana_clip_cq.py"
    spec = importlib.util.spec_from_file_location("banana_clip_cq", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CadQueryGeneratorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.generator = load_cq_generator()
        cls.tmp = tempfile.TemporaryDirectory()
        cls.step_out = Path(cls.tmp.name) / "outputs_step"
        cls.stl_out = Path(cls.tmp.name) / "outputs_cad_stl"
        cls.generated = cls.generator.generate(cls.step_out, cls.stl_out)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_expected_files_are_generated(self):
        expected = [
            "upper_arm",
            "lower_arm",
            "pin_loose",
            "pin_nominal",
            "pin_snug",
            "tolerance_kit",
            "elastic_helper",
            "hinge_stress_coupon",
            "tooth_slot_coupon",
            "snap_latch_coupon",
            "comfort_radius_coupon",
            "coupon_plate_first",
        ]
        for stem in expected:
            self.assertTrue((self.step_out / f"{stem}.step").exists())
            self.assertTrue((self.stl_out / f"{stem}.stl").exists())

    def test_step_files_are_non_empty(self):
        for path in self.step_out.glob("*.step"):
            self.assertGreater(path.stat().st_size, 1024, path.name)

    def test_exported_stls_are_watertight(self):
        for path in self.stl_out.glob("*.stl"):
            mesh = trimesh.load(path, force="mesh")
            self.assertTrue(mesh.is_watertight, path.name)

    def test_pin_clearances_match_config(self):
        self.assertAlmostEqual(self.generator.G.PIN_HOLE_RADIUS - C.PIN_RADIUS_MM, C.PIN_CLEARANCE_MM)
        self.assertGreaterEqual(self.generator.G.PIN_HOLE_RADIUS - C.PIN_VARIANTS_MM["pin_snug"], 0.35)

    def test_tooth_slot_collision_checks_pass_2d(self):
        upper_body = G.slotted_body_polygon(+1)
        lower_body = G.slotted_body_polygon(-1)
        self.assertLess(upper_body.intersection(G.teeth_union(-1)).area, 1e-4)
        self.assertLess(lower_body.intersection(G.teeth_union(+1)).area, 1e-4)
        self.assertLess(G.non_hinge_profile(+1).intersection(G.non_hinge_profile(-1)).area, 1e-4)

    def test_hinge_knuckle_z_ranges_are_interleaved(self):
        ranges = {}
        for side, name in [(+1, "upper"), (-1, "lower")]:
            base = G.non_hinge_profile(side)
            boss = G.hinge_boss_polygon(side)
            ranges[name] = []
            for z0, z1, poly in G.arm_layer_profiles(side):
                if poly.difference(base).intersection(boss).area > 1.0:
                    ranges[name].append((z0, z1))
        self.assertEqual(len(ranges["upper"]), 2)
        self.assertEqual(len(ranges["lower"]), 1)
        for uz0, uz1 in ranges["upper"]:
            for lz0, lz1 in ranges["lower"]:
                self.assertLessEqual(min(uz1, lz1) - max(uz0, lz0), 1e-6)


if __name__ == "__main__":
    unittest.main()
