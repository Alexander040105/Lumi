import { describe, it, expect } from "vitest";
import {
  matchProviders,
  normalizeTechnology,
  providerHasTechnology,
} from "./matchProviders";

const P = (over) => ({
  name: "Provider",
  region: "NCR",
  technology: "Solar",
  ...over,
});

const providers = [
  P({ name: "regionI-verified", region: "I", verified: true }),
  P({ name: "car-hydro", region: "CAR", technology: "Hydro", verified: true }),
  P({ name: "ncr-wind", technology: "Wind", verified: true }),
  P({ name: "ncr-solar-verified", verified: true }),
  P({ name: "ncr-solar-legacy" }),
  P({ name: "viii-verified", region: "VIII", verified: true }),
  P({ name: "ncr-solarhydro", technology: "Solar / Hydro", verified: true }),
];

describe("normalizeTechnology", () => {
  it("maps Hydropower to Hydro", () => {
    expect(normalizeTechnology("Hydropower")).toBe("Hydro");
  });
  it("passes other sources through and handles null", () => {
    expect(normalizeTechnology("Solar")).toBe("Solar");
    expect(normalizeTechnology(null)).toBeNull();
    expect(normalizeTechnology(undefined)).toBeNull();
  });
});

describe("providerHasTechnology", () => {
  it("matches multi-technology providers for each token", () => {
    const p = P({ technology: "Solar / Hydro" });
    expect(providerHasTechnology(p, "Solar")).toBe(true);
    expect(providerHasTechnology(p, "Hydro")).toBe(true);
    expect(providerHasTechnology(p, "Wind")).toBe(false);
  });
  it("treats a missing technology as Solar", () => {
    const legacy = P({ technology: undefined });
    expect(providerHasTechnology(legacy, "Solar")).toBe(true);
    expect(providerHasTechnology(legacy, "Wind")).toBe(false);
  });
  it("matches everything when technology is null", () => {
    expect(providerHasTechnology(P({ technology: "Wind" }), null)).toBe(true);
  });
});

describe("matchProviders", () => {
  it("filters by region", () => {
    const { matched } = matchProviders({ providers, region: "I", technology: "Solar" });
    expect(matched).toHaveLength(1);
    expect(matched[0].name).toBe("regionI-verified");
  });

  it("orders same-technology first, verified before unverified", () => {
    const { matched } = matchProviders({ providers, region: "NCR", technology: "Solar" });
    expect(matched.map((p) => p.name)).toEqual([
      "ncr-solar-verified",
      "ncr-solarhydro",
      "ncr-solar-legacy",
      "ncr-wind",
    ]);
  });

  it("orders hydro-capable providers first for a Hydro recommendation", () => {
    const { matched } = matchProviders({ providers, region: "NCR", technology: "Hydropower" });
    expect(matched[0].name).toBe("ncr-solarhydro");
  });

  it("returns up to 3 verified fallback providers across distinct regions", () => {
    const { matched, fallback } = matchProviders({ providers, region: "V", technology: "Solar" });
    expect(matched).toHaveLength(0);
    expect(fallback).toHaveLength(3);
    expect(fallback.every((p) => p.verified)).toBe(true);
    expect(new Set(fallback.map((p) => p.region)).size).toBe(3);
  });

  it("prefers same-technology providers in the fallback", () => {
    const { fallback } = matchProviders({ providers, region: "V", technology: "Hydropower" });
    expect(fallback[0].name).toBe("car-hydro");
    expect(fallback[1].name).toBe("ncr-solarhydro");
  });

  it("does not mutate the input array", () => {
    const input = [...providers];
    matchProviders({ providers: input, region: "NCR", technology: "Solar" });
    expect(input).toEqual(providers);
  });

  it("returns empty fallback when no verified providers exist", () => {
    const legacy = [P({ name: "old", region: "IX" })];
    const { matched, fallback } = matchProviders({ providers: legacy, region: "V", technology: "Solar" });
    expect(matched).toHaveLength(0);
    expect(fallback).toHaveLength(0);
  });
});

describe("matchProviders — category and nationwide", () => {
  const R = (over) => ({
    name: "Retailer",
    category: "retailer",
    region: null,
    technology: "Solar",
    ...over,
  });

  const mixed = [
    P({ name: "ncr-provider", verified: true }),
    R({ name: "nationwide-shop", nationwide: true }),
    R({ name: "ncr-retailer", region: "NCR" }),
    R({ name: "nationwide-wind-shop", nationwide: true, technology: "Wind" }),
    R({ name: "iii-retailer", region: "III" }),
  ];

  it("filters by category, treating missing category as provider", () => {
    const prov = matchProviders({ providers: mixed, region: "NCR", technology: "Solar", category: "provider" });
    expect(prov.matched.map((p) => p.name)).toEqual(["ncr-provider"]);

    const ret = matchProviders({ providers: mixed, region: "NCR", technology: "Solar", category: "retailer" });
    expect(ret.matched.every((p) => p.category === "retailer")).toBe(true);
  });

  it("appends nationwide retailers after regional matches", () => {
    const { matched } = matchProviders({ providers: mixed, region: "NCR", technology: "Solar", category: "retailer" });
    expect(matched.map((p) => p.name)).toEqual([
      "ncr-retailer",
      "nationwide-shop",
      "nationwide-wind-shop",
    ]);
  });

  it("counts a nationwide retailer with a matching region as regional", () => {
    const list = [
      R({ name: "local-plus-nationwide", region: "NCR", nationwide: true }),
      R({ name: "pure-nationwide", nationwide: true }),
    ];
    const { matched } = matchProviders({ providers: list, region: "NCR", technology: "Solar", category: "retailer" });
    expect(matched[0].name).toBe("local-plus-nationwide");
  });

  it("shows only nationwide retailers when the region has none", () => {
    const { matched, fallback } = matchProviders({ providers: mixed, region: "V", technology: "Solar", category: "retailer" });
    expect(matched.map((p) => p.name)).toEqual(["nationwide-shop", "nationwide-wind-shop"]);
    expect(fallback).toHaveLength(0);
  });

  it("excludes retailers from the verified provider fallback", () => {
    const list = [R({ name: "verified-retailer", nationwide: false, verified: true })];
    const { matched, fallback } = matchProviders({ providers: list, region: "V", technology: "Solar", category: "provider" });
    expect(matched).toHaveLength(0);
    expect(fallback).toHaveLength(0);
  });

  it("returns everything when category is undefined or 'all'", () => {
    const { matched } = matchProviders({ providers: mixed, region: "NCR", technology: "Solar" });
    expect(matched.map((p) => p.name)).toContain("ncr-provider");
    expect(matched.map((p) => p.name)).toContain("ncr-retailer");
  });
});
