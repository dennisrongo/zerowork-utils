# ZeroWork Workflow → Playwright Recreation Map

Research from Aug 15, 2026 (docs.zerowork.io). Use when you want a self-hosted Playwright version of a ZeroWork workflow — relevant for cost avoidance and as a product seed (a self-hosted ZeroWork-style runner is a viable product).

## What ZeroWork is
- Browser-based creator (drag-drop vertical blocks) + local desktop agent (Electron, port 9990) executing blocks in real Chromium on the user's PC.
- Data layer: Native Tables or Google Sheets; loops iterate table rows; selectors = CSS + XPath with text/hierarchy filters.
- Run governance: scheduler, webhooks, concurrent-run limits, per-run/hour/day action caps, random delays, spintax, fingerprint obfuscation, proxies, cookies per run.

## Full docs index
https://docs.zerowork.io/llms.txt — every page available as markdown by appending `.md`. Building blocks reference: /using-zerowork/using-building-blocks.

## Block → Playwright mapping (~90% direct)
| ZeroWork block | Playwright |
|---|---|
| Open Link | `page.goto()` |
| Save Page URL | `page.url()` |
| Switch or Close Tab | `context.pages()` + `bringToFront()` / `close()` |
| Go Back or Forward | `goBack()` / `goForward()` |
| Launch / Quit Browser | `chromium.launch()` / `browser.close()` |
| Switch Frame | `frameLocator()` |
| Browser Alert | `page.on('dialog')` |
| Click Web Element | `locator.click()` |
| Check Web Element | `locator.count()` / `isVisible()` |
| Save Web Element (+ Save Lists, Enrich) | `locator.textContent()` / `locator.all()` loop |
| Insert Text or Data | `fill()` / `pressSequentially()` |
| Hover Web Element | `hover()` |
| Select Web Dropdown | `selectOption()` |
| Keyboard Action | `page.keyboard` |
| Start/Set Condition (=, ≠, <, ≤, >, ≥, contains, date before/after) | plain `if` expressions |
| Start Repeat (standard/dynamic loop, auto-scroll, pagination, auto-continue) | `for`/`while`; dynamic loop = table rows; auto-continue = persisted cursor |
| Break Repeat / Try-Catch / Raise Error / Abort Run | native language features |
| Run TaskBot | function call / module |
| Update Data, Number Ops, Format, Split, Apply Regex, Remove Duplicates, Delete | stdlib one-liners |
| Tables | CSV/JSON or Sheets API |
| Ask ChatGPT | one `fetch` |
| Send Notification | Telegram/webhook post |
| Send HTTP Request | `request` / `fetch` |
| Write JavaScript | disappears — you're already in JS |
| Delay (randomized min/max) | `waitForTimeout()` + jitter |
| Take Screenshot | `page.screenshot()` |
| Spintax `{Hi\|Hey}` | ~10-line resolver function |

## The 5 real gaps (and fixes)
1. **Anti-detection** — vanilla Playwright is fingerprintable (CDP, `navigator.webdriver`). Fix: patchright, playwright-extra + stealth, or camoufox (hardened Firefox). Needs ongoing attention; this is ZeroWork's core moat for social automation.
2. **Regular browser mode** (run in daily Chrome w/ existing logins) → `launchPersistentContext()` on a dedicated profile, or `connectOverCDP()` to Chrome with `--remote-debugging-port` (needs separate user-data-dir on Chrome 149+). Cookies → `storageState` export/import.
3. **Scheduler / webhooks / concurrency** — wrap runs: node-cron, Windows Task Scheduler, Hermes cron, or the NAS n8n instance (webhook triggers free there).
4. **Rate caps per run/hour/day + human pacing** — token-bucket limiter + randomized delays, ~50 lines.
5. **Visual builder** — none in Playwright. Replacement: YAML task DSL + ~300-line interpreter. Handlers = one function per block type; ctx = {page, tables, vars, limiter}; resume-from-checkpoint = serialize cursor after every step.

## Build paths
- **A. Straight scripts** — one TS file per TaskBot. Right for one-off client builds.
- **B. Faithful recreation** — YAML DSL + interpreter engine (open_link, save-list, repeat, insert-text, delay, spintax blocks verified conceptually). Product-seed candidate.

## Target-site notes
books.toscrape.com = clean demo target (no anti-bot, 20 books/page, `.product_pod h3 a` titles with title attributes).
