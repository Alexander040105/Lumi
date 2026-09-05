"""
IRENA Data Preprocessing
=========================
Parses IRENA capacity, generation, and renewable share statistics
into clean CSVs for LUMI EnergyHub benchmarking layer.

Input files (from newDataset/IRENA/):
- C-ELECCAP_*.csv     → Country-level electricity capacity by technology
- C-ELECGEN_*.csv     → Country-level electricity generation by technology
- R-ELECGEN_*.csv     → Regional (Asia) generation data
- RESHARE_*.xlsx      → Renewable share of electricity generation (%)

Output files (to data_v2_preprocessed/):
- irena_ph_capacity_by_tech.csv
- irena_ph_generation_by_tech.csv
- irena_asia_generation.csv
- irena_renewable_share.csv
"""

from pathlib import Path
import pandas as pd

INPUT_DIR = Path(__file__).resolve().parent / "newDataset" / "IRENA"
OUTPUT_DIR = Path(__file__).resolve().parent / "data_v2_preprocessed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _find_file(pattern: str) -> Path | None:
    matches = list(INPUT_DIR.glob(pattern))
    return matches[0] if matches else None


def parse_capacity() -> pd.DataFrame:
    path = _find_file("C-ELECCAP_*.csv")
    if not path:
        raise FileNotFoundError("Capacity CSV not found")
    df = pd.read_csv(path, skiprows=2)
    df = df.rename(columns={
        "Country/area": "country",
        "Technology": "technology",
        "Grid connection": "grid_connection",
        "Year": "year",
        "Electricity capacity statistics": "capacity_mw",
    })
    # Filter Philippines only
    df = df[df["country"].str.contains("Philippines", case=False, na=False)]
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["capacity_mw"] = pd.to_numeric(df["capacity_mw"], errors="coerce")
    df = df.dropna(subset=["year", "capacity_mw"])
    df = df.sort_values(["technology", "year"])
    return df[["technology", "grid_connection", "year", "capacity_mw"]]


def parse_generation() -> pd.DataFrame:
    path = _find_file("C-ELECGEN_*.csv")
    if not path:
        raise FileNotFoundError("Generation CSV not found")
    df = pd.read_csv(path, skiprows=2)
    df = df.rename(columns={
        "Country/area": "country",
        "Technology": "technology",
        "Data Type": "data_type",
        "Grid connection": "grid_connection",
        "Year": "year",
        "Electricity generation statistics": "generation_gwh",
    })
    # Filter Philippines only, remove "All" grid to avoid double-counting
    df = df[df["country"].str.contains("Philippines", case=False, na=False)]
    df = df[df["grid_connection"] != "All"]
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["generation_gwh"] = pd.to_numeric(df["generation_gwh"], errors="coerce")
    df = df.dropna(subset=["year", "generation_gwh"])
    df = df.sort_values(["technology", "grid_connection", "year"])
    return df[["technology", "grid_connection", "year", "generation_gwh"]]


def parse_regional_generation() -> pd.DataFrame:
    path = _find_file("R-ELECGEN_*.csv")
    if not path:
        raise FileNotFoundError("Regional generation CSV not found")
    df = pd.read_csv(path, skiprows=2)
    df = df.rename(columns={
        "Region": "region",
        "Technology": "technology",
        "Data Type": "data_type",
        "Year": "year",
        "Electricity generation statistics": "generation_gwh",
    })
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["generation_gwh"] = pd.to_numeric(df["generation_gwh"], errors="coerce")
    df = df.dropna(subset=["year", "generation_gwh"])
    df = df.sort_values(["region", "technology", "year"])
    return df[["region", "technology", "year", "generation_gwh"]]


def parse_renewable_share() -> pd.DataFrame:
    path = _find_file("RESHARE_*.xlsx")
    if not path:
        raise FileNotFoundError("Renewable share XLSX not found")
    df = pd.read_excel(path, header=None)
    # First row after header is country name, then year/value pairs
    # Row 0: NaN, NaN, NaN, NaN
    # Row 1: Country, Indicator, Year, Value
    # Data starts from row 1
    df = df.iloc[1:].reset_index(drop=True)
    df.columns = ["country", "indicator", "year", "renewable_share_pct"]
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["renewable_share_pct"] = pd.to_numeric(df["renewable_share_pct"], errors="coerce")
    df = df.dropna(subset=["year", "renewable_share_pct"])
    df = df.sort_values("year")
    return df[["year", "renewable_share_pct"]]


def main():
    print("Parsing IRENA capacity...")
    cap = parse_capacity()
    cap.to_csv(OUTPUT_DIR / "irena_ph_capacity_by_tech.csv", index=False)
    print(f"  → {len(cap)} rows, {cap['technology'].nunique()} technologies")

    print("Parsing IRENA generation...")
    gen = parse_generation()
    gen.to_csv(OUTPUT_DIR / "irena_ph_generation_by_tech.csv", index=False)
    print(f"  → {len(gen)} rows, {gen['technology'].nunique()} technologies")

    print("Parsing IRENA regional generation...")
    reg = parse_regional_generation()
    reg.to_csv(OUTPUT_DIR / "irena_asia_generation.csv", index=False)
    print(f"  → {len(reg)} rows, region={reg['region'].unique()}")

    print("Parsing IRENA renewable share...")
    share = parse_renewable_share()
    share.to_csv(OUTPUT_DIR / "irena_renewable_share.csv", index=False)
    print(f"  → {len(share)} rows, years {share['year'].min()}-{share['year'].max()}")

    print("\nAll IRENA files written to", OUTPUT_DIR)


if __name__ == "__main__":
    main()
