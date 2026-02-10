/**
 * Leaderboard Table Component
 * Premium marketplace-style leaderboard with glassmorphism design
 */

'use client';

import { LeaderboardBox } from '../../lib/api/leaderboard';
import { getBoxImageUrl } from '../../lib/utils/boxImages';
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
              className={`marketplace-row ${isRankOne ? 'rank-1' : ''} p-3 max-[430px]:p-2 xl:p-6 cursor-pointer transition-all duration-200`}
              style={{ borderBottom: index < boxes.length - 1 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none' }}
              onClick={() => (window.location.href = `/boxes/${box.id}`)}
            >
              <div className="grid grid-cols-12 gap-2 max-[430px]:gap-1 xl:gap-4 items-center">
              {/* Rank - congruent size with other data cells */}
              <div className="col-span-1 text-left px-3 min-h-[44px] max-[430px]:min-h-[36px] xl:min-h-0 flex items-center" style={{ fontFamily: 'Helvetica' }}>
                <span className="text-sm max-[430px]:text-xs xl:text-lg font-bold font-mono text-foreground-muted" style={{ color: 'rgba(255, 255, 255, 1)' }}>
                  #{box.rank}
                </span>
              </div>

              {/* Collection - smaller rows and text on mobile */}
              <div className="col-span-3 flex items-center gap-3 max-[430px]:gap-2 xl:gap-5 min-h-[64px] max-[430px]:min-h-[48px] xl:min-h-[96px] px-3 py-1 max-[430px]:py-0.5">
                <div className="flex-shrink-0 w-16 h-16 max-[430px]:w-12 max-[430px]:h-12 xl:w-24 xl:h-24 flex items-center justify-center">
                  {(() => {
                    const imageUrl = box.image_url || getBoxImageUrl(box.product_name);
                    return imageUrl ? (
                      <img
                        src={imageUrl}
                        alt={box.product_name}
                        className="w-full h-full object-contain rounded-lg"
                        style={{ maxWidth: '100%', maxHeight: '100%' }}
                      />
                    ) : (
                      <div className="w-full h-full bg-surface flex items-center justify-center rounded-lg">
                        <span className="text-sm text-foreground-muted">📦</span>
                      </div>
                    );
                  })()}
                </div>
                <div 
                  className="flex-1 min-w-0 flex flex-col justify-center"
                  title={cleanProductName(box.product_name)}
                >
                  <div className="text-sm max-[430px]:text-xs xl:text-lg font-bold text-white" style={{ 
                    color: 'rgba(255, 255, 255, 0.95)',
                    lineHeight: '1.5',
                    marginBottom: '4px'
                  }}>
                    {cleanProductName(box.product_name)}
                  </div>
                  {box.set_name && (
                    <div 
                      className="text-xs max-[430px]:text-[10px] text-white/60"
                      style={{ marginTop: '2px' }}
                      title={box.set_name}
                    >
                      {box.set_name}
                    </div>
                  )}
                </div>
                {box.rank_change_direction && (
                  <span
                    className={`text-xs max-[430px]:text-[10px] font-mono flex-shrink-0 ${
                      box.rank_change_direction === 'up' ? 'marketplace-positive' : 'marketplace-negative'
                    }`}
                    title={`Rank ${box.rank_change_direction} ${box.rank_change_amount || 0}`}
                  >
                    {getRankChangeIcon(box.rank_change_direction)}
                  </span>
                )}
              </div>

              {/* Floor */}
              <div className="col-span-1 text-right px-2 min-h-[44px] max-[430px]:min-h-[36px] xl:min-h-0 flex items-center justify-end">
                <div className="text-sm max-[430px]:text-xs xl:text-lg font-bold text-foreground financial-number">
                  {formatCurrency(box.metrics.floor_price_usd)}
                </div>
              </div>

              {/* Price Change % - Dynamic based on timeRange */}
              <div className="col-span-1 text-center relative pl-[33px] pr-0 min-h-[44px] max-[430px]:min-h-[36px] xl:min-h-0 flex items-center justify-center">
                <div 
                  className={`text-sm max-[430px]:text-xs xl:text-lg font-bold financial-number ${getPriceChangeColor(
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
              <div className="col-span-2 text-right pl-0 pr-2 -ml-1 min-h-[44px] max-[430px]:min-h-[36px] xl:min-h-0 flex flex-col items-end justify-center">
                <div className="text-sm max-[430px]:text-xs xl:text-lg font-bold text-foreground financial-number">
                  {(() => {
                    if (timeRange === '24h') {
                      return box.metrics.daily_volume_usd !== null && box.metrics.daily_volume_usd !== undefined
                        ? formatCurrency(box.metrics.daily_volume_usd)
                        : '--';
                    } else if (timeRange === '7d') {
                      const volume7d = (box.metrics as any).volume_7d !== null && (box.metrics as any).volume_7d !== undefined
                        ? (box.metrics as any).volume_7d
                        : (box.metrics.daily_volume_usd !== null && box.metrics.daily_volume_usd !== undefined
                          ? box.metrics.daily_volume_usd * 7
                          : null);
                      return volume7d !== null ? formatCurrency(volume7d) : '--';
                    } else {
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
                {(() => {
                  // Only show DoD (vs yesterday) for now; WoW and MoM tracked in backend, will show once we have a week of daily refreshes
                  if (timeRange !== '24h') return null;
                  const volChange = (box.metrics as any).volume_1d_change_pct;
                  if (volChange == null || volChange === undefined) return null;
                  const n = typeof volChange === 'number' ? volChange : Number(volChange);
                  if (isNaN(n)) return null;
                  return (
                    <div className={`text-xs mt-0.5 ${n >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {n >= 0 ? '▲' : '▼'} {Math.abs(n).toFixed(1)}% vs yesterday
                    </div>
                  );
                })()}
              </div>

              {/* Sales - Dynamic based on timeRange */}
              <div className="col-span-1 text-right px-3 min-h-[44px] max-[430px]:min-h-[36px] xl:min-h-0 flex items-center justify-end">
                <div className="text-sm max-[430px]:text-xs xl:text-lg font-bold text-foreground financial-number">
                  {(() => {
                    if (timeRange === '24h') {
                      // 24h: Show daily sales rate
                      return box.metrics.boxes_sold_today !== null && box.metrics.boxes_sold_today !== undefined
                        ? formatNumber(box.metrics.boxes_sold_today)
                        : formatNumber(box.metrics.units_sold_count);
                    } else if (timeRange === '7d') {
                      // 7d: Show total sales over 7 days (daily * 7)
                      const sales7d = box.metrics.boxes_sold_today !== null && box.metrics.boxes_sold_today !== undefined
                        ? box.metrics.boxes_sold_today * 7
                        : null;
                      return sales7d !== null ? formatNumber(sales7d) : formatNumber(box.metrics.units_sold_count);
                    } else { // 30d
                      // 30d: Show total sales over 30 days (30d avg * 30, or daily * 30 as fallback)
                      if (box.metrics.boxes_sold_30d_avg !== null && box.metrics.boxes_sold_30d_avg !== undefined) {
                        // boxes_sold_30d_avg is average per day, multiply by 30 for total
                        return formatNumber(box.metrics.boxes_sold_30d_avg * 30);
                      } else if (box.metrics.boxes_sold_today !== null && box.metrics.boxes_sold_today !== undefined) {
                        // Fallback: use daily rate * 30
                        return formatNumber(box.metrics.boxes_sold_today * 30);
                      } else {
                        return formatNumber(box.metrics.units_sold_count);
                      }
                    }
                  })()}
                </div>
              </div>

              {/* Top 10 Card Value */}
              <div className="col-span-2 text-center px-3 min-h-[44px] max-[430px]:min-h-[36px] xl:min-h-0 flex items-center justify-center">
                <div className="text-sm max-[430px]:text-xs xl:text-lg font-bold text-foreground financial-number">
                  {box.metrics.top_10_value_usd !== null && box.metrics.top_10_value_usd !== undefined
                    ? formatCurrency(box.metrics.top_10_value_usd)
                    : '--'}
                </div>
              </div>

              {/* Days to 20% - same data as box detail */}
              <div className="col-span-1 text-center px-2 min-h-[44px] max-[430px]:min-h-[36px] xl:min-h-0 flex items-center justify-center">
                <div className={`text-sm max-[430px]:text-xs xl:text-lg financial-number ${
                  box.metrics.days_to_20pct_increase != null && box.metrics.days_to_20pct_increase !== undefined
                    ? 'text-foreground'
                    : 'text-white/30'
                }`}>
                  {box.metrics.days_to_20pct_increase != null && box.metrics.days_to_20pct_increase !== undefined
                    ? Math.round(box.metrics.days_to_20pct_increase)
                    : 'No squeeze'}
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

