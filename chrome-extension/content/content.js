/**
 * BoosterBoxPro Chrome Extension - Content Script
 * Auto-detects One Piece booster boxes on TCGplayer & eBay and displays market data panel
 */

(function() {
  'use strict';

  const DEBUG = false;
  function log(...args) { if (DEBUG) console.log('[BBP]', ...args); }

  // Prevent multiple injections - if already loaded, just show the panel
  if (window.__bbpLoaded) {
    log('Already loaded, showing panel');
    const existingPanel = document.getElementById('bbp-panel');
    if (existingPanel) {
      existingPanel.style.display = 'flex';
      existingPanel.classList.remove('bbp-collapsed');
    }
    return;
  }
  window.__bbpLoaded = true;

  const siteName = window.location.hostname.includes('ebay') ? 'eBay' : 'TCGplayer';
  log(`Content script loaded on ${siteName}`);

  // Config fetched from background at init
  let config = { dashboardUrl: 'https://booster-box-pro.vercel.app' };

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

  // State
  let currentSetCode = null;
  let currentBoxData = null;
  let panelElement = null;
  let isCompareMode = false;
  let compareBoxData = null;
  let panelOpenedAt = null;
  // Track which boxes the user has already seen (auto-opened) this session
  let seenBoxesThisSession = new Set();
  // Whether the user explicitly collapsed/closed the panel
  let userDismissed = false;

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
   * Try to match a set code from a single text string.
   * Returns "OP-XX" / "EB-XX" / "PRB-XX" or null.
   */
  function matchSetCode(text) {
    if (!text) return null;
    const lower = text.toLowerCase();

    // Try set name mapping first — most reliable, avoids false regex matches
    for (const [setName, setCode] of Object.entries(SET_NAME_MAP)) {
      if (lower.includes(setName)) {
        return setCode;
      }
    }

    // Regex patterns — only match codes that look like our tracked boxes
    const patterns = [
      /\b(op|eb|prb)-(\d{1,2})\b/i,
      /\b(op|eb|prb)(\d{1,2})\b/i,
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        const prefix = match[1].toUpperCase();
        const num = match[2].padStart(2, '0');
        const candidate = `${prefix}-${num}`;
        // Only return codes within our known range to avoid false positives
        const n = parseInt(num, 10);
        if (prefix === 'OP' && n >= 1 && n <= 13) return candidate;
        if (prefix === 'EB' && n >= 1 && n <= 2) return candidate;
        if (prefix === 'PRB' && n >= 1 && n <= 2) return candidate;
      }
    }

    return null;
  }

  /**
   * Extract set code from page using priority-ordered sources.
   * Checks URL first (most reliable on navigation), then H1/product title,
   * then breadcrumbs, then body text as last resort.
   */
  function extractSetCode() {
    // 1. URL — most reliable after SPA navigation
    const url = decodeURIComponent(window.location.href);
    const urlCode = matchSetCode(url);
    if (urlCode) {
      log(`Found set code in URL: ${urlCode}`);
      return urlCode;
    }

    // 2. Page title (browser tab)
    const titleCode = matchSetCode(document.title);
    if (titleCode) {
      log(`Found set code in title: ${titleCode}`);
      return titleCode;
    }

    // 3. H1 / product title element — specific to the viewed product
    const h1 = document.querySelector('h1');
    if (h1) {
      const h1Code = matchSetCode(h1.textContent);
      if (h1Code) {
        log(`Found set code in H1: ${h1Code}`);
        return h1Code;
      }
    }

    // 4. eBay product page title selectors
    if (siteName === 'eBay') {
      const ebaySelectors = [
        'h1.x-item-title__mainTitle span.ux-textspans',
        'h1.it-title',
        '#itemTitle',
        '.vim.x-item-title span.ux-textspans',
      ];
      for (const sel of ebaySelectors) {
        const el = document.querySelector(sel);
        if (el) {
          const code = matchSetCode(el.textContent);
          if (code) {
            log(`Found set code in eBay title: ${code}`);
            return code;
          }
        }
      }
    }

    // 5. TCGplayer product title element
    const productTitle = document.querySelector(
      '[class*="product-details__name"], [class*="ProductDetails__name"]'
    );
    if (productTitle) {
      const ptCode = matchSetCode(productTitle.textContent);
      if (ptCode) {
        log(`Found set code in product title: ${ptCode}`);
        return ptCode;
      }
    }

    // 6. Breadcrumbs
    const breadcrumbs = document.querySelectorAll('[class*="breadcrumb"] a, nav a');
    for (const el of breadcrumbs) {
      const bcCode = matchSetCode(el.textContent);
      if (bcCode) {
        log(`Found set code in breadcrumb: ${bcCode}`);
        return bcCode;
      }
    }

    // 7. eBay search results — detect if viewing a search for booster boxes
    if (siteName === 'eBay') {
      const searchInput = document.querySelector('input#gh-ac');
      if (searchInput && searchInput.value) {
        const code = matchSetCode(searchInput.value);
        if (code) {
          log(`Found set code in eBay search: ${code}`);
          return code;
        }
      }
    }

    // 8. Body text (first 3000 chars) — last resort, may pick up related products
    if (document.body) {
      const bodyCode = matchSetCode(document.body.innerText.substring(0, 3000));
      if (bodyCode) {
        log(`Found set code in body text: ${bodyCode}`);
        return bodyCode;
      }
    }

    log('No set code detected on this page');
    return null;
  }

  /**
   * Mark a box as seen so it won't auto-open again within this tab.
   * Tracking is purely in-memory (per-tab). Each new tab starts fresh.
   */
  function markBoxSeen(setCode) {
    seenBoxesThisSession.add(setCode);
  }

  /**
   * Load saved panel height from storage
   */
  async function loadPanelHeight() {
    try {
      const { bbpPanelHeight } = await chrome.storage.local.get('bbpPanelHeight');
      return bbpPanelHeight || null;
    } catch (e) {
      return null;
    }
  }

  /**
   * Save panel height to storage
   */
  async function savePanelHeight(height) {
    try {
      await chrome.storage.local.set({ bbpPanelHeight: height });
    } catch (e) {
      // storage unavailable
    }
  }

  /**
   * Load saved panel position from storage
   */
  async function loadPanelPosition() {
    try {
      const { bbpPanelPos } = await chrome.storage.local.get('bbpPanelPos');
      return bbpPanelPos || null; // { top, left }
    } catch (e) {
      return null;
    }
  }

  /**
   * Save panel position to storage
   */
  async function savePanelPosition(top, left) {
    try {
      await chrome.storage.local.set({ bbpPanelPos: { top, left } });
    } catch (e) {
      // storage unavailable
    }
  }

  /**
   * Load collapsed state from session storage.
   * Returns the set code the user collapsed on, or null.
   */
  async function loadCollapsedState() {
    try {
      const { bbpCollapsedSetCode } = await chrome.storage.session.get('bbpCollapsedSetCode');
      return bbpCollapsedSetCode || null;
    } catch (e) {
      return null;
    }
  }

  /**
   * Save collapsed state — records which box was collapsed so it survives page refresh.
   */
  async function saveCollapsedState(setCode) {
    if (!setCode) return;
    try {
      await chrome.storage.session.set({ bbpCollapsedSetCode: setCode });
    } catch (e) {
      // storage unavailable
    }
  }

  /**
   * Clear collapsed state (user expanded or navigated to a different box).
   */
  async function clearCollapsedState() {
    try {
      await chrome.storage.session.remove('bbpCollapsedSetCode');
    } catch (e) {
      // storage unavailable
    }
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
      <div class="bbp-panel-header" id="bbp-drag-handle">
        <div class="bbp-logo">
          <img src="${logoUrl}" alt="BoosterPro" class="bbp-logo-img" onerror="this.style.display='none'">
          <span class="bbp-title">BoosterPro</span>
        </div>
        <div class="bbp-controls">
          <button class="bbp-btn-collapse" title="Collapse"><svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.5 3L9.5 7L5.5 11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></button>
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
                <div class="bbp-key-metric-label">24h Volume</div>
                <div class="bbp-key-metric-value" id="bbp-volume-24h">—</div>
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
                <div class="bbp-stat"><span class="bbp-stat-label">Sold Today</span><span class="bbp-stat-value" id="bbp-sales-day">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Time to Sale</span><span class="bbp-stat-value" id="bbp-time-sale">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Top 10 Value</span><span class="bbp-stat-value" id="bbp-top10">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Daily Vol</span><span class="bbp-stat-value" id="bbp-daily-volume">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Reprint Risk</span><span class="bbp-stat-value" id="bbp-reprint-risk">—</span></div>
                <div class="bbp-stat"><span class="bbp-stat-label">Listings Added</span><span class="bbp-stat-value" id="bbp-listings-added">—</span></div>
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
          <button class="bbp-retry-btn">Retry</button>
        </div>
      </div>
      <div class="bbp-resize-handle"></div>
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
   * Apply a percentage value to an element using textContent (XSS-safe).
   * Sets text and toggles bbp-positive / bbp-negative classes.
   */
  function applyPercent(element, value) {
    if (value === null || value === undefined) { element.textContent = '—'; return; }
    const sign = value >= 0 ? '+' : '';
    const arrow = value > 0 ? ' ▲' : value < 0 ? ' ▼' : '';
    element.textContent = `${sign}${value.toFixed(1)}%${arrow}`;
    element.classList.remove('bbp-positive', 'bbp-negative');
    if (value > 0) element.classList.add('bbp-positive');
    else if (value < 0) element.classList.add('bbp-negative');
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
      } else {
        noBox.style.display = 'block';
      }
      chrome.runtime.sendMessage({ action: 'noBoxDetected' });
      return;
    }

    boxInfo.style.display = 'block';
    noBox.style.display = 'none';
    error.style.display = 'none';
    chrome.runtime.sendMessage({ action: 'boxDetected' });

    trackEvent('extension_box_detected', { set_code: data.box?.set_code || currentSetCode, site: siteName });
    trackEvent('extension_panel_opened', { set_code: data.box?.set_code || currentSetCode, site: siteName });
    panelOpenedAt = Date.now();

    const box = data.box;
    const metrics = data.metrics;

    // Update box info
    panelElement.querySelector('.bbp-box-name').textContent = box.product_name;

    // Update image if available
    const img = panelElement.querySelector('.bbp-box-image');
    if (box.image_url) {
      img.src = `${config.dashboardUrl}${box.image_url}`;
      img.style.display = 'block';
    } else {
      img.style.display = 'none';
    }

    // Key metrics (same as box detail page)
    document.getElementById('bbp-floor-price').textContent = formatCurrency(metrics.floor_price_usd);
    const el24h = document.getElementById('bbp-24h-change');
    if (el24h) {
      if (metrics.floor_price_1d_change_pct != null) {
        applyPercent(el24h, metrics.floor_price_1d_change_pct);
      } else {
        el24h.textContent = '—';
      }
    }
    document.getElementById('bbp-volume-24h').textContent = formatCurrency(metrics.daily_volume_usd);
    document.getElementById('bbp-days-20').textContent = metrics.days_to_20pct_increase != null ? Math.round(metrics.days_to_20pct_increase) : 'No squeeze';
    // Volume change (DoD)
    const volChangeWrap = document.getElementById('bbp-volume-change-wrap');
    const volChangeEl = document.getElementById('bbp-volume-change');
    if (volChangeWrap && volChangeEl && metrics.volume_1d_change_pct != null) {
      volChangeWrap.style.display = 'block';
      const arrow = metrics.volume_1d_change_pct >= 0 ? '▲' : '▼';
      volChangeEl.textContent = `${arrow} ${Math.abs(metrics.volume_1d_change_pct).toFixed(1)}%`;
      volChangeEl.classList.remove('bbp-positive', 'bbp-negative');
      volChangeEl.classList.add(metrics.volume_1d_change_pct >= 0 ? 'bbp-positive' : 'bbp-negative');
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
    document.getElementById('bbp-sales-day').textContent = (metrics.boxes_sold_today != null ? (Math.round(metrics.boxes_sold_today * 10) / 10) : metrics.boxes_sold_30d_avg != null ? (Math.round(metrics.boxes_sold_30d_avg * 10) / 10) : '—').toString();
    document.getElementById('bbp-time-sale').textContent = (metrics.expected_time_to_sale_days != null || metrics.expected_days_to_sell != null) ? (Number(metrics.expected_time_to_sale_days || metrics.expected_days_to_sell).toFixed(2) + ' days') : 'N/A';
    document.getElementById('bbp-top10').textContent = (metrics.top_10_value_usd != null) ? formatCurrency(metrics.top_10_value_usd) : '—';
    document.getElementById('bbp-daily-volume').textContent = formatCurrency(metrics.daily_volume_usd);
    const reprintRisk = (box.reprint_risk || 'UNKNOWN').toString();
    const riskClass = reprintRisk.toLowerCase() === 'low' ? 'bbp-risk-low' : reprintRisk.toLowerCase() === 'high' ? 'bbp-risk-high' : 'bbp-risk-medium';
    const reprintEl = document.getElementById('bbp-reprint-risk');
    reprintEl.textContent = reprintRisk;
    reprintEl.classList.remove('bbp-risk-low', 'bbp-risk-medium', 'bbp-risk-high');
    reprintEl.classList.add(riskClass);
    const listingsAdded = metrics.boxes_added_today != null ? metrics.boxes_added_today : (metrics.avg_boxes_added_per_day != null ? metrics.avg_boxes_added_per_day : null);
    document.getElementById('bbp-listings-added').textContent = listingsAdded != null ? formatNumber(Math.round(listingsAdded)) + '/day' : '—';
    const dashboardLink = panelElement.querySelector('.bbp-dashboard-link');
    dashboardLink.href = config.dashboardUrl + '/boxes/' + box.id;
    dashboardLink.addEventListener('click', () => {
      trackEvent('extension_dashboard_link_clicked', { set_code: box.set_code || currentSetCode, box_id: box.id });
    });
    currentBoxData = data;
    const cmp1 = document.getElementById('bbp-compare-box1-name');
    if (cmp1) cmp1.textContent = box.set_code || currentSetCode;
  }

  /**
   * Setup drag-to-move on the panel header
   */
  function setupDrag() {
    const handle = panelElement.querySelector('#bbp-drag-handle');
    let isDragging = false;
    let dragOffsetX = 0;
    let dragOffsetY = 0;

    handle.addEventListener('mousedown', (e) => {
      // Don't start drag on button clicks (walk up DOM to catch SVG children inside buttons)
      let el = e.target;
      while (el && el !== handle) {
        if (el.tagName === 'BUTTON') return;
        el = el.parentElement;
      }
      // Don't start drag when collapsed (header click expands)
      if (panelElement.classList.contains('bbp-collapsed')) return;

      isDragging = true;
      const rect = panelElement.getBoundingClientRect();
      dragOffsetX = e.clientX - rect.left;
      dragOffsetY = e.clientY - rect.top;
      panelElement.classList.add('bbp-dragging');
      e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return;

      let newLeft = e.clientX - dragOffsetX;
      let newTop = e.clientY - dragOffsetY;

      // Clamp to viewport
      const panelWidth = panelElement.offsetWidth;
      const panelHeight = panelElement.offsetHeight;
      newLeft = Math.max(0, Math.min(window.innerWidth - panelWidth, newLeft));
      newTop = Math.max(0, Math.min(window.innerHeight - panelHeight, newTop));

      panelElement.style.left = newLeft + 'px';
      panelElement.style.top = newTop + 'px';
      // Clear right/bottom so left/top take precedence
      panelElement.style.right = 'auto';
    });

    document.addEventListener('mouseup', () => {
      if (!isDragging) return;
      isDragging = false;
      panelElement.classList.remove('bbp-dragging');

      // Save position
      const rect = panelElement.getBoundingClientRect();
      savePanelPosition(rect.top, rect.left);
    });
  }

  /**
   * Setup drag-to-resize on the bottom handle
   */
  function setupResize() {
    const handle = panelElement.querySelector('.bbp-resize-handle');
    let isResizing = false;

    handle.addEventListener('mousedown', (e) => {
      if (panelElement.classList.contains('bbp-collapsed')) return;
      isResizing = true;
      panelElement.classList.add('bbp-resizing');
      document.body.style.userSelect = 'none';
      e.preventDefault();
    });

    document.addEventListener('mousemove', (e) => {
      if (!isResizing) return;
      const panelRect = panelElement.getBoundingClientRect();
      const minHeight = 120;
      const maxHeight = window.innerHeight - 100;
      let newHeight = e.clientY - panelRect.top;
      newHeight = Math.max(minHeight, Math.min(maxHeight, newHeight));
      panelElement.style.height = newHeight + 'px';
    });

    document.addEventListener('mouseup', () => {
      if (!isResizing) return;
      isResizing = false;
      panelElement.classList.remove('bbp-resizing');
      document.body.style.userSelect = '';
      savePanelHeight(panelElement.offsetHeight);
    });
  }

  /**
   * Setup event listeners
   */
  function setupEventListeners() {
    if (!panelElement) return;

    // Collapse button — minimizes to strip, does NOT set userDismissed
    // (panel will still auto-expand when navigating to a new box)
    const collapseBtn = panelElement.querySelector('.bbp-btn-collapse');
    let savedHeightBeforeCollapse = '';
    collapseBtn.addEventListener('click', () => {
      const isCollapsed = panelElement.classList.toggle('bbp-collapsed');
      if (isCollapsed) {
        trackEvent('extension_panel_collapsed', { set_code: currentSetCode });
        // Track session duration on collapse
        if (panelOpenedAt) {
          const durationSeconds = Math.round((Date.now() - panelOpenedAt) / 1000);
          trackEvent('extension_session_ended', { duration_seconds: durationSeconds, set_code: currentSetCode });
          panelOpenedAt = null;
        }
        savedHeightBeforeCollapse = panelElement.style.height;
        panelElement.style.height = '';
        saveCollapsedState(currentSetCode);
      } else {
        trackEvent('extension_panel_expanded', { set_code: currentSetCode });
        panelOpenedAt = Date.now();
        panelElement.style.height = savedHeightBeforeCollapse;
        clearCollapsedState();
      }
      collapseBtn.innerHTML = isCollapsed
        ? '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M8.5 3L4.5 7L8.5 11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
        : '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.5 3L9.5 7L5.5 11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
      collapseBtn.title = isCollapsed ? 'Expand' : 'Collapse';
    });

    // Also allow clicking header to expand when collapsed
    panelElement.querySelector('.bbp-panel-header').addEventListener('click', (e) => {
      let clickedEl = e.target;
      let isButton = false;
      while (clickedEl && clickedEl !== e.currentTarget) {
        if (clickedEl.tagName === 'BUTTON') { isButton = true; break; }
        clickedEl = clickedEl.parentElement;
      }
      if (panelElement.classList.contains('bbp-collapsed') && !isButton) {
        panelElement.classList.remove('bbp-collapsed');
        trackEvent('extension_panel_expanded', { set_code: currentSetCode });
        panelOpenedAt = Date.now();
        panelElement.style.height = savedHeightBeforeCollapse;
        collapseBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M5.5 3L9.5 7L5.5 11" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        collapseBtn.title = 'Collapse';
        clearCollapsedState();
      }
    });

    // Close button (X) — hides panel entirely until user clicks "Open Extension" in popup
    panelElement.querySelector('.bbp-btn-close').addEventListener('click', () => {
      trackEvent('extension_panel_dismissed', { set_code: currentSetCode });
      // Track session duration on dismiss
      if (panelOpenedAt) {
        const durationSeconds = Math.round((Date.now() - panelOpenedAt) / 1000);
        trackEvent('extension_session_ended', { duration_seconds: durationSeconds, set_code: currentSetCode });
        panelOpenedAt = null;
      }
      panelElement.style.display = 'none';
      userDismissed = true;
    });

    // Tab switching
    panelElement.querySelectorAll('.bbp-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        trackEvent('extension_tab_switched', { tab_name: tabName, set_code: currentSetCode });

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
      trackEvent('extension_compare_selected', { current_box: currentSetCode, compare_box: compareCode });

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
        log('Compare error:', err);
      }
    });

    // Retry button
    panelElement.querySelector('.bbp-retry-btn').addEventListener('click', () => {
      trackEvent('extension_retry_clicked', { set_code: currentSetCode });
      detectAndFetch();
    });

    // Drag to move
    setupDrag();

    // Resize from bottom edge
    setupResize();
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
    applyPercent(document.getElementById('bbp-cmp-change1'), m1.floor_price_30d_change_pct);
    applyPercent(document.getElementById('bbp-cmp-change2'), m2.floor_price_30d_change_pct);

    // Volume
    document.getElementById('bbp-cmp-volume1').textContent = formatCurrency(m1.daily_volume_usd);
    document.getElementById('bbp-cmp-volume2').textContent = formatCurrency(m2.daily_volume_usd);

    // Sales (boxes_sold_today primary, boxes_sold_30d_avg fallback — matches frontend)
    const sales1 = m1.boxes_sold_today != null ? m1.boxes_sold_today : m1.boxes_sold_30d_avg;
    const sales2 = m2.boxes_sold_today != null ? m2.boxes_sold_today : m2.boxes_sold_30d_avg;
    document.getElementById('bbp-cmp-sales1').textContent = sales1 != null ? Number(sales1).toFixed(1) : '—';
    document.getElementById('bbp-cmp-sales2').textContent = sales2 != null ? Number(sales2).toFixed(1) : '—';

    // Liquidity (categorical: High/Moderate/Low — matches stats tab and frontend)
    document.getElementById('bbp-cmp-liq1').textContent = m1.liquidity_score != null ? (m1.liquidity_score >= 70 ? 'High' : m1.liquidity_score >= 40 ? 'Moderate' : 'Low') : '—';
    document.getElementById('bbp-cmp-liq2').textContent = m2.liquidity_score != null ? (m2.liquidity_score >= 70 ? 'High' : m2.liquidity_score >= 40 ? 'Moderate' : 'Low') : '—';

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
    const panelAlreadyVisible = panelElement && panelElement.style.display !== 'none';

    // Show loading state only when:
    // - User explicitly clicked "Open Extension" (forceShow)
    // - Panel is already visible (e.g., SPA navigation between box pages)
    // For auto-detection on a new page, panel stays hidden until API confirms a match.
    if (panelElement && (forceShow || panelAlreadyVisible)) {
      if (forceShow) {
        panelElement.style.display = 'flex';
        panelElement.classList.remove('bbp-collapsed');
        userDismissed = false;
        clearCollapsedState();
      }
      panelElement.querySelector('.bbp-loading').style.display = 'flex';
      panelElement.querySelector('.bbp-box-info').style.display = 'none';
      panelElement.querySelector('.bbp-no-box').style.display = 'none';
      panelElement.querySelector('.bbp-error').style.display = 'none';
    }

    // Detect set code
    const newSetCode = extractSetCode();
    log(`Detected set code: ${newSetCode} (attempt ${retryCount + 1})`);

    // If not found and we haven't retried enough, wait and try again
    // TCGplayer loads content dynamically
    if (!newSetCode && retryCount < 3) {
      log('No set code found, retrying in 500ms...');
      setTimeout(() => detectAndFetch(retryCount + 1, forceShow), 500);
      return;
    }

    if (!newSetCode) {
      // No box detected
      currentSetCode = null;
      if (forceShow && panelElement) {
        // User explicitly opened — show "no box" message
        updatePanel(null);
      } else if (panelElement) {
        // Auto-detect found nothing — hide panel silently
        panelElement.style.display = 'none';
      }
      chrome.runtime.sendMessage({ action: 'noBoxDetected' });
      return;
    }

    // Determine if this is a new box the user hasn't seen yet
    const isNewBox = newSetCode !== currentSetCode;
    const isFirstTimeSeeingThisBox = !seenBoxesThisSession.has(newSetCode);
    currentSetCode = newSetCode;
    markBoxSeen(newSetCode);

    // DON'T show panel yet for auto-detection — wait for API to confirm match.
    // forceShow case already handled above (panel visible with loading spinner).

    // Fetch data from background script
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

      // After API response: show panel only if box matched (unless forceShow, already visible)
      if (!forceShow && panelElement) {
        if (response && response.matched && !userDismissed) {
          // API confirmed match — now show the panel
          panelElement.style.display = 'flex';
          if (isFirstTimeSeeingThisBox) {
            const collapsedCode = await loadCollapsedState();
            if (collapsedCode === newSetCode) {
              panelElement.classList.add('bbp-collapsed');
            } else {
              panelElement.classList.remove('bbp-collapsed');
              clearCollapsedState();
            }
          } else if (isNewBox) {
            panelElement.classList.remove('bbp-collapsed');
            clearCollapsedState();
          }
        } else if (!response || !response.matched) {
          // Not matched — hide panel
          panelElement.style.display = 'none';
          chrome.runtime.sendMessage({ action: 'noBoxDetected' });
          return;
        }
      }

      updatePanel(response);
    } catch (error) {
      log('Error fetching data:', error);
      const isTimeout = error && (error.message === 'Request timed out' || error.message === 'Timeout');
      if (forceShow || panelAlreadyVisible) {
        // Show error only if panel was explicitly opened or already visible
        updatePanel({
          matched: false,
          error: isTimeout
            ? 'Request timed out. Please click Retry.'
            : 'Unable to connect to BoosterBoxPro. Please try again in a moment.'
        });
      } else if (panelElement) {
        // Auto-detect error — silently hide
        panelElement.style.display = 'none';
      }
    }
  }

  /**
   * Initialize extension
   */
  async function init(forceShow = false) {
    log('Initializing BoosterBoxPro panel');

    // Fetch config from background
    try {
      const cfg = await chrome.runtime.sendMessage({ action: 'getConfig' });
      if (cfg && cfg.dashboardUrl) config = cfg;
    } catch (e) {
      // Use defaults
    }

    // Create and inject panel — keep hidden until a box is actually detected
    // (prevents the panel from flashing on irrelevant pages like eBay homepage)
    panelElement = createPanel();
    panelElement.style.display = forceShow ? 'flex' : 'none';
    document.body.appendChild(panelElement);

    // Restore saved position or use default (right side)
    const savedPos = await loadPanelPosition();
    if (savedPos) {
      panelElement.style.top = savedPos.top + 'px';
      panelElement.style.left = savedPos.left + 'px';
      panelElement.style.right = 'auto';
    }

    // Restore saved height
    const savedHeight = await loadPanelHeight();
    if (savedHeight) {
      panelElement.style.height = savedHeight + 'px';
    }

    // Setup event listeners
    setupEventListeners();

    // Detect and fetch data
    detectAndFetch(0, forceShow);

    // Re-detect on SPA navigation
    let lastUrl = location.href;
    new MutationObserver(() => {
      const url = location.href;
      if (url !== lastUrl) {
        lastUrl = url;
        log('URL changed, re-detecting...');
        // Do NOT reset userDismissed — if user clicked X, panel stays hidden
        // until they click "Open Extension" in the Chrome popup
        setTimeout(() => detectAndFetch(0, false), 600);
      }
    }).observe(document, { subtree: true, childList: true });
  }

  // Listen for messages from popup/background
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    log('Received message:', request);

    if (request.action === 'ping') {
      // Used to check if content script is loaded
      sendResponse({ pong: true });
      return true;
    }

    if (request.action === 'showPanel' || request.action === 'togglePanel') {
      // User manually triggered - show panel even if no box detected (forceShow=true)
      userDismissed = false;
      if (!panelElement) {
        init(true); // forceShow = true
      } else {
        panelElement.style.display = 'flex';
        panelElement.classList.remove('bbp-collapsed');
        detectAndFetch(0, true); // forceShow = true
      }
      sendResponse({ success: true });
    }

    return true;
  });

  // Track session end on page unload
  window.addEventListener('beforeunload', () => {
    if (panelOpenedAt && currentSetCode) {
      const durationSeconds = Math.round((Date.now() - panelOpenedAt) / 1000);
      trackEvent('extension_session_ended', { duration_seconds: durationSeconds, set_code: currentSetCode });
    }
  });

  // Start when DOM is ready (auto-detect, don't force show)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init(false));
  } else {
    init(false);
  }

})();
