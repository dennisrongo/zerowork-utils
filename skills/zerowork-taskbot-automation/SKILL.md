---
name: zerowork-taskbot-automation
description: "Use when building, running, or automating ZeroWork TaskBots."
version: 1.2.0
author: Dennis Rongo (@codingmenace)
license: MIT
metadata:
  hermes:
    tags: [ZeroWork, RPA, TaskBot, browser-automation, React-Flow]
---

# ZeroWork TaskBot Automation

Automate the ZeroWork platform itself: desktop agent lifecycle, building TaskBots in the creator (creator.zerowork.io) via the undocumented REST API plus drawers, connecting blocks, running, and verifying results. Built so an agent can take any automation scenario and assemble it on ZeroWork.io from this skill alone.

## When to Use

- "build/create/run a ZeroWork TaskBot", "automate ZeroWork", ZeroWork client build or troubleshooting work
- Researching ZeroWork: full docs index at https://docs.zerowork.io/llms.txt (every page has a .md version — append `.md` to any docs URL)

## SAFETY FIRST: Verify the account BEFORE touching anything

ZeroWork sessions found in a browser may belong to someone else's workspace, not yours.

1. **Never assume an existing authenticated session is yours.** Navigate to `/workflows` and check the TaskBot list FIRST.
2. If the bot list doesn't match the account you expect (unfamiliar names, missing bots you know should be there) → wrong account → stop and confirm with the account owner.
3. To switch accounts: click "Log out" (clears the local cookie only — harmless), then the owner logs in themselves. Never type credentials.
4. Navigating to `/login` while authenticated auto-redirects to `/workflows` — log out first.

## Desktop Agent lifecycle
- Installed at `%LOCALAPPDATA%\Programs\ZeroWork\ZeroWork.exe` (Electron tray app, no UI)
- Health check: `curl -s http://localhost:9990` → `{"message":"ZeroWork Agent running","version":...,"port":9990}`
- Start if down: launch ZeroWork.exe (background terminal), wait 10–12s, re-curl
- Runs TaskBots in real Chrome windows; window closes after run unless "Stay on page after run" is enabled
- Linux agent exists (.deb/.AppImage/.rpm, download login-gated); VPS installs officially supported. See the Ubuntu install script in this repo's root.

## REST-first build path (PREFERRED over canvas drags)

The creator has a full undocumented REST API (`taskbot-server.zerowork.io`, Bearer = localStorage
`access`). Building via REST + drawers is dramatically faster and more reliable than palette
drags. Verified endpoints, auth, node/edge payloads, table & variable creation, run history, and
the hard validator wiring rules: **[references/rest-api.md]**. Canonical node `type` strings
(wrong ones render as dead husks): **[references/node-types.md]**.

Key facts: edges via `POST /connector/<id>/edge/` (full object incl. `reactflow__edge-<s>a-<t>a`
id); edge/node REST is create-only — deletion = canvas click on edge interaction path + Delete
key; tables are per-bot (create fresh, no cross-attach); After Repeat and On-Catch/After-Try all
wire DIRECTLY off their Start node, never chained after siblings; runs trigger only from the UI
(no REST trigger), verify via `GET /execution/`.

Run semantics — persistent start/end markers, 1s-vs-17s error signatures, variable-vs-table
writes, condition/regex/math block rules, deletion mechanics, and an account-snapshot recipe:
**[references/run-semantics.md]**

Official run/agent/schedule/webhook/reports/common-problems (and release-note behavior
that changes building): **[references/run-and-platform.md]**

Block operational catalog (every palette `type` + Save Lists / Enrich Existing Data):
purpose, drawer fields, wiring/companions, when-to-use, gotchas —
**[references/block-catalog.md]**

Selectors, `{id, name}` refs, `${}` / `$${}` code-in-inputs, spintax, variables vs
native/Sheets/CSV tables: **[references/platform-primitives.md]**

Write JavaScript `zw.*` API (local vs browser, setRef/getRef, deviceStorage, state,
browserContext, packages): **[references/write-javascript.md]**

Verified build patterns — native list scrape (XPath `{loop_index}`), nested-loop pagination,
Write-JS table writes, try-catch/condition pipelines, browserless HTTP+ChatGPT chains, plus
the per-bot table-attachment rule: **[references/build-patterns.md]**

Copyable browser_exec helpers (drop/dump/connect/run/save-drawer): **[scripts/zw_helpers.py]**
— exec into the session after copying to the browser-use workspace:
`exec(open('zw_helpers.py').read())`. Auto-align **does exist** (React Flow controls);
prefer it over guessing canvas coordinates.

## Scenario → TaskBot construction procedure

Use **only** ZeroWork.io nodes and primitives documented in this skill. REST-first
assembly; drawers for config the API cannot write.

1. **Decompose the scenario** into: navigate / interact / decide / repeat / persist /
   notify / (optional) HTTP or JS. Name the human outcome ("N rows in table X",
   "form submitted or error emailed").
2. **Choose blocks** from [block-catalog.md](references/block-catalog.md). Defaults:
   - Open a URL → `open_link` (add `launch_browser` only if sticky/proxy/bypass/scripts
     must change before the first page).
   - List scrape → Standard `loop` + `save` with `{loop_index}` (XPath for grids).
   - Enrich existing rows → Dynamic `loop` + `open_link` (URL column) + `save`.
   - Pagination → outer Standard `loop` (pages) → inner `loop` (items) →
     `continue_after_repeat` off the **inner** opener → `click` Next.
   - Optional web element → `check` (Found / Not Found), not a Set Condition.
   - Data tests → `check_dynamic_data` + N `conditionNode` (one operator each, include
     **Else**). Sanitize numbers (`math` Remove format) before `<` `>`.
   - Recoverable failure → `try` + body; `catch` and `after_try` **both off `try`**.
   - Browserless API → `update_or_configure_api` → `math` / `format_data` / `regex` →
     `log` / `email` / `ask_chatgpt`.
   - Custom / npm / Playwright / secrets → `write_js` with `// @zw-run-locally`.
   - Sub-bot (agent ≥ 1.1.75) → `run_taskbot`; older fire-and-forget → HTTP to webhook.
3. **Design the data model** ([platform-primitives.md](references/platform-primitives.md)):
   - One-value scratch (counter, flag, cleaned price) → variable on the auto
     Variables table.
   - Many rows → native table (default). Sheets only if a human must share/filter
     outside ZeroWork. CSV import creates a native table.
   - REST: `POST /data_group/` `{name, type:'NATIVE', columns:[{colName}…], connector_id}`.
     Tables are **per-bot** — never reuse another bot's table id.
   - Overwrite-each-run → `delete_table_data` (all rows) **before** the Standard loop.
   - Dedup → `remove_duplicate_rows` **after** the loop.
4. **Assemble (REST-first)** ([rest-api.md](references/rest-api.md)):
   - Create bot from `/workflows` → "New TaskBot".
   - `POST /node/` × N with **canonical** `type` strings ([node-types.md](references/node-types.md));
     verify `react-flow__node-<type>` (not `node-default`).
   - `POST /edge/` full objects. Validator: one starting block; After Repeat off
     Start Repeat; catch + after_try off try; non-branch nodes one-out.
   - Reload the editor (new columns appear only after reload).
5. **Configure drawers** — React setters + placeholder targeting; Monaco for
   Write JS; SAVE → "Updated successfully". Clear stray `x` helpers.
   Auto-align, then connect any remaining edges (REST preferred; CDP only if
   the editor tab is visible).
6. **Detect errors** — toolbar. Fix every named node id. Structure errors
   (orphan, companion wired off the body) will also block Run.
7. **Run** — `aria-label="Run"`. Agent must answer `localhost:9990`. No REST
   trigger. Scheduler / webhook need a **linked** agent + awake machine.
8. **Verify** — `GET /execution/` (`result`, `errors_count`, `run_duration`) +
   table `item/` side-effects + Log interpolation. Duration ~1s success on a
   browser bot usually means the browser phase was skipped. Clear leftover
   start/end markers (`className`) before debugging 1s failures.

Worked sketches for (i) paginated list scrape, (ii) form + conditions +
try-catch, (iii) browserless HTTP → transform → Log/Notify live in
[build-patterns.md](references/build-patterns.md) (Patterns 2, 4, 5).

## Creator editor automation — core loop

The creator is React + MUI + React Flow. Node/edge/table **create** is REST
(preferred). Drawer field writes have no REST (they go over websocket) — use
the loop below. Full selectors, event sequences, and pitfalls: **[references/creator-editor-automation.md]**. Copyable drag helper: **[templates/zw_drag.py]**.

1. **Add block** — synthetic HTML5 drag: palette card (`[draggable=true]`, match by innerText) → `dragstart` with `DataTransfer.setData('application/reactflow', '<type>')` (verified: `open_link`) → drop on `div.invisible-drop`. Each drop auto-opens the new block's config drawer.
2. **Configure** — drawer opens CENTER-screen (not right side). Fill via React prototype value-setters + `input`/`change` events. Write JavaScript uses Monaco: `monaco.editor.getEditors()[0].getModel().setValue(code)`. Click SAVE (button text 'SAVE', toast = "Updated successfully").
3. **Connect blocks (trusted input ONLY)** — React Flow's d3-drag ignores synthetic events. Must (a) `switch_tab(targetId)` so the editor tab is VISIBLE (trusted CDP input fails on hidden tabs), then (b) CDP `Input.dispatchMouseEvent` drag: source `.react-flow__handle-bottom` → target `.react-flow__handle-top`. Unconnected blocks fail validation ("more than one starting building block"); edges must run top-to-bottom / left-to-right.
4. **Auto-align** — bottom-left control ("Auto-align top to bottom", a react-flow controls button) fixes messy layouts in one click. Prefer it over dragging nodes.
5. **Rename** — dblclick the title `<p>` → it becomes an `<input>` → set value + Enter. (Or `PATCH /connector/<id>/ {name}` via REST.)
6. **Run** — toolbar button `aria-label="Run"`. Progress streams at the body tail; results at `/reports` (summary only — Write JavaScript `console.log` output is NOT persisted there).

## browser-use quirks that bite here
- Canvas viewport culling: nodes far from origin (x≈-400) drop out of the DOM entirely — `querySelector` returns null even after fit-view/zoom-out; pane-drag pans via CDP are unreliable. Fallback for deleting an edge whose nodes are culled: delete the TARGET NODE (hover → ✕; node deletion removes all its edges), then recreate node + rewire via REST. Before clicking any edge midpoint, verify with `document.elementsFromPoint` that the top element is the pane — the left palette MuiList eats clicks near x<100.
- `click_at_xy` clicks at SCREEN coordinates — if the automation tab isn't foreground it hits whatever the user has open. Prefer `cdp('Input.dispatchMouseEvent', ...)` which goes to the bound target.
- `js()` context drifts when the user opens/closes tabs — rebind via `list_tabs()` + `switch_tab()`. Expect page state to reset after switching.
- `agent_helpers.py` is NOT auto-imported by the current CLI — use `exec(open('agent_helpers.py').read())`.
- CDP input (but not js) dies on long-lived/hidden tabs with IPC TimeoutError — open the same URL via `new_tab()` for a fresh input-alive renderer; js()/fetch keep working on the old one.
- Multi-line inline JS in `js()` gets mangled (stray tokens, dropped parens) when built by string interpolation — build the payload in Python, keep each `js()` call a small clean expression, or write JSON to disk and re-read it in the page.

## Recreating ZeroWork workflows in Playwright
Block→Playwright API mapping, the 5 real gaps (anti-detection, regular-browser mode, scheduling/webhooks, rate caps, visual builder), and two build paths: **[references/playwright-recreation-map.md]**
