"""Scraper for solarwarehouse.ph.

The site is a React SPA backed by a public Supabase project; the anon key
below is shipped to every browser and grants read-only SELECT access
(the site owners granted permission to scrape). We query PostgREST
directly instead of scraping the SPA.
"""

import csv
import json
import os
from typing import Dict, List

import requests


SUPABASE_URL = "https://hzlkwfsebkolglibakzd.supabase.co/rest/v1"
ANON_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imh6bGt3ZnNlYmtvbGdsaWJha3pkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3MTI5OTMsImV4cCI6MjA5MTI4ODk5M30."
    "vMVquJbxQe5AMhGbXuU9jTkLGiONaBN77mE2p8qsk4E"
)
HEADERS = {"apikey": ANON_KEY, "Authorization": f"Bearer {ANON_KEY}"}

SITE_BASE = "https://solarwarehouse.ph"
FALLBACK_URL = f"{SITE_BASE}/products"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CSV_PATH = os.path.join(OUTPUT_DIR, "solarwarehouse_catalog.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "solarwarehouse_catalog.json")

FIELDS = [
    "name", "price", "currency", "url", "source_category", "brand",
    "model_number", "short_description", "description", "specs_json",
    "image_url", "ratings", "reviews", "price_type",
]


def get_json(path: str) -> list:
    resp = requests.get(f"{SUPABASE_URL}/{path}", headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_products() -> List[dict]:
    """Approved products with category names embedded via FK join."""
    rows = get_json("products?select=*,product_categories(name)&status=eq.approved")
    return sorted(rows, key=lambda r: (r.get("name") or "", r["id"]))


def url_resolves(url: str) -> bool:
    try:
        return requests.get(
            url, timeout=20, headers={"User-Agent": "Mozilla/5.0"}
        ).status_code == 200
    except requests.RequestException:
        return False


def build_product_url(product: dict, slug_works: bool) -> str:
    slug = product.get("slug")
    if slug and slug_works:
        return f"{SITE_BASE}/p/{slug}"
    return FALLBACK_URL


def format_price(value) -> str:
    if value is None:
        return ""
    try:
        num = float(value)
    except (TypeError, ValueError):
        return ""
    if num == int(num):
        return str(int(num))
    return str(num)


def to_row(product: dict, slug_works: bool) -> Dict[str, str]:
    price_val = product.get("sale_price")
    if price_val is None:
        price_val = product.get("price")
    price = format_price(price_val)
    priced = bool(price) and float(price) > 0

    cat = product.get("product_categories")
    category = (cat or {}).get("name") or product.get("category_id") or ""

    images = product.get("images") or []
    specs = dict(product.get("specifications") or {})
    specs.update({
        "stock_quantity": product.get("stock_quantity"),
        "sku": product.get("sku"),
        "discount_percent": product.get("discount_percent"),
        "supplier_id": product.get("supplier_id"),
    })

    return {
        "name": product.get("name") or "",
        "price": price,
        "currency": "PHP",
        "url": build_product_url(product, slug_works),
        "source_category": category,
        "brand": product.get("brand") or "",
        "model_number": product.get("sku") or "",
        "short_description": product.get("short_description") or "",
        "description": product.get("description") or "",
        "specs_json": json.dumps(specs, ensure_ascii=False, sort_keys=True),
        "image_url": images[0] if images else "",
        # No reviews/ratings tables exposed in the public schema.
        "ratings": "",
        "reviews": "",
        "price_type": "fixed" if priced else "quote",
    }


def save_to_csv(rows: List[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def save_to_json(rows: List[dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def main() -> None:
    products = fetch_products()

    # Verify the /p/<slug> route resolves once, on the first slugged product.
    slug_works = False
    for product in products:
        if product.get("slug"):
            slug_works = url_resolves(f"{SITE_BASE}/p/{product['slug']}")
            break
    print(f"slug URLs resolve: {slug_works}")

    rows = [to_row(p, slug_works) for p in products]

    save_to_csv(rows, CSV_PATH)
    save_to_json(rows, JSON_PATH)

    priced = sum(1 for r in rows if r["price_type"] == "fixed")
    assert len(rows) >= 70, f"expected >=70 rows, got {len(rows)}"
    assert priced >= 0.7 * len(rows), f"only {priced}/{len(rows)} priced"

    print(f"Total rows: {len(rows)} | priced: {priced}")
    for row in rows[:2]:
        print(json.dumps(row, ensure_ascii=False, indent=2))
    print(f"Saved to {CSV_PATH} and {JSON_PATH}")


if __name__ == "__main__":
    main()
