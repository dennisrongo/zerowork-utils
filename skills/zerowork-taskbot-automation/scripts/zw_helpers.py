"""ZeroWork creator UI automation helpers for browser_exec sessions.

Usage in a browser_exec call:
    exec(open('zw_helpers.py').read())   # after copying this file into the
                                        # browser-use workspace

Then:
    zw_harvest(['Open','Link'])                 # drop + dump drawer + delete
    zw_drop_capture(['Write','JavaScript'])     # drop (returns payload string)
    zw_dump_drawer()                            # JSON of open drawer
    zw_delete('<nodeId>')                       # delete node by data-id
    zw_canvas_ids()                             # current node ids
    zw_set_textarea("document.querySelector('textarea')", 'value')
    zw_save_drawer()                            # click SAVE + check toast
    zw_connect(src_id, tgt_id)                  # trusted CDP drag (tab must be VISIBLE)
    zw_run()                                    # click Run toolbar button

Auto-align DOES exist: bottom-left React Flow controls
(".react-flow__controls-button", tooltips "Auto-align top to bottom" /
"left to right"). Prefer that over guessing canvas coordinates — a click
near (214,876) hits "toggle interactivity", not align. Official:
docs.zerowork.io/.../building-block-options/auto-align.md

Edges: prefer REST POST /connector/<id>/edge/ over CDP. The creator is not
"no API" — node/edge/table/rename are REST; drawer SAVE is websocket-only.

Paired-Chrome / no page-JS: use zw_cua.py (cua-driver UIA). Do not use this
file's zw_run() from Playwright — that Chrome is unpaired ("Agent offline").
"""

def zw_edge_payload(source_id, target_id, source_handle="a", target_handle="a"):
    """REST body for POST /connector/<botId>/edge/. Full object or the API 400s."""
    src, tgt = str(source_id), str(target_id)
    return {
        "id": "reactflow__edge-%s%s-%s%s" % (src, source_handle, tgt, target_handle),
        "source": src,
        "target": tgt,
        "sourceHandle": source_handle,
        "targetHandle": target_handle,
        "type": "buttonEdge",
        "deletable": False,
        "zIndex": 1,
    }


def zw_auto_align_selectors():
    """Official Auto-align controls (they exist). Do not click raw (214,876)."""
    return {
        "button": ".react-flow__controls-button",
        "top_to_bottom": "Auto-align top to bottom",
        "left_to_right": "Auto-align left to right",
    }


def zw_canvas_ids():
    return js("Array.from(document.querySelectorAll('.react-flow__node')).map(n => n.getAttribute('data-id'))")

def zw_drop_capture(match_parts, dx=300, dy=250):
    """Synthetic HTML5 drag palette -> invisible-drop zone.
    match_parts: list of innerText fragments, e.g. ['Open','Link'].
    Returns (status, payload_string). Payload/type strings: references/node-types.md"""
    conds = " && ".join(["(t||'').includes('%s')" % p for p in match_parts])
    body = (
        "(() => {"
        "window.__zwPayload = null;"
        "const orig = DataTransfer.prototype.setData;"
        "DataTransfer.prototype.setData = function(type, val) { if (type === 'application/reactflow') window.__zwPayload = val; return orig.call(this, type, val); };"
        "try {"
        "const drags = Array.from(document.querySelectorAll('[draggable=true]'));"
        "const item = drags.find(d => { const t = (d.innerText||'').replace(/\\n/g,' '); return %s; });"
        "const zone = document.querySelector('div.invisible-drop');"
        "if (!item || !zone) return 'missing:' + (!item ? 'palette' : 'zone');"
        "const r = zone.getBoundingClientRect();"
        "const dt = new DataTransfer();"
        "const mk = (type, x, y) => new DragEvent(type, {bubbles: true, cancelable: true, clientX: x, clientY: y, dataTransfer: dt});"
        "item.dispatchEvent(mk('dragstart', 100, 300));"
        "zone.dispatchEvent(mk('dragenter', r.x + %d, r.y + %d));"
        "zone.dispatchEvent(mk('dragover',  r.x + %d, r.y + %d));"
        "zone.dispatchEvent(mk('drop',      r.x + %d, r.y + %d));"
        "item.dispatchEvent(mk('dragend',   r.x + %d, r.y + %d));"
        "return 'ok';"
        "} finally { DataTransfer.prototype.setData = orig; }"
        "})()"
    ) % (conds, dx, dy, dx, dy, dx, dy, dx, dy)
    status = js(body)
    payload = js("(window.__zwPayload !== undefined && window.__zwPayload !== null) ? window.__zwPayload : null")
    return status, payload

def zw_set_textarea(selector_or_js, value):
    """Set a React-controlled input/textarea via native setter + events."""
    return js("""(() => {
      const el = %s;
      if (!el) return 'el not found';
      const proto = el.tagName === 'TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
      const setter = Object.getOwnPropertyDescriptor(proto, 'value').set;
      setter.call(el, %r);
      el.dispatchEvent(new Event('input', {bubbles: true}));
      el.dispatchEvent(new Event('change', {bubbles: true}));
      return 'set';
    })()""" % (selector_or_js, value))

def zw_save_drawer():
    """Click the drawer's SAVE button; returns toast result after 1s."""
    import time as _t
    r = js("(() => { const b = Array.from(document.querySelectorAll('button')).find(x => x.innerText.trim()==='SAVE'); if (b) { b.click(); return 'clicked'; } return 'no-save-btn'; })()")
    _t.sleep(1.2)
    toast = js("document.body.innerText.includes('Updated successfully') ? 'saved' : 'check-toast'")
    return r + ' / ' + toast

def zw_dump_drawer():
    """JSON dump of the open settings drawer (text + fields + monaco flag)."""
    return js("""(() => {
      const saveBtn = Array.from(document.querySelectorAll('button')).find(b => b.innerText.trim() === 'SAVE');
      if (!saveBtn) return null;
      let panel = saveBtn;
      for (let i = 0; i < 12 && panel.parentElement; i++) {
        panel = panel.parentElement;
        const r = panel.getBoundingClientRect();
        if (r.height > 250 && r.width > 250) break;
      }
      const text = (panel.innerText || '').replace(/\\s+/g, ' ').substring(0, 700);
      const fields = [];
      for (const el of panel.querySelectorAll('input, textarea, [role=combobox]')) {
        const r = el.getBoundingClientRect();
        if (r.width === 0 && r.height === 0) continue;
        fields.push({tag: el.tagName, type: el.type || '', ph: (el.placeholder||'').substring(0,40),
                     val: ((el.value !== undefined && el.value !== '') ? el.value : '').toString().substring(0,30)});
      }
      const monaco = !!panel.querySelector('.monaco-editor');
      return JSON.stringify({text: text, fields: fields, monaco: monaco});
    })()""")

def zw_delete(data_id):
    """Delete node via its x button (hover first if needed - synthetic-safe version)."""
    return js("""(() => {
      const n = document.querySelector('.react-flow__node[data-id="%s"]');
      if (!n) return 'gone';
      const btn = n.querySelector('button');
      if (!btn) return 'no-x-btn (hover via CDP mouseMoved; viewport-culled nodes need fit-view or pan first)';
      btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
      return 'deleted';
    })()""" % data_id)

def zw_connect(source_id, target_id):
    """Trusted CDP drag: source bottom handle -> target top handle.
    REQUIRES: editor tab visible (switch_tab first). Edge creation is the one
    thing REST can also do (POST /connector/<id>/edge/) - prefer REST."""
    import time as _t, json as _json
    centers = js("""(() => {
      const s = document.querySelector('.react-flow__node[data-id="%s"] .react-flow__handle-bottom');
      const t = document.querySelector('.react-flow__node[data-id="%s"] .react-flow__handle-top');
      if (!s || !t) return null;
      const sr = s.getBoundingClientRect(), tr = t.getBoundingClientRect();
      return JSON.stringify({sx: sr.x + sr.width/2, sy: sr.y + sr.height/2, tx: tr.x + tr.width/2, ty: tr.y + tr.height/2});
    })()""" % (source_id, target_id))
    if not centers:
        return 'handles not found'
    c = _json.loads(centers)
    cdp('Input.dispatchMouseEvent', type='mouseMoved', x=c['sx'], y=c['sy'])
    _t.sleep(0.3)
    cdp('Input.dispatchMouseEvent', type='mousePressed', x=c['sx'], y=c['sy'], button='left', buttons=1, clickCount=1)
    for i in range(1, 9):
        x = c['sx'] + (c['tx'] - c['sx']) * i / 8
        y = c['sy'] + (c['ty'] - c['sy']) * i / 8
        cdp('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y, buttons=1)
        _t.sleep(0.06)
    cdp('Input.dispatchMouseEvent', type='mouseReleased', x=c['tx'], y=c['ty'], button='left', buttons=0, clickCount=1)
    _t.sleep(1.2)
    return js("Array.from(document.querySelectorAll('.react-flow__edge')).length")

def zw_harvest(match_parts, wait=1.5, monaco_wait=0.0):
    """Full discovery cycle: drop -> dump drawer -> delete node."""
    import time as _t
    before = zw_canvas_ids()
    status, payload = zw_drop_capture(match_parts)
    _t.sleep(wait + monaco_wait)
    after = zw_canvas_ids()
    new_ids = [i for i in (after or []) if i not in (before or [])]
    drawer = zw_dump_drawer()
    rec = {'match': match_parts, 'drop_status': status, 'payload': payload,
           'node_created': new_ids[0] if new_ids else None, 'drawer': drawer}
    if new_ids:
        _t.sleep(0.3)
        rec['delete'] = zw_delete(new_ids[0])
        _t.sleep(0.6)
    return rec

def zw_run():
    """Click the Run toolbar button."""
    return js("""(() => {
      const btn = Array.from(document.querySelectorAll('button')).find(b => b.getAttribute('aria-label') === 'Run');
      if (!btn) return 'no run button';
      btn.click();
      return 'RUN clicked';
    })()""")
