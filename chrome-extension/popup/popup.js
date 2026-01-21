/**
 * BoosterBoxPro Chrome Extension - Popup Script
 */

document.addEventListener('DOMContentLoaded', async () => {
  console.log('[BBP] Popup loaded');
  
  // Load top movers
  loadTopMovers();
  
  // Setup compare button
  const compareBtn = document.getElementById('compare-btn');
  const box1Select = document.getElementById('compare-box1');
  const box2Select = document.getElementById('compare-box2');
  
  compareBtn.addEventListener('click', () => {
    const box1 = box1Select.value;
    const box2 = box2Select.value;
    
    if (box1 && box2) {
      // Open dashboard with compare view
      const url = `http://localhost:3000/compare?box1=${box1}&box2=${box2}`;
      chrome.tabs.create({ url });
    }
  });
  
  // Update compare button state
  function updateCompareButton() {
    compareBtn.disabled = !box1Select.value || !box2Select.value;
  }
  
  box1Select.addEventListener('change', updateCompareButton);
  box2Select.addEventListener('change', updateCompareButton);
  updateCompareButton();
  
  // Search functionality
  const searchInput = document.getElementById('search-input');
  searchInput.addEventListener('input', async (e) => {
    const query = e.target.value.trim();
    if (query.length < 2) return;
    
    // Could implement live search here
    console.log('[BBP] Searching for:', query);
  });
  
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const query = searchInput.value.trim();
      if (query) {
        // Open dashboard with search
        const url = `http://localhost:3000/dashboard?search=${encodeURIComponent(query)}`;
        chrome.tabs.create({ url });
      }
    }
  });
});

/**
 * Load and display top movers
 */
async function loadTopMovers() {
  const container = document.getElementById('top-movers');
  
  try {
    const response = await chrome.runtime.sendMessage({ action: 'getTopMovers' });
    
    if (response.error) {
      container.innerHTML = '<div class="no-data">Unable to load data</div>';
      return;
    }
    
    const movers = [...(response.gainers || []), ...(response.losers || [])].slice(0, 5);
    
    if (movers.length === 0) {
      container.innerHTML = '<div class="no-data">No data available</div>';
      return;
    }
    
    container.innerHTML = movers.map(mover => {
      const isPositive = mover.change_pct >= 0;
      const icon = isPositive ? '📈' : '📉';
      const changeClass = isPositive ? 'positive' : 'negative';
      const sign = isPositive ? '+' : '';
      
      return `
        <div class="mover-item">
          <span class="mover-icon">${icon}</span>
          <span class="mover-name">${mover.set_code}</span>
          <span class="mover-price">$${mover.price?.toFixed(2) || '—'}</span>
          <span class="mover-change ${changeClass}">${sign}${mover.change_pct?.toFixed(1) || 0}%</span>
        </div>
      `;
    }).join('');
    
  } catch (error) {
    console.error('[BBP] Error loading top movers:', error);
    container.innerHTML = '<div class="no-data">Unable to connect</div>';
  }
}

