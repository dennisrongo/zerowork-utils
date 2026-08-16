/* X home-feed harvest-while-scroll.
   Paste into Write JS. Browser execution (do NOT tick Run locally).
   Table id: leave TABLE = 0 to resolve via zw.getTaskbotInfo(), or paste
   the ref_id from the drawer's My references. Never copy another bot's id.
   Unique key = status id. Stop after 3 empty scroll rounds or MAX posts. */
function txt(el, sel) {
  if (!el) return "";
  var n = typeof sel === "string" ? el.querySelector(sel) : sel;
  if (!n) return "";
  return ((n.innerText || n.textContent || "").replace(/\s+/g, " ").trim());
}
function firstHref(el, sel) {
  if (!el) return "";
  var n = el.querySelector(sel);
  return n && n.getAttribute("href") ? n.getAttribute("href") : "";
}
function absUrl(href) {
  if (!href) return "";
  if (href.indexOf("http") === 0) return href.split("?")[0];
  return "https://x.com" + href.split("?")[0];
}
function countFrom(el, testid) {
  var n = el.querySelector('[data-testid="' + testid + '"]');
  if (!n) return "";
  var al = (n.getAttribute("aria-label") || "").replace(/,/g, "");
  var m = al.match(/(\d+)/);
  if (m) return m[1];
  var t = (n.innerText || "").replace(/,/g, "").trim();
  return /^\d+$/.test(t) ? t : "";
}
function statusIdFrom(href) {
  var m = (href || "").match(/\/status\/(\d+)/);
  return m ? m[1] : "";
}
function findScrollRoot() {
  var col = document.querySelector('[data-testid="primaryColumn"]');
  var el = col || document.body;
  while (el && el !== document.documentElement) {
    var st = window.getComputedStyle(el);
    var oy = st.overflowY;
    if ((oy === "auto" || oy === "scroll" || oy === "overlay") &&
        el.scrollHeight > el.clientHeight + 80) {
      return el;
    }
    el = el.parentElement;
  }
  return document.scrollingElement || document.documentElement;
}
function clickShowMore() {
  var want = ["show more posts", "see new posts", "retry"];
  var nodes = document.querySelectorAll('button, div[role="button"], [data-testid="retry"]');
  var clicked = 0;
  for (var i = 0; i < nodes.length; i++) {
    var t = ((nodes[i].innerText || nodes[i].textContent || "") + " " +
      (nodes[i].getAttribute("aria-label") || "")).replace(/\s+/g, " ").trim().toLowerCase();
    for (var j = 0; j < want.length; j++) {
      if (t.indexOf(want[j]) !== -1) {
        try { nodes[i].click(); clicked += 1; } catch (e) {}
        break;
      }
    }
  }
  return clicked;
}
function scrollFeed() {
  var last = document.querySelector('article[data-testid="tweet"]:last-of-type') ||
    document.querySelector('[data-testid="cellInnerDiv"]:last-of-type');
  if (last) {
    try { last.scrollIntoView({ block: "end", inline: "nearest" }); } catch (e) {
      try { last.scrollIntoView(false); } catch (e2) {}
    }
  }
  var root = findScrollRoot();
  var before = root.scrollTop;
  var step = Math.max(root.clientHeight || window.innerHeight, 900);
  root.scrollTop = before + step;
  if (root.scrollTop === before) root.scrollTop = root.scrollHeight;
  window.scrollBy(0, step);
  return { before: before, after: root.scrollTop };
}

if (/\/i\/flow\/login|\/login/i.test(location.href) ||
    document.querySelector('input[autocomplete="username"]') ||
    document.querySelector('[data-testid="loginButton"]') ||
    document.querySelector('a[href="/login"]')) {
  await zw.log({
    message: "X login required. Sign in once in Agent Chrome and re-run.",
    status: "fail",
    tag: "x-feed"
  });
  throw new Error("X session missing");
}

var TABLE_NAME = "x_feed_posts";
var TABLE = 0;
var MAX = 40;
var EMPTY_STOP = 3;
var seen = {};
var posts = [];
var emptyRounds = 0;
var rounds = 0;
var roundLog = [];

if (!TABLE) {
  var info = await zw.getTaskbotInfo();
  var tables = (info && info.tables) ? info.tables : [];
  var t;
  for (var ti = 0; ti < tables.length; ti++) {
    if (tables[ti].name === TABLE_NAME) { t = tables[ti]; break; }
  }
  if (!t) {
    for (var tj = 0; tj < tables.length; tj++) {
      if (tables[tj].type === "ZW_NATIVE" && tables[tj].name !== "Variables") {
        t = tables[tj];
        break;
      }
    }
  }
  if (!t || !t.ref_id) {
    throw new Error("No native table on this TaskBot — create one, or set TABLE from My references");
  }
  TABLE = t.ref_id;
}

function harvest() {
  var cards = document.querySelectorAll('article[data-testid="tweet"]');
  var added = 0;
  for (var i = 0; i < cards.length; i++) {
    var el = cards[i];
    var statusHref = firstHref(el, 'a[href*="/status/"]');
    var sid = statusIdFrom(statusHref);
    var handleHref = firstHref(el, '[data-testid="User-Name"] a[href^="/"]');
    var authorBlock = txt(el, '[data-testid="User-Name"]');
    var handle = "";
    var hm = (handleHref || "").match(/^\/([A-Za-z0-9_]+)/);
    if (hm) handle = hm[1];
    var author = authorBlock.split("@")[0].trim() || handle;
    var body = txt(el, '[data-testid="tweetText"]');
    var timeEl = el.querySelector("time");
    var posted = timeEl ? (timeEl.getAttribute("datetime") || txt(el, "time")) : "";
    var key = sid || (handle + "|" + body.slice(0, 80));
    if (!key || seen[key]) continue;
    if (!author && !body && !sid) continue;
    seen[key] = true;
    added += 1;
    posts.push({
      post_id: sid,
      author: author,
      handle: handle,
      author_url: handle ? "https://x.com/" + handle : "",
      post_text: body.slice(0, 49000),
      posted_at: posted,
      post_url: sid ? absUrl(statusHref) : "",
      replies: countFrom(el, "reply"),
      reposts: countFrom(el, "retweet"),
      likes: countFrom(el, "like"),
      views: countFrom(el, "views") || "",
      has_media: el.querySelector('img[src*="pbs.twimg.com"], video, [data-testid="videoPlayer"], [data-testid="tweetPhoto"]') ? "yes" : "no",
      is_repost: /reposted|retweeted/i.test(el.innerText.slice(0, 80)) ? "yes" : "no"
    });
  }
  return { mounted: cards.length, added: added, total: posts.length };
}

while (posts.length < MAX && emptyRounds < EMPTY_STOP && rounds < 24) {
  var snap = harvest();
  rounds += 1;
  if (snap.added === 0) emptyRounds += 1;
  else emptyRounds = 0;
  roundLog.push("r" + rounds + " m" + snap.mounted + "+" + snap.added + "=" + snap.total);
  await zw.log({
    message: "scroll round " + rounds + " mounted=" + snap.mounted + " added=" + snap.added + " total=" + posts.length,
    status: snap.added ? "success" : "warning",
    tag: "x-feed"
  });
  if (posts.length >= MAX || emptyRounds >= EMPTY_STOP) break;
  clickShowMore();
  scrollFeed();
  await zw.delay({ min: 1600, max: 2400 });
}

for (var p = 0; p < posts.length; p++) {
  var row = posts[p];
  var names = Object.keys(row);
  for (var k = 0; k < names.length; k++) {
    await zw.setRef({
      ref_id: TABLE,
      name: names[k],
      value: String(row[names[k]] == null ? "" : row[names[k]]),
      appendIndex: p
    });
  }
}

await zw.log({
  message: "X feed scraped " + posts.length + " posts in " + rounds +
    " scroll rounds (" + location.pathname + ") [" + roundLog.join(" | ") + "]",
  status: posts.length ? "success" : "warning",
  tag: "x-feed"
});
if (!posts.length) throw new Error("No X posts found - not logged in, or DOM changed");
