/**
 * BoosterBoxPro Chrome Extension - TCGplayer Content Script
 * Auto-detects One Piece booster boxes and displays market data panel
 */

(function() {
  'use strict';

  // Prevent multiple injections - if already loaded, just show the panel
  if (window.__bbpLoaded) {
    console.log('[BBP] Already loaded, showing panel');
    const existingPanel = document.getElementById('bbp-panel');
    if (existingPanel) {
      existingPanel.style.display = 'block';
      existingPanel.classList.remove('bbp-collapsed');
      const collapseBtn = existingPanel.querySelector('.bbp-btn-collapse');
      if (collapseBtn) {
        collapseBtn.textContent = '◀';
        collapseBtn.title = 'Collapse';
      }
    }
    return;
  }
  window.__bbpLoaded = true;

  console.log('[BBP] BoosterBoxPro content script loaded on TCGplayer');

  // State
  let currentSetCode = null;
  let currentBoxData = null;
  let panelElement = null;
  let isCompareMode = false;
  let compareBoxData = null;

  /**
   * Set name to set code mapping (matches database product names)
   */
  const SET_NAME_MAP = {
    'romance dawn': 'OP-01',
    'paramount war': 'OP-02',
    'pillars of strength': 'OP-03',
    'kingdoms of intrigue': 'OP-04',
    'awakening of the new era': 'OP-05',
    'wings of the captain': 'OP-06',
    '500 years in the future': 'OP-07',
    'two legends': 'OP-08',
    'emperors in the new world': 'OP-09',
    'royal blood': 'OP-10',
    'a fist of divine speed': 'OP-11',
    'fist of divine speed': 'OP-11',
    'legacy of the master': 'OP-12',
    'carrying on his will': 'OP-13',
    'memorial collection': 'EB-01',
    'anime 25th collection': 'EB-02',
    'premium booster': 'PRB-01',
  };

  /**
   * Extract set code from page (OP-01, OP-02, EB-01, PRB-01, etc.)
   */
  function extractSetCode() {
    const url = decodeURIComponent(window.location.href).toLowerCase();
    const title = document.title.toLowerCase();
    
    // Get page text - try multiple selectors for TCGplayer's dynamic content
    let pageText = '';
    const h1 = document.querySelector('h1');
    if (h1) pageText += ' ' + h1.textContent.toLowerCase();
    const productTitle = document.querySelector('[class*="product-details__name"], [class*="ProductDetails__name"]');
    if (productTitle) pageText += ' ' + productTitle.textContent.toLowerCase();
    const breadcrumbs = document.querySelectorAll('[class*="breadcrumb"] a, nav a');
    breadcrumbs.forEach(el => pageText += ' ' + el.textContent.toLowerCase());
    
    // Also get body text but limit it
    if (document.body) {
      pageText += ' ' + document.body.innerText.substring(0, 5000).toLowerCase();
    }
    
    // Combine all text sources
    const allText = url + ' ' + title + ' ' + pageText;
    
    console.log('[BBP] Searching text for set code...');
    
    // 1. Try direct set code patterns - multiple regex patterns
    // Matches: OP-13, OP13, OP 13, (OP13), op-13, etc.
    const patterns = [
      /[([\s]?(op|eb|prb)[-\s]?(\d{1,2})[\s)\]]/i,  // (OP13) or [OP-13]
      /\b(op|eb|prb)-(\d{1,2})\b/i,                  // OP-13 with hyphen
      /\b(op|eb|prb)(\d{1,2})\b/i,                   // OP13 no separator
      /(op|eb|prb)[-\s]?(\d{1,2})/i,                 // Loose match anywhere
    ];
    
    for (const pattern of patterns) {
      const match = allText.match(pattern);
      if (match) {
        const prefix = match[1].toUpperCase();
        const num = match[2].padStart(2, '0');
        console.log(`[BBP] Found set code via pattern: ${prefix}-${num}`);
        return `${prefix}-${num}`;
      }
    }
    
    // 2. Try set name mapping
    for (const [setName, setCode] of Object.entries(SET_NAME_MAP)) {
      if (allText.includes(setName)) {
        console.log(`[BBP] Found set name "${setName}" → ${setCode}`);
        return setCode;
      }
    }
    
    // 3. Check product title element specifically with wait
    const productTitleEl = document.querySelector('h1, [class*="product-details__name"]');
    if (productTitleEl) {
      const titleText = productTitleEl.textContent.toLowerCase();
      console.log(`[BBP] H1 text: "${titleText}"`);
      
      // Check for set code in title with looser pattern
      const titleMatch = titleText.match(/(op|eb|prb)[-\s]?(\d{1,2})/i);
      if (titleMatch) {
        const prefix = titleMatch[1].toUpperCase();
        const num = titleMatch[2].padStart(2, '0');
        console.log(`[BBP] Found in H1: ${prefix}-${num}`);
        return `${prefix}-${num}`;
      }
      
      // Check for set name in title
      for (const [setName, setCode] of Object.entries(SET_NAME_MAP)) {
        if (titleText.includes(setName)) {
          console.log(`[BBP] Found set name in title "${setName}" → ${setCode}`);
          return setCode;
        }
      }
    }
    
    console.log('[BBP] No set code detected in:', allText.substring(0, 500));
    return null;
  }

  /**
   * Create the stats panel HTML
   */
  function createPanel() {
    const panel = document.createElement('div');
    panel.id = 'bbp-panel';
    panel.className = 'bbp-panel';
    // Get extension URL for logo
    const logoUrl = chrome.runtime.getURL('icons/logo.png');
    
    panel.innerHTML = `
      <div class="bbp-panel-header">
        <div class="bbp-logo">
          <img src="${logoUrl}" alt="BoosterPro" class="bbp-logo-img" onerror="this.style.display='none'">
          <span class="bbp-title">BoosterPro</span>
        </div>
        <div class="bbp-controls">
          <button class="bbp-btn-collapse" title="Collapse">▶</button>
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
            <div class="bbp-key-metrics">
              <div class="bbp-key-metric">
                <div class="bbp-key-metric-label">Current Floor</div>
                <div class="bbp-key-metric-value" id="bbp-floor-price">—</div>
                <div class="bbp-key-metric-sub" id="bbp-24h-change">—</div>
              </div>
              <div class="bbp-key-metric">
                <div class="bbp-key-metric-label">Volume (7d EMA)</div>
                <div class="bbp-key-metric-value" id="bbp-volume-7d">—</div>
              </div>
              <div class="bbp-key-metric">
                <div class="bbp-key-metric-label">Days to +20%</div>
                <div class="bbp-key-metric-value" id="bbp-days-20">—</div>
              </div>
            </div>
            <div class="bbp-volume-change" id="bbp-volume-change-wrap" style="display: none;">
              <div class="bbp-volume-change-label">Volume Change (Day-over-Day)</div>
              <div id="bbp-volume-change">—</div>
            </div>
            <div class="bbp-sentiment-bar">
              <div class="bbp-sentiment-label">
                <span>Community Sentiment</span>
                <span id="bbp-sentiment-value">50/100</span>
              </div>
              <div class="bbp-sentiment-track">
                <div class="bbp-sentiment-fill" id="bbp-sentiment-fill" style="width: 50%;"></div>
              </div>
            </div>
            <div class="bbp-section">
              <div class="bbp-section-title">Metrics (same as box detail)</div>
              <div class="bbp-stats-grid">
                <div class="bbp-stat"><span class="bbp-stat-label">Liquidity</span><span class="bbp-stat-value" id="bbp-liquidity">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Boxes Listed to 20%</span><span class="bbp-stat-value" id="bbp-listings">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Sold/Day</span><span class="bbp-stat-value" id="bbp-sales-day">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Time to Sale</span><span class="bbp-stat-value" id="bbp-time-sale">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Top 10 Value</span><span class="bbp-stat-value" id="bbp-top10">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Daily Vol</span><span class="bbp-stat-value" id="bbp-daily-volume">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Reprint Risk</span><span class="bbp-stat-value" id="bbp-reprint-risk">—</span></div>
              </div>
            </div>
            <a class="bbp-dashboard-link" href="#" target="_blank">View full box detail →</a>
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
                <option value="OP-09">OP-09 Emperors in the New World</option>
                <option value="OP-10">OP-10 Royal Blood</option>
                <option value="OP-11">OP-11 A Fist of Divine Speed</option>
                <option value="OP-12">OP-12 Legacy of the Master</option>
                <option value="OP-13">OP-13 Carrying on His Will</option>
                <option value="EB-01">EB-01 Memorial Collection</option>
                <option value="EB-02">EB-02 Anime 25th Collection</option>
                <option value="PRB-01">PRB-01 Premium Booster</option>
                <option value="PRB-02">PRB-02 Premium Booster</option>
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
              
              <div class="bbp-compare-row">
                <div class="bbp-compare-label">Days to +20%</div>
                <div class="bbp-compare-col" id="bbp-cmp-days1">—</div>
                <div class="bbp-compare-col" id="bbp-cmp-days2">—</div>
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
          <div class="bbp-error-url" style="display: none;"></div>
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
        const errText = error.querySelector('.bbp-error-text');
        errText.textContent = data.error;
        const errUrl = error.querySelector('.bbp-error-url');
        if (errUrl) {
          if (data.apiBaseUrl) {
            errUrl.textContent = 'Backend: ' + data.apiBaseUrl;
            errUrl.style.display = 'block';
          } else {
            errUrl.style.display = 'none';
          }
        }
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
    
    // Key metrics (same as box detail page)
    document.getElementById('bbp-floor-price').textContent = formatCurrency(metrics.floor_price_usd);
    const el24h = document.getElementById('bbp-24h-change');
    if (el24h) el24h.innerHTML = metrics.floor_price_1d_change_pct != null ? formatPercent(metrics.floor_price_1d_change_pct) : '—';
    document.getElementById('bbp-volume-7d').textContent = formatCurrency(metrics.unified_volume_7d_ema || metrics.unified_volume_usd);
    document.getElementById('bbp-days-20').textContent = metrics.days_to_20pct_increase != null ? Math.round(metrics.days_to_20pct_increase) : 'N/A';
    // Volume change (DoD)
    const volChangeWrap = document.getElementById('bbp-volume-change-wrap');
    const volChangeEl = document.getElementById('bbp-volume-change');
    if (volChangeWrap && volChangeEl && metrics.volume_1d_change_pct != null) {
      volChangeWrap.style.display = 'block';
      volChangeEl.innerHTML = `<span class="${metrics.volume_1d_change_pct >= 0 ? 'bbp-positive' : 'bbp-negative'}">${metrics.volume_1d_change_pct >= 0 ? '▲' : '▼'} ${Math.abs(metrics.volume_1d_change_pct).toFixed(1)}%</span>`;
    } else if (volChangeWrap) volChangeWrap.style.display = 'none';
    // Community sentiment (same as box detail)
    const sentiment = metrics.community_sentiment != null ? metrics.community_sentiment : 50;
    const sentimentVal = document.getElementById('bbp-sentiment-value');
    const sentimentFill = document.getElementById('bbp-sentiment-fill');
    if (sentimentVal) sentimentVal.textContent = Math.round(sentiment) + '/100';
    if (sentimentFill) sentimentFill.style.width = Math.min(100, Math.max(0, sentiment)) + '%';
    // Grid metrics
    const liqLabel = metrics.liquidity_score >= 70 ? 'High' : metrics.liquidity_score >= 40 ? 'Moderate' : 'Low';
    document.getElementById('bbp-liquidity').textContent = metrics.liquidity_score != null ? liqLabel : '—';
    document.getElementById('bbp-listings').textContent = formatNumber(metrics.active_listings_count);
    document.getElementById('bbp-sales-day').textContent = (metrics.boxes_sold_30d_avg != null ? (Math.round(metrics.boxes_sold_30d_avg * 10) / 10) : metrics.sales_per_day != null ? (Math.round(metrics.sales_per_day * 10) / 10) : '—').toString();
    document.getElementById('bbp-time-sale').textContent = (metrics.expected_time_to_sale_days != null || metrics.expected_days_to_sell != null) ? (Number(metrics.expected_time_to_sale_days || metrics.expected_days_to_sell).toFixed(2) + ' days') : 'N/A';
    document.getElementById('bbp-top10').textContent = (metrics.top_10_value_usd != null) ? formatCurrency(metrics.top_10_value_usd) : '—';
    document.getElementById('bbp-daily-volume').textContent = formatCurrency(metrics.daily_volume_usd);
    const reprintRisk = (box.reprint_risk || 'UNKNOWN').toString();
    const riskClass = reprintRisk.toLowerCase() === 'low' ? 'bbp-risk-low' : reprintRisk.toLowerCase() === 'high' ? 'bbp-risk-high' : 'bbp-risk-medium';
    document.getElementById('bbp-reprint-risk').innerHTML = '<span class="' + riskClass + '">' + reprintRisk + '</span>';
    const dashboardLink = panelElement.querySelector('.bbp-dashboard-link');
    dashboardLink.href = 'http://localhost:3000/boxes/' + box.id;
    currentBoxData = data;
    const cmp1 = document.getElementById('bbp-compare-box1-name');
    if (cmp1) cmp1.textContent = box.set_code || currentSetCode;
  }

  /**
   * Setup event listeners
   */
  function setupEventListeners() {
    if (!panelElement) return;
    
    // Collapse button - slides panel to edge (panel is on LEFT)
    const collapseBtn = panelElement.querySelector('.bbp-btn-collapse');
    collapseBtn.addEventListener('click', () => {
      const isCollapsed = panelElement.classList.toggle('bbp-collapsed');
      collapseBtn.textContent = isCollapsed ? '◀' : '▶';
      collapseBtn.title = isCollapsed ? 'Expand' : 'Collapse';
    });
    
    // Also allow clicking header to expand when collapsed
    panelElement.querySelector('.bbp-panel-header').addEventListener('click', (e) => {
      if (panelElement.classList.contains('bbp-collapsed') && e.target !== collapseBtn) {
        panelElement.classList.remove('bbp-collapsed');
        collapseBtn.textContent = '▶';
        collapseBtn.title = 'Collapse';
      }
    });
    
    // Close button - now collapses instead of hiding (so tab stays visible)
    panelElement.querySelector('.bbp-btn-close').addEventListener('click', () => {
      panelElement.classList.add('bbp-collapsed');
      collapseBtn.textContent = '◀';
      collapseBtn.title = 'Expand';
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
    
    // Days to +20%
    document.getElementById('bbp-cmp-days1').textContent = m1.days_to_20pct_increase ? `${Math.round(m1.days_to_20pct_increase)} days` : '—';
    document.getElementById('bbp-cmp-days2').textContent = m2.days_to_20pct_increase ? `${Math.round(m2.days_to_20pct_increase)} days` : '—';
  }

  /**
   * Main detection and fetch function
   * @param {number} retryCount - Number of detection retries
   * @param {boolean} forceShow - If true, show panel even if no box detected (user clicked button)
   */
  async function detectAndFetch(retryCount = 0, forceShow = false) {
    // Show loading state only if panel is visible or forceShow
    if (panelElement && (panelElement.style.display !== 'none' || forceShow)) {
      panelElement.querySelector('.bbp-loading').style.display = 'flex';
      panelElement.querySelector('.bbp-box-info').style.display = 'none';
      panelElement.querySelector('.bbp-no-box').style.display = 'none';
      panelElement.querySelector('.bbp-error').style.display = 'none';
    }
    
    // Detect set code
    currentSetCode = extractSetCode();
    console.log(`[BBP] Detected set code: ${currentSetCode} (attempt ${retryCount + 1})`);
    
    // If not found and we haven't retried enough, wait and try again
    // TCGplayer loads content dynamically
    if (!currentSetCode && retryCount < 3) {
      console.log(`[BBP] No set code found, retrying in 500ms...`);
      setTimeout(() => detectAndFetch(retryCount + 1, forceShow), 500);
      return;
    }
    
    if (!currentSetCode) {
      // No box detected - only show panel if user explicitly requested (forceShow)
      if (forceShow && panelElement) {
        panelElement.style.display = 'block';
        updatePanel(null);
      } else if (panelElement) {
        // Hide panel completely on non-applicable pages
        panelElement.style.display = 'none';
      }
      chrome.runtime.sendMessage({ action: 'noBoxDetected' });
      return;
    }
    
    // Box detected - show panel and fetch data
    if (panelElement) {
      panelElement.style.display = 'block';
      panelElement.classList.remove('bbp-collapsed');
    }
    
    // Fetch data from background script (with timeout so we never hang on loading)
    const FETCH_TIMEOUT_MS = 12000;
    try {
      const response = await Promise.race([
        chrome.runtime.sendMessage({
          action: 'fetchBoxData',
          setCode: currentSetCode
        }),
        new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Request timed out')), FETCH_TIMEOUT_MS)
        )
      ]);
      updatePanel(response);
    } catch (error) {
      console.error('[BBP] Error fetching data:', error);
      const isTimeout = error && (error.message === 'Request timed out' || error.message === 'Timeout');
      updatePanel({
        matched: false,
        error: isTimeout
          ? "Request timed out. Is the backend running at http://localhost:8000? Start it with python main.py, then click Retry."
          : "Could not reach the extension or API. Refresh this page, ensure the backend is running at http://localhost:8000, then click Retry.",
        apiBaseUrl: 'http://localhost:8000'
      });
    }
  }

  /**
   * Initialize extension
   */
  function init(forceShow = false) {
    console.log('[BBP] Initializing BoosterBoxPro panel');
    
    // Create and inject panel (hidden by default)
    panelElement = createPanel();
    panelElement.style.display = 'none'; // Hide initially
    document.body.appendChild(panelElement);
    
    // Setup event listeners
    setupEventListeners();
    
    // Detect and fetch data - only show if applicable
    detectAndFetch(0, forceShow);
    
    // Re-detect on navigation (SPA support)
    let lastUrl = location.href;
    new MutationObserver(() => {
      const url = location.href;
      if (url !== lastUrl) {
        lastUrl = url;
        console.log('[BBP] URL changed, re-detecting...');
        setTimeout(() => detectAndFetch(0, false), 500); // Small delay for page to load
      }
    }).observe(document, { subtree: true, childList: true });
  }

  // Listen for messages from popup/background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('[BBP] Received message:', request);
    
    if (request.action === 'ping') {
      // Used to check if content script is loaded
      sendResponse({ pong: true });
      return true;
    }
    
    if (request.action === 'showPanel' || request.action === 'togglePanel') {
      // User manually triggered - show panel even if no box detected (forceShow=true)
      if (!panelElement) {
        init(true); // forceShow = true
      } else {
        panelElement.style.display = 'block';
        panelElement.classList.remove('bbp-collapsed');
        const collapseBtn = panelElement.querySelector('.bbp-btn-collapse');
        if (collapseBtn) {
          collapseBtn.textContent = '▶';
          collapseBtn.title = 'Collapse';
        }
        detectAndFetch(0, true); // forceShow = true
      }
      sendResponse({ success: true });
    }
    
    return true;
  });

  // Start when DOM is ready (auto-detect, don't force show)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init(false));
  } else {
    init(false); // Don't force show - only show if box detected
  }

})();
