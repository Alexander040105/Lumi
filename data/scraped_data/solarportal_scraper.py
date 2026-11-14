import csv
import json
import os
import re
import time
from collections import Counter
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

import requests


BASE_URL = "https://solarportal.store"
PRODUCTS_PAGE_URL = f"{BASE_URL}/products"

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CSV_PATH = os.path.join(OUTPUT_DIR, "solarportal_catalog.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "solarportal_catalog.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}
POLITENESS_DELAY = 1.0  # seconds between HTTP calls
REQUEST_TIMEOUT = 30

FIELDS = [
    "name", "price", "currency", "url", "source_category", "brand",
    "model_number", "short_description", "description", "specs_json",
    "image_url", "ratings", "reviews", "price_type",
]


@dataclass
class Product:
    name: str
    price: str
    currency: str
    url: str
    source_category: str
    brand: str
    model_number: str
    short_description: str
    description: str
    specs_json: str
    image_url: str
    ratings: str
    reviews: str
    price_type: str


def fetch(url: str) -> requests.Response:
    time.sleep(POLITENESS_DELAY)
    response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response


def discover_app_id() -> str:
    html = fetch(PRODUCTS_PAGE_URL).text
    bundle_paths = re.findall(r'src="(/assets/index-[^"]+\.js)"', html)
    if not bundle_paths:
        raise RuntimeError("Could not find JS bundle path on products page")
    bundle = fetch(BASE_URL + bundle_paths[0]).text
    candidates = Counter(re.findall(r"[0-9a-f]{24}", bundle))
    if not candidates:
        raise RuntimeError("Could not find app_id in JS bundle")
    app_id, count = candidates.most_common(1)[0]
    print(f"Discovered app_id={app_id} (appears {count}x in bundle)")
    return app_id


def fetch_products(app_id: str) -> List[Dict]:
    url = f"{BASE_URL}/api/apps/{app_id}/entities/Product"
    data = fetch(url).json()
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected entities response: {type(data)}")
    return data


def detail_url_scheme(bundle_html: Optional[str] = None) -> Optional[str]:
    # The SPA router declares /products/:id, so deep links resolve client-side.
    # Verified by checking the bundle for the route pattern; server returns the
    # same shell for all paths, so an HTTP probe cannot distinguish routes.
    try:
        html = fetch(PRODUCTS_PAGE_URL).text
        bundle_paths = re.findall(r'src="(/assets/index-[^"]+\.js)"', html)
        if bundle_paths:
            bundle = fetch(BASE_URL + bundle_paths[0]).text
            if "/products/:id" in bundle:
                return BASE_URL + "/products/{id}"
    except Exception:
        pass
    return None


def build_product(raw: Dict, url_scheme: Optional[str]) -> Optional[Product]:
    if not raw.get("active"):
        return None

    name = (raw.get("name") or "").strip()
    if not name:
        return None

    retail = raw.get("retail_price")
    try:
        price_value = float(retail)
    except (TypeError, ValueError):
        price_value = 0.0
    price = f"{price_value:.2f}"
    price_type = "fixed" if price_value > 0 else "quote"

    images = raw.get("images") or []
    image_url = images[0] if images else ""

    specs = {
        "specifications": raw.get("specifications"),
        "rated_power": raw.get("rated_power"),
        "voltage": raw.get("voltage"),
        "warranty": raw.get("warranty"),
        "datasheet_url": raw.get("datasheet_url"),
        "dealer_price": raw.get("dealer_price"),
        "wholesale_price": raw.get("wholesale_price"),
        "sku": raw.get("sku"),
    }

    if url_scheme:
        url = url_scheme.format(id=raw.get("id"))
    else:
        url = PRODUCTS_PAGE_URL

    return Product(
        name=name,
        price=price,
        currency="PHP",
        url=url,
        source_category=raw.get("category") or "",
        brand=raw.get("brand") or "",
        model_number=raw.get("model_number") or "",
        short_description=raw.get("short_description") or "",
        description=raw.get("full_description") or "",
        specs_json=json.dumps(specs, ensure_ascii=False),
        image_url=image_url,
        ratings="",
        reviews="",
        price_type=price_type,
    )


def save_to_csv(products: List[Product], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for product in products:
            writer.writerow(asdict(product))


def save_to_json(products: List[Product], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in products], f, ensure_ascii=False, indent=2)


def main() -> None:
    app_id = discover_app_id()
    url_scheme = detail_url_scheme()
    print(f"Per-product URL scheme: {url_scheme or 'none found, using listing URL'}")

    raw_products = fetch_products(app_id)
    print(f"Fetched {len(raw_products)} raw products")

    products: List[Product] = []
    for raw in raw_products:
        product = build_product(raw, url_scheme)
        if product:
            products.append(product)

    # Deterministic order: API order is stable, but sort by name for safety.
    products.sort(key=lambda p: p.name.lower())

    priced = sum(1 for p in products if p.price_type == "fixed")
    print(f"Rows kept (active): {len(products)} | priced (fixed): {priced}")

    # Self-check
    assert len(products) >= 50, f"Expected >= 50 rows, got {len(products)}"
    assert priced / len(products) >= 0.8, f"Priced ratio {priced}/{len(products)} < 80%"

    save_to_csv(products, CSV_PATH)
    save_to_json(products, JSON_PATH)
    print(f"Saved {len(products)} products to {CSV_PATH} and {JSON_PATH}")

    print("\nSample rows:")
    for p in products[:2]:
        print(json.dumps(asdict(p), ensure_ascii=False, indent=2))

    print("\nCategory distribution:")
    for cat, count in Counter(p.source_category for p in products).most_common():
        print(f"  {count:3d}  {cat}")


if __name__ == "__main__":
    main()
