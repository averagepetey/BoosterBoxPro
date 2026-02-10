'use client';

import { MarketMacroData } from '@/lib/api/marketMacro';

interface MacroTrends7dProps {
  data: MarketMacroData;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

export function MacroTrends7d({ data }: MacroTrends7dProps) {
  const indexTrending = data.index_7d_change_pct !== null
    ? data.index_7d_change_pct >= 0 ? 'up' : 'down'
    : null;

  const volumeTrending = data.volume_7d_change_pct !== null
    ? data.volume_7d_change_pct >= 0 ? 'growing' : 'shrinking'
    : null;

  return (
    <div>
      <h4 className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-2">7D Trends</h4>
      <ul className="space-y-1.5">
        <li className="flex items-center gap-1.5 text-xs">
          <span className="text-white/40">Index</span>
          {indexTrending ? (
            <span className={indexTrending === 'up' ? 'text-green-400' : 'text-red-400'}>
              trending {indexTrending} {formatPct(data.index_7d_change_pct)}
            </span>
          ) : (
            <span className="text-white/40">--</span>
          )}
        </li>
        <li className="flex items-center gap-1.5 text-xs">
          <span className="text-white/40">Volume</span>
          {volumeTrending ? (
            <span className={volumeTrending === 'growing' ? 'text-green-400' : 'text-red-400'}>
              {volumeTrending} {formatPct(data.volume_7d_change_pct)}
            </span>
          ) : (
            <span className="text-white/40">--</span>
          )}
        </li>
      </ul>
    </div>
  );
}
