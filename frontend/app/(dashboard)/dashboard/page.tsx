/**
 * Dashboard/Leaderboard Page
 * Main page showing featured boxes and leaderboard table
 */

'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navigation } from '@/components/ui/Navigation';
import { LeaderboardTable } from '@/components/leaderboard/LeaderboardTable';
import { NewReleases } from '@/components/leaderboard/NewReleases';
import { useLeaderboard } from '@/hooks/useLeaderboard';
import { useState } from 'react';

export default function DashboardPage() {
  const [sortBy, setSortBy] = useState('unified_volume_usd');
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
      <div style={{ 
        background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)',
        minHeight: '100vh',
        width: '100%'
      }}>
      {/* Hero Section with Clouds - Header Only */}
      <section 
        className="relative overflow-hidden lb-hero"
        style={{
          minHeight: '200px',
          background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)',
          width: '100%',
          display: 'block',
          position: 'relative'
        }}
      >
        <div className="pointer-events-none absolute inset-0">
          <div 
            className="lb-hero-sky absolute inset-0"
            style={{
              background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)',
              zIndex: 0
            }}
          />
          <img 
            src="/images/headerCloud.png" 
            alt=""
            className="absolute inset-0 w-full h-full object-cover"
            style={{ zIndex: 1, opacity: 1 }}
          />
          <div 
            className="lb-hero-stars absolute inset-0"
            style={{
              backgroundImage: 'radial-gradient(2px 2px at 20% 30%, white, transparent), radial-gradient(2px 2px at 60% 70%, white, transparent), radial-gradient(1px 1px at 50% 50%, white, transparent), radial-gradient(1px 1px at 80% 10%, white, transparent), radial-gradient(2px 2px at 90% 40%, white, transparent), radial-gradient(1px 1px at 33% 60%, white, transparent), radial-gradient(1px 1px at 15% 80%, white, transparent)',
              backgroundRepeat: 'repeat',
              backgroundSize: '200px 200px',
              opacity: 0.6,
              zIndex: 2
            }}
          />
        </div>

        <div className="absolute inset-0 z-10 flex flex-col" style={{ zIndex: 10 }}>
          <Navigation />
          
          <div className="container mx-auto px-6 flex-1 flex flex-col justify-center">
            {/* Header */}
            <div className="text-center" style={{ paddingTop: '3.5rem', paddingBottom: '1rem' }}>
              <h1 className="lb-title font-extrabold tracking-tight text-5xl mb-2" style={{ color: '#FFFFFF', textShadow: '0 0 20px rgba(241, 48, 61, 0.8), 0 0 40px rgba(241, 48, 61, 0.6), 0 0 60px rgba(241, 48, 61, 0.4), 0 4px 8px rgba(0, 0, 0, 0.5)' }}>Leaderboard</h1>
              <p className="text-[color:var(--muted)] tracking-wide text-base">
                Track the top performing TCG booster boxes
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Page Content - Clean Background (No Clouds) */}
      <div 
        className="lb-page relative"
        style={{
          background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)',
          minHeight: '100vh',
          position: 'relative',
          width: '100%'
        }}
      >
        {/* Side decorative clouds - Behind table, at edges, scroll with page */}
        <div 
          style={{ 
            position: 'fixed', 
            top: 0, 
            bottom: 0, 
            left: 0, 
            width: '300px', 
            pointerEvents: 'none', 
            zIndex: 0,
            opacity: 1
          }}
        >
          {/* Multiple clouds positioned randomly vertically on left side */}
          <img src="/sidecloud.png" alt="" style={{ position: 'absolute', top: '60%', left: 0, opacity: 0.3, width: '220px', height: 'auto', pointerEvents: 'none' }} />
          <img src="/sidecloud.png" alt="" style={{ position: 'absolute', top: '85%', left: 0, opacity: 0.18, width: '160px', height: 'auto', pointerEvents: 'none' }} />
        </div>
        <div 
          style={{ 
            position: 'fixed', 
            top: 0, 
            bottom: 0, 
            right: 0, 
            width: '300px', 
            pointerEvents: 'none', 
            zIndex: 0,
            opacity: 1
          }}
        >
          {/* Multiple clouds positioned randomly vertically on right side */}
          <img src="/sidecloud.png" alt="" style={{ position: 'absolute', top: '65%', right: 0, opacity: 0.3, width: '220px', height: 'auto', pointerEvents: 'none', transform: 'scaleX(-1)' }} />
          <img src="/sidecloud.png" alt="" style={{ position: 'absolute', top: '80%', right: 0, opacity: 0.18, width: '160px', height: 'auto', pointerEvents: 'none', transform: 'scaleX(-1)' }} />
        </div>
        <main className="container mx-auto px-6 pt-6 pb-12" style={{ maxWidth: '1400px' }}>
          {/* New Releases Section */}
          <NewReleases />

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
              className="rounded-full text-[#1b1b1b] font-semibold bg-[linear-gradient(180deg,var(--gold),var(--gold-2))] shadow-[0_10px_24px_rgba(246,195,90,0.35)] px-4 py-2 text-sm focus:outline-none relative overflow-hidden"
              style={{ appearance: 'none', WebkitAppearance: 'none' }}
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
            <div 
              className="relative rounded-3xl overflow-hidden"
              style={{
                boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)',
                background: '#141414 !important',
                border: '1px solid rgba(255, 255, 255, 0.15) !important'
              }}
            >
            {/* Horizontal Scroll Wrapper for Mobile */}
            <div className="overflow-x-auto scrollbar-hide">
              <div className="min-w-[950px] sm:min-w-0 px-3 sm:px-6 py-4 sm:py-6">
            {/* Column Headers - Sticky */}
            <div 
              className="sticky top-0 z-20 grid grid-cols-12 gap-2 sm:gap-4 px-2 sm:px-4 mb-4 pb-3 text-white/70 uppercase tracking-widest text-[10px] sm:text-xs rounded-t-3xl"
              style={{
                background: 'transparent',
                backgroundColor: 'transparent',
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                backdropFilter: 'blur(60px) saturate(180%)',
                WebkitBackdropFilter: 'blur(60px) saturate(180%)',
                boxShadow: 'none',
                paddingTop: '0.5rem',
                paddingBottom: '0.75rem',
                borderTopLeftRadius: '1.5rem',
                borderTopRightRadius: '1.5rem'
              }}
            >
              <div className="col-span-1 text-left font-medium">
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
                onClick={() => handleSort('floor_price_30d_change_pct')}
              >
                30d %
                {sortBy === 'floor_price_30d_change_pct' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-2 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('unified_volume_usd')}
              >
                30d Volume
                {sortBy === 'unified_volume_usd' && (
                  <span className="ml-1 text-[10px] font-bold">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-1 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('boxes_sold_30d_avg')}
              >
                Sales
                {sortBy === 'boxes_sold_30d_avg' && (
                  <span className="ml-1 text-[10px]">{sortDirection === 'desc' ? '▼' : '▲'}</span>
                )}
              </div>
              <div 
                className="col-span-2 text-right font-medium cursor-pointer hover:text-white transition-colors"
                onClick={() => handleSort('top_10_value_usd')}
              >
                Top 10 Value
                {sortBy === 'top_10_value_usd' && (
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
            </div>
          </div>
        </main>
      </div>
      </div>
    </ProtectedRoute>
  );
}
