---
name: zerowork-to-playwright
description: "Use when Dennis gives a ZeroWork workflow URL or name and wants the entire TaskBot recreated as local Playwright."
version: 1.1.1
author: Dennis Rongo (@codingmenace)
---

# ZeroWork → Playwright

The inverse of [`../zerowork-taskbot-automation/`](../zerowork-taskbot-automation/). That skill: scenario → build a ZeroWork TaskBot. This skill: existing TaskBot (URL or name) → recreate the entire workflow as local Playwright.

Block → Playwright mapping and Path A / Path B live in the sibling skill. **Link, do not copy the table:**

[../zerowork-taskbot-automation/references/playwright-recreation-map.md](../zerowork-taskbot-automation/references/playwright-recreation-map.md)

Canvas extract + locator translation (Playwright-side only): [references/extract-and-port.md](references/extract-and-port.md).

## When to use

Dennis (or a brief) gives `https://creator.zerowork.io/workflows/<id>` or a TaskBot name. Recreate the full graph locally in Playwright. Not for building new ZeroWork bots (that is the sibling skill).

## Hard rules

1. **E2E required.** A port is not done until `npx playwright test` runs on a public target, or Dennis explicitly allows a logged-in run. Write-only extracts are a midpoint, not delivery.
2. **Data parity.** Local storage must match the live TaskBot tables/columns/variable names exactly. Default: JSON files in `data/` — one object file per variable set (`vars.json`), one array-of-rows file per table (`<table-slug>.json`) using the ZeroWork column names as keys. `getRef`/`setRef` analogs read/write those files. No SQLite unless he asks. Do not invent extra columns. Do not drop columns the bot writes.
3. **Stale workflow bugs stay on the canvas.** If the live TaskBot has a bug (hard-coded test URL, wrong tableRefId, dead selector), do NOT edit the ZeroWork bot. Fix only in the Playwright port so the *requirement* is fulfilled. Comment the original bug next to the fix.
4. **Sticky notes → comments.** Port load-bearing sticky notes into the Playwright source as comments at the matching step.
5. **Server-like run.** The script must be runnable the same way ZeroWork's agent would: Chromium, viewport 1440×900 (ZeroWork default), existing cookies via `storageState` or `launchPersistentContext` on a profile **Dennis** created (never type passwords). Document the exact auth path in the port README. Gitignore `auth/` and `.env`.
6. **Selectors: verify live, then fix in the port.** After extract, hit the public page (or he-authed page) and confirm CSS still matches. If the site changed, update Playwright locators only.
7. **Unobserved drawers:** throw `needSelector(nodeName)` / `needWriteJs(nodeName)` — never invent CSS or JS. Then go back and extract; don't ship TODOs as "done".
8. **Keep.** Read-only on the live TaskBot (do NOT click Run, Log out, Auto-align, or edit drawers / scheduler / webhook). Confirm `/workflows` list first (session must be Dennis's). **Dennis does all site logins.** Never store passwords, cookie JSON, 2FA, or session tokens. CSS-first selectors (same as sibling); convert ZeroWork `>> nth=` / `{loop_index}` to Playwright locators (`nth()`, `locator().nth(i)`). Do not bake live workflow/table IDs into the Playwright repo output as required handles (config placeholders / `TABLE` names are OK). Path A default (one TypeScript file per TaskBot); YAML DSL (Path B) only if he asks. Do not commit secrets. Put generated scripts under a folder he names, or `playwright-ports/<safe-slug>/` (gitignored / generated — keep in this repo only if he asks). Prefer `playwright-ports/<slug>/` with a `.gitignore` for `auth/` and `.env`.

9. **Never reuse a live TaskBot's Google Sheet (Dennis 2026-08-17).** Never open, edit, or reuse a live TaskBot's existing Google Sheet. When a port needs Sheets, create a **new** Google Sheet on Dennis's account. Do not change the live TaskBot's Sheets link. Local JSON in `data/` remains the runtime store; the new Sheet is an optional export/sync he owns.

## Procedure

1. Resolve name → open `/workflows`, search, open the bot. URL is already a handle.
2. Fit-view / node search. Extract: node id, name, type, edges (body vs After Repeat vs Found/Not Found vs Else), tables/columns **exactly as named**, drawer fields (selectors, URLs, loop type Standard/Dynamic, HTTP method/paths, Write JS full source), load-bearing sticky notes. Recipe: [references/extract-and-port.md](references/extract-and-port.md).
3. Map each node via the recreation map. Write JS nodes become functions (already JS) — keep his `tableRefId` / `varRefId` constants at the top, but point them at local JSON (`data/vars.json`, `data/<table-slug>.json`), not ZeroWork numeric ids.
4. Loops: Standard = for N / while locator count; Dynamic = for each row in local table; After Repeat = code after the loop; Break = break; nested = nested loops; message-cap = counter + break.
5. Tabs: `context.pages()`, URL match preferred.
6. HTTP: `APIRequestContext`. SAVE RESPONSE nested paths = lodash-style get. Status-only = `response.status()`.
7. Conditions: if/else. ELSE Set Condition = `else`. Contains keywords = comma-split includes.
8. Notifications: stub `console.log` or webhook POST placeholder — do not email his account from the script.
9. Scheduler/webhook: document as cron / HTTP server stub in README of the port; do not invent infra.
10. Verify selectors on the live public (or he-authed) page; if the site changed, update Playwright locators only. Stale canvas bugs: fix only in the Playwright port and comment the original bug.
11. **E2E:** `npx playwright test` on a **public** target, or a logged-in run he explicitly allows. Write-only is a midpoint. Never Run the live ZeroWork client bot. Never hit production outreach (LI/FB/IG DM) unless he explicitly says to run the Playwright port.

## Deliverable

- `playwright.config.ts` — Chromium, viewport 1440×900
- `src/<slug>.ts` (or spec) that mirrors the graph top-to-bottom, with sticky-note comments and `needSelector` / `needWriteJs` for unobserved drawers
- `data/vars.json` (object) + `data/<table-slug>.json` (array of rows; ZeroWork column names as keys)
- `README.md` in the port: how to run, exact auth path he must set up first, what was not ported (scheduler, email-to-account-owner)
- A passing `npx playwright test` (E2E) — not optional
