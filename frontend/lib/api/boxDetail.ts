/**
 * Box Detail API
 * Functions for fetching individual box detail data
 */

import { getApiBaseUrl, getAuthToken } from '@/lib/api/client';
// Note: getApiBaseUrl used for time-series and rank history endpoints
import { BoxMetricsSummary } from './leaderboard';

export interface BoxDetail {
  id: string;
  product_name: string;
  set_name?: string | null;
  game_type?: string | null;
  image_url?: string | null;
  release_date?: string | null;
  external_product_id?: string | null;
  estimated_total_supply?: number | null;
  reprint_risk?: string | null;
  current_rank_by_volume?: number | null;
  current_rank_by_market_cap?: number | null;
  rank_change_direction?: 'up' | 'down' | 'same' | null;
  rank_change_amount?: number | null;
  is_favorited?: boolean;
  notes?: string[] | null;
  metrics: BoxMetricsSummary & {
    volume_30d?: number | null; // rolling 30d total from daily data (or ramp in first month)
    volume_1d_change_pct?: number | null;
    volume_7d_change_pct?: number | null;
    volume_30d_change_pct?: number | null;
    boxes_sold_per_day?: number | null;
    boxes_sold_30d_avg?: number | null;
    boxes_added_today?: number | null;
    boxes_added_7d_ema?: number | null;
    boxes_added_30d_ema?: number | null;
    volume_30d_sma?: number | null;
    momentum_score?: number | null;
    community_sentiment?: number | null;
    expected_time_to_sale_days?: number | null;
    top_10_value_usd?: number | null;
  };
}

export interface TimeSeriesDataPoint {
  date: string;
  floor_price_usd?: number | null;
  floor_price_1d_change_pct?: number | null;
  unified_volume_usd?: number | null;
  unified_volume_7d_ema?: number | null;
  active_listings_count?: number | null;
  units_sold_count?: number | null;
  visible_market_cap_usd?: number | null;
  listed_percentage?: number | null;
  days_to_20pct_increase?: number | null;
  momentum_score?: number | null;
  boxes_added_today?: number | null;
  boxes_sold_per_day?: number | null;
}

export interface RankHistoryPoint {
  date: string;
  rank: number;
}

/**
 * Fetch box detail by ID
 * Uses Next.js API proxy to avoid CORS issues and handle slow backend
 */
export async function getBoxDetail(id: string): Promise<BoxDetail> {
  // Use Next.js API proxy (avoids CORS, handles timeouts better)
  const url = `/api/booster-boxes/${id}`;
  const token = getAuthToken();
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  console.log(`Fetching box detail for ID: ${id} via proxy: ${url}`);
  
  try {
    const response = await fetch(url, {
      method: 'GET',
      headers,
      cache: 'no-store',
    });
    
    console.log('Box detail response status:', response.status);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: response.statusText }));
      console.error('Box detail error:', errorData);
      
      if (response.status === 404) {
        throw new Error(`Box with ID "${id}" was not found`);
      }
      if (response.status === 504) {
        throw new Error('Request timed out. The backend server may not be running or is taking too long to respond.');
      }
      throw new Error(errorData.detail || errorData.error || `Failed to fetch box detail: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Box detail received:', data.data?.product_name);
    
    // Backend returns { data: {...} } format
    if (data.data) {
      return data.data;
    }
    return data;
  } catch (error) {
    console.error('Box detail fetch error:', error);
    throw error;
  }
}

/**
 * Fetch time-series data for a box
 */
export async function getBoxTimeSeries(
  id: string,
  metric: string = 'floor_price',
  days: number = 30,
  onePerMonth: boolean = false
): Promise<TimeSeriesDataPoint[]> {
  const baseUrl = getApiBaseUrl();
  const token = getAuthToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const params = new URLSearchParams({
    metric,
    days: days.toString(),
  });
  if (onePerMonth) {
    params.append('one_per_month', 'true');
  }
  
  const response = await fetch(
    `${baseUrl}/booster-boxes/${id}/time-series?${params.toString()}`,
    {
      method: 'GET',
      headers,
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to fetch time-series data: ${response.statusText}`);
  }
  
  const data = await response.json();
  return data.data || data;
}

/**
 * Fetch rank history for a box
 */
export async function getBoxRankHistory(
  id: string,
  days: number = 30
): Promise<RankHistoryPoint[]> {
  const baseUrl = getApiBaseUrl();
  const token = getAuthToken();
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const url = `${baseUrl}/booster-boxes/${id}/rank-history?days=${days}`;
  console.log('getBoxRankHistory: Fetching from:', url);
  
  const response = await fetch(url, {
    method: 'GET',
    headers,
  });
  
  if (!response.ok) {
    const errorText = await response.text();
    console.error('getBoxRankHistory: Error response:', response.status, errorText);
    throw new Error(`Failed to fetch rank history: ${response.statusText}`);
  }
  
  const data = await response.json();
  console.log('getBoxRankHistory: Response data:', data);
  return data.data || data;
}

/**
 * Toggle favorite status for a box
 */
export async function toggleBoxFavorite(id: string, isFavorited: boolean): Promise<boolean> {
  const baseUrl = getApiBaseUrl();
  const token = getAuthToken();
  
  if (!token) {
    throw new Error('Authentication required to favorite boxes');
  }
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`,
  };
  
  const method = isFavorited ? 'POST' : 'DELETE';
  const response = await fetch(
    `${baseUrl}/api/v1/booster-boxes/${id}/favorite`,
    {
      method,
      headers,
    }
  );
  
  if (!response.ok) {
    throw new Error(`Failed to ${isFavorited ? 'add' : 'remove'} favorite: ${response.statusText}`);
  }
  
  return !isFavorited;
}

