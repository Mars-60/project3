console.log("Atlas Extension v2 - Loaded");

// ── Queue for events that arrive before Flask is ready ────────────────────
const pendingQueue = [];
let flaskReady = false;
let flushTimer = null;

async function sendActivity(title, url) {
  if (!url) return;
  if (
    url.startsWith('chrome://') ||
    url.startsWith('chrome-extension://') ||
    url.startsWith('edge://') ||
    url.startsWith('about:') ||
    url.startsWith('file://') ||
    url.includes('127.0.0.1') ||
    url.includes('localhost')
  ) return;

  pendingQueue.push({ title, url, time: Date.now() });
  scheduleFlush();
}

function scheduleFlush() {
  if (flushTimer) return; // already scheduled
  flushTimer = setTimeout(flushQueue, 1000);
}

async function flushQueue() {
  flushTimer = null;
  if (pendingQueue.length === 0) return;

  // Try to send all queued items
  const toSend = [...pendingQueue];
  pendingQueue.length = 0;

  for (const item of toSend) {
    const sent = await trySend(item.title, item.url);
    if (!sent) {
      // Flask not up yet — put back in queue and retry in 3s
      pendingQueue.push(item);
    }
  }

  // If items still pending, retry after 3 seconds
  if (pendingQueue.length > 0) {
    setTimeout(flushQueue, 3000);
  }
}

async function trySend(title, url) {
  try {
    const res = await fetch("http://127.0.0.1:5000/browser_activity", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, url })
    });
    if (res.ok) {
      flaskReady = true;
      return true;
    }
    return false;
  } catch (e) {
    flaskReady = false;
    return false;
  }
}

// ── Tab switch tracking ───────────────────────────────────────────────────
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  try {
    const tab = await chrome.tabs.get(activeInfo.tabId);
    sendActivity(tab.title, tab.url);
  } catch (e) {}
});

// ── Tab URL change tracking ───────────────────────────────────────────────
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.active) {
    sendActivity(tab.title, tab.url);
  }
});

// ── Heartbeat every 5s for active tab (accurate time tracking) ────────────
setInterval(async () => {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) sendActivity(tab.title, tab.url);
  } catch (e) {}
}, 5000);

// ── On Chrome startup: capture current tab immediately ────────────────────
chrome.runtime.onStartup.addListener(async () => {
  // Wait 8 seconds for Flask to start, then capture current tab
  setTimeout(async () => {
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (tab) sendActivity(tab.title, tab.url);
    } catch (e) {}
  }, 8000);
});