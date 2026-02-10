/**
 * Market Macro Hooks
 * React Query hooks for market-wide aggregate data
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { getMarketMacro, getMarketIndexTimeSeries, MarketMacroData, MarketIndexPoint } from '@/lib/api/marketMacro';

export function useMarketMacro() {
  return useQuery<MarketMacroData>({
    queryKey: ['marketMacro'],
    queryFn: getMarketMacro,
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
    retry: false,
  });
}

export function useMarketIndexTimeSeries(days: number = 30) {
  return useQuery<MarketIndexPoint[]>({
    queryKey: ['marketIndexTimeSeries', days],
    queryFn: () => getMarketIndexTimeSeries(days),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchOnWindowFocus: false,
    retry: false,
  });
}
