import React from "react";
import { Sequence, AbsoluteFill } from "remotion";
import { SceneCard } from "../components/SceneCard";
import { FPS } from "../Root";

/**
 * LUMI 10-minute demonstration — segment skeleton matching
 * video/prompts/DEMO_PROMPT.md. Each Sequence is one demo segment;
 * replace SceneCard with the recorded screen capture (<Video src={staticFile(...)} />)
 * plus overlays/captions. If no admin account exists, fold its 30 s into EnergyHub.
 */
const SEGMENTS: Array<{ from: number; dur: number; kicker: string; title: string; note?: string }> = [
  { from: 0, dur: 20, kicker: "Intro", title: "LUMI — full system demonstration", note: "Title card: logo, product name, what this video covers." },
  { from: 20, dur: 50, kicker: "Getting in", title: "Sign up, log in, land on the dashboard", note: "Auth: email + Google, first-run state." },
  { from: 70, dur: 60, kicker: "Dashboard", title: "Your energy workspace", note: "Profile, quick actions, what a signed-in user sees." },
  { from: 130, dur: 150, kicker: "EcoSim", title: "Simulate renewables for your municipality", note: "The hero flow: municipality → inputs → results → AI analysis → save." },
  { from: 280, dur: 150, kicker: "EnergyHub", title: "National energy analytics", note: "Trends, source breakdown, forecasts, AI insight." },
  { from: 430, dur: 50, kicker: "Geospatial", title: "Maps: suitability across the country", note: "Layered maps inside EnergyHub." },
  { from: 480, dur: 60, kicker: "Saved work", title: "Saved simulations & security", note: "Re-open a saved sim; security settings + MFA." },
  { from: 540, dur: 30, kicker: "Admin", title: "For administrators", note: "Admin pages if an admin account exists — else fold into EnergyHub." },
  { from: 570, dur: 30, kicker: "Wrap", title: "Every estimate, grounded in data", note: "Recap card + closing tagline." },
];

export const LumiDemo: React.FC = () => {
  return (
    <AbsoluteFill>
      {SEGMENTS.map((s) => (
        <Sequence key={s.kicker} from={s.from * FPS} durationInFrames={s.dur * FPS}>
          <SceneCard kicker={s.kicker} title={s.title} note={s.note} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
