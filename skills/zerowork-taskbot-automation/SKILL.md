---
name: zerowork-taskbot-automation
description: "Use when building, running, or automating ZeroWork TaskBots."
version: 1.3.20
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

## Skill maintenance

**Standing rule:** the repo README skill section (`README.md` at the
repo root) must be updated in the same change as any skill version bump (patterns, selector policy, Write JS convention, new templates,
Job intake). Do not ship a bump that leaves the README stale.

## SAFETY FIRST: Verify the account BEFORE touching anything

ZeroWork sessions found in a browser may belong to someone else's workspace, not yours.

1. **Never assume an existing authenticated session is yours.** Navigate to `/workflows` and check the TaskBot list FIRST.
2. If the bot list doesn't match the account you expect (unfamiliar names, missing bots you know should be there) → wrong account → stop and confirm with the account owner.
3. To switch accounts: click "Log out" (clears the local cookie only — harmless), then the owner logs in themselves. Never type credentials.
4. Navigating to `/login` while authenticated auto-redirects to `/workflows` — log out first.

5. **Never store or type site logins.** Passwords, cookie JSON, 2FA
   codes, and session tokens must never go in the skill, templates,
   notes, or committed files. Never type credentials into a TaskBot.
   Dennis does all site logins himself (Agent Chrome, cookies, 2FA).
   A brief may say "logged-in site"; the human signs in on Agent
   Chrome before Run.


## Job intake

An agent can take a client job from a brief without Dennis in the
loop for the *build*. Required brief fields:

- **Outcome** — table columns / email / webhook / DM cap (name the
  human result)
- **Site URL(s)** + public vs logged-in
- **Pattern hint** if obvious (or pick from Patterns 1–19)
- **Schedule / webhook / one-shot**
- **Whether Run is allowed** — default: Detect errors only; do not
  Run client bots or type passwords unless the brief says so
- **Secrets** go in Variables via **My references**, never inline

### Login and credentials (hard rule)

Dennis does all site logins himself (Agent Chrome, cookies, 2FA).

- Never store passwords, cookie JSON, 2FA codes, or session tokens
  in the skill, templates, notes, or committed files.
- Never type credentials into a TaskBot.
- The job brief may say "logged-in site"; the human signs in on
  Agent Chrome before Run.
- Default: build + Detect errors only. Do not Run client bots unless he says.

## Desktop Agent lifecycle
- Installed at `%LOCALAPPDATA%\Programs\ZeroWork\ZeroWork.exe` (Electron tray app, no UI)
- Health check: `curl -s http://localhost:9990` → `{"message":"ZeroWork Agent running","version":...,"port":9990}`. **1.1.75:** if 9990 is taken the Agent falls back to another port — read `port` from the JSON (do not hard-fail on 9990).
- Start if down: launch ZeroWork.exe (background terminal), wait 10–12s, re-curl
- **Chrome must be installed** even if you build/start from another browser — TaskBots run in automated Chrome. Brave **Shields** (and similar blockers) can block Run because the creator talks to the local Agent.
- Runs TaskBots in real Chrome windows; window closes after run unless "Stay on page after run" is enabled
- Agent model (1.1.75): **Guest** (not logged in — manual Run only, no schedule/webhook, blocks same-bot concurrency) / **Default** (exactly one per account; schedule/webhook/concurrency; pauseable from creator.zerowork.io/agents) / **Additional** (purchased + API-key link). Pause-from-browser rejects all runs until unpaused.
- Linux agent exists (.deb/.AppImage/.rpm, download login-gated); VPS installs officially supported. openSUSE is **unsupported**; AppImage → AppImageLauncher; if tray is missing after 30s but localhost answers, install the GNOME appindicator extension. See the Ubuntu install script in this repo's root.

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
key; tables are per-bot (REST create-fresh; attach-existing is 405 — UI **Add an existing table** can still reuse); After Repeat and On-Catch/After-Try all
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
that file; put constants (`tableRefId`, `varRefId`) at the top. Do not
SendInput the buffer when they can paste.

Verified build patterns — native list scrape (CSS `{loop_index}`: `:nth-child` or `>> nth=`), nested-loop pagination, tabs + nested loops (Pattern 9),
scheduled Dynamic scrape + keyword email (Pattern 10), webhook + HTTP work queue + branch rejoin (Pattern 11),
large branched form + webhook possibly inactive (Pattern 12),
LinkedIn outreach DM + daily cap (Pattern 13), Dynamic enrich RUN LIST (Pattern 14),
Facebook group scrape + criteria reply (Pattern 15), Instagram hashtag engage + vision comment (Pattern 16),
two-phase collect then Dynamic enrich with no Run TaskBot (Pattern 17),
Sheets as a table property (Pattern 18), HTTP status-only link check (Pattern 19),
Write-JS table writes, try-catch/condition pipelines, browserless HTTP+ChatGPT chains,
form input/select/upload (the-internet, including number/iframe/checkbox/shadow hard cases), plus
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
   - List scrape → Standard `loop` + `save` with CSS `{loop_index}`
     (`:nth-child({loop_index})` on the repeating sibling, or
     `>> nth={loop_index,1}` / `>> nth={loop_index}` /
     `>> nth={loop_index,0}` — live client confirmation, 0-based). **Prefer regular CSS selectors unless XPath is absolutely necessary.**
     Grids stay CSS — not a reason to switch to XPath. Paginated
     lists → **nested Standard loops** (Pattern 2 / 9). Infinite /
     virtualized feeds → Keyboard PageDown/Space first (Pattern
     7); Keyboard **Space** also forces lazy LinkedIn sections
     (Pattern 14); Keyboard **Enter** sends a Facebook Thread
     composer DM (Pattern 15, no submit button). Write JS only if the virtualizer remounts cards so
     `{loop_index}` cannot hold a stable list. CSS `{loop_index}`
     does **not** fix virtualized X feeds (find-selector in
     [platform-primitives.md](references/platform-primitives.md)).
   - Form fill → Insert Text (selector = the **INPUT**, not the
     label; Pattern 8 `#username` / `#password`; number inputs
     still use Insert Text, `input[type=number]`) + Select Web
     Dropdown (`<select>` selector **AND** the option text;
     Pattern 8 `#dropdown` + `Option 2`) + Upload File (Click the
     file input first; prefer **From file URL**, portable demo
     is the gitignore README). Iframe: Switch Frame (Iframe
     selected, selector `iframe` or `#mce_0_ifr`) then Insert
     Text on `body#tinymce`. Checkboxes:
     Click `#checkboxes input:nth-of-type(1)`. Shadow DOM:
     inspect slotted light DOM vs shadowRoot — on /shadowdom
     `span[slot="my-text"]` is light DOM (plain CSS). Do not
     always Write JS for /shadowdom. If a future run shows no
     text change (span is not an input), Write JS on
     `document.querySelector('my-paragraph').shadowRoot`
     (browser, not Run locally). Practice site:
     the-internet.herokuapp.com (not a client form). Pattern 8.
   - Name every node by role (`Clear previous rows`, `Page down to load
     more`). Add `sticky_note`s for login, selectors, and stop
     conditions — notes are not executed. On client bots sticky notes
     are **load-bearing** (selector history, branch intent).
   - Enrich existing rows → Dynamic `loop` + `open_link` (URL column) + `save`.
     Dynamic extras: optional reverse ("Newest rows first"), start-from
     row, auto-continue from last row, repetition limit. Bind the
     existing table via **My references** — dropdown labels can be
     stale; never paste another bot's table id.
     Two-phase in one bot (no Run TaskBot): truncate → Standard collect
     → After Repeat → Dynamic enrich the same table (Pattern 17).
   - Pagination → outer Standard `loop` (pages) → inner `loop` (items) →
     `continue_after_repeat` off the **inner** opener → `click` Next.
     After Repeat wires DIRECTLY off its Start Repeat, never after
     Save siblings. Loop type MUST be set (Standard vs Dynamic).
     Continue-until-no-element needs a web-element action in the
     body; set a repetition limit on long/endless lists.
     Skip-if-not-found / Try-Catch swallows the end condition —
     then you need auto-scroll or Break.
   - Tabs → Open Link **open in new tab** (stays background) +
     Switch or Close Tab. Prefer **Tab URL matching** (full /
     partial / `/regex/flags`). Partial `/windows` also matches
     `/windows/new` — be specific. Creation order ≠ visual
     order; regular-browser mode cannot guarantee tab number.
     Bring Pages to Front is a **run setting** for watching new
     tabs. Pattern 9. Tab-number switching (Tab **2** then back to
     Tab **1**) exists — still prefer URL match.
   - Optional web element → `check` (Found / Not Found), not a Set Condition.
     Found / Not Found are **no-drawer** outcome marker cards. Branching
     is edge wiring off Check, not a drawer field. Both branches may
     **rejoin** at a later node (not only dead-end). A **dead-end**
     Found/Not Found (no outgoing edge) = skip row. **Inverted check:**
     presence of a waitlist `input[placeholder=Email]` means unavailable.
   - Data tests → `check_dynamic_data` + N `conditionNode` (one operator each, include
     **ELSE** — "if no other condition is met"). Sanitize numbers (`math` Remove format) before `<` `>`.
     Message-cap: EQUALS `{id, name: MessageCount}` → Break Repeat; ELSE continues
     (Pattern 13). Pick refs with **V / My references**.
   - Start Repeat: pick **Standard** or **Dynamic**. Live Pattern 4 had
     loop type **UNSET** (neither selected). Detect errors may stay
     quiet — set Standard before a client build.
   - Go Back or Forward: live playground had **neither** Go back nor
     Go forward selected (dead default footgun). Set one before a
     client build.
   - Switch Frame: live playground had **neither** Iframe nor
     Main page selected (docs say **Main frame**; live drawer
     may say **Main page** — same radio). Dead default, same
     class as Go Back. Choosing Iframe requires the iframe's
     selector (`iframe` or `#mce_0_ifr` on the-internet), not
     just the radio. min/max 0/0. Set one before a client
     build. Pattern 8 hard case: Iframe selected + selector,
     then Insert Text `body#tinymce`.
   - Browser Alert (palette label; search "dialog" — there is no
     Accept/Dismiss Dialog card): optional **Prompt response**
     textarea; min/max 0/0. No explicit Accept vs Dismiss control.
   - Abort Run: **no drawer**, no configurable fields. Do not retry
     select+click.
   - Send Notification: **Subject** + **Email content** + min/max.
     Sends to the signed-in account email — **no To: field**.
     Subject/body from `{id, name}` tokens via **My references**.
     Loop-exit digest (After Repeat → email) is the cheap "run finished"
     signal; the same block is also a per-row alert inside the loop.
   - Upload File: tip "Make sure to initiate the upload by clicking the 'Upload' button in the previous step."
     File source radios **From file URL** / **From folder path on your computer**
     — live default **neither** selected. Detect errors **names the node** if File source is unset. **From folder path on your computer**
     is the Agent machine, not the creator browser. Prefer **From file URL**
     for a portable demo (`https://raw.githubusercontent.com/github/gitignore/main/README.md`).
     A file column/variable can also be referenced via From file URL
     (Upload FAQ). Save File cannot write a file column.
     Click the file input (`#file-upload`) in the
     previous step. min/max.
   - Record Date: **Select date format** dropdown (nothing selected
     live). No min/max. Run stamp: Calendar date, MM/DD/YYYY, **Today**
     → Date Added column (Pattern 17).
   - Save from Clipboard: **Save copied text to** table/variable
     picker. No min/max.
   - Save Page URL: **Save current page URL to** table/variable
     picker. No min/max.
   - Quit Browser: **Force quit** checkbox (unchecked live). No min/max.
   - Recoverable failure → `try` + body; `catch` and `after_try` **both off `try`**.
     Catch is a **dead-end on purpose** in the Pattern 4 proof (no outgoing edge, no drawer).
     After Try-Catch is the continue path (also no drawer). The proof
     is a Log after After Try-Catch, not a catch→log wire.
     Outreach (Pattern 13): Start Try-Catch drawer **"Save error message to"** a
     table column (`Error`); catch may **rejoin** the same Delay as the happy path.
     Start Try-Catch may have at most THREE connections (one body + On Catch +
     After Try-Catch). A Write JS sibling off Try is a fourth wire and fails
     Detect errors: "The Start Try-Catch building block can have up to three
     connections...". Valid JS demo: Wait for timeline → Harvest while scroll
     → Scrape scope (try) → (Scroll rounds | catch | after_try).
   - Browserless API → `update_or_configure_api` → `math` / `format_data` / `regex` →
     `log` / `email` / `ask_chatgpt`. HTTP must **SAVE RESPONSE** or
     the call is a no-op. SAVE RESPONSE has **three independent slots**:
     body / nested record paths / **Save response status code**.
     Filling **only** the status-code slot is intentional (Pattern 19
     link-rot checker) — unlike Pattern 5's accidental no-op (body +
     nested + status **all empty**). Secrets in headers are
     `Bearer {id, name}` variable tokens — never a literal. Live
     Pattern 5 left body / nested path / status **all empty** —
     Detect errors can stay quiet while the API result is discarded.
     Math writes back to `fx_x100` (Multiply × 2.5). Ask ChatGPT
     one-word HIGH or LOW → `gpt_answer`. Pick refs with **V / My
     references**.
   - Custom / npm / Playwright / secrets → `write_js` with `// @zw-run-locally`.
   - Sub-bot (agent ≥ 1.1.75) → `run_taskbot`. **Wait until the TaskBot finishes** CHECKED = sync; uncheck =
     fire-and-forget.
     No min/max delay. Older fire-and-forget → HTTP to webhook.
     **Honest hole:** Run TaskBot, cookies/proxies/Launch Browser, and
     file columns / Upload File / Save File are **absent from this
     client's live bots**. Catalog fields remain; do not invent a
     client recipe. Live substitute = Pattern 17 (two-phase, no
     `run_taskbot`). A variable-only bot can look child-shaped; nothing
     calls it.
   - Grid / feed cards → Standard loop mode **"Count elements matching selector"**
     + **Lead selector** (Pattern 16 `section main a[href*="/p"]`;
     Pattern 17 `a[href*=products]` + Save WE
     `a[href*=products] >> nth={loop_index,0}`). Or Standard
     Fixed N + Auto-scroll ON. **Prefer regular CSS selectors unless XPath is absolutely necessary.**
   - Save WE **Custom attribute** `src` (dialog `img`) feeds a vision HTTP body
     (Pattern 16). Nested SAVE RESPONSE path `choices[0].message.content` — the
     JSON path can become the variable name. Secrets are `Bearer {id, name}`.
   - Destructive nodes (Follow / Post / Send / Delete-all test sub-flow) left
     **deactivated** = production hygiene (Patterns 14, 16). Class `deactive`.
   - Click: **Perform right-click** and **Use human-like clicking**
     (both often OFF). Pattern 4 left-click, human-like off.
   - Insert Text or Data: **Use spintax** is CHECKED by default
     (independent of typing speed). When **Insert instantly** is
     unchecked, the typing-speed slider **PRO → VERY SLOW** is
     human-like. Selector is the **INPUT**, not the label (Pattern 8:
     `#username` / `#password`). Number inputs still use Insert
     Text (`input[type=number]`). Iframe: Switch Frame first
     (selector `iframe` or `#mce_0_ifr`), then Insert Text on
     `body#tinymce`. Shadow: inspect
     slotted light DOM vs shadowRoot (`span[slot="my-text"]`
     is light DOM). Do not always Write JS for /shadowdom.
   - Select Web Dropdown: needs the `<select>` selector **AND** the
     option text (Pattern 8: `#dropdown` + `Option 2`). Custom
     div/button menus are Click + Click, not this block.
   - Raise Error: optional message (live default "A custom error was raised.");
     **Mark this TaskBot run as failed in the run report**
     and **Include this error in the error report** both unchecked live.
3. **Design the data model** ([platform-primitives.md](references/platform-primitives.md)):
   - One-value scratch (counter, flag, cleaned price) → variable on the auto
     Variables table.
   - Many rows → native table (default). Sheets only if a human must share/filter
     outside ZeroWork. CSV import creates a native table.
   - REST: `POST /data_group/` `{name, type:'NATIVE', columns:[{colName}…], connector_id}`.
     Tables are **per-bot**. REST has no attach-existing-table route (405).
     The UI (1.1.75) can **Add an existing table** — do not collapse this
     to "tables can never be reused". Never paste another bot's table id
     into REST create.
   - Overwrite-each-run → `delete_table_data` (all rows) **before** the Standard loop
     (**truncate-then-refill**, Pattern 17). On a Sheets-linked table this
     clears the spreadsheet.
   - Consume a Dynamic queue → `delete_table_data` mode **"Delete current row in a loop"**
     after a successful send (Pattern 13). Blank-row guard: Start Condition
     **NOT_EXISTS** on the URL column → same delete mode.
   - Dedup → `remove_duplicate_rows` **after** the loop (key column; Preserve newest).
   - Driver-table gating → an `isActive` column + Start Condition EQUALS `true`
     (Pattern 15). Enable/disable targets from the table, not the graph.
   - A Sheets-backed table can exist **without a Sheets *block*** — Sheets is a
     **table property** (sidebar Tables → green Sheets icon; kebab: Edit
     Google Sheets link / Remove from this TaskBot / Delete table / About
     this table). Ordinary save / update / delete_table_data write through
     and sync. A bot can mix plain native tables and Sheets-linked tables.
     Loop either like a native table (Pattern 18). Never bake a Sheets URL.
4. **Assemble (REST-first)** ([rest-api.md](references/rest-api.md)):
   - Create bot: `POST /connector/` `{name}` (or `/workflows` → "New TaskBot").
     Names must be **unique** (1.1.61) — a colliding create fails.
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
   need a **linked** agent + awake machine. Scheduler UI: Frequency
   Every day + Interval + unit Hours + N + optional "Delay hour-based
   start by X minutes" + optional time range + Timezone; REMOVE /
   RESCHEDULE; cadence and TZ are per-bot; no catch-up. Webhook UI
   (live-verified): one `https://webhook.zerowork.io/trigger/<token>` URL;
   active/inactive toggle; copy; delete=rotate. A bot can have a
   webhook configured but inactive. No method picker (inbound POST).
   Official docs also allow **GET or POST** plus query-params (same
   case-sensitive variable / JSONPath rules as the body). Multi-agent
   (1.1.74): `https://webhook.zerowork.io/s=<TASKBOT_KEY>&agent=<AGENT_ID>`
   — scheduler cannot target an Agent yet.
   Deactivated nodes stay wired (react-flow class `deactive`) — the
   canvas lies about what runs.
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
style virtualized feed, (v) X/Twitter infinite-scroll feed, (vi) form
input / select / upload plus number / iframe / checkbox / shadow
hard cases, (vii) tabs + nested loops, (viii) scheduled Dynamic
scrape + keyword email, (ix) webhook + HTTP work queue + branch
rejoin, (x) large branched form + webhook (possibly inactive), (xi) LinkedIn outreach DM + daily cap,
(xii) Dynamic enrich RUN LIST, (xiii) Facebook group scrape + criteria reply,
(xiv) Instagram hashtag engage + vision comment,
(xv) two-phase collect then Dynamic enrich (no Run TaskBot),
(xvi) Sheets as a table property, (xvii) HTTP status-only link check live in
[build-patterns.md](references/build-patterns.md) (Patterns 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19).

## Creator editor automation — core loop

The creator is React + MUI + React Flow. Node/edge/table **create** is REST
(preferred). Drawer field writes have no REST (they go over websocket) — use
the loop below. Full selectors, event sequences, and pitfalls: **[references/creator-editor-automation.md]**. Copyable drag helper: **[templates/zw_drag.py]**.

1. **Add block** — synthetic HTML5 drag: palette card (`[draggable=true]`, match by innerText) → `dragstart` with `DataTransfer.setData('application/reactflow', '<type>')` (verified: `open_link`) → drop on `div.invisible-drop`. Each drop auto-opens the new block's config drawer. Palette-drop quirk: drag from the right panel can leave a pending ghost; the next canvas click places the node and opens the drawer.
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
