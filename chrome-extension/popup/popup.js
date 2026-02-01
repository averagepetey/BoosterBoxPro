/**
 * BoosterBoxPro Chrome Extension - Popup Script
 * Opens box detail panel on TCGplayer and link to dashboard.
 */

document.addEventListener('DOMContentLoaded', async () => {
  const dashboardLink = document.getElementById('dashboard-link');
  dashboardLink.href = 'https://boosterboxpro.vercel.app/dashboard';

  const sidebarBtn = document.getElementById('open-sidebar-btn');
  sidebarBtn.addEventListener('click', async () => {
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
