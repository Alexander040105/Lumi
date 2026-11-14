import csv
import json
import os
import re
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup


# prosolar.ph is a client-rendered Vite/React SPA: GET /shop and /shop/<slug>
# all return the same empty <div id="root"> shell. The full product catalog is
# embedded as a JS array literal inside the site's module bundle (the same data
# the React app renders), so we fetch the live page, follow its bundle script
# tag, and parse the catalog array out of the bundle. No browser needed.

BASE_URL = "https://prosolar.ph"
SHOP_URL = f"{BASE_URL}/shop"
DELAY_SECONDS = 1.0
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CSV_PATH = os.path.join(OUTPUT_DIR, "prosolar_catalog.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "prosolar_catalog.json")

FIELDNAMES = [
    "name", "price", "currency", "url", "source_category", "brand",
    "model_number", "short_description", "description", "specs_json",
    "image_url", "ratings", "reviews", "price_type",
]

CATEGORY_LABELS = {
    "panels": "Solar Panels",
    "inverters": "Inverters",
    "batteries": "Batteries",
}

# Longest first so "Canadian Solar" wins over single-word prefixes.
KNOWN_BRANDS = [
    "Canadian Solar", "Pylontech", "Enphase", "Growatt",
    "LONGi", "Jinko", "Deye", "SMA", "BYD",
]

JS_STRING = r'"((?:[^"\\]|\\.)*)"'
POWER_TOKEN = re.compile(
    r"\b\d+(?:\.\d+)?\s*(?:kwh|kva|kw|wh|ah|w|v)\b", re.IGNORECASE
)
GENERIC_SUFFIXES = (" microinverter", " inverter")


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


def fetch(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.text


def find_bundle_url(shop_html: str) -> str:
    soup = BeautifulSoup(shop_html, "html.parser")
    for script in soup.find_all("script", src=True):
        src = script["src"]
        if re.search(r"/assets/index-.*\.js$", src):
            return src if src.startswith("http") else BASE_URL + src
    raise RuntimeError("module bundle <script> not found in /shop HTML")


def unescape_js_string(value: str) -> str:
    return value.replace('\\"', '"').replace("\\\\", "\\")


def extract_array_literal(js: str) -> str:
    """Return the `[{id:1,...}]` catalog array text, string-aware bracket match."""
    start = js.find('[{id:1,slug:')
    if start == -1:
        raise RuntimeError("catalog array literal not found in bundle")
    depth = 0
    in_str: Optional[str] = None
    escaped = False
    for i in range(start, len(js)):
        ch = js[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", "`"):
                in_str = ch
            elif ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    return js[start:i + 1]
    raise RuntimeError("catalog array literal not terminated")


def split_objects(array_text: str) -> List[str]:
    """Split `[{...},{...}]` into top-level `{...}` chunks, string-aware."""
    objects = []
    depth = 0
    in_str: Optional[str] = None
    escaped = False
    obj_start = -1
    for i, ch in enumerate(array_text):
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", "`"):
                in_str = ch
            elif ch == "{":
                if depth == 0:
                    obj_start = i
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and obj_start != -1:
                    objects.append(array_text[obj_start:i + 1])
    return objects


def first_string(obj: str, key: str) -> str:
    m = re.search(rf"\b{key}:{JS_STRING}", obj)
    return unescape_js_string(m.group(1)) if m else ""


def first_number(obj: str, key: str) -> str:
    m = re.search(rf"\b{key}:([0-9]+(?:\.[0-9]+)?)", obj)
    return m.group(1) if m else ""


def string_list(obj: str, key: str) -> List[str]:
    m = re.search(rf"\b{key}:\[([^\]]*)\]", obj)
    if not m:
        return []
    return [unescape_js_string(s) for s in re.findall(JS_STRING, m.group(1))]


def image_var_map(js: str) -> Dict[str, str]:
    """Map bundle consts like K5="/assets/x.jpg" -> absolute URL."""
    pairs = re.findall(r'\b([A-Za-z_$][\w$]*)="(/assets/[^"]+)"', js)
    return {var: BASE_URL + path for var, path in pairs}


def split_brand_model(name: str) -> tuple:
    for brand in KNOWN_BRANDS:
        if name.startswith(brand + " ") or name == brand:
            model = name[len(brand):].strip()
            break
    else:
        brand, model = "", name
    model = POWER_TOKEN.sub("", model)
    model = re.sub(r"\s+", " ", model).strip(" -")
    lower = model.lower()
    for suffix in GENERIC_SUFFIXES:
        if lower.endswith(suffix):
            model = model[: -len(suffix)].strip(" -")
            break
    return brand, model


def short_description(description: str) -> str:
    sentence = description.split(". ", 1)[0].strip()
    return sentence + "." if sentence and not sentence.endswith(".") else sentence


def parse_product(obj: str, images: Dict[str, str]) -> Optional[Product]:
    slug = first_string(obj, "slug")
    name = first_string(obj, "name")
    if not slug or not name:
        return None
    image_var = re.search(r"\bimage:([A-Za-z_$][\w$]*)", obj)
    image_url = images.get(image_var.group(1), "") if image_var else ""
    brand, model = split_brand_model(name)
    specs = string_list(obj, "specs")
    features = string_list(obj, "features")
    description = first_string(obj, "description")
    specs_json = json.dumps(
        {"specifications": specs, "features": features}, ensure_ascii=False
    )
    return Product(
        name=name,
        price="",
        currency="PHP",
        url=f"{BASE_URL}/shop/{slug}",
        source_category=CATEGORY_LABELS.get(
            first_string(obj, "category"), first_string(obj, "category")
        ),
        brand=brand,
        model_number=model,
        short_description=short_description(description),
        description=description,
        specs_json=specs_json,
        image_url=image_url,
        ratings=first_number(obj, "rating"),
        reviews=first_number(obj, "reviews"),
        price_type="quote",
    )


def save_to_csv(products: List[Product], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        for product in products:
            writer.writerow(asdict(product))


def save_to_json(products: List[Product], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in products], f, ensure_ascii=False, indent=2)


def main() -> None:
    shop_html = fetch(SHOP_URL)
    time.sleep(DELAY_SECONDS)
    bundle_url = find_bundle_url(shop_html)
    bundle_js = fetch(bundle_url)

    images = image_var_map(bundle_js)
    array_text = extract_array_literal(bundle_js)
    objects = split_objects(array_text)

    products: List[Product] = []
    for obj in objects:
        product = parse_product(obj, images)
        if product:
            products.append(product)

    for p in products:
        spec_count = len(json.loads(p.specs_json)["specifications"])
        feat_count = len(json.loads(p.specs_json)["features"])
        print(f"{p.name} | {p.source_category} | specs={spec_count} features={feat_count}")

    save_to_csv(products, CSV_PATH)
    save_to_json(products, JSON_PATH)
    print(f"Saved {len(products)} products to {CSV_PATH} and {JSON_PATH}")

    # Self-check
    assert len(products) >= 8, f"expected >= 8 rows, got {len(products)}"
    assert all(p.price_type == "quote" for p in products)
    assert all(p.url and p.image_url and p.description for p in products)
    print("Self-check passed.")


if __name__ == "__main__":
    main()
