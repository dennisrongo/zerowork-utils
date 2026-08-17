# zerowork-utils

This repo is **zerowork-utils**: the ZeroWork TaskBot agent skill plus the Ubuntu Chrome/ZeroWork installer.

## Start here

Read `skills/zerowork-taskbot-automation/SKILL.md` first (version is in the frontmatter; currently **1.3.20**). Depth lives in `skills/zerowork-taskbot-automation/references/`. Do not duplicate that material here.

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
```
