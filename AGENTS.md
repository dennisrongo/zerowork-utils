# zerowork-utils

This repo is **zerowork-utils**: the ZeroWork TaskBot agent skill plus the Ubuntu Chrome/ZeroWork installer.

## Start here

Read `skills/zerowork-taskbot-automation/SKILL.md` first when building a TaskBot (version is in the frontmatter; currently **1.3.20**). Depth lives in `skills/zerowork-taskbot-automation/references/`. Do not duplicate that material here.

When the user gives a ZeroWork workflow URL or TaskBot name to recreate in Playwright, use `skills/zerowork-to-playwright/SKILL.md` (currently **1.1.1**) — the inverse path. Ports are not done until E2E (`npx playwright test`); keep data parity; fix stale canvas bugs only in the Playwright port. Do not build a new TaskBot for that request.

**Keep `README.md` in sync with every skill version bump.**

## Hard rules

- **CSS-first** selectors (`:nth-child({loop_index})` or `>> nth=`). XPath is a last resort.
- Write JS: put `tableRefId` / `varRefId` / `indexRefId` constants at the top. Portable scripts call `zw.getTaskbotInfo()` then use those consts.
- **Dennis does all site logins.** Never store passwords, cookie JSON, 2FA, or session tokens. Never type credentials into a TaskBot.
- Default: build + Detect errors only. Do not Run client bots unless the brief says so.
- No live IDs or secrets in commits. Use `{id,name}` / **My references**.
- Confirm the `/workflows` bot list before assuming the creator session is this account.

## Job intake

Need: outcome, site URL(s) + public vs logged-in, schedule/webhook/one-shot, whether Run is allowed. Patterns 1–19 are in `skills/zerowork-taskbot-automation/references/build-patterns.md`.

## Verify

```
python skills/zerowork-taskbot-automation/scripts/check_skill_coverage.py
python -m unittest skills/zerowork-taskbot-automation/tests/test_skill_coverage_and_helpers.py -v
python -m unittest skills/zerowork-to-playwright/tests/test_skill.py -v
```
