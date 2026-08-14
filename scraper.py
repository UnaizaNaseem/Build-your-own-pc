import csv
import json
import os
from playwright.sync_api import sync_playwright


# ============================================================
# SETTINGS
# ============================================================

CSV_FILE = "Products-Data-14-08-2026.csv"

OUTPUT_FILE = "pc_components_data.json"
FAILED_FILE = "scraping_failed.json"

BASE_URL = "https://www.gb-tech.pk"


# ============================================================
# LOAD EXISTING SCRAPED DATA
# ============================================================

if os.path.exists(OUTPUT_FILE):

    with open(
        OUTPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        scraped_products = json.load(file)

else:

    scraped_products = []


# Create a set of IDs that have already been scraped

scraped_ids = {
    str(product["Product ID"])
    for product in scraped_products
}


# ============================================================
# SCRAPE ONE PRODUCT
# ============================================================

def scrape_product(page, product):

    product_name = product["Product Name"]
    product_url = product["Product URL"]

    print(f"    Opening: {product_url}")

    # --------------------------------------------------------
    # Check URL
    # --------------------------------------------------------

    if not product_url:

        raise Exception(
            "Product has no URL"
        )

    # Convert relative URL into full URL

    if product_url.startswith("/"):

        product_url = BASE_URL + product_url


    # --------------------------------------------------------
    # OPEN PRODUCT PAGE
    # --------------------------------------------------------

    page.goto(
        product_url,
        wait_until="networkidle",
        timeout=30000
    )

    print(
        f"    Page loaded: {page.title()}"
    )


    # --------------------------------------------------------
    # FIND SPECIFICATIONS TAB
    # --------------------------------------------------------

    specifications_tab = page.get_by_text(
        "Specifications",
        exact=True
    )

    if specifications_tab.count() == 0:

        raise Exception(
            "Specifications tab not found"
        )


    # --------------------------------------------------------
    # CLICK SPECIFICATIONS
    # --------------------------------------------------------

    specifications_tab.first.click()

    # Give the page time to render the second tab

    page.wait_for_timeout(1000)


    # --------------------------------------------------------
    # FIND SPECIFICATION ROWS
    # --------------------------------------------------------

    rows = page.locator(
        "div.grid.grid-cols-12"
    )

    specifications = {}


    for i in range(rows.count()):

        row = rows.nth(i)


        # Specification name

        name_column = row.locator(
            "div.col-span-3"
        )


        # Specification value

        value_column = row.locator(
            "div.col-span-9"
        )


        if name_column.count() == 0:
            continue

        if value_column.count() == 0:
            continue


        name = name_column.inner_text().strip()

        value = value_column.inner_text().strip()


        if not name:
            continue

        if not value:
            continue


        specifications[name] = value


    # --------------------------------------------------------
    # MAKE SURE WE ACTUALLY FOUND DATA
    # --------------------------------------------------------

    if not specifications:

        raise Exception(
            "Specifications tab opened but no specifications were found"
        )


    # --------------------------------------------------------
    # BUILD PRODUCT DATA
    # --------------------------------------------------------

    product_data = {

        "Product ID":
            product["Product ID"],

        "Product Name":
            product["Product Name"],

        "Category":
            product["Category"],

        "Brand":
            product["Brand"],

        "Price":
            product["Price"],

        "Product URL":
            product_url,

        "Image":
            product["Image"],

        "Specifications":
            specifications
    }


    return product_data


# ============================================================
# MAIN
# ============================================================

def main():


    # ========================================================
    # READ CSV
    # ========================================================

    pc_components = []


    with open(
        CSV_FILE,
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)


        for product in reader:

            category = product["Category"].strip()


            # ------------------------------------------------
            # ANY PC COMPONENT CATEGORY
            # ------------------------------------------------

            if category.startswith(
                "PC Components"
            ):

                pc_components.append(product)


    # ========================================================
    # DETERMINE NEW PRODUCTS
    # ========================================================

    new_products = []


    for product in pc_components:

        product_id = str(
            product["Product ID"]
        )


        if product_id not in scraped_ids:

            new_products.append(product)


    # ========================================================
    # HEADER
    # ========================================================

    print()

    print("=" * 60)
    print("PC COMPONENT SCRAPER")
    print("=" * 60)

    print(
        f"Total PC Components in CSV: "
        f"{len(pc_components)}"
    )

    print(
        f"Previously scraped: "
        f"{len(scraped_products)}"
    )

    print(
        f"New products found: "
        f"{len(new_products)}"
    )

    print()


    # ========================================================
    # IF NOTHING NEW
    # ========================================================

    if not new_products:

        print(
            "No new products need to be scraped."
        )

        return


    # ========================================================
    # STORAGE
    # ========================================================

    successful_products = []

    failed_products = []


    # ========================================================
    # START PLAYWRIGHT
    # ========================================================

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )


        page = browser.new_page()


        # ====================================================
        # SCRAPE NEW PRODUCTS
        # ====================================================

        total = len(new_products)


        for index, product in enumerate(
            new_products,
            start=1
        ):


            print(
                f"[{index}/{total}] "
                f"{product['Product Name']}"
            )

            print(
                f"    Category: "
                f"{product['Category']}"
            )


            try:

                product_data = scrape_product(
                    page,
                    product
                )


                successful_products.append(
                    product_data
                )


                print(
                    f"    ✓ Success "
                    f"({len(product_data['Specifications'])} specifications)"
                )


            except Exception as error:


                print(
                    f"    ✗ Failed: {error}"
                )


                failed_products.append(

                    {
                        "Product ID":
                            product["Product ID"],

                        "Product Name":
                            product["Product Name"],

                        "Category":
                            product["Category"],

                        "Product URL":
                            product["Product URL"],

                        "Error":
                            str(error)
                    }

                )


            print()


        browser.close()


    # ========================================================
    # ADD NEW PRODUCTS TO EXISTING DATA
    # ========================================================

    all_products = (
        scraped_products
        + successful_products
    )


    # ========================================================
    # SAVE JSON
    # ========================================================

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_products,
            file,
            indent=4,
            ensure_ascii=False
        )


    # ========================================================
    # SAVE FAILED PRODUCTS
    # ========================================================

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


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print("=" * 60)
    print("SCRAPING COMPLETE")
    print("=" * 60)

    print(
        f"Total PC Components in CSV: "
        f"{len(pc_components)}"
    )

    print(
        f"Previously scraped: "
        f"{len(scraped_products)}"
    )

    print(
        f"New products found: "
        f"{len(new_products)}"
    )

    print(
        f"Successfully scraped: "
        f"{len(successful_products)}"
    )

    print(
        f"Failed: "
        f"{len(failed_products)}"
    )

    print(
        f"Total products in JSON: "
        f"{len(all_products)}"
    )

    print()

    print(
        f"Output file: {OUTPUT_FILE}"
    )

    print(
        f"Failed file: {FAILED_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()