/**
 * Simplify Philippine GeoJSON by truncating coordinate precision.
 * 3 decimal places ≈ 100m accuracy — visually identical for national choropleth.
 */
const fs = require("fs");
const path = require("path");

const DECIMALS = 3;

function roundCoord(coord) {
  if (typeof coord === "number") {
    return Math.round(coord * 10 ** DECIMALS) / 10 ** DECIMALS;
  }
  return coord;
}

function simplifyGeometry(geometry) {
  if (!geometry) return geometry;
  const { type, coordinates } = geometry;

  if (type === "Point") {
    return { type, coordinates: coordinates.map(roundCoord) };
  }
  if (type === "MultiPoint" || type === "LineString") {
    return { type, coordinates: coordinates.map((c) => c.map(roundCoord)) };
  }
  if (type === "MultiLineString" || type === "Polygon") {
    return {
      type,
      coordinates: coordinates.map((ring) => ring.map((c) => c.map(roundCoord))),
    };
  }
  if (type === "MultiPolygon") {
    return {
      type,
      coordinates: coordinates.map((poly) =>
        poly.map((ring) => ring.map((c) => c.map(roundCoord)))
      ),
    };
  }
  return geometry;
}

function simplifyFeature(feature) {
  return {
    ...feature,
    geometry: simplifyGeometry(feature.geometry),
  };
}

function simplifyGeoJSON(geojson) {
  return {
    ...geojson,
    features: geojson.features.map(simplifyFeature),
  };
}

const INPUT = path.resolve(__dirname, "../react-frontend/public/philippine_geojson_file_per_provinces.json");
const OUTPUT = path.resolve(__dirname, "../react-frontend/public/philippine_geojson_file_per_provinces.min.json");

const raw = fs.readFileSync(INPUT, "utf8");
const geojson = JSON.parse(raw);
const simplified = simplifyGeoJSON(geojson);

fs.writeFileSync(OUTPUT, JSON.stringify(simplified), "utf8");

const beforeMB = (raw.length / 1024 / 1024).toFixed(2);
const afterMB = (JSON.stringify(simplified).length / 1024 / 1024).toFixed(2);
console.log(`Simplified GeoJSON: ${beforeMB} MB → ${afterMB} MB`);
console.log(`Features: ${geojson.features.length}`);
console.log(`Written to: ${OUTPUT}`);
