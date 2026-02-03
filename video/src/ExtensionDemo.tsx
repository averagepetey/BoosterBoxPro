import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  spring,
  Img,
  staticFile,
} from "remotion";
import { BrowserFrame } from "./components/BrowserFrame";
import { ExtensionPanel } from "./components/ExtensionPanel";
import { Callout } from "./components/Callout";
import { EndCard } from "./components/EndCard";

export const ExtensionDemo: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Global fade out at end for seamless loop
  const fadeOut = interpolate(frame, [180, 210], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Fast scroll down the TCGplayer page: frames 0-25
  const scrollY = interpolate(frame, [0, 25], [0, -200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.quad),
  });

  // Zoom + pan to focus on extension panel once it's in
  // Starts at frame 55 (as panel info starts populating), settles by frame 100
  const zoomProgress = spring({
    frame: frame - 55,
    fps,
    config: { damping: 200 },
  });

  // Scale up to 1.5x, zooming from the right side of the frame
  // so the panel on the left stays fully visible
  const scale = interpolate(zoomProgress, [0, 1], [1, 1.5]);
  // Nudge right so the panel's left edge isn't clipped
  const panX = interpolate(zoomProgress, [0, 1], [0, 32]);

  // Blur the TCGplayer screenshot as zoom kicks in
  const bgBlur = interpolate(zoomProgress, [0, 1], [0, 4]);

  return (
    <AbsoluteFill className="bg-black" style={{ overflow: "hidden" }}>
      {/* Slight padding around browser frame for premium look */}
      <div
        style={{
          opacity: fadeOut,
          transform: `translateX(${panX}px) scale(${scale})`,
          transformOrigin: "0% 20%",
        }}
        className="absolute inset-[32px]"
      >
        <BrowserFrame>
          {/* TCGplayer page screenshot - scrolls down then holds */}
          <div
            style={{ transform: `translateY(${scrollY}px)` }}
            className="absolute top-0 left-0 w-full"
          >
            <Img
              src={staticFile("tcgplayer-op13.png")}
              style={{
                width: "100%",
                display: "block",
                filter: `blur(${bgBlur}px)`,
              }}
            />
          </div>

          {/* Extension panel overlay */}
          <ExtensionPanel />

          {/* Callout labels */}
          <Callout
            text="Real-time floor price"
            top={145}
            left={335}
            delay={65}
            arrowDirection="left"
          />
          <Callout
            text="Track daily supply and demand"
            top={260}
            left={335}
            delay={85}
            arrowDirection="left"
          />
          <Callout
            text="Live top-10 card value tracking"
            top={380}
            left={335}
            delay={92}
            arrowDirection="left"
          />
        </BrowserFrame>
      </div>
      {/* End card appears after main content fades out */}
      <EndCard />
    </AbsoluteFill>
  );
};
