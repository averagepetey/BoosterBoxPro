'use client';

interface FearGreedGaugeProps {
  value: number; // 0-100
  size?: number;
}

function getLabel(value: number): string {
  if (value <= 20) return 'Extreme Fear';
  if (value <= 40) return 'Fear';
  if (value <= 60) return 'Neutral';
  if (value <= 80) return 'Greed';
  return 'Extreme Greed';
}

function getColor(value: number): string {
  if (value <= 20) return '#ef4444'; // red
  if (value <= 40) return '#f97316'; // orange
  if (value <= 60) return '#eab308'; // yellow
  if (value <= 80) return '#84cc16'; // lime
  return '#22c55e'; // green
}

export function FearGreedGauge({ value, size = 120 }: FearGreedGaugeProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const label = getLabel(clamped);
  const color = getColor(clamped);

  // SVG semi-circle gauge
  const cx = size / 2;
  const cy = size * 0.55;
  const r = size * 0.4;
  const strokeWidth = size * 0.08;

  // Arc from 180deg (left) to 0deg (right)
  const startAngle = Math.PI; // 180 deg
  const endAngle = 0;
  const needleAngle = startAngle - (clamped / 100) * Math.PI;

  // Arc path for background
  const arcPath = describeArc(cx, cy, r, startAngle, endAngle);
  // Arc path for filled portion
  const filledPath = describeArc(cx, cy, r, startAngle, needleAngle);

  // Needle endpoint
  const needleLen = r - strokeWidth;
  const nx = cx + needleLen * Math.cos(needleAngle);
  const ny = cy - needleLen * Math.sin(needleAngle);

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.6} viewBox={`0 0 ${size} ${size * 0.6}`}>
        {/* Background arc */}
        <path
          d={arcPath}
          fill="none"
          stroke="rgba(255,255,255,0.1)"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Filled arc */}
        <path
          d={filledPath}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          style={{ filter: `drop-shadow(0 0 6px ${color}40)` }}
        />
        {/* Needle */}
        <line
          x1={cx}
          y1={cy}
          x2={nx}
          y2={ny}
          stroke="white"
          strokeWidth={2}
          strokeLinecap="round"
        />
        {/* Center dot */}
        <circle cx={cx} cy={cy} r={3} fill="white" />
      </svg>
      <div className="text-center -mt-1">
        <span className="text-lg font-bold" style={{ color }}>{Math.round(clamped)}</span>
        <span className="text-white/50 text-xs ml-1">/100</span>
      </div>
      <div className="text-xs font-medium" style={{ color }}>{label}</div>
    </div>
  );
}

function describeArc(cx: number, cy: number, r: number, startAngle: number, endAngle: number): string {
  const x1 = cx + r * Math.cos(startAngle);
  const y1 = cy - r * Math.sin(startAngle);
  const x2 = cx + r * Math.cos(endAngle);
  const y2 = cy - r * Math.sin(endAngle);
  const largeArc = Math.abs(startAngle - endAngle) > Math.PI ? 1 : 0;
  // Sweep flag: arc goes clockwise in SVG (which means decreasing angle)
  return `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}`;
}
