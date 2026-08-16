# ZeroWork Creator — Editor Automation Reference

Verified Aug 15, 2026 against creator.zerowork.io (React + MUI + React Flow, Monaco editor), using a throwaway demo bot in a test account.

## Editor layout
- Left: block palette, grouped (BROWSER / WEB INTERACTION / LOGIC / DATA / EXTERNAL / FILES / TOOLS). ~45 blocks, each a `[draggable=true]` MUI card. Two search inputs: "Search by ID, name or type" (bottom-left, searches canvas nodes) and "Search blocks" (top-right, filters palette).
- Center: React Flow canvas. Each node = a block, `data-id` = numeric ZeroWork ID. Nodes have 4 handles: `a` top (target), `b` left (target), `a` bottom (source), `b` right (source).
- Config drawer opens CENTER-screen (≈x 500-950), not right side. Common mistake: filtering for "right panel" inputs and finding nothing.
- Toolbar (top-right, y<40): Run (`aria-label="Run"`), Detect errors, Schedule, Webhook, Reports, Browser launch settings.
- Bottom-left: React Flow controls; includes Auto-align buttons ("Auto-align top to bottom" / "left to right") — tooltip/hover spans, the clickable element is the `.react-flow__controls-button`.

## Adding a block (synthetic drag — works headless of tab visibility)
```js
const item = [...document.querySelectorAll('[draggable=true]')]
  .find(d => (d.innerText||'').replace(/\n/g,' ').includes('Open') && ...includes('Link'));
const zone = document.querySelector('div.invisible-drop');  // canvas drop overlay
const dt = new DataTransfer();
const mk = (type,x,y) => new DragEvent(type,{bubbles:true,cancelable:true,clientX:x,clientY:y,dataTransfer:dt});
item.dispatchEvent(mk('dragstart',100,300));
zone.dispatchEvent(mk('dragenter', r.x+300, r.y+200));
zone.dispatchEvent(mk('dragover',  r.x+300, r.y+200));
zone.dispatchEvent(mk('drop',      r.x+300, r.y+200));
item.dispatchEvent(mk('dragend',   r.x+300, r.y+200));
```
- The palette's own dragstart sets `application/reactflow` = snake_case type. Verified: `open_link`. Extract others by intercepting `DataTransfer.prototype.setData` during a synthetic dragstart on each palette card.
- The app's drop handler lives on `div.invisible-drop` (class literally `invisible-drop`), NOT the standard react-flow wrapper.
- Each successful drop: creates the node AND auto-opens its config drawer. Drop coordinates influence initial node position but NOT execution order (edges do).
- IMPORTANT ORDERING BUG: the drop→configure→SAVE pattern configures the NEWEST node. If you re-drop a block to reopen its drawer and then delete "the duplicate", you may delete the configured one. Sequence: re-drop → configure new → SAVE → delete the OLD node id.

## Configuring a block
- Fields: React prototype setters, not `el.value=`:
```js
const setter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set;
setter.call(el, 'value'); el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true}));
```
- Open Link: `textarea[placeholder="https://example.com"]`.
- Save Web Element: `textarea[placeholder="Enter CSS or XPath selector"]`; "Save as" is a MUI Select (Text/Link/HTML/Custom attribute/Image file URL); "Save to" is a MUI Autocomplete whose popup is easily clobbered by a stale listbox — Escape the old menu FIRST. Synthetic typing + Enter/blur was NOT reliably committing the Autocomplete (unresolved; workaround = use a Write JavaScript block instead).
- Write JavaScript: Monaco. Wait ~2.5s after drop ("Loading..."), then:
```js
monaco.editor.getEditors()[0].getModel().setValue(code)
```
  Docs buttons in that drawer: "Copy table or variable reference" and "Copy AI instructions" (env docs for the zw.* API — worth grabbing on next session; click copies to clipboard, clipboard read needs permissions).
- Log: first visible textarea = "Log message".
- SAVE button: text 'SAVE', bottom of drawer. Success toast: "Updated successfully". Unsaved banner: "Unsaved changes".

## Connecting blocks (the hard part)
- Synthetic MouseEvent/PointerEvent sequences and calling the app's `onConnect` prop directly DO NOT create edges (onConnect dispatches a collab-layer message that didn't apply when tried; d3-drag needs trusted input).
- WORKING METHOD: trusted CDP input, tab must be VISIBLE:
  1. `list_tabs()` → find the editor target → `switch_tab(targetId)` → confirm `document.visibilityState === 'visible'`. Hidden tabs break trusted input entirely (browser-use's `cdp()` routes to the bound target, but the throttled/hidden page drops the drag).
  2. Get handle centers via getBoundingClientRect.
  3. CDP drag:
```python
cdp('Input.dispatchMouseEvent', type='mouseMoved', x=sx, y=sy)
cdp('Input.dispatchMouseEvent', type='mousePressed', x=sx, y=sy, button='left', buttons=1, clickCount=1)
for i in range(1,9):  # interpolate sx,sy -> tx,ty
    cdp('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y, buttons=1); time.sleep(0.06)
cdp('Input.dispatchMouseEvent', type='mouseReleased', x=tx, y=ty, button='left', buttons=0, clickCount=1)
```
- Direction matters: edges must go top→bottom (or left→right). A right-to-left edge = "connected backwards" = still counts as disconnected. Use Auto-align first, then connect in visual order.
- Node drags (repositioning) also need the same trusted CDP drag on the node body. A CDP node-drag can grab the WRONG node if coordinates are stale — re-read rects immediately before dragging.

## Deleting nodes
- Each node has an × button (first `button` in the node) — synthetic click works. BUT: hover-revealed in some states; after a React-setter save + tab switch a node can render with NO button in the DOM (persisted-but-broken). Recover by deleting neighbors and rewiring, or delete the orphan if it is unused.
- App's own delete path: ancestor fiber of the react-flow div exposes `onNodesDelete` → dispatches `D("delete", {triggered:true, data:{ids, prevNodes, prevEdges}})`. Not needed if × buttons work.
- "Undo delete" appears after deletions.

## Running + results
- Run button → validation first ("Checking for disconnected blocks or missing input data"). Failure: lists offending block IDs. Success: browser window opens via desktop agent, blocks execute in edge order, progress streams at body tail.
- Verified run: Open Link → Write JavaScript ("Browser execution / Executed custom JavaScript code") → Log ("Scrape finished") → "Your TaskBot ran successfully." ~5s.
- `/reports` shows step statuses + duration only. Write JavaScript console.log output was NOT found in the report UI or in `%APPDATA%/ZeroWork/Local Storage/leveldb` — if you need extraction output persisted, write it to a ZeroWork table or use Send Notification instead of console.log/return.
- Agent must be running (`localhost:9990`) or Run fails.

## browser-use CLI notes
- `switch_tab(targetId)` rebinds js()/cdp() AND may reset page render state — re-query nodes after switching.
- `click_at_xy` = SCREEN coordinates, hits the user's foreground app if automation tab isn't frontmost. Avoid in this workflow.
- `agent_helpers.py` in the workspace is NOT auto-imported — `exec(open('agent_helpers.py').read())`.
- Long inline grep one-liners with multiple `-o` patterns can be rejected as a malformed payload — write a script file or split the command.
