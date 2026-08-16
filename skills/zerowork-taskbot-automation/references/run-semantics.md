# Run semantics, markers, and block quirks (verified Aug 16, 2026)

## "Start run from here" / "End run here" markers are PERSISTENT — check before debugging

Setting them (right-click menu) writes `className: 'start'` / `className: 'end'` on the node in `get_workflow()`. They survive page reloads and redirect subsequent FULL runs to start/end mid-chain. Symptom: deterministic 1-second errors on every full run while "run-from-here" of a mid-chain slice works fine.

- Clear via right-click → **"Clear start"** / **"Clear end"** (items only appear when a marker exists on that node).
- Before debugging any weird 1s failure: `GET /connector/<id>/get_workflow/` → check for nodes with non-null `className`.
- Orphaned nodes (no incoming edge, e.g. after deleting an upstream node) trigger "more than one starting building block" — delete or reconnect them. Deleting a node severs its edges; downstream nodes become orphans.

## Run signatures (diagnostic)

- **~1 second + success** = browserless bot (HTTP/math/log pipeline) OR browser blocks all skipped/deactivated. Browser runs take 7–17s+. Use duration to distinguish "config skipped everything" from "actually executed".
- ~1 second + error = persistent marker misdirecting the start, or an orphaned-node structure error.
- 17–19s + error = executed the browser phase then failed in a data block (regex/condition/update).

## Variable semantics

- Variables are runtime refs, NOT table rows: `get_count` / `item/` on the bot's auto-generated Variables table return 0 even after successful Update Data writes. Verify values by interpolating the ref into a Log message (`Result: {id: <dgId>, name: <var>}`).
- Reference syntax `{id: <dataGroupId>, name: <columnName>}` — typed literals in textareas work (verified via the drawer's "Copy variable reference" button + clipboard read).
- New REST-created columns are invisible to open drawers until the editor page is RELOADED (drawers cache variable lists from page load).

## Block-level run rules (each cost a debugging cycle)

- **Numeric condition comparisons throw on non-numeric strings**: `TEST123 > 50` = runtime error; `51.77 > 50` = fine. Sanitize first (math `Remove format`, or regex Replace).
- **Regex patterns need JS delimiters**: `/£/` works, bare `£` errors. Modes: Extract matches / Check if pattern matches / Replace text.
- **Set Condition (conditionNode) has ONE output** — never wire two. Multi-branch = multiple Set Condition blocks chained off one Start Condition (`check_dynamic_data`), each with its own operator. 18 operators total: `= ≠ < > ≤ ≥`, Contains/Not-contains, Data found/empty, Longer/Shorter than, Before/After date, Is (not) a valid number, **Else**.
- **Try-Catch wiring**: `catch` AND `after_try` BOTH wire directly off the `try` node, never off the body or off each other (validator: "must be preceded by a single Start Try-Catch building block"). A/B verified: failing click with try-catch → run Success/0 errors; without → run error.
- **After Repeat** takes the inner loop's SECOND output (see pagination pattern in SKILL.md); hooks always go on the STRUCTURE node, not the last body block.
- Loop drawer: Standard radio is pre-selected; repetition count is an INPUT (placeholder `Enter number of repetitions`), not a textarea.
- Math ops: Add, Subtract, Multiply, Divide, Remainder, Round, Round up/down, Random, Set decimals, Remove format (`1,500,500.2 → 1500500.2`).
- Ask ChatGPT: model select (ChatGPT 5.5 default), prompt textarea (placeholder "Example: Write an uplifting haiku…"), answer saved to table/variable; verified 5s browserless run.
- Send HTTP: Method select (GET default), URL textarea (placeholder `https://api.com`), HEADERS/REQUEST BODY/SAVE RESPONSE sections; GET to a public API verified working with response flowing downstream.

## Deletion & UI mechanics

- **Drawer config saves over WEBSOCKET, not REST** — a fetch hook catches nothing on SAVE. Drawer-driven config is the only write path; REST covers nodes/edges/tables/columns/renames.
- Renames: `PATCH /connector/<id>/ {name}` — reliable (verified on 4 bots).
- Edge deletion (canvas only): real CDP click on `.react-flow__edge-interaction` path + Delete key. `deletable:false` on REST-created edges suppresses the hover ✕ but click+Delete still works. If the edge's nodes are viewport-culled → delete the target node and rewire.
- `js()` gotcha: NEVER `delete window.fetch` to unhook a fetch spy — fetch becomes undefined and every later call throws. Reload to recover; when hooking, keep the original reference.
- Run logs are WS-only — no REST endpoint exposes per-run log text; the Reports LOGS button doesn't respond to automation clicks. Verify via `/execution/` result/errors_count + Log interpolation.

# Estate audit (how to snapshot any account)

- All bots: `GET /connector/?page=1..N` (~20/page, 3 pages on a mature account) → id + name.
- Scheduled bots carry a `scheduler` id on the connector object; `GET /scheduler/<id>/` → cron,
  timezone, interval mode. Only bots with schedulers run unattended — everything else is manual.
- `notify_on_statuses: ['failed']` on a connector = failure emails enabled.
- Run health: `GET /execution/?page=1&page_size=100` — covers ~today only; aggregate by
  `connector_name` client-side (the `?connector=` filter param is IGNORED). Don't rely on it
  for long-term stats.
- Bots deleted (or outside the workspace) return `{}` from `GET /connector/<id>/`.

## Demo bot set worth keeping in a scratch account

A paginated scraper · an advanced-logic bot (try-catch + regex + condition branches) · a
no-try-catch control twin (the A/B proof pair) · a browserless HTTP+math+ChatGPT pipeline ·
a node playground for drawer-schema harvesting (expect some dead husks if you experiment with
type strings).
