import React from "react";
import { Composition } from "remotion";
import { LumiPromo } from "./compositions/LumiPromo";
import { LumiDemo } from "./compositions/LumiDemo";

export const FPS = 30;
export const WIDTH = 1920;
export const HEIGHT = 1080;

export const Root: React.FC = () => {
  return (
    <>
      {/* Marketing promo — target ~2:00 (max 5:00 per brief) */}
      <Composition
        id="LumiPromo"
        component={LumiPromo}
        durationInFrames={150 * FPS}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
      {/* 10-minute demonstration */}
      <Composition
        id="LumiDemo"
        component={LumiDemo}
        durationInFrames={600 * FPS}
        fps={FPS}
        width={WIDTH}
        height={HEIGHT}
      />
    </>
  );
};
