/**
 * Rank History Chart Component
 * Simple SVG-based line chart for rank over time
 */

'use client';

import { useRef, useEffect, useState } from 'react';

interface RankHistoryChartProps {
  data: Array<{
    date: string;
    rank: number;
  }>;
  height?: number;
}

export function RankHistoryChart({ data, height = 200 }: RankHistoryChartProps) {
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
      const resizeObserver = new ResizeObserver(() => {
        updateWidth();
      });
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
      <div className="h-48 flex items-center justify-center">
        <p className="text-white/50 text-sm">No rank history available</p>
      </div>
    );
  }

  // Calculate chart dimensions
  const padding = { top: 20, right: 20, bottom: 40, left: 40 };
  const chartHeight = height;
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  // Find min/max rank (lower rank = better, so we invert for display)
  const ranks = data.map(d => d.rank);
  const minRank = Math.min(...ranks);
  const maxRank = Math.max(...ranks);
  const rankRange = maxRank - minRank || 1;

  // Create points for the line (inverted so rank 1 is at top)
  const points = data.map((d, i) => {
    const x = padding.left + (i / (data.length - 1 || 1)) * innerWidth;
    // Invert: lower rank (better) = higher on chart
    const y = padding.top + ((d.rank - minRank) / rankRange) * innerHeight;
    return { x, y, rank: d.rank, date: d.date };
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
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
          const y = padding.top + ratio * innerHeight;
          const rank = Math.round(minRank + ratio * rankRange);
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
                #{rank}
              </text>
            </g>
          );
        })}

        {/* X-axis labels */}
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

        {/* Rank line */}
        <path
          d={pathData}
          fill="none"
          stroke="#f6c35a"
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
            fill="#f6c35a"
            className="hover:r-4 transition-all"
          />
        ))}
      </svg>
    </div>
  );
}

