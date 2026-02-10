/**
 * Market Macro API
 * Functions for fetching market-wide aggregate data
 */

import { getAuthToken } from '@/lib/api/client';

export interface MarketMacroData {
  metric_date: string;
  index_value: number | null;
  index_1d_change_pct: number | null;
  index_7d_change_pct: number | null;
  index_30d_change_pct: number | null;
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL' | null;
  fear_greed_score: number | null;
  floors_up_count: number | null;
  floors_down_count: number | null;
  floors_flat_count: number | null;
  biggest_gainer: {
    box_id: string | null;
    name: string | null;
    pct: number | null;
  };
  biggest_loser: {
    box_id: string | null;
    name: string | null;
    pct: number | null;
  };
  total_daily_volume_usd: number | null;
  total_7d_volume_usd: number | null;
  total_30d_volume_usd: number | null;
  volume_1d_change_pct: number | null;
  volume_7d_change_pct: number | null;
  avg_liquidity_score: number | null;
  total_boxes_sold_today: number | null;
  total_active_listings: number | null;
  total_boxes_added_today: number | null;
  net_supply_change: number | null;
  listings_1d_change: number | null;
  prev_day?: {
    index_value: number | null;
    total_daily_volume_usd: number | null;
    total_active_listings: number | null;
  };
}

export interface MarketIndexPoint {
  date: string;
  index_value: number | null;
  sentiment: string | null;
  fear_greed_score: number | null;
  total_daily_volume_usd: number | null;
}

export async function getMarketMacro(): Promise<MarketMacroData> {
  const token = getAuthToken();
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch('/api/booster-boxes/market-macro', {
    method: 'GET',
    headers,
    cache: 'no-store',
  });

  if (!response.ok) {
    if (response.status === 401) {
      const { removeAuthToken } = await import('@/lib/api/client');
      removeAuthToken();
      if (typeof window !== 'undefined') window.location.href = '/landing';
      throw new Error('Authentication required.');
    }
    throw new Error(`Failed to fetch market macro: ${response.status}`);
  }

  const json = await response.json();
  return json.data;
}

export async function getMarketIndexTimeSeries(days: number = 30): Promise<MarketIndexPoint[]> {
  const token = getAuthToken();
  const headers: HeadersInit = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`/api/booster-boxes/market-index/time-series?days=${days}`, {
    method: 'GET',
    headers,
    cache: 'no-store',
  });

  if (!response.ok) {
    if (response.status === 401) {
      const { removeAuthToken } = await import('@/lib/api/client');
      removeAuthToken();
      if (typeof window !== 'undefined') window.location.href = '/landing';
      throw new Error('Authentication required.');
    }
    throw new Error(`Failed to fetch market index time-series: ${response.status}`);
  }

  const json = await response.json();
  return json.data;
}
