'use client';

import { MarketMacroData } from '@/lib/api/marketMacro';

interface MacroSupplyProps {
  data: MarketMacroData;
}

function formatNum(value: number | null): string {
  if (value === null || value === undefined) return '--';
  return value.toLocaleString();
}

export function MacroSupply({ data }: MacroSupplyProps) {
  return (
    <div>
      <h4 className="text-white/50 text-[10px] font-semibold uppercase tracking-wider mb-2">Supply</h4>
      <div className="space-y-1 text-xs">
        <div>
          <span className="text-white/40">Listings: </span>
          <span className="text-white/80">{formatNum(data.total_active_listings)}</span>
        </div>
        <div>
          <span className="text-white/40">Added: </span>
          <span className="text-white/80">{data.total_boxes_added_today !== null && data.total_boxes_added_today !== undefined ? (data.total_boxes_added_today > 0 ? '+' : '') + formatNum(data.total_boxes_added_today) : '--'}</span>
        </div>
        <div>
          <span className="text-white/40">Net: </span>
          <span className={
            data.net_supply_change !== null
              ? data.net_supply_change > 0 ? 'text-red-400' : data.net_supply_change < 0 ? 'text-green-400' : 'text-white/40'
              : 'text-white/40'
          }>
            {data.net_supply_change !== null
              ? (data.net_supply_change > 0 ? '+' : '') + data.net_supply_change
              : '--'}
          </span>
        </div>
      </div>
    </div>
  );
}
