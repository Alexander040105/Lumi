"""Scrape solarmallph.com.ph homepage: spreadsheet pricelist tables + shop product cards."""

import csv
import json
import os
import re
from typing import Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

URL = "https://solarmallph.com.ph/"
PRICELIST_URL = URL + "#pricelist"
SHOP_URL = URL + "#shop"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
CSV_PATH = os.path.join(OUTPUT_DIR, "solarmallph_catalog.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "solarmallph_catalog.json")

FIELDS = [
    "name", "price", "currency", "url", "source_category", "brand",
    "model_number", "short_description", "description", "specs_json",
    "image_url", "ratings", "reviews", "price_type",
]

BRANDS = [
    "Canadian Solar", "Astroenergy", "Lux Power", "LVtopsun", "AE Solar",
    "One Solar", "Growatt", "Enphase", "Pylontech", "Sunnix", "Vinergy",
    "Jinko", "Longi", "Solax", "Solis", "SRNE", "Deye", "SMA", "BYD",
]


def fetch_html(url: str) -> str:
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    resp.raise_for_status()
    return resp.text


def detect_brand(name: str) -> str:
    upper = name.upper()
    for brand in BRANDS:
        if upper.startswith(brand.upper()):
            return brand
    return ""


def parse_price(text: str) -> Tuple[str, str]:
    """Return (numeric price string, price_type). Ranges keep 'low - high'."""
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text or re.search(r"messag|quote|contact|call", text, re.I):
        return "", "quote"
    text = re.sub(r"(?i)price\s*(range)?\s*:", "", text)
    text = re.sub(r"(?i)php|₱", "", text).replace(",", "").strip()
    text = re.sub(r"\s*[-–—]\s*", " - ", text).strip()
    if not re.search(r"\d", text):
        return "", "quote"
    return text, "fixed"


def base_row(**kw) -> Dict[str, str]:
    row = {f: "" for f in FIELDS}
    row.update(kw)
    return row


def scrape_pricelist(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Each pricelist section is an <article> with an <h4> heading and an Item/Details/Price table."""
    rows: List[Dict[str, str]] = []
    section = soup.find(id="pricelist")
    if not section:
        return rows
    for article in section.find_all("article"):
        heading = article.find(["h4", "h3", "h2"])
        category = heading.get_text(strip=True) if heading else "Pricelist"
        table = article.find("table")
        if not table:
            continue
        for tr in table.find_all("tr"):
            tds = tr.find_all("td")
            if len(tds) < 3:
                continue
            name = tds[0].get_text(" ", strip=True)
            details = tds[1].get_text(" ", strip=True)
            price, price_type = parse_price(tds[2].get_text(" ", strip=True))
            if not name:
                continue
            rows.append(base_row(
                name=name,
                price=price,
                currency="PHP",
                url=PRICELIST_URL,
                source_category=category,
                brand=detect_brand(name),
                description=details,
                specs_json=json.dumps({"details": details}, ensure_ascii=False),
                price_type=price_type,
            ))
    return rows


def scrape_shop(soup: BeautifulSoup) -> List[Dict[str, str]]:
    """Shop shelves are <section id='shop-*'> with <article> cards: photo link, name, optional price."""
    rows: List[Dict[str, str]] = []
    shop = soup.find(id="shop")
    if not shop:
        return rows
    for section in shop.find_all("section", id=re.compile(r"^shop-")):
        heading = section.find(["h3", "h4", "h2"])
        category = heading.get_text(strip=True) if heading else "Shop"
        for article in section.find_all("article"):
            h4 = article.find("h4")
            name = h4.get_text(" ", strip=True) if h4 else ""
            if not name:
                continue
            link = article.find("a", href=True)
            img = article.find("img", src=True)
            price_p = article.find("p", class_=re.compile(r"bg-"))
            price, price_type = parse_price(
                price_p.get_text(" ", strip=True) if price_p else ""
            )
            href = link["href"] if link else ""
            src = img["src"] if img else ""
            rows.append(base_row(
                name=name,
                price=price,
                currency="PHP",
                url=requests.compat.urljoin(URL, href) if href else SHOP_URL,
                source_category=category,
                brand=detect_brand(name),
                image_url=requests.compat.urljoin(URL, src),
                price_type=price_type,
            ))
    return rows


def save_to_csv(rows: List[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def save_to_json(rows: List[Dict[str, str]], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)


def main() -> None:
    soup = BeautifulSoup(fetch_html(URL), "html.parser")
    pricelist_rows = scrape_pricelist(soup)
    shop_rows = scrape_shop(soup)
    rows = pricelist_rows + shop_rows

    priced = sum(1 for r in rows if r["price_type"] == "fixed")
    categories = sorted({r["source_category"] for r in rows})
    counts: Dict[str, int] = {}
    for r in rows:
        counts[r["source_category"]] = counts.get(r["source_category"], 0) + 1

    assert len(rows) >= 150, f"too few rows: {len(rows)}"
    assert priced >= 90, f"too few priced rows: {priced}"
    assert len(categories) >= 5, f"too few categories: {categories}"

    save_to_csv(rows, CSV_PATH)
    save_to_json(rows, JSON_PATH)

    print(f"Pricelist rows (A): {len(pricelist_rows)}")
    print(f"Shop rows (B):      {len(shop_rows)}")
    print(f"Total: {len(rows)} | priced: {priced} | quote: {len(rows) - priced}")
    print(f"Categories ({len(categories)}):")
    for cat in categories:
        print(f"  {counts[cat]:3d}  {cat}")
    print("Sample rows:")
    for r in (pricelist_rows[0], pricelist_rows[-1], shop_rows[0]):
        print(" ", json.dumps(r, ensure_ascii=False))
    print(f"Saved {len(rows)} rows to {CSV_PATH} and {JSON_PATH}")


if __name__ == "__main__":
    main()
