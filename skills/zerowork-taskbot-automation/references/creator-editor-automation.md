# ZeroWork Creator — Editor Automation Reference

Verified Aug 15, 2026 against creator.zerowork.io (React + MUI + React Flow, Monaco editor), using a throwaway demo bot in a test account.

## Editor layout
- Left: block palette, grouped (BROWSER / WEB INTERACTION / LOGIC / DATA / EXTERNAL / FILES / TOOLS). ~45 blocks, each a `[draggable=true]` MUI card. Two search inputs: "Search by ID, name or type" (bottom-left, searches canvas nodes) and "Search blocks" (top-right, filters palette). Palette labels that do not match guessed names: Accept/Dismiss Dialog → **Browser Alert** (search "dialog"); Abort / Stop TaskBot → **Abort Run**; Email / Send Email → **Send Notification**; Insert Date → **Record Date**; Save Clipboard / Copy to Clipboard → **Save from Clipboard**.
- Center: React Flow canvas. Each node = a block, `data-id` = numeric ZeroWork ID. Nodes have 4 handles: `a` top (target), `b` left (target), `a` bottom (source), `b` right (source).
- Config drawer opens CENTER-screen (≈x 500-950), not right side. Common mistake: filtering for "right panel" inputs and finding nothing.
- Toolbar (top-right, y<40): Run (`aria-label="Run"`), Detect errors, Schedule, Webhook, Reports, Browser launch settings.
- Bottom-left: React Flow controls; includes Auto-align buttons ("Auto-align top to bottom" / "left to right") — tooltip/hover spans, the clickable element is the `.react-flow__controls-button`.

## Adding a block (synthetic drag — works headless of tab visibility)
```js
const item = [...document.querySelectorAll('[draggable=true]')]
  .find(d => (d.innerText||'').replace(/\n/g,' ').includes('Open') && ...includes('Link'));
const zone = document.querySelector('div.invisible-drop');  // canvas drop overlay
const dt = new DataTransfer();
const mk = (type,x,y) => new DragEvent(type,{bubbles:true,cancelable:true,clientX:x,clientY:y,dataTransfer:dt});
item.dispatchEvent(mk('dragstart',100,300));
zone.dispatchEvent(mk('dragenter', r.x+300, r.y+200));
zone.dispatchEvent(mk('dragover',  r.x+300, r.y+200));
zone.dispatchEvent(mk('drop',      r.x+300, r.y+200));
item.dispatchEvent(mk('dragend',   r.x+300, r.y+200));
```
- The palette's own dragstart sets `application/reactflow` = snake_case type. Verified: `open_link`. Extract others by intercepting `DataTransfer.prototype.setData` during a synthetic dragstart on each palette card.
- The app's drop handler lives on `div.invisible-drop` (class literally `invisible-drop`), NOT the standard react-flow wrapper.
- Each successful drop: creates the node AND auto-opens its config drawer. Drop coordinates influence initial node position but NOT execution order (edges do).
- IMPORTANT ORDERING BUG: the drop→configure→SAVE pattern configures the NEWEST node. If you re-drop a block to reopen its drawer and then delete "the duplicate", you may delete the configured one. Sequence: re-drop → configure new → SAVE → delete the OLD node id.

## Opening an existing node's drawer
- Click the **icon body** of a large-enough card. Working recipe:
  select-click, then a **second click on the card body**. First click
  often only **selects** the node (shows `ID <n>`) and does **not**
  open settings. Search-by-ID (bottom-left) is the same select-only trap.
  Right-click menu is Deactivate / Duplicate / Copy / Start-run-from-here —
  there is no Settings item.
- Catch / After-Try / Break / After-Repeat / Abort Run: select+click
  often opens **no drawer** (no configurable fields). That is
  expected, not a failed open — do not retry forever.
- After fit-view, cards shrink and clicks only select. Zoom in until the
  card is ~100px+, keep the target in the viewport (far nodes cull), then
  click. `scrollIntoView` on a culled node is not enough — React Flow has
  already dropped it from the DOM.

## Overcoming drawer / Run limits (paired Chrome + cua-driver)

REST cannot write drawer fields (websocket only). Playwright / a fresh
Chrome profile cannot click Run — the creator is HTTPS and cannot talk to
`localhost:9990`, so the toolbar reports "Desktop Agent is offline" even
when the agent is healthy. Those are not dead ends.

The **creator window** (where you click Run) is not the **agent window**
(where the TaskBot browses). See [run-and-platform.md](run-and-platform.md)
"Two Chromes". Helpers: [../scripts/zw_cua.py](../scripts/zw_cua.py).
Session driver (list windows, rename, fill notes):
[../scripts/zw_canvas.py](../scripts/zw_canvas.py) —
`ZW_CUA_PID` + `ZW_CUA_WINDOW_ID`, never a hardcoded hwnd. CLIs:
[../scripts/zw_rename.py](../scripts/zw_rename.py),
[../scripts/zw_fill_notes.py](../scripts/zw_fill_notes.py).

### Same Chrome pid, several windows

`list_windows` on the Chrome pid often returns more than the editor.
A smaller Chrome window (NTP, another tab popped out) can sit **on
top of** the creator canvas. SendInput then hits that overlay:
clicks look like they fire, titles do not rename, notes stay
`"Write a note..."`, drawers never open.

1. `list_windows({pid})` and pick the window whose title is the
   TaskBot name (`Demo - X Feed Scraper - Google Chrome`), not
   `"Google Chrome"` or some other tab.
2. If notes / rename / drawer clicks do nothing, `bring_to_front`
   that `window_id`. Live: rename and sticky-note type-in started
   working only after the editor was actually foreground.
3. Do not assume `pid` alone addresses the creator. Always pass
   `window_id`.

### Windows PowerShell + cua-driver

Pipe JSON on **stdin**. PowerShell 5.1 / 7 mangles quotes if you put a
JSON object in argv:

```powershell
'{"pid":<chromePid>,"window_id":<hwnd>}' | & cua-driver call get_window_state
```

Write large payloads (Monaco source) to a temp `.json` file and
`Get-Content -Raw .\payload.json | & cua-driver call type_text`. Never
put access/refresh JWTs, cookies, or account ids in those files if they
might be committed.

`cua-driver serve` must already be running (element-index cache dies
between one-shot processes). Declare a session (`start_session`) and
pass the same `session` on every call.

### Binding that is refused (do not retry)

- `get_browser_state` / `browser_prepare` with `strategy.kind=existing_profile`
  → `browser_consent_required` in standard permission mode (needs
  `--grant existing-profile` or an authorization host).
- Legacy `page` `execute_javascript` → `unbounded_operation_requires_unrestricted`.
- Do not spend a cycle attaching CDP to the user's everyday Chrome
  profile. Drive UIA on the already-open creator window instead.

### Snapshot invariant

Every `element_index` is valid only for the last `get_window_state` of
that `(pid, window_id)`. Re-snapshot after every action. Prefer
`capture_mode: "ax"` while hunting labels; pass `screenshot_out_file`
when you need pixels (drawer open / toast).

### Open a node drawer

1. Cards must be ~100px+ and in the viewport (fit-view shrinks them;
   far nodes cull from the DOM).
2. Find the ~114×115 **Group** that **parents** the node-label Text
   (`"Open Link"`, `"Delay"`, …). Click that Group, **not** the Text.
   Search-by-ID selects (shows `ID <n>`) and does **not** open settings.
   Right-click is Deactivate / Duplicate / Copy / Start-run-from-here —
   no Settings item.
3. First `click` on Chromium often returns `path: post_message`,
   `effect: unverifiable`. Re-snapshot. If the drawer is absent, that
   is a verified no-op — retry the **same** group with
   `delivery_mode: "foreground"` (brief focus swap, then restore).
   Do **not** pass foreground on the first attempt.
4. Live Runs (bottom-right) can cover cards near the bottom of the
   canvas. Click the panel's **Minimize** control, then re-snapshot,
   then click the card.
5. Drawer open is **two clicks**: select-click, then a **second
   click on the card body**. First click often only **selects**
   (card shows `ID <n>` + a small settings badge) — that is not
   a drawer open. Live: even a 130×130 Group, background then
   **same** index foreground, still only selected — Open Link,
   Delay, and Write JS alike. After the select, click the card
   body once more. If two clicks still only select, do not loop
   forever — escalate: human click, or page-JS
   `monaco.editor.getEditors()[0].getModel().setValue` once a
   human has the drawer open.
6. SendInput palette-drag can **drop** a new node without
   auto-opening the drawer. Extra unwired `write_js` husks then
   overlap Delay / Open Link and steal later clicks. Auto-align
   or delete extras before retrying.
7. The card **×** deletes the node. `"Undo delete"` is a short-lived
   toolbar toast — if it expires, `POST /node/` + `POST /edge/`
   again. Do not click × while hunting the icon body.

The left rail (Variables / Tables) can open and change hit
targets. Collapse it with the small chevron Group just left of
the TaskBot title (~28×28). **Do not** click
**Back to Main Menu** — that leaves the editor for `/workflows`.

### Fill + SAVE

- `set_value` on a UIA **Edit** works for ordinary fields (Open Link
  URL, Delay min/max, Log message/tag). The Edit's accessible name is
  often the **placeholder**, not the current value. Proof the write
  landed: the drawer shows **Unsaved changes**.
- MUI table / column pickers are **Buttons** (`"Select a table"`,
  `"Select a column"`). Click → List / ListItem appears → click the
  item (`linkedin_feed_posts`, `post_urn`, …). After a table is chosen,
  Delete Data reveals radios **Delete all rows** /
  **Delete current row**. Remove Duplicates reveals the column picker
  and **Preserve newest rows**.
- Launch Browser is a long drawer of tri-state radios
  (`Use current defaults` / `On` / `Off`) per group (bypass, background,
  stay-on-page, bring-to-front). Stay-on-page sits near the **bottom**.
  Click the **On** radio for that group, confirm **Unsaved changes**,
  then SAVE. A click that misses the radio can close the drawer
  without saving.
- **SAVE** is a Button labeled `SAVE`. After Chrome has been
  foregrounded once this session, SAVE often lands via background
  PostMessage. Toast **Updated successfully**.
- `GET /connector/<id>/get_workflow()` never contains drawer field
  values. Persistence proof is the toast + a later run, not the REST
  node payload.

### Rename nodes

There is **no REST node rename**. `POST /node/` `data.name` is
overwritten by the default type label (`"Open Link"`, `"Start Repeat"`).
`PATCH /connector/<id>/ {name}` renames the **TaskBot**, not a block.

On the canvas (page JS or cua-driver):

1. Zoom until the card is ~100px+ and in view.
2. **Double-click the title Text** (the `<p>`), not the icon Group.
   It becomes an `<input>`.
3. **Ctrl+A** (foreground on Chromium — background is
   `background_unavailable`), then `type_text` the job name, then
   Enter.
4. Re-snapshot. The title must **equal** the new name, not
   `Delete Data` + the new name glued together.

Without Ctrl+A, type_text **appends**. Live mashed title:
`"Delete DataClear previous rows"`. Same rule for every node
(loops, Save WE, Keyboard, Logs).

Proof the rename landed is `GET /get_workflow()` `data.name`,
not UIA: wrapped titles often do not exact-match the string you
typed even when REST has the new name.

The creator window must be the actual foreground window among
that Chrome pid (see "Same Chrome pid, several windows").
Rename and note type-in were no-ops until `bring_to_front`.

Name nodes by job (`Clear previous rows`, `Harvest while scroll`).
Use `sticky_note`s for login / selectors / stop conditions — notes
are not executed and REST-create as empty `"Write a note..."`.
Repo CLIs: `python scripts/zw_rename.py --map "Open Link=Open X home"`
and `python scripts/zw_fill_notes.py --text "..."`.

**Notes that landed (cua-driver):** find the yellow note in the
screenshot (not the 114px node Group), **double-click** the note
body, `type_text`, Escape. REST `data.name` stays `None`; the
visible text survives reload. Single-click can show the color
toolbar without committing text. Yellow centroids:
`zw_canvas.yellow_centroids(shot)` / `zw_fill_notes.py --yellow`.

### Sticky notes — place and drag (live, Demo - X Feed Scraper)

Notes sit **next to the node they document**, not in a top row.

Drag a note by the **top strip** only. A drag that starts on the
text body selects text. If interactivity / lock is off, a drag
pans the pane instead of moving the note — turn interactivity
back on, then grab the strip.

Palette drag-and-drop for sticky notes is flaky. Drops in the
far-left canvas often produce nothing. Workaround: create the
note in the mid/right canvas, type text immediately, then drag
by the **top strip** to the target node.

An empty note is discarded if you click away before typing.

Auto-align top-to-bottom can yank notes into a horizontal row.
Place notes **after** node layout, or skip auto-align once notes
are placed.

X-feed notes that belong on that canvas (exact copy):

- "Agent Chrome must be signed into X. Creator tab login does not count."
  → next to Launch Chrome / Open X home
- "Write JS harvest-while-scroll: X remounts tweet cards. Dedup column is post_id."
  → right of Harvest while scroll
- "Stop after 3 empty scroll rounds or 40 unique posts."
  → lower-right of Harvest while scroll
- "Outer N = scroll rounds, not tweet count."
  → right of Scroll rounds

### Sticky notes — palette unreachable (live, Demo - HTTP + Math Pipeline)

When the react-flow control bar (zoom/fit/sticky-note drag) sits
below a 1280×800 viewport, palette sticky notes are unreachable.

Workaround: each node's speech-bubble icon (bottom-right of the
card) → "Write a note…" → SAVE. That attaches a note beside
the node.

Empty notes still discard on click-away.

### Monaco (Write JavaScript)

If a human is in this drawer (or pastes **Copy AI instructions**),
give one pasteable script — do not type it in. Contract:
[write-javascript.md](write-javascript.md) "Authoring for a human".

Page JS (when you have it): `monaco.editor.getEditors()[0].getModel().setValue(code)`.
That is the live-verified write for `templates/x_feed_harvest.js`.
UIA `set_value` does not land. Leave **Run locally** unchecked
(in-page harvest — the script reads the X DOM).

On the paired Chrome via cua-driver (no page JS):

| Attempt | Result |
|---|---|
| UIA `set_value` on Edit `"Editor content"` | Ignored. No Unsaved changes. |
| Clipboard + Ctrl+V (foreground) | Ctrl+A selects; paste does not replace. |
| Focus editor → Ctrl+A foreground → `type_text` **without** `element_index`, `delivery_mode: "foreground"`, `delay_ms: 0` | Replaces the buffer. Unsaved changes appears. |
| `type_text` of a multi-line string | `\n` (LF) is **dropped**. `\r` / CRLF **does** insert a Monaco newline (LinkedIn import landed as 29 lines because the file was CRLF). LF-only flatten looks like `func` / `r is not defined` when `function` / `require` wrap. |
| Non-ASCII in the payload (em dash, smart quotes) | SendInput can abort after the first Unicode char. Keep Monaco type-ins ASCII. |

Workarounds that landed: flatten the script to **one line** (no `//` comments — use `/* … */` only if the closer is on the same line), **or** `press_key` Return after each line. For local execution, tick **Run locally in the app** (checkbox). A trailing `// @zw-run-locally` on a flattened one-liner was **not** honored — the block ran as Browser execution and `require` threw `ReferenceError: require is not defined`. A flattened in-page harvest that started with `function txt(...)` executed as `ReferenceError: func is not defined` — do not start a typed-in one-liner with the `function` keyword; prefer `var txt = function (...)` or a short `require` runner plus the checkbox.

`// @zw-run-locally` on its **own** line is enough to run locally; the
drawer checkbox is the reliable cua-driver path when you cannot insert
newlines. After a foreground type-in, SAVE immediately — do not assume
`set_value` committed.

### Detect errors + Run

- **Detect errors** can sit on *"Checking for disconnected blocks or
  missing input data, please wait..."* for a long time, sometimes
  with **no result banner**. That toast is not a hard lock: **Run**
  still starts (it runs the same validator).
- Empty **unconnected** Write JS nodes fail Detect errors. Delete
  orphan husks (palette-drag leftovers). Keep one connected Write
  JS named **Harvest while scroll** when that is the X harvest
  path; fill it from `templates/x_feed_harvest.js`. On the JS demo,
  Harvest sits **before** Try, not as a sibling off Try.
- Start Try-Catch may have **at most three connections** (one body
  + On Catch + After Try-Catch). A Write JS sibling off Try is a
  fourth wire and fails Detect errors: "The Start Try-Catch
  building block can have up to three connections...". Valid JS
  demo: Wait for timeline → Harvest while scroll → Scrape scope
  (try) → (Scroll rounds | catch | after_try).
- Run is the toolbar UIA Button `"Run"` (`aria-label="Run"`) on the
  **paired** creator window. Same background-then-foreground click
  rule. While a run is live the button's name becomes `"running"`.
- Never click Run in Playwright / a second Chrome on the same machine.

### Verify (do not stop at execution.success)

`GET /execution/` `result=success` + `errors_count=0` can still mean
Try-Catch swallowed a scrape failure (login page, 0 cards). Also:

1. `GET /data_group/<id>/item/get_count/` — rows actually present.
2. Live Runs step text (UIA labels): `"Opened the URL: …"`,
   `"Pausing run for N seconds"`, `"Browser execution"`, the throw
   message, `"N duplicate rows were removed. M unique rows remain."`,
   `"Your TaskBot ran successfully."`
3. Item **cells**, not a guessed `data` dict — [rest-api.md](rest-api.md).

A ~1s browser-bot success still means the browser phase was skipped.

## Configuring a block
- Fields: React prototype setters, not `el.value=`:
```js
const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
setter.call(el, 'value'); el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true}));
```
- Open Link: `textarea[placeholder="https://example.com"]`.
- Save Web Element: `textarea[placeholder="Enter CSS or XPath selector"]`; "Save as" is a MUI Select (Text/Link/HTML/Custom attribute/Image file URL); "Save to" is a MUI Autocomplete whose popup is easily clobbered by a stale listbox — Escape the old menu FIRST. Synthetic typing + Enter/blur was NOT reliably committing the Autocomplete (unresolved; workaround = use a Write JavaScript block instead).
- Write JavaScript: Monaco. Wait ~2.5s after drop ("Loading..."). With
  page JS: `monaco.editor.getEditors()[0].getModel().setValue(code)`.
  Without page JS (cua-driver): see **Monaco** under "Overcoming drawer /
  Run limits" — UIA `set_value` is a no-op. Docs buttons: "Copy table or
  variable reference" and "Copy AI instructions".
- Log: first visible textarea = "Log message".
- SAVE button: text 'SAVE', bottom of drawer. Success toast: "Updated successfully". Unsaved banner: "Unsaved changes".

## Connecting blocks (the hard part)
- Synthetic MouseEvent/PointerEvent sequences and calling the app's `onConnect` prop directly DO NOT create edges (onConnect dispatches a collab-layer message that didn't apply when tried; d3-drag needs trusted input).
- WORKING METHOD: trusted CDP input, tab must be VISIBLE:
  1. `list_tabs()` → find the editor target → `switch_tab(targetId)` → confirm `document.visibilityState === 'visible'`. Hidden tabs break trusted input entirely (browser-use's `cdp()` routes to the bound target, but the throttled/hidden page drops the drag).
  2. Get handle centers via getBoundingClientRect.
  3. CDP drag:
```python
cdp('Input.dispatchMouseEvent', type='mouseMoved', x=sx, y=sy)
cdp('Input.dispatchMouseEvent', type='mousePressed', x=sx, y=sy, button='left', buttons=1, clickCount=1)
for i in range(1,9):  # interpolate sx,sy -> tx,ty
    cdp('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y, buttons=1); time.sleep(0.06)
cdp('Input.dispatchMouseEvent', type='mouseReleased', x=tx, y=ty, button='left', buttons=0, clickCount=1)
```
- Direction matters: edges must go top→bottom (or left→right). A right-to-left edge = "connected backwards" = still counts as disconnected. Use Auto-align first, then connect in visual order.
- Node drags (repositioning) also need the same trusted CDP drag on the node body. A CDP node-drag can grab the WRONG node if coordinates are stale — re-read rects immediately before dragging.

## Deleting nodes
- Each node has an × button (first `button` in the node) — synthetic click works. BUT: hover-revealed in some states; after a React-setter save + tab switch a node can render with NO button in the DOM (persisted-but-broken). Recover by deleting neighbors and rewiring, or delete the orphan if it is unused.
- App's own delete path: ancestor fiber of the react-flow div exposes `onNodesDelete` → dispatches `D("delete", {triggered:true, data:{ids, prevNodes, prevEdges}})`. Not needed if × buttons work.
- "Undo delete" appears after deletions.

## Running + results
- Run button → validation first ("Checking for disconnected blocks or missing input data"). Failure: lists offending block IDs. The "please wait" toast can linger; Run still proceeds. Success: **agent** Chrome opens (separate profile), blocks execute in edge order, Live Runs streams at the canvas corner.
- Verified run: Open Link → Write JavaScript ("Browser execution / Executed custom JavaScript code") → Log → "Your TaskBot ran successfully."
- `/reports` shows step statuses + duration only. Write JavaScript `console.log` is NOT persisted. Persist via table write / `zw.log` / Send Notification.
- Agent must answer `localhost:9990`. The creator tab must be the **paired** Chrome — see "Overcoming drawer / Run limits".

## browser-use CLI notes
- `switch_tab(targetId)` rebinds js()/cdp() AND may reset page render state — re-query nodes after switching.
- `click_at_xy` = SCREEN coordinates, hits the user's foreground app if automation tab isn't frontmost. Avoid in this workflow.
- `agent_helpers.py` in the workspace is NOT auto-imported — `exec(open('agent_helpers.py').read())`.
- Long inline grep one-liners with multiple `-o` patterns can be rejected as a malformed payload — write a script file or split the command.
