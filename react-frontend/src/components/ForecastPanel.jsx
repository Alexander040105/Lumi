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
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-xl font-bold text-gray-900 mb-4">Energy Forecasting</h2>

      <div className="flex gap-2 mb-4">
        <button
          onClick={() => setActiveTab("forecast")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            activeTab === "forecast" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"
          }`}
        >
          Forecast
        </button>
        <button
          onClick={() => setActiveTab("backtest")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            activeTab === "backtest" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"
          }`}
        >
          Backtest
        </button>
        <button
          onClick={() => setActiveTab("models")}
          className={`px-4 py-2 rounded-lg text-sm font-medium ${
            activeTab === "models" ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-700"
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
          className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Running..." : activeTab === "backtest" ? "Run Backtest" : "Run Forecast"}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {activeTab === "forecast" && forecast && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {forecast.forecast_years?.map((year, i) => (
              <div key={year} className="bg-gray-50 rounded-lg p-3">
                <div className="text-xs text-gray-500">{year}</div>
                <div className="text-lg font-bold text-gray-900">
                  {forecast.forecast_values?.[i]?.toLocaleString() ?? "—"}
                </div>
                <div className="text-xs text-gray-400">
                  CI: {forecast.ci_lower?.[i]?.toLocaleString() ?? "—"} – {forecast.ci_upper?.[i]?.toLocaleString() ?? "—"}
                </div>
              </div>
            ))}
          </div>
          {forecast.metrics && (
            <div className="bg-blue-50 rounded-lg p-3">
              <div className="text-sm font-medium text-blue-900 mb-1">Backtest Metrics</div>
              <div className="grid grid-cols-4 gap-2 text-xs">
                <div>MAE: {forecast.metrics.mae}</div>
                <div>RMSE: {forecast.metrics.rmse}</div>
                <div>MAPE: {forecast.metrics.mape}%</div>
                <div>sMAPE: {forecast.metrics.smape}%</div>
              </div>
            </div>
          )}
          <div className="text-xs text-gray-500">
            Model: {forecast.model} | Training: {forecast.training_period} | Test: {forecast.test_period}
          </div>
        </div>
      )}

      {activeTab === "backtest" && backtest && (
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm font-medium text-gray-900 mb-2">
              {backtest.model_name} — {backtest.train_period} → {backtest.test_period}
            </div>
            <div className="grid grid-cols-4 gap-2 text-sm">
              <div><span className="text-gray-500">MAE:</span> {backtest.metrics?.mae}</div>
              <div><span className="text-gray-500">RMSE:</span> {backtest.metrics?.rmse}</div>
              <div><span className="text-gray-500">MAPE:</span> {backtest.metrics?.mape}%</div>
              <div><span className="text-gray-500">sMAPE:</span> {backtest.metrics?.smape}%</div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3">Actual</th>
                  <th className="text-left py-2 px-3">Predicted</th>
                  <th className="text-left py-2 px-3">Residual</th>
                </tr>
              </thead>
              <tbody>
                {backtest.actual_values?.map((actual, i) => (
                  <tr key={i} className="border-b border-gray-100">
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
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 px-3">Type</th>
                <th className="text-left py-2 px-3">Target</th>
                <th className="text-left py-2 px-3">Status</th>
                <th className="text-left py-2 px-3">MAPE</th>
                <th className="text-left py-2 px-3">Date</th>
              </tr>
            </thead>
            <tbody>
              {modelRuns.map((run) => (
                <tr key={run.id} className="border-b border-gray-100">
                  <td className="py-2 px-3">{run.run_type}</td>
                  <td className="py-2 px-3">{run.target_variable}</td>
                  <td className="py-2 px-3">
                    <span className={`inline-block px-2 py-0.5 rounded text-xs ${
                      run.status === "success" ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
                    }`}>
                      {run.status}
                    </span>
                  </td>
                  <td className="py-2 px-3">
                    {run.metrics ? JSON.parse(run.metrics).mape : "—"}
                  </td>
                  <td className="py-2 px-3 text-gray-500">
                    {new Date(run.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
              {modelRuns.length === 0 && (
                <tr>
                  <td colSpan={5} className="py-4 text-center text-gray-400">No model runs yet</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
