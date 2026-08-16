"""cua-driver helpers for the paired ZeroWork creator Chrome.

Use when you do not have page JS / CDP on the creator tab. Full loop:
references/creator-editor-automation.md.

Windows PowerShell — pipe JSON on stdin (argv quoting will mangle it):

    '{"pid":<pid>,"window_id":<hwnd>}' | & cua-driver call get_window_state

Never put access/refresh JWTs, cookies, or account ids in this file.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def zw_cua_parse_tree(path: str | Path) -> list[dict[str, Any]]:
    """Load a cua-driver get_window_state JSON (or a dump that contains one)."""
    raw = Path(path).read_text(encoding="utf-8")
    try:
        obj = json.loads(raw)
        if isinstance(obj, dict) and "elements" in obj:
            return list(obj["elements"])
    except json.JSONDecodeError:
        pass
    dec = json.JSONDecoder()
    idx = 0
    while True:
        j = raw.find("{", idx)
        if j < 0:
            break
        try:
            obj, end = dec.raw_decode(raw, j)
        except json.JSONDecodeError:
            idx = j + 1
            continue
        if isinstance(obj, dict) and "elements" in obj:
            return list(obj["elements"])
        idx = j + end
    raise ValueError("no elements array in %s" % path)


def zw_cua_find_card_group(
    elements: list[dict[str, Any]], label: str, min_size: int = 100
) -> dict[str, Any] | None:
    """Return the ~114px Group that parents a node-label Text.

    Click this element's element_index (not the Text). Search-by-ID only
    selects. Background PostMessage on Chromium is often a no-op — after a
    verified miss, retry delivery_mode=foreground.
    """
    want = label.strip().lower()
    by_index = {int(e["element_index"]): e for e in elements if "element_index" in e}
    for e in elements:
        lab = (e.get("label") or "").strip()
        if lab.lower() != want:
            continue
        if str(e.get("role") or "") not in ("Text", "text"):
            continue
        frame = e.get("frame") or {}
        # Walk backward for the nearest large unlabeled Group above this text.
        i = int(e["element_index"])
        for j in range(i - 1, max(-1, i - 16), -1):
            g = by_index.get(j)
            if not g:
                continue
            if str(g.get("role") or "") not in ("Group", "group"):
                continue
            if g.get("label"):
                continue
            gf = g.get("frame") or {}
            if int(gf.get("w") or 0) >= min_size and int(gf.get("h") or 0) >= min_size:
                return g
        return e
    return None


def zw_cua_labels(elements: list[dict[str, Any]], *needles: str) -> list[dict[str, Any]]:
    """Elements whose label contains any needle (case-insensitive)."""
    keys = tuple(n.lower() for n in needles)
    out = []
    for e in elements:
        lab = (e.get("label") or "").lower()
        if any(k in lab for k in keys):
            out.append(e)
    return out
