#!/usr/bin/env python3
"""Fill sticky notes on the paired creator canvas.

Replacement for session scratch `zw_fill_notes_now.py`. REST-created notes
stay `"Write a note..."` until typed in the UI. `GET /get_workflow()`
`data.name` stays None even after the visible text lands.

    python zw_fill_notes.py --old "Write a note..." --text "Agent Chrome must be signed into X."
    python zw_fill_notes.py --yellow --shot canvas.png --text "login" --text "selectors" --text "stop"

The yellow path double-clicks sticky-note yellow pixels (not the 114px
node Group). Bring the TaskBot window to the front first
(`python zw_canvas.py bring-to-front`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from zw_canvas import Canvas, CuaTargetError, target_from_env  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Fill ZeroWork sticky notes via cua-driver.")
    parser.add_argument("--pid", type=int, default=None)
    parser.add_argument("--window-id", type=int, default=None)
    parser.add_argument("--session", default=None)
    parser.add_argument("--old", default="Write a note...")
    parser.add_argument("--text", action="append", default=[], help="repeat for several notes")
    parser.add_argument("--file", help="one note per non-empty line")
    parser.add_argument("--yellow", action="store_true")
    parser.add_argument("--shot", help="PNG used by --yellow")
    args = parser.parse_args(argv)

    texts = list(args.text)
    if args.file:
        for line in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                texts.append(line)
    if not texts:
        parser.error("pass --text and/or --file")

    canvas = Canvas(target_from_env(args.pid, args.window_id, args.session))
    if args.yellow:
        if not args.shot:
            parser.error("--yellow requires --shot PNG")
        print(json.dumps(canvas.fill_notes_yellow(texts, args.shot)))
        return 0

    failed = 0
    for text in texts:
        result = canvas.fill_note(args.old, text)
        print(result)
        if result not in ("ok", "already"):
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CuaTargetError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
