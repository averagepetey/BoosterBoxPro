/**
 * Leaderboard Table Component
 * Premium marketplace-style leaderboard with glassmorphism design
 */

'use client';

import { LeaderboardBox } from '../../lib/api/leaderboard';
import { useState } from 'react';

interface LeaderboardTableProps {
  boxes: LeaderboardBox[];
  isLoading?: boolean;
  onSort?: (sortBy: string) => void;
  currentSort?: string;
  timeRange?: '24h' | '7d' | '30d';
}

export function LeaderboardTable({
  boxes,
  isLoading = false,
  onSort,
  currentSort = 'unified_volume_7d_ema',
  timeRange = '30d',
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
    // Always show 1 decimal place to avoid floating-point precision issues
    return numValue.toFixed(1);
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
        // Get price change based on timeRange
        const priceChangeValue = (timeRange === '24h' || timeRange === '7d') 
          ? box.metrics.floor_price_1d_change_pct 
          : box.metrics.floor_price_30d_change_pct;
        const priceChange = priceChangeValue !== null && priceChangeValue !== undefined
          ? (typeof priceChangeValue === 'number' 
              ? priceChangeValue 
              : Number(priceChangeValue))
          : null;
        const isPositive = priceChange !== null && priceChange > 0;
        const isNegative = priceChange !== null && priceChange < 0;

        return (
          <div key={box.id} className="leaderboard-row-wrapper">
            <div
              className={`marketplace-row ${isRankOne ? 'rank-1' : ''} p-2 sm:p-4 cursor-pointer transition-all duration-200`}
              style={{ borderBottom: index < boxes.length - 1 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none' }}
              onClick={() => (window.location.href = `/boxes/${box.id}`)}
            >
              <div className="grid grid-cols-12 gap-1 sm:gap-2 items-center">
              {/* Rank */}
              <div className="col-span-1 text-left px-3" style={{ height: '30px', fontFamily: 'Helvetica' }}>
                <span className="text-xs sm:text-sm text-foreground-muted font-mono" style={{ color: 'rgba(255, 255, 255, 1)' }}>
                  #{box.rank}
                </span>
              </div>

              {/* Collection */}
              <div className="col-span-3 flex items-center gap-3 sm:gap-4 min-h-[48px] sm:min-h-[80px] px-3">
                <div className="flex-shrink-0 w-12 h-12 sm:w-20 sm:h-20 flex items-center justify-center">
                  {box.image_url ? (
                    <img
                      src={box.image_url}
                      alt={box.product_name}
                      className="w-full h-full object-contain rounded-lg"
                      style={{ maxWidth: '100%', maxHeight: '100%' }}
                    />
                  ) : (
                    <div className="w-full h-full bg-surface flex items-center justify-center rounded-lg">
                      <span className="text-xs text-foreground-muted">📦</span>
                    </div>
                  )}
                </div>
                <div 
                  className="flex-1 min-w-0 flex flex-col justify-center"
                  title={cleanProductName(box.product_name)}
                >
                  <div className="text-xs sm:text-base font-semibold text-white" style={{ 
                    color: 'rgba(255, 255, 255, 0.95)',
                    lineHeight: '1.5',
                    marginBottom: '4px'
                  }}>
                    {cleanProductName(box.product_name)}
                  </div>
                  {box.set_name && (
                    <div 
                      className="text-[10px] sm:text-xs text-white/60"
                      style={{ marginTop: '2px' }}
                      title={box.set_name}
                    >
                      {box.set_name}
                    </div>
                  )}
                </div>
                {box.rank_change_direction && (
                  <span
                    className={`text-[10px] sm:text-xs font-mono flex-shrink-0 ${
                      box.rank_change_direction === 'up' ? 'marketplace-positive' : 'marketplace-negative'
                    }`}
                    title={`Rank ${box.rank_change_direction} ${box.rank_change_amount || 0}`}
                  >
                    {getRankChangeIcon(box.rank_change_direction)}
                  </span>
                )}
              </div>

              {/* Floor */}
              <div className="col-span-1 text-right px-2">
                <div className="text-xs sm:text-sm text-foreground financial-number">
                  {formatCurrency(box.metrics.floor_price_usd)}
                </div>
              </div>

              {/* Price Change % - Dynamic based on timeRange */}
              <div className="col-span-1 text-center relative px-2">
                <div 
                  className={`text-xs sm:text-sm financial-number ${getPriceChangeColor(
                    timeRange === '24h' || timeRange === '7d' 
                      ? box.metrics.floor_price_1d_change_pct 
                      : box.metrics.floor_price_30d_change_pct
                  )}`}
                  style={{
                    color: (() => {
                      const change = timeRange === '24h' || timeRange === '7d' 
                        ? box.metrics.floor_price_1d_change_pct 
                        : box.metrics.floor_price_30d_change_pct;
                      if (change === null || change === undefined) return undefined;
                      const numChange = typeof change === 'number' ? change : Number(change);
                      return numChange > 0 ? '#10b981' : numChange < 0 ? '#ef4444' : undefined;
                    })()
                  }}
                >
                  {(() => {
                    const change = timeRange === '24h' || timeRange === '7d' 
                      ? box.metrics.floor_price_1d_change_pct 
                      : box.metrics.floor_price_30d_change_pct;
                    if (change === null || change === undefined) return '--';
                    const numChange = typeof change === 'number' ? change : Number(change);
                    const isPos = numChange > 0;
                    const isNeg = numChange < 0;
                    return `${isPos ? '▲' : isNeg ? '▼' : ''} ${formatPercentage(change)}`;
                  })()}
                </div>
              </div>

              {/* Volume - Dynamic based on timeRange */}
              <div className="col-span-2 text-right px-2">
                <div className="text-xs sm:text-sm font-semibold text-foreground financial-number">
                  {(() => {
                    if (timeRange === '24h') {
                      return box.metrics.daily_volume_usd !== null && box.metrics.daily_volume_usd !== undefined
                        ? formatCurrency(box.metrics.daily_volume_usd)
                        : '--';
                    } else if (timeRange === '7d') {
                      // Prefer volume_7d (actual rolling sum of 7 days)
                      // Fallback to daily_volume_usd * 7 (NOT unified_volume_7d_ema, which is an EMA, not a sum)
                      const volume7d = (box.metrics as any).volume_7d !== null && (box.metrics as any).volume_7d !== undefined
                        ? (box.metrics as any).volume_7d
                        : (box.metrics.daily_volume_usd !== null && box.metrics.daily_volume_usd !== undefined
                          ? box.metrics.daily_volume_usd * 7
                          : null);
                      return volume7d !== null ? formatCurrency(volume7d) : '--';
                    } else { // 30d
                      // Prefer volume_30d (actual rolling sum of 30 days)
                      // Fallback to unified_volume_usd or daily_volume_usd * 30
                      const volume30d = (box.metrics as any).volume_30d !== null && (box.metrics as any).volume_30d !== undefined
                        ? (box.metrics as any).volume_30d
                        : (box.metrics.unified_volume_usd !== null && box.metrics.unified_volume_usd !== undefined
                          ? box.metrics.unified_volume_usd
                          : (box.metrics.daily_volume_usd !== null && box.metrics.daily_volume_usd !== undefined
                            ? box.metrics.daily_volume_usd * 30
                            : null));
                      return volume30d !== null ? formatCurrency(volume30d) : '--';
                    }
                  })()}
                </div>
              </div>

              {/* Sales - Dynamic based on timeRange */}
              <div className="col-span-1 text-right px-3">
                <div className="text-xs sm:text-sm text-foreground financial-number">
                  {(() => {
                    if (timeRange === '24h') {
                      // 24h: Show daily sales rate
                      return box.metrics.boxes_sold_per_day !== null && box.metrics.boxes_sold_per_day !== undefined
                        ? formatNumber(box.metrics.boxes_sold_per_day)
                        : formatNumber(box.metrics.units_sold_count);
                    } else if (timeRange === '7d') {
                      // 7d: Show total sales over 7 days (daily * 7)
                      const sales7d = box.metrics.boxes_sold_per_day !== null && box.metrics.boxes_sold_per_day !== undefined
                        ? box.metrics.boxes_sold_per_day * 7
                        : null;
                      return sales7d !== null ? formatNumber(sales7d) : formatNumber(box.metrics.units_sold_count);
                    } else { // 30d
                      // 30d: Show total sales over 30 days (30d avg * 30, or daily * 30 as fallback)
                      if (box.metrics.boxes_sold_30d_avg !== null && box.metrics.boxes_sold_30d_avg !== undefined) {
                        // boxes_sold_30d_avg is average per day, multiply by 30 for total
                        return formatNumber(box.metrics.boxes_sold_30d_avg * 30);
                      } else if (box.metrics.boxes_sold_per_day !== null && box.metrics.boxes_sold_per_day !== undefined) {
                        // Fallback: use daily rate * 30
                        return formatNumber(box.metrics.boxes_sold_per_day * 30);
                      } else {
                        return formatNumber(box.metrics.units_sold_count);
                      }
                    }
                  })()}
                </div>
              </div>

              {/* Top 10 Card Value */}
              <div className="col-span-2 text-center px-3">
                <div className="text-xs sm:text-sm font-semibold text-foreground financial-number">
                  {box.metrics.top_10_value_usd !== null && box.metrics.top_10_value_usd !== undefined
                    ? formatCurrency(box.metrics.top_10_value_usd)
                    : '--'}
                </div>
              </div>

              {/* Last 1d Sparkline */}
              <div className="col-span-1 flex justify-center px-3">
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
