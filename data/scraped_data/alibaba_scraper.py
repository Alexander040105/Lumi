import csv
import json
import os
import re
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


# # SEARCH_URL = "https://www.alibaba.com/showroom/micro-hydro-turbine.html"
SEARCH_URL = "https://www.alibaba.com/showroom/wind-turbine-alibaba.html"
# SEARCH_URL = "https://www.alibaba.com/showroom/solar-panels.html"

load_dotenv(override=True)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
RUNTIME_DIR = os.path.join(os.path.dirname(__file__), "runtime")
CSV_PATH = os.path.join(OUTPUT_DIR, "alibaba_products_wind_turbine.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "alibaba_products_wind_turbine.json")


@dataclass
class Product:
    name: str
    price: str
    ratings: str
    url: str


# Primary and fallback selectors for product cards and fields.
CARD_SELECTORS = [
    "div[data-modulename='ProductList-G'] div[data-product_id]",
    "div[data-product_id]"
]

NAME_SELECTORS = [
    "a.product-title h2",
    "a.product-title"
]

PRICE_SELECTORS = [
    "div[data-component='ProductPrice'] span.il-text-lg",
    "div[data-component='ProductPrice'] span"
]

RATING_SELECTORS = [
    "div[data-component='SupplierInfo'] span"
]

LINK_SELECTORS = [
    "a.product-title"
]

RATING_PATTERN = re.compile(r"\b\d+(?:\.\d+)?/5\.0\b")
REVIEW_PATTERN = re.compile(r"\(\d+\)")


def setup_driver(headless: bool = False) -> webdriver.Chrome:
    options = Options()
    # Use a realistic user agent to reduce simple bot flags.
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    options.add_argument("--window-size=1400,900")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Keep browser cache/profile inside project to avoid system cache failures.
    os.makedirs(RUNTIME_DIR, exist_ok=True)
    profile_dir = os.path.join(RUNTIME_DIR, "profile")
    cache_dir = os.path.join(RUNTIME_DIR, "cache")
    os.makedirs(profile_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument(f"--disk-cache-dir={cache_dir}")

    if headless:
        # Use the new headless mode for Chrome 109+.
        options.add_argument("--headless=new")

    driver_path = os.getenv("CHROMEDRIVER_PATH")
    chrome_binary = os.getenv("CHROME_BINARY")
    brave_binary = os.getenv("BRAVE_BINARY")
    if brave_binary:
        options.binary_location = brave_binary
    elif chrome_binary:
        options.binary_location = chrome_binary

    # If Selenium Manager fails (e.g., low disk space), set CHROMEDRIVER_PATH.
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


def extract_rating(card) -> str:
    rating_value = ""
    review_count = ""
    for selector in RATING_SELECTORS:
        try:
            elements = card.find_elements(By.CSS_SELECTOR, selector)
        except Exception:
            continue
        for element in elements:
            text = element.text.strip()
            if not text:
                continue
            if not rating_value and RATING_PATTERN.search(text):
                rating_value = text
            elif not review_count and REVIEW_PATTERN.search(text):
                review_count = text
            if rating_value and review_count:
                break
        if rating_value:
            break
    if rating_value and review_count:
        return f"{rating_value} {review_count}"
    return rating_value


def scrape_product_card(card) -> Optional[Product]:
    name = safe_find_text(card, NAME_SELECTORS)
    price = safe_find_text(card, PRICE_SELECTORS)
    ratings = extract_rating(card)
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
        # Wait for at least one product card to render.
        wait.until(lambda d: len(get_cards(d)) > 0)
    except TimeoutException:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        driver.save_screenshot(os.path.join(OUTPUT_DIR, "last_page.png"))
        with open(os.path.join(OUTPUT_DIR, "last_page.html"), "w", encoding="utf-8") as f:
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


def go_to_next_page(driver) -> bool:
    # Common next button selectors for Alibaba search pages.
    next_selectors = [
        "a.next",  # legacy
        "button.next",  # fallback
        "a[aria-label='Next']",
        "button[aria-label='Next']"
    ]

    for selector in next_selectors:
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, selector)
            if not next_button.is_enabled():
                return False
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            next_button.click()
            return True
        except Exception:
            continue
    return False


def build_showroom_page_url(base_url: str, page_index: int) -> Optional[str]:
    match = re.match(r"^(https?://www\.alibaba\.com/showroom/[^?]+)\.html", base_url)
    if not match:
        return None
    base = match.group(1)
    if page_index <= 1:
        return f"{base}.html"
    return f"{base}_{page_index}.html"


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
    headless = False  # Set True to run headless
    driver = setup_driver(headless=headless)
    all_products: List[Product] = []
    seen: Set[str] = set()
    manual_challenge = False  # Set True to manually solve any bot checks.
    run_error: Optional[Exception] = None

    try:
        driver.get(SEARCH_URL)
        if manual_challenge:
            input("Solve any on-page checks, then press Enter to continue...")

        page_index = 1
        base_url = driver.current_url
        while True:
            products = scrape_page(driver, seen)
            all_products.extend(products)
            print(f"Page {page_index}: collected {len(products)} items")

            page_index += 1
            next_url = build_showroom_page_url(base_url, page_index)
            if next_url:
                driver.get(next_url)
                try:
                    WebDriverWait(driver, 25).until(
                        lambda d: len(get_cards(d)) > 0
                    )
                except TimeoutException:
                    print(f"Timed out loading {next_url}. Saving collected results...")
                    break
                continue

            if not go_to_next_page(driver):
                break
            current_url = driver.current_url
            WebDriverWait(driver, 25).until(
                lambda d: d.current_url != current_url or len(get_cards(d)) > 0
            )

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
