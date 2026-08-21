import json
import re


# ============================================================
# SETTINGS
# ============================================================

INPUT_FILE = "pc_components_normalized.json"

# ------------------------------------------------------------
# FINAL TEST SWITCH
#
# True  = run automated compatibility tests
# False = run normal interactive PC builder
# ------------------------------------------------------------

TEST_MODE = False


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
        r"\bDDR\s*([2-5])\b",
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
            "⚠ Cooler socket support could not be verified."
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
            f"✓ Cooler supports {motherboard_socket}."
        )

        return True

    print(
        f"✗ Cooler does not list support for "
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

    if "micro-atx" in text:

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
# FAN ↔ CASE
# ============================================================

def check_fan_case(
    fan,
    case
):

    fan_size = get_value(
        fan,
        "size_mm"
    )

    fan_support = get_value(
        case,
        "fan_support"
    )

    if fan_size is None:

        print(
            "⚠ Fan size could not be verified."
        )

        return None

    if not fan_support:

        print(
            "⚠ Case fan support could not "
            "be verified."
        )

        return None

    # --------------------------------------------------------
    # Allow:
    #
    # "120mm, 140mm"
    # ["120mm", "140mm"]
    # [120, 140]
    # --------------------------------------------------------

    if isinstance(
        fan_support,
        list
    ):

        supported_sizes = []

        for item in fan_support:

            match = re.search(
                r"\b(\d{2,3})\s*mm\b",
                str(item),
                re.IGNORECASE
            )

            if match:

                supported_sizes.append(
                    float(match.group(1))
                )

            else:

                try:

                    supported_sizes.append(
                        float(item)
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    pass

    else:

        support_text = str(
            fan_support
        )

        supported_sizes = [

            float(match.group(1))

            for match in re.finditer(
                r"\b(\d{2,3})\s*mm\b",
                support_text,
                re.IGNORECASE
            )
        ]

    try:

        fan_size = float(
            fan_size
        )

    except (
        ValueError,
        TypeError
    ):

        print(
            "⚠ Fan size could not be verified."
        )

        return None

    if fan_size in supported_sizes:

        print(
            f"✓ Case lists support for "
            f"{fan_size:g}mm fans."
        )

        return True

    print(
        f"✗ Case does not list support for "
        f"{fan_size:g}mm fans."
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
    psu,
    fan
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
    # Fan ↔ Case
    # --------------------------------------------------------

    print()
    print("Fan ↔ Case")

    result = check_fan_case(
        fan,
        case
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
# AUTOMATED TEST DATA
# ============================================================

def test_product(
    name,
    component_type,
    **values
):

    return {
        "Product Name": name,
        "Compatibility": {
            "type": component_type,
            **values
        }
    }


# ============================================================
# TEST 1
#
# EVERYTHING COMPATIBLE
# Expected:
#
# ✓ RAM
# ✓ CASE
# ✓ GPU
# ✓ PSU
# ✓ COOLER
# ✓ FAN
#
# Final:
# ✓ NO CONFIRMED BASIC COMPATIBILITY ISSUES
# ============================================================

def run_test_1():

    print_header(
        "TEST 1 — FULLY COMPATIBLE BUILD"
    )

    motherboard = test_product(
        "TEST ASUS B850 ATX",
        "motherboard",
        socket="AM5",
        memory_type="DDR5",
        form_factor="ATX"
    )

    ram = test_product(
        "TEST DDR5 DIMM",
        "ram",
        memory_type="DDR5 DIMM"
    )

    gpu = test_product(
        "TEST RTX GPU 320mm",
        "graphics_card",
        length_mm=320,
        recommended_psu_wattage=750
    )

    case = test_product(
        "TEST ATX CASE",
        "case",
        motherboard_support=[
            "ATX",
            "Micro-ATX",
            "Mini-ITX"
        ],
        gpu_clearance_mm=400,
        fan_support="120mm, 140mm"
    )

    cooling = test_product(
        "TEST AM5 COOLER",
        "cooling",
        socket_support=[
            "AM4",
            "AM5",
            "LGA1700"
        ]
    )

    psu = test_product(
        "TEST 850W PSU",
        "power_supply",
        wattage=850
    )

    fan = test_product(
        "TEST 140mm FAN",
        "fan",
        size_mm=140
    )

    problems = check_build(
        motherboard,
        ram,
        gpu,
        case,
        cooling,
        psu,
        fan
    )

    assert problems == 0

    print()
    print("TEST 1 RESULT: PASS")


# ============================================================
# TEST 2
#
# DDR4 RAM ON DDR5 MOTHERBOARD
#
# Expected:
# ✗ RAM generation
#
# ============================================================

def run_test_2():

    print_header(
        "TEST 2 — DDR GENERATION MISMATCH"
    )

    motherboard = test_product(
        "TEST DDR5 MOTHERBOARD",
        "motherboard",
        socket="AM5",
        memory_type="DDR5",
        form_factor="ATX"
    )

    ram = test_product(
        "TEST DDR4 RAM",
        "ram",
        memory_type="DDR4 DIMM"
    )

    result = check_motherboard_ram(
        motherboard,
        ram
    )

    assert result is False

    print()
    print("TEST 2 RESULT: PASS")


# ============================================================
# TEST 3
#
# SO-DIMM RAM
#
# Expected:
# ✗ SO-DIMM
# ============================================================

def run_test_3():

    print_header(
        "TEST 3 — SO-DIMM RAM"
    )

    motherboard = test_product(
        "TEST DESKTOP MOTHERBOARD",
        "motherboard",
        socket="AM5",
        memory_type="DDR5",
        form_factor="ATX"
    )

    ram = test_product(
        "TEST LAPTOP RAM",
        "ram",
        memory_type="DDR5 SO-DIMM"
    )

    result = check_motherboard_ram(
        motherboard,
        ram
    )

    assert result is False

    print()
    print("TEST 3 RESULT: PASS")


# ============================================================
# TEST 4
#
# CASE TOO SMALL FOR GPU
#
# Expected:
# ✗ GPU length
# ============================================================

def run_test_4():

    print_header(
        "TEST 4 — GPU TOO LONG FOR CASE"
    )

    gpu = test_product(
        "TEST 350mm GPU",
        "graphics_card",
        length_mm=350
    )

    case = test_product(
        "TEST 300mm CASE",
        "case",
        gpu_clearance_mm=300
    )

    result = check_gpu_case(
        gpu,
        case
    )

    assert result is False

    print()
    print("TEST 4 RESULT: PASS")


# ============================================================
# TEST 5
#
# PSU TOO WEAK
#
# Expected:
# ✗ PSU
# ============================================================

def run_test_5():

    print_header(
        "TEST 5 — PSU TOO WEAK"
    )

    gpu = test_product(
        "TEST HIGH POWER GPU",
        "graphics_card",
        recommended_psu_wattage=850
    )

    psu = test_product(
        "TEST 750W PSU",
        "power_supply",
        wattage=750
    )

    result = check_gpu_psu(
        gpu,
        psu
    )

    assert result is False

    print()
    print("TEST 5 RESULT: PASS")


# ============================================================
# TEST 6
#
# WRONG COOLER SOCKET
#
# Expected:
# ✗ Cooler socket
# ============================================================

def run_test_6():

    print_header(
        "TEST 6 — COOLER SOCKET MISMATCH"
    )

    motherboard = test_product(
        "TEST AM5 MOTHERBOARD",
        "motherboard",
        socket="AM5"
    )

    cooling = test_product(
        "TEST LGA1200 COOLER",
        "cooling",
        socket_support=[
            "LGA1200",
            "LGA1151"
        ]
    )

    result = check_motherboard_cooling(
        motherboard,
        cooling
    )

    assert result is False

    print()
    print("TEST 6 RESULT: PASS")


# ============================================================
# TEST 7
#
# FAN NOT SUPPORTED BY CASE
#
# Expected:
# ✗ Fan size
# ============================================================

def run_test_7():

    print_header(
        "TEST 7 — FAN SIZE MISMATCH"
    )

    fan = test_product(
        "TEST 140mm FAN",
        "fan",
        size_mm=140
    )

    case = test_product(
        "TEST 120mm CASE",
        "case",
        fan_support="120mm"
    )

    result = check_fan_case(
        fan,
        case
    )

    assert result is False

    print()
    print("TEST 7 RESULT: PASS")


# ============================================================
# TEST 8
#
# UNKNOWN DATA
#
# Expected:
# ⚠
#
# NOT a compatibility failure.
# ============================================================

def run_test_8():

    print_header(
        "TEST 8 — UNKNOWN / MISSING DATA"
    )

    gpu = test_product(
        "TEST GPU WITHOUT LENGTH",
        "graphics_card"
    )

    case = test_product(
        "TEST CASE WITHOUT CLEARANCE",
        "case"
    )

    result = check_gpu_case(
        gpu,
        case
    )

    assert result is None

    print()
    print("TEST 8 RESULT: PASS")


# ============================================================
# RUN ALL AUTOMATED TESTS
# ============================================================

def run_all_tests():

    print_header(
        "GB TECH COMPATIBILITY ENGINE — FINAL TEST SUITE"
    )

    tests = [

        run_test_1,
        run_test_2,
        run_test_3,
        run_test_4,
        run_test_5,
        run_test_6,
        run_test_7,
        run_test_8

    ]

    passed = 0

    failed = 0

    for test in tests:

        try:

            test()

            passed += 1

        except AssertionError:

            failed += 1

            print()
            print(
                "TEST RESULT: FAILED"
            )

        except Exception as error:

            failed += 1

            print()
            print(
                f"TEST RESULT: ERROR — {error}"
            )

    print_header(
        "FINAL TEST SUMMARY"
    )

    print(
        f"Tests passed: {passed}"
    )

    print(
        f"Tests failed: {failed}"
    )

    print()

    if failed == 0:

        print(
            "✓ ALL COMPATIBILITY TESTS PASSED"
        )

        print(
            "The compatibility engine is ready "
            "for the next stage."
        )

    else:

        print(
            "✗ SOME TESTS FAILED"
        )

        print(
            "Do not finalize until the failed "
            "tests are investigated."
        )


# ============================================================
# NORMAL INTERACTIVE BUILDER
# ============================================================

def run_interactive_builder():

    # --------------------------------------------------------
    # LOAD
    # --------------------------------------------------------

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        products = json.load(file)

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

    ram = choose_product(
        get_components(
            products,
            "ram"
        ),
        "ram"
    )

    gpu = choose_product(
        get_components(
            products,
            "graphics_card"
        ),
        "graphics card"
    )

    case = choose_product(
        get_components(
            products,
            "case"
        ),
        "case"
    )

    cooling = choose_product(
        get_components(
            products,
            "cooling"
        ),
        "cooling"
    )

    psu = choose_product(
        get_components(
            products,
            "power_supply"
        ),
        "power supply"
    )

    fan = choose_product(
        get_components(
            products,
            "fan"
        ),
        "fan"
    )

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

    print(
        "Fan:",
        fan.get(
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
        psu,
        fan
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    if TEST_MODE:

        run_all_tests()

    else:

        run_interactive_builder()