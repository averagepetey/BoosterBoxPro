/**
 * Leaderboard skeleton for loading state
 * Matches the table grid layout for a smooth perceived load
 */

'use client';

const ROWS = 12;

function SkeletonBar({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded bg-white/15 ${className}`}
      style={{ minHeight: '12px' }}
    />
  );
}

export function LeaderboardSkeleton() {
  return (
    <div className="space-y-0">
      {Array.from({ length: ROWS }).map((_, i) => (
        <div
          key={i}
          className="p-2 sm:p-4"
          style={{
            borderBottom: i < ROWS - 1 ? '1px solid rgba(255, 255, 255, 0.1)' : 'none',
          }}
        >
          <div className="grid grid-cols-12 gap-1 sm:gap-2 items-center">
            {/* Rank */}
            <div className="col-span-1 px-3">
              <SkeletonBar className="w-6 h-4" />
            </div>
            {/* Collection: image + name */}
            <div className="col-span-3 flex items-center gap-3 sm:gap-4 px-3">
              <div className="flex-shrink-0 w-12 h-12 sm:w-20 sm:h-20 rounded-lg bg-white/15 animate-pulse" />
              <div className="flex-1 min-w-0 space-y-2">
                <SkeletonBar className="h-4 w-full max-w-[140px]" />
                <SkeletonBar className="h-3 w-20" />
              </div>
            </div>
            {/* Floor */}
            <div className="col-span-1 text-right px-2">
              <SkeletonBar className="h-4 w-14 ml-auto" />
            </div>
            {/* Price change % */}
            <div className="col-span-1 flex justify-center px-2">
              <SkeletonBar className="h-4 w-12" />
            </div>
            {/* Volume */}
            <div className="col-span-2 text-right px-2">
              <SkeletonBar className="h-4 w-16 ml-auto" />
            </div>
            {/* Sales */}
            <div className="col-span-1 text-right px-3">
              <SkeletonBar className="h-4 w-8 ml-auto" />
            </div>
            {/* Top 10 Value */}
            <div className="col-span-2 flex justify-center px-3">
              <SkeletonBar className="h-4 w-14" />
            </div>
            {/* Days to 20% */}
            <div className="col-span-1 flex justify-center px-3">
              <SkeletonBar className="h-4 w-10" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
