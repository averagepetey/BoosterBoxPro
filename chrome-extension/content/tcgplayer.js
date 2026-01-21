/**
 * BoosterBoxPro Chrome Extension - TCGplayer Content Script
 * Auto-detects One Piece booster boxes and displays market data panel
 */

(function() {
  'use strict';

  console.log('[BBP] BoosterBoxPro content script loaded on TCGplayer');

  // State
  let currentSetCode = null;
  let currentBoxData = null;
  let panelElement = null;
  let isCompareMode = false;
  let compareBoxData = null;

  /**
   * Extract set code from page (OP-01, OP-02, EB-01, PRB-01, etc.)
   */
  function extractSetCode() {
    // Try URL first
    const url = window.location.href;
    
    // Pattern: op-01, op01, op 01, OP-01, etc.
    const urlMatch = url.match(/[oO][pP][-\s]?(\d{1,2})|[eE][bB][-\s]?(\d{1,2})|[pP][rR][bB][-\s]?(\d{1,2})/i);
    
    if (urlMatch) {
      const num = urlMatch[1] || urlMatch[2] || urlMatch[3];
      const prefix = url.toLowerCase().includes('eb') ? 'EB' : 
                     url.toLowerCase().includes('prb') ? 'PRB' : 'OP';
      return `${prefix}-${num.padStart(2, '0')}`;
    }
    
    // Try page title
    const title = document.title;
    const titleMatch = title.match(/[oO][pP][-\s]?(\d{1,2})|[eE][bB][-\s]?(\d{1,2})|[pP][rR][bB][-\s]?(\d{1,2})/i);
    
    if (titleMatch) {
      const num = titleMatch[1] || titleMatch[2] || titleMatch[3];
      const prefix = title.toLowerCase().includes('eb') ? 'EB' : 
                     title.toLowerCase().includes('prb') ? 'PRB' : 'OP';
      return `${prefix}-${num.padStart(2, '0')}`;
    }
    
    // Try product name on page
    const productNameEl = document.querySelector('.product-details__name, h1.product__name, [data-testid="product-name"]');
    if (productNameEl) {
      const text = productNameEl.textContent;
      const productMatch = text.match(/[oO][pP][-\s]?(\d{1,2})|[eE][bB][-\s]?(\d{1,2})|[pP][rR][bB][-\s]?(\d{1,2})/i);
      
      if (productMatch) {
        const num = productMatch[1] || productMatch[2] || productMatch[3];
        const prefix = text.toLowerCase().includes('eb') ? 'EB' : 
                       text.toLowerCase().includes('prb') ? 'PRB' : 'OP';
        return `${prefix}-${num.padStart(2, '0')}`;
      }
    }
    
    // Check if it's a One Piece booster box page at all
    const pageText = document.body.innerText.toLowerCase();
    if (pageText.includes('one piece') && pageText.includes('booster')) {
      // Try to find any OP pattern
      const bodyMatch = pageText.match(/op[-\s]?(\d{1,2})/i);
      if (bodyMatch) {
        return `OP-${bodyMatch[1].padStart(2, '0')}`;
      }
    }
    
    return null;
  }

  /**
   * Create the stats panel HTML
   */
  function createPanel() {
    const panel = document.createElement('div');
    panel.id = 'bbp-panel';
    panel.className = 'bbp-panel';
    panel.innerHTML = `
      <div class="bbp-panel-header">
        <div class="bbp-logo">
          <span class="bbp-icon">🎯</span>
          <span class="bbp-title">BoosterBoxPro</span>
        </div>
        <div class="bbp-controls">
          <button class="bbp-btn-minimize" title="Minimize">─</button>
          <button class="bbp-btn-close" title="Close">×</button>
        </div>
      </div>
      
      <div class="bbp-panel-content">
        <div class="bbp-loading">
          <div class="bbp-spinner"></div>
          <span>Detecting box...</span>
        </div>
        
        <div class="bbp-box-info" style="display: none;">
          <div class="bbp-box-header">
            <img class="bbp-box-image" src="" alt="">
            <div class="bbp-box-name"></div>
          </div>
          
          <div class="bbp-tabs">
            <button class="bbp-tab active" data-tab="stats">📊 Stats</button>
            <button class="bbp-tab" data-tab="compare">⚖️ Compare</button>
          </div>
          
          <div class="bbp-tab-content" data-content="stats">
            <div class="bbp-section">
              <div class="bbp-section-title">💰 Pricing</div>
              <div class="bbp-stats-grid">
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Floor Price</span>
                  <span class="bbp-stat-value" id="bbp-floor-price">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">24h Change</span>
                  <span class="bbp-stat-value" id="bbp-24h-change">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">30d Change</span>
                  <span class="bbp-stat-value" id="bbp-30d-change">—</span>
                </div>
              </div>
            </div>
            
            <div class="bbp-section">
              <div class="bbp-section-title">📈 Volume & Sales</div>
              <div class="bbp-stats-grid">
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Daily Volume</span>
                  <span class="bbp-stat-value" id="bbp-daily-volume">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">30d Volume</span>
                  <span class="bbp-stat-value" id="bbp-30d-volume">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Sales/Day</span>
                  <span class="bbp-stat-value" id="bbp-sales-day">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">30d Avg Sales</span>
                  <span class="bbp-stat-value" id="bbp-30d-avg-sales">—</span>
                </div>
              </div>
            </div>
            
            <div class="bbp-section">
              <div class="bbp-section-title">📦 Supply</div>
              <div class="bbp-stats-grid">
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Active Listings</span>
                  <span class="bbp-stat-value" id="bbp-listings">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Added Today</span>
                  <span class="bbp-stat-value" id="bbp-added-today">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Liquidity</span>
                  <span class="bbp-stat-value" id="bbp-liquidity">—</span>
                </div>
              </div>
            </div>
            
            <div class="bbp-section">
              <div class="bbp-section-title">⏱️ Investment</div>
              <div class="bbp-stats-grid">
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Days to +20%</span>
                  <span class="bbp-stat-value" id="bbp-days-20">—</span>
                </div>
                <div class="bbp-stat">
                  <span class="bbp-stat-label">Reprint Risk</span>
                  <span class="bbp-stat-value" id="bbp-reprint-risk">—</span>
                </div>
              </div>
            </div>
            
            <a class="bbp-dashboard-link" href="#" target="_blank">
              View Full Dashboard →
            </a>
          </div>
          
          <div class="bbp-tab-content" data-content="compare" style="display: none;">
            <div class="bbp-compare-search">
              <label>Compare to:</label>
              <select id="bbp-compare-select">
                <option value="">Select a box...</option>
                <option value="OP-01">OP-01 Romance Dawn</option>
                <option value="OP-02">OP-02 Paramount War</option>
                <option value="OP-03">OP-03 Pillars of Strength</option>
                <option value="OP-04">OP-04 Kingdoms of Intrigue</option>
                <option value="OP-05">OP-05 Awakening of the New Era</option>
                <option value="OP-06">OP-06 Wings of the Captain</option>
                <option value="OP-07">OP-07 500 Years in the Future</option>
                <option value="OP-08">OP-08 Two Legends</option>
                <option value="OP-09">OP-09 The Four Emperors</option>
                <option value="EB-01">EB-01 Memorial Collection</option>
                <option value="PRB-01">PRB-01 Premium Booster</option>
              </select>
            </div>
            
            <div class="bbp-compare-results" style="display: none;">
              <div class="bbp-compare-header">
                <div class="bbp-compare-col">
                  <span id="bbp-compare-box1-name">Current</span>
                </div>
                <div class="bbp-compare-vs">vs</div>
                <div class="bbp-compare-col">
                  <span id="bbp-compare-box2-name">—</span>
                </div>
              </div>
              
              <div class="bbp-compare-row">
                <div class="bbp-compare-label">Floor Price</div>
                <div class="bbp-compare-col" id="bbp-cmp-price1">—</div>
                <div class="bbp-compare-col" id="bbp-cmp-price2">—</div>
              </div>
              
              <div class="bbp-compare-row">
                <div class="bbp-compare-label">30d Change</div>
                <div class="bbp-compare-col" id="bbp-cmp-change1">—</div>
                <div class="bbp-compare-col" id="bbp-cmp-change2">—</div>
              </div>
              
              <div class="bbp-compare-row">
                <div class="bbp-compare-label">Daily Volume</div>
                <div class="bbp-compare-col" id="bbp-cmp-volume1">—</div>
                <div class="bbp-compare-col" id="bbp-cmp-volume2">—</div>
              </div>
              
              <div class="bbp-compare-row">
                <div class="bbp-compare-label">Sales/Day</div>
                <div class="bbp-compare-col" id="bbp-cmp-sales1">—</div>
                <div class="bbp-compare-col" id="bbp-cmp-sales2">—</div>
              </div>
              
              <div class="bbp-compare-row">
                <div class="bbp-compare-label">Liquidity</div>
                <div class="bbp-compare-col" id="bbp-cmp-liq1">—</div>
                <div class="bbp-compare-col" id="bbp-cmp-liq2">—</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="bbp-no-box" style="display: none;">
          <div class="bbp-no-box-icon">🔍</div>
          <div class="bbp-no-box-text">No One Piece booster box detected on this page.</div>
          <div class="bbp-no-box-hint">Navigate to a booster box product page to see market data.</div>
        </div>
        
        <div class="bbp-error" style="display: none;">
          <div class="bbp-error-icon">⚠️</div>
          <div class="bbp-error-text">Unable to load market data.</div>
          <button class="bbp-retry-btn">Retry</button>
        </div>
      </div>
    `;
    
    return panel;
  }

  /**
   * Format currency
   */
  function formatCurrency(value) {
    if (value === null || value === undefined) return '—';
    return '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  /**
   * Format percentage with color
   */
  function formatPercent(value, includeSign = true) {
    if (value === null || value === undefined) return '—';
    const sign = value >= 0 ? '+' : '';
    const colorClass = value > 0 ? 'bbp-positive' : value < 0 ? 'bbp-negative' : '';
    const arrow = value > 0 ? ' ▲' : value < 0 ? ' ▼' : '';
    return `<span class="${colorClass}">${includeSign ? sign : ''}${value.toFixed(1)}%${arrow}</span>`;
  }

  /**
   * Format number
   */
  function formatNumber(value) {
    if (value === null || value === undefined) return '—';
    return value.toLocaleString('en-US');
  }

  /**
   * Update panel with box data
   */
  function updatePanel(data) {
    if (!panelElement) return;
    
    const loading = panelElement.querySelector('.bbp-loading');
    const boxInfo = panelElement.querySelector('.bbp-box-info');
    const noBox = panelElement.querySelector('.bbp-no-box');
    const error = panelElement.querySelector('.bbp-error');
    
    loading.style.display = 'none';
    
    if (!data || !data.matched) {
      if (data && data.error) {
        error.style.display = 'block';
        error.querySelector('.bbp-error-text').textContent = data.error;
      } else {
        noBox.style.display = 'block';
      }
      chrome.runtime.sendMessage({ action: 'noBoxDetected' });
      return;
    }
    
    boxInfo.style.display = 'block';
    chrome.runtime.sendMessage({ action: 'boxDetected' });
    
    const box = data.box;
    const metrics = data.metrics;
    
    // Update box info
    panelElement.querySelector('.bbp-box-name').textContent = box.product_name;
    
    // Update image if available
    const img = panelElement.querySelector('.bbp-box-image');
    if (box.image_url) {
      img.src = `http://localhost:3000${box.image_url}`;
      img.style.display = 'block';
    } else {
      img.style.display = 'none';
    }
    
    // Update stats
    document.getElementById('bbp-floor-price').textContent = formatCurrency(metrics.floor_price_usd);
    document.getElementById('bbp-24h-change').innerHTML = formatPercent(metrics.floor_price_1d_change_pct);
    document.getElementById('bbp-30d-change').innerHTML = formatPercent(metrics.floor_price_30d_change_pct);
    
    document.getElementById('bbp-daily-volume').textContent = formatCurrency(metrics.daily_volume_usd);
    document.getElementById('bbp-30d-volume').textContent = formatCurrency(metrics.unified_volume_usd);
    document.getElementById('bbp-sales-day').textContent = metrics.sales_per_day ? metrics.sales_per_day.toFixed(1) : '—';
    document.getElementById('bbp-30d-avg-sales').textContent = metrics.boxes_sold_30d_avg ? metrics.boxes_sold_30d_avg.toFixed(1) : '—';
    
    document.getElementById('bbp-listings').textContent = formatNumber(metrics.active_listings_count);
    document.getElementById('bbp-added-today').textContent = metrics.boxes_added_today ? `+${metrics.boxes_added_today}` : '—';
    document.getElementById('bbp-liquidity').textContent = metrics.liquidity_score ? `${metrics.liquidity_score.toFixed(1)}/10` : '—';
    
    document.getElementById('bbp-days-20').textContent = metrics.days_to_20pct_increase ? `${Math.round(metrics.days_to_20pct_increase)} days` : '—';
    
    const reprintRisk = box.reprint_risk || 'UNKNOWN';
    const riskClass = reprintRisk === 'LOW' ? 'bbp-risk-low' : reprintRisk === 'HIGH' ? 'bbp-risk-high' : 'bbp-risk-medium';
    document.getElementById('bbp-reprint-risk').innerHTML = `<span class="${riskClass}">${reprintRisk}</span>`;
    
    // Update dashboard link
    const dashboardLink = panelElement.querySelector('.bbp-dashboard-link');
    dashboardLink.href = box.dashboard_url || `http://localhost:3000/box/${box.id}`;
    
    // Store for compare
    currentBoxData = data;
    document.getElementById('bbp-compare-box1-name').textContent = box.set_code || currentSetCode;
  }

  /**
   * Setup event listeners
   */
  function setupEventListeners() {
    if (!panelElement) return;
    
    // Minimize button
    panelElement.querySelector('.bbp-btn-minimize').addEventListener('click', () => {
      panelElement.classList.toggle('bbp-minimized');
    });
    
    // Close button
    panelElement.querySelector('.bbp-btn-close').addEventListener('click', () => {
      panelElement.style.display = 'none';
    });
    
    // Tab switching
    panelElement.querySelectorAll('.bbp-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        
        // Update tab buttons
        panelElement.querySelectorAll('.bbp-tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        
        // Update tab content
        panelElement.querySelectorAll('.bbp-tab-content').forEach(content => {
          content.style.display = content.dataset.content === tabName ? 'block' : 'none';
        });
      });
    });
    
    // Compare dropdown
    const compareSelect = document.getElementById('bbp-compare-select');
    compareSelect.addEventListener('change', async (e) => {
      const compareCode = e.target.value;
      if (!compareCode || !currentSetCode) return;
      
      // Remove current box from options display
      const resultsDiv = panelElement.querySelector('.bbp-compare-results');
      resultsDiv.style.display = 'block';
      
      // Update header
      document.getElementById('bbp-compare-box2-name').textContent = compareCode;
      
      // Fetch comparison data
      try {
        const response = await chrome.runtime.sendMessage({
          action: 'fetchBoxData',
          setCode: compareCode
        });
        
        if (response && response.matched) {
          compareBoxData = response;
          updateCompareView();
        }
      } catch (err) {
        console.error('[BBP] Compare error:', err);
      }
    });
    
    // Retry button
    panelElement.querySelector('.bbp-retry-btn').addEventListener('click', () => {
      detectAndFetch();
    });
  }

  /**
   * Update compare view
   */
  function updateCompareView() {
    if (!currentBoxData || !compareBoxData) return;
    
    const m1 = currentBoxData.metrics;
    const m2 = compareBoxData.metrics;
    
    // Price
    document.getElementById('bbp-cmp-price1').textContent = formatCurrency(m1.floor_price_usd);
    document.getElementById('bbp-cmp-price2').textContent = formatCurrency(m2.floor_price_usd);
    
    // 30d change
    document.getElementById('bbp-cmp-change1').innerHTML = formatPercent(m1.floor_price_30d_change_pct);
    document.getElementById('bbp-cmp-change2').innerHTML = formatPercent(m2.floor_price_30d_change_pct);
    
    // Volume
    document.getElementById('bbp-cmp-volume1').textContent = formatCurrency(m1.daily_volume_usd);
    document.getElementById('bbp-cmp-volume2').textContent = formatCurrency(m2.daily_volume_usd);
    
    // Sales
    document.getElementById('bbp-cmp-sales1').textContent = m1.sales_per_day ? m1.sales_per_day.toFixed(1) : '—';
    document.getElementById('bbp-cmp-sales2').textContent = m2.sales_per_day ? m2.sales_per_day.toFixed(1) : '—';
    
    // Liquidity
    document.getElementById('bbp-cmp-liq1').textContent = m1.liquidity_score ? `${m1.liquidity_score.toFixed(1)}/10` : '—';
    document.getElementById('bbp-cmp-liq2').textContent = m2.liquidity_score ? `${m2.liquidity_score.toFixed(1)}/10` : '—';
  }

  /**
   * Main detection and fetch function
   */
  async function detectAndFetch() {
    // Show loading
    if (panelElement) {
      panelElement.querySelector('.bbp-loading').style.display = 'flex';
      panelElement.querySelector('.bbp-box-info').style.display = 'none';
      panelElement.querySelector('.bbp-no-box').style.display = 'none';
      panelElement.querySelector('.bbp-error').style.display = 'none';
    }
    
    // Detect set code
    currentSetCode = extractSetCode();
    console.log(`[BBP] Detected set code: ${currentSetCode}`);
    
    if (!currentSetCode) {
      updatePanel(null);
      return;
    }
    
    // Fetch data from background script
    try {
      const response = await chrome.runtime.sendMessage({
        action: 'fetchBoxData',
        setCode: currentSetCode
      });
      
      updatePanel(response);
    } catch (error) {
      console.error('[BBP] Error fetching data:', error);
      updatePanel({ matched: false, error: 'Connection error' });
    }
  }

  /**
   * Initialize extension
   */
  function init() {
    console.log('[BBP] Initializing BoosterBoxPro panel');
    
    // Create and inject panel
    panelElement = createPanel();
    document.body.appendChild(panelElement);
    
    // Setup event listeners
    setupEventListeners();
    
    // Detect and fetch data
    detectAndFetch();
    
    // Re-detect on navigation (SPA support)
    let lastUrl = location.href;
    new MutationObserver(() => {
      const url = location.href;
      if (url !== lastUrl) {
        lastUrl = url;
        console.log('[BBP] URL changed, re-detecting...');
        setTimeout(detectAndFetch, 500); // Small delay for page to load
      }
    }).observe(document, { subtree: true, childList: true });
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();

