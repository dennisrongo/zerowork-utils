# Block catalog — palette blocks, drawer fields, and quirks

44 palette blocks. UI names + canonical `type` strings: **references/node-types.md**.
This file: what each drawer contains and the field gotchas learned while configuring.

## Companion-pair rule

`loop`+`continue_after_repeat`, `try`+`after_try`+`catch` — the opener carries the
config; companions are flow structure with no drawers of their own. Drop/create the
opener; wire companions off it per the validator rules in rest-api.md.

## Drawer field reference

| Block | Drawer fields (placeholder / type) |
|---|---|
| Open Link | textarea[`https://example.com`]; "open in new tab" cb; min/max sec |
| Save Page URL | save-target picker |
| Switch or Close Tab | radios: switch/close × latest/prev/next/URL-match/tab# |
| Go Back or Forward | radios back/forward; min/max |
| Launch Browser | bypass bot detection, background, maximize, window size, cookies, proxy, browser engine, launch args, scripts, page visibility (tri-state) |
| Quit Browser | checkbox |
| Switch Frame | radios enter/exit frame; min/max |
| Browser Alert | textarea[response text]; min/max |
| Click Web Element | textarea[CSS/XPath]; skip-if-not-found cb; open-in-new-tab cb; min/max |
| Check Web Element | textarea[CSS/XPath]; timeout; TWO branch outputs (Found / Not Found) |
| Save Web Element | textarea[CSS/XPath]; Save-as select (Text / Link / **Custom attribute** + "Enter attribute" field / HTML / Image file URL); Save-to picker (table → column, two-step); skip-if-missing cb; min/max |
| Insert Text or Data | textarea[content] + spintax cb; no-Enter cb; optional selector textarea; typing speed radios (instant → VERY SLOW/SLOW/AVG/FAST/PRO) |
| Hover Web Element | textarea[CSS/XPath]; min/max |
| Select Web Dropdown | input[option]; textarea[dropdown selector]; min/max |
| Keyboard Action | key picker UI; min/max |
| Start Repeat | Loop-type radios: **Standard** (add rows / repeat actions — pre-selected) vs **Dynamic** (process table rows). Standard sub-radios: Fixed repetitions / Continue-until-no-element / Count-elements(selector); repetition count = INPUT placeholder `Enter number of repetitions` (NOT a textarea); Auto-scroll cb; Start-from (element number, optional) |
| Update Data | value textarea (empty = clear var); "Data to be updated" = two MUI selects (table → column/var) |
| Number Operations | operation select (Add/Subtract/Multiply/Divide/Remainder/Round/Round up/Round down/Random/Set decimals/**Remove format** — `1,500,500.2 → 1500500.2`); number field + number-to-operate-on (literal or ref); save-to |
| Format Data | format options + input + save-to |
| Split Text | separator + input + save-to |
| Apply Regex | 3 method radios: Extract matches / Check if pattern matches / **Replace text** (+ optional Replacement text); pattern textarea placeholder `/example/` — **patterns need JS delimiters** (`/£/` ✓, bare `£` ✗); Text-to-apply (literal or `{id, name}` ref); Save result to |
| Remove Duplicates | table picker; condition cb |
| Delete Data | table picker; scope |
| Ask ChatGPT | Model select (default "ChatGPT 5.5"); prompt textarea (placeholder "Example: Write an uplifting haiku…"); Save answer to (table/var). Refs interpolate in the prompt. |
| Send Notification | input[email]; textarea[subject]; textarea[body] |
| Send HTTP Request | Method select (GET default); URL textarea (placeholder `https://api.com`); HEADERS / REQUEST BODY (`{}`) / SAVE RESPONSE sections; Body instructions; min/max sec |
| Write JavaScript | **MONACO** editor — `monaco.editor.getEditors()[0].getModel().setValue(code)` (waits ~2.5s load); "Run locally" cb |
| Save File / Upload File | radios; min/max |
| Delay | min/max sec |
| Record Date | format + save-to |
| Take Screenshot | visible/full-page/element radios; png/jpeg; local folder |
| Save from Clipboard | save-to |
| Log | textarea[message] (refs interpolate: `Result: {id: <dg>, name: <var>}`); tag; status select (Success/Fail/Warning) |

## Save-to pickers (the fiddly part)

- Two-step MUI selects: table → column. The column step silently fails if the drawer
  closes mid-selection — reopen and redo. Error banner "A column or variable is
  required" = column never landed.
- Save-to lists ONLY tables attached to the current bot. Typing filters; no create-option.
- New REST-created columns are invisible until a full page reload (drawer caches at load).
- Scroll drawer to bottom before hunting MUI selects — fields near the drawer edge clip
  their listboxes.

## Stray-'x' trap

SaveWE/regex/HTTP drawers pair each field with a slim helper textarea that captures a
stray 'x' from CDP typing. Target fields by PLACEHOLDER, never y-coordinates; clear
stray 'x' values before SAVE or they may corrupt the saved payload.
