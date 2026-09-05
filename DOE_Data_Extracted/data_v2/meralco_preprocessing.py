"""
Meralco Rates Preprocessing
============================
Parses the Meralco Actual Implemented Rates Excel (2011-2020)
and extracts the Generation Energy Charge per year.

Each sheet is named by year (2011-2020) and contains monthly
breakdowns of generation, transmission, distribution, and other
charges. We extract the Generation Energy Charge as the primary
rate component.

Input: FOI_-_Meralco_Actual_Implemented_Rates_2011-2020_*.xlsx
Output: meralco_rates_2011_2020.csv
"""

from pathlib import Path
import pandas as pd

INPUT_DIR = Path(__file__).resolve().parent / "newDataset"
OUTPUT_DIR = Path(__file__).resolve().parent / "data_v2_preprocessed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _first_numeric(row, start_col=2):
    """Return the first non-null numeric value starting from start_col."""
    for col in range(start_col, len(row)):
        val = row.iloc[col]
        try:
            f = float(val)
            if pd.notna(f) and f > 0:
                return f
        except (ValueError, TypeError):
            continue
    return None


def parse_meralco_rates() -> pd.DataFrame:
    path = list(INPUT_DIR.glob("FOI_-_Meralco_Actual_Implemented_Rates_*.xlsx"))
    if not path:
        raise FileNotFoundError("Meralco Excel not found")
    path = path[0]

    xls = pd.ExcelFile(path)
    items = []

    for sheet in xls.sheet_names:
        try:
            year = int(sheet)
        except ValueError:
            continue

        df = pd.read_excel(xls, sheet_name=sheet, header=None)

        rate = None
        # Strategy 1: look for "Generation Energy Charge" in first 30 rows
        for i in range(min(30, len(df))):
            first = str(df.iloc[i, 0]).lower() if len(df.columns) > 0 else ""
            if "generation energy" in first:
                rate = _first_numeric(df.iloc[i])
                if rate:
                    break

        # Strategy 2: look for "Generation Charge" or similar
        if rate is None:
            for i in range(min(30, len(df))):
                first = str(df.iloc[i, 0]).lower() if len(df.columns) > 0 else ""
                if "generation charge" in first or "generation rate" in first:
                    rate = _first_numeric(df.iloc[i])
                    if rate:
                        break

        # Strategy 3: 2011 sheet has different layout — look for "CCP AVERAGE RATES"
        if rate is None and year == 2011:
            for i in range(min(25, len(df))):
                first = str(df.iloc[i, 0]).lower() if len(df.columns) > 0 else ""
                if "ccp average" in first or "average rates" in first:
                    rate = _first_numeric(df.iloc[i])
                    if rate:
                        break

        if rate is not None:
            items.append({
                "year": year,
                "customer_class": "Residential",
                "rate_php_per_kwh": round(rate, 4),
                "charge_component": "Generation Energy Charge",
                "source_note": "Meralco Actual Implemented Rates (FOI)",
            })
        else:
            print(f"  WARNING: Could not extract rate for year {year}")

    return pd.DataFrame(items)


def main():
    print("Parsing Meralco rates...")
    df = parse_meralco_rates()
    if df.empty:
        print("WARNING: Could not extract any Meralco rates.")
        df = pd.DataFrame(columns=["year", "customer_class", "rate_php_per_kwh", "charge_component", "source_note"])
    df.to_csv(OUTPUT_DIR / "meralco_rates_2011_2020.csv", index=False)
    print(f"  → {len(df)} rows written to {OUTPUT_DIR / 'meralco_rates_2011_2020.csv'}")
    if not df.empty:
        print(df.to_string(index=False))


if __name__ == "__main__":
    main()
