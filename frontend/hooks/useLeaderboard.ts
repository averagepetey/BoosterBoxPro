/**
 * Leaderboard Hook
 * Fetches leaderboard data using React Query
 */

'use client';

import { useQuery } from '@tanstack/react-query';
import { getLeaderboard, LeaderboardParams, LeaderboardResponse } from '@/lib/api/leaderboard';

export function useLeaderboard(params: LeaderboardParams = {}) {
  return useQuery<LeaderboardResponse>({
    queryKey: ['leaderboard', params],
    queryFn: () => getLeaderboard(params),
    staleTime: 60 * 1000, // 1 minute
    refetchOnWindowFocus: false,
  });
}

