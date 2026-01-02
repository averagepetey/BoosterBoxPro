/**
 * Price Chart Component
 * Simple SVG-based line chart for price trends
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

export function PriceChart({ data, height = 256 }: PriceChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(600);

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        // Get the actual width of the container, accounting for any padding
        const rect = containerRef.current.getBoundingClientRect();
        setChartWidth(Math.max(rect.width, 600));
      }
    };

    // Use ResizeObserver for more accurate width tracking
    if (containerRef.current) {
      const resizeObserver = new ResizeObserver(() => {
        updateWidth();
      });
      resizeObserver.observe(containerRef.current);
      
      // Initial update with a small delay to ensure DOM is ready
      const timeoutId = setTimeout(updateWidth, 100);
      
      return () => {
        clearTimeout(timeoutId);
        resizeObserver.disconnect();
      };
    }
    
    // Fallback to window resize if ResizeObserver not available
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

  // Calculate chart dimensions
  const padding = { top: 20, right: 20, bottom: 40, left: 50 };
  const chartHeight = height;
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  // Find min/max values for scaling
  const prices = data.map(d => d.floor_price_usd);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  const priceRange = maxPrice - minPrice || 1; // Avoid division by zero

  // Create points for the line
  const points = data.map((d, i) => {
    const x = padding.left + (i / (data.length - 1 || 1)) * innerWidth;
    const y = padding.top + innerHeight - ((d.floor_price_usd - minPrice) / priceRange) * innerHeight;
    return { x, y, price: d.floor_price_usd, date: d.date };
  });

  // Create path string for the line
  const pathData = points
    .map((point, i) => `${i === 0 ? 'M' : 'L'} ${point.x} ${point.y}`)
    .join(' ');

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Format currency
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <div ref={containerRef} className="w-full h-full min-w-0">
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        preserveAspectRatio="none"
        className="w-full h-full"
        style={{ minWidth: 0 }}
      >
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const y = padding.top + innerHeight - ratio * innerHeight;
          const value = minPrice + ratio * priceRange;
          return (
            <g key={ratio}>
              <line
                x1={padding.left}
                y1={y}
                x2={padding.left + innerWidth}
                y2={y}
                stroke="rgba(255, 255, 255, 0.05)"
                strokeWidth="1"
              />
              <text
                x={padding.left - 10}
                y={y + 4}
                textAnchor="end"
                fill="rgba(255, 255, 255, 0.5)"
                fontSize="10"
              >
                {formatCurrency(value)}
              </text>
            </g>
          );
        })}

        {/* X-axis labels (show first, middle, last) */}
        {data.length > 0 && (
          <>
            <text
              x={padding.left}
              y={chartHeight - 5}
              fill="rgba(255, 255, 255, 0.5)"
              fontSize="10"
            >
              {formatDate(data[0].date)}
            </text>
            {data.length > 1 && (
              <text
                x={padding.left + innerWidth / 2}
                y={chartHeight - 5}
                textAnchor="middle"
                fill="rgba(255, 255, 255, 0.5)"
                fontSize="10"
              >
                {formatDate(data[Math.floor(data.length / 2)].date)}
              </text>
            )}
            {data.length > 2 && (
              <text
                x={padding.left + innerWidth}
                y={chartHeight - 5}
                textAnchor="end"
                fill="rgba(255, 255, 255, 0.5)"
                fontSize="10"
              >
                {formatDate(data[data.length - 1].date)}
              </text>
            )}
          </>
        )}

        {/* Price line */}
        <path
          d={pathData}
          fill="none"
          stroke="#10b981"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {points.map((point, i) => (
          <circle
            key={i}
            cx={point.x}
            cy={point.y}
            r="3"
            fill="#10b981"
            className="hover:r-4 transition-all"
          />
        ))}

        {/* Gradient fill under line */}
        <defs>
          <linearGradient id="priceGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path
          d={`${pathData} L ${points[points.length - 1].x} ${padding.top + innerHeight} L ${points[0].x} ${padding.top + innerHeight} Z`}
          fill="url(#priceGradient)"
        />
      </svg>
    </div>
  );
}

