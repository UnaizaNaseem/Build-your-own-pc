import json
import re


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "pc_components_data.json"
OUTPUT_FILE = "pc_components_normalized.json"


# ============================================================
# BASIC HELPERS
# ============================================================

def clean_text(value):
    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return re.sub(r"\s+", " ", value)


def get_specs(product):
    return product.get("Specifications") or {}


def get_overview(product):
    return clean_text(product.get("Overview")) or ""


def get_name(product):
    return clean_text(product.get("Product Name")) or ""


def combined_text(product):
    specs = get_specs(product)

    parts = []

    for key, value in specs.items():
        if value:
            parts.append(f"{key}: {value}")

    overview = get_overview(product)
    name = get_name(product)

    if overview:
        parts.append(overview)

    if name:
        parts.append(name)

    return "\n".join(parts)


def find_spec(specs, names):
    """
    Find a specification using generic label matching.

    Exact labels are preferred, but we do not depend on
    one retailer's exact wording.
    """

    if not specs:
        return None

    normalized = {
        re.sub(r"\s+", " ", str(k).strip()).lower(): clean_text(v)
        for k, v in specs.items()
    }

    # Exact label
    for name in names:
        value = normalized.get(
            re.sub(r"\s+", " ", name.strip()).lower()
        )

        if value:
            return value

    # Partial label
    for key, value in normalized.items():

        if not value:
            continue

        for name in names:

            target = name.lower().strip()

            if target in key:
                return value

    return None


def first_number(text, minimum=None, maximum=None):
    if not text:
        return None

    matches = re.findall(
        r"\b\d+(?:\.\d+)?\b",
        text
    )

    for value in matches:

        number = float(value)

        if minimum is not None and number < minimum:
            continue

        if maximum is not None and number > maximum:
            continue

        return int(number) if number.is_integer() else number

    return None


# ============================================================
# GENERIC PATTERN EXTRACTORS
# ============================================================

def extract_socket(text):
    if not text:
        return None

    # Generic socket forms:
    # LGA 1700
    # LGA1700
    # AM5
    # AM4
    # sTRX4
    # TR4
    # SP5
    # SP6

    patterns = [
        r"\bLGA\s*\d{3,5}\b",
        r"\bsTRX\d+\b",
        r"\bSTRX\d+\b",
        r"\bTR\d+\b",
        r"\bSP\d+\b",
        r"\bAM\d+\+?\b",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return re.sub(
                r"\s+",
                "",
                match.group(0)
            ).upper()

    return None


def extract_all_sockets(text):
    if not text:
        return []

    patterns = [
        r"\bLGA\s*\d{3,5}\b",
        r"\bsTRX\d+\b",
        r"\bSTRX\d+\b",
        r"\bTR\d+\b",
        r"\bSP\d+\b",
        r"\bAM\d+\+?\b",
    ]

    found = []

    for pattern in patterns:

        for match in re.findall(
            pattern,
            text,
            re.IGNORECASE
        ):

            value = re.sub(
                r"\s+",
                "",
                match
            ).upper()

            if value not in found:
                found.append(value)

    return found


def extract_memory_type(text):
    if not text:
        return None

    match = re.search(
        r"\bDDR\s*([2-6])\b",
        text,
        re.IGNORECASE
    )

    if match:
        return f"DDR{match.group(1)}"

    return None


def extract_memory_speed(text):
    if not text:
        return None

    # DDR5-6000
    match = re.search(
        r"\bDDR[2-6]\s*[- ]\s*(\d{3,5})\b",
        text,
        re.IGNORECASE
    )

    if match:
        return f"{match.group(1)} MT/s"

    # 6000 MT/s
    match = re.search(
        r"\b(\d{3,6})\s*MT/s\b",
        text,
        re.IGNORECASE
    )

    if match:
        return f"{match.group(1)} MT/s"

    # 3200 MHz
    match = re.search(
        r"\b(\d{3,6})\s*MHz\b",
        text,
        re.IGNORECASE
    )

    if match:
        return f"{match.group(1)} MHz"

    return None


def extract_capacity(text):
    if not text:
        return None

    matches = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(GB|TB)\b",
        text,
        re.IGNORECASE
    )

    if not matches:
        return None

    values = []

    for number, unit in matches:

        value = float(number)

        if unit.upper() == "TB":
            value *= 1024

        values.append(value)

    if not values:
        return None

    value = max(values)

    return (
        f"{int(value)} GB"
        if value.is_integer()
        else f"{value} GB"
    )


def extract_form_factor(text):
    if not text:
        return None

    patterns = [
        (r"\bE[-\s]?ATX\b", "E-ATX"),
        (r"\bMicro[-\s]?ATX\b", "Micro-ATX"),
        (r"\bM[-\s]?ATX\b", "Micro-ATX"),
        (r"\bMATX\b", "Micro-ATX"),
        (r"\bMini[-\s]?ITX\b", "Mini-ITX"),
        (r"\bM[-\s]?ITX\b", "Mini-ITX"),
        (r"\bATX\b", "ATX"),
    ]

    for pattern, value in patterns:

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            return value

    return None


def extract_all_form_factors(text):
    if not text:
        return []

    found = []

    patterns = [
        (r"\bE[-\s]?ATX\b", "E-ATX"),
        (r"\bMicro[-\s]?ATX\b", "Micro-ATX"),
        (r"\bM[-\s]?ATX\b", "Micro-ATX"),
        (r"\bMATX\b", "Micro-ATX"),
        (r"\bMini[-\s]?ITX\b", "Mini-ITX"),
        (r"\bM[-\s]?ITX\b", "Mini-ITX"),
        (r"\bATX\b", "ATX"),
    ]

    for pattern, value in patterns:

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            if value not in found:
                found.append(value)

    return found


def extract_wattage(text):
    if not text:
        return None

    matches = re.findall(
        r"\b(\d{3,4})\s*W\b",
        text,
        re.IGNORECASE
    )

    valid = []

    for value in matches:

        wattage = int(value)

        if 200 <= wattage <= 3000:
            valid.append(wattage)

    if valid:
        return max(valid)

    return None


def extract_mm(text):
    if not text:
        return None

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*mm\b",
        text,
        re.IGNORECASE
    )

    if match:
        value = float(match.group(1))
        return int(value) if value.is_integer() else value

    return None


def extract_dimensions_first_value(text):
    if not text:
        return None

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*[x×]\s*"
        r"(\d+(?:\.\d+)?)\s*[x×]\s*"
        r"(\d+(?:\.\d+)?)\s*mm\b",
        text,
        re.IGNORECASE
    )

    if match:
        value = float(match.group(1))
        return int(value) if value.is_integer() else value

    return None


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_component_type(category):

    category = clean_text(category) or ""
    value = category.lower()

    if "motherboard" in value:
        return "motherboard"

    if (
        "graphics card" in value
        or "graphic card" in value
        or "gpu" in value
    ):
        return "graphics_card"

    if (
        "ram" in value
        or "memory" in value
    ):
        return "ram"

    if (
        "power supply" in value
        or "power supplies" in value
        or re.search(r"\bpsu\b", value)
    ):
        return "power_supply"

    if (
        "fan" in value
    ):
        return "fan"

    if (
        "cooling" in value
        or "cooler" in value
        or "aio" in value
    ):
        return "cooling"

    if (
        "case" in value
        or "chassis" in value
    ):
        return "case"

    return "unknown"


# ============================================================
# MOTHERBOARD
# ============================================================

def normalize_motherboard(product):

    specs = get_specs(product)
    overview = get_overview(product)
    name = get_name(product)

    text = combined_text(product)

    cpu = find_spec(
        specs,
        [
            "CPU Support",
            "CPU",
            "Processor",
            "CPU Socket",
            "Socket"
        ]
    ) or ""

    memory = find_spec(
        specs,
        [
            "Memory",
            "Memory Support",
            "Memory Type",
            "RAM",
            "RAM Type"
        ]
    ) or ""

    form_factor = find_spec(
        specs,
        [
            "Form Factor",
            "Motherboard Form Factor"
        ]
    ) or ""

    socket = extract_socket(cpu)

    if not socket:
        socket = extract_socket(text)

    memory_type = extract_memory_type(memory)

    if not memory_type:
        memory_type = extract_memory_type(text)

    form = extract_form_factor(form_factor)

    if not form:
        form = extract_form_factor(text)

    # Only extract memory slots when the text explicitly
    # associates the number with slots/DIMM.
    memory_slots = None

    slot_match = re.search(
        r"\b(\d+)\s*(?:x\s*)?"
        r"(?:DDR[2-6]\s*)?"
        r"(?:DIMM|memory)\s*slots?\b",
        text,
        re.IGNORECASE
    )

    if slot_match:
        memory_slots = int(slot_match.group(1))

    # Maximum supported RAM
    max_memory_gb = None

    max_match = re.search(
        r"(?:maximum|max\.?|max)\s*"
        r"(?:memory|ram|capacity)"
        r".{0,50}?"
        r"(\d+(?:\.\d+)?)\s*(GB|TB)",
        text,
        re.IGNORECASE
    )

    if max_match:

        value = float(max_match.group(1))

        if max_match.group(2).upper() == "TB":
            value *= 1024

        max_memory_gb = int(value)

    chipset = find_spec(
        specs,
        [
            "Chipset",
            "Chipset Type"
        ]
    )

    return {
        "type": "motherboard",
        "socket": socket,
        "memory_type": memory_type,
        "memory_slots": memory_slots,
        "max_memory_gb": max_memory_gb,
        "form_factor": form,
        "chipset": chipset
    }


# ============================================================
# RAM
# ============================================================

def normalize_ram(product):

    specs = get_specs(product)
    overview = get_overview(product)
    name = get_name(product)

    text = combined_text(product)

    memory = find_spec(
        specs,
        [
            "Memory Type",
            "Memory",
            "Type",
            "RAM Type"
        ]
    ) or ""

    speed = find_spec(
        specs,
        [
            "Speed",
            "Memory Speed",
            "Frequency",
            "Memory Frequency"
        ]
    ) or ""

    capacity = find_spec(
        specs,
        [
            "Capacity",
            "Memory Capacity",
            "Size",
            "Total Capacity"
        ]
    ) or ""

    form_factor = find_spec(
        specs,
        [
            "Form Factor",
            "Memory Form Factor"
        ]
    )

    memory_type = extract_memory_type(memory)

    if not memory_type:
        memory_type = extract_memory_type(text)

    speed_value = extract_memory_speed(speed)

    if not speed_value:
        speed_value = extract_memory_speed(text)

    capacity_value = extract_capacity(capacity)

    if not capacity_value:
        capacity_value = extract_capacity(text)

    return {
        "type": "ram",
        "memory_type": memory_type,
        "speed": speed_value,
        "capacity": capacity_value,
        "form_factor": form_factor
    }


# ============================================================
# GRAPHICS CARD
# ============================================================

def normalize_graphics_card(product):

    specs = get_specs(product)
    text = combined_text(product)

    interface = find_spec(
        specs,
        [
            "Interface",
            "Bus Interface",
            "Bus",
            "Interface Type"
        ]
    )

    length_text = find_spec(
        specs,
        [
            "Card Length",
            "Length",
            "GPU Length",
            "Graphics Card Length",
            "Dimensions",
            "Card Dimensions",
            "Product Dimensions"
        ]
    )

    length_mm = extract_dimensions_first_value(
        length_text
    )

    if length_mm is None:
        length_mm = extract_mm(length_text)

    if length_mm is None:

        match = re.search(
            r"(?:card|gpu|graphics card)"
            r".{0,60}?"
            r"(\d+(?:\.\d+)?)\s*mm",
            text,
            re.IGNORECASE
        )

        if match:
            length_mm = float(match.group(1))

    recommended = find_spec(
        specs,
        [
            "Recommended PSU",
            "Recommended Power Supply",
            "Power Supply Recommendation",
            "Recommended Power"
        ]
    )

    recommended_psu_wattage = extract_wattage(
        recommended
    )

    if recommended_psu_wattage is None:

        match = re.search(
            r"(?:recommended|suggested)"
            r".{0,80}?"
            r"(\d{3,4})\s*W",
            text,
            re.IGNORECASE
        )

        if match:
            recommended_psu_wattage = int(
                match.group(1)
            )

    return {
        "type": "graphics_card",
        "interface": interface,
        "length_mm": length_mm,
        "recommended_psu_wattage":
            recommended_psu_wattage
    }


# ============================================================
# CASE
# ============================================================

def normalize_case(product):

    specs = get_specs(product)
    text = combined_text(product)

    motherboard = find_spec(
        specs,
        [
            "Motherboard Support",
            "Motherboard Compatibility",
            "Supported Motherboards",
            "Motherboard Form Factor"
        ]
    )

    gpu = find_spec(
        specs,
        [
            "GPU Clearance",
            "Graphics Card Length",
            "Maximum GPU Length",
            "Maximum Graphics Card Length"
        ]
    )

    fan = find_spec(
        specs,
        [
            "Fan Support",
            "Cooling Support",
            "Fan Compatibility"
        ]
    )

    motherboard_support = extract_all_form_factors(
        motherboard or ""
    )

    if not motherboard_support:
        motherboard_support = extract_all_form_factors(
            text
        )

    gpu_clearance_mm = None

    gpu_match = re.search(
        r"(?:GPU|graphics card|video card|VGA)"
        r".{0,100}?"
        r"(\d+(?:\.\d+)?)\s*mm",
        text,
        re.IGNORECASE
    )

    if gpu_match:
        gpu_clearance_mm = float(
            gpu_match.group(1)
        )

    fan_support = fan

    return {
        "type": "case",
        "motherboard_support": motherboard_support,
        "gpu_clearance_mm": gpu_clearance_mm,
        "fan_support": fan_support
    }


# ============================================================
# POWER SUPPLY
# ============================================================

def normalize_power_supply(product):

    specs = get_specs(product)

    name = get_name(product)
    overview = get_overview(product)

    wattage = extract_wattage(name)

    if wattage is None:

        power_spec = find_spec(
            specs,
            [
                "Total Power",
                "Maximum Power",
                "Power Output",
                "Rated Power",
                "Wattage",
                "Total Wattage"
            ]
        )

        wattage = extract_wattage(
            power_spec
        )

    if wattage is None:
        wattage = extract_wattage(
            overview
        )

    return {
        "type": "power_supply",
        "wattage": wattage
    }


# ============================================================
# COOLING
# ============================================================

def normalize_cooling(product):

    specs = get_specs(product)
    text = combined_text(product)

    socket_text = find_spec(
        specs,
        [
            "Socket Support",
            "CPU Socket",
            "Supported Sockets",
            "Compatibility",
            "CPU Compatibility"
        ]
    )

    sockets = extract_all_sockets(
        socket_text or ""
    )

    if not sockets:
        sockets = extract_all_sockets(text)

    radiator_size = None

    match = re.search(
        r"(?:radiator|rad)"
        r".{0,50}?"
        r"(\d{2,4})\s*mm",
        text,
        re.IGNORECASE
    )

    if match:
        radiator_size = int(
            match.group(1)
        )

    return {
        "type": "cooling",
        "socket_support": sockets,
        "radiator_size_mm": radiator_size
    }


# ============================================================
# FAN
# ============================================================

def normalize_fan(product):

    specs = get_specs(product)
    text = combined_text(product)

    size = find_spec(
        specs,
        [
            "Size",
            "Fan Size",
            "Dimensions",
            "Fan Dimensions"
        ]
    )

    size_mm = extract_mm(
        size or ""
    )

    if size_mm is None:

        match = re.search(
            r"\b(\d{2,3})\s*mm\b",
            text,
            re.IGNORECASE
        )

        if match:
            size_mm = int(
                match.group(1)
            )

    return {
        "type": "fan",
        "size": size,
        "size_mm": size_mm
    }


# ============================================================
# NORMALIZE PRODUCT
# ============================================================

def normalize_product(product):

    category = product.get(
        "Category",
        ""
    )

    component_type = detect_component_type(
        category
    )

    if component_type == "motherboard":
        compatibility = normalize_motherboard(product)

    elif component_type == "ram":
        compatibility = normalize_ram(product)

    elif component_type == "graphics_card":
        compatibility = normalize_graphics_card(product)

    elif component_type == "case":
        compatibility = normalize_case(product)

    elif component_type == "power_supply":
        compatibility = normalize_power_supply(product)

    elif component_type == "cooling":
        compatibility = normalize_cooling(product)

    elif component_type == "fan":
        compatibility = normalize_fan(product)

    else:
        compatibility = {
            "type": "unknown"
        }

    return {
        "Product ID": product.get("Product ID"),
        "Product Name": product.get("Product Name"),
        "Category": category,
        "Brand": product.get("Brand"),
        "Price": product.get("Price"),
        "Product URL": product.get("Product URL"),
        "Image": product.get("Image"),
        "Compatibility": compatibility
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

    normalized_products = [
        normalize_product(product)
        for product in products
    ]

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

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    counts = {}
    useful_counts = {}

    for product in normalized_products:

        compatibility = product.get(
            "Compatibility",
            {}
        )

        component_type = compatibility.get(
            "type",
            "unknown"
        )

        counts[component_type] = (
            counts.get(component_type, 0) + 1
        )

        useful = any(
            value not in (None, "", [], {})
            for key, value
            in compatibility.items()
            if key != "type"
        )

        if useful:
            useful_counts[component_type] = (
                useful_counts.get(
                    component_type,
                    0
                ) + 1
            )

    print()
    print("=" * 65)
    print("NORMALIZATION COMPLETE")
    print("=" * 65)

    for component_type, count in counts.items():

        print(
            f"{component_type}: "
            f"{count} "
            f"({useful_counts.get(component_type, 0)} "
            f"with useful compatibility data)"
        )

    print()
    print(
        "Products with useful compatibility data: "
        f"{sum(useful_counts.values())}"
    )

    print()
    print(
        f"Output file: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()