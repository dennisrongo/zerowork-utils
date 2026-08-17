# Platform primitives — selectors, variables, tables, dynamic inputs

Official index: https://docs.zerowork.io/llms.txt. Distilled 2026-08-16 from the
Using Selectors, Using Variables, Using Tables, and Dynamic Inputs pages. REST
create/attach facts stay in [rest-api.md](rest-api.md); this file teaches how
ZeroWork the product uses those primitives when a TaskBot runs.

## Selectors

Official hub: https://docs.zerowork.io/using-zerowork/using-selectors.md

A selector is the address of a web element. Every web-interaction block
(Click / Check / Save / Insert / Hover / Select dropdown / Keyboard-with-target)
takes CSS, XPath, or ZeroWork-only text/nth filters. Wrong or non-unique
selectors are the #1 "No selector is found" failure.

### Copy vs custom

- Copy (DevTools Copy → Copy selector / Copy XPath, or ZeroWork's copy-selector
  helper) is enough on stable sites (Wikipedia-class). Prefer custom selectors
  on "tricky" sites (LinkedIn, Facebook, SPAs) whose generated class hashes
  change.
- Always prove a CSS selector in the page console **before** the first run:
  `document.querySelectorAll("YOUR_SELECTOR")`.
  - 1 match → unique, good for a single-element action.
  - N matches → a list (use `{loop_index}` / `>> nth=`), **or** not unique
    enough for a single click/save.
  - 0 matches → typo or wrong quotes (use single quotes inside the attribute
    brackets).
- ZeroWork-only syntax **cannot** be checked with `querySelectorAll`:
  `text=…`, `text="…"`, `>> nth=`, `>> text=`. Those are runtime filters.

### Anatomy of a CSS selector

Structure: `tag[attribute='value']` (no space before `[`). Multiple attributes
stack: `button[class='pure-button'][type='submit']`.

- **Exact match** `=` — the whole attribute value must equal the string.
- **Loose match** `*=` — the attribute contains the substring. Prefer this
  when class lists grow (`button[class*='pure-button']`).
- **Strict hierarchy** `>` — immediate child. `body > div > form > button`.
- **Loose hierarchy** space — descendant anywhere below. `body button`.
- Mix them: `body > div button[class*='pure-button']`.
- Siblings sit on the same DOM level (a list of `li`s). Do not chain them
  with `>`; address them as a list (`:nth-child` / `>> nth=`) or with sibling
  combinators (`+`, `~`).

### Element text (ZeroWork-only)

- Exact, case-sensitive: `text="Start a post"`.
- Loose contains: `text=people follow this` (no quotes) — use when a number
  or other token changes (`1,456 people follow this`).
- Combine with CSS via a trailing filter only:
  `div[role='main'] >> text="Like"`.
  `>>` **must be at the end**. `div >> text="Like" > span` is invalid.

### Incremental list selectors

Copied list items increment a number:

```
li:nth-child(1) > … > span
li:nth-child(2) > … > span
```

Replace the increment with `{loop_index}` (see Start Repeat):

```
li:nth-child({loop_index}) > … > span
```

**Prefer regular CSS selectors unless XPath is absolutely necessary**
(readability). Official docs treat CSS as the default and XPath as
advanced. Official incremental example:
`main#main li:nth-child({loop_index}) > …`

Two official methods:

| Method | Example | Index base | Console-checkable? |
|---|---|---|---|
| `:nth-child(N)` | `li:nth-child({loop_index}) a[data-anonymize='person-name']` | **1-based** | Yes (`querySelectorAll`) |
| `>> nth=N` (ZeroWork filter) | `a[data-anonymize='person-name'] >> nth={loop_index,1}` | **0-based** (`0` = first) | **No** |

Prefer `:nth-child({loop_index})` on the **repeating sibling** when you
can (console-checkable). `>> nth=` is easier (you don't have to find the
incrementing ancestor) but less precise and not console-checkable.

Official whole-list forms for `>> nth=` are slightly inconsistent:
lists page writes `{loop_index,1}`; Standard Loop writes
`>> nth={loop_index}`. Encode both. The nth filter itself is 0-based
(`0` = first). Prefer `:nth-child({loop_index})` to avoid the
ambiguity.

**Verified gotcha (this skill):** CSS `:nth-of-type({loop_index})`
**breaks when matches live under different parents** (product grids).
It found item 1 then hard-failed. That is a gotcha about
`:nth-of-type`, not a reason to use XPath. The fix is `>> nth=`
on the global match list, or a correct `:nth-child` on the repeating
`li`:

```
ol.row > li:nth-child({loop_index}) h3 a
article.product_pod >> nth={loop_index,1}
```

(`>> nth={loop_index}` is the Standard Loop wording of the same
filter.) Live client confirmation of the CSS-first official form:
lead selector + `>> nth={loop_index,0}` (0-based; `0` = first),
e.g. `a[href*=products] >> nth={loop_index,0}` (Pattern 17).
Encode `{loop_index,0}` alongside `{loop_index,1}` /
`>> nth={loop_index}`. Grids stay CSS. XPath is last resort, not
"because it's a grid".

Without `{loop_index}`, Save Web Element always grabs the **first**
match (20 identical rows).

CSS `{loop_index}` does **not** fix virtualized / remounting feeds
(X, LinkedIn). Those stay Write JS (Pattern 7).

### `{loop_index}` syntax (Standard loop)

Official: Start Repeat → Standard Loop.

| Syntax | Meaning |
|---|---|
| `{loop_index}` | Current iteration (1-based when used inside `:nth-child`) |
| `{loop_index,2}` | Start counting from element 2 |
| `{loop_index,1,2}` | Start at 1, skip 2 each step (odd items: 1, 3, 5…) |
| `{loop_index_123}` | Index of the Start Repeat whose node id is `123` (parent loop, for nested row×column tables) |

`>> nth=` is 0-based (`0` = first). Official whole-list forms:
lists page `{loop_index,1}`; Standard Loop `>> nth={loop_index}`;
live client `>> nth={loop_index,0}` (Pattern 17).
`:nth-child` is 1-based — prefer it when you can pin the repeating
sibling.

### XPath (advanced / last resort)

ZeroWork auto-detects XPath when the selector starts with `//`. You can also
prefix `xpath=//button`. Same `{loop_index}` substitution as CSS. Official
docs treat XPath as advanced. **Prefer regular CSS selectors unless XPath
is absolutely necessary.** Allowed only when CSS + ZeroWork filters
(`text=` / `>> text=` / `>> nth=` / `:nth-child`) cannot express the
address: ancestor/following axes, or complex predicates CSS cannot
write. Not "because it's a grid".

### Uniqueness rule of thumb

- Single-target action (click this button): **exactly one** match.
- List scrape: **N identical-shape matches**, then `{loop_index}` to walk them.
- Prefer stable attributes (`data-*`, `aria-label`, `type`, role) over hashed
  CSS modules. Prefer loose `*=` over exact class soup.

### Find a selector (live page)

Do this **on the page the TaskBot will see** — usually Agent Chrome after
login, not only a tab in Creator Chrome. A selector that works while you
are signed in can return 0 in the agent's incognito window.

1. **Iframe first.** If the control sits in an iframe, Switch Frame
   before any Click/Save. A "selector not found" on an embedded
   form/checkout is usually a missing Switch Frame, not a bad CSS string.
2. **Inspect, don't trust Copy selector.** Right-click → Inspect. Walk
   up from the text node to the smallest element with a **stable** hook:
   `data-testid`, `data-urn`, `aria-label`, `role`, `name`, `type`.
   Chrome's Copy → Copy selector often emits a long `:nth-child` chain
   that dies on the next render. Copy XPath is the same class of
   brittle — rewrite as CSS `:nth-child` / `>> nth=` before falling
   back to XPath.
3. **Harvest candidates in the console** (page JS, on that document):

   ```js
   (function (root) {
     const rows = [];
     root.querySelectorAll("[data-testid],[data-urn],[aria-label],[role]").forEach((el) => {
       const hook = el.getAttribute("data-testid")
         || el.getAttribute("data-urn")
         || el.getAttribute("aria-label")
         || el.getAttribute("role");
       if (!hook) return;
       const sel = el.dataset.testid
         ? `[data-testid="${el.dataset.testid}"]`
         : el.getAttribute("data-urn")
           ? `[data-urn="${el.getAttribute("data-urn")}"]`
           : el.getAttribute("aria-label")
             ? `[aria-label="${el.getAttribute("aria-label")}"]`
             : `[role="${el.getAttribute("role")}"]`;
       rows.push({ tag: el.tagName.toLowerCase(), sel, n: root.querySelectorAll(sel).length });
     });
     return rows.filter((r, i, a) => a.findIndex((x) => x.sel === r.sel) === i)
       .sort((a, b) => a.n - b.n)
       .slice(0, 40);
   })(document);
   ```

   Prefer hooks whose `n` matches the job (1 for a click, N for a list).
4. **Prove** with `document.querySelectorAll(sel)` (CSS only). Then
   prove **inside one card**: `card.querySelector(inner)` so a list
   scrape does not grab the first page-wide match every row.
5. **Pick the block:**
   - Stable repeating grid, same parent shape → Save Web Element +
     CSS `{loop_index}` (Pattern 1): pin
     `ol.row > li:nth-child({loop_index}) h3 a`, or
     `article.product_pod >> nth={loop_index,1}`.
   - Next/page numbered UI → nested loops (Pattern 2 / 9).
   - Virtualized / infinite feed (cards unmount on scroll: LinkedIn,
     X/Twitter, Facebook) → Write JS. Collect **while scrolling**; a
     selector that matches 8 cards at the top can match 0 after the
     virtualizer recycles the DOM. Do **not** use `{loop_index}` here.
     CSS `{loop_index}` does **not** fix virtualized X feeds.
6. **When you have no page JS** (cua-driver on Creator Chrome cannot
   `execute_javascript` in standard mode): UIA names are not CSS. Open
   the **target site** in a tab you can console, or drop a temporary
   Write JS that `zw.log`s `querySelectorAll(sel).length` and run it
   on Agent Chrome. `query_dom` only sees simple tags (`article`,
   `a`, `button`) — not `[data-testid]`.
7. **ZeroWork copy-selector helper** (drawer button) is official; treat
   its output like DevTools Copy — rewrite hashed/nth chains before
   SAVE. Unverified as an automation target this session.

**Infinite / virtualized scroll (Write JS):** keep a `Set` of stable
ids (`data-urn`, `/status/123`). Each round: read currently mounted
cards → add unseen ids → scroll → `zw.delay` 1–2s. Stop when **no new
ids** for 2–3 consecutive rounds **or** you hit a cap (e.g. 40).
Writing only after the last scroll misses everything the virtualizer
already unmounted. Dedup column = that same id, never empty.

How to tell a feed is virtualized (do not use `{loop_index}`):

- Mounted card count stays roughly constant while you scroll (8–15
  `article`s) even though more posts exist.
- Cards sit in recycle wrappers (`[data-testid="cellInnerDiv"]` on X,
  `occludable-update` on LinkedIn) that unmount off-screen.
- There is no Next / page-number control — only more content as you
  scroll, sometimes a **Show more posts** / **Retry** chip.

**Find the real scroller.** `window.scrollBy` / `document.body.scrollHeight`
is a no-op on many X layouts. Walk up from
`[data-testid="primaryColumn"]` (or the first card) until
`overflow-y` is `auto|scroll|overlay` **and**
`scrollHeight > clientHeight + 80`. Also `scrollIntoView` the last
mounted card. Click **Show more posts** / **Retry** when present.

**Prove pagination worked** (not just "N cards exist"):

```
scroll round 1 mounted=6 added=6 total=6
scroll round 2 mounted=7 added=5 total=11
scroll round 3 mounted=6 added=4 total=15
```

`rounds > 1` **and** `added > 0` after a scroll is the proof. Log that
string with `zw.log` so Live Runs shows it. A single harvest after one
`scrollTo(bottom)` is not infinite-scroll handling.

**X/Twitter stable hooks** (prefer these over hashed classes):

| Job | Selector |
|---|---|
| Card | `article[data-testid="tweet"]` |
| Recycle wrapper | `[data-testid="cellInnerDiv"]` |
| Author block | `[data-testid="User-Name"]` |
| Body | `[data-testid="tweetText"]` |
| Stable id | `a[href*="/status/"]` → `/status/(\d+)` |
| Time | `time[datetime]` |
| Counts | `[data-testid="reply"|"retweet"|"like"|"views"]` `aria-label` |
| Login wall | `/i/flow/login`, `[data-testid="loginButton"]` |

Harvest **inside** the card (`card.querySelector(...)`) so engagement
counts do not leak from the first tweet on the page.

8. **Temporary probe block.** When you cannot open DevTools on Agent
   Chrome, a one-shot Write JS that only
   `zw.log(document.querySelectorAll(sel).length)` + `location.href`
   is the cheapest selector proof. Delete it after.

**cua-driver / Monaco note:** `type_text` drops `\n`. Flatten harvest
JS to one line and do **not** start it with `//` (that comments out
the rest). Tick **Run locally** if you need `require`/`fs`; a trailing
`// @zw-run-locally` on a one-liner was not honored.

## Dynamic inputs

- **Official:** https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs/references-to-variables-and-tables.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs/code-in-inputs.md
  https://docs.zerowork.io/using-zerowork/using-building-blocks/dynamic-inputs/spintax.md
- **Purpose:** Every building-block input accepts three kinds of dynamic
  value so you do not hard-code what the run already knows.
- **Config / drawer fields:** Insert refs via the **V** / **T** buttons
  (top-right of a drawer). Code via `${…}` / `$${…}` in any text field
  (agent ≥ 1.1.72). Spintax checkbox on Update Data (off by default) and
  Insert Text or Data.
- **Wiring / companions:** Not a block. Works inside any configured
  drawer field. Code always runs **locally**.
- **When to use vs adjacent:** Refs for table/variable values. `${}` for
  a one-liner (`zw.deviceStorage.get`, `Math.random`). `$${}` when you
  need `import` / `return`. Spintax only for anti-spam unique copy.
- **Gotchas:** `{id, name}` inside code is replaced *before* JS runs —
  wrap it in quotes or use `zw.getRef`. Prefer the V/T picker over
  hand-typed refs. Agent must be ≥ 1.1.72 for code-in-inputs.

Every building-block input accepts three kinds of dynamic value.

### 1. Variable / table references — `{id, name}`

Click **V** (variables) or **T** (tables) at the top-right of a drawer to
insert a reference. The stored form is:

```
{id: <dataGroupId>, name: <columnOrVariableName>}
```

Example in a message body:

```
Hello {id: 123, name: "Profile name"}, I wanted to reach out because…
```

- `id` is the **data-group id** (the Variables table, or an attached native /
  Sheets table), not the TaskBot id.
- `name` is the column / variable name.
- Prefer the V/T picker over hand-typing. A hand-typed ref in Regex "text to
  apply" produced a run error in one live test; the picker is the verified path.
- New REST-created columns do not appear in already-open drawers until the
  editor page is reloaded (drawers cache the list at load).
- Interpolation also works in Log messages:
  `Result: {id: <dgId>, name: <var>}`.
- **Variable interpolated inside a CSS selector** is first-class:
  `{id, name: CurrentSubSectionID} + ul + p a` (regex-extracted hash
  + sibling combinators). Reset the variable each iteration so a
  stale value cannot leak. Pick the ref with **V / My references**.

### 2. Code in inputs (Desktop Agent ≥ 1.1.72)

All code runs **locally on the device**.

| Form | Meaning |
|---|---|
| `${…}` | Expression. The result is inserted. |
| `$${…}` | Code block. Must `return` a value. Can `import` (auto-installs locally). |

Examples:

```
${await zw.deviceStorage.get("password")}
${Math.random()}
${(await zw.getRef({ ref_id: 1234, name: "Country Code" })).trim().toUpperCase()}
```

`{id: 1234, name: Country Code}` inside code is **not** a JS object — ZeroWork
replaces it with the value first. To treat that value as a string inside code,
wrap it in quotes or read it with `zw.getRef`.

### 3. Spintax

Randomly pick one alternative. Useful against anti-spam uniqueness checks.

```
{ Hi | Hey | Howdy }! How { are you | are things going }?
{hi|hello|hey|howdy}
```

Officially supported in **Update Data** (opt-in checkbox **Use spintax**,
off by default) and **Insert Text or Data** (spintax checkbox in the drawer).

## Variables vs tables

Official: https://docs.zerowork.io/using-zerowork/using-variables.md
and https://docs.zerowork.io/using-zerowork/using-tables.md

### When to use which

| Use a **variable** | Use a **table** |
|---|---|
| One value that changes during the run (counter, flag, last URL, cleaned price) | Many rows (scrape results, input lists, CRM exports) |
| Loop-independent state (a DM-limit counter that increments each iteration) | Data that should persist as a list after the run |
| Temporary scratch that you interpolate into later blocks | Anything you will Dynamic-Loop over |

Worked official example: cap outbound DMs at 30 per run → variable
`DM counter` + Number Operations (+1 each iteration) + Start/Set Condition
(`< 30`). A table of 30 counter rows would be the wrong model.

### Variable runtime facts (verified)

- Every bot auto-gets a "Variables" table (`is_autogenerated: true`).
- Creating a variable = adding a column on that table
  (`POST /data_group/<varsId>/column/` `{name: 'price_raw'}`).
- Variables are **runtime refs, not rows**: `get_count` / `item/` on the
  Variables table return 0 even after successful Update Data writes. Verify
  by interpolating the ref into a Log message.
- `zw.setRef({ref_id, name, value})` / `zw.getRef({ref_id, name})`. Value
  must be a string. Writing a missing variable name errors the run.

### Three ways to add a table

1. **Native table** — created in ZeroWork. REST:
   `POST /data_group/` `{name, type: 'NATIVE', columns: [{colName}…], connector_id}`.
   Tables are **per-TaskBot**. There is no attach-existing-table route (405).
   Always create fresh per bot.
2. **Google Sheet** — paste a Sheet link, authenticate. Columns come from
   the Sheet; after adding columns in Sheets, click **Refresh / Refetch
   columns from Google Sheet**.
3. **CSV import** — creates a **native** table from the file's columns, or
   appends/overwrites an existing native table. Column matching is by name,
   case-insensitive; order and filename do not matter. Non-matching columns
   are ignored. Default is append; checkbox **overwrite current data**
   permanently deletes existing rows first (export CSV first if you care).

### Native vs Google Sheets

| | Native | Google Sheets |
|---|---|---|
| Reliability | Streamlined with TaskBot runs | Subject to Google quota / outages |
| Rename a column | All block refs **auto-remap** | Must remap (or refetch; deleted columns drop refs) |
| Share outside ZeroWork | Export CSV | Share the Sheet |
| UI | 50 rows/page | Full Sheets UI |
| Max cells | 1,500,000 | 10,000,000 |
| Max chars/cell | 50,000 | 50,000 |
| Duplicate TaskBot | New table id | New table id, **same Sheet URL** |

Sheets writes are batched (default every 50 rows; adjustable on Start Repeat
additional options). Parallel TaskBots on Sheets are the usual quota-killer.
Deleted / de-authed Sheet → run refuses to start.
A **Sheets-backed table can exist without a Sheets *block*** — Sheets is a
**table property**, not a building block (Pattern 18). Sidebar → Tables:
grey grid = native; **green Sheets icon** = linked. Kebab: **Edit Google Sheets link** / **Remove from this TaskBot** / **Delete table** / **About this table** (Table ID, Created, Sheets URL, Selected sheet, Used in
TaskBots). Ordinary save / update_variable / delete_table_data write
through and sync. "Delete Spreadsheet Data" is just delete_table_data
all-rows on the linked table. A bot can **mix** plain native tables and
Sheets-linked tables. Loop either with Start Repeat Dynamic like a
native table (Pattern 15 / 18). There is no Google Sheets palette node.
Never bake a Sheets URL.

### Convert native → Google Sheet

**Irreversible.** Table id stays the same so block refs survive if column
names still match (case-insensitive). Native rows are **permanently deleted**
on convert — export CSV first. You cannot convert back.

### Standard vs Dynamic loop (data model)

- **Standard loop** — **appends new rows**. Ignores existing table data.
  Use for "save this list of profiles/products". In-loop Format/Update acts
  on the row being appended this iteration.
- **Dynamic loop** — **iterates existing rows**. Use for "visit every
  profile link already in the table and enrich it". Open Link points at the
  row's URL column; Save Web Element writes extra columns on the **current**
  row.

Overwrite-a-list: Delete Data (or CSV overwrite) **before** the Standard
loop, not after. Dedup: Remove Duplicates **after** the loop.

## Wiring primitives (validator)

Repeated here because they constrain every scenario, not just one block.
Full REST wording: [rest-api.md](rest-api.md).

1. Exactly **one starting block** (no incoming edge). Orphans after a delete
   = "more than one starting building block".
2. Non-branch blocks: **one outgoing edge**. Branch-capable:
   Start Condition, Start Repeat, Check Web Element, Start Try-Catch.
3. **After Repeat** wires **directly off Start Repeat** (2nd output), never
   after the last body block.
4. **On Catch Error** and **After Try-Catch** both wire **directly off
   Start Try-Catch**, never off the try-body or each other.
5. Set Condition (`conditionNode`) has **one** output. Multi-branch = N Set
   Condition blocks off one Start Condition, including an **ELSE** ("if no other condition is met").
6. Deactivated nodes still count for structural rules.
7. Empty required fields are named by node id.

## Detect errors / Run / verify

- **Detect errors** (toolbar) is the same pre-run validator that blocks Run.
  Trust the node ids it names.
- Runs are **UI-triggered** (`aria-label="Run"`) or Scheduler / Webhook
  (agent must be logged in + machine awake). No REST run trigger
  (`/execution/run/` 404).
- Verify: `GET /execution/?page=1` → `result`, `errors_count`,
  `run_duration`, `connector_name`. Plus table `item/get_count/` (success
  can still mean catch swallowed a scrape throw) and Log / Live Runs
  text. Item JSON is `cells[].text` + `column_id`, not a flat `data`
  object — [rest-api.md](rest-api.md). Per-step log text has no REST
  endpoint. There is no REST create-row.
- Duration signature: ~1s success = browserless (or everything skipped);
  7–17s+ = a real browser phase. See [run-semantics.md](run-semantics.md)
  and [run-and-platform.md](run-and-platform.md).
