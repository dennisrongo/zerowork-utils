/* LinkedIn home-feed scrape.
   Paste into Write JS. Browser execution (do NOT tick Run locally).
   tableRefId / varRefId resolve via zw.getTaskbotInfo() so this is not
   bound to one bot. Change tableRefId to your own if My references
   already shows it. */
// Reference: https://docs.zerowork.io/using-zerowork/using-building-blocks/write-javascript
const info = await zw.getTaskbotInfo();
const varRefId = (info && info.variables && info.variables.ref_id) ? info.variables.ref_id : 0;
const TABLE_NAME = "linkedin_feed_posts";
var _tables = (info && info.tables) ? info.tables : [];
var _t;
for (var _ti = 0; _ti < _tables.length; _ti++) {
  if (_tables[_ti].name === TABLE_NAME) { _t = _tables[_ti]; break; }
}
if (!_t) {
  for (var _tj = 0; _tj < _tables.length; _tj++) {
    if (_tables[_tj].type === "ZW_NATIVE" && _tables[_tj].name !== "Variables") {
      _t = _tables[_tj];
      break;
    }
  }
}
if (!_t || !_t.ref_id) {
  throw new Error("No native table on this TaskBot — create one, or set tableRefId from My references");
}
const tableRefId = _t.ref_id;
function txt(el, sels) {
  if (!el) return "";
  for (var i = 0; i < sels.length; i++) {
    var n = el.querySelector(sels[i]);
    if (!n) continue;
    var t = (n.innerText || n.textContent || "").trim();
    if (t) return t.replace(/\s+/g, " ");
  }
  return "";
}
function attr(el, sels, a) {
  if (!el) return "";
  for (var i = 0; i < sels.length; i++) {
    var n = el.querySelector(sels[i]);
    if (n && n.getAttribute(a)) return n.getAttribute(a);
  }
  return "";
}
function clickSeeMore() {
  var buttons = document.querySelectorAll("button");
  for (var i = 0; i < buttons.length; i++) {
    var t = (buttons[i].innerText || "").trim().toLowerCase();
    if (t === "see more" || t.indexOf("see more") !== -1) {
      try { buttons[i].click(); } catch (e) {}
    }
  }
}

if (/\/login|\/uas\/login|\/checkpoint/i.test(location.href) ||
    document.querySelector('input#username, input[name="session_key"]')) {
  await zw.log({
    message: "LinkedIn login required. Sign in once (cookies or sticky profile) and re-run.",
    status: "fail",
    tag: "linkedin"
  });
  throw new Error("LinkedIn session missing");
}

clickSeeMore();
var rounds = 8;
for (var r = 0; r < rounds; r++) {
  window.scrollBy(0, Math.max(window.innerHeight, 900));
  await zw.delay({ min: 1200, max: 2000 });
  clickSeeMore();
}

var cardSels = [
  "div.feed-shared-update-v2",
  'div[data-urn*="urn:li:activity"]',
  'div[data-id*="urn:li:activity"]',
  "div.occludable-update"
];
var cards = [];
for (var s = 0; s < cardSels.length; s++) {
  cards = Array.prototype.slice.call(document.querySelectorAll(cardSels[s]));
  if (cards.length) break;
}

var seen = {};
var posts = [];
for (var c = 0; c < cards.length; c++) {
  var el = cards[c];
  var urn = el.getAttribute("data-urn") || el.getAttribute("data-id") || "";
  var author = txt(el, [
    '.update-components-actor__title span[aria-hidden="true"]',
    ".update-components-actor__title",
    ".update-components-actor__name",
    "a.update-components-actor__meta-link"
  ]);
  var headline = txt(el, [
    ".update-components-actor__description"
  ]);
  var posted = txt(el, [
    ".update-components-actor__sub-description",
    "time"
  ]);
  var body = txt(el, [
    ".update-components-text",
    ".feed-shared-update-v2__description",
    ".feed-shared-inline-show-more-text",
    "div.feed-shared-text"
  ]);
  var authorUrl = attr(el, [
    "a.update-components-actor__meta-link",
    "a.update-components-actor__image",
    ".update-components-actor__title a"
  ], "href");
  var postUrl = attr(el, [
    'a[href*="/feed/update/"]',
    'a[href*="activity:"]',
    "a.update-components-actor__sub-description-link"
  ], "href");
  var reactions = txt(el, [
    ".social-details-social-counts__reactions-count",
    'button[aria-label*="reaction"]'
  ]);
  var comments = txt(el, [
    'button[aria-label*="comment"]',
    "li.social-details-social-counts__comments"
  ]);
  var reposts = txt(el, [
    'button[aria-label*="repost"]'
  ]);
  var hasMedia = !!(el.querySelector(
    "img.update-components-image__image, video, .update-components-linkedin-video, .feed-shared-linkedin-video, .update-components-image"
  ));
  var head = (el.innerText || "").slice(0, 180);
  var isRepost = /reposted|shared this/i.test(head);
  var key = urn || (author + "|" + body.slice(0, 80));
  if (!key || seen[key]) continue;
  if (!author && !body) continue;
  seen[key] = true;
  posts.push({
    post_urn: urn,
    author: author,
    author_headline: headline,
    author_url: authorUrl,
    post_text: body.slice(0, 49000),
    posted_at: posted,
    post_url: postUrl,
    reactions: reactions,
    comments: comments,
    reposts: reposts,
    has_media: hasMedia ? "yes" : "no",
    post_type: isRepost ? "repost" : "original"
  });
}

for (var i = 0; i < posts.length; i++) {
  var p = posts[i];
  var names = Object.keys(p);
  for (var k = 0; k < names.length; k++) {
    await zw.setRef({
      ref_id: tableRefId,
      name: names[k],
      value: String(p[names[k]] == null ? "" : p[names[k]]),
      appendIndex: i
    });
  }
}

await zw.log({
  message: "LinkedIn feed scraped " + posts.length + " posts (" + location.pathname + ")",
  status: posts.length ? "success" : "warning",
  tag: "linkedin-feed"
});
if (!posts.length) {
  throw new Error("No feed posts found — not logged in, or LinkedIn DOM changed");
}
