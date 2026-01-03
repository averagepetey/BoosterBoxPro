/**
 * Hook for fetching box detail data
 */

import { useState, useEffect } from 'react';
import { getBoxDetail, getBoxTimeSeries, getBoxRankHistory, BoxDetail, TimeSeriesDataPoint, RankHistoryPoint } from '@/lib/api/boxDetail';

export function useBoxDetail(id: string) {
  const [box, setBox] = useState<BoxDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;
    let abortController: AbortController | null = null;

    async function fetchBox() {
      setIsLoading(true);
      setError(null);

      try {
        console.log('useBoxDetail: Fetching box detail for ID:', id);
        const data = await getBoxDetail(id);
        console.log('useBoxDetail: Box detail received:', data);
        if (!cancelled) {
          setBox(data);
          setIsLoading(false);
        }
      } catch (err) {
        console.error('useBoxDetail: Error fetching box detail:', err);
        if (!cancelled) {
          let errorMessage = 'Failed to load box detail';
          if (err instanceof Error) {
            errorMessage = err.message;
            // Provide more helpful error messages
            if (err.message.includes('timeout')) {
              errorMessage = 'Request timed out. The backend server may not be running or is taking too long to respond.';
            } else if (err.message.includes('not found')) {
              errorMessage = `Box with ID "${id}" was not found in the leaderboard.`;
            } else if (err.message.includes('aborted')) {
              errorMessage = 'Request was cancelled. This may happen if the page is reloaded or navigated away from.';
            }
          }
          setError(new Error(errorMessage));
          setIsLoading(false);
        }
      }
    }

    if (id && id.trim() !== '') {
      fetchBox();
    } else {
      setIsLoading(false);
      setError(new Error('No box ID provided'));
    }

    return () => {
      cancelled = true;
    };
  }, [id]);

  return { box, isLoading, error };
}

export function useBoxTimeSeries(id: string, metric: string = 'floor_price', days: number = 30, onePerMonth: boolean = false) {
  const [data, setData] = useState<TimeSeriesDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchTimeSeries() {
      setIsLoading(true);
      setError(null);

      try {
        const timeSeriesData = await getBoxTimeSeries(id, metric, days, onePerMonth);
        if (!cancelled) {
          setData(timeSeriesData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to load time-series data'));
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    if (id) {
      fetchTimeSeries();
    }

    return () => {
      cancelled = true;
    };
  }, [id, metric, days, onePerMonth]);

  return { data, isLoading, error };
}

export function useBoxRankHistory(id: string, days: number = 30) {
  const [data, setData] = useState<RankHistoryPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function fetchRankHistory() {
      setIsLoading(true);
      setError(null);

      try {
        const rankData = await getBoxRankHistory(id, days);
        if (!cancelled) {
          setData(rankData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error('Failed to load rank history'));
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    if (id) {
      fetchRankHistory();
    }

    return () => {
      cancelled = true;
    };
  }, [id, days]);

  return { data, isLoading, error };
}

