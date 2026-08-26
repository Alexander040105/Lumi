import { useMemo } from "react";
import Plot from "react-plotly.js";

import { useTheme } from "@/hooks/useTheme";
import cssVarToHsl from "@/utils/cssVarToHsl";

const DEFAULT_LAYOUT = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  margin: { t: 24, r: 16, b: 40, l: 48 },
  showlegend: true,
  autosize: true,
};

const DEFAULT_CONFIG = {
  displayModeBar: false,
  responsive: true,
};

export default function PlotlyChart({ data, layout = {}, config = {}, className = "" }) {
  const { theme } = useTheme();

  const themeLayout = useMemo(() => {
    const foreground = cssVarToHsl("--foreground", "#334155");
    const border = cssVarToHsl("--border", "#cbd5e1");
    return {
      font: { color: foreground, family: "Inter, sans-serif", size: 12 },
      xaxis: {
        gridcolor: border,
        zerolinecolor: border,
        tickfont: { color: foreground },
      },
      yaxis: {
        gridcolor: border,
        zerolinecolor: border,
        tickfont: { color: foreground },
      },
      legend: {
        orientation: "h",
        y: -0.2,
        x: 0.5,
        xanchor: "center",
        font: { color: foreground },
      },
    };
  }, [theme]);

  const mergedLayout = {
    ...DEFAULT_LAYOUT,
    ...themeLayout,
    ...layout,
    margin: { ...DEFAULT_LAYOUT.margin, ...layout.margin },
    font: { ...themeLayout.font, ...layout.font },
    xaxis: { ...themeLayout.xaxis, ...layout.xaxis },
    yaxis: { ...themeLayout.yaxis, ...layout.yaxis },
    legend: {
      ...themeLayout.legend,
      ...(layout.legend || {}),
      font: {
        ...themeLayout.legend.font,
        ...(layout.legend?.font || {}),
      },
    },
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
