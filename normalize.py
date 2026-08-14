import json
import re

# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "pc_components_data.json"
OUTPUT_FILE = "pc_components_normalized.json"


# ============================================================
# HELPERS
# ============================================================

def clean(value):
    if value is None:
        return ""

    return str(value).strip()


def get_specs(product):
    specs = product.get("Specifications", {})

    if isinstance(specs, dict):
        return specs

    return {}


def get_spec(product, *names):
    """
    Look for an exact specification name.
    """

    specs = get_specs(product)

    for name in names:

        for key, value in specs.items():

            if clean(key).lower() == name.lower():
                return clean(value)

    return ""


def combined_text(product):
    parts = [
        clean(product.get("Product Name"))
    ]

    for value in get_specs(product).values():
        parts.append(clean(value))

    return " ".join(parts)


def number_from_text(text):
    if not text:
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)",
        text
    )

    if match:
        try:
            return float(match.group(1))
        except ValueError:
            pass

    return None


# ============================================================
# MOTHERBOARD
# ============================================================

def normalize_motherboard(product):

    text = combined_text(product)

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if re.search(r"\bDDR5\b", text, re.I):
        memory_type = "DDR5"

    elif re.search(r"\bDDR4\b", text, re.I):
        memory_type = "DDR4"

    else:
        memory_type = None

    # --------------------------------------------------------
    # FORM FACTOR
    # --------------------------------------------------------

    form_factor_text = get_spec(
        product,
        "Form Factor",
        "Form factor"
    )

    form_factor_search = (
        form_factor_text
        if form_factor_text
        else text
    )

    form_factor = None

    if re.search(
        r"Micro[\s-]?ATX|mATX",
        form_factor_search,
        re.I
    ):
        form_factor = "Micro-ATX"

    elif re.search(
        r"Mini[\s-]?ITX",
        form_factor_search,
        re.I
    ):
        form_factor = "Mini-ITX"

    elif re.search(
        r"E[\s-]?ATX",
        form_factor_search,
        re.I
    ):
        form_factor = "E-ATX"

    elif re.search(
        r"\bATX\b",
        form_factor_search,
        re.I
    ):
        form_factor = "ATX"

    # --------------------------------------------------------
    # SOCKET
    # --------------------------------------------------------

    socket = None

    socket_patterns = [
        (r"\bLGA\s*1851\b", "LGA1851"),
        (r"\bLGA\s*1700\b", "LGA1700"),
        (r"\bLGA\s*1200\b", "LGA1200"),
        (r"\bAM5\b", "AM5"),
        (r"\bAM4\b", "AM4"),
    ]

    for pattern, value in socket_patterns:

        if re.search(pattern, text, re.I):
            socket = value
            break

    # --------------------------------------------------------
    # PLATFORM
    # --------------------------------------------------------

    if socket in ["AM4", "AM5"]:
        platform = "AMD"

    elif socket in ["LGA1200", "LGA1700", "LGA1851"]:
        platform = "Intel"

    else:
        platform = None

    return {
        "type": "motherboard",
        "memory_type": memory_type,
        "form_factor": form_factor,
        "socket": socket,
        "platform": platform
    }


# ============================================================
# GRAPHICS CARD
# ============================================================

def normalize_graphics_card(product):

    # --------------------------------------------------------
    # DIMENSIONS
    # --------------------------------------------------------

    dimensions = get_spec(
        product,
        "Dimensions"
    )

    length_mm = None

    if dimensions:

        # Example:
        # 228 x 123 x 50mm

        match = re.search(
            r"(\d+(?:\.\d+)?)\s*x\s*"
            r"(\d+(?:\.\d+)?)\s*x\s*"
            r"(\d+(?:\.\d+)?)\s*mm",
            dimensions,
            re.I
        )

        if match:
            length_mm = float(match.group(1))

    # --------------------------------------------------------
    # PSU
    # --------------------------------------------------------

    recommended_psu = get_spec(
        product,
        "Recommended PSU",
        "Recommended Power Supply",
        "Recommended System Power Supply"
    )

    recommended_psu_wattage = None

    if recommended_psu:

        value = number_from_text(
            recommended_psu
        )

        if value is not None:
            recommended_psu_wattage = int(value)

    # --------------------------------------------------------
    # GPU BRAND
    # --------------------------------------------------------

    text = combined_text(product)

    if re.search(
        r"\bGeForce\b|\bRTX\b",
        text,
        re.I
    ):
        gpu_brand = "NVIDIA"

    elif re.search(
        r"\bRadeon\b|\bRX\s*\d",
        text,
        re.I
    ):
        gpu_brand = "AMD"

    else:
        gpu_brand = None

    return {
        "type": "graphics_card",
        "length_mm": length_mm,
        "recommended_psu_wattage": recommended_psu_wattage,
        "brand": gpu_brand
    }


# ============================================================
# RAM
# ============================================================

def normalize_ram(product):

    text = combined_text(product)

    # --------------------------------------------------------
    # MEMORY TYPE
    # --------------------------------------------------------

    if re.search(r"\bDDR5\b", text, re.I):
        memory_type = "DDR5"

    elif re.search(r"\bDDR4\b", text, re.I):
        memory_type = "DDR4"

    else:
        memory_type = None

    # --------------------------------------------------------
    # FORM FACTOR
    # --------------------------------------------------------

    form_factor_text = get_spec(
        product,
        "Form Factor"
    )

    search_text = (
        form_factor_text
        if form_factor_text
        else text
    )

    if re.search(
        r"SO[-\s]?DIMM",
        search_text,
        re.I
    ):
        form_factor = "SO-DIMM"

    elif re.search(
        r"U[-\s]?DIMM",
        search_text,
        re.I
    ):
        form_factor = "DIMM"

    elif re.search(
        r"\bDIMM\b",
        search_text,
        re.I
    ):
        form_factor = "DIMM"

    else:
        form_factor = None

    # --------------------------------------------------------
    # CAPACITY
    # --------------------------------------------------------

    capacity_text = get_spec(
        product,
        "Capacity"
    )

    if not capacity_text:
        capacity_text = clean(
            product.get("Product Name")
        )

    capacity_gb = None

    # 32GB (2x16GB)
    kit_match = re.search(
        r"(\d+)\s*GB\s*\(\s*(\d+)\s*x\s*(\d+)\s*GB",
        capacity_text,
        re.I
    )

    if kit_match:

        capacity_gb = int(
            kit_match.group(1)
        )

    else:

        values = re.findall(
            r"(\d+)\s*GB",
            capacity_text,
            re.I
        )

        if values:

            numbers = [
                int(x)
                for x in values
            ]

            capacity_gb = max(numbers)

    return {
        "type": "ram",
        "memory_type": memory_type,
        "form_factor": form_factor,
        "capacity_gb": capacity_gb
    }


# ============================================================
# CASE
# ============================================================

def normalize_case(product):

    form_factor_text = get_spec(
        product,
        "Motherboard Support",
        "Motherboard Compatibility",
        "Supported Motherboards",
        "Form Factor"
    )

    if not form_factor_text:
        form_factor_text = combined_text(product)

    supported_form_factors = []

    if re.search(
        r"E[\s-]?ATX",
        form_factor_text,
        re.I
    ):
        supported_form_factors.append(
            "E-ATX"
        )

    if re.search(
        r"\bATX\b",
        form_factor_text,
        re.I
    ):
        supported_form_factors.append(
            "ATX"
        )

    if re.search(
        r"Micro[\s-]?ATX|mATX",
        form_factor_text,
        re.I
    ):
        supported_form_factors.append(
            "Micro-ATX"
        )

    if re.search(
        r"Mini[\s-]?ITX",
        form_factor_text,
        re.I
    ):
        supported_form_factors.append(
            "Mini-ITX"
        )

    supported_form_factors = list(
        dict.fromkeys(
            supported_form_factors
        )
    )

    if not supported_form_factors:
        supported_form_factors = None

    # --------------------------------------------------------
    # GPU CLEARANCE
    # --------------------------------------------------------

    gpu_clearance_text = get_spec(
        product,
        "GPU Length",
        "Maximum GPU Length",
        "Graphics Card Length",
        "VGA Length"
    )

    max_gpu_length_mm = None

    if gpu_clearance_text:

        value = number_from_text(
            gpu_clearance_text
        )

        if value:
            max_gpu_length_mm = value

    return {
        "type": "case",
        "supported_form_factors":
            supported_form_factors,
        "max_gpu_length_mm":
            max_gpu_length_mm
    }


# ============================================================
# COOLING
# ============================================================

def normalize_cooling(product):

    text = combined_text(product)

    supported_sockets = []

    socket_patterns = [
        (r"\bAM4\b", "AM4"),
        (r"\bAM5\b", "AM5"),
        (r"\bLGA\s*1700\b", "LGA1700"),
        (r"\bLGA\s*1851\b", "LGA1851"),
        (r"\bLGA\s*1200\b", "LGA1200"),
    ]

    for pattern, socket in socket_patterns:

        if re.search(
            pattern,
            text,
            re.I
        ):
            supported_sockets.append(
                socket
            )

    supported_sockets = list(
        dict.fromkeys(
            supported_sockets
        )
    )

    if not supported_sockets:
        supported_sockets = None

    return {
        "type": "cooling",
        "supported_sockets":
            supported_sockets
    }


# ============================================================
# POWER SUPPLY
# ============================================================

def normalize_power_supply(product):

    # IMPORTANT:
    # Do NOT scan the entire specification text first.
    # Read explicitly labelled power fields.

    wattage_text = get_spec(
        product,
        "Wattage",
        "Power Output",
        "Power Output (W)",
        "Total Power",
        "Maximum Power"
    )

    wattage = None

    if wattage_text:

        # Example:
        # 1650W
        # 850W / 1000W

        values = re.findall(
            r"(\d{3,4})\s*W",
            wattage_text,
            re.I
        )

        if values:

            numbers = [
                int(x)
                for x in values
            ]

            # If multiple variants are listed,
            # we use the highest available wattage.
            wattage = max(numbers)

    # --------------------------------------------------------
    # FALLBACK TO PRODUCT NAME ONLY
    # --------------------------------------------------------

    if wattage is None:

        product_name = clean(
            product.get("Product Name")
        )

        match = re.search(
            r"\b(\d{3,4})\s*W\b",
            product_name,
            re.I
        )

        if match:

            wattage = int(
                match.group(1)
            )

    return {
        "type": "power_supply",
        "wattage": wattage
    }


# ============================================================
# FAN
# ============================================================

def normalize_fan(product):

    text = combined_text(product)

    # --------------------------------------------------------
    # INDIVIDUAL FAN SIZE
    # --------------------------------------------------------

    size_mm = None

    match = re.search(
        r"\b(80|92|120|140|200)\s*mm\b",
        text,
        re.I
    )

    if match:
        size_mm = int(
            match.group(1)
        )

    return {
        "type": "fan",
        "size_mm": size_mm
    }


# ============================================================
# PRODUCT TYPE
# ============================================================

def determine_type(product):

    category = clean(
        product.get("Category")
    ).lower()

    if "motherboard" in category:
        return "motherboard"

    if "graphics card" in category:
        return "graphics_card"

    if "ram" in category:
        return "ram"

    if "power supplies" in category:
        return "power_supply"

    if "cooling" in category:
        return "cooling"

    if "fans" in category or "fan" in category:
        return "fan"

    if "cases" in category or "case" in category:
        return "case"

    return None


# ============================================================
# NORMALIZE ONE PRODUCT
# ============================================================

def normalize_product(product):

    product_type = determine_type(
        product
    )

    if product_type == "motherboard":
        compatibility = normalize_motherboard(
            product
        )

    elif product_type == "graphics_card":
        compatibility = normalize_graphics_card(
            product
        )

    elif product_type == "ram":
        compatibility = normalize_ram(
            product
        )

    elif product_type == "case":
        compatibility = normalize_case(
            product
        )

    elif product_type == "cooling":
        compatibility = normalize_cooling(
            product
        )

    elif product_type == "power_supply":
        compatibility = normalize_power_supply(
            product
        )

    elif product_type == "fan":
        compatibility = normalize_fan(
            product
        )

    else:
        return None

    return {
        "Product ID":
            product.get("Product ID"),

        "Product Name":
            product.get("Product Name"),

        "Category":
            product.get("Category"),

        "Brand":
            product.get("Brand"),

        "Price":
            product.get("Price"),

        "Product URL":
            product.get("Product URL"),

        "Image":
            product.get("Image"),

        "Compatibility":
            compatibility
    }


# ============================================================
# MAIN
# ============================================================

def main():

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        products = json.load(file)

    print(
        f"Products loaded: {len(products)}"
    )

    normalized_products = []
    counts = {}

    for product in products:

        normalized = normalize_product(
            product
        )

        if normalized is None:
            continue

        normalized_products.append(
            normalized
        )

        product_type = (
            normalized[
                "Compatibility"
            ]["type"]
        )

        counts[product_type] = (
            counts.get(product_type, 0) + 1
        )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            normalized_products,
            file,
            indent=4,
            ensure_ascii=False
        )

    print()
    print("=" * 60)
    print("NORMALIZATION COMPLETE")
    print("=" * 60)

    for product_type, count in counts.items():

        print(
            f"{product_type}: {count}"
        )

    print()
    print(
        f"Output file: {OUTPUT_FILE}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()