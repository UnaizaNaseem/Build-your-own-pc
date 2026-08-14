# ============================================================
# BASIC PC COMPATIBILITY ENGINE
# ============================================================

def normalize(value):
    """
    Convert a value into a simple lowercase string
    so comparisons are easier.
    """

    if value is None:
        return ""

    return str(value).strip().lower()


# ============================================================
# CPU ↔ MOTHERBOARD
# ============================================================

def check_cpu_motherboard(cpu, motherboard):

    cpu_socket = normalize(
        cpu.get("socket")
    )

    motherboard_socket = normalize(
        motherboard.get("socket")
    )

    # We cannot determine compatibility
    if not cpu_socket or not motherboard_socket:

        return {
            "status": "unknown",
            "message": "CPU or motherboard socket information is unavailable."
        }

    # Exact socket match
    if cpu_socket == motherboard_socket:

        return {
            "status": "compatible",
            "message": f"CPU socket {cpu_socket.upper()} matches motherboard socket."
        }

    # Different sockets
    return {
        "status": "incompatible",
        "message": (
            f"CPU uses {cpu_socket.upper()}, "
            f"but motherboard uses {motherboard_socket.upper()}."
        )
    }


# ============================================================
# MOTHERBOARD ↔ RAM
# ============================================================

def check_motherboard_ram(motherboard, ram):

    motherboard_memory = normalize(
        motherboard.get("memory_type")
    )

    ram_memory = normalize(
        ram.get("memory_type")
    )

    # Information unavailable
    if not motherboard_memory or not ram_memory:

        return {
            "status": "unknown",
            "message": "Memory type information is unavailable."
        }

    # Match
    if motherboard_memory == ram_memory:

        return {
            "status": "compatible",
            "message": (
                f"{ram_memory.upper()} RAM matches "
                f"the motherboard memory type."
            )
        }

    # Different memory generations
    return {
        "status": "incompatible",
        "message": (
            f"Motherboard supports {motherboard_memory.upper()}, "
            f"but selected RAM is {ram_memory.upper()}."
        )
    }


# ============================================================
# CPU ↔ RAM
# ============================================================

def check_cpu_ram(cpu, ram):

    cpu_memory = normalize(
        cpu.get("memory_type")
    )

    ram_memory = normalize(
        ram.get("memory_type")
    )

    # If CPU doesn't provide memory information,
    # don't incorrectly mark it incompatible.
    if not cpu_memory:

        return {
            "status": "unknown",
            "message": "CPU memory compatibility information is unavailable."
        }

    if not ram_memory:

        return {
            "status": "unknown",
            "message": "RAM memory type information is unavailable."
        }

    if cpu_memory == ram_memory:

        return {
            "status": "compatible",
            "message": (
                f"{ram_memory.upper()} RAM is compatible "
                f"with the CPU memory type."
            )
        }

    return {
        "status": "incompatible",
        "message": (
            f"CPU supports {cpu_memory.upper()}, "
            f"but selected RAM is {ram_memory.upper()}."
        )
    }


# ============================================================
# MOTHERBOARD ↔ CASE
# ============================================================

def check_motherboard_case(motherboard, case):

    motherboard_form_factor = normalize(
        motherboard.get("form_factor")
    )

    supported_form_factors = case.get(
        "motherboard_support",
        []
    )

    supported_form_factors = [
        normalize(x)
        for x in supported_form_factors
    ]

    # Information unavailable
    if not motherboard_form_factor:

        return {
            "status": "unknown",
            "message": "Motherboard form factor information is unavailable."
        }

    if not supported_form_factors:

        return {
            "status": "unknown",
            "message": "Case motherboard compatibility information is unavailable."
        }

    # Direct match
    if motherboard_form_factor in supported_form_factors:

        return {
            "status": "compatible",
            "message": (
                f"{motherboard_form_factor.upper()} motherboard "
                f"is supported by the case."
            )
        }

    return {
        "status": "incompatible",
        "message": (
            f"The case does not list support for "
            f"{motherboard_form_factor.upper()} motherboards."
        )
    }


# ============================================================
# GPU ↔ MOTHERBOARD
# ============================================================

def check_gpu_motherboard(gpu, motherboard):

    gpu_interface = normalize(
        gpu.get("interface")
    )

    motherboard_interface = normalize(
        motherboard.get("gpu_interface")
    )

    # If we don't have enough information,
    # don't claim incompatibility.
    if not gpu_interface or not motherboard_interface:

        return {
            "status": "unknown",
            "message": (
                "GPU/motherboard interface information "
                "is unavailable."
            )
        }

    if gpu_interface == motherboard_interface:

        return {
            "status": "compatible",
            "message": "GPU interface is compatible with the motherboard."
        }

    return {
        "status": "unknown",
        "message": (
            "GPU and motherboard interface information "
            "does not match exactly. Please verify specifications."
        )
    }


# ============================================================
# GPU ↔ CASE
# ============================================================

def check_gpu_case(gpu, case):

    gpu_length = gpu.get("length_mm")
    case_gpu_clearance = case.get("gpu_clearance_mm")

    # We don't have enough information
    if gpu_length is None or case_gpu_clearance is None:

        return {
            "status": "unknown",
            "message": (
                "GPU length or case clearance information "
                "is unavailable."
            )
        }

    try:

        gpu_length = float(gpu_length)
        case_gpu_clearance = float(case_gpu_clearance)

    except (ValueError, TypeError):

        return {
            "status": "unknown",
            "message": "GPU/case physical dimensions could not be verified."
        }

    if gpu_length <= case_gpu_clearance:

        return {
            "status": "compatible",
            "message": "GPU length fits within the case clearance."
        }

    return {
        "status": "incompatible",
        "message": "GPU is longer than the case's listed GPU clearance."
    }


# ============================================================
# PSU ↔ SYSTEM
# ============================================================

def check_psu_wattage(psu, required_wattage):

    psu_wattage = psu.get("wattage")

    if psu_wattage is None:

        return {
            "status": "unknown",
            "message": "PSU wattage information is unavailable."
        }

    try:

        psu_wattage = float(psu_wattage)
        required_wattage = float(required_wattage)

    except (ValueError, TypeError):

        return {
            "status": "unknown",
            "message": "PSU wattage could not be verified."
        }

    if psu_wattage >= required_wattage:

        return {
            "status": "compatible",
            "message": (
                f"{int(psu_wattage)}W PSU meets the "
                f"estimated {int(required_wattage)}W requirement."
            )
        }

    return {
        "status": "incompatible",
        "message": (
            f"{int(psu_wattage)}W PSU is below the "
            f"estimated {int(required_wattage)}W requirement."
        )
    }


# ============================================================
# COOLER ↔ CPU
# ============================================================

def check_cooler_cpu(cooler, cpu):

    cpu_socket = normalize(
        cpu.get("socket")
    )

    supported_sockets = cooler.get(
        "socket_support",
        []
    )

    supported_sockets = [
        normalize(x)
        for x in supported_sockets
    ]

    if not cpu_socket:

        return {
            "status": "unknown",
            "message": "CPU socket information is unavailable."
        }

    if not supported_sockets:

        return {
            "status": "unknown",
            "message": "Cooler socket support information is unavailable."
        }

    if cpu_socket in supported_sockets:

        return {
            "status": "compatible",
            "message": (
                f"Cooler supports {cpu_socket.upper()}."
            )
        }

    return {
        "status": "incompatible",
        "message": (
            f"Cooler does not list support for "
            f"{cpu_socket.upper()}."
        )


# ============================================================
# FAN ↔ CASE
# ============================================================

def check_fan_case(fan, case):

    fan_size = normalize(
        fan.get("size")
    )

    supported_fan_sizes = case.get(
        "fan_support",
        []
    )

    supported_fan_sizes = [
        normalize(x)
        for x in supported_fan_sizes
    ]

    if not fan_size:

        return {
            "status": "unknown",
            "message": "Fan size information is unavailable."
        }

    if not supported_fan_sizes:

        return {
            "status": "unknown",
            "message": "Case fan support information is unavailable."
        }

    if fan_size in supported_fan_sizes:

        return {
            "status": "compatible",
            "message": (
                f"Case supports {fan_size} fans."
            )
        }

    return {
        "status": "unknown",
        "message": (
            f"Fan size {fan_size} is not explicitly "
            f"listed by the case."
        )
    }


# ============================================================
# GENERAL RESULT FORMAT
# ============================================================

def compatibility_result(status, message):

    return {
        "status": status,
        "message": message
    }