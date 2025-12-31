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
    limit: 50,
  });

  const handleSort = (column: string) => {
    const newDirection = sortBy === column && sortDirection === 'desc' ? 'asc' : 'desc';
    setSortDirection(newDirection);
    setSortBy(column);
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen marketplace-bg">
        <Navigation />
        
        <main className="container mx-auto px-6 py-8 relative z-10">
          {/* Header */}
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-foreground mb-2 tracking-tight">Leaderboard</h1>
            <p className="text-foreground-muted text-sm">
              Track the top performing TCG booster boxes
            </p>
          </div>

          {/* Controls Bar */}
          <div className="mb-6 flex items-center justify-between">
            <div className="flex items-center gap-3">
              {/* Time Range Buttons */}
              <div className="flex items-center gap-2 bg-surface/30 backdrop-blur-sm rounded-full p-1 border border-white/5">
                <button className="px-4 py-1.5 text-xs font-medium text-foreground-secondary rounded-full hover:text-foreground transition-colors">
                  24H
                </button>
                <button className="px-4 py-1.5 text-xs font-medium text-foreground-secondary rounded-full hover:text-foreground transition-colors">
                  7D
                </button>
                <button className="px-4 py-1.5 text-xs font-medium marketplace-accent bg-white/5 rounded-full">
                  30D
                </button>
              </div>
            </div>
            
            {/* Sort Dropdown */}
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-4 py-2 bg-surface/30 backdrop-blur-sm border border-white/5 rounded-full text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-rocket-red/50 transition-all"
            >
              <option value="unified_volume_7d_ema">Volume (7d EMA)</option>
              <option value="floor_price_usd">Floor Price</option>
              <option value="liquidity_score">Liquidity Score</option>
              <option value="units_sold_count">Sales</option>
            </select>
          </div>

          {/* Featured Section - TODO: Build this */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-foreground">New Releases</h2>
              <button className="text-xs marketplace-accent hover:opacity-80 transition-opacity">
                See all →
              </button>
            </div>
            <div className="bg-surface/20 backdrop-blur-sm border border-white/5 rounded-xl p-8 text-center">
              <p className="text-foreground-muted text-sm">
                Featured sections coming soon...
              </p>
            </div>
          </div>

          {/* Leaderboard */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-foreground">Top Boxes</h2>
            </div>

            {error && (
              <div className="bg-error/10 border border-error/20 rounded-xl p-4 mb-4 backdrop-blur-sm">
                <p className="text-sm text-error">
                  Failed to load leaderboard. Please try again.
                </p>
              </div>
            )}

            {/* Column Headers */}
            <div className="grid grid-cols-12 gap-4 px-4 mb-3 pb-2 border-b border-white/5">
              <div className="col-span-1 text-center text-xs font-medium text-foreground-muted uppercase tracking-wider">
                #
              </div>
              <div className="col-span-3 text-left text-xs font-medium text-foreground-muted uppercase tracking-wider">
                Collection
              </div>
              <div 
                className="col-span-1 text-right text-xs font-medium text-foreground-muted uppercase tracking-wider cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('floor_price_usd')}
              >
                Floor
                {sortBy === 'floor_price_usd' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-1 text-right text-xs font-medium text-foreground-muted uppercase tracking-wider cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('floor_price_1d_change_pct')}
              >
                1d %
                {sortBy === 'floor_price_1d_change_pct' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-2 text-right text-xs font-medium text-foreground-muted uppercase tracking-wider cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('unified_volume_7d_ema')}
              >
                Volume
                {sortBy === 'unified_volume_7d_ema' && (
                  <span className="ml-1 text-[10px] font-bold">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-1 text-right text-xs font-medium text-foreground-muted uppercase tracking-wider cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('units_sold_count')}
              >
                Sales
                {sortBy === 'units_sold_count' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-2 text-right text-xs font-medium text-foreground-muted uppercase tracking-wider cursor-pointer hover:text-foreground transition-colors"
                onClick={() => handleSort('listed_percentage')}
              >
                Listed
                {sortBy === 'listed_percentage' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div className="col-span-1 text-center text-xs font-medium text-foreground-muted uppercase tracking-wider">
                1d
              </div>
            </div>

            <LeaderboardTable
              boxes={data?.data || []}
              isLoading={isLoading}
              onSort={handleSort}
              currentSort={sortBy}
            />
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
