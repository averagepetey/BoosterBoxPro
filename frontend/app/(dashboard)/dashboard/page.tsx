/**
 * Dashboard/Leaderboard Page
 * Main page showing featured boxes and leaderboard table
 */

'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navigation } from '@/components/ui/Navigation';
import { LeaderboardTable } from '@/components/leaderboard/LeaderboardTable';
import { useLeaderboard } from '@/hooks/useLeaderboard';
import { useState } from 'react';

export default function DashboardPage() {
  const [sortBy, setSortBy] = useState('unified_volume_7d_ema');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const { data, isLoading, error } = useLeaderboard({
    sort: sortBy,
    limit: 100, // Maximum allowed by backend
  });

  const handleSort = (column: string) => {
    const newDirection = sortBy === column && sortDirection === 'desc' ? 'asc' : 'desc';
    setSortDirection(newDirection);
    setSortBy(column);
  };

  return (
    <ProtectedRoute>
      {/* Hero Section with Clouds - Header Only */}
      <section className="relative overflow-hidden lb-hero">
        <div className="pointer-events-none absolute inset-0">
          <div className="lb-hero-sky absolute inset-0" />
          <div className="lb-hero-stars absolute inset-0" />
        </div>

        <div className="relative z-10">
          <Navigation />
          
          <div className="container mx-auto px-6">
            {/* Header */}
            <div className="mb-4 text-center pt-12">
              <h1 className="lb-title text-white font-extrabold tracking-tight text-5xl mb-2">Leaderboard</h1>
              <p className="text-[color:var(--muted)] tracking-wide text-base">
                Track the top performing TCG booster boxes
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Page Content - Clean Background (No Clouds) */}
      <div className="lb-page relative">
        <main className="container mx-auto px-6 py-12">
          {/* Featured Section - TODO: Build this */}
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-base font-semibold text-white">New Releases</h2>
              <button className="text-xs text-white/85 hover:text-white transition-all hover:translate-x-1">
                See all →
              </button>
            </div>
            <div className="relative rounded-2xl border border-white/15 bg-[rgba(10,24,60,0.35)] backdrop-blur-xl shadow-[0_18px_50px_rgba(0,0,0,0.20)] p-4 text-center min-h-[120px] flex items-center justify-center">
              <p className="text-white/80 text-sm">
                Featured sections coming soon...
              </p>
            </div>
          </div>

          {/* Controls Bar */}
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Time Range Buttons */}
              <div className="rounded-full bg-white/12 border border-white/15 backdrop-blur-md shadow-[0_10px_30px_rgba(0,0,0,0.18)] flex items-center gap-0 p-1">
                <button className="text-white/85 hover:bg-white/10 transition lb-anim px-4 py-1.5 text-xs font-medium rounded-full">
                  24H
                </button>
                <button className="text-white/85 hover:bg-white/10 transition lb-anim px-4 py-1.5 text-xs font-medium rounded-full">
                  7D
                </button>
                <button className="text-[#1b1b1b] font-semibold bg-[linear-gradient(180deg,var(--gold),var(--gold-2))] shadow-[0_10px_24px_rgba(246,195,90,0.35)] relative overflow-hidden px-4 py-1.5 text-xs rounded-full">
                  <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
                  <span className="relative z-10">30D</span>
                </button>
              </div>
            </div>
            
            {/* Top Boxes Title */}
            <h2 className="text-xl font-semibold text-white lb-title">Top Boxes</h2>
            
            {/* Sort Dropdown */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="rounded-full bg-white/12 border border-white/15 backdrop-blur-md text-white/90 shadow-[0_10px_30px_rgba(0,0,0,0.18)] hover:bg-white/16 transition lb-anim px-4 py-2 text-sm focus:outline-none"
            >
              <option value="unified_volume_7d_ema">Volume (7d EMA)</option>
              <option value="floor_price_usd">Floor Price</option>
              <option value="liquidity_score">Liquidity Score</option>
              <option value="units_sold_count">Sales</option>
            </select>
          </div>

          {/* Leaderboard */}
          <div className="mb-4">

            {error && (
              <div className="bg-error/10 border border-error/20 rounded-xl p-4 mb-4 backdrop-blur-sm">
                <p className="text-sm text-error">
                  Failed to load leaderboard: {error instanceof Error ? error.message : 'Unknown error'}
                </p>
                <p className="text-xs text-error/70 mt-2">
                  Make sure the backend API is running at {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}
                </p>
              </div>
            )}
            
            {isLoading && !error && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30 mx-auto mb-2"></div>
                <p className="text-white/60 text-sm">Loading leaderboard...</p>
              </div>
            )}

            {/* Table Container - Scrollable */}
            <div className="relative rounded-3xl lb-glass px-6 py-6 overflow-visible">
              <div className="lb-sheen" />
            {/* Column Headers - Sticky */}
            <div className="sticky top-0 bg-transparent z-20 grid grid-cols-12 gap-4 px-4 mb-4 pb-3 text-white/70 uppercase tracking-widest text-xs border-b border-white/10 backdrop-blur-sm">
              <div className="col-span-1 text-center font-medium">
                #
              </div>
              <div className="col-span-3 text-left font-medium">
                Collection
              </div>
              <div 
                className="col-span-1 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('floor_price_usd')}
              >
                Floor
                {sortBy === 'floor_price_usd' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-1 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('floor_price_1d_change_pct')}
              >
                1d %
                {sortBy === 'floor_price_1d_change_pct' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-2 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('unified_volume_7d_ema')}
              >
                Volume
                {sortBy === 'unified_volume_7d_ema' && (
                  <span className="ml-1 text-[10px] font-bold">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-1 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('units_sold_count')}
              >
                Sales
                {sortBy === 'units_sold_count' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-2 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('listed_percentage')}
              >
                Listed
                {sortBy === 'listed_percentage' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div className="col-span-1 text-center font-medium">
                1d
              </div>
            </div>

            {!isLoading && !error && (
              <LeaderboardTable
                boxes={data?.data || []}
                isLoading={false}
                onSort={handleSort}
                currentSort={sortBy}
              />
            )}
            {/* Debug: Show total count */}
            {data && (
              <div className="mt-4 text-center text-white/60 text-sm">
                Showing {data.data.length} of {data.meta.total} boxes
              </div>
            )}
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
