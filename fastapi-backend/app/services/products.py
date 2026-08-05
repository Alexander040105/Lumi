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

import logging
import os
import threading
from pathlib import Path
import pandas as pd
from fastapi import HTTPException, status

from app.services.data_cache import cache_get_sync, cache_set_sync
from app.services.supabase_service import get_supabase_client

logger = logging.getLogger(__name__)

_PRODUCTS_CSV = Path(__file__).resolve().parent / "local_data" / "products.csv"

# Lazy-loaded DataFrame
_products_df: pd.DataFrame | None = None
_products_lock = threading.Lock()


def _load_products() -> pd.DataFrame:
    global _products_df
    with _products_lock:
        if _products_df is not None:
            return _products_df

        cache_key = "products:dataframe"
        cached = cache_get_sync(cache_key)
        if cached is not None:
            _products_df = pd.DataFrame(cached)
            return _products_df

        try:
            client = get_supabase_client()
            resp = client.table("products").select("*").execute()
            rows = resp.data or []
            if rows:
                df = pd.DataFrame(rows)
                df["price_value"] = pd.to_numeric(df["price_value"], errors="coerce")
                df["energy_category"] = df.apply(_fix_category, axis=1)
                cache_set_sync(cache_key, rows, ttl=1800)
                _products_df = df
                return _products_df
        except Exception as exc:
            logger.warning("Failed to load products from Supabase: %s", exc)

        if os.getenv("USE_LOCAL_DATA_FALLBACK", "").lower() == "true" and _PRODUCTS_CSV.exists():
            _products_df = pd.read_csv(_PRODUCTS_CSV)
            _products_df["price_value"] = pd.to_numeric(_products_df["price_value"], errors="coerce")
            _products_df["energy_category"] = _products_df.apply(_fix_category, axis=1)
            return _products_df

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Product dataset not available.",
        )


def _fix_category(row: pd.Series) -> str:
    """Correct misclassified categories using source_file hints."""
    cat = str(row.get("energy_category", "")).lower().strip()
    src = str(row.get("source_file", "")).lower()
    base = src.split("/")[-1].split("\\")[-1]
    # Only override when the source file name explicitly indicates the category
    if base.endswith("_hydro.csv") and cat == "wind":
        return "hydro"
    if base.endswith("_solar.csv") and cat != "solar":
        return "solar"
    if base.endswith("_wind.csv") and cat != "wind":
        return "wind"
    if base.endswith("_geothermal.csv") and cat != "geothermal":
        return "geothermal"
    return cat


def _row_to_dict(row: pd.Series) -> dict:
    """Serialize a product row for API responses."""
    def _clean(val):
        if val is None:
            return None
        try:
            if pd.isna(val):
                return None
        except (TypeError, ValueError):
            pass
        return val

    return {
        "product_name": _clean(row.get("product_name")),
        "price_value": round(row.get("price_value"), 2) if pd.notna(row.get("price_value")) else None,
        "currency": _clean(row.get("currency")),
        "energy_category": _clean(row.get("energy_category")),
        "energy_subcategory": _clean(row.get("energy_subcategory")),
        "source_site": _clean(row.get("source_site")),
        "url": _clean(row.get("url")),
        "ratings": _clean(row.get("ratings")),
        "reviews": _clean(row.get("reviews")),
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

    # Rough conversion: assume USD if currency is USD, otherwise use as-is
    def in_php(row):
        val = row["price_value"]
        if pd.isna(val):
            return float("inf")
        curr = str(row.get("currency", "")).upper()
        if "USD" in curr:
            return val * 56.0  # configurable fallback rate
        return val

    if budget_php is not None and budget_php > 0:
        filtered = filtered[filtered.apply(lambda r: in_php(r) <= budget_php, axis=1)]

    filtered = filtered.copy()
    filtered["price_in_php"] = filtered.apply(in_php, axis=1)
    filtered = filtered.sort_values("price_in_php", na_position="last").head(limit)
    filtered = filtered.drop(columns=["price_in_php"])
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
