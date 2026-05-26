"""Extract kW values from product listing names and write a new CSV.

- Parses kW/W ranges and lists in product_name/product_name_raw.
- Adds a `kw` column with the mean value per row.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd

KW_REGEX = re.compile(r"(?<![a-z0-9])([0-9]+(?:\.[0-9]+)?)\s*(kw|k\s*w)(?![a-z0-9])")
W_REGEX = re.compile(r"(?<![a-z0-9])([0-9]+(?:\.[0-9]+)?)\s*w(?![a-z0-9])")


def extract_kw_values(text: str) -> List[float]:
    """Extract kW values from text. Converts W to kW. Ignores volts-only."""
    values: List[float] = []
    for match in KW_REGEX.finditer(text):
        values.append(float(match.group(1)))
    for match in W_REGEX.finditer(text):
        watts = float(match.group(1))
        values.append(watts / 1000.0)
    return values


def mean_or_none(values: Iterable[float]) -> Optional[float]:
    items = list(values)
    if not items:
        return None
    return sum(items) / len(items)


def compute_kw(row: pd.Series) -> Optional[float]:
    for column in ("product_name", "product_name_raw"):
        value = row.get(column)
        if isinstance(value, str) and value.strip():
            kw_values = extract_kw_values(value.lower())
            if kw_values:
                return mean_or_none(kw_values)
    return None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract kW values from product listings.")
    parser.add_argument(
        "--input",
        default=str(Path("scraped_data") / "output" / "cleaned" / "cleaned_products_master.csv"),
        help="Input CSV path.",
    )
    parser.add_argument(
        "--output",
        default=str(Path("scraped_data") / "output" / "cleaned" / "cleaned_products_master_kw.csv"),
        help="Output CSV path.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    input_path = Path(args.input)
    output_path = Path(args.output)

    df = pd.read_csv(input_path)
    df["kw"] = df.apply(compute_kw, axis=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Wrote {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
