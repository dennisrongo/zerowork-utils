# REST API — verified endpoints & validator rules (taskbot-server.zerowork.io)

Base: `https://taskbot-server.zerowork.io` · Auth: `Authorization: Bearer <localStorage 'access' JWT>`
(in-page `fetch` from a creator.zerowork.io tab; 401 "token not valid" = expired → reload the app
page, it self-refreshes). js() runs work on hidden tabs; CDP *input* does not.

Repo helper (no tokens in source): [../scripts/zw_api.py](../scripts/zw_api.py).
Set `ZW_ACCESS` or `ZW_ACCESS_FILE`. Refresh with `ZW_REFRESH` /
`ZW_REFRESH_FILE` via `POST /auth/token/refresh/`. Never reconstruct or re-sign a JWT from decoded claims.
Never commit `zw_access.txt`. Inspect: [../scripts/zw_inspect.py](../scripts/zw_inspect.py).
Assemble a spec: [../scripts/zw_assemble.py](../scripts/zw_assemble.py).

## Nodes & edges (create-only — no PUT/PATCH/DELETE anywhere, all 405)

- `POST /connector/<botId>/node/` — `{type, data: {name}, position: {x, y}, deletable: true, zIndex: 1}`.
  Node rows are ~200 y-units apart in canvas coordinates. Valid types: see node-types.md.
  Custom `data.name` is overwritten by the default type label ("Open Link", not
  your title). Drawer config is still websocket-only — it is not in `get_workflow()`.
- `POST /connector/<botId>/edge/` — FULL object or 400 "Required data was not provided":
  `{id: 'reactflow__edge-<src>a-<tgt>a', source, target, sourceHandle: 'a', targetHandle: 'a', type: 'buttonEdge', deletable: false, zIndex: 1}`
- `GET /connector/<botId>/get_workflow/` — ground truth for nodes + edges. Never trust the canvas
  renderer: it culls off-screen nodes and can show 0 rendered edges while the API holds them all
  (stale edge layer; reload or open a fresh tab to fix).
- Edge/node DELETION is canvas-only: real CDP click on the edge's `.react-flow__edge-interaction`
  path (bounding-rect center), then `Delete` key. Node ✕ needs hover; REST-created edges with
  `deletable: false` never show the hover ✕ button — use click+Delete instead.
- Deactivate/reactivate a node WITHOUT hover: js-dispatch `contextmenu` (MouseEvent, button 2) on
  the node → click the "Deactivate"/"Activate" menu item via js. Deactivated nodes get class
  `deactive` and are skipped at run — but STILL count for structural validator rules.

## Workflow assembly (REST-first — minutes, not canvas hours)

1. Create bot: `POST /connector/` `{name}` → `{id, name, variables_id}` (200).
   Names must be **unique** (1.1.61) — a colliding create fails.
   (The `/workflows` "New TaskBot" button does the same.) `POST /auth/token/refresh/`
   `{refresh}` returns a new `access` JWT when the stored access token is expired.
2. `POST /node/` × N (grid positions), `POST /edge/` × chain.
3. `POST /data_group/` `{name, type: 'NATIVE', columns: [{colName}...], connector_id}` — creates
   AND attaches a table with columns in one call. Tables are per-bot instances; REST has NO route
   to attach an existing table to another bot (405) — always create fresh per bot via REST.
   The UI (1.1.75) can **Add an existing table** — do not tell a weaker model
   tables can never be reused.
4. Reload the editor → configure drawers (paired-Chrome cua-driver, or
   page-JS setters — [creator-editor-automation.md](creator-editor-automation.md))
   → "Detect errors" → Run. Rename the **TaskBot**:
   `PATCH /connector/<id>/ {name}` (200 "Ok"). That does **not**
   rename nodes — `data.name` is overwritten on create; UI recipe in
   [creator-editor-automation.md](creator-editor-automation.md).

## Tables, variables, items

- `GET /connector/<id>/data_group/list_all/` — attachments (every bot auto-has a "Variables" table).
- `GET/POST /data_group/<id>/column/` — POST field is **`name`** (not colName) on existing tables:
  `{name: 'price_raw'}` → 200. Creating variables for a bot = POST columns to its Variables table.
- Variables created via REST do NOT appear in already-open drawer dropdowns until a full page
  reload (drawer caches the list at load).
- `GET /data_group/<id>/item/?page=1&ordering=id` (page_size up to 100), `.../item/get_count/`,
  `DELETE /data_group/<id>/item/<itemId>/` → 204 (batch_delete broken — loop per-item).
- **No REST create-row.** `POST` / `PUT` / `PATCH` on `/data_group/<id>/item/`,
  `/item/create/`, `/items/`, `/row/`, `/item/add/` are 405 or 404. Rows appear
  only when a **run** writes them (`zw.setRef`, Save Web Element, Update Data).
- Item JSON is **not** a flat `data` dict. Shape:
  `{results:[{id, cells:[{column_id, text, is_preview}], files:[]}]}`.
  Map `column_id` through `GET /data_group/<id>/column/` (`colName` on create,
  `name` on later POSTs). Reading `row["author"]` will look empty even when
  `cells` hold the value.

## Runs & observability

- Runs are triggered from the creator UI (`aria-label="Run"` button) and execute on the desktop
  agent. No REST trigger exists (`/execution/run/` etc all 404) — the scheduler runs server-side
  but exposes no manual-run endpoint.
- `GET /execution/?page=1` — run history: `created_at, result ("success"|"error"), errors_count,
  run_duration, connector_name`. The programmatic assertion hook. Scheduled bots
  appear here too — match `connector_id`/`connector_name`, not just "latest".
- Run LOGS have no REST endpoint (`/execution/<id>/logs/` etc 404). The Reports page LOGS button
  did not respond to automation; the editor "Live Runs" panel only renders during an active run.
  Best available evidence: errors_count + result + table side-effects. Reading per-step logs
  remains an open gap — capture the Live Runs DOM during a run if step detail is required.
- Pre-run validator ("Detect errors" = same check): blocks the run, names offending node IDs.
  Trust it; fix what it names.

## Validator structure rules (each hard-blocks the run)

1. Non-branch blocks may have only ONE outgoing edge. Branch-capable: Start Condition, Start
   Repeat, Check Web Element, Start Try-Catch ("Building blocks other than ... cannot be
   connected to more than one building block").
2. **After Repeat must be wired DIRECTLY off a Start Repeat node** (its 2nd output), not chained
   after the loop's children: "The After Repeat building block must be preceded by a single Start
   Repeat building block". Verified pagination pattern:
   `Open → loop(pages) → loop(count elements) → [out1] saves×N / [out2] After Repeat → Click Next → Log`.
3. **Same rule for Try-Catch**: On Catch Error AND After Try-Catch each wire directly off the
   Start Try-Catch node. `try → click-body … try → catch`, `try → after_try → rest`.
   Start Try-Catch may have **at most THREE connections**: one body + On Catch +
   After Try-Catch. A fourth wire (Write JS sibling off Try) fails Detect errors:
   "The Start Try-Catch building block can have up to three connections...".
   Valid JS demo topology: Wait for timeline → Harvest while scroll → Scrape
   scope (try) → (Scroll rounds | catch | after_try). Do not also wire harvest
   off try.
4. Empty required fields are named by node ID ("Some required fields are empty... <nodeId>").
5. Rules apply to deactivated nodes too.

## Verified semantics (controlled experiments, Aug 16 2026)

- **Try-Catch works**: bot with `open → try → click(definitely-not-present-element)`
  + catch (dead-end, no outgoing edge) + after_try → Log
  `TRY-CATCH TEST: run continued after error` ran Success/0 errors; identical control bot without try ran error/1 error. Catch swallows the
  step failure; execution continues at After Try-Catch. Do not wire catch → log.
- **Pagination**: the nested-loop pattern above scraped 54/60 rows across 3 pages in 11s
  (inner loop raced page-3 render for ~6 books — add Delay after Click Next or wait-selectors).
- **Condition system**: Start Condition (`check_dynamic_data`) holds the value to compare; each
   Set Condition (`conditionNode`) holds ONE comparison + ONE outgoing edge. 18 operators:
   `= ≠ < > ≤ ≥` (number), Contains/Does not contain keywords, Data found (not empty)/Data not
   found (empty), Longer/Shorter than (char length), Before/After (date), Is (not) a valid
   number, **Else** (fallback when no other condition met). Multi-branch = N Set Condition blocks
   chained from one Start Condition.
- **Hand-typed variable references** (`{id: <dgId>, name: <col>}`) in a Regex "text to apply"
   field produced a run error in the one test attempted — unverified whether the format or the
   setup was wrong; prefer the drawer's V reference picker. (Unresolved at capture time.)

## CDP / browser-use gotchas specific to this app

- **CDP input death on long-lived tabs**: `Input.dispatchMouseEvent` starts timing out (IPC
  TimeoutError) after heavy canvas work or when the tab is hidden, while js() keeps working.
  Fix that worked twice: `new_tab(<same URL>)` — fresh renderer, input alive immediately.
- Tab hidden (`visibilityState: 'hidden'`) → CDP input unreliable even after
  `Target.activateTarget`. Duplicate editor tabs of the same bot share server state; the VISIBLE
  dup tab may differ from the bound automation tab (computer_use drives the visible one,
  browser-use drives its bound one — verify which DOM you're reading).
- MUI Autocomplete/Select dropdowns: open on real mousedown at the field; listbox renders at
  different coords than the trigger; one click opens, a second closes. Sequence: click → sleep →
  query `[role=listbox]` rect → click option. If a select won't open, scroll the drawer to
  bottom (`scrollTop = 9999` on its scrollable) and retry — fields near the drawer edge are
  clipped.
- SaveWE/regex drawers pair each textarea with a slim helper textarea that tends to capture a
  stray 'x' from CDP typing; target fields by PLACEHOLDER (e.g. '/example/...', 'Enter number',
  'Enter text'), never by y-coordinate pairs, and clear stray 'x' values before SAVE.
- Node drawers: click the node card (icon body), not the label text; label-only clicks do nothing.
- fit-view control: `aria-label="fit view"` (quote the attribute in querySelector — unquoted
  values with spaces throw). Zoom ≲0.5 collapses node cards to label-only chips.
