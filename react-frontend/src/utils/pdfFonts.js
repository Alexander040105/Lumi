/**
 * Lazy-loads pdfmake and configures the fonts. Fonts are self-hosted in
 * public/fonts/roboto/ and fetched same-origin — the production CSP only
 * allows connect-src 'self', so CDN font URLs would be blocked.
 */

const SELF_HOSTED_FONTS = {
  Roboto: {
    normal: "/fonts/roboto/Roboto-Regular.ttf",
    bold: "/fonts/roboto/Roboto-Medium.ttf",
    italics: "/fonts/roboto/Roboto-Italic.ttf",
    bolditalics: "/fonts/roboto/Roboto-MediumItalic.ttf",
  },
};

let pdfMakePromise = null;

export async function getPdfMake() {
  if (!pdfMakePromise) {
    pdfMakePromise = import("pdfmake/build/pdfmake").then((mod) => {
      const pdfMake = mod.default || mod;
      if (pdfMake && typeof pdfMake.createPdf === "function") {
        pdfMake.fonts = { ...(pdfMake.fonts || {}), ...SELF_HOSTED_FONTS };
        return pdfMake;
      }
      // Fallback for UMD builds that expose a global instead of a default export.
      if (typeof window !== "undefined" && window.pdfMake) {
        window.pdfMake.fonts = { ...(window.pdfMake.fonts || {}), ...SELF_HOSTED_FONTS };
        return window.pdfMake;
      }
      throw new Error("Unable to load pdfmake");
    });
  }
  return pdfMakePromise;
}
