'use client';

import { useMemo } from 'react';
import { LeaderboardBox } from '@/lib/api/leaderboard';
import { FearGreedGauge } from './FearGreedGauge';

interface MarketOverviewBarProps {
  boxes: LeaderboardBox[];
}

function formatUsd(value: number): string {
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

function clamp(val: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, val));
}

function computeFearGreedIndex(boxes: LeaderboardBox[]): number {
  if (!boxes.length) return 50;

  // 1. Price Momentum (25%): avg floor_price_1d_change_pct, mapped -5% to +5% -> 0-100
  const priceChanges = boxes
    .map(b => b.metrics.floor_price_1d_change_pct)
    .filter((v): v is number => v !== null && v !== undefined);
  const avgPriceChange = priceChanges.length
    ? priceChanges.reduce((a, b) => a + b, 0) / priceChanges.length
    : 0;
  const priceMomentum = clamp((avgPriceChange + 5) / 10, 0, 1) * 100;

  // 2. Volume Momentum (25%): daily_volume_usd sum vs 7d avg, mapped -50% to +50% -> 0-100
  const dailyVolSum = boxes.reduce((sum, b) => sum + (b.metrics.daily_volume_usd || 0), 0);
  const vol7dSum = boxes.reduce((sum, b) => sum + (b.metrics.volume_7d || 0), 0);
  const avgDailyFrom7d = vol7dSum / 7;
  const volChangePct = avgDailyFrom7d > 0 ? ((dailyVolSum - avgDailyFrom7d) / avgDailyFrom7d) * 100 : 0;
  const volumeMomentum = clamp((volChangePct + 50) / 100, 0, 1) * 100;

  // 3. Listing Trend (25%): inverted - more listings = fear, fewer = greed
  // Use boxes_added_today: negative (removals) = greed, positive (additions) = fear
  const addedValues = boxes
    .map(b => b.metrics.boxes_added_today)
    .filter((v): v is number => v !== null && v !== undefined);
  const avgAdded = addedValues.length
    ? addedValues.reduce((a, b) => a + b, 0) / addedValues.length
    : 0;
  // Map: -5 (net removals) -> 100 (greed), +5 (net additions) -> 0 (fear)
  const listingTrend = clamp((-avgAdded + 5) / 10, 0, 1) * 100;

  // 4. Sales Velocity (25%): avg boxes_sold_per_day, mapped 0-3 -> 0-100
  const salesValues = boxes
    .map(b => b.metrics.boxes_sold_per_day)
    .filter((v): v is number => v !== null && v !== undefined);
  const avgSales = salesValues.length
    ? salesValues.reduce((a, b) => a + b, 0) / salesValues.length
    : 0;
  const salesVelocity = clamp(avgSales / 3, 0, 1) * 100;

  const index = (priceMomentum * 0.25) + (volumeMomentum * 0.25) + (listingTrend * 0.25) + (salesVelocity * 0.25);
  return Math.round(clamp(index, 0, 100));
}

export function MarketOverviewBar({ boxes }: MarketOverviewBarProps) {
  const stats = useMemo(() => {
    if (!boxes.length) return null;

    // Total Market Volume Today
    const totalVolToday = boxes.reduce((sum, b) => sum + (b.metrics.daily_volume_usd || 0), 0);

    // Yesterday's volume (from 7d volume / 7 as proxy since we don't have yesterday's specific number)
    const vol7dSum = boxes.reduce((sum, b) => sum + (b.metrics.volume_7d || 0), 0);
    const avgDailyFrom7d = vol7dSum / 7;
    const volChangePct = avgDailyFrom7d > 0
      ? ((totalVolToday - avgDailyFrom7d) / avgDailyFrom7d) * 100
      : null;

    // Box Index: sum of all floor prices (cost to buy one of every tracked box)
    const boxIndex = boxes.reduce((sum, b) => sum + (b.metrics.floor_price_usd || 0), 0);

    // Box Index change: weighted avg of 1d price changes (weighted by floor price)
    let boxIndexChangePct: number | null = null;
    const totalFloor = boxes.reduce((s, b) => s + (b.metrics.floor_price_usd || 0), 0);
    if (totalFloor > 0) {
      const weightedChange = boxes.reduce((s, b) => {
        const floor = b.metrics.floor_price_usd || 0;
        const change = b.metrics.floor_price_1d_change_pct;
        if (change !== null && change !== undefined && floor > 0) {
          return s + change * (floor / totalFloor);
        }
        return s;
      }, 0);
      boxIndexChangePct = weightedChange;
    }

    // Fear & Greed
    const fearGreedIndex = computeFearGreedIndex(boxes);

    return {
      totalVolToday,
      volChangePct,
      boxIndex,
      boxIndexChangePct,
      fearGreedIndex,
    };
  }, [boxes]);

  if (!stats) return null;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6 px-3 sm:px-0">
      {/* Total Market Volume Today */}
      <div className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-4 min-h-[120px] flex flex-col items-center justify-center">
        <div className="text-white/50 text-xs font-medium uppercase tracking-wider mb-2 text-center">
          Market Volume Today
        </div>
        <div className="flex items-baseline gap-2 justify-center">
          <span className="text-white text-xl font-bold">{formatUsd(stats.totalVolToday)}</span>
          {stats.volChangePct !== null && (
            <span className={`text-xs font-medium ${stats.volChangePct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatPct(stats.volChangePct)}
            </span>
          )}
        </div>
        <div className="text-white/30 text-[10px] mt-1 text-center">vs 7d daily avg</div>
      </div>

      {/* Box Index */}
      <div className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-4 min-h-[120px] flex flex-col items-center justify-center">
        <div className="text-white/50 text-xs font-medium uppercase tracking-wider mb-2 text-center">
          Box Index
        </div>
        <div className="flex items-baseline gap-2 justify-center">
          <span className="text-white text-xl font-bold">{formatUsd(stats.boxIndex)}</span>
          {stats.boxIndexChangePct !== null && (
            <span className={`text-xs font-medium ${stats.boxIndexChangePct >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatPct(stats.boxIndexChangePct)}
            </span>
          )}
        </div>
        <div className="text-white/30 text-[10px] mt-1 text-center">sum of all floor prices</div>
      </div>

      {/* Fear & Greed Index */}
      <div className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-4 min-h-[120px] flex flex-col items-center justify-center">
        <div className="text-white/50 text-xs font-medium uppercase tracking-wider mb-1 text-center">
          Fear & Greed Index
        </div>
        <FearGreedGauge value={stats.fearGreedIndex} size={110} />
      </div>

      {/* Total Manga Price - Placeholder */}
      <div className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-4 min-h-[120px] flex flex-col items-center justify-center">
        <div className="text-white/50 text-xs font-medium uppercase tracking-wider mb-2 text-center">
          Total Manga Price
        </div>
        <div className="text-white/20 text-sm font-medium text-center">Coming Soon</div>
        <div className="text-white/15 text-[10px] mt-1 text-center">Manga market tracking</div>
      </div>
    </div>
  );
}
