/**
 * Client-side cleanup for LLM-generated insight text.
 *
 * The backend already guarantees output ends at a complete sentence
 * (see fastapi-backend/app/services/llm_sanitizer.py). This helper only
 * normalises presentation quirks (greetings, duplicated recommendation
 * numbering, excess blank lines). It must NOT truncate — cutting text here
 * is what made AI panels appear to end mid-sentence.
 */
export function sanitizeLLMOutput(text = "") {
  if (!text) return "";
  let t = text;

  // Remove repetitive greeting lines that appear in every panel
  t = t.replace(/Hello there! I'm LUMI, your friendly energy advisor\.\s*Let's chat about.*?\n*/is, "");
  t = t.replace(/Hi there! I'm LUMI.*?\n*/is, "");

  // Normalize repeated "Recommendation 1:" blocks into a single numbered list
  // When the LLM restarts numbering mid-text, renumber them sequentially
  const recBlocks = [];
  const recRegex = /\*?\s*\*\*?\s*Recommendation\s*(\d+)[:\.*\-]*\s*\*?\*?\s*(.*?)(?=\*?\s*\*\*?\s*Recommendation\s*\d+[:\.*\-]*|$)/gis;
  let m;
  while ((m = recRegex.exec(t)) !== null) {
    recBlocks.push(m[2].trim());
  }
  if (recBlocks.length > 0) {
    const numbered = recBlocks.map((b, i) => `${i + 1}. ${b.replace(/\n+/g, " ")}`).join("\n");
    t = t.replace(/\*?\s*\*\*?\s*Recommendation\s*\d+[:\.*\-]*\s*\*?\*?\s*.*/gis, "").trim();
    t = t + "\n\nRecommendations:\n" + numbered;
  }

  // Collapse multiple blank lines into one
  t = t.replace(/\n{3,}/g, "\n\n");

  return t.trim();
}
