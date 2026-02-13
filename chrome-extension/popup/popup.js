/**
 * BoosterBoxPro Chrome Extension - Popup Script
 * Opens box detail panel on TCGplayer and link to dashboard.
 */

/**
 * Send an analytics event to PostHog via background script
 */
function trackEvent(event, properties = {}) {
  try {
    chrome.runtime.sendMessage({ action: 'trackEvent', event, properties });
  } catch (e) {
    // Extension context invalidated — ignore
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  trackEvent('popup_opened');

  // Get config from background for centralized URL management
  let dashboardUrl = 'https://booster-box-pro.vercel.app';
  try {
    const cfg = await chrome.runtime.sendMessage({ action: 'getConfig' });
    if (cfg && cfg.dashboardUrl) dashboardUrl = cfg.dashboardUrl;
  } catch (e) {
    // Use default
  }

  const dashboardLink = document.getElementById('dashboard-link');
  dashboardLink.href = dashboardUrl + '/dashboard';
  dashboardLink.addEventListener('click', () => {
    trackEvent('popup_dashboard_clicked');
  });

  const sidebarBtn = document.getElementById('open-sidebar-btn');
  sidebarBtn.addEventListener('click', async () => {
    trackEvent('popup_open_extension_clicked');
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) {
        alert('No active tab found');
        return;
      }
      const url = tab.url || '';
      const isSupported = url.includes('tcgplayer.com') || url.includes('ebay.com');
      if (!isSupported) {
        alert('Please open a TCGplayer or eBay booster box page first.');
        return;
      }
      chrome.runtime.sendMessage({ action: 'injectPanel', tabId: tab.id }, (response) => {
        if (chrome.runtime.lastError) {
          alert('Error: ' + chrome.runtime.lastError.message);
          return;
        }
        if (response && response.success) {
          window.close();
        } else {
          alert('Error: ' + (response?.error || 'Unknown error'));
        }
      });
    } catch (err) {
      alert('Error: ' + err.message);
    }
  });
});
