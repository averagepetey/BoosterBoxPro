/**
 * BoosterBoxPro Chrome Extension - Background Service Worker
 * Handles API communication and caching
 */

// API Configuration
const API_BASE_URL = 'http://localhost:8000'; // Change to production URL for release
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes cache

// In-memory cache for box data
const boxCache = new Map();

/**
 * Fetch box data from BoosterBoxPro API
 */
async function fetchBoxData(setCode) {
  // Check cache first
  const cached = boxCache.get(setCode);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    console.log(`[BBP] Cache hit for ${setCode}`);
    return cached.data;
  }

  console.log(`[BBP] Fetching data for ${setCode}`);
  
  try {
    const response = await fetch(`${API_BASE_URL}/extension/box/${setCode}`);
    
    if (!response.ok) {
      if (response.status === 404) {
        return { matched: false, error: 'Box not found' };
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
    console.error(`[BBP] Error fetching box data:`, error);
    return { matched: false, error: error.message };
  }
}

/**
 * Compare two boxes
 */
async function compareBoxes(box1, box2) {
  try {
    const response = await fetch(`${API_BASE_URL}/extension/compare?box1=${box1}&box2=${box2}`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`[BBP] Error comparing boxes:`, error);
    return { error: error.message };
  }
}

/**
 * Search boxes for compare dropdown
 */
async function searchBoxes(query) {
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

console.log('[BBP] BoosterBoxPro background service worker loaded');

