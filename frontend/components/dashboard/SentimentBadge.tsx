'use client';

interface SentimentBadgeProps {
  sentiment: 'BULLISH' | 'BEARISH' | 'NEUTRAL' | null;
}

const CONFIG = {
  BULLISH: { bg: 'bg-green-500/15', border: 'border-green-500/30', text: 'text-green-400' },
  BEARISH: { bg: 'bg-red-500/15', border: 'border-red-500/30', text: 'text-red-400' },
  NEUTRAL: { bg: 'bg-yellow-500/15', border: 'border-yellow-500/30', text: 'text-yellow-400' },
};

export function SentimentBadge({ sentiment }: SentimentBadgeProps) {
  const key = sentiment || 'NEUTRAL';
  const { bg, border, text } = CONFIG[key];

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${bg} ${border} ${text}`}>
      {key}
    </span>
  );
}
