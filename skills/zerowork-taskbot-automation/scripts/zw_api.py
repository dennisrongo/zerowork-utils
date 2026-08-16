#!/usr/bin/env python3
"""ZeroWork REST client. Tokens come from the environment or files — never from source.

This is the secret-free replacement for session scratch `zw_api.py`. Do not
reconstruct JWTs, do not embed account claims, and do not write
`zw_access.txt` next to this file.

Auth (any one of):
    ZW_ACCESS              Bearer access JWT
    ZW_ACCESS_FILE         path to a one-line access JWT
    ZW_REFRESH             refresh JWT → POST /auth/token/refresh/
    ZW_REFRESH_FILE        path to a one-line refresh JWT

Optional:
    ZW_WRITE_ACCESS_FILE   if set, a successful refresh writes the new access
                           token here (never default this to the skill tree)

Usage:
    python zw_api.py list
    python zw_api.py workflow <bot_id>
    python zw_api.py tables <bot_id>
    python zw_api.py count <data_group_id>
    python zw_api.py items <data_group_id>
    python zw_api.py refresh

Never print tokens. Never commit token files.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Iterator

BASE = "https://taskbot-server.zerowork.io"
USER_AGENT = "Mozilla/5.0"

# Column names only — not account or table ids.
X_FEED_COLUMNS = [
    "post_id",
    "author",
    "handle",
    "author_url",
    "post_text",
    "posted_at",
    "post_url",
    "replies",
    "reposts",
    "likes",
    "views",
    "has_media",
    "is_repost",
]

LINKEDIN_FEED_COLUMNS = [
    "post_urn",
    "author",
    "author_headline",
    "author_url",
    "post_text",
    "posted_at",
    "post_url",
    "reactions",
    "comments",
    "reposts",
    "has_media",
    "post_type",
]


class TokenError(RuntimeError):
    """No usable access/refresh token in the environment."""


def _read_one_line(path: str) -> str:
    return Path(path).read_text(encoding="utf-8").strip()


def load_refresh() -> str:
    env = os.environ.get("ZW_REFRESH", "").strip()
    if env:
        return env
    path = os.environ.get("ZW_REFRESH_FILE", "").strip()
    if path and Path(path).is_file():
        return _read_one_line(path)
    return ""


def load_access(*, allow_refresh: bool = True) -> str:
    env = os.environ.get("ZW_ACCESS", "").strip()
    if env:
        return env
    path = os.environ.get("ZW_ACCESS_FILE", "").strip()
    if path and Path(path).is_file():
        tok = _read_one_line(path)
        if tok:
            return tok
    if allow_refresh and load_refresh():
        return refresh_access()
    raise TokenError(
        "No access token. Set ZW_ACCESS or ZW_ACCESS_FILE, or set "
        "ZW_REFRESH / ZW_REFRESH_FILE so this client can POST "
        "/auth/token/refresh/. Do not hard-code JWTs."
    )


def refresh_access() -> str:
    """Exchange a refresh JWT for a new access JWT. Does not reconstruct tokens."""
    refresh = load_refresh()
    if not refresh:
        raise TokenError(
            "No refresh token. Set ZW_REFRESH or ZW_REFRESH_FILE. "
            "Copy the live `refresh` value from creator.zerowork.io localStorage "
            "after you log in — never invent or re-sign a JWT."
        )
    status, body = request(
        "/auth/token/refresh/",
        method="POST",
        payload={"refresh": refresh},
        token=None,
    )
    if status != 200 or not isinstance(body, dict) or not body.get("access"):
        raise TokenError("refresh failed status=%s" % status)
    access = str(body["access"])
    dest = os.environ.get("ZW_WRITE_ACCESS_FILE", "").strip()
    if dest:
        Path(dest).write_text(access, encoding="utf-8")
    os.environ["ZW_ACCESS"] = access
    return access


def request(
    path: str,
    method: str = "GET",
    payload: Any = None,
    token: str | None = None,
    timeout: int = 45,
) -> tuple[int, Any]:
    """Low-level HTTP. `token=None` means no Authorization header (refresh)."""
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": USER_AGENT,
    }
    if token:
        headers["Authorization"] = "Bearer " + token
    url = path if path.startswith("http") else BASE + path
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if not raw:
                return resp.status, None
            try:
                return resp.status, json.loads(raw)
            except json.JSONDecodeError:
                return resp.status, raw.decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        try:
            parsed = json.loads(raw) if raw else None
        except Exception:
            parsed = raw[:500].decode("utf-8", "replace") if raw else None
        return exc.code, parsed


def api(
    path: str,
    method: str = "GET",
    payload: Any = None,
    token: str | None = None,
    timeout: int = 45,
) -> tuple[int, Any]:
    """Authenticated call. Retries once after refresh on 401."""
    tok = token if token is not None else load_access()
    status, body = request(path, method=method, payload=payload, token=tok, timeout=timeout)
    if status == 401 and token is None and load_refresh():
        tok = refresh_access()
        status, body = request(
            path, method=method, payload=payload, token=tok, timeout=timeout
        )
    return status, body


def edge_payload(source_id: int | str, target_id: int | str) -> dict[str, Any]:
    """Same shape as zw_helpers.zw_edge_payload — import-safe from this module."""
    scripts = Path(__file__).resolve().parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from zw_helpers import zw_edge_payload

    return zw_edge_payload(source_id, target_id)


def iter_connectors(token: str | None = None) -> Iterator[dict[str, Any]]:
    page = 1
    while page <= 50:
        status, data = api("/connector/?page=%d" % page, token=token)
        if status != 200 or not isinstance(data, dict):
            return
        for row in data.get("results") or []:
            if isinstance(row, dict):
                yield row
        if not data.get("next"):
            return
        page += 1


def find_connector(
    name: str, token: str | None = None
) -> dict[str, Any] | None:
    want = name.strip()
    for row in iter_connectors(token=token):
        if (row.get("name") or "").strip() == want:
            return row
    return None


def get_workflow(bot_id: int | str, token: str | None = None) -> tuple[int, Any]:
    return api("/connector/%s/get_workflow/" % bot_id, token=token)


def list_data_groups(bot_id: int | str, token: str | None = None) -> tuple[int, Any]:
    return api("/connector/%s/data_group/list_all/" % bot_id, token=token)


def table_count(data_group_id: int | str, token: str | None = None) -> tuple[int, Any]:
    return api("/data_group/%s/item/get_count/" % data_group_id, token=token)


def list_columns(data_group_id: int | str, token: str | None = None) -> tuple[int, Any]:
    return api("/data_group/%s/column/" % data_group_id, token=token)


def list_items(
    data_group_id: int | str, page: int = 1, token: str | None = None
) -> tuple[int, Any]:
    return api(
        "/data_group/%s/item/?page=%d&ordering=id" % (data_group_id, page),
        token=token,
    )


def create_bot(name: str, token: str | None = None) -> tuple[int, Any]:
    return api("/connector/", method="POST", payload={"name": name}, token=token)


def create_table(
    bot_id: int | str,
    name: str,
    columns: Iterable[str],
    token: str | None = None,
) -> tuple[int, Any]:
    return api(
        "/data_group/",
        method="POST",
        payload={
            "name": name,
            "type": "NATIVE",
            "columns": [{"colName": c} for c in columns],
            "connector_id": bot_id,
        },
        token=token,
    )


def post_node(
    bot_id: int | str,
    type_name: str,
    x: float,
    y: float,
    name: str = "",
    z_index: int = 1,
    token: str | None = None,
) -> tuple[int, Any]:
    return api(
        "/connector/%s/node/" % bot_id,
        method="POST",
        payload={
            "type": type_name,
            "data": {"name": name or type_name},
            "position": {"x": x, "y": y},
            "deletable": True,
            "zIndex": z_index,
        },
        token=token,
    )


def post_edge(
    bot_id: int | str,
    source_id: int | str,
    target_id: int | str,
    token: str | None = None,
) -> tuple[int, Any]:
    return api(
        "/connector/%s/edge/" % bot_id,
        method="POST",
        payload=edge_payload(source_id, target_id),
        token=token,
    )


def columns_by_id(column_payload: Any) -> dict[Any, str]:
    rows = column_payload
    if isinstance(column_payload, dict):
        rows = column_payload.get("results") or column_payload.get("data") or []
    out: dict[Any, str] = {}
    if not isinstance(rows, list):
        return out
    for col in rows:
        if not isinstance(col, dict):
            continue
        cid = col.get("id")
        name = col.get("name") or col.get("colName") or str(cid)
        if cid is not None:
            out[cid] = str(name)
    return out


def item_as_dict(item: dict[str, Any], colmap: dict[Any, str]) -> dict[str, Any]:
    """Map item `cells[].text` through column ids. There is no flat `data` dict."""
    row: dict[str, Any] = {"id": item.get("id")}
    for cell in item.get("cells") or []:
        if not isinstance(cell, dict):
            continue
        key = colmap.get(cell.get("column_id"), str(cell.get("column_id")))
        row[key] = cell.get("text")
    return row


def summarize_workflow(wf: Any) -> dict[str, Any]:
    nodes = []
    edges = []
    if isinstance(wf, dict):
        raw_nodes = wf.get("nodes") or []
        raw_edges = wf.get("edges") or []
        if isinstance(raw_nodes, dict):
            raw_nodes = list(raw_nodes.values())
        if isinstance(raw_edges, dict):
            raw_edges = list(raw_edges.values())
        if isinstance(raw_nodes, list):
            for node in raw_nodes:
                if not isinstance(node, dict):
                    continue
                data = node.get("data") or {}
                nodes.append(
                    {
                        "id": node.get("id"),
                        "type": node.get("type"),
                        "name": data.get("name") if isinstance(data, dict) else None,
                        "className": node.get("className"),
                        "position": node.get("position"),
                    }
                )
        if isinstance(raw_edges, list):
            for edge in raw_edges:
                if not isinstance(edge, dict):
                    continue
                edges.append(
                    {
                        "id": edge.get("id"),
                        "source": edge.get("source"),
                        "target": edge.get("target"),
                    }
                )
    return {"node_count": len(nodes), "edge_count": len(edges), "nodes": nodes, "edges": edges}


def normalize_data_groups(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [g for g in payload if isinstance(g, dict)]
    if isinstance(payload, dict):
        rows = payload.get("results") or payload.get("data") or []
        if isinstance(rows, list):
            return [g for g in rows if isinstance(g, dict)]
    return []


def _print_json(obj: Any) -> None:
    print(json.dumps(obj, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ZeroWork REST helper (tokens from env).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="list TaskBots (id + name only)")
    wf = sub.add_parser("workflow", help="summarize get_workflow for a bot")
    wf.add_argument("bot_id")
    tables = sub.add_parser("tables", help="list data groups on a bot")
    tables.add_argument("bot_id")
    count = sub.add_parser("count", help="item/get_count for a data group")
    count.add_argument("data_group_id")
    items = sub.add_parser("items", help="page of items as cells[].text maps")
    items.add_argument("data_group_id")
    items.add_argument("--page", type=int, default=1)
    sub.add_parser("refresh", help="exchange ZW_REFRESH for a new access token")
    args = parser.parse_args(argv)

    if args.cmd == "refresh":
        tok = refresh_access()
        print("access_len", len(tok))
        return 0

    if args.cmd == "list":
        rows = []
        for bot in iter_connectors():
            rows.append({"id": bot.get("id"), "name": bot.get("name")})
        _print_json(rows)
        return 0

    if args.cmd == "workflow":
        status, wf = get_workflow(args.bot_id)
        if status != 200:
            print("status", status)
            _print_json(wf)
            return 1
        _print_json(summarize_workflow(wf))
        return 0

    if args.cmd == "tables":
        status, groups = list_data_groups(args.bot_id)
        if status != 200:
            print("status", status)
            _print_json(groups)
            return 1
        out = []
        for group in normalize_data_groups(groups):
            out.append(
                {
                    "id": group.get("id"),
                    "name": group.get("name"),
                    "type": group.get("type"),
                    "auto": group.get("is_autogenerated"),
                }
            )
        _print_json(out)
        return 0

    if args.cmd == "count":
        status, body = table_count(args.data_group_id)
        print("status", status)
        _print_json(body)
        return 0 if status == 200 else 1

    if args.cmd == "items":
        st_cols, cols = list_columns(args.data_group_id)
        colmap = columns_by_id(cols) if st_cols == 200 else {}
        status, body = list_items(args.data_group_id, page=args.page)
        if status != 200 or not isinstance(body, dict):
            print("status", status)
            _print_json(body)
            return 1
        rows = [item_as_dict(it, colmap) for it in (body.get("results") or []) if isinstance(it, dict)]
        _print_json({"count": body.get("count"), "page": args.page, "rows": rows})
        return 0

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TokenError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
