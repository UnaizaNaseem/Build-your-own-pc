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



def memory_generations(value):

    if not value:
        return []

    values = value if isinstance(
        value,
        (list, tuple, set)
    ) else [value]

    found = []

    for item in values:

        generation = memory_generation(
            item
        )

        if (
            generation
            and generation not in found
        ):

            found.append(
                generation
            )

    return found


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

    mb_generations = memory_generations(
        get_value(
            motherboard,
            "memory_types"
        )
    )

    if not mb_generations:

        mb_generations = memory_generations(
            get_value(
                motherboard,
                "memory_type"
            )
        )

    ram_generations = memory_generations(
        get_value(
            ram,
            "memory_types"
        )
    )

    if not ram_generations:

        ram_generations = memory_generations(
            get_value(
                ram,
                "memory_type"
            )
        )

    incompatible = False

    # --------------------------------------------------------
    # Memory generation
    # --------------------------------------------------------

    if (
        not mb_generations
        or not ram_generations
    ):

        print(
            "⚠ Motherboard/RAM memory generation "
            "could not be verified."
        )

    elif not (
        set(mb_generations)
        & set(ram_generations)
    ):

        print(
            f"✗ Motherboard supports "
            f"{', '.join(mb_generations)}, "
            f"but RAM is "
            f"{', '.join(ram_generations)}."
        )

        incompatible = True

    else:

        common = [
            item
            for item in mb_generations
            if item in ram_generations
        ]

        print(
            f"✓ Motherboard supports "
            f"{', '.join(mb_generations)} "
            f"and RAM is "
            f"{', '.join(ram_generations)} "
            f"(compatible: {', '.join(common)})."
        )

    # --------------------------------------------------------
    # Desktop vs laptop memory
    # --------------------------------------------------------

    ram_form_value = get_value(
        ram,
        "form_factor"
    )

    ram_form = memory_form_factor(
        ram_form_value
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


def normalize_socket(socket):

    if not socket:
        return None

    text = str(socket).strip().upper()

    text = re.sub(
        r"[\s\-]",
        "",
        text
    )

    # Intel often publishes FCLGA1700/FCLGA1851.
    # Canonicalize these to LGA1700/LGA1851 so they
    # compare correctly with motherboard socket data.
    text = re.sub(
        r"^FCLGA",
        "LGA",
        text
    )

    return text


def check_processor_motherboard(
    processor,
    motherboard
):

    processor_socket = normalize_socket(
        get_value(
            processor,
            "socket"
        )
    )

    motherboard_socket = normalize_socket(
        get_value(
            motherboard,
            "socket"
        )
    )

    # --------------------------------------------------------
    # Missing CPU socket
    # --------------------------------------------------------

    if not processor_socket:

        print(
            "⚠ Processor socket could not be verified."
        )

        return None

    # --------------------------------------------------------
    # Missing motherboard socket
    # --------------------------------------------------------

    if not motherboard_socket:

        print(
            "⚠ Motherboard socket could not be verified."
        )

        return None

    # --------------------------------------------------------
    # Socket comparison
    # --------------------------------------------------------

    if processor_socket == motherboard_socket:

        print(
            f"✓ Processor socket ({processor_socket}) "
            f"matches motherboard socket "
            f"({motherboard_socket})."
        )

        return True

    print(
        f"✗ Processor socket ({processor_socket}) "
        f"does not match motherboard socket "
        f"({motherboard_socket})."
    )

    return False


def check_processor_ram(
    processor,
    ram
):

    processor_generations = memory_generations(
        get_value(
            processor,
            "memory_types"
        )
    )

    if not processor_generations:

        processor_generations = memory_generations(
            get_value(
                processor,
                "memory_type"
            )
        )

    ram_generations = memory_generations(
        get_value(
            ram,
            "memory_types"
        )
    )

    if not ram_generations:

        ram_generations = memory_generations(
            get_value(
                ram,
                "memory_type"
            )
        )

    if (
        not processor_generations
        or not ram_generations
    ):

        print(
            "⚠ Processor/RAM memory generation "
            "could not be verified."
        )

        return None

    common = set(
        processor_generations
    ) & set(
        ram_generations
    )

    if common:

        common_ordered = [
            item
            for item in processor_generations
            if item in common
        ]

        print(
            f"✓ Processor supports "
            f"{', '.join(processor_generations)} "
            f"and RAM is "
            f"{', '.join(ram_generations)} "
            f"(compatible: {', '.join(common_ordered)})."
        )

        return True

    print(
        f"✗ Processor supports "
        f"{', '.join(processor_generations)}, "
        f"but RAM is "
        f"{', '.join(ram_generations)}."
    )

    return False


def check_processor_cooling(
    processor,
    cooling
):

    processor_socket = normalize_socket(
        get_value(
            processor,
            "socket"
        )
    )

    supported_sockets = get_value(
        cooling,
        "socket_support"
    )

    if not processor_socket:

        print(
            "⚠ Processor socket could not be verified "
            "for cooling compatibility."
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

    normalized_supported = []

    for socket in supported_sockets:

        normalized = normalize_socket(
            socket
        )

        if (
            normalized
            and normalized not in normalized_supported
        ):

            normalized_supported.append(
                normalized
            )

    if not normalized_supported:

        print(
            "⚠ Cooling socket support could not be "
            "normalized reliably."
        )

        return None

    if processor_socket in normalized_supported:

        print(
            f"✓ Cooling supports processor socket "
            f"{processor_socket}."
        )

        return True

    print(
        f"✗ Cooling does not list support for "
        f"processor socket {processor_socket}."
    )

    return False


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
    processor,
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
    # Processor ↔ Motherboard
    # --------------------------------------------------------

    print()
    print("Processor ↔ Motherboard")

    result = check_processor_motherboard(
        processor,
        motherboard
    )

    if result is False:

        problems += 1

    # --------------------------------------------------------
    # Processor ↔ RAM
    # --------------------------------------------------------

    print()
    print("Processor ↔ RAM")

    result = check_processor_ram(
        processor,
        ram
    )

    if result is False:

        problems += 1

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
    # Processor ↔ Cooling
    # --------------------------------------------------------

    print()
    print("Processor ↔ Cooling")

    result = check_processor_cooling(
        processor,
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

    processor = choose_product(
        get_components(
            products,
            "processor"
        ),
        "processor"
    )

    if processor is None:
        return

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
        "Processor:",
        processor.get(
            "Product Name"
        )
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
        processor,
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