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



if __name__ == "__main__":
    unittest.main()
