import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";

export const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // End card starts at frame 215 (after main content fades to black)
  const localFrame = frame - 215;

  // Overall visibility: fade in at 215, fade out at 340-360
  const fadeIn = interpolate(frame, [215, 225], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [340, 360], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Red accent line scales out from center
  const lineScale = spring({
    frame: localFrame,
    fps,
    config: { damping: 20, stiffness: 200 },
  });

  // Line 1: "Pops up & detects your box" — appears almost immediately
  const line1Spring = spring({
    frame: localFrame - 3,
    fps,
    config: { damping: 18, stiffness: 200 },
  });
  const line1Y = interpolate(line1Spring, [0, 1], [30, 0]);
  const line1Opacity = interpolate(line1Spring, [0, 1], [0, 1]);

  // Line 2: "automatically as you browse." — follows quickly
  const line2Spring = spring({
    frame: localFrame - 8,
    fps,
    config: { damping: 18, stiffness: 200 },
  });
  const line2Y = interpolate(line2Spring, [0, 1], [30, 0]);
  const line2Opacity = interpolate(line2Spring, [0, 1], [0, 1]);

  // Subtle glow pulse
  const glowPulse = interpolate(
    localFrame,
    [20, 60, 100],
    [0.3, 0.6, 0.3],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity: fadeIn * fadeOut,
      }}
    >
      {/* Radial glow behind text */}
      <div
        style={{
          position: "absolute",
          width: 800,
          height: 800,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(239,68,68,${glowPulse * 0.15}) 0%, rgba(239,68,68,0) 70%)`,
          pointerEvents: "none",
        }}
      />

      {/* Red accent line */}
      <div
        style={{
          width: 120,
          height: 3,
          borderRadius: 2,
          background:
            "linear-gradient(90deg, #ef4444 0%, #f97316 100%)",
          transform: `scaleX(${lineScale})`,
          marginBottom: 40,
          boxShadow: "0 0 20px rgba(239,68,68,0.5)",
        }}
      />

      {/* Line 1 */}
      <div
        style={{
          opacity: line1Opacity,
          transform: `translateY(${line1Y}px)`,
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontWeight: 800,
            color: "white",
            textAlign: "center",
            letterSpacing: "-1px",
            lineHeight: 1.1,
          }}
        >
          Pops up & detects your box
        </div>
      </div>

      {/* Line 2 — gradient accent */}
      <div
        style={{
          opacity: line2Opacity,
          transform: `translateY(${line2Y}px)`,
          marginTop: 8,
        }}
      >
        <div
          style={{
            fontSize: 64,
            fontWeight: 800,
            textAlign: "center",
            letterSpacing: "-1px",
            lineHeight: 1.1,
            background:
              "linear-gradient(135deg, #ef4444 0%, #f97316 50%, #fbbf24 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
          }}
        >
          automatically as you browse.
        </div>
      </div>

      {/* Small tagline below */}
      <div
        style={{
          opacity: interpolate(line2Spring, [0, 1], [0, 0.5]),
          transform: `translateY(${interpolate(line2Spring, [0, 1], [20, 0])}px)`,
          marginTop: 32,
          fontSize: 22,
          fontWeight: 500,
          color: "rgba(255,255,255,0.45)",
          letterSpacing: "3px",
          textTransform: "uppercase" as const,
        }}
      >
        Zero setup required
      </div>
    </div>
  );
};
