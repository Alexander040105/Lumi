import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig(({ mode }) => {
  // CARTO_API_KEY lives in the repo-root .env (shared with the backend) rather
  // than react-frontend/.env. loadEnv reads .env* files in the given dir plus
  // process.env, so this also picks up the var from Vercel project settings.
  const cartoApiKey =
    loadEnv(mode, fileURLToPath(new URL("..", import.meta.url)), "CARTO_")
      .CARTO_API_KEY ?? "";

  return {
    plugins: [react(), tailwindcss()],
    define: {
      "import.meta.env.CARTO_API_KEY": JSON.stringify(cartoApiKey),
    },
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url))
      }
    },
    server: {
      host: "127.0.0.1",
      port: 5173,
      proxy: {
        "/api": {
          target: "http://127.0.0.1:8000",
          changeOrigin: true,
        },
      },
    },
    build: {
      rollupOptions: {
        output: {
          // Heavy third-party libs split into named vendor chunks so the entry
          // bundle stays small; route-level React.lazy() then loads them on
          // demand. Function form because pdfmake/leaflet are pulled via
          // subpath specifiers (pdfmake/build/pdfmake, etc.).
          manualChunks(id) {
            if (!id.includes("node_modules")) return;
            if (id.includes("plotly")) return "plotly";
            if (id.includes("pdfmake")) return "pdfmake";
            if (id.includes("leaflet")) return "leaflet";
            if (id.includes("recharts")) return "recharts";
          },
        },
      },
    }
  };
});
