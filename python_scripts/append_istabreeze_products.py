import argparse
from pathlib import Path
from typing import List, Dict

import pandas as pd


DEFAULT_CLEANED_PATH = (
    Path(__file__).resolve().parents[1]
    / "scraped_data"
    / "output"
    / "cleaned"
    / "cleaned_products_master.csv"
)


def normalize_name(text: str) -> str:
    cleaned = text.lower().strip()
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() or ch in "-" else " " for ch in cleaned)
    cleaned = " ".join(cleaned.split())
    return cleaned


def build_rows() -> List[Dict[str, object]]:
    return [
        {
            "product_name": "IstaBreeze 450plus 12V or 24V wind generator",
            "price_raw": "EUR 360.00",
            "price_value": 360.00,
            "currency": "EUR",
            "energy_category": "wind",
            "energy_subcategory": "turbine",
            "source_site": "istabreeze",
            "source_file": "istabreeze_collection_500w.csv",
            "url": "https://en.istabreeze.store/de-fr/products/windgenerator-istabreeze%C2%AE-air-speed-in-12v-oder-24v",
        },
        {
            "product_name": "IstaBreeze Air-Speed 500W 12V or 24V wind turbine with carbon blades",
            "price_raw": "EUR 290.00",
            "price_value": 290.00,
            "currency": "EUR",
            "energy_category": "wind",
            "energy_subcategory": "turbine",
            "source_site": "istabreeze",
            "source_file": "istabreeze_collection_500w.csv",
            "url": "https://en.istabreeze.store/de-fr/products/istabreeze-airspeed-500w-carbon-buy",
        },
        {
            "product_name": "IstaBreeze i-500 12V or 24V wind turbine",
            "price_raw": "EUR 210.00",
            "price_value": 210.00,
            "currency": "EUR",
            "energy_category": "wind",
            "energy_subcategory": "turbine",
            "source_site": "istabreeze",
            "source_file": "istabreeze_collection_500w.csv",
            "url": "https://en.istabreeze.store/de-fr/products/i500-12v-24v-windkraftanlage",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Append ISTABREEZE products to cleaned dataset.")
    parser.add_argument("--cleaned", type=Path, default=DEFAULT_CLEANED_PATH)
    args = parser.parse_args()

    cleaned_path = args.cleaned
    df = pd.read_csv(cleaned_path, dtype=str)
    columns = list(df.columns)

    new_rows = []
    for row in build_rows():
        full_row = {col: "" for col in columns}
        full_row.update(row)
        full_row["product_name_raw"] = row["product_name"]
        full_row["product_name_normalized"] = normalize_name(row["product_name"])
        full_row.setdefault("ratings", "")
        full_row.setdefault("reviews", "")
        full_row.setdefault("price_note", "")
        full_row.setdefault("rejection_reason", "")
        new_rows.append(full_row)

    combined = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
    combined = combined.drop_duplicates(
        subset=["product_name_normalized", "price_value", "currency", "source_site", "url"],
        keep="first",
    )

    combined.to_csv(cleaned_path, index=False)


if __name__ == "__main__":
    main()
