'use client';

import { useRef, useEffect, useState } from 'react';
import { MarketIndexPoint } from '@/lib/api/marketMacro';

interface MarketIndexChartProps {
  data: MarketIndexPoint[];
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

export function MarketIndexChart({ data, height = 200 }: MarketIndexChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = useState(600);

  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        setChartWidth(Math.max(rect.width, 300));
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

  const validData = data.filter(d => d.index_value !== null);
  if (validData.length === 0) {
    return (
      <div className="h-[200px] flex items-center justify-center">
        <p className="text-white/50 text-sm">No index data available</p>
      </div>
    );
  }

  const padding = { top: 20, right: 16, bottom: 36, left: 48 };
  const chartHeight = height;
  const innerWidth = chartWidth - padding.left - padding.right;
  const innerHeight = chartHeight - padding.top - padding.bottom;

  const values = validData.map(d => d.index_value!);
  const minVal = Math.min(...values);
  const maxVal = Math.max(...values);
  const valRange = maxVal - minVal || 1;
  const pad = valRange * 0.02;
  const scaleMin = minVal - pad;
  const scaleMax = maxVal + pad;
  const scaleRange = scaleMax - scaleMin || 1;

  const points = validData.map((d, i) => {
    const x = padding.left + (i / (validData.length - 1 || 1)) * innerWidth;
    const y = padding.top + innerHeight - ((d.index_value! - scaleMin) / scaleRange) * innerHeight;
    return { x, y, value: d.index_value!, date: d.date };
  });

  const linePath = smoothPath(points);
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${padding.top + innerHeight} L ${points[0].x} ${padding.top + innerHeight} Z`;

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const formatCurrency = (value: number) => `$${Math.round(value)}`;

  const gridSteps = 4;
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
          <linearGradient id="indexChartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#F6C35A" stopOpacity="0.3" />
            <stop offset="100%" stopColor="#F6C35A" stopOpacity="0" />
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
                x={padding.left - 6}
                y={y + 4}
                textAnchor="end"
                fill="rgba(255, 255, 255, 0.45)"
                fontSize="10"
                fontFamily="system-ui, sans-serif"
              >
                {formatCurrency(value)}
              </text>
            </g>
          );
        })}

        {/* X-axis labels */}
        {validData.length > 0 && (
          <>
            <text x={padding.left} y={chartHeight - 6} fill="rgba(255, 255, 255, 0.45)" fontSize="10" fontFamily="system-ui, sans-serif">
              {formatDate(validData[0].date)}
            </text>
            {validData.length > 2 && (
              <text x={padding.left + innerWidth / 2} y={chartHeight - 6} textAnchor="middle" fill="rgba(255, 255, 255, 0.45)" fontSize="10" fontFamily="system-ui, sans-serif">
                {formatDate(validData[Math.floor(validData.length / 2)].date)}
              </text>
            )}
            {validData.length > 1 && (
              <text x={padding.left + innerWidth} y={chartHeight - 6} textAnchor="end" fill="rgba(255, 255, 255, 0.45)" fontSize="10" fontFamily="system-ui, sans-serif">
                {formatDate(validData[validData.length - 1].date)}
              </text>
            )}
          </>
        )}

        {/* Area fill */}
        <path d={areaPath} fill="url(#indexChartGradient)" />

        {/* Smooth line - gold/amber */}
        <path
          d={linePath}
          fill="none"
          stroke="#F6C35A"
          strokeWidth={2}
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data point dots */}
        {points.length <= 60 && points.map((point, i) => (
          <circle key={i} cx={point.x} cy={point.y} r="2" fill="#F6C35A" opacity={0.8} />
        ))}
      </svg>
    </div>
  );
}
