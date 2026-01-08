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
import { useState, useEffect } from 'react';
import Image from 'next/image';

export default function DashboardPage() {
  const [sortBy, setSortBy] = useState('unified_volume_usd');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('30d');
  const [isMounted, setIsMounted] = useState(false);
  const { data, isLoading, error } = useLeaderboard({
    sort: sortBy,
    limit: 100, // Maximum allowed by backend
  });

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleSort = (column: string) => {
    const newDirection = sortBy === column && sortDirection === 'desc' ? 'asc' : 'desc';
    setSortDirection(newDirection);
    setSortBy(column);
  };

  const getVolumeSortField = (): string => {
    if (timeRange === '24h') {
      return 'daily_volume_usd';
    } else if (timeRange === '7d') {
      return 'unified_volume_7d_ema';
    } else {
      return 'unified_volume_usd';
    }
  };

  const getSortLabel = (value: string): string => {
    const labels: Record<string, string> = {
      'daily_volume_usd': 'Volume',
      'unified_volume_7d_ema': 'Volume',
      'unified_volume_usd': 'Volume',
      'floor_price_usd': 'Floor Price',
      'liquidity_score': 'Liquidity Score',
      'units_sold_count': 'Sales',
    };
    return labels[value] || 'Volume';
  };

  const handleSortChange = (value: string) => {
    // If Volume is selected, use the appropriate field based on time range
    if (value === 'volume') {
      const volumeField = getVolumeSortField();
      setSortBy(volumeField);
    } else {
      setSortBy(value);
    }
    setSortDirection('desc');
  };

  const handleTimeRangeChange = (range: '24h' | '7d' | '30d') => {
    setTimeRange(range);
    // If currently sorting by volume, update to the correct volume field for the new time range
    const isCurrentlySortingByVolume = 
      sortBy === 'daily_volume_usd' || 
      sortBy === 'unified_volume_7d_ema' || 
      sortBy === 'unified_volume_usd';
    
    if (isCurrentlySortingByVolume) {
      if (range === '24h') {
        setSortBy('daily_volume_usd');
      } else if (range === '7d') {
        setSortBy('unified_volume_7d_ema');
      } else {
        setSortBy('unified_volume_usd');
      }
      setSortDirection('desc');
    }
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
                className={`absolute inset-0 flex items-center ${isMounted ? 'header-fade-in' : ''}`}
                style={{
                  zIndex: 0,
                  opacity: isMounted ? 0.5 : 0,
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
              <div 
                className={`relative ${isMounted ? 'header-fade-in' : ''}`} 
                style={{ 
                  position: 'relative', 
                  zIndex: 10, 
                  isolation: 'isolate',
                  opacity: isMounted ? 1 : 0
                }}
              >
                <h1 className="lb-title font-extrabold tracking-tight text-4xl sm:text-6xl lg:text-7xl mb-2" style={{ color: '#FFFFFF', textShadow: '0 0 20px rgba(255, 255, 255, 0.9), 0 0 40px rgba(255, 255, 255, 0.7), 0 0 60px rgba(255, 255, 255, 0.5), 0 4px 8px rgba(0, 0, 0, 0.8)', position: 'relative', zIndex: 10 }}>Leaderboard</h1>
                <p 
                  className={`text-[color:var(--muted)] tracking-wide text-sm sm:text-base font-bold ${isMounted ? 'header-fade-in-delay' : ''}`} 
                  style={{ 
                    textShadow: '0 2px 4px rgba(0, 0, 0, 0.8)', 
                    position: 'relative', 
                    zIndex: 10,
                    opacity: isMounted ? 1 : 0,
                    fontWeight: 700
                  }}
                >
                  Most Advanced One Piece Booster Box Tracking
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Page Content */}
        <main className="container mx-auto px-0 sm:px-6 pt-6 pb-12" style={{ maxWidth: '1400px' }}>
          {/* New Releases Section */}
          <div style={{ marginTop: '-95px' }}>
            <NewReleases />
          </div>

          {/* Controls Bar */}
          <div className="mb-4 flex items-center justify-between px-3 sm:px-0 gap-1.5 sm:gap-4">
            <div className="flex items-center gap-2 flex-shrink-0">
              {/* Time Range Buttons */}
              <div className="rounded-full bg-white/12 border border-white/15 backdrop-blur-md shadow-[0_10px_30px_rgba(0,0,0,0.18)] flex items-center gap-0 p-1">
                <button 
                  onClick={() => handleTimeRangeChange('24h')}
                  className={`transition lb-anim px-2.5 sm:px-4 py-1.5 text-xs font-medium rounded-full ${
                    timeRange === '24h' 
                      ? 'text-[#1b1b1b] font-semibold bg-[linear-gradient(180deg,var(--gold),var(--gold-2))] shadow-[0_10px_24px_rgba(246,195,90,0.35)] relative overflow-hidden' 
                      : 'text-white/85 hover:bg-white/10'
                  }`}
                >
                  {timeRange === '24h' && (
                    <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
                  )}
                  <span className={timeRange === '24h' ? 'relative z-10' : ''}>24H</span>
                </button>
                <button 
                  onClick={() => handleTimeRangeChange('7d')}
                  className={`transition lb-anim px-2.5 sm:px-4 py-1.5 text-xs font-medium rounded-full ${
                    timeRange === '7d' 
                      ? 'text-[#1b1b1b] font-semibold bg-[linear-gradient(180deg,var(--gold),var(--gold-2))] shadow-[0_10px_24px_rgba(246,195,90,0.35)] relative overflow-hidden' 
                      : 'text-white/85 hover:bg-white/10'
                  }`}
                >
                  {timeRange === '7d' && (
                    <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
                  )}
                  <span className={timeRange === '7d' ? 'relative z-10' : ''}>7D</span>
                </button>
                <button 
                  onClick={() => handleTimeRangeChange('30d')}
                  className={`transition lb-anim px-2.5 sm:px-4 py-1.5 text-xs font-medium rounded-full ${
                    timeRange === '30d' 
                      ? 'text-[#1b1b1b] font-semibold bg-[linear-gradient(180deg,var(--gold),var(--gold-2))] shadow-[0_10px_24px_rgba(246,195,90,0.35)] relative overflow-hidden' 
                      : 'text-white/85 hover:bg-white/10'
                  }`}
                >
                  {timeRange === '30d' && (
                    <span className="pointer-events-none absolute inset-x-1 top-1 h-1/2 rounded-full bg-white/30 blur-[0.2px]" />
                  )}
                  <span className={timeRange === '30d' ? 'relative z-10' : ''}>30D</span>
                </button>
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
