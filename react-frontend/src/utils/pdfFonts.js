/**
 * Lazy-loads pdfmake and registers the bundled Roboto fontContainer. The TTFs
 * ship inside pdfmake as base64 and are written into the virtual file system
 * at runtime — no network fetch, so nothing can be blocked by CSP.
 */

let pdfMakePromise = null;

export async function getPdfMake() {
  if (!pdfMakePromise) {
    pdfMakePromise = Promise.all([
      import("pdfmake/build/pdfmake"),
      import("pdfmake/build/fonts/Roboto.js"),
    ]).then(([pdfMakeMod, robotoMod]) => {
      const pdfMake = pdfMakeMod.default || pdfMakeMod;
      const roboto = robotoMod.default || robotoMod;
      if (pdfMake && typeof pdfMake.createPdf === "function") {
        pdfMake.addFontContainer(roboto);
        return pdfMake;
      }
      // Fallback for UMD builds that expose a global instead of a default export.
      if (typeof window !== "undefined" && window.pdfMake) {
        window.pdfMake.addFontContainer(roboto);
        return window.pdfMake;
      }
      throw new Error("Unable to load pdfmake");
    });
  }
  return pdfMakePromise;
}
