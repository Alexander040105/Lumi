export function resolveSourceAnalysis(result, key, fallback) {
  return (
    result?.ai_analysis?.renewable_analysis?.[key] ||
    result?.explanations?.[key] ||
    fallback
  );
}
