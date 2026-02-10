'use client';

import { MarketMacroData } from '@/lib/api/marketMacro';

interface MacroHighlights24hProps {
  data: MarketMacroData;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

function formatUsd(value: number | null): string {
  if (value === null || value === undefined) return '--';
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

export function MacroHighlights24h({ data }: MacroHighlights24hProps) {
  const items = [
    {
      label: 'Index',
      value: formatPct(data.index_1d_change_pct),
      positive: data.index_1d_change_pct !== null ? data.index_1d_change_pct >= 0 : null,
    },
    {
      label: 'Vol',
      value: formatPct(data.volume_1d_change_pct),
      positive: data.volume_1d_change_pct !== null ? data.volume_1d_change_pct >= 0 : null,
    },
    {
      label: 'Sold',
      value: data.total_boxes_sold_today !== null ? `${Math.round(data.total_boxes_sold_today)} boxes` : '--',
      positive: null,
    },
  ];

  return (
    <div>
      <h4 className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-2">24H Highlights</h4>
      <ul className="space-y-1.5">
        {items.map((item) => (
          <li key={item.label} className="flex items-center gap-1.5 text-xs">
            <span className="text-white/40">{item.label}</span>
            <span className={
              item.positive === null
                ? 'text-white/70'
                : item.positive
                  ? 'text-green-400'
                  : 'text-red-400'
            }>
              {item.positive !== null && (item.positive ? '▲' : '▼')} {item.value}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
