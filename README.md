# zerowork-utils

Utilities for the [ZeroWork](https://zerowork.io) browser-automation platform:

- **`skills/zerowork-taskbot-automation/`** — a production-tested agent skill for building, configuring, and running ZeroWork TaskBots programmatically (undocumented REST API, all 44 node types, canvas automation, verified build patterns).
- **`ubuntu-chrome-zerowork-installation.sh`** — a one-command installer that sets up an Ubuntu VPS with a full desktop environment, Google Chrome, and the ZeroWork agent.

## ZeroWork TaskBot Automation (agent skill)

An agent skill that lets an AI agent (or serves as reference documentation for a human) automate the ZeroWork platform itself: manage the desktop agent, build TaskBots in the creator at creator.zerowork.io, wire blocks together, trigger runs, and verify results — without manual clicking.

What's covered:

- The undocumented REST API (`taskbot-server.zerowork.io`) — endpoints, auth, node/edge payloads, table and variable creation, and the validator's wiring rules
- All 44 canonical node types and their internal `type` strings (wrong strings render as dead nodes)
- Canvas and drawer automation via CDP — palette drags, edge connections, MUI/React/Monaco field gotchas
- Verified build patterns: native list scraping, nested-loop pagination, try-catch and condition pipelines, Write-JS table writes, browserless HTTP + ChatGPT chains
- Run semantics: start/end markers, error signatures, variable-vs-table writes, estate audits

### Layout

```
skills/zerowork-taskbot-automation/
├── SKILL.md                    # Entry point: safety checks, agent lifecycle, build paths
├── references/
│   ├── rest-api.md             # Undocumented REST API + validator wiring rules
│   ├── node-types.md           # All 44 canonical node type strings
│   ├── block-catalog.md        # Per-block drawer fields and MUI traps
│   ├── build-patterns.md       # Verified TaskBot patterns (pagination, try-catch, …)
│   ├── run-semantics.md        # Run markers, error signatures, data writes, audits
│   ├── creator-editor-automation.md  # Canvas/drawer automation via CDP
│   └── playwright-recreation-map.md  # Recreating ZeroWork flows in Playwright
├── scripts/
│   └── zw_helpers.py           # Drop/connect/harvest/run helpers for browser sessions
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

The skill auto-activates on ZeroWork-related requests; see its `SKILL.md` for triggers and safety rules (including account-verification steps before touching a logged-in session).

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
