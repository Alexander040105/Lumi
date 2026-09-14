/**
 * Lazy-loads pdfmake and configures the fonts. Using a CDN avoids Vite/VFS
 * build issues and keeps the initial bundle small.
 */

const CDN_FONTS = {
  Roboto: {
    normal:
      "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-Regular.ttf",
    bold:
      "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-Medium.ttf",
    italics:
      "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-Italic.ttf",
    bolditalics:
      "https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.66/fonts/Roboto/Roboto-MediumItalic.ttf",
  },
};

let pdfMakePromise = null;

export async function getPdfMake() {
  if (!pdfMakePromise) {
    pdfMakePromise = import("pdfmake/build/pdfmake").then((mod) => {
      const pdfMake = mod.default || mod;
      if (pdfMake && typeof pdfMake.createPdf === "function") {
        pdfMake.fonts = { ...(pdfMake.fonts || {}), ...CDN_FONTS };
        return pdfMake;
      }
      // Fallback for UMD builds that expose a global instead of a default export.
      if (typeof window !== "undefined" && window.pdfMake) {
        window.pdfMake.fonts = { ...(window.pdfMake.fonts || {}), ...CDN_FONTS };
        return window.pdfMake;
      }
      throw new Error("Unable to load pdfmake");
    });
  }
  return pdfMakePromise;
}
