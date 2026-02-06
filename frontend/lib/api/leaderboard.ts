/**
 * Leaderboard API
 * Functions for fetching leaderboard data
 */

import { getAuthToken } from '@/lib/api/client';

export interface LeaderboardParams {
  sort?: string;
  limit?: number;
  offset?: number;
  date?: string;
}

export interface BoxMetricsSummary {
  floor_price_usd?: number | null;
  floor_price_1d_change_pct?: number | null;
  floor_price_30d_change_pct?: number | null;
  daily_volume_usd?: number | null;
  unified_volume_7d_ema?: number | null;
  unified_volume_usd?: number | null; // 30d volume
  volume_7d?: number | null; // 7d rolling sum
  volume_30d?: number | null; // 30d rolling sum
  volume_1d_change_pct?: number | null; // day-over-day volume % change
  volume_7d_change_pct?: number | null; // week-over-week volume % change
  volume_30d_change_pct?: number | null; // month-over-month volume % change
  boxes_sold_per_day?: number | null;
  units_sold_count?: number | null;
  boxes_sold_30d_avg?: number | null;
  active_listings_count?: number | null;
  top_10_value_usd?: number | null;
  liquidity_score?: number | null;
  days_to_20pct_increase?: number | null;
  expected_days_to_sell?: number | null;
  boxes_added_today?: number | null;
  // eBay marketplace data (from Phase 1b — 130point.com scraper)
  ebay_sold_today?: number | null;
  ebay_daily_volume_usd?: number | null;
  ebay_median_price_usd?: number | null;
  ebay_active_listings?: number | null;
  ebay_active_low_price?: number | null;
  ebay_volume_30d_usd?: number | null;
  ebay_boxes_added_today?: number | null;
  ebay_boxes_removed_today?: number | null;
  combined_boxes_sold_today?: number | null;
  daily_volume_tcg_usd?: number | null;
  daily_volume_ebay_usd?: number | null;
}

export interface LeaderboardBox {
  id: string;
  rank: number;
  rank_change_direction?: 'up' | 'down' | 'same' | null;
  rank_change_amount?: number | null;
  product_name: string;
  set_name?: string | null;
  game_type?: string | null;
  image_url?: string | null;
  metrics: BoxMetricsSummary;
  reprint_risk: string;
  metric_date?: string | null;
}

export interface ResponseMeta {
  total: number;
  sort: string;
  sort_direction: string;
  date?: string | null;
  limit: number;
  offset: number;
}

export interface LeaderboardResponse {
  data: LeaderboardBox[];
  meta: ResponseMeta;
}

/**
 * Get leaderboard data
 * Uses Next.js API proxy route to avoid CORS issues
 */
export async function getLeaderboard(params: LeaderboardParams = {}): Promise<LeaderboardResponse> {
  const searchParams = new URLSearchParams();
  if (params.sort) searchParams.append('sort', params.sort);
  if (params.limit) searchParams.append('limit', params.limit.toString());
  if (params.offset) searchParams.append('offset', params.offset.toString());
  if (params.date) searchParams.append('date', params.date);

  // Use Next.js API proxy route (avoids CORS issues)
  const url = `/api/booster-boxes?${searchParams.toString()}`;

  // Get auth token for authentication
  const token = getAuthToken();
  
  // Build headers
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  // Add authorization header if token exists
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  console.log('Fetching leaderboard from proxy:', url);
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
    cache: 'no-store',
  });

  console.log('Response status:', response.status, response.statusText);

  if (!response.ok) {
    const errorText = await response.text();
    console.error('API Error Response:', errorText);
    let errorData;
    try {
      errorData = JSON.parse(errorText);
    } catch {
      errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
    }
    
    // Handle 401 Unauthorized - clear token and redirect to login
    if (response.status === 401) {
      // Clear invalid/expired token
      const { removeAuthToken } = await import('@/lib/api/client');
      removeAuthToken();
      
      // Redirect to landing page (where user can login)
      if (typeof window !== 'undefined') {
        window.location.href = '/landing';
      }
      
      throw new Error('Authentication required. Please log in to continue.');
    }
    
    throw new Error(errorData.detail || `Failed to fetch leaderboard: ${response.status} ${response.statusText}`);
  }

  const data = await response.json();
  console.log('Leaderboard data received:', data);
  return data;
}

