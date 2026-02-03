import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

type CalloutProps = {
  text: string;
  top: number;
  left: number;
  delay: number;
  arrowDirection?: "left" | "right";
};

export const Callout: React.FC<CalloutProps> = ({
  text,
  top,
  left,
  delay,
  arrowDirection = "left",
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [delay, delay + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const translateX = interpolate(
    frame,
    [delay, delay + 15],
    [arrowDirection === "left" ? 10 : -10, 0],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }
  );

  // Fade out with panel
  const fadeOut = interpolate(frame, [180, 210], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <div
      style={{
        position: "absolute",
        top,
        left,
        opacity: opacity * fadeOut,
        transform: `translateX(${translateX}px)`,
        zIndex: 20,
      }}
    >
      <div className="flex items-center gap-4">
        {arrowDirection === "left" && (
          <svg width="24" height="16" viewBox="0 0 24 16" fill="none">
            <path d="M24 8L0 0v16l24-8z" fill="rgba(239,68,68,0.7)" />
          </svg>
        )}
        <div
          className="px-7 py-3.5 rounded-2xl text-[22px] font-semibold text-white tracking-wide"
          style={{
            background: "rgba(10,10,10,0.92)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(239,68,68,0.4)",
            boxShadow: "0 6px 20px rgba(0,0,0,0.5), 0 0 15px rgba(239,68,68,0.15)",
          }}
        >
          {text}
        </div>
        {arrowDirection === "right" && (
          <svg width="24" height="16" viewBox="0 0 24 16" fill="none">
            <path d="M0 8l24-8v16L0 8z" fill="rgba(239,68,68,0.7)" />
          </svg>
        )}
      </div>
    </div>
  );
};
