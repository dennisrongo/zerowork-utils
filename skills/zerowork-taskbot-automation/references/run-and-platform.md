# Run, agent, schedule, webhooks, reports, common problems

Official hub: https://docs.zerowork.io/using-zerowork/general-run-schedule-share-webhooks.md
Verified REST / duration facts: [run-semantics.md](run-semantics.md), [rest-api.md](rest-api.md).

This file is how ZeroWork the product **runs** a TaskBot. It does not replace
the REST executor facts; it adds the official product knobs you must choose
when assembling a bot.

## Desktop Agent

Official: https://docs.zerowork.io/install-the-agent.md

- Windows install: `%LOCALAPPDATA%\Programs\ZeroWork\ZeroWork.exe` (Electron
  tray app). Health: `curl http://localhost:9990` →
  `{"message":"ZeroWork Agent running","version":…,"port":9990}`.
  **1.1.75:** if 9990 is taken the Agent falls back to another port —
  read `port` from the JSON.
- If down: launch ZeroWork.exe, wait 10–12s, re-curl.
- **Chrome must be installed** even if you build/start from another
  browser. Brave **Shields** (and similar blockers) can block Run
  because the creator talks to the local Agent. VPN / firewall /
  antivirus can also block start.
- Linux: `.deb` / `.AppImage` / `.rpm` (download is login-gated). VPS
  installs are officially supported. **openSUSE is unsupported.**
  AppImage → install AppImageLauncher. If no tray icon after 30s but
  localhost answers, install the GNOME **appindicator** extension.
  Prove install with Open Link to wikipedia.
- The agent drives **real Chrome**. The window closes after a run unless
  **Stay on page after run** is on (or a Launch Browser block set it).
- Agent model (1.1.75): **Guest** (not logged in — manual Run only; no
  schedule/webhook; blocks same-bot concurrency) / **Default** (exactly
  one per account; schedule/webhook/concurrency; listed and
  **pauseable** at creator.zerowork.io/agents) / **Additional**
  (purchased + API-key link; same schedule/webhook/concurrency).
  Pause-from-browser rejects all runs until unpaused.

### Two Chromes (do not confuse them)

| | **Creator Chrome** | **Agent Chrome** |
|---|---|---|
| What it is | The window on `creator.zerowork.io` where you build and click **Run** | The window the Desktop Agent launches to execute browser blocks |
| Pairing | Must be the profile the agent native-host is paired with | A **separate** profile / cookie jar |
| LinkedIn (or any) login | Irrelevant to the scrape | This is the session Open Link / Write JS see |

A logged-in site tab in Creator Chrome does **not** log Agent Chrome in.
Symptom: run `success` / `errors_count: 0`, Live Runs shows the login-throw
message, table `get_count` is 0 (or only whatever survived Delete Data).

**Cookie transfer from Creator Chrome → Launch Browser JSON** was tried and
failed as an unattended path: Chrome's Cookies SQLite is exclusively locked
while Chrome is running (`CreateFile` with `FILE_SHARE_READ` still
`ERROR_SHARING_VIOLATION`; `esentutl /y` same). Extension popups
(EditThisCookie and similar) often have **no UIA tree**. Do not burn a
cycle on DB copy. Working options: a human Cookie-Editor export pasted
into Launch Browser / TaskBot Settings, or a **sticky** profile signed in
once inside the agent window (Stay on page helps that first session).
Never type site credentials. Never commit cookie JSON.

### Log in to the Agent

Required once before Scheduler or Webhook will fire on that machine.
Logging in on machine A and **not** on machine B is the official way to keep
scheduled/webhook jobs on a dedicated box while you still click Run on a
laptop.

Restart the agent after you schedule/reschedule from a *different* machine —
the desktop app is not pushed from the cloud; it pulls its job list on
start, or when the scheduling UI on that same frontend session tells it to.

### Update

Check/update from the agent menu. Outdated agents are a common
"TaskBot does not start" and "try-catch didn't catch the start failure"
cause.

## How a run starts

Four triggers, same executor:

| Trigger | Needs linked agent? | Notes |
|---|---|---|
| Toolbar **Run** / list Play | No | UI only. No REST `/execution/run/` (404). |
| Scheduler | Yes + machine awake | Skipped if agent off. If already running and Concurrent Runs **off**, new fire is skipped. |
| Webhook GET/POST | Yes + machine awake | Anyone with the URL can fire it. Rotate by delete+regenerate. |
| Run TaskBot block (`run_taskbot`, agent ≥ 1.1.75) | Same as parent | Optional wait; no recursive A→B→A. |

Verify after any trigger via `GET /execution/?page=1`
(`result`, `errors_count`, `run_duration`, `connector_name`) plus table
side-effects. The `?connector=` filter is ignored — match client-side.

Stop: toolbar Stop. Stopping a parent also stops children started with
**Wait until the TaskBot finishes**.

## Browser Launch Settings / Run Settings

Gear icon on the TaskBot. Launch Browser blocks can override these mid-run
(those overrides become the new runtime defaults).

### Run in background

Hides the Chrome window. Use it only after the bot is reliable. Background
viewport falls back to **1280×720** when Window size is unset (Launch
Browser page). Official Write-JS / launch `contextOptions.viewport`
default is **1440×900** — do not treat 1280×720 as the documented
platform default. Do **not**
combine with Stay-on-page — leaves an invisible browser eating RAM; sticky
profiles can drop after machine sleep until the agent is restarted.

### Stay on page after run

Keeps Chrome open for manual inspection. Off by default (saves resources).
An explicit **Quit Browser** overrides this and closes anyway.
**1.1.61:** Stay-on-page now applies to **scheduled and webhook** runs
too (previously ignored). An unintentionally enabled setting leaves an
invisible idle Chrome after those fires.

### Bring pages to front

When on, new tabs come to the foreground (useful while watching a build).
When off, Open-Link-in-new-tab / Switch Tab work silently in the background
(this is also Open Link's default new-tab behavior). macOS may still raise
Chrome once at launch.

### Concurrent runs (agent ≥ 1.1.75)

Off by default. When on, the **same** TaskBot can have overlapping runs
(manual + webhook + schedule). Different TaskBots have always been able to
run in parallel.

Shared across overlapping runs: **persisted** variables (last write wins —
turn off **Persist value** per variable to isolate), native tables, Sheets,
`zw.deviceStorage`. Hardware is the only cap.

**Behavior change:** before 1.1.75 a scheduled fire was skipped if the bot
was already running. With Concurrent Runs **on**, the schedule overlaps.
If a bot can outlive its interval it will now stack on itself.

Guest Agent: a second manual run is rejected; scheduled/webhook never fire.

A green "**N running**" badge lists each in-flight run with its own Stop.

### Cookies

Paste Cookie-Editor JSON (each cookie needs at least `name`, `value`,
`domain`) into TaskBot Settings or a Launch Browser block. Logging out of
the source site, or letting the cookie expire, silently invalidates the
session — re-export. Some sites reject cookie replay: build an Insert+Click
login (encrypt the password field) or use a **sticky** profile instead.

### Proxies

`host:port` (required colon). SOCKS5: `socks5://host:port`. HTTP auth
username/password; SOCKS5 has no user/pass in the official UI. Bypass
domains: comma-separated. A Launch Browser block can override per-run.
Timezone can be auto-aligned to the proxy (1.1.75); disable with
`zw.temp.disableExtraTimezoneBypass()` if it misbehaves.

### Sticky vs incognito

- **Incognito** — isolated; nothing persists across runs.
- **Sticky** — named profile id; cookies/storage/login survive. Multiple
  TaskBots with the same profile id **share one browser** (parallel tabs).
  Launch Browser **attaches** if that profile is already up; browser-level
  settings (background, bypass, size, engine, args) are then ignored.
  Cookies / scripts / page-visibility still apply.
- Create sticky profiles in Browser Launch Settings; Launch Browser can
  pick one via **COPY PROFILE ID**.

### Bypass bot detection

Makes the session harder to fingerprint. Side effects: Window size, Launch
arguments, and Browser engine are **ignored**; file **uploads ≳ 50 MB are
blocked** (downloads are fine). 1.1.75 added extra bypass; revert for one
run with `zw.temp.disableExtraBypass()` /
`zw.temp.disableExtraHeadlessBypass()`.

## Scheduler

Click the scheduler icon (Manage scheduler → **Schedule** modal).

Live UI shape (read-only facts):

- **Frequency / Select how often:** e.g. **Every day**
- **Select when:** **Interval** + unit (**Hours**) + interval **N**
- optional **"Delay hour-based start by X minutes"**
- optional **"Run within a time range"**
- **Timezone** (IANA, e.g. `Europe/Berlin` / `America/Los_Angeles`)
- Buttons: **REMOVE** / **RESCHEDULE**

Cadence and timezone are **per-bot** — sibling bots can differ. First
use: log in to the agent. Machine must be on and not asleep or the
fire is **skipped** (**no catch-up**). Two machines: log the scheduler
in only on the dedicated box. Linked agent + machine awake.

## Webhooks

Header **Webhook** icon → Webhook modal.

**Official** (trigger-run-via-webhook.md): the webhook can be triggered
with a **POST or GET**. Query parameters are supported on both (same
case-sensitive variable / JSONPath rules as the body).

**Live UI** (keep — official page does not show this URL): **no method
picker** (inbound **POST**).

Live UI shape:

- Toggle **Webhook is active** / **Webhook is inactive**. A bot can
  **HAVE** a webhook configured but **inactive**.
- One URL: `https://webhook.zerowork.io/trigger/<token>`
- Copy icon. Red delete icon = **rotate** (new token).
- No method picker.

**Multi-agent targeting (1.1.74):**
`https://webhook.zerowork.io/s=<TASKBOT_KEY>&agent=<AGENT_ID>`
(Agent ID from the Agents list). Scheduler **cannot** target an Agent
yet — webhook only. Keep documenting the live `trigger/<token>` URL.

- Full body is stored (stringified JSON) in auto-variable **`zw_webhook_data`**.
  Parse with `JSON.parse` in Write JS.
- Top-level JSON keys matching variable names (case-sensitive) are copied
  into those variables. Nested: name the variable as a JSONPath
  (`city.name`, `cities[*].city`, `cities[?(@.population>5000000)]`). `$`
  prefix optional. Invalid path / no match = silent skip, not an error.
- From another bot: Send HTTP Request to the webhook URL.
- Deactivate with the toggle; rotate by deleting and regenerating.
  Linked agent + machine awake.

## Sharing

Sharing is a **full copy**, not a view/run ACL. Two official options:
share to an email, or generate a live link. A full copy of the TaskBot
(parameters, variables, tables) is added to the receiver's account.
Native rows are **empty**; variables are **empty**. Google Sheet tables
still contain **your Sheet URL**. Cookies / proxy / scheduler / other
run settings are **never** shared. The link always reflects the current
bot; reset rotates it.

Duplicating a bot in the same account also duplicates its **table id**
but a Google Sheet URL is **shared** (both bots write the same Sheet)
until you Edit link.

## Remote / cloud execution

Official page exists; as of the 2026-08-17 fetch it is still a short
**Upcoming** stub (pay-per-cloud-credit teaser). Do not assume a public
cloud runner. The verified path is still: local/VPS desktop agent + UI /
schedule / webhook.

## Run reports and notifications

Official: https://docs.zerowork.io/using-zerowork/using-run-reports.md

- Reports = per-step timestamps, status, duration. **View Logs** + Side View
  next to the canvas; **View Building Block** zooms the node.
- Write JS `console.log` is **not** persisted in reports. Persist via
  `zw.log` / Log block / table write / Send Notification.
- Notifications (email, Slack incoming webhook, custom POST webhook) always
  include error reports. Run-notification emails: **max 10** addresses
  (1.1.61). Error-report screenshots retained **14 days** (1.1.61).
  Custom payload fields:
  `run_status` (`success|fail|warning|unknown|manually_stopped`),
  `run_type` (`webhook|scheduled|immediate`), `run_errors[]` with
  `error_message`, `screenshot`, `building_block.{id,name,type}`.
- Thrown JS errors land in Error Reports and can be caught by Try-Catch.

## Common problems that change how you BUILD

Official hub: https://docs.zerowork.io/using-zerowork/common-problems.md

| Symptom | Build implication |
|---|---|
| TaskBot does not start | Agent down/outdated; more than one starting block; Detect-errors failures; invalid Sheet; Guest Agent + schedule/webhook |
| Table ref pulls no data | You used a Standard loop (ignores existing rows) or the ref is outside a Dynamic loop / not on the current row. Open Link "no url" is this. |
| Website flashing / glitching | Official: the TaskBot cannot find a selector. Live-verified extra: **Bring pages to front** + rapid nav, or a site fighting automation. Fix the selector first; then slow down (Delay), run in background, or Bypass. |
| No selector found | Selector not unique / increment missing `{loop_index}` / element in iframe (Switch Frame) / not yet in DOM (Check + timeout, or Delay). Prove with `querySelectorAll`. |
| Saves some rows, not all | Last-page render race (add Delay after Click Next); list not scrolled (auto-scroll failed → Keyboard PageDown / space); skip-if-not-found swallowed misses. |
| Data in wrong format | Sanitize with Format Data / Regex / Number Operations **Remove format** before numeric conditions. |
| Site wants SMS / email verify | Official path: **Check** for the verify popup → long **Delay** so a human can complete it in a **visible** Agent window (not Run in Background). If background: abort + Send Notification. After a manual verify, cookies or sticky persist the session. Do not automate the SMS. |
| Keyboard action does nothing | Focus the field first (Click or Insert). Some sites eat keys; try Insert Text. See Keyboard Action. |
| Check says Found, next block misses | Race: the element flickered or a overlay. Add Delay / wait, or re-Check immediately before the action. Check timeout ≠ later block timeout. |
| Insert Text drops first letters | Site wasn't ready; Click the field first, or slow the typing speed, or add a short Delay. |
| More than one starting block | Orphan node (deleted upstream). Delete or reconnect. After Repeat / Catch wired off the body instead of the opener also produces structure errors. |
| Does not auto-scroll | Standard "continue until no element" + auto-scroll can fail on custom virtual lists. Keyboard ArrowDown / Space, or Click a "Load more". |
| Run success / 0 errors but table empty | Try-Catch swallowed a login or 0-card throw; or Remove Duplicates keyed on an empty column. Check Live Runs + `item/get_count/`. Creator Chrome login does not count. |

Start-failure (agent / invalid setup) is **not** catchable by Try-Catch even
if you wrap the whole canvas.

## Release-note behavior that changes building (1.1.61–1.1.75)

Scanned 2026-08-17. 1.1.61–1.1.74 are **not** "mostly reliability" —
several lines change how you build:

- **1.1.61** — Unique TaskBot names (colliding create fails). Auto-scroll
  default ON except Dynamic. Stay-on-page applies to scheduled/webhook.
  Caps: selector later 50k (1.1.62); spintax 5k; log 5k/run; 10
  notification emails; error screenshots 14 days.
- **1.1.69** — HTTP full-object save; Sheets real-time sync Additional
  option; Remove Duplicates can run every Sheets-loop iteration (native
  still once).
- **1.1.72** — Code in inputs (`${}` / `$${}`). Upload File **390 MB**
  hard cap. Random **whole number** checkbox. `zw.*` API surface
  (imports, deviceStorage, state, browserContext) documented as current.
- **1.1.74** — Multi-agent webhook `…/s=<TASKBOT_KEY>&agent=<AGENT_ID>`;
  scheduler cannot target an Agent.
- **1.1.75** — Run TaskBot block; Concurrent Runs; Guest / Default /
  Additional Agent + pause-from-browser; Agent port fallback; Launch
  Browser Custom profile field accepts refs; `zw.getAgentInfo()` **async
  in browser** (official metadata.md is **stale** — still says sync
  everywhere); default Insert Text typing slower (Robotic 0-delay or
  Insert instantly). Revert knobs: `@zw-revert` (old `zw.*` in **browser**
  execution only), `zw.temp.disableExtraBypass()`,
  `zw.temp.disableExtraHeadlessBypass()`,
  `zw.temp.disableExtraTimezoneBypass()` (per run).
- Launch Browser / Quit Browser / sticky profiles appear as first-class
  palette blocks (they are **not** listed on the building-blocks hub).
- Official **scheduler.md** FAQ "skip if already running" is **stale**
  when Concurrent Runs is on (1.1.75) — do not copy it blindly.
- Official stubs (prefer live drawer + this skill): Raise Error
  (Upcoming), Auto-scroll page (Upcoming), Remote/cloud (Upcoming),
  thin Check / Click / Go Back / Save Page URL / Abort / Take Screenshot
  pages. Official metadata.md is stale vs 1.1.75 as noted above.

They do not remove any palette type. Prefer the live drawer + this skill
over a guessed historical type string.
