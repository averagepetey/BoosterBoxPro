/**
 * BoosterBoxPro Chrome Extension - Background Service Worker
 * Handles API communication and caching
 */

// PostHog analytics (lightweight HTTP client)
importScripts('lib/posthog.js');

const DEFAULT_API_BASE_URL = 'https://boosterboxpro.onrender.com';
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes cache

// In-memory cache for box data
const boxCache = new Map();

/**
 * Get API base URL from storage (user-configurable in extension options)
 */
async function getApiBaseUrl() {
  try {
    const { apiBaseUrl } = await chrome.storage.local.get('apiBaseUrl');
    const url = (apiBaseUrl || DEFAULT_API_BASE_URL).replace(/\/+$/, '');
    return url || DEFAULT_API_BASE_URL;
  } catch {
    return DEFAULT_API_BASE_URL;
  }
}

/**
 * User-friendly message for network/connection failures
 */
function connectionErrorMessage(baseUrl, err) {
  const url = baseUrl || DEFAULT_API_BASE_URL;
  if (!err || /failed to fetch|network|connection refused|load failed/i.test(String(err.message || ''))) {
    return `Can't reach the API at ${url}. Make sure the BoosterBoxPro backend is running, then click Retry.`;
  }
  return err.message || 'Connection error';
}

/**
 * Fetch box data from BoosterBoxPro API
 */
async function fetchBoxData(setCode) {
  const API_BASE_URL = await getApiBaseUrl();

  // Check cache first
  const cached = boxCache.get(setCode);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    console.log(`[BBP] Cache hit for ${setCode}`);
    return cached.data;
  }

  console.log(`[BBP] Fetching data for ${setCode} from ${API_BASE_URL}`);
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);

  try {
    const response = await fetch(`${API_BASE_URL}/extension/box/${setCode}`, {
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      if (response.status === 404) {
        return { matched: false, error: 'Box not found', apiBaseUrl: API_BASE_URL };
      }
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Cache the result
    boxCache.set(setCode, {
      data: data,
      timestamp: Date.now()
    });
    
    return data;
  } catch (error) {
    clearTimeout(timeoutId);
    console.error(`[BBP] Error fetching box data:`, error);
    const message = error.name === 'AbortError'
      ? `Request timed out. Is the backend running at ${API_BASE_URL}? Start it (e.g. python main.py), then click Retry.`
      : connectionErrorMessage(API_BASE_URL, error);
    return {
      matched: false,
      error: message,
      apiBaseUrl: API_BASE_URL
    };
  }
}

/**
 * Compare two boxes
 */
async function compareBoxes(box1, box2) {
  const API_BASE_URL = await getApiBaseUrl();
  try {
    const response = await fetch(`${API_BASE_URL}/extension/compare?box1=${box1}&box2=${box2}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`[BBP] Error comparing boxes:`, error);
    return { error: connectionErrorMessage(API_BASE_URL, error) };
  }
}

/**
 * Search boxes for compare dropdown
 */
async function searchBoxes(query) {
  const API_BASE_URL = await getApiBaseUrl();
  try {
    const response = await fetch(`${API_BASE_URL}/extension/search?q=${encodeURIComponent(query)}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`[BBP] Error searching boxes:`, error);
    return { results: [] };
  }
}

/**
 * Get top movers for popup
 */
async function getTopMovers() {
  const API_BASE_URL = await getApiBaseUrl();
  try {
    const response = await fetch(`${API_BASE_URL}/extension/top-movers`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`[BBP] Error fetching top movers:`, error);
    return { gainers: [], losers: [] };
  }
}

/**
 * Inject content script into a tab
 */
async function injectContentScript(tabId) {
  try {
    // First try to message existing content script
    try {
      const response = await chrome.tabs.sendMessage(tabId, { action: 'ping' });
      if (response && response.pong) {
        // Content script already loaded, just show panel
        await chrome.tabs.sendMessage(tabId, { action: 'showPanel' });
        return { success: true, alreadyLoaded: true };
      }
    } catch (e) {
      // Content script not loaded, proceed with injection
      console.log('[BBP] Content script not loaded, injecting...');
    }
    
    // Inject CSS
    await chrome.scripting.insertCSS({
      target: { tabId: tabId },
      files: ['content/panel.css']
    });
    
    // Inject JS
    await chrome.scripting.executeScript({
      target: { tabId: tabId },
      files: ['content/tcgplayer.js']
    });
    // Tell the newly injected script to show the panel (it starts hidden)
    await new Promise(r => setTimeout(r, 100));
    try {
      await chrome.tabs.sendMessage(tabId, { action: 'showPanel' });
    } catch (e) {
      console.log('[BBP] showPanel after inject:', e.message);
    }
    return { success: true };
  } catch (error) {
    console.error('[BBP] Injection error:', error);
    return { success: false, error: error.message };
  }
}

// Listen for messages from content scripts and popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log(`[BBP] Received message:`, request);
  
  switch (request.action) {
    case 'fetchBoxData':
      fetchBoxData(request.setCode).then(sendResponse);
      return true; // Keep channel open for async response
      
    case 'compareBoxes':
      compareBoxes(request.box1, request.box2).then(sendResponse);
      return true;
      
    case 'searchBoxes':
      searchBoxes(request.query).then(sendResponse);
      return true;
      
    case 'getTopMovers':
      getTopMovers().then(sendResponse);
      return true;
    
    case 'injectPanel':
      injectContentScript(request.tabId).then(sendResponse);
      return true;

    case 'trackEvent':
      captureEvent(request.event, request.properties || {}).then(() => sendResponse({ success: true }));
      return true;

    default:
      console.warn(`[BBP] Unknown action: ${request.action}`);
      sendResponse({ error: 'Unknown action' });
  }
});

// Update badge when box is detected
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'boxDetected') {
    chrome.action.setBadgeText({ text: '✓', tabId: sender.tab.id });
    chrome.action.setBadgeBackgroundColor({ color: '#22c55e', tabId: sender.tab.id });
  } else if (request.action === 'noBoxDetected') {
    chrome.action.setBadgeText({ text: '', tabId: sender.tab.id });
  }
});

// Ensure PostHog distinct_id is initialized on service worker load
getDistinctId().then(id => console.log('[BBP] PostHog distinct_id:', id));

console.log('[BBP] BoosterBoxPro background service worker loaded');
