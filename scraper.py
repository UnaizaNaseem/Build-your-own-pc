import csv
import json
import os
import shutil
import glob
from datetime import datetime

from playwright.sync_api import sync_playwright


CSV_PREFIX = "Products-Data"

OUTPUT_FILE = "pc_components_data.json"
FAILED_FILE = "scraping_failed.json"

BASE_URL = "https://www.gb-tech.pk"


def find_csv_file():
    # Pick the newest Products-Data CSV automatically.
    files = glob.glob(f"{CSV_PREFIX}*.csv")

    if not files:
        raise FileNotFoundError(
            f"No CSV file starting with '{CSV_PREFIX}' was found."
        )

    files.sort(
        key=os.path.getmtime,
        reverse=True
    )

    selected_file = files[0]

    print(f"Using CSV file: {selected_file}")

    return selected_file


CSV_FILE = find_csv_file()


def clean_value(value):
    if value is None:
        return ""

    return str(value).strip()


def product_id(value):
    return clean_value(value)


def backup_existing_json():
    # Keep a copy of the previous catalogue before updating it.
    if not os.path.exists(OUTPUT_FILE):
        return None

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    backup_file = (
        f"{OUTPUT_FILE}.backup_{timestamp}"
    )

    shutil.copy2(
        OUTPUT_FILE,
        backup_file
    )

    print(f"Backup created: {backup_file}")

    return backup_file


def load_existing_products():

    if not os.path.exists(OUTPUT_FILE):
        return []

    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except Exception as error:

        print(
            f"Could not read existing JSON: {error}"
        )

        return []


def build_existing_product_map(products):

    product_map = {}

    for product in products:

        if not isinstance(product, dict):
            continue

        pid = product_id(
            product.get("Product ID")
        )

        if pid:
            product_map[pid] = product

    return product_map


def merge_product_data(
    old_product,
    new_product
):

    merged = dict(
        old_product or {}
    )

    basic_fields = [
        "Product ID",
        "Product Name",
        "Category",
        "Brand",
        "Price",
        "Product URL",
        "Image"
    ]

    for field in basic_fields:

        value = clean_value(
            new_product.get(field)
        )

        if value:
            merged[field] = value

    old_specs = (
        old_product.get(
            "Specifications",
            {}
        )
        if isinstance(old_product, dict)
        else {}
    )

    new_specs = new_product.get(
        "Specifications",
        {}
    )

    if not isinstance(old_specs, dict):
        old_specs = {}

    if not isinstance(new_specs, dict):
        new_specs = {}

    merged_specs = dict(old_specs)

    for name, value in new_specs.items():

        name = clean_value(name)
        value = clean_value(value)

        if not name or not value:
            continue

        merged_specs[name] = value

    merged["Specifications"] = merged_specs

    return merged


def scrape_product(
    page,
    product
):

    product_url = clean_value(
        product.get("Product URL")
    )

    if not product_url:
        raise Exception(
            "Product has no URL"
        )

    if product_url.startswith("/"):
        product_url = BASE_URL + product_url

    print(
        f"    Opening: {product_url}"
    )

    page.goto(
        product_url,
        wait_until="networkidle",
        timeout=30000
    )

    print(
        f"    Page loaded: {page.title()}"
    )

    specifications_tab = page.get_by_text(
        "Specifications",
        exact=True
    )

    specifications = {}

    if specifications_tab.count() > 0:

        specifications_tab.first.click()

        page.wait_for_timeout(1000)

        rows = page.locator(
            "div.grid.grid-cols-12"
        )

        for i in range(rows.count()):

            row = rows.nth(i)

            try:

                name_column = row.locator(
                    ":scope > div.col-span-3"
                )

                value_column = row.locator(
                    ":scope > div.col-span-9"
                )

                if name_column.count() != 1:
                    continue

                if value_column.count() != 1:
                    continue

                name = clean_value(
                    name_column.inner_text()
                )

                value = clean_value(
                    value_column.inner_text()
                )

                if not name or not value:
                    continue

                specifications[name] = value

            except Exception:
                continue

    product_data = {

        "Product ID":
            clean_value(
                product.get("Product ID")
            ),

        "Product Name":
            clean_value(
                product.get("Product Name")
            ),

        "Category":
            clean_value(
                product.get("Category")
            ),

        "Brand":
            clean_value(
                product.get("Brand")
            ),

        "Price":
            clean_value(
                product.get("Price")
            ),

        "Product URL":
            product_url,

        "Image":
            clean_value(
                product.get("Image")
            ),

        "Specifications":
            specifications
    }

    return product_data


def load_csv_products():

    products = []

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        for row_number, product in enumerate(
            reader,
            start=2
        ):

            cleaned = {}

            for key, value in product.items():

                if key is None:
                    continue

                key = str(key).strip()

                value = (
                    str(value).strip()
                    if value is not None
                    else ""
                )

                cleaned[key] = value

            pid = clean_value(
                cleaned.get("Product ID")
            )

            url = clean_value(
                cleaned.get("Product URL")
            )

            # Empty rows sometimes end up in exports.
            # They don't need to be processed.
            if not pid and not url:
                continue

            # No URL means there is nothing for Playwright to open.
            # Keep these out of the scrape rather than treating them
            # like actual products.
            if not url:
                continue

            products.append(cleaned)

    return products


def main():

    print()
    print("=" * 65)
    print("GB TECH — PRODUCT DATA UPDATE")
    print("=" * 65)
    print()

    existing_products_list = (
        load_existing_products()
    )

    existing_products = (
        build_existing_product_map(
            existing_products_list
        )
    )

    print(
        f"Existing products: "
        f"{len(existing_products)}"
    )

    all_products = load_csv_products()

    print(
        f"Products in CSV: "
        f"{len(all_products)}"
    )

    # Process the complete catalogue.
    # Nothing is limited to a particular category.
    products_to_scrape = all_products

    print(
        f"Products to process: "
        f"{len(products_to_scrape)}"
    )

    print()

    if not products_to_scrape:

        print(
            "Nothing to scrape."
        )

        return

    if existing_products_list:
        backup_existing_json()

    successful_products = []
    failed_products = []

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        total = len(
            products_to_scrape
        )

        for index, product in enumerate(
            products_to_scrape,
            start=1
        ):

            pid = product_id(
                product.get("Product ID")
            )

            name = clean_value(
                product.get("Product Name")
            )

            print()
            print("-" * 65)

            print(
                f"[{index}/{total}] {name}"
            )

            print(
                f"    Product ID: {pid}"
            )

            print(
                f"    Category: "
                f"{product.get('Category', '')}"
            )

            try:

                scraped_product = scrape_product(
                    page,
                    product
                )

                if pid in existing_products:

                    final_product = merge_product_data(
                        existing_products[pid],
                        scraped_product
                    )

                    print(
                        "    Updated existing product"
                    )

                else:

                    final_product = scraped_product

                    print(
                        "    Added new product"
                    )

                successful_products.append(
                    final_product
                )

                print(
                    f"    Specifications: "
                    f"{len(final_product.get('Specifications', {}))}"
                )

            except Exception as error:

                print(
                    f"    Failed: {error}"
                )

                failed_products.append(
                    {
                        "Product ID": pid,
                        "Product Name": name,
                        "Category": clean_value(
                            product.get("Category")
                        ),
                        "Product URL": clean_value(
                            product.get("Product URL")
                        ),
                        "Error": str(error),
                        "Existing Product":
                            pid in existing_products
                    }
                )

                # If the product already has good data,
                # don't replace it with an empty result.
                if pid in existing_products:

                    print(
                        "    Keeping previous product data."
                    )

        browser.close()

    # Start with the existing catalogue.
    # Successful updates will replace their old versions.
    final_products = dict(
        existing_products
    )

    for product in successful_products:

        pid = product_id(
            product.get("Product ID")
        )

        if pid:
            final_products[pid] = product

    final_product_list = list(
        final_products.values()
    )

    # Keep the final JSON neatly organised.
    final_product_list.sort(
        key=lambda item: (
            clean_value(
                item.get("Category")
            ).lower(),

            clean_value(
                item.get("Brand")
            ).lower(),

            clean_value(
                item.get("Product Name")
            ).lower()
        )
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            final_product_list,
            file,
            indent=4,
            ensure_ascii=False
        )

    with open(
        FAILED_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            failed_products,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 65)
    print("UPDATE COMPLETE")
    print("=" * 65)
    print()

    print(
        f"Products in CSV: "
        f"{len(all_products)}"
    )

    print(
        f"Successfully processed: "
        f"{len(successful_products)}"
    )

    print(
        f"Could not update: "
        f"{len(failed_products)}"
    )

    print(
        f"Products in final JSON: "
        f"{len(final_product_list)}"
    )

    print()

    print(
        f"Product data saved to: "
        f"{OUTPUT_FILE}"
    )

    if failed_products:

        print(
            f"Failed products saved to: "
            f"{FAILED_FILE}"
        )

    print()

    print(
        "Existing product data was kept where an update failed."
    )

    print()
    print("=" * 65)


if __name__ == "__main__":
    main()