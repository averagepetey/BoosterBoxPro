'use client';

import { useState, useRef, useEffect } from 'react';
import { useMarketMacro, useMarketIndexTimeSeries } from '@/hooks/useMarketMacro';
import { MarketIndexChart } from './MarketIndexChart';
import { SentimentBadge } from './SentimentBadge';
import { FearGreedGauge } from './FearGreedGauge';
import { MacroHighlights24h } from './MacroHighlights24h';
import { MacroTrends7d } from './MacroTrends7d';
import { MacroPriceMovers } from './MacroPriceMovers';
import { MacroVolumeLiquidity } from './MacroVolumeLiquidity';
import { MacroSupply } from './MacroSupply';

type ChartRange = 7 | 30 | 90 | 365;

function formatUsd(value: number | null): string {
  if (value === null || value === undefined) return '--';
  return `$${value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

function InfoTooltip() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  return (
    <div className="relative inline-flex" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="ml-1.5 w-4 h-4 rounded-full bg-white/10 hover:bg-white/20 text-white/40 hover:text-white/60 text-[10px] font-bold flex items-center justify-center transition"
        aria-label="What is the BoosterBox Index?"
      >
        i
      </button>
      {open && (
        <div className="absolute left-0 top-full mt-2 z-50 w-64 rounded-lg border border-white/15 bg-[#1a1a1a] p-3 shadow-xl text-xs text-white/70 leading-relaxed">
          <p className="font-semibold text-white/90 mb-1">BoosterBox Index</p>
          <p>The total cost to own one of every sealed One Piece booster box. It tracks the combined floor prices of all 18 sets to show the overall market direction at a glance.</p>
        </div>
      )}
    </div>
  );
}

export function MarketMacroPanel() {
  const [chartRange, setChartRange] = useState<ChartRange>(30);
  const { data: macro, isLoading: macroLoading, error: macroError } = useMarketMacro();
  const { data: timeSeries } = useMarketIndexTimeSeries(chartRange);

  if (macroLoading) {
    return (
      <div className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-sm p-6 mb-6 mx-3 sm:mx-0">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-white/10 rounded w-1/3" />
          <div className="h-[200px] bg-white/5 rounded" />
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-20 bg-white/5 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (macroError) {
    console.error('[MarketMacroPanel] Error loading macro data:', macroError);
  }

  if (!macro) return null;

  const indexChangePct = macro.index_1d_change_pct;
  const isPositive = indexChangePct !== null && indexChangePct >= 0;

  const rangeBtns: { label: string; value: ChartRange }[] = [
    { label: '7d', value: 7 },
    { label: '30d', value: 30 },
    { label: '90d', value: 90 },
    { label: '1y', value: 365 },
  ];

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] backdrop-blur-sm mb-6 mx-3 sm:mx-0 overflow-hidden">
      {/* Top row: Index value + Sentiment/F&G */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-0">
        {/* Left: Index + Chart (2 cols on lg) */}
        <div className="lg:col-span-2 p-4 sm:p-6 border-b lg:border-b-0 lg:border-r border-white/10">
          {/* Index header */}
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-1 flex items-center">
                BoosterBox Index
                <InfoTooltip />
              </div>
              <div className="flex items-baseline gap-2">
                <span className="text-white text-2xl font-bold">{formatUsd(macro.index_value)}</span>
                {indexChangePct !== null && (
                  <span className={`text-sm font-medium ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
                    {isPositive ? '▲' : '▼'} {formatPct(indexChangePct)}
                  </span>
                )}
              </div>
            </div>
            {/* Chart range pills */}
            <div className="flex items-center gap-1 bg-white/5 rounded-full p-0.5">
              {rangeBtns.map((btn) => (
                <button
                  key={btn.value}
                  onClick={() => setChartRange(btn.value)}
                  className={`px-2.5 py-1 text-[10px] font-medium rounded-full transition ${
                    chartRange === btn.value
                      ? 'bg-white/15 text-white'
                      : 'text-white/40 hover:text-white/60'
                  }`}
                >
                  {btn.label}
                </button>
              ))}
            </div>
          </div>

          {/* Chart */}
          <div className="h-[200px]">
            {timeSeries && timeSeries.length > 0 ? (
              <MarketIndexChart data={timeSeries} height={200} />
            ) : (
              <div className="h-full flex items-center justify-center text-white/30 text-sm">
                Loading chart...
              </div>
            )}
          </div>
        </div>

        {/* Right: Sentiment + Fear & Greed */}
        <div className="p-4 sm:p-6 flex flex-col items-center justify-center gap-4">
          <div>
            <div className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-2 text-center">
              Sentiment
            </div>
            <SentimentBadge sentiment={macro.sentiment} />
          </div>
          <div>
            <div className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-1 text-center">
              Fear & Greed
            </div>
            <FearGreedGauge value={macro.fear_greed_score ?? 50} size={120} />
          </div>
        </div>
      </div>

      {/* Bottom sections */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-0 border-t border-white/10">
        <div className="p-4 border-b lg:border-b-0 lg:border-r border-white/10">
          <MacroHighlights24h data={macro} />
        </div>
        <div className="p-4 border-b lg:border-b-0 lg:border-r border-white/10">
          <MacroTrends7d data={macro} />
        </div>
        <div className="p-4 border-b lg:border-b-0 lg:border-r border-white/10">
          <MacroPriceMovers data={macro} />
        </div>
        <div className="p-4 border-b lg:border-b-0 lg:border-r border-white/10">
          <MacroVolumeLiquidity data={macro} />
        </div>
        <div className="p-4">
          <MacroSupply data={macro} />
        </div>
      </div>
    </div>
  );
}
