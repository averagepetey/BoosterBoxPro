/**
 * Price Chart Component
 * SVG line chart with smooth monotone curve and gradient fill (no external chart API).
 * Optional: use QuickChart.io (free) for chart-as-image via PRICE_CHART_QUICKCHART_URL env.
 */

'use client';

import { useRef, useEffect, useState } from 'react';

interface PriceChartProps {
  data: Array<{
    date: string;
    floor_price_usd: number;
    volume?: number;
    listings_count?: number;
  }>;
  height?: number;
}

/** Build smooth curve path through points using cubic Bezier (Catmull-Rom style). */
function smoothPath(points: { x: number; y: number }[]): string {
  if (points.length === 0) return '';
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;
  if (points.length === 2) return `M ${points[0].x} ${points[0].y} L ${points[1].x} ${points[1].y}`;
  const tension = 0.3;
  let d = `M ${points[0].x} ${points[0].y}`;
  for (let i = 1; i < points.length; i++) {
    const p0 = points[Math.max(0, i - 2)];
    const p1 = points[i - 1];
    const p2 = points[i];
    const p3 = points[Math.min(points.length - 1, i + 1)];
    const cp1x = p1.x + (p2.x - p0.x) * tension / 6;
    const cp1y = p1.y + (p2.y - p0.y) * tension / 6;
    const cp2x = p2.x - (p3.x - p1.x) * tension / 6;
    const cp2y = p2.y - (p3.y - p1.y) * tension / 6;
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }
  return d;
}

export function PriceChart({ data, height = 256 }: PriceChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(600);

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setChartWidth(Math.max(rect.width, 600));
      }
    };
    if (containerRef.current) {
      const resizeObserver = new ResizeObserver(updateWidth);
      resizeObserver.observe(containerRef.current);
      const timeoutId = setTimeout(updateWidth, 100);
      return () => {
        clearTimeout(timeoutId);
        resizeObserver.disconnect();
      };
    }
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);

  if (!data || data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-white/50 text-sm">No data available</p>
      </div>
    );
  }

  const padding = { top: 24, right: 24, bottom: 44, left: 52 };
  const chartHeight = height;
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  const prices = data.map(d => d.floor_price_usd);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice || 1;
  const pad = priceRange * 0.02;
  const scaleMin = minPrice - pad;
  const scaleMax = maxPrice + pad;
  const scaleRange = scaleMax - scaleMin || 1;

  const points = data.map((d, i) => {
    const x = padding.left + (i / (data.length - 1 || 1)) * innerWidth;
    const y = padding.top + innerHeight - ((d.floor_price_usd - scaleMin) / scaleRange) * innerHeight;
    return { x, y, price: d.floor_price_usd, date: d.date };
  });

  const linePath = smoothPath(points);
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${padding.top + innerHeight} L ${points[0].x} ${padding.top + innerHeight} Z`;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const gridSteps = 5;
  const gridValues = Array.from({ length: gridSteps + 1 }, (_, i) => scaleMin + (scaleRange * i) / gridSteps);

  return (
    <div ref={containerRef} className="w-full h-full min-w-0">
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        preserveAspectRatio="xMidYMid meet"
        className="w-full h-full"
        style={{ minWidth: 0 }}
      >
        <defs>
          <linearGradient id="priceChartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.35" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
          </linearGradient>
        </defs>

        {/* Grid */}
        {gridValues.map((value, i) => {
          const y = padding.top + innerHeight - ((value - scaleMin) / scaleRange) * innerHeight;
          return (
            <g key={i}>
              <line
                x1={padding.left}
                y1={y}
                x2={padding.left + innerWidth}
                y2={y}
                stroke="rgba(255, 255, 255, 0.06)"
                strokeWidth="1"
              />
              <text
                x={padding.left - 8}
                y={y + 4}
                textAnchor="end"
                fill="rgba(255, 255, 255, 0.55)"
                fontSize="11"
                fontFamily="system-ui, sans-serif"
              >
                {formatCurrency(value)}
              </text>
            </g>
          );
        })}

        {/* X-axis labels */}
        {data.length > 0 && (
          <>
            <text x={padding.left} y={chartHeight - 8} fill="rgba(255, 255, 255, 0.55)" fontSize="11" fontFamily="system-ui, sans-serif">
              {formatDate(data[0].date)}
            </text>
            {data.length > 2 && (
              <text x={padding.left + innerWidth / 2} y={chartHeight - 8} textAnchor="middle" fill="rgba(255, 255, 255, 0.55)" fontSize="11" fontFamily="system-ui, sans-serif">
                {formatDate(data[Math.floor(data.length / 2)].date)}
              </text>
            )}
            {data.length > 1 && (
              <text x={padding.left + innerWidth} y={chartHeight - 8} textAnchor="end" fill="rgba(255, 255, 255, 0.55)" fontSize="11" fontFamily="system-ui, sans-serif">
                {formatDate(data[data.length - 1].date)}
              </text>
            )}
          </>
        )}

        {/* Area fill (under line) */}
        <path d={areaPath} fill="url(#priceChartGradient)" />

        {/* Smooth price line */}
        <path
          d={linePath}
          fill="none"
          stroke="#34d399"
          strokeWidth={2.5}
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data point dots (subtle) */}
        {points.map((point, i) => (
          <circle key={i} cx={point.x} cy={point.y} r="2.5" fill="#34d399" opacity={0.9} />
        ))}
      </svg>
    </div>
  );
}

