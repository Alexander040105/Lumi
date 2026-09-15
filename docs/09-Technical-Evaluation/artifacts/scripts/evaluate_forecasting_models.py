"""Re-execution of the LUMI EnergyHub forecasting model evaluation.

Protocol reproduced from the project docs (ML_MODEL_EVALUATION_SUMMARY.md):
  - Dataset : data/DOE_Data_Extracted/data_v2_preprocessed/master_preprocessed.csv
              (DOE national statistics; this run uses total_consumption_gwh and
              also verifies total_peak_demand_mw and renewable_generation_gwh)
  - Train   : 2003-2020 (n=18)
  - Test    : 2021-2024 (n=4, held out)
  - Models  : Linear Trend, Naive w/ Drift, Holt Linear, ARIMA(1,1,1),
              SARIMAX(1,1,1)+Exog (renewable_share_pct, capacity_margin_pct),
              RandomForest(trend, lag_1)

Unlike the checked-in model_comparison_*.csv (whose SARIMAX / Random Forest
rows are marked "placeholder - model not executed"), every number produced
here comes from an actual fit+predict call in this environment.

Outputs (artifacts/rerun-2026-09-15/ml/):
  model_metrics_consumption.csv / _peak_demand.csv / _renewable.csv
  forecast_vs_actual.csv, residuals_test.csv, cv_expanding_window.csv,
  directional_confusion.csv, aic_grid.csv, robustness_perturbation.csv,
  latency_and_size.json, dm_test.json, summary.json, forecast_plot.png
"""

from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from scipy import stats
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.stats.diagnostic import acorr_ljungbox

warnings.filterwarnings("ignore")

REPO = Path(__file__).resolve().parents[4]
DATA = REPO / "data" / "DOE_Data_Extracted" / "data_v2_preprocessed" / "master_preprocessed.csv"
OUT = REPO / "docs" / "09-Technical-Evaluation" / "artifacts" / "rerun-2026-09-15" / "ml"
OUT.mkdir(parents=True, exist_ok=True)

TRAIN_END = 2020
TEST_YEARS = [2021, 2022, 2023, 2024]
EXOG_COLS = ["renewable_share_pct", "capacity_margin_pct"]


def mape(y_true, y_pred) -> float:
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def metrics(y_true, y_pred) -> dict:
    return {
        "mae": round(float(mean_absolute_error(y_true, y_pred)), 2),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, y_pred))), 2),
        "mape": round(mape(y_true, y_pred), 3),
        "r2": round(float(r2_score(y_true, y_pred)), 4),
    }


def fit_predict_all(train: pd.DataFrame, test: pd.DataFrame, target: str) -> dict:
    """Fit all six models on train[target]; return {name: test predictions}."""
    y = train[target].astype(float).values
    years_train = train["year"].values.reshape(-1, 1)
    years_test = test["year"].values.reshape(-1, 1)
    n_test = len(test)
    preds: dict[str, np.ndarray] = {}
    fit_seconds: dict[str, float] = {}
    fitted = {}

    t0 = time.perf_counter()
    lin = LinearRegression().fit(years_train, y)
    fit_seconds["Linear Trend Regression"] = time.perf_counter() - t0
    fitted["Linear Trend Regression"] = lin
    preds["Linear Trend Regression"] = lin.predict(years_test)

    t0 = time.perf_counter()
    diffs = np.diff(y)
    drift = float(diffs.mean())
    naive = y[-1] + drift * np.arange(1, n_test + 1)
    fit_seconds["Naive with Drift"] = time.perf_counter() - t0
    preds["Naive with Drift"] = naive

    t0 = time.perf_counter()
    holt = ExponentialSmoothing(y, trend="add", damped_trend=False).fit()
    fit_seconds["Holt Linear Smoothing"] = time.perf_counter() - t0
    fitted["Holt Linear Smoothing"] = holt
    preds["Holt Linear Smoothing"] = np.asarray(holt.forecast(n_test))

    t0 = time.perf_counter()
    arima = ARIMA(y, order=(1, 1, 1)).fit()
    fit_seconds["ARIMA(1,1,1)"] = time.perf_counter() - t0
    fitted["ARIMA(1,1,1)"] = arima
    fc = arima.get_forecast(steps=n_test)
    preds["ARIMA(1,1,1)"] = np.asarray(fc.predicted_mean)
    fitted["_arima_ci"] = fc.conf_int(alpha=0.05)

    exog_train = train[EXOG_COLS].astype(float).values
    exog_test = test[EXOG_COLS].astype(float).values
    t0 = time.perf_counter()
    try:
        sar = SARIMAX(y, exog=exog_train, order=(1, 1, 1),
                      enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        fit_seconds["SARIMAX(1,1,1) + Exog"] = time.perf_counter() - t0
        fitted["SARIMAX(1,1,1) + Exog"] = sar
        preds["SARIMAX(1,1,1) + Exog"] = np.asarray(sar.get_forecast(steps=n_test, exog=exog_test).predicted_mean)
    except Exception as exc:  # pragma: no cover - recorded, not hidden
        fit_seconds["SARIMAX(1,1,1) + Exog"] = time.perf_counter() - t0
        fitted["SARIMAX(1,1,1) + Exog"] = f"FAILED: {exc}"
        preds["SARIMAX(1,1,1) + Exog"] = np.full(n_test, np.nan)

    rf_train = train[["year", target]].copy()
    rf_train["trend"] = np.arange(len(rf_train))
    rf_train["lag_1"] = rf_train[target].shift(1)
    rf_train = rf_train.dropna()
    t0 = time.perf_counter()
    rf = RandomForestRegressor(n_estimators=100, random_state=42)
    rf.fit(rf_train[["trend", "lag_1"]].values, rf_train[target].values)
    fit_seconds["Random Forest Regression"] = time.perf_counter() - t0
    fitted["Random Forest Regression"] = rf
    last_val = y[-1]
    rf_preds = []
    for i in range(n_test):
        p = float(rf.predict([[len(train) + i, last_val]])[0])
        rf_preds.append(p)
        last_val = p
    preds["Random Forest Regression"] = np.array(rf_preds)

    fitted["_fit_seconds"] = fit_seconds
    return preds, fitted


def main() -> None:
    df = pd.read_csv(DATA).sort_values("year").reset_index(drop=True)
    print(f"Dataset: {len(df)} rows, years {df.year.min()}-{df.year.max()}, {df.shape[1]} cols")

    targets = {
        "consumption": "total_consumption_gwh",
        "peak_demand": "total_peak_demand_mw",
        "renewable": "renewable_generation_gwh",
    }

    all_metrics: dict[str, list[dict]] = {}
    fitted_main = None
    preds_main: dict[str, np.ndarray] = {}
    test_main = pd.DataFrame()

    for label, col in targets.items():
        train = df[df.year <= TRAIN_END]
        test = df[df.year.isin(TEST_YEARS)]
        y_true = test[col].astype(float).values
        preds, fitted = fit_predict_all(train, test, col)
        rows = []
        for name, y_pred in preds.items():
            if np.isnan(y_pred).all():
                rows.append({"model": name, "mae": None, "rmse": None, "mape": None, "r2": None})
                continue
            m = metrics(y_true, y_pred)
            m["model"] = name
            m["fit_seconds"] = round(fitted["_fit_seconds"].get(name, 0.0), 4)
            rows.append(m)
        all_metrics[label] = rows
        pd.DataFrame(rows)[["model", "mae", "rmse", "mape", "r2", "fit_seconds"]].to_csv(
            OUT / f"model_metrics_{label}.csv", index=False)
        if label == "consumption":
            fitted_main, preds_main, test_main = fitted, preds, test

    # ---- forecast vs actual + residuals (consumption) ----
    y_true = test_main["total_consumption_gwh"].astype(float).values
    fa = pd.DataFrame({"year": test_main.year.values, "actual": y_true})
    for name, y_pred in preds_main.items():
        fa[name] = np.round(y_pred, 1)
        fa[f"{name}__resid"] = np.round(y_true - y_pred, 1)
        fa[f"{name}__pct_err"] = np.round((y_pred - y_true) / y_true * 100, 2)
    fa.to_csv(OUT / "forecast_vs_actual.csv", index=False)

    resid_rows = []
    for name in preds_main:
        e = y_true - preds_main[name]
        for yr, te, pe in zip(test_main.year.values, y_true, preds_main[name]):
            resid_rows.append({"model": name, "year": int(yr), "actual": te,
                               "predicted": round(pe, 1), "residual": round(te - pe, 1),
                               "abs_pct_err": round(abs(te - pe) / te * 100, 2)})
    pd.DataFrame(resid_rows).to_csv(OUT / "residuals_test.csv", index=False)

    # ---- ARIMA diagnostics: coefficients, AIC/BIC, Ljung-Box, PICP ----
    arima = fitted_main["ARIMA(1,1,1)"]
    ci = np.asarray(fitted_main["_arima_ci"])
    picp_hits = sum(1 for i, a in enumerate(y_true) if ci[i, 0] <= a <= ci[i, 1])
    lb = acorr_ljungbox(arima.resid, lags=[5], return_df=True)
    diagnostics = {
        "arima_params": {k: round(float(v), 4) for k, v in
                         zip(getattr(arima, "param_names", [f"p{i}" for i in range(len(arima.params))]),
                             np.atleast_1d(arima.params))},
        "arima_aic": round(float(arima.aic), 2),
        "arima_bic": round(float(arima.bic), 2),
        "ljung_box_lag5": {"lb_stat": round(float(lb.lb_stat.iloc[0]), 3),
                           "p_value": round(float(lb.lb_pvalue.iloc[0]), 4)},
        "picp_95pct_test": f"{picp_hits}/{len(y_true)}",
    }

    # AIC/BIC grid over orders (p,d,q) with d=1
    grid = []
    y_train = df.loc[df.year <= TRAIN_END, "total_consumption_gwh"].astype(float).values
    for p in range(3):
        for q in range(3):
            try:
                m = ARIMA(y_train, order=(p, 1, q)).fit()
                grid.append({"order": f"({p},1,{q})", "aic": round(float(m.aic), 2),
                             "bic": round(float(m.bic), 2)})
            except Exception:
                grid.append({"order": f"({p},1,{q})", "aic": None, "bic": None})
    pd.DataFrame(grid).to_csv(OUT / "aic_grid.csv", index=False)

    # ---- expanding-window CV (consumption): train <=Y, predict Y+1 ----
    cv_rows = []
    for y_end in range(2014, 2021):
        tr = df[df.year <= y_end]
        te = df[df.year == y_end + 1]
        if te.empty:
            continue
        actual = float(te["total_consumption_gwh"].iloc[0])
        tr_y = tr["total_consumption_gwh"].astype(float).values
        fold_preds = {}
        fold_preds["Linear Trend"] = float(LinearRegression()
            .fit(tr.year.values.reshape(-1, 1), tr_y).predict([[y_end + 1]])[0])
        fold_preds["Naive w/ Drift"] = float(tr_y[-1] + np.diff(tr_y).mean())
        try:
            fold_preds["Holt"] = float(ExponentialSmoothing(tr_y, trend="add").fit().forecast(1)[0])
        except Exception:
            fold_preds["Holt"] = np.nan
        try:
            fold_preds["ARIMA(1,1,1)"] = float(ARIMA(tr_y, order=(1, 1, 1)).fit().forecast(1)[0])
        except Exception:
            fold_preds["ARIMA(1,1,1)"] = np.nan
        for name, p in fold_preds.items():
            cv_rows.append({"fold_end": y_end, "predict_year": y_end + 1, "model": name,
                            "actual": actual, "predicted": round(p, 1),
                            "abs_pct_err": round(abs(actual - p) / actual * 100, 3)})
    cv = pd.DataFrame(cv_rows)
    cv.to_csv(OUT / "cv_expanding_window.csv", index=False)
    cv_summary = (cv.groupby("model")["abs_pct_err"]
                    .agg(["count", "mean", "std"]).round(3).reset_index())
    cv_summary.to_csv(OUT / "cv_summary.csv", index=False)

    # ---- directional accuracy (2x2) across CV folds + test years ----
    dir_rows = []
    for _, r in cv[cv.model.isin(["ARIMA(1,1,1)", "Linear Trend"])].iterrows():
        prev_actual = float(df.loc[df.year == r.fold_end, "total_consumption_gwh"].iloc[0])
        dir_rows.append({"model": r.model, "year": int(r.predict_year),
                         "actual_dir": "up" if r.actual > prev_actual else "down",
                         "pred_dir": "up" if r.predicted > prev_actual else "down"})
    test_prev = df[df.year <= TRAIN_END].set_index("year")["total_consumption_gwh"]
    for i, yr in enumerate(TEST_YEARS):
        prev = float(df.loc[df.year == yr - 1, "total_consumption_gwh"].iloc[0])
        actual = y_true[i]
        for name in ["ARIMA(1,1,1)", "Linear Trend Regression"]:
            dir_rows.append({"model": name, "year": yr,
                             "actual_dir": "up" if actual > prev else "down",
                             "pred_dir": "up" if preds_main[name][i] > prev else "down"})
    ddf = pd.DataFrame(dir_rows)
    ddf["correct"] = ddf.actual_dir == ddf.pred_dir
    ddf.to_csv(OUT / "directional_confusion.csv", index=False)
    dir_acc = ddf.groupby("model")["correct"].agg(["sum", "count", "mean"]).round(3)

    # ---- Diebold-Mariano: ARIMA vs Linear Trend on test ----
    e_arima = y_true - preds_main["ARIMA(1,1,1)"]
    e_lin = y_true - preds_main["Linear Trend Regression"]
    d = np.abs(e_arima) - np.abs(e_lin)
    dm_stat = float(d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))) if d.std(ddof=1) > 0 else 0.0
    p_val = float(2 * (1 - stats.norm.cdf(abs(dm_stat))))
    dm = {"comparison": "ARIMA(1,1,1) vs Linear Trend (|error| loss)",
          "dm_stat": round(dm_stat, 3), "p_value_normal_approx": round(p_val, 4),
          "n_test": int(len(d)),
          "caveat": "n=4 -> test has essentially no power; reported for completeness"}
    (OUT / "dm_test.json").write_text(json.dumps(dm, indent=2))

    # ---- robustness: perturb training target with noise, refit ARIMA ----
    rng = np.random.default_rng(42)
    rob_rows = []
    for i in range(30):
        noisy = y_train + rng.normal(0, 0.01 * y_train.std(), len(y_train))
        try:
            m = ARIMA(noisy, order=(1, 1, 1)).fit()
            p = np.asarray(m.forecast(len(y_true)))
            rob_rows.append({"run": i, "mape": round(mape(y_true, p), 3)})
        except Exception:
            rob_rows.append({"run": i, "mape": None})
    rob = pd.DataFrame(rob_rows)
    rob.to_csv(OUT / "robustness_perturbation.csv", index=False)

    # ---- inference latency + serialized size ----
    lat = {}
    t0 = time.perf_counter()
    for _ in range(100):
        arima.forecast(6)
    lat["arima_forecast6_ms_mean"] = round((time.perf_counter() - t0) / 100 * 1000, 3)
    rf = fitted_main["Random Forest Regression"]
    t0 = time.perf_counter()
    for _ in range(100):
        rf.predict([[18, y_train[-1]]])
    lat["rf_predict_ms_mean"] = round((time.perf_counter() - t0) / 100 * 1000, 3)
    tmp = OUT / "_tmp_arima.joblib"
    joblib.dump(arima, tmp)
    arima_size = tmp.stat().st_size
    tmp2 = OUT / "_tmp_rf.joblib"
    joblib.dump(rf, tmp2)
    rf_size = tmp2.stat().st_size
    tmp.unlink(); tmp2.unlink()
    lat["arima_joblib_bytes"] = arima_size
    lat["rf_joblib_bytes"] = rf_size
    lat["fit_seconds_consumption"] = fitted_main["_fit_seconds"]
    (OUT / "latency_and_size.json").write_text(json.dumps(lat, indent=2))

    # ---- summary ----
    summary = {
        "dataset": {"rows": int(len(df)), "years": [int(df.year.min()), int(df.year.max())],
                    "train": f"2003-{TRAIN_END} (n={int((df.year <= TRAIN_END).sum())})",
                    "test": f"{TEST_YEARS[0]}-{TEST_YEARS[-1]} (n={len(TEST_YEARS)})"},
        "consumption_metrics": all_metrics["consumption"],
        "arima_diagnostics": diagnostics,
        "cv_summary_mape": cv_summary.to_dict(orient="records"),
        "directional_accuracy": dir_acc.reset_index().to_dict(orient="records"),
        "dm_test": dm,
        "robustness_mape": {"n_runs": int(rob.mape.notna().sum()),
                            "mean": round(float(rob.mape.mean()), 3),
                            "std": round(float(rob.mape.std()), 3),
                            "min": round(float(rob.mape.min()), 3),
                            "max": round(float(rob.mape.max()), 3)},
        "latency_size": lat,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))

    # ---- plot ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(11, 6))
    plt.plot(df.year, df.total_consumption_gwh, "o-", color="black", label="Actual (DOE)")
    plt.axvspan(2020.5, 2024.5, color="grey", alpha=0.12, label="Held-out test period")
    fy = np.array(TEST_YEARS)
    for name, color in zip(["Linear Trend Regression", "ARIMA(1,1,1)", "Random Forest Regression"],
                           ["tab:blue", "tab:red", "tab:green"]):
        plt.plot(fy, preds_main[name], "o--", label=name, color=color, alpha=0.85)
    plt.plot(fy, ci[:, 0], ":", color="tab:red", alpha=0.6)
    plt.plot(fy, ci[:, 1], ":", color="tab:red", alpha=0.6, label="ARIMA 95% PI")
    plt.xlabel("Year"); plt.ylabel("Total consumption (GWh)")
    plt.title("LUMI EnergyHub - held-out test forecasts vs actual (2021-2024)")
    plt.legend(fontsize=8); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(OUT / "forecast_plot.png", dpi=150)

    print(json.dumps(summary["consumption_metrics"], indent=1))
    print("\nCV summary (abs pct err):"); print(cv_summary.to_string(index=False))
    print("\nDirectional accuracy:"); print(dir_acc.to_string())
    print("\nDM:", dm)
    print("\nRobustness MAPE:", summary["robustness_mape"])
    print("\nLatency/size:", lat)
    print("\nARIMA diagnostics:", diagnostics)


if __name__ == "__main__":
    main()
