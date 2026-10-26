import React from "react";
import { Sequence, AbsoluteFill, Audio } from "remotion";
import { SceneCard } from "../components/SceneCard";
import { FPS } from "../Root";

/**
 * LUMI marketing promo — scene skeleton matching video/prompts/PROMO_PROMPT.md.
 * Replace SceneCard internals with real scenes (UI captures, registry blocks,
 * kinetic type); keep the timing unless the brief changes.
 * Narration: generate assets/voice/*.wav per scene (see voiceover/ENGINE_NOTES.md),
 * then add <Audio src={staticFile('voice/NN.wav')} /> inside each Sequence.
 */
const SCENES: Array<{
  from: number; // seconds
  dur: number;
  kicker: string;
  title: string;
  note?: string;
  gold?: boolean;
}> = [
  { from: 0, dur: 10, kicker: "Opening", title: "What would solar actually save your household?", note: "Hook: one question, no answer yet." },
  { from: 10, dur: 15, kicker: "The problem", title: "Guessing is expensive.", note: "Problem + market need: scattered data, generic advice, no municipality-level answer." },
  { from: 25, dur: 15, kicker: "Meet LUMI", title: "Environmental intelligence for the Philippines.", note: "Product intro: logo + tagline + purpose." },
  { from: 40, dur: 15, kicker: "Why it is different", title: "Your municipality. Your data. Your estimate.", note: "USP: LGU-level, PH datasets, AI that explains plainly." },
  { from: 55, dur: 30, kicker: "What it does", title: "EcoSim · EnergyHub · AI insights", note: "Key features → benefits, not specs.", gold: true },
  { from: 85, dur: 25, kicker: "See it", title: "The product, working.", note: "Product preview: real UI captures from localhost.", gold: true },
  { from: 110, dur: 15, kicker: "Who it is for", title: "Homeowners · LGU planners · researchers", note: "Target market." },
  { from: 125, dur: 15, kicker: "What it saves", title: "Hours of research, answered in minutes.", note: "Value proposition — honest, hedged." },
  { from: 140, dur: 10, kicker: "Try it", title: "LUMI — power decisions, grounded in data.", note: "CTA + memorable tagline." },
];

export const LumiPromo: React.FC = () => {
  return (
    <AbsoluteFill>
      {SCENES.map((s) => (
        <Sequence key={s.kicker} from={s.from * FPS} durationInFrames={s.dur * FPS}>
          <SceneCard kicker={s.kicker} title={s.title} note={s.note} gold={s.gold} />
        </Sequence>
      ))}
      {/* Music bed: place assets/music/bed.mp3 then uncomment, ducked under narration
      <Audio src={staticFile('music/bed.mp3')} volume={0.15} /> */}
    </AbsoluteFill>
  );
};
