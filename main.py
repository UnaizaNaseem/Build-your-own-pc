import json


# ============================================================
# SETTINGS
# ============================================================

JSON_FILE = "pc_components_normalized.json"


# ============================================================
# LOAD PRODUCTS
# ============================================================

with open(JSON_FILE, "r", encoding="utf-8") as file:
    products = json.load(file)


# ============================================================
# GROUP PRODUCTS BY TYPE
# ============================================================

products_by_type = {}

for product in products:
    compatibility = product.get("Compatibility", {})
    component_type = compatibility.get("type")

    if not component_type:
        continue

    products_by_type.setdefault(component_type, []).append(product)


# ============================================================
# DISPLAY COMPONENTS
# ============================================================

def choose_product(component_type):

    available = products_by_type.get(component_type, [])

    if not available:
        print(f"\nNo {component_type} products available.")
        return None

    print("\n" + "=" * 60)
    print(component_type.upper().replace("_", " "))
    print("=" * 60)

    for index, product in enumerate(available, start=1):
        print(
            f"{index}. {product.get('Product Name', 'Unknown Product')}"
        )

    while True:

        try:

            choice = int(
                input(
                    f"\nChoose {component_type.replace('_', ' ')} "
                    f"(1-{len(available)}): "
                )
            )

            if 1 <= choice <= len(available):
                return available[choice - 1]

            print("Please enter a valid number.")

        except ValueError:
            print("Please enter a number.")


# ============================================================
# COMPATIBILITY HELPERS
# ============================================================

def get_compatibility(product):

    return product.get("Compatibility", {})


def normalize_string(value):

    if value is None:
        return ""

    return str(value).strip().upper()


# ============================================================
# MOTHERBOARD ↔ RAM
# ============================================================

def check_motherboard_ram(motherboard, ram):

    mb = get_compatibility(motherboard)
    memory = get_compatibility(ram)

    mb_memory = normalize_string(
        mb.get("memory_type")
    )

    ram_memory = normalize_string(
        memory.get("memory_type")
    )

    print("\nMotherboard ↔ RAM")

    if not mb_memory or not ram_memory:

        print(
            "⚠ Memory type information is unavailable."
        )

        return "warning"

    if mb_memory == ram_memory:

        print(
            f"✓ Motherboard uses {mb_memory} "
            f"and RAM is {ram_memory}."
        )

        return "compatible"

    print(
        f"✗ Motherboard uses {mb_memory}, "
        f"but RAM is {ram_memory}."
    )

    return "incompatible"


# ============================================================
# MOTHERBOARD ↔ CASE
# ============================================================

def check_motherboard_case(motherboard, case):

    mb = get_compatibility(motherboard)
    case_data = get_compatibility(case)

    motherboard_form_factor = normalize_string(
        mb.get("form_factor")
    )

    supported_form_factors = case_data.get(
        "supported_form_factors"
    )

    print("\nMotherboard ↔ Case")

    if (
        not motherboard_form_factor
        or not supported_form_factors
    ):

        print(
            "⚠ Case motherboard support information "
            "is unavailable."
        )

        return "warning"

    supported = [
        normalize_string(x)
        for x in supported_form_factors
    ]

    if motherboard_form_factor in supported:

        print(
            f"✓ {motherboard_form_factor} "
            f"motherboard is supported by the case."
        )

        return "compatible"

    print(
        f"✗ Case does not appear to support "
        f"{motherboard_form_factor} motherboards."
    )

    return "incompatible"


# ============================================================
# GPU ↔ CASE
# ============================================================

def check_gpu_case(graphics_card, case):

    gpu = get_compatibility(graphics_card)
    case_data = get_compatibility(case)

    gpu_length = gpu.get("length_mm")
    case_gpu_limit = case_data.get(
        "max_gpu_length_mm"
    )

    print("\nGraphics Card ↔ Case")

    if gpu_length is None:

        print(
            "⚠ GPU length is unavailable."
        )

        return "warning"

    if case_gpu_limit is None:

        print(
            "⚠ Case GPU clearance information "
            "is unavailable."
        )

        return "warning"

    if gpu_length <= case_gpu_limit:

        print(
            f"✓ GPU length ({gpu_length} mm) "
            f"fits within case clearance "
            f"({case_gpu_limit} mm)."
        )

        return "compatible"

    print(
        f"✗ GPU is {gpu_length} mm long, "
        f"but case supports up to "
        f"{case_gpu_limit} mm."
    )

    return "incompatible"


# ============================================================
# GPU ↔ PSU
# ============================================================

def check_gpu_psu(graphics_card, power_supply):

    gpu = get_compatibility(graphics_card)
    psu = get_compatibility(power_supply)

    recommended_wattage = gpu.get(
        "recommended_psu_wattage"
    )

    psu_wattage = psu.get("wattage")

    print("\nGraphics Card ↔ Power Supply")

    if recommended_wattage is None:

        print(
            "⚠ GPU recommended PSU wattage "
            "is unavailable."
        )

        return "warning"

    if psu_wattage is None:

        print(
            "⚠ PSU wattage is unavailable."
        )

        return "warning"

    if psu_wattage >= recommended_wattage:

        print(
            f"✓ PSU provides {psu_wattage}W; "
            f"GPU recommends {recommended_wattage}W."
        )

        return "compatible"

    print(
        f"✗ PSU provides {psu_wattage}W, "
        f"but GPU recommends at least "
        f"{recommended_wattage}W."
    )

    return "incompatible"


# ============================================================
# MOTHERBOARD ↔ COOLING
# ============================================================

def check_motherboard_cooling(motherboard, cooling):

    mb = get_compatibility(motherboard)
    cooler = get_compatibility(cooling)

    socket = normalize_string(
        mb.get("socket")
    )

    supported_sockets = cooler.get(
        "supported_sockets"
    )

    print("\nMotherboard ↔ Cooling")

    if not socket or not supported_sockets:

        print(
            "⚠ CPU cooler socket support "
            "could not be verified."
        )

        return "warning"

    supported = [
        normalize_string(x)
        for x in supported_sockets
    ]

    if socket in supported:

        print(
            f"✓ Cooler supports {socket}."
        )

        return "compatible"

    print(
        f"✗ Cooler does not list support "
        f"for {socket}."
    )

    return "incompatible"


# ============================================================
# FAN ↔ CASE
# ============================================================

def check_fan_case(fan, case):

    fan_data = get_compatibility(fan)
    case_data = get_compatibility(case)

    fan_size = fan_data.get("size_mm")

    supported_sizes = case_data.get(
        "supported_fan_sizes_mm"
    )

    print("\nFan ↔ Case")

    if fan_size is None or not supported_sizes:

        print(
            "⚠ Fan/case size information "
            "could not be verified."
        )

        return "warning"

    if fan_size in supported_sizes:

        print(
            f"✓ Case supports {fan_size}mm fans."
        )

        return "compatible"

    print(
        f"✗ Case does not list support "
        f"for {fan_size}mm fans."
    )

    return "incompatible"


# ============================================================
# RUN COMPATIBILITY CHECKS
# ============================================================

def check_compatibility(build):

    print("\n" + "=" * 60)
    print("COMPATIBILITY CHECK")
    print("=" * 60)

    results = []

    # --------------------------------------------------------
    # Motherboard ↔ RAM
    # --------------------------------------------------------

    results.append(
        check_motherboard_ram(
            build["motherboard"],
            build["ram"]
        )
    )

    # --------------------------------------------------------
    # Motherboard ↔ Case
    # --------------------------------------------------------

    results.append(
        check_motherboard_case(
            build["motherboard"],
            build["case"]
        )
    )

    # --------------------------------------------------------
    # GPU ↔ Case
    # --------------------------------------------------------

    results.append(
        check_gpu_case(
            build["graphics_card"],
            build["case"]
        )
    )

    # --------------------------------------------------------
    # GPU ↔ PSU
    # --------------------------------------------------------

    results.append(
        check_gpu_psu(
            build["graphics_card"],
            build["power_supply"]
        )
    )

    # --------------------------------------------------------
    # Motherboard ↔ Cooling
    # --------------------------------------------------------

    results.append(
        check_motherboard_cooling(
            build["motherboard"],
            build["cooling"]
        )
    )

    # --------------------------------------------------------
    # Fan ↔ Case
    # --------------------------------------------------------

    results.append(
        check_fan_case(
            build["fan"],
            build["case"]
        )
    )

    # ========================================================
    # FINAL RESULT
    # ========================================================

    print("\n" + "=" * 60)

    if "incompatible" in results:

        print(
            "✗ BUILD HAS A BASIC COMPATIBILITY ISSUE"
        )

        print(
            "=" * 60
        )

        print(
            "\nPlease review the items marked with ✗ "
            "before purchasing."
        )

        return False

    if "warning" in results:

        print(
            "⚠ BUILD PASSED BASIC CHECKS"
        )

        print(
            "=" * 60
        )

        print(
            "\nSome compatibility details could not "
            "be verified."
        )

        return True

    print(
        "✓ BUILD PASSED BASIC COMPATIBILITY CHECKS"
    )

    print(
        "=" * 60
    )

    return True


# ============================================================
# DISPLAY SELECTED BUILD
# ============================================================

def display_build(build):

    print("\n" + "=" * 60)
    print("SELECTED COMPONENTS")
    print("=" * 60)

    print(
        f"Motherboard: "
        f"{build['motherboard']['Product Name']}"
    )

    print(
        f"RAM: "
        f"{build['ram']['Product Name']}"
    )

    print(
        f"Graphics Card: "
        f"{build['graphics_card']['Product Name']}"
    )

    print(
        f"Case: "
        f"{build['case']['Product Name']}"
    )

    print(
        f"Cooling: "
        f"{build['cooling']['Product Name']}"
    )

    print(
        f"Power Supply: "
        f"{build['power_supply']['Product Name']}"
    )

    print(
        f"Fan: "
        f"{build['fan']['Product Name']}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 60)
    print("GB TECH — BUILD YOUR OWN PC")
    print("=" * 60)

    print("\nAvailable component types:")

    for component_type in products_by_type:

        print(
            f"  • {component_type}"
        )

    # --------------------------------------------------------
    # SELECT COMPONENTS
    # --------------------------------------------------------

    build = {}

    build["motherboard"] = choose_product(
        "motherboard"
    )

    build["ram"] = choose_product(
        "ram"
    )

    build["graphics_card"] = choose_product(
        "graphics_card"
    )

    build["case"] = choose_product(
        "case"
    )

    build["cooling"] = choose_product(
        "cooling"
    )

    build["power_supply"] = choose_product(
        "power_supply"
    )

    build["fan"] = choose_product(
        "fan"
    )

    # --------------------------------------------------------
    # SHOW BUILD
    # --------------------------------------------------------

    display_build(build)

    # --------------------------------------------------------
    # CHECK COMPATIBILITY
    # --------------------------------------------------------

    check_compatibility(build)

    # --------------------------------------------------------
    # DISCLAIMER
    # --------------------------------------------------------

    print("\n" + "-" * 60)

    print(
        "COMPATIBILITY NOTICE"
    )

    print(
        "This tool performs basic compatibility checks "
        "using available product specifications."
    )

    print(
        "It does not guarantee complete system "
        "compatibility."
    )

    print(
        "Always verify detailed specifications with "
        "the manufacturer before purchasing."
    )

    print("-" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()