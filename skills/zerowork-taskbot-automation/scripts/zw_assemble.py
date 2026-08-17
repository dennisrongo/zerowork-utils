#!/usr/bin/env python3
"""REST-assemble a TaskBot from a JSON spec (create bot, table, nodes, edges).

Replacement for session scratch `zw_build_*.py` / `zw_rebuild_*.py`.
The spec has no account ids. Custom `data.name` is overwritten by the
default type label — rename on the canvas after assemble
(`zw_rename.py`). Drawer fields are still websocket-only. Spec keys `fill`, `text`, and
`source` are post-assemble hints — this script does not POST them.

    python zw_assemble.py templates/x_feed_nocode.json
    python zw_assemble.py templates/linkedin_feed.json --name "Demo - LinkedIn Feed"

`--reuse` finds an existing bot with that name (create-only REST — a
second assemble still POSTs every node and will duplicate the graph).
New bots always create a fresh table (tables are per-bot; do not reuse
another bot's id).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_SCRIPTS = Path(__file__).resolve().parent
_SKILL = _SCRIPTS.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from zw_api import (  # noqa: E402
    TokenError,
    create_bot,
    create_table,
    find_connector,
    get_workflow,
    list_data_groups,
    normalize_data_groups,
    post_edge,
    post_node,
)


def load_spec(path: Path) -> dict[str, Any]:
    spec = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(spec, dict):
        raise ValueError("spec must be a JSON object")
    if not spec.get("nodes"):
        raise ValueError("spec.nodes is required")
    return spec


def _existing_keys(wf: Any) -> set[str]:
    """REST cannot store our keys; we only know type+position from get_workflow."""
    keys: set[str] = set()
    if not isinstance(wf, dict):
        return keys
    nodes = wf.get("nodes") or []
    if isinstance(nodes, dict):
        nodes = list(nodes.values())
    if isinstance(nodes, list):
        for node in nodes:
            if isinstance(node, dict) and node.get("id") is not None:
                keys.add(str(node["id"]))
    return keys


def assemble(spec: dict[str, Any], name: str, reuse: bool) -> dict[str, Any]:
    bot_id = None
    if reuse:
        hit = find_connector(name)
        if hit:
            bot_id = hit.get("id")
    created_bot = False
    if bot_id is None:
        status, body = create_bot(name)
        if status != 200 or not isinstance(body, dict) or body.get("id") is None:
            raise RuntimeError("create bot failed status=%s" % status)
        bot_id = body["id"]
        created_bot = True

    table = spec.get("table") or {}
    table_id = None
    if table.get("name") and table.get("columns"):
        stg, groups = list_data_groups(bot_id)
        for group in normalize_data_groups(groups):
            if group.get("name") == table["name"]:
                table_id = group.get("id")
                break
        if table_id is None:
            st, created = create_table(bot_id, table["name"], table["columns"])
            if st != 200 or not isinstance(created, dict):
                raise RuntimeError("create table failed status=%s" % st)
            table_id = created.get("id")

    ids: dict[str, Any] = {}
    created_nodes: list[dict[str, Any]] = []
    for node in spec["nodes"]:
        key = node.get("key") or node.get("type")
        z = 1000 if node.get("type") == "sticky_note" else node.get("zIndex", 1)
        st, body = post_node(
            bot_id,
            node["type"],
            node.get("x", 0),
            node.get("y", 0),
            name=node.get("name") or key,
            z_index=z,
        )
        nid = body.get("id") if isinstance(body, dict) else None
        ids[str(key)] = nid
        created_nodes.append({"key": key, "type": node.get("type"), "status": st, "id": nid})

    created_edges = []
    for pair in spec.get("edges") or []:
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            continue
        src, tgt = ids.get(str(pair[0])), ids.get(str(pair[1]))
        if not src or not tgt:
            created_edges.append({"from": pair[0], "to": pair[1], "skipped": True})
            continue
        st, _body = post_edge(bot_id, src, tgt)
        created_edges.append({"from": pair[0], "to": pair[1], "status": st})

    return {
        "bot": bot_id,
        "created_bot": created_bot,
        "table": table_id,
        "ids": ids,
        "nodes": created_nodes,
        "edges": created_edges,
        "existing_node_ids": sorted(_existing_keys(get_workflow(bot_id)[1])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Assemble a TaskBot from a JSON spec.")
    parser.add_argument("spec", type=Path)
    parser.add_argument("--name", help="override spec.name")
    parser.add_argument("--reuse", action="store_true", help="reuse a bot with that name")
    parser.add_argument("--out", type=Path, help="write the created id map as JSON")
    args = parser.parse_args(argv)

    spec_path = args.spec
    if not spec_path.is_file():
        alt = _SKILL / spec_path
        if alt.is_file():
            spec_path = alt
    spec = load_spec(spec_path)
    name = args.name or spec.get("name")
    if not name:
        parser.error("spec has no name; pass --name")
    result = assemble(spec, name, reuse=args.reuse)
    print(json.dumps(result, indent=2))
    if args.out:
        args.out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TokenError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2)
    except (ValueError, RuntimeError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
