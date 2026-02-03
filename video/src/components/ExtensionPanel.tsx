import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Img,
  staticFile,
} from "remotion";

const PANEL_WIDTH = 320;

// Metric card component
const MetricCard: React.FC<{
  label: string;
  value: string;
  delay: number;
}> = ({ label, value, delay }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame - delay, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateY = interpolate(frame - delay, [0, 8], [8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{ opacity, transform: `translateY(${translateY}px)` }}
      className="bg-white/5 rounded-lg p-2.5"
    >
      <span className="block text-[10px] text-white/50 mb-1">{label}</span>
      <span className="block text-[13px] font-semibold text-white">
        {value}
      </span>
    </div>
  );
};

export const ExtensionPanel: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Panel slides in from left: starts at frame 30
  const slideProgress = spring({
    frame: frame - 30,
    fps,
    config: { damping: 20, stiffness: 200 },
  });

  const translateX = interpolate(slideProgress, [0, 1], [-PANEL_WIDTH, 0]);

  // Header content fades in: frames 45-55
  const headerOpacity = interpolate(frame, [45, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Key metrics fade in with tight stagger starting at frame 55
  const floorOpacity = interpolate(frame, [55, 63], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const floorTranslate = interpolate(frame, [55, 63], [12, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const volumeOpacity = interpolate(frame, [59, 67], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const volumeTranslate = interpolate(frame, [59, 67], [12, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const daysOpacity = interpolate(frame, [63, 71], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const daysTranslate = interpolate(frame, [63, 71], [12, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Tabs + section title: frame 72
  const tabsOpacity = interpolate(frame, [72, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // CTA button: frame 110
  const ctaOpacity = interpolate(frame, [110, 118], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const ctaTranslate = interpolate(frame, [110, 118], [8, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fade out at end: frames 330-360
  const fadeOut = interpolate(frame, [180, 210], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        width: PANEL_WIDTH,
        transform: `translateX(${translateX}px)`,
        opacity: fadeOut,
      }}
      className="absolute left-0 top-0 bg-[#141414] border-r border-white/15 z-10 flex flex-col rounded-r-2xl"
    >
      {/* Rounded right corners */}
      <div className="absolute inset-0 rounded-r-2xl overflow-hidden pointer-events-none border border-l-0 border-white/15" />

      {/* Header */}
      <div
        style={{ opacity: headerOpacity }}
        className="flex items-center justify-between px-4 py-3 shrink-0"
      >
        <div
          className="h-[44px] w-full flex items-center justify-between"
          style={{
            background:
              "linear-gradient(180deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.1) 100%)",
            borderBottom: "1px solid rgba(239, 68, 68, 0.2)",
            borderRadius: "0 12px 0 0",
            margin: "-12px -16px",
            padding: "0 16px",
          }}
        >
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded bg-red-500 flex items-center justify-center">
              <span className="text-[10px] font-bold text-white">B</span>
            </div>
            <span
              className="font-bold text-[15px]"
              style={{
                background: "linear-gradient(180deg, #ef4444 0%, #dc2626 100%)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              BoosterPro
            </span>
          </div>
          <div className="flex gap-1.5">
            {["\u25B6", "\u2212", "\u00D7"].map((icon, i) => (
              <div
                key={i}
                className="w-[26px] h-[26px] rounded-md bg-white/5 border border-white/10 flex items-center justify-center text-white/50 text-[14px]"
              >
                {icon}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 px-4 pt-2 pb-4 overflow-hidden">
        {/* Box header */}
        <div
          style={{ opacity: headerOpacity }}
          className="flex items-center gap-3 mb-3 pb-3 border-b border-white/10"
        >
          <Img
            src={staticFile("op-13.png")}
            style={{
              width: 56,
              height: 56,
              objectFit: "contain",
              borderRadius: 8,
              background: "rgba(255,255,255,0.05)",
            }}
          />
          <div className="text-[13px] font-semibold text-white leading-tight">
            One Piece TCG: Carrying On His Will [OP-13] Booster Box
          </div>
        </div>

        {/* Key metrics row */}
        <div className="grid grid-cols-3 mb-3 pb-3 border-b border-white/10 text-center">
          <div
            style={{
              opacity: floorOpacity,
              transform: `translateY(${floorTranslate}px)`,
            }}
            className="px-1 py-2 border-r border-white/10"
          >
            <div className="text-[9px] text-white/50 uppercase tracking-wide mb-0.5">
              Current Floor
            </div>
            <div className="text-[14px] font-bold text-white">$655</div>
            <div className="text-[10px] mt-0.5 text-green-400">+2.3% ▲</div>
          </div>
          <div
            style={{
              opacity: volumeOpacity,
              transform: `translateY(${volumeTranslate}px)`,
            }}
            className="px-1 py-2 border-r border-white/10"
          >
            <div className="text-[9px] text-white/50 uppercase tracking-wide mb-0.5">
              Volume (7d EMA)
            </div>
            <div className="text-[14px] font-bold text-white">$94.5K</div>
          </div>
          <div
            style={{
              opacity: daysOpacity,
              transform: `translateY(${daysTranslate}px)`,
            }}
            className="px-1 py-2"
          >
            <div className="text-[9px] text-white/50 uppercase tracking-wide mb-0.5">
              Days to +20%
            </div>
            <div className="text-[24px] font-bold text-white leading-none">
              1.4
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div
          style={{ opacity: tabsOpacity }}
          className="flex gap-1 mb-3 bg-white/[0.04] border border-white/[0.06] p-1 rounded-[10px]"
        >
          <div className="flex-1 py-2 px-3 rounded-[7px] text-center text-[12px] font-medium text-white bg-red-500/20 border border-red-500/30">
            Stats
          </div>
          <div className="flex-1 py-2 px-3 rounded-[7px] text-center text-[12px] font-medium text-white/45">
            Compare
          </div>
        </div>

        {/* Section title */}
        <div
          style={{ opacity: tabsOpacity }}
          className="text-[10px] font-semibold uppercase text-white/40 tracking-wide mb-2"
        >
          Metrics
        </div>

        {/* Stats grid - staggered fade in */}
        <div className="grid grid-cols-2 gap-2">
          <MetricCard label="Liquidity" value="High" delay={80} />
          <MetricCard label="Boxes Listed" value="47" delay={83} />
          <MetricCard label="Sold/Day" value="30" delay={86} />
          <MetricCard label="Time to Sale" value="0.87 days" delay={89} />
          <MetricCard label="Top 10 Value" value="$30.5K" delay={92} />
          <MetricCard label="Daily Vol" value="$12,345" delay={95} />
          <MetricCard label="Reprint Risk" value="Low" delay={98} />
          <MetricCard label="Listings Added" value="12/day" delay={101} />
        </div>

        {/* CTA button */}
        <div
          style={{
            opacity: ctaOpacity,
            transform: `translateY(${ctaTranslate}px)`,
          }}
          className="mt-4"
        >
          <div
            className="text-center py-3 rounded-[10px] text-[13px] font-semibold text-white"
            style={{
              background:
                "linear-gradient(135deg, #ef4444 0%, #dc2626 60%, #b91c1c 100%)",
              border: "1px solid rgba(255,255,255,0.1)",
              boxShadow: "0 4px 14px rgba(239,68,68,0.3)",
            }}
          >
            View full box detail →
          </div>
        </div>
      </div>
    </div>
  );
};
