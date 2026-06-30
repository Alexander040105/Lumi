"""
Product Recommendation Service
==============================
Reads cleaned_products_master.csv and provides filtering / recommendation
endpoints for renewable energy products.

Known data quality issues:
- Some hydro products are mis-tagged as "wind" due to scraper categorization
  errors. The _fix_category helper corrects these using the source_file name.
- Products without URLs are excluded from recommendation but included in audit.
"""

from pathlib import Path
import pandas as pd
from fastapi import HTTPException, status

_PRODUCTS_CSV = (
    Path(__file__).resolve().parents[3]
    / "scraped_data"
    / "output"
    / "cleaned"
    / "cleaned_products_master.csv"
)

# Lazy-loaded DataFrame
_products_df: pd.DataFrame | None = None


def _load_products() -> pd.DataFrame:
    global _products_df
    if _products_df is None:
        if not _PRODUCTS_CSV.exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Product dataset not found.",
            )
        _products_df = pd.read_csv(_PRODUCTS_CSV)
        _products_df["price_value"] = pd.to_numeric(_products_df["price_value"], errors="coerce")
        # Fix misclassified categories based on source_file name
        _products_df["energy_category"] = _products_df.apply(_fix_category, axis=1)
    return _products_df


def _fix_category(row: pd.Series) -> str:
    """Correct misclassified categories using source_file hints."""
    cat = str(row.get("energy_category", "")).lower().strip()
    src = str(row.get("source_file", "")).lower()
    if "hydro" in src and cat == "wind":
        return "hydro"
    if "solar" in src and cat != "solar":
        return "solar"
    if "wind" in src and cat != "wind":
        return "wind"
    if "geothermal" in src and cat != "geothermal":
        return "geothermal"
    return cat


def _row_to_dict(row: pd.Series) -> dict:
    """Serialize a product row for API responses."""
    return {
        "product_name": row.get("product_name"),
        "price_value": round(row.get("price_value"), 2) if pd.notna(row.get("price_value")) else None,
        "currency": row.get("currency"),
        "energy_category": row.get("energy_category"),
        "energy_subcategory": row.get("energy_subcategory"),
        "source_site": row.get("source_site"),
        "url": row.get("url"),
        "ratings": row.get("ratings"),
        "reviews": row.get("reviews"),
    }


def get_product_recommendations(energy_type: str, budget_php: float | None = None, limit: int = 5) -> dict:
    """Return top-N matching products for a given renewable energy type."""
    df = _load_products()
    et = energy_type.lower().strip()

    # Map frontend names to CSV categories
    category_map = {
        "solar": "solar",
        "wind": "wind",
        "hydropower": "hydro",
        "hydro": "hydro",
        "geothermal": "geothermal",
    }
    target_cat = category_map.get(et, et)

    filtered = df[df["energy_category"] == target_cat]
    # Only recommend products with valid URLs
    filtered = filtered[filtered["url"].notna() & (filtered["url"].str.strip() != "")]

    if budget_php is not None and budget_php > 0:
        # Rough conversion: assume USD if currency is USD, otherwise use as-is
        def in_php(row):
            val = row["price_value"]
            if pd.isna(val):
                return float("inf")
            curr = str(row.get("currency", "")).upper()
            if "USD" in curr:
                return val * 56.0  # configurable fallback rate
            return val
        filtered = filtered[filtered.apply(lambda r: in_php(r) <= budget_php, axis=1)]

    filtered = filtered.sort_values("price_value", na_position="last").head(limit)
    items = [_row_to_dict(r) for _, r in filtered.iterrows()]

    return {
        "energy_type": energy_type,
        "items": items,
        "count": len(items),
        "note": "Prices converted from USD using PHP 56 = 1 USD when applicable. Links may be outdated; verify before purchase.",
    }


def browse_products(
    category: str | None = None,
    subcategory: str | None = None,
    source_site: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict:
    """Paginated product browser with filters."""
    df = _load_products()

    if category:
        df = df[df["energy_category"] == category.lower().strip()]
    if subcategory:
        df = df[df["energy_subcategory"] == subcategory.lower().strip()]
    if source_site:
        df = df[df["source_site"].str.lower() == source_site.lower().strip()]
    if min_price is not None and min_price > 0:
        df = df[df["price_value"] >= min_price]
    if max_price is not None and max_price > 0:
        df = df[df["price_value"] <= max_price]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = df.iloc[start:end]

    items = [_row_to_dict(r) for _, r in paginated.iterrows()]
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "note": "Prices may be in USD or local currency. Verify links before purchase.",
    }


def get_product_data_audit() -> dict:
    """Return a data quality audit of the scraped product dataset."""
    df = _load_products()
    total = len(df)
    with_url = df["url"].notna() & (df["url"].str.strip() != "")
    without_url = total - with_url.sum()

    # Categorization audit
    hydro_misclassified = len(df[(df["energy_category"] == "wind") & (df["source_file"].str.contains("hydro", case=False, na=False))])
    solar_misclassified = len(df[(df["energy_category"] != "solar") & (df["source_file"].str.contains("solar", case=False, na=False))])

    category_counts = df["energy_category"].value_counts().to_dict()
    source_counts = df["source_site"].value_counts().to_dict()

    return {
        "total_products": total,
        "with_url": int(with_url.sum()),
        "without_url": int(without_url),
        "hydro_misclassified_as_wind": int(hydro_misclassified),
        "solar_misclassified": int(solar_misclassified),
        "category_counts": category_counts,
        "source_counts": source_counts,
        "recommendations": [
            "Fix scraper categorization logic for hydro products (currently tagged as wind).",
            "Add product image and description fields to scraper output.",
            "Verify and update stale marketplace URLs quarterly.",
            "Add availability / stock status scraping.",
        ],
    }
