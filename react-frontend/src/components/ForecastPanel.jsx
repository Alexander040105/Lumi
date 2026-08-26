import { useState, useEffect } from "react";
import { runForecast, runBacktest, getModelRuns } from "../services/apiClient";

export default function ForecastPanel() {
  const [metric, setMetric] = useState("consumption");
  const [forecast, setForecast] = useState(null);
  const [backtest, setBacktest] = useState(null);
  const [modelRuns, setModelRuns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("forecast");

  useEffect(() => {
    getModelRuns(10).then(setModelRuns).catch(() => {});
  }, []);

  async function handleRunForecast() {
    setLoading(true);
    setError(null);
    try {
      const result = await runForecast(metric);
      setForecast(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleRunBacktest() {
    setLoading(true);
    setError(null);
    try {
      const result = await runBacktest(metric);
      setBacktest(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="bg-card rounded-xl shadow-sm border border-border p-6">
      <h2 className="text-xl font-bold text-foreground mb-4">Energy Forecasting</h2>

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab("forecast")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            activeTab === "forecast" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
          }`}
        >
          Forecast
        </button>
        <button
          onClick={() => setActiveTab("backtest")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            activeTab === "backtest" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
          }`}
        >
          Backtest
        </button>
        <button
          onClick={() => setActiveTab("models")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            activeTab === "models" ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
          }`}
        >
          Model Registry
        </button>
      </div>

      <div className="flex items-center gap-3 mb-4">
        <select
          value={metric}
          onChange={(e) => setMetric(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
        >
          <option value="consumption">Total Consumption (GWh)</option>
          <option value="peak_demand">Peak Demand (MW)</option>
        </select>
        <button
          onClick={activeTab === "backtest" ? handleRunBacktest : handleRunForecast}
          disabled={loading}
          className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50"
        >
          {loading ? "Running..." : activeTab === "backtest" ? "Run Backtest" : "Run Forecast"}
        </button>
      </div>

      {error && (
        <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-3 text-sm text-destructive mb-4">
          {error}
        </div>
      )}

      {activeTab === "forecast" && forecast && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {forecast.forecast_years?.map((year, i) => (
              <div key={year} className="bg-muted rounded-lg p-3">
                <div className="text-xs text-muted-foreground">{year}</div>
                <div className="text-lg font-bold text-foreground">
                  {forecast.forecast_values?.[i]?.toLocaleString() ?? "—"}
                </div>
                <div className="text-xs text-muted-foreground">
                  CI: {forecast.ci_lower?.[i]?.toLocaleString() ?? "—"} – {forecast.ci_upper?.[i]?.toLocaleString() ?? "—"}
                </div>
              </div>
            ))}
          </div>
          {forecast.metrics && (
            <div className="bg-muted rounded-lg p-3">
              <div className="text-sm font-medium text-foreground mb-1">Backtest Metrics</div>
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div>MAE: {forecast.metrics.mae}</div>
                <div>RMSE: {forecast.metrics.rmse}</div>
                <div>MAPE: {forecast.metrics.mape}%</div>
                <div>sMAPE: {forecast.metrics.smape}%</div>
              </div>
            </div>
          )}
          <div className="text-xs text-muted-foreground">
            Model: {forecast.model} | Training: {forecast.training_period} | Test: {forecast.test_period}
          </div>
        </div>
      )}

      {activeTab === "backtest" && backtest && (
        <div className="space-y-4">
          <div className="bg-muted rounded-lg p-4">
            <div className="text-sm font-medium text-foreground mb-2">
              {backtest.model_name} — {backtest.train_period} → {backtest.test_period}
            </div>
            <div className="grid grid-cols-4 gap-2 text-sm">
              <div><span className="text-muted-foreground">MAE:</span> {backtest.metrics?.mae}</div>
              <div><span className="text-muted-foreground">RMSE:</span> {backtest.metrics?.rmse}</div>
              <div><span className="text-muted-foreground">MAPE:</span> {backtest.metrics?.mape}%</div>
              <div><span className="text-muted-foreground">sMAPE:</span> {backtest.metrics?.smape}%</div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 px-3">Actual</th>
                  <th className="text-left py-2 px-3">Predicted</th>
                  <th className="text-left py-2 px-3">Residual</th>
                </tr>
              </thead>
              <tbody>
                {backtest.actual_values?.map((actual, i) => (
                  <tr key={i} className="border-b border-border">
                    <td className="py-2 px-3">{actual.toLocaleString()}</td>
                    <td className="py-2 px-3">{backtest.predicted_values?.[i]?.toLocaleString()}</td>
                    <td className="py-2 px-3">{backtest.residuals?.[i]?.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === "models" && (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-border">
                <th className="text-left py-2 px-3">Type</th>
                <th className="text-left py-2 px-3">Target</th>
                <th className="text-left py-2 px-3">Status</th>
                <th className="text-left py-2 px-3">MAPE</th>
                <th className="text-left py-2 px-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {modelRuns.map((run) => (
                <tr key={run.id} className="border-b border-border">
                  <td className="py-2 px-3">{run.run_type}</td>
                  <td className="py-2 px-3">{run.target_variable}</td>
                  <td className="py-2 px-3">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs ${
                      run.status === "success" ? "bg-primary/10 text-primary" : "bg-destructive/10 text-destructive"
                    }`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    {run.metrics ? JSON.parse(run.metrics).mape : "—"}
                  </td>
                  <td className="py-2 px-3 text-muted-foreground">
                    {new Date(run.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {modelRuns.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-4 text-center text-muted-foreground">No model runs yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
