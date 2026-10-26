import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate } from "remotion";
import { brand } from "../brand";

/**
 * Placeholder scene card — swap the inside of each scene for real content
 * (UI footage, kinetic type, registry blocks). Kept so every scene renders
 * visibly before footage exists.
 */
export const SceneCard: React.FC<{
  kicker: string;
  title: string;
  note?: string;
  gold?: boolean;
}> = ({ kicker, title, note, gold }) => {
  const frame = useCurrentFrame();
  const ease = interpolate(frame, [0, 18], [0, 1], {
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill
      style={{
        background: `linear-gradient(160deg, ${brand.colors.paleMeadow} 0%, ${brand.colors.mist} 100%)`,
        fontFamily: brand.font,
        justifyContent: "center",
        alignItems: "center",
        padding: 120,
      }}
    >
      <div
        style={{
          opacity: ease,
          transform: `translateY(${(1 - ease) * 24}px)`,
          textAlign: "center",
        }}
      >
        <div
          style={{
            color: gold ? brand.colors.geothermalEmber : brand.colors.lumiGreen,
            fontSize: 26,
            fontWeight: 500,
            letterSpacing: "0.08em",
            textTransform: "uppercase",
            marginBottom: 24,
          }}
        >
          {kicker}
        </div>
        <div
          style={{
            color: brand.colors.forestInk,
            fontSize: 84,
            fontWeight: 800,
            letterSpacing: "-0.025em",
            lineHeight: 1.1,
            maxWidth: 1400,
          }}
        >
          {title}
        </div>
        {note ? (
          <div
            style={{
              color: brand.colors.forestDeep,
              fontSize: 30,
              lineHeight: 1.5,
              marginTop: 32,
              opacity: 0.75,
            }}
          >
            {note}
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};
