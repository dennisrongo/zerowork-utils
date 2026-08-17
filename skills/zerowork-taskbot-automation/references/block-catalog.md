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
almost no) drawers of their own. Catch / After-Try / Break / After-Repeat / Found / Not Found /
Abort Run: select+click often opens **no drawer**. That is expected,
not a failed open. Drop/create the opener; wire companions
**directly off it** (never after the last body block). Validator wording:
[rest-api.md](rest-api.md).

Branch-capable (may have more than one outgoing edge): Start Condition,
Start Repeat, Check Web Element, Start Try-Catch. Everyone else: one out.
Start Try-Catch is still capped at **THREE** connections (one body +
On Catch + After Try-Catch). A fourth wire fails Detect errors:
"The Start Try-Catch building block can have up to three connections...".

## Common browser-node drawer pattern

Selector-driven web blocks share: CSS/XPath selector + **Selector
options** collapsible + min/max sec + **V / T** insert helpers.
**Check Web Element** also has **Selector must be visible on screen**.
**Hover** does not.
Per-block min/max delay always fires **AFTER** the action. To delay
**before** Click / Save / Insert / Keyboard / Check, raise the
**preceding** block (or drop a Delay block). Selector timeout is not
delay: 30–60s is abandoned as soon as the element is found (does not
slow a hit).

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
  watch. **Bring Pages to Front** is a **run setting** (not a block)
  for watching those new tabs.
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
- **Config / drawer fields:** **Save current page URL to** table/variable
  picker. No min/max.
- **Wiring / companions:** Single-out. Place after Open Link / Click that
  landed on the page you want recorded.
- **When to use vs adjacent:** Current location. Save Web Element → Save-as
  **Link** for an element's `href`. Clipboard if the site only exposes Copy.
- **Gotchas:** Save-to lists only tables attached to this bot.

## Switch or Close Tab (`tabs`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/switch-or-close-tab.md
- **Purpose:** Activate or close a tab by latest / previous / next /
  URL-match / tab number.
- **Config / drawer fields:** Action **Switch** / **Close**. Target:
  **Latest** / **Previous** / **Next** / **Tab URL matching** (full /
  partial / regex — `/regex/flags`; invalid regex is treated as a
  literal, no error) / **Tab number** (default **1**, leftmost).
  Min/max.
- **Wiring / companions:** Single-out. After Open-in-new-tab, or to close
  leftovers. Closing the last tab **ends the browser context**; next
  browser action needs Open Link / Launch Browser or the run errors.
- **When to use vs adjacent:** Tab management. Not for iframes (Switch
  Frame). Not for history (Go Back or Forward).
- **Gotchas:** Tab number / latest / prev / next follow **creation order**,
  not visual order after a human drag. In "regular browser" / sticky-shared
  sessions prefer **URL matching**. Partial URL can over-match
  (`/windows` also matches `/windows/new`) — be specific (full URL or
  tighter path). Closing the active tab activates the
  next-right, else next-left. Tab-number switching (Tab **2** then
  back to Tab **1**) exists on live crawls — still prefer URL match.

## Go Back or Forward (`navigate`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/go-back-or-forward.md
- **Purpose:** Browser history back or forward.
- **Config / drawer fields:** radios **Go back** / **Go forward**. Live
  playground had **neither** selected (dead default footgun — Detect
  errors may stay quiet; set one before a client build). Min/max.
- **Wiring / companions:** Single-out.
- **When to use vs adjacent:** History. Prefer Open Link to a known URL
  when you can — more deterministic than history.
- **Gotchas:** No history entry = no-op, run continues. Unset radios
  (neither selected) is a dead default — the block will not navigate.

## Launch Browser (`launch_browser`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/launch-browser.md
  (not listed on the building-blocks hub).
- **Purpose:** Create (or replace) the browser context and optionally
  override Browser Launch Settings mid-run. Starts on `about:blank` — follow
  with Open Link. Subsequent no-code web blocks use this context.
- **Config / drawer fields:** Each group defaults to **Use current
  defaults**. Override: **Launch mode** Incognito vs Sticky (+ Sticky
  profile ID / COPY PROFILE ID); **Bypass bot detection**; **Run in
  background**; **Maximize**; **Window size** W×H; **Custom** profile
  field (1.1.75 — accepts plain text, expressions, or variable/table
  refs); **Cookies** JSON
  (`name`,`value`,`domain`) + ADD COOKIE; **Proxy** `host:port` or
  `socks5://host:port`, user/pass (HTTP only), bypass domains; **Browser**
  Default Chrome vs custom executable path; **Launch arguments**
  space-separated flags; **Scripts** path or inline content, reinjected on
  relaunch; **Stay on page after run**.
- **Wiring / companions:** Single-out. Usually the first block when
  settings matter. Pair with Quit Browser to tear down mid-flow. Overrides
  become the new runtime defaults until another Launch Browser reverses them.
  **Honest hole:** cookies / proxies / Launch Browser are **absent from
  this client's live bots**. Catalog fields remain; do not invent a
  client recipe.
- **When to use vs adjacent:** Need sticky / proxy / bypass / scripts
  without Write JS. Open Link alone is enough when defaults are fine.
  `zw.browserContext.launch()` for the full Playwright surface.
- **Gotchas:** Always becomes the **main** context (replaces an existing
  one). Sticky attach (profile already live): browser-level settings
  (background, bypass, size, engine, args) are **ignored**; cookies /
  scripts / page-visibility still apply. Bypass ignores window size, launch
  args, browser engine; blocks uploads ≳ 50 MB (the general Upload
  File cap is **390 MB**, 1.1.72 — both limits are true). Background + stay-on-page
  leaves an invisible browser. Closing the last tab ends the context.
  The live drawer is a long stack of tri-state radios (`Use current
  defaults` / `On` / `Off`); Stay-on-page is near the **bottom**. Click
  **On**, wait for Unsaved changes, then SAVE — a miss can close the
  drawer with no write.

## Quit Browser (`quit_browser`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/quit-browser.md
  (not listed on the building-blocks hub).
- **Purpose:** Close the browser this TaskBot is using. Often unnecessary —
  the agent closes Chrome at run end unless Stay-on-page is on.
- **Config / drawer fields:** **Force quit** checkbox (unchecked live).
  No min/max.
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
- **Config / drawer fields:** radios **Iframe** / **Main page**. Official
  docs say **Main frame**; live drawer may say **Main page** (same
  radio). Live playground had **neither** selected (dead default, same
  class as Go Back — Detect errors may stay quiet; set one before a
  client build). min/max **0/0**. Choosing Iframe reveals the iframe
  selector — docs require that selector, not just the Iframe radio
  (`iframe` or `#mce_0_ifr` on the-internet).
- **Wiring / companions:** Single-out. All following web blocks stay in
  that frame until Main frame / Open Link / Switch-or-Close Tab (those
  **clear** the frame). Nested iframes = chained Switch Frame blocks.
- **When to use vs adjacent:** Iframes only. A "selector not found" inside
  an embedded form/checkout/recaptcha is usually a missing Switch Frame.
  Pattern 8 hard case: Switch Frame (Iframe selected, selector
  `iframe` or `#mce_0_ifr`) then Insert Text `body#tinymce` on
  https://the-internet.herokuapp.com/iframe.
- **Gotchas:** Unset radios (neither Iframe nor Main page / Main frame
  selected) is a dead default — same class as Go Back. Missing iframe
  → error, stop. Increase selector timeout on in-frame Click/Save/Hover.
  Nested: you must walk each level.

## Browser Alert (`accept_dialog`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/browser-alert.md
- **Purpose:** Accept a native dialog (`alert` / `confirm` / `prompt` /
  `beforeunload`). Default platform behavior is **Cancel**.
- **Config / drawer fields:** optional **Prompt response** textarea
  (prompt only; ignored for alert/confirm/beforeunload). Live
  playground min/max **0/0**. No explicit Accept vs Dismiss control
  in the drawer. Palette card is **Browser Alert** — there is no
  Accept/Dismiss Dialog block (search "dialog" returns this).
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
  **open in new tab**; **Perform right-click**; **Use human-like clicking**
  (both often OFF); min/max; selector timeout in Selector Options.
- **Wiring / companions:** Single-out. Pair with Check Web Element when
  the target is optional. For file upload: Click the control, then Upload
  File. For download: Click, then Save File (from download action).
- **When to use vs adjacent:** Any clickable. Select Web Dropdown **only**
  if the control is a real `<select>`. Hover first if the target appears
  on hover. Native checkboxes are Clicks, not Insert Text (Pattern 8
  `#checkboxes input:nth-of-type(1)` on
  https://the-internet.herokuapp.com/checkboxes).
- **Gotchas:** Prove uniqueness with `querySelectorAll`. Custom-styled
  "dropdowns" (`div`/`button`) are Clicks, not Select. First-letters-cut
  on a following Insert Text → Click the field first. Per-block delay
  is AFTER this click — raise **this** block (not the next) to wait
  before the following action.
  Skip-if-not-found **off** + a missing selector is a catchable
  error (Pattern 4 uses `definitely-not-present-element` on
  purpose). Skip-if-not-found **on** swallows the miss without
  entering catch. Live Pattern 4: left click, human-like **off**.
  Pattern 8 checkbox: Click `#checkboxes input:nth-of-type(1)`
  on https://the-internet.herokuapp.com/checkboxes (native
  checkbox is a Click, not Insert Text).

## Check Web Element (`check`) — branches `element_present` / `element_absent`

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/check-web-element.md
- **Purpose:** Branch on whether a selector is in the DOM. **Found** =
  `element_present`, **Not Found** = `element_absent`. Those two are
  canvas branch markers, not standalone configurable blocks.
- **Config / drawer fields:** selector CSS/XPath; **Selector options**
  collapsible; **Selector must be visible on screen** checkbox; min/max
  sec. **V / T** insert helpers. Found and Not Found are **no-drawer**
  outcome marker cards (`element_present` / `element_absent`) — do not
  open a drawer on them. Branching is **edge wiring off Check**, not a
  drawer field.
- **Wiring / companions:** **Two outgoing edges** (Found / Not Found).
  Typical: Found → continue happy path; Not Found → Send Notification /
  Break Repeat / skip. Wire those edges off `check`; Found / Not Found
  cards have no config. Found / Not Found can **rejoin** at a later
  node (not only dead-end) — Pattern 11. A **dead-end** Found/Not Found
  (no outgoing edge) = skip row. **Inverted check:** presence of a
  waitlist `input[placeholder=Email]` means unavailable (Found is the
  skip) — Pattern 17.
- **When to use vs adjacent:** Presence of a **web element**. For "is this
  variable empty?" use Start/Set Condition **Data found / not found**. For
  "did the HTTP call return 200?" save status + Set Condition.
- **Gotchas:** Check timeout ≠ later block timeout. Official common
  problem: Check says Found, next Click/Save misses — race / overlay.
  Re-Check or Delay immediately before the action. Increase selector
  timeout to **30–60s** — unlike delay, timeout is **abandoned when
  the element is found**. **Must be visible on screen** diagnostic:
  Check + visible = Not Found → Keyboard-scroll the element into view
  (prove with a 30s Delay + manual scroll). Per-block delay is AFTER
  Check — raise the **preceding** block to wait before this Check.
  Increase timeout in iframes. Select+click on Found / Not Found opens
  **no drawer** — that is expected.

## Save Web Element (`save`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-web-element.md
- **Purpose:** Read public page data into a table/variable.
- **Config / drawer fields:** textarea CSS/XPath; **Save as** Text / Link
  / **Custom attribute** (+ "Enter attribute", e.g. `title` or `src` on a dialog `img`) / HTML /
  Image file URL; **Save to** two-step table → column **or Variables**
  ("Save to: Variables"); **skip if no
  element is found**; min/max.
- **Wiring / companions:** Single-out. Two first-class modes below.
- **When to use vs adjacent:** DOM text/attrs. Current URL → Save Page
  URL. Files → Save File. Clipboard-only sites → Save from Clipboard.
- **Gotchas:** Without `{loop_index}` a list Save always writes the
  **first** match. CSS `:nth-of-type({loop_index})` breaks on grid items
  under different parents — that is a `:nth-of-type` gotcha. The fix
  is CSS `>> nth={loop_index,1}` (or `>> nth={loop_index}` or live
  `>> nth={loop_index,0}`) / a
  correct `:nth-child({loop_index})` on the repeating `li`
  (`ol.row > li:nth-child({loop_index}) h3 a`), **not** XPath.
  **Prefer regular CSS selectors unless XPath is absolutely necessary.**
  Skip-if-not-found also prevents "continue until no element" from
  ending the loop (swallows the end condition — then you need
  auto-scroll or Break). Per-block delay is AFTER the save — raise
  the **preceding** block to wait before this Save.

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
- **Config / drawer fields:** **Content** textarea (`{id,name}` / `${}` /
  spintax); **Use spintax** CHECKED by default; **Don't press Enter on
  line breaks**; optional selector; typing-speed slider **PRO / FAST /
  AVERAGE / SLOW / VERY SLOW** (~65-90 wpm at FAST) — visible and
  load-bearing when **Insert instantly** is unchecked (human-like;
  Pattern 11). **Use spintax** is independent of the slider.
  **Insert instantly** checkbox (paste; selector required when on);
  min/max; **Encrypt content** (password — irreversible; delete and
  re-enter to change). **1.1.75 breaking:** default typing is slower
  (benchmarked human WPM). Keep the old speed with **Robotic, 0 delay**
  or **Insert instantly**.
- **Wiring / companions:** Single-out. Click the field first if the site
  swallows leading keystrokes. Pair with Keyboard Enter to submit if
  no-Enter is on.
- **When to use vs adjacent:** Text fields. Keyboard Action for shortcuts
  / Tab / Escape, not long strings. Encrypt + Insert for login when
  cookies/sticky are not an option.
- **Gotchas:** Instant-on → selector **required**. Instant-off → selector
  optional (types at caret; Wikipedia/Google often focus search). First
  letters cut off → Click first, slower speed, or Delay (raise the
  **preceding** block — per-block delay is AFTER Insert). Table ref empty
  → not in a Dynamic loop. Selector is the **INPUT**, not the label
  (Pattern 8: `#username` / `#password` on the-internet.herokuapp.com, not a client form).
  Number inputs still use Insert Text (`input[type=number]`). Iframe:
  Switch Frame first, then Insert Text on the inner document (`body#tinymce`).
  Shadow DOM (Pattern 8 /shadowdom): inspect whether the target is
  slotted light DOM vs inside shadowRoot. On
  https://the-internet.herokuapp.com/shadowdom, `<my-paragraph>`'s
  shadowRoot only contains `<slot name="my-text">`. The visible
  text lives in the LIGHT DOM as `<span slot="my-text">`
  (`span[slot="my-text"]`). A
  plain CSS selector reaches it — do **not** always Write JS
  for /shadowdom. If a future run shows no text change (span
  is not an input), then Write JS on
  `document.querySelector('my-paragraph').shadowRoot`
  (browser, not Run locally).

## Hover Web Element (`hover`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/hover-web-element.md
- **Purpose:** Hover so a tooltip / date / menu appears, then Save or Click
  it.
- **Config / drawer fields:** selector CSS/XPath; **Selector options**
  collapsible; min/max. **No** "Selector must be visible on screen"
  checkbox (that is Check-only). **V / T** insert helpers.
- **Wiring / companions:** Single-out. Hover → Save/Click the revealed node.
- **When to use vs adjacent:** Reveal-on-hover only. Not a substitute for
  Click.
- **Gotchas:** Revealed nodes often need a slightly longer timeout.

## Select Web Dropdown (`select`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/select-web-dropdown.md
- **Purpose:** Choose an `<option>` in a native `<select>`.
- **Config / drawer fields:** **Dropdown option** (text/value); selector
  of the dropdown (must be a `select` tag); **Selector options**
  collapsible; min/max. **V / T** insert helpers.
- **Wiring / companions:** Single-out.
- **When to use vs adjacent:** Real `<select>` only. Custom `div`/`button`
  "dropdowns" → Click (open) + Click (option), or Keyboard.
- **Gotchas:** Wrong tag = silent failure / not-found. Option can be a
  variable/table ref. Needs the `<select>` selector **AND** the option text
  (Pattern 8: `#dropdown` + `Option 2`).

## Keyboard Action (`keyboard`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/keyboard-action.md
- **Purpose:** Fire a key or combo: Enter, Tab, Shift+Tab, Escape,
  arrows, letters, Ctrl/Cmd+C (Meta = Ctrl/Cmd in the UI).
- **Config / drawer fields:** key picker; min/max.
- **Wiring / companions:** Single-out. Focus the target first (Click or
  Insert). Tab × N + Enter can replace brittle selectors on simple forms.
- **When to use vs adjacent:** Shortcuts, dismiss popups (Escape), reload
  (Meta+R), scroll fallback (Space / ArrowDown), form Tab-through. Keyboard **Space** also forces lazy LinkedIn sections (Pattern 14). Keyboard Enter sends a Facebook Thread composer DM (Pattern 15 — no submit button). Long
  text → Insert Text. Native browser chrome (Ctrl+P print, Ctrl+F find,
  Cmd+S save-as, maximize) **does not work**.
- **Gotchas:** Shift+Tab order is Shift **then** Tab. Tab twice = **two separate Keyboard blocks** (one block can look like a shortcut).
  Common-problem page: nothing happens = no focus, or the site eats
  keys. Not a substitute for Click on custom widgets. Empty key field
  can pass Detect errors but the scrape still fails — Page down to
  load more must be **PageDown** (or End). Per-block delay is AFTER
  the key — raise this block (or the preceding one) to wait before
  the next action.

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
    dates). 18 operators: `=` `≠` `<` `>` `≤` `≥`; **Contains / Does not
    contain** (official: comma-separated **keywords** — this IS the
    keywords operator, not a live-only extra; UI may label it Contains
    keywords); Data found (not empty) / Data not found (empty); Longer than /
    Shorter than (char length only — a second-text operand is invalid
    since 1.1.61); Before (Date) / After (Date) + **days
    shift** (pos or neg); Is a valid number / Is not a valid number;
    **ELSE** ("if no other condition is met"). Pick the Start Condition
    reference via **My references**.
- **Wiring / companions:** Start Condition is **branch-capable** (N Set
  Condition blocks off it). Each Set Condition is **single-out**. Chain
  another Start/Set pair for AND-across-fields. Always include **ELSE** ("if no other condition is met")
  if you need a fallback. Message-cap (Pattern 13): EQUALS `{id, name: MessageCount}` -> Break Repeat; ELSE continues.
- **When to use vs adjacent:** Data/variable tests. Web-element presence
  → Check Web Element. Regex true/false → Apply Regex "Check if pattern
  matches" then condition on the result. Driver-table gating: an `isActive`
  column + EQUALS `true` (Pattern 15) enables/disables targets from the table.
- **Gotchas:** Numeric `<` `>` throw on non-numeric strings (`TEST123 > 50`
  errors; `51.77 > 50` is fine). Sanitize first (math **Remove format**,
  or regex). Date formats on both sides **must match**. **Before/After
  is exclusive of the shifted day:** 10 Jul + 3 days → comparison date
  is 13 Jul; After matches **14+** (not 13+); Before matches **12-**.
  Equal-to-shifted-date does **not** match. Deactivating a
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
  element is found**; **Count elements matching selector** + **Lead selector** (Pattern 16 `section main a[href*="/p"]`; Pattern 17 `a[href*=products]` + Save WE `a[href*=products] >> nth={loop_index,0}`).
  Optional **Start from** (element/row number). **Auto-scroll** checkbox
  — **default ON** in all loop setups except Dynamic (1.1.61). Disable
  it if you already Keyboard / Write-JS scroll (do not stack). Official
  auto-scroll page is a stub. **Auto-continue from last row or element**
  (resume across runs).
  Dynamic extras: **Newest rows first (reverse order)** checkbox;
  optional **Start from** row; optional **repetition limit**. Bind
  the existing table via **My references** — dropdown **labels can
  be stale** (hidden numeric ref id is truth); never paste another
  bot's table id. Sheets Additional options: write-batch size
  (default 50) and **real-time sync** (1.1.69).
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
  - Auto-scroll official page is a stub; default ON except Dynamic.
    Fails on some virtual lists (Keyboard fallback). Disable if you
    already custom-scroll.
  - Auto-continue: Dynamic = next **row**; Standard = next **list
    selector**. `Start from` is a floor.
  - Loop type can be **UNSET** (neither Standard nor Dynamic
    selected). Detect errors may stay quiet. Set **Standard**
    before a client build (live Pattern 4 footgun).

## After Repeat (`continue_after_repeat`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/after-repeat.md
- **Purpose:** Run once after a loop finishes (notify, Click Next, start
  a second independent loop in the same bot — Pattern 17 phase-2 Dynamic,
  or a loop-exit email digest).
- **Config / drawer fields:** None (flow structure).
- **Wiring / companions:** **Must be wired directly off Start Repeat**
  (its second output). Validator: "must be preceded by a single Start
  Repeat". For pagination, After Repeat hangs off the **inner** loop, then
  Click Next, then the outer loop continues.
- **When to use vs adjacent:** Post-loop work. Deactivating Start Repeat
  skips the body and continues at After Repeat.
- **Gotchas:** Never chain it after the last Save in the body.
  Select+click often opens **no drawer** (no configurable fields).

## Break Repeat (`loop_exit`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/break-repeat.md
- **Purpose:** Leave the **current** loop early (no more results, HTTP
  status ≠ 200, DM counter hit the cap).
- **Config / drawer fields:** None — select+click often opens **no drawer**.
- **Wiring / companions:** Single-out. Typically under a Set Condition or
  Check Not-Found **inside** the loop. Execution continues at After Repeat
  (if any).
- **When to use vs adjacent:** Exit this loop, keep the bot running.
  Abort Run kills the **whole** run. Raise Error / throw fails the run
  (catchable).
- **Gotchas:** Breaks the innermost loop only. Wire off a Set
  Condition (or Check Not-Found), **not** after the last body
  block. Select+click often opens **no drawer**.

## Run TaskBot (`run_taskbot`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/run-taskbot.md
  (agent **≥ 1.1.75**; not on the building-blocks hub).
- **Purpose:** Start another TaskBot from this one (sub-bot). Optionally
  wait; optionally pass variable values.
- **Config / drawer fields:** **Select a TaskBot** dropdown (your bots),
  or **Custom** id (literal / ref / `${}`). Variable name/value pairs
  (only listed vars change). **Wait until the TaskBot finishes**
  checkbox — **CHECKED = sync**; uncheck = fire-and-forget. **No min/max
  delay.** Persist-value is a setting **on the child variable**, not
  here (off = this-run-only).
- **Wiring / companions:** Single-out. Wrap with Try-Catch if Wait is on
  (child fail / manual stop throws here). Concurrent Runs on the child
  lets several parents call it in parallel.
- **When to use vs adjacent:** Structured sub-bot. Webhook+HTTP is the
  older "fire and forget another bot" path (no wait, uses
  `zw_webhook_data`).
- **Gotchas:** Recursion A→B→A is rejected. Wait-off: child errors do
  **not** surface here. Stopping a parent stops wait-on children (and
  their children). No depth cap besides recursion.
  **Honest hole:** this client's live bots have **zero** `run_taskbot`
  nodes. Live substitute = Pattern 17 (two-phase collect then Dynamic
  enrich). Catalog fields remain; do not invent a client recipe. A
  variable-only bot can look child-shaped; nothing calls it.

## Start Try-Catch (`try`), After Try-Catch (`after_try`), On Catch Error (`catch`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/try-catch.md
- **Purpose:** Swallow a step failure and continue. Body after `try` is
  the protected scope. On error, jump to `catch`. After success **or**
  catch, continue at `after_try`.
- **Config / drawer fields:** Opener may include **"Save error message to"** a table column (e.g. `Error`)
  so the failing row keeps the exception text (Pattern 13 outreach).
  Catch and After Try-Catch have **no drawer** — select+click often
  opens nothing. That is expected.
- **Wiring / companions:** `catch` AND `after_try` **both wire directly
  off `try`**. Never `try → body → catch` or `catch → after_try`.
  At most THREE connections total: one body + On Catch + After
  Try-Catch. A Write JS sibling off Try (fourth wire) fails Detect
  errors: "The Start Try-Catch building block can have up to three
  connections...". Valid JS demo: Wait for timeline → Harvest while
  scroll → Scrape scope (try) → (Scroll rounds | catch | after_try).
  Verified: failing click with try-catch → Success/0 errors; without →
  run error. Catch is a **dead-end on purpose** in the Pattern 4 proof (no outgoing edge).
  Do not wire `catch → log` for that proof. The continue path is `try → after_try → Log`.
  Outreach (Pattern 13) may let catch **rejoin** the same Delay as the happy path.
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
- **Config / drawer fields:** optional message (live default **"A custom error was raised."**);
  checkboxes **Mark this TaskBot run as failed in the run report** and
  **Include this error in the error report** (both **unchecked** live). Write JS `throw new Error("...")` is the
  documented equivalent.
- **Wiring / companions:** Single-out. Place inside a try body to force
  the catch path.
- **When to use vs adjacent:** Intentional failure. Abort Run stops
  **without** treating it as a catchable step error in the same way —
  use Abort when you just want out. Log + Abort if you only need a
  breadcrumb.
- **Gotchas:** Official page is a stub. Live defaults leave both report
  checkboxes off — turn them on if you want the run / error report to
  record the raise. Prefer Write JS `throw` when you need a precise
  custom message beyond the default.

## Abort Run (`abort`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/abort-run.md
- **Purpose:** Stop the **entire** run immediately (critical data missing,
  hard cap reached and you do not want After Repeat).
- **Config / drawer fields:** **No drawer** — no configurable fields.
  Select+click opens nothing. That is expected. Palette card is
  **Abort Run** (LOGIC), not "Abort / Stop TaskBot".
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
  Doubles as a **cross-table cell copier**: dest := `{id, name: Section}`
  from another table (via **My references**). Reset-to-empty at the top
  of an iteration so a stale value cannot leak into a selector.

## Number Operations (`math`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/number-operations.md
  and https://docs.zerowork.io/using-zerowork/using-building-blocks/number-operations/example-standardize-different-formats.md
- **Purpose:** Arithmetic and numeric cleanup.
- **Config / drawer fields:** operation select: **Add** (also concatenates
  strings) / Subtract / Multiply / Divide / Remainder / Round / Round up /
  Round down / **Random** (default range 0–1e9; 1.1.72 checkbox
  **Generate a whole number (no decimals)**) / **Set decimals** /
  **Remove format** (`1,500,500.2` → `1500500.2`; also `1.000.000,23` →
  `1000000.23`; mixed grouping errors). Number field + number-to-operate-on
  (literal or ref); save-to.
- **Wiring / companions:** Single-out. Increment a counter variable each
  loop (Pattern 13 message-cap: **Add** 1 onto `{id, name: CurrentMessageCount}`); Remove format **before** numeric Set Condition.
- **When to use vs adjacent:** Numbers. Format Data for text. Regex for
  extract-then-math.
- **Gotchas:** Empty operand → skip, continue. Non-numeric input to any
  op except Add → error, stop. Remove format is the sanitizer for prices.
  Live Pattern 5: **Multiply** `fx_x100` × **2.5**, write back to
  `fx_x100`. Pick `{id, name: fx_x100}` via **V / My references**.

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
- **Config / drawer fields:** Live playground empty default shows only
  **Text to split** table/variable picker. After a source is chosen,
  official fields: separator; positions → destinations. Positions
  1-based from the start; **negative** from the end (agent
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
  picker for refs. A **deactivated** Extract-matches twin may sit beside
  live Write JS as documentation (`deactive`) — Pattern 17.

## Remove Duplicates (`remove_duplicate_rows`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/remove-duplicates.md
- **Purpose:** Batch-dedup a table. Default keeps **oldest** rows.
- **Config / drawer fields:** table picker; **key column** (specify one — faster);
  **Preserve newest** rows (native tables only, not Sheets). File columns
  are ignored in the comparison.
- **Wiring / companions:** Single-out. Place **after** the scrape loop.
  Native tables: still runs **once** even if placed inside a loop.
  Sheets (1.1.69): **can run every iteration** — do not put it inside
  a Sheets loop unless you want per-row dedup.
- **When to use vs adjacent:** After Save Lists. Prevent-rerun while
  iterating = Update Data status + condition, not this.
- **Gotchas:** Always specify a column unless you have a reason not to.
  If every row's comparison value is empty, **all rows are duplicates of
  each other** and one remains. Populate the key column (e.g. `post_urn`)
  before this block.

## Delete Table Data (`delete_table_data`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/delete-data.md
- **Purpose:** Delete **all rows** (overwrite-before-scrape) or **one
  row** (current Dynamic-loop row, e.g. disqualified lead).
- **Config / drawer fields:** Live playground empty default shows only
  **Delete from** table/variable picker. Official / live modes: **Delete all rows** vs
  **Delete current row in a loop** (current Dynamic-loop row — queue shrinks
  so re-runs never re-message; Pattern 13).
- **Wiring / companions:** All-rows: **before** the Standard loop. One-row:
  inside Dynamic loop under a Set Condition.
- **When to use vs adjacent:** Wipe or prune. Clear a variable = Update
  Data with empty value, not this.
- **Gotchas:** All-rows is permanent. Export CSV first if you might care.
  **Truncate-then-refill** (Delete all rows first, Pattern 17) vs
  **Delete current row in a loop** (Pattern 13 queue). On a Sheets-linked
  table, Delete all rows clears the spreadsheet ("Delete Spreadsheet
  Data" is just this mode on the linked table).

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
  Live Pattern 5: model **ChatGPT 5.5** (`gpt-5.5`); prompt
  `Classify this number as HIGH or LOW in one word, nothing else: {fx_x100}`;
  answer → variable `gpt_answer`. Pick the dest with **V / My
  references**.

## Send Notification (`email`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/send-notification.md
- **Purpose:** Email **the account owner** (not arbitrary recipients).
- **Config / drawer fields:** **Subject**; **Email content**
  (plaintext and/or minified HTML); min/max. **No To: field.** Sends
  to the signed-in account email (drawer copy says the email will be
  sent there). Not an arbitrary recipient. Subject/body accept
  `{id, name}` tokens via **My references**. Palette card is **Send
  Notification** (EXTERNAL), not "Email" / "Send Email".
- **Wiring / companions:** Single-out. After Check Not-Found, After Repeat,
  or a failure branch. Loop-exit digest (After Repeat → email) is the
  cheap "run finished" signal (Pattern 17); per-row alert stays inside
  the loop.
- **When to use vs adjacent:** Self-alert. Other recipients → Send HTTP to
  an email API. Run-level Slack/webhook notifications are TaskBot
  Settings, not this block.
- **Gotchas:** Per-minute rate limit inside Start Repeat. Standard footer
  is appended.

## Send HTTP Request (`update_or_configure_api`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/apis-send-http-request.md
- **Purpose:** Arbitrary HTTP. Browserless pipelines start here.
- **Config / drawer fields:** Method (GET default); URL textarea
  (`https://api.com`); HEADERS (secrets as `Bearer {id, name}`
  variable tokens — never a literal); REQUEST BODY (`{}`); SAVE
  RESPONSE has **three independent slots**: body → Variables or a table;
  **multiple Nested record path** entries, e.g.
  `data.records[0]['fields']['Job URL']` or `choices[0]['text']`;
  **Save response status code** → table column; **full object** save
  (1.1.69 — not only nested paths). Each slot is optional;
  min/max.
- **Wiring / companions:** Single-out. Create dest columns first. Replace
  `"` → `'` in dynamic JSON bodies (Format Replace). Condition + Break
  on status ≠ 200. Can POST to another bot's webhook.
- **When to use vs adjacent:** Any HTTP API. Ask ChatGPT for OpenAI chat.
  Write JS `axios` only when the drawer cannot express the call.
- **Gotchas:** Flat JSON keys match column names exactly; extras ignored;
  **no matching columns = no save, no error**. Trailing-slash sensitivity.
  Auto-retry on 429 / network timeout (1.1.61). Verified GET → downstream
  math works.
  Empty **SAVE RESPONSE** (body, nested path, and status code **all empty**) = the HTTP call is a **no-op**. Detect errors can stay quiet while the API result is discarded (live Pattern 5 **footgun**,
  GET `https://api.frankfurter.app/latest?from=USD&to=GBP`, no headers,
  no body). Fill SAVE RESPONSE or the GET is discarded. Multiple
  Nested record paths are first-class (Pattern 11). Status-code
  dest is optional. Filling **only** **Save response status code** is
  intentional (Pattern 19 link-rot checker) — body and nested paths
  empty on purpose, unlike Pattern 5's accidental no-op. **The JSON
  path can become the variable name**
  (Pattern 16: dest token `{id, name: choices[0].message.content}`).

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
  `// @zw-run-locally`). Drawer buttons: **Copy table or variable
  reference**, **Copy AI instructions**. The AI-instructions prompt
  includes **My references** (`ref_id` + column names) — authoring
  contract in [write-javascript.md](write-javascript.md).
- **Wiring / companions:** Single-out. Throws are catchable and land in
  reports. `console.log` is **not** persisted.
- **When to use vs adjacent:** Bulk `setRef`/`appendIndex`, npm,
  Playwright, device secrets. Prefer no-code for list scrape / HTTP /
  conditions.
- **Gotchas:** Local vs browser matrix, string-only refs, do not mix
  `appendIndex` with Start Repeat. `require` / `import` in browser
  throws `require is not defined`. When a human is in this drawer,
  one pasteable script — do not SendInput
  ([write-javascript.md](write-javascript.md) "Authoring for a
  human"). Do **not** hard-code `tableRefId` or a test URL — resolve
  via `zw.getTaskbotInfo()` / **My references**, and use the URL you
  just saved. Strip `"` from values interpolated into a hand-written
  JSON HTTP body so the JSON stays valid (Pattern 19).

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
- **Config / drawer fields:** tip "Make sure to initiate the upload by clicking the 'Upload' button in the previous step."
  File source radios **From file URL** / **From folder path on your computer** —
  live playground had **neither** selected. Detect errors **names the node** if File source is unset. min/max.
  Official examples treat the folder-path option as a **file pathname**.
- **Wiring / companions:** **Click the upload control first**. Chooser is
  invisible during the run.
- **When to use vs adjacent:** Page uploads. A file column/variable can
  be referenced via **From file URL** (Upload FAQ). Save File cannot
  write a file column (path/URL → standard column). Creating a
  file-column value in the table UI is still a table action.
- **Gotchas:** Hard cap **390 MB** (1.1.72; does not apply to downloads).
  Bypass detection **also** blocks uploads ≳ 50 MB — both limits are
  true. **From folder
  path on your computer** is the **Agent machine**, not the creator browser. Prefer **From file URL** for a portable demo (`https://raw.githubusercontent.com/github/gitignore/main/README.md`). Detect errors
  **names the node** if File source is unset. Requires a prior Click
  on the file input (`#file-upload`). From file URL also accepts a
  file-column / variable ref.

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
- **When to use vs adjacent:** Explicit wait **before** the next action.
  Per-block min/max on other nodes fires **after** that node — raise
  the **preceding** block (or use this Delay) for selector / Insert-cutoff
  races. `zw.delay` is milliseconds.
- **Gotchas:** Empty field → block **skipped**. max < min → wait min.
  Both 0 → no pause. Invalid ref → skipped.

## Record Date (`insert_date`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/record-date.md
- **Purpose:** Write a formatted now/offset date into a var/column for
  later Before/After conditions.
- **Config / drawer fields:** **Select date format** dropdown (nothing
  selected live). No min/max. Official page is thin; dest/save-to
  may appear after a format is chosen. Palette card is **Record
  Date** (TOOLS), not "Insert Date".
- **Wiring / companions:** Single-out. Pair with Set Condition Before/After
  (same format both sides; days shift lives on the condition).
- **When to use vs adjacent:** Structured dates. Write JS `Date`/`dayjs`
  for fancy timestamps.
- **Gotchas:** Mismatched formats make Before/After wrong. 1.1.63 fixed a
  timezone bug — keep the agent current. **insert_date as a run stamp:**
  Calendar date, MM/DD/YYYY, **Today** → Date Added (Pattern 17).

## Take Screenshot (`screenshot`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/take-screenshot.md
  (stub; fields from live drawer + release notes).
- **Purpose:** Capture visible / full page / element as png or jpeg to a
  local folder; optionally save the path.
- **Config / drawer fields:** **Visible page** / **Full page** / **Web
  element**; **.png** / **.jpeg**; folder path placeholder
  `/Users/<your-username>/Downloads`; **File options** collapsible
  (same unique-on-conflict / custom name / save-path as Save File);
  min/max. Max wait default 2 minutes.
- **Wiring / companions:** Single-out. Upload File via saved path.
- **When to use vs adjacent:** Pixels. Save Web Element for text/HTML.
- **Gotchas:** Path → standard column, not file column.

## Save from Clipboard (`save_clipboard`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/save-from-clipboard.md
- **Purpose:** Read the OS clipboard into a var/column.
- **Config / drawer fields:** **Save copied text to** table/variable
  picker. No min/max. Palette card is **Save from Clipboard**
  (TOOLS), not "Save Clipboard" / "Copy to Clipboard".
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
  secrets. Reports do not store `console.log`. Persistent log messages
  are capped at **5,000 per run** (1.1.61).

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
  Auto-align top-to-bottom can yank sticky notes into a row. Place
  notes after node layout, or skip auto-align once notes are placed.

## Sticky note (`sticky_note`)

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/building-block-options/sticky-notes.md
- **Purpose:** Canvas comment / grouping. Not executed. Markdown as of
  1.1.75.
- **Config / drawer fields:** note text.
- **Wiring / companions:** None.
- **When to use vs adjacent:** Documentation on the canvas. Log is for
  run-time messages. On client bots sticky notes are **load-bearing**
  (selector history, AM/PM branch intent) — not decoration.
- **Gotchas:** Not executed. Do not POST `sticky_note` expecting a run
  step. Markdown rendering is agent ≥ 1.1.75. REST-create stays
  `"Write a note..."`; fill with
  [../scripts/zw_fill_notes.py](../scripts/zw_fill_notes.py)
  (label click or yellow double-click). `data.name` stays `None`.
  Sit the note **next to** the node it documents, not in a top row.
  Drag by the **top strip** only — a text-body drag selects text;
  interactivity / lock off pans the pane instead of moving the note.
  Palette drag-and-drop is flaky: drops in the far-left canvas often
  produce nothing. Create the note in the mid/right canvas, type
  text immediately, then drag by the **top strip** to the target
  node. An empty note is discarded if you click away before typing.
  When the react-flow control bar (zoom/fit/sticky-note drag) sits
  below a 1280×800 viewport, palette sticky notes are unreachable
  (live: Demo - HTTP + Math Pipeline). Workaround: each node's
  speech-bubble icon (bottom-right of the card) → "Write a note…"
  → SAVE. That attaches a note beside the node. Empty notes still
  discard on click-away.

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
  count** for validator structure (class `deactive`, skipped at run). The
  canvas **lies** about what runs — a wired Save / Write JS with
  `deactive` is skipped. Skip a loop = deactivate Start Repeat
  (continues at After Repeat). Skip try = deactivate Start Try-Catch
  (continues at After Try-Catch).
- **When to use vs adjacent:** Temporarily mute a path without deleting
  edges. **Destructive nodes left deactivated = production hygiene**
  (Follow / Post / Send / Delete-all test sub-flow — Patterns 14, 16).
  A Delay block is an explicit wait **before** the next action;
  per-block delay is **after** — raise the preceding block, not the
  failing one.
- **Gotchas:** Deactivating a Start Condition **and** its Sets makes the
  next path **random**. Multi-select: Shift+drag or Cmd/Ctrl+click.
  Randomizing inter-block delays (3–15s example) can greatly slow the run.

Internal canvas types also include `fake` and `delete` (not user-facing).

---

## Drawer field cheat-sheet (automation)

| Block | Drawer fields (placeholder / type) |
|---|---|
| Open Link | textarea[`https://example.com`]; "open in new tab" cb; min/max sec |
| Save Page URL | Save current page URL to picker; no min/max |
| Switch or Close Tab | Action Switch/Close; Target Latest/Previous/Next/Tab URL matching (full/partial/regex)/Tab number (default 1); min/max |
| Go Back or Forward | radios Go back/Go forward (live default NEITHER — dead default footgun); min/max |
| Launch Browser | bypass bot detection, background, maximize, window size, Custom profile field (plain text / expr / refs, 1.1.75), cookies, proxy, browser engine, launch args, scripts, page visibility (tri-state), sticky/incognito |
| Quit Browser | Force quit checkbox (unchecked live); no min/max |
| Switch Frame | radios Iframe / Main page (docs: Main frame; live drawer may say Main page); iframe selector required when Iframe selected (`iframe` or `#mce_0_ifr`); live default NEITHER — dead default, same class as Go Back; min/max 0/0 |
| Browser Alert | optional Prompt response textarea; min/max 0/0; no Accept vs Dismiss control; palette label Browser Alert |
| Click Web Element | textarea[CSS/XPath]; skip-if-not-found cb; open-in-new-tab cb; Perform right-click; Use human-like clicking; min/max |
| Check Web Element | selector CSS/XPath; Selector options; must-be-visible cb; min/max; Found/Not Found are **no-drawer** markers (edge wiring, not a field) |
| Save Web Element | textarea[CSS/XPath]; Save-as (Text / Link / Custom attribute + "Enter attribute" / HTML / Image file URL); Save-to table column or Variables; skip-if-missing cb; min/max |
| Insert Text or Data | Content textarea; Use spintax CHECKED by default (independent of speed); Don't press Enter; optional selector; speed slider PRO/FAST/AVERAGE/SLOW/VERY SLOW when instant unchecked; 1.1.75 default slower — Robotic 0-delay or Insert instantly; Insert instantly cb; min/max |
| Hover Web Element | selector + Selector options + min/max; NO must-be-visible cb |
| Select Web Dropdown | Dropdown option; dropdown selector; Selector options; min/max |
| Keyboard Action | key picker UI; min/max |
| On Catch / After Try-Catch / Break Repeat / After Repeat / Found / Not Found / Abort Run | **No drawer** — select+click often opens nothing |
| Raise Error | optional message (default "A custom error was raised."); Mark run failed in run report cb; Include in error report cb (both unchecked live) |
| Start Repeat | Standard vs Dynamic; Fixed / Continue-until-no-element / Count-elements; repetition INPUT `Enter number of repetitions`; Auto-scroll default ON except Dynamic; Start-from; Auto-continue; Dynamic: Newest rows first (reverse), repetition limit, table via My references (label can be stale); Sheets Additional: batch 50 + real-time sync |
| Start / Set Condition | Start = value picker; Set = 18 operators + operand / ELSE ("if no other condition is met"); Contains = comma-separated keywords; Before/After exclusive of shifted day |
| Update Data | value textarea (empty = clear); two MUI selects; Use spintax cb |
| Number Operations | Add/Subtract/Multiply/Divide/Remainder/Round/Round up/Round down/Random (whole-number checkbox 1.1.72)/Set decimals/Remove format; operands; save-to |
| Format Data | Remove word / Replace / Shorten / case / Normalize URL / Trim / line breaks / smileys; input; save-to |
| Split Text | live empty default: only Text to split picker; then separator + positions |
| Apply Regex | Extract / Check / Replace; pattern `/example/`; Text-to-apply; Save result to |
| Remove Duplicates | table picker; column; Preserve newest (native only); native once / Sheets every iteration (1.1.69) |
| Delete Data | live empty default: only Delete from picker; official all vs one |
| Ask ChatGPT | Model select; prompt textarea; Save answer to |
| Send Notification | Subject; Email content; min/max; no To: field (signed-in account email) |
| Send HTTP Request | Method; URL; HEADERS (Bearer {id, name}); BODY / SAVE RESPONSE three independent slots (body / nested paths / Save response status code) + full-object save (1.1.69); min/max |
| Write JavaScript | MONACO; Run locally cb |
| Save File | source radios; folder/path; file options; min/max |
| Upload File | previous-step Upload-button tip; From file URL / From folder path on your computer (live NEITHER); 390 MB hard cap + Bypass ~50 MB; min/max |
| Delay | min/max sec |
| Record Date | Select date format dropdown (nothing selected live); no min/max |
| Take Screenshot | Visible page/Full page/Web element; .png/.jpeg; folder `/Users/<your-username>/Downloads`; File options; min/max |
| Save from Clipboard | Save copied text to picker; no min/max |
| Log | textarea[message]; tag; status (Success/Fail/Warning); 5,000 messages/run |
| Run TaskBot | Select a TaskBot dropdown; Wait until finishes CHECKED=sync / uncheck=fire-and-forget; no min/max |

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
