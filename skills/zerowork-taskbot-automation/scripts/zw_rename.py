#!/usr/bin/env python3
"""Rename canvas nodes: dblclick title, Ctrl+A, type, Enter.

Replacement for session scratch `zw_rename_now.py`. Pass pairs on the
command line. Pid / window from ZW_CUA_PID + ZW_CUA_WINDOW_ID.

    python zw_rename.py --map "Open Link=Open X home" "Delay=Wait for timeline"
    python zw_rename.py --old "Write JavaScript" --new "Harvest visible tweets"

Proof the rename landed is GET /connector/<id>/get_workflow/ data.name,
not the UIA label (wrapped titles often do not exact-match).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from zw_canvas import Canvas, CuaTargetError, target_from_env  # noqa: E402


def parse_map(items: list[str]) -> list[tuple[str, str]]:
    out = []
    for item in items:
        if "=" not in item:
            raise ValueError("map entry must be old=new, got %r" % item)
        old, new = item.split("=", 1)
        old, new = old.strip(), new.strip()
        if not old or not new:
            raise ValueError("empty old or new in %r" % item)
        out.append((old, new))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Rename ZeroWork canvas nodes via cua-driver.")
    parser.add_argument("--pid", type=int, default=None)
    parser.add_argument("--window-id", type=int, default=None)
    parser.add_argument("--session", default=None)
    parser.add_argument("--old")
    parser.add_argument("--new")
    parser.add_argument(
        "--map",
        nargs="*",
        default=[],
        help='pairs as old=new (quote if the old title has spaces)',
    )
    args = parser.parse_args(argv)

    pairs: list[tuple[str, str]] = []
    if args.old and args.new:
        pairs.append((args.old, args.new))
    if args.map:
        pairs.extend(parse_map(args.map))
    if not pairs:
        parser.error("pass --old/--new or --map old=new")

    canvas = Canvas(target_from_env(args.pid, args.window_id, args.session))
    canvas.press("escape", foreground=True)
    failed = 0
    for old, new in pairs:
        result = canvas.rename(old, new)
        print(result)
        if not (result.startswith("ok:") or result.startswith("already:")):
            failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CuaTargetError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
