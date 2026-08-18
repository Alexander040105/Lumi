# Frontend (React)
## `react-frontend/src/App.jsx`

### `App`

- **File:** `react-frontend/src/App.jsx`
- **Lines:** `5-12`
- **Purpose:** Renders the `App` component.

**Code:**
```jsx
export default function App() {
    return (
        <ErrorBoundary>
            <AppRoutes />
            <Toaster />
        </ErrorBoundary>
    );
}
```

**Explanation:** This React component renders UI for the `App` view or widget.

## `react-frontend/src/__tests__/I18nProvider.test.jsx`

### `TestComponent`

- **File:** `react-frontend/src/__tests__/I18nProvider.test.jsx`
- **Lines:** `5-15`
- **Purpose:** Renders the `TestComponent` component.

**Code:**
```jsx
function TestComponent() {
  const { t, locale, setLocale } = useI18n();
  return (
    <div>
      <p data-testid="greeting">{t("greeting")}</p>
      <p data-testid="interpolated">{t("interpolated", { name: "Mundo" })}</p>
      <p data-testid="locale">{locale}</p>
      <button onClick={() => setLocale("fil")}>Switch to Filipino</button>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `TestComponent` view or widget.

### `renderWithI18n`

- **File:** `react-frontend/src/__tests__/I18nProvider.test.jsx`
- **Lines:** `17-23`
- **Purpose:** Utility function `renderWithI18n`.

**Code:**
```jsx
function renderWithI18n() {
  return render(
    <I18nProvider>
      <TestComponent />
    </I18nProvider>
  );
}
```

**Explanation:** This helper performs the `renderWithI18n` operation. See the code for the full implementation.

## `react-frontend/src/__tests__/theme-contrast.test.js`

### `removeComments`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `11-13`
- **Purpose:** Removes Comments.

**Code:**
```javascript
function removeComments(source) {
  return source.replace(/\/\*[\s\S]*?\*\//g, "");
}
```

**Explanation:** This function removes Comments. See the code for the full implementation.

### `parseBlock`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `15-30`
- **Purpose:** Converts Block.

**Code:**
```javascript
function parseBlock(name) {
  const cleaned = removeComments(css);
  const regex = new RegExp(`${name}\\s*\\{([^}]+)\\}`, "i");
  const match = cleaned.match(regex);
  if (!match) return {};
  const block = match[1];
  const vars = {};
  const propRegex = /--([\w-]+):\s*([0-9.\s%]+);/g;
  let m;
  while ((m = propRegex.exec(block)) !== null) {
    const key = `--${m[1]}`;
    const value = m[2].trim();
    vars[key] = value;
  }
  return vars;
}
```

**Explanation:** This function converts Block. See the code for the full implementation.

### `parseHsl`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `32-35`
- **Purpose:** Converts Hsl.

**Code:**
```javascript
function parseHsl(hslString) {
  const parts = hslString.split(/\s+/).map((p) => parseFloat(p.replace(/[^0-9.]/g, "")));
  return [parts[0] || 0, parts[1] || 0, parts[2] || 0];
}
```

**Explanation:** This function converts Hsl. See the code for the full implementation.

### `hslToRgb`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `37-44`
- **Purpose:** Utility function `hslToRgb`.

**Code:**
```javascript
function hslToRgb(h, s, l) {
  s /= 100;
  l /= 100;
  const k = (n) => (n + h / 30) % 12;
  const a = s * Math.min(l, 1 - l);
  const f = (n) => l - a * Math.max(-1, Math.min(k(n) - 3, Math.min(9 - k(n), 1)));
  return [f(0), f(8), f(4)];
}
```

**Explanation:** This helper performs the `hslToRgb` operation. See the code for the full implementation.

### `relativeLuminance`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `46-52`
- **Purpose:** Utility function `relativeLuminance`.

**Code:**
```javascript
function relativeLuminance(rgb) {
  const [r, g, b] = rgb.map((c) => {
    c = c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    return c;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}
```

**Explanation:** This helper performs the `relativeLuminance` operation. See the code for the full implementation.

### `contrastRatio`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `54-60`
- **Purpose:** Utility function `contrastRatio`.

**Code:**
```javascript
function contrastRatio(fg, bg) {
  const l1 = relativeLuminance(fg);
  const l2 = relativeLuminance(bg);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}
```

**Explanation:** This helper performs the `contrastRatio` operation. See the code for the full implementation.

### `getColor`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `62-67`
- **Purpose:** Retrieves Color.

**Code:**
```javascript
function getColor(variables, key) {
  const raw = variables[key];
  if (!raw) throw new Error(`Missing CSS variable ${key}`);
  const [h, s, l] = parseHsl(raw);
  return hslToRgb(h, s, l);
}
```

**Explanation:** This function retrieves Color. See the code for the full implementation.

### `assertContrast`

- **File:** `react-frontend/src/__tests__/theme-contrast.test.js`
- **Lines:** `84-94`
- **Purpose:** Utility function `assertContrast`.

**Code:**
```javascript
function assertContrast(theme, name) {
  for (const [fgKey, bgKey] of PAIRS) {
    const fg = getColor(theme, fgKey);
    const bg = getColor(theme, bgKey);
    const ratio = contrastRatio(fg, bg);
    expect(
      ratio,
      `${name}: ${fgKey} on ${bgKey} must meet WCAG 2.1 AA (4.5:1)`
    ).toBeGreaterThanOrEqual(4.5);
  }
}
```

**Explanation:** This helper performs the `assertContrast` operation. See the code for the full implementation.

## `react-frontend/src/components/CoverageDashboard.jsx`

### `CoverageDashboard`

- **File:** `react-frontend/src/components/CoverageDashboard.jsx`
- **Lines:** `4-117`
- **Purpose:** Renders the `CoverageDashboard` component.

**Code:**
```jsx
export default function CoverageDashboard() {
  const [level, setLevel] = useState("municipality");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getCoverageSummary(level)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [level]);

  const items = data?.items || [];
  const total = data?.total_units ?? items.length;
  const withClimate = data?.with_climate_data ?? items.filter((i) => i.has_climate_data).length;
  const coveragePct = data?.coverage_pct ?? (total > 0 ? (withClimate / total) * 100 : 0);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Data Coverage</h3>
        <select
          value={level}
          onChange={(e) => setLevel(e.target.value)}
          className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
        >
          <option value="municipality">Municipality</option>
          <option value="province">Province</option>
        </select>
      </div>

      {loading && <div className="text-gray-400 text-sm">Loading...</div>}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Overall coverage gauge */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-gray-700">Climate Data Coverage</span>
              <span className={`text-sm font-bold ${
                coveragePct >= 80 ? "text-green-600" : coveragePct >= 50 ? "text-yellow-600" : "text-red-600"
              }`}>
                {coveragePct.toFixed(1)}%
              </span>
            </div>
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all ${
                  coveragePct >= 80 ? "bg-green-500" : coveragePct >= 50 ? "bg-yellow-500" : "bg-red-500"
                }`}
                style={{ width: `${Math.min(coveragePct, 100)}%` }}
              />
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {withClimate.toLocaleString()} / {total.toLocaleString()} {level}s with climate data
            </div>
          </div>

          {/* Per-source breakdown if items have detailed data */}
          {items.length > 0 && items[0]?.renewable_type && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-gray-700">By Renewable Type</h4>
              {items.map((item) => {
                const pct = item.coverage_pct ?? 0;
                return (
                  <div key={item.renewable_type} className="space-y-1">
                    <div className="flex justify-between text-sm">
                      <span className="capitalize text-gray-700">{item.renewable_type}</span>
                      <span className="text-gray-500">{pct.toFixed(1)}%</span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${
                          pct >= 80 ? "bg-green-500" : pct >= 50 ? "bg-yellow-500" : "bg-red-500"
                        }`}
                        style={{ width: `${Math.min(pct, 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Summary stats */}
          <div className="mt-4 pt-3 border-t border-gray-100 grid grid-cols-3 gap-3 text-center">
            <div>
              <div className="text-2xl font-bold text-gray-900">{total.toLocaleString()}</div>
              <div className="text-xs text-gray-500">Total Units</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">{withClimate.toLocaleString()}</div>
              <div className="text-xs text-gray-500">With Data</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {(total - withClimate).toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">Gaps</div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `CoverageDashboard` view or widget.

## `react-frontend/src/components/ErrorBoundary.jsx`

### `constructor`

- **File:** `react-frontend/src/components/ErrorBoundary.jsx`
- **Lines:** `8-11`
- **Purpose:** Utility function `constructor`.

**Code:**
```jsx
constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
```

**Explanation:** This helper performs the `constructor` operation. See the code for the full implementation.

### `getDerivedStateFromError`

- **File:** `react-frontend/src/components/ErrorBoundary.jsx`
- **Lines:** `13-15`
- **Purpose:** Retrieves DerivedStateFromError.

**Code:**
```jsx
static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
```

**Explanation:** This function retrieves DerivedStateFromError. See the code for the full implementation.

### `componentDidCatch`

- **File:** `react-frontend/src/components/ErrorBoundary.jsx`
- **Lines:** `17-20`
- **Purpose:** Utility function `componentDidCatch`.

**Code:**
```jsx
componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    console.error("ErrorBoundary caught:", error, errorInfo);
  }
```

**Explanation:** This helper performs the `componentDidCatch` operation. See the code for the full implementation.

### `render`

- **File:** `react-frontend/src/components/ErrorBoundary.jsx`
- **Lines:** `26-62`
- **Purpose:** Utility function `render`.

**Code:**
```jsx
render() {
    if (this.state.hasError) {
      const { t } = this.context || {};

      const isApiError = this.state.error?.message?.includes("fetch") ||
                         this.state.error?.message?.includes("Network") ||
                         this.state.error?.message?.includes("Request failed");

      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-8">
          <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-gray-200 p-6 text-center">
            <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
              <svg className="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">
              {isApiError ? t?.("errorBoundary.connectionErrorTitle") : t?.("errorBoundary.genericErrorTitle")}
            </h3>
            <p className="text-sm text-gray-500 mb-4">
              {isApiError
                ? t?.("errorBoundary.connectionErrorDescription")
                : this.state.error?.message || t?.("errorBoundary.genericErrorDescription")}
            </p>
            <button
              onClick={this.handleRetry}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700"
            >
              {t?.("errorBoundary.tryAgain")}
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
```

**Explanation:** This helper performs the `render` operation. See the code for the full implementation.

## `react-frontend/src/components/ErrorState.jsx`

### `ErrorState`

- **File:** `react-frontend/src/components/ErrorState.jsx`
- **Lines:** `1-23`
- **Purpose:** Renders the `ErrorState` component.

**Code:**
```jsx
export default function ErrorState({ title = "Error", message, onRetry, retryLabel = "Try Again" }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] p-6">
      <div className="max-w-sm w-full bg-white rounded-xl shadow-sm border border-gray-200 p-5 text-center">
        <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-red-100 flex items-center justify-center">
          <svg className="w-5 h-5 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h4 className="text-base font-semibold text-gray-900 mb-1">{title}</h4>
        <p className="text-sm text-gray-500 mb-3">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            {retryLabel}
          </button>
        )}
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `ErrorState` view or widget.

### `LoadingState`

- **File:** `react-frontend/src/components/ErrorState.jsx`
- **Lines:** `25-34`
- **Purpose:** Renders the `LoadingState` component.

**Code:**
```jsx
export function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex items-center justify-center min-h-[200px]">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-3 border-blue-200 border-t-blue-600 rounded-full animate-spin" />
        <span className="text-sm text-gray-500">{label}</span>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `LoadingState` view or widget.

### `EmptyState`

- **File:** `react-frontend/src/components/ErrorState.jsx`
- **Lines:** `36-58`
- **Purpose:** Renders the `EmptyState` component.

**Code:**
```jsx
export function EmptyState({ title = "No data", message, actionLabel, onAction }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] p-6">
      <div className="max-w-sm w-full text-center">
        <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-gray-100 flex items-center justify-center">
          <svg className="w-6 h-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
        </div>
        <h4 className="text-base font-semibold text-gray-900 mb-1">{title}</h4>
        {message && <p className="text-sm text-gray-500 mb-3">{message}</p>}
        {actionLabel && onAction && (
          <button
            onClick={onAction}
            className="bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700"
          >
            {actionLabel}
          </button>
        )}
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EmptyState` view or widget.

## `react-frontend/src/components/ForecastPanel.jsx`

### `ForecastPanel`

- **File:** `react-frontend/src/components/ForecastPanel.jsx`
- **Lines:** `4-209`
- **Purpose:** Renders the `ForecastPanel` component.

**Code:**
```jsx
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
```

**Explanation:** This React component renders UI for the `ForecastPanel` view or widget.

## `react-frontend/src/components/LcoePanel.jsx`

### `LcoePanel`

- **File:** `react-frontend/src/components/LcoePanel.jsx`
- **Lines:** `4-93`
- **Purpose:** Renders the `LcoePanel` component.

**Code:**
```jsx
export default function LcoePanel({ options }) {
  const { t } = useI18n();
  if (!options || !Array.isArray(options) || options.length === 0) {
    return null;
  }

  const sorted = useMemo(
    () => [...options].sort((a, b) => (a.lcoe_php_kwh ?? Infinity) - (b.lcoe_php_kwh ?? Infinity)),
    [options]
  );

  const bestLcoe = sorted[0]?.lcoe_php_kwh;
  const tariff = options[0]?.monthly_savings && options[0]?.estimated_generation_kwh
    ? options[0].monthly_savings / options[0].estimated_generation_kwh
    : null;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-1">{t("ecosim.lcoe.title")}</h3>
      <p className="text-sm text-gray-500 mb-4">
        {t("ecosim.lcoe.description")}
        {tariff && (
          <span className="ml-1 text-blue-600">
            {t("ecosim.lcoe.rateText", { rate: tariff.toFixed(2) })}
          </span>
        )}
      </p>

      <div className="space-y-3">
        {sorted.map((opt) => {
          const lcoe = opt.lcoe_php_kwh;
          const isBest = lcoe === bestLcoe && lcoe != null;
          const gridTariff = tariff ?? 12.0;
          const barWidth = lcoe != null
            ? Math.min((lcoe / gridTariff) * 100, 200)
            : 0;

          return (
            <div key={opt.source} className="space-y-1">
              <div className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">{opt.source}</span>
                  {isBest && (
                    <span className="inline-block px-2 py-0.5 rounded text-xs bg-green-100 text-green-700 font-medium">
                      {t("ecosim.lcoe.bestLcoe")}
                    </span>
                  )}
                </div>
                <div className="text-right">
                  <span className={`font-bold ${isBest ? "text-green-600" : "text-gray-900"}`}>
                    {lcoe != null ? `₱${lcoe.toFixed(2)}` : "—"}
                  </span>
                  <span className="text-gray-400 text-xs ml-1">/kWh</span>
                </div>
              </div>

              {/* LCOE bar */}
              <div className="relative h-6 bg-gray-100 rounded-lg overflow-hidden">
                <div
                  className={`h-full rounded-lg transition-all ${
                    isBest ? "bg-green-500" : lcoe != null && lcoe < gridTariff ? "bg-blue-400" : "bg-orange-400"
                  }`}
                  style={{ width: `${barWidth}%` }}
                />
                {/* Grid tariff marker */}
                <div
                  className="absolute top-0 bottom-0 w-0.5 bg-gray-700"
                  style={{ left: "50%" }}
                  title={t("ecosim.lcoe.gridTariff", { rate: gridTariff.toFixed(2) })}
                />
              </div>

              {/* Financial details */}
              <div className="flex flex-wrap gap-3 text-xs text-gray-500">
                <span>{t("ecosim.lcoe.npv")}: {opt.npv_php != null ? `₱${(opt.npv_php / 1e6).toFixed(1)}M` : "—"}</span>
                <span>{t("ecosim.lcoe.irr")}: {opt.irr != null ? `${(opt.irr * 100).toFixed(1)}%` : "—"}</span>
                <span>{t("ecosim.lcoe.discountedPayback")}: {opt.discounted_payback_years != null ? `${opt.discounted_payback_years.toFixed(1)} yrs` : "—"}</span>
                <span>{t("ecosim.lcoe.bcr")}: {opt.benefit_cost_ratio != null ? opt.benefit_cost_ratio.toFixed(2) : "—"}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-100 text-xs text-gray-400">
        {t("ecosim.lcoe.formula")}
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `LcoePanel` view or widget.

## `react-frontend/src/components/MapPanel.jsx`

### `MapPanel`

- **File:** `react-frontend/src/components/MapPanel.jsx`
- **Lines:** `11-140`
- **Purpose:** Renders the `MapPanel` component.

**Code:**
```jsx
export default function MapPanel() {
  const [renewableType, setRenewableType] = useState("solar");
  const [level, setLevel] = useState("municipality");
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getSuitabilityMap(renewableType, level)
      .then((result) => setData(result.items || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [renewableType, level]);

  const scores = data.map((d) => d.score).filter((s) => s != null);
  const maxScore = Math.max(...scores, 100);
  const minScore = Math.min(...scores, 0);

  function getScoreColor(score) {
    if (score == null) return "#e5e7eb";
    const pct = (score - minScore) / (maxScore - minScore || 1);
    if (pct >= 0.75) return "#16a34a";
    if (pct >= 0.5) return "#84cc16";
    if (pct >= 0.25) return "#facc15";
    return "#f87171";
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Suitability Map</h3>
        <div className="flex gap-2">
          <select
            value={renewableType}
            onChange={(e) => setRenewableType(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          >
            {RENEWABLE_TYPES.map((rt) => (
              <option key={rt.key} value={rt.key}>{rt.label}</option>
            ))}
          </select>
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="municipality">Municipality</option>
            <option value="province">Province</option>
          </select>
        </div>
      </div>

      {loading && <div className="text-gray-400 text-sm py-8 text-center">Loading map data...</div>}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700 mb-4">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          {/* Legend */}
          <div className="flex items-center gap-4 mb-3 text-xs text-gray-600">
            <span>Score:</span>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded" style={{ background: "#f87171" }} />
              <span>Low</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded" style={{ background: "#facc15" }} />
              <span>Medium</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-4 h-4 rounded" style={{ background: "#16a34a" }} />
              <span>High</span>
            </div>
            <span className="ml-auto text-gray-400">{data.length} {level}s</span>
          </div>

          {/* Data table (fallback for when no map renderer is available) */}
          <div className="overflow-x-auto max-h-96 overflow-y-auto">
            <table className="min-w-full text-sm">
              <thead className="sticky top-0 bg-white">
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3">Name</th>
                  <th className="text-left py-2 px-3">Score</th>
                  <th className="text-left py-2 px-3">Lat</th>
                  <th className="text-left py-2 px-3">Lon</th>
                </tr>
              </thead>
              <tbody>
                {data.slice(0, 200).map((item, i) => (
                  <tr
                    key={i}
                    onClick={() => setSelectedItem(item)}
                    className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
                  >
                    <td className="py-2 px-3 font-medium text-gray-900">{item.name}</td>
                    <td className="py-2 px-3">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 rounded" style={{ background: getScoreColor(item.score) }} />
                        <span>{item.score?.toFixed(1) ?? "—"}</span>
                      </div>
                    </td>
                    <td className="py-2 px-3 text-gray-500">{item.lat?.toFixed(4) ?? "—"}</td>
                    <td className="py-2 px-3 text-gray-500">{item.lon?.toFixed(4) ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Selected item detail */}
          {selectedItem && (
            <div className="mt-3 bg-gray-50 rounded-lg p-3 text-sm">
              <div className="font-medium text-gray-900">{selectedItem.name}</div>
              <div className="text-gray-500 mt-1">
                Score: {selectedItem.score?.toFixed(2)} |
                Location: {selectedItem.lat?.toFixed(4)}, {selectedItem.lon?.toFixed(4)}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `MapPanel` view or widget.

## `react-frontend/src/components/__tests__/DashboardChart.test.jsx`

### `MockChart`

- **File:** `react-frontend/src/components/__tests__/DashboardChart.test.jsx`
- **Lines:** `5-15`
- **Purpose:** Renders the `MockChart` component.

**Code:**
```jsx
function MockChart({ dataPoints }) {
  return (
    <div data-testid="chart-container">
      {dataPoints.map((dp, i) => (
        <div key={i} data-testid={`data-point-${i}`}>
          {dp.year}: {dp.value}
        </div>
      ))}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `MockChart` view or widget.

## `react-frontend/src/components/admin/CreateUserModal.jsx`

### `CreateUserModal`

- **File:** `react-frontend/src/components/admin/CreateUserModal.jsx`
- **Lines:** `16-164`
- **Purpose:** Renders the `CreateUserModal` component.

**Code:**
```jsx
export default function CreateUserModal({ open, onClose, onCreated }) {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("user");
  const [plan, setPlan] = useState("free");

  // Admins are always premium
  const isAdminRole = role === "admin" || role === "dev";
  const displayPlan = isAdminRole ? "premium" : plan;
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const reset = () => {
    setEmail("");
    setFullName("");
    setRole("user");
    setPlan("free");
    setResult(null);
    setError("");
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ email, full_name: fullName, role, plan }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || t("admin.createUserModal.createUser"));
      setResult(data);
      onCreated?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>{t("admin.createUserModal.title")}</DialogTitle>
          <DialogDescription>
            {t("admin.createUserModal.description")}
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="space-y-4">
            <div className="rounded-lg bg-green-50 p-4 text-sm text-green-700">
              <p className="font-semibold">{t("admin.createUserModal.userCreated")}</p>
              <p className="mt-1">{t("admin.createUserModal.email")}: {result.email}</p>
              <p className="mt-1">{t("admin.createUserModal.role")}: {result.role}</p>
              <p className="mt-1">{t("admin.createUserModal.plan")}: {result.plan}</p>
              <p className="mt-2 break-all">
                <span className="font-semibold">{t("admin.createUserModal.tempPassword")}:</span>{" "}
                {result.temp_password}
              </p>
            </div>
            <Button onClick={reset} className="w-full">
              {t("admin.createUserModal.createAnother")}
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="text-sm font-medium">{t("admin.createUserModal.emailLabel")}</label>
              <Input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder={t("admin.createUserModal.emailPlaceholder")}
              />
            </div>
            <div>
              <label className="text-sm font-medium">{t("admin.createUserModal.fullNameLabel")}</label>
              <Input
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder={t("admin.createUserModal.fullNamePlaceholder")}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm font-medium">{t("admin.createUserModal.roleLabel")}</label>
                <select
                  value={role}
                  onChange={(e) => {
                    const newRole = e.target.value;
                    setRole(newRole);
                    if (newRole === "admin" || newRole === "dev") {
                      setPlan("premium");
                    }
                  }}
                  className="w-full rounded-md border px-3 py-2 text-sm"
                >
                  <option value="user">{t("admin.usersPage.roleUser")}</option>
                  <option value="admin">{t("admin.usersPage.roleAdmin")}</option>
                  <option value="dev">{t("admin.usersPage.roleDev")}</option>
                </select>
              </div>
              <div>
                <label className="text-sm font-medium">{t("admin.createUserModal.planLabel")}</label>
                <select
                  value={displayPlan}
                  onChange={(e) => setPlan(e.target.value)}
                  disabled={isAdminRole}
                  className="w-full rounded-md border px-3 py-2 text-sm disabled:opacity-50"
                >
                  <option value="free">{t("admin.usersPage.planFree")}</option>
                  <option value="premium">{t("admin.usersPage.planPremium")}</option>
                </select>
                {isAdminRole && (
                  <p className="text-xs text-muted-foreground mt-1">{t("admin.createUserModal.adminPremium")}</p>
                )}
              </div>
            </div>
            {error && <p className="text-sm text-destructive">{error}</p>}
            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={handleClose}>
                {t("admin.createUserModal.cancel")}
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? t("admin.createUserModal.creating") : t("admin.createUserModal.createUser")}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );
}
```

**Explanation:** This React component renders UI for the `CreateUserModal` view or widget.

## `react-frontend/src/components/admin/UserDetailDrawer.jsx`

### `UserDetailDrawer`

- **File:** `react-frontend/src/components/admin/UserDetailDrawer.jsx`
- **Lines:** `15-224`
- **Purpose:** Renders the `UserDetailDrawer` component.

**Code:**
```jsx
export default function UserDetailDrawer({ user, open, onClose }) {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [activeTab, setActiveTab] = useState("overview");
  const [detail, setDetail] = useState(null);
  const [sims, setSims] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user || !open) return;
    setActiveTab("overview");
    setDetail(null);
    setSims([]);
    setReport(null);
    fetchDetail();
  }, [user, open]);

  const fetchDetail = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users/${user.id}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      setDetail(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchSimulations = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/simulations`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setSims(data.simulations || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const fetchReport = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/users/${user.id}/reports`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setReport(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const handleTab = (tab) => {
    setActiveTab(tab);
    if (tab === "simulations" && sims.length === 0) fetchSimulations();
    if (tab === "reports" && !report) fetchReport();
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

  if (!user) return null;

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-full sm:max-w-lg overflow-y-auto">
        <SheetHeader>
          <SheetTitle>{t("admin.userDetail.title")}</SheetTitle>
        </SheetHeader>

        <div className="mt-4 flex gap-2 border-b pb-2">
          {["overview", "simulations", "reports"].map((tab) => (
            <button
              key={tab}
              onClick={() => handleTab(tab)}
              className={`text-sm px-3 py-1 rounded-md capitalize ${
                activeTab === tab
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-muted"
              }`}
            >
              {t(`admin.userDetail.tabs.${tab}`)}
            </button>
          ))}
        </div>

        {loading && <p className="text-sm text-muted-foreground py-4">{t("admin.userDetail.loading")}</p>}

        {activeTab === "overview" && detail && (
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.email")}</span>
              <span className="font-medium">{detail.email || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.name")}</span>
              <span className="font-medium">{detail.profile?.full_name || t("common.notAvailable")}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t("admin.userDetail.role")}</span>
              <Badge variant="outline" className="capitalize">
                {detail.role}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">{t("admin.userDetail.plan")}</span>
              <Badge variant="secondary" className="capitalize">
                {detail.role === "admin" || detail.role === "dev"
                  ? t("admin.usersPage.planPremium")
                  : (detail.profile?.plan ? detail.profile.plan === "premium" ? t("admin.usersPage.planPremium") : t("admin.usersPage.planFree") : t("admin.usersPage.planFree"))}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.status")}</span>
              <Badge
                variant={detail.profile?.is_active ? "default" : "destructive"}
              >
                {detail.profile?.is_active ? t("admin.userDetail.active") : t("admin.userDetail.banned")}
              </Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.joined")}</span>
              <span>{formatDate(detail.created_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.lastSignIn")}</span>
              <span>{formatDate(detail.last_sign_in_at)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">{t("admin.userDetail.emailConfirmed")}</span>
              <span>{detail.email_confirmed ? t("admin.userDetail.yes") : t("admin.userDetail.no")}</span>
            </div>
          </div>
        )}

        {activeTab === "simulations" && (
          <div className="mt-4 space-y-2">
            {sims.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("admin.userDetail.noSavedSimulations")}</p>
            ) : (
              sims.map((s) => (
                <div key={s.id} className="border rounded-lg p-3 text-sm">
                  <p className="font-medium">{s.name || t("admin.userDetail.untitled")}</p>
                  <p className="text-muted-foreground">
                    {t("admin.userDetail.municipality")}: {s.municipality_id || t("common.notAvailable")}
                  </p>
                  <p className="text-muted-foreground">{formatDate(s.created_at)}</p>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "reports" && report && (
          <div className="mt-4 space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.totalSimulations")}</p>
                <p className="text-xl font-bold">{report.total_simulations}</p>
              </div>
              <div className="border rounded-lg p-3">
                <p className="text-xs text-muted-foreground">{t("admin.userDetail.chatSessions")}</p>
                <p className="text-xl font-bold">{report.total_chat_sessions}</p>
              </div>
            </div>
            <div className="text-sm space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t("admin.userDetail.peakMunicipality")}</span>
                <span className="font-medium">
                  {report.peak_municipality_id || t("common.notAvailable")}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">{t("admin.userDetail.lastActive")}</span>
                <span>{formatDate(report.last_active)}</span>
              </div>
            </div>
            {report.recent_simulations?.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">{t("admin.userDetail.recentSimulations")}</p>
                <div className="space-y-2">
                  {report.recent_simulations.map((s) => (
                    <div key={s.id} className="border rounded-lg p-2 text-sm">
                      <p className="font-medium">{s.name || t("admin.userDetail.untitled")}</p>
                      <p className="text-muted-foreground text-xs">
                        {formatDate(s.created_at)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
```

**Explanation:** This React component renders UI for the `UserDetailDrawer` view or widget.

## `react-frontend/src/components/ecosim/EcosimBOM.jsx`

### `formatCurrency`

- **File:** `react-frontend/src/components/ecosim/EcosimBOM.jsx`
- **Lines:** `13-18`
- **Purpose:** Converts Currency.

**Code:**
```jsx
const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0,
  }).format(value ?? 0)
```

**Explanation:** This function converts Currency. See the code for the full implementation.

### `deriveSystemKw`

- **File:** `react-frontend/src/components/ecosim/EcosimBOM.jsx`
- **Lines:** `20-34`
- **Purpose:** Utility function `deriveSystemKw`.

**Code:**
```jsx
function deriveSystemKw(source, generationKwh) {
  if (!generationKwh) return 0;
  switch (source) {
    case "Solar":
      return generationKwh / (30 * 4.5);
    case "Wind":
      return generationKwh / (30 * 24 * 0.25);
    case "Hydro":
      return generationKwh / (30 * 24 * 0.5);
    case "Geothermal":
      return generationKwh / (30 * 24);
    default:
      return 0;
  }
}
```

**Explanation:** This helper performs the `deriveSystemKw` operation. See the code for the full implementation.

### `EcosimBOM`

- **File:** `react-frontend/src/components/ecosim/EcosimBOM.jsx`
- **Lines:** `62-148`
- **Purpose:** Renders the `EcosimBOM` component.

**Code:**
```jsx
export default function EcosimBOM({ result }) {
  const { t } = useI18n();
  const source = result?.recommended_source;
  const rec = result?.options?.find((o) => o.source === source) || {};
  const installationCost = rec.installation_cost ?? result?.installation_cost ?? 0;
  const systemKw = rec.system_kw ?? deriveSystemKw(source, rec.estimated_generation_kwh ?? result?.estimated_generation_kwh);

  if (!source || installationCost <= 0) {
    return null;
  }

  if (source === "Geothermal") {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Package className="h-5 w-5 text-primary" />
            {t("ecosim.bom.title")}
          </CardTitle>
          <CardDescription>{t("ecosim.bom.description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            {t("ecosim.bom.notApplicable")}
          </p>
        </CardContent>
      </Card>
    );
  }

  const items = BOM_SCHEMA[source] || [];
  const rows = items.map((entry) => {
    const qty = entry.qtyFn(systemKw);
    const totalCost = installationCost * entry.costShare;
    const unitCost = qty > 0 ? totalCost / qty : 0;
    return {
      ...entry,
      qty,
      unitCost,
      totalCost,
    };
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Package className="h-5 w-5 text-primary" />
          {t("ecosim.bom.title")}
        </CardTitle>
        <CardDescription>
          {t("ecosim.bom.estimated", { kw: systemKw.toFixed(2), source: t("ecosim.results.sources." + source), cost: formatCurrency(installationCost) })}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>{t("ecosim.bom.component")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.qty")}</TableHead>
              <TableHead>{t("ecosim.bom.unit")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.unitCost")}</TableHead>
              <TableHead className="text-right">{t("ecosim.bom.total")}</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{t("ecosim.bom.items." + row.id + ".item")}</TableCell>
                <TableCell className="text-right font-medium">{row.qty}</TableCell>
                <TableCell className="text-muted-foreground">{t("ecosim.bom.items." + row.id + ".unit")}</TableCell>
                <TableCell className="text-right">{formatCurrency(row.unitCost)}</TableCell>
                <TableCell className="text-right font-medium">{formatCurrency(row.totalCost)}</TableCell>
              </TableRow>
            ))}
            <TableRow>
              <TableCell colSpan={4} className="text-right font-semibold">
                {t("ecosim.bom.estimatedTotal")}
              </TableCell>
              <TableCell className="text-right font-bold">{formatCurrency(installationCost)}</TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
```

**Explanation:** This React component renders UI for the `EcosimBOM` view or widget.

## `react-frontend/src/components/ecosim/EcosimInputForm.jsx`

### `EcosimInputForm`

- **File:** `react-frontend/src/components/ecosim/EcosimInputForm.jsx`
- **Lines:** `11-341`
- **Purpose:** Renders the `EcosimInputForm` component.

**Code:**
```jsx
export default function EcosimInputForm({
  mode,
  setMode,
  searchQuery,
  setSearchQuery,
  searchResults,
  searching,
  selectedId,
  handleSelect,
  monthlyConsumption,
  setMonthlyConsumption,
  monthlyBill,
  setMonthlyBill,
  desiredSavings,
  setDesiredSavings,
  includeAi,
  setIncludeAi,
  onRun,
  loading,
  onSave,
}) {
  const { t } = useI18n();
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const canProceed = useMemo(() => {
    if (step === 1) return selectedId !== null;
    if (step === 2) return monthlyConsumption > 0 && monthlyBill > 0;
    return true;
  }, [step, selectedId, monthlyConsumption, monthlyBill]);

  const selectedName = useMemo(() => {
    if (!selectedId) return "";
    const found = searchResults.find((r) => r.id === selectedId);
    return found ? `${found.name}, ${found.province || ""}` : "";
  }, [selectedId, searchResults]);

  const savingsLabel = useMemo(() => {
    const s = desiredSavings || 0;
    if (s <= 10) return t("ecosim.wizard.savingsLevels.exploring");
    if (s <= 30) return t("ecosim.wizard.savingsLevels.little");
    if (s <= 60) return t("ecosim.wizard.savingsLevels.half");
    return t("ecosim.wizard.savingsLevels.offGrid");
  }, [desiredSavings, t]);

  return (
    <div className="space-y-4">
      {/* Step indicator */}
      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, i) => {
          const n = i + 1;
          const active = n === step;
          const done = n < step;
          return (
            <div key={n} className="flex items-center gap-2">
              <div
                className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-colors ${
                  done
                    ? "bg-emerald-500 text-white"
                    : active
                    ? "bg-sky-500 text-white"
                    : "bg-muted text-muted-foreground"
                }`}
              >
                {done ? <Check className="h-4 w-4" /> : n}
              </div>
              {n < totalSteps && <div className={`h-0.5 w-6 ${done ? "bg-emerald-500" : "bg-muted"}`} />}
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {step === 1 && <MapPin className="h-5 w-5 text-sky-500" />}
                {step === 2 && <Zap className="h-5 w-5 text-amber-500" />}
                {step === 3 && <Target className="h-5 w-5 text-emerald-500" />}
                {step === 4 && <ArrowRight className="h-5 w-5 text-rose-500" />}
                {t("ecosim.wizard.step", { current: step, total: totalSteps })}
              </CardTitle>
              <CardDescription>
                {step === 1 && t("ecosim.wizard.steps.step1")}
                {step === 2 && t("ecosim.wizard.steps.step2")}
                {step === 3 && t("ecosim.wizard.steps.step3")}
                {step === 4 && t("ecosim.wizard.steps.step4")}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Step 1: Location */}
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <label className="text-sm font-medium">{t("ecosim.wizard.searchMode")}</label>
                      <HelpTooltip term="municipality">
                        <span className="text-sm font-medium">{t("ecosim.wizard.municipality")}</span>
                      </HelpTooltip>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant={mode === "municipality" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMode("municipality")}
                      >
                        {t("ecosim.wizard.municipality")}
                      </Button>
                      <Button
                        variant={mode === "province" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setMode("province")}
                      >
                        {t("ecosim.wizard.province")}
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {t("ecosim.wizard.municipalityHint")}
                    </p>
                  </div>

                  <div>
                    <label className="text-sm font-medium block mb-1">
                      {mode === "municipality" ? t("ecosim.wizard.searchMunicipality") : t("ecosim.wizard.searchProvince")}
                    </label>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      <Input
                        className="pl-9"
                        placeholder={mode === "municipality" ? t("ecosim.wizard.placeholderMunicipality") : t("ecosim.wizard.placeholderProvince")}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </div>
                    {searching && <p className="text-xs text-muted-foreground mt-1">{t("common.loading")}</p>}
                    {searchResults.length > 0 && !selectedId && (
                      <div className="mt-2 max-h-48 overflow-y-auto rounded-lg border bg-card shadow-sm">
                        {searchResults.map((item) => (
                          <button
                            key={item.id}
                            className="w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors"
                            onClick={() => handleSelect(item.id)}
                          >
                            <span className="font-medium">{item.name}</span>
                            {item.province && <span className="text-muted-foreground">, {item.province}</span>}
                          </button>
                        ))}
                      </div>
                    )}
                    {selectedId && (
                      <div className="mt-2 rounded-lg border bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                        {t("ecosim.wizard.selected", { name: selectedName })}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Step 2: Energy Use */}
              {step === 2 && (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="text-sm font-medium block mb-1">
                        <HelpTooltip term="kWh">{t("ecosim.wizard.consumptionLabel")}</HelpTooltip>
                      </label>
                      <Input
                        type="number"
                        placeholder={t("ecosim.wizard.consumptionPlaceholder")}
                        value={monthlyConsumption || ""}
                        onChange={(e) => setMonthlyConsumption(Number(e.target.value))}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        {t("ecosim.wizard.consumptionHint")}
                      </p>
                    </div>
                    <div>
                      <label className="text-sm font-medium block mb-1">{t("ecosim.wizard.billLabel")}</label>
                      <Input
                        type="number"
                        placeholder={t("ecosim.wizard.billPlaceholder")}
                        value={monthlyBill || ""}
                        onChange={(e) => setMonthlyBill(Number(e.target.value))}
                      />
                      <p className="text-xs text-muted-foreground mt-1">
                        {t("ecosim.wizard.billHint")}
                      </p>
                    </div>
                  </div>
                  {monthlyConsumption > 0 && monthlyBill > 0 && (
                    <div className="rounded-lg border bg-muted/30 p-3 text-sm">
                      <p className="text-muted-foreground">
                        {t("ecosim.wizard.rateText", { rate: (monthlyBill / monthlyConsumption).toFixed(2) })}
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Step 3: Goal */}
              {step === 3 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium">{t("ecosim.wizard.savingsLabel")}</label>
                      <span className="text-sm font-bold text-sky-600">{desiredSavings}%</span>
                    </div>
                    <Slider
                      value={[desiredSavings]}
                      onValueChange={(v) => setDesiredSavings(v[0])}
                      max={100}
                      step={5}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>{t("ecosim.wizard.savingsSliderStart")}</span>
                      <span className="font-medium text-foreground">{savingsLabel}</span>
                      <span>{t("ecosim.wizard.savingsSliderEnd")}</span>
                    </div>
                  </div>

                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <Switch checked={includeAi} onCheckedChange={setIncludeAi} />
                      <label className="text-sm font-medium">{t("ecosim.wizard.aiAnalysis")}</label>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {t("ecosim.wizard.aiAnalysisHint")}
                    </p>
                  </div>
                </div>
              )}

              {/* Step 4: Review & Run */}
              {step === 4 && (
                <div className="space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p>
                      <p className="text-sm font-medium">{selectedName || t("ecosim.wizard.notSelected")}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p>
                      <p className="text-sm font-medium">{monthlyConsumption || 0} kWh</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p>
                      <p className="text-sm font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p>
                    </div>
                    <div className="rounded-lg border bg-muted/30 p-3">
                      <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p>
                      <p className="text-sm font-medium">{desiredSavings}% — {savingsLabel}</p>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {t("ecosim.wizard.compareText")}
                  </p>
                </div>
              )}

              {/* Navigation buttons */}
              <div className="flex items-center justify-between pt-2">
                {step > 1 ? (
                  <Button variant="outline" onClick={() => setStep(step - 1)} disabled={loading}>
                    <ArrowLeft className="h-4 w-4 mr-1" /> {t("ecosim.wizard.back")}
                  </Button>
                ) : (
                  <div />
                )}
                {step < totalSteps ? (
                  <Button onClick={() => setStep(step + 1)} disabled={!canProceed || loading}>
                    {t("ecosim.wizard.next")} <ArrowRight className="h-4 w-4 ml-1" />
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={onSave} disabled={loading}>
                      {t("ecosim.wizard.save")}
                    </Button>
                    <Button onClick={onRun} disabled={loading}>
                      {loading ? (
                        <>
                          <Loader2 className="h-4 w-4 mr-1 animate-spin" /> {t("ecosim.wizard.running")}
                        </>
                      ) : (
                        <>
                          {t("ecosim.wizard.runSimulation")} <ArrowRight className="h-4 w-4 ml-1" />
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar summary */}
        <div className="hidden md:block">
          <Card className="bg-muted/30">
            <CardHeader>
              <CardTitle className="text-sm">{t("ecosim.wizard.summaryTitle")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p>
                <p className="font-medium">{selectedName || t("common.notAvailable")}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p>
                <p className="font-medium">{monthlyConsumption || 0} kWh</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p>
                <p className="font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p>
                <p className="font-medium">{desiredSavings}%</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.aiAnalysis")}</p>
                <p className="font-medium">{includeAi ? t("ecosim.wizard.yes") : t("ecosim.wizard.no")}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EcosimInputForm` view or widget.

## `react-frontend/src/components/ecosim/EcosimResults.jsx`

### `formatNumber`

- **File:** `react-frontend/src/components/ecosim/EcosimResults.jsx`
- **Lines:** `17-18`
- **Purpose:** Converts Number.

**Code:**
```jsx
const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0)
```

**Explanation:** This function converts Number. See the code for the full implementation.

### `formatCurrency`

- **File:** `react-frontend/src/components/ecosim/EcosimResults.jsx`
- **Lines:** `19-20`
- **Purpose:** Converts Currency.

**Code:**
```jsx
const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", { style: "currency", currency: "PHP", maximumFractionDigits: 0 }).format(value ?? 0)
```

**Explanation:** This function converts Currency. See the code for the full implementation.

### `solarInfo`

- **File:** `react-frontend/src/components/ecosim/EcosimResults.jsx`
- **Lines:** `29-34`
- **Purpose:** Utility function `solarInfo`.

**Code:**
```jsx
function solarInfo(ghi, t) {
  if (ghi >= 5.0) return { level: "excellent", label: t("common.ratings.excellent"), desc: t("ecosim.results.info.Solar.excellent") };
  if (ghi >= 4.0) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Solar.good") };
  if (ghi >= 3.0) return { level: "moderate", label: t("common.ratings.moderate"), desc: t("ecosim.results.info.Solar.moderate") };
  return { level: "fair", label: t("common.ratings.fair"), desc: t("ecosim.results.info.Solar.fair") };
}
```

**Explanation:** This helper performs the `solarInfo` operation. See the code for the full implementation.

### `windInfo`

- **File:** `react-frontend/src/components/ecosim/EcosimResults.jsx`
- **Lines:** `35-40`
- **Purpose:** Utility function `windInfo`.

**Code:**
```jsx
function windInfo(ws, t) {
  if (ws >= 5.0) return { level: "excellent", label: t("common.ratings.excellent"), desc: t("ecosim.results.info.Wind.excellent") };
  if (ws >= 3.5) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Wind.good") };
  if (ws >= 2.5) return { level: "moderate", label: t("common.ratings.moderate"), desc: t("ecosim.results.info.Wind.moderate") };
  return { level: "poor", label: t("common.ratings.poor"), desc: t("ecosim.results.info.Wind.poor") };
}
```

**Explanation:** This helper performs the `windInfo` operation. See the code for the full implementation.

### `hydroInfo`

- **File:** `react-frontend/src/components/ecosim/EcosimResults.jsx`
- **Lines:** `41-45`
- **Purpose:** Utility function `hydroInfo`.

**Code:**
```jsx
function hydroInfo(score, t) {
  if (score >= 70) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Hydro.good") };
  if (score >= 40) return { level: "moderate", label: t("common.ratings.moderate"), desc: t("ecosim.results.info.Hydro.moderate") };
  return { level: "fair", label: t("common.ratings.fair"), desc: t("ecosim.results.info.Hydro.fair") };
}
```

**Explanation:** This helper performs the `hydroInfo` operation. See the code for the full implementation.

### `geoInfo`

- **File:** `react-frontend/src/components/ecosim/EcosimResults.jsx`
- **Lines:** `46-49`
- **Purpose:** Utility function `geoInfo`.

**Code:**
```jsx
function geoInfo(score, t) {
  if (score >= 70) return { level: "good", label: t("common.ratings.good"), desc: t("ecosim.results.info.Geothermal.good") };
  return { level: "limited", label: t("common.ratings.limited"), desc: t("ecosim.results.info.Geothermal.limited") };
}
```

**Explanation:** This helper performs the `geoInfo` operation. See the code for the full implementation.

### `EcosimResults`

- **File:** `react-frontend/src/components/ecosim/EcosimResults.jsx`
- **Lines:** `51-442`
- **Purpose:** Renders the `EcosimResults` component.

**Code:**
```jsx
export default function EcosimResults({ result, productRecs, productLoading }) {
  const { t } = useI18n();
  const [showDetails, setShowDetails] = useState(false);
  if (!result) return null;

  const rec = result.options?.find((o) => o.source === result.recommended_source) || {};
  const recScore = rec.suitability_score || 0;
  const recLabel = getRating(recScore, 100);
  const RecIcon = sourceMeta[result.recommended_source]?.icon || Zap;

  const climate = result.climate || {};
  const sInfo = solarInfo(climate.avg_allsky_sfc_sw_dwn, t);
  const wInfo = windInfo(climate.avg_ws10m, t);
  const hInfo = hydroInfo(result.renewable_energy_results?.hydro_output?.hydro_score, t);
  const gInfo = geoInfo(result.renewable_energy_results?.geothermal_output?.suitability_score, t);

  const bill = result.monthly_bill || 0;
  const cons = result.monthly_consumption_kwh || 0;
  const rate = cons > 0 ? bill / cons : 0;
  const netBill = result.comparison?.renewable_monthly_bill || 0;
  const savings = bill - netBill;
  const savingsPct = bill > 0 ? (savings / bill) * 100 : 0;
  const coverage = cons > 0 ? (rec.estimated_generation_kwh / cons) * 100 : 0;

  const maxGen = Math.max(...(result.options || []).map((o) => o.estimated_generation_kwh || 0), 1);

  return (
    <div className="space-y-6">
      {/* Hero Recommendation */}
      <div className={`rounded-2xl border-2 ${recLabel.border || "border-primary/30"} ${recLabel.bg || "bg-secondary"} p-6 md:p-8`}>
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={recLabel.color || "bg-primary text-primary-foreground"}>{t("ecosim.results.bestMatch", { match: t("common.ratings." + (recLabel.label || "excellent").toLowerCase()) })}</Badge>
              <span className="text-2xl tracking-widest">{getStars(recScore, 100)}</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-bold text-foreground">
              <span className="inline-flex items-center gap-2">
                <RecIcon className="h-8 w-8" />
                {t("ecosim.results.isBestFor", { source: t("ecosim.results.sources." + result.recommended_source) })}
              </span>
            </h2>
            <p className="text-muted-foreground max-w-2xl leading-relaxed">{result.explanation}</p>
          </div>
          <div className="shrink-0 text-center md:text-right">
            <p className="text-sm text-muted-foreground">{t("ecosim.results.suitabilityScore")}</p>
            <p className="text-4xl font-bold">
              {formatNumber(recScore, 0)}<span className="text-lg text-muted-foreground">/100</span>
            </p>
          </div>
        </div>
      </div>

      {/* Quick Benefits */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-primary">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-primary mb-1">
              <PiggyBank className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.monthlySavings")}</span>
            </div>
            <p className="text-2xl font-bold">{formatCurrency(savings)}</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.offYourCurrentBill", { pct: savingsPct.toFixed(0) })}</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-chart-wind">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-primary mb-1">
              <Zap className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.energyCoverage")}</span>
            </div>
            <p className="text-2xl font-bold">{formatNumber(coverage, 0)}%</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.ofYourMonthlyConsumption")}</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-warning">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-foreground mb-1">
              <ArrowRight className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.paybackPeriod")}</span>
            </div>
            <p className="text-2xl font-bold">{result.payback_years ? `${formatNumber(result.payback_years, 1)} yrs` : t("common.notAvailable")}</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.timeToBreakEven")}</p>
          </CardContent>
        </Card>
        <Card className="border-l-4 border-l-primary">
          <CardContent className="p-5">
            <div className="flex items-center gap-2 text-primary mb-1">
              <TreePine className="h-4 w-4" />
              <span className="text-sm font-medium">{t("ecosim.results.benefits.co2Reduction")}</span>
            </div>
            <p className="text-2xl font-bold">{formatNumber(result.carbon_reduction)} kg</p>
            <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.benefits.lessCarbonPerMonth")}</p>
          </CardContent>
        </Card>
      </div>

      {/* Why Recommended */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-primary" />
            {t("ecosim.results.whyRecommended.title", { source: t("ecosim.results.sources." + result.recommended_source) })}
          </CardTitle>
          <CardDescription>{t("ecosim.results.whyRecommended.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className="font-semibold mb-1">{t("ecosim.results.whyRecommended.yourLocation")}</p>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.whyRecommended.locationText", { municipality: result.municipality, id: result.municipality_id })}</p>
              <p className="text-sm mt-2">
                {t("ecosim.results.whyRecommended.usageText", { consumption: cons.toFixed(0), bill: formatCurrency(bill), rate: formatCurrency(rate) })}
              </p>
            </div>
            <div className="rounded-lg border bg-muted/30 p-4">
              <p className="font-semibold mb-1">{t("ecosim.results.whyRecommended.climateAdvantage")}</p>
              <p className="text-sm text-muted-foreground">
                {t("ecosim.results.climateTemplates." + result.recommended_source, {
                  value: result.recommended_source === "Hydro"
                    ? result.renewable_energy_results?.hydro_output?.hydro_score?.toFixed(0)
                    : (result.recommended_source === "Solar" ? climate.avg_allsky_sfc_sw_dwn?.toFixed(2) : climate.avg_ws10m?.toFixed(2)),
                  desc: { Solar: sInfo.desc, Wind: wInfo.desc, Hydro: hInfo.desc, Geothermal: gInfo.desc }[result.recommended_source]
                })}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Renewable Potential Comparison */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">{t("ecosim.results.potentialTitle")}</CardTitle>
          <CardDescription>{t("ecosim.results.potentialDescription")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {[
            { source: "Solar", info: sInfo, score: climate.avg_allsky_sfc_sw_dwn, max: 6, unit: "kWh/m²/day", output: result.renewable_energy_results?.solar_output },
            { source: "Wind", info: wInfo, score: climate.avg_ws10m, max: 6, unit: "m/s", output: result.renewable_energy_results?.wind_output },
            { source: "Hydro", info: hInfo, score: result.renewable_energy_results?.hydro_output?.hydro_score, max: 100, unit: "score", output: result.renewable_energy_results?.hydro_output },
            { source: "Geothermal", info: gInfo, score: result.renewable_energy_results?.geothermal_output?.suitability_score, max: 100, unit: "score", output: result.renewable_energy_results?.geothermal_output },
          ].map((item) => {
            const isRec = item.source === result.recommended_source;
            const meta = sourceMeta[item.source];
            const scoreVal = parseFloat(item.score) || 0;
            const rating = getRating(scoreVal, item.max);
            const stars = getStars(scoreVal, item.max);
            const pct = maxGen > 0 ? ((item.output?.estimated_generation_kwh || item.output?.monthly_energy_kwh || item.output?.monthly_solar_output || 0) / maxGen) * 100 : 0;
            return (
              <div key={item.source} className={`flex items-center gap-4 p-3 rounded-lg border ${isRec ? "border-primary/30 bg-secondary/50" : ""}`}>
                <div className={`shrink-0 w-10 h-10 rounded-full ${meta.bg} flex items-center justify-center`}>
                  <meta.icon className={`h-5 w-5 ${meta.iconColor}`} />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold">{t("ecosim.results.sources." + item.source)}</span>
                    {isRec && <Badge className="bg-primary text-primary-foreground text-xs">{t("ecosim.results.recommended")}</Badge>}
                    <Badge className={`${rating.color} text-xs`}>{item.info.label}</Badge>
                    <span className="tracking-widest text-sm">{stars}</span>
                  </div>
                  <p className="text-sm text-muted-foreground mt-0.5">
                    {item.score?.toFixed ? item.score.toFixed(2) : item.score} {item.unit} — {item.info.desc}
                  </p>
                  {pct > 0 && (
                    <div className="mt-2 h-2 rounded-full bg-muted overflow-hidden">
                      <div className={`h-2 rounded-full ${meta.bar} transition-all`} style={{ width: `${Math.min(pct, 100)}%` }} />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </CardContent>
      </Card>

      {/* Financial Impact */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Wallet className="h-5 w-5 text-primary" />
            {t("ecosim.results.financial.title")}
          </CardTitle>
          <CardDescription>{t("ecosim.results.financial.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-xl border bg-destructive/10 p-5 text-center">
              <p className="text-sm text-foreground font-medium">{t("ecosim.results.financial.currentBill")}</p>
              <p className="text-3xl font-bold text-foreground mt-1">{formatCurrency(bill)}</p>
              <p className="text-xs text-foreground mt-1">{t("ecosim.results.financial.used", { consumption: cons.toFixed(0) })}</p>
            </div>
            <div className="rounded-xl border bg-secondary p-5 text-center">
              <p className="text-sm text-primary font-medium">{t("ecosim.results.financial.newBill")}</p>
              <p className="text-3xl font-bold text-primary mt-1">{formatCurrency(netBill)}</p>
              <p className="text-xs text-primary mt-1">{t("ecosim.results.financial.afterOffset", { source: t("ecosim.results.sources." + result.recommended_source).toLowerCase() })}</p>
            </div>
            <div className="rounded-xl border bg-warning/10 p-5 text-center">
              <p className="text-sm text-foreground font-medium">{t("ecosim.results.financial.monthlySavings")}</p>
              <p className="text-3xl font-bold text-foreground mt-1">{formatCurrency(savings)}</p>
              <p className="text-xs text-warning mt-1">{t("ecosim.results.financial.reduction", { pct: savingsPct.toFixed(0) })}</p>
            </div>
          </div>
          <div className="rounded-lg border bg-muted/30 p-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-sm text-muted-foreground">{t("ecosim.results.financial.installationCost")}</p>
                <p className="text-xl font-semibold">{formatCurrency(result.installation_cost)}</p>
                <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.financial.costNote")}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">{t("ecosim.results.financial.payback")}</p>
                <p className="text-xl font-semibold">
                  {result.payback_years ? t("ecosim.results.financial.years", { years: formatNumber(result.payback_years, 1) }) : t("ecosim.results.financial.notCalculable")}
                </p>
                <p className="text-xs text-muted-foreground mt-1">{t("ecosim.results.financial.paybackNote")}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      {/* Bill of Materials */}
      <EcosimBOM result={result} />

      {/* Meralco Rate */}
      {result.meralco_rate && result.meralco_rate.rate_php_per_kwh && (
        <Card>
          <CardHeader>
            <CardTitle>{t("ecosim.results.meralco.title")}</CardTitle>
            <CardDescription>{t("ecosim.results.meralco.description")}</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.meralco.generationCharge", { year: result.meralco_rate.year })}</p>
              <p className="text-lg font-semibold">{formatCurrency(result.meralco_rate.rate_php_per_kwh)} / kWh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.meralco.yourEffectiveRate")}</p>
              <p className="text-lg font-semibold">{formatCurrency(rate)} / kWh</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{t("ecosim.results.meralco.customerClass")}</p>
              <p className="text-lg font-semibold">{result.meralco_rate.customer_class}</p>
            </div>
          </CardContent>
          <p className="px-6 pb-4 text-xs text-muted-foreground">{result.meralco_rate.note}</p>
        </Card>
      )}

      {/* Product Recommendations */}
      {(productRecs || productLoading) && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Zap className="h-5 w-5 text-warning" />
              {t("ecosim.results.productRecs.title", { source: t("ecosim.results.sources." + result.recommended_source) })}
            </CardTitle>
            <CardDescription>{t("ecosim.results.productRecs.description")}</CardDescription>
          </CardHeader>
          <CardContent>
            {productLoading && <div className="h-24 animate-pulse rounded bg-muted" />}
            {!productLoading && productRecs?.items?.length > 0 && (
              <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                {productRecs.items.map((item) => (
                  <a key={item.url || item.product_name} href={item.url} target="_blank" rel="noopener noreferrer" className="rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow">
                    <p className="text-sm font-medium line-clamp-2">{item.product_name}</p>
                    <p className="mt-1 text-sm font-semibold text-primary">{item.currency} {item.price_value?.toLocaleString?.() || item.price_value}</p>
                    <p className="text-xs text-muted-foreground capitalize">{item.source_site} · {item.energy_subcategory}</p>
                    {item.ratings && <p className="text-xs text-foreground mt-1">{item.ratings}</p>}
                  </a>
                ))}
              </div>
            )}
            {!productLoading && productRecs && (!productRecs.items || productRecs.items.length === 0) && (
              <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
                <AlertTriangle className="h-4 w-4 inline mr-1 text-warning" />
                {t("ecosim.results.productRecs.none", { source: result.recommended_source.toLowerCase() })}
              </div>
            )}
            {productRecs?.note && <p className="mt-2 text-xs text-muted-foreground">{t("ecosim.results.productRecs.note", { note: productRecs.note })}</p>}
          </CardContent>
        </Card>
      )}

      {/* Provider Recommendations */}
      <ProviderRecommendations municipalityName={result.municipality} provinceName={result.municipality} />

      {/* Next Steps */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-primary" />
            {t("ecosim.results.nextSteps.title")}
          </CardTitle>
          <CardDescription>{t("ecosim.results.nextSteps.description")}</CardDescription>
        </CardHeader>
        <CardContent>
          <NextStepList steps={t("ecosim.results.nextStepsList." + result.recommended_source)} />
        </CardContent>
      </Card>

      {/* Technical Details Toggle */}
      <div className="text-center">
        <Button variant="ghost" size="sm" onClick={() => setShowDetails(!showDetails)} className="text-muted-foreground hover:text-foreground">
          {showDetails ? <ChevronUp className="h-4 w-4 mr-1" /> : <ChevronDown className="h-4 w-4 mr-1" />}
          {showDetails ? t("ecosim.results.technical.hide") : t("ecosim.results.technical.show")}
        </Button>
      </div>

      {showDetails && (
        <div className="space-y-6">
          {/* Climate data */}
          {climate && (
            <Card>
              <CardHeader>
                <CardTitle>{t("ecosim.results.technical.climateData")}</CardTitle>
                <CardDescription>{t("ecosim.results.technical.climateDescription")}</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-3 lg:grid-cols-4">
                {[
                  { label: t("ecosim.results.climateLabels.temperature"), value: climate.avg_t2m, unit: "°C", digits: 1 },
                  { label: t("ecosim.results.climateLabels.humidity"), value: climate.avg_rh2m, unit: "%", digits: 1 },
                  { label: t("ecosim.results.climateLabels.rainfall"), value: climate.avg_prectotcorr, unit: "mm/day", digits: 1 },
                  { label: t("ecosim.results.climateLabels.solarIrradiance"), value: climate.avg_allsky_sfc_sw_dwn, unit: "kWh/m²/day", digits: 2 },
                  { label: t("ecosim.results.climateLabels.windSpeed"), value: climate.avg_ws10m, unit: "m/s", digits: 2 },
                  { label: t("ecosim.results.climateLabels.cloudCoverage"), value: climate.avg_cloud_amt, unit: "%", digits: 1 },
                  { label: t("ecosim.results.climateLabels.surfacePressure"), value: climate.avg_surface_pressure, unit: "kPa", digits: 1 },
                  { label: t("ecosim.results.climateLabels.elevation"), value: climate.elevation, unit: "m", digits: 0 },
                ].map((item) => (
                  <div key={item.label}>
                    <p className="text-sm text-muted-foreground">{item.label}</p>
                    <p className="text-lg font-semibold">{formatNumber(item.value, item.digits)} {item.unit}</p>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Detailed renewable outputs */}
          {result.renewable_energy_results && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              {["solar", "wind", "hydro", "geothermal"].map((key) => {
                const data = result.renewable_energy_results[`${key}_output`];
                if (!data) return null;
                const title = key.charAt(0).toUpperCase() + key.slice(1);
                const meta = sourceMeta[title] || sourceMeta.Solar;
                return (
                  <Card key={key} className={`border-t-4 border-t-${meta.bar.replace("bg-", "")}`}>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2 text-sm">
                        <span className={`inline-block h-3 w-3 rounded-full ${meta.bar}`} />
                        {t("ecosim.results.technical.output", { source: t("ecosim.results.sources." + title) })}
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2 text-sm">
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.daily")}</span><span className="font-medium">{formatNumber(data.daily_solar_output || data.daily_energy_kwh || data.daily_hydro_output, 2)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.monthly")}</span><span className="font-medium">{formatNumber(data.monthly_solar_output || data.monthly_energy_kwh || data.monthly_hydro_output, 1)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.annual")}</span><span className="font-medium">{formatNumber(data.annual_solar_output || data.annual_wind_output_kwh || data.annual_hydro_output, 0)} kWh</span></div>
                      <div className="flex justify-between"><span className="text-muted-foreground">{t("ecosim.results.technical.score")}</span><span className="font-medium">{formatNumber(data.solar_score || data.capacity_factor || data.hydro_score || data.suitability_score, 0)} / 100</span></div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Scenario comparison */}
          {result.comparison && (
            <Card>
              <CardHeader>
                <CardTitle>{t("ecosim.results.technical.scenarioComparison")}</CardTitle>
                <CardDescription>{t("ecosim.results.technical.scenarioDescription")}</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-3 md:grid-cols-2">
                <div className="rounded-lg border bg-destructive/10 p-4">
                  <p className="text-sm font-medium text-foreground">{t("ecosim.results.technical.current")}</p>
                  <p className="text-xl font-bold text-foreground">{formatCurrency(result.comparison.current_monthly_bill)}</p>
                  <p className="text-xs text-foreground">{formatNumber(result.comparison.current_monthly_consumption_kwh)} kWh</p>
                </div>
                <div className="rounded-lg border bg-secondary p-4">
                  <p className="text-sm font-medium text-primary">{t("ecosim.results.technical.withSource", { source: t("ecosim.results.sources." + result.recommended_source) })}</p>
                  <p className="text-xl font-bold text-primary">{formatCurrency(result.comparison.renewable_monthly_bill)}</p>
                  <p className="text-xs text-primary">{formatNumber(result.comparison.renewable_monthly_consumption_kwh)} kWh</p>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EcosimResults` view or widget.

## `react-frontend/src/components/ecosim/EcosimWizard.jsx`

### `EcosimWizard`

- **File:** `react-frontend/src/components/ecosim/EcosimWizard.jsx`
- **Lines:** `9-232`
- **Purpose:** Renders the `EcosimWizard` component.

**Code:**
```jsx
export default function EcosimWizard({
  mode, setMode,
  muniQuery, setMuniQuery, muniOpen, setMuniOpen, filteredMunicipalities, municipalityId, setMunicipalityId, municipalitiesError,
  provinceQuery, setProvinceQuery, provinceOpen, setProvinceOpen, filteredProvinces, provinceId, setProvinceId, provincesError,
  monthlyConsumption, setMonthlyConsumption, monthlyBill, setMonthlyBill,
  desiredSavings, setDesiredSavings, includeAi, setIncludeAi,
  onRun, loading, activeId, result, user, onSave,
}) {
  const { t } = useI18n();
  const [step, setStep] = useState(1);
  const totalSteps = 4;

  const canProceed = useMemo(() => {
    if (step === 1) return activeId !== null && activeId !== "";
    if (step === 2) return monthlyConsumption > 0 && monthlyBill > 0;
    return true;
  }, [step, activeId, monthlyConsumption, monthlyBill]);

  const selectedName = useMemo(() => {
    if (mode === "municipality") {
      const found = filteredMunicipalities.find((m) => String(m.municipality_id) === municipalityId);
      return found ? found.name : muniQuery;
    }
    const found = filteredProvinces.find((p) => String(p.province_id) === provinceId);
    return found ? found.name : provinceQuery;
  }, [mode, municipalityId, provinceId, filteredMunicipalities, filteredProvinces, muniQuery, provinceQuery]);

  const savingsLabel = useMemo(() => {
    const s = desiredSavings || 0;
    if (s <= 10) return t("ecosim.wizard.savingsLevels.exploring");
    if (s <= 30) return t("ecosim.wizard.savingsLevels.little");
    if (s <= 60) return t("ecosim.wizard.savingsLevels.half");
    return t("ecosim.wizard.savingsLevels.offGrid");
  }, [desiredSavings, t]);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        {Array.from({ length: totalSteps }).map((_, i) => {
          const n = i + 1;
          const active = n === step;
          const done = n < step;
          return (
            <div key={n} className="flex items-center gap-2">
              <div className={`flex h-8 w-8 items-center justify-center rounded-full text-sm font-bold transition-colors ${done ? "bg-emerald-500 text-white" : active ? "bg-sky-500 text-white" : "bg-muted text-muted-foreground"}`}>
                {done ? <Check className="h-4 w-4" /> : n}
              </div>
              {n < totalSteps && <div className={`h-0.5 w-6 ${done ? "bg-emerald-500" : "bg-muted"}`} />}
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {step === 1 && <MapPin className="h-5 w-5 text-sky-500" />}
                {step === 2 && <Zap className="h-5 w-5 text-amber-500" />}
                {step === 3 && <Target className="h-5 w-5 text-emerald-500" />}
                {step === 4 && <ArrowRight className="h-5 w-5 text-rose-500" />}
                {t("ecosim.wizard.step", { current: step, total: totalSteps })}
              </CardTitle>
              <CardDescription>
                {t(`ecosim.wizard.steps.step${step}`)}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {step === 1 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <label className="text-sm font-medium">{t("ecosim.wizard.searchMode")}</label>
                    </div>
                    <div className="flex gap-2">
                      <Button variant={mode === "municipality" ? "default" : "outline"} size="sm" onClick={() => setMode("municipality")}>{t("ecosim.wizard.municipality")}</Button>
                      <Button variant={mode === "province" ? "default" : "outline"} size="sm" onClick={() => setMode("province")}>{t("ecosim.wizard.province")}</Button>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.municipalityHint")}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium block mb-1">{mode === "municipality" ? t("ecosim.wizard.searchMunicipality") : t("ecosim.wizard.searchProvince")}</label>
                    <div className="relative">
                      <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                      {mode === "municipality" ? (
                        <Input className="pl-9" placeholder={t("ecosim.wizard.placeholderMunicipality")} value={muniQuery} onChange={(e) => { setMuniQuery(e.target.value); setMuniOpen(true); }} onFocus={() => setMuniOpen(true)} onBlur={() => setMuniOpen(false)} disabled={loading} autoComplete="off" />
                      ) : (
                        <Input className="pl-9" placeholder={t("ecosim.wizard.placeholderProvince")} value={provinceQuery} onChange={(e) => { setProvinceQuery(e.target.value); setProvinceOpen(true); }} onFocus={() => setProvinceOpen(true)} onBlur={() => setProvinceOpen(false)} disabled={loading} autoComplete="off" />
                      )}
                    </div>
                    {mode === "municipality" && muniOpen && (
                      <div className="mt-1 max-h-48 overflow-y-auto rounded-lg border bg-card shadow-sm z-10 relative">
                        {filteredMunicipalities.length ? filteredMunicipalities.map((item) => (
                          <button key={item.municipality_id} className={"w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors " + (String(item.municipality_id) === municipalityId ? "bg-accent font-medium" : "")} onMouseDown={(e) => e.preventDefault()} onClick={() => { setMunicipalityId(String(item.municipality_id)); setMuniQuery(item.name); setMuniOpen(false); }}>
                            {item.name}
                          </button>
                        )) : <div className="px-3 py-2 text-sm text-muted-foreground">{t("ecosim.wizard.noResults")}</div>}
                      </div>
                    )}
                    {mode === "province" && provinceOpen && (
                      <div className="mt-1 max-h-48 overflow-y-auto rounded-lg border bg-card shadow-sm z-10 relative">
                        {filteredProvinces.length ? filteredProvinces.map((item) => (
                          <button key={item.province_id} className={"w-full px-3 py-2 text-left text-sm hover:bg-muted transition-colors " + (String(item.province_id) === provinceId ? "bg-accent font-medium" : "")} onMouseDown={(e) => e.preventDefault()} onClick={() => { setProvinceId(String(item.province_id)); setProvinceQuery(item.name); setProvinceOpen(false); }}>
                            {item.name}
                          </button>
                        )) : <div className="px-3 py-2 text-sm text-muted-foreground">{t("ecosim.wizard.noResults")}</div>}
                      </div>
                    )}
                    {mode === "municipality" && municipalitiesError && <p className="text-xs text-destructive mt-1">{municipalitiesError}</p>}
                    {mode === "province" && provincesError && <p className="text-xs text-destructive mt-1">{provincesError}</p>}
                    {activeId && (
                      <div className="mt-2 rounded-lg border bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
                        {t("ecosim.wizard.selected", { name: selectedName })}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-4">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div>
                      <label className="text-sm font-medium block mb-1"><HelpTooltip term="kWh">{t("ecosim.wizard.consumptionLabel")}</HelpTooltip></label>
                      <Input type="number" placeholder={t("ecosim.wizard.consumptionPlaceholder")} value={monthlyConsumption || ""} onChange={(e) => setMonthlyConsumption(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.consumptionHint")}</p>
                    </div>
                    <div>
                      <label className="text-sm font-medium block mb-1">{t("ecosim.wizard.billLabel")}</label>
                      <Input type="number" placeholder={t("ecosim.wizard.billPlaceholder")} value={monthlyBill || ""} onChange={(e) => setMonthlyBill(Number(e.target.value))} />
                      <p className="text-xs text-muted-foreground mt-1">{t("ecosim.wizard.billHint")}</p>
                    </div>
                  </div>
                  {monthlyConsumption > 0 && monthlyBill > 0 && (
                    <div className="rounded-lg border bg-muted/30 p-3 text-sm">
                      <p className="text-muted-foreground">{t("ecosim.wizard.rateText", { rate: (monthlyBill / monthlyConsumption).toFixed(2) })}</p>
                    </div>
                  )}
                </div>
              )}

              {step === 3 && (
                <div className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <label className="text-sm font-medium">{t("ecosim.wizard.savingsLabel")}</label>
                      <span className="text-sm font-bold text-sky-600">{desiredSavings}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      step="5"
                      value={desiredSavings}
                      onChange={(e) => setDesiredSavings(Number(e.target.value))}
                      className="w-full h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-sky-500"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground mt-1">
                      <span>{t("ecosim.wizard.savingsSliderStart")}</span>
                      <span className="font-medium text-foreground">{savingsLabel}</span>
                      <span>{t("ecosim.wizard.savingsSliderEnd")}</span>
                    </div>
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <input
                        type="checkbox"
                        checked={includeAi}
                        onChange={(e) => setIncludeAi(e.target.checked)}
                        className="h-4 w-4 rounded border-gray-300 text-primary accent-primary"
                      />
                      <label className="text-sm font-medium">{t("ecosim.wizard.aiAnalysis")}</label>
                    </div>
                    <p className="text-xs text-muted-foreground">{t("ecosim.wizard.aiAnalysisHint")}</p>
                  </div>
                </div>
              )}

              {step === 4 && (
                <div className="space-y-4">
                  <div className="grid gap-3 md:grid-cols-2">
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p><p className="text-sm font-medium">{selectedName || t("ecosim.wizard.notSelected")}</p></div>
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p><p className="text-sm font-medium">{monthlyConsumption || 0} kWh</p></div>
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p><p className="text-sm font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p></div>
                    <div className="rounded-lg border bg-muted/30 p-3"><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p><p className="text-sm font-medium">{desiredSavings}% — {savingsLabel}</p></div>
                  </div>
                  <p className="text-sm text-muted-foreground">{t("ecosim.wizard.compareText")}</p>
                </div>
              )}

              <div className="flex items-center justify-between pt-2">
                {step > 1 ? <Button variant="outline" onClick={() => setStep(step - 1)} disabled={loading}><ArrowLeft className="h-4 w-4 mr-1" /> {t("ecosim.wizard.back")}</Button> : <div />}
                {step < totalSteps ? (
                  <Button onClick={() => setStep(step + 1)} disabled={!canProceed || loading}>{t("ecosim.wizard.next")} <ArrowRight className="h-4 w-4 ml-1" /></Button>
                ) : (
                  <div className="flex gap-2">
                    {result && user && <Button variant="outline" onClick={onSave} disabled={loading}>{t("ecosim.wizard.save")}</Button>}
                    <Button onClick={(e) => { e.preventDefault(); onRun(e); }} disabled={loading || !activeId}>
                      {loading ? <><Loader2 className="h-4 w-4 mr-1 animate-spin" /> {t("ecosim.wizard.running")}</> : <>{t("ecosim.wizard.runSimulation")} <ArrowRight className="h-4 w-4 ml-1" /></>}
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="hidden md:block">
          <Card className="bg-muted/30">
            <CardHeader><CardTitle className="text-sm">{t("ecosim.wizard.summaryTitle")}</CardTitle></CardHeader>
            <CardContent className="space-y-3 text-sm">
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.location")}</p><p className="font-medium">{selectedName || "—"}</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.consumption")}</p><p className="font-medium">{monthlyConsumption || 0} kWh</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.bill")}</p><p className="font-medium">PHP {monthlyBill?.toLocaleString() || 0}</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.savingsGoal")}</p><p className="font-medium">{desiredSavings}%</p></div>
              <div><p className="text-xs text-muted-foreground">{t("ecosim.wizard.summary.aiAnalysis")}</p><p className="font-medium">{includeAi ? t("ecosim.wizard.yes") : t("ecosim.wizard.no")}</p></div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EcosimWizard` view or widget.

## `react-frontend/src/components/ecosim/ProviderRecommendations.jsx`

### `ProviderRecommendations`

- **File:** `react-frontend/src/components/ecosim/ProviderRecommendations.jsx`
- **Lines:** `11-76`
- **Purpose:** ProviderRecommendations — shows DOE-registered solar installers in the user's region.

**Code:**
```jsx
export default function ProviderRecommendations({ municipalityName, provinceName }) {
  const { t } = useI18n();
  // Determine region
  let region = getRegionFromProvince(provinceName) || getRegionFromMunicipality(municipalityName);

  // Fallback: try to extract region from municipality name itself (e.g., "Quezon City" → NCR)
  if (!region && municipalityName) {
    region = getRegionFromMunicipality(municipalityName);
  }

  const matched = region
    ? providersData.filter((p) => p.region === region)
    : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Building2 className="h-5 w-5 text-primary" />
          {t("ecosim.providers.title")}
        </CardTitle>
        <CardDescription>
          {t("ecosim.providers.description")}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {matched.length > 0 ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {matched.map((p, i) => (
              <a
                key={i}
                href={p.url}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-lg border bg-card p-4 shadow-sm hover:shadow-md transition-shadow flex flex-col gap-2"
              >
                <div className="flex items-start gap-2">
                  <MapPin className="h-4 w-4 text-primary shrink-0 mt-0.5" />
                  <div className="min-w-0">
                    <p className="text-sm font-medium line-clamp-2">{p.name}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{p.type}</p>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">{p.address}</p>
                <div className="flex items-center justify-between mt-auto pt-1">
                  <span className="text-xs text-muted-foreground">{p.years}</span>
                  <span className="text-xs text-primary flex items-center gap-1">
                    {t("ecosim.providers.visit")} <ExternalLink className="h-3 w-3" />
                  </span>
                </div>
              </a>
            ))}
          </div>
        ) : (
          <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
            <AlertTriangle className="h-4 w-4 inline mr-1 text-warning" />
            {t("ecosim.providers.none", { area: municipalityName || provinceName || t("common.notAvailable") })}
          </div>
        )}
        <p className="mt-3 text-xs text-muted-foreground">
          {t("ecosim.providers.note")}
        </p>
      </CardContent>
    </Card>
  );
}
```

**Explanation:** This React component renders UI for the `ProviderRecommendations` view or widget.

## `react-frontend/src/components/energyhub/AiInsightPanel.jsx`

### `AiInsightPanel`

- **File:** `react-frontend/src/components/energyhub/AiInsightPanel.jsx`
- **Lines:** `6-112`
- **Purpose:** Renders the `AiInsightPanel` component.

**Code:**
```jsx
export default function AiInsightPanel({
  insight,
  onToggleLlm,
  useLlm = false,
  llmLoading = {},
  chartAnalyses = {},
  onAnalyzeChart,
}) {
  const { t } = useI18n();
  const [activeTab, setActiveTab] = useState("overview");

  const anyLoading = Object.values(llmLoading || {}).some(Boolean);
  const tabLoading = !!(llmLoading || {})[activeTab];

  if (!insight) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          {t("energyHub.aiInsight.title")}
        </h3>
        <div className="mt-4 h-24 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  const activeAnalysis = chartAnalyses[activeTab];

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          {t("energyHub.aiInsight.title")}
        </h3>
        <Button
          variant={useLlm ? "default" : "outline"}
          size="sm"
          onClick={onToggleLlm}
          disabled={anyLoading}
          className="gap-1.5"
        >
          {anyLoading ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Sparkles className="h-3.5 w-3.5" />
          )}
          {useLlm ? t("energyHub.aiInsight.llmMode") : t("energyHub.aiInsight.staticMode")}
        </Button>
      </div>

      <p className="mt-1 text-xs text-muted-foreground">
        {useLlm
          ? t("energyHub.aiInsight.poweredByLlm")
          : t("energyHub.aiInsight.poweredByStatic", { year: insight.data_year })}
      </p>

      {/* Tabs for different chart analyses */}
      {useLlm && onAnalyzeChart && (
        <div className="mt-3 flex gap-2 overflow-x-auto pb-1">
          {["overview", "trends", "sources", "map"].map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab);
                if (!chartAnalyses[tab]) {
                  onAnalyzeChart(tab);
                }
              }}
              disabled={!!(llmLoading || {})[tab]}
              className={`px-3 py-1 rounded-md text-xs font-medium whitespace-nowrap transition-colors disabled:opacity-50 ${
                activeTab === tab
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              }`}
            >
              {t(`energyHub.aiInsight.tabs.${tab}`)}
              {chartAnalyses[tab] && <span className="ml-1 text-[10px]">✓</span>}
            </button>
          ))}
        </div>
      )}

      <div className="mt-4 rounded-lg bg-amber-50 border border-amber-100 p-4">
        {tabLoading && !activeAnalysis?.insight ? (
          <div className="flex items-center gap-2 text-sm text-amber-800">
            <Loader2 className="h-4 w-4 animate-spin" />
            {t("energyHub.aiInsight.loading")}
          </div>
        ) : (
          <p className="text-sm leading-relaxed text-amber-900 whitespace-pre-line">
            {activeAnalysis?.insight || insight?.insight || ""}
          </p>
        )}
      </div>

      {(activeAnalysis?.recommendation || insight.recommendation) && (
        <div className="mt-3 rounded-lg bg-sky-50 border border-sky-100 p-4 flex gap-3">
          <Info className="h-4 w-4 text-sky-600 shrink-0 mt-0.5" />
          <p className="text-sm leading-relaxed text-sky-900">
            {activeAnalysis?.recommendation || insight.recommendation}
          </p>
        </div>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `AiInsightPanel` view or widget.

## `react-frontend/src/components/energyhub/ChartExplanation.jsx`

### `ChartExplanation`

- **File:** `react-frontend/src/components/energyhub/ChartExplanation.jsx`
- **Lines:** `9-38`
- **Purpose:** ChartExplanation — reusable "What / Why / Action" explanation block

**Code:**
```jsx
export default function ChartExplanation({ title, what, why, action }) {
  const { t } = useI18n();
  return (
    <Card className="mt-3 border-l-4 border-l-primary bg-muted/40">
      <CardContent className="py-3 px-4">
        <div className="flex items-start gap-2">
          <Info className="mt-0.5 h-4 w-4 text-primary shrink-0" />
          <div className="space-y-1 text-sm">
            {title && <p className="font-semibold text-foreground">{title}</p>}
            {what && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{t("energyHub.chartExplanation.what")}</span> {what}
              </p>
            )}
            {why && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{t("energyHub.chartExplanation.why")}</span> {why}
              </p>
            )}
            {action && (
              <p className="text-muted-foreground">
                <span className="font-medium text-foreground">{t("energyHub.chartExplanation.action")}</span> {action}
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

**Explanation:** This React component renders UI for the `ChartExplanation` view or widget.

## `react-frontend/src/components/energyhub/EnergyMap.jsx`

### `isSuitabilityMetric`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `23-25`
- **Purpose:** Utility function `isSuitabilityMetric`.

**Code:**
```jsx
function isSuitabilityMetric(metric) {
  return SUITABILITY_METRICS.includes(metric);
}
```

**Explanation:** This helper performs the `isSuitabilityMetric` operation. See the code for the full implementation.

### `getColorForValue`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `27-37`
- **Purpose:** Retrieves ColorForValue.

**Code:**
```jsx
function getColorForValue(value) {
  if (value === null || value === undefined) {
    return "var(--map-no-data)";
  }
  // 5-tier classification for all suitability metrics
  if (value >= 81) return "var(--map-very-high)";
  if (value >= 61) return "var(--map-high)";
  if (value >= 41) return "var(--map-moderate)";
  if (value >= 21) return "var(--map-low)";
  return "var(--map-very-low)";
}
```

**Explanation:** This function retrieves ColorForValue. See the code for the full implementation.

### `getClassificationLabel`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `39-48`
- **Purpose:** Retrieves ClassificationLabel.

**Code:**
```jsx
function getClassificationLabel(value, t) {
  let key;
  if (value === null || value === undefined) key = "noData";
  else if (value >= 81) key = "veryHigh";
  else if (value >= 61) key = "high";
  else if (value >= 41) key = "moderate";
  else if (value >= 21) key = "low";
  else key = "veryLow";
  return t(`energyHub.map.classification.${key}`);
}
```

**Explanation:** This function retrieves ClassificationLabel. See the code for the full implementation.

### `formatFactors`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `50-65`
- **Purpose:** Converts Factors.

**Code:**
```jsx
function formatFactors(factors) {
  // Supabase JSONB may return a string; parse lazily
  let parsed = factors;
  if (typeof factors === "string") {
    try { parsed = JSON.parse(factors); } catch { return factors; }
  }
  if (!parsed || typeof parsed !== "object") return "";
  const parts = [];
  for (const [key, val] of Object.entries(parsed)) {
    if (val !== null && val !== undefined) {
      const label = key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase());
      parts.push(`${label}: ${val}`);
    }
  }
  return parts.join("<br/>");
}
```

**Explanation:** This function converts Factors. See the code for the full implementation.

### `fetchGeoJsonCached`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `72-94`
- **Purpose:** Retrieves GeoJsonCached.

**Code:**
```jsx
async function fetchGeoJsonCached(url) {
  const cacheKey = `lumi_geojson_${url}`;
  try {
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      const { ts, data } = JSON.parse(cached);
      if (Date.now() - ts < GEOJSON_CACHE_TTL_MS) {
        return data;
      }
    }
  } catch {
    // ignore parse errors
  }
  const resp = await fetch(url);
  if (!resp.ok) return null;
  const data = await resp.json();
  try {
    localStorage.setItem(cacheKey, JSON.stringify({ ts: Date.now(), data }));
  } catch {
    // ignore quota errors
  }
  return data;
}
```

**Explanation:** This function retrieves GeoJsonCached. See the code for the full implementation.

### `removeAccents`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `96-100`
- **Purpose:** Removes Accents.

**Code:**
```jsx
function removeAccents(str) {
  return str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}
```

**Explanation:** This function removes Accents. See the code for the full implementation.

### `normalizeGeoName`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `102-117`
- **Purpose:** Converts GeoName.

**Code:**
```jsx
function normalizeGeoName(name) {
  if (!name) return "";
  return removeAccents(name)
    .toLowerCase()
    .trim()
    .replace(/^city of\s+/i, "")
    .replace(/^municipality of\s+/i, "")
    .replace(/\s+capital$/i, "")
    .replace(/\s+\(capital\)$/i, "")
    .replace(/\bsta\.?\b/g, "santa")
    .replace(/\bsto\.?\b/g, "santo")
    .replace(/\bsan\b/g, "san")
    .replace(/[-']/g, "")
    .replace(/\s+/g, " ")
    .trim();
}
```

**Explanation:** This function converts GeoName. See the code for the full implementation.

### `computeCentroid`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `122-142`
- **Purpose:** Calculates Centroid.

**Code:**
```jsx
function computeCentroid(geometry) {
  if (!geometry?.coordinates) return { lat: 0, lon: 0 };
  const coords = geometry.coordinates;
  const lats = [];
  const lons = [];

  function visit(c) {
    if (Array.isArray(c[0])) {
      c.forEach(visit);
    } else {
      lons.push(c[0]);
      lats.push(c[1]);
    }
  }
  visit(coords);

  if (lats.length === 0) return { lat: 0, lon: 0 };
  const lat = lats.reduce((a, b) => a + b, 0) / lats.length;
  const lon = lons.reduce((a, b) => a + b, 0) / lons.length;
  return { lat, lon };
}
```

**Explanation:** This function calculates Centroid. See the code for the full implementation.

### `matchByCoordinates`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `144-198`
- **Purpose:** Utility function `matchByCoordinates`.

**Code:**
```jsx
function matchByCoordinates(geojson, data, maxDeg = 0.8) {
  // maxDeg ≈ 0.8° ≈ 90 km radius — generous enough for municipality centroids
  if (!geojson?.features || !data?.length) return {};

  // 1. Pre-compute centroids (skip null geometries), build lookup by original index
  const centroidByIdx = new Map();
  const centroidList = [];
  geojson.features.forEach((f, idx) => {
    const c = computeCentroid(f.geometry);
    if (c.lat !== 0 || c.lon !== 0) {
      const entry = { idx, ...c };
      centroidByIdx.set(idx, entry);
      centroidList.push(entry);
    }
  });

  // 2. For each data item, find nearest centroid
  const map = {};
  for (const item of data) {
    if (item.lat == null || item.lon == null) continue;

    let bestIdx = -1;
    let bestDist = Infinity;

    for (const c of centroidList) {
      const dLat = c.lat - item.lat;
      const dLon = c.lon - item.lon;
      const dist = dLat * dLat + dLon * dLon;
      if (dist < bestDist) {
        bestDist = dist;
        bestIdx = c.idx;
      }
    }

    if (bestIdx >= 0 && bestDist <= maxDeg * maxDeg) {
      // Prefer coordinate match, but if a feature already has a closer item, keep closer
      const existing = map[bestIdx];
      if (!existing) {
        map[bestIdx] = item;
      } else {
        const cent = centroidByIdx.get(bestIdx);
        if (cent) {
          const dLatE = cent.lat - existing.lat;
          const dLonE = cent.lon - existing.lon;
          const distE = dLatE * dLatE + dLonE * dLonE;
          if (bestDist < distE) {
            map[bestIdx] = item;
          }
        }
      }
    }
  }

  return map;
}
```

**Explanation:** This helper performs the `matchByCoordinates` operation. See the code for the full implementation.

### `FallbackMapGrid`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `200-231`
- **Purpose:** Renders the `FallbackMapGrid` component.

**Code:**
```jsx
function FallbackMapGrid({ data, metric, level }) {
  const { t } = useI18n();
  if (!data || data.length === 0) return null;
  const labelKey = level === "municipality" ? "municipality" : "province";
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
      {data.map((item, idx) => {
        const hasData = item.value !== null && item.value !== undefined;
        const displayName = item[labelKey] || item.province || item.region;
        return (
          <div
            key={`${item.region}-${item.province || idx}-${item.municipality || ""}`}
            className="rounded-lg border p-3 text-center transition-transform hover:scale-[1.02]"
            style={{ borderLeft: `4px solid ${getColorForValue(item.value)}` }}
          >
            <p className="text-xs text-muted-foreground truncate">
              {displayName}
            </p>
            <p className="mt-1 text-lg font-bold" style={{ color: getColorForValue(item.value) }}>
              {hasData ? `${item.value}` : t("energyHub.map.na")}
              {hasData && <span className="text-xs ml-0.5">{t("energyHub.map.unit")}</span>}
            </p>
            {hasData && (
              <p className="text-[10px] text-muted-foreground">{getClassificationLabel(item.value, t)}</p>
            )}
            <p className="text-[10px] text-muted-foreground uppercase tracking-wide">{t(`energyHub.map.metrics.${metric}`)}</p>
          </div>
        );
      })}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `FallbackMapGrid` view or widget.

### `LeafletMap`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `233-502`
- **Purpose:** Renders the `LeafletMap` component.

**Code:**
```jsx
function LeafletMap({ data, metric, level, geothermalPlants = [], overlays = {} }) {
  const { t } = useI18n();
  const [L, setL] = useState(null);
  const [RL, setRL] = useState(null);
  const [rawGeojson, setRawGeojson] = useState(null);
  const [volcanoGeojson, setVolcanoGeojson] = useState(null);

  const geojsonUrl =
    level === "municipality"
      ? "/philippine_geojson_file_per_provinces.min.json"
      : "/philippine_geojson_file_per_region.json";

  const nameProperty = level === "municipality" ? "adm3_en" : "adm2_en";

  // 1. Name-based lookup (fallback)
  const nameLookup = useMemo(() => {
    const map = {};
    for (const item of data) {
      const rawName = level === "municipality"
        ? item.municipality || ""
        : item.province || "";
      const key = normalizeGeoName(rawName);
      const altKey = rawName.toLowerCase().trim();
      if (key) {
        const entry = {
          value: item.value,
          classification: item.classification,
          factors: item.factors,
          province: item.province,
          municipality: item.municipality,
        };
        map[key] = entry;
        map[altKey] = entry;
      }
    }
    return map;
  }, [data, level]);

  // 2. Coordinate-based matching (primary) + name fallback
  const enrichedGeojson = useMemo(() => {
    if (!rawGeojson?.features) return null;

    const coordMap = matchByCoordinates(rawGeojson, data);

    const features = rawGeojson.features.map((feature, idx) => {
      // Try coordinate match first
      let matched = coordMap[idx];

      // Fallback to name match
      if (!matched) {
        const name = normalizeGeoName(feature.properties?.[nameProperty] || "");
        matched = nameLookup[name];
      }

      return {
        ...feature,
        properties: {
          ...feature.properties,
          _lumi_data: matched || null,
        },
      };
    });

    return { ...rawGeojson, features };
  }, [rawGeojson, data, nameLookup, nameProperty]);

  // Load volcano GeoJSON once
  useEffect(() => {
    let mounted = true;
    fetchGeoJsonCached("/geothermal_volcanoes.json")
      .then((volcanoData) => {
        if (mounted) setVolcanoGeojson(volcanoData);
      })
      .catch(() => {});
    return () => {
      mounted = false;
    };
  }, []);

  // Load Leaflet + GeoJSON once per level change
  useEffect(() => {
    let mounted = true;
    setRawGeojson(null);
    Promise.all([
      import("leaflet"),
      import("react-leaflet"),
      fetchGeoJsonCached(geojsonUrl),
    ])
      .then(([leafletMod, reactLeafletMod, geoData]) => {
        if (!mounted) return;
        const leaflet = leafletMod.default || leafletMod;
        const rl = reactLeafletMod;
        setL(leaflet);
        setRL(rl);
        setRawGeojson(geoData);
      })
      .catch(() => {
        // Silently fall back
      });
    return () => {
      mounted = false;
    };
  }, [geojsonUrl]);

  if (!L || !RL || !enrichedGeojson) {
    return <FallbackMapGrid data={data} metric={metric} level={level} />;
  }

  const { MapContainer, TileLayer, GeoJSON, ImageOverlay } = RL;

  const styleFeature = (feature) => {
    const item = feature.properties?._lumi_data;
    const val = item?.value ?? null;
    return {
      fillColor: getColorForValue(val),
      weight: level === "municipality" ? 0.6 : 1.5,
      opacity: 1,
      color: "var(--border)",
      dashArray: "",
      fillOpacity: level === "municipality" ? 0.6 : 0.65,
    };
  };

  const onEachFeature = (feature, layer) => {
    const geoName = feature.properties?.[nameProperty] || t("energyHub.map.unknown");
    const item = feature.properties?._lumi_data;
    const hasData = item && item.value !== null && item.value !== undefined;
    const displayName = item?.municipality || geoName;
    const province = item?.province || "";

    let tooltipHtml = `<div style="font-family:sans-serif;font-size:13px;line-height:1.4;min-width:160px">
      <div style="font-size:14px;font-weight:600;color:var(--foreground);margin-bottom:2px">${displayName}</div>`;

    if (level === "municipality" && province) {
      tooltipHtml += `<div style="color:var(--muted-foreground);font-size:12px;margin-bottom:4px">${province}</div>`;
    }

    if (hasData) {
      const unit = t("energyHub.map.unit");
      const color = getColorForValue(item.value);
      tooltipHtml += `<div style="margin-top:4px">
        <span style="color:var(--muted-foreground);font-size:12px">${t(`energyHub.map.metrics.${metric}`)}:</span>
        <strong style="font-size:14px;color:${color}">${item.value.toLocaleString()}${unit}</strong>
      </div>`;
      tooltipHtml += `<div style="margin-top:2px;font-size:12px;color:${color};font-weight:500">${getClassificationLabel(item.value, t)}</div>`;
      const factorsHtml = formatFactors(item.factors);
      if (factorsHtml) {
        tooltipHtml += `<div style="margin-top:6px;padding-top:4px;border-top:1px solid var(--border);color:var(--muted-foreground);font-size:11px;line-height:1.5">${factorsHtml}</div>`;
      }
    } else {
      tooltipHtml += `<div style="margin-top:4px;color:var(--map-no-data);font-size:12px">${t("energyHub.map.classification.noData")}</div>`;
    }

    tooltipHtml += `</div>`;
    layer.bindTooltip(tooltipHtml, { sticky: true, className: "lumi-tooltip" });
  };

  const showVolcanoes = overlays.volcanoes?.visible;

  const volcanoPointToLayer = (feature, latlng) => {
    return L.circleMarker(latlng, {
      radius: 6,
      color: "var(--chart-geothermal)",
      fillColor: "var(--chart-geothermal)",
      fillOpacity: 0.8,
      weight: 2,
    });
  };

  const onEachVolcano = (feature, layer) => {
    const name = feature.properties?.name || t("energyHub.map.volcano");
    const province = feature.properties?.province || "";
    const tooltipHtml = `<div style="font-family:sans-serif;font-size:13px;line-height:1.4;min-width:140px">
      <div style="font-size:14px;font-weight:600;color:var(--foreground)">${name}</div>
      ${province ? `<div style="color:var(--muted-foreground);font-size:12px">${province}</div>` : ""}
    </div>`;
    layer.bindTooltip(tooltipHtml, { sticky: true, className: "lumi-tooltip" });
  };

  // Filter operating plants for markers
  const showPlantMarkers = metric === "geothermal_potential";
  const operatingPlants = geothermalPlants.filter((p) => p.status === "operating");

  return (
    <div className="rounded-xl border overflow-hidden" style={{ height: 480 }}>
      <MapContainer
        center={[12.8797, 121.774]}
        zoom={level === "municipality" ? 7 : 6}
        scrollWheelZoom={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        <GeoJSON data={enrichedGeojson} style={styleFeature} onEachFeature={onEachFeature} />
        {showPlantMarkers && L && RL && operatingPlants.map((p) => {
          const icon = L.divIcon({
            className: "",
            html: `<div style="width:14px;height:14px;border-radius:50%;background:var(--chart-geothermal);border:2px solid var(--map-marker-stroke);box-shadow:0 1px 3px rgba(0,0,0,0.3);"></div>`,
            iconSize: [14, 14],
            iconAnchor: [7, 7],
          });
          return (
            <RL.Marker
              key={p.project_name + (p.unit_name || "")}
              position={[p.latitude, p.longitude]}
              icon={icon}
            >
              <RL.Popup>
                <div style={{ fontFamily: "sans-serif", fontSize: 13, lineHeight: 1.4, minWidth: 160 }}>
                  <div style={{ fontWeight: 600, color: "var(--foreground)", marginBottom: 4 }}>
                    {p.project_name}
                  </div>
                  <div style={{ color: "var(--muted-foreground)", fontSize: 12 }}>
                    {p.capacity_mw !== null && p.capacity_mw !== undefined ? `${p.capacity_mw} MW` : ""}
                    {p.technology ? ` · ${p.technology}` : ""}
                  </div>
                  <div style={{ color: "var(--muted-foreground)", fontSize: 12, marginTop: 2 }}>
                    {t("energyHub.map.status")}: <span style={{ color: "var(--primary)", fontWeight: 500 }}>{p.status}</span>
                  </div>
                  {p.wiki_url && (
                    <div style={{ marginTop: 6 }}>
                      <a
                        href={p.wiki_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ color: "var(--primary)", fontSize: 12 }}
                      >
                        {t("energyHub.map.viewOnGemWiki")}
                      </a>
                    </div>
                  )}
                </div>
              </RL.Popup>
            </RL.Marker>
          );
        })}
        {/* Geothermal raster overlays (volcanoes, faults) */}
        {overlays.volcanoes?.visible && overlays.volcanoes?.bounds && (
          <ImageOverlay
            url={overlays.volcanoes.url}
            bounds={[
              [overlays.volcanoes.bounds.south, overlays.volcanoes.bounds.west],
              [overlays.volcanoes.bounds.north, overlays.volcanoes.bounds.east],
            ]}
            opacity={0.5}
          />
        )}
        {overlays.faults?.visible && overlays.faults?.bounds && (
          <ImageOverlay
            url={overlays.faults.url}
            bounds={[
              [overlays.faults.bounds.south, overlays.faults.bounds.west],
              [overlays.faults.bounds.north, overlays.faults.bounds.east],
            ]}
            opacity={0.5}
          />
        )}
        {showVolcanoes && volcanoGeojson && (
          <GeoJSON
            data={volcanoGeojson}
            pointToLayer={volcanoPointToLayer}
            onEachFeature={onEachVolcano}
          />
        )}
      </MapContainer>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `LeafletMap` view or widget.

### `EnergyMap`

- **File:** `react-frontend/src/components/energyhub/EnergyMap.jsx`
- **Lines:** `504-662`
- **Purpose:** Renders the `EnergyMap` component.

**Code:**
```jsx
function EnergyMap({ mapData, metric, level, onMetricChange, onLevelChange, mapLoading = false, geothermalPlants = [] }) {
  const { t } = useI18n();
  const [leafletReady, setLeafletReady] = useState(false);
  const [overlayManifest, setOverlayManifest] = useState(null);
  const [showVolcanoes, setShowVolcanoes] = useState(false);
  const [showFaults, setShowFaults] = useState(false);

  useEffect(() => {
    import("leaflet")
      .then(() => setLeafletReady(true))
      .catch(() => setLeafletReady(false));
  }, []);

  // Fetch overlay manifest once
  useEffect(() => {
    fetch("/geothermal_overlays.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => setOverlayManifest(data))
      .catch(() => setOverlayManifest(null));
  }, []);

  const data = mapData?.items || [];

  const showSuitabilityLegend = isSuitabilityMetric(metric);
  const isGeothermal = metric === "geothermal_potential";

  const overlays = {
    volcanoes: overlayManifest?.volcanoes
      ? {
          url: `/${overlayManifest.volcanoes.png_filename}`,
          bounds: overlayManifest.volcanoes.bounds,
          visible: showVolcanoes,
        }
      : null,
    faults: overlayManifest?.faults
      ? {
          url: `/${overlayManifest.faults.png_filename}`,
          bounds: overlayManifest.faults.bounds,
          visible: showFaults,
        }
      : null,
  };

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <MapPin className="h-5 w-5 text-primary" />
            {t("energyHub.map.title")}
          </h3>
          <p className="text-sm text-muted-foreground">
            {t("energyHub.map.subtitle", { level: t(`energyHub.map.levels.${level}`) })}
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {/* Level toggle */}
          <div className="flex items-center gap-1.5 rounded-md border bg-background px-2 py-1">
            <MapIcon className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              className="bg-transparent text-sm focus:outline-none"
              value={level}
              onChange={(e) => onLevelChange(e.target.value)}
            >
              {LEVEL_KEYS.map((key) => (
                <option key={key} value={key}>
                  {t(`energyHub.map.levels.${key}`)}
                </option>
              ))}
            </select>
          </div>

          {/* Metric selector */}
          <div className="flex items-center gap-1.5 rounded-md border bg-background px-2 py-1">
            <Layers className="h-3.5 w-3.5 text-muted-foreground" />
            <select
              className="bg-transparent text-sm focus:outline-none"
              value={metric}
              onChange={(e) => onMetricChange(e.target.value)}
            >
              {METRIC_KEYS.map((key) => (
                <option key={key} value={key}>
                  {t(`energyHub.map.metrics.${key}`)}
                </option>
              ))}
            </select>
          </div>

          {/* Overlay toggles (only when geothermal metric selected) */}
          {isGeothermal && overlayManifest && (
            <>
              <button
                type="button"
                onClick={() => setShowVolcanoes((v) => !v)}
                className={`flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium transition-colors ${
                  showVolcanoes
                    ? "bg-destructive/10 border-destructive/20 text-foreground"
                    : "bg-background border-muted text-muted-foreground hover:bg-muted"
                }`}
                title={t("energyHub.map.toggleVolcanoes")}
              >
                <span className="inline-block h-2 w-2 rounded-full bg-destructive" />
                {t("energyHub.map.volcanoes")}
              </button>
              <button
                type="button"
                onClick={() => setShowFaults((v) => !v)}
                className={`flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-medium transition-colors ${
                  showFaults
                    ? "bg-chart-geothermal/10 border-chart-geothermal/20 text-foreground"
                    : "bg-background border-muted text-muted-foreground hover:bg-muted"
                }`}
                title={t("energyHub.map.toggleFaults")}
              >
                <span className="inline-block h-2 w-2 rounded-full bg-chart-geothermal" />
                {t("energyHub.map.faults")}
              </button>
            </>
          )}
        </div>
      </div>

      {mapLoading && (
        <div className="mt-4 flex items-center justify-center gap-2 text-sm text-muted-foreground" style={{ height: 480 }}>
          <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
          {t("energyHub.map.loading")}
        </div>
      )}

      {!mapLoading && (
        <div className="mt-4">
          {leafletReady ? (
            <LeafletMap data={data} metric={metric} level={level} geothermalPlants={geothermalPlants} overlays={overlays} />
          ) : (
            <FallbackMapGrid data={data} metric={metric} level={level} />
          )}
        </div>
      )}

      {showSuitabilityLegend && (
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-muted-foreground">
          {[
            { key: "veryHigh", cls: "bg-map-very-high" },
            { key: "high", cls: "bg-map-high" },
            { key: "moderate", cls: "bg-map-moderate" },
            { key: "low", cls: "bg-map-low" },
            { key: "veryLow", cls: "bg-map-very-low" },
            { key: "noData", cls: "bg-map-no-data" },
          ].map((item) => (
            <span key={item.key} className="inline-flex items-center gap-1">
              <span className={`inline-block h-3 w-3 rounded-sm ${item.cls}`} />
              {t(`energyHub.map.legend.${item.key}`)}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EnergyMap` view or widget.

## `react-frontend/src/components/energyhub/EnergyOverview.jsx`

### `EnergyOverview`

- **File:** `react-frontend/src/components/energyhub/EnergyOverview.jsx`
- **Lines:** `4-91`
- **Purpose:** Renders the `EnergyOverview` component.

**Code:**
```jsx
export default function EnergyOverview({ data }) {
  const { t } = useI18n();
  if (!data || !data.latest) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="h-32 bg-muted rounded-xl animate-pulse" />
        ))}
      </div>
    );
  }

  const { latest, forecast_summary } = data;

  const cards = [
    {
      label: t("energyHub.overview.consumption.label"),
      value: t("energyHub.overview.consumption.value", { value: latest.total_consumption_gwh.toLocaleString() }),
      sub: t("energyHub.overview.consumption.sub", { year: latest.year }),
      interpretation: t("energyHub.overview.consumption.interpretation", { value: latest.total_consumption_gwh.toLocaleString(), year: latest.year }),
      icon: Zap,
      color: "text-amber-500",
      bg: "bg-amber-50",
    },
    {
      label: t("energyHub.overview.peakDemand.label"),
      value: t("energyHub.overview.peakDemand.value", { value: latest.total_peak_demand_mw.toLocaleString() }),
      sub: t("energyHub.overview.peakDemand.sub", { year: latest.year }),
      interpretation: t("energyHub.overview.peakDemand.interpretation"),
      icon: Activity,
      color: "text-rose-500",
      bg: "bg-rose-50",
    },
    {
      label: t("energyHub.overview.renewableShare.label"),
      value: t("energyHub.overview.renewableShare.value", { share: latest.renewable_share_pct }),
      sub: t("energyHub.overview.renewableShare.sub", { generated: latest.renewable_generation_gwh.toLocaleString() }),
      interpretation: t("energyHub.overview.renewableShare.interpretation", { share: latest.renewable_share_pct }),
      icon: Sun,
      color: "text-emerald-500",
      bg: "bg-emerald-50",
    },
    {
      label: t("energyHub.overview.forecastGrowth.label"),
      value: t("energyHub.overview.forecastGrowth.value", {
        value: forecast_summary?.forecast_growth_pct
          ? `+${forecast_summary.forecast_growth_pct}%`
          : t("energyHub.overview.forecastGrowth.na")
      }),
      sub: forecast_summary?.forecast_2030_gwh
        ? t("energyHub.overview.forecastGrowth.sub", { value: forecast_summary.forecast_2030_gwh.toLocaleString() })
        : t("energyHub.overview.forecastGrowth.subEmpty"),
      interpretation: forecast_summary?.forecast_growth_pct
        ? t("energyHub.overview.forecastGrowth.interpretation", { pct: forecast_summary.forecast_growth_pct })
        : t("energyHub.overview.forecastGrowth.interpretationFallback"),
      icon: TrendingUp,
      color: "text-sky-500",
      bg: "bg-sky-50",
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => (
        <div
          key={card.label}
          className="rounded-xl border bg-card p-5 shadow-sm transition-shadow hover:shadow-md"
        >
          <div className="flex items-start justify-between">
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-muted-foreground">{card.label}</p>
              <p className="mt-1 text-2xl font-bold tracking-tight">{card.value}</p>
              <p className="mt-0.5 text-xs text-muted-foreground">{card.sub}</p>
              {card.interpretation && (
                <p className="mt-2 text-xs text-slate-600 leading-relaxed border-t pt-2 border-slate-100">
                  {card.interpretation}
                </p>
              )}
            </div>
            <div className={`rounded-lg p-2.5 ${card.bg} shrink-0 ml-3`}>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EnergyOverview` view or widget.

## `react-frontend/src/components/energyhub/EnergySources.jsx`

### `EnergySources`

- **File:** `react-frontend/src/components/energyhub/EnergySources.jsx`
- **Lines:** `17-122`
- **Purpose:** Renders the `EnergySources` component.

**Code:**
```jsx
export default function EnergySources({ breakdown }) {
  const { t } = useI18n();
  const chartData = useMemo(() => {
    if (!breakdown || !breakdown.share_pct) return [];
    const entries = Object.entries(breakdown.share_pct)
      .filter(([, v]) => v > 0)
      .sort(([, a], [, b]) => b - a);

    return entries.map(([key, value]) => ({
      key,
      label: t(`energyHub.sources.labels.${key}`) || key,
      color: SOURCE_META[key]?.color || "#cbd5e1",
      share: value,
      gwh: breakdown.generation_gwh?.[key] || 0,
    }));
  }, [breakdown, t]);

  const plotlyData = useMemo(() => {
    if (chartData.length === 0) return [];
    return [
      {
        values: chartData.map((d) => d.share),
        labels: chartData.map((d) => d.label),
        type: "pie",
        hole: 0.55,
        marker: { colors: chartData.map((d) => d.color) },
        textinfo: "percent",
        textposition: "inside",
        insidetextorientation: "radial",
        textfont: { size: 11, color: "#ffffff" },
        hovertemplate: t("energyHub.sources.hover", { value: "%{value}", gwh: "%{customdata:,.0f}" }),
        customdata: chartData.map((d) => d.gwh),
        showlegend: false,
        sort: false,
      },
    ];
  }, [chartData]);

  const plotlyLayout = useMemo(
    () => ({
      showlegend: false,
      margin: { t: 12, r: 12, b: 12, l: 12 },
      annotations: [
        {
          text: `<b>${breakdown?.year || ""}</b><br><span style="font-size:11px;color:#64748b">GWh</span>`,
          showarrow: false,
          font: { size: 20, color: "#1e293b", family: "Inter, sans-serif" },
        },
      ],
    }),
    [breakdown]
  );

  if (!breakdown || chartData.length === 0) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold">{t("energyHub.sources.title")}</h3>
        <div className="mt-4 h-48 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <h3 className="text-lg font-semibold">
        {t("energyHub.sources.title")} ({breakdown.year})
      </h3>
      <p className="text-sm text-muted-foreground">
        {t("energyHub.sources.totalGeneration", { value: breakdown.total_generation_gwh.toLocaleString() })}
      </p>
      <ChartExplanation
        what={t("energyHub.sources.explanation.what")}
        why={t("energyHub.sources.explanation.why")}
        action={t("energyHub.sources.explanation.action")}
      />

      <div className="mt-4 flex flex-col md:flex-row items-center gap-6">
        <div className="w-80 h-80 shrink-0">
          <PlotlyChart data={plotlyData} layout={plotlyLayout} />
        </div>

        <div className="flex-1 w-full">
          <div className="space-y-2.5">
            {chartData.map((d) => (
              <div key={d.key} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block h-3 w-3 rounded-sm"
                    style={{ backgroundColor: d.color }}
                  />
                  <span className="text-sm font-medium">{d.label}</span>
                </div>
                <div className="text-right min-w-[70px]">
                  <span className="text-sm font-semibold">{d.share}%</span>
                  <span className="ml-4 text-xs text-muted-foreground">
                    {d.gwh.toLocaleString()} GWh
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EnergySources` view or widget.

## `react-frontend/src/components/energyhub/EnergyTrends.jsx`

### `sanitizeLLMOutput`

- **File:** `react-frontend/src/components/energyhub/EnergyTrends.jsx`
- **Lines:** `7-38`
- **Purpose:** Utility function `sanitizeLLMOutput`.

**Code:**
```jsx
function sanitizeLLMOutput(text = "") {
  if (!text) return "";
  let t = text;

  // Remove repetitive greeting lines that appear in every panel
  t = t.replace(/Hello there! I'm LUMI, your friendly energy advisor\.\s*Let's chat about.*?\n*/is, "");
  t = t.replace(/Hi there! I'm LUMI.*?\n*/is, "");

  // Normalize repeated "Recommendation 1:" blocks into a single numbered list
  // When the LLM restarts numbering mid-text, renumber them sequentially
  const recBlocks = [];
  const recRegex = /\*?\s*\*\*?\s*Recommendation\s*(\d+)[:\.*\-]*\s*\*?\*?\s*(.*?)(?=\*?\s*\*\*?\s*Recommendation\s*\d+[:\.*\-]*|$)/gis;
  let m;
  while ((m = recRegex.exec(t)) !== null) {
    recBlocks.push(m[2].trim());
  }
  if (recBlocks.length > 0) {
    const numbered = recBlocks.map((b, i) => `${i + 1}. ${b.replace(/\n+/g, " ")}`).join("\n");
    t = t.replace(/\*?\s*\*\*?\s*Recommendation\s*\d+[:\.*\-]*\s*\*?\*?\s*.*/gis, "").trim();
    t = t + "\n\nRecommendations:\n" + numbered;
  }

  // Collapse multiple blank lines into one
  t = t.replace(/\n{3,}/g, "\n\n");

  // Trim to a reasonable length for panel display (soft cap ~800 chars)
  if (t.length > 900) {
    t = t.slice(0, 900).replace(/\s+\S*$/, "") + "…";
  }

  return t.trim();
}
```

**Explanation:** This helper performs the `sanitizeLLMOutput` operation. See the code for the full implementation.

### `ChartAiPanel`

- **File:** `react-frontend/src/components/energyhub/EnergyTrends.jsx`
- **Lines:** `40-80`
- **Purpose:** Renders the `ChartAiPanel` component.

**Code:**
```jsx
function ChartAiPanel({ chartKey, analysis, onAnalyze, onRefresh, loading }) {
  const { t } = useI18n();
  if (!analysis && !loading) {
    return (
      <button
        onClick={onAnalyze}
        className="mt-2 inline-flex items-center gap-1.5 rounded-md bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 border border-amber-200 hover:bg-amber-100 transition-colors"
      >
        <Sparkles className="h-3 w-3" />
        {t("energyHub.trends.aiExplain")}
      </button>
    );
  }

  if (loading) {
    return (
      <div className="mt-2 inline-flex items-center gap-2 rounded-md bg-amber-50 px-3 py-2 text-xs text-amber-700 border border-amber-200">
        <Loader2 className="h-3 w-3 animate-spin" />
        {t("energyHub.trends.generating")}
      </div>
    );
  }

  return (
    <div className="mt-2 rounded-lg bg-amber-50 border border-amber-100 p-3">
      <div className="flex items-start justify-between gap-2">
        <p className="text-xs leading-relaxed text-amber-900 whitespace-pre-line flex-1">{sanitizeLLMOutput(analysis?.insight)}</p>
        {onRefresh && (
          <button
            onClick={onRefresh}
            title={t("energyHub.trends.getDifferent")}
            className="shrink-0 inline-flex items-center gap-1 rounded-md bg-amber-100 px-2 py-1 text-[10px] font-medium text-amber-700 border border-amber-200 hover:bg-amber-200 transition-colors"
          >
            <Sparkles className="h-3 w-3" />
            {t("energyHub.trends.refresh")}
          </button>
        )}
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `ChartAiPanel` view or widget.

### `EnergyTrends`

- **File:** `react-frontend/src/components/energyhub/EnergyTrends.jsx`
- **Lines:** `82-309`
- **Purpose:** Renders the `EnergyTrends` component.

**Code:**
```jsx
export default function EnergyTrends({ trends, chartAnalyses, llmLoading, onAnalyzeChart }) {
  const { t } = useI18n();
  const years = trends?.years || [];
  const series = trends?.series || {};
  const forecast = trends?.forecast || {};

  const consumptionSeries = useMemo(() => {
    const hist = series.total_consumption_gwh || [];
    const fYears = forecast.forecast_years || [];
    const fValues = forecast.forecast_values || [];
    return {
      years: [...years, ...fYears],
      values: [...hist, ...fValues],
      isForecast: [...Array(hist.length).fill(false), ...Array(fValues.length).fill(true)],
    };
  }, [years, series, forecast]);

  const consumptionTraces = useMemo(() => {
    const allYears = consumptionSeries.years;
    const allValues = consumptionSeries.values;
    const isF = consumptionSeries.isForecast;

    const histX = [];
    const histY = [];
    const forecastX = [];
    const forecastY = [];

    for (let i = 0; i < allYears.length; i++) {
      if (isF[i]) {
        forecastX.push(allYears[i]);
        forecastY.push(allValues[i]);
      } else {
        histX.push(allYears[i]);
        histY.push(allValues[i]);
      }
    }

    // Junction point for continuity
    if (histX.length > 0 && forecastX.length > 0) {
      forecastX.unshift(histX[histX.length - 1]);
      forecastY.unshift(histY[histY.length - 1]);
    }

    return [
      {
        x: histX,
        y: histY,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.legend.historical"),
        line: { color: "#3b82f6", width: 3 },
        marker: { size: 6 },
        hovertemplate: t("energyHub.trends.hover.consumption", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.historical") }),
      },
      {
        x: forecastX,
        y: forecastY,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.legend.forecast"),
        line: { color: "#f87171", width: 3, dash: "dash" },
        marker: { size: 6 },
        hovertemplate: t("energyHub.trends.hover.consumption", { year: "%{x}", value: "%{y:,.0f}", extra: t("energyHub.trends.legend.forecast") }),
      },
    ];
  }, [consumptionSeries, t]);

  const consumptionLayout = useMemo(
    () => ({
      title: { text: "", font: { size: 14 } },
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.gwh") },
      legend: { orientation: "v", x: 1, xanchor: "right", y: 1, yanchor: "top", font: { size: 11 } },
      margin: { t: 16, r: 100, b: 40, l: 56 },
    }),
    [t]
  );

  const peakDemandTrace = useMemo(() => {
    const vals = series.total_peak_demand_mw || [];
    return [
      {
        x: years,
        y: vals,
        type: "scatter",
        mode: "lines+markers",
        name: t("energyHub.trends.peakDemand.title"),
        line: { color: "#f43f5e", width: 2 },
        marker: { size: 5 },
        hovertemplate: t("energyHub.trends.hover.peakDemand", { year: "%{x}", value: "%{y:,.0f}" }),
      },
    ];
  }, [years, series, t]);

  const peakDemandLayout = useMemo(
    () => ({
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.mw") },
      legend: { orientation: "v", x: 1, xanchor: "right", y: 1, yanchor: "top", font: { size: 11 } },
      margin: { t: 16, r: 100, b: 40, l: 56 },
    }),
    [t]
  );

  const renewableGenTrace = useMemo(() => {
    const vals = series.renewable_generation_gwh || [];
    return [
      {
        x: years,
        y: vals,
        type: "bar",
        name: t("energyHub.trends.renewable.title"),
        marker: { color: "#10b981" },
        hovertemplate: t("energyHub.trends.hover.renewable", { year: "%{x}", value: "%{y:,.0f}" }),
      },
    ];
  }, [years, series, t]);

  const renewableGenLayout = useMemo(
    () => ({
      xaxis: { title: t("energyHub.trends.chartAxis.year"), tickmode: "linear", dtick: 1 },
      yaxis: { title: t("energyHub.trends.chartAxis.gwh") },
      legend: { orientation: "v", x: 1, xanchor: "right", y: 1, yanchor: "top", font: { size: 11 } },
      margin: { t: 16, r: 120, b: 40, l: 56 },
    }),
    [t]
  );

  if (!years.length) {
    return (
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="text-lg font-semibold">{t("energyHub.trends.title")}</h3>
        <div className="mt-4 h-48 bg-muted rounded-lg animate-pulse" />
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-6 shadow-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">{t("energyHub.trends.title")}</h3>
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-blue-500" />
            {t("energyHub.trends.legend.historical")}
          </span>
          <span className="inline-flex items-center gap-1">
            <span className="inline-block h-2 w-2 rounded-full bg-red-400" />
            {t("energyHub.trends.legend.forecast")}
          </span>
        </div>
      </div>

      {/* Consumption trend */}
      <div className="mt-4">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-foreground">{t("energyHub.trends.consumption.title")}</p>
            <p className="text-xs text-muted-foreground">{t("energyHub.trends.consumption.subtitle")}</p>
          </div>
        </div>
        <ChartExplanation
          what={t("energyHub.trends.consumption.explanation.what")}
          why={t("energyHub.trends.consumption.explanation.why")}
          action={t("energyHub.trends.consumption.explanation.action")}
        />
        <div className="relative rounded-lg border bg-white p-3 h-64 overflow-hidden">
          <PlotlyChart data={consumptionTraces} layout={consumptionLayout} />
        </div>
        {onAnalyzeChart && (
          <ChartAiPanel
            chartKey="consumption_trend"
            analysis={chartAnalyses?.consumption_trend}
            onAnalyze={() => onAnalyzeChart("consumption_trend")}
            onRefresh={() => onAnalyzeChart("consumption_trend", true)}
            loading={llmLoading?.["consumption_trend"] || false}
          />
        )}
      </div>

      {/* Peak demand + Renewable generation */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <p className="text-sm font-semibold text-foreground">{t("energyHub.trends.peakDemand.title")}</p>
          <p className="text-xs text-muted-foreground mb-2">{t("energyHub.trends.peakDemand.subtitle")}</p>
          <ChartExplanation
            what={t("energyHub.trends.peakDemand.explanation.what")}
            why={t("energyHub.trends.peakDemand.explanation.why")}
            action={t("energyHub.trends.peakDemand.explanation.action")}
          />
          <div className="rounded-lg border bg-white p-3 h-52 overflow-hidden">
            <PlotlyChart data={peakDemandTrace} layout={peakDemandLayout} />
          </div>
          {onAnalyzeChart && (
            <ChartAiPanel
              chartKey="peak_demand"
              analysis={chartAnalyses?.peak_demand}
              onAnalyze={() => onAnalyzeChart("peak_demand")}
              onRefresh={() => onAnalyzeChart("peak_demand", true)}
              loading={llmLoading?.["peak_demand"] || false}
            />
          )}
        </div>
        <div>
          <p className="text-sm font-semibold text-foreground">{t("energyHub.trends.renewable.title")}</p>
          <p className="text-xs text-muted-foreground mb-2">{t("energyHub.trends.renewable.subtitle")}</p>
          <ChartExplanation
            what={t("energyHub.trends.renewable.explanation.what")}
            why={t("energyHub.trends.renewable.explanation.why")}
            action={t("energyHub.trends.renewable.explanation.action")}
          />
          <div className="rounded-lg border bg-white p-3 h-52 overflow-hidden">
            <PlotlyChart data={renewableGenTrace} layout={renewableGenLayout} />
          </div>
          {onAnalyzeChart && (
            <ChartAiPanel
              chartKey="renewable_generation"
              analysis={chartAnalyses?.renewable_generation}
              onAnalyze={() => onAnalyzeChart("renewable_generation")}
              onRefresh={() => onAnalyzeChart("renewable_generation", true)}
              loading={llmLoading?.["renewable_generation"] || false}
            />
          )}
        </div>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EnergyTrends` view or widget.

## `react-frontend/src/components/energyhub/PlotlyChart.jsx`

### `PlotlyChart`

- **File:** `react-frontend/src/components/energyhub/PlotlyChart.jsx`
- **Lines:** `20-41`
- **Purpose:** Renders the `PlotlyChart` component.

**Code:**
```jsx
export default function PlotlyChart({ data, layout = {}, config = {}, className = "" }) {
  const mergedLayout = {
    ...DEFAULT_LAYOUT,
    ...layout,
    margin: { ...DEFAULT_LAYOUT.margin, ...layout.margin },
    font: { ...DEFAULT_LAYOUT.font, ...layout.font },
    xaxis: { ...DEFAULT_LAYOUT.xaxis, ...layout.xaxis },
    yaxis: { ...DEFAULT_LAYOUT.yaxis, ...layout.yaxis },
    legend: { ...DEFAULT_LAYOUT.legend, ...layout.legend },
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
```

**Explanation:** This React component renders UI for the `PlotlyChart` view or widget.

## `react-frontend/src/components/energyhub/ProvincialDemand.jsx`

### `formatNumber`

- **File:** `react-frontend/src/components/energyhub/ProvincialDemand.jsx`
- **Lines:** `20-22`
- **Purpose:** Converts Number.

**Code:**
```jsx
function formatNumber(value) {
  return new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(value ?? 0);
}
```

**Explanation:** This function converts Number. See the code for the full implementation.

### `ProvincialDemand`

- **File:** `react-frontend/src/components/energyhub/ProvincialDemand.jsx`
- **Lines:** `24-177`
- **Purpose:** Renders the `ProvincialDemand` component.

**Code:**
```jsx
export default function ProvincialDemand({ region = null }) {
  const { t } = useI18n();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    getProvincialDemand(region)
      .then((res) => {
        if (!cancelled) setData(res);
      })
      .catch((err) => {
        if (!cancelled) setError(err?.message || t("energyHub.provincialDemand.error"));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [region]);

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("energyHub.provincialDemand.title")}</CardTitle>
          <CardDescription>{t("energyHub.provincialDemand.loading")}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 animate-pulse rounded bg-muted" />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("energyHub.provincialDemand.title")}</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-destructive text-sm">{error}</p>
        </CardContent>
      </Card>
    );
  }

  const items = data?.items || [];
  if (!items.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{t("energyHub.provincialDemand.title")}</CardTitle>
          <CardDescription>{data?.note || t("energyHub.provincialDemand.noData")}</CardDescription>
        </CardHeader>
      </Card>
    );
  }

  // Build chart data: normalize region names, aggregate by region+sector,
  // then produce one row per unique region.
  const aggregated = {};
  for (const item of items) {
    const region = (item.region ?? "").trim();
    if (!region) continue;
    // Skip rows where region looks like a number (corrupted data)
    if (/^\d{1,3}(,\d{3})+$/.test(region)) continue;
    if (!VALID_REGIONS.has(region.toUpperCase())) continue;
    const sector = item.sector;
    const key = `${region}||${sector}`;
    if (!aggregated[key]) {
      aggregated[key] = { region, sector, value_mwh: 0 };
    }
    aggregated[key].value_mwh += item.value_mwh ?? 0;
  }

  const regionSet = new Set();
  for (const key in aggregated) {
    regionSet.add(aggregated[key].region);
  }

  // Sort regions by total consumption (descending) for visual impact
  const regions = [...regionSet].sort((a, b) => {
    const totalA = SECTORS.reduce((sum, s) => sum + (aggregated[`${a}||${s}`]?.value_mwh ?? 0), 0);
    const totalB = SECTORS.reduce((sum, s) => sum + (aggregated[`${b}||${s}`]?.value_mwh ?? 0), 0);
    return totalB - totalA;
  });

  const chartData = regions.map((r) => {
    const row = { region: r };
    for (const sector of SECTORS) {
      const key = `${r}||${sector}`;
      row[sector] = aggregated[key] ? aggregated[key].value_mwh / 1000 : 0;
    }
    return row;
  });

  return (
    <Card>
      <CardHeader>
        <CardTitle>{t("energyHub.provincialDemand.title")} (2025)</CardTitle>
        <CardDescription>
          {t("energyHub.provincialDemand.note")}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="region" />
              <YAxis tickFormatter={(v) => `${v.toFixed(0)}`} />
              <Tooltip
                formatter={(value, name) => [formatNumber(value) + " GWh", name]}
                labelFormatter={(label) => t("energyHub.provincialDemand.regionLabel", { region: label })}
              />
              {SECTORS.map((sector) => (
                <Bar
                  key={sector}
                  dataKey={sector}
                  stackId="a"
                  fill={COLORS[sector]}
                  name={t(`energyHub.provincialDemand.sectors.${sector.toLowerCase()}`)}
                  radius={[0, 0, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="rounded-md bg-sky-50 border border-sky-100 p-3 space-y-2">
          <div className="flex items-center gap-1.5 text-sky-800">
            <Lightbulb className="h-3.5 w-3.5" />
            <span className="text-xs font-semibold">{t("energyHub.provincialDemand.insight.title")}</span>
          </div>
          <p className="text-xs text-sky-700 leading-relaxed">
            {t("energyHub.provincialDemand.insight.description")}
          </p>
          <div className="flex items-center gap-1.5 text-sky-800 pt-1">
            <Info className="h-3.5 w-3.5" />
            <span className="text-xs font-semibold">{t("energyHub.provincialDemand.insight.whyTitle")}</span>
          </div>
          <p className="text-xs text-sky-700 leading-relaxed">
            {t("energyHub.provincialDemand.insight.whyDescription")}
          </p>
        </div>
        <p className="text-xs text-muted-foreground">{data?.note || ""}</p>
      </CardContent>
    </Card>
  );
}
```

**Explanation:** This React component renders UI for the `ProvincialDemand` view or widget.

## `react-frontend/src/components/layout/Navbar.jsx`

### `UserAvatar`

- **File:** `react-frontend/src/components/layout/Navbar.jsx`
- **Lines:** `24-58`
- **Purpose:** Renders the `UserAvatar` component.

**Code:**
```jsx
function UserAvatar({ user, profile, className = "" }) {
  const displayName =
    profile?.full_name ||
    user?.user_metadata?.full_name ||
    user?.email ||
    "U";
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const url =
    profile?.avatar_url ||
    user?.user_metadata?.avatar_url ||
    user?.user_metadata?.picture;
  return (
    <div
      className={`relative inline-flex items-center justify-center rounded-full overflow-hidden border bg-primary/10 ${className}`}
    >
      {url ? (
        <img
          src={url}
          alt=""
          className="h-full w-full object-cover"
          onError={(e) => {
            e.currentTarget.style.display = "none";
          }}
        />
      ) : (
        <span className="text-xs font-bold text-primary">{initials}</span>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `UserAvatar` view or widget.

### `LumLogo`

- **File:** `react-frontend/src/components/layout/Navbar.jsx`
- **Lines:** `68-74`
- **Purpose:** Renders the `LumLogo` component.

**Code:**
```jsx
function LumLogo() {
  return (
    <div className="flex items-center gap-2">
      <img src="/logo.png" alt="LUMI" className="h-14 w-auto object-contain" />
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `LumLogo` view or widget.

### `Navbar`

- **File:** `react-frontend/src/components/layout/Navbar.jsx`
- **Lines:** `76-237`
- **Purpose:** Renders the `Navbar` component.

**Code:**
```jsx
export default function Navbar() {
  const { t, locale, setLocale } = useI18n();
  const { session, user, profile, signOut, isAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  const links = navLinks.map((link) => ({ ...link, label: t(link.key) }));

  const displayName =
    profile?.full_name ||
    user?.user_metadata?.full_name ||
    user?.email?.split("@")[0] ||
    t("common.user");
  const userEmail = user?.email || "";

  const NavLink = ({ link, onClick }) => {
    const isActive =
      location.pathname === link.to ||
      (link.to !== "/" && location.pathname.startsWith(link.to));
    return (
      <Link
        to={link.to}
        onClick={onClick}
        className={
          "rounded-md px-3 py-2 text-sm font-medium transition-colors " +
          (isActive
            ? "bg-primary text-primary-foreground"
            : "text-muted-foreground hover:bg-muted hover:text-foreground")
        }
      >
        {link.label}
      </Link>
    );
  };

  return (
    <header className="relative border-b bg-card/80 backdrop-blur supports-[backdrop-filter]:bg-card/60">
      <div className="page-container flex items-center justify-between">
        <Link to="/" aria-label={t("nav.home")}>
          <LumLogo />
        </Link>

        <nav className="flex items-center gap-1">
          {/* Desktop navigation */}
          <div className="hidden md:flex items-center gap-1">
            {links.map((link) => (
              <NavLink key={link.to} link={link} />
            ))}
          </div>

          {session ? (
            <div className="flex items-center gap-2 ml-2">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 rounded-md hover:bg-muted transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-ring px-2 py-1">
                    <UserAvatar user={user} profile={profile} className="h-8 w-8" />
                    <span
                      className="text-sm font-medium hidden md:inline max-w-[120px] truncate"
                      title={displayName}
                    >
                      {displayName}
                    </span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64 p-2">
                  <div className="flex items-center gap-3 px-2 py-2">
                    <UserAvatar user={user} profile={profile} className="h-10 w-10" />
                    <div className="flex flex-col min-w-0">
                      <span className="text-sm font-semibold truncate" title={displayName}>
                        {displayName}
                      </span>
                      <span className="text-xs text-muted-foreground truncate" title={userEmail}>
                        {userEmail}
                      </span>
                    </div>
                  </div>
                  <DropdownMenuSeparator />
                  {isAdmin && (
                    <DropdownMenuItem
                      onClick={() => navigate("/admin")}
                      className="flex items-center gap-2 text-primary focus:text-primary"
                    >
                      <span className="text-base">🛡️</span>
                      <span>{t("nav.adminPortal")}</span>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={() => navigate("/dashboard")} className="flex items-center gap-2">
                    <span className="text-base">👤</span>
                    <span>{t("nav.dashboard")}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => navigate("/saved-simulations")} className="flex items-center gap-2">
                    <span className="text-base">📊</span>
                    <span>{t("nav.savedSims")}</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={() => {
                      signOut();
                      navigate("/");
                    }}
                    className="flex items-center gap-2 text-destructive focus:text-destructive"
                  >
                    <span className="text-base">🚪</span>
                    <span>{t("nav.logout")}</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          ) : (
            <TooltipProvider delayDuration={150}>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Link to="/login" aria-label={t("login.signIn")}>
                    <Button size="sm">{t("nav.login")}</Button>
                  </Link>
                </TooltipTrigger>
                <TooltipContent side="bottom">
                  <p>{t("login.signIn")}</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          )}

          <div className="hidden md:flex items-center gap-2 ml-2">
            <LanguageToggle />
            <ThemeToggle />
          </div>

          {/* Mobile hamburger */}
          <button
            type="button"
            aria-label={mobileOpen ? t("nav.closeMenu") : t("nav.openMenu")}
            onClick={() => setMobileOpen((v) => !v)}
            className="md:hidden ml-2 rounded-md p-2 text-foreground hover:bg-muted"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </nav>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden absolute inset-x-0 top-full z-50 border-b bg-card p-4 shadow-lg">
          <div className="flex flex-col gap-1">
            {links.map((link) => (
              <NavLink key={link.to} link={link} onClick={() => setMobileOpen(false)} />
            ))}
          </div>
          <div className="mt-4 flex items-center justify-between border-t pt-4">
            <LanguageToggle />
            <ThemeToggle />
          </div>
        </div>
      )}
    </header>
  );
}
```

**Explanation:** This React component renders UI for the `Navbar` view or widget.

## `react-frontend/src/components/layout/Sidebar.jsx`

### `Sidebar`

- **File:** `react-frontend/src/components/layout/Sidebar.jsx`
- **Lines:** `6-30`
- **Purpose:** Renders the `Sidebar` component.

**Code:**
```jsx
export default function Sidebar() {
  const { t } = useI18n();

  const items = [
    { label: t("layout.overview"), icon: LayoutDashboard },
    { label: t("layout.modules"), icon: Layers },
    { label: t("layout.settings"), icon: Settings }
  ];

  return (
    <aside className="hidden w-60 shrink-0 border-r bg-card/50 p-6 md:block">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-wider text-primary">{t("layout.workspace")}</p>
        <div className="space-y-1">
          {items.map((item) => (
            <Button key={item.label} variant="ghost" className="w-full justify-start gap-2 text-muted-foreground hover:bg-muted hover:text-foreground">
              <item.icon size={16} />
              {item.label}
            </Button>
          ))}
        </div>
      </div>
    </aside>
  );
}
```

**Explanation:** This React component renders UI for the `Sidebar` view or widget.

## `react-frontend/src/components/shared/AdminRoute.jsx`

### `AdminRoute`

- **File:** `react-frontend/src/components/shared/AdminRoute.jsx`
- **Lines:** `6-23`
- **Purpose:** Renders the `AdminRoute` component.

**Code:**
```jsx
export default function AdminRoute({ children }) {
  const { user, isAdmin, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loading />;
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
}
```

**Explanation:** This React component renders UI for the `AdminRoute` view or widget.

## `react-frontend/src/components/shared/BillHelpModal.jsx`

### `BillHelpModal`

- **File:** `react-frontend/src/components/shared/BillHelpModal.jsx`
- **Lines:** `12-60`
- **Purpose:** Renders the `BillHelpModal` component.

**Code:**
```jsx
export default function BillHelpModal({
  triggerText = "Where can I find this on my bill?",
  title = "Finding your actual consumption",
  description = "Look for the \"Actual Consumption\" line on your Meralco bill. It is usually shown in kWh near the usage or metering section.",
  className = "",
}) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button
          type="button"
          className={`inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded ${className}`}
          aria-haspopup="dialog"
        >
          <HelpCircle className="h-3.5 w-3.5" />
          {triggerText}
        </button>
      </DialogTrigger>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <div className="mt-2 aspect-video w-full rounded-lg border bg-muted p-4 flex items-center justify-center relative overflow-hidden">
          <div className="w-full max-w-sm rounded-md border border-border bg-card p-3 shadow-sm">
            <div className="space-y-2">
              <div className="h-2 w-1/2 rounded bg-muted-foreground/20" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Account Details</span>
                <span>Billing Period</span>
              </div>
              <div className="h-px bg-border" />
              <div className="rounded border border-dashed border-primary/50 bg-primary/5 p-2">
                <div className="text-[10px] uppercase tracking-wide text-muted-foreground">Actual Consumption</div>
                <div className="text-lg font-semibold text-foreground">300 kWh</div>
              </div>
              <div className="h-2 w-3/4 rounded bg-muted-foreground/20" />
            </div>
          </div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none">
            <svg width="120" height="80" viewBox="0 0 120 80" fill="none" className="opacity-80">
              <circle cx="60" cy="40" r="32" stroke="hsl(var(--primary))" strokeWidth="2" fill="none" strokeDasharray="4 4" />
            </svg>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
```

**Explanation:** This React component renders UI for the `BillHelpModal` view or widget.

## `react-frontend/src/components/shared/CitationSources.jsx`

### `CitationSources`

- **File:** `react-frontend/src/components/shared/CitationSources.jsx`
- **Lines:** `16-97`
- **Purpose:** Renders the `CitationSources` component.

**Code:**
```jsx
export default function CitationSources({
  ids,
  mode = "dialog",
  inlineLabel,
  dialogLabel,
  className = "",
}) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);

  const filtered = useMemo(() => {
    if (!ids || !ids.length) return [];
    return references.filter((r) => ids.includes(r.id));
  }, [ids]);

  const inlineText =
    inlineLabel || t("citationSources.basedOn") || "Based on the Philippine and international research";
  const buttonText =
    dialogLabel || t("citationSources.viewSources") || "View Sources";

  if (!filtered.length) return null;

  if (mode === "inline") {
    return (
      <div className={`citation-sources-inline ${className}`}>
        <button
          type="button"
          onClick={() => setExpanded((v) => !v)}
          className="inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded"
          aria-expanded={expanded}
        >
          <BookOpen className="h-3.5 w-3.5" />
          {inlineText}
          {expanded ? (
            <ChevronUp className="h-3.5 w-3.5" />
          ) : (
            <ChevronDown className="h-3.5 w-3.5" />
          )}
        </button>
        {expanded && (
          <div className="mt-2 rounded-lg border bg-card p-3 text-xs text-muted-foreground">
            <ol className="list-decimal list-inside space-y-1.5">
              {filtered.map((ref) => (
                <li key={ref.id}>{ref.text}</li>
              ))}
            </ol>
          </div>
        )}
      </div>
    );
  }

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className={`gap-1.5 ${className}`}
          aria-haspopup="dialog"
        >
          <BookOpen className="h-4 w-4" />
          {buttonText}
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{t("citationSources.title") || "Sources & References"}</DialogTitle>
          <DialogDescription>
            {t("citationSources.description") ||
              "LUMI uses published research and trusted climate and energy data sources."}
          </DialogDescription>
        </DialogHeader>
        <ol className="mt-4 list-decimal list-inside space-y-3 text-sm text-muted-foreground">
          {filtered.map((ref) => (
            <li key={ref.id}>{ref.text}</li>
          ))}
        </ol>
      </DialogContent>
    </Dialog>
  );
}
```

**Explanation:** This React component renders UI for the `CitationSources` view or widget.

## `react-frontend/src/components/shared/ExpandableBlock.jsx`

### `ExpandableBlock`

- **File:** `react-frontend/src/components/shared/ExpandableBlock.jsx`
- **Lines:** `7-39`
- **Purpose:** Renders the `ExpandableBlock` component.

**Code:**
```jsx
export default function ExpandableBlock({
  title,
  children,
  defaultOpen = false,
  className = "",
  contentClassName = "",
}) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className={cn("rounded-xl border bg-card", className)}>
      <Button
        type="button"
        variant="ghost"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="w-full justify-between px-4 py-3 h-auto text-left font-semibold hover:bg-muted/50"
      >
        <span className="text-sm">{title}</span>
        {open ? (
          <ChevronUp className="h-4 w-4 shrink-0 text-muted-foreground" />
        ) : (
          <ChevronDown className="h-4 w-4 shrink-0 text-muted-foreground" />
        )}
      </Button>
      {open && (
        <div className={cn("px-4 pb-4 text-sm text-muted-foreground", contentClassName)}>
          {children}
        </div>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `ExpandableBlock` view or widget.

## `react-frontend/src/components/shared/HelpTooltip.jsx`

### `HelpTooltip`

- **File:** `react-frontend/src/components/shared/HelpTooltip.jsx`
- **Lines:** `11-42`
- **Purpose:** HelpTooltip — wraps children with a hover tooltip that shows a plain-English

**Code:**
```jsx
export default function HelpTooltip({ term, children, className = "" }) {
  const [show, setShow] = useState(false);
  const { t } = useI18n();

  const key = (term || "").toLowerCase().trim().replace(/\s+/g, "_");
  const glossaryKey = `glossary.${key}`;
  const translated = t(glossaryKey);
  const definition = translated !== glossaryKey ? translated : getGlossary(term);

  if (!definition) {
    return <span className={className}>{children}</span>;
  }

  return (
    <span className={`relative inline-flex items-center gap-1 ${className}`}>
      {children}
      <span
        className="cursor-help text-muted-foreground hover:text-foreground transition-colors"
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        onClick={() => setShow(!show)}
      >
        <HelpCircle className="h-3.5 w-3.5" />
      </span>
      {show && (
        <span className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 rounded-lg bg-slate-800 px-3 py-2 text-xs text-white shadow-lg z-50">
          {definition}
        </span>
      )}
    </span>
  );
}
```

**Explanation:** This React component renders UI for the `HelpTooltip` view or widget.

## `react-frontend/src/components/shared/InfoTooltip.jsx`

### `InfoTooltip`

- **File:** `react-frontend/src/components/shared/InfoTooltip.jsx`
- **Lines:** `10-28`
- **Purpose:** Renders the `InfoTooltip` component.

**Code:**
```jsx
export default function InfoTooltip({ label, content, className = "" }) {
  return (
    <TooltipProvider delayDuration={150}>
      <Tooltip>
        <TooltipTrigger
          type="button"
          className={`inline-flex items-center gap-1 text-xs font-medium text-primary underline-offset-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded ${className}`}
          aria-label={label}
        >
          <Info className="h-3.5 w-3.5" />
          <span>{label}</span>
        </TooltipTrigger>
        <TooltipContent side="top" align="start" className="max-w-xs">
          <p>{content}</p>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
}
```

**Explanation:** This React component renders UI for the `InfoTooltip` view or widget.

## `react-frontend/src/components/shared/InsightCard.jsx`

### `InsightCard`

- **File:** `react-frontend/src/components/shared/InsightCard.jsx`
- **Lines:** `11-50`
- **Purpose:** InsightCard — displays a metric with:

**Code:**
```jsx
export default function InsightCard({
  icon: Icon,
  iconColor = "text-slate-600",
  iconBg = "bg-slate-100",
  borderColor = "border-l-4 border-l-slate-400",
  title,
  value,
  subtitle,
  interpretation,
  recommendation,
  nextStep,
}) {
  return (
    <Card className={borderColor}>
      <CardContent className="p-5">
        <div className="flex items-start gap-3">
          {Icon && (
            <div className={`shrink-0 rounded-lg p-2 ${iconBg}`}>
              <Icon className={`h-5 w-5 ${iconColor}`} />
            </div>
          )}
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="mt-1 text-2xl font-bold tracking-tight">{value}</p>
            {subtitle && <p className="text-xs text-muted-foreground mt-0.5">{subtitle}</p>}
            {interpretation && (
              <p className="mt-2 text-sm text-slate-700 leading-relaxed">{interpretation}</p>
            )}
            {recommendation && (
              <p className="mt-1.5 text-sm font-medium text-emerald-700">{recommendation}</p>
            )}
            {nextStep && (
              <p className="mt-1 text-xs text-slate-500">{nextStep}</p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
```

**Explanation:** This React component renders UI for the `InsightCard` view or widget.

## `react-frontend/src/components/shared/InterpretationBadge.jsx`

### `getRating`

- **File:** `react-frontend/src/components/shared/InterpretationBadge.jsx`
- **Lines:** `17-20`
- **Purpose:** Retrieves Rating.

**Code:**
```jsx
export function getRating(score, max = 100) {
  const pct = (score ?? 0) / max;
  return RATINGS.find((r) => pct >= r.pct) || RATINGS[RATINGS.length - 1];
}
```

**Explanation:** This function retrieves Rating. See the code for the full implementation.

### `getStars`

- **File:** `react-frontend/src/components/shared/InterpretationBadge.jsx`
- **Lines:** `22-29`
- **Purpose:** Retrieves Stars.

**Code:**
```jsx
export function getStars(score, max = 100) {
  const pct = Math.max(0, Math.min(1, (score ?? 0) / max));
  const full = Math.floor(pct * 5);
  let s = "";
  for (let i = 0; i < full; i++) s += "★";
  while (s.length < 5) s += "☆";
  return s;
}
```

**Explanation:** This function retrieves Stars. See the code for the full implementation.

### `InterpretationBadge`

- **File:** `react-frontend/src/components/shared/InterpretationBadge.jsx`
- **Lines:** `31-41`
- **Purpose:** Renders the `InterpretationBadge` component.

**Code:**
```jsx
export default function InterpretationBadge({ score, max = 100, showStars = true, className = "" }) {
  const { t } = useI18n();
  const rating = getRating(score, max);
  const stars = getStars(score, max);
  return (
    <div className={`flex items-center gap-2 flex-wrap ${className}`}>
      <Badge className={`${rating.color} hover:${rating.color}`}>{t("common.ratings." + rating.label.toLowerCase())}</Badge>
      {showStars && <span className="text-warning tracking-widest text-sm">{stars}</span>}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `InterpretationBadge` view or widget.

## `react-frontend/src/components/shared/LanguageToggle.jsx`

### `LanguageToggle`

- **File:** `react-frontend/src/components/shared/LanguageToggle.jsx`
- **Lines:** `4-33`
- **Purpose:** Renders the `LanguageToggle` component.

**Code:**
```jsx
export default function LanguageToggle() {
  const { t, locale, setLocale } = useI18n();

  return (
    <div
      className="inline-flex items-center rounded-md border border-border bg-background p-0.5"
      role="group"
      aria-label={t("common.language")}
    >
      <Button
        variant={locale === "en" ? "default" : "ghost"}
        size="sm"
        className="h-7 px-2 text-xs"
        onClick={() => setLocale("en")}
        aria-pressed={locale === "en"}
      >
        EN
      </Button>
      <Button
        variant={locale === "fil" ? "default" : "ghost"}
        size="sm"
        className="h-7 px-2 text-xs"
        onClick={() => setLocale("fil")}
        aria-pressed={locale === "fil"}
      >
        FIL
      </Button>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `LanguageToggle` view or widget.

## `react-frontend/src/components/shared/Loading.jsx`

### `Loading`

- **File:** `react-frontend/src/components/shared/Loading.jsx`
- **Lines:** `3-6`
- **Purpose:** Renders the `Loading` component.

**Code:**
```jsx
export default function Loading() {
  const { t } = useI18n();
  return <div className="page-container">{t("common.loading")}</div>;
}
```

**Explanation:** This React component renders UI for the `Loading` view or widget.

## `react-frontend/src/components/shared/LoadingSkeleton.jsx`

### `LoadingSkeleton`

- **File:** `react-frontend/src/components/shared/LoadingSkeleton.jsx`
- **Lines:** `3-14`
- **Purpose:** Renders the `LoadingSkeleton` component.

**Code:**
```jsx
export default function LoadingSkeleton() {
  return (
    <div className="grid gap-4">
      <Skeleton className="h-6 w-2/3" />
      <Skeleton className="h-24 w-full" />
      <div className="grid grid-cols-2 gap-4">
        <Skeleton className="h-16" />
        <Skeleton className="h-16" />
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `LoadingSkeleton` view or widget.

## `react-frontend/src/components/shared/NextStepList.jsx`

### `NextStepList`

- **File:** `react-frontend/src/components/shared/NextStepList.jsx`
- **Lines:** `10-29`
- **Purpose:** NextStepList — renders a numbered checklist of actionable steps with

**Code:**
```jsx
export default function NextStepList({ steps, className = "" }) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className={`grid gap-3 md:grid-cols-2 ${className}`}>
      {steps.map((step, i) => (
        <div
          key={i}
          className="flex items-start gap-3 p-3 rounded-lg border bg-muted/20 hover:bg-muted/30 transition-colors"
        >
          <CheckCircle className="h-5 w-5 text-emerald-500 shrink-0 mt-0.5" />
          <div>
            <p className="font-medium text-sm">{step.title}</p>
            <p className="text-xs text-muted-foreground mt-0.5">{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `NextStepList` view or widget.

## `react-frontend/src/components/shared/ProtectedRoute.jsx`

### `ProtectedRoute`

- **File:** `react-frontend/src/components/shared/ProtectedRoute.jsx`
- **Lines:** `6-19`
- **Purpose:** Renders the `ProtectedRoute` component.

**Code:**
```jsx
export default function ProtectedRoute({ children }) {
  const { session, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <Loading />;
  }

  if (!session) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
```

**Explanation:** This React component renders UI for the `ProtectedRoute` view or widget.

## `react-frontend/src/components/shared/ThemeToggle.jsx`

### `ThemeToggle`

- **File:** `react-frontend/src/components/shared/ThemeToggle.jsx`
- **Lines:** `7-16`
- **Purpose:** Renders the `ThemeToggle` component.

**Code:**
```jsx
export default function ThemeToggle() {
  const { t } = useI18n();
  const { theme, toggleTheme } = useTheme();

  return (
    <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label={t("common.toggleTheme")}>
      {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
    </Button>
  );
}
```

**Explanation:** This React component renders UI for the `ThemeToggle` view or widget.

## `react-frontend/src/components/ui/badge.jsx`

### `Badge`

- **File:** `react-frontend/src/components/ui/badge.jsx`
- **Lines:** `21-23`
- **Purpose:** Renders the `Badge` component.

**Code:**
```jsx
export function Badge({ className, variant, ...props }) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `Badge` view or widget.

## `react-frontend/src/components/ui/button.jsx`

### `Button`

- **File:** `react-frontend/src/components/ui/button.jsx`
- **Lines:** `32-35`
- **Purpose:** Renders the `Button` component.

**Code:**
```jsx
const Button = React.forwardRef(({ className, variant, size, asChild = false, ...props }, ref) => {
  const Comp = asChild ? Slot : "button";
  return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
})
```

**Explanation:** This React component renders UI for the `Button` view or widget.

## `react-frontend/src/components/ui/card.jsx`

### `Card`

- **File:** `react-frontend/src/components/ui/card.jsx`
- **Lines:** `3-5`
- **Purpose:** Renders the `Card` component.

**Code:**
```jsx
export function Card({ className, ...props }) {
  return <div className={cn("rounded-lg border bg-card text-card-foreground shadow-sm", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `Card` view or widget.

### `CardHeader`

- **File:** `react-frontend/src/components/ui/card.jsx`
- **Lines:** `7-9`
- **Purpose:** Renders the `CardHeader` component.

**Code:**
```jsx
export function CardHeader({ className, ...props }) {
  return <div className={cn("flex flex-col space-y-2 p-6", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `CardHeader` view or widget.

### `CardTitle`

- **File:** `react-frontend/src/components/ui/card.jsx`
- **Lines:** `11-13`
- **Purpose:** Renders the `CardTitle` component.

**Code:**
```jsx
export function CardTitle({ className, ...props }) {
  return <h3 className={cn("text-lg font-semibold", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `CardTitle` view or widget.

### `CardDescription`

- **File:** `react-frontend/src/components/ui/card.jsx`
- **Lines:** `15-17`
- **Purpose:** Renders the `CardDescription` component.

**Code:**
```jsx
export function CardDescription({ className, ...props }) {
  return <p className={cn("text-sm text-muted-foreground", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `CardDescription` view or widget.

### `CardContent`

- **File:** `react-frontend/src/components/ui/card.jsx`
- **Lines:** `19-21`
- **Purpose:** Renders the `CardContent` component.

**Code:**
```jsx
export function CardContent({ className, ...props }) {
  return <div className={cn("p-6 pt-0", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `CardContent` view or widget.

### `CardFooter`

- **File:** `react-frontend/src/components/ui/card.jsx`
- **Lines:** `23-25`
- **Purpose:** Renders the `CardFooter` component.

**Code:**
```jsx
export function CardFooter({ className, ...props }) {
  return <div className={cn("flex items-center p-6 pt-0", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `CardFooter` view or widget.

## `react-frontend/src/components/ui/dialog.jsx`

### `DialogContent`

- **File:** `react-frontend/src/components/ui/dialog.jsx`
- **Lines:** `10-23`
- **Purpose:** Renders the `DialogContent` component.

**Code:**
```jsx
export function DialogContent({ className, ...props }) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50" />
      <DialogPrimitive.Content
        className={cn(
          "fixed left-1/2 top-1/2 z-50 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-lg border bg-background p-6 shadow-lg",
          className
        )}
        {...props}
      />
    </DialogPrimitive.Portal>
  );
}
```

**Explanation:** This React component renders UI for the `DialogContent` view or widget.

### `DialogHeader`

- **File:** `react-frontend/src/components/ui/dialog.jsx`
- **Lines:** `25-27`
- **Purpose:** Renders the `DialogHeader` component.

**Code:**
```jsx
export function DialogHeader({ className, ...props }) {
  return <div className={cn("flex flex-col gap-2", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `DialogHeader` view or widget.

### `DialogFooter`

- **File:** `react-frontend/src/components/ui/dialog.jsx`
- **Lines:** `29-31`
- **Purpose:** Renders the `DialogFooter` component.

**Code:**
```jsx
export function DialogFooter({ className, ...props }) {
  return <div className={cn("flex items-center justify-end gap-3", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `DialogFooter` view or widget.

### `DialogTitle`

- **File:** `react-frontend/src/components/ui/dialog.jsx`
- **Lines:** `33-35`
- **Purpose:** Renders the `DialogTitle` component.

**Code:**
```jsx
export function DialogTitle({ className, ...props }) {
  return <DialogPrimitive.Title className={cn("text-lg font-semibold", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `DialogTitle` view or widget.

### `DialogDescription`

- **File:** `react-frontend/src/components/ui/dialog.jsx`
- **Lines:** `37-39`
- **Purpose:** Renders the `DialogDescription` component.

**Code:**
```jsx
export function DialogDescription({ className, ...props }) {
  return <DialogPrimitive.Description className={cn("text-sm text-muted-foreground", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `DialogDescription` view or widget.

## `react-frontend/src/components/ui/dropdown-menu.jsx`

### `DropdownMenuContent`

- **File:** `react-frontend/src/components/ui/dropdown-menu.jsx`
- **Lines:** `7-18`
- **Purpose:** Renders the `DropdownMenuContent` component.

**Code:**
```jsx
const DropdownMenuContent = ({ className, sideOffset = 8, ...props }) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      sideOffset={sideOffset}
      className={cn(
        "z-50 min-w-40 rounded-md border bg-popover p-2 text-popover-foreground shadow-md",
        className
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
)
```

**Explanation:** This React component renders UI for the `DropdownMenuContent` view or widget.

### `DropdownMenuItem`

- **File:** `react-frontend/src/components/ui/dropdown-menu.jsx`
- **Lines:** `20-28`
- **Purpose:** Renders the `DropdownMenuItem` component.

**Code:**
```jsx
const DropdownMenuItem = ({ className, ...props }) => (
  <DropdownMenuPrimitive.Item
    className={cn(
      "cursor-pointer select-none rounded-sm px-2 py-1.5 text-sm outline-none focus:bg-accent focus:text-accent-foreground",
      className
    )}
    {...props}
  />
)
```

**Explanation:** This React component renders UI for the `DropdownMenuItem` view or widget.

### `DropdownMenuSeparator`

- **File:** `react-frontend/src/components/ui/dropdown-menu.jsx`
- **Lines:** `30-35`
- **Purpose:** Renders the `DropdownMenuSeparator` component.

**Code:**
```jsx
const DropdownMenuSeparator = ({ className, ...props }) => (
  <DropdownMenuPrimitive.Separator
    className={cn("my-1 h-px bg-muted", className)}
    {...props}
  />
)
```

**Explanation:** This React component renders UI for the `DropdownMenuSeparator` view or widget.

## `react-frontend/src/components/ui/form.jsx`

### `FormField`

- **File:** `react-frontend/src/components/ui/form.jsx`
- **Lines:** `13-19`
- **Purpose:** Renders the `FormField` component.

**Code:**
```jsx
function FormField({ name, ...props }) {
  return (
    <FormFieldContext.Provider value={{ name }}>
      <Controller {...props} name={name} />
    </FormFieldContext.Provider>
  );
}
```

**Explanation:** This React component renders UI for the `FormField` view or widget.

### `useFormField`

- **File:** `react-frontend/src/components/ui/form.jsx`
- **Lines:** `21-41`
- **Purpose:** Custom React hook `useFormField`.

**Code:**
```jsx
function useFormField() {
  const fieldContext = React.useContext(FormFieldContext);
  const itemContext = React.useContext(FormItemContext);
  const { getFieldState, formState } = useFormContext();
  const fieldState = getFieldState(fieldContext.name, formState);

  if (!fieldContext.name) {
    throw new Error("useFormField must be used within <FormField>");
  }

  const id = itemContext.id;

  return {
    id,
    name: fieldContext.name,
    formItemId: `${id}-form-item`,
    formDescriptionId: `${id}-form-item-description`,
    formMessageId: `${id}-form-item-message`,
    ...fieldState
  };
}
```

**Explanation:** This hook returns state and helpers used by React components. See the code for the full implementation.

### `FormItem`

- **File:** `react-frontend/src/components/ui/form.jsx`
- **Lines:** `43-50`
- **Purpose:** Renders the `FormItem` component.

**Code:**
```jsx
const FormItem = React.forwardRef(({ className, ...props }, ref) => {
  const id = React.useId();
  return (
    <FormItemContext.Provider value={{ id }}>
      <div ref={ref} className={cn("space-y-2", className)} {...props} />
    </FormItemContext.Provider>
  );
})
```

**Explanation:** This React component renders UI for the `FormItem` view or widget.

### `FormLabel`

- **File:** `react-frontend/src/components/ui/form.jsx`
- **Lines:** `53-56`
- **Purpose:** Renders the `FormLabel` component.

**Code:**
```jsx
const FormLabel = React.forwardRef(({ className, ...props }, ref) => {
  const { formItemId } = useFormField();
  return <label ref={ref} className={cn("text-sm font-medium", className)} htmlFor={formItemId} {...props} />;
})
```

**Explanation:** This React component renders UI for the `FormLabel` view or widget.

### `FormControl`

- **File:** `react-frontend/src/components/ui/form.jsx`
- **Lines:** `59-70`
- **Purpose:** Renders the `FormControl` component.

**Code:**
```jsx
const FormControl = React.forwardRef(({ ...props }, ref) => {
  const { formItemId, formDescriptionId, formMessageId, error } = useFormField();
  return (
    <Slot
      ref={ref}
      id={formItemId}
      aria-describedby={`${formDescriptionId} ${formMessageId}`}
      aria-invalid={!!error}
      {...props}
    />
  );
})
```

**Explanation:** This React component renders UI for the `FormControl` view or widget.

### `FormDescription`

- **File:** `react-frontend/src/components/ui/form.jsx`
- **Lines:** `73-76`
- **Purpose:** Renders the `FormDescription` component.

**Code:**
```jsx
const FormDescription = React.forwardRef(({ className, ...props }, ref) => {
  const { formDescriptionId } = useFormField();
  return <p ref={ref} id={formDescriptionId} className={cn("text-sm text-muted-foreground", className)} {...props} />;
})
```

**Explanation:** This React component renders UI for the `FormDescription` view or widget.

### `FormMessage`

- **File:** `react-frontend/src/components/ui/form.jsx`
- **Lines:** `79-88`
- **Purpose:** Renders the `FormMessage` component.

**Code:**
```jsx
const FormMessage = React.forwardRef(({ className, ...props }, ref) => {
  const { formMessageId, error } = useFormField();
  const body = error ? String(error?.message) : null;
  if (!body) return null;
  return (
    <p ref={ref} id={formMessageId} className={cn("text-sm font-medium text-destructive", className)} {...props}>
      {body}
    </p>
  );
})
```

**Explanation:** This React component renders UI for the `FormMessage` view or widget.

## `react-frontend/src/components/ui/input.jsx`

### `Input`

- **File:** `react-frontend/src/components/ui/input.jsx`
- **Lines:** `5-15`
- **Purpose:** Renders the `Input` component.

**Code:**
```jsx
const Input = React.forwardRef(({ className, type = "text", ...props }, ref) => (
  <input
    ref={ref}
    type={type}
    className={cn(
      "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
      className
    )}
    {...props}
  />
))
```

**Explanation:** This React component renders UI for the `Input` view or widget.

## `react-frontend/src/components/ui/progress.jsx`

### `Progress`

- **File:** `react-frontend/src/components/ui/progress.jsx`
- **Lines:** `5-19`
- **Purpose:** Renders the `Progress` component.

**Code:**
```jsx
const Progress = React.forwardRef(({ className, value, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "relative h-4 w-full overflow-hidden rounded-full bg-secondary",
      className
    )}
    {...props}
  >
    <div
      className="h-full w-full flex-1 bg-primary transition-all"
      style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
    />
  </div>
))
```

**Explanation:** This React component renders UI for the `Progress` view or widget.

## `react-frontend/src/components/ui/sheet.jsx`

### `SheetContent`

- **File:** `react-frontend/src/components/ui/sheet.jsx`
- **Lines:** `17-31`
- **Purpose:** Renders the `SheetContent` component.

**Code:**
```jsx
export function SheetContent({ side = "right", className, ...props }) {
  return (
    <SheetPrimitive.Portal>
      <SheetPrimitive.Overlay className="fixed inset-0 z-50 bg-black/50" />
      <SheetPrimitive.Content
        className={cn(
          "fixed z-50 bg-background p-6 shadow-lg transition",
          sheetVariants[side],
          className
        )}
        {...props}
      />
    </SheetPrimitive.Portal>
  );
}
```

**Explanation:** This React component renders UI for the `SheetContent` view or widget.

### `SheetHeader`

- **File:** `react-frontend/src/components/ui/sheet.jsx`
- **Lines:** `33-35`
- **Purpose:** Renders the `SheetHeader` component.

**Code:**
```jsx
export function SheetHeader({ className, ...props }) {
  return <div className={cn("flex flex-col gap-2", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `SheetHeader` view or widget.

### `SheetFooter`

- **File:** `react-frontend/src/components/ui/sheet.jsx`
- **Lines:** `37-39`
- **Purpose:** Renders the `SheetFooter` component.

**Code:**
```jsx
export function SheetFooter({ className, ...props }) {
  return <div className={cn("flex items-center justify-end gap-3", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `SheetFooter` view or widget.

### `SheetTitle`

- **File:** `react-frontend/src/components/ui/sheet.jsx`
- **Lines:** `41-43`
- **Purpose:** Renders the `SheetTitle` component.

**Code:**
```jsx
export function SheetTitle({ className, ...props }) {
  return <SheetPrimitive.Title className={cn("text-lg font-semibold", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `SheetTitle` view or widget.

### `SheetDescription`

- **File:** `react-frontend/src/components/ui/sheet.jsx`
- **Lines:** `45-47`
- **Purpose:** Renders the `SheetDescription` component.

**Code:**
```jsx
export function SheetDescription({ className, ...props }) {
  return <SheetPrimitive.Description className={cn("text-sm text-muted-foreground", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `SheetDescription` view or widget.

## `react-frontend/src/components/ui/skeleton.jsx`

### `Skeleton`

- **File:** `react-frontend/src/components/ui/skeleton.jsx`
- **Lines:** `3-5`
- **Purpose:** Renders the `Skeleton` component.

**Code:**
```jsx
export function Skeleton({ className, ...props }) {
  return <div className={cn("animate-pulse rounded-md bg-muted", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `Skeleton` view or widget.

## `react-frontend/src/components/ui/sonner.jsx`

### `Toaster`

- **File:** `react-frontend/src/components/ui/sonner.jsx`
- **Lines:** `3-5`
- **Purpose:** Renders the `Toaster` component.

**Code:**
```jsx
export function Toaster() {
  return <Sonner richColors position="top-right" />;
}
```

**Explanation:** This React component renders UI for the `Toaster` view or widget.

## `react-frontend/src/components/ui/table.jsx`

### `Table`

- **File:** `react-frontend/src/components/ui/table.jsx`
- **Lines:** `3-5`
- **Purpose:** Renders the `Table` component.

**Code:**
```jsx
export function Table({ className, ...props }) {
  return <table className={cn("w-full text-sm", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `Table` view or widget.

### `TableHeader`

- **File:** `react-frontend/src/components/ui/table.jsx`
- **Lines:** `7-9`
- **Purpose:** Renders the `TableHeader` component.

**Code:**
```jsx
export function TableHeader({ className, ...props }) {
  return <thead className={cn("border-b", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `TableHeader` view or widget.

### `TableBody`

- **File:** `react-frontend/src/components/ui/table.jsx`
- **Lines:** `11-13`
- **Purpose:** Renders the `TableBody` component.

**Code:**
```jsx
export function TableBody({ className, ...props }) {
  return <tbody className={cn("[&>tr:last-child]:border-0", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `TableBody` view or widget.

### `TableRow`

- **File:** `react-frontend/src/components/ui/table.jsx`
- **Lines:** `15-17`
- **Purpose:** Renders the `TableRow` component.

**Code:**
```jsx
export function TableRow({ className, ...props }) {
  return <tr className={cn("border-b transition-colors hover:bg-muted/50", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `TableRow` view or widget.

### `TableHead`

- **File:** `react-frontend/src/components/ui/table.jsx`
- **Lines:** `19-21`
- **Purpose:** Renders the `TableHead` component.

**Code:**
```jsx
export function TableHead({ className, ...props }) {
  return <th className={cn("h-10 px-3 text-left font-medium text-muted-foreground", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `TableHead` view or widget.

### `TableCell`

- **File:** `react-frontend/src/components/ui/table.jsx`
- **Lines:** `23-25`
- **Purpose:** Renders the `TableCell` component.

**Code:**
```jsx
export function TableCell({ className, ...props }) {
  return <td className={cn("p-3 align-middle", className)} {...props} />;
}
```

**Explanation:** This React component renders UI for the `TableCell` view or widget.

## `react-frontend/src/components/ui/tooltip.jsx`

### `TooltipContent`

- **File:** `react-frontend/src/components/ui/tooltip.jsx`
- **Lines:** `12-26`
- **Purpose:** Renders the `TooltipContent` component.

**Code:**
```jsx
const TooltipContent = React.forwardRef(
  ({ className, sideOffset = 4, children, ...props }, ref) => (
    <TooltipPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      className={cn(
        "z-50 overflow-hidden rounded-md border bg-popover px-3 py-1.5 text-sm text-popover-foreground shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
      {...props}
    >
      {children}
    </TooltipPrimitive.Content>
  )
)
```

**Explanation:** This React component renders UI for the `TooltipContent` view or widget.

## `react-frontend/src/context/AuthContext.jsx`

### `AuthProvider`

- **File:** `react-frontend/src/context/AuthContext.jsx`
- **Lines:** `8-147`
- **Purpose:** Renders the `AuthProvider` component.

**Code:**
```jsx
export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [role, setRole] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [emailConfirmed, setEmailConfirmed] = useState(false);

  useEffect(() => {
    let isMounted = true;

    supabase.auth.getSession().then(({ data }) => {
      if (!isMounted) return;
      setSession(data.session);
      setEmailConfirmed(!!data.session?.user?.email_confirmed_at);
      setLoading(false);
    });

    const { data: listener } = supabase.auth.onAuthStateChange((_event, newSession) => {
      setSession(newSession);
      setEmailConfirmed(!!newSession?.user?.email_confirmed_at);
    });

    return () => {
      isMounted = false;
      listener.subscription.unsubscribe();
    };
  }, []);

  // Fetch user role and profile whenever the session changes
  useEffect(() => {
    if (!session?.user) {
      setRole(null);
      setProfile(null);
      return;
    }

    const fetchRoleAndProfile = async () => {
      try {
        // Fetch role + profile from backend (bypasses RLS, authoritative source)
        const res = await fetch(`${getApiBaseUrl()}/protected/me`, {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
        if (res.ok) {
          const data = await res.json();
          const backendRole = data.user?.role;
          if (backendRole) {
            console.log("[AuthContext] Role from backend:", backendRole);
            setRole(backendRole);
          } else {
            setRole("user");
          }
        } else {
          console.error("[AuthContext] /protected/me failed:", res.status);
          setRole("user");
        }

        // Fetch profile from backend (bypasses RLS infinite recursion)
        const profileRes = await fetch(`${getApiBaseUrl()}/protected/profile`, {
          headers: { Authorization: `Bearer ${session.access_token}` },
        });
        if (profileRes.ok) {
          const profileJson = await profileRes.json();
          if (profileJson.profile) {
            setProfile(profileJson.profile);
          }
        } else {
          console.error("[AuthContext] /protected/profile failed:", profileRes.status);
        }
      } catch (err) {
        console.error("[AuthContext] Unexpected error fetching role/profile:", err);
        setRole("user");
      }
    };

    fetchRoleAndProfile();

    // Sync OAuth avatar from auth metadata to profiles
    fetch(`${getApiBaseUrl()}/protected/sync-avatar`, {
      method: "POST",
      headers: { Authorization: `Bearer ${session.access_token}` },
    }).catch(() => {});
  }, [session]);

  const isAdmin = role === "admin" || role === "dev";
  const effectivePlan = isAdmin ? "premium" : "free";
  const isPremium = isAdmin;

  const value = useMemo(
    () => ({
      session,
      user: session?.user ?? null,
      accessToken: session?.access_token ?? null,
      profile,
      loading,
      role,
      isAdmin,
      effectivePlan,
      isPremium,
      emailConfirmed,
      signInWithProvider: (provider) =>
        supabase.auth.signInWithOAuth({
          provider,
          options: { redirectTo: `${window.location.origin}/login` },
        }),
      signInWithPassword: (email, password) =>
        supabase.auth.signInWithPassword({ email, password }),
      signUp: async (email, password, options = {}) => {
        const { data, error } = await supabase.auth.signUp({ email, password, options });
        return {
          user: data?.user ?? null,
          session: data?.session ?? null,
          error,
          // If session is null, email confirmation is required
          confirmationRequired: !data?.session && !error,
        };
      },
      resetPassword: (email) =>
        supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/reset-password`
        }),
      updatePassword: (newPassword) => supabase.auth.updateUser({ password: newPassword }),
      signOut: () => {
        setEmailConfirmed(false);
        return supabase.auth.signOut();
      },
      refreshProfile: async () => {
        if (!session?.user) return;
        const { data } = await supabase
          .from("profiles")
          .select("*")
          .eq("id", session.user.id)
          .single();
        if (data) setProfile(data);
      },
    }),
    [session, loading, role, isAdmin, effectivePlan, isPremium, profile, emailConfirmed]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
```

**Explanation:** This React component renders UI for the `AuthProvider` view or widget.

## `react-frontend/src/context/ThemeContext.jsx`

### `ThemeProvider`

- **File:** `react-frontend/src/context/ThemeContext.jsx`
- **Lines:** `7-32`
- **Purpose:** Renders the `ThemeProvider` component.

**Code:**
```jsx
export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");

  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved === "dark" || saved === "light") {
      setTheme(saved);
    }
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    localStorage.setItem(STORAGE_KEY, theme);
  }, [theme]);

  const value = useMemo(
    () => ({
      theme,
      setTheme,
      toggleTheme: () => setTheme((prev) => (prev === "dark" ? "light" : "dark"))
    }),
    [theme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
```

**Explanation:** This React component renders UI for the `ThemeProvider` view or widget.

## `react-frontend/src/hooks/useAuth.js`

### `useAuth`

- **File:** `react-frontend/src/hooks/useAuth.js`
- **Lines:** `5-7`
- **Purpose:** Custom React hook `useAuth`.

**Code:**
```javascript
export function useAuth() {
  return useContext(AuthContext);
}
```

**Explanation:** This hook returns state and helpers used by React components. See the code for the full implementation.

## `react-frontend/src/hooks/useTheme.js`

### `useTheme`

- **File:** `react-frontend/src/hooks/useTheme.js`
- **Lines:** `5-7`
- **Purpose:** Custom React hook `useTheme`.

**Code:**
```javascript
export function useTheme() {
  return useContext(ThemeContext);
}
```

**Explanation:** This hook returns state and helpers used by React components. See the code for the full implementation.

## `react-frontend/src/i18n/index.jsx`

### `getByPath`

- **File:** `react-frontend/src/i18n/index.jsx`
- **Lines:** `7-9`
- **Purpose:** Retrieves ByPath.

**Code:**
```jsx
function getByPath(obj, path) {
  return path.split(".").reduce((acc, part) => (acc ? acc[part] : undefined), obj);
}
```

**Explanation:** This function retrieves ByPath. See the code for the full implementation.

### `I18nProvider`

- **File:** `react-frontend/src/i18n/index.jsx`
- **Lines:** `13-45`
- **Purpose:** Renders the `I18nProvider` component.

**Code:**
```jsx
export function I18nProvider({ children, defaultLocale = "en" }) {
  const [locale, setLocaleState] = useState(() => {
    if (typeof window === "undefined") return defaultLocale;
    const saved = window.localStorage.getItem("lumi-locale");
    if (saved && DICTIONARIES[saved]) return saved;
    const nav = navigator.language?.slice(0, 2);
    if (nav && DICTIONARIES[nav]) return nav;
    return defaultLocale;
  });

  const setLocale = useCallback((next) => {
    if (DICTIONARIES[next]) {
      setLocaleState(next);
      if (typeof window !== "undefined") {
        window.localStorage.setItem("lumi-locale", next);
      }
    }
  }, []);

  const t = useCallback(
    (key, params = {}) => {
      const current = DICTIONARIES[locale];
      const template = getByPath(current, key) ?? getByPath(en, key) ?? key;
      if (Array.isArray(template) || typeof template !== "string") return template;
      return template.replace(/\{\{(\w+)\}\}/g, (_, p) => (params[p] !== undefined ? String(params[p]) : `{{${p}}}`));
    },
    [locale]
  );

  const value = useMemo(() => ({ locale, setLocale, t }), [locale, setLocale, t]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}
```

**Explanation:** This React component renders UI for the `I18nProvider` view or widget.

### `useI18n`

- **File:** `react-frontend/src/i18n/index.jsx`
- **Lines:** `47-51`
- **Purpose:** Custom React hook `useI18n`.

**Code:**
```jsx
export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within an I18nProvider");
  return ctx;
}
```

**Explanation:** This hook returns state and helpers used by React components. See the code for the full implementation.

### `Trans`

- **File:** `react-frontend/src/i18n/index.jsx`
- **Lines:** `53-66`
- **Purpose:** Renders the `Trans` component.

**Code:**
```jsx
export function Trans({ k, components = {} }) {
  const { t } = useI18n();
  const template = t(k);
  if (typeof template !== "string") return null;

  const parts = template.split(/(\{\{\w+\}\})/g);
  return parts.map((part, i) => {
    const match = part.match(/^\{\{(\w+)\}\}$/);
    if (match && components[match[1]] !== undefined) {
      return <Fragment key={i}>{components[match[1]]}</Fragment>;
    }
    return <Fragment key={i}>{part}</Fragment>;
  });
}
```

**Explanation:** This React component renders UI for the `Trans` view or widget.

## `react-frontend/src/layouts/MainLayout.jsx`

### `MainLayout`

- **File:** `react-frontend/src/layouts/MainLayout.jsx`
- **Lines:** `5-14`
- **Purpose:** Renders the `MainLayout` component.

**Code:**
```jsx
export default function MainLayout() {
  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `MainLayout` view or widget.

## `react-frontend/src/lib/utils.js`

### `cn`

- **File:** `react-frontend/src/lib/utils.js`
- **Lines:** `4-6`
- **Purpose:** Utility function `cn`.

**Code:**
```javascript
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
```

**Explanation:** This helper performs the `cn` operation. See the code for the full implementation.

## `react-frontend/src/pages/About.jsx`

### `Cite`

- **File:** `react-frontend/src/pages/About.jsx`
- **Lines:** `23-29`
- **Purpose:** Renders the `Cite` component.

**Code:**
```jsx
function Cite({ children }) {
  return (
    <span className="text-sm font-medium text-primary/80">
      {" "}({children})
    </span>
  );
}
```

**Explanation:** This React component renders UI for the `Cite` view or widget.

### `SectionHeading`

- **File:** `react-frontend/src/pages/About.jsx`
- **Lines:** `31-49`
- **Purpose:** Renders the `SectionHeading` component.

**Code:**
```jsx
function SectionHeading({ badge, title, subtitle }) {
  return (
    <div className="mx-auto max-w-3xl text-center space-y-4">
      {badge && (
        <Badge variant="secondary" className="text-xs font-medium tracking-wide uppercase">
          {badge}
        </Badge>
      )}
      <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
        {title}
      </h2>
      {subtitle && (
        <p className="text-lg text-muted-foreground leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `SectionHeading` view or widget.

### `ValueCard`

- **File:** `react-frontend/src/pages/About.jsx`
- **Lines:** `51-63`
- **Purpose:** Renders the `ValueCard` component.

**Code:**
```jsx
function ValueCard({ icon: Icon, title, description }) {
  return (
    <Card className="border-border/60 bg-card/80 transition-all hover:border-primary/30 hover:shadow-md">
      <CardHeader className="space-y-3">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
          <Icon className="h-6 w-6" />
        </div>
        <CardTitle className="text-xl">{title}</CardTitle>
        <CardDescription className="text-sm leading-relaxed">{description}</CardDescription>
      </CardHeader>
    </Card>
  );
}
```

**Explanation:** This React component renders UI for the `ValueCard` view or widget.

### `TechItem`

- **File:** `react-frontend/src/pages/About.jsx`
- **Lines:** `65-82`
- **Purpose:** Renders the `TechItem` component.

**Code:**
```jsx
function TechItem({ icon: Icon, title, items }) {
  return (
    <div className="rounded-2xl border border-border/60 bg-card p-6 transition-all hover:border-primary/30 hover:shadow-md">
      <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
        <Icon className="h-6 w-6" />
      </div>
      <h3 className="text-lg font-semibold text-foreground">{title}</h3>
      <ul className="mt-3 space-y-2">
        {items.map((item) => (
          <li key={item} className="flex items-center gap-2 text-sm text-muted-foreground">
            <span className="inline-block h-1.5 w-1.5 rounded-full bg-brand-success" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `TechItem` view or widget.

### `About`

- **File:** `react-frontend/src/pages/About.jsx`
- **Lines:** `84-520`
- **Purpose:** Renders the `About` component.

**Code:**
```jsx
export default function About() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col">
      {/* HERO */}
      <section className="relative overflow-hidden border-b border-border/40">
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-muted/50" />
        <div className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-accent/20 blur-3xl" />
        <div className="absolute -bottom-24 -left-24 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />

        <div className="relative page-container py-16 sm:py-24">
          <div className="mx-auto max-w-4xl text-center space-y-6">
            <Badge
              variant="outline"
              className="border-primary/30 bg-primary/5 text-primary px-3 py-1 text-sm"
            >
              {t("about.hero.badge")}
            </Badge>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl md:text-6xl">
              {t("about.hero.title")}{" "}
              <span className="bg-gradient-to-r from-primary to-brand-success bg-clip-text text-transparent">
                {t("about.hero.titleHighlight")}
              </span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl">
              {t("about.hero.subtitle")}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <Link to="/energyhub">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <BarChart3 className="h-5 w-5" />
                  {t("about.hero.tryEnergyHub")}
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  {t("about.hero.tryEcosim")}
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ABOUT LUMI */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <div className="grid gap-12 lg:grid-cols-2 items-center">
          <div className="space-y-6">
            <Badge variant="secondary" className="uppercase tracking-wide text-xs">
              {t("about.problem.badge")}
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              {t("about.problem.title")}
            </h2>
            <div className="space-y-4 text-muted-foreground leading-relaxed">
              <p>
                <Trans
                  k="about.problem.paragraph1"
                  components={{
                    c1: <Cite>Gonocruz et al., 2024</Cite>,
                    c2: <Cite>Zhindon-Almeida &amp; Ruiz-Carrillo, 2025; Rana et al., 2025</Cite>,
                    c3: <Cite>Wong et al., 2023</Cite>
                  }}
                />
              </p>
              <p>
                <Trans
                  k="about.problem.paragraph2"
                  components={{
                    c1: <Cite>Lenain, 2026</Cite>,
                    c2: <Cite>Esiri et al., 2024; Aguilera et al., 2024</Cite>
                  }}
                />
              </p>
              <p>
                <Trans
                  k="about.problem.paragraph3"
                  components={{
                    c1: <Cite>Beriro et al., 2022; Bączkiewicz et al., 2024</Cite>
                  }}
                />
              </p>
            </div>
          </div>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
              <div className="text-3xl font-bold text-primary">{t("about.problem.stats.fossilShare.value")}</div>
              <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.fossilShare.label")}</div>
              <div className="text-xs text-muted-foreground mt-1">
                <Trans
                  k="about.problem.stats.fossilShare.description"
                  components={{ c1: <Cite>Gonocruz et al., 2024</Cite> }}
                />
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6">
              <div className="text-3xl font-bold text-primary">{t("about.problem.stats.renewableShare.value")}</div>
              <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.renewableShare.label")}</div>
              <div className="text-xs text-muted-foreground mt-1">
                <Trans
                  k="about.problem.stats.renewableShare.description"
                  components={{ c1: <Cite>Gonocruz et al., 2024</Cite> }}
                />
              </div>
            </div>
            <div className="rounded-2xl border border-border/60 bg-gradient-to-br from-card to-muted/30 p-6 sm:col-span-2">
              <div className="text-3xl font-bold text-primary">{t("about.problem.stats.barriers.value")}</div>
              <div className="text-sm font-medium text-foreground mt-1">{t("about.problem.stats.barriers.label")}</div>
              <div className="text-xs text-muted-foreground mt-1">
                <Trans
                  k="about.problem.stats.barriers.description"
                  components={{ c1: <Cite>Zhindon-Almeida &amp; Ruiz-Carrillo, 2025</Cite> }}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MISSION & VISION */}
      <section className="relative overflow-hidden border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge={t("about.mission.badge")}
            title={t("about.mission.title")}
            subtitle={t("about.mission.subtitle")}
          />

          <div className="grid gap-6 md:grid-cols-2">
            <ValueCard
              icon={Globe}
              title={t("about.mission.mission.title")}
              description={t("about.mission.mission.description")}
            />
            <ValueCard
              icon={Lightbulb}
              title={t("about.mission.vision.title")}
              description={t("about.mission.vision.description")}
            />
          </div>
        </div>
      </section>

      {/* RESEARCH BACKGROUND */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge={t("about.research.badge")}
          title={t("about.research.title")}
          subtitle={t("about.research.subtitle")}
        />

        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <BookOpen className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.research.educational.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                <Trans
                  k="about.research.educational.description"
                  components={{ c1: <Cite>Aguilera et al., 2024</Cite> }}
                />
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <Microscope className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.research.decisionSupport.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                <Trans
                  k="about.research.decisionSupport.description"
                  components={{ c1: <Cite>Estévez et al., 2021; Witt &amp; Klumpp, 2021</Cite> }}
                />
              </CardDescription>
            </CardHeader>
          </Card>
          <Card className="border-border/60 bg-card/80">
            <CardHeader className="space-y-3">
              <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
                <FlaskConical className="h-6 w-6" />
              </div>
              <CardTitle>{t("about.research.researchGroundwork.title")}</CardTitle>
              <CardDescription className="text-sm leading-relaxed">
                <Trans
                  k="about.research.researchGroundwork.description"
                  components={{ c1: <Cite>Bassetti, 2024</Cite> }}
                />
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-card to-muted/30 p-6 sm:p-8">
          <h3 className="text-lg font-semibold text-foreground mb-3">
            {t("about.research.problemStatement.title")}
          </h3>
          <p className="text-muted-foreground leading-relaxed">
            <Trans
              k="about.research.problemStatement.description"
              components={{
                c1: <Cite>Wong et al., 2023</Cite>,
                c2: <Cite>Gonocruz et al., 2024</Cite>,
                c3: <Cite>Zhindon-Almeida &amp; Ruiz-Carrillo, 2025; Rana et al., 2025</Cite>,
                c4: <Cite>Beriro et al., 2022; Bączkiewicz et al., 2024</Cite>
              }}
            />
          </p>
        </div>
      </section>

      {/* SYSTEM OVERVIEW */}
      <section className="relative overflow-hidden border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge={t("about.system.badge")}
            title={t("about.system.title")}
            subtitle={t("about.system.subtitle")}
          />

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {[
              { icon: BarChart3, key: "energyHub", cites: { c1: <Cite>"Dashboard," 2026; What Is Data Visualization?, n.d.</Cite>, c2: <Cite>Das et al., 2022; Bandara et al., 2026</Cite> } },
              { icon: Zap, key: "ecosim", cites: { c1: <Cite>Shatnawi et al., 2021</Cite> } },
              { icon: BrainCircuit, key: "ai", cites: { c1: <Cite>Panagoulias et al., 2023</Cite>, c2: <Cite>Algburi et al., 2025</Cite> } },
              { icon: Database, key: "dataViz", cites: { c1: <Cite>What Is Data Visualization?, n.d.</Cite>, c2: <Cite>Mustafa &amp; Al-Yozbaky, 2025</Cite> } }
            ].map(({ icon: Icon, key, cites }) => (
              <div key={key} className="rounded-2xl border border-border/60 bg-card p-6 text-center transition-all hover:border-primary/30 hover:shadow-md">
                <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
                  <Icon className="h-7 w-7" />
                </div>
                <h3 className="text-lg font-semibold text-foreground">{t(`about.system.modules.${key}.title`)}</h3>
                <p className="mt-2 text-sm text-muted-foreground leading-relaxed">
                  <Trans k={`about.system.modules.${key}.description`} components={cites} />
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* TECHNOLOGY STACK */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge={t("about.technology.badge")}
          title={t("about.technology.title")}
          subtitle={t("about.technology.subtitle")}
        />

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <TechItem
            icon={Monitor}
            title={t("about.technology.frontend.title")}
            items={t("about.technology.frontend.items")}
          />
          <TechItem
            icon={Server}
            title={t("about.technology.backend.title")}
            items={t("about.technology.backend.items")}
          />
          <TechItem
            icon={Database}
            title={t("about.technology.database.title")}
            items={t("about.technology.database.items")}
          />
          <TechItem
            icon={BrainCircuit}
            title={t("about.technology.ai.title")}
            items={t("about.technology.ai.items")}
          />
        </div>

        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-primary/5 to-accent/5 p-6 sm:p-8 text-center">
          <h3 className="text-xl font-semibold text-foreground">
            {t("about.technology.impact.title")}
          </h3>
          <p className="mx-auto mt-3 max-w-2xl text-muted-foreground leading-relaxed">
            {t("about.technology.impact.description")}
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-3">
            {t("about.technology.impact.tags").map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center rounded-full bg-card border border-border/60 px-3 py-1 text-xs font-medium text-muted-foreground"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </section>

      {/* REFERENCES */}
      <section className="border-t border-border/40 bg-muted/20">
        <div className="page-container py-12">
          <div className="mx-auto max-w-4xl space-y-6">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
              {t("about.references")}
            </h3>
            <ol className="space-y-3 text-xs text-muted-foreground list-decimal list-inside">
              <li>
                Abdullah, A. G., Utami, H. P., Gunawan, B., Ratmono, B. M., & Pasaribu, N. T. (2025).
                Multi-criteria decision-making for wind power project feasibility: Trends, techniques, and future directions.
                <em> Cleaner Engineering and Technology</em>, 27, 100987.
              </li>
              <li>
                Aguilera, F., Reyes, R., Schueftan, A., Zerriffi, H., & Sanhueza, R. (2024).
                Understanding the role of people&apos;s preferences and perceptions in the analysis of residential energy transition: A meta-analysis.
                <em> Energy for Sustainable Development</em>, 82, 101534.
              </li>
              <li>
                Algburi, S., Kareem, S. S. a. A., Sapaev, I., Mukhitdinov, O., Hassan, Q., Khalaf, D. H., & Jabbar, F. I. (2025).
                The role of artificial intelligence in accelerating renewable energy adoption for global energy transformation.
                <em> Unconventional Resources</em>, 8, 100229.
              </li>
              <li>
                Bandara, A., Pandukabhaya, M., Ratnayake, K., Godaliyadda, R., Ekanayake, P., & Ekanayake, J. (2026).
                LSTM based model for weather-based Solar Irradiance Prediction for Long-Term PV Energy Planning.
                In <em>2025 IEEE 19th International Conference on Industrial and Information Systems (ICIIS)</em> (pp. 376–381).
              </li>
              <li>
                Bassetti, (2024). Environmental intelligence. <em>EcoMagazine</em>.
              </li>
              <li>
                Bączkiewicz, A., Wątróbski, J., Jankowski, J., & Sałabun, W. (2024).
                Multi-criteria Temporal Intelligent Decision Support System for Sustainable Energy Mix assessment.
                In <em>Lecture notes in computer science</em> (pp. 95–106).
              </li>
              <li>
                Beriro, D., Nathanail, J., Salazar, J., Kingdon, A., Marchant, A., Richardson, S., et al. (2022).
                A decision support system to assess the feasibility of onshore renewable energy infrastructure.
                <em> Renewable and Sustainable Energy Reviews</em>, 168, 112771.
              </li>
              <li>
                Das, U. K., Tey, K. S., Idris, M. Y. I. B., Mekhilef, S., Seyedmahmoudian, M., Stojcevski, A., & Horan, B. (2022).
                Optimized support Vector Regression-Based model for solar power generation forecasting on the basis of online weather reports.
                <em> IEEE Access</em>, 10, 15594–15604.
              </li>
              <li>
                Esiri, A. E., Kwakye, J. M., Ekechukwu, D. E., Ogundipe, O. B., & Ikevuje, A. H. (2024).
                Public perception and policy development in the transition to renewable energy.
                <em> Magna Scientia Advanced Research and Reviews</em>, 8(2), 228–237.
              </li>
              <li>
                Estévez, R. A., Espinoza, V., Ponce Oliva, R. D., Vásquez-Lavín, F., & Gelcich, S. (2021).
                Multi-criteria decision analysis for renewable energies: research trends, gaps and the challenge of improving participation.
                <em> Sustainability</em>, 13(6), 3515.
              </li>
              <li>
                Gonocruz, R. a. T., Yoshida, Y., Silava, N. E., Aguirre, R. A., Maguindayao, E. J. H., Ozawa, A., & Santiago, J. V. (2024).
                A multi-scenario evaluation of the energy transition mechanism in the Philippines towards decarbonization.
                <em> Journal of Cleaner Production</em>, 438, 140819.
              </li>
              <li>
                Lenain (2026). The Philippines&apos; climate adaptation initiatives. <em>Encyclopedia Britannica</em>.
              </li>
              <li>
                Mustafa, A. T., & Al-Yozbaky, O. S. A. (2025).
                Forecasting energy demand and generation using time series models: A comparative analysis of classical, grey, fuzzy, and intelligent approaches.
                <em> Franklin Open</em>, 12, 100350.
              </li>
              <li>
                Panagoulias, D. P., Sarmas, E., Marinakis, V., Virvou, M., Tsihrintzis, G. A., & Doukas, H. (2023).
                Intelligent Decision Support for Energy Management: A methodology for Tailored explainability of Artificial intelligence analytics.
                <em> Electronics</em>, 12(21), 4430.
              </li>
              <li>
                Rana, M., Mamun, M. a. A., Hossain, M. K., Rekha, R. S., & Alam, S. M. S. (2025).
                Understanding the adoption of renewable energy technologies by households in South Asia: a theory of planned behavior perspective.
                <em> Discover Sustainability</em>, 6(1).
              </li>
              <li>
                Shatnawi, N., Abu-Qdais, H., & Qdais, F. A. (2021).
                Selecting renewable energy options: an application of multi-criteria decision making for Jordan.
                <em> Sustainability Science Practice and Policy</em>, 17(1), 209–219.
              </li>
              <li>
                What Is Data Visualization? Definition, Examples, And Learning Resources. (n.d.). Tableau.
                https://www.tableau.com/visualization/what-is-data-visualization
              </li>
              <li>
                Witt, T., & Klumpp, M. (2021).
                Multi-period multi-criteria decision making under uncertainty: a renewable energy transition case from Germany.
                <em> Sustainability</em>, 13(11), 6300.
              </li>
              <li>
                Wong, G., Wong, K., Lau, T., Lee, J., & Kok, Y. (2023).
                Study of intention to use renewable energy technology in Malaysia using TAM and TPB.
                <em> Renewable Energy</em>, 221, 119787.
              </li>
              <li>
                Zhindon-Almeida, R. G., & Ruiz-Carrillo, J. A. (2025).
                Factors Influencing the Adoption of Renewable Energies in Developing Countries.
                <em> Sustainable Development</em>, 33(5), 7222–7244.
              </li>
            </ol>
          </div>
        </div>
      </section>

      {/* FOOTER CTA */}
      <section className="relative overflow-hidden border-t border-border/40">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
        <div className="relative page-container py-16 sm:py-20">
          <div className="mx-auto max-w-3xl text-center space-y-6">
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              {t("about.footer.title")}
            </h2>
            <p className="mx-auto max-w-xl text-lg text-muted-foreground leading-relaxed">
              {t("about.footer.subtitle")}
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link to="/energyhub">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <BarChart3 className="h-5 w-5" />
                  {t("about.footer.tryEnergyHub")}
                </Button>
              </Link>
              <Link to="/ecosim">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <Zap className="h-5 w-5" />
                  {t("about.footer.launchEcosim")}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `About` view or widget.

## `react-frontend/src/pages/ChatPage.jsx`

### `formatCitations`

- **File:** `react-frontend/src/pages/ChatPage.jsx`
- **Lines:** `10-28`
- **Purpose:** Converts Citations.

**Code:**
```jsx
function formatCitations(text) {
  if (!text) return text;
  const parts = text.split(/(\[Source \d+:[^\]]+\])/g);
  return parts.map((part, idx) => {
    const match = part.match(/^\[Source (\d+):\s*(.+)]$/);
    if (match) {
      return (
        <span
          key={idx}
          className="inline-flex items-center gap-1 rounded-md bg-emerald-100 px-1.5 py-0.5 text-xs font-semibold text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200 mx-0.5"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          {match[2]}
        </span>
      );
    }
    return <span key={idx}>{part}</span>;
  });
}
```

**Explanation:** This function converts Citations. See the code for the full implementation.

### `ChatPage`

- **File:** `react-frontend/src/pages/ChatPage.jsx`
- **Lines:** `30-195`
- **Purpose:** Renders the `ChatPage` component.

**Code:**
```jsx
export default function ChatPage() {
  const { t } = useI18n();
  const { user, accessToken } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(searchParams.get("session") || null);

  // Load existing session messages
  useEffect(() => {
    const sid = searchParams.get("session");
    if (!sid || !user?.id) return;

    setSessionId(sid);

    const loadMessages = async () => {
      const { data, error } = await supabase
        .from("chat_messages")
        .select("role, content, created_at")
        .eq("session_id", sid)
        .order("created_at", { ascending: true });

      if (error) {
        toast.error(t("chat.failedToLoadHistory"));
        return;
      }

      if (data) {
        setMessages(data.map((m) => ({ role: m.role, content: m.content })));
      }
    };

    loadMessages();
  }, [searchParams, user]);

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(null);
    setSearchParams({});
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    let currentSessionId = sessionId;

    try {
      // Create session on first message
      if (!currentSessionId && user?.id) {
        const title = input.trim().slice(0, 30) + (input.length > 30 ? "..." : "");
        const { data: session, error } = await supabase
          .from("chat_sessions")
          .insert({ user_id: user.id, title })
          .select("id")
          .single();

        if (error) throw new Error(t("chat.failedToCreateSession"));
        currentSessionId = session.id;
        setSessionId(currentSessionId);
        setSearchParams({ session: currentSessionId });
      }

      // Persist user message
      if (currentSessionId) {
        await supabase.from("chat_messages").insert({
          session_id: currentSessionId,
          role: "user",
          content: userMsg.content,
        });
      }

      const res = await fetch(`${getApiBaseUrl()}/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ message: userMsg.content }),
      });

      if (!res.ok) {
        throw new Error(t("chat.serverError", { status: res.status, statusText: res.statusText }));
      }

      const data = await res.json();
      if (data.message) {
        const assistantMsg = { role: "assistant", content: data.message };
        setMessages((prev) => [...prev, assistantMsg]);

        // Persist assistant message
        if (currentSessionId) {
          await supabase.from("chat_messages").insert({
            session_id: currentSessionId,
            role: "assistant",
            content: data.message,
          });
        }
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${err.message}` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-4xl mx-auto p-4">
      <div className="flex items-center justify-between mb-4">
        <h1 className="text-2xl font-bold">{t("chat.title")}</h1>
        <Button variant="outline" size="sm" onClick={handleNewChat}>
          {t("chat.newChat")}
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto border rounded-lg p-4 space-y-3 bg-muted/30">
        {messages.length === 0 && (
          <p className="text-muted-foreground text-center mt-8">
            {t("chat.empty")}
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-3 rounded-lg max-w-[80%] ${
              m.role === "user"
                ? "bg-primary text-primary-foreground ml-auto"
                : "bg-muted"
            }`}
          >
            {m.role === "assistant" ? formatCitations(m.content) : m.content}
          </div>
        ))}
        {isLoading && (
          <div className="bg-muted p-3 rounded-lg max-w-[80%] animate-pulse">
            {t("chat.thinking")}
          </div>
        )}
      </div>
      <div className="flex gap-2 mt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder={t("chat.placeholder")}
          className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <button
          onClick={handleSend}
          disabled={isLoading}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
        >
          {t("chat.send")}
        </button>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `ChatPage` view or widget.

## `react-frontend/src/pages/Dashboard.jsx`

### `Dashboard`

- **File:** `react-frontend/src/pages/Dashboard.jsx`
- **Lines:** `21-467`
- **Purpose:** Renders the `Dashboard` component.

**Code:**
```jsx
export default function Dashboard() {
  const { user, refreshProfile, isAdmin } = useAuth();
  const { t } = useI18n();
  const isLoggedIn = !!user;

  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [editForm, setEditForm] = useState({ full_name: "", organization: "", location: "" });
  const [savingProfile, setSavingProfile] = useState(false);

  const [savedLocations, setSavedLocations] = useState([]);
  const [savedSimulations, setSavedSimulations] = useState([]);
  const [municipalities, setMunicipalities] = useState([]);
  const [selectedMuni, setSelectedMuni] = useState("");
  const [compositeScore, setCompositeScore] = useState(0);

  const fileInputRef = useRef(null);

  // Load dashboard data
  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // Profile (if logged in)
        if (isLoggedIn) {
          const { data: prof } = await supabase
            .from("profiles")
            .select("*")
            .eq("id", user.id)
            .single();
          setProfile(prof);
          setEditForm({
            full_name: prof?.full_name || "",
            organization: prof?.organization || "",
            location: prof?.location || "",
          });

          // Saved locations
          const { data: locs } = await supabase
            .from("saved_locations")
            .select("*, municipalities(name)")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          setSavedLocations(locs || []);

          // Saved simulations
          const { data: sims } = await supabase
            .from("saved_simulations")
            .select("*, municipalities(name)")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false });
          setSavedSimulations(sims || []);
        }

        // Municipalities for dropdown
        const { data: munis } = await supabase
          .from("municipalities")
          .select("municipality_id, name")
          .order("name", { ascending: true })
          .limit(500);
        setMunicipalities(munis || []);
      } catch (err) {
        toast.error(t("dashboard.loadError"));
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [isLoggedIn, user?.id]);

  const fetchCompositeScore = async (muniId) => {
    if (!muniId) return;
    try {
      const [solar, wind, hydro, geo] = await Promise.all([
        supabase.from("solar_suitability").select("solar_score").eq("municipality_id", muniId).single(),
        supabase.from("wind_suitability").select("wind_score").eq("municipality_id", muniId).single(),
        supabase.from("hydropower_suitability").select("hydro_suitability_score").eq("municipality_id", muniId).single(),
        supabase.from("geothermal_suitability").select("geothermal_score").eq("municipality_id", muniId).single(),
      ]);
      const scores = [
        solar.data?.solar_score || 0,
        wind.data?.wind_score || 0,
        hydro.data?.hydro_suitability_score || 0,
        geo.data?.geothermal_score || 0,
      ];
      const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
      setCompositeScore(Math.round(Math.min(100, Math.max(0, avg))));
    } catch {
      setCompositeScore(0);
    }
  };

  useEffect(() => {
    if (selectedMuni) fetchCompositeScore(selectedMuni);
  }, [selectedMuni]);

  // Profile save
  const handleSaveProfile = async () => {
    if (!isLoggedIn) {
      toast.info(t("dashboard.loginToSaveProfileToast"));
      return;
    }
    setSavingProfile(true);
    try {
      const { error } = await supabase
        .from("profiles")
        .update({
          full_name: editForm.full_name,
          organization: editForm.organization,
          location: editForm.location,
          updated_at: new Date().toISOString(),
        })
        .eq("id", user.id);

      if (error) throw error;

      setProfile((prev) => ({
        ...prev,
        full_name: editForm.full_name,
        organization: editForm.organization,
        location: editForm.location,
      }));
      setIsEditingProfile(false);
      toast.success(t("dashboard.profileUpdated"));
    } catch (err) {
      toast.error(t("dashboard.profileUpdateFailed"));
    } finally {
      setSavingProfile(false);
    }
  };

  // Avatar upload
  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file || !isLoggedIn) return;

    if (file.size > 2 * 1024 * 1024) {
      toast.error(t("dashboard.imageTooLarge"));
      return;
    }

    const ext = file.name.split(".").pop();
    const path = `${user.id}/avatar.${ext}`;

    try {
      setSavingProfile(true);
      const { error: uploadError } = await supabase.storage
        .from("avatars")
        .upload(path, file, { upsert: true });

      if (uploadError) throw uploadError;

      const { data: urlData } = supabase.storage.from("avatars").getPublicUrl(path);
      const avatarUrl = urlData.publicUrl;

      const { error: updateError } = await supabase
        .from("profiles")
        .update({ avatar_url: avatarUrl })
        .eq("id", user.id);

      if (updateError) throw updateError;

      setProfile((prev) => ({ ...prev, avatar_url: avatarUrl }));
      if (refreshProfile) await refreshProfile();
      toast.success(t("dashboard.photoUpdated"));
    } catch (err) {
      toast.error(t("dashboard.uploadFailed") + err.message);
    } finally {
      setSavingProfile(false);
    }
  };

  const displayName = profile?.full_name || user?.email || t("common.guest");
  const displayOrg = profile?.organization || "";
  const displayLoc = profile?.location || "";
  const avatarUrl = profile?.avatar_url || "";

  if (loading) {
    return (
      <section className="page-container stack">
        <h1 className="text-2xl font-bold">{t("dashboard.title")}</h1>
        <LoadingSkeleton />
      </section>
    );
  }

  return (
    <section className="page-container stack space-y-6">
      {isAdmin && (
        <div className="rounded-lg border bg-primary/10 p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <p className="text-sm font-medium">{t("dashboard.adminLink")}</p>
          <Link to="/admin">
            <Button variant="outline" size="sm">{t("nav.adminPortal")}</Button>
          </Link>
        </div>
      )}
      {/* ===== Profile Card ===== */}
      <Card className="overflow-hidden">
        <div className="bg-gradient-to-r from-primary/10 to-primary/5 px-6 py-6">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
            {/* Avatar */}
            <div className="relative shrink-0">
              <div className="w-20 h-20 rounded-full bg-muted border-2 border-background overflow-hidden flex items-center justify-center">
                {avatarUrl ? (
                  <img src={avatarUrl} alt="avatar" className="w-full h-full object-cover" />
                ) : (
                  <span className="text-2xl font-bold text-muted-foreground">
                    {displayName.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>
              {isLoggedIn && (
                <>
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="absolute -bottom-1 -right-1 bg-primary text-primary-foreground text-xs rounded-full px-2 py-0.5 shadow hover:bg-primary/90"
                    disabled={savingProfile}
                  >
                    {savingProfile ? "..." : t("common.edit")}
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    className="hidden"
                    onChange={handleAvatarUpload}
                  />
                </>
              )}
            </div>

            {/* Profile Info */}
            <div className="flex-1 min-w-0">
              {!isEditingProfile ? (
                <div className="space-y-1">
                  <h2 className="text-xl font-bold truncate">{displayName}</h2>
                  {(displayOrg || displayLoc) && (
                    <p className="text-sm text-muted-foreground">
                      {displayOrg && <span className="mr-3">{displayOrg}</span>}
                      {displayLoc && <span>{displayLoc}</span>}
                    </p>
                  )}
                  {!isLoggedIn && (
                    <p className="text-sm text-muted-foreground">
                      <Link to="/login" className="underline text-primary">{t("nav.login")}</Link>{" "}{t("dashboard.loginToSaveProfile")}
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-2 max-w-md">
                  <input
                    type="text"
                    placeholder={t("dashboard.fullNamePlaceholder")}
                    value={editForm.full_name}
                    onChange={(e) => setEditForm((p) => ({ ...p, full_name: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder={t("dashboard.organizationPlaceholder")}
                    value={editForm.organization}
                    onChange={(e) => setEditForm((p) => ({ ...p, organization: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                  <input
                    type="text"
                    placeholder={t("dashboard.locationPlaceholder")}
                    value={editForm.location}
                    onChange={(e) => setEditForm((p) => ({ ...p, location: e.target.value }))}
                    className="w-full px-3 py-1.5 border rounded-md text-sm"
                  />
                </div>
              )}
            </div>

            {/* Edit Actions */}
            {isLoggedIn && (
              <div className="shrink-0">
                {!isEditingProfile ? (
                  <Button variant="outline" size="sm" onClick={() => setIsEditingProfile(true)}>
                    {t("dashboard.editProfile")}
                  </Button>
                ) : (
                  <div className="flex gap-2">
                    <Button size="sm" variant="ghost" onClick={() => setIsEditingProfile(false)}>
                      {t("common.cancel")}
                    </Button>
                    <Button size="sm" onClick={handleSaveProfile} disabled={savingProfile}>
                      {savingProfile ? t("common.saving") : t("common.save")}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </Card>

      {/* ===== Dashboard Grid ===== */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Overview */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>{t("dashboard.overview")}</CardTitle>
            <CardDescription>{t("dashboard.overviewDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              value={selectedMuni}
              onChange={(e) => setSelectedMuni(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="">{t("dashboard.selectMunicipality")}</option>
              {municipalities.map((m) => (
                <option key={m.municipality_id} value={m.municipality_id}>
                  {m.name}
                </option>
              ))}
            </select>

            {selectedMuni && (
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>{t("dashboard.compositeScore")}</span>
                  <span className="font-bold">{compositeScore}/100</span>
                </div>
                <Progress value={compositeScore} className="h-3" />
                <p className="text-xs text-muted-foreground">
                  {t("dashboard.compositeDescription")}
                </p>
              </div>
            )}

            {!selectedMuni && (
              <p className="text-sm text-muted-foreground text-center py-4">
                {t("dashboard.selectPrompt")}
              </p>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.quickActions")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Link to="/ecosim" className="block">
              <Button className="w-full">{t("dashboard.runEcosim")}</Button>
            </Link>
            <Link to="/chat" className="block">
              <Button variant="outline" className="w-full">{t("dashboard.askLumiAi")}</Button>
            </Link>
            <Link to="/energyhub" className="block">
              <Button variant="outline" className="w-full">{t("dashboard.viewEnergyHub")}</Button>
            </Link>
            <Link to="/mfa" className="block">
              <Button variant="outline" className="w-full">{t("dashboard.mfaLink")}</Button>
            </Link>
          </CardContent>
        </Card>

        {/* Saved Locations */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.savedLocations")}</CardTitle>
            <CardDescription>{t("dashboard.savedLocationsDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            {!isLoggedIn ? (
              <p className="text-sm text-muted-foreground">
                <Link to="/login" className="underline text-primary">{t("nav.login")}</Link>{" "}{t("dashboard.loginToSaveLocations")}
              </p>
            ) : savedLocations.length === 0 ? (
              <p className="text-sm text-muted-foreground">{t("dashboard.noSavedLocations")}</p>
            ) : (
              <ul className="space-y-2">
                {savedLocations.map((loc) => (
                  <li key={loc.id} className="flex items-center justify-between text-sm">
                    <span>{loc.label || loc.municipalities?.name || t("dashboard.municipality")}</span>
                    <Link to={`/ecosim?municipality=${loc.municipality_id}`}>
                      <Button variant="ghost" size="sm">{t("common.open")}</Button>
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {/* Saved Simulations CTA */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.savedSims")}</CardTitle>
            <CardDescription>{t("dashboard.savedSimsDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            {!isLoggedIn ? (
              <p className="text-sm text-muted-foreground">
                <Link to="/login" className="underline text-primary">{t("nav.login")}</Link>{" "}{t("dashboard.loginToSaveSims")}
              </p>
            ) : (
              <Link to="/saved-simulations">
                <Button variant="outline" className="w-full">
                  {t("dashboard.viewAllSavedSims")}
                </Button>
              </Link>
            )}
          </CardContent>
        </Card>

        {/* AI Center */}
        <Card>
          <CardHeader>
            <CardTitle>{t("dashboard.aiCenter")}</CardTitle>
            <CardDescription>{t("dashboard.aiCenterDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <p className="text-sm text-muted-foreground">
              {t("dashboard.askAi")}
            </p>
            <div className="flex gap-2 flex-wrap">
              <Link to="/chat">
                <Button size="sm" variant="secondary">
                  {t("dashboard.exampleQuery1")}
                </Button>
              </Link>
              <Link to="/chat">
                <Button size="sm" variant="secondary">
                  {t("dashboard.exampleQuery2")}
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Forecasting & Coverage */}
      <div className="grid gap-4 md:grid-cols-2 mt-4">
        <ForecastPanel />
        <CoverageDashboard />
      </div>
    </section>
  );
}
```

**Explanation:** This React component renders UI for the `Dashboard` view or widget.

## `react-frontend/src/pages/Ecosim.jsx`

### `formatNumber`

- **File:** `react-frontend/src/pages/Ecosim.jsx`
- **Lines:** `28-29`
- **Purpose:** Converts Number.

**Code:**
```jsx
const formatNumber = (value, digits = 0) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: digits }).format(value ?? 0)
```

**Explanation:** This function converts Number. See the code for the full implementation.

### `formatCurrency`

- **File:** `react-frontend/src/pages/Ecosim.jsx`
- **Lines:** `31-36`
- **Purpose:** Converts Currency.

**Code:**
```jsx
const formatCurrency = (value) =>
  new Intl.NumberFormat("en-PH", {
    style: "currency",
    currency: "PHP",
    maximumFractionDigits: 0
  }).format(value ?? 0)
```

**Explanation:** This function converts Currency. See the code for the full implementation.

### `Ecosim`

- **File:** `react-frontend/src/pages/Ecosim.jsx`
- **Lines:** `38-397`
- **Purpose:** Renders the `Ecosim` component.

**Code:**
```jsx
export default function Ecosim() {
  const { t } = useI18n();
  const { user, accessToken } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();

  const [mode, setMode] = useState("municipality");
  const [municipalityId, setMunicipalityId] = useState("");
  const [municipalities, setMunicipalities] = useState([]);
  const [municipalitiesError, setMunicipalitiesError] = useState(null);
  const [muniQuery, setMuniQuery] = useState("");
  const [muniOpen, setMuniOpen] = useState(false);
  const [provinceId, setProvinceId] = useState("");
  const [provinces, setProvinces] = useState([]);
  const [provincesError, setProvincesError] = useState(null);
  const [provinceQuery, setProvinceQuery] = useState("");
  const [provinceOpen, setProvinceOpen] = useState(false);
  const [monthlyConsumption, setMonthlyConsumption] = useState(350);
  const [monthlyBill, setMonthlyBill] = useState(5000);
  const [desiredSavings, setDesiredSavings] = useState(50);
  const [includeAi, setIncludeAi] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [productRecs, setProductRecs] = useState(null);
  const [productLoading, setProductLoading] = useState(false);

  // Save simulation dialog state
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [saveLabel, setSaveLabel] = useState("");
  const [saving, setSaving] = useState(false);

  const filteredMunicipalities = useMemo(() => {
    const q = muniQuery.trim().toLowerCase();
    if (!q) return municipalities;
    return municipalities.filter((m) => m.name.toLowerCase().includes(q));
  }, [municipalities, muniQuery]);

  const filteredProvinces = useMemo(() => {
    const q = provinceQuery.trim().toLowerCase();
    if (!q) return provinces;
    return provinces.filter((p) => p.name.toLowerCase().includes(q));
  }, [provinces, provinceQuery]);

  const comparisonMax = useMemo(() => {
    if (!result?.options?.length) return 0;
    return Math.max(...result.options.map((item) => item.estimated_generation_kwh || 0), 1);
  }, [result]);

  useEffect(() => {
    let isActive = true;

    const loadMunicipalities = async () => {
      try {
        const data = await getMunicipalities();
        if (!isActive) return;
        const items = data?.items || [];
        setMunicipalities(items);
        if (items.length) {
          setMunicipalityId(String(items[0].municipality_id));
          setMuniQuery(items[0].name);
        }
      } catch (err) {
        if (!isActive) return;
        setMunicipalitiesError(err?.message || t("ecosim.toasts.municipalitiesError"));
      }
    };

    loadMunicipalities();
    return () => {
      isActive = false;
    };
  }, []);

  // Load saved simulation from query param ?simulation_id={id}
  useEffect(() => {
    const simId = searchParams.get("simulation_id");
    if (!simId || !user?.id) return;

    let isActive = true;
    const loadSaved = async () => {
      try {
        const { data: sim, error } = await supabase
          .from("saved_simulations")
          .select("*")
          .eq("id", simId)
          .eq("user_id", user.id)
          .single();

        if (error || !sim) throw new Error(error?.message || t("ecosim.toasts.loadFailed"));
        if (!isActive) return;

        // Pre-populate inputs
        const inputs = sim.inputs || {};
        if (inputs.monthly_consumption_kwh) {
          setMonthlyConsumption(inputs.monthly_consumption_kwh);
        }
        if (inputs.monthly_bill_php) {
          setMonthlyBill(inputs.monthly_bill_php);
        }
        if (inputs.desired_savings_pct !== undefined) {
          setDesiredSavings(inputs.desired_savings_pct);
        }
        if (inputs.include_ai !== undefined) {
          setIncludeAi(inputs.include_ai);
        }
        if (sim.municipality_id) {
          setMunicipalityId(String(sim.municipality_id));
          const found = municipalities.find(
            (m) => String(m.municipality_id) === String(sim.municipality_id)
          );
          if (found) setMuniQuery(found.name);
        }
        // Pre-populate results
        if (sim.results) {
          setResult(sim.results);
        }
        toast.success(t("ecosim.toasts.loadSuccess"));
      } catch (err) {
        toast.error(err?.message || t("ecosim.toasts.loadFailed"));
      }
    };

    loadSaved();
    return () => {
      isActive = false;
    };
  }, [searchParams, user, municipalities]);

  useEffect(() => {
    let isActive = true;

    const loadProvinces = async () => {
      try {
        const data = await getProvinces();
        if (!isActive) return;
        const items = data?.items || [];
        setProvinces(items);
        if (items.length && !provinceId) {
          setProvinceId(String(items[0].province_id));
          setProvinceQuery(items[0].name);
        }
      } catch (err) {
        if (!isActive) return;
        setProvincesError(err?.message || t("ecosim.toasts.provincesError"));
      }
    };

    loadProvinces();
    return () => {
      isActive = false;
    };
  }, []);

  const activeId = mode === "province" ? provinceId : municipalityId;

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const data = await getEcosim({
        municipalityId: String(activeId).trim(),
        monthlyConsumption: Number(monthlyConsumption),
        monthlyBill: Number(monthlyBill),
        desiredSavings: Number(desiredSavings) / 100,
        includeAi,
        mode,
      });
      setResult(data);
      // Fetch product recommendations for the recommended source
      const source = data?.recommended_source?.toLowerCase();
      if (source && source !== "geothermal") {
        setProductLoading(true);
        try {
          const recs = await getProductRecommendations(source, null, 4);
          setProductRecs(recs);
        } catch {
          setProductRecs(null);
        } finally {
          setProductLoading(false);
        }
      } else {
        setProductRecs(null);
      }
    } catch (err) {
      setError(err?.message || t("ecosim.toasts.ecosimError"));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveSimulation = async () => {
    if (!user || !accessToken) {
      toast.error(t("ecosim.toasts.loginRequired"));
      return;
    }
    if (!result || !municipalityId) {
      toast.error(t("ecosim.toasts.runFirst"));
      return;
    }

    const defaultLabel = `${result.municipality || t("ecosim.defaults.simulation")} — ${result.recommended_source || t("ecosim.defaults.renewable")}`;
    const label = saveLabel.trim() || defaultLabel;

    setSaving(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/simulations`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            label,
            municipality_id: Number(municipalityId),
            inputs: {
              monthly_consumption_kwh: Number(monthlyConsumption),
              monthly_bill_php: Number(monthlyBill),
              desired_savings_pct: Number(desiredSavings),
              include_ai: includeAi,
            },
            results: result,
          }),
        }
      );

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        if (res.status === 403 && errData.detail?.upgrade) {
          toast.error(t("ecosim.toasts.saveLimit", { limit: errData.detail.limit }));
        } else {
          toast.error(errData.detail?.message || t("ecosim.toasts.saveFailed"));
        }
        return;
      }

      toast.success(t("ecosim.toasts.saveSuccess"));
      setSaveDialogOpen(false);
      setSaveLabel("");
    } catch (err) {
      toast.error(err?.message || t("ecosim.toasts.saveFailed"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <section className="page-container stack">
      <div className="space-y-2">
        <h1>{t("ecosim.title")}</h1>
        <p className="text-muted-foreground">
          {t("ecosim.subtitle")}
        </p>
      </div>

      <EcosimWizard
        mode={mode}
        setMode={setMode}
        muniQuery={muniQuery}
        setMuniQuery={setMuniQuery}
        muniOpen={muniOpen}
        setMuniOpen={setMuniOpen}
        filteredMunicipalities={filteredMunicipalities}
        municipalityId={municipalityId}
        setMunicipalityId={setMunicipalityId}
        municipalitiesError={municipalitiesError}
        provinceQuery={provinceQuery}
        setProvinceQuery={setProvinceQuery}
        provinceOpen={provinceOpen}
        setProvinceOpen={setProvinceOpen}
        filteredProvinces={filteredProvinces}
        provinceId={provinceId}
        setProvinceId={setProvinceId}
        provincesError={provincesError}
        monthlyConsumption={monthlyConsumption}
        setMonthlyConsumption={setMonthlyConsumption}
        monthlyBill={monthlyBill}
        setMonthlyBill={setMonthlyBill}
        desiredSavings={desiredSavings}
        setDesiredSavings={setDesiredSavings}
        includeAi={includeAi}
        setIncludeAi={setIncludeAi}
        onRun={handleSubmit}
        loading={loading}
        activeId={activeId}
        result={result}
        user={user}
        onSave={() => {
          const defaultLabel = `${result.municipality || t("ecosim.defaults.simulation")} — ${result.recommended_source || t("ecosim.defaults.renewable")}`;
          setSaveLabel(defaultLabel);
          setSaveDialogOpen(true);
        }}
      />

      {error && (
        <Card className="border-destructive text-destructive">
          <CardHeader>
            <CardTitle>{t("ecosim.errorCardTitle")}</CardTitle>
            <CardDescription>{error}</CardDescription>
          </CardHeader>
        </Card>
      )}

      {loading && <LoadingSkeleton />}

      {result && !loading && (
        <EcosimResults
          result={result}
          productRecs={productRecs}
          productLoading={productLoading}
        />
      )}

      {result?.options && !loading && (
        <div className="mt-4">
          <LcoePanel options={result.options} />
        </div>
      )}

      {/* Save Simulation Dialog */}
      <Dialog open={saveDialogOpen} onOpenChange={setSaveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{t("ecosim.saveDialog.title")}</DialogTitle>
            <DialogDescription>
              {t("ecosim.saveDialog.description")}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <label className="text-sm font-medium">{t("ecosim.saveDialog.label")}</label>
            <Input
              value={saveLabel}
              onChange={(e) => setSaveLabel(e.target.value)}
              placeholder={t("ecosim.saveDialog.placeholder")}
              className="mt-2"
              autoFocus
            />
          </div>
          <DialogFooter>
            <DialogClose asChild>
              <Button type="button" variant="outline">
                {t("ecosim.saveDialog.cancel")}
              </Button>
            </DialogClose>
            <Button
              type="button"
              onClick={handleSaveSimulation}
              disabled={saving}
            >
              {saving ? t("ecosim.saveDialog.saving") : t("ecosim.saveDialog.save")}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </section>
  );
}
```

**Explanation:** This React component renders UI for the `Ecosim` view or widget.

## `react-frontend/src/pages/EnergyHub.jsx`

### `EnergyHub`

- **File:** `react-frontend/src/pages/EnergyHub.jsx`
- **Lines:** `31-324`
- **Purpose:** Renders the `EnergyHub` component.

**Code:**
```jsx
export default function EnergyHub() {
  const { t } = useI18n();
  const [overview, setOverview] = useState(null);
  const [trends, setTrends] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [sourceBreakdown, setSourceBreakdown] = useState(null);
  const [insight, setInsight] = useState(null);
  const [mapMetric, setMapMetric] = useState("renewable_potential");
  const [mapLevel, setMapLevel] = useState("province");
  const [loading, setLoading] = useState(true);
  const [useLlm, setUseLlm] = useState(true);
  const [llmLoading, setLlmLoading] = useState({});
  const [chartAnalyses, setChartAnalyses] = useState({});
  const [mapLoading, setMapLoading] = useState(false);
  const [geothermalPlants, setGeothermalPlants] = useState([]);
  const [irena, setIrena] = useState(null);

  // Cache for map data: { [metric]: { [level]: response } }
  const mapCacheRef = useRef({});

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------
  const getCachedMapData = (metric, level) => {
    return mapCacheRef.current[metric]?.[level] ?? null;
  };

  const setCachedMapData = (metric, level, data) => {
    if (!mapCacheRef.current[metric]) mapCacheRef.current[metric] = {};
    mapCacheRef.current[metric][level] = data;
  };

  const fetchAndCacheMapData = async (metric, level) => {
    const cached = getCachedMapData(metric, level);
    if (cached) return cached;
    const data = await getEnergyHubMapData(metric, level);
    setCachedMapData(metric, level, data);
    return data;
  };

  // ---------------------------------------------------------------------------
  // Initial load — overview + trends + province map + pre-fetch all metrics
  // ---------------------------------------------------------------------------
  useEffect(() => {
    let cancelled = false;

    async function loadAll() {
      setLoading(true);
      setLlmLoading((prev) => ({ ...prev, overview: true }));
      try {
        const [ov, tr, mp, src, ir] = await Promise.all([
          getEnergyHubOverview(),
          getEnergyHubTrends(),
          fetchAndCacheMapData("renewable_potential", "province"),
          getEnergyHubSourceBreakdown(),
          getIrenaOverview().catch(() => null),
        ]);
        if (!cancelled) {
          setOverview(ov);
          setTrends(tr);
          setMapData(mp);
          setSourceBreakdown(src);
          setIrena(ir);
        }
      } catch (err) {
        if (!cancelled) {
          toast.error(t("energyHub.toast.loadError"), { description: err.message });
        }
      } finally {
        if (!cancelled) setLoading(false);
      }

      // Pre-fetch all suitability metrics in background (province level)
      Promise.all(
        SUITABILITY_METRICS.filter((m) => m !== "renewable_potential").map((m) =>
          fetchAndCacheMapData(m, "province").catch(() => null)
        )
      );

      // Fetch geothermal plant list for map markers
      try {
        const plants = await getGeothermalPlants();
        if (!cancelled) setGeothermalPlants(plants || []);
      } catch {
        // Non-critical; markers simply won't appear
      }

      // Load LLM insight in background
      try {
        const ai = await getEnergyHubAiInsight(true);
        if (!cancelled) setInsight(ai);
      } catch (err) {
        if (!cancelled) {
          toast.error(t("energyHub.toast.llmError"), { description: err.message });
          try {
            const staticAi = await getEnergyHubAiInsight(false);
            if (!cancelled) setInsight(staticAi);
          } catch {}
        }
      } finally {
        if (!cancelled) setLlmLoading((prev) => ({ ...prev, overview: false }));
      }
    }

    loadAll();
    return () => {
      cancelled = true;
    };
  }, []);

  // ---------------------------------------------------------------------------
  // Switch metric or level — use cache if available, else fetch + cache
  // ---------------------------------------------------------------------------
  useEffect(() => {
    let cancelled = false;
    const cached = getCachedMapData(mapMetric, mapLevel);
    if (cached) {
      setMapData(cached);
      return;
    }
    setMapLoading(true);
    fetchAndCacheMapData(mapMetric, mapLevel)
      .then((mp) => {
        if (!cancelled) setMapData(mp);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setMapLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [mapMetric, mapLevel]);

  const handleToggleLlm = async () => {
    const next = !useLlm;
    setUseLlm(next);
    if (next && !insight?.insight?.includes("LLM")) {
      setLlmLoading((prev) => ({ ...prev, overview: true }));
      try {
        const ai = await getEnergyHubAiInsight(true);
        setInsight(ai);
      } catch (err) {
        toast.error("LLM insight failed", { description: err.message });
      } finally {
        setLlmLoading((prev) => ({ ...prev, overview: false }));
      }
    }
  };

  const handleAnalyzeChart = async (chartType, forceRefresh = false) => {
    if (chartAnalyses[chartType] && !forceRefresh) return;
    setLlmLoading((prev) => ({ ...prev, [chartType]: true }));
    try {
      let chartData = {};
      if (chartType === "trends" && trends) {
        chartData = {
          years: trends.years,
          consumption: trends.series?.total_consumption_gwh || [],
          forecast: trends.forecast?.forecast_values || [],
        };
      } else if (chartType === "consumption_trend" && trends) {
        chartData = {
          years: trends.years,
          consumption: trends.series?.total_consumption_gwh || [],
          forecast_years: trends.forecast?.forecast_years || [],
          forecast_values: trends.forecast?.forecast_values || [],
        };
      } else if (chartType === "peak_demand" && trends) {
        chartData = {
          years: trends.years,
          peak_demand: trends.series?.total_peak_demand_mw || [],
        };
      } else if (chartType === "renewable_generation" && trends) {
        chartData = {
          years: trends.years,
          renewable_generation: trends.series?.renewable_generation_gwh || [],
          total_generation: trends.series?.total_generation_gwh || [],
        };
      } else if (chartType === "sources" && sourceBreakdown) {
        chartData = { shares: sourceBreakdown.share_pct || {} };
      } else if (chartType === "map") {
        chartData = { metric: mapMetric };
      }
      const result = await analyzeChart(chartType, chartData, forceRefresh);
      setChartAnalyses((prev) => ({ ...prev, [chartType]: result }));
    } catch (err) {
      toast.error(t("energyHub.toast.analyzeError", { chartType }), { description: err.message });
    } finally {
      setLlmLoading((prev) => ({ ...prev, [chartType]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-background pb-12">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold tracking-tight">{t("energyHub.title")}</h1>
          <p className="mt-2 max-w-2xl text-muted-foreground">
            {t("energyHub.description")}
          </p>
          <p className="mt-1 text-xs text-muted-foreground">
            {t("energyHub.disclaimer")}
          </p>
        </div>
      </div>

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8 space-y-8">
        {/* Section 1: Overview Cards */}
        <section>
          <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
            {t("energyHub.sections.nationalOverview")}
          </h2>
          <EnergyOverview data={overview} />
        </section>

        {/* Section 2: Provincial Demand */}
        <section>
          <ProvincialDemand />
        </section>

        {/* Section 2b: IRENA Benchmark */}
        {irena && irena.capacity?.length > 0 && (
          <section className="rounded-xl border bg-card p-6 shadow-sm">
            <h2 className="text-lg font-semibold">{t("energyHub.sections.irena.title")}</h2>
            <p className="text-sm text-muted-foreground">{t("energyHub.sections.irena.description")}</p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="text-xs text-muted-foreground">{t("energyHub.sections.irena.latestReCapacity")}</p>
                <p className="text-lg font-semibold">
                  {irena.capacity.filter(c => c.technology === "Total renewable energy" && c.grid_connection === "On-grid").pop()?.capacity_mw?.toLocaleString?.() ?? "—"} {t("energyHub.sections.irena.unitMW")}
                </p>
              </div>
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="text-xs text-muted-foreground">{t("energyHub.sections.irena.latestReGeneration")}</p>
                <p className="text-lg font-semibold">
                  {irena.generation.filter(g => g.technology === "Total renewable" && g.grid_connection === "On-grid").pop()?.generation_gwh?.toLocaleString?.() || "—"} {t("energyHub.sections.irena.unitGWh")}
                </p>
              </div>
              <div className="rounded-lg border bg-muted/30 p-3">
                <p className="text-xs text-muted-foreground">{t("energyHub.sections.irena.reShareLatest")}</p>
                <p className="text-lg font-semibold">
                  {irena.renewable_share?.pop()?.renewable_share_pct ?? "—"}%
                </p>
              </div>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{irena.note}</p>
          </section>
        )}

        {/* Section 3: Choropleth Map */}
        <section>
          <EnergyMap
            mapData={mapData}
            metric={mapMetric}
            level={mapLevel}
            onMetricChange={setMapMetric}
            onLevelChange={setMapLevel}
            mapLoading={mapLoading}
            geothermalPlants={geothermalPlants}
          />
        </section>

        {/* Section 3: Energy Trends */}
        <section>
          <EnergyTrends
            trends={trends}
            chartAnalyses={chartAnalyses}
            llmLoading={llmLoading}
            onAnalyzeChart={handleAnalyzeChart}
          />
        </section>

        {/* Section 4: Energy Source Comparison */}
        <section>
          <EnergySources breakdown={sourceBreakdown} />
        </section>

        {/* Section 5: AI Insight Panel */}
        <section>
          <AiInsightPanel
            insight={insight}
            useLlm={useLlm}
            llmLoading={llmLoading}
            chartAnalyses={chartAnalyses}
            onToggleLlm={handleToggleLlm}
            onAnalyzeChart={handleAnalyzeChart}
          />
        </section>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EnergyHub` view or widget.

## `react-frontend/src/pages/Home.jsx`

### `SectionHeading`

- **File:** `react-frontend/src/pages/Home.jsx`
- **Lines:** `24-42`
- **Purpose:** Renders the `SectionHeading` component.

**Code:**
```jsx
function SectionHeading({ badge, title, subtitle }) {
  return (
    <div className="mx-auto max-w-3xl text-center space-y-4">
      {badge && (
        <Badge variant="secondary" className="text-xs font-medium tracking-wide uppercase">
          {badge}
        </Badge>
      )}
      <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
        {title}
      </h2>
      {subtitle && (
        <p className="text-lg text-muted-foreground leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `SectionHeading` view or widget.

### `FeatureCard`

- **File:** `react-frontend/src/pages/Home.jsx`
- **Lines:** `44-76`
- **Purpose:** Renders the `FeatureCard` component.

**Code:**
```jsx
function FeatureCard({ icon: Icon, title, description, tags, badge }) {
  return (
    <Card className="group relative overflow-hidden border-border/60 bg-card/80 backdrop-blur-sm transition-all hover:border-primary/40 hover:shadow-lg">
      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-primary via-accent to-brand-success opacity-0 transition-opacity group-hover:opacity-100" />
      <CardHeader className="space-y-3">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/20">
          <Icon className="h-6 w-6" />
        </div>
        {badge && (
          <Badge variant="outline" className="w-fit text-[10px] uppercase tracking-wide">
            {badge}
          </Badge>
        )}
        <CardTitle className="text-xl">{title}</CardTitle>
        <CardDescription className="text-sm leading-relaxed">
          {description}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="inline-flex items-center rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground"
            >
              {tag}
            </span>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
```

**Explanation:** This React component renders UI for the `FeatureCard` view or widget.

### `StepCard`

- **File:** `react-frontend/src/pages/Home.jsx`
- **Lines:** `78-96`
- **Purpose:** Renders the `StepCard` component.

**Code:**
```jsx
function StepCard({ number, icon: Icon, title, description }) {
  const { t } = useI18n();
  return (
    <div className="relative flex flex-col items-center text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl border-2 border-primary-foreground/40 bg-primary-foreground/15 text-primary-foreground shadow-lg">
        <Icon className="h-7 w-7" />
      </div>
      <div className="mt-5 space-y-2">
        <div className="text-xs font-bold uppercase tracking-wider text-primary-foreground/70">
          {t("home.howItWorks.step")} {number}
        </div>
        <h3 className="text-lg font-semibold text-primary-foreground">{title}</h3>
        <p className="text-sm leading-relaxed text-primary-foreground/85 max-w-xs">
          {description}
        </p>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `StepCard` view or widget.

### `EnergyTypeCard`

- **File:** `react-frontend/src/pages/Home.jsx`
- **Lines:** `98-123`
- **Purpose:** Renders the `EnergyTypeCard` component.

**Code:**
```jsx
function EnergyTypeCard({ icon: Icon, title, header, description, citationIds, colorClass }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-border/60 bg-card p-6 transition-all hover:shadow-lg hover:border-primary/30">
      <div className={`absolute -right-4 -top-4 h-24 w-24 rounded-full opacity-10 ${colorClass}`} />
      <div className="space-y-4">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary">
          <Icon className="h-6 w-6" />
        </div>
        <h3 className="text-xl font-semibold text-foreground">{title}</h3>
        {header && (
          <p className="text-xs font-medium uppercase tracking-wider text-primary/80">
            {header}
          </p>
        )}
        <p className="text-sm leading-relaxed text-muted-foreground">
          {description}
        </p>
        {citationIds?.length > 0 && (
          <div className="pt-2">
            <CitationSources ids={citationIds} mode="inline" />
          </div>
        )}
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `EnergyTypeCard` view or widget.

### `Home`

- **File:** `react-frontend/src/pages/Home.jsx`
- **Lines:** `125-372`
- **Purpose:** Renders the `Home` component.

**Code:**
```jsx
export default function Home() {
  const { t } = useI18n();

  return (
    <div className="flex flex-col">
      {/* HERO */}
      <section className="relative overflow-hidden">
        {/* Decorative background elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-muted/50" />
        <div className="absolute -top-24 -right-24 h-96 w-96 rounded-full bg-accent/20 blur-3xl" />
        <div className="absolute -bottom-24 -left-24 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />

      <div className="relative page-container py-20 sm:py-28">
        <div className="mx-auto max-w-4xl text-center space-y-8">
          <div className="flex justify-center">
            <img
              src="/lumi-logo.png"
              alt="LUMI Logo"
              className="h-20 w-auto object-contain drop-shadow-sm sm:h-24"
            />
          </div>

          <div className="space-y-4">
            <Badge
              variant="outline"
              className="border-primary/30 bg-primary/5 text-primary px-3 py-1 text-sm"
            >
              {t("home.hero.badge")}
            </Badge>
            <h1 className="text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl md:text-6xl">
              {t("home.hero.title")}{" "}
              <span className="bg-gradient-to-r from-primary to-brand-success bg-clip-text text-transparent">
                {t("home.hero.titleHighlight")}
              </span>
            </h1>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground leading-relaxed sm:text-xl">
              {t("home.hero.subtitle")}
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link to="/energyhub">
              <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                <BarChart3 className="h-5 w-5" />
                {t("home.hero.tryEnergyHub")}
              </Button>
            </Link>
            <Link to="/about">
              <Button size="lg" variant="outline" className="gap-2 text-base">
                {t("home.hero.learnMore")}
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-2 gap-4 pt-8 sm:grid-cols-4">
            {[
              { label: t("home.stats.regionsCovered.label"), value: t("home.stats.regionsCovered.value"), sub: t("home.stats.regionsCovered.sub") },
              { label: t("home.stats.energySources.label"), value: t("home.stats.energySources.value"), sub: t("home.stats.energySources.sub") },
              { label: t("home.stats.dataPoints.label"), value: t("home.stats.dataPoints.value"), sub: t("home.stats.dataPoints.sub") },
              { label: t("home.stats.aiInsights.label"), value: t("home.stats.aiInsights.value"), sub: t("home.stats.aiInsights.sub") }
            ].map((stat) => (
              <div
                key={stat.label}
                className="rounded-xl border border-border/50 bg-card/60 p-4 backdrop-blur-sm"
              >
                <div className="text-2xl font-bold text-primary sm:text-3xl">{stat.value}</div>
                <div className="text-sm font-medium text-foreground">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.sub}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>

      {/* FEATURES */}
      <section className="relative border-t border-border/40 bg-gradient-to-b from-muted/30 to-background">
        <div className="page-container py-20 sm:py-24 space-y-16">
          <SectionHeading
            badge={t("home.features.badge")}
            title={t("home.features.title")}
            subtitle={t("home.features.subtitle")}
          />

          <div className="grid gap-6 md:grid-cols-3">
            <FeatureCard
              icon={BarChart3}
              title={t("home.features.energyHub.title")}
              description={t("home.features.energyHub.description")}
              tags={t("home.features.energyHub.tags")}
            />
            <FeatureCard
              icon={Zap}
              title={t("home.features.ecosim.title")}
              description={t("home.features.ecosim.description")}
              tags={t("home.features.ecosim.tags")}
            />
            <FeatureCard
              icon={BrainCircuit}
              title={t("home.features.ai.title")}
              description={t("home.features.ai.description")}
              tags={t("home.features.ai.tags")}
              badge={t("home.features.ai.badge")}
            />
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="relative overflow-hidden bg-primary text-primary-foreground">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYtMi42ODYgNi02cy0yLjY4Ni02LTYtNi02IDIuNjg2LTYgNiAyLjY4NiA2IDYgNnptMCAzMGMzLjMxNCAwIDYtMi42ODYgNi02cy0yLjY4Ni02LTYtNi02IDIuNjg2LTYgNiAyLjY4NiA2IDYgNnptLTE4LTE1YzMuMzE0IDAgNi0yLjY4NiA2LTZzLTIuNjg2LTYtNi02LTYgMi42ODYtNiA2IDIuNjg2IDYgNiA2eiIgZmlsbD0iI2ZmZiIgZmlsbC1vcGFjaXR5PSIwLjAzIi8+PC9nPjwvc3ZnPg==')] opacity-30" />
        <div className="page-container py-20 sm:py-24 space-y-16">
          <div className="mx-auto max-w-3xl text-center space-y-4">
            <Badge className="bg-primary-foreground/10 text-primary-foreground border-primary-foreground/20 uppercase tracking-wide">
              {t("home.howItWorks.badge")}
            </Badge>
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              {t("home.howItWorks.title")}
            </h2>
            <p className="text-lg text-primary-foreground/80 leading-relaxed">
              {t("home.howItWorks.subtitle")}
            </p>
          </div>

          <div className="relative grid gap-12 md:grid-cols-4">
            {/* Connector line for desktop */}
            <div className="hidden md:block absolute top-8 left-[12.5%] right-[12.5%] h-0.5 bg-primary-foreground/40" />

            {t("home.howItWorks.steps").map((step, index) => {
              const icons = [Database, LineChart, BrainCircuit, Lightbulb];
              const Icon = icons[index];
              return (
                <StepCard
                  key={step.title}
                  number={index + 1}
                  icon={Icon}
                  title={step.title}
                  description={step.description}
                />
              );
            })}
          </div>
        </div>
      </section>

      {/* RENEWABLE ENERGY */}
      <section className="page-container py-20 sm:py-24 space-y-16">
        <SectionHeading
          badge={t("home.renewable.badge")}
          title={t("home.renewable.title")}
          subtitle={t("home.renewable.subtitle")}
        />

        <div className="grid gap-6 sm:grid-cols-3">
          {[
            { icon: Sun, key: "solar", colorClass: "bg-accent" },
            { icon: Wind, key: "wind", colorClass: "bg-brand-success" },
            { icon: Droplets, key: "hydro", colorClass: "bg-primary" }
          ].map(({ icon: Icon, key, colorClass }) => (
            <EnergyTypeCard
              key={key}
              icon={Icon}
              title={t(`home.renewable.${key}.title`)}
              header={t(`home.renewable.${key}.header`)}
              description={t(`home.renewable.${key}.description`)}
              citationIds={t(`home.renewable.${key}.citations`)}
              colorClass={colorClass}
            />
          ))}
        </div>

        {/* Insight banner */}
        <div className="rounded-2xl border border-border/60 bg-gradient-to-r from-card to-muted/30 p-6 sm:p-8">
          <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div className="space-y-3">
              <h3 className="text-lg font-semibold text-foreground">
                {t("home.renewable.insight.title")}
              </h3>
              <p className="text-sm text-muted-foreground max-w-xl">
                {t("home.renewable.insight.description")}
              </p>
              <CitationSources
                ids={t("home.renewable.insight.citations")}
                mode="inline"
                inlineLabel={t("home.renewable.insight.readResearch")}
              />
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="relative overflow-hidden border-t border-border/40">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-background to-accent/5" />
        <div className="relative page-container py-20 sm:py-24">
          <div className="mx-auto max-w-3xl rounded-3xl border border-border/60 bg-card/80 p-8 text-center shadow-xl backdrop-blur-sm sm:p-12">
            <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-lg mb-6">
              <TrendingUp className="h-8 w-8" />
            </div>
            <h2 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
              {t("home.cta.title")}
            </h2>
            <p className="mx-auto mt-4 max-w-xl text-lg text-muted-foreground leading-relaxed">
              {t("home.cta.subtitle")}
            </p>
            <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
              <Link to="/ecosim">
                <Button size="lg" className="gap-2 text-base shadow-lg shadow-primary/20">
                  <Zap className="h-5 w-5" />
                  {t("home.cta.tryEcosim")}
                </Button>
              </Link>
              <Link to="/energyhub">
                <Button size="lg" variant="outline" className="gap-2 text-base">
                  <BarChart3 className="h-5 w-5" />
                  {t("home.cta.tryEnergyHub")}
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* REFERENCES */}
      <section className="border-t border-border/40 bg-muted/20">
        <div className="page-container py-12">
          <div className="mx-auto max-w-4xl space-y-6">
            <div className="space-y-2">
              <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">
                {t("home.references.title")}
              </h3>
              <p className="text-sm text-muted-foreground max-w-2xl">
                {t("home.references.intro")}
              </p>
            </div>
            <CitationSources
              ids={[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]}
              mode="dialog"
              dialogLabel={t("home.references.viewSources")}
            />
          </div>
        </div>
      </section>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `Home` view or widget.

## `react-frontend/src/pages/Login.jsx`

### `Login`

- **File:** `react-frontend/src/pages/Login.jsx`
- **Lines:** `12-303`
- **Purpose:** Renders the `Login` component.

**Code:**
```jsx
export default function Login() {
  const { t } = useI18n();
  const { session, signInWithProvider, signInWithPassword, signUp, resetPassword } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const redirectTo = location.state?.from?.pathname || "/dashboard";
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [signupStatus, setSignupStatus] = useState(null); // 'confirm' | 'auto' | null

  // MFA state
  const [mfaRequired, setMfaRequired] = useState(null); // null = checking, false = no mfa, true = mfa needed
  const [mfaFactorId, setMfaFactorId] = useState(null);
  const [mfaCode, setMfaCode] = useState("");
  const [verifying, setVerifying] = useState(false);

  const checkMfa = async () => {
    try {
      // Supabase MFA may not be available in all projects; fail open (treat as no MFA)
      if (!supabase.auth.mfa || typeof supabase.auth.mfa.getAuthenticatorAssuranceLevel !== "function") {
        setMfaRequired(false);
        return;
      }

      const { data: aal, error: aalError } = await supabase.auth.mfa.getAuthenticatorAssuranceLevel();
      if (aalError) throw aalError;

      if (aal?.nextLevel === "aal2" && aal?.currentLevel === "aal1") {
        const { data: factors, error: fError } = await supabase.auth.mfa.listFactors();
        if (fError) throw fError;

        const factor =
          factors?.totp?.find((f) => f.status === "verified") ||
          factors?.all?.find((f) => f.status === "verified");

        if (factor) {
          setMfaFactorId(factor.id);
          setMfaRequired(true);
          return;
        }
      }
    } catch (error) {
      // MFA check failed (e.g., not enabled or network) — do not block the user
      console.error("[Login] MFA check failed:", error);
    }
    setMfaRequired(false);
  };

  useEffect(() => {
    if (session) {
      checkMfa();
    } else {
      setMfaRequired(null);
    }
  }, [session]);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setSignupStatus(null);

    try {
      if (mode === "signup" && password !== confirmPassword) {
        toast.error(t("mfa.passwordsDoNotMatch"));
        return;
      }

      if (mode === "login") {
        const { error } = await signInWithPassword(email, password);
        if (error) throw error;
        // Session will trigger useEffect, which calls checkMfa.
      }

      if (mode === "signup") {
        const result = await signUp(email, password);
        if (result.error) throw result.error;

        if (result.confirmationRequired) {
          setSignupStatus("confirm");
          toast.success(t("login.accountCreated"));
        } else {
          setSignupStatus("auto");
          toast.success(t("login.accountCreated"));
        }
      }

      if (mode === "reset") {
        const { error } = await resetPassword(email);
        if (error) throw error;
        toast.success(t("mfa.resetSent"));
      }
    } catch (error) {
      toast.error(error?.message || t("login.error"));
    } finally {
      setBusy(false);
    }
  };

  const handleVerifyMfa = async (event) => {
    event.preventDefault();
    if (!mfaFactorId || !mfaCode) return;

    setVerifying(true);
    try {
      const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
        factorId: mfaFactorId,
      });
      if (challengeError) throw challengeError;

      const { error } = await supabase.auth.mfa.verify({
        factorId: mfaFactorId,
        challengeId: challenge.id,
        code: mfaCode.replace(/\s/g, ""),
      });
      if (error) throw error;

      toast.success(t("mfa.verified"));
      navigate(redirectTo, { replace: true });
    } catch (error) {
      toast.error(error?.message || t("mfa.verifyError"));
    } finally {
      setVerifying(false);
    }
  };

  const resendConfirmation = async () => {
    setBusy(true);
    try {
      const { error } = await supabase.auth.resend({
        type: "signup",
        email,
      });
      if (error) throw error;
      toast.success(t("mfa.confirmResent"));
    } catch (error) {
      toast.error(error?.message || t("mfa.resendError"));
    } finally {
      setBusy(false);
    }
  };

  // Fully authenticated with no pending MFA
  if (session && mfaRequired === false) {
    return <Navigate to={redirectTo} replace />;
  }

  // Authenticated but waiting for MFA verification
  if (session && mfaRequired === true) {
    return (
      <section className="page-container">
        <Card className="mx-auto max-w-md">
          <CardHeader>
            <CardTitle>{t("mfa.verifyTitle")}</CardTitle>
            <CardDescription>{t("mfa.verifyDescription")}</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleVerifyMfa} className="space-y-3">
              <Input
                value={mfaCode}
                onChange={(event) => setMfaCode(event.target.value)}
                placeholder={t("mfa.codePlaceholder")}
                maxLength={10}
                autoComplete="one-time-code"
                inputMode="numeric"
              />
              <Button className="w-full" type="submit" disabled={verifying || !mfaCode}>
                {verifying ? t("common.loading") : t("mfa.verify")}
              </Button>
            </form>
          </CardContent>
        </Card>
      </section>
    );
  }

  // Session present but MFA state is still being checked
  if (session && mfaRequired === null) {
    return (
      <section className="page-container flex items-center justify-center">
        <p className="text-muted-foreground">{t("common.loading")}</p>
      </section>
    );
  }

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>{t("login.welcomeBack")}</CardTitle>
          <CardDescription>{t("login.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button
              type="button"
              variant={mode === "login" ? "default" : "outline"}
              className="w-full"
              onClick={() => setMode("login")}
            >
              {t("login.signIn")}
            </Button>
            <Button
              type="button"
              variant={mode === "signup" ? "default" : "outline"}
              className="w-full"
              onClick={() => setMode("signup")}
            >
              {t("login.signUp")}
            </Button>
          </div>

          <form className="space-y-3" onSubmit={handleSubmit}>
            <Input
              type="email"
              placeholder={t("login.email")}
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
            {mode !== "reset" && (
              <Input
                type="password"
                placeholder={t("login.password")}
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
              />
            )}
            {mode === "signup" && (
              <Input
                type="password"
                placeholder={t("login.confirmPassword")}
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                required
              />
            )}

            <Button className="w-full" type="submit" disabled={busy}>
              {mode === "login" && t("login.signIn")}
              {mode === "signup" && t("login.createAccount")}
              {mode === "reset" && t("login.sendResetEmail")}
            </Button>

            {mode === "signup" && signupStatus === "confirm" && (
              <div className="rounded-md bg-warning/10 p-3 text-sm text-foreground border border-warning/20">
                <p className="font-medium">{t("login.checkYourEmail")}</p>
                <p className="mt-1">{t("login.confirmationSentDesc", { email })}</p>
                <Button
                  type="button"
                  variant="link"
                  className="h-auto p-0 text-primary underline"
                  onClick={resendConfirmation}
                  disabled={busy}
                >
                  {t("login.resend")}
                </Button>
              </div>
            )}

            {mode === "signup" && signupStatus === "auto" && (
              <div className="rounded-md bg-secondary p-3 text-sm text-foreground border border-border">
                <p className="font-medium">{t("login.accountCreated")}</p>
                <p className="mt-1">{t("login.noEmailConfirmation")}</p>
              </div>
            )}
          </form>

          <div className="flex items-center justify-between text-sm">
            <Button type="button" variant="ghost" onClick={() => setMode("reset")}>
              {t("login.forgotPassword")}
            </Button>
            {mode === "reset" && (
              <Button type="button" variant="ghost" onClick={() => setMode("login")}>
                {t("login.backToSignIn")}
              </Button>
            )}
          </div>

          <div className="space-y-2">
            <Button className="w-full" variant="outline" onClick={() => signInWithProvider("google")}>
              {t("login.continueWithGoogle")}
            </Button>
          </div>
        </CardContent>
      </Card>
    </section>
  );
}
```

**Explanation:** This React component renders UI for the `Login` view or widget.

## `react-frontend/src/pages/MFASetup.jsx`

### `MFASetup`

- **File:** `react-frontend/src/pages/MFASetup.jsx`
- **Lines:** `13-182`
- **Purpose:** Renders the `MFASetup` component.

**Code:**
```jsx
export default function MFASetup() {
  const { t } = useI18n();
  const { user } = useAuth();

  const [factors, setFactors] = useState([]);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [verifying, setVerifying] = useState(false);
  const [enrollment, setEnrollment] = useState(null); // { id, qr_code, secret }
  const [code, setCode] = useState("");

  const fetchFactors = async () => {
    try {
      const { data, error } = await supabase.auth.mfa.listFactors();
      if (error) throw error;
      setFactors(data?.all || []);
    } catch (err) {
      toast.error(t("mfa.factorError") + ": " + (err.message || err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFactors();
  }, []);

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      const { data, error } = await supabase.auth.mfa.enroll({
        factorType: "totp",
        friendlyName: "LUMI Authenticator",
      });
      if (error) throw error;
      setEnrollment(data);
    } catch (err) {
      toast.error(t("mfa.enrollError") + ": " + (err.message || err));
    } finally {
      setEnrolling(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!enrollment || !code) return;
    setVerifying(true);
    try {
      const { data: challenge, error: challengeError } = await supabase.auth.mfa.challenge({
        factorId: enrollment.id,
      });
      if (challengeError) throw challengeError;

      const { data, error } = await supabase.auth.mfa.verify({
        factorId: enrollment.id,
        challengeId: challenge.id,
        code: code.replace(/\s/g, ""),
      });
      if (error) throw error;

      toast.success(t("mfa.enabled"));
      setEnrollment(null);
      setCode("");
      await fetchFactors();
      if (data.session) {
        // The session is already refreshed by the MFA verify event in most cases,
        // but we can help the AuthContext along.
        supabase.auth.getSession().catch(() => {});
      }
    } catch (err) {
      toast.error(t("mfa.verifyError") + ": " + (err.message || err));
    } finally {
      setVerifying(false);
    }
  };

  const handleUnenroll = async (factorId) => {
    if (!window.confirm(t("mfa.disableConfirm"))) return;
    try {
      const { error } = await supabase.auth.mfa.unenroll({ factorId });
      if (error) throw error;
      toast.success(t("mfa.disabled"));
      await fetchFactors();
    } catch (err) {
      toast.error(t("mfa.unenrollError") + ": " + (err.message || err));
    }
  };

  const verifiedFactor = factors.find((f) => f.status === "verified");

  return (
    <div className="page-container stack max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold flex items-center gap-2">
        <Shield className="h-6 w-6 text-primary" />
        {t("mfa.title")}
      </h1>

      <Card>
        <CardHeader>
          <CardTitle>{t("mfa.status")}</CardTitle>
          <CardDescription>{t("mfa.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {loading ? (
            <p className="text-sm text-muted-foreground">{t("common.loading")}</p>
          ) : verifiedFactor ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-sm">
                <ShieldCheck className="h-5 w-5 text-primary" />
                <span className="font-medium">{t("mfa.enabledStatus")}</span>
              </div>
              <Button
                type="button"
                variant="destructive"
                onClick={() => handleUnenroll(verifiedFactor.id)}
              >
                <ShieldOff className="h-4 w-4 mr-2" />
                {t("mfa.disable")}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">{t("mfa.disabledStatus")}</p>
              <Button type="button" onClick={handleEnroll} disabled={enrolling}>
                {enrolling ? t("common.loading") : t("mfa.enable")}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {enrollment && (
        <Card>
          <CardHeader>
            <CardTitle>{t("mfa.scanQR")}</CardTitle>
            <CardDescription>{t("mfa.scanQRDescription")}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-center">
              <img
                src={enrollment.totp?.qr_code}
                alt="TOTP QR code"
                className="rounded-lg border bg-white p-2"
              />
            </div>
            <div className="rounded bg-muted p-3 text-sm font-mono break-all">
              {enrollment.totp?.secret}
            </div>
            <form onSubmit={handleVerify} className="space-y-2">
              <Input
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder={t("mfa.codePlaceholder")}
                maxLength={10}
                autoComplete="one-time-code"
              />
              <Button type="submit" disabled={verifying || !code}>
                {verifying ? t("common.loading") : t("mfa.verify")}
              </Button>
            </form>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `MFASetup` view or widget.

## `react-frontend/src/pages/MapPage.jsx`

### `MapPage`

- **File:** `react-frontend/src/pages/MapPage.jsx`
- **Lines:** `5-27`
- **Purpose:** Renders the `MapPage` component.

**Code:**
```jsx
export default function MapPage() {
  const { t } = useI18n();

  return (
    <section className="container mx-auto px-4 py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="text-2xl font-bold">{t("map.title")}</h1>
        <p className="text-muted-foreground">
          {t("map.description")}
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
```

**Explanation:** This React component renders UI for the `MapPage` view or widget.

## `react-frontend/src/pages/NotFound.jsx`

### `NotFound`

- **File:** `react-frontend/src/pages/NotFound.jsx`
- **Lines:** `4-18`
- **Purpose:** Renders the `NotFound` component.

**Code:**
```jsx
export default function NotFound() {
  const { t } = useI18n();

  return (
    <section className="page-container stack">
      <div className="space-y-2">
        <h1>{t("notFound.title")}</h1>
        <p>{t("notFound.description")}</p>
      </div>
      <Link to="/" className="text-sm text-primary">
        {t("notFound.goHome")}
      </Link>
    </section>
  );
}
```

**Explanation:** This React component renders UI for the `NotFound` view or widget.

## `react-frontend/src/pages/ProfilePage.jsx`

### `ProfilePage`

- **File:** `react-frontend/src/pages/ProfilePage.jsx`
- **Lines:** `9-254`
- **Purpose:** Renders the `ProfilePage` component.

**Code:**
```jsx
export default function ProfilePage() {
  const { t } = useI18n();
  const { user, accessToken, emailConfirmed } = useAuth();
  const [profile, setProfile] = useState({
    full_name: "",
    organization: "",
    location: "",
    avatar_url: "",
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!user) return;
    supabase
      .from("profiles")
      .select("full_name, organization, location, avatar_url")
      .eq("id", user.id)
      .single()
      .then(({ data }) => {
        if (data) setProfile((p) => ({ ...p, ...data }));
      });

    // Sync OAuth avatar from auth metadata to profiles on first load
    fetch(`${getApiBaseUrl()}/protected/sync-avatar`, {
      method: "POST",
      headers: { Authorization: `Bearer ${accessToken}` },
    }).catch(() => {});
  }, [user, accessToken]);

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(profile),
      });
      setMessage(t("profile.updated"));
    } catch {
      setMessage(t("profile.updateFailed"));
    } finally {
      setSaving(false);
    }
  };

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ALLOWED_EXTS = ["jpg", "jpeg", "png", "gif", "webp"];
    const MAX_FILE_SIZE = 2 * 1024 * 1024; // 2 MB
    const ext = file.name.split(".").pop()?.toLowerCase();
    if (!ext || !ALLOWED_EXTS.includes(ext)) {
      setMessage(t("profile.avatarUploadFailed") + "Invalid file type. Allowed: JPG, PNG, GIF, WebP");
      return;
    }
    if (!file.type.startsWith("image/")) {
      setMessage(t("profile.avatarUploadFailed") + "File must be an image.");
      return;
    }
    if (file.size > MAX_FILE_SIZE) {
      setMessage(t("profile.avatarUploadFailed") + "File too large. Maximum size is 2 MB.");
      return;
    }

    setUploading(true);
    setMessage("");
    try {
      const ext = file.name.split(".").pop();
      const path = `${user.id}/avatar.${ext}`;
      const { error: uploadError } = await supabase.storage
        .from("avatars")
        .upload(path, file, { upsert: true, contentType: file.type });
      if (uploadError) throw uploadError;

      const { data: urlData } = supabase.storage.from("avatars").getPublicUrl(path);
      const publicUrl = urlData?.publicUrl;
      if (!publicUrl) throw new Error("Failed to get public URL");

      // Update profile in DB
      await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ avatar_url: publicUrl }),
      });

      setProfile((p) => ({ ...p, avatar_url: publicUrl }));
      setMessage(t("profile.avatarUpdated"));
    } catch (err) {
      setMessage(t("profile.avatarUploadFailed") + err.message);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handleRemoveAvatar = async () => {
    setUploading(true);
    try {
      await fetch(`${getApiBaseUrl()}/protected/profile`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ avatar_url: null }),
      });
      setProfile((p) => ({ ...p, avatar_url: "" }));
      setMessage(t("profile.avatarRemoved"));
    } catch {
      setMessage(t("profile.avatarRemoveFailed"));
    } finally {
      setUploading(false);
    }
  };

  const initials = (profile.full_name || user?.email || "U")
    .split(" ")
    .map((n) => n[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const currentAvatar =
    profile.avatar_url || user?.user_metadata?.avatar_url || user?.user_metadata?.picture;

  if (!user) return <p>{t("common.loading")}</p>;

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-2">{t("profile.title")}</h1>

      <div className="flex items-center gap-2 mb-6 text-sm text-muted-foreground">
        <span>{user?.email}</span>
        {emailConfirmed ? (
          <span className="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800">
            ✓ {t("profile.verified")}
          </span>
        ) : (
          <span className="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
            ⚠ {t("profile.unverified")}
          </span>
        )}
      </div>

      {/* Avatar Section */}
      <div className="flex items-center gap-4 mb-6">
        <div className="relative">
          {currentAvatar ? (
            <img
              src={currentAvatar}
              alt=""
              className="h-20 w-20 rounded-full object-cover border"
            />
          ) : (
            <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center text-xl font-bold text-primary border">
              {initials}
            </div>
          )}
        </div>
        <div className="flex flex-col gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleFileChange}
          />
          <Button
            variant="outline"
            size="sm"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? t("common.saving") : t("profile.changePhoto")}
          </Button>
          {currentAvatar && (
            <Button
              variant="ghost"
              size="sm"
              className="text-destructive"
              onClick={handleRemoveAvatar}
              disabled={uploading}
            >
              {t("profile.removePhoto")}
            </Button>
          )}
        </div>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">{t("profile.fullName")}</label>
          <input
            type="text"
            value={profile.full_name || ""}
            onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">{t("profile.organization")}</label>
          <input
            type="text"
            value={profile.organization || ""}
            onChange={(e) => setProfile({ ...profile, organization: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">{t("profile.location")}</label>
          <input
            type="text"
            value={profile.location || ""}
            onChange={(e) => setProfile({ ...profile, location: e.target.value })}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>

        {message && (
          <p className={`text-sm ${message.includes("Failed") ? "text-destructive" : "text-green-600"}`}>
            {message}
          </p>
        )}

        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? t("common.saving") : t("profile.saveChanges")}
        </button>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `ProfilePage` view or widget.

## `react-frontend/src/pages/ResetPassword.jsx`

### `ResetPassword`

- **File:** `react-frontend/src/pages/ResetPassword.jsx`
- **Lines:** `10-74`
- **Purpose:** Renders the `ResetPassword` component.

**Code:**
```jsx
export default function ResetPassword() {
  const { t } = useI18n();
  const { session, updatePassword } = useAuth();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmPassword) {
      toast.error(t("resetPassword.passwordsDoNotMatch"));
      return;
    }

    setBusy(true);
    try {
      const { error } = await updatePassword(password);
      if (error) throw error;
      toast.success(t("resetPassword.success"));
    } catch (error) {
      toast.error(error?.message || t("resetPassword.error"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="page-container">
      <Card className="mx-auto max-w-md">
        <CardHeader>
          <CardTitle>{t("resetPassword.title")}</CardTitle>
          <CardDescription>{t("resetPassword.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {!session && (
            <p className="text-sm text-muted-foreground">
              {t("resetPassword.noSession")}
            </p>
          )}
          <form className="space-y-3" onSubmit={handleSubmit}>
            <Input
              type="password"
              placeholder={t("resetPassword.newPasswordPlaceholder")}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={6}
            />
            <Input
              type="password"
              placeholder={t("resetPassword.confirmPasswordPlaceholder")}
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              minLength={6}
            />
            <Button className="w-full" type="submit" disabled={busy || !session}>
              {t("resetPassword.updatePassword")}
            </Button>
          </form>
        </CardContent>
      </Card>
    </section>
  );
}
```

**Explanation:** This React component renders UI for the `ResetPassword` view or widget.

## `react-frontend/src/pages/SavedSimulations.jsx`

### `SavedSimulations`

- **File:** `react-frontend/src/pages/SavedSimulations.jsx`
- **Lines:** `18-286`
- **Purpose:** Renders the `SavedSimulations` component.

**Code:**
```jsx
export default function SavedSimulations() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [savedSimulations, setSavedSimulations] = useState([]);
  const [chatSessions, setChatSessions] = useState([]);
  const [expandedSession, setExpandedSession] = useState(null);

  useEffect(() => {
    if (!user) return;
    const load = async () => {
      setLoading(true);
      try {
        // Try joined query first; fall back to plain select if FK/RLS blocks it
        let simsQuery = supabase
          .from("saved_simulations")
          .select("*, municipalities(name)")
          .eq("user_id", user.id)
          .order("created_at", { ascending: false });
        let { data: sims, error: simsError } = await simsQuery;

        if (simsError || !sims) {
          ({ data: sims, error: simsError } = await supabase
            .from("saved_simulations")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false }));
        }

        const [{ data: sessions }] = await Promise.all([
          supabase
            .from("chat_sessions")
            .select("*")
            .eq("user_id", user.id)
            .order("created_at", { ascending: false }),
        ]);

        setSavedSimulations(sims || []);
        setChatSessions(sessions || []);
      } catch {
        toast.error(t("savedSimulations.loadError"));
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [user]);

  const fetchSessionMessages = async (sessionId) => {
    if (expandedSession === sessionId) {
      setExpandedSession(null);
      return;
    }
    const { data } = await supabase
      .from("chat_messages")
      .select("role, content, created_at")
      .eq("session_id", sessionId)
      .order("created_at", { ascending: true });
    setChatSessions((prev) =>
      prev.map((s) => (s.id === sessionId ? { ...s, messages: data || [] } : s))
    );
    setExpandedSession(sessionId);
  };

  const deleteSimulation = async (id) => {
    if (!window.confirm(t("savedSimulations.deleteSimConfirm"))) return;
    try {
      const { error } = await supabase
        .from("saved_simulations")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);
      if (error) throw error;
      setSavedSimulations((prev) => prev.filter((s) => s.id !== id));
      toast.success(t("savedSimulations.simDeleted"));
    } catch {
      toast.error(t("savedSimulations.simDeleteFailed"));
    }
  };

  const deleteChatSession = async (id) => {
    if (!window.confirm(t("savedSimulations.deleteChatConfirm"))) return;
    try {
      const { error } = await supabase
        .from("chat_sessions")
        .delete()
        .eq("id", id)
        .eq("user_id", user.id);
      if (error) throw error;
      setChatSessions((prev) => prev.filter((s) => s.id !== id));
      if (expandedSession === id) setExpandedSession(null);
      toast.success(t("savedSimulations.chatDeleted"));
    } catch {
      toast.error(t("savedSimulations.chatDeleteFailed"));
    }
  };

  if (!user) return <p className="p-6">{t("savedSimulations.pleaseLogin")}</p>;
  if (loading) {
    return (
      <section className="page-container stack">
        <h1 className="text-2xl font-bold">{t("savedSimulations.title")}</h1>
        <LoadingSkeleton />
      </section>
    );
  }

  return (
    <section className="page-container stack space-y-6">
      <h1 className="text-2xl font-bold">{t("savedSimulations.title")}</h1>

      {/* EcoSim Saves */}
      <Card>
        <CardHeader>
          <CardTitle>{t("savedSimulations.ecoSimsTitle")}</CardTitle>
          <CardDescription>{t("savedSimulations.ecoSimsDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          {savedSimulations.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {t("savedSimulations.noSimulations")}{" "}
              <Link to="/ecosim" className="underline text-primary">
                {t("savedSimulations.runOne")}
              </Link>
              .
            </p>
          ) : (
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {savedSimulations.map((sim) => {
                const res = sim.results || {};
                const recSource = res.recommended_source || "—";
                const municipality = res.municipality || sim.municipalities?.name || "—";
                const gen = res.estimated_generation_kwh;
                const created = sim.created_at
                  ? new Date(sim.created_at).toLocaleDateString()
                  : "";
                return (
                  <div
                    key={sim.id}
                    className="rounded-lg border bg-card p-4 hover:shadow-sm transition-shadow"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h3
                        className="font-semibold text-sm truncate flex-1"
                        title={sim.label || t("savedSimulations.unnamedSimulation")}
                      >
                        {sim.label || t("savedSimulations.unnamedSimulation")}
                      </h3>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {municipality} • {recSource}
                    </p>
                    {gen !== undefined && gen !== null && (
                      <p className="text-xs mt-2">
                        <span className="font-medium">{Math.round(gen).toLocaleString()}</span>{" "}
                        kWh/mo
                      </p>
                    )}
                    {created && (
                      <p className="text-xs text-muted-foreground mt-1">{created}</p>
                    )}
                    <div className="flex items-center gap-2 mt-3">
                      <Link to={`/ecosim?simulation_id=${sim.id}`} className="flex-1">
                        <Button variant="outline" size="sm" className="w-full">
                          {t("savedSimulations.open")}
                        </Button>
                      </Link>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteSimulation(sim.id)}
                        className="text-destructive hover:text-destructive"
                      >
                        {t("savedSimulations.delete")}
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Chat History */}
      <Card>
        <CardHeader>
          <CardTitle>{t("savedSimulations.chatHistoryTitle")}</CardTitle>
          <CardDescription>{t("savedSimulations.chatHistoryDescription")}</CardDescription>
        </CardHeader>
        <CardContent>
          {chatSessions.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {t("savedSimulations.noChatHistory")}{" "}
              <Link to="/chat" className="underline text-primary">
                {t("savedSimulations.startChat")}
              </Link>
              .
            </p>
          ) : (
            <div className="space-y-2">
              {chatSessions.map((session) => {
                const isOpen = expandedSession === session.id;
                const created = session.created_at
                  ? new Date(session.created_at).toLocaleDateString()
                  : "";
                return (
                  <div key={session.id} className="rounded-lg border bg-card">
                    <button
                      onClick={() => fetchSessionMessages(session.id)}
                      className="w-full flex items-center justify-between p-3 text-left hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-2 min-w-0">
                        <span className="text-sm font-medium truncate">
                          {session.title || t("savedSimulations.newChat")}
                        </span>
                        {session.is_flagged && (
                          <span className="text-xs bg-destructive/10 text-destructive px-1.5 py-0.5 rounded">
                            {t("savedSimulations.flagged")}
                          </span>
                        )}
                      </div>
                      <span className="text-xs text-muted-foreground shrink-0">
                        {created} {isOpen ? "▲" : "▼"}
                      </span>
                    </button>
                    {isOpen && session.messages && (
                      <div className="px-3 pb-3 space-y-2 border-t bg-muted/30">
                        {session.messages.map((msg, i) => (
                          <div key={i} className="py-1">
                            <span
                              className={`text-xs font-bold uppercase ${
                                msg.role === "user"
                                  ? "text-primary"
                                  : "text-muted-foreground"
                              }`}
                            >
                              {msg.role}
                            </span>
                            <p className="text-sm text-muted-foreground">{msg.content}</p>
                          </div>
                        ))}
                        <div className="flex items-center gap-2 mt-1">
                          <Link to={`/chat?session=${session.id}`}>
                            <Button size="sm" variant="outline">
                              {t("savedSimulations.continueChat")}
                            </Button>
                          </Link>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => deleteChatSession(session.id)}
                            className="text-destructive hover:text-destructive"
                          >
                            {t("savedSimulations.delete")}
                          </Button>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </section>
  );
}
```

**Explanation:** This React component renders UI for the `SavedSimulations` view or widget.

## `react-frontend/src/pages/admin/AdminAnalytics.jsx`

### `AdminAnalytics`

- **File:** `react-frontend/src/pages/admin/AdminAnalytics.jsx`
- **Lines:** `7-52`
- **Purpose:** Renders the `AdminAnalytics` component.

**Code:**
```jsx
export default function AdminAnalytics() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${getApiBaseUrl()}/admin/analytics`, {
      headers: { Authorization: `Bearer ${accessToken}` },
    })
      .then((r) => r.json())
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [accessToken]);

  if (loading) return <p className="p-6">{t("common.loading")}</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{t("admin.analyticsPage.title")}</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.totalUsers")}</p>
          <p className="text-2xl font-bold">{stats?.total_users ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.simulations")}</p>
          <p className="text-2xl font-bold">{stats?.total_simulations ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.chatSessions")}</p>
          <p className="text-2xl font-bold">{stats?.total_chat_sessions ?? 0}</p>
        </div>
        <div className="border rounded-lg p-4">
          <p className="text-sm text-muted-foreground">{t("admin.analyticsPage.freePremium")}</p>
          <p className="text-2xl font-bold">
            {stats?.free_users ?? 0} / {stats?.premium_users ?? 0}
          </p>
        </div>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `AdminAnalytics` view or widget.

## `react-frontend/src/pages/admin/AdminConfig.jsx`

### `AdminConfig`

- **File:** `react-frontend/src/pages/admin/AdminConfig.jsx`
- **Lines:** `7-94`
- **Purpose:** Renders the `AdminConfig` component.

**Code:**
```jsx
export default function AdminConfig() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [config, setConfig] = useState({
    chatbot_enabled: true,
    maintenance_mode: false,
    free_chat_limit: 5,
    free_sim_limit: 3,
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const handleSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await fetch(`${getApiBaseUrl()}/admin/config`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify(config),
      });
      setMessage(t("admin.configPage.saved"));
    } catch {
      setMessage(t("admin.configPage.failed"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{t("admin.configPage.title")}</h1>
      <div className="space-y-4">
        <label className="flex items-center justify-between p-3 border rounded-lg">
          <span>{t("admin.configPage.chatbotEnabled")}</span>
          <input
            type="checkbox"
            checked={config.chatbot_enabled}
            onChange={(e) => setConfig({ ...config, chatbot_enabled: e.target.checked })}
            className="w-5 h-5"
          />
        </label>
        <label className="flex items-center justify-between p-3 border rounded-lg">
          <span>{t("admin.configPage.maintenanceMode")}</span>
          <input
            type="checkbox"
            checked={config.maintenance_mode}
            onChange={(e) => setConfig({ ...config, maintenance_mode: e.target.checked })}
            className="w-5 h-5"
          />
        </label>
        <div className="p-3 border rounded-lg">
          <label className="block text-sm font-medium mb-1">{t("admin.configPage.freeChatLimit")}</label>
          <input
            type="number"
            value={config.free_chat_limit}
            onChange={(e) => setConfig({ ...config, free_chat_limit: parseInt(e.target.value) || 0 })}
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>
        <div className="p-3 border rounded-lg">
          <label className="block text-sm font-medium mb-1">{t("admin.configPage.freeSimLimit")}</label>
          <input
            type="number"
            value={config.free_sim_limit}
            onChange={(e) => setConfig({ ...config, free_sim_limit: parseInt(e.target.value) || 0 })}
            className="w-full px-3 py-2 border rounded-lg"
          />
        </div>
        {message && (
          <p className={`text-sm ${message.includes("Failed") ? "text-destructive" : "text-green-600"}`}>
            {message}
          </p>
        )}
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50"
        >
          {saving ? t("admin.configPage.saving") : t("admin.configPage.saveConfiguration")}
        </button>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `AdminConfig` view or widget.

## `react-frontend/src/pages/admin/AdminDashboard.jsx`

### `AdminDashboard`

- **File:** `react-frontend/src/pages/admin/AdminDashboard.jsx`
- **Lines:** `10-123`
- **Purpose:** Renders the `AdminDashboard` component.

**Code:**
```jsx
export default function AdminDashboard() {
  const { t } = useI18n();
  const { user } = useAuth();
  const [stats, setStats] = useState({ users: 0, simulations: 0, loading: true });

  useEffect(() => {
    let mounted = true;
    const fetchStats = async () => {
      try {
        const [{ count: users }, { count: simulations }] = await Promise.all([
          supabase.from("profiles").select("*", { count: "exact", head: true }),
          supabase.from("saved_simulations").select("*", { count: "exact", head: true }),
        ]);
        if (mounted) setStats({ users: users || 0, simulations: simulations || 0, loading: false });
      } catch {
        if (mounted) setStats({ users: 0, simulations: 0, loading: false });
      }
    };
    fetchStats();
    return () => {
      mounted = false;
    };
  }, []);

  const adminName = user?.user_metadata?.full_name || user?.email || t("common.user");

  const links = [
    {
      to: "/admin/users",
      icon: Users,
      title: t("admin.users"),
      desc: t("admin.usersDesc"),
    },
    {
      to: "/admin/analytics",
      icon: BarChart3,
      title: t("admin.analytics"),
      desc: t("admin.analyticsDesc"),
    },
    {
      to: "/admin/config",
      icon: Settings,
      title: t("admin.config"),
      desc: t("admin.configDesc"),
    },
    {
      to: "/admin/moderate",
      icon: Shield,
      title: t("admin.moderation"),
      desc: t("admin.moderationDesc"),
    },
  ];

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold flex items-center gap-2">
          <LayoutDashboard className="h-6 w-6 text-primary" />
          {t("admin.portal")}
        </h1>
        <p className="text-muted-foreground mt-1">
          {t("admin.welcome")} &mdash; {t("admin.summary")}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("common.user", { count: stats.users })}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.loading ? "..." : t("admin.usersCount", { count: stats.users })}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {t("nav.savedSims")}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold">{stats.loading ? "..." : t("admin.simsCount", { count: stats.simulations })}</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {links.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="group flex items-start gap-4 p-6 border rounded-lg bg-card hover:bg-muted transition-colors"
          >
            <div className="p-3 rounded-lg bg-primary/10 text-primary">
              <link.icon className="h-6 w-6" />
            </div>
            <div>
              <h2 className="text-lg font-semibold group-hover:text-primary transition-colors">
                {link.title}
              </h2>
              <p className="text-sm text-muted-foreground mt-1">{link.desc}</p>
            </div>
          </Link>
        ))}
      </div>

      <p className="text-sm text-muted-foreground">
        {t("common.user")}: <span className="font-medium text-foreground">{adminName}</span>
      </p>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `AdminDashboard` view or widget.

## `react-frontend/src/pages/admin/AdminModeration.jsx`

### `AdminModeration`

- **File:** `react-frontend/src/pages/admin/AdminModeration.jsx`
- **Lines:** `9-158`
- **Purpose:** Renders the `AdminModeration` component.

**Code:**
```jsx
export default function AdminModeration() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState({});

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${getApiBaseUrl()}/admin/chat-sessions?limit=50`,
        { headers: { Authorization: `Bearer ${accessToken}` } }
      );
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  const toggleFlag = async (sessionId, currentFlag) => {
    try {
      await fetch(
        `${getApiBaseUrl()}/admin/chat-sessions/${sessionId}/flag`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({ is_flagged: !currentFlag }),
        }
      );
      setSessions((prev) =>
        prev.map((s) =>
          s.id === sessionId ? { ...s, is_flagged: !currentFlag } : s
        )
      );
    } catch {
      // ignore
    }
  };

  const toggleExpand = (id) => {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleString() : "—");

  if (loading) return <p className="p-6">{t("admin.moderationPage.loading")}</p>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">{t("admin.moderationPage.title")}</h1>
      <div className="border rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-muted">
            <tr>
              <th className="text-left p-3">{t("admin.moderationPage.columns.session")}</th>
              <th className="text-left p-3">{t("admin.moderationPage.columns.userId")}</th>
              <th className="text-left p-3">{t("admin.moderationPage.columns.messages")}</th>
              <th className="text-left p-3">{t("admin.moderationPage.columns.created")}</th>
              <th className="text-left p-3">{t("admin.moderationPage.columns.flagged")}</th>
              <th className="text-left p-3">{t("admin.moderationPage.columns.actions")}</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((s) => (
              <>
                <tr key={s.id} className="border-t hover:bg-muted/50">
                  <td className="p-3 font-medium">{s.title || t("admin.moderationPage.untitled")}</td>
                  <td className="p-3 text-xs text-muted-foreground truncate max-w-[120px]">
                    {s.user_id}
                  </td>
                  <td className="p-3">{(s.chat_messages || []).length}</td>
                  <td className="p-3">{formatDate(s.created_at)}</td>
                  <td className="p-3">
                    {s.is_flagged ? (
                      <Badge variant="destructive">{t("admin.moderationPage.flagged")}</Badge>
                    ) : (
                      <Badge variant="outline">{t("admin.moderationPage.clean")}</Badge>
                    )}
                  </td>
                  <td className="p-3">
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => toggleExpand(s.id)}
                      >
                        {expanded[s.id] ? t("admin.moderationPage.hide") : t("admin.moderationPage.view")}
                      </Button>
                      <Button
                        size="sm"
                        variant={s.is_flagged ? "default" : "destructive"}
                        onClick={() => toggleFlag(s.id, s.is_flagged)}
                      >
                        {s.is_flagged ? t("admin.moderationPage.unflag") : t("admin.moderationPage.flag")}
                      </Button>
                    </div>
                  </td>
                </tr>
                {expanded[s.id] && (
                  <tr>
                    <td colSpan={6} className="p-3 bg-muted/30">
                      <div className="space-y-2 max-h-64 overflow-y-auto">
                        {(s.chat_messages || []).map((msg, idx) => (
                          <div
                            key={idx}
                            className={`text-sm p-2 rounded ${
                              msg.role === "user"
                                ? "bg-primary/10 ml-4"
                                : "bg-secondary/50 mr-4"
                            }`}
                          >
                            <span className="text-xs font-semibold uppercase text-muted-foreground">
                              {msg.role}
                            </span>
                            <p className="mt-1">{msg.content}</p>
                          </div>
                        ))}
                        {(s.chat_messages || []).length === 0 && (
                          <p className="text-sm text-muted-foreground">{t("admin.moderationPage.noMessages")}</p>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </>
            ))}
            {sessions.length === 0 && (
              <tr>
                <td colSpan={6} className="p-6 text-center text-muted-foreground">
                  {t("admin.moderationPage.noSessions")}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `AdminModeration` view or widget.

## `react-frontend/src/pages/admin/AdminUsers.jsx`

### `AdminUsers`

- **File:** `react-frontend/src/pages/admin/AdminUsers.jsx`
- **Lines:** `12-284`
- **Purpose:** Renders the `AdminUsers` component.

**Code:**
```jsx
export default function AdminUsers() {
  const { t } = useI18n();
  const { accessToken } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("all");
  const [filterPlan, setFilterPlan] = useState("all");
  const [filterStatus, setFilterStatus] = useState("all");
  const [createOpen, setCreateOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/admin/users`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      const data = await res.json();
      setUsers(data.users || []);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [accessToken]);

  const filtered = useMemo(() => {
    return users.filter((u) => {
      const matchesSearch =
        (u.email || "").toLowerCase().includes(search.toLowerCase()) ||
        (u.full_name || "").toLowerCase().includes(search.toLowerCase());
      const matchesRole = filterRole === "all" || u.role === filterRole;
      const matchesPlan = filterPlan === "all" || u.plan === filterPlan;
      const matchesStatus =
        filterStatus === "all"
          ? true
          : filterStatus === "active"
          ? u.is_active
          : !u.is_active;
      return matchesSearch && matchesRole && matchesPlan && matchesStatus;
    });
  }, [users, search, filterRole, filterPlan, filterStatus]);

  const handleAction = async (url, method = "POST", body = null) => {
    try {
      await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: body ? JSON.stringify(body) : undefined,
      });
      fetchUsers();
    } catch {
      // ignore
    }
  };

  const openDetail = (u) => {
    setSelectedUser(u);
    setDrawerOpen(true);
  };

  const formatDate = (d) => (d ? new Date(d).toLocaleDateString() : "—");

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">{t("admin.usersPage.title")}</h1>
        <Button onClick={() => setCreateOpen(true)}>{t("admin.usersPage.createUser")}</Button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 mb-4">
        <Input
          placeholder={t("admin.usersPage.searchPlaceholder")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
        />
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">{t("admin.usersPage.allRoles")}</option>
          <option value="user">{t("admin.usersPage.roleUser")}</option>
          <option value="admin">{t("admin.usersPage.roleAdmin")}</option>
          <option value="dev">{t("admin.usersPage.roleDev")}</option>
        </select>
        <select
          value={filterPlan}
          onChange={(e) => setFilterPlan(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">{t("admin.usersPage.allPlans")}</option>
          <option value="free">{t("admin.usersPage.planFree")}</option>
          <option value="premium">{t("admin.usersPage.planPremium")}</option>
        </select>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-md border px-3 py-2 text-sm"
        >
          <option value="all">{t("admin.usersPage.allStatus")}</option>
          <option value="active">{t("admin.usersPage.statusActive")}</option>
          <option value="banned">{t("admin.usersPage.statusBanned")}</option>
        </select>
      </div>

      {loading ? (
        <p className="text-muted-foreground">{t("admin.usersPage.loading")}</p>
      ) : (
        <div className="border rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-muted">
              <tr>
                <th className="text-left p-3">{t("admin.usersPage.columns.user")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.email")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.role")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.plan")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.status")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.joined")}</th>
                <th className="text-left p-3">{t("admin.usersPage.columns.actions")}</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => {
                const initials = (u.full_name || u.email || "U")
                  .split(" ")
                  .map((n) => n[0])
                  .join("")
                  .slice(0, 2)
                  .toUpperCase();
                return (
                <tr key={u.id} className="border-t hover:bg-muted/50">
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      {u.avatar_url ? (
                        <img
                          src={u.avatar_url}
                          alt=""
                          className="h-8 w-8 rounded-full object-cover border"
                          onError={(e) => { e.target.style.display = "none"; }}
                        />
                      ) : (
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary">
                          {initials}
                        </div>
                      )}
                      <span>{u.full_name || t("common.notAvailable")}</span>
                    </div>
                  </td>
                  <td className="p-3 text-xs text-muted-foreground truncate max-w-[160px]">
                    {u.email || t("common.notAvailable")}
                  </td>
                  <td className="p-3">
                    <Badge variant="outline" className="capitalize">
                      {u.role === "admin" ? t("admin.usersPage.roleAdmin") : u.role === "dev" ? t("admin.usersPage.roleDev") : t("admin.usersPage.roleUser")}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge variant="secondary" className="capitalize">
                      {u.role === "admin" || u.role === "dev" ? t("admin.usersPage.planPremium") : (u.plan === "premium" ? t("admin.usersPage.planPremium") : t("admin.usersPage.planFree"))}
                    </Badge>
                  </td>
                  <td className="p-3">
                    <Badge
                      variant={u.is_active ? "default" : "destructive"}
                      className="text-xs"
                    >
                      {u.is_active ? t("admin.usersPage.statusActive") : t("admin.usersPage.statusBanned")}
                    </Badge>
                  </td>
                  <td className="p-3">{formatDate(u.created_at)}</td>
                  <td className="p-3">
                    <div className="flex flex-wrap gap-1">
                      <Button size="sm" variant="outline" onClick={() => openDetail(u)}>
                        {t("admin.usersPage.view")}
                      </Button>
                      <Button
                        size="sm"
                        variant={u.is_active ? "destructive" : "default"}
                        onClick={() =>
                          handleAction(
                            `${getApiBaseUrl()}/admin/users/${u.id}/ban`
                          )
                        }
                      >
                        {u.is_active ? t("admin.usersPage.ban") : t("admin.usersPage.unban")}
                      </Button>
                      <select
                        value={u.role}
                        onChange={(e) =>
                          handleAction(
                            `${getApiBaseUrl()}/admin/users/${u.id}/role`,
                            "PUT",
                            { role: e.target.value }
                          )
                        }
                        className="rounded-md border px-2 py-1 text-xs"
                      >
                        <option value="user">{t("admin.usersPage.roleUser")}</option>
                        <option value="admin">{t("admin.usersPage.roleAdmin")}</option>
                        <option value="dev">{t("admin.usersPage.roleDev")}</option>
                      </select>
                      <select
                        value={u.plan}
                        onChange={(e) =>
                          handleAction(
                            `${getApiBaseUrl()}/admin/users/${u.id}/plan`,
                            "PUT",
                            { plan: e.target.value }
                          )
                        }
                        className="rounded-md border px-2 py-1 text-xs"
                      >
                        <option value="free">{t("admin.usersPage.planFree")}</option>
                        <option value="premium">{t("admin.usersPage.planPremium")}</option>
                      </select>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-destructive"
                        onClick={() => {
                          if (confirm(t("admin.usersPage.deleteConfirm"))) {
                            handleAction(
                              `${getApiBaseUrl()}/admin/users/${u.id}`,
                              "DELETE"
                            );
                          }
                        }}
                      >
                        {t("admin.usersPage.delete")}
                      </Button>
                    </div>
                  </td>
                </tr>
                );
              })}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} className="p-6 text-center text-muted-foreground">
                    {t("admin.usersPage.noResults")}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      <CreateUserModal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        onCreated={fetchUsers}
      />

      <UserDetailDrawer
        user={selectedUser}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
      />
    </div>
  );
}
```

**Explanation:** This React component renders UI for the `AdminUsers` view or widget.

## `react-frontend/src/routes/AppRoutes.jsx`

### `AppRoutes`

- **File:** `react-frontend/src/routes/AppRoutes.jsx`
- **Lines:** `23-122`
- **Purpose:** Renders the `AppRoutes` component.

**Code:**
```jsx
export default function AppRoutes() {
  return (
    <BrowserRouter
      future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}
    >
      <Routes future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <Route element={<MainLayout />}>
          <Route index element={<Home />} />
          <Route path="login" element={<Login />} />
          <Route path="reset-password" element={<ResetPassword />} />
          <Route path="about" element={<About />} />
          <Route
            path="dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="ecosim"
            element={
              <ProtectedRoute>
                <Ecosim />
              </ProtectedRoute>
            }
          />
          <Route
            path="energyhub"
            element={
              <ProtectedRoute>
                <EnergyHub />
              </ProtectedRoute>
            }
          />
          <Route
            path="saved-simulations"
            element={
              <ProtectedRoute>
                <SavedSimulations />
              </ProtectedRoute>
            }
          />
          <Route
            path="mfa"
            element={
              <ProtectedRoute>
                <MFASetup />
              </ProtectedRoute>
            }
          />
          <Route
            path="admin"
            element={
              <AdminRoute>
                <AdminDashboard />
              </AdminRoute>
            }
          />
          <Route
            path="admin/users"
            element={
              <AdminRoute>
                <AdminUsers />
              </AdminRoute>
            }
          />
          <Route
            path="admin/analytics"
            element={
              <AdminRoute>
                <AdminAnalytics />
              </AdminRoute>
            }
          />
          <Route
            path="admin/config"
            element={
              <AdminRoute>
                <AdminConfig />
              </AdminRoute>
            }
          />
          <Route
            path="admin/moderate"
            element={
              <AdminRoute>
                <AdminModeration />
              </AdminRoute>
            }
          />
        </Route>
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  );
}
```

**Explanation:** This React component renders UI for the `AppRoutes` view or widget.

## `react-frontend/src/services/apiClient.js`

### `generateRequestId`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `8-13`
- **Purpose:** Utility function `generateRequestId`.

**Code:**
```javascript
function generateRequestId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}
```

**Explanation:** This helper performs the `generateRequestId` operation. See the code for the full implementation.

### `sleep`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `15-17`
- **Purpose:** Utility function `sleep`.

**Code:**
```javascript
async function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
```

**Explanation:** This helper performs the `sleep` operation. See the code for the full implementation.

### `fetchWithTimeout`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `19-27`
- **Purpose:** Retrieves WithTimeout.

**Code:**
```javascript
async function fetchWithTimeout(url, options, timeoutMs = DEFAULT_TIMEOUT_MS) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } finally {
    clearTimeout(id);
  }
}
```

**Explanation:** This function retrieves WithTimeout. See the code for the full implementation.

### `request`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `29-89`
- **Purpose:** Utility function `request`.

**Code:**
```javascript
export async function request(path, { token, timeoutMs, ...options } = {}) {
  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }
  headers.set("X-Request-ID", generateRequestId());

  const url = `${BASE_URL}${path}`;
  const fetchOptions = { ...options, headers };
  const effectiveTimeout = timeoutMs ?? DEFAULT_TIMEOUT_MS;

  let lastError;
  for (let attempt = 0; attempt < MAX_RETRIES; attempt += 1) {
    try {
      const response = await fetchWithTimeout(url, fetchOptions, effectiveTimeout);

      if (!response.ok) {
        // Retry on rate limit or server overload with backoff
        if ((response.status === 429 || response.status >= 500) && attempt < MAX_RETRIES - 1) {
          const retryAfter = response.headers.get("Retry-After");
          const delay = retryAfter ? Number(retryAfter) * 1000 : INITIAL_RETRY_DELAY_MS * 2 ** attempt;
          await sleep(delay);
          continue;
        }

        let message = "Request failed";
        const text = await response.clone().text();
        try {
          const errorBody = JSON.parse(text);
          if (Array.isArray(errorBody.detail)) {
            message = errorBody.detail.map((d) => d.msg || String(d)).join("; ");
          } else if (typeof errorBody.detail === "string") {
            message = errorBody.detail;
          } else if (errorBody.message) {
            message = errorBody.message;
          } else {
            message = JSON.stringify(errorBody);
          }
        } catch {
          if (text) message = text;
        }
        throw new Error(message);
      }

      return response.json();
    } catch (error) {
      lastError = error;
      const isNetworkError = error.name === "TypeError" || error.name === "AbortError";
      if (isNetworkError && attempt < MAX_RETRIES - 1) {
        await sleep(INITIAL_RETRY_DELAY_MS * 2 ** attempt);
        continue;
      }
      throw error;
    }
  }

  throw lastError || new Error("Request failed after retries");
}
```

**Explanation:** This helper performs the `request` operation. See the code for the full implementation.

### `getHealth`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `91-93`
- **Purpose:** Retrieves Health.

**Code:**
```javascript
export function getHealth() {
  return request("/health/");
}
```

**Explanation:** This function retrieves Health. See the code for the full implementation.

### `getProtectedMe`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `95-97`
- **Purpose:** Retrieves ProtectedMe.

**Code:**
```javascript
export function getProtectedMe(token) {
  return request("/protected/me", { token });
}
```

**Explanation:** This function retrieves ProtectedMe. See the code for the full implementation.

### `createItem`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `99-105`
- **Purpose:** Builds Item.

**Code:**
```javascript
export function createItem(token, payload) {
  return request("/items/", {
    token,
    method: "POST",
    body: JSON.stringify(payload)
  });
}
```

**Explanation:** This function builds Item. See the code for the full implementation.

### `getEcosim`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `107-128`
- **Purpose:** Retrieves Ecosim.

**Code:**
```javascript
export function getEcosim(params) {
  const search = new URLSearchParams({
    municipality_id: params.municipalityId,
    monthly_consumption: params.monthlyConsumption,
    monthly_bill: params.monthlyBill,
  });
  if (params.desiredSavings !== undefined && params.desiredSavings !== null) {
    search.append("desired_savings", String(params.desiredSavings));
  }
  if (params.includeAi) {
    search.append("include_ai", "true");
  }
  if (params.useRag && params.ragQuery) {
    search.append("use_rag", "true");
    search.append("rag_query", params.ragQuery);
  }
  if (params.mode) {
    search.append("mode", params.mode);
  }

  return request(`/ecosim/?${search.toString()}`);
}
```

**Explanation:** This function retrieves Ecosim. See the code for the full implementation.

### `getMunicipalities`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `130-132`
- **Purpose:** Retrieves Municipalities.

**Code:**
```javascript
export function getMunicipalities() {
  return request("/ecosim/municipalities");
}
```

**Explanation:** This function retrieves Municipalities. See the code for the full implementation.

### `getProvinces`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `134-136`
- **Purpose:** Retrieves Provinces.

**Code:**
```javascript
export function getProvinces() {
  return request("/ecosim/provinces");
}
```

**Explanation:** This function retrieves Provinces. See the code for the full implementation.

### `getProductRecommendations`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `138-142`
- **Purpose:** Retrieves ProductRecommendations.

**Code:**
```javascript
export function getProductRecommendations(energyType, budgetPhp = null, limit = 5) {
  const params = new URLSearchParams({ energy_type: energyType, limit: String(limit) });
  if (budgetPhp) params.append("budget_php", String(budgetPhp));
  return request(`/products/recommend?${params.toString()}`);
}
```

**Explanation:** This function retrieves ProductRecommendations. See the code for the full implementation.

### `browseProducts`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `144-154`
- **Purpose:** Utility function `browseProducts`.

**Code:**
```javascript
export function browseProducts(filters = {}) {
  const params = new URLSearchParams();
  if (filters.category) params.append("category", filters.category);
  if (filters.subcategory) params.append("subcategory", filters.subcategory);
  if (filters.source_site) params.append("source_site", filters.source_site);
  if (filters.min_price) params.append("min_price", String(filters.min_price));
  if (filters.max_price) params.append("max_price", String(filters.max_price));
  params.append("page", String(filters.page || 1));
  params.append("page_size", String(filters.page_size || 20));
  return request(`/products/browse?${params.toString()}`);
}
```

**Explanation:** This helper performs the `browseProducts` operation. See the code for the full implementation.

### `getProductAudit`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `156-158`
- **Purpose:** Retrieves ProductAudit.

**Code:**
```javascript
export function getProductAudit() {
  return request("/products/audit");
}
```

**Explanation:** This function retrieves ProductAudit. See the code for the full implementation.

### `getGeothermal`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `160-162`
- **Purpose:** Retrieves Geothermal.

**Code:**
```javascript
export function getGeothermal(municipalityId) {
  return request(`/geothermal/${municipalityId}`);
}
```

**Explanation:** This function retrieves Geothermal. See the code for the full implementation.

### `runForecast`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `166-175`
- **Purpose:** --- Forecasting ---

**Code:**
```javascript
export function runForecast(metric = "consumption", orderP = 1, orderD = 1, orderQ = 1, forecastTo = 2030) {
  const params = new URLSearchParams({
    metric,
    order_p: String(orderP),
    order_d: String(orderD),
    order_q: String(orderQ),
    forecast_to: String(forecastTo),
  });
  return request(`/forecast/run?${params.toString()}`);
}
```

**Explanation:** This helper performs the `runForecast` operation. See the code for the full implementation.

### `runBacktest`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `177-180`
- **Purpose:** Utility function `runBacktest`.

**Code:**
```javascript
export function runBacktest(metric = "consumption", trainEndYear = 2020) {
  const params = new URLSearchParams({ metric, train_end_year: String(trainEndYear) });
  return request(`/forecast/backtest?${params.toString()}`);
}
```

**Explanation:** This helper performs the `runBacktest` operation. See the code for the full implementation.

### `getModelRuns`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `182-184`
- **Purpose:** Retrieves ModelRuns.

**Code:**
```javascript
export function getModelRuns(limit = 20) {
  return request(`/forecast/models?limit=${limit}`);
}
```

**Explanation:** This function retrieves ModelRuns. See the code for the full implementation.

### `getSuitabilityMap`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `188-190`
- **Purpose:** --- Map / GIS ---

**Code:**
```javascript
export function getSuitabilityMap(renewableType, level = "municipality") {
  return request(`/map/${renewableType}?level=${level}`);
}
```

**Explanation:** This function retrieves SuitabilityMap. See the code for the full implementation.

### `getPsgcHierarchy`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `192-197`
- **Purpose:** Retrieves PsgcHierarchy.

**Code:**
```javascript
export function getPsgcHierarchy(municipalityId = null, provinceId = null) {
  const params = new URLSearchParams();
  if (municipalityId) params.append("municipality_id", String(municipalityId));
  if (provinceId) params.append("province_id", String(provinceId));
  return request(`/map/psgc/hierarchy?${params.toString()}`);
}
```

**Explanation:** This function retrieves PsgcHierarchy. See the code for the full implementation.

### `getCoverageSummary`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `199-201`
- **Purpose:** Retrieves CoverageSummary.

**Code:**
```javascript
export function getCoverageSummary(level = "municipality") {
  return request(`/map/coverage?level=${level}`);
}
```

**Explanation:** This function retrieves CoverageSummary. See the code for the full implementation.

### `runClimateEtl`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `205-207`
- **Purpose:** --- ETL ---

**Code:**
```javascript
export function runClimateEtl() {
  return request("/etl/run/climate", { method: "POST" });
}
```

**Explanation:** This helper performs the `runClimateEtl` operation. See the code for the full implementation.

### `getLineage`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `209-214`
- **Purpose:** Retrieves Lineage.

**Code:**
```javascript
export function getLineage(source = null, table = null, limit = 50) {
  const params = new URLSearchParams({ limit: String(limit) });
  if (source) params.append("source", source);
  if (table) params.append("table", table);
  return request(`/etl/lineage?${params.toString()}`);
}
```

**Explanation:** This function retrieves Lineage. See the code for the full implementation.

### `sendChatMessage`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `218-222`
- **Purpose:** --- Chat ---

**Code:**
```javascript
export function sendChatMessage(message, sessionId = null) {
  const body = { message };
  if (sessionId) body.session_id = sessionId;
  return request("/chat/", { method: "POST", body: JSON.stringify(body) });
}
```

**Explanation:** This helper performs the `sendChatMessage` operation. See the code for the full implementation.

### `getChatSessions`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `224-226`
- **Purpose:** Retrieves ChatSessions.

**Code:**
```javascript
export function getChatSessions() {
  return request("/chat/sessions");
}
```

**Explanation:** This function retrieves ChatSessions. See the code for the full implementation.

### `getChatSessionMessages`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `228-230`
- **Purpose:** Retrieves ChatSessionMessages.

**Code:**
```javascript
export function getChatSessionMessages(sessionId) {
  return request(`/chat/sessions/${sessionId}`);
}
```

**Explanation:** This function retrieves ChatSessionMessages. See the code for the full implementation.

### `getDetailedHealth`

- **File:** `react-frontend/src/services/apiClient.js`
- **Lines:** `234-236`
- **Purpose:** --- Health ---

**Code:**
```javascript
export function getDetailedHealth() {
  return request("/health/detailed");
}
```

**Explanation:** This function retrieves DetailedHealth. See the code for the full implementation.

## `react-frontend/src/services/energyhub.js`

### `getEnergyHubOverview`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `5-7`
- **Purpose:** Retrieves EnergyHubOverview.

**Code:**
```javascript
export function getEnergyHubOverview() {
  return request(`${ENERGYHUB_BASE}/overview`);
}
```

**Explanation:** This function retrieves EnergyHubOverview. See the code for the full implementation.

### `getEnergyHubForecast`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `9-11`
- **Purpose:** Retrieves EnergyHubForecast.

**Code:**
```javascript
export function getEnergyHubForecast(metric = "consumption") {
  return request(`${ENERGYHUB_BASE}/forecast?metric=${encodeURIComponent(metric)}`);
}
```

**Explanation:** This function retrieves EnergyHubForecast. See the code for the full implementation.

### `getEnergyHubTrends`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `13-15`
- **Purpose:** Retrieves EnergyHubTrends.

**Code:**
```javascript
export function getEnergyHubTrends() {
  return request(`${ENERGYHUB_BASE}/trends`);
}
```

**Explanation:** This function retrieves EnergyHubTrends. See the code for the full implementation.

### `getEnergyHubMapData`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `17-21`
- **Purpose:** Retrieves EnergyHubMapData.

**Code:**
```javascript
export function getEnergyHubMapData(metric = "renewable_potential", level = "province") {
  return request(
    `${ENERGYHUB_BASE}/map-data?metric=${encodeURIComponent(metric)}&level=${encodeURIComponent(level)}`
  );
}
```

**Explanation:** This function retrieves EnergyHubMapData. See the code for the full implementation.

### `getEnergyHubSourceBreakdown`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `23-26`
- **Purpose:** Retrieves EnergyHubSourceBreakdown.

**Code:**
```javascript
export function getEnergyHubSourceBreakdown(year) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/source-breakdown${qs}`);
}
```

**Explanation:** This function retrieves EnergyHubSourceBreakdown. See the code for the full implementation.

### `getEnergyHubGridBreakdown`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `28-31`
- **Purpose:** Retrieves EnergyHubGridBreakdown.

**Code:**
```javascript
export function getEnergyHubGridBreakdown(year) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/grid-breakdown${qs}`);
}
```

**Explanation:** This function retrieves EnergyHubGridBreakdown. See the code for the full implementation.

### `getEnergyHubModelComparison`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `33-35`
- **Purpose:** Retrieves EnergyHubModelComparison.

**Code:**
```javascript
export function getEnergyHubModelComparison() {
  return request(`${ENERGYHUB_BASE}/model-comparison`);
}
```

**Explanation:** This function retrieves EnergyHubModelComparison. See the code for the full implementation.

### `getEnergyHubAiInsight`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `37-39`
- **Purpose:** Retrieves EnergyHubAiInsight.

**Code:**
```javascript
export function getEnergyHubAiInsight(useLlm = false) {
  return request(`${ENERGYHUB_BASE}/ai-insight?use_llm=${useLlm}`);
}
```

**Explanation:** This function retrieves EnergyHubAiInsight. See the code for the full implementation.

### `getGeothermalSummary`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `41-43`
- **Purpose:** Retrieves GeothermalSummary.

**Code:**
```javascript
export function getGeothermalSummary() {
  return request("/geothermal/ecohub/geothermal-summary");
}
```

**Explanation:** This function retrieves GeothermalSummary. See the code for the full implementation.

### `getGeothermalPlants`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `45-47`
- **Purpose:** Retrieves GeothermalPlants.

**Code:**
```javascript
export function getGeothermalPlants() {
  return request("/geothermal/plants");
}
```

**Explanation:** This function retrieves GeothermalPlants. See the code for the full implementation.

### `getProvincialDemand`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `49-52`
- **Purpose:** Retrieves ProvincialDemand.

**Code:**
```javascript
export function getProvincialDemand(region = null) {
  const qs = region ? `?region=${encodeURIComponent(region)}` : "";
  return request(`${ENERGYHUB_BASE}/provincial-demand${qs}`);
}
```

**Explanation:** This function retrieves ProvincialDemand. See the code for the full implementation.

### `getIrenaOverview`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `54-56`
- **Purpose:** Retrieves IrenaOverview.

**Code:**
```javascript
export function getIrenaOverview() {
  return request(`${ENERGYHUB_BASE}/irena/overview`);
}
```

**Explanation:** This function retrieves IrenaOverview. See the code for the full implementation.

### `getIrenaCapacity`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `58-61`
- **Purpose:** Retrieves IrenaCapacity.

**Code:**
```javascript
export function getIrenaCapacity(year = null) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/irena/capacity${qs}`);
}
```

**Explanation:** This function retrieves IrenaCapacity. See the code for the full implementation.

### `getIrenaGeneration`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `63-66`
- **Purpose:** Retrieves IrenaGeneration.

**Code:**
```javascript
export function getIrenaGeneration(year = null) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/irena/generation${qs}`);
}
```

**Explanation:** This function retrieves IrenaGeneration. See the code for the full implementation.

### `getIrenaRenewableShare`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `68-70`
- **Purpose:** Retrieves IrenaRenewableShare.

**Code:**
```javascript
export function getIrenaRenewableShare() {
  return request(`${ENERGYHUB_BASE}/irena/renewable-share`);
}
```

**Explanation:** This function retrieves IrenaRenewableShare. See the code for the full implementation.

### `getMeralcoRate`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `72-75`
- **Purpose:** Retrieves MeralcoRate.

**Code:**
```javascript
export function getMeralcoRate(year = null) {
  const qs = year ? `?year=${year}` : "";
  return request(`${ENERGYHUB_BASE}/meralco-rate${qs}`);
}
```

**Explanation:** This function retrieves MeralcoRate. See the code for the full implementation.

### `getSolarAtlas`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `77-80`
- **Purpose:** Retrieves SolarAtlas.

**Code:**
```javascript
export function getSolarAtlas(location = null) {
  const qs = location ? `?location=${encodeURIComponent(location)}` : "";
  return request(`${ENERGYHUB_BASE}/solar-atlas${qs}`);
}
```

**Explanation:** This function retrieves SolarAtlas. See the code for the full implementation.

### `analyzeChart`

- **File:** `react-frontend/src/services/energyhub.js`
- **Lines:** `82-88`
- **Purpose:** Utility function `analyzeChart`.

**Code:**
```javascript
export function analyzeChart(chartType, chartData, forceRefresh = false) {
  const qs = forceRefresh ? "?force_refresh=true" : "";
  return request(`${ENERGYHUB_BASE}/analyze-chart${qs}`, {
    method: "POST",
    body: JSON.stringify({ chart_type: chartType, chart_data: chartData }),
  });
}
```

**Explanation:** This helper performs the `analyzeChart` operation. See the code for the full implementation.

## `react-frontend/src/utils/env.js`

### `getSupabaseUrl`

- **File:** `react-frontend/src/utils/env.js`
- **Lines:** `1-6`
- **Purpose:** Retrieves SupabaseUrl.

**Code:**
```javascript
export function getSupabaseUrl() {
  return (
    import.meta.env.VITE_SUPABASE_URL ||
    "https://husnkzlccdrjpwlqcfbt.supabase.co"
  );
}
```

**Explanation:** This function retrieves SupabaseUrl. See the code for the full implementation.

### `getSupabaseAnonKey`

- **File:** `react-frontend/src/utils/env.js`
- **Lines:** `8-13`
- **Purpose:** Retrieves SupabaseAnonKey.

**Code:**
```javascript
export function getSupabaseAnonKey() {
  return (
    import.meta.env.VITE_SUPABASE_ANON_KEY ||
    "sb_publishable_dth7eXs1Shn6pBPstjr0dQ_wprh2qGR"
  );
}
```

**Explanation:** This function retrieves SupabaseAnonKey. See the code for the full implementation.

### `getApiBaseUrl`

- **File:** `react-frontend/src/utils/env.js`
- **Lines:** `15-32`
- **Purpose:** Retrieves ApiBaseUrl.

**Code:**
```javascript
export function getApiBaseUrl() {
  if (import.meta.env.DEV) {
    return "/api/v1";
  }
  const base = (
    import.meta.env.VITE_API_BASE_URL ||
    "https://lumi-backend-ten.vercel.app"
  )
    .trim()
    .replace(/\/+$/, "");
  if (base.endsWith("/api/v1")) {
    return base;
  }
  if (base.endsWith("/api")) {
    return `${base}/v1`;
  }
  return `${base}/api/v1`;
}
```

**Explanation:** This function retrieves ApiBaseUrl. See the code for the full implementation.

## `react-frontend/src/utils/glossary.js`

### `getGlossary`

- **File:** `react-frontend/src/utils/glossary.js`
- **Lines:** `61-64`
- **Purpose:** Retrieves Glossary.

**Code:**
```javascript
export function getGlossary(term) {
  const normalized = (term || "").toLowerCase().trim();
  return GLOSSARY[normalized] || null;
}
```

**Explanation:** This function retrieves Glossary. See the code for the full implementation.

## `react-frontend/src/utils/regionMap.js`

### `getRegionFromProvince`

- **File:** `react-frontend/src/utils/regionMap.js`
- **Lines:** `58-62`
- **Purpose:** Retrieves RegionFromProvince.

**Code:**
```javascript
export function getRegionFromProvince(provinceName) {
  if (!provinceName) return null;
  const normalized = provinceName.toLowerCase().trim();
  return PROVINCE_TO_REGION[normalized] || null;
}
```

**Explanation:** This function retrieves RegionFromProvince. See the code for the full implementation.

### `getRegionFromMunicipality`

- **File:** `react-frontend/src/utils/regionMap.js`
- **Lines:** `64-75`
- **Purpose:** Retrieves RegionFromMunicipality.

**Code:**
```javascript
export function getRegionFromMunicipality(muniName) {
  if (!muniName) return null;
  // Try common city names that map directly to NCR
  const ncrCities = [
    "manila", "caloocan", "las piñas", "las pinas", "makati", "malabon",
    "mandaluyong", "marikina", "muntinlupa", "navotas", "parañaque", "paranaque",
    "pasay", "pasig", "pateros", "quezon city", "san juan", "taguig", "valenzuela",
  ];
  const normalized = muniName.toLowerCase().trim();
  if (ncrCities.some((c) => normalized.includes(c))) return "NCR";
  return null;
}
```

**Explanation:** This function retrieves RegionFromMunicipality. See the code for the full implementation.
