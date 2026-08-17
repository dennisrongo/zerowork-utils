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
        self.assertIn("harvest", keys)
        self.assertIn(["try", "outer"], spec["edges"])
        self.assertIn(["delay", "harvest"], spec["edges"])
        self.assertIn(["harvest", "try"], spec["edges"])
        self.assertNotIn(["try", "harvest"], spec["edges"])

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


class TestXFeedLiveCanvasRules(unittest.TestCase):
    """Live Demo - X Feed Scraper rules a weaker model must not invent."""

    NOTE_TEXTS = (
        "Agent Chrome must be signed into X. Creator tab login does not count.",
        "Write JS harvest-while-scroll: X remounts tweet cards. Dedup column is post_id.",
        "Stop after 3 empty scroll rounds or 40 unique posts.",
        "Outer N = scroll rounds, not tweet count.",
    )

    def test_spec_has_harvest_pointer_and_four_note_texts(self):
        assemble = _load("zw_assemble_live", SCRIPTS / "zw_assemble.py")
        spec = assemble.load_spec(TEMPLATES / "x_feed_nocode.json")
        harvest = next(n for n in spec["nodes"] if n["key"] == "harvest")
        self.assertEqual(harvest["type"], "write_js")
        self.assertEqual(harvest["name"], "Harvest while scroll")
        self.assertIn("x_feed_harvest.js", harvest["source"])
        # Spec-only fill hints. REST cannot write Monaco or note bodies.
        for banned in ("code", "javascript", "script", "run_locally", "content"):
            self.assertNotIn(banned, harvest)
        texts = [n.get("text") for n in spec["nodes"] if n.get("type") == "sticky_note"]
        self.assertEqual(len(texts), 4)
        for expected in self.NOTE_TEXTS:
            self.assertIn(expected, texts)

    def test_docs_encode_live_canvas_mechanics(self):
        refs = SKILL_ROOT / "references"
        editor = (refs / "creator-editor-automation.md").read_text(encoding="utf-8")
        pats = (refs / "build-patterns.md").read_text(encoding="utf-8")
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        catalog = (refs / "block-catalog.md").read_text(encoding="utf-8")
        wjs = (refs / "write-javascript.md").read_text(encoding="utf-8")

        for blob in (editor, pats, skill):
            self.assertIn("top strip", blob.lower())
            self.assertIn("Harvest while scroll", blob)
            self.assertIn("yank", blob.lower())
        self.assertIn("unconnected", editor.lower())
        self.assertIn("write js", editor.lower())
        self.assertIn("detect errors", editor.lower())
        self.assertIn("orphan", editor.lower())
        self.assertIn("Run locally", pats)
        self.assertIn("post_id", pats)
        self.assertIn("3 empty scroll rounds", pats)
        for expected in self.NOTE_TEXTS:
            self.assertIn(expected, editor)
            self.assertIn(expected, pats)
        self.assertIn("top strip", catalog.lower())
        self.assertIn("yank", catalog.lower())
        self.assertIn("Run locally", wjs)
        self.assertIn("Harvest while scroll", wjs)
        self.assertIn("setValue", skill)
        self.assertIn("Ctrl+A", skill)

    def test_spec_try_is_three_wire_harvest_before_try(self):
        assemble = _load("zw_assemble_three_wire", SCRIPTS / "zw_assemble.py")
        spec = assemble.load_spec(TEMPLATES / "x_feed_nocode.json")
        try_outs = [e[1] for e in spec["edges"] if e[0] == "try"]
        self.assertCountEqual(try_outs, ["outer", "catch", "after_try"])
        self.assertIn(["delay", "harvest"], spec["edges"])
        self.assertIn(["harvest", "try"], spec["edges"])
        self.assertNotIn(["try", "harvest"], spec["edges"])
        raw = (TEMPLATES / "x_feed_nocode.json").read_text(encoding="utf-8")
        self.assertNotIn("87460", raw)
        for node in spec["nodes"]:
            self.assertNotIn("id", node)

    def test_spec_fill_hints_match_live_drawers(self):
        assemble = _load("zw_assemble_fill", SCRIPTS / "zw_assemble.py")
        spec = assemble.load_spec(TEMPLATES / "x_feed_nocode.json")
        by_key = {n["key"]: n for n in spec["nodes"]}
        self.assertIn("post_assemble", spec)
        self.assertIn("no REST drawer write", spec["post_assemble"])

        url = by_key["save_url"]["fill"]
        self.assertEqual(
            url["selector"],
            "(//article[@data-testid='tweet'])[{loop_index}]//a[contains(@href,'/status/')]",
        )
        self.assertIn(">> nth=", url["selector_css"])
        self.assertIn('article[data-testid="tweet"]', url["selector_css"])
        self.assertEqual(url["save_as"], "Link")
        self.assertEqual(url["table"], "x_feed_posts")
        self.assertEqual(url["column"], "post_url")
        self.assertIs(url["skip_if_missing"], False)

        author = by_key["save_author"]["fill"]
        self.assertEqual(
            author["selector"],
            '(//article[@data-testid="tweet"])[{loop_index}]//*[@data-testid="User-Name"]',
        )
        self.assertEqual(author["save_as"], "Text")
        self.assertEqual(author["table"], "x_feed_posts")
        self.assertEqual(author["column"], "author")

        text_fill = by_key["save_text"]["fill"]
        self.assertEqual(
            text_fill["selector"],
            '(//article[@data-testid="tweet"])[{loop_index}]//*[@data-testid="tweetText"]',
        )
        self.assertEqual(text_fill["save_as"], "Text")
        self.assertIs(text_fill["skip_if_missing"], True)
        self.assertEqual(text_fill["table"], "x_feed_posts")
        self.assertEqual(text_fill["column"], "post_text")

        time_fill = by_key["save_time"]["fill"]
        self.assertEqual(
            time_fill["selector"],
            '(//article[@data-testid="tweet"])[{loop_index}]//time',
        )
        self.assertEqual(time_fill["save_as"], "Custom attribute")
        self.assertEqual(time_fill["attribute"], "datetime")
        self.assertEqual(time_fill["table"], "x_feed_posts")
        self.assertEqual(time_fill["column"], "posted_at")
        self.assertIs(time_fill["skip_if_missing"], True)

        outer = by_key["outer"]["fill"]
        self.assertEqual(outer["repeat"], "Standard")
        self.assertEqual(outer["count"], "Fixed")
        self.assertEqual(outer["times"], 6)
        self.assertIs(outer["auto_scroll"], False)

        inner = by_key["inner"]["fill"]
        self.assertEqual(inner["repeat"], "Standard")
        self.assertEqual(inner["count"], "Count")
        self.assertEqual(inner["selector"], 'article[data-testid="tweet"]')

        self.assertEqual(by_key["pagedown"]["fill"]["key"], "PageDown")

        delete = by_key["delete"]["fill"]
        self.assertEqual(delete["table"], "x_feed_posts")
        self.assertEqual(delete["scope"], "Delete all rows")

        launch = by_key["launch"]["fill"]
        self.assertEqual(launch["bypass_bot_detection"], "On")
        self.assertEqual(launch["other_groups"], "Use current defaults")

        self.assertEqual(by_key["open"]["fill"]["url"], "https://x.com/home")

        delay = by_key["delay"]["fill"]
        self.assertEqual(delay["min"], 4)
        self.assertEqual(delay["max"], 6)

        wait_new = by_key["wait_new"]["fill"]
        self.assertEqual(wait_new["min"], 2)
        self.assertEqual(wait_new["max"], 2)
        self.assertIn("min 1 / max 1", wait_new["live"])
        self.assertIn("Do not silently change the live bot", wait_new["live"])

        dedupe = by_key["dedupe"]["fill"]
        self.assertEqual(dedupe["table"], "x_feed_posts")
        self.assertEqual(dedupe["column"], "post_url")
        self.assertIs(dedupe["preserve_newest"], False)

        harvest = by_key["harvest"]
        for banned in ("code", "javascript", "script", "run_locally", "content", "fill"):
            self.assertNotIn(banned, harvest)

    def test_docs_encode_three_wire_and_drawer_fill(self):
        refs = SKILL_ROOT / "references"
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        rest = (refs / "rest-api.md").read_text(encoding="utf-8")
        editor = (refs / "creator-editor-automation.md").read_text(encoding="utf-8")
        pats = (refs / "build-patterns.md").read_text(encoding="utf-8")
        for blob in (skill, rest, editor, pats):
            self.assertIn("up to three connections", blob)
            self.assertNotIn("87460", blob)
        self.assertIn("second click on the card body", skill)
        self.assertIn("second click on the card body", editor)
        self.assertIn("second click on the card body", pats)
        self.assertIn('[@data-testid="User-Name"]', pats)
        self.assertIn('[@data-testid="tweetText"]', pats)
        self.assertIn("skip-if-missing", pats)
        self.assertIn("PageDown", pats)
        self.assertIn("empty key", pats.lower())
        self.assertIn("datetime", pats)
        self.assertIn("posted_at", pats)
        self.assertIn("auto-scroll", pats.lower())
        self.assertIn("no REST drawer write", pats)
        self.assertIn("Wait for timeline → Harvest while scroll", pats)
        # Weaker model: fill posted_at; do not invent a missing time node.
        self.assertNotIn("node **MISSING**", pats)
        self.assertIn("below Save tweet text, already wired", pats)
        self.assertIn("Do not assume the time node is", pats)
        self.assertIn("skip-if-missing **ON**", pats)
        self.assertIn("Bypass bot detection", pats)
        self.assertIn("Use current defaults", pats)
        self.assertIn("Delete all rows", pats)
        self.assertIn("min **4** / max **6**", pats)
        self.assertIn("min 1 / max 1", pats)
        self.assertIn("recipe default", pats)
        self.assertIn("do not silently change the live bot", pats.lower())
        self.assertIn("Preserve newest", pats)
        self.assertIn("column `post_url`", pats)
        self.assertIn("Good news! The basic check found no errors.", pats)


class TestPattern4AdvancedLogicLiveRules(unittest.TestCase):
    """Live Demo - Advanced Logic (TryCatch+Conditions+Regex) rebuild rules."""

    NOTE_TEXTS = (
        "Click: intentional miss",
        "Catch: no outgoing edge on purpose; after_try is the proof",
        "Regex: strip £",
        "Start Condition: one operator per Set Condition + Else",
        "Start Repeat: set Standard",
        "Break: off Set Condition, not after last body",
    )

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
            "editor": (refs / "creator-editor-automation.md").read_text(encoding="utf-8"),
            "rest": (refs / "rest-api.md").read_text(encoding="utf-8"),
        }

    def test_fake_selector_and_proof_log(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("definitely-not-present-element", pats)
        self.assertIn("TRY-CATCH TEST: run continued after error", pats)
        self.assertIn("https://books.toscrape.com/", pats)
        self.assertIn("price_raw", pats)
        self.assertIn("£51.77", pats)
        self.assertIn("/£/", pats)
        self.assertIn("price_clean", pats)
        self.assertIn("PRICE HIGH branch taken (>50)", pats)
        self.assertIn("{id, name: price_raw}", pats)
        self.assertIn("My references", pats)
        self.assertIn("Replace text", pats)
        for expected in self.NOTE_TEXTS:
            self.assertIn(expected, pats)
        # Catalog also names the fake selector so Click skip-if-not-found
        # cannot swallow the intentional miss.
        self.assertIn("definitely-not-present-element", docs["catalog"])
        self.assertIn("TRY-CATCH TEST: run continued after error", docs["rest"])

    def test_unset_loop_type_footgun(self):
        docs = self._docs()
        for key in ("pats", "skill", "catalog"):
            blob = docs[key]
            self.assertIn("UNSET", blob)
            self.assertIn("Standard", blob)
        self.assertIn("neither Standard nor Dynamic", docs["pats"])
        self.assertIn("Detect errors may stay quiet", docs["pats"])
        self.assertIn("Detect errors may stay quiet", docs["catalog"])
        self.assertIn("before a client build", docs["pats"])
        self.assertIn("Set **Standard**", docs["pats"])
        self.assertIn("footgun", docs["pats"].lower())
        self.assertIn("footgun", docs["catalog"].lower())

    def test_catch_dead_end_is_intentional(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("Catch-dead-end is intentional", pats)
        self.assertIn("no outgoing edge on purpose", pats)
        self.assertIn("after_try is the proof", pats)
        self.assertIn("Do not wire catch", pats)
        self.assertIn("dead-end on purpose", docs["skill"])
        self.assertIn("no outgoing edge", docs["skill"])
        self.assertIn("dead-end on purpose", docs["catalog"])
        self.assertIn("no outgoing edge", docs["catalog"])
        self.assertIn("Do not wire `catch", docs["catalog"])
        # Catch / After-Try / Break have no drawer
        for blob in (pats, docs["skill"], docs["catalog"], docs["editor"]):
            self.assertIn("no drawer", blob.lower())
        self.assertIn("After-Try", docs["catalog"])
        self.assertIn("Break", docs["catalog"])

    def test_no_baked_workflow_or_node_ids(self):
        docs = self._docs()
        for blob in docs.values():
            self.assertNotIn("87452", blob)
            # Do not copy a live 5-digit-looking Variables id into the skill.
            self.assertNotRegex(blob, r"\{id:\s*\d{5,}")

    def test_detect_errors_toast_can_hang_without_banner(self):
        docs = self._docs()
        for key in ("pats", "skill", "editor"):
            self.assertIn("please wait", docs[key])
            self.assertIn("no result banner", docs[key])


class TestPattern5HttpMathPipelineLiveRules(unittest.TestCase):
    """Live Demo - HTTP + Math Pipeline rebuild rules."""

    NOTE_TEXTS = (
        "HTTP must SAVE RESPONSE or the call is a no-op",
        "math writes back to fx_x100",
        "ChatGPT one-word classify",
    )

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
        }

    def test_frankfurter_url_and_empty_save_response_footgun(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn(
            "https://api.frankfurter.app/latest?from=USD&to=GBP", pats
        )
        self.assertIn("SAVE RESPONSE", pats)
        self.assertIn("ALL EMPTY", pats)
        self.assertIn("no-op", pats.lower())
        self.assertIn("footgun", pats.lower())
        self.assertIn("Detect errors can stay quiet", pats)
        self.assertIn("discarded", pats.lower())
        self.assertIn(
            "https://api.frankfurter.app/latest?from=USD&to=GBP",
            docs["catalog"],
        )
        self.assertIn("SAVE RESPONSE", docs["catalog"])
        self.assertIn("all empty", docs["catalog"].lower())
        self.assertIn("no-op", docs["catalog"].lower())
        self.assertIn("footgun", docs["catalog"].lower())
        self.assertIn("Detect errors can stay quiet", docs["catalog"])
        self.assertIn("SAVE RESPONSE", docs["skill"])
        self.assertIn("no-op", docs["skill"].lower())
        self.assertIn("all empty", docs["skill"].lower())

    def test_multiply_chatgpt_prompt_and_notes(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("2.5", pats)
        self.assertIn("Multiply", pats)
        self.assertIn("fx_x100", pats)
        self.assertIn("gpt_answer", pats)
        self.assertIn(
            "Classify this number as HIGH or LOW in one word, nothing else: {fx_x100}",
            pats,
        )
        self.assertIn("Result: {fx_x100}", pats)
        self.assertIn("ChatGPT says: {gpt_answer}", pats)
        self.assertIn("ChatGPT 5.5", pats)
        self.assertIn("My references", pats)
        self.assertIn("{id, name", pats)
        for expected in self.NOTE_TEXTS:
            self.assertIn(expected, pats)
        self.assertIn("2.5", docs["catalog"])
        self.assertIn("fx_x100", docs["catalog"])
        self.assertIn("gpt_answer", docs["catalog"])
        self.assertIn(
            "Classify this number as HIGH or LOW in one word, nothing else: {fx_x100}",
            docs["catalog"],
        )
        self.assertIn("fx_x100", docs["skill"])
        self.assertIn("gpt_answer", docs["skill"])
        self.assertIn("2.5", docs["skill"])
        self.assertIn("HIGH or LOW", docs["skill"])
        self.assertIn("My references", docs["skill"])

    def test_no_baked_workflow_or_variable_ids(self):
        docs = self._docs()
        for blob in docs.values():
            self.assertNotIn("87454", blob)
            self.assertNotIn("199826", blob)
            self.assertNotRegex(blob, r"\{id:\s*\d{5,}")


class TestNodePlaygroundCoverageMap(unittest.TestCase):
    """Live Demo - Node Playground is a living coverage map, not a client bot."""

    PRESENT = (
        "check",
        "element_present",
        "element_absent",
        "hover",
        "select",
        "run_taskbot",
        "update_variable",
        "format_data",
        "delete_table_data",
        "ask_chatgpt",
        "sticky_note",
        "tabs",
        "save_file",
        "sleep",
        "update_or_configure_api",
        "math",
        "throw",
        "catch",
        "try",
        "after_try",
        "loop_exit",
        "check_dynamic_data",
        "conditionNode",
        "split_data",
        "regex",
        "remove_duplicate_rows",
        "screenshot",
        "insert_data",
        "navigate",
        "save_url",
        "quit_browser",
        "switch_frame",
        "accept_dialog",
        "abort",
        "email",
        "upload",
        "insert_date",
        "save_clipboard",
    )

    MISSING_PALETTE = (
        "open_link",
        "launch_browser",
        "click",
        "save",
        "keyboard",
        "loop",
        "continue_after_repeat",
        "write_js",
        "log",
    )

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "types": (refs / "node-types.md").read_text(encoding="utf-8"),
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "run": (refs / "run-semantics.md").read_text(encoding="utf-8"),
        }

    def test_census_and_husk_lesson(self):
        docs = self._docs()
        for key in ("pats", "types", "skill"):
            blob = docs[key]
            self.assertIn("25", blob)
            self.assertIn("node-default", blob)
            self.assertIn("never ship", blob.lower())
            self.assertIn("client bot", blob.lower())
            self.assertIn("living coverage map", blob.lower())
            self.assertIn("incomplete vs the 44", blob.lower())
        for key in ("pats", "types"):
            blob = docs[key]
            self.assertIn("65 canvas nodes", blob)
            self.assertIn("40 named", blob)
            self.assertIn("25 dead husks", blob)
            self.assertIn("react-flow__node-default", blob)
            self.assertIn("react-flow__node-<type>", blob)
            self.assertIn("Write a note...", blob)
            self.assertIn("please wait", blob)
            self.assertIn("no result banner", blob)
            self.assertIn("Node Playground", blob)
        self.assertIn("25 dead", docs["run"])
        self.assertIn("node-default", docs["run"])
        self.assertIn("never on a client bot", docs["run"].lower())
        self.assertIn("**Node Playground**", docs["pats"])

    def test_missing_palette_types_are_coverage_holes(self):
        docs = self._docs()
        check = _load(
            "zw_check_skill_coverage_playground",
            SCRIPTS / "check_skill_coverage.py",
        )
        palette = [
            t
            for t in check.parse_palette_types(docs["types"])
            if t not in check.BRANCH_TYPES
        ]
        self.assertEqual(len(palette), 44)
        computed = [t for t in palette if t not in set(self.PRESENT)]
        self.assertEqual(computed, list(self.MISSING_PALETTE))
        self.assertEqual(len(self.MISSING_PALETTE), 9)
        for blob in (docs["pats"], docs["types"]):
            self.assertIn("NOT on this playground", blob)
            self.assertIn("coverage holes", blob)
            for t in self.MISSING_PALETTE:
                self.assertIn("`%s`" % t, blob)
            for t in self.PRESENT:
                self.assertIn("`%s`" % t, blob)
        self.assertIn("incomplete vs the 44", docs["skill"].lower())

    def test_no_baked_workflow_or_node_ids(self):
        docs = self._docs()
        for blob in docs.values():
            self.assertNotIn("87451", blob)
        for key in ("pats", "types"):
            self.assertIn(
                "Do **not** treat a workflow id or node",
                docs[key],
            )
            self.assertIn("required handle", docs[key])


class TestNodePlaygroundDrawerSchemas(unittest.TestCase):
    """Live Node Playground drawer schemas a weaker model must not invent."""

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "types": (refs / "node-types.md").read_text(encoding="utf-8"),
        }

    def _section(self, blob: str, heading: str) -> str:
        start = blob.find(heading)
        self.assertGreaterEqual(start, 0, heading)
        nxt = blob.find("\n## ", start + len(heading))
        return blob[start: nxt if nxt != -1 else None]

    def test_found_not_found_are_no_drawer_markers(self):
        docs = self._docs()
        for key in ("catalog", "skill", "types"):
            blob = docs[key]
            self.assertIn("no-drawer", blob)
            self.assertIn("Found", blob)
            self.assertIn("Not Found", blob)
            self.assertIn("edge wiring", blob)
            self.assertIn("not a", blob.lower())
            self.assertIn("field", blob.lower())
        catalog = docs["catalog"]
        check = self._section(catalog, "## Check Web Element")
        self.assertIn("Selector must be visible on screen", check)
        self.assertIn("no-drawer", check)
        self.assertIn("edge wiring off Check", check)
        self.assertIn("not a\n  drawer field", check)
        hover = self._section(catalog, "## Hover Web Element")
        self.assertNotIn("Selector must be visible on screen", hover.replace("No** \"Selector must be visible on screen\"", ""))
        self.assertIn("No", hover)
        self.assertIn("Selector must be visible on screen", hover)
        self.assertIn("Check-only", hover)

    def test_run_taskbot_wait_checkbox(self):
        docs = self._docs()
        for key in ("catalog", "skill"):
            blob = docs[key]
            self.assertIn("Wait until the TaskBot finishes", blob)
            self.assertIn("CHECKED", blob)
            self.assertIn("sync", blob.lower())
            self.assertIn("fire-and-forget", blob.lower())
            self.assertIn("No min/max", blob)
        run = self._section(docs["catalog"], "## Run TaskBot")
        self.assertIn("Select a TaskBot", run)
        self.assertIn("CHECKED = sync", run)
        self.assertIn("1.1.75", run)

    def test_raise_error_two_report_checkboxes(self):
        docs = self._docs()
        for key in ("catalog", "skill"):
            blob = docs[key]
            self.assertIn("A custom error was raised.", blob)
            self.assertIn("Mark this TaskBot run as failed in the run report", blob)
            self.assertIn("Include this error in the error report", blob)
            self.assertIn("unchecked", blob.lower())
        throw = self._section(docs["catalog"], "## Raise Error")
        self.assertIn("both **unchecked** live", throw)

    def test_insert_text_spintax_checked_by_default(self):
        docs = self._docs()
        for key in ("catalog", "skill"):
            self.assertIn("Use spintax", docs[key])
            self.assertRegex(docs[key], r"CHECKED by default")
        insert = self._section(docs["catalog"], "## Insert Text or Data")
        self.assertIn("Use spintax** CHECKED by default", insert)
        self.assertIn("Don't press Enter on\n  line breaks", insert)
        self.assertIn("PRO / FAST", insert)
        self.assertIn("65-90 wpm", insert)
        self.assertIn("Insert instantly", insert)

    def test_go_back_neither_selected_footgun(self):
        docs = self._docs()
        for key in ("catalog", "skill"):
            blob = docs[key]
            self.assertIn("dead default footgun", blob)
            self.assertIn("Go back", blob)
            self.assertIn("Go forward", blob)
            self.assertIn("neither", blob.lower())
        nav = self._section(docs["catalog"], "## Go Back or Forward")
        self.assertIn("neither** selected", nav)
        self.assertIn("dead default footgun", nav)

    def test_no_baked_playground_workflow_or_node_ids(self):
        docs = self._docs()
        for blob in docs.values():
            self.assertNotIn("87451", blob)


    def test_browser_alert_palette_label(self):
        docs = self._docs()
        for key in ("catalog", "skill", "types"):
            blob = docs[key]
            self.assertIn("Browser Alert", blob)
            self.assertIn("Accept/Dismiss Dialog", blob)
            self.assertIn("dialog", blob.lower())
        alert = self._section(docs["catalog"], "## Browser Alert")
        self.assertIn("Prompt response", alert)
        self.assertIn("0/0", alert)
        self.assertIn("No explicit Accept vs Dismiss", alert)
        self.assertIn("Browser Alert", alert)
        self.assertIn("Accept/Dismiss Dialog", alert)

    def test_abort_run_has_no_drawer(self):
        docs = self._docs()
        for key in ("catalog", "skill", "types"):
            blob = docs[key]
            self.assertIn("Abort Run", blob)
            self.assertIn("no drawer", blob.lower())
        abort = self._section(docs["catalog"], "## Abort Run")
        self.assertIn("No drawer", abort)
        self.assertIn("no configurable fields", abort.lower())
        self.assertIn("Abort / Stop TaskBot", abort)

    def test_send_notification_has_no_to_field(self):
        docs = self._docs()
        for key in ("catalog", "skill"):
            blob = docs[key]
            self.assertIn("signed-in account email", blob)
            self.assertIn("no to", blob.lower())
            self.assertIn("Subject", blob)
            self.assertIn("Email content", blob)
        notify = self._section(docs["catalog"], "## Send Notification")
        self.assertIn("No To: field", notify)
        self.assertIn("signed-in account email", notify)
        self.assertNotIn("input[email]", notify)
        self.assertNotIn("To:", notify.replace("No To: field", ""))

    def test_switch_frame_neither_selected(self):
        docs = self._docs()
        for key in ("catalog", "skill"):
            blob = docs[key]
            self.assertIn("Iframe", blob)
            self.assertIn("Main page", blob)
            self.assertIn("neither", blob.lower())
        frame = self._section(docs["catalog"], "## Switch Frame")
        self.assertIn("neither** selected", frame)
        self.assertIn("dead default", frame)
        self.assertIn("Go Back", frame)
        self.assertIn("0/0", frame)
        self.assertIn("Main frame", frame)
        self.assertIn("Main page", frame)
        self.assertTrue("#mce_0_ifr" in frame or "iframe" in frame)

    def test_upload_file_previous_step_tip(self):
        docs = self._docs()
        tip = "Make sure to initiate the upload by clicking the 'Upload' button in the previous step."
        self.assertIn(tip, docs["catalog"])
        self.assertIn(tip, docs["skill"])
        upload = self._section(docs["catalog"], "## Upload File")
        self.assertIn(tip, upload)
        self.assertIn("From file URL", upload)
        self.assertIn("From folder path on your computer", upload)
        self.assertIn("neither", upload.lower())

    def test_skill_tree_has_no_raw_email_addresses(self):
        email = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
        skip_parts = {".git", "__pycache__", "node_modules"}
        suffixes = {".md", ".py", ".js", ".json", ".txt"}
        checked = 0
        for path in SKILL_ROOT.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in suffixes:
                continue
            if any(part in skip_parts for part in path.parts):
                continue
            if path.name.startswith("_patch_"):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            checked += 1
            hit = email.search(text)
            self.assertIsNone(
                hit,
                "%s contains a raw email address: %r" % (path, hit.group(0) if hit else ""),
            )
        self.assertGreater(checked, 10)


class TestPattern8FormInputSelectUpload(unittest.TestCase):
    """Live Demo - Form Input Select Upload rebuild rules."""

    NOTE_TEXTS = (
        "Insert Text selector is the INPUT not the label",
        "Select needs the <select> selector AND the option text",
        "Upload File requires a prior click on the file input",
        "Number inputs still use Insert Text",
        "Switch Frame first, then Insert Text targets the inner document",
        "Shadow DOM: Insert Text often fails. Write JS on shadowRoot.",
    )

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
            "editor": (refs / "creator-editor-automation.md").read_text(encoding="utf-8"),
        }

    def test_the_internet_urls_and_selectors(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 8", pats)
        self.assertIn("Demo - Form Input Select Upload", pats)
        self.assertIn("the-internet.herokuapp.com", pats)
        self.assertIn("not a client form", pats)
        self.assertIn("https://the-internet.herokuapp.com/login", pats)
        self.assertIn("https://the-internet.herokuapp.com/dropdown", pats)
        self.assertIn("https://the-internet.herokuapp.com/upload", pats)
        self.assertIn("https://the-internet.herokuapp.com/inputs", pats)
        self.assertIn("https://the-internet.herokuapp.com/iframe", pats)
        self.assertIn("https://the-internet.herokuapp.com/checkboxes", pats)
        self.assertIn("https://the-internet.herokuapp.com/shadowdom", pats)
        self.assertIn("#checkboxes input:nth-of-type(1)", pats)
        self.assertIn('span[slot="my-text"]', pats)
        self.assertIn("input[type=number]", pats)
        self.assertIn("body#tinymce", pats)
        self.assertIn("#username", pats)
        self.assertIn("#password", pats)
        self.assertIn("#dropdown", pats)
        self.assertIn("Option 2", pats)
        self.assertIn("tomsmith", pats)
        self.assertIn("SuperSecretPassword!", pats)
        self.assertIn("published the-internet demo password", pats)
        self.assertIn("public", pats.lower())
        self.assertIn("not a secret", pats.lower())
        self.assertIn('button[type="submit"]', pats)
        self.assertIn("#file-upload", pats)
        self.assertIn("#file-submit", pats)
        for key in ("skill", "catalog"):
            blob = docs[key]
            self.assertIn("#username", blob)
            self.assertIn("#password", blob)
            self.assertIn("#dropdown", blob)
            self.assertIn("Option 2", blob)
            self.assertIn("the-internet.herokuapp.com", blob)
        self.assertIn("not a client form", docs["skill"])
        self.assertIn("Pattern 8", docs["skill"])

    def test_upload_file_source_and_prior_click(self):
        docs = self._docs()
        for key in ("pats", "skill", "catalog"):
            blob = docs[key]
            self.assertIn("From file URL", blob)
            self.assertIn("From folder path on your computer", blob)
            self.assertIn("Agent machine", blob)
            self.assertIn("creator browser", blob.lower())
            self.assertIn("portable", blob.lower())
            self.assertIn("names the node", blob)
            self.assertIn("#file-upload", blob)
        pats = docs["pats"]
        self.assertIn("prior click", pats.lower())
        self.assertIn("file input", pats.lower())
        self.assertIn("Click the file input", docs["skill"])
        self.assertIn("prior Click", docs["catalog"])
        gitignore = "https://raw.githubusercontent.com/github/gitignore/main/README.md"
        self.assertIn(gitignore, pats)
        self.assertIn("gitignore", pats)
        self.assertIn("README.md", pats)
        self.assertIn(gitignore, docs["skill"])
        self.assertIn(gitignore, docs["catalog"])

    def test_teaching_notes_and_hard_cases(self):
        docs = self._docs()
        pats = docs["pats"]
        for expected in self.NOTE_TEXTS:
            self.assertIn(expected, pats)
        self.assertIn("INPUT", docs["skill"])
        self.assertIn("not the label", docs["skill"])
        self.assertIn("<select>", docs["skill"])
        self.assertIn("option text", docs["skill"])
        self.assertIn("INPUT", docs["catalog"])
        self.assertIn("not the label", docs["catalog"])
        self.assertIn("<select>", docs["catalog"])
        self.assertIn("option text", docs["catalog"])
        self.assertIn("## Pattern 9", pats)
        self.assertIn("https://the-internet.herokuapp.com/inputs", pats)
        self.assertIn("input[type=number]", pats)
        self.assertIn("https://the-internet.herokuapp.com/iframe", pats)
        self.assertIn("Switch Frame", pats)
        self.assertIn("body#tinymce", pats)
        p8 = pats.split("## Pattern 8", 1)[1].split("## Pattern 9", 1)[0]
        self.assertLess(
            p8.find("Switch Frame"),
            p8.find("body#tinymce"),
            "Switch Frame then body#tinymce",
        )
        self.assertTrue(
            ("#mce_0_ifr" in p8) or ("`iframe`" in p8) or ("selector `iframe`" in p8),
            "Pattern 8 iframe requires an iframe selector",
        )
        self.assertIn("From file URL", pats)
        self.assertIn(
            "https://raw.githubusercontent.com/github/gitignore/main/README.md",
            pats,
        )
        self.assertIn("gitignore", pats)
        self.assertIn("README.md", pats)
        for key in ("skill", "catalog"):
            blob = docs[key]
            self.assertIn("input[type=number]", blob)
            self.assertIn("body#tinymce", blob)
            self.assertIn("Switch Frame", blob)
            self.assertIn(
                "https://raw.githubusercontent.com/github/gitignore/main/README.md",
                blob,
            )

    def test_checkboxes_and_shadow_hard_cases(self):
        docs = self._docs()
        pats = docs["pats"]
        p8 = pats.split("## Pattern 8", 1)[1].split("## Pattern 9", 1)[0]
        self.assertIn("https://the-internet.herokuapp.com/checkboxes", p8)
        self.assertIn("#checkboxes input:nth-of-type(1)", p8)
        self.assertIn("https://the-internet.herokuapp.com/shadowdom", p8)
        self.assertIn('span[slot="my-text"]', p8)
        self.assertIn("typed in shadow", p8)
        self.assertIn("slotted light DOM", p8.replace("**", ""))
        self.assertIn("shadowRoot", p8)
        self.assertIn("my-paragraph", p8)
        self.assertIn('slot name="my-text"', p8)
        self.assertIn("not an input", p8)
        self.assertIn("always Write JS", p8)
        self.assertIn("hard rule", p8)
        self.assertIn("document.querySelector('my-paragraph').shadowRoot", p8)
        self.assertIn("Run locally", p8)
        self.assertIn("pending ghost", p8)
        self.assertIn("right panel", p8)
        self.assertIn("Detect errors stayed green", p8)
        # Catalog Click / Insert Text lock the same selectors and inspect-first rule.
        catalog = docs["catalog"]
        self.assertIn("#checkboxes input:nth-of-type(1)", catalog)
        self.assertIn("https://the-internet.herokuapp.com/checkboxes", catalog)
        self.assertIn("https://the-internet.herokuapp.com/shadowdom", catalog)
        self.assertIn('span[slot="my-text"]', catalog)
        self.assertIn("slotted light DOM", catalog)
        self.assertIn("shadowRoot", catalog)
        self.assertIn("my-paragraph", catalog)
        self.assertIn("document.querySelector('my-paragraph').shadowRoot", catalog)
        self.assertIn("not an input", catalog)
        self.assertIn("always Write JS", catalog)
        self.assertIn("Run locally", catalog)
        skill = docs["skill"]
        self.assertIn("#checkboxes input:nth-of-type(1)", skill)
        self.assertIn('span[slot="my-text"]', skill)
        self.assertIn("slotted light DOM", skill)
        self.assertIn("shadowRoot", skill)
        self.assertIn("my-paragraph", skill)
        self.assertIn("not an input", skill)
        self.assertIn("always Write JS", skill)
        self.assertIn("pending ghost", skill)
        self.assertIn("right panel", skill)
        editor = docs["editor"]
        self.assertIn("pending ghost", editor)
        self.assertIn("right panel", editor)
        self.assertIn("Form Input Select Upload", editor)

    def test_no_baked_workflow_or_node_ids(self):
        docs = self._docs()
        for blob in docs.values():
            self.assertNotIn("87462", blob)
            self.assertNotRegex(blob, r"\{id:\s*\d{5,}")
        self.assertIn("required handle", docs["pats"])
        self.assertIn("Do **not** treat a workflow id or node", docs["pats"])


class TestCssFirstSelectorsAndPattern9(unittest.TestCase):
    """CSS-first incremental lists; XPath last resort; Pattern 9 tabs + nested loops."""

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "prim": (refs / "platform-primitives.md").read_text(encoding="utf-8"),
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
        }

    def test_version_is_1_3_17(self):
        skill = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("version: 1.3.17", skill)
        self.assertNotIn("version: 1.3.16", skill)

    def test_css_first_rule_and_nth_filter(self):
        docs = self._docs()
        for key in ("skill", "prim", "pats", "catalog"):
            blob = docs[key]
            self.assertIn("Prefer regular CSS selectors unless XPath is absolutely necessary", blob)
            self.assertIn(">> nth=", blob)
        prim = docs["prim"]
        self.assertIn(":nth-child({loop_index})", prim)
        self.assertIn("{loop_index,1}", prim)
        self.assertIn(">> nth={loop_index}", prim)
        self.assertIn("0-based", prim)
        self.assertIn("last resort", prim.lower())
        self.assertIn("not a reason to use xpath", prim.lower())
        self.assertIn("ol.row > li:nth-child({loop_index}) h3 a", prim)
        self.assertIn("article.product_pod >> nth={loop_index,1}", prim)
        self.assertIn("does **not** fix virtualized", prim)
        # old preferred XPath-for-grids recipe must not remain the default
        self.assertNotIn(
            "this skill prefers XPath positional predicates",
            prim,
        )
        catalog = docs["catalog"]
        self.assertNotIn(
            '(//article[contains(@class,"product_pod")])[{loop_index}]//h3/a',
            catalog,
        )
        self.assertIn(">> nth={loop_index,1}", catalog)
        self.assertIn(":nth-child({loop_index})", catalog)

    def test_pattern1_and_2_are_css(self):
        pats = self._docs()["pats"]
        p1 = pats.split("## Pattern 1", 1)[1].split("## Pattern 2", 1)[0]
        self.assertIn("ol.row > li:nth-child({loop_index}) h3 a", p1)
        self.assertIn("article.product_pod >> nth={loop_index,1}", p1)
        self.assertIn("**not** XPath", p1)
        self.assertNotIn(
            '(//article[contains(@class,"product_pod")])[{loop_index}]//h3/a',
            p1,
        )
        p2 = pats.split("## Pattern 2", 1)[1].split("## Pattern 3", 1)[0]
        self.assertIn("CSS {loop_index}", p2)
        self.assertIn("ol.row > li:nth-child({loop_index}) h3 a", p2)
        self.assertNotIn("XPath {loop_index} per column", p2)

    def test_pattern7_css_is_fallback_write_js_verified(self):
        pats = self._docs()["pats"]
        p7 = pats.split("## Pattern 7", 1)[1].split("## Pattern 8", 1)[0]
        self.assertIn('article[data-testid="tweet"]', p7)
        self.assertIn(">> nth={loop_index,1}", p7)
        self.assertIn("Legacy XPath", p7)
        self.assertIn('[@data-testid="User-Name"]', p7)
        self.assertIn('[@data-testid="tweetText"]', p7)
        self.assertIn("does **not** fix virtualized X feeds", p7)
        self.assertIn("Write JS stays the verified Pattern 7 path", p7)
        self.assertIn("no-code fallback", p7.lower())

    def test_pattern9_tabs_and_nested_loops(self):
        docs = self._docs()
        pats = docs["pats"]
        skill = docs["skill"]
        catalog = docs["catalog"]
        self.assertIn("## Pattern 9", pats)
        p9 = pats.split("## Pattern 9", 1)[1].split("## Pattern 10", 1)[0]
        self.assertIn("Tab URL matching", p9)
        self.assertIn("/windows/new", p9)
        self.assertIn("https://the-internet.herokuapp.com/windows", p9)
        self.assertIn("https://books.toscrape.com/", p9)
        self.assertIn("ol.row > li:nth-child({loop_index}) h3 a", p9)
        self.assertIn("li.next > a", p9)
        self.assertIn("TAB TEST: opened, switched, closed", p9)
        self.assertIn("NESTED LOOP TEST: 2 pages x 3 books", p9)
        self.assertIn("over-match", p9.lower())
        self.assertIn("Bring Pages to Front", p9)
        self.assertIn("run setting", p9.lower())
        self.assertIn("Pattern 9", skill)
        self.assertIn("Tab URL matching", skill)
        self.assertIn("/windows/new", skill)
        self.assertIn("Tab URL matching", catalog)
        self.assertIn("/windows", catalog)
        self.assertIn("/windows/new", catalog)

    def test_iframe_selector_and_main_frame_alias(self):
        docs = self._docs()
        for key in ("skill", "pats", "catalog"):
            blob = docs[key]
            self.assertIn("#mce_0_ifr", blob)
            self.assertIn("Main frame", blob)
            self.assertIn("Main page", blob)

    def test_upload_file_column_via_url_and_keyboard_tab_twice(self):
        catalog = self._docs()["catalog"]
        self.assertIn("file column/variable", catalog.lower())
        self.assertIn("From file URL", catalog)
        self.assertIn("two separate Keyboard blocks", catalog)
        skill = self._docs()["skill"]
        self.assertIn("file column/variable", skill.lower())




class TestClientPatterns10And11(unittest.TestCase):
    """Client-bot Patterns 10/11/12: scheduler, webhook queue, branched form."""

    FORBIDDEN = ("56878", "55290", "21214", "aitablekey")

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
            "run": (refs / "run-and-platform.md").read_text(encoding="utf-8"),
        }

    def test_version_is_1_3_17(self):
        skill = self._docs()["skill"]
        self.assertIn("version: 1.3.17", skill)
        self.assertNotIn("version: 1.3.16", skill)

    def test_pattern10_scheduled_dynamic_scrape(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 10", pats)
        p10 = pats.split("## Pattern 10", 1)[1].split("## Pattern 11", 1)[0]
        self.assertIn("Dynamic", p10)
        self.assertIn("Contains keywords", p10)
        self.assertIn("Send Notification", p10)
        self.assertIn("no To:", p10)
        self.assertIn("{id, name}", p10)
        self.assertIn("CurrentDate", p10)
        self.assertIn("Break Repeat", p10)
        self.assertIn("Every day", p10)
        self.assertIn("Delay hour-based start", p10)
        self.assertIn("Timezone", p10)
        self.assertIn("no catch-up", p10.lower())
        self.assertIn("deactive", p10)
        self.assertIn("My references", p10)
        self.assertIn("Pattern 10", docs["skill"])
        self.assertIn("Newest rows first", docs["catalog"])

    def test_pattern11_webhook_http_rejoin(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 11", pats)
        p11 = pats.split("## Pattern 11", 1)[1].split("## Pattern 12", 1)[0]
        self.assertIn("webhook.zerowork.io/trigger", p11)
        self.assertIn("Bearer {id, name}", p11)
        self.assertIn("Nested record path", p11)
        self.assertIn("rejoin", p11.lower())
        self.assertIn("PRO", p11)
        self.assertIn("VERY SLOW", p11)
        self.assertIn("Insert instantly", p11)
        self.assertIn("inactive", p11.lower())
        self.assertIn("webhook.zerowork.io/trigger", docs["skill"])
        self.assertIn("webhook.zerowork.io/trigger", docs["run"])
        self.assertIn("Nested record path", docs["catalog"])
        self.assertIn("Pattern 11", docs["skill"])

    def test_pattern12_branched_form_short(self):
        pats = self._docs()["pats"]
        self.assertIn("## Pattern 12", pats)
        p12 = pats.split("## Pattern 12", 1)[1].split("## Pattern 13", 1)[0]
        self.assertIn("AM / PM", p12)
        self.assertIn("toLocaleString", p12)
        self.assertIn("Apply Regex", p12)
        self.assertIn("146-node", p12)
        self.assertIn("deactive", p12)
        self.assertIn("webhook.zerowork.io/trigger", p12)
        self.assertIn("Pattern 12", self._docs()["skill"])

    def test_webhook_dynamic_deactive_nested_path(self):
        docs = self._docs()
        blobs = "\n".join(docs.values())
        self.assertIn("webhook.zerowork.io/trigger", blobs)
        self.assertIn("Dynamic", docs["pats"])
        self.assertIn("deactive", docs["pats"])
        self.assertIn("deactive", docs["catalog"])
        self.assertIn("deactivated", docs["pats"].lower())
        self.assertIn("Nested record path", docs["pats"])
        self.assertIn("Nested record path", docs["catalog"])
        self.assertIn("canvas", docs["catalog"].lower())
        self.assertIn("lies", docs["catalog"])

    def test_no_live_client_ids_or_aitablekey(self):
        docs = self._docs()
        for name, blob in docs.items():
            for token in self.FORBIDDEN:
                self.assertNotIn(
                    token,
                    blob,
                    "%s must not contain live id/token %s" % (name, token),
                )
            self.assertNotRegex(blob, r"\{id:\s*\d{5,}")






class TestClientPatterns13To16(unittest.TestCase):
    """Client-bot Patterns 13-16: outreach DM, enrich, FB scrape/reply, IG vision."""

    FORBIDDEN = (
        "61072",
        "60018",
        "49000",
        "56935",
        "51184",
        "n8n.gohighroad",
        "leancodeautomation",
    )

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
            "prim": (refs / "platform-primitives.md").read_text(encoding="utf-8"),
            "wjs": (refs / "write-javascript.md").read_text(encoding="utf-8"),
        }

    def test_version_is_1_3_17(self):
        skill = self._docs()["skill"]
        self.assertIn("version: 1.3.17", skill)
        self.assertNotIn("version: 1.3.16", skill)

    def test_pattern13_linkedin_outreach_dm(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 13", pats)
        p13 = pats.split("## Pattern 13", 1)[1].split("## Pattern 14", 1)[0]
        self.assertIn("Delete current row in a loop", p13)
        self.assertIn("ELSE", p13)
        self.assertIn("if no other condition is met", p13)
        self.assertIn("Save error message to", p13)
        self.assertIn("My references", p13)
        self.assertIn("{id, name", p13)
        self.assertIn("No LinkedIn API", p13)
        self.assertIn("main button[aria-label*=\"Message\"]", p13)
        self.assertIn("Use spintax", p13)
        self.assertIn("Pattern 13", docs["skill"])
        self.assertIn("Delete current row in a loop", docs["catalog"])
        self.assertIn("if no other condition is met", docs["catalog"])
        self.assertIn("Save error message to", docs["catalog"])

    def test_pattern14_dynamic_enrich(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 14", pats)
        p14 = pats.split("## Pattern 14", 1)[1].split("## Pattern 15", 1)[0]
        self.assertIn("RUN LIST", p14)
        self.assertIn("Keyboard Space", p14)
        self.assertIn("50000", p14)
        self.assertIn("deactivated", p14.lower())
        self.assertIn("My references", p14)
        self.assertIn("Pattern 14", docs["skill"])
        self.assertIn("production hygiene", docs["catalog"])

    def test_pattern15_facebook_scrape_reply(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 15", pats)
        p15 = pats.split("## Pattern 15", 1)[1].split("## Pattern 16", 1)[0]
        self.assertIn("isActive", p15)
        self.assertIn("appendIndex", p15)
        self.assertIn("Keyboard Enter", p15)
        self.assertIn("remove_duplicate_rows", p15)
        self.assertIn("Sheets-backed", p15)
        self.assertIn("My references", p15)
        self.assertIn("Pattern 15", docs["skill"])
        self.assertIn("appendIndex", docs["wjs"])
        self.assertIn("Keyboard Enter", docs["catalog"])
        self.assertIn("without a Sheets", docs["prim"])

    def test_pattern16_instagram_vision(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 16", pats)
        p16 = pats.split("## Pattern 16", 1)[1].split("## Pattern 17", 1)[0]
        self.assertIn("Count elements matching selector", p16)
        self.assertIn("Lead selector", p16)
        self.assertIn("Custom attribute", p16)
        self.assertIn("src", p16)
        self.assertIn("choices[0].message.content", p16)
        self.assertIn("JSON path can become the variable name", p16)
        self.assertIn("deactivated", p16.lower())
        self.assertIn("My references", p16)
        self.assertIn("Pattern 16", docs["skill"])
        self.assertIn("Count elements matching selector", docs["catalog"])
        self.assertIn("Custom attribute", docs["catalog"])
        self.assertIn("`src`", docs["catalog"])

    def test_catalog_platform_facts(self):
        docs = self._docs()
        blobs = "\n".join(docs.values())
        self.assertIn("ELSE", blobs)
        self.assertIn("if no other condition is met", blobs)
        self.assertIn("Delete current row in a loop", blobs)
        self.assertIn("appendIndex", blobs)
        self.assertIn("Count elements matching selector", blobs)
        self.assertIn("Custom attribute", blobs)
        self.assertIn("Keyboard Enter", blobs)
        self.assertIn("isActive", blobs)
        self.assertIn("JSON path can become the variable name", blobs)
        self.assertIn("production hygiene", blobs)
        self.assertIn("Sheets-backed table can exist without a Sheets", blobs)

    def test_no_live_client_ids_or_vendor_tokens(self):
        docs = self._docs()
        for name, blob in docs.items():
            for token in self.FORBIDDEN:
                self.assertNotIn(
                    token,
                    blob,
                    "%s must not contain live id/token %s" % (name, token),
                )
            self.assertNotRegex(blob, r"\{id:\s*\d{5,}")



class TestClientPatterns17To19(unittest.TestCase):
    """Client-bot Patterns 17-19: two-phase enrich, Sheets property, HTTP status."""

    FORBIDDEN = (
        "58586",
        "58439",
        "59008",
        "57800",
        "57424",
        "31875",
        "114268",
        "113956",
        "115164",
        "115157",
        "112723",
        "112719",
        "112710",
        "112105",
        "57446",
        "docs.google.com/spreadsheet",
        "docs.google.com/spread",
        "activepieces",
        "appsumo.com/products/",
    )

    def _docs(self):
        refs = SKILL_ROOT / "references"
        return {
            "skill": (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8"),
            "pats": (refs / "build-patterns.md").read_text(encoding="utf-8"),
            "catalog": (refs / "block-catalog.md").read_text(encoding="utf-8"),
            "prim": (refs / "platform-primitives.md").read_text(encoding="utf-8"),
            "wjs": (refs / "write-javascript.md").read_text(encoding="utf-8"),
        }

    def test_version_is_1_3_17(self):
        skill = self._docs()["skill"]
        self.assertIn("version: 1.3.17", skill)
        self.assertNotIn("version: 1.3.16", skill)

    def test_pattern17_two_phase_no_run_taskbot(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 17", pats)
        p17 = pats.split("## Pattern 17", 1)[1].split("## Pattern 18", 1)[0]
        self.assertIn("Delete all rows", p17)
        self.assertIn("Count elements matching selector", p17)
        self.assertIn("a[href*=products]", p17)
        self.assertIn(">> nth={loop_index,0}", p17)
        self.assertIn("After Repeat", p17)
        self.assertIn("Dynamic", p17)
        self.assertIn("My references", p17)
        self.assertIn("{id, name", p17)
        self.assertIn("no To:", p17)
        self.assertIn("run finished", p17)
        self.assertIn("Truncate-then-refill", p17)
        self.assertIn("Delete current row in a loop", p17)
        self.assertIn("insert_date", p17)
        self.assertIn("Date Added", p17)
        self.assertIn("dead-end", p17.lower())
        self.assertIn("input[placeholder=Email]", p17)
        self.assertIn("tableRefId", p17)
        self.assertIn("test URL", p17)
        self.assertIn("Honest hole", p17)
        self.assertIn("run_taskbot", p17)
        self.assertIn("absent from", p17.lower())
        self.assertIn("Pattern 17", docs["skill"])
        self.assertIn(">> nth={loop_index,0}", docs["skill"])
        self.assertIn(">> nth={loop_index,0}", docs["catalog"])
        self.assertIn(">> nth={loop_index,0}", docs["prim"])

    def test_pattern18_sheets_table_property(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 18", pats)
        p18 = pats.split("## Pattern 18", 1)[1].split("## Pattern 19", 1)[0]
        self.assertIn("table property", p18)
        self.assertIn("Sheets icon", p18)
        self.assertIn("Edit Google Sheets link", p18)
        self.assertIn("Remove from this TaskBot", p18)
        self.assertIn("About this table", p18)
        self.assertIn("Selected sheet", p18)
        self.assertIn("Used in TaskBots", p18)
        self.assertIn("Delete Spreadsheet Data", p18)
        self.assertIn("mix", p18.lower())
        self.assertIn("My references", p18)
        self.assertIn("{id, name: CurrentSubSectionID} + ul + p a", p18)
        self.assertIn("/#(.*)/", p18)
        self.assertIn("Save to: Variables", p18)
        self.assertIn("cross-table cell copier", p18)
        self.assertIn("Tab number", p18)
        self.assertIn("Pattern 18", docs["skill"])
        self.assertIn("green Sheets icon", docs["skill"])
        self.assertIn("green Sheets icon", docs["prim"])
        self.assertIn("table property", docs["prim"])
        self.assertIn("Edit Google Sheets link", docs["prim"])
        self.assertIn("Variable interpolated inside a CSS selector", docs["prim"])
        self.assertIn("cross-table cell copier", docs["catalog"])
        self.assertIn("Save to: Variables", docs["catalog"])

    def test_pattern19_http_status_only(self):
        docs = self._docs()
        pats = docs["pats"]
        self.assertIn("## Pattern 19", pats)
        p19 = pats.split("## Pattern 19", 1)[1].split("## Node Playground", 1)[0]
        self.assertIn("Save response status code", p19)
        self.assertIn("three independent slots", p19)
        self.assertIn("200", p19)
        self.assertIn("intentional", p19.lower())
        self.assertIn("My references", p19)
        self.assertIn("{id, name: URL}", p19)
        self.assertIn("outbound webhook", p19.lower())
        self.assertIn("{id, name: transcript}", p19)
        self.assertIn("{id, name: videoId}", p19)
        self.assertIn("Perform right-click", p19)
        self.assertIn("Use human-like clicking", p19)
        self.assertIn("Pattern 19", docs["skill"])
        self.assertIn("Save response status code", docs["skill"])
        self.assertIn("three independent slots", docs["skill"])
        self.assertIn("Save response status code", docs["catalog"])
        self.assertIn("three independent slots", docs["catalog"])
        self.assertIn("Perform right-click", docs["catalog"])
        self.assertIn("Use human-like clicking", docs["catalog"])
        self.assertIn("tableRefId", docs["wjs"])
        self.assertIn("test URL", docs["wjs"])
        self.assertIn("My references", docs["wjs"])

    def test_nth_loop_index_zero_and_status_code(self):
        docs = self._docs()
        blobs = "\n".join(docs.values())
        self.assertIn(">> nth={loop_index,0}", blobs)
        self.assertIn("Save response status code", blobs)
        self.assertIn("green Sheets icon", blobs)
        self.assertIn("table property", blobs)
        self.assertIn("Perform right-click", blobs)
        self.assertIn("Use human-like clicking", blobs)
        self.assertIn("absent from", blobs.lower())
        self.assertIn("this client", blobs.lower())

    def test_no_live_ids_sheets_urls_or_activepieces(self):
        docs = self._docs()
        for name, blob in docs.items():
            for token in self.FORBIDDEN:
                self.assertNotIn(
                    token,
                    blob,
                    "%s must not contain live id/url/token %s" % (name, token),
                )
            self.assertNotRegex(blob, r"\{id:\s*\d{5,}")


if __name__ == "__main__":
    unittest.main()
