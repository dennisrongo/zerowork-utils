"""Minimal contract for the zerowork-to-playwright skill."""
from __future__ import annotations

import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN = (
    "aitablekey",
    "n8n.gohighroad",
)


def _skill() -> str:
    return (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")


def _docs() -> dict[str, str]:
    docs = {"SKILL.md": _skill()}
    refs = SKILL_ROOT / "references"
    if refs.is_dir():
        for path in refs.glob("*.md"):
            docs[path.name] = path.read_text(encoding="utf-8")
    return docs


class TestSkillContract(unittest.TestCase):
    def test_skill_md_exists(self):
        self.assertTrue((SKILL_ROOT / "SKILL.md").is_file())

    def test_version_is_1_1_1(self):
        self.assertIn("version: 1.1.1", _skill())

    def test_create_new_google_sheet_not_reuse_live(self):
        text = _skill()
        self.assertIn("create a **new** Google Sheet", text)
        self.assertIn("Never open, edit, or reuse a live TaskBot's existing Google Sheet", text)

    def test_says_playwright(self):
        self.assertIn("Playwright", _skill())

    def test_says_read_only(self):
        text = _skill()
        self.assertTrue(
            "Read-only" in text or "read-only" in text,
            "SKILL.md must say read-only",
        )

    def test_dennis_does_logins(self):
        self.assertIn("Dennis does all site logins", _skill())

    def test_mentions_e2e(self):
        self.assertIn("E2E", _skill())

    def test_mentions_data_parity(self):
        text = _skill().lower()
        self.assertIn("data parity", text)
        self.assertIn("column names", text)

    def test_stale_bugs_fixed_only_in_playwright(self):
        self.assertIn("fix only in the Playwright", _skill())

    def test_forbids_live_secrets(self):
        for name, blob in _docs().items():
            lower = blob.lower()
            for token in FORBIDDEN:
                self.assertNotIn(
                    token,
                    lower,
                    "%s must not contain %s" % (name, token),
                )


if __name__ == "__main__":
    unittest.main()
