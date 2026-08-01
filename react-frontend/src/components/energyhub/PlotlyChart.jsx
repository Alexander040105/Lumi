import Plot from "react-plotly.js";

const DEFAULT_LAYOUT = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: { color: "#334155", family: "Inter, sans-serif", size: 12 },
  margin: { t: 24, r: 16, b: 40, l: 48 },
  xaxis: { gridcolor: "#cbd5e1", zerolinecolor: "#cbd5e1" },
  yaxis: { gridcolor: "#cbd5e1", zerolinecolor: "#cbd5e1" },
  showlegend: true,
  legend: { orientation: "h", y: -0.2, x: 0.5, xanchor: "center", font: { color: "#334155" } },
  autosize: true,
};

const DEFAULT_CONFIG = {
  displayModeBar: false,
  responsive: true,
};

export default function PlotlyChart({ data, layout = {}, config = {}, className = "" }) {
  const mergedLayout = {
    ...DEFAULT_LAYOUT,
    ...layout,
    margin: { ...DEFAULT_LAYOUT.margin, ...layout.margin },
    font: { ...DEFAULT_LAYOUT.font, ...layout.font },
    xaxis: { ...DEFAULT_LAYOUT.xaxis, ...layout.xaxis },
    yaxis: { ...DEFAULT_LAYOUT.yaxis, ...layout.yaxis },
    legend: { ...DEFAULT_LAYOUT.legend, ...layout.legend },
  };

  return (
    <Plot
      data={data}
      layout={mergedLayout}
      config={{ ...DEFAULT_CONFIG, ...config }}
      style={{ width: "100%", height: "100%" }}
      useResizeHandler
      className={`w-full h-full ${className}`}
    />
  );
}
