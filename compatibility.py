import json
import re


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "pc_components_normalized.json"


# ============================================================
# BASIC HELPERS
# ============================================================

def clean(value):

    if value is None:
        return None

    value = str(value).strip()

    if not value:
        return None

    return re.sub(r"\s+", " ", value)


def is_known(value):

    return value not in (None, "", [], {})


def normalize_text(value):

    value = clean(value)

    if not value:
        return ""

    return value.lower()


# ============================================================
# DISPLAY
# ============================================================

def print_header(title):

    print()
    print("=" * 65)
    print(title)
    print("=" * 65)


def print_products(products):

    for index, product in enumerate(products, 1):

        print(
            f"{index}. "
            f"{product.get('Product Name', 'Unknown')}"
        )


def choose_product(products, component_type):

    print_header(component_type.upper())

    if not products:

        print(
            f"No {component_type.lower()} products "
            f"are available."
        )

        return None

    print_products(products)

    while True:

        try:

            choice = int(
                input(
                    f"\nChoose {component_type.lower()} "
                    f"(1-{len(products)}): "
                )
            )

            if 1 <= choice <= len(products):

                return products[choice - 1]

        except ValueError:

            pass

        print(
            "Invalid selection. Please try again."
        )


# ============================================================
# COMPONENT FILTERING
# ============================================================

def get_components(products, component_type):

    return [
        product
        for product in products
        if product.get(
            "Compatibility",
            {}
        ).get("type") == component_type
    ]


# ============================================================
# NORMALIZED VALUES
# ============================================================

def compatibility(product):

    if not product:
        return {}

    return product.get(
        "Compatibility",
        {}
    ) or {}


def get_value(product, key):

    return compatibility(product).get(key)


# ============================================================
# MEMORY
# ============================================================

def memory_generation(value):

    if not value:
        return None

    match = re.search(
        r"\bDDR\s*([2-6])\b",
        str(value),
        re.IGNORECASE
    )

    if match:

        return f"DDR{match.group(1)}"

    return None


def memory_form_factor(value):

    if not value:
        return None

    text = normalize_text(value)

    # --------------------------------------------------------
    # Laptop memory
    # --------------------------------------------------------

    if (
        "so-dimm" in text
        or "sodimm" in text
        or "laptop" in text
        or "notebook" in text
    ):

        return "SO-DIMM"

    # --------------------------------------------------------
    # Desktop memory
    # --------------------------------------------------------

    if (
        "u-dimm" in text
        or "udimm" in text
        or "desktop" in text
        or "dimm" in text
    ):

        return "DIMM"

    return None


def check_motherboard_ram(
    motherboard,
    ram
):

    mb_memory = get_value(
        motherboard,
        "memory_type"
    )

    ram_memory = get_value(
        ram,
        "memory_type"
    )

    mb_generation = memory_generation(
        mb_memory
    )

    ram_generation = memory_generation(
        ram_memory
    )

    incompatible = False

    # --------------------------------------------------------
    # Generation
    # --------------------------------------------------------

    if (
        not mb_generation
        or not ram_generation
    ):

        print(
            "⚠ Motherboard/RAM memory generation "
            "could not be verified."
        )

    elif mb_generation != ram_generation:

        print(
            f"✗ Motherboard uses {mb_generation}, "
            f"RAM is {ram_generation}."
        )

        incompatible = True

    else:

        print(
            f"✓ Motherboard uses {mb_generation} "
            f"and RAM is {ram_generation}."
        )

    # --------------------------------------------------------
    # Desktop vs laptop memory
    # --------------------------------------------------------

    ram_form = memory_form_factor(
        ram_memory
    )

    if ram_form == "SO-DIMM":

        print(
            "✗ RAM is SO-DIMM/laptop memory; "
            "this motherboard requires desktop DIMM memory."
        )

        incompatible = True

    elif ram_form == "DIMM":

        print(
            "✓ RAM is desktop DIMM memory."
        )

    else:

        print(
            "⚠ RAM form factor could not be verified."
        )

    return not incompatible


# ============================================================
# SOCKET NORMALIZATION
# ============================================================

def normalize_socket(socket):

    if not socket:
        return None

    text = str(socket).upper()

    text = re.sub(
        r"[\s\-]",
        "",
        text
    )

    return text


def check_motherboard_cooling(
    motherboard,
    cooling
):

    motherboard_socket = normalize_socket(
        get_value(
            motherboard,
            "socket"
        )
    )

    supported_sockets = get_value(
        cooling,
        "socket_support"
    )

    if not motherboard_socket:

        print(
            "⚠ Motherboard socket could not be verified."
        )

        return None

    if not supported_sockets:

        print(
            "⚠ Cooling socket support could not be verified."
        )

        return None

    if isinstance(
        supported_sockets,
        str
    ):

        supported_sockets = [
            supported_sockets
        ]

    normalized_supported = [

        normalize_socket(socket)

        for socket in supported_sockets

        if socket
    ]

    if motherboard_socket in normalized_supported:

        print(
            f"✓ Cooling supports {motherboard_socket}."
        )

        return True

    print(
        f"✗ Cooling does not list support for "
        f"{motherboard_socket}."
    )

    return False


# ============================================================
# FORM FACTOR
# ============================================================

def normalize_form_factor(value):

    if not value:
        return None

    text = normalize_text(value)

    # IMPORTANT:
    # Check E-ATX before ATX because E-ATX contains "ATX".

    if (
        "e-atx" in text
        or "eatx" in text
    ):

        return "E-ATX"

    if (
        "micro-atx" in text
        or "micro atx" in text
    ):

        return "Micro-ATX"

    if "mini-itx" in text:

        return "Mini-ITX"

    if re.search(
        r"\batx\b",
        text
    ):

        return "ATX"

    return None


def check_motherboard_case(
    motherboard,
    case
):

    motherboard_form = normalize_form_factor(
        get_value(
            motherboard,
            "form_factor"
        )
    )

    supported = get_value(
        case,
        "motherboard_support"
    )

    if not motherboard_form:

        print(
            "⚠ Motherboard form factor "
            "could not be verified."
        )

        return None

    if not supported:

        print(
            "⚠ Case motherboard support "
            "could not be verified."
        )

        return None

    if isinstance(
        supported,
        str
    ):

        supported = [
            supported
        ]

    supported_normalized = [

        normalize_form_factor(item)

        for item in supported

        if item
    ]

    if motherboard_form in supported_normalized:

        print(
            f"✓ Case supports {motherboard_form}."
        )

        return True

    print(
        f"✗ Case does not list support for "
        f"{motherboard_form}."
    )

    return False


# ============================================================
# GPU LENGTH
# ============================================================

def get_safe_gpu_length(gpu):

    """
    IMPORTANT:

    Never interpret an arbitrary dimension as GPU length.

    Only use length_mm when the normalizer explicitly
    identifies the value as the GPU/card length.
    """

    value = get_value(
        gpu,
        "length_mm"
    )

    if value is None:

        return None

    try:

        value = float(value)

    except (
        ValueError,
        TypeError
    ):

        return None

    # Reject suspicious values.

    if value < 150:

        return None

    return value


def get_case_gpu_clearance(case):

    value = get_value(
        case,
        "gpu_clearance_mm"
    )

    if value is None:

        return None

    try:

        value = float(value)

    except (
        ValueError,
        TypeError
    ):

        return None

    if value <= 0:

        return None

    return value


def check_gpu_case(
    gpu,
    case
):

    gpu_length = get_safe_gpu_length(
        gpu
    )

    clearance = get_case_gpu_clearance(
        case
    )

    if gpu_length is None:

        print(
            "⚠ GPU length could not be verified "
            "reliably."
        )

        return None

    if clearance is None:

        print(
            "⚠ Case GPU clearance could not "
            "be verified."
        )

        return None

    if gpu_length <= clearance:

        print(
            f"✓ GPU length ({gpu_length:g} mm) "
            f"fits within case clearance "
            f"({clearance:g} mm)."
        )

        return True

    print(
        f"✗ GPU length ({gpu_length:g} mm) "
        f"exceeds case clearance "
        f"({clearance:g} mm)."
    )

    return False


# ============================================================
# PSU
# ============================================================

def get_psu_wattage(psu):

    value = get_value(
        psu,
        "wattage"
    )

    if value is None:

        return None

    try:

        return float(value)

    except (
        ValueError,
        TypeError
    ):

        return None


def get_gpu_psu_requirement(gpu):

    value = get_value(
        gpu,
        "recommended_psu_wattage"
    )

    if value is None:

        return None

    try:

        return float(value)

    except (
        ValueError,
        TypeError
    ):

        return None


def check_gpu_psu(
    gpu,
    psu
):

    gpu_requirement = get_gpu_psu_requirement(
        gpu
    )

    psu_wattage = get_psu_wattage(
        psu
    )

    if gpu_requirement is None:

        print(
            "⚠ GPU recommended PSU wattage "
            "could not be verified."
        )

        return None

    if psu_wattage is None:

        print(
            "⚠ PSU wattage could not be verified."
        )

        return None

    if psu_wattage >= gpu_requirement:

        print(
            f"✓ PSU provides {psu_wattage:g}W; "
            f"GPU recommends {gpu_requirement:g}W."
        )

        return True

    print(
        f"✗ PSU provides {psu_wattage:g}W; "
        f"GPU recommends {gpu_requirement:g}W."
    )

    return False


# ============================================================
# BUILD CHECK
# ============================================================

def check_build(
    motherboard,
    ram,
    gpu,
    case,
    cooling,
    psu
):

    print_header(
        "COMPATIBILITY CHECK"
    )

    problems = 0

    # --------------------------------------------------------
    # Motherboard ↔ RAM
    # --------------------------------------------------------

    print()
    print("Motherboard ↔ RAM")

    result = check_motherboard_ram(
        motherboard,
        ram
    )

    if result is False:

        problems += 1

    # --------------------------------------------------------
    # Motherboard ↔ Case
    # --------------------------------------------------------

    print()
    print("Motherboard ↔ Case")

    result = check_motherboard_case(
        motherboard,
        case
    )

    if result is False:

        problems += 1

    # --------------------------------------------------------
    # GPU ↔ Case
    # --------------------------------------------------------

    print()
    print("Graphics Card ↔ Case")

    result = check_gpu_case(
        gpu,
        case
    )

    if result is False:

        problems += 1

    # --------------------------------------------------------
    # GPU ↔ PSU
    # --------------------------------------------------------

    print()
    print("Graphics Card ↔ Power Supply")

    result = check_gpu_psu(
        gpu,
        psu
    )

    if result is False:

        problems += 1

    # --------------------------------------------------------
    # Motherboard ↔ Cooling
    # --------------------------------------------------------

    print()
    print("Motherboard ↔ Cooling")

    result = check_motherboard_cooling(
        motherboard,
        cooling
    )

    if result is False:

        problems += 1

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    print()

    if problems:

        print_header(
            "✗ BUILD HAS A BASIC COMPATIBILITY ISSUE"
        )

        print(
            f"{problems} confirmed compatibility "
            f"issue(s) found."
        )

        print(
            "Please review the items marked with ✗."
        )

    else:

        print_header(
            "✓ NO CONFIRMED BASIC COMPATIBILITY ISSUES"
        )

        print(
            "No confirmed incompatibilities were found "
            "using the available product data."
        )

    print()
    print("-" * 65)
    print("COMPATIBILITY NOTICE")
    print(
        "This tool performs basic compatibility checks "
        "using available product data."
    )
    print(
        "If information is unavailable or ambiguous, "
        "the tool will not guess."
    )
    print(
        "Always verify detailed specifications with "
        "the manufacturer before purchasing."
    )
    print("-" * 65)

    return problems


# ============================================================
# NORMAL INTERACTIVE BUILDER
# ============================================================

def run_interactive_builder():

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    try:

        with open(
            INPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            products = json.load(file)

    except FileNotFoundError:

        print()
        print(
            f"ERROR: Could not find '{INPUT_FILE}'."
        )

        return

    except json.JSONDecodeError as error:

        print()
        print(
            f"ERROR: Invalid JSON in '{INPUT_FILE}'."
        )

        print(error)

        return

    # --------------------------------------------------------
    # AVAILABLE COMPONENTS
    # --------------------------------------------------------

    component_types = []

    for product in products:

        component_type = (
            product
            .get("Compatibility", {})
            .get("type")
        )

        if (
            component_type
            and component_type not in component_types
        ):

            component_types.append(
                component_type
            )

    print_header(
        "GB TECH — BUILD YOUR OWN PC"
    )

    print()
    print(
        "Available component types:"
    )

    for component_type in component_types:

        print(
            f"  • {component_type}"
        )

    # --------------------------------------------------------
    # COMPONENT SELECTION
    # --------------------------------------------------------

    motherboard = choose_product(
        get_components(
            products,
            "motherboard"
        ),
        "motherboard"
    )

    if motherboard is None:
        return

    ram = choose_product(
        get_components(
            products,
            "ram"
        ),
        "ram"
    )

    if ram is None:
        return

    gpu = choose_product(
        get_components(
            products,
            "graphics_card"
        ),
        "graphics card"
    )

    if gpu is None:
        return

    case = choose_product(
        get_components(
            products,
            "case"
        ),
        "case"
    )

    if case is None:
        return

    cooling = choose_product(
        get_components(
            products,
            "cooling"
        ),
        "cooling"
    )

    if cooling is None:
        return

    psu = choose_product(
        get_components(
            products,
            "power_supply"
        ),
        "power supply"
    )

    if psu is None:
        return

    # --------------------------------------------------------
    # SELECTED
    # --------------------------------------------------------

    print_header(
        "SELECTED COMPONENTS"
    )

    print(
        "Motherboard:",
        motherboard.get(
            "Product Name"
        )
    )

    print(
        "RAM:",
        ram.get(
            "Product Name"
        )
    )

    print(
        "Graphics Card:",
        gpu.get(
            "Product Name"
        )
    )

    print(
        "Case:",
        case.get(
            "Product Name"
        )
    )

    print(
        "Cooling:",
        cooling.get(
            "Product Name"
        )
    )

    print(
        "Power Supply:",
        psu.get(
            "Product Name"
        )
    )

    # --------------------------------------------------------
    # CHECK
    # --------------------------------------------------------

    check_build(
        motherboard,
        ram,
        gpu,
        case,
        cooling,
        psu
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_interactive_builder()