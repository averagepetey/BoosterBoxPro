import React from "react";

export const BrowserFrame: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  return (
    <div className="flex flex-col w-full h-full bg-[#1a1a1a] rounded-2xl overflow-hidden border border-white/10">
      {/* Title bar */}
      <div className="flex items-center h-[48px] px-4 bg-[#2a2a2a] border-b border-white/10 shrink-0">
        {/* Traffic light dots */}
        <div className="flex gap-2 mr-4">
          <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
          <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
          <div className="w-3 h-3 rounded-full bg-[#28c840]" />
        </div>
        {/* URL bar */}
        <div className="flex-1 flex items-center h-[30px] bg-[#1a1a1a] rounded-lg px-4 border border-white/10">
          {/* Lock icon */}
          <svg
            width="12"
            height="12"
            viewBox="0 0 12 12"
            fill="none"
            className="mr-2 shrink-0"
          >
            <path
              d="M3.5 5V3.5a2.5 2.5 0 015 0V5"
              stroke="rgba(255,255,255,0.4)"
              strokeWidth="1.2"
              strokeLinecap="round"
            />
            <rect
              x="2.5"
              y="5"
              width="7"
              height="5.5"
              rx="1.5"
              fill="rgba(255,255,255,0.4)"
            />
          </svg>
          <span className="text-[13px] text-white/40 truncate">
            tcgplayer.com/product/one-piece-card-game-carrying-on-his-will-op-13-booster-box
          </span>
        </div>
        {/* Extension icon area */}
        <div className="flex items-center gap-2 ml-3">
          <div className="w-6 h-6 rounded bg-red-500/80 flex items-center justify-center">
            <span className="text-[8px] font-bold text-white">B</span>
          </div>
        </div>
      </div>
      {/* Content area */}
      <div className="flex-1 relative overflow-hidden">{children}</div>
    </div>
  );
};
