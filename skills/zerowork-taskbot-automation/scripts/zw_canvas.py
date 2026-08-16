#!/usr/bin/env python3
"""Paired-Chrome cua-driver session for the ZeroWork creator.

Replacement for session scratch `zw_canvas.py`. Pid / window_id come from
the environment or CLI — never hard-code a Chrome hwnd. Same Chrome pid
can own several windows; an NTP overlay swallows SendInput until
`bring_to_front` on the TaskBot-titled window.

Env:
    ZW_CUA_PID          Chrome process id (required for live calls)
    ZW_CUA_WINDOW_ID    hwnd of the *editor* window (required)
    ZW_CUA_SESSION      cua-driver session name (default zw-canvas)
    ZW_CUA_SNAP         optional path for the last get_window_state JSON

Usage:
    python zw_canvas.py snapshot
    python zw_canvas.py list-windows
    python zw_canvas.py bring-to-front
    python zw_canvas.py rename --old "Open Link" --new "Open X home"
    python zw_canvas.py fill-note --old "Write a note..." --text "Agent Chrome must be signed in."
    python zw_canvas.py fill-notes-yellow --text "note one" --text "note two"

PowerShell: pipe JSON on stdin to cua-driver (argv quoting mangles it).
See references/creator-editor-automation.md.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from zw_cua import zw_cua_find_card_group, zw_cua_parse_tree  # noqa: E402


class CuaTargetError(RuntimeError):
    """Pid / window_id missing or a cua-driver call failed."""


@dataclass
class CuaTarget:
    pid: int
    window_id: int
    session: str = "zw-canvas"
    snap_path: Path | None = None

    def base(self) -> dict[str, Any]:
        return {
            "pid": int(self.pid),
            "window_id": int(self.window_id),
            "session": self.session,
        }


def target_from_env(
    pid: int | None = None,
    window_id: int | None = None,
    session: str | None = None,
) -> CuaTarget:
    raw_pid = pid if pid is not None else os.environ.get("ZW_CUA_PID", "").strip()
    raw_wid = (
        window_id
        if window_id is not None
        else os.environ.get("ZW_CUA_WINDOW_ID", "").strip()
    )
    if raw_pid in ("", None) or raw_wid in ("", None):
        raise CuaTargetError(
            "Set ZW_CUA_PID and ZW_CUA_WINDOW_ID (cua-driver list_windows). "
            "Pick the window whose title is the TaskBot, not a bare "
            "'Google Chrome' overlay. Hwnds change every Chrome restart."
        )
    snap = os.environ.get("ZW_CUA_SNAP", "").strip()
    return CuaTarget(
        pid=int(raw_pid),
        window_id=int(raw_wid),
        session=session
        or os.environ.get("ZW_CUA_SESSION", "").strip()
        or "zw-canvas",
        snap_path=Path(snap) if snap else None,
    )


def cua_call(tool: str, payload: dict[str, Any]) -> dict[str, Any] | str:
    """Invoke `cua-driver call <tool>` with JSON on stdin (PowerShell-safe)."""
    raw = json.dumps(payload)
    proc = subprocess.run(
        ["cua-driver", "call", tool],
        input=raw.encode("utf-8"),
        capture_output=True,
    )
    out = (proc.stdout or b"").decode("utf-8", "replace")
    err = (proc.stderr or b"").decode("utf-8", "replace")
    if proc.returncode != 0:
        return {"_error": True, "stdout": out[-2000:], "stderr": err[-2000:]}
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return out


def is_background_miss(res: dict[str, Any] | str) -> bool:
    blob = json.dumps(res) if isinstance(res, dict) else str(res)
    if isinstance(res, dict) and res.get("_error"):
        return True
    return "background_unavailable" in blob


def bg_then_fg(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    kwargs = dict(kwargs)
    kwargs["foreground"] = False
    res = fn(*args, **kwargs)
    if is_background_miss(res):
        kwargs["foreground"] = True
        return fn(*args, **kwargs)
    return res


class Canvas:
    def __init__(self, target: CuaTarget):
        self.target = target

    def call(self, tool: str, extra: dict[str, Any] | None = None) -> dict[str, Any] | str:
        payload = {**self.target.base(), **(extra or {})}
        return cua_call(tool, payload)

    def bring_to_front(self) -> dict[str, Any] | str:
        return self.call("bring_to_front")

    def list_windows(self, pid: int | None = None) -> dict[str, Any] | str:
        payload: dict[str, Any] = {}
        use_pid = self.target.pid if pid is None else pid
        if use_pid:
            payload["pid"] = int(use_pid)
        return cua_call("list_windows", payload)

    def snapshot(
        self, shot: str | Path | None = None, mode: str = "ax"
    ) -> list[dict[str, Any]]:
        payload: dict[str, Any] = {**self.target.base(), "capture_mode": mode}
        if shot:
            payload["screenshot_out_file"] = str(shot)
            payload["capture_mode"] = "som"
        res = cua_call("get_window_state", payload)
        els = self._elements_from(res)
        labs = {(e.get("label") or "") for e in els}
        if len(els) < 120 or "Deactivate" in labs:
            self.press("escape", foreground=True)
            time.sleep(0.25)
            res2 = cua_call("get_window_state", payload)
            els = self._elements_from(res2)
        return els

    def _elements_from(self, res: dict[str, Any] | str) -> list[dict[str, Any]]:
        snap = self.target.snap_path
        if isinstance(res, dict) and res.get("elements"):
            if snap:
                snap.write_text(json.dumps(res), encoding="utf-8")
            return list(res["elements"])
        if snap:
            snap.write_text(
                json.dumps(res) if isinstance(res, dict) else str(res),
                encoding="utf-8",
            )
            try:
                return zw_cua_parse_tree(snap)
            except Exception:
                return []
        if isinstance(res, dict) and isinstance(res.get("elements"), list):
            return list(res["elements"])
        return []

    def click_idx(self, idx: int, foreground: bool = False) -> dict[str, Any] | str:
        extra: dict[str, Any] = {"element_index": int(idx)}
        if foreground:
            extra["delivery_mode"] = "foreground"
        return self.call("click", extra)

    def dblclick_idx(self, idx: int, foreground: bool = False) -> dict[str, Any] | str:
        extra: dict[str, Any] = {"element_index": int(idx)}
        if foreground:
            extra["delivery_mode"] = "foreground"
        return self.call("double_click", extra)

    def click_xy(
        self, x: int, y: int, foreground: bool = False, double: bool = False
    ) -> dict[str, Any] | str:
        extra: dict[str, Any] = {"x": int(x), "y": int(y)}
        if foreground:
            extra["delivery_mode"] = "foreground"
        return self.call("double_click" if double else "click", extra)

    def hotkey(self, keys: list[str], foreground: bool = False) -> dict[str, Any] | str:
        extra: dict[str, Any] = {"keys": keys}
        if foreground:
            extra["delivery_mode"] = "foreground"
        return self.call("hotkey", extra)

    def press(
        self,
        key: str,
        foreground: bool = False,
        element_index: int | None = None,
    ) -> dict[str, Any] | str:
        extra: dict[str, Any] = {"key": key}
        if foreground:
            extra["delivery_mode"] = "foreground"
        if element_index is not None:
            extra["element_index"] = int(element_index)
        return self.call("press_key", extra)

    def type_text(
        self,
        text: str,
        foreground: bool = False,
        delay_ms: int = 0,
        element_index: int | None = None,
        x: int | None = None,
        y: int | None = None,
    ) -> dict[str, Any] | str:
        extra: dict[str, Any] = {"text": text, "delay_ms": delay_ms}
        if foreground:
            extra["delivery_mode"] = "foreground"
        if element_index is not None:
            extra["element_index"] = int(element_index)
        if x is not None:
            extra["x"] = int(x)
        if y is not None:
            extra["y"] = int(y)
        return self.call("type_text", extra)

    def find_text(
        self, els: list[dict[str, Any]], exact: str, max_x: int = 1280
    ) -> dict[str, Any] | None:
        want = exact.strip()
        for el in els:
            if str(el.get("role") or "") not in ("Text", "text"):
                continue
            if (el.get("label") or "").strip() != want:
                continue
            frame = el.get("frame") or {}
            if int(frame.get("x") or 0) > max_x:
                continue
            return el
        return None

    def labels(
        self, els: list[dict[str, Any]], *needles: str, max_x: int = 1280
    ) -> list[dict[str, Any]]:
        keys = tuple(n.lower() for n in needles)
        out = []
        for el in els:
            lab = (el.get("label") or "").strip()
            if not lab:
                continue
            frame = el.get("frame") or {}
            if int(frame.get("x") or 0) > max_x:
                continue
            low = lab.lower()
            if any(k in low for k in keys):
                out.append(el)
        return out

    def card_group(self, els: list[dict[str, Any]], label: str) -> dict[str, Any] | None:
        return zw_cua_find_card_group(els, label)

    def rename(self, old: str, new: str) -> str:
        """Dblclick title Text, Ctrl+A, type, Enter. Proof is get_workflow data.name."""
        els = self.snapshot()
        hit = self.find_text(els, old)
        if not hit:
            if self.find_text(els, new):
                return "already:%s" % new
            return "miss:%s" % old
        idx = int(hit["element_index"])
        bg_then_fg(self.dblclick_idx, idx)
        time.sleep(0.4)
        bg_then_fg(self.hotkey, ["ctrl", "a"])
        time.sleep(0.15)
        self.type_text(new, foreground=True, delay_ms=8)
        time.sleep(0.12)
        self.press("return", foreground=True)
        time.sleep(0.3)
        els2 = self.snapshot()
        if self.find_text(els2, new) and not self.find_text(els2, old):
            return "ok:%s" % new
        leftover = None
        for el in els2:
            lab = (el.get("label") or "").strip()
            if new in lab or old in lab:
                leftover = lab
                break
        return "fail:%s" % leftover

    def fill_note(self, old: str, text: str) -> str:
        """Click existing note text (or 'Write a note...'), Ctrl+A, type, Escape."""
        els = self.snapshot()
        hit = self.find_text(els, old)
        if not hit:
            preview = text[:24]
            for el in els:
                lab = (el.get("label") or "").strip()
                if lab.startswith(preview[:16]):
                    return "already"
            return "miss-note"
        idx = int(hit["element_index"])
        res = self.click_idx(idx, foreground=False)
        if is_background_miss(res):
            self.click_idx(idx, foreground=True)
        time.sleep(0.3)
        self.snapshot()
        hk = self.hotkey(["ctrl", "a"], foreground=False)
        if is_background_miss(hk):
            self.hotkey(["ctrl", "a"], foreground=True)
        self.type_text(text, foreground=True, delay_ms=6)
        time.sleep(0.15)
        self.press("escape", foreground=True)
        time.sleep(0.2)
        els2 = self.snapshot()
        preview = text[:20]
        for el in els2:
            lab = (el.get("label") or "").strip()
            if lab.startswith(preview[:16]) or preview[:16] in lab:
                return "ok"
        return "fail-note"

    def fill_notes_yellow(
        self, texts: list[str], shot: str | Path
    ) -> list[str]:
        """Double-click yellow sticky centroids in a screenshot, then type."""
        cents = yellow_centroids(shot)
        results = []
        for (x, y), text in zip(cents, texts):
            self.click_xy(x, y, foreground=True, double=True)
            time.sleep(0.35)
            extra: dict[str, Any] = {
                "x": x,
                "y": y + 8,
                "text": text,
                "delay_ms": 8,
                "delivery_mode": "foreground",
            }
            self.call("type_text", extra)
            time.sleep(0.2)
            self.press("escape", foreground=True)
            time.sleep(0.25)
            results.append("typed@%d,%d" % (x, y))
        if len(cents) < len(texts):
            results.append("short-yellow:%d<%d" % (len(cents), len(texts)))
        return results


def is_sticky_yellow(r: int, g: int, b: int) -> bool:
    return r > 210 and g > 200 and b < 185 and r > b + 35 and g > b + 25


def cluster_xy(
    points: list[tuple[int, int]], n_bands: int = 3
) -> list[tuple[int, int]]:
    """Split yellow hits into left-to-right bands; return each band's centroid."""
    if not points:
        return []
    xs = [p[0] for p in points]
    xmin, xmax = min(xs), max(xs)
    span = max(xmax - xmin, 1)
    bands: list[list[tuple[int, int]]] = [[] for _ in range(n_bands)]
    for point in points:
        idx = min(n_bands - 1, int((point[0] - xmin) * n_bands / span))
        bands[idx].append(point)
    out: list[tuple[int, int]] = []
    for band in bands:
        if not band:
            continue
        out.append(
            (
                sum(p[0] for p in band) // len(band),
                sum(p[1] for p in band) // len(band),
            )
        )
    out.sort(key=lambda p: p[0])
    return out


def yellow_hits_from_png(
    path: str | Path,
    y0_frac: float = 0.08,
    y1_frac: float = 0.35,
    x0_frac: float = 0.15,
    x1_frac: float = 0.85,
) -> list[tuple[int, int]]:
    """Scan a screenshot for sticky-note yellow. Pillow if present, else stdlib PNG."""
    path = Path(path)
    try:
        from PIL import Image  # type: ignore

        img = Image.open(path).convert("RGB")
        width, height = img.size
        px = img.load()
        hits = []
        for y in range(int(height * y0_frac), int(height * y1_frac)):
            for x in range(int(width * x0_frac), int(width * x1_frac)):
                r, g, b = px[x, y]
                if is_sticky_yellow(r, g, b):
                    hits.append((x, y))
        return hits
    except ImportError:
        return _yellow_hits_stdlib_png(path, y0_frac, y1_frac, x0_frac, x1_frac)


def _yellow_hits_stdlib_png(
    path: Path,
    y0_frac: float,
    y1_frac: float,
    x0_frac: float,
    x1_frac: float,
) -> list[tuple[int, int]]:
    width, height, pixels = _decode_png_rgb(path)
    hits = []
    for y in range(int(height * y0_frac), int(height * y1_frac)):
        row = pixels[y]
        for x in range(int(width * x0_frac), int(width * x1_frac)):
            r, g, b = row[x]
            if is_sticky_yellow(r, g, b):
                hits.append((x, y))
    return hits


def _decode_png_rgb(path: Path) -> tuple[int, int, list[list[tuple[int, int, int]]]]:
    """Minimal 8-bit RGB/RGBA PNG reader (creator screenshots)."""
    import struct
    import zlib

    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: %s" % path)
    pos = 8
    width = height = None
    bit_depth = color_type = None
    idat = bytearray()
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        ctype = data[pos + 4 : pos + 8]
        chunk = data[pos + 8 : pos + 8 + length]
        pos += 12 + length
        if ctype == b"IHDR":
            width, height, bit_depth, color_type = struct.unpack(">IIBB", chunk[:10])
        elif ctype == b"IDAT":
            idat.extend(chunk)
        elif ctype == b"IEND":
            break
    if width is None or height is None or bit_depth != 8 or color_type not in (2, 6):
        raise ValueError("need 8-bit RGB/RGBA PNG")
    raw = zlib.decompress(bytes(idat))
    bpp = 3 if color_type == 2 else 4
    stride = width * bpp
    rows: list[list[tuple[int, int, int]]] = []
    i = 0
    prev = bytearray(stride)
    for _y in range(height):
        filt = raw[i]
        i += 1
        scan = bytearray(raw[i : i + stride])
        i += stride
        if filt == 1:
            for x in range(stride):
                left = scan[x - bpp] if x >= bpp else 0
                scan[x] = (scan[x] + left) & 255
        elif filt == 2:
            for x in range(stride):
                scan[x] = (scan[x] + prev[x]) & 255
        elif filt == 3:
            for x in range(stride):
                left = scan[x - bpp] if x >= bpp else 0
                up = prev[x]
                scan[x] = (scan[x] + ((left + up) // 2)) & 255
        elif filt == 4:
            for x in range(stride):
                a = scan[x - bpp] if x >= bpp else 0
                b = prev[x]
                c = prev[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                scan[x] = (scan[x] + pr) & 255
        elif filt != 0:
            raise ValueError("unsupported PNG filter %s" % filt)
        prev = scan
        row = []
        for x in range(width):
            o = x * bpp
            row.append((scan[o], scan[o + 1], scan[o + 2]))
        rows.append(row)
    return width, height, rows


def yellow_centroids(path: str | Path, n_bands: int = 3) -> list[tuple[int, int]]:
    return cluster_xy(yellow_hits_from_png(path), n_bands=n_bands)


def js_lines_for_type_text(source: str) -> list[str]:
    """Split JS so cua type_text can send one line at a time (LF is dropped)."""
    text = source.replace("\r\n", "\n").replace("\r", "\n")
    return text.split("\n")


def js_crlf(source: str) -> str:
    """CRLF newlines — the only line break SendInput reliably inserts in Monaco."""
    return source.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")


def _canvas_from_args(args: argparse.Namespace) -> Canvas:
    return Canvas(
        target_from_env(
            pid=args.pid,
            window_id=args.window_id,
            session=args.session,
        )
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paired-Chrome cua session (pid/window from env or flags)."
    )
    parser.add_argument("--pid", type=int, default=None)
    parser.add_argument("--window-id", type=int, default=None)
    parser.add_argument("--session", default=None)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("snapshot", help="get_window_state; print label count")
    sub.add_parser("list-windows", help="list_windows for this pid")
    sub.add_parser("bring-to-front", help="foreground the editor window")
    rn = sub.add_parser("rename", help="dblclick title, Ctrl+A, type, Enter")
    rn.add_argument("--old", required=True)
    rn.add_argument("--new", required=True)
    note = sub.add_parser("fill-note", help="type into a sticky by current label")
    note.add_argument("--old", default="Write a note...")
    note.add_argument("--text", required=True)
    ynote = sub.add_parser(
        "fill-notes-yellow", help="double-click yellow centroids then type"
    )
    ynote.add_argument("--shot", required=True, help="PNG screenshot of the canvas")
    ynote.add_argument("--text", action="append", required=True)
    args = parser.parse_args(argv)

    canvas = _canvas_from_args(args)
    if args.cmd == "snapshot":
        els = canvas.snapshot()
        print("elements", len(els))
        return 0
    if args.cmd == "list-windows":
        print(json.dumps(canvas.list_windows(), indent=2, default=str))
        return 0
    if args.cmd == "bring-to-front":
        print(json.dumps(canvas.bring_to_front(), indent=2, default=str))
        return 0
    if args.cmd == "rename":
        print(canvas.rename(args.old, args.new))
        return 0
    if args.cmd == "fill-note":
        print(canvas.fill_note(args.old, args.text))
        return 0
    if args.cmd == "fill-notes-yellow":
        print(json.dumps(canvas.fill_notes_yellow(args.text, args.shot)))
        return 0
    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CuaTargetError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
