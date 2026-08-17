# Write JavaScript (`write_js`) — `zw` API

Official: https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript.md

Use this block when no-code cannot express the step: npm packages, bulk
table writes, Playwright-level browser control, device-local secrets, or
custom error throws. Drawer: Monaco editor + **Run locally** checkbox.
Page JS can set the buffer with
`monaco.editor.getEditors()[0].getModel().setValue(code)`. cua-driver
UIA `set_value` on Monaco is a no-op — use the type_text recipe in
[creator-editor-automation.md](creator-editor-automation.md) only when
you must type into the drawer yourself. If a human is sitting in the
Write JS block, give them **one pasteable script** (see Authoring
below) — do not spend a cycle SendInput-ing thousands of characters.
In-page harvest (X/LinkedIn feed): leave **Run locally** unchecked
and `setValue` from the matching `templates/*_harvest.js`. Empty
unconnected Write JS nodes fail Detect errors — delete orphans;
keep one connected Write JS named **Harvest while scroll** on the
X canvas.

## Local vs browser execution

Code runs in the **browser context** unless you opt into local:

- Check **Run locally**, or
- Put `// @zw-run-locally` anywhere in the script (top is conventional).

| Surface | Browser | Local (`@zw-run-locally`) |
|---|---|---|
| `zw.getRef` / `zw.setRef` | Yes | Yes |
| `zw.deviceStorage.*` | Yes | Yes |
| `zw.delay` / `zw.log` / `zw.logTemp` | Yes | Yes |
| `zw.getTaskbotInfo` / `zw.getAgentInfo` | Yes | Yes |
| `zw.import` / `zw.packages.*` install | Use already-imported via `exposeFunction` | Yes |
| `zw.state.access()` / `zw.globalState.access()` | No — use `*.browser.getCopy` / `.commit` | Yes |
| `zw.state.clear()` / `zw.globalState.clear()` | Yes | Yes |
| `zw.browserContext.launch/quit/pages` | No | Yes |
| `zw.browserContext.getContextInfo` / `getDefaults` | Yes | Yes |

Thrown errors go to Run Reports (and email/Slack/webhook notifications) and
are catchable by Try-Catch. `console.log` is **not** persisted — use
`zw.log` / Log block / table write.

Old unprefixed `log()`, `delay()`, `setRef()`, `getRef()`, `activePage`,
`taskbotContext` still work. Prefer `zw.*` and
`zw.browserContext.getActivePage()` / `getContext()`.

`zw` also works in no-code inputs: `${…}` expressions and `$${…}` blocks
(must `return`). See [platform-primitives.md](platform-primitives.md).

Per-block min/max delay still fires **after** the script. Context cleanup
waits for that delay (1.1.68) so fire-and-forget async can finish.

### 1.1.75 revert knobs (current run only)

- `@zw-revert` — previous `zw.*` behavior in **browser** execution.
- `zw.temp.disableExtraBypass()`
- `zw.temp.disableExtraHeadlessBypass()`
- `zw.temp.disableExtraTimezoneBypass()`

## Variables and tables

```js
const email = await zw.getRef({ ref_id: 3623, name: "Email" });
await zw.setRef({ ref_id: 3624, name: "Email copy", value: email });
await zw.setRef({ ref_id: dgId, name: "title", value: String(text), appendIndex: i });
```

- `ref_id` = data-group id (Variables table or an attached table). `name`
  is case-sensitive.
- `value` **must be a string**. `JSON.stringify` on write, `JSON.parse` on
  read. A missing name errors the run.
- `appendIndex` is 0-based among **appended** rows and works **without** a
  loop (verified 20/20). Do **not** mix `appendIndex` with being inside a
  Start Repeat — the built-in loop index and custom append disagree.
- Read existing rows: Dynamic Start Repeat around the block, **or**
  `getRef` per known name. Variables are not rows — `item/` count stays 0.
- Always `await` `setRef` in browser execution or you write a Promise and
  get "value must be a string".
- There is no REST create-row ([rest-api.md](rest-api.md)). Local Write JS
  (`// @zw-run-locally`) may `fs.readFileSync` a **device** JSON and
  `setRef` it — useful only as a last resort when Agent Chrome has no
  site session and the rows already exist on disk. Do not commit that
  file. Prefer the in-page scrape once a sticky/cookie session exists.
- `appendIndex` rows that share an empty dedupe column collapse to one
  row at Remove Duplicates. Write a unique key per row.

## Device storage

```js
await zw.deviceStorage.get(key)      // string | undefined
await zw.deviceStorage.set(key, value) // strings only
await zw.deviceStorage.remove(key)
await zw.deviceStorage.has(key)
await zw.deviceStorage.getAll()
```

Survives agent restart and reinstall. **Never uploaded**. ~3,000,000 char
cap. Add secrets from the agent tray (Device storage → Add key) — do not
`set()` passwords in source. Log secrets with `zw.logTemp`, never `zw.log`.
Avoid `deviceStorage.get()` inside no-code dynamic inputs (many blocks
echo inputs into reports).

## State

| | `zw.state` | `zw.globalState` |
|---|---|---|
| Lifetime | This run | Until the agent quits |
| Local | `zw.state.access()` live object (any JS value) | `zw.globalState.access()` |
| Browser | `zw.state.browser.getCopy({key?})` / `.commit({state, key?})` | same under `zw.globalState.browser` |
| Clear | `zw.state.clear()` | `zw.globalState.clear()` |

Browser snapshots must be JSON-safe. ~3e6 char cap. Durable data belongs
in tables/variables or `deviceStorage`, not state.

## Utilities

```js
await zw.delay({ min: 1500, max: 2500 }); // ms; fixed if max omitted/equal
await zw.log("starting");
await zw.log({ message: obj, status: "success"|"fail"|"warning", tag: "scrape" });
await zw.logTemp(secret); // live view only, not reports
```

Persistent report message ~500 chars; live view ~500,000. Truncated, no throw.

## Metadata

```js
zw.getAgentInfo(); // { version, type: "API_KEY"|"DEFAULT"|"GUEST", id|null }
await zw.getTaskbotInfo();
// { id, name, runType: "immediate"|"scheduled"|"webhook",
//   currentRunResult, variables: {ref_id, variableNames},
//   tables: [{ref_id, name, type: "G_SHEETS"|"ZW_NATIVE", columnNames}],
//   webhookURL }
```

Names only — use `getRef` for values.

## Imports / packages (local)

```js
// @zw-run-locally
import dayjs from "dayjs@1.11.11";           // auto-install
const lodash = await zw.import("lodash@4.17.21", { isolate: true });
await zw.packages.list();
await zw.packages.uninstall(id);
await zw.packages.uninstallAll();
```

- `// @zw-disable-auto-import` to require explicit `zw.import`.
- Unused packages auto-removed after 1 week unless `uninstallIfUnusedFor: null`.
- `isolate: true` scopes the package to this TaskBot.
- Allowed: `"lodash"`, `"lodash@4.17.21"`, `"lodash/chunk"`, HTTPS git URLs.
  Rejected: tarballs, local paths, non-HTTPS git.
- Built-ins (not listed, not uninstallable): Node core, `axios@^1.6.6`,
  `playwright@^1.45.0`.
- Pure ESM packages are **not** supported (use a CJS fork or pin, e.g. `chalk@4`).
- Use a package in the **page** by importing locally and
  `context.exposeFunction` inside `onContextReady`. Exposed fns are always
  async in the page.

## Browser context (local)

Ways to get a browser: Open Link (auto-launch), Launch Browser block,
`zw.browserContext.launch()`, or in-browser Write JS (auto-launch of
current defaults). One **main** context at a time; Launch Browser /
`launch({policy:{makeMain:true}})` **replaces** it.

```js
// @zw-run-locally
await zw.browserContext.launch({
  launchConfig: {
    mode: "incognito", // or "sticky" + stickyProfileId
    bypassDetection: true,
    maximize: true,
    cookies: [/* {name,value,domain} */],
    scripts: [{ content: "/* before any page */" }],
    launchOptions: { headless: true, proxy: { server: "host:port" } },
    contextOptions: { viewport: { width: 1280, height: 720 } },
    onContextReady: async (ctx) => { /* every launch AND sticky attach */ },
  },
  runConfig: { keepAlive: false, bringToFront: true },
  policy: { makeMain: true, inheritDefaults: true, setAsDefaults: true },
});
const page = zw.browserContext.getActivePage();
await zw.browserContext.setActivePage(page);
await zw.browserContext.quit(); // { forceQuit: true } kills shared sticky
```

Other methods: `getContext()`, `getContextInfo()`, `getDefaults()`,
`setDefaults()`, `resetDefaults()`, `createPage({url})`, `listPages()`,
`isActivePage(page)`, `adoptContext(ctx)`,
`clearProfile` / `cloneProfile` / `listProfiles`.

Closing the last tab (Switch or Close Tab) **ends the context**. The next
Open Link launches fresh from **current defaults**.

Bypass detection: uploads ≳ 50 MB blocked; some launch/context options
ignored. SOCKS5 auth is not supported. Do not combine headless + keepAlive.
Sticky: one live browser per profile id; attach ignores browser-level
launch options.

## Authoring for a human in the Write JS drawer

The drawer buttons **Copy table or variable reference** and
**Copy AI instructions** exist so a human can paste the official
prompt into an agent and get a script back. That prompt is the
authoring contract. When the user pastes it (or is already
inside Write JS), follow it — do not invent a second `zw`
surface.

### Recognize the official prompt

It starts *"You are helping me write code for ZeroWork"* /
*"I am currently inside the Write JavaScript building block."*
Then it lists what the block can do, local vs browser, docs URLs,
getRef/setRef rules, and a **My references** footer. Treat that
paste as this section, not as a generic coding request.

### What the official prompt asserts

- `import` and `require()` auto-install (no `npm install`). That
  is **local-only**. Browser execution of `require` / `import`
  throws `ReferenceError: require is not defined`. To use a
  package in the page: import it in a **local** Write JS block
  and `context.exposeFunction` it; the next **browser** Write JS
  block can call that function.
- Default is **browser** (page DOM, `querySelectorAll`). Opt
  into local with `// @zw-run-locally` on its **own** first line,
  or tick **Run locally in the app**. A trailing pragma on a
  flattened one-liner is **not** honored.
- Browser-available: `getRef` / `setRef`, `deviceStorage.*`,
  `delay` / `log` / `logTemp`, `getTaskbotInfo` / `getAgentInfo`.
  Limited: packages (`exposeFunction`), state
  (`*.browser.getCopy` / `.commit`, not `.access()`),
  `browserContext` (`getContextInfo` / `getDefaults` only).
- `zw.setRef` `value` **must be a string**. `JSON.stringify`
  objects, `String(...)` everything else. Names are
  case-sensitive. Always `await` in browser mode or you write a
  Promise and get "value must be a string".
- `appendIndex: 0` is the first **appended** row (table already
  has 3 rows → that write is row 4). Do not put this block
  inside a Start Repeat when using `appendIndex`.
- Persist with `zw.log` / table writes. `console.log` is not in
  Reports.
- Drawer docs URLs often end in `-upcoming`. The live pages also
  exist without that suffix — append `.md` to any docs URL.

### My references (live ids)

The prompt ends with this shape (ids are **per bot** — never
copy example ids from another TaskBot):

```
My references:
  - Variables: ref_id: <id>, names: [<var>, …].
  - Tables:
    - Table "<table>": ref_id: <id>, names: "<col>", "<col>", ….
```

Use those `ref_id` + `name` values. Do not guess. If the
section is missing, `await zw.getTaskbotInfo()` and read
`tables[].ref_id` / `columnNames` / `variables.ref_id`.

### How to respond (official)

- ONE best solution. Not multiple speculative options.
- Code that is **directly pasteable** into the Write JS Monaco
  editor. Short comments only where they help.
- Correct `await`s. No extra complexity.
- Need packages, `zw.state.access()`, or
  `zw.browserContext.launch` / `getActivePage` → first line
  `// @zw-run-locally` (or tell the user to tick Run locally).

**Do not type the script in via cua-driver** when the user can
paste. SendInput drops `\n` (LF flatten → `func is not defined`
/ `r is not defined`), aborts on Unicode, and ignores a trailing
pragma. That path is a last resort in
[creator-editor-automation.md](creator-editor-automation.md)
(Monaco). `zw_canvas.js_crlf` / `js_lines_for_type_text` split a
file if you must type.

Pasteable harvest scripts (no account table ids — they call
`zw.getTaskbotInfo()` or take `TABLE` from **My references**):
[../templates/x_feed_harvest.js](../templates/x_feed_harvest.js),
[../templates/linkedin_feed_harvest.js](../templates/linkedin_feed_harvest.js).

Official pages (append `.md`):

https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/imports-and-package-management.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/write-and-read-variables-and-tables.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/local-and-global-state.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/device-storage.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/utilities.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/browser-context.md
https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript/metadata.md

## When to pick Write JS vs no-code

- List scrape of a simple repeating card → Save Web Element + `{loop_index}`
  (no JS). JS is faster when you already have `querySelectorAll` and want
  `setRef`/`appendIndex` in one block (Pattern 3).
- HTTP + transform + notify → Send HTTP / math / ChatGPT / Log (no JS).
- Need Playwright routes, npm, or device secrets → Write JS, run locally.
