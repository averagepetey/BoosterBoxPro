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

    // Regex patterns in priority order
    const patterns = [
      /[([\s]?(op|eb|prb)[-\s]?(\d{1,2})[\s)\]]/i,
      /\b(op|eb|prb)-(\d{1,2})\b/i,
      /\b(op|eb|prb)(\d{1,2})\b/i,
      /(op|eb|prb)[-\s]?(\d{1,2})/i,
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);
      if (match) {
        const prefix = match[1].toUpperCase();
        const num = match[2].padStart(2, '0');
        return `${prefix}-${num}`;
      }
    }

    // Try set name mapping
    for (const [setName, setCode] of Object.entries(SET_NAME_MAP)) {
      if (lower.includes(setName)) {
        return setCode;
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
      console.log(`[BBP] Found set code in URL: ${urlCode}`);
      return urlCode;
    }

    // 2. Page title (browser tab)
    const titleCode = matchSetCode(document.title);
    if (titleCode) {
      console.log(`[BBP] Found set code in title: ${titleCode}`);
      return titleCode;
    }

    // 3. H1 / product title element — specific to the viewed product
    const h1 = document.querySelector('h1');
    if (h1) {
      const h1Code = matchSetCode(h1.textContent);
      if (h1Code) {
        console.log(`[BBP] Found set code in H1: ${h1Code}`);
        return h1Code;
      }
    }

    const productTitle = document.querySelector(
      '[class*="product-details__name"], [class*="ProductDetails__name"]'
    );
    if (productTitle) {
      const ptCode = matchSetCode(productTitle.textContent);
      if (ptCode) {
        console.log(`[BBP] Found set code in product title: ${ptCode}`);
        return ptCode;
      }
    }

    // 4. Breadcrumbs
    const breadcrumbs = document.querySelectorAll('[class*="breadcrumb"] a, nav a');
    for (const el of breadcrumbs) {
      const bcCode = matchSetCode(el.textContent);
      if (bcCode) {
        console.log(`[BBP] Found set code in breadcrumb: ${bcCode}`);
        return bcCode;
      }
    }

    // 5. Body text (first 3000 chars) — last resort, may pick up related products
    if (document.body) {
      const bodyCode = matchSetCode(document.body.innerText.substring(0, 3000));
      if (bodyCode) {
        console.log(`[BBP] Found set code in body text: ${bodyCode}`);
        return bodyCode;
      }
    }

    console.log('[BBP] No set code detected on this page');
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
          <button class="bbp-btn-collapse" title="Collapse">▶</button>
          <button class="bbp-btn-minimize" title="Minimize">−</button>
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
    noBox.style.display = 'none';
    error.style.display = 'none';
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
    const listingsAdded = metrics.boxes_added_today != null ? metrics.boxes_added_today : (metrics.avg_boxes_added_per_day != null ? metrics.avg_boxes_added_per_day : null);
    document.getElementById('bbp-listings-added').textContent = listingsAdded != null ? formatNumber(Math.round(listingsAdded)) + '/day' : '—';
    const dashboardLink = panelElement.querySelector('.bbp-dashboard-link');
    dashboardLink.href = 'http://localhost:3000/boxes/' + box.id;
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
      // Don't start drag on button clicks
      if (e.target.closest('button')) return;
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
   * Setup event listeners
   */
  function setupEventListeners() {
    if (!panelElement) return;

    // Collapse button — minimizes to strip, does NOT set userDismissed
    // (panel will still auto-expand when navigating to a new box)
    const collapseBtn = panelElement.querySelector('.bbp-btn-collapse');
    collapseBtn.addEventListener('click', () => {
      const isCollapsed = panelElement.classList.toggle('bbp-collapsed');
      collapseBtn.textContent = isCollapsed ? '◀' : '▶';
      collapseBtn.title = isCollapsed ? 'Expand' : 'Collapse';
    });

    // Also allow clicking header to expand when collapsed
    panelElement.querySelector('.bbp-panel-header').addEventListener('click', (e) => {
      if (panelElement.classList.contains('bbp-collapsed') && !e.target.closest('button')) {
        panelElement.classList.remove('bbp-collapsed');
        collapseBtn.textContent = '▶';
        collapseBtn.title = 'Collapse';
      }
    });

    // Minimize button (−) — toggles between full height and compact scrollable view
    const minimizeBtn = panelElement.querySelector('.bbp-btn-minimize');
    minimizeBtn.addEventListener('click', () => {
      const isMinimized = panelElement.classList.toggle('bbp-minimized');
      minimizeBtn.textContent = isMinimized ? '+' : '−';
      minimizeBtn.title = isMinimized ? 'Expand' : 'Minimize';
    });

    // Close button (X) — hides panel entirely until user clicks "Open Extension" in popup
    panelElement.querySelector('.bbp-btn-close').addEventListener('click', () => {
      panelElement.style.display = 'none';
      userDismissed = true;
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

    // Drag to move
    setupDrag();
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
    const newSetCode = extractSetCode();
    console.log(`[BBP] Detected set code: ${newSetCode} (attempt ${retryCount + 1})`);

    // If not found and we haven't retried enough, wait and try again
    // TCGplayer loads content dynamically
    if (!newSetCode && retryCount < 3) {
      console.log(`[BBP] No set code found, retrying in 500ms...`);
      setTimeout(() => detectAndFetch(retryCount + 1, forceShow), 500);
      return;
    }

    if (!newSetCode) {
      // No box detected
      currentSetCode = null;
      if (forceShow && panelElement) {
        panelElement.style.display = 'block';
        updatePanel(null);
      } else if (panelElement) {
        panelElement.style.display = 'none';
      }
      chrome.runtime.sendMessage({ action: 'noBoxDetected' });
      return;
    }

    // Determine if this is a new box the user hasn't seen yet
    const isNewBox = newSetCode !== currentSetCode;
    const isFirstTimeSeeingThisBox = !seenBoxesThisSession.has(newSetCode);
    currentSetCode = newSetCode;

    // Decide whether to show/expand the panel
    if (forceShow) {
      // User clicked "Open Extension" in popup — always show expanded
      panelElement.style.display = 'block';
      panelElement.classList.remove('bbp-collapsed');
      userDismissed = false;
    } else if (userDismissed) {
      // User clicked X — panel stays hidden until they click "Open Extension"
      // Just update data silently in the background
    } else if (isFirstTimeSeeingThisBox) {
      // First time seeing this box in this tab — auto-open expanded
      panelElement.style.display = 'block';
      panelElement.classList.remove('bbp-collapsed');
    } else if (isNewBox) {
      // Different box (previously seen in this tab) — keep panel visible, don't force expand
      panelElement.style.display = 'block';
    }
    // Same box, same state — keep as-is

    // Mark this box as seen
    markBoxSeen(newSetCode);

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
  async function init(forceShow = false) {
    console.log('[BBP] Initializing BoosterBoxPro panel');

    // Create and inject panel (hidden by default)
    panelElement = createPanel();
    panelElement.style.display = 'none'; // Hide initially
    document.body.appendChild(panelElement);

    // Restore saved position or use default (right side)
    const savedPos = await loadPanelPosition();
    if (savedPos) {
      panelElement.style.top = savedPos.top + 'px';
      panelElement.style.left = savedPos.left + 'px';
      panelElement.style.right = 'auto';
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
        console.log('[BBP] URL changed, re-detecting...');
        // Do NOT reset userDismissed — if user clicked X, panel stays hidden
        // until they click "Open Extension" in the Chrome popup
        setTimeout(() => detectAndFetch(0, false), 600);
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
      userDismissed = false;
      if (!panelElement) {
        init(true); // forceShow = true
      } else {
        panelElement.style.display = 'block';
        panelElement.classList.remove('bbp-collapsed');
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
    init(false);
  }

})();
