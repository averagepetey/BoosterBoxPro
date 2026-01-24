/**
 * Advanced Metrics Table Component
 * Displays historical metrics in a sortable table format
 */

'use client';

import { useState, useMemo } from 'react';

interface MetricRow {
  date: string;
  floor_price_usd?: number | null;
  floor_price_1d_change_pct?: number | null;
  unified_volume_7d_ema?: number | null;
  unified_volume_usd?: number | null;
  active_listings_count?: number | null;
  visible_market_cap_usd?: number | null;
  units_sold_count?: number | null;
  boxes_sold_per_day?: number | null;
  boxes_added_today?: number | null;
  days_to_20pct_increase?: number | null;
}

interface AdvancedMetricsTableProps {
  data: MetricRow[];
  isLoading?: boolean;
}

type SortColumn = keyof MetricRow | null;
type SortDirection = 'asc' | 'desc';

export function AdvancedMetricsTable({ data, isLoading = false }: AdvancedMetricsTableProps) {
  const [sortColumn, setSortColumn] = useState<SortColumn>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (column: keyof MetricRow) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const sortedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.log('AdvancedMetricsTable: No data to sort');
      return [];
    }
    if (!sortColumn) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      // Handle null/undefined values
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      // Compare values
      let comparison = 0;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal;
      } else if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal);
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  const formatCurrency = (value: number | null | undefined): string => {
    if (value == null) return '--';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number | null | undefined): string => {
    if (value == null) return '--';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  const formatNumber = (value: number | null | undefined): string => {
    if (value == null) return '--';
    return value.toLocaleString();
  };

  const formatDecimal = (value: number | null | undefined, decimals: number = 1): string => {
    if (value == null) return '--';
    return value.toFixed(decimals);
  };

  const SortIcon = ({ column }: { column: keyof MetricRow }) => {
    if (sortColumn !== column) return null;
    return <span className="ml-1 text-xs">{sortDirection === 'asc' ? '▲' : '▼'}</span>;
  };

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-white/50 text-sm">No metrics data available</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th
              className="text-left py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('date')}
            >
              Date <SortIcon column="date" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('floor_price_usd')}
            >
              Floor Price <SortIcon column="floor_price_usd" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('floor_price_1d_change_pct')}
            >
              Change % <SortIcon column="floor_price_1d_change_pct" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('unified_volume_7d_ema')}
            >
              Volume (7d EMA) <SortIcon column="unified_volume_7d_ema" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('unified_volume_usd')}
            >
              30d Volume <SortIcon column="unified_volume_usd" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('active_listings_count')}
            >
              Listings <SortIcon column="active_listings_count" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('units_sold_count')}
            >
              Units Sold <SortIcon column="units_sold_count" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('days_to_20pct_increase')}
            >
              Days to +20% <SortIcon column="days_to_20pct_increase" />
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, index) => (
            <tr
              key={index}
              className="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              <td className="py-3 px-4 text-white/90">{formatDate(row.date)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.floor_price_usd)}</td>
              <td className={`py-3 px-4 text-right ${
                row.floor_price_1d_change_pct && row.floor_price_1d_change_pct > 0
                  ? 'text-green-400'
                  : row.floor_price_1d_change_pct && row.floor_price_1d_change_pct < 0
                  ? 'text-red-400'
                  : 'text-white/70'
              }`}>
                {formatPercentage(row.floor_price_1d_change_pct)}
              </td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.unified_volume_7d_ema)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.unified_volume_usd)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatNumber(row.active_listings_count)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatNumber(row.units_sold_count)}</td>
              <td className="py-3 px-4 text-right text-white/90">
                {row.days_to_20pct_increase != null ? formatDecimal(row.days_to_20pct_increase) : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


 * Displays historical metrics in a sortable table format
 */

'use client';

import { useState, useMemo } from 'react';

interface MetricRow {
  date: string;
  floor_price_usd?: number | null;
  floor_price_1d_change_pct?: number | null;
  unified_volume_7d_ema?: number | null;
  unified_volume_usd?: number | null;
  active_listings_count?: number | null;
  visible_market_cap_usd?: number | null;
  units_sold_count?: number | null;
  boxes_sold_per_day?: number | null;
  boxes_added_today?: number | null;
  days_to_20pct_increase?: number | null;
}

interface AdvancedMetricsTableProps {
  data: MetricRow[];
  isLoading?: boolean;
}

type SortColumn = keyof MetricRow | null;
type SortDirection = 'asc' | 'desc';

export function AdvancedMetricsTable({ data, isLoading = false }: AdvancedMetricsTableProps) {
  const [sortColumn, setSortColumn] = useState<SortColumn>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (column: keyof MetricRow) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const sortedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.log('AdvancedMetricsTable: No data to sort');
      return [];
    }
    if (!sortColumn) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      // Handle null/undefined values
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      // Compare values
      let comparison = 0;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal;
      } else if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal);
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  const formatCurrency = (value: number | null | undefined): string => {
    if (value == null) return '--';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number | null | undefined): string => {
    if (value == null) return '--';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  const formatNumber = (value: number | null | undefined): string => {
    if (value == null) return '--';
    return value.toLocaleString();
  };

  const formatDecimal = (value: number | null | undefined, decimals: number = 1): string => {
    if (value == null) return '--';
    return value.toFixed(decimals);
  };

  const SortIcon = ({ column }: { column: keyof MetricRow }) => {
    if (sortColumn !== column) return null;
    return <span className="ml-1 text-xs">{sortDirection === 'asc' ? '▲' : '▼'}</span>;
  };

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-white/50 text-sm">No metrics data available</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th
              className="text-left py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('date')}
            >
              Date <SortIcon column="date" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('floor_price_usd')}
            >
              Floor Price <SortIcon column="floor_price_usd" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('floor_price_1d_change_pct')}
            >
              Change % <SortIcon column="floor_price_1d_change_pct" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('unified_volume_7d_ema')}
            >
              Volume (7d EMA) <SortIcon column="unified_volume_7d_ema" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('unified_volume_usd')}
            >
              30d Volume <SortIcon column="unified_volume_usd" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('active_listings_count')}
            >
              Listings <SortIcon column="active_listings_count" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('units_sold_count')}
            >
              Units Sold <SortIcon column="units_sold_count" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('days_to_20pct_increase')}
            >
              Days to +20% <SortIcon column="days_to_20pct_increase" />
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, index) => (
            <tr
              key={index}
              className="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              <td className="py-3 px-4 text-white/90">{formatDate(row.date)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.floor_price_usd)}</td>
              <td className={`py-3 px-4 text-right ${
                row.floor_price_1d_change_pct && row.floor_price_1d_change_pct > 0
                  ? 'text-green-400'
                  : row.floor_price_1d_change_pct && row.floor_price_1d_change_pct < 0
                  ? 'text-red-400'
                  : 'text-white/70'
              }`}>
                {formatPercentage(row.floor_price_1d_change_pct)}
              </td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.unified_volume_7d_ema)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.unified_volume_usd)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatNumber(row.active_listings_count)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatNumber(row.units_sold_count)}</td>
              <td className="py-3 px-4 text-right text-white/90">
                {row.days_to_20pct_increase != null ? formatDecimal(row.days_to_20pct_increase) : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


 * Displays historical metrics in a sortable table format
 */

'use client';

import { useState, useMemo } from 'react';

interface MetricRow {
  date: string;
  floor_price_usd?: number | null;
  floor_price_1d_change_pct?: number | null;
  unified_volume_7d_ema?: number | null;
  unified_volume_usd?: number | null;
  active_listings_count?: number | null;
  visible_market_cap_usd?: number | null;
  units_sold_count?: number | null;
  boxes_sold_per_day?: number | null;
  boxes_added_today?: number | null;
  days_to_20pct_increase?: number | null;
}

interface AdvancedMetricsTableProps {
  data: MetricRow[];
  isLoading?: boolean;
}

type SortColumn = keyof MetricRow | null;
type SortDirection = 'asc' | 'desc';

export function AdvancedMetricsTable({ data, isLoading = false }: AdvancedMetricsTableProps) {
  const [sortColumn, setSortColumn] = useState<SortColumn>('date');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  const handleSort = (column: keyof MetricRow) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
  };

  const sortedData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      console.log('AdvancedMetricsTable: No data to sort');
      return [];
    }
    if (!sortColumn) return data;

    return [...data].sort((a, b) => {
      const aVal = a[sortColumn];
      const bVal = b[sortColumn];

      // Handle null/undefined values
      if (aVal == null && bVal == null) return 0;
      if (aVal == null) return 1;
      if (bVal == null) return -1;

      // Compare values
      let comparison = 0;
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        comparison = aVal - bVal;
      } else if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal);
      }

      return sortDirection === 'asc' ? comparison : -comparison;
    });
  }, [data, sortColumn, sortDirection]);

  const formatCurrency = (value: number | null | undefined): string => {
    if (value == null) return '--';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const formatPercentage = (value: number | null | undefined): string => {
    if (value == null) return '--';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  };

  const formatNumber = (value: number | null | undefined): string => {
    if (value == null) return '--';
    return value.toLocaleString();
  };

  const formatDecimal = (value: number | null | undefined, decimals: number = 1): string => {
    if (value == null) return '--';
    return value.toFixed(decimals);
  };

  const SortIcon = ({ column }: { column: keyof MetricRow }) => {
    if (sortColumn !== column) return null;
    return <span className="ml-1 text-xs">{sortDirection === 'asc' ? '▲' : '▼'}</span>;
  };

  if (isLoading) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30"></div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-white/50 text-sm">No metrics data available</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th
              className="text-left py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('date')}
            >
              Date <SortIcon column="date" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('floor_price_usd')}
            >
              Floor Price <SortIcon column="floor_price_usd" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('floor_price_1d_change_pct')}
            >
              Change % <SortIcon column="floor_price_1d_change_pct" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('unified_volume_7d_ema')}
            >
              Volume (7d EMA) <SortIcon column="unified_volume_7d_ema" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('unified_volume_usd')}
            >
              30d Volume <SortIcon column="unified_volume_usd" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('active_listings_count')}
            >
              Listings <SortIcon column="active_listings_count" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('units_sold_count')}
            >
              Units Sold <SortIcon column="units_sold_count" />
            </th>
            <th
              className="text-right py-3 px-4 text-white/70 font-medium cursor-pointer hover:text-white transition-colors"
              onClick={() => handleSort('days_to_20pct_increase')}
            >
              Days to +20% <SortIcon column="days_to_20pct_increase" />
            </th>
          </tr>
        </thead>
        <tbody>
          {sortedData.map((row, index) => (
            <tr
              key={index}
              className="border-b border-white/5 hover:bg-white/5 transition-colors"
            >
              <td className="py-3 px-4 text-white/90">{formatDate(row.date)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.floor_price_usd)}</td>
              <td className={`py-3 px-4 text-right ${
                row.floor_price_1d_change_pct && row.floor_price_1d_change_pct > 0
                  ? 'text-green-400'
                  : row.floor_price_1d_change_pct && row.floor_price_1d_change_pct < 0
                  ? 'text-red-400'
                  : 'text-white/70'
              }`}>
                {formatPercentage(row.floor_price_1d_change_pct)}
              </td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.unified_volume_7d_ema)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatCurrency(row.unified_volume_usd)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatNumber(row.active_listings_count)}</td>
              <td className="py-3 px-4 text-right text-white/90">{formatNumber(row.units_sold_count)}</td>
              <td className="py-3 px-4 text-right text-white/90">
                {row.days_to_20pct_increase != null ? formatDecimal(row.days_to_20pct_increase) : 'N/A'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

