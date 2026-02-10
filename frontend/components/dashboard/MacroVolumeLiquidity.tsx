'use client';

import { MarketMacroData } from '@/lib/api/marketMacro';

interface MacroVolumeLiquidityProps {
  data: MarketMacroData;
}

function formatUsd(value: number | null): string {
  if (value === null || value === undefined) return '--';
  if (value >= 1_000_000) return `$${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `$${(value / 1_000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined || isNaN(value)) return '--';
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(1)}%`;
}

export function MacroVolumeLiquidity({ data }: MacroVolumeLiquidityProps) {
  return (
    <div>
      <h4 className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-2">Volume & Liquidity</h4>
      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
        <div>
          <span className="text-white/40">Today: </span>
          <span className="text-white/80">{formatUsd(data.total_daily_volume_usd)}</span>
        </div>
        <div>
          <span className="text-white/40">7d: </span>
          <span className="text-white/80">{formatUsd(data.total_7d_volume_usd)}</span>
        </div>
        <div>
          <span className="text-white/40">Vol &Delta;: </span>
          <span className={
            data.volume_1d_change_pct !== null
              ? data.volume_1d_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
              : 'text-white/40'
          }>
            {formatPct(data.volume_1d_change_pct)}
          </span>
        </div>
        <div>
          <span className="text-white/40">Liq: </span>
          <span className="text-white/80">{data.avg_liquidity_score?.toFixed(1) ?? '--'}</span>
        </div>
      </div>
    </div>
  );
}
