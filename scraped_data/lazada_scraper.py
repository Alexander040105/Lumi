import csv
import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Set

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv


SEARCH_URL = "https://www.lazada.com.ph/catalog/?q=solar%20panel"

load_dotenv(override=True)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
RUNTIME_DIR = os.path.join(os.path.dirname(__file__), "runtime")
CSV_PATH = os.path.join(OUTPUT_DIR, "lazada_products_solar_panel.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "lazada_products_solar_panel.json")


@dataclass
class Product:
    name: str
    price: str
    ratings: str
    url: str


CARD_SELECTORS = [
    "div[data-qa-locator='product-item']",
    "div[data-qa-locator='product-item'] div[data-qa-locator='product-card']"
]

NAME_SELECTORS = [
    "a[title]",
    "a[title] span"
]

PRICE_SELECTORS = [
    "span[data-qa-locator='product-item-price']",
    "div[data-qa-locator='product-item-price'] span",
    "div.aBrP0 span.ooOxS",
    "span.ooOxS",
    "span[class*='price']",
    "span[class*='Price']",
    "span[class*='current-price']"
]

PRICE_ATTR_SELECTORS = [
    "[data-price]",
    "[data-spm-price]",
    "meta[itemprop='price']"
]

RATING_SELECTORS = [
    "span[data-qa-locator='rating']",
    "span[class*='rating']"
]

LINK_SELECTORS = [
    "a[title]"
]


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    profile_dir = os.path.join(RUNTIME_DIR, "profile")
    cache_dir = os.path.join(RUNTIME_DIR, "cache")
    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument(f"--disk-cache-dir={cache_dir}")

    if headless:
        options.add_argument("--headless=new")

    driver_path = os.getenv("CHROMEDRIVER_PATH")
    chrome_binary = os.getenv("CHROME_BINARY")
    brave_binary = os.getenv("BRAVE_BINARY")
    if brave_binary:
        options.binary_location = brave_binary
    elif chrome_binary:
        options.binary_location = chrome_binary

    service = Service(driver_path) if driver_path else Service()
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(60)
    return driver


def safe_find_text(card, selectors: List[str]) -> str:
    for selector in selectors:
        try:
            element = card.find_element(By.CSS_SELECTOR, selector)
            text = element.text.strip()
            if text:
                return text
        except Exception:
            continue
    return ""


def safe_find_attr(card, selectors: List[str], attr: str) -> str:
    for selector in selectors:
        try:
            element = card.find_element(By.CSS_SELECTOR, selector)
            value = element.get_attribute(attr)
            if value:
                return value.strip()
        except Exception:
            continue
    return ""


def extract_price(card) -> str:
    price = safe_find_text(card, PRICE_SELECTORS)
    if price:
        return price
    for selector in PRICE_ATTR_SELECTORS:
        try:
            element = card.find_element(By.CSS_SELECTOR, selector)
        except Exception:
            continue
        for attr in ("data-price", "data-spm-price", "content"):
            value = element.get_attribute(attr)
            if value:
                return value.strip()
    return ""


def scrape_product_card(card) -> Optional[Product]:
    name = safe_find_text(card, NAME_SELECTORS)
    price = extract_price(card)
    ratings = safe_find_text(card, RATING_SELECTORS)
    url = safe_find_attr(card, LINK_SELECTORS, "href")

    if not name:
        return None

    return Product(
        name=name,
        price=price or "N/A",
        ratings=ratings or "N/A",
        url=url or "N/A",
    )


def get_cards(driver) -> List:
    for selector in CARD_SELECTORS:
        cards = driver.find_elements(By.CSS_SELECTOR, selector)
        if cards:
            return cards
    return []


def scrape_page(driver, seen: Set[str]) -> List[Product]:
    wait = WebDriverWait(driver, 25)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    try:
        wait.until(lambda d: len(get_cards(d)) > 0)
    except TimeoutException:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        driver.save_screenshot(os.path.join(OUTPUT_DIR, "lazada_last_page.png"))
        with open(os.path.join(OUTPUT_DIR, "lazada_last_page.html"), "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        return []

    cards = get_cards(driver)
    products: List[Product] = []

    for card in cards:
        product = scrape_product_card(card)
        if not product:
            continue
        dedupe_key = f"{product.name}|{product.url}"
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        products.append(product)

    return products


def build_lazada_page_url(base_url: str, page_index: int) -> str:
    if page_index <= 1:
        return base_url
    if "?" in base_url:
        return f"{base_url}&page={page_index}"
    return f"{base_url}?page={page_index}"


def save_to_csv(products: List[Product], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "price", "ratings", "url"])
        writer.writeheader()
        for product in products:
            writer.writerow(asdict(product))


def save_to_json(products: List[Product], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in products], f, ensure_ascii=False, indent=2)


def main() -> None:
    headless = False
    driver = setup_driver(headless=headless)
    all_products: List[Product] = []
    seen: Set[str] = set()
    manual_challenge = False
    run_error: Optional[Exception] = None

    try:
        driver.get(SEARCH_URL)
        if manual_challenge:
            input("Solve any on-page checks, then press Enter to continue...")

        page_index = 1
        while True:
            products = scrape_page(driver, seen)
            all_products.extend(products)
            print(f"Page {page_index}: collected {len(products)} items")

            page_index += 1
            next_url = build_lazada_page_url(SEARCH_URL, page_index)
            driver.get(next_url)
            try:
                WebDriverWait(driver, 25).until(lambda d: len(get_cards(d)) > 0)
            except TimeoutException:
                print(f"Timed out loading {next_url}. Saving collected results...")
                break

    except Exception as exc:
        run_error = exc
    finally:
        driver.quit()
        save_to_csv(all_products, CSV_PATH)
        save_to_json(all_products, JSON_PATH)
        print(f"Saved {len(all_products)} products to {CSV_PATH} and {JSON_PATH}")
        if run_error:
            raise run_error


if __name__ == "__main__":
    main()
