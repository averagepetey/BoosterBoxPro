/**
 * Box Detail Page
 * Individual booster box details page with comprehensive metrics
 * Responsive design: mobile-first with desktop layout
 */

'use client';

import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { Navigation } from '@/components/ui/Navigation';
import { use } from 'react';
import Link from 'next/link';
import { useBoxDetail, useBoxTimeSeries } from '@/hooks/useBoxDetail';
import { useState } from 'react';
import { PriceChart } from '@/components/charts/PriceChart';
import { AdvancedMetricsTable } from '@/components/AdvancedMetricsTable';

export default function BoxDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { box, isLoading, error } = useBoxDetail(id);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y' | 'all'>('30d');
  // Enable time-series and rank history hooks
  const { data: timeSeriesData, isLoading: isLoadingTimeSeries } = useBoxTimeSeries(
    id, 
    'floor_price', 
    timeRange === 'all' ? 365 : parseInt(timeRange)
  );
  // Advanced Metrics table shows one entry per month
  const { data: allHistoricalData, isLoading: isLoadingAllHistorical } = useBoxTimeSeries(
    id,
    'floor_price',
    365,  // Always fetch all available data for the table
    true  // Filter to one entry per month
  );

  const formatCurrency = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '--';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(value);
  };

  const formatPercentage = (value: number | null | undefined): string => {
    if (value === null || value === undefined) return '--';
    const sign = value >= 0 ? '+' : '';
    return `${sign}${value.toFixed(2)}%`;
  };

  const getLiquidityScoreLabel = (score: number | null | undefined): string => {
    if (score === null || score === undefined) return 'N/A';
    if (score >= 70) return 'High';
    if (score >= 40) return 'Moderate';
    return 'Low';
  };

  const getLiquidityScoreColor = (score: number | null | undefined): string => {
    if (score === null || score === undefined) return 'text-white/70';
    if (score >= 70) return 'text-green-400';
    if (score >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getReprintRiskLabel = (risk: string | null | undefined): string => {
    if (!risk) return 'Unknown';
    return risk.charAt(0).toUpperCase() + risk.slice(1).toLowerCase();
  };

  const getReprintRiskColor = (risk: string | null | undefined): string => {
    if (!risk) return 'text-white/70';
    const lower = risk.toLowerCase();
    if (lower === 'low') return 'text-green-400';
    if (lower === 'moderate' || lower === 'medium') return 'text-yellow-400';
    return 'text-red-400';
  };

  const getReprintRiskBgColor = (risk: string | null | undefined): string => {
    if (!risk) return 'bg-white/10';
    const lower = risk.toLowerCase();
    if (lower === 'low') return 'bg-green-500/20 border-green-500/50';
    if (lower === 'moderate' || lower === 'medium') return 'bg-yellow-500/20 border-yellow-500/50';
    return 'bg-red-500/20 border-red-500/50';
  };

  const formatDate = (dateString: string | null | undefined): string => {
    if (!dateString) return '--';
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return dateString;
    }
  };

  if (isLoading) {
    return (
      <ProtectedRoute>
        <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)' }}>
          <Navigation />
          <div className="container mx-auto px-4 py-8">
            <div className="text-center py-16">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white/30 mx-auto mb-4"></div>
              <p className="text-white/60 text-sm">Loading box details...</p>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error || !box) {
  return (
    <ProtectedRoute>
        <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)' }}>
        <Navigation />
        <div className="container mx-auto px-4 py-8">
            <Link 
              href="/dashboard"
              className="inline-flex items-center text-white/70 hover:text-white mb-6 transition-colors"
            >
              ← Back to Leaderboard
            </Link>
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-6">
              <p className="text-red-400 text-sm">
                {error ? `Failed to load box: ${error.message}` : 'Box not found'}
              </p>
            </div>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  // Extract set number from product name (e.g., "OP-01", "OP-05")
  const setMatch = box.product_name.match(/(OP-\d+)/i);
  const setNumber = setMatch ? setMatch[1].toUpperCase() : null;

  return (
    <ProtectedRoute>
      <div className="min-h-screen" style={{ background: 'linear-gradient(180deg, #396EF0 0%, #2d5fe8 30%, #2563eb 60%, #1b5fd8 100%)' }}>
        <Navigation />
        <div className="container mx-auto px-3 lg:px-6 py-2 lg:py-8" style={{ maxWidth: '1400px' }}>
          {/* Back Button - Mobile: just icon, Desktop: icon + text */}
          <div className="flex items-center gap-2 mb-2 lg:mb-6">
            <Link 
              href="/dashboard"
              className="inline-flex items-center text-white/70 hover:text-white transition-colors"
            >
              <svg className="w-5 h-5 lg:w-6 lg:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              <span className="hidden lg:inline ml-1 text-white/70">Back</span>
            </Link>
          </div>

          {/* Main Product Information Section */}
          <div 
            className="rounded-xl lg:rounded-3xl p-3 lg:p-6 mb-3 lg:mb-6"
            style={{
              background: '#141414',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
            }}
          >
            {/* Mobile: Title, Image, then 3 key metrics */}
            <div className="lg:hidden mb-3">
              {/* Title and Info - inside container */}
              <div className="text-center mb-3 pb-3 border-b border-white/10">
                <h1 className="text-xl font-bold text-white">{box.product_name}</h1>
                <div className="flex items-center justify-center gap-2 text-white/50 text-xs mt-1">
                  {setNumber && <span>{setNumber}</span>}
                  {box.release_date && setNumber && <span>•</span>}
                  {box.release_date && <span>{formatDate(box.release_date)}</span>}
                </div>
              </div>
              {/* Image */}
              {box.image_url && (
                <div className="flex justify-center mb-3 pb-3 border-b border-white/10">
                  <img
                    src={box.image_url}
                    alt={box.product_name}
                    className="w-24 h-24 object-contain rounded-lg"
                  />
                </div>
              )}
              {/* 3 Key Metrics - evenly spaced with dividers */}
              <div className="grid grid-cols-3 text-center mb-3 pb-3 border-b border-white/10">
                {/* Current Price */}
                <div className="border-r border-white/10 pr-2">
                  <div className="text-white/50 text-[10px] mb-0.5">Current Floor</div>
                  <div className="text-lg font-bold text-green-400">
                    {formatCurrency(box.metrics.floor_price_usd)}
                  </div>
                  {box.metrics.floor_price_1d_change_pct !== null && box.metrics.floor_price_1d_change_pct !== undefined && (
                    <div className={`text-[10px] font-semibold ${
                      box.metrics.floor_price_1d_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {box.metrics.floor_price_1d_change_pct >= 0 ? '▲' : '▼'}
                      {formatPercentage(box.metrics.floor_price_1d_change_pct)}
                    </div>
                  )}
                </div>
                {/* Volume EMA */}
                <div className="border-r border-white/10 px-2">
                  <div className="text-white/50 text-[10px] mb-0.5">Volume (7d EMA)</div>
                  <div className="text-lg font-bold text-white">
                    {formatCurrency(box.metrics.unified_volume_7d_ema)}
                  </div>
                </div>
                {/* Days to +20% */}
                <div className="pl-2">
                  <div className="text-white/50 text-[10px] mb-0.5">Days to +20%</div>
                  <div className="text-lg font-bold text-white">
                    {box.metrics.days_to_20pct_increase !== null && box.metrics.days_to_20pct_increase !== undefined
                      ? Math.round(box.metrics.days_to_20pct_increase)
                      : 'N/A'}
                  </div>
                  <div className="text-white/50 text-[10px]">Estimated</div>
                </div>
              </div>
            </div>

            {/* Mobile: Compact metrics grid - 2 rows only, chart follows immediately */}
            <div className="lg:hidden">
              {/* Row 1: Key metrics */}
              <div className="grid grid-cols-4 text-center pb-2 mb-2 border-b border-white/10">
                <div className="border-r border-white/10">
                  <div className="text-white/50 text-[10px]">Liquidity</div>
                  <div className={`text-sm font-bold ${getLiquidityScoreColor(box.metrics.liquidity_score)}`}>
                    {getLiquidityScoreLabel(box.metrics.liquidity_score)}
                  </div>
                </div>
                <div className="border-r border-white/10">
                  <div className="text-white/50 text-[10px]">Listed</div>
                  <div className="text-sm font-bold text-white">
                    {box.metrics.active_listings_count !== null && box.metrics.active_listings_count !== undefined
                      ? box.metrics.active_listings_count.toLocaleString()
                      : '--'}
                  </div>
                </div>
                <div className="border-r border-white/10">
                  <div className="text-white/50 text-[10px]">Sold/Day</div>
                  <div className="text-sm font-bold text-white">
                    {box.metrics.boxes_sold_per_day !== null && box.metrics.boxes_sold_per_day !== undefined
                      ? Math.round(box.metrics.boxes_sold_per_day * 10) / 10
                      : '--'}
                  </div>
                </div>
                <div>
                  <div className="text-white/50 text-[10px]">Time to Sale</div>
                  <div className="text-sm font-bold text-white">
                    {box.metrics.expected_time_to_sale_days !== null && box.metrics.expected_time_to_sale_days !== undefined
                      ? `${Math.round(box.metrics.expected_time_to_sale_days)}d`
                      : 'N/A'}
                  </div>
                </div>
              </div>

              {/* Row 2: Secondary metrics */}
              <div className="grid grid-cols-4 text-center pb-2 mb-2 border-b border-white/10">
                <div className="border-r border-white/10">
                  <div className="text-white/50 text-[10px]">Market Cap</div>
                  <div className="text-sm font-bold text-white">
                    {((box.metrics as any).visible_market_cap_usd !== null && (box.metrics as any).visible_market_cap_usd !== undefined)
                      ? formatCurrency((box.metrics as any).visible_market_cap_usd)
                      : '--'}
                  </div>
                </div>
                <div className="border-r border-white/10">
                  <div className="text-white/50 text-[10px]">Top 10 Cards</div>
                  <div className="text-sm font-bold text-white">
                    {box.metrics.top_10_value_usd !== null && box.metrics.top_10_value_usd !== undefined
                      ? formatCurrency(box.metrics.top_10_value_usd)
                      : '--'}
                  </div>
                </div>
                <div className="border-r border-white/10">
                  <div className="text-white/50 text-[10px]">Daily Vol</div>
                  <div className="text-sm font-bold text-white">
                    {(box.metrics as any).daily_volume_usd !== null && (box.metrics as any).daily_volume_usd !== undefined
                      ? formatCurrency((box.metrics as any).daily_volume_usd)
                      : '--'}
                  </div>
                </div>
                <div>
                  <div className="text-white/50 text-[10px]">30d Avg Sold</div>
                  <div className="text-sm font-bold text-white">
                    {box.metrics.boxes_sold_30d_avg
                      ? `${Math.round(box.metrics.boxes_sold_30d_avg * 10) / 10}/d`
                      : '--'}
                  </div>
                </div>
              </div>

              {/* Liquidity Warning - compact */}
              {box.metrics.active_listings_count !== null && box.metrics.active_listings_count !== undefined && box.metrics.active_listings_count < 3 && (
                <div className="mb-2 px-2 py-1 rounded bg-yellow-500/20 border border-yellow-500/50 flex items-center gap-1">
                  <span className="text-yellow-400 text-xs">⚠️ Low Liquidity</span>
                </div>
              )}
            </div>

            {/* Desktop: Original layout */}
            <div className="hidden lg:flex flex-col lg:flex-row gap-6">
              {/* Left: Product Image and Gauges */}
              <div className="flex-shrink-0 lg:w-96 flex flex-col gap-4">
                {box.image_url && (
                  <img
                    src={box.image_url}
                    alt={box.product_name}
                    className="w-full lg:w-96 lg:h-96 object-contain rounded-lg"
                  />
                )}
                
                {/* Liquidity Score and Reprint Risk Gauges */}
                <div 
                  className="rounded-2xl p-4"
                  style={{
                    background: '#141414',
                    border: '1px solid rgba(255, 255, 255, 0.15)',
                    boxShadow: '0 30px 80px rgba(0,0,0,0.2)'
                  }}
                >
                  <div className="grid grid-cols-2 gap-4">
                    {/* Liquidity Score Gauge */}
                    <div>
                      <h3 className="text-sm font-bold text-white mb-3 text-center">Liquidity Score</h3>
                      <div className="relative w-full h-24 mb-2">
                        {/* Gauge Background */}
                        <svg className="w-full h-full" viewBox="0 0 200 100">
                          <path
                            d="M 20 80 A 80 80 0 0 1 180 80"
                            fill="none"
                            stroke="rgba(255, 255, 255, 0.1)"
                            strokeWidth="12"
                          />
                          {/* Gauge Fill */}
                          <path
                            d="M 20 80 A 80 80 0 0 1 180 80"
                            fill="none"
                            stroke={box.metrics.liquidity_score && box.metrics.liquidity_score >= 70 ? '#10b981' : box.metrics.liquidity_score && box.metrics.liquidity_score >= 40 ? '#fbbf24' : '#ef4444'}
                            strokeWidth="12"
                            strokeDasharray={`${(box.metrics.liquidity_score || 0) * 2.51} 251`}
                            strokeDashoffset="0"
                            strokeLinecap="round"
                          />
                        </svg>
                        {/* Label */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className={`text-lg font-bold ${getLiquidityScoreColor(box.metrics.liquidity_score)}`}>
                            {getLiquidityScoreLabel(box.metrics.liquidity_score).toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Reprint Risk Gauge */}
                    <div>
                      <h3 className="text-sm font-bold text-white mb-3 text-center">Reprint Risk</h3>
                      <div className="relative w-full h-24 mb-2">
                        {/* Gauge Background */}
                        <svg className="w-full h-full" viewBox="0 0 200 100">
                          <path
                            d="M 20 80 A 80 80 0 0 1 180 80"
                            fill="none"
                            stroke="rgba(255, 255, 255, 0.1)"
                            strokeWidth="12"
                          />
                          {/* Gauge Fill */}
                          <path
                            d="M 20 80 A 80 80 0 0 1 180 80"
                            fill="none"
                            stroke={box.reprint_risk?.toLowerCase() === 'low' ? '#10b981' : box.reprint_risk?.toLowerCase() === 'moderate' || box.reprint_risk?.toLowerCase() === 'medium' ? '#fbbf24' : '#ef4444'}
                            strokeWidth="12"
                            strokeDasharray={box.reprint_risk?.toLowerCase() === 'low' ? '84 251' : box.reprint_risk?.toLowerCase() === 'moderate' || box.reprint_risk?.toLowerCase() === 'medium' ? '125 251' : '167 251'}
                            strokeDashoffset="0"
                            strokeLinecap="round"
                          />
                        </svg>
                        {/* Label */}
                        <div className="absolute inset-0 flex items-center justify-center">
                          <span className={`text-lg font-bold ${getReprintRiskColor(box.reprint_risk)}`}>
                            {getReprintRiskLabel(box.reprint_risk).toUpperCase()}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right: Product Info and Metrics */}
              <div className="flex-1 min-w-0">
                {/* Product Title, Rank, and Info */}
                <div className="mb-3">
                  <div className="flex items-start justify-between mb-2">
                    <h1 className="text-3xl lg:text-4xl font-bold text-white flex-1">{box.product_name}</h1>
                    {/* Rank Badge */}
                    {box.current_rank_by_volume && (
                      <div className="flex items-center gap-2 ml-4">
                        <div className="px-3 py-1 rounded-full bg-white/10 border border-white/20">
                          <span className="text-white/70 text-sm">Rank</span>
                          <span className="text-white font-bold text-lg ml-2">#{box.current_rank_by_volume}</span>
                        </div>
                        {/* Rank Change Indicator */}
                        {box.rank_change_direction && box.rank_change_amount !== null && box.rank_change_amount !== 0 && (
                          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-semibold ${
                            box.rank_change_direction === 'up' 
                              ? 'bg-green-500/20 text-green-400' 
                              : box.rank_change_direction === 'down'
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-white/10 text-white/70'
                          }`}>
                            {box.rank_change_direction === 'up' ? '↑' : box.rank_change_direction === 'down' ? '↓' : '→'}
                            <span>{Math.abs(box.rank_change_amount || 0)}</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-2 text-white/70 text-sm">
                    {box.game_type && <span>{box.game_type}</span>}
                    {setNumber && box.game_type && <span>•</span>}
                    {setNumber && <span>{setNumber}</span>}
                    {box.release_date && (setNumber || box.game_type) && <span>•</span>}
                    {box.release_date && (
                      <span>Released: {formatDate(box.release_date)}</span>
                    )}
                    {box.estimated_total_supply && (
                      <>
                        {(setNumber || box.game_type || box.release_date) && <span>•</span>}
                        <span>Supply: {box.estimated_total_supply.toLocaleString()}</span>
                      </>
                    )}
                  </div>
                </div>

                {/* Community Sentiment Rainbow Bar */}
                <div className="mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-white/70 text-sm">Community Sentiment</div>
                    <div className="text-white font-semibold text-sm">
                      {box.metrics.community_sentiment !== null && box.metrics.community_sentiment !== undefined
                        ? Math.round(box.metrics.community_sentiment)
                        : 50}/100
                    </div>
                  </div>
                  <div className="relative w-full h-6 rounded-full overflow-hidden bg-white/5 border border-white/10">
                    {/* Rainbow gradient background - full width */}
                    <div 
                      className="absolute inset-0"
                      style={{
                        background: 'linear-gradient(to right, #ef4444 0%, #f97316 12.5%, #eab308 25%, #84cc16 37.5%, #22c55e 50%, #3b82f6 62.5%, #8b5cf6 75%, #a855f7 87.5%, #ec4899 100%)'
                      }}
                    />
                    {/* Dark overlay for unfilled portion */}
                    <div 
                      className="absolute inset-0 bg-black/40"
                      style={{
                        clipPath: `inset(0 0 0 ${box.metrics.community_sentiment !== null && box.metrics.community_sentiment !== undefined ? box.metrics.community_sentiment : 50}%)`
                      }}
                    />
                    {/* Current value indicator line */}
                    <div 
                      className="absolute top-0 bottom-0 w-0.5 bg-white shadow-[0_0_4px_rgba(255,255,255,0.8)] z-10"
                      style={{
                        left: `${box.metrics.community_sentiment !== null && box.metrics.community_sentiment !== undefined ? box.metrics.community_sentiment : 50}%`,
                        transform: 'translateX(-50%)'
                      }}
                    />
                  </div>
                </div>

                {/* Primary Price Metrics */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
                  {/* Floor Price */}
                  <div>
                    <div className="text-white/70 text-sm mb-1">Current Floor Price</div>
                    <div className="text-4xl font-bold text-green-400 mb-1">
                      {formatCurrency(box.metrics.floor_price_usd)}
                    </div>
                    {/* 24h Change */}
                    {box.metrics.floor_price_1d_change_pct !== null && box.metrics.floor_price_1d_change_pct !== undefined && (
                      <div className={`text-base font-semibold flex items-center gap-1 ${
                        box.metrics.floor_price_1d_change_pct >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {box.metrics.floor_price_1d_change_pct >= 0 ? '▲' : '▼'}
                        {formatPercentage(box.metrics.floor_price_1d_change_pct)}
                        <span className="text-white/70 text-sm font-normal">24h</span>
                      </div>
                    )}
                  </div>

                  {/* Days to +20% */}
                  <div>
                    <div className="text-white/70 text-sm mb-1">Days to +20%</div>
                    <div className="text-3xl font-bold text-white mb-1">
                      {box.metrics.days_to_20pct_increase !== null && box.metrics.days_to_20pct_increase !== undefined
                        ? `${Math.round(box.metrics.days_to_20pct_increase)}`
                        : 'N/A'}
                    </div>
                    <div className="text-white/60 text-sm">
                      Estimated time to price increase
                    </div>
                  </div>

                  {/* Expected Time to Sale */}
                  <div>
                    <div className="text-white/70 text-sm mb-1">Expected Time to Sale</div>
                    <div className="text-3xl font-bold text-white mb-1">
                      {box.metrics.expected_time_to_sale_days !== null && box.metrics.expected_time_to_sale_days !== undefined
                        ? `${Math.round(box.metrics.expected_time_to_sale_days)} days`
                        : 'N/A'}
                    </div>
                    <div className="text-white/60 text-sm">
                      Estimated time until sale
                    </div>
                  </div>
                </div>

                {/* Market Cap and Liquidity - Compact Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 mb-4 mt-6">
                  <div>
                    <div className="text-white/70 text-sm mb-1">Market Cap</div>
                    <div className="text-lg font-semibold text-white">
                      {((box.metrics as any).visible_market_cap_usd !== null && (box.metrics as any).visible_market_cap_usd !== undefined)
                        ? formatCurrency((box.metrics as any).visible_market_cap_usd)
                        : '--'}
                    </div>
                  </div>
                  <div>
                    <div className="text-white/70 text-sm mb-1">Avg Added/Day</div>
                    <div className="text-lg font-semibold text-white">
                      {box.metrics.boxes_added_7d_ema !== null && box.metrics.boxes_added_7d_ema !== undefined
                        ? `${Math.round(box.metrics.boxes_added_7d_ema * 10) / 10}`
                        : box.metrics.boxes_added_30d_ema !== null && box.metrics.boxes_added_30d_ema !== undefined
                        ? `${Math.round(box.metrics.boxes_added_30d_ema * 10) / 10}`
                        : '--'}
                    </div>
                  </div>
                  <div>
                    <div className="text-white/70 text-sm mb-1">Boxes Listed</div>
                    <div className="text-lg font-semibold text-white">
                      {box.metrics.active_listings_count !== null && box.metrics.active_listings_count !== undefined
                        ? box.metrics.active_listings_count.toLocaleString()
                        : '--'}
                    </div>
                  </div>
                </div>

                {/* Supply & Demand Metrics - Compact Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 mb-4">
                  <div>
                    <div className="text-white/70 text-sm mb-1">Sold/Day</div>
                    <div className="text-lg font-semibold text-white">
                      {box.metrics.boxes_sold_per_day !== null && box.metrics.boxes_sold_per_day !== undefined
                        ? Math.round(box.metrics.boxes_sold_per_day * 10) / 10
                        : '--'}
                    </div>
                  </div>
                  <div>
                    <div className="text-white/70 text-sm mb-1">Top 10 Cards Value</div>
                    <div className="text-lg font-semibold text-white">
                      {box.metrics.top_10_value_usd !== null && box.metrics.top_10_value_usd !== undefined
                        ? formatCurrency(box.metrics.top_10_value_usd)
                        : '--'}
                    </div>
                  </div>
                  {(box.metrics as any).daily_volume_usd !== null && (box.metrics as any).daily_volume_usd !== undefined && (
                    <div>
                      <div className="text-white/70 text-sm mb-1">Daily Volume</div>
                      <div className="text-lg font-semibold text-white">
                        {formatCurrency((box.metrics as any).daily_volume_usd)}
                      </div>
                    </div>
                  )}
                  {box.metrics.boxes_sold_30d_avg && (
                    <div>
                      <div className="text-white/70 text-sm mb-1">30d Avg Sold</div>
                      <div className="text-lg font-semibold text-white">
                        {Math.round(box.metrics.boxes_sold_30d_avg * 10) / 10}/day
                      </div>
                    </div>
                  )}
                </div>


                {/* Additional Metrics - Momentum Score if available */}
                {box.metrics.momentum_score !== null && box.metrics.momentum_score !== undefined && (
                  <div className="mb-6">
                    <div className="text-white/70 text-sm mb-1">Momentum Score</div>
                    <div className="text-xl font-semibold text-white">
                      {box.metrics.momentum_score.toFixed(2)}
                    </div>
                  </div>
                )}

                {/* Calculated Metrics - Absorption Rate */}
                {/* Hidden until we have multi-day data for accurate daily additions comparison */}
                {/* {box.metrics.boxes_sold_per_day && box.metrics.boxes_added_today && box.metrics.boxes_added_today > 0 && (
                  <div className="mb-6 p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="text-white/70 text-sm mb-1">Absorption Rate</div>
                    <div className="text-xl font-semibold text-white">
                      {(box.metrics.boxes_sold_per_day / box.metrics.boxes_added_today).toFixed(2)}x
                    </div>
                    <div className="text-white/50 text-xs mt-1">
                      Selling {((box.metrics.boxes_sold_per_day / box.metrics.boxes_added_today) * 100).toFixed(0)}% faster than supply added
                    </div>
                  </div>
                )} */}

                {/* Liquidity Warning */}
                {box.metrics.active_listings_count !== null && box.metrics.active_listings_count !== undefined && box.metrics.active_listings_count < 3 && (
                  <div className="mb-6 p-3 rounded-lg bg-yellow-500/20 border border-yellow-500/50">
                    <div className="flex items-center gap-2">
                      <span className="text-yellow-400">⚠️</span>
                      <span className="text-yellow-400 text-sm font-semibold">Low Liquidity Warning</span>
                    </div>
                    <div className="text-yellow-400/80 text-xs mt-1">
                      Less than 3 active listings - metrics may be unreliable
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* Recent Trends / Price Chart - Mobile compact, Desktop full */}
            <div className="mt-3 lg:mt-6 pt-3 lg:pt-6 border-t border-white/10">
              <div className="flex items-center justify-between mb-2 lg:mb-4">
                <h2 className="text-sm lg:text-xl font-bold text-white">Price Trends</h2>
                {/* Time Range Buttons - inline on mobile */}
                <div className="flex gap-1 lg:gap-2">
                  {['7d', '30d', '90d', '1y', 'all'].map((range) => (
                    <button
                      key={range}
                      onClick={() => setTimeRange(range as any)}
                      className={`px-2 lg:px-3 py-0.5 lg:py-1.5 text-[10px] lg:text-xs rounded-full transition-colors ${
                        timeRange === range
                          ? 'bg-white/20 text-white'
                          : 'bg-white/5 text-white/70 hover:bg-white/10'
                      }`}
                    >
                      {range.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              {/* Price Chart - Compact on mobile */}
              {isLoadingTimeSeries ? (
                <div className="h-36 lg:h-80 flex items-center justify-center border border-white/10 rounded-lg bg-white/5 w-full">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white/30"></div>
                </div>
              ) : timeSeriesData && timeSeriesData.length > 0 ? (
                <div className="border border-white/10 rounded-lg bg-white/5 p-2 lg:p-6 h-36 lg:h-80 w-full overflow-hidden">
                  <div className="w-full h-full">
                    <PriceChart data={timeSeriesData.map((d: any) => ({
                      date: d.date,
                      floor_price_usd: d.floor_price_usd || 0,
                      volume: d.volume,
                      listings_count: d.listings_count,
                    }))} height={128} />
                  </div>
                </div>
              ) : (
                <div className="h-36 lg:h-80 flex items-center justify-center border border-white/10 rounded-lg bg-white/5 w-full">
                  <p className="text-white/50 text-sm">No price data available</p>
                </div>
              )}
            </div>

            {/* Mobile: Reprint Risk indicator + Gauges */}
            <div className="lg:hidden mt-4 pt-4 border-t border-white/10">
              {/* Reprint Risk Text Indicator */}
              <div className="flex items-center gap-2 mb-4">
                <span className="text-lg font-bold text-white">Reprint Risk</span>
                <span className={`text-sm ${getReprintRiskColor(box.reprint_risk)}`}>
                  {box.reprint_risk?.toLowerCase() === 'moderate' || box.reprint_risk?.toLowerCase() === 'medium' ? '⚠️' : box.reprint_risk?.toLowerCase() === 'high' ? '🔴' : '🟢'}
                </span>
                <span className={`font-semibold ${getReprintRiskColor(box.reprint_risk)}`}>
                  {getReprintRiskLabel(box.reprint_risk)}
                </span>
              </div>

              {/* Gauges side by side */}
              <div className="grid grid-cols-2 gap-3">
                {/* Liquidity Score Gauge */}
                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <h3 className="text-xs font-bold text-white mb-2 text-center">Liquidity Score</h3>
                  <div className="relative w-full h-16">
                    <svg className="w-full h-full" viewBox="0 0 200 100">
                      <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none" stroke="rgba(255, 255, 255, 0.1)" strokeWidth="10" />
                      <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none"
                        stroke={box.metrics.liquidity_score && box.metrics.liquidity_score >= 70 ? '#10b981' : box.metrics.liquidity_score && box.metrics.liquidity_score >= 40 ? '#fbbf24' : '#ef4444'}
                        strokeWidth="10" strokeDasharray={`${(box.metrics.liquidity_score || 0) * 2.51} 251`} strokeLinecap="round" />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center pt-2">
                      <span className={`text-sm font-bold ${getLiquidityScoreColor(box.metrics.liquidity_score)}`}>
                        {getLiquidityScoreLabel(box.metrics.liquidity_score).toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Reprint Risk Gauge */}
                <div className="bg-white/5 rounded-xl p-3 border border-white/10">
                  <h3 className="text-xs font-bold text-white mb-2 text-center">Reprint Risk</h3>
                  <div className="relative w-full h-16">
                    <svg className="w-full h-full" viewBox="0 0 200 100">
                      <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none" stroke="rgba(255, 255, 255, 0.1)" strokeWidth="10" />
                      <path d="M 20 80 A 80 80 0 0 1 180 80" fill="none"
                        stroke={box.reprint_risk?.toLowerCase() === 'low' ? '#10b981' : box.reprint_risk?.toLowerCase() === 'moderate' || box.reprint_risk?.toLowerCase() === 'medium' ? '#fbbf24' : '#ef4444'}
                        strokeWidth="10" strokeDasharray={box.reprint_risk?.toLowerCase() === 'low' ? '84 251' : box.reprint_risk?.toLowerCase() === 'moderate' || box.reprint_risk?.toLowerCase() === 'medium' ? '125 251' : '167 251'} strokeLinecap="round" />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center pt-2">
                      <span className={`text-sm font-bold ${getReprintRiskColor(box.reprint_risk)}`}>
                        {getReprintRiskLabel(box.reprint_risk).toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Market Notes & Signals Section */}
          <div 
            className="rounded-2xl lg:rounded-3xl p-4 lg:p-6 mb-4 lg:mb-6"
            style={{
              background: '#141414',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
            }}
          >
            <h2 className="text-lg lg:text-xl font-bold text-white mb-3 lg:mb-4">Notes</h2>
            <div className="space-y-2">
              <div className="text-white/70 text-sm">• No notes yet</div>
            </div>
          </div>

          {/* Comprehensive Metrics Section */}
          <div 
            className="rounded-2xl lg:rounded-3xl p-4 lg:p-6 mb-4 lg:mb-6"
            style={{
              background: '#141414',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
            }}
          >
            <h2 className="text-lg lg:text-xl font-bold text-white mb-4 lg:mb-6">Complete Metrics Overview</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Volume Metrics Column */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-white/70 uppercase tracking-wider mb-3">Volume Metrics</h3>
                <div>
                  <div className="text-white/70 text-xs mb-1">Daily Volume USD</div>
                  <div className="text-lg font-semibold text-white">
                    {(box.metrics as any).daily_volume_usd !== null && (box.metrics as any).daily_volume_usd !== undefined
                      ? formatCurrency((box.metrics as any).daily_volume_usd)
                      : '--'}
                  </div>
                </div>
                {(box.metrics as any).unified_volume_usd && (
                  <div>
                    <div className="text-white/70 text-xs mb-1">30-Day Volume Estimate</div>
                    <div className="text-lg font-semibold text-white">
                      {formatCurrency((box.metrics as any).unified_volume_usd)}
                    </div>
                  </div>
                )}
                <div>
                  <div className="text-white/70 text-xs mb-1">7-Day EMA Volume</div>
                  <div className="text-lg font-semibold text-white">
                    {formatCurrency(box.metrics.unified_volume_7d_ema)}
                  </div>
                </div>
                {box.metrics.volume_30d_sma && (
                  <div>
                    <div className="text-white/70 text-xs mb-1">30-Day SMA Volume</div>
                    <div className="text-lg font-semibold text-white">
                      {formatCurrency(box.metrics.volume_30d_sma)}
                    </div>
                  </div>
                )}
              </div>

              {/* Supply Metrics Column */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-white/70 uppercase tracking-wider mb-3">Supply Metrics</h3>
                <div>
                  <div className="text-white/70 text-xs mb-1">Active Listings</div>
                  <div className="text-lg font-semibold text-white">
                    {box.metrics.active_listings_count !== null && box.metrics.active_listings_count !== undefined
                      ? box.metrics.active_listings_count.toLocaleString()
                      : '--'}
                  </div>
                </div>
                <div>
                  <div className="text-white/70 text-xs mb-1">Volume Change</div>
                  <div className={`text-lg font-semibold ${
                    (() => {
                      // Use monthly data for month-over-month calculation
                      if (!allHistoricalData || allHistoricalData.length < 2) return 'text-white';
                      const currentMonth = allHistoricalData[allHistoricalData.length - 1];
                      const previousMonth = allHistoricalData[allHistoricalData.length - 2];
                      const currentVolume = currentMonth?.unified_volume_usd || 0;
                      const previousVolume = previousMonth?.unified_volume_usd || 0;
                      if (previousVolume === 0) return 'text-white';
                      const change = ((currentVolume - previousVolume) / previousVolume) * 100;
                      return change >= 0 ? 'text-green-400' : 'text-red-400';
                    })()
                  }`}>
                    {(() => {
                      // Use monthly data for month-over-month calculation
                      if (!allHistoricalData || allHistoricalData.length < 2) return '--';
                      const currentMonth = allHistoricalData[allHistoricalData.length - 1];
                      const previousMonth = allHistoricalData[allHistoricalData.length - 2];
                      const currentVolume = currentMonth?.unified_volume_usd || 0;
                      const previousVolume = previousMonth?.unified_volume_usd || 0;
                      if (previousVolume === 0) return '--';
                      const change = ((currentVolume - previousVolume) / previousVolume) * 100;
                      return `${change >= 0 ? '+' : ''}${change.toFixed(1)}%`;
                    })()}
                  </div>
                  <div className="text-white/50 text-xs mt-1">Month over Month</div>
                </div>
                {box.metrics.boxes_added_today !== null && box.metrics.boxes_added_today !== undefined && (
                  <div>
                    <div className="text-white/70 text-xs mb-1">Boxes Added Today</div>
                    <div className="text-lg font-semibold text-white">
                      {box.metrics.boxes_added_today.toLocaleString()}
                    </div>
                  </div>
                )}
                {box.metrics.boxes_added_7d_ema !== null && box.metrics.boxes_added_7d_ema !== undefined && (
                  <div>
                    <div className="text-white/70 text-xs mb-1">7-Day EMA Supply</div>
                    <div className="text-lg font-semibold text-white">
                      {Math.round(box.metrics.boxes_added_7d_ema * 10) / 10}/day
                    </div>
                  </div>
                )}
                {box.metrics.boxes_added_30d_ema !== null && box.metrics.boxes_added_30d_ema !== undefined && (
                  <div>
                    <div className="text-white/70 text-xs mb-1">30-Day EMA Supply</div>
                    <div className="text-lg font-semibold text-white">
                      {Math.round(box.metrics.boxes_added_30d_ema * 10) / 10}/day
                    </div>
                  </div>
                )}
              </div>
              
              {/* Demand & Performance Column */}
              <div className="space-y-4">
                <h3 className="text-sm font-semibold text-white/70 uppercase tracking-wider mb-3">Demand & Performance</h3>
                <div>
                  <div className="text-white/70 text-xs mb-1">Boxes Sold/Day</div>
                  <div className="text-lg font-semibold text-white">
                    {box.metrics.boxes_sold_per_day !== null && box.metrics.boxes_sold_per_day !== undefined
                      ? Math.round(box.metrics.boxes_sold_per_day * 10) / 10
                      : '--'}
                  </div>
                  {box.metrics.boxes_sold_30d_avg && (
                    <div className="text-white/50 text-xs mt-1">
                      30-Day Avg: {Math.round(box.metrics.boxes_sold_30d_avg * 10) / 10}/day
                    </div>
                  )}
                </div>
                <div>
                  <div className="text-white/70 text-xs mb-1">Days to +20% Increase</div>
                  <div className="text-lg font-semibold text-white">
                    {box.metrics.days_to_20pct_increase !== null && box.metrics.days_to_20pct_increase !== undefined
                      ? `${Math.round(box.metrics.days_to_20pct_increase)} days`
                      : 'N/A'}
                  </div>
                </div>
                {box.metrics.momentum_score !== null && box.metrics.momentum_score !== undefined && (
                  <div>
                    <div className="text-white/70 text-xs mb-1">Momentum Score</div>
                    <div className="text-lg font-semibold text-white">
                      {box.metrics.momentum_score.toFixed(2)}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Advanced Metrics Table Section */}
          <div 
            className="rounded-2xl lg:rounded-3xl p-4 lg:p-6 mb-4 lg:mb-6"
            style={{
              background: '#141414',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
            }}
          >
            <h2 className="text-lg lg:text-xl font-bold text-white mb-3 lg:mb-4">Advanced Metrics</h2>
            {isLoadingAllHistorical ? (
              <div className="h-64 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white/30"></div>
              </div>
            ) : (
              <AdvancedMetricsTable 
                data={allHistoricalData || []} 
                isLoading={isLoadingAllHistorical}
              />
            )}
          </div>

          {/* Marketplace Attribution & Context */}
          <div 
            className="rounded-2xl lg:rounded-3xl p-4 lg:p-6 mb-4 lg:mb-6"
            style={{
              background: '#141414',
              border: '1px solid rgba(255, 255, 255, 0.15)',
              boxShadow: '0 0 20px rgba(241, 48, 61, 0.6), 0 0 40px rgba(241, 48, 61, 0.4), 0 0 60px rgba(241, 48, 61, 0.2), 0 30px 80px rgba(0,0,0,0.2)'
            }}
          >
            <h2 className="text-lg lg:text-xl font-bold text-white mb-3 lg:mb-4">Data Sources & Context</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-white/70 text-xs mb-1">Floor Price Source</div>
                <div className="text-white font-medium">TCGplayer (Authoritative)</div>
              </div>
              <div>
                <div className="text-white/70 text-xs mb-1">Volume Source</div>
                <div className="text-white font-medium">Unified (TCGplayer 70% + eBay 30%)</div>
              </div>
              <div>
                <div className="text-white/70 text-xs mb-1">Supply Source</div>
                <div className="text-white font-medium">TCGplayer</div>
              </div>
              {box.set_name && (
                <div>
                  <div className="text-white/70 text-xs mb-1">Set Name</div>
                  <div className="text-white font-medium">{box.set_name}</div>
                </div>
              )}
            </div>
          </div>

          {/* Mobile: Back to Leaderboard button at bottom */}
          <div className="lg:hidden pb-4">
            <Link
              href="/dashboard"
              className="block w-full text-center py-3 rounded-xl bg-white/10 text-white font-medium hover:bg-white/20 transition-colors"
            >
              Back to Leaderboard
            </Link>
          </div>

        </div>
      </div>
    </ProtectedRoute>
  );
}
