import json
import re


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "pc_components_data.json"
OUTPUT_FILE = "pc_components_normalized.json"


# ============================================================
# PC BUILDER CATEGORIES
# ============================================================
# Only products in these categories are assigned a PC Builder
# component type. Everything else becomes type = unknown.
# ============================================================

PC_BUILDER_CATEGORIES = {

    "processor": [
        "PC Components > Processors / CPUs",
        "PC Components > Processors / CPUs > Intel Processors",
        "PC Components > Processors / CPUs > AMD Processors",
    ],

    "motherboard": [
        "PC Components > Motherboards",
        "PC Components > Motherboards > Intel",
        "PC Components > Motherboards > AMD",
        "PC Components > Motherboards > Intel Motherboards",
        "PC Components > Motherboards > AMD Motherboards",
    ],

    "ram": [
        "PC Components > RAM",
    ],

    "graphics_card": [
        "PC Components > Graphics Cards",
        "PC Components > Graphics Cards > NVIDIA",
        "PC Components > Graphics Cards > AMD",
        "PC Components > Graphics Cards > NVIDIA Graphic Cards",
        "PC Components > Graphics Cards > AMD Graphic Cards",
    ],

    "case": [
        "PC Components > Cases",
        "PC Components > PC Cases",
    ],

    "cooling": [
        "PC Components > Cooling",
    ],

    "power_supply": [
        "PC Components > Power Supplies",
    ],

}


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
    parts = []

    for key, value in get_specs(product).items():
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
    """Return the first matching specification value.

    Exact key matches are preferred. Partial key matches are used
    only when an exact key is not available.
    """

    if not specs:
        return None

    normalized = {}

    for key, value in specs.items():
        normalized_key = re.sub(r"\s+", " ", str(key).strip()).lower()
        normalized[normalized_key] = clean_text(value)

    # Exact labels first.
    for name in names:
        target = re.sub(r"\s+", " ", name.strip()).lower()
        value = normalized.get(target)

        if value:
            return value

    # Then partial labels.
    for key, value in normalized.items():
        if not value:
            continue

        for name in names:
            target = name.strip().lower()
            if target in key:
                return value

    return None


# ============================================================
# CATEGORY NORMALIZATION
# ============================================================


def normalize_category(value):
    if not value:
        return ""

    value = str(value).strip()
    value = re.sub(r"\s* > \s*", " > ", value)
    value = re.sub(r"\s+", " ", value)
    return value.lower()


def get_category_parts(category):
    normalized = normalize_category(category)

    if not normalized:
        return []

    return [
        part.strip()
        for part in normalized.split(">")
        if part.strip()
    ]


def get_pc_builder_type(category):
    category_normalized = normalize_category(category)

    if not category_normalized:
        return "unknown"

    # Exact full category match.
    for component_type, categories in PC_BUILDER_CATEGORIES.items():
        for allowed_category in categories:
            if category_normalized == normalize_category(allowed_category):
                return component_type

    # Leaf match for short category variants.
    parts = get_category_parts(category)

    if not parts:
        return "unknown"

    leaf = parts[-1]

    for component_type, categories in PC_BUILDER_CATEGORIES.items():
        for allowed_category in categories:
            allowed_parts = get_category_parts(allowed_category)
            if allowed_parts and leaf == allowed_parts[-1]:
                return component_type

    return "unknown"


# ============================================================
# SOCKET EXTRACTION
# ============================================================


def normalize_socket_value(value):
    if not value:
        return None

    text = str(value).strip().upper()
    text = re.sub(r"[\s\-]", "", text)

    # Intel product specifications often use FCLGA1700/FCLGA1851.
    # Canonical form used everywhere in the builder is LGA1700/LGA1851.
    text = re.sub(r"^FCLGA", "LGA", text)

    return text


def extract_socket(text):
    if not text:
        return None

    patterns = [
        # Intel
        r"\bFCLGA\s*\d{3,5}\b",
        r"\bLGA\s*\d{3,5}\b",

        # AMD workstation/server
        r"\bsTRX\s*\d+\b",
        r"\bSTRX\s*\d+\b",
        r"\bTR\s*\d+\b",
        r"\bSP\s*\d+\b",

        # AMD desktop
        r"\bAM\s*\d+\+?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, str(text), re.IGNORECASE)
        if match:
            return normalize_socket_value(match.group(0))

    return None


def extract_all_sockets(text):
    if not text:
        return []

    patterns = [
        r"\bFCLGA\s*\d{3,5}\b",
        r"\bLGA\s*\d{3,5}\b",
        r"\bsTRX\s*\d+\b",
        r"\bSTRX\s*\d+\b",
        r"\bTR\s*\d+\b",
        r"\bSP\s*\d+\b",
        r"\bAM\s*\d+\+?\b",
    ]

    found = []

    for pattern in patterns:
        for match in re.findall(pattern, str(text), re.IGNORECASE):
            value = normalize_socket_value(match)

            if value and value not in found:
                found.append(value)

    return found


# ============================================================
# MEMORY EXTRACTION
# ============================================================


def extract_memory_type(text):
    if not text:
        return None

    match = re.search(
        r"\bDDR\s*([2-6])\b",
        str(text),
        re.IGNORECASE,
    )

    if match:
        return f"DDR{match.group(1)}"

    return None


def extract_all_memory_types(text):
    if not text:
        return []

    found = []

    for match in re.findall(
        r"\bDDR\s*([2-6])\b",
        str(text),
        re.IGNORECASE,
    ):
        value = f"DDR{match}"

        if value not in found:
            found.append(value)

    return found


def extract_memory_speed(text):
    if not text:
        return None

    # DDR5-6000 / DDR5 6000
    match = re.search(
        r"\bDDR[2-6]\s*[- ]\s*(\d{3,5})\b",
        str(text),
        re.IGNORECASE,
    )

    if match:
        return f"{match.group(1)} MT/s"

    # 6000 MT/s
    match = re.search(
        r"\b(\d{3,6})\s*MT/s\b",
        str(text),
        re.IGNORECASE,
    )

    if match:
        return f"{match.group(1)} MT/s"

    # 3200 MHz
    match = re.search(
        r"\b(\d{3,6})\s*MHz\b",
        str(text),
        re.IGNORECASE,
    )

    if match:
        return f"{match.group(1)} MHz"

    return None


def extract_capacity(text):
    if not text:
        return None

    matches = re.findall(
        r"\b(\d+(?:\.\d+)?)\s*(GB|TB)\b",
        str(text),
        re.IGNORECASE,
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

    if value.is_integer():
        return f"{int(value)} GB"

    return f"{value} GB"


def memory_form_factor(text):
    if not text:
        return None

    text = str(text).lower()

    if any(token in text for token in [
        "so-dimm",
        "sodimm",
        "laptop",
        "notebook",
    ]):
        return "SO-DIMM"

    if any(token in text for token in [
        "u-dimm",
        "udimm",
        "desktop",
        "dimm",
    ]):
        return "DIMM"

    return None


# ============================================================
# FORM FACTOR EXTRACTION
# ============================================================


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
        if re.search(pattern, str(text), re.IGNORECASE):
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
        if re.search(pattern, str(text), re.IGNORECASE):
            if value not in found:
                found.append(value)

    return found


def normalize_form_factor(value):
    return extract_form_factor(value)


# ============================================================
# NUMERIC EXTRACTION
# ============================================================


def extract_wattage(text):
    if not text:
        return None

    matches = re.findall(
        r"\b(\d{3,4})\s*W\b",
        str(text),
        re.IGNORECASE,
    )

    valid = []

    for value in matches:
        wattage = int(value)

        if 200 <= wattage <= 3000:
            valid.append(wattage)

    return max(valid) if valid else None


def extract_mm(text):
    if not text:
        return None

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*mm\b",
        str(text),
        re.IGNORECASE,
    )

    if not match:
        return None

    value = float(match.group(1))

    return int(value) if value.is_integer() else value


def extract_dimensions_first_value(text):
    if not text:
        return None

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*[x×]\s*"
        r"(\d+(?:\.\d+)?)\s*[x×]\s*"
        r"(\d+(?:\.\d+)?)\s*mm\b",
        str(text),
        re.IGNORECASE,
    )

    if not match:
        return None

    value = float(match.group(1))
    return int(value) if value.is_integer() else value


# ============================================================
# PROCESSOR / CPU
# ============================================================


def normalize_processor(product):
    specs = get_specs(product)
    text = combined_text(product)

    socket_text = find_spec(
        specs,
        [
            "Socket",
            "CPU Socket",
            "Processor Socket",
            "Socket Type",
            "Sockets Supported",
            "Supported Sockets",
            "Package",
        ],
    ) or ""

    socket = extract_socket(socket_text)

    if not socket:
        socket = extract_socket(text)

    memory_text = find_spec(
        specs,
        [
            "Memory Type",
            "Memory Support",
            "System Memory Type",
            "System Memory",
            "Memory",
            "RAM",
        ],
    ) or ""

    memory_type = extract_memory_type(memory_text)

    if not memory_type:
        memory_type = extract_memory_type(text)

    memory_types = extract_all_memory_types(memory_text)

    if not memory_types:
        memory_types = extract_all_memory_types(text)

    return {
        "type": "processor",
        "socket": socket,
        "memory_type": memory_type,
        "memory_types": memory_types,
    }


# ============================================================
# MOTHERBOARD SOCKET INFERENCE
# ============================================================


def infer_motherboard_socket(product):
    """
    Recover a motherboard socket when the scraped Specifications
    object is empty or does not contain a socket field.

    This uses the motherboard's explicit Intel/AMD category plus
    well-defined chipset/model families. It does NOT infer a socket
    from arbitrary product-name text.
    """
    category = normalize_category(product.get("Category")).upper()
    name = get_name(product).upper()
    specs = get_specs(product)

    # Prefer an explicit chipset field when available.
    chipset = find_spec(
        specs,
        ["Chipset", "Chipset Type"]
    ) or ""

    source = f"{name} {chipset}".upper()

    is_intel = (
        "MOTHERBOARDS > INTEL" in category
        or "INTEL MOTHERBOARDS" in category
    )
    is_amd = (
        "MOTHERBOARDS > AMD" in category
        or "AMD MOTHERBOARDS" in category
    )

    if is_intel:
        # LGA1851 desktop chipset families.
        if re.search(r"\b(?:Z890|B860[A-Z-]*|H810[A-Z-]*)\b", source):
            return "LGA1851"

        # LGA1700 desktop chipset families.
        if re.search(
            r"\b(?:Z790|Z690|B760[A-Z-]*|B660[A-Z-]*|B760E[A-Z-]*|H770[A-Z-]*|H670[A-Z-]*|H610[A-Z-]*|Q670[A-Z-]*|W680[A-Z-]*)\b",
            source
        ):
            return "LGA1700"

        # LGA1200 desktop chipset families.
        if re.search(r"\b(?:Z590|Z490|B560[A-Z-]*|B460[A-Z-]*|H570[A-Z-]*|H510[A-Z-]*|H470[A-Z-]*|H410[A-Z-]*|W480[A-Z-]*)\b", source):
            return "LGA1200"

        # LGA1151 desktop chipset families.
        if re.search(r"\b(?:Z390|Z370|B365|B360|H370|H310|H270|B250|H110)\b", source):
            return "LGA1151"

    if is_amd:
        # AM5 desktop chipset families.
        if re.search(
            r"\b(?:X870E|X870|X670E|X670|B850|B840|B650E|B650|A620)\b",
            source
        ):
            return "AM5"

        # AM4 desktop chipset families.
        if re.search(
            r"\b(?:X570[A-Z-]*|B550[A-Z-]*|A520[A-Z-]*|B450[A-Z-]*|X470[A-Z-]*|B350[A-Z-]*|X370[A-Z-]*|A320[A-Z-]*)\b",
            source
        ):
            return "AM4"

    return None


# ============================================================
# MOTHERBOARD
# ============================================================


def normalize_motherboard(product):
    specs = get_specs(product)
    text = combined_text(product)

    cpu_text = find_spec(
        specs,
        [
            "CPU Support",
            "CPU Socket",
            "CPU",
            "Processor",
            "Socket",
            "Sockets Supported",
        ],
    ) or ""

    socket = extract_socket(cpu_text)

    if not socket:
        socket = extract_socket(text)

    # Some scraped motherboard records have Specifications = {}.
    # Recover the socket from an unambiguous chipset/model family.
    if not socket:
        socket = infer_motherboard_socket(product)

    memory_text = find_spec(
        specs,
        [
            "Memory",
            "Memory Support",
            "System Memory Type",
            "Memory Type",
            "RAM",
            "RAM Type",
        ],
    ) or ""

    memory_type = extract_memory_type(memory_text)

    if not memory_type:
        memory_type = extract_memory_type(text)

    memory_types = extract_all_memory_types(memory_text)

    if not memory_types:
        memory_types = extract_all_memory_types(text)

    form_factor_text = find_spec(
        specs,
        [
            "Form Factor",
            "Motherboard Form Factor",
        ],
    ) or ""

    form_factor = extract_form_factor(form_factor_text)

    if not form_factor:
        form_factor = extract_form_factor(text)

    memory_slots = None

    slot_patterns = [
        r"\b(\d+)\s*(?:x\s*)?(?:DDR[2-6]\s*)?DIMM\s*slots?\b",
        r"\b(\d+)\s*(?:x\s*)?(?:DDR[2-6]\s*)?memory\s*slots?\b",
    ]

    for pattern in slot_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            memory_slots = int(match.group(1))
            break

    max_memory_gb = None

    max_match = re.search(
        r"(?:maximum|max\.?|max)\s*"
        r"(?:memory|ram|capacity)"
        r".{0,80}?"
        r"(\d+(?:\.\d+)?)\s*(GB|TB)",
        text,
        re.IGNORECASE,
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
            "Chipset Type",
        ],
    )

    return {
        "type": "motherboard",
        "socket": socket,
        "memory_type": memory_type,
        "memory_types": memory_types,
        "memory_slots": memory_slots,
        "max_memory_gb": max_memory_gb,
        "form_factor": form_factor,
        "chipset": chipset,
    }


# ============================================================
# RAM
# ============================================================


def normalize_ram(product):
    specs = get_specs(product)
    text = combined_text(product)

    memory_text = find_spec(
        specs,
        [
            "Memory Type",
            "Memory",
            "System Memory Type",
            "Type",
            "RAM Type",
        ],
    ) or ""

    memory_type = extract_memory_type(memory_text)

    if not memory_type:
        memory_type = extract_memory_type(text)

    memory_types = extract_all_memory_types(memory_text)

    if not memory_types:
        memory_types = extract_all_memory_types(text)

    speed_text = find_spec(
        specs,
        [
            "Speed",
            "Memory Speed",
            "Frequency",
            "Memory Frequency",
        ],
    ) or ""

    speed_value = extract_memory_speed(speed_text)

    if not speed_value:
        speed_value = extract_memory_speed(text)

    capacity_text = find_spec(
        specs,
        [
            "Capacity",
            "Memory Capacity",
            "Size",
            "Total Capacity",
        ],
    ) or ""

    capacity_value = extract_capacity(capacity_text)

    if not capacity_value:
        capacity_value = extract_capacity(text)

    form_factor_text = find_spec(
        specs,
        [
            "Form Factor",
            "Memory Form Factor",
        ],
    ) or ""

    form_factor = memory_form_factor(form_factor_text)

    if not form_factor:
        form_factor = memory_form_factor(memory_text)

    if not form_factor:
        form_factor = memory_form_factor(text)

    return {
        "type": "ram",
        "memory_type": memory_type,
        "memory_types": memory_types,
        "speed": speed_value,
        "capacity": capacity_value,
        "form_factor": form_factor,
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
            "Interface Type",
        ],
    )

    length_text = find_spec(
        specs,
        [
            "Card Length",
            "GPU Length",
            "Graphics Card Length",
            "Length",
        ],
    ) or ""

    length_mm = extract_dimensions_first_value(length_text)

    if length_mm is None:
        length_mm = extract_mm(length_text)

    recommended_text = find_spec(
        specs,
        [
            "Recommended PSU",
            "Recommended Power Supply",
            "Power Supply Recommendation",
            "Recommended Power",
        ],
    ) or ""

    recommended_psu_wattage = extract_wattage(recommended_text)

    if recommended_psu_wattage is None:
        match = re.search(
            r"(?:recommended|suggested).{0,80}?"
            r"(\d{3,4})\s*W",
            text,
            re.IGNORECASE,
        )

        if match:
            recommended_psu_wattage = int(match.group(1))

    return {
        "type": "graphics_card",
        "interface": interface,
        "length_mm": length_mm,
        "recommended_psu_wattage": recommended_psu_wattage,
    }


# ============================================================
# CASE
# ============================================================


def normalize_case(product):
    specs = get_specs(product)
    text = combined_text(product)

    motherboard_text = find_spec(
        specs,
        [
            "Motherboard Support",
            "Motherboard Compatibility",
            "Supported Motherboards",
            "Motherboard Form Factor",
        ],
    ) or ""

    motherboard_support = extract_all_form_factors(motherboard_text)

    if not motherboard_support:
        motherboard_support = extract_all_form_factors(text)

    gpu_text = find_spec(
        specs,
        [
            "GPU Clearance",
            "Maximum GPU Length",
            "Maximum Graphics Card Length",
            "Graphics Card Length",
        ],
    ) or ""

    gpu_clearance_mm = None

    # Prefer the actual GPU-clearance specification.
    clearance_match = re.search(
        r"(\d+(?:\.\d+)?)\s*mm",
        gpu_text,
        re.IGNORECASE,
    )

    if clearance_match:
        gpu_clearance_mm = float(clearance_match.group(1))

    if gpu_clearance_mm is None:
        match = re.search(
            r"(?:GPU|graphics card|video card|VGA)"
            r".{0,100}?"
            r"(\d+(?:\.\d+)?)\s*mm",
            text,
            re.IGNORECASE,
        )

        if match:
            gpu_clearance_mm = float(match.group(1))

    fan_support = find_spec(
        specs,
        [
            "Fan Support",
            "Cooling Support",
            "Fan Compatibility",
        ],
    )

    return {
        "type": "case",
        "motherboard_support": motherboard_support,
        "gpu_clearance_mm": gpu_clearance_mm,
        "fan_support": fan_support,
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
        power_text = find_spec(
            specs,
            [
                "Total Power",
                "Maximum Power",
                "Power Output",
                "Rated Power",
                "Wattage",
                "Total Wattage",
            ],
        )

        wattage = extract_wattage(power_text)

    if wattage is None:
        wattage = extract_wattage(overview)

    return {
        "type": "power_supply",
        "wattage": wattage,
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
            "CPU Compatibility",
        ],
    ) or ""

    sockets = extract_all_sockets(socket_text)

    if not sockets:
        sockets = extract_all_sockets(text)

    radiator_size = None

    match = re.search(
        r"(?:radiator|rad).{0,50}?"
        r"(\d{2,4})\s*mm",
        text,
        re.IGNORECASE,
    )

    if match:
        radiator_size = int(match.group(1))

    return {
        "type": "cooling",
        "socket_support": sockets,
        "radiator_size_mm": radiator_size,
    }


# ============================================================
# FAN
# ============================================================


def normalize_fan(product):
    specs = get_specs(product)
    text = combined_text(product)

    size_text = find_spec(
        specs,
        [
            "Size",
            "Fan Size",
            "Dimensions",
            "Fan Dimensions",
        ],
    ) or ""

    size_mm = extract_mm(size_text)

    if size_mm is None:
        match = re.search(
            r"\b(\d{2,3})\s*mm\b",
            text,
            re.IGNORECASE,
        )

        if match:
            size_mm = int(match.group(1))

    return {
        "type": "fan",
        "size": size_text or None,
        "size_mm": size_mm,
    }


# ============================================================
# NORMALIZE PRODUCT
# ============================================================


def normalize_product(product):
    category = clean_text(product.get("Category")) or ""
    component_type = get_pc_builder_type(category)

    if component_type == "processor":
        compatibility = normalize_processor(product)

    elif component_type == "motherboard":
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
        compatibility = {"type": "unknown"}

    return {
        "Product ID": product.get("Product ID"),
        "Product Name": product.get("Product Name"),
        "Category": category,
        "Brand": product.get("Brand"),
        "Price": product.get("Price"),
        "Product URL": product.get("Product URL"),
        "Image": product.get("Image"),
        "Compatibility": compatibility,
    }


# ============================================================
# VALIDATION / DIAGNOSTICS
# ============================================================


def validate_normalized_products(products):
    """Print useful diagnostics so missing compatibility data is visible."""

    print()
    print("COMPATIBILITY DATA CHECK")
    print("-" * 65)

    for component_type in [
        "processor",
        "motherboard",
        "ram",
        "graphics_card",
        "case",
        "cooling",
        "power_supply",
    ]:
        items = [
            p for p in products
            if p.get("Compatibility", {}).get("type") == component_type
        ]

        if not items:
            continue

        print(f"{component_type}: {len(items)}")

        missing = []

        for product in items:
            comp = product.get("Compatibility", {})

            if component_type in ("processor", "motherboard"):
                if not comp.get("socket"):
                    missing.append(product.get("Product Name", "Unknown"))

        if missing:
            print(f"  WARNING: {len(missing)} missing socket")
            for name in missing[:10]:
                print(f"    - {name}")


# ============================================================
# MAIN
# ============================================================


def main():

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as file:
            products = json.load(file)

    except FileNotFoundError:
        print()
        print(f"ERROR: Could not find '{INPUT_FILE}'.")
        print("Make sure pc_components_data.json is in the same folder as normalize.py.")
        return

    except json.JSONDecodeError as error:
        print()
        print(f"ERROR: Invalid JSON in '{INPUT_FILE}'.")
        print(error)
        return

    print()
    print("=" * 65)
    print("PC BUILDER NORMALIZER")
    print("=" * 65)
    print()
    print(f"Products loaded: {len(products)}")

    normalized_products = [
        normalize_product(product)
        for product in products
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            normalized_products,
            file,
            indent=4,
            ensure_ascii=False,
        )

    counts = {}
    useful_counts = {}
    unknown_categories = {}

    for product in normalized_products:
        compatibility = product.get("Compatibility", {})
        component_type = compatibility.get("type", "unknown")

        counts[component_type] = counts.get(component_type, 0) + 1

        useful = any(
            value not in (None, "", [], {})
            for key, value in compatibility.items()
            if key != "type"
        )

        if useful:
            useful_counts[component_type] = (
                useful_counts.get(component_type, 0) + 1
            )

        if component_type == "unknown":
            category = product.get("Category") or "No Category"
            unknown_categories[category] = (
                unknown_categories.get(category, 0) + 1
            )

    print()
    print("=" * 65)
    print("NORMALIZATION COMPLETE")
    print("=" * 65)

    print()
    print("PC BUILDER COMPONENTS")
    print("-" * 65)

    for component_type in sorted(
        key for key in counts if key != "unknown"
    ):
        print(
            f"{component_type}: {counts[component_type]} "
            f"({useful_counts.get(component_type, 0)} with useful compatibility data)"
        )

    unknown_count = counts.get("unknown", 0)

    print()
    print(f"Unknown / excluded products: {unknown_count}")

    if unknown_categories:
        print()
        print("EXCLUDED CATEGORIES")
        print("-" * 65)

        for category, count in sorted(
            unknown_categories.items(),
            key=lambda item: (-item[1], item[0]),
        ):
            print(f"{category}: {count}")

    useful_total = sum(useful_counts.values())

    print()
    print(f"Products with useful compatibility data: {useful_total}")
    print(f"Total products processed: {len(normalized_products)}")
    print(f"Output file: {OUTPUT_FILE}")

    validate_normalized_products(normalized_products)

    print()
    print("=" * 65)


if __name__ == "__main__":
    main()