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
import Image from 'next/image';

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
      <div className="lb-page" style={{ 
        minHeight: '100vh',
        width: '100%'
      }}>
        {/* Hero Section */}
        <section 
          className="relative"
          style={{
            minHeight: '200px',
            width: '100%',
            position: 'relative'
          }}
        >
          <Navigation />
          
          <div className="container mx-auto px-6 flex-1 flex flex-col justify-center">
            {/* Header */}
            <div 
              className="text-center relative" 
              style={{ 
                paddingTop: '3.5rem', 
                paddingBottom: '1rem',
                minHeight: '290px',
                overflow: 'hidden'
              }}
            >
              {/* Background Image - Always behind text */}
              <div 
                className="absolute inset-0 flex items-center"
                style={{
                  zIndex: 0,
                  opacity: 0.5,
                  pointerEvents: 'none',
                  justifyContent: 'center',
                  paddingLeft: '10%',
                  transform: 'translate(-90px, 30px)'
                }}
              >
                <Image 
                  src="/images/boot trail.png" 
                  alt=""
                  width={500}
                  height={600}
                  style={{
                    objectFit: 'contain',
                    maxWidth: '70%',
                    height: 'auto',
                    position: 'relative'
                  }}
                  priority
                />
              </div>
              {/* Text Content - Always on top */}
              <div className="relative" style={{ position: 'relative', zIndex: 10, isolation: 'isolate' }}>
                <h1 className="lb-title font-extrabold tracking-tight text-7xl mb-2" style={{ color: '#FFFFFF', textShadow: '0 0 20px rgba(255, 255, 255, 0.9), 0 0 40px rgba(255, 255, 255, 0.7), 0 0 60px rgba(255, 255, 255, 0.5), 0 4px 8px rgba(0, 0, 0, 0.8)', position: 'relative', zIndex: 10 }}>Leaderboard</h1>
                <p className="text-[color:var(--muted)] tracking-wide text-base" style={{ textShadow: '0 2px 4px rgba(0, 0, 0, 0.8)', position: 'relative', zIndex: 10 }}>
                  Most Advanced One Piece Booster Box Tracking
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Page Content */}
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
                boxShadow: '0 0 20px rgba(255, 255, 255, 0.6), 0 0 40px rgba(255, 255, 255, 0.4), 0 0 60px rgba(255, 255, 255, 0.2), 0 30px 80px rgba(0,0,0,0.2)',
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
    </ProtectedRoute>
  );
}

              </div>
            </div>
            
            {/* Top Boxes Title - Center on all screens */}
            <h2 className="text-sm sm:text-xl font-semibold text-white lb-title whitespace-nowrap flex-shrink-0 mx-1 sm:mx-0">Top Boxes</h2>
            
            {/* Sort Dropdown */}
            <div className="rounded-full bg-white/12 border border-white/15 backdrop-blur-md shadow-[0_10px_30px_rgba(0,0,0,0.18)] flex items-center gap-0 p-1 relative flex-shrink-0">
              <div className="relative">
                <select
                  value={sortBy === 'daily_volume_usd' || sortBy === 'unified_volume_7d_ema' || sortBy === 'unified_volume_usd' ? 'volume' : sortBy}
                  onChange={(e) => handleSortChange(e.target.value)}
                  className="text-transparent font-medium bg-red-600/80 hover:bg-red-600/90 transition lb-anim pl-8 sm:pl-16 pr-5 sm:pr-8 py-1.5 text-xs rounded-full border-none focus:outline-none cursor-pointer appearance-none relative overflow-hidden"
                  style={{ WebkitAppearance: 'none', MozAppearance: 'none', color: 'transparent' }}
                >
                  <option value="volume" className="bg-[#2a2a2a] text-white">Volume</option>
                  <option value="floor_price_usd" className="bg-[#2a2a2a] text-white">Floor Price</option>
                  <option value="liquidity_score" className="bg-[#2a2a2a] text-white">Liquidity Score</option>
                  <option value="units_sold_count" className="bg-[#2a2a2a] text-white">Sales</option>
                </select>
                {/* "Sort by:" Text Overlay - Hidden on mobile, shown on desktop */}
                <span className="hidden sm:block pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-white text-xs font-semibold z-10">
                  Sort by:
                </span>
                {/* Current Selection Display - Adjusted for mobile */}
                <span className="pointer-events-none absolute left-2 sm:left-20 top-1/2 -translate-y-1/2 text-white text-[10px] sm:text-xs font-semibold z-10">
                  {getSortLabel(sortBy)}
                </span>
                {/* Shiny Gradient Overlay */}
                <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
              </div>
              {/* Dropdown Triangle Indicator */}
              <div className="absolute right-2 sm:right-3 pointer-events-none z-20">
                <svg className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Leaderboard */}
          <div className="mb-4">

            {isLoading && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30 mx-auto mb-2"></div>
                <p className="text-white/60 text-sm">Loading leaderboard...</p>
              </div>
            )}

            {/* Table Container - Scrollable */}
            {(!isLoading || data) && (
            <div 
              className="relative rounded-none sm:rounded-3xl overflow-hidden leaderboard-container"
              style={{
                background: '#141414 !important',
                border: '1px solid rgba(255, 255, 255, 0.15) !important'
              }}
            >
            {/* Horizontal Scroll Wrapper for Mobile */}
            <div className="overflow-x-auto scrollbar-hide">
              <div className="min-w-[950px] sm:min-w-0 px-2 sm:px-6 py-2 sm:py-6">
            {/* Column Headers - Sticky */}
            <div 
              className="sticky top-0 z-20 grid grid-cols-12 gap-1 sm:gap-4 px-1 sm:px-4 mb-2 sm:mb-4 pb-2 sm:pb-3 text-white/70 uppercase tracking-widest text-[9px] sm:text-xs rounded-t-3xl"
              style={{
                background: 'transparent',
                backgroundColor: 'transparent',
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                backdropFilter: 'blur(60px) saturate(180%)',
                WebkitBackdropFilter: 'blur(60px) saturate(180%)',
                boxShadow: 'none',
                paddingTop: '0.25rem',
                paddingBottom: '0.5rem',
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

            {data && data.data && data.data.length > 0 && (
              <LeaderboardTable
                boxes={data.data}
                isLoading={isLoading}
                onSort={handleSort}
                currentSort={sortBy}
              />
            )}
            {/* Debug: Show total count */}
            {data && data.data && data.data.length > 0 && (
              <div className="mt-4 text-center text-white/60 text-sm">
                {error && (
                  <p className="text-yellow-400/80 text-xs mb-2">
                    ⚠️ Using sample data (backend server is not running)
                  </p>
                )}
                Showing {data.data.length} of {data.meta?.total || data.data.length} boxes
              </div>
            )}
              </div>
            </div>
            </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}

              </div>
            </div>
            
            {/* Top Boxes Title - Center on all screens */}
            <h2 className="text-sm sm:text-xl font-semibold text-white lb-title whitespace-nowrap flex-shrink-0 mx-1 sm:mx-0">Top Boxes</h2>
            
            {/* Sort Dropdown */}
            <div className="rounded-full bg-white/12 border border-white/15 backdrop-blur-md shadow-[0_10px_30px_rgba(0,0,0,0.18)] flex items-center gap-0 p-1 relative flex-shrink-0">
              <div className="relative">
                <select
                  value={sortBy === 'daily_volume_usd' || sortBy === 'unified_volume_7d_ema' || sortBy === 'unified_volume_usd' ? 'volume' : sortBy}
                  onChange={(e) => handleSortChange(e.target.value)}
                  className="text-transparent font-medium bg-red-600/80 hover:bg-red-600/90 transition lb-anim pl-8 sm:pl-16 pr-5 sm:pr-8 py-1.5 text-xs rounded-full border-none focus:outline-none cursor-pointer appearance-none relative overflow-hidden"
                  style={{ WebkitAppearance: 'none', MozAppearance: 'none', color: 'transparent' }}
                >
                  <option value="volume" className="bg-[#2a2a2a] text-white">Volume</option>
                  <option value="floor_price_usd" className="bg-[#2a2a2a] text-white">Floor Price</option>
                  <option value="liquidity_score" className="bg-[#2a2a2a] text-white">Liquidity Score</option>
                  <option value="units_sold_count" className="bg-[#2a2a2a] text-white">Sales</option>
                </select>
                {/* "Sort by:" Text Overlay - Hidden on mobile, shown on desktop */}
                <span className="hidden sm:block pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-white text-xs font-semibold z-10">
                  Sort by:
                </span>
                {/* Current Selection Display - Adjusted for mobile */}
                <span className="pointer-events-none absolute left-2 sm:left-20 top-1/2 -translate-y-1/2 text-white text-[10px] sm:text-xs font-semibold z-10">
                  {getSortLabel(sortBy)}
                </span>
                {/* Shiny Gradient Overlay */}
                <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
              </div>
              {/* Dropdown Triangle Indicator */}
              <div className="absolute right-2 sm:right-3 pointer-events-none z-20">
                <svg className="w-2.5 h-2.5 sm:w-3 sm:h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </div>
          </div>

          {/* Leaderboard */}
          <div className="mb-4">

            {isLoading && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30 mx-auto mb-2"></div>
                <p className="text-white/60 text-sm">Loading leaderboard...</p>
              </div>
            )}

            {/* Table Container - Scrollable */}
            {(!isLoading || data) && (
            <div 
              className="relative rounded-none sm:rounded-3xl overflow-hidden leaderboard-container"
              style={{
                background: '#141414 !important',
                border: '1px solid rgba(255, 255, 255, 0.15) !important'
              }}
            >
            {/* Horizontal Scroll Wrapper for Mobile */}
            <div className="overflow-x-auto scrollbar-hide">
              <div className="min-w-[950px] sm:min-w-0 px-2 sm:px-6 py-2 sm:py-6">
            {/* Column Headers - Sticky */}
            <div 
              className="sticky top-0 z-20 grid grid-cols-12 gap-1 sm:gap-4 px-1 sm:px-4 mb-2 sm:mb-4 pb-2 sm:pb-3 text-white/70 uppercase tracking-widest text-[9px] sm:text-xs rounded-t-3xl"
              style={{
                background: 'transparent',
                backgroundColor: 'transparent',
                borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
                backdropFilter: 'blur(60px) saturate(180%)',
                WebkitBackdropFilter: 'blur(60px) saturate(180%)',
                boxShadow: 'none',
                paddingTop: '0.25rem',
                paddingBottom: '0.5rem',
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

            {data && data.data && data.data.length > 0 && (
              <LeaderboardTable
                boxes={data.data}
                isLoading={isLoading}
                onSort={handleSort}
                currentSort={sortBy}
              />
            )}
            {/* Debug: Show total count */}
            {data && data.data && data.data.length > 0 && (
              <div className="mt-4 text-center text-white/60 text-sm">
                {error && (
                  <p className="text-yellow-400/80 text-xs mb-2">
                    ⚠️ Using sample data (backend server is not running)
                  </p>
                )}
                Showing {data.data.length} of {data.meta?.total || data.data.length} boxes
              </div>
            )}
              </div>
            </div>
            </div>
            )}
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
