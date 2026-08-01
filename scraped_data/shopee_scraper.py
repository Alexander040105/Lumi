import csv
import json
import os
import time
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


SEARCH_URL = "https://shopee.ph/search?keyword=wind%20power%20generator"

load_dotenv(override=True)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
RUNTIME_DIR = os.path.join(os.path.dirname(__file__), "runtime")
CSV_PATH = os.path.join(OUTPUT_DIR, "shopee_products_wind_power_generator.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "shopee_products_wind_power_generator.json")


@dataclass
class Product:
    name: str
    price: str
    ratings: str
    url: str


CARD_SELECTORS = [
    "div[data-sqe='item']",
    "div.shopee-search-item-result__item",
    "li[data-sqe='item']",
    "li.shopee-search-item-result__item"
]

NAME_SELECTORS = [
    "div[data-sqe='name']",
    "div[aria-label][role='link']",
    "a[data-sqe='link'] div[aria-label]",
    "a[aria-label]"
]

PRICE_SELECTORS = [
    "span.truncate.text-base\\/5.font-medium",
    "span[data-testid='item-card-price']",
    "div[data-testid='item-card-price']",
    "span[aria-label*='price' i]",
    "span[class*='price']",
    "span[class*='Price']",
    "div[class*='price'] span"
]

RATING_SELECTORS = [
    "span[aria-label*='rating' i]",
    "span[class*='rating']"
]

LINK_SELECTORS = [
    "a[data-sqe='link']",
    "a[aria-label]",
    "a[href*='/product/']"
]


def scroll_to_load(driver, max_scrolls: int = 12, delay_seconds: float = 1.0) -> None:
    last_count = 0
    stable_rounds = 0
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(delay_seconds)
        current_count = len(get_cards(driver))
        if current_count <= last_count:
            stable_rounds += 1
        else:
            stable_rounds = 0
        last_count = current_count
        if stable_rounds >= 2:
            break
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(0.2)


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


def scrape_product_card(card) -> Optional[Product]:
    name = safe_find_text(card, NAME_SELECTORS)
    price = safe_find_text(card, PRICE_SELECTORS)
    if not price:
        try:
            price_container = card.find_element(By.CSS_SELECTOR, "div[data-testid='item-card-price']")
            price = "".join([span.text for span in price_container.find_elements(By.CSS_SELECTOR, "span")]).strip()
        except Exception:
            price = ""
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
        scroll_to_load(driver, max_scrolls=12, delay_seconds=1.0)
        wait.until(lambda d: len(get_cards(d)) > 0)
    except TimeoutException:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        driver.save_screenshot(os.path.join(OUTPUT_DIR, "shopee_last_page.png"))
        with open(os.path.join(OUTPUT_DIR, "shopee_last_page.html"), "w", encoding="utf-8") as f:
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


def build_shopee_page_url(base_url: str, page_index: int) -> str:
    if page_index <= 0:
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

        page_index = 0
        while True:
            products = scrape_page(driver, seen)
            all_products.extend(products)
            print(f"Page {page_index + 1}: collected {len(products)} items")

            page_index += 1
            time.sleep(1)
            next_url = build_shopee_page_url(SEARCH_URL, page_index)
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
