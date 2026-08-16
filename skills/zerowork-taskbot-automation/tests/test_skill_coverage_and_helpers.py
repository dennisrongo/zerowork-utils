"""Drive the shipped coverage checker and helper constructors.

The coverage checker reads the real skill markdown (not a reimplementation
of ZeroWork). The helper test imports zw_helpers from a consumer module
path, not by executing zw_helpers.py as __main__.
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
TEMPLATES = SKILL_ROOT / "templates"


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


class TestSelectorAndXFeedDocs(unittest.TestCase):
    def test_find_selector_and_pattern7_are_documented(self):
        refs = SKILL_ROOT / "references"
        prim = (refs / "platform-primitives.md").read_text(encoding="utf-8")
        pats = (refs / "build-patterns.md").read_text(encoding="utf-8")
        self.assertIn("### Find a selector (live page)", prim)
        self.assertIn("article[data-testid=\"tweet\"]", prim)
        self.assertIn("primaryColumn", prim)
        self.assertIn("scroll round", prim)
        self.assertIn("## Pattern 7", pats)
        self.assertIn("https://x.com/home", pats)
        self.assertIn("Page down", pats)
        self.assertIn("sticky", pats.lower())
        editor = (refs / "creator-editor-automation.md").read_text(encoding="utf-8")
        self.assertIn("dropped", editor.lower())
        self.assertIn("require is not defined", editor)


class TestWriteJsAuthoringAndRenameDocs(unittest.TestCase):
    def test_official_copy_ai_contract_and_rename_recipe(self):
        refs = SKILL_ROOT / "references"
        wjs = (refs / "write-javascript.md").read_text(encoding="utf-8")
        editor = (refs / "creator-editor-automation.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        rest = (refs / "rest-api.md").read_text(encoding="utf-8")
        catalog = (refs / "block-catalog.md").read_text(encoding="utf-8")

        self.assertIn("## Authoring for a human in the Write JS drawer", wjs)
        self.assertIn("Copy AI instructions", wjs)
        self.assertIn("You are helping me write code for ZeroWork", wjs)
        self.assertIn("I am currently inside the Write JavaScript building block", wjs)
        self.assertIn("My references", wjs)
        self.assertIn("ONE best solution", wjs)
        self.assertIn("directly pasteable", wjs)
        self.assertIn("exposeFunction", wjs)
        self.assertIn("require is not defined", wjs)
        self.assertIn("getTaskbotInfo", wjs)
        # Official docs use 4-digit examples. Live workspace ids are longer.
        self.assertNotRegex(wjs, r"ref_id:\s*\d{5,}")

        self.assertIn("### Rename nodes", editor)
        self.assertIn("There is **no REST node rename**", editor)
        self.assertIn("Ctrl+A", editor)
        self.assertIn("Delete DataClear previous rows", editor)
        self.assertIn("PATCH /connector", editor)
        self.assertIn("Copy AI instructions", editor)

        self.assertIn("Ctrl+A", skill)
        self.assertIn("Rename nodes", skill)
        self.assertIn("pasteable", skill)
        self.assertIn("Copy AI instructions", skill)

        self.assertIn("does **not**", rest)
        self.assertIn("TaskBot", rest)
        self.assertIn("Copy AI instructions", catalog)

        self.assertIn("Same Chrome pid, several windows", editor)
        self.assertIn("bring_to_front", editor)
        self.assertIn("Back to Main Menu", editor)
        self.assertIn("only **selects**", editor)
        self.assertIn("Undo delete", editor)
        self.assertIn("My references", catalog)


class TestSelfContainedScripts(unittest.TestCase):
    """The skill ships the scripts a successor needs. No Temp, no secrets."""

    REQUIRED_SCRIPTS = (
        "zw_helpers.py",
        "zw_cua.py",
        "zw_api.py",
        "zw_inspect.py",
        "zw_assemble.py",
        "zw_canvas.py",
        "zw_rename.py",
        "zw_fill_notes.py",
        "check_skill_coverage.py",
    )
    REQUIRED_TEMPLATES = (
        "zw_drag.py",
        "x_feed_harvest.js",
        "linkedin_feed_harvest.js",
        "x_feed_nocode.json",
        "linkedin_feed.json",
    )
    # Generic leak shapes only — never list a real token, hash, or workspace id.
    LEAK_PATTERNS = (
        re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\."),
        re.compile(r"hash_password\s*[:=]"),
        re.compile(r"['\"]user_id['\"]\s*:\s*['\"]?\d{4,}"),
    )

    def test_shipped_scripts_and_templates_exist(self):
        for name in self.REQUIRED_SCRIPTS:
            self.assertTrue((SCRIPTS / name).is_file(), name)
        for name in self.REQUIRED_TEMPLATES:
            self.assertTrue((TEMPLATES / name).is_file(), name)

    def test_docs_point_at_shipped_scripts(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        readme = (SKILL_ROOT.parents[1] / "README.md").read_text(encoding="utf-8")
        rest = (SKILL_ROOT / "references" / "rest-api.md").read_text(encoding="utf-8")
        editor = (SKILL_ROOT / "references" / "creator-editor-automation.md").read_text(
            encoding="utf-8"
        )
        for blob in (skill, readme):
            self.assertIn("zw_api.py", blob)
            self.assertIn("zw_canvas.py", blob)
            self.assertIn("x_feed_harvest.js", blob)
        self.assertIn("ZW_ACCESS", rest)
        self.assertIn("zw_rename.py", editor)
        self.assertIn("zw_fill_notes.py", editor)

    def test_repo_and_skill_have_no_token_or_claim_payloads(self):
        roots = [SKILL_ROOT, SKILL_ROOT.parents[1]]
        skip_parts = {".git", "__pycache__", "node_modules"}
        suffixes = {".md", ".py", ".js", ".json", ".sh", ".txt", ".yml", ".yaml"}
        checked = 0
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if not path.is_file() or path.suffix.lower() not in suffixes:
                    continue
                if any(part in skip_parts for part in path.parts):
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
                checked += 1
                for pat in self.LEAK_PATTERNS:
                    hit = pat.search(text)
                    self.assertIsNone(
                        hit,
                        "%s matches %s: %r" % (path, pat.pattern, hit.group(0) if hit else ""),
                    )
        self.assertGreater(checked, 10)

    def test_access_token_comes_from_env_not_source(self):
        api = _load("zw_api_consumer", SCRIPTS / "zw_api.py")
        saved = {
            key: os.environ.get(key)
            for key in ("ZW_ACCESS", "ZW_ACCESS_FILE", "ZW_REFRESH", "ZW_REFRESH_FILE")
        }
        try:
            os.environ["ZW_ACCESS"] = "test-access-token"
            os.environ.pop("ZW_ACCESS_FILE", None)
            os.environ.pop("ZW_REFRESH", None)
            os.environ.pop("ZW_REFRESH_FILE", None)
            self.assertEqual(api.load_access(allow_refresh=False), "test-access-token")
            os.environ.pop("ZW_ACCESS", None)
            with self.assertRaises(api.TokenError):
                api.load_access(allow_refresh=False)
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_canvas_target_requires_env(self):
        canvas = _load("zw_canvas_consumer", SCRIPTS / "zw_canvas.py")
        saved = {
            key: os.environ.get(key)
            for key in ("ZW_CUA_PID", "ZW_CUA_WINDOW_ID", "ZW_CUA_SESSION")
        }
        try:
            os.environ.pop("ZW_CUA_PID", None)
            os.environ.pop("ZW_CUA_WINDOW_ID", None)
            with self.assertRaises(canvas.CuaTargetError):
                canvas.target_from_env()
            os.environ["ZW_CUA_PID"] = "4242"
            os.environ["ZW_CUA_WINDOW_ID"] = "99"
            target = canvas.target_from_env()
            self.assertEqual(target.pid, 4242)
            self.assertEqual(target.window_id, 99)
            self.assertEqual(target.session, "zw-canvas")
        finally:
            for key, value in saved.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_item_cells_map_through_column_ids(self):
        api = _load("zw_api_cells", SCRIPTS / "zw_api.py")
        colmap = api.columns_by_id(
            {"results": [{"id": 1, "name": "author"}, {"id": 2, "colName": "post_url"}]}
        )
        row = api.item_as_dict(
            {"id": 9, "cells": [{"column_id": 1, "text": "Ada"}, {"column_id": 2, "text": "https://x.com/a"}]},
            colmap,
        )
        self.assertEqual(row["author"], "Ada")
        self.assertEqual(row["post_url"], "https://x.com/a")
        self.assertEqual(row["id"], 9)

    def test_yellow_cluster_and_js_line_helpers(self):
        canvas = _load("zw_canvas_helpers", SCRIPTS / "zw_canvas.py")
        cents = canvas.cluster_xy([(10, 20), (12, 22), (80, 21), (82, 23)], n_bands=2)
        self.assertEqual(len(cents), 2)
        self.assertLess(cents[0][0], cents[1][0])
        self.assertTrue(canvas.is_sticky_yellow(230, 220, 140))
        self.assertFalse(canvas.is_sticky_yellow(10, 10, 10))
        lines = canvas.js_lines_for_type_text("function a() {\n  return 1;\n}")
        self.assertEqual(lines[0], "function a() {")
        self.assertIn("\r\n", canvas.js_crlf("a\nb"))

    def test_rename_map_parser(self):
        rename = _load("zw_rename_consumer", SCRIPTS / "zw_rename.py")
        pairs = rename.parse_map(["Open Link=Open X home", "Delay=Wait for timeline"])
        self.assertEqual(pairs[0], ("Open Link", "Open X home"))
        with self.assertRaises(ValueError):
            rename.parse_map(["noscale"])

    def test_assemble_spec_loads_without_account_ids(self):
        assemble = _load("zw_assemble_consumer", SCRIPTS / "zw_assemble.py")
        spec = assemble.load_spec(TEMPLATES / "x_feed_nocode.json")
        self.assertEqual(spec["table"]["name"], "x_feed_posts")
        self.assertIn("post_url", spec["table"]["columns"])
        keys = {n["key"] for n in spec["nodes"]}
        self.assertIn("pagedown", keys)
        self.assertIn(["try", "outer"], spec["edges"])

    def test_harvest_templates_resolve_table_at_runtime(self):
        xjs = (TEMPLATES / "x_feed_harvest.js").read_text(encoding="utf-8")
        lijs = (TEMPLATES / "linkedin_feed_harvest.js").read_text(encoding="utf-8")
        for src in (xjs, lijs):
            self.assertIn("getTaskbotInfo", src)
            self.assertIn("var TABLE = 0", src)
            self.assertIn("appendIndex", src)
            self.assertNotRegex(src, r"\bTABLE\s*=\s*[1-9]\d*")
        self.assertIn('article[data-testid="tweet"]', xjs)
        self.assertIn("primaryColumn", xjs)
        self.assertIn("scroll round", xjs)
        self.assertIn("feed-shared-update-v2", lijs)
        self.assertIn("post_urn", lijs)


if __name__ == "__main__":
    unittest.main()
