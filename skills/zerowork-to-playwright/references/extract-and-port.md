# Extract a TaskBot and port it to Playwright

Read-only on the live canvas. Do not click Run, Log out, Auto-align, or SAVE any drawer.

Sibling block → Playwright table and Path A / Path B (do not copy the table here):

[../../zerowork-taskbot-automation/references/playwright-recreation-map.md](../../zerowork-taskbot-automation/references/playwright-recreation-map.md)

This file is the Playwright-side extract + write procedure only.

## Canvas extract

1. **Confirm the session.** Open `https://creator.zerowork.io/workflows`. The list must be Dennis's bots. If names look wrong, stop — he logs in himself. Never type credentials. Never click Log out unless he asks.
2. **Resolve the handle.**
   - URL `https://creator.zerowork.io/workflows/<id>` is already a handle — open it.
   - Name only → use the list search, then open the matching card.
3. **Fit-view first.** React Flow control `aria-label="fit view"` so culled nodes re-enter the DOM. Nodes far from origin (x≈-400) drop out of the DOM; `querySelector` returns null until they are in view. Fit-view shrinks cards — zoom back in until a card is ~100px+ before clicking.
4. **Node search.** Bottom-left input: "Search by ID, name or type". Search-by-ID **selects** the node (shows `ID <n>`) and does **not** open the drawer. That is expected.
5. **Walk the graph top-to-bottom.** For each node record:
   - canvas id, display name, type (`react-flow__node-<type>` — skip `node-default` husks)
   - outgoing edges and their kind: body / After Repeat / Found / Not Found / Else / On Catch / After Try
   - table **names**, column **names**, and variable **names** exactly as on the live bot (data parity — never invent or drop columns; never numeric ref ids from the live bot)
   - load-bearing sticky notes (port as comments at the matching Playwright step)
6. **Drawer fields (read-only — never SAVE, never edit scheduler/webhook).**
   - Open: select-click, then a **second click on the card body**. First click often only shows `ID <n>` (selected, drawer still closed).
   - Catch / After-Try / Break / After-Repeat / Found / Not Found / Abort Run: no drawer — do not retry.
   - Copy: CSS selectors, URLs, loop type (Standard vs Dynamic), HTTP method + nested paths, Write JS **full source**, condition operators, notification subject/body tokens (redact).
   - Unobserved drawer (could not open, or field empty): do not invent CSS or JS. The port throws `needSelector(nodeName)` / `needWriteJs(nodeName)`. Then go back and extract; do not ship TODOs as "done".
7. **Redact before anything is written to disk.** Strip passwords, cookie JSON, 2FA, session tokens, Bearer literals, webhook tokens, and account emails. Replace live numeric workflow / table / variable ids with placeholder names (`TABLE`, `varRefId` pointing at local files). Do not commit secrets.
8. **Stale canvas bugs stay on the canvas.** If the live TaskBot has a bug (hard-coded test URL, wrong tableRefId, dead selector), do NOT edit the ZeroWork bot. Fix only in the Playwright port so the requirement is fulfilled. Comment the original bug next to the fix.

## Locator translation

CSS-first, same as the sibling skill. Convert ZeroWork loop indexes to Playwright locators — do not keep `{loop_index}` in the port.

| ZeroWork selector | Playwright |
|---|---|
| `>> nth={loop_index,0}` | `locator(css).nth(i)` (0-based) |
| `>> nth={loop_index}` | `locator(css).nth(i)` (0-based) |
| `>> nth={loop_index,1}` | `locator(css).nth(i)` — treat as 0-based unless the live bot clearly used a 1-based offset; document the choice in the port README |
| `:nth-child({loop_index})` | CSS `:nth-child` is 1-based (`i + 1`), or `parent.locator(child).nth(i)` |
| `{loop_index}` in any other CSS | same: `nth(i)` or 1-based `:nth-child` |

XPath only if the live bot already used XPath and CSS cannot hold the list.

**Verify live, then fix in the port.** After extract, hit the public page (or the page he already authenticated) and confirm CSS still matches. If the site changed, update Playwright locators only — do not edit the live TaskBot.

## Playwright-side procedure

Default is **Path A** from the map: one TypeScript file per TaskBot. **Path B** (YAML DSL + interpreter) only if Dennis asks.

### Output layout

Ask him where to write. Default: a folder he names, or `playwright-ports/<safe-slug>/` (gitignored / generated — only keep it in this repo if he asks). Each port gets:

```
playwright-ports/<slug>/
  playwright.config.ts   # Chromium, viewport 1440×900
  src/<slug>.ts          # or a spec — graph top-to-bottom
  data/
    vars.json            # object — one key per ZeroWork variable name
    <table-slug>.json    # array of row objects — ZeroWork column names as keys
  README.md              # how to run + exact auth path
  .gitignore             # auth/ and .env
  auth/                  # empty; he drops storageState here
```

**Data parity.** Local storage must match the live TaskBot tables/columns/variable names exactly. Default is those JSON files — not SQLite unless he asks. `getRef` / `setRef` analogs read/write them. Do not invent extra columns. Do not drop columns the bot writes.

**Google Sheets (Dennis 2026-08-17).** Never open, edit, or reuse a live TaskBot's existing Google Sheet. When a port needs Sheets, create a **new** Google Sheet on Dennis's account. Do not change the live TaskBot's Sheets link. Local JSON in `data/` remains the runtime store; the new Sheet is an optional export/sync he owns.

Do not bake live workflow/table ids as required handles. `config.ts` / `.env.example` may have `TABLE` **names** and public URLs.

### Auth (server-like run)

The script must be runnable the same way ZeroWork's agent would: **Chromium**, viewport **1440×900** (ZeroWork default), existing cookies via `storageState` or `launchPersistentContext` on a profile **Dennis** created.

**Dennis does all site logins.** Never type credentials. Never write cookie JSON into the repo. Document the exact auth path in the port README (`auth/storageState.json`, or the user-data-dir he created). Gitignore `auth/` and `.env`.

### How to write each node

Use the sibling map for the block → API table. This skill only adds how to *write* the port:

- **Open Link** → `page.goto(url)`.
- **Write JS** → a named function. Keep `tableRefId` / `varRefId` (and `indexRefId` if present) as constants at the top; point them at `data/vars.json` / `data/<table-slug>.json`, not ZeroWork numeric ids. The `zw.*` API is gone — replace `zw.setRef` / `zw.getRef` with the local file analogs. Unobserved Write JS → `needWriteJs(nodeName)` (never invent JS).
- **Standard loop** → `for (let i = 0; i < n; i++)` or `while ((await locator.count()) > 0)`.
- **Dynamic loop** → `for (const row of tableRows)` from `data/<table-slug>.json`.
- **After Repeat** → statements after the loop (not inside).
- **Break Repeat** → `break`.
- **Nested loops** → nested `for` / `while`.
- **Message-cap** → increment a counter; `if (count >= cap) break`.
- **Tabs** → `context.pages()`; prefer matching `page.url()` (full / includes / regex). Creation order ≠ visual order.
- **Switch Frame** → `page.frameLocator(selector)`.
- **HTTP** → `APIRequestContext` (`request.get` / `post` / …). SAVE RESPONSE nested paths = lodash-style `get(body, "choices[0].message.content")`. Status-only = `response.status()`.
- **Start / Set Condition** → `if` / `else if`. ELSE Set Condition = `else`. Contains keywords = split the needle on commas, then `haystack.includes(part.trim())`.
- **Check WE Found / Not Found** → `if (await locator.count())` / `else`.
- **Try-Catch / After Try** → `try { ... } catch { ... }` then the after-try statements.
- **Send Notification** → `console.log` or a webhook POST **placeholder**. Do not email his account from the script.
- **Ask ChatGPT** → one `fetch` to an env-configured endpoint; never hardcode keys.
- **Delay** → mirror min/max with jitter only when the live bot used a delay. Prefer Playwright auto-waits over a blanket timeout.
- **Scheduler / webhook** → do not invent infra. Document cron / `node-cron` / a tiny HTTP server stub in the port README.
- **Run TaskBot** → `import` / function call of another port module.
- **Spintax** `{Hi|Hey}` → a small resolver.
- **Sticky notes** → comments at the matching step (load-bearing notes only).
- **Unobserved selector** → `needSelector(nodeName)` — never invent CSS. Then go back and extract.

### Verify

- **E2E required.** A port is not done until `npx playwright test` runs on a **public** target, or Dennis explicitly allows a logged-in run. Write-only extracts are a midpoint, not delivery.
- After extract, confirm CSS on the public (or he-authed) page. Site changed → update Playwright locators only.
- Never click Run on the live ZeroWork client bot.
- Never hit production outreach (LinkedIn / Facebook / Instagram DMs) unless he explicitly says to run the Playwright port.

### Port README must say

- How to install and run (`npx playwright install`, then `npx playwright test`).
- Exact auth path (persistent context user-data-dir, or `storageState` file he drops in `auth/`).
- Chromium + viewport 1440×900.
- What was not ported (scheduler, email-to-account-owner, ZeroWork anti-detect / regular-browser mode — the five gaps on the map).
