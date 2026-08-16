"""Drive the shipped coverage checker and helper constructors.

The coverage checker reads the real skill markdown (not a reimplementation
of ZeroWork). The helper test imports zw_helpers from a consumer module
path, not by executing zw_helpers.py as __main__.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError("cannot load %s from %s" % (name, path))
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestSkillCoverage(unittest.TestCase):
    def test_every_palette_type_and_official_url_has_operational_fields(self):
        check = _load("zw_check_skill_coverage", SCRIPTS / "check_skill_coverage.py")
        result = check.evaluate()
        self.assertEqual(
            result["missing"],
            [],
            "skill coverage gaps:\n" + "\n".join(result["missing"]),
        )
        self.assertGreater(result["covered"], 0)
        self.assertEqual(result["covered"], result["total"])
        self.assertGreaterEqual(len(result["types"]), 44)
        self.assertGreaterEqual(len(result["urls"]), 44)


class TestHelpersFromConsumer(unittest.TestCase):
    def test_edge_payload_from_fresh_import(self):
        helpers = _load("zw_helpers_consumer", SCRIPTS / "zw_helpers.py")
        payload = helpers.zw_edge_payload(1044, 2099)
        self.assertEqual(payload["id"], "reactflow__edge-1044a-2099a")
        self.assertEqual(payload["source"], "1044")
        self.assertEqual(payload["target"], "2099")
        self.assertEqual(payload["sourceHandle"], "a")
        self.assertEqual(payload["targetHandle"], "a")
        self.assertEqual(payload["type"], "buttonEdge")
        self.assertIs(payload["deletable"], False)

    def test_auto_align_selectors_from_fresh_import(self):
        helpers = _load("zw_helpers_consumer_align", SCRIPTS / "zw_helpers.py")
        sel = helpers.zw_auto_align_selectors()
        self.assertEqual(sel["button"], ".react-flow__controls-button")
        self.assertIn("Auto-align top to bottom", sel["top_to_bottom"])


class TestCuaHelpers(unittest.TestCase):
    def test_find_card_group_picks_large_parent_not_the_text(self):
        cua = _load("zw_cua_consumer", SCRIPTS / "zw_cua.py")
        elements = [
            {
                "element_index": 10,
                "role": "Group",
                "label": None,
                "frame": {"w": 114, "h": 115, "x": 0, "y": 0},
            },
            {
                "element_index": 11,
                "role": "Group",
                "label": None,
                "frame": {"w": 26, "h": 88, "x": 0, "y": 0},
            },
            {
                "element_index": 12,
                "role": "Text",
                "label": "Open Link",
                "frame": {"w": 88, "h": 26, "x": 0, "y": 0},
            },
        ]
        hit = cua.zw_cua_find_card_group(elements, "Open Link")
        self.assertIsNotNone(hit)
        self.assertEqual(hit["element_index"], 10)


if __name__ == "__main__":
    unittest.main()
