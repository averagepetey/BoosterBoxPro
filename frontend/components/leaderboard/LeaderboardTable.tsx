/**
 * Leaderboard Table Component
 * Premium marketplace-style leaderboard with glassmorphism design
 */

'use client';

import { LeaderboardBox } from '@/lib/api/leaderboard';
import { useState } from 'react';

interface LeaderboardTableProps {
  boxes: LeaderboardBox[];
  isLoading?: boolean;
  onSort?: (sortBy: string) => void;
  currentSort?: string;
}

export function LeaderboardTable({
  boxes,
  isLoading = false,
  onSort,
  currentSort = 'unified_volume_7d_ema',
}: LeaderboardTableProps) {
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  const handleSort = (column: string) => {
    if (onSort) {
      const newDirection = currentSort === column && sortDirection === 'desc' ? 'asc' : 'desc';
      setSortDirection(newDirection);
      onSort(column);
    }
  };

  const formatCurrency = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '--';
    const numValue = typeof value === 'number' ? value : Number(value);
    if (isNaN(numValue)) return '--';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(numValue);
  };

  const formatPercentage = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '--';
    const numValue = typeof value === 'number' ? value : Number(value);
    if (isNaN(numValue)) return '--';
    const sign = numValue >= 0 ? '+' : '';
    return `${sign}${numValue.toFixed(2)}%`;
  };

  const formatNumber = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '--';
    const numValue = typeof value === 'number' ? value : Number(value);
    if (isNaN(numValue)) return '--';
    if (numValue >= 1000) {
      return `${(numValue / 1000).toFixed(1)}K`;
    }
    return numValue.toString();
  };

  const getRankChangeIcon = (direction: string | null): string => {
    if (direction === 'up') return '▲';
    if (direction === 'down') return '▼';
    return '';
  };

  const getPriceChangeColor = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return 'text-foreground-muted';
    const numValue = typeof value === 'number' ? value : Number(value);
    if (isNaN(numValue)) return 'text-foreground-muted';
    if (numValue > 0) return 'marketplace-positive';
    if (numValue < 0) return 'marketplace-negative';
    return 'text-foreground-muted';
  };

  const cleanProductName = (name: string): string => {
    return name.replace(/^One Piece\s*-\s*/i, '').trim();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-rocket-red mx-auto mb-4"></div>
          <p className="text-foreground-secondary">Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  if (boxes.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-foreground-secondary">No data available</p>
      </div>
    );
  }

  return (
    <div className="space-y-0">
      {boxes.map((box, index) => {
        const isRankOne = box.rank === 1;
        const priceChange = box.metrics.floor_price_1d_change_pct !== null && box.metrics.floor_price_1d_change_pct !== undefined
          ? (typeof box.metrics.floor_price_1d_change_pct === 'number' 
              ? box.metrics.floor_price_1d_change_pct 
              : Number(box.metrics.floor_price_1d_change_pct))
          : null;
        const isPositive = priceChange !== null && priceChange > 0;
        const isNegative = priceChange !== null && priceChange < 0;

        return (
          <div key={box.id} className="leaderboard-row-wrapper">
            <div
              className={`marketplace-row ${isRankOne ? 'rank-1' : ''} p-4 cursor-pointer transition-all duration-200`}
              onClick={() => (window.location.href = `/boxes/${box.id}`)}
            >
              <div className="grid grid-cols-12 gap-2 sm:gap-4 items-center px-2 sm:px-0">
              {/* Rank */}
              <div className="col-span-1 text-center" style={{ height: '30px', fontFamily: 'Helvetica' }}>
                <span className="text-sm text-foreground-muted font-mono" style={{ color: 'rgba(255, 255, 255, 1)' }}>
                  #{box.rank}
                </span>
              </div>

              {/* Collection */}
              <div className="col-span-3 flex items-center justify-center gap-2 sm:gap-4 min-w-[200px]">
                {box.image_url ? (
                  <img
                    src={box.image_url}
                    alt={box.product_name}
                    className="w-14 h-14 sm:w-20 sm:h-20 object-contain rounded-lg flex-shrink-0"
                  />
                ) : (
                  <div className="w-14 h-14 sm:w-20 sm:h-20 bg-surface flex items-center justify-center rounded-lg flex-shrink-0">
                    <span className="text-xs text-foreground-muted">📦</span>
                  </div>
                )}
                <div 
                  className="flex-1 min-w-[140px] sm:min-w-0"
                  title={cleanProductName(box.product_name)}
                >
                  <div className="text-xs sm:text-sm md:text-base font-semibold text-foreground text-left sm:text-center break-words" style={{ 
                    display: '-webkit-box',
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    lineHeight: '1.3'
                  }}>
                    {cleanProductName(box.product_name)}
                  </div>
                  {box.set_name && (
                    <div 
                      className="text-[10px] sm:text-xs text-foreground-muted text-left sm:text-center break-words mt-0.5"
                      style={{ 
                        display: '-webkit-box',
                        WebkitLineClamp: 1,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden'
                      }}
                      title={box.set_name}
                    >
                      {box.set_name}
                    </div>
                  )}
                </div>
                {box.rank_change_direction && (
                  <span
                    className={`text-xs font-mono ${
                      box.rank_change_direction === 'up' ? 'marketplace-positive' : 'marketplace-negative'
                    }`}
                    title={`Rank ${box.rank_change_direction} ${box.rank_change_amount || 0}`}
                  >
                    {getRankChangeIcon(box.rank_change_direction)}
                  </span>
                )}
              </div>

              {/* Floor */}
              <div className="col-span-1 text-center">
                <div className="text-sm text-foreground financial-number">
                  {formatCurrency(box.metrics.floor_price_usd)}
                </div>
              </div>

              {/* Floor 1d % */}
              <div className="col-span-1 text-center relative">
                <div 
                  className={`text-sm financial-number ${getPriceChangeColor(box.metrics.floor_price_1d_change_pct)}`}
                  style={{
                    color: priceChange !== null 
                      ? (priceChange > 0 ? '#10b981' : priceChange < 0 ? '#ef4444' : undefined)
                      : undefined
                  }}
                >
                  {priceChange !== null
                    ? `${isPositive ? '▲' : isNegative ? '▼' : ''} ${formatPercentage(box.metrics.floor_price_1d_change_pct)}`
                    : '--'}
                </div>
              </div>

              {/* Volume */}
              <div className="col-span-2 text-center">
                <div className="text-sm font-semibold text-foreground financial-number">
                  {formatCurrency(box.metrics.unified_volume_7d_ema)}
                </div>
              </div>

              {/* Sales */}
              <div className="col-span-1 text-center">
                <div className="text-sm text-foreground financial-number">
                  {formatNumber(box.metrics.units_sold_count)}
                </div>
              </div>

              {/* Top 10 Card Value */}
              <div className="col-span-2 text-center">
                <div className="text-sm font-semibold text-foreground financial-number">
                  {box.metrics.top_10_value_usd !== null && box.metrics.top_10_value_usd !== undefined
                    ? formatCurrency(box.metrics.top_10_value_usd)
                    : '--'}
                </div>
              </div>

              {/* Last 1d Sparkline */}
              <div className="col-span-1 flex justify-center">
                <div className={`marketplace-sparkline ${isPositive ? 'marketplace-sparkline-positive' : isNegative ? 'marketplace-sparkline-negative' : ''}`}>
                  <svg width="100" height="32" viewBox="0 0 100 32" className="w-full h-full">
                    {/* Placeholder sparkline - will be replaced with actual chart data */}
                    <polyline
                      points="0,24 20,20 40,16 60,12 80,8 100,4"
                      fill="none"
                      stroke={isPositive ? '#10b981' : isNegative ? '#ef4444' : '#64748b'}
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </div>
              </div>
            </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
