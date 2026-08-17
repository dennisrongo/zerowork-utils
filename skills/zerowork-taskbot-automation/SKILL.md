---
name: zerowork-taskbot-automation
description: "Use when building, running, or automating ZeroWork TaskBots."
version: 1.3.10
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
(wrong ones render as dead husks): **[references/node-types.md]**. Demo -
Node Playground is the living coverage map (incomplete vs the 44; 25
`node-default` husks are expected there — never ship those on a client bot).

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
browserContext, packages): **[references/write-javascript.md]**. If a human is
in the Write JS drawer (or pastes **Copy AI instructions** / **My
references**), give **one pasteable script** — authoring contract in
that file. Do not SendInput the buffer when they can paste.

Verified build patterns — native list scrape (XPath `{loop_index}`), nested-loop pagination,
Write-JS table writes, try-catch/condition pipelines, browserless HTTP+ChatGPT chains, plus
the per-bot table-attachment rule: **[references/build-patterns.md]**

Copyable helpers live in this skill — do not depend on Temp implementer
files. Browser_exec (drop/dump/connect/run/save-drawer):
**[scripts/zw_helpers.py]** — `exec(open('zw_helpers.py').read())` after
copying into the browser-use workspace. REST (tokens from `ZW_ACCESS` /
`ZW_REFRESH` only — never reconstruct JWTs): **[scripts/zw_api.py]**,
inspect **[scripts/zw_inspect.py]**, assemble from a JSON spec
**[scripts/zw_assemble.py]**. Paired-Chrome cua-driver: parse UIA tree
**[scripts/zw_cua.py]**; session driver (list windows, rename, notes)
**[scripts/zw_canvas.py]** + **[scripts/zw_rename.py]** +
**[scripts/zw_fill_notes.py]** — pid/window from `ZW_CUA_PID` /
`ZW_CUA_WINDOW_ID`, never a hardcoded hwnd. Pasteable harvest scripts:
**[templates/x_feed_harvest.js]**, **[templates/linkedin_feed_harvest.js]**
(resolve `ref_id` via `zw.getTaskbotInfo()`, not another bot's table id).
Graph specs: **[templates/x_feed_nocode.json]**,
**[templates/linkedin_feed.json]** (`text` / `source` on that spec are
fill hints — REST cannot write note bodies or Monaco). Auto-align
**does exist** (React Flow controls); prefer it over guessing canvas
coordinates. Auto-align top-to-bottom can yank sticky notes into a
row — place notes after node layout, or skip auto-align once notes
are placed. Session-only
probes (palette-click experiments, screenshots, token files) stay out of
the repo.

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
     Paginated / infinite feeds → **nested Standard loops + Keyboard
     PageDown/Space** first (Pattern 2 / 7). Write JS only if the
     virtualizer still remounts cards so `{loop_index}` cannot hold a
     stable list (find-selector in
     [platform-primitives.md](references/platform-primitives.md)).
   - Name every node by role (`Clear previous rows`, `Page down to load
     more`). Add `sticky_note`s for login, selectors, and stop
     conditions — notes are not executed.
   - Enrich existing rows → Dynamic `loop` + `open_link` (URL column) + `save`.
   - Pagination → outer Standard `loop` (pages) → inner `loop` (items) →
     `continue_after_repeat` off the **inner** opener → `click` Next.
   - Optional web element → `check` (Found / Not Found), not a Set Condition.
     Found / Not Found are **no-drawer** outcome marker cards. Branching
     is edge wiring off Check, not a drawer field.
   - Data tests → `check_dynamic_data` + N `conditionNode` (one operator each, include
     **Else**). Sanitize numbers (`math` Remove format) before `<` `>`.
   - Start Repeat: pick **Standard** or **Dynamic**. Live Pattern 4 had
     loop type **UNSET** (neither selected). Detect errors may stay
     quiet — set Standard before a client build.
   - Go Back or Forward: live playground had **neither** Go back nor
     Go forward selected (dead default footgun). Set one before a
     client build.
   - Switch Frame: live playground had **neither** Iframe nor
     Main page selected (dead default, same class as Go Back).
     min/max 0/0. Set one before a client build.
   - Browser Alert (palette label; search "dialog" — there is no
     Accept/Dismiss Dialog card): optional **Prompt response**
     textarea; min/max 0/0. No explicit Accept vs Dismiss control.
   - Abort Run: **no drawer**, no configurable fields. Do not retry
     select+click.
   - Send Notification: **Subject** + **Email content** + min/max.
     Sends to the signed-in account email — **no To: field**.
   - Upload File: tip "Make sure to initiate the upload by clicking the 'Upload' button in the previous step."
     File source radios From file URL / From folder path on your
     computer — live default **neither** selected. min/max.
   - Record Date: **Select date format** dropdown (nothing selected
     live). No min/max.
   - Save from Clipboard: **Save copied text to** table/variable
     picker. No min/max.
   - Save Page URL: **Save current page URL to** table/variable
     picker. No min/max.
   - Quit Browser: **Force quit** checkbox (unchecked live). No min/max.
   - Recoverable failure → `try` + body; `catch` and `after_try` **both off `try`**.
     Catch is a **dead-end on purpose** (no outgoing edge, no drawer).
     After Try-Catch is the continue path (also no drawer). The proof
     is a Log after After Try-Catch, not a catch→log wire.
     Start Try-Catch may have at most THREE connections (one body + On Catch +
     After Try-Catch). A Write JS sibling off Try is a fourth wire and fails
     Detect errors: "The Start Try-Catch building block can have up to three
     connections...". Valid JS demo: Wait for timeline → Harvest while scroll
     → Scrape scope (try) → (Scroll rounds | catch | after_try).
   - Browserless API → `update_or_configure_api` → `math` / `format_data` / `regex` →
     `log` / `email` / `ask_chatgpt`. HTTP must **SAVE RESPONSE** or
     the call is a no-op. Live Pattern 5 left body / nested path /
     status **all empty** — Detect errors can stay quiet while the
     API result is discarded. Math writes back to `fx_x100`
     (Multiply × 2.5). Ask ChatGPT one-word HIGH or LOW →
     `gpt_answer`. Pick refs with **V / My references**.
   - Custom / npm / Playwright / secrets → `write_js` with `// @zw-run-locally`.
   - Sub-bot (agent ≥ 1.1.75) → `run_taskbot`. **Wait until the TaskBot finishes** CHECKED = sync; uncheck =
     fire-and-forget.
     No min/max delay. Older fire-and-forget → HTTP to webhook.
   - Insert Text or Data: **Use spintax** is CHECKED by default.
   - Raise Error: optional message (live default "A custom error was raised.");
     **Mark this TaskBot run as failed in the run report**
     and **Include this error in the error report** both unchecked live.
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
   - Create bot: `POST /connector/` `{name}` (or `/workflows` → "New TaskBot").
   - `POST /node/` × N with **canonical** `type` strings ([node-types.md](references/node-types.md));
     verify `react-flow__node-<type>` (not `node-default`). **Never ship
     `node-default` husks on a client bot** — the playground has 25 as a
     lesson, not a template. Custom `data.name`
     is overwritten by the default type label.
   - `POST /edge/` full objects. Validator: one starting block; After Repeat off
     Start Repeat; catch + after_try off try; Start Try-Catch at most THREE
     connections (one body + On Catch + After Try-Catch — a fourth wire, e.g.
     Write JS sibling off Try, fails Detect errors: "up to three connections");
     non-branch nodes one-out.
   - Reload the editor (new columns appear only after reload).
5. **Configure drawers** — no REST write. On the **paired** Chrome window
   (not Playwright): cua-driver loop in
   [creator-editor-automation.md](references/creator-editor-automation.md)
   (helpers: [scripts/zw_cua.py](scripts/zw_cua.py)). `list_windows`
   first — a second Chrome window of the **same pid** can overlay
   the editor and swallow SendInput. `bring_to_front` the window
   whose title is the TaskBot. Snapshot → click the ~114px Group
   parent of the node label (`foreground` only after a background
   no-op) → `set_value` / MUI ListItem → SAVE → "Updated
   successfully". Drawer open: select-click, then a **second click on the card body**.
   First click often only shows `ID <n>` (selected, drawer still closed).
   Do not treat the ID-only state as open, and do not retry the same
   select-click forever
   ([creator-editor-automation.md](references/creator-editor-automation.md)).
   Catch / After-Try / Break / After-Repeat / Found / Not Found /
   Abort Run: select+click often opens **no drawer** (no configurable
   fields) — do not retry forever.
   Monaco ignores UIA `set_value` — type_text recipe in
   that file. If the user is sitting in Write JS, hand them one
   pasteable script ([write-javascript.md](references/write-javascript.md)
   "Authoring for a human") — do not type it in. Monaco: page JS
   `monaco.editor.getEditors()[0].getModel().setValue(code)` works;
   UIA `set_value` does not. Leave **Run locally** unchecked for
   in-page harvest (`templates/x_feed_harvest.js`). **Rename:**
   dblclick the title, **Ctrl+A**, type the job name, Enter (without
   Ctrl+A the new text appends; `PATCH /connector` is the TaskBot
   name only). Add `sticky_note`s **next to** the node they document
   (not a top row). Drag a note by its **top strip** only — a
   text-body drag selects text; interactivity/lock off pans the
   pane. Clear stray `x` helpers. Auto-align **nodes** first, then
   place notes (top-to-bottom auto-align yanks notes into a row).
   Connect remaining edges (REST preferred). Empty unconnected
   Write JS husks fail Detect errors — delete orphans; keep one
   connected Write JS named **Harvest while scroll** when that is
   the X harvest path. On the JS demo, Harvest sits on the spine
   **before** Try (Wait for timeline → Harvest while scroll →
   Scrape scope). Do not also wire Harvest off Try — that fourth
   wire fails Detect errors ("up to three connections").
6. **Detect errors** — toolbar. The "please wait" toast can hang
   with only "please wait" and no result banner. That is not a
   hard lock; Run still starts. Fix every named node id. Structure errors (orphan,
   companion wired off the body, empty unconnected Write JS, Start
   Try-Catch with a fourth wire) also block Run. Delete orphan Write
   JS husks. Try max = one body + On Catch + After Try-Catch.
   Catch is a dead-end on purpose (no outgoing edge).
7. **Run** — `aria-label="Run"` **from the Chrome profile the Desktop Agent
   is paired with**. A Playwright / fresh Chrome window on the same machine
   will say "Your Desktop Agent is offline" even when `localhost:9990`
   answers — the creator page cannot `fetch` http://127.0.0.1 from HTTPS
   and has no native-host pairing. No REST trigger. Scheduler / webhook
   need a **linked** agent + awake machine.
8. **Verify** — `GET /execution/` (`result`, `errors_count`, `run_duration`)
   is not enough: Try-Catch can swallow a login/scrape throw and still
   report success / 0 errors. Also `GET /data_group/<id>/item/get_count/`
   (read `cells[].text`, not a flat `data` dict) + Live Runs step text.
   Duration ~1s success on a browser bot usually means the browser phase
   was skipped. Creator Chrome login ≠ agent Chrome login
   ([run-and-platform.md](references/run-and-platform.md)). Clear leftover
   start/end markers (`className`) before debugging 1s failures. There is
   no REST create-row.

Worked sketches for (i) paginated list scrape, (ii) form + conditions +
try-catch, (iii) browserless HTTP → transform → Log/Notify, (iv) LinkedIn-
style virtualized feed, (v) X/Twitter infinite-scroll feed live in
[build-patterns.md](references/build-patterns.md) (Patterns 2, 4, 5, 6, 7).

## Creator editor automation — core loop

The creator is React + MUI + React Flow. Node/edge/table **create** is REST
(preferred). Drawer field writes have no REST (they go over websocket) — use
the loop below. Full selectors, event sequences, and pitfalls: **[references/creator-editor-automation.md]**. Copyable drag helper: **[templates/zw_drag.py]**.

1. **Add block** — synthetic HTML5 drag: palette card (`[draggable=true]`, match by innerText) → `dragstart` with `DataTransfer.setData('application/reactflow', '<type>')` (verified: `open_link`) → drop on `div.invisible-drop`. Each drop auto-opens the new block's config drawer.
2. **Configure** — drawer opens CENTER-screen (not right side). Fill via React prototype value-setters + `input`/`change` events when you have page JS; otherwise the cua-driver loop in [creator-editor-automation.md](references/creator-editor-automation.md). Write JavaScript / Monaco: page JS `monaco.editor.getEditors()[0].getModel().setValue(code)` — UIA `set_value` does not work. Leave **Run locally** unchecked for in-page harvest. Click SAVE (button text 'SAVE', toast = "Updated successfully").
3. **Connect blocks (trusted input ONLY)** — React Flow's d3-drag ignores synthetic events. Must (a) `switch_tab(targetId)` so the editor tab is VISIBLE (trusted CDP input fails on hidden tabs), then (b) CDP `Input.dispatchMouseEvent` drag: source `.react-flow__handle-bottom` → target `.react-flow__handle-top`. Unconnected blocks fail validation ("more than one starting building block"); edges must run top-to-bottom / left-to-right.
4. **Auto-align** — bottom-left control ("Auto-align top to bottom", a react-flow controls button) fixes messy node layouts in one click. Prefer it over dragging nodes. Do it **before** placing sticky notes — top-to-bottom auto-align yanks notes into a row. Skip it once notes sit next to their nodes.
5. **Rename** — dblclick the title `<p>` → `<input>` → **Ctrl+A** →
   type the job name → Enter. Without Ctrl+A the new text appends.
   `PATCH /connector/<id>/ {name}` renames the TaskBot only. No REST
   node rename. Full recipe:
   [creator-editor-automation.md](references/creator-editor-automation.md)
   "Rename nodes".
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
