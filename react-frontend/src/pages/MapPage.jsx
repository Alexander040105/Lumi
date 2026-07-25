import MapPanel from "../components/MapPanel";
import CoverageDashboard from "../components/CoverageDashboard";

export default function MapPage() {
  return (
    <section className="container mx-auto px-4 py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold">Renewable Energy Map</h1>
        <p className="text-muted-foreground">
          Explore suitability scores for solar, wind, hydro, and geothermal across the Philippines.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <MapPanel />
        </div>
        <div>
          <CoverageDashboard />
        </div>
      </div>
    </section>
  );
}
