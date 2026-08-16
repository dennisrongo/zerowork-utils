# ZeroWork creator palette drag helper.
# Usage in browser_exec: exec(open('agent_helpers.py').read())
# zw_drag(['Open', 'Link'], dx=300, dy=180)  -> drops block on canvas, opens its drawer
# NOTE: configures the NEWEST node; after SAVE, delete the old node id if replacing.
def zw_drag(match, dx=300, dy=200):
    conds = " && ".join(["(t||'').includes('%s')" % p for p in match])
    body = (
        "(() => {"
        "const drags = Array.from(document.querySelectorAll('[draggable=true]'));"
        "const item = drags.find(d => { const t = (d.innerText||'').replace(/\\n/g,' '); return %s; });"
        "const zone = document.querySelector('div.invisible-drop');"
        "if (!item || !zone) return 'missing';"
        "const r = zone.getBoundingClientRect();"
        "const dt = new DataTransfer();"
        "const mk = (type, x, y) => new DragEvent(type, {bubbles: true, cancelable: true, clientX: x, clientY: y, dataTransfer: dt});"
        "item.dispatchEvent(mk('dragstart', 100, 300));"
        "zone.dispatchEvent(mk('dragenter', r.x + %d, r.y + %d));"
        "zone.dispatchEvent(mk('dragover',  r.x + %d, r.y + %d));"
        "zone.dispatchEvent(mk('drop',      r.x + %d, r.y + %d));"
        "item.dispatchEvent(mk('dragend',   r.x + %d, r.y + %d));"
        "return 'ok';"
        "})()"
    ) % (conds, dx, dy, dx, dy, dx, dy, dx, dy)
    return js(body)


# Trusted CDP handle-to-handle connection drag (tab MUST be visible first via switch_tab).
# node ids = ZeroWork block IDs from .react-flow__node[data-id]
def zw_connect(sid, tid):
    import time, json
    centers = js(
        "(() => {"
        "const s = document.querySelector('.react-flow__node[data-id=\"%s\"] .react-flow__handle-bottom');"
        "const t = document.querySelector('.react-flow__node[data-id=\"%s\"] .react-flow__handle-top');"
        "if (!s || !t) return null;"
        "const sr = s.getBoundingClientRect(), tr = t.getBoundingClientRect();"
        "return JSON.stringify({sx: sr.x + sr.width/2, sy: sr.y + sr.height/2,"
        " tx: tr.x + tr.width/2, ty: tr.y + tr.height/2});"
        "})()" % (sid, tid)
    )
    c = json.loads(centers)
    cdp('Input.dispatchMouseEvent', type='mouseMoved', x=c['sx'], y=c['sy'])
    time.sleep(0.3)
    cdp('Input.dispatchMouseEvent', type='mousePressed', x=c['sx'], y=c['sy'], button='left', buttons=1, clickCount=1)
    for i in range(1, 9):
        x = c['sx'] + (c['tx'] - c['sx']) * i / 8
        y = c['sy'] + (c['ty'] - c['sy']) * i / 8
        cdp('Input.dispatchMouseEvent', type='mouseMoved', x=x, y=y, buttons=1)
        time.sleep(0.06)
    cdp('Input.dispatchMouseEvent', type='mouseReleased', x=c['tx'], y=c['ty'], button='left', buttons=0, clickCount=1)
    time.sleep(1.5)
    return js("Array.from(document.querySelectorAll('.react-flow__edge')).length")
