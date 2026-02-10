'use client';

import { MarketMacroData } from '@/lib/api/marketMacro';

interface MacroPriceMoversProps {
  data: MarketMacroData;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

function extractSetCode(name: string | null): string {
  if (!name) return '??';
  const match = name.match(/(OP-\d+|EB-\d+|PRB-\d+)/i);
  return match ? match[1] : name.slice(0, 12);
}

export function MacroPriceMovers({ data }: MacroPriceMoversProps) {
  const up = data.floors_up_count ?? 0;
  const down = data.floors_down_count ?? 0;
  const flat = data.floors_flat_count ?? 0;

  return (
    <div>
      <h4 className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-2">Price Movement</h4>
      <div className="text-xs text-white/70 mb-2">
        <span className="text-green-400">{up} up</span>
        {' / '}
        <span className="text-red-400">{down} down</span>
        {' / '}
        <span className="text-white/40">{flat} flat</span>
      </div>
      {data.biggest_gainer.name && (
        <div className="text-xs mb-1">
          <span className="text-white/40">Gainer: </span>
          <span className="text-green-400">
            {extractSetCode(data.biggest_gainer.name)} {formatPct(data.biggest_gainer.pct)}
          </span>
        </div>
      )}
      {data.biggest_loser.name && (
        <div className="text-xs">
          <span className="text-white/40">Loser: </span>
          <span className="text-red-400">
            {extractSetCode(data.biggest_loser.name)} {formatPct(data.biggest_loser.pct)}
          </span>
        </div>
      )}
    </div>
  );
}
