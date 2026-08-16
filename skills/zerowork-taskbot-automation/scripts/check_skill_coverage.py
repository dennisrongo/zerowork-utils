#!/usr/bin/env python3
"""Coverage check for the ZeroWork TaskBot skill.

Parses the real skill files (node-types.md + every references/*.md and SKILL.md).
Asserts every palette `type` and every official building-block URL has a
non-empty operational section: Purpose, type, config/drawer fields, wiring/
companions, when-to-use, gotchas.

Does not hard-code official-docs prose. Drive this file, not a reimplementation
of ZeroWork.

Usage:
    python check_skill_coverage.py
    python check_skill_coverage.py --write-coverage path/to/docs-coverage.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
REFS = SKILL_ROOT / "references"
NODE_TYPES = REFS / "node-types.md"

# Palette types = node-types table rows with a single `type` cell.
# Branches ride with Check Web Element; canvas-only are documented separately.
BRANCH_TYPES = ("element_present", "element_absent")
CANVAS_ONLY = ("sticky_note", "fake", "delete", "auto-align")

FIELD_PATTERNS = {
    "purpose": re.compile(r"\*\*Purpose:\*\*", re.I),
    "config": re.compile(r"\*\*Config / drawer fields:\*\*", re.I),
    "wiring": re.compile(r"\*\*Wiring / companions:\*\*", re.I),
    "when_to_use": re.compile(r"\*\*When to use vs adjacent:\*\*", re.I),
    "gotchas": re.compile(r"\*\*Gotchas:\*\*", re.I),
}


def load_skill_text() -> str:
    parts = []
    skill_md = SKILL_ROOT / "SKILL.md"
    if skill_md.exists():
        parts.append(skill_md.read_text(encoding="utf-8"))
    for p in sorted(REFS.glob("*.md")):
        parts.append(p.read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def parse_palette_types(node_types_md: str) -> list[str]:
    types: list[str] = []
    seen = set()
    for m in re.finditer(r"\|\s*`([a-zA-Z][a-zA-Z0-9_]*)`\s*\|", node_types_md):
        t = m.group(1)
        if t in seen or t in CANVAS_ONLY:
            continue
        seen.add(t)
        types.append(t)
    return types


def parse_official_block_urls(node_types_md: str) -> list[str]:
    urls = []
    seen = set()
    for m in re.finditer(
        r"https://docs\.zerowork\.io/using-zerowork/using-building-blocks/[^\s)|]+",
        node_types_md,
    ):
        url = m.group(0).rstrip(").,")
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    return urls


def heading_sections(text: str) -> list[tuple[str, str]]:
    """Return (heading, body) for ## / ### headings."""
    parts = re.split(r"(?m)^(#{2,3} .+)$", text)
    out = []
    i = 1
    while i < len(parts) - 1:
        heading = parts[i].strip()
        body = parts[i + 1]
        out.append((heading, body))
        i += 2
    return out


def section_for_type(sections: list[tuple[str, str]], type_name: str) -> tuple[str, str] | None:
    token = "`%s`" % type_name
    for heading, body in sections:
        if token in heading or ("(`%s`" % type_name) in heading:
            return heading, body
    # Branch markers live inside the Check Web Element section.
    if type_name in BRANCH_TYPES:
        for heading, body in sections:
            if "`check`" in heading and type_name in body:
                return heading, body
    return None


def section_for_url(sections: list[tuple[str, str]], url: str) -> tuple[str, str] | None:
    hits = []
    for heading, body in sections:
        if "Official building-block URL set" in heading:
            continue
        if url in body or url in heading:
            hits.append((heading, body))
    if not hits:
        return None
    # Prefer the section that already carries operational fields.
    hits.sort(key=lambda hb: sum(fields_present(hb[0] + "\n" + hb[1]).values()), reverse=True)
    return hits[0]


def fields_present(body: str) -> dict[str, bool]:
    return {name: bool(pat.search(body)) for name, pat in FIELD_PATTERNS.items()}


def evaluate() -> dict:
    node_md = NODE_TYPES.read_text(encoding="utf-8")
    skill_text = load_skill_text()
    sections = heading_sections(skill_text)
    types = parse_palette_types(node_md)
    urls = parse_official_block_urls(node_md)

    type_rows = []
    missing = []
    for t in types:
        found = section_for_type(sections, t)
        if not found:
            missing.append("type %s: no section" % t)
            type_rows.append(
                {
                    "kind": "type",
                    "key": t,
                    "section": "",
                    "fields": {n: False for n in FIELD_PATTERNS},
                }
            )
            continue
        heading, body = found
        blob = heading + "\n" + body
        fields = fields_present(blob)
        # type string must appear
        if ("`%s`" % t) not in blob and t not in blob:
            fields["type_string"] = False
        else:
            fields["type_string"] = True
        type_rows.append(
            {"kind": "type", "key": t, "section": heading.lstrip("# ").strip(), "fields": fields}
        )
        for name, ok in fields.items():
            if not ok:
                missing.append("type %s: missing %s (section %s)" % (t, name, heading))

    url_rows = []
    for url in urls:
        found = section_for_url(sections, url)
        if not found:
            missing.append("url %s: not cited in any skill section" % url)
            url_rows.append(
                {
                    "kind": "url",
                    "key": url,
                    "section": "",
                    "fields": {n: False for n in FIELD_PATTERNS},
                }
            )
            continue
        heading, body = found
        fields = fields_present(heading + "\n" + body)
        url_rows.append(
            {"kind": "url", "key": url, "section": heading.lstrip("# ").strip(), "fields": fields}
        )
        for name, ok in fields.items():
            if not ok:
                missing.append("url %s: missing %s (section %s)" % (url, name, heading))

    covered = sum(
        1
        for row in type_rows + url_rows
        if row["section"] and all(row["fields"].values())
    )
    return {
        "types": types,
        "urls": urls,
        "type_rows": type_rows,
        "url_rows": url_rows,
        "missing": missing,
        "covered": covered,
        "total": len(type_rows) + len(url_rows),
    }


def write_coverage_md(path: Path, result: dict) -> None:
    lines = [
        "# Docs / node coverage inventory",
        "",
        "Generated by `scripts/check_skill_coverage.py` from the real skill files.",
        "",
        "Each row names the skill section that must contain Purpose, `type`,",
        "config/drawer fields, wiring/companions, when-to-use, and gotchas.",
        "",
        "## Palette types",
        "",
        "| type | skill section | purpose | type string | config | wiring | when-to-use | gotchas |",
        "|---|---|---|---|---|---|---|---|",
    ]
    yn = lambda b: "yes" if b else "NO"
    for row in result["type_rows"]:
        f = row["fields"]
        lines.append(
            "| `%s` | %s | %s | %s | %s | %s | %s | %s |"
            % (
                row["key"],
                row["section"] or "_missing_",
                yn(f.get("purpose")),
                yn(f.get("type_string")),
                yn(f.get("config")),
                yn(f.get("wiring")),
                yn(f.get("when_to_use")),
                yn(f.get("gotchas")),
            )
        )
    lines += [
        "",
        "## Official building-block URLs",
        "",
        "| official URL | skill section | purpose | config | wiring | when-to-use | gotchas |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in result["url_rows"]:
        f = row["fields"]
        lines.append(
            "| %s | %s | %s | %s | %s | %s | %s |"
            % (
                row["key"],
                row["section"] or "_missing_",
                yn(f.get("purpose")),
                yn(f.get("config")),
                yn(f.get("wiring")),
                yn(f.get("when_to_use")),
                yn(f.get("gotchas")),
            )
        )
    lines += [
        "",
        "## Totals",
        "",
        "covered=%d total=%d missing=%d" % (result["covered"], result["total"], len(result["missing"])),
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-coverage", type=Path, default=None)
    args = parser.parse_args(argv)

    result = evaluate()
    if args.write_coverage:
        args.write_coverage.parent.mkdir(parents=True, exist_ok=True)
        write_coverage_md(args.write_coverage, result)

    print("types=%d official_urls=%d covered=%d total=%d" % (
        len(result["types"]),
        len(result["urls"]),
        result["covered"],
        result["total"],
    ))
    if result["missing"]:
        print("MISSING:")
        for line in result["missing"]:
            print(" -", line)
        return 1
    print("OK all operational fields present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
