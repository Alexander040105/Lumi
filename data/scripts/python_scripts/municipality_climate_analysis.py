# pip install pandas matplotlib python-dotenv supabase
#
# .env example:
# SUPABASE_URL=your_supabase_url
# SUPABASE_KEY=your_supabase_key

# =========================
# IMPORTS
# =========================
import os
import re
import sys
from typing import List, Dict, Any
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import httpx
from supabase import create_client, Client


# =========================
# CONSTANTS AND CONFIG
# =========================
TABLE_NAME = "municipality_climate_monthly"
PAGE_SIZE = 1000
OUTPUT_CSV = "municipality_climate_averages.csv"

NASA_POWER_COLUMNS = [
    "t2m",
    "t2m_max",
    "t2m_min",
    "rh2m",
    "rhoa",
    "prectotcorr",
    "ws10m",
    "allsky_sfc_sw_dwn",
    "cloud_amt",
    "surface_pressure",
]

ELEVATION_COLUMN = "elevation"
JWT_PATTERN = re.compile(r"^[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*$")


# =========================
# ENVIRONMENT SETUP
# =========================
def load_env() -> Dict[str, str]:
    """Load required environment variables."""
    repo_root = Path(__file__).resolve().parents[1]
    load_dotenv(dotenv_path=repo_root / ".env", override=False)
    print(f"Loaded environment variables from: {repo_root / '.env'}")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = None
    for key_name in (
        "SUPABASE_JWT_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_JWT_ANON_KEY",
        "SUPABASE_ANON_KEY",
        "SUPABASE_KEY",
    ):
        value = os.getenv(key_name)
        if value:
            supabase_key = value
            break

    if not supabase_url or not supabase_key:
        raise EnvironmentError(
            "Missing SUPABASE_URL or SUPABASE_KEY. Add them to your .env file."
        )

    return {"SUPABASE_URL": supabase_url, "SUPABASE_KEY": supabase_key}


def is_jwt_key(key: str | None) -> bool:
    return bool(key) and JWT_PATTERN.match(key) is not None


class SupabaseRestQuery:
    def __init__(self, client: "SupabaseRestClient", table: str):
        self._client = client
        self._table = table
        self._select = "*"
        self._filters: list[tuple[str, str]] = []

    def select(self, columns: str = "*") -> "SupabaseRestQuery":
        self._select = columns
        return self

    def range(self, start: int, end: int) -> "SupabaseRestQuery":
        self._range = (start, end)
        return self

    def execute(self):
        params: dict[str, str] = {"select": self._select}
        headers = dict(self._client.headers)
        if hasattr(self, "_range"):
            start, end = self._range
            headers["Range"] = f"{start}-{end}"
        url = f"{self._client.base_url}/rest/v1/{self._table}"
        response = self._client.http.get(url, params=params, headers=headers)
        response.raise_for_status()
        return type("Resp", (), {"data": response.json()})


class SupabaseRestClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "apikey": api_key,
            "Authorization": f"Bearer {api_key}",
        }
        self.http = httpx.Client(timeout=10.0)

    def table(self, table_name: str) -> SupabaseRestQuery:
        return SupabaseRestQuery(self, table_name)


# =========================
# SUPABASE CLIENT
# =========================
def get_supabase_client() -> Client:
    """Initialize and return a Supabase client."""
    env = load_env()
    if is_jwt_key(env["SUPABASE_KEY"]):
        try:
            return create_client(env["SUPABASE_URL"], env["SUPABASE_KEY"])
        except Exception:
            return SupabaseRestClient(env["SUPABASE_URL"], env["SUPABASE_KEY"])
    return SupabaseRestClient(env["SUPABASE_URL"], env["SUPABASE_KEY"])


# =========================
# DATA FETCHING WITH PAGINATION
# =========================
def fetch_all_rows(supabase: Client, table_name: str) -> List[Dict[str, Any]]:
    """Fetch all rows from a Supabase table using pagination."""
    all_rows: List[Dict[str, Any]] = []
    start = 0

    while True:
        end = start + PAGE_SIZE - 1
        try:
            response = (
                supabase
                .table(table_name)
                .select("*")
                .range(start, end)
                .execute()
            )
        except Exception as exc:
            raise RuntimeError(f"Supabase API request failed: {exc}") from exc

        data = response.data if response and response.data else []

        if not data:
            break

        all_rows.extend(data)
        start += PAGE_SIZE

        # Safety guard against unexpected pagination issues
        if start > 10_000_000:
            raise RuntimeError("Pagination exceeded safe limit. Check table size or API response.")

    if not all_rows:
        raise ValueError("No data returned from Supabase. Check table name and credentials.")

    return all_rows


# =========================
# DATA VALIDATION AND CLEANING
# =========================
def validate_dataframe(df: pd.DataFrame) -> None:
    """Basic validation checks for expected columns and non-empty data."""
    if df.empty:
        raise ValueError("DataFrame is empty. No data to analyze.")

    missing_cols = [col for col in NASA_POWER_COLUMNS + ["municipality_id"] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}")


# =========================
# EXPLORATORY DATA ANALYSIS
# =========================
def summarize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Return a summary of missing values by column."""
    missing_counts = df.isna().sum().sort_values(ascending=False)
    missing_percent = (missing_counts / len(df) * 100).round(2)
    return pd.DataFrame({
        "missing_count": missing_counts,
        "missing_percent": missing_percent
    })


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics for numeric NASA POWER columns."""
    return df[NASA_POWER_COLUMNS].describe().T


# =========================
# VISUALIZATION EXAMPLES
# =========================
def plot_histogram(df: pd.DataFrame, column: str) -> None:
    """Plot a histogram for a single column."""
    plt.figure(figsize=(8, 4))
    plt.hist(df[column].dropna(), bins=30, color="#2E86AB", alpha=0.85)
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.show()


def plot_boxplot(df: pd.DataFrame, column: str) -> None:
    """Plot a boxplot for a single column."""
    plt.figure(figsize=(6, 4))
    plt.boxplot(df[column].dropna(), vert=True)
    plt.title(f"Boxplot of {column}")
    plt.ylabel(column)
    plt.tight_layout()
    plt.show()


def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    """Plot a correlation heatmap using matplotlib."""
    corr = df[NASA_POWER_COLUMNS].corr()
    plt.figure(figsize=(10, 8))
    plt.imshow(corr, cmap="coolwarm", interpolation="nearest")
    plt.colorbar()
    plt.xticks(range(len(corr.columns)), corr.columns, rotation=45, ha="right")
    plt.yticks(range(len(corr.columns)), corr.columns)
    plt.title("Correlation Heatmap: NASA POWER Parameters")
    plt.tight_layout()
    plt.show()


def plot_municipality_distribution(df: pd.DataFrame, column: str, sample_size: int = 10) -> None:
    """Plot a distribution of values for a subset of municipalities."""
    sample_ids = df["municipality_id"].dropna().unique()[:sample_size]
    plt.figure(figsize=(10, 5))
    for municipality_id in sample_ids:
        subset = df[df["municipality_id"] == municipality_id][column].dropna()
        plt.plot(subset.values, label=f"{municipality_id}")
    plt.title(f"{column} Distribution (Sample Municipalities)")
    plt.xlabel("Record Index")
    plt.ylabel(column)
    plt.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.show()


# =========================
# AGGREGATION LOGIC
# =========================
def compute_all_time_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Compute all-time averages per municipality for NASA POWER parameters."""
    if ELEVATION_COLUMN not in df.columns:
        df[ELEVATION_COLUMN] = pd.NA

    avg_df = (
        df.groupby("municipality_id")[NASA_POWER_COLUMNS]
        .mean(numeric_only=True)
        .reset_index()
    )

    elevation_df = (
        df[["municipality_id", ELEVATION_COLUMN]]
        .dropna(subset=[ELEVATION_COLUMN])
        .drop_duplicates(subset=["municipality_id"])
        .rename(columns={ELEVATION_COLUMN: "elevation"})
    )

    merged = avg_df.merge(elevation_df, on="municipality_id", how="left")
    if "elevation" not in merged.columns:
        merged["elevation"] = pd.NA

    return merged.rename(columns={
        "t2m": "avg_t2m",
        "t2m_max": "avg_t2m_max",
        "t2m_min": "avg_t2m_min",
        "rh2m": "avg_rh2m",
        "rhoa": "avg_rhoa",
        "prectotcorr": "avg_prectotcorr",
        "ws10m": "avg_ws10m",
        "allsky_sfc_sw_dwn": "avg_allsky_sfc_sw_dwn",
        "cloud_amt": "avg_cloud_amt",
        "surface_pressure": "avg_surface_pressure",
    })


# =========================
# DOMAIN NOTES (COMMENTARY)
# =========================
# NASA POWER parameter meanings:
# - t2m: Mean air temperature at 2 meters (C)
# - t2m_max: Maximum air temperature at 2 meters (C)
# - t2m_min: Minimum air temperature at 2 meters (C)
# - rh2m: Relative humidity at 2 meters (%)
# - prectotcorr: Corrected total precipitation
# - ws10m: Wind speed at 10 meters (m/s)
# - allsky_sfc_sw_dwn: Solar irradiance at surface (energy)
# - cloud_amt: Cloud amount or fraction
# - surface_pressure: Surface pressure
#
# Why historical averaging matters (2018-2025):
# - Reduces the impact of short-term anomalies
# - Builds stable baselines for long-term energy planning
# - Provides consistent signals for AI models and scoring systems
#
# How LUMI can use the averages:
# - Solar suitability: high avg_allsky_sfc_sw_dwn, lower avg_cloud_amt
# - Wind suitability: high avg_ws10m
# - Hydro or resilience modeling: precipitation and temperature stability


# =========================
# MAIN WORKFLOW
# =========================
def main() -> None:
    """Main execution flow."""
    try:
        supabase = get_supabase_client()
        rows = fetch_all_rows(supabase, TABLE_NAME)
    except Exception as exc:
        print(f"Error loading data: {exc}")
        sys.exit(1)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    # Data validation
    try:
        validate_dataframe(df)
    except Exception as exc:
        print(f"Validation error: {exc}")
        sys.exit(1)

    # Basic EDA
    print("Shape:", df.shape)
    print("Columns:", df.columns.tolist())
    print("\nMissing Values:\n", summarize_missing_values(df).head(15))
    print("\nDescriptive Statistics:\n", descriptive_statistics(df).head(15))

    # Visualization examples
    plot_histogram(df, "t2m")
    plot_boxplot(df, "t2m")
    plot_correlation_heatmap(df)
    plot_municipality_distribution(df, "t2m")

    # Compute all-time averages
    avg_df = compute_all_time_averages(df)

    # Save output
    avg_df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved averages to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
