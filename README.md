# zerowork-utils

Utilities for the [ZeroWork](https://zerowork.io) browser-automation platform:

- **`skills/zerowork-taskbot-automation/`** — a production-tested agent skill for building, configuring, and running ZeroWork TaskBots programmatically (undocumented REST API, all 44 node types, canvas automation, verified build patterns).
- **`ubuntu-chrome-zerowork-installation.sh`** — a one-command installer that sets up an Ubuntu VPS with a full desktop environment, Google Chrome, and the ZeroWork agent.

## ZeroWork TaskBot Automation (agent skill)

An agent skill that lets an AI agent (or serves as reference documentation for a human) automate the ZeroWork platform itself: manage the desktop agent, build TaskBots in the creator at creator.zerowork.io, wire blocks together, trigger runs, and verify results — without manual clicking.

What's covered:

- The undocumented REST API (`taskbot-server.zerowork.io`) — endpoints, auth, node/edge payloads, table and variable creation, and the validator's wiring rules
- All 44 canonical node types and their internal `type` strings (wrong strings render as dead nodes), plus official-docs operational knowledge (purpose, drawer fields, wiring, when-to-use, gotchas)
- Selectors, variables vs tables (native / Google Sheets / CSV), dynamic inputs (`{id,name}`, `${}` / `$${}`, spintax), and the scenario → TaskBot construction procedure
- Write JavaScript `zw.*` API (local vs browser, refs, deviceStorage, state, browserContext, packages)
- Canvas and drawer automation via CDP **and** cua-driver on the paired Chrome (Playwright cannot click Run — mixed-content / no native-host pairing)
- Verified build patterns: native list scraping, nested-loop pagination, try-catch and condition pipelines, Write-JS table writes, browserless HTTP + ChatGPT chains, LinkedIn-style virtualized-feed scrape
- Run semantics: start/end markers, error signatures, agent / schedule / webhook / reports, account snapshot

### Layout

```
skills/zerowork-taskbot-automation/
├── SKILL.md                    # Entry point: safety, agent lifecycle, construction procedure
├── references/
│   ├── rest-api.md             # Undocumented REST API + validator wiring rules
│   ├── node-types.md           # All 44 canonical type strings + official docs URLs
│   ├── block-catalog.md        # Per-node purpose, fields, wiring, when-to-use, gotchas
│   ├── platform-primitives.md  # Selectors, variables, tables, dynamic inputs
│   ├── write-javascript.md     # zw.* API (local vs browser)
│   ├── run-and-platform.md     # Agent, run settings, scheduler, webhooks, reports
│   ├── build-patterns.md       # Verified TaskBot patterns (pagination, try-catch, …)
│   ├── run-semantics.md        # Run markers, error signatures, data writes, audits
│   ├── creator-editor-automation.md  # Canvas/drawer via CDP + paired-Chrome cua-driver
│   └── playwright-recreation-map.md  # Recreating ZeroWork flows in Playwright
├── scripts/
│   ├── zw_helpers.py           # Drop/connect/harvest/run helpers for browser sessions
│   ├── zw_cua.py               # Parse cua-driver UIA trees; find the ~114px card Group
│   └── check_skill_coverage.py # Parses real skill files; asserts every node is documented
├── tests/
│   └── test_skill_coverage_and_helpers.py
└── templates/
    └── zw_drag.py              # Reusable palette-drag template
```

### Installing

Install with the [skills CLI](https://github.com/vercel-labs/skills) (recommended — works with Claude Code, Hermes, Codex, Cursor, Copilot, and 15+ other agents):

```bash
npx skills add dennisrongo/zerowork-utils
```

The CLI lists skills found in the repo and installs into the agents it detects. To install non-interactively:

```bash
npx skills add dennisrongo/zerowork-utils --skill zerowork-taskbot-automation -y
```

Or copy the `skills/zerowork-taskbot-automation/` folder manually into your agent's skill library:

- **Hermes Agent** — your profile's `skills/` directory (e.g. `%LOCALAPPDATA%\hermes\profiles\<profile>\skills\automation\`)
- **Claude Code / other agents** — the project or user skills directory your agent scans (e.g. `.claude/skills/`)

The skill auto-activates on ZeroWork-related requests. If you are reading this on GitHub and have not installed it into an agent, treat **`skills/zerowork-taskbot-automation/SKILL.md`** as the entry point and follow the procedure below. The `references/` files are the depth; you do not need a local agent install to *design* a TaskBot from them.

### Using the skill from this repo (GitHub)

This repo **is** the skill. There is no separate package. Clone or browse:

```
https://github.com/dennisrongo/zerowork-utils/tree/master/skills/zerowork-taskbot-automation
```

1. Read `SKILL.md` first (safety + procedure). **Never assume a logged-in creator.zerowork.io session is yours** — open `/workflows` and confirm the TaskBot list before creating anything.
2. Pick blocks from [`references/block-catalog.md`](skills/zerowork-taskbot-automation/references/block-catalog.md) (canonical `type` strings in [`node-types.md`](skills/zerowork-taskbot-automation/references/node-types.md)).
3. Design data and selectors with [`platform-primitives.md`](skills/zerowork-taskbot-automation/references/platform-primitives.md).
4. Assemble REST-first with [`rest-api.md`](skills/zerowork-taskbot-automation/references/rest-api.md). Drawer writes have no REST (websocket only).
5. Run/verify with [`run-and-platform.md`](skills/zerowork-taskbot-automation/references/run-and-platform.md) and [`run-semantics.md`](skills/zerowork-taskbot-automation/references/run-semantics.md).
6. Copy a verified shape from [`build-patterns.md`](skills/zerowork-taskbot-automation/references/build-patterns.md) when the scenario matches (paginated scrape, try-catch + conditions, browserless HTTP).

To have an AI agent build from this repo without `npx skills add`, point it at that folder and say: follow `SKILL.md`, then the construction procedure.

### Scenario → TaskBot construction procedure

Use only ZeroWork.io nodes documented in this skill. REST-first assembly; drawers for config the API cannot write.

1. **Decompose** the scenario into navigate / interact / decide / repeat / persist / notify / (optional) HTTP or JS. Name the outcome ("N rows in table X", "form submitted or error emailed").
2. **Choose blocks** from the [block catalog](skills/zerowork-taskbot-automation/references/block-catalog.md):
   - Open a URL → `open_link` (add `launch_browser` only if sticky / proxy / bypass / scripts must change first).
   - List scrape → Standard `loop` + `save` with `{loop_index}` (XPath for grids).
   - Enrich existing rows → Dynamic `loop` + `open_link` (URL column) + `save`.
   - Pagination → outer Standard `loop` (pages) → inner `loop` (items) → `continue_after_repeat` off the **inner** opener → `click` Next.
   - Optional web element → `check` (Found / Not Found), not a Set Condition.
   - Data tests → `check_dynamic_data` + N `conditionNode` (one operator each, include **Else**). Sanitize numbers (`math` Remove format) before `<` `>`.
   - Recoverable failure → `try` + body; `catch` and `after_try` **both off `try`**.
   - Browserless API → `update_or_configure_api` → `math` / `format_data` / `regex` → `log` / `email` / `ask_chatgpt`.
   - Custom / npm / Playwright / secrets → `write_js` with `// @zw-run-locally`.
   - Sub-bot (agent ≥ 1.1.75) → `run_taskbot`; older fire-and-forget → HTTP to a webhook.
3. **Data model** ([platform primitives](skills/zerowork-taskbot-automation/references/platform-primitives.md)):
   - One-value scratch (counter, flag, cleaned price) → variable on the auto Variables table.
   - Many rows → native table (default). Google Sheets only if a human must share/filter outside ZeroWork. CSV import creates a native table.
   - REST: `POST /data_group/` `{name, type:'NATIVE', columns:[{colName}…], connector_id}`. Tables are **per-bot** — never reuse another bot's table id.
   - Overwrite each run → `delete_table_data` (all rows) **before** the Standard loop. Dedup → `remove_duplicate_rows` **after**.
4. **Assemble (REST-first)** ([REST API](skills/zerowork-taskbot-automation/references/rest-api.md)):
   - Create the bot: `POST /connector/` `{name}` (or `/workflows` → New TaskBot).
   - `POST /node/` × N with **canonical** `type` strings. Verify the rendered class is `react-flow__node-<type>` (not `node-default` — that is a dead husk).
   - `POST /edge/` full objects (`id: reactflow__edge-<src>a-<tgt>a`). Validator: exactly one starting block; After Repeat off Start Repeat; catch + after_try off try; non-branch nodes one-out.
   - Reload the editor (new columns appear in drawers only after reload).
5. **Configure drawers** — no REST write. On the **paired** Chrome (not Playwright): cua-driver loop in [creator-editor-automation.md](skills/zerowork-taskbot-automation/references/creator-editor-automation.md). Monaco ignores UIA `set_value`. SAVE → "Updated successfully". Auto-align, then connect leftover edges (REST preferred).
6. **Detect errors** — toolbar. The "please wait" toast can linger; Run still starts. Fix every named node id.
7. **Run** — toolbar `aria-label="Run"` on the Chrome profile the Desktop Agent is paired with. A second/Playwright Chrome reports "Agent offline" even when `:9990` answers. No REST run trigger. Scheduler / webhook need a linked agent and an awake machine.
8. **Verify** — `GET /execution/` is not enough (`success` / 0 errors can be a swallowed login throw). Also `item/get_count/` (read `cells[].text`) and Live Runs step text. Creator Chrome login ≠ agent Chrome login. A ~1s "success" on a browser bot usually means the browser phase was skipped. There is no REST create-row.

Hard wiring rules that fail Detect errors if you get them wrong:

- After Repeat and On-Catch / After-Try wire **directly off their opener**, never after the last body block.
- Set Condition has **one** output. Multi-branch = several Set Condition blocks off one Start Condition.
- Start Repeat may have multiple outgoing edges; almost every other block may not.

### Coverage check

From the repo root:

```bash
python skills/zerowork-taskbot-automation/scripts/check_skill_coverage.py
python -m unittest skills/zerowork-taskbot-automation/tests/test_skill_coverage_and_helpers.py -v
```

This parses the real skill markdown and asserts every palette `type` and official building-block URL has purpose, config, wiring, when-to-use, and gotchas.

## Install ZeroWork on Ubuntu (VPS)

This guide provides step-by-step instructions on how to execute the ZeroWork installation script on your Ubuntu VPS. This automated script will set up a complete desktop environment with Google Chrome and ZeroWork.

### Video Demonstration

For a visual walkthrough of this installation process, check out this [YouTube demonstration video](https://youtu.be/_uhx_y_ZvGM) which shows the entire process in action.

### Credit

This installation script is adapted from the original work by [DEPINspirationHUB](https://github.com/depinspirationhub/ubuntu-desktop/blob/main/ubuntu-desktop.sh). I've modified it specifically for ZeroWork installation while maintaining the core functionality.

### Running the Installation Script

#### The Installation Command

Copy and paste the following command into your SSH terminal:

```bash
wget https://raw.githubusercontent.com/dennisrongo/zerowork-utils/refs/heads/master/ubuntu-chrome-zerowork-installation.sh && chmod +x ubuntu-chrome-zerowork-installation.sh && ./ubuntu-chrome-zerowork-installation.sh 1.1.66
```

#### Understanding the Command

This command performs three actions in sequence:

1. `wget https://raw.githubusercontent.com/dennisrongo/zerowork-utils/refs/heads/master/ubuntu-chrome-zerowork-installation.sh`
   - Downloads the installation script from the GitHub repository

2. `chmod +x ubuntu-chrome-zerowork-installation.sh`
   - Makes the downloaded script executable (grants permission to run the script)

3. `./ubuntu-chrome-zerowork-installation.sh 1.1.66`
   - Executes the script with version 1.1.66 of ZeroWork as a parameter
   - You can replace "1.1.66" with a different version number if needed

### Installation Process Walkthrough

#### 1. Disclaimer Acknowledgment

After running the command:

- A disclaimer will appear, explaining potential risks
- Type `y` and press Enter to agree and continue
- If you type anything else, the installation will abort

#### 2. System Updates

- The script will update your system packages
- You'll see package lists being refreshed and upgrades being applied
- This may take several minutes depending on your system

#### 3. Desktop Environment Installation

- XFCE desktop environment will be installed
- You'll see progress as packages are downloaded and configured

#### 4. Remote Desktop Configuration

- XRDP (Remote Desktop Protocol) service is installed and configured
- The firewall is updated to allow RDP connections on port 3389

#### 5. User Account Setup

- You'll be prompted to enter a new username for RDP login
- Type your desired username and press Enter
- You'll then be asked to create and confirm a password
  - The password won't be visible as you type (for security)
  - You must enter the same password twice

#### 6. Application Installation

- Google Chrome will be downloaded and installed
- GDebi package manager will be installed for handling .deb files
- ZeroWork version 1.1.66 (or your specified version) will be downloaded and installed

#### 7. Completion

- The script will display a completion message with connection details
- You'll be asked if you want to delete the installation script
  - Type `y` to remove it (recommended for security)
  - Type `n` to keep it

### Connecting to Your Desktop

After successful installation:

1. Use any RDP client software on your local computer
   - Windows: Built-in Remote Desktop Connection
   - Mac: Microsoft Remote Desktop from the App Store
   - Linux: Remmina or similar RDP client

2. Enter your VPS IP address as the connection address

3. When prompted, enter the username and password you created during installation

4. You should now see the XFCE desktop with Google Chrome and ZeroWork installed

### Troubleshooting Tips

- If connection fails, ensure port 3389 is open on your VPS firewall
- If login fails, double-check the username and password you created
- For VPS performance issues, ensure your server has at least 2GB of RAM

### Next Steps

Once connected to your desktop environment:

1. Launch Google Chrome from the Applications menu
2. Open ZeroWork from the Applications menu to begin using the software

The installation process is now complete, and your Ubuntu system is ready with ZeroWork installed.
