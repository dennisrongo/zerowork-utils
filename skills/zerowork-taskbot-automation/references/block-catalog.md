# Block catalog — operational knowledge for every palette node

44 palette blocks plus Check Web Element's Found/Not-Found branches and
Save Web Element's Save Lists / Enrich Existing Data modes. UI names +
canonical `type` strings: [node-types.md](node-types.md). Drawer automation
gotchas live at the bottom. Selectors / refs / tables:
[platform-primitives.md](platform-primitives.md). Write JS API:
[write-javascript.md](write-javascript.md). Run / agent / schedule:
[run-and-platform.md](run-and-platform.md).

Official building-blocks hub:
https://docs.zerowork.io/using-zerowork/using-building-blocks.md
The hub **omits** Launch Browser, Quit Browser, and Run TaskBot — they
still exist in the palette and in llms.txt. Coverage is the UNION.

Every section below encodes: **Purpose**, **`type`**, official URL,
**Config / drawer fields**, **Wiring / companions**, **When to use vs
adjacent**, **Gotchas**.

## Using Building Blocks (hub)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks.md
- **Purpose:** Index of palette blocks plus the three dynamic-input
  kinds every field accepts (refs, code, spintax). The hub **omits**
  Launch Browser, Quit Browser, and Run TaskBot — still build those from
  this catalog.
- **Config / drawer fields:** Not a block. See Dynamic Inputs in
  [platform-primitives.md](platform-primitives.md) and each node section.
- **Wiring / companions:** Hub reminder: After Repeat / Try-Catch
  companions and the single-starting-block rule. Details in each logic
  section and [rest-api.md](rest-api.md).
- **When to use vs adjacent:** Start here only to find a block; assemble
  from the per-node sections below.
- **Gotchas:** Hub list ≠ palette. Coverage is the UNION of this catalog
  and llms.txt.

## Companion-pair rule

`loop` + `continue_after_repeat`, `try` + `after_try` + `catch` — the
opener carries the config; companions are flow structure with no (or
almost no) drawers of their own. Drop/create the opener; wire companions
**directly off it** (never after the last body block). Validator wording:
[rest-api.md](rest-api.md).

Branch-capable (may have more than one outgoing edge): Start Condition,
Start Repeat, Check Web Element, Start Try-Catch. Everyone else: one out.

---

# BROWSER

## Open Link (`open_link`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/open-link.md
- **Purpose:** Open a URL in Chrome. If no browser context exists, this
  **launches** one from current Browser Launch Settings / defaults.
- **Config / drawer fields:** textarea placeholder `https://example.com`
  (static URL, `{id,name}` ref, or `${}` code); **open in new tab**
  checkbox; min/max sec delay after the action.
- **Wiring / companions:** Typical starting block. Single-out. New tab
  stays in the background; add Switch or Close Tab if a human needs to
  watch, or enable Bring pages to front.
- **When to use vs adjacent:** First navigation, or reopen after Quit
  Browser. Use Launch Browser first when you must override engine / sticky
  / proxy / bypass *before* any URL. Use Write JS
  `zw.browserContext.launch()` for Playwright-level control.
- **Gotchas:** Unreachable URL stops the run with a Chrome network error
  code (`chrome://network-errors/`). Table-ref "no url" = you are not in a
  Dynamic loop over that table. Cookies / sticky profile for login, not
  this block.

## Save Page URL (`save_url`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-page-url.md
- **Purpose:** Write the **current tab's URL** to a variable or table column.
- **Config / drawer fields:** save-target picker (table → column / variable).
- **Wiring / companions:** Single-out. Place after Open Link / Click that
  landed on the page you want recorded.
- **When to use vs adjacent:** Current location. Save Web Element → Save-as
  **Link** for an element's `href`. Clipboard if the site only exposes Copy.
- **Gotchas:** Save-to lists only tables attached to this bot.

## Switch or Close Tab (`tabs`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/switch-or-close-tab.md
- **Purpose:** Activate or close a tab by latest / previous / next /
  URL-match / tab number.
- **Config / drawer fields:** Action radios **Switch** vs **Close**. Target:
  Latest, Previous, Next, Tab URL matching (full, partial, or
  `/regex/flags` — invalid regex is treated as a literal, no error), Tab
  number (1 = leftmost). Min/max delay.
- **Wiring / companions:** Single-out. After Open-in-new-tab, or to close
  leftovers. Closing the last tab **ends the browser context**; next
  browser action needs Open Link / Launch Browser or the run errors.
- **When to use vs adjacent:** Tab management. Not for iframes (Switch
  Frame). Not for history (Go Back or Forward).
- **Gotchas:** Tab number / latest / prev / next follow **creation order**,
  not visual order after a human drag. In "regular browser" / sticky-shared
  sessions prefer **URL matching**. Closing the active tab activates the
  next-right, else next-left.

## Go Back or Forward (`navigate`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/go-back-or-forward.md
- **Purpose:** Browser history back or forward.
- **Config / drawer fields:** radios back / forward; min/max.
- **Wiring / companions:** Single-out.
- **When to use vs adjacent:** History. Prefer Open Link to a known URL
  when you can — more deterministic than history.
- **Gotchas:** No history entry = no-op, run continues.

## Launch Browser (`launch_browser`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/launch-browser.md
  (not listed on the building-blocks hub).
- **Purpose:** Create (or replace) the browser context and optionally
  override Browser Launch Settings mid-run. Starts on `about:blank` — follow
  with Open Link. Subsequent no-code web blocks use this context.
- **Config / drawer fields:** Each group defaults to **Use current
  defaults**. Override: **Launch mode** Incognito vs Sticky (+ Sticky
  profile ID / COPY PROFILE ID); **Bypass bot detection**; **Run in
  background**; **Maximize**; **Window size** W×H; **Cookies** JSON
  (`name`,`value`,`domain`) + ADD COOKIE; **Proxy** `host:port` or
  `socks5://host:port`, user/pass (HTTP only), bypass domains; **Browser**
  Default Chrome vs custom executable path; **Launch arguments**
  space-separated flags; **Scripts** path or inline content, reinjected on
  relaunch; **Stay on page after run**.
- **Wiring / companions:** Single-out. Usually the first block when
  settings matter. Pair with Quit Browser to tear down mid-flow. Overrides
  become the new runtime defaults until another Launch Browser reverses them.
- **When to use vs adjacent:** Need sticky / proxy / bypass / scripts
  without Write JS. Open Link alone is enough when defaults are fine.
  `zw.browserContext.launch()` for the full Playwright surface.
- **Gotchas:** Always becomes the **main** context (replaces an existing
  one). Sticky attach (profile already live): browser-level settings
  (background, bypass, size, engine, args) are **ignored**; cookies /
  scripts / page-visibility still apply. Bypass ignores window size, launch
  args, browser engine; blocks uploads ≳ 50 MB. Background + stay-on-page
  leaves an invisible browser. Closing the last tab ends the context.

## Quit Browser (`quit_browser`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/quit-browser.md
  (not listed on the building-blocks hub).
- **Purpose:** Close the browser this TaskBot is using. Often unnecessary —
  the agent closes Chrome at run end unless Stay-on-page is on.
- **Config / drawer fields:** **Force quit** checkbox.
- **Wiring / companions:** Single-out. Place before a later Open Link /
  Launch Browser if you need a **fresh** context mid-run.
- **When to use vs adjacent:** Explicit teardown, or to override
  Stay-on-page. Write JS `zw.browserContext.quit({forceQuit})` is the code
  equivalent.
- **Gotchas:** No browser → warning, run continues. Sticky shared with
  other bots: default closes **your tabs only**; Force quit kills the
  shared instance for everyone. Explicit quit **overrides** Stay-on-page.

## Switch Frame (`switch_frame`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/switch-frame.md
- **Purpose:** Enter an iframe (or return to the main frame) so later
  selector blocks see that document.
- **Config / drawer fields:** radios enter iframe (selector of the
  `<iframe>`) vs **Main frame**; min/max.
- **Wiring / companions:** Single-out. All following web blocks stay in
  that frame until Main frame / Open Link / Switch-or-Close Tab (those
  **clear** the frame). Nested iframes = chained Switch Frame blocks.
- **When to use vs adjacent:** Iframes only. A "selector not found" inside
  an embedded form/checkout/recaptcha is usually a missing Switch Frame.
- **Gotchas:** Missing iframe → error, stop. Increase selector timeout on
  in-frame Click/Save/Hover. Nested: you must walk each level.

## Browser Alert (`accept_dialog`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/browser-alert.md
- **Purpose:** Accept a native dialog (`alert` / `confirm` / `prompt` /
  `beforeunload`). Default platform behavior is **Cancel**.
- **Config / drawer fields:** textarea **response text** (prompt only;
  ignored for alert/confirm/beforeunload); min/max.
- **Wiring / companions:** Single-out. Place **after** the action that
  triggers the dialog.
- **When to use vs adjacent:** Native browser dialogs, not in-page modals
  (those are Click / Keyboard Escape).
- **Gotchas:** No dialog present = no-op. Does not click in-page cookie
  banners.

---

# WEB INTERACTION

## Click Web Element (`click`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/click-web-element.md
- **Purpose:** Click a button, link, custom dropdown, "Next", upload
  control, etc.
- **Config / drawer fields:** textarea CSS/XPath; **skip if not found**;
  **open in new tab**; min/max; selector timeout in Selector Options.
- **Wiring / companions:** Single-out. Pair with Check Web Element when
  the target is optional. For file upload: Click the control, then Upload
  File. For download: Click, then Save File (from download action).
- **When to use vs adjacent:** Any clickable. Select Web Dropdown **only**
  if the control is a real `<select>`. Hover first if the target appears
  on hover.
- **Gotchas:** Prove uniqueness with `querySelectorAll`. Custom-styled
  "dropdowns" (`div`/`button`) are Clicks, not Select. First-letters-cut
  on a following Insert Text → Click the field first.

## Check Web Element (`check`) — branches `element_present` / `element_absent`

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/check-web-element.md
- **Purpose:** Branch on whether a selector is in the DOM. **Found** =
  `element_present`, **Not Found** = `element_absent`. Those two are
  canvas branch markers, not standalone configurable blocks.
- **Config / drawer fields:** textarea CSS/XPath; timeout; two outputs.
- **Wiring / companions:** **Two outgoing edges** (Found / Not Found).
  Typical: Found → continue happy path; Not Found → Send Notification /
  Break Repeat / skip.
- **When to use vs adjacent:** Presence of a **web element**. For "is this
  variable empty?" use Start/Set Condition **Data found / not found**. For
  "did the HTTP call return 200?" save status + Set Condition.
- **Gotchas:** Check timeout ≠ later block timeout. Official common
  problem: Check says Found, next Click/Save misses — race / overlay.
  Re-Check or Delay immediately before the action. Increase timeout in
  iframes.

## Save Web Element (`save`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-web-element.md
- **Purpose:** Read public page data into a table/variable.
- **Config / drawer fields:** textarea CSS/XPath; **Save as** Text / Link
  / **Custom attribute** (+ "Enter attribute", e.g. `title`) / HTML /
  Image file URL; **Save to** two-step table → column; **skip if no
  element is found**; min/max.
- **Wiring / companions:** Single-out. Two first-class modes below.
- **When to use vs adjacent:** DOM text/attrs. Current URL → Save Page
  URL. Files → Save File. Clipboard-only sites → Save from Clipboard.
- **Gotchas:** Without `{loop_index}` a list Save always writes the
  **first** match. CSS `:nth-of-type({loop_index})` breaks on grid items
  under different parents — use XPath
  `(//article[contains(@class,"product_pod")])[{loop_index}]//h3/a`.
  Skip-if-not-found also prevents "continue until no element" from
  ending the loop.

### Save Lists mode

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-web-element/save-lists.md
- **Purpose:** Append N items from a visible list (LinkedIn results,
  product grid, FB members).
- **Config / drawer fields:** Same Save Web Element drawer (selector with
  `{loop_index}`, Save-as, Save-to, skip-if-missing). Loop drawer: Standard
  + fixed N / count-elements / continue-until-no-element.
- **Wiring / companions:** Open Link → Start Repeat Standard → Save ×
  columns (single-out chain). After Repeat only if more work follows the
  list. Nested After Repeat + Click Next for pagination.
- **When to use vs adjacent:** New rows from a page list. Enrich Existing
  Data when the URLs already live in a table. Write JS `appendIndex` when
  you would rather scrape in one script.
- **Gotchas:** Data always **appends**. Overwrite = Delete Data before the
  loop. Dedup = Remove Duplicates **after**. Pagination = nested loops.
  Auto-scroll can fail; fall back to Keyboard Space / ArrowDown.

### Enrich Existing Data mode

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-web-element/enrich-existing-data.md
- **Purpose:** Visit each already-stored URL and write extra columns onto
  the **same row**.
- **Config / drawer fields:** Dynamic Start Repeat (table picker + optional
  repetition cap + auto-continue). Open Link URL = table column ref. Save
  Web Element selectors are **page** selectors (no `{loop_index}`).
- **Wiring / companions:** Start Repeat Dynamic → Open Link → Save × extra
  fields. Optional Update Data `visited` + Start/Set Condition
  (`≠ visited`) + Else skip.
- **When to use vs adjacent:** Existing rows. Save Lists when you are
  creating the list. Standard loop would append, not enrich.
- **Gotchas:** Standard loop would **append new rows**, not enrich. Table
  refs outside a Dynamic loop pull nothing. Re-visiting the same profiles
  triggers anti-bot — stamp a status column.

## Insert Text or Data (`insert_data`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/insert-text-or-data.md
- **Purpose:** Type or paste into an input (forms, search, DMs, login).
- **Config / drawer fields:** content textarea + `{id,name}` / `${}` /
  **spintax** checkbox; **Insert instantly without typing delay** (paste);
  typing-speed radios when not instant (VERY SLOW → PRO); **no-Enter**;
  optional selector; **Encrypt content** (password — irreversible; delete
  and re-enter to change).
- **Wiring / companions:** Single-out. Click the field first if the site
  swallows leading keystrokes. Pair with Keyboard Enter to submit if
  no-Enter is on.
- **When to use vs adjacent:** Text fields. Keyboard Action for shortcuts
  / Tab / Escape, not long strings. Encrypt + Insert for login when
  cookies/sticky are not an option.
- **Gotchas:** Instant-on → selector **required**. Instant-off → selector
  optional (types at caret; Wikipedia/Google often focus search). First
  letters cut off → Click first, slower speed, or Delay. Table ref empty
  → not in a Dynamic loop.

## Hover Web Element (`hover`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/hover-web-element.md
- **Purpose:** Hover so a tooltip / date / menu appears, then Save or Click
  it.
- **Config / drawer fields:** textarea CSS/XPath; min/max.
- **Wiring / companions:** Single-out. Hover → Save/Click the revealed node.
- **When to use vs adjacent:** Reveal-on-hover only. Not a substitute for
  Click.
- **Gotchas:** Revealed nodes often need a slightly longer timeout.

## Select Web Dropdown (`select`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/select-web-dropdown.md
- **Purpose:** Choose an `<option>` in a native `<select>`.
- **Config / drawer fields:** input option text/value; textarea dropdown
  selector (must be a `select` tag); min/max.
- **Wiring / companions:** Single-out.
- **When to use vs adjacent:** Real `<select>` only. Custom `div`/`button`
  "dropdowns" → Click (open) + Click (option), or Keyboard.
- **Gotchas:** Wrong tag = silent failure / not-found. Option can be a
  variable/table ref.

## Keyboard Action (`keyboard`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/keyboard-action.md
- **Purpose:** Fire a key or combo: Enter, Tab, Shift+Tab, Escape,
  arrows, letters, Ctrl/Cmd+C (Meta = Ctrl/Cmd in the UI).
- **Config / drawer fields:** key picker; min/max.
- **Wiring / companions:** Single-out. Focus the target first (Click or
  Insert). Tab × N + Enter can replace brittle selectors on simple forms.
- **When to use vs adjacent:** Shortcuts, dismiss popups (Escape), reload
  (Meta+R), scroll fallback (Space / ArrowDown), form Tab-through. Long
  text → Insert Text. Native browser chrome (Ctrl+P print, Ctrl+F find,
  Cmd+S save-as, maximize) **does not work**.
- **Gotchas:** Shift+Tab order is Shift **then** Tab. Common-problem page:
  nothing happens = no focus, or the site eats keys. Not a substitute for
  Click on custom widgets.

---

# LOGIC

## Start Condition (`check_dynamic_data`) and Set Condition (`conditionNode`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition.md
  plus
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/actions-and.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/actions-less-than-greater-than.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/data-found-and-data-not-found.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/contains-and-does-not-contain.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-condition-and-set-condition/before-date-and-after-date.md
- **Purpose:** Branch on a value. Start Condition holds the **reference**
  (variable/column). Each Set Condition holds **one** operator + one
  outgoing edge.
- **Config / drawer fields:**
  - Start: value picker (variable / table column).
  - Set: operator + comparison operand (literal, ref, or days-shift for
    dates). 18 operators: `=` `≠` `<` `>` `≤` `≥`; Contains / Does not
    contain; Data found (not empty) / Data not found (empty); Longer than /
    Shorter than (char length); Before (Date) / After (Date) + **days
    shift** (pos or neg); Is a valid number / Is not a valid number;
    **Else**.
- **Wiring / companions:** Start Condition is **branch-capable** (N Set
  Condition blocks off it). Each Set Condition is **single-out**. Chain
  another Start/Set pair for AND-across-fields. Always include **Else**
  if you need a fallback.
- **When to use vs adjacent:** Data/variable tests. Web-element presence
  → Check Web Element. Regex true/false → Apply Regex "Check if pattern
  matches" then condition on the result.
- **Gotchas:** Numeric `<` `>` throw on non-numeric strings (`TEST123 > 50`
  errors; `51.77 > 50` is fine). Sanitize first (math **Remove format**,
  or regex). Date formats on both sides **must match**. Deactivating a
  condition **and** its Sets makes the next path **random**.

## Start Repeat (`loop`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat.md
  plus
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/standard-loop.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/dynamic-loop.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/continue-until-no-element-is-found.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/auto-scroll.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/auto-continue-from-last-row-or-element.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/start-repeat/nested-loops-handle-pagination.md
- **Purpose:** Repeat a body. **Standard** appends new table rows (scrape
  a list, or repeat a static action). **Dynamic** walks **existing** rows
  (enrich, message, visit).
- **Config / drawer fields:** Loop-type radios Standard (pre-selected) vs
  Dynamic. Standard sub-modes: **Fixed repetitions** (INPUT placeholder
  `Enter number of repetitions` — not a textarea); **Continue until no
  element is found**; **Count elements** matching a lead selector.
  Optional **Start from** (element/row number). **Auto-scroll** checkbox.
  **Auto-continue from last row or element** (resume across runs). Sheets
  additional option: write-batch size (default 50).
- **Wiring / companions:** **Branch-capable**. Output 1 = loop body.
  Output 2 = **After Repeat** (must come off this node). MAY have multiple
  outgoing edges. Body includes every block until After Repeat / end.
- **When to use vs adjacent:** Any repetition. Nested Start Repeat for
  pagination (outer = pages, inner = items). Write JS `appendIndex` can
  replace a Standard scrape loop.
- **Gotchas:**
  - Standard **ignores** existing table data — table refs inside it see
    the row being appended, not old rows.
  - Dynamic without a table = nothing happens. Optional repetition cap
    (e.g. 100/day) + auto-continue.
  - Continue-until-no-element with **no** web-element action = infinite
    loop. Skip-if-not-found / Try-Catch **suppress** the end condition;
    then you need auto-scroll or a manual Break. Prefer a **fixed N**
    when you know page size (10 LinkedIn results).
  - `{loop_index}` / `{loop_index,start}` / `{loop_index,start,step}` /
    `{loop_index_NODEID}` — see platform-primitives.md.
  - Auto-scroll official page is a stub; it fails on some virtual lists
    (Keyboard fallback).
  - Auto-continue: Dynamic = next **row**; Standard = next **list
    selector**. `Start from` is a floor.

## After Repeat (`continue_after_repeat`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/after-repeat.md
- **Purpose:** Run once after a loop finishes (notify, Click Next, start
  a second independent loop in the same bot).
- **Config / drawer fields:** None (flow structure).
- **Wiring / companions:** **Must be wired directly off Start Repeat**
  (its second output). Validator: "must be preceded by a single Start
  Repeat". For pagination, After Repeat hangs off the **inner** loop, then
  Click Next, then the outer loop continues.
- **When to use vs adjacent:** Post-loop work. Deactivating Start Repeat
  skips the body and continues at After Repeat.
- **Gotchas:** Never chain it after the last Save in the body.

## Break Repeat (`loop_exit`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/break-repeat.md
- **Purpose:** Leave the **current** loop early (no more results, HTTP
  status ≠ 200, DM counter hit the cap).
- **Config / drawer fields:** None significant.
- **Wiring / companions:** Single-out. Typically under a Set Condition or
  Check Not-Found **inside** the loop. Execution continues at After Repeat
  (if any).
- **When to use vs adjacent:** Exit this loop, keep the bot running.
  Abort Run kills the **whole** run. Raise Error / throw fails the run
  (catchable).
- **Gotchas:** Breaks the innermost loop only.

## Run TaskBot (`run_taskbot`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/run-taskbot.md
  (agent **≥ 1.1.75**; not on the building-blocks hub).
- **Purpose:** Start another TaskBot from this one (sub-bot). Optionally
  wait; optionally pass variable values.
- **Config / drawer fields:** TaskBot picker, or **Custom** id (literal /
  ref / `${}`). Variable name/value pairs (only listed vars change).
  **Wait until the TaskBot finishes**. Persist-value is a setting **on
  the child variable**, not here (off = this-run-only).
- **Wiring / companions:** Single-out. Wrap with Try-Catch if Wait is on
  (child fail / manual stop throws here). Concurrent Runs on the child
  lets several parents call it in parallel.
- **When to use vs adjacent:** Structured sub-bot. Webhook+HTTP is the
  older "fire and forget another bot" path (no wait, uses
  `zw_webhook_data`).
- **Gotchas:** Recursion A→B→A is rejected. Wait-off: child errors do
  **not** surface here. Stopping a parent stops wait-on children (and
  their children). No depth cap besides recursion.

## Start Try-Catch (`try`), After Try-Catch (`after_try`), On Catch Error (`catch`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/try-catch.md
- **Purpose:** Swallow a step failure and continue. Body after `try` is
  the protected scope. On error, jump to `catch`. After success **or**
  catch, continue at `after_try`.
- **Config / drawer fields:** Opener may be empty; companions are structure.
- **Wiring / companions:** `catch` AND `after_try` **both wire directly
  off `try`**. Never `try → body → catch` or `catch → after_try`.
  Verified: failing click with try-catch → Success/0 errors; without →
  run error.
- **When to use vs adjacent:** Recoverable step failures. Abort Run for
  unrecoverable. Raise Error / `throw` to **enter** a catch on purpose.
- **Gotchas:** Start-failure (outdated agent, invalid setup, more than
  one starting block) is **not** catchable. Deactivating Start Try-Catch
  skips to After Try-Catch.

## Raise Error (`throw`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/raise-error.md
  (page is a stub — "upcoming").
- **Purpose:** Fail the current step with an error so Try-Catch can
  branch, or so the run is marked failed and notifications fire.
- **Config / drawer fields:** Error message (live drawer; official page
  empty). Write JS `throw new Error("…")` is the documented equivalent.
- **Wiring / companions:** Single-out. Place inside a try body to force
  the catch path.
- **When to use vs adjacent:** Intentional failure. Abort Run stops
  **without** treating it as a catchable step error in the same way —
  use Abort when you just want out. Log + Abort if you only need a
  breadcrumb.
- **Gotchas:** Official page has no field list; prefer Write JS `throw`
  when you need a precise message in reports.

## Abort Run (`abort`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/abort-run.md
- **Purpose:** Stop the **entire** run immediately (critical data missing,
  hard cap reached and you do not want After Repeat).
- **Config / drawer fields:** None significant.
- **Wiring / companions:** Terminal. Typically under a Set Condition.
- **When to use vs adjacent:** Kill the run. Break Repeat only leaves the
  loop. Raise Error marks failure (and is catchable).
- **Gotchas:** After Repeat will **not** run.

---

# DATA

## Update Data (`update_variable`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/update-data.md
- **Purpose:** Set a variable or the current table cell to a new value
  (empty = clear). Classic: mark `qualified` / `visited` / `sent`.
- **Config / drawer fields:** value textarea (empty clears); **Data to be
  updated** two MUI selects (table → column/var); **Use spintax**
  checkbox (off by default).
- **Wiring / companions:** Single-out. Inside Dynamic loop to stamp the
  current row; outside loops to set a variable.
- **When to use vs adjacent:** Assign / flag. Number Operations to
  increment. Format / Regex / Split to transform first.
- **Gotchas:** Table column update outside a Dynamic loop does nothing
  useful ("no data is being pulled"). Empty value is a valid clear.

## Number Operations (`math`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/number-operations.md
  and https://docs.zerowork.io/using-zerowork/using-building-blocks/number-operations/example-standardize-different-formats.md
- **Purpose:** Arithmetic and numeric cleanup.
- **Config / drawer fields:** operation select: **Add** (also concatenates
  strings) / Subtract / Multiply / Divide / Remainder / Round / Round up /
  Round down / **Random** (default range 0–1e9) / **Set decimals** /
  **Remove format** (`1,500,500.2` → `1500500.2`; also `1.000.000,23` →
  `1000000.23`; mixed grouping errors). Number field + number-to-operate-on
  (literal or ref); save-to.
- **Wiring / companions:** Single-out. Increment a counter variable each
  loop; Remove format **before** numeric Set Condition.
- **When to use vs adjacent:** Numbers. Format Data for text. Regex for
  extract-then-math.
- **Gotchas:** Empty operand → skip, continue. Non-numeric input to any
  op except Add → error, stop. Remove format is the sanitizer for prices.

## Format Data (`format_data`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/format-data.md
  plus
  https://docs.zerowork.io/using-zerowork/using-building-blocks/format-data/remove-words.md
  and
  https://docs.zerowork.io/using-zerowork/using-building-blocks/format-data/shorten-content-length.md
- **Purpose:** Text cleanup.
- **Config / drawer fields:** action + input + save-to. Actions: **Remove
  word** (comma-separated list; cannot remove commas — use Replace empty);
  **Replace text**; **Shorten content length** (N chars; use before Ask
  ChatGPT to cut tokens); lower / upper / Capitalize first letters;
  **Normalize URL** (`wikipedia.org` → `https://www.wikipedia.org/`; bare
  `wikipedia` errors); Trim white spaces; Remove line breaks; Remove
  smileys.
- **Wiring / companions:** Single-out. Empty input → no-op, continue.
- **When to use vs adjacent:** Everyday text. Regex when you need a
  pattern. Split when you need pieces in different columns.
- **Gotchas:** Remove-words cannot delete commas.

## Split Text (`split_data`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/split-data.md
- **Purpose:** Break a value on a separator into columns/variables.
- **Config / drawer fields:** value; separator; positions → destinations.
  Positions 1-based from the start; **negative** from the end (agent
  ≥ 1.1.61). Position `0` errors.
- **Wiring / companions:** Single-out. Missing position → that dest stays
  empty, no error.
- **When to use vs adjacent:** Known delimiter. Regex extract for messy
  text.
- **Gotchas:** `"Hello world"` pos 3 saves nothing.

## Apply Regex (`regex`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/apply-regex.md
- **Purpose:** Replace / extract / test a JS regular expression.
- **Config / drawer fields:** 3 radios: **Extract matches** / **Check if
  pattern matches** (`true`/`false`) / **Replace text** (+ replacement).
  Pattern textarea placeholder `/example/` — **must include JS
  delimiters** (`/£/` works, bare `£` errors). Flags `g` `i` `m` inside
  the delimiters. Text-to-apply (literal or `{id,name}`); Save result to.
- **Wiring / companions:** Single-out. Check-mode → Start/Set Condition
  on the boolean. Extract → later math/format.
- **When to use vs adjacent:** Patterns. Format Replace for literal
  strings. Number Remove format for thousands-separators.
- **Gotchas:** Empty input → no-op. Invalid regex → error, stop/break.
  Without `g`, extract/replace hit the first match only. Prefer the V
  picker for refs.

## Remove Duplicates (`remove_duplicate_rows`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/remove-duplicates.md
- **Purpose:** Batch-dedup a table. Default keeps **oldest** rows.
- **Config / drawer fields:** table picker; column (specify one — faster);
  **Preserve newest rows** (native tables only, not Sheets). File columns
  are ignored in the comparison.
- **Wiring / companions:** Single-out. Place **after** the scrape loop,
  never inside it (batch; inside a loop it still runs only once).
- **When to use vs adjacent:** After Save Lists. Prevent-rerun while
  iterating = Update Data status + condition, not this.
- **Gotchas:** Always specify a column unless you have a reason not to.

## Delete Table Data (`delete_table_data`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/delete-data.md
- **Purpose:** Delete **all rows** (overwrite-before-scrape) or **one
  row** (current Dynamic-loop row, e.g. disqualified lead).
- **Config / drawer fields:** table picker; scope all vs one.
- **Wiring / companions:** All-rows: **before** the Standard loop. One-row:
  inside Dynamic loop under a Set Condition.
- **When to use vs adjacent:** Wipe or prune. Clear a variable = Update
  Data with empty value, not this.
- **Gotchas:** All-rows is permanent. Export CSV first if you might care.

---

# EXTERNAL

## Ask ChatGPT (`ask_chatgpt`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/ask-chatgpt.md
- **Purpose:** Prompt OpenAI and save the answer to a var/column.
- **Config / drawer fields:** Model select (drawer default observed:
  "ChatGPT 5.5"); prompt textarea (placeholder "Example: Write an
  uplifting haiku…"; refs interpolate); Save answer to. Account API key
  at `creator.zerowork.io/settings` — not in the block. Optional max
  token length (too low truncates).
- **Wiring / companions:** Single-out. Format → Shorten before the prompt
  to cut tokens. Try-Catch around it (custom per-block error handling was
  removed; existing bots still work).
- **When to use vs adjacent:** Chat completions. Send HTTP for any other
  API (including non-OpenAI LLMs).
- **Gotchas:** Missing key / bad model / empty prompt hard-stop. Token
  budget is shared prompt+completion. Verified browserless run ~5s.

## Send Notification (`email`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/send-notification.md
- **Purpose:** Email **the account owner** (not arbitrary recipients).
- **Config / drawer fields:** live drawer also has input[email] (account
  dest / override — official page says destination is the account email);
  subject; body (plaintext and/or minified HTML). From
  `no-reply@notifications.zerowork.io`.
- **Wiring / companions:** Single-out. After Check Not-Found, After Repeat,
  or a failure branch.
- **When to use vs adjacent:** Self-alert. Other recipients → Send HTTP to
  an email API. Run-level Slack/webhook notifications are TaskBot
  Settings, not this block.
- **Gotchas:** Per-minute rate limit inside Start Repeat. Standard footer
  is appended.

## Send HTTP Request (`update_or_configure_api`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/apis-send-http-request.md
- **Purpose:** Arbitrary HTTP. Browserless pipelines start here.
- **Config / drawer fields:** Method (GET default); URL textarea
  (`https://api.com`); HEADERS; REQUEST BODY (`{}`); SAVE RESPONSE
  (body → table, nested **record path** becomes the column name, e.g.
  `choices[0]['text']`); save status code; min/max.
- **Wiring / companions:** Single-out. Create dest columns first. Replace
  `"` → `'` in dynamic JSON bodies (Format Replace). Condition + Break
  on status ≠ 200. Can POST to another bot's webhook.
- **When to use vs adjacent:** Any HTTP API. Ask ChatGPT for OpenAI chat.
  Write JS `axios` only when the drawer cannot express the call.
- **Gotchas:** Flat JSON keys match column names exactly; extras ignored;
  **no matching columns = no save, no error**. Trailing-slash sensitivity.
  Auto-retry on 429 / network timeout (1.1.61). Verified GET → downstream
  math works.

## Write JavaScript (`write_js`)

See [write-javascript.md](write-javascript.md) for the full `zw` API.

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript.md
  plus
  https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/imports-and-package-management.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/write-and-read-variables-and-tables.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/local-and-global-state.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/device-storage.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/utilities.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/browser-context.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/metadata.md
- **Purpose:** Custom JS in the TaskBot runtime.
- **Config / drawer fields:** Monaco; **Run locally** (or
  `// @zw-run-locally`).
- **Wiring / companions:** Single-out. Throws are catchable and land in
  reports. `console.log` is **not** persisted.
- **When to use vs adjacent:** Bulk `setRef`/`appendIndex`, npm,
  Playwright, device secrets. Prefer no-code for list scrape / HTTP /
  conditions.
- **Gotchas:** Local vs browser matrix, string-only refs, do not mix
  `appendIndex` with Start Repeat.

---

# FILES

## Save File (`save_file`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-file.md
- **Purpose:** Persist a file from a URL or from a just-triggered download.
- **Config / drawer fields:** Source: **From file URL** + dest folder, or
  **From download action** (after Click) → save URL and/or save to folder.
  File options: unique-on-conflict (append id vs overwrite); custom name;
  save full path to a **standard** (not file) column. Max wait default
  5 minutes; timeout errors.
- **Wiring / companions:** Download path: Click then Save File. Pair with
  Upload File via saved URL or full path.
- **When to use vs adjacent:** Downloads. Screenshots have their own
  block (shares file options).
- **Gotchas:** Path/URL strings go to a **standard** column. File columns
  expect an actual uploaded file. OS save dialog is hidden.

## Upload File (`upload`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/upload-file.md
- **Purpose:** Feed a file chooser from a URL or a local full path.
- **Config / drawer fields:** From file URL (or file-column ref) vs from
  folder path (docs say folder; examples are the **file pathname**).
- **Wiring / companions:** **Click the upload control first**. Chooser is
  invisible during the run.
- **When to use vs adjacent:** Page uploads. Not for stuffing a file
  column (that's a table UI action).
- **Gotchas:** Bypass detection blocks uploads ≳ 50 MB. Path is on **this**
  agent machine only.

---

# TOOLS

## Delay (`sleep`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/delay.md
- **Purpose:** Pause **before** the next block. Human-like min–max
  (seconds, decimals ok).
- **Config / drawer fields:** min (default 1), max (default 1). Refs/code
  allowed.
- **Wiring / companions:** Single-out. After Click Next (pagination race),
  between HTTP calls, after Keyboard reload.
- **When to use vs adjacent:** Explicit wait. Per-block min/max fires
  **after** that block. `zw.delay` is milliseconds.
- **Gotchas:** Empty field → block **skipped**. max < min → wait min.
  Both 0 → no pause. Invalid ref → skipped.

## Record Date (`insert_date`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/record-date.md
- **Purpose:** Write a formatted now/offset date into a var/column for
  later Before/After conditions.
- **Config / drawer fields:** format + save-to (official page is thin;
  live drawer has format + dest).
- **Wiring / companions:** Single-out. Pair with Set Condition Before/After
  (same format both sides; days shift lives on the condition).
- **When to use vs adjacent:** Structured dates. Write JS `Date`/`dayjs`
  for fancy timestamps.
- **Gotchas:** Mismatched formats make Before/After wrong. 1.1.63 fixed a
  timezone bug — keep the agent current.

## Take Screenshot (`screenshot`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/take-screenshot.md
  (stub; fields from live drawer + release notes).
- **Purpose:** Capture visible / full page / element as png or jpeg to a
  local folder; optionally save the path.
- **Config / drawer fields:** visible / full-page / element radios;
  png/jpeg; local folder; same file options as Save File. Max wait
  default 2 minutes.
- **Wiring / companions:** Single-out. Upload File via saved path.
- **When to use vs adjacent:** Pixels. Save Web Element for text/HTML.
- **Gotchas:** Path → standard column, not file column.

## Save from Clipboard (`save_clipboard`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-from-clipboard.md
- **Purpose:** Read the OS clipboard into a var/column.
- **Config / drawer fields:** save-to.
- **Wiring / companions:** Click the site's Copy control, then this.
  Launch always grants clipboard-read/write.
- **When to use vs adjacent:** Copy-only UIs. Prefer Save Web Element /
  Save Page URL when the value is in the DOM.
- **Gotchas:** **No isolation** between parallel TaskBots — they share
  one clipboard.

## Log (`log`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/log.md
- **Purpose:** Persist a message in live run + Run Reports. Best
  verification hook for variables (`Result: {id, name}`).
- **Config / drawer fields:** message textarea (refs interpolate); **tag**;
  status select Success / Fail / Warning.
- **Wiring / companions:** Single-out. End of a branch, after a scrape,
  after HTTP+math.
- **When to use vs adjacent:** No-code breadcrumb. `zw.log` / `zw.logTemp`
  from JS (`logTemp` = not persisted — use for secrets).
- **Gotchas:** Empty message = warning, run still succeeds. Don't log
  secrets. Reports do not store `console.log`.

---

# CANVAS-ONLY / OPTIONS

## Auto-align (`auto-align`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/auto-align.md
- **Purpose:** Rearrange the graph top-to-bottom or left-to-right. **No
  runtime effect.** Bottom-left React Flow controls
  (`.react-flow__controls-button`, tooltip "Auto-align top to bottom" /
  "left to right").
- **Config / drawer fields:** None — canvas control, not a config drawer.
  Two buttons: top-to-bottom and left-to-right.
- **Wiring / companions:** None. Prefer it before connecting handles
  (edges must run top→bottom / left→right).
- **When to use vs adjacent:** Layout only. Not a node you POST.
- **Gotchas:** Earlier helper comments claimed this control did not exist.
  It does. Clicking a random bottom-left coord can hit "toggle
  interactivity" instead — click the labeled controls button.

## Sticky note (`sticky_note`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/sticky-notes.md
- **Purpose:** Canvas comment / grouping. Not executed. Markdown as of
  1.1.75.
- **Config / drawer fields:** note text.
- **Wiring / companions:** None.
- **When to use vs adjacent:** Documentation on the canvas. Log is for
  run-time messages.
- **Gotchas:** Not executed. Do not POST `sticky_note` expecting a run
  step. Markdown rendering is agent ≥ 1.1.75.

## Deactivate / shortcuts / inter-block delay

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/deactivate-building-blocks.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/shortcuts.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/delay-times-between-the-building-blocks.md
- **Purpose:** Canvas options that are not palette nodes: skip blocks,
  multi-select, and human-like waits between steps.
- **Config / drawer fields:** No dedicated drawer. Right-click Deactivate /
  Activate. Per-block min/max delay (after the action). Optional
  randomize-all-delays after the graph is built.
- **Wiring / companions:** Deactivated nodes stay in the graph and **still
  count** for validator structure (class `deactive`, skipped at run). Skip
  a loop = deactivate Start Repeat (continues at After Repeat). Skip try =
  deactivate Start Try-Catch (continues at After Try-Catch).
- **When to use vs adjacent:** Temporarily mute a path without deleting
  edges. A Delay block is an explicit wait **before** the next action;
  per-block delay is **after**.
- **Gotchas:** Deactivating a Start Condition **and** its Sets makes the
  next path **random**. Multi-select: Shift+drag or Cmd/Ctrl+click.
  Randomizing inter-block delays (3–15s example) can greatly slow the run.

Internal canvas types also include `fake` and `delete` (not user-facing).

---

## Drawer field cheat-sheet (automation)

| Block | Drawer fields (placeholder / type) |
|---|---|
| Open Link | textarea[`https://example.com`]; "open in new tab" cb; min/max sec |
| Save Page URL | save-target picker |
| Switch or Close Tab | radios: switch/close × latest/prev/next/URL-match/tab# |
| Go Back or Forward | radios back/forward; min/max |
| Launch Browser | bypass bot detection, background, maximize, window size, cookies, proxy, browser engine, launch args, scripts, page visibility (tri-state), sticky/incognito |
| Quit Browser | Force quit checkbox |
| Switch Frame | radios enter/exit (main) frame; iframe selector; min/max |
| Browser Alert | textarea[response text]; min/max |
| Click Web Element | textarea[CSS/XPath]; skip-if-not-found cb; open-in-new-tab cb; min/max |
| Check Web Element | textarea[CSS/XPath]; timeout; TWO branch outputs (Found / Not Found) |
| Save Web Element | textarea[CSS/XPath]; Save-as (Text / Link / Custom attribute + "Enter attribute" / HTML / Image file URL); Save-to picker; skip-if-missing cb; min/max |
| Insert Text or Data | textarea[content] + spintax cb; no-Enter cb; optional selector; typing speed; encrypt; instant-paste cb |
| Hover Web Element | textarea[CSS/XPath]; min/max |
| Select Web Dropdown | input[option]; textarea[dropdown selector]; min/max |
| Keyboard Action | key picker UI; min/max |
| Start Repeat | Standard vs Dynamic; Fixed / Continue-until-no-element / Count-elements; repetition INPUT `Enter number of repetitions`; Auto-scroll; Start-from; Auto-continue |
| Start / Set Condition | Start = value picker; Set = 18 operators + operand / Else |
| Update Data | value textarea (empty = clear); two MUI selects; Use spintax cb |
| Number Operations | Add/Subtract/Multiply/Divide/Remainder/Round/Round up/Round down/Random/Set decimals/Remove format; operands; save-to |
| Format Data | Remove word / Replace / Shorten / case / Normalize URL / Trim / line breaks / smileys; input; save-to |
| Split Text | separator + input + 1-based or negative positions + dests |
| Apply Regex | Extract / Check / Replace; pattern `/example/`; Text-to-apply; Save result to |
| Remove Duplicates | table picker; column; Preserve newest (native only) |
| Delete Data | table picker; all rows vs one row |
| Ask ChatGPT | Model select; prompt textarea; Save answer to |
| Send Notification | input[email]; textarea[subject]; textarea[body] |
| Send HTTP Request | Method; URL; HEADERS / BODY / SAVE RESPONSE; record path; status dest; min/max |
| Write JavaScript | MONACO; Run locally cb |
| Save File / Upload File | source radios; folder/path; file options; min/max |
| Delay | min/max sec |
| Record Date | format + save-to |
| Take Screenshot | visible/full-page/element; png/jpeg; local folder |
| Save from Clipboard | save-to |
| Log | textarea[message]; tag; status (Success/Fail/Warning) |
| Run TaskBot | bot picker or Custom id; var pairs; Wait until finishes |

## Save-to pickers (the fiddly part)

- Two-step MUI selects: table → column. The column step silently fails if
  the drawer closes mid-selection — reopen and redo. Error banner "A
  column or variable is required" = column never landed.
- Save-to lists ONLY tables attached to the current bot. Typing filters;
  no create-option.
- New REST-created columns are invisible until a full page reload
  (drawer caches at load).
- Scroll drawer to bottom before hunting MUI selects — fields near the
  drawer edge clip their listboxes.

## Stray-'x' trap

SaveWE/regex/HTTP drawers pair each field with a slim helper textarea
that captures a stray 'x' from CDP typing. Target fields by PLACEHOLDER,
never y-coordinates; clear stray 'x' values before SAVE or they may
corrupt the saved payload.
