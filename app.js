/* ============================================================
   PRODUCTS
   ============================================================ */

const PRODUCTS = [];

let build = {};
let currentType = "";
let brand = "All";

const WHATSAPP_NUMBER = "923055183777";


/* ============================================================
   PC BUILDER CONFIGURATION
   ============================================================

   THIS IS THE MAIN CONTROL PANEL.

   To ADD a component:

       enabled: true

   To REMOVE a component:

       enabled: false

   IMPORTANT:
   `type` must match Compatibility.type in the JSON.

   Example:

   storage: {
       enabled: true,
       label: "Storage",
       aliases: [
           "storage",
           "ssd",
           "nvme"
       ]
   }

   ============================================================ */

const BUILDER_CONFIG = {

    motherboard: {
        enabled: true,

        label: "Motherboard",

        aliases: [
            "motherboard",
            "motherboards"
        ]
    },


    graphics_card: {
        enabled: true,

        label: "Graphics Card",

        aliases: [
            "graphics card",
            "graphics cards",
            "graphic card",
            "graphic cards",
            "gpu",
            "video card"
        ]
    },


    ram: {
        enabled: true,

        label: "RAM",

        aliases: [
            "ram",
            "memory"
        ]
    },


    case: {
        enabled: true,

        label: "Case",

        aliases: [
            "case",
            "cases",
            "pc case",
            "pc cases",
            "chassis"
        ]
    },


    cooling: {
        enabled: true,

        label: "CPU Cooling",

        aliases: [
            "cooling",
            "cooler",
            "coolers",
            "cpu cooler",
            "cpu coolers",
            "cpu cooling",
            "liquid cooling",
            "aio",
            "radiator"
        ]
    },


    power_supply: {
        enabled: true,

        label: "Power Supply",

        aliases: [
            "power supply",
            "power supplies",
            "psu"
        ]
    }


    /*
    ------------------------------------------------------------
    EXAMPLE FUTURE COMPONENT
    ------------------------------------------------------------

    storage: {
        enabled: false,

        label: "Storage",

        aliases: [
            "storage",
            "ssd",
            "nvme",
            "sata ssd",
            "hdd"
        ]
    }

    ------------------------------------------------------------
    */

};


/* ============================================================
   COMPATIBILITY RELATIONSHIPS
   ============================================================

   Add/remove relationships here later.

   ============================================================ */

const COMPATIBILITY_RELATIONS = [

    {
        a: "motherboard",
        b: "ram",
        title: "Motherboard ↔ RAM"
    },

    {
        a: "motherboard",
        b: "case",
        title: "Motherboard ↔ Case"
    },

    {
        a: "graphics_card",
        b: "power_supply",
        title: "Graphics Card ↔ Power Supply"
    },

    {
        a: "motherboard",
        b: "cooling",
        title: "Motherboard ↔ Cooling"
    },

    {
        a: "graphics_card",
        b: "case",
        title: "Graphics Card ↔ Case"
    }

];


/* ============================================================
   ENABLED BUILDER CATEGORIES
   ============================================================ */

const categories =
    Object.keys(
        BUILDER_CONFIG
    )
        .filter(
            type =>
                BUILDER_CONFIG[type].enabled
        );


/* ============================================================
   LABELS
   ============================================================ */

const labels =
    Object.fromEntries(
        Object.entries(
            BUILDER_CONFIG
        )
            .map(
                ([type, config]) => [
                    type,
                    config.label
                ]
            )
    );


/* ============================================================
   HELPERS
   ============================================================ */

const money = (
    value
) => {

    return new Intl.NumberFormat(
        "en-PK",
        {
            maximumFractionDigits: 0
        }
    ).format(
        Number(value) || 0
    );
};


const safePrice = (
    product
) => {

    return Number(
        product?.Price
    ) || 0;
};


const image = (
    product
) => {

    return product?.Image || "";
};


const normalizeText = (
    value
) => {

    return String(
        value ?? ""
    )
        .trim()
        .toLowerCase()
        .replace(
            /\s+/g,
            " "
        );
};


const escapeHTML = (
    value
) => {

    return String(
        value ?? ""
    )
        .replace(
            /&/g,
            "&amp;"
        )
        .replace(
            /</g,
            "&lt;"
        )
        .replace(
            />/g,
            "&gt;"
        )
        .replace(
            /"/g,
            "&quot;"
        )
        .replace(
            /'/g,
            "&#039;"
        );
};


/* ============================================================
   CATEGORY RESOLUTION
   ============================================================

   Priority:

   1. Compatibility.type
   2. Explicit category aliases

   ============================================================ */

const getProductCategory = (
    product
) => {

    return normalizeText(
        product?.Category
    );
};


const getProductCompatibilityType = (
    product
) => {

    return normalizeText(
        product?.Compatibility?.type
    );
};


const getConfiguredTypeFromCategory = (
    category
) => {

    const normalizedCategory =
        normalizeText(
            category
        );

    if (!normalizedCategory) {

        return "";
    }


    const parts =
        normalizedCategory
            .split(">")
            .map(
                part =>
                    part.trim()
            );


    for (
        const [type, config]
        of Object.entries(
            BUILDER_CONFIG
        )
    ) {

        if (!config.enabled) {

            continue;
        }


        for (
            const alias
            of config.aliases || []
        ) {

            const normalizedAlias =
                normalizeText(
                    alias
                );


            /*
             ----------------------------------------------------
             Exact category match
             ----------------------------------------------------
            */

            if (
                normalizedCategory ===
                normalizedAlias
            ) {

                return type;
            }


            /*
             ----------------------------------------------------
             Category path match
             ----------------------------------------------------

             Example:

             PC Components > Cooling

             contains:

             cooling
            */

            if (
                parts.includes(
                    normalizedAlias
                )
            ) {

                return type;
            }

        }

    }


    return "";
};


/* ============================================================
   RESOLVE PRODUCT TYPE
   ============================================================ */

const resolveProductType = (
    product
) => {

    const compatibilityType =
        getProductCompatibilityType(
            product
        );

    const category =
        getProductCategory(
            product
        );


    /*
     ------------------------------------------------------------
     FIRST:
     Trust normalized Compatibility.type
     ------------------------------------------------------------
    */

    if (
        BUILDER_CONFIG[
            compatibilityType
        ]?.enabled
    ) {

        return compatibilityType;
    }


    /*
     ------------------------------------------------------------
     SECOND:
     Fall back to configured category aliases
     ------------------------------------------------------------
    */

    const categoryType =
        getConfiguredTypeFromCategory(
            category
        );


    if (
        categoryType &&
        BUILDER_CONFIG[
            categoryType
        ]?.enabled
    ) {

        return categoryType;
    }


    return "";
};


/* ============================================================
   PRODUCTS BY TYPE
   ============================================================ */

const productsBy = (
    type
) => {

    if (
        !BUILDER_CONFIG[type]?.enabled
    ) {

        return [];
    }


    return PRODUCTS.filter(
        product =>
            resolveProductType(
                product
            ) === type
    );
};


/* ============================================================
   SELECTED PRODUCTS
   ============================================================ */

const selectedEntries = () => {

    return Object.entries(
        build
    )
        .filter(
            ([, product]) =>
                product
        );
};


const selectedTotal = () => {

    return selectedEntries()
        .reduce(
            (
                total,
                [, product]
            ) =>
                total +
                safePrice(
                    product
                ),
            0
        );
};


/* ============================================================
   LOAD PRODUCTS
   ============================================================ */

async function loadProducts() {

    try {

        const response =
            await fetch(
                "./pc_components_normalized.json",
                {
                    cache: "no-store"
                }
            );


        if (!response.ok) {

            throw new Error(
                `HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        if (!Array.isArray(data)) {

            throw new Error(
                "pc_components_normalized.json must contain an array."
            );
        }


        PRODUCTS.length = 0;

        PRODUCTS.push(
            ...data
        );


        render();

    }
    catch (error) {

        console.error(
            "Could not load product data:",
            error
        );


        const builder =
            document.getElementById(
                "builder"
            );


        if (builder) {

            builder.innerHTML = `
                <div class="empty">
                    Could not load product data.

                    Make sure
                    <b>pc_components_normalized.json</b>
                    is in the same folder as index.html.
                </div>
            `;
        }

    }

}


/* ============================================================
   MAIN BUILDER RENDER
   ============================================================ */

function render() {

    const builder =
        document.getElementById(
            "builder"
        );


    if (!builder) {

        return;
    }


    builder.innerHTML =
        categories
            .map(
                (
                    type,
                    index
                ) => {

                    const product =
                        build[type];


                    return `

                        <div class="step">

                            <div class="stephead">

                                <div class="stepname">

                                    ${
                                        index + 1
                                    }.

                                    ${
                                        escapeHTML(
                                            labels[type]
                                        )
                                    }

                                </div>


                                <div class="selected">

                                    ${
                                        product
                                            ? "Selected"
                                            : "Not selected"
                                    }

                                </div>

                            </div>


                            ${
                                product

                                    ? selectedProductHTML(
                                        type,
                                        product
                                    )

                                    : `

                                        <button
                                            type="button"
                                            class="btn add-product-btn"
                                            onclick="openModal('${type}')"
                                        >

                                            Add
                                            ${
                                                escapeHTML(
                                                    labels[type]
                                                )
                                            }

                                        </button>

                                      `
                            }

                        </div>

                    `;

                }
            )
            .join("");


    updateSummary();

}


/* ============================================================
   SELECTED PRODUCT CARD
   ============================================================ */

function selectedProductHTML(
    type,
    product
) {

    const productName =
        escapeHTML(
            product[
                "Product Name"
            ] ||
            "Unnamed product"
        );


    const productBrand =
        escapeHTML(
            product.Brand || ""
        );


    const productImage =
        escapeHTML(
            image(product)
        );


    const productPrice =
        money(
            safePrice(product)
        );


    const productURL =
        product[
            "Product URL"
        ]
            ? escapeHTML(
                product[
                    "Product URL"
                ]
            )
            : "";


    return `

        <div class="product">

            <img
                src="${productImage}"
                alt=""
                onerror="this.style.display='none'"
            >


            <div class="product-info">

                <div class="pname">
                    ${productName}
                </div>


                <div class="meta">
                    ${productBrand}
                </div>


                <div class="price">
                    PKR ${productPrice}
                </div>

            </div>


            <div class="product-actions">

                <button
                    type="button"
                    class="btn change-product-btn"
                    onclick="openModal('${type}')"
                >
                    Change
                </button>


                ${
                    productURL

                        ? `

                            <a
                                class="btn view-product-btn"
                                href="${productURL}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                View Product
                            </a>

                          `

                        : ""
                }


                <!-- NEW:
                     Remove the currently selected product.
                -->

                <button
                    type="button"
                    class="btn remove-product-btn"
                    onclick="removeProduct('${type}')"
                    aria-label="Remove ${escapeHTML(
                        labels[type] || type
                    )}"
                >
                    Remove
                </button>

            </div>

        </div>

    `;

}


function removeProduct(type) {

    if (!type) {
        return;
    }

    // Remove the selected product
    delete build[type];

    // Clear any active product/category state
    if (currentType === type) {
        currentType = "";
    }

    // Re-render builder
    render();

    // Recalculate summary
    updateSummary();

    // Recalculate compatibility
    checks();
}

/* ============================================================
   SUMMARY
   ============================================================ */

function updateSummary() {

    const total =
        selectedTotal();


    const totalElement =
        document.getElementById(
            "total"
        );


    if (totalElement) {

        totalElement.textContent =
            `PKR ${money(total)}`;
    }


    const compatibility =
        checks();


    const compatElement =
        document.getElementById(
            "compat"
        );


    if (compatElement) {

        compatElement.innerHTML =
            compatibility
                .map(
                    item => `

                        <div
                            class="compat ${item.level}"
                        >

                            <span class="dot"></span>

                            <div>

                                <b>
                                    ${
                                        escapeHTML(
                                            item.title
                                        )
                                    }
                                </b>

                                <br>

                                ${
                                    escapeHTML(
                                        item.text
                                    )
                                }

                            </div>

                        </div>

                    `
                )
                .join("");
    }


    const hasBad =
        compatibility.some(
            item =>
                item.level === "bad"
        );


    const hasWarning =
        compatibility.some(
            item =>
                item.level === "warn"
        );


    const status =
        document.getElementById(
            "status"
        );


    if (!status) {

        return;
    }


    status.className =
        "status " +
        (
            hasBad
                ? "bad"
                : hasWarning
                    ? "warn"
                    : "ok"
        );


    status.textContent =
        hasBad

            ? "Compatibility issue found"

            : hasWarning

                ? "Build passes, but some details are unavailable"

                : "Build passes basic checks";

}


/* ============================================================
   COMPATIBILITY HELPERS
   ============================================================ */

function getCompatibility(
    type
) {

    return (
        build[type]
            ?.Compatibility
        || {}
    );
}


function cleanArray(
    value
) {

    if (!Array.isArray(value)) {

        return [];
    }


    return value
        .map(
            item =>
                normalizeText(item)
        )
        .filter(Boolean);
}


/* ============================================================
   CHECK MOTHERBOARD ↔ RAM
   ============================================================ */

function checkMotherboardRAM() {

    const motherboard =
        build.motherboard;

    const ram =
        build.ram;


    if (
        !motherboard ||
        !ram
    ) {

        return null;
    }


    const motherboardMemory =
        normalizeText(
            getCompatibility(
                "motherboard"
            ).memory_type
        ).toUpperCase();


    const ramCompatibility =
        getCompatibility(
            "ram"
        );


    let ramMemory =
        normalizeText(
            ramCompatibility.memory_type
        ).toUpperCase();


    /*
     Some RAM records may have DDR information
     embedded in speed.
    */

    if (!ramMemory) {

        const speed =
            normalizeText(
                ramCompatibility.speed
            ).toUpperCase();


        if (
            speed.includes(
                "DDR5"
            )
        ) {

            ramMemory = "DDR5";

        }
        else if (
            speed.includes(
                "DDR4"
            )
        ) {

            ramMemory = "DDR4";
        }

    }


    if (
        motherboardMemory &&
        ramMemory
    ) {

        const compatible =
            motherboardMemory ===
            ramMemory;


        return {

            title:
                "Motherboard ↔ RAM",

            level:
                compatible
                    ? "ok"
                    : "bad",

            text:
                compatible

                    ? `Motherboard uses ${motherboardMemory} and RAM is ${ramMemory}.`

                    : `Motherboard uses ${motherboardMemory}, but RAM is ${ramMemory}.`

        };

    }


    return {

        title:
            "Motherboard ↔ RAM",

        level:
            "warn",

        text:
            "Memory type information is unavailable."

    };

}


/* ============================================================
   CHECK MOTHERBOARD ↔ CASE
   ============================================================ */

function checkMotherboardCase() {

    const motherboard =
        build.motherboard;

    const pcCase =
        build.case;


    if (
        !motherboard ||
        !pcCase
    ) {

        return null;
    }


    const motherboardFormFactor =
        normalizeText(
            getCompatibility(
                "motherboard"
            ).form_factor
        );


    /*
     The normalizer currently stores case motherboard
     compatibility under motherboard_support.

     Some future versions may use form_factor.

     Support both.
    */

    const caseCompatibility =
        getCompatibility(
            "case"
        );


    let caseFormFactors =
        cleanArray(
            caseCompatibility
                .motherboard_support
        );


    if (
        !caseFormFactors.length &&
        caseCompatibility.form_factor
    ) {

        caseFormFactors = [

            normalizeText(
                caseCompatibility.form_factor
            )

        ];

    }


    if (
        motherboardFormFactor &&
        caseFormFactors.length
    ) {

        const compatible =
            caseFormFactors.some(
                supported =>
                    supported ===
                    motherboardFormFactor
            );


        return {

            title:
                "Motherboard ↔ Case",

            level:
                compatible
                    ? "ok"
                    : "bad",

            text:
                compatible

                    ? `Motherboard form factor is ${motherboardFormFactor}; the case supports ${caseFormFactors.join(", ")}.`

                    : `Motherboard is ${motherboardFormFactor}, but the case supports ${caseFormFactors.join(", ")}.`

        };

    }


    return {

        title:
            "Motherboard ↔ Case",

        level:
            "warn",

        text:
            "Case or motherboard form-factor details are unavailable."

    };

}


/* ============================================================
   CHECK GPU ↔ PSU
   ============================================================ */

function checkGraphicsPSU() {

    const graphics =
        build.graphics_card;

    const psu =
        build.power_supply;


    if (
        !graphics ||
        !psu
    ) {

        return null;
    }


    const watts =
        Number(
            getCompatibility(
                "power_supply"
            ).wattage
        );


    const recommended =
        Number(
            getCompatibility(
                "graphics_card"
            ).recommended_psu_wattage
        );


    if (
        watts &&
        recommended
    ) {

        const compatible =
            watts >=
            recommended;


        return {

            title:
                "Graphics Card ↔ Power Supply",

            level:
                compatible
                    ? "ok"
                    : "bad",

            text:
                compatible

                    ? `PSU provides ${watts}W; GPU recommends ${recommended}W.`

                    : `PSU provides ${watts}W, but the GPU recommends ${recommended}W.`

        };

    }


    return {

        title:
            "Graphics Card ↔ Power Supply",

        level:
            "warn",

        text:
            "PSU wattage or GPU recommendation is unavailable."

    };

}


/* ============================================================
   CHECK MOTHERBOARD ↔ COOLING
   ============================================================ */

function checkMotherboardCooling() {

    const motherboard =
        build.motherboard;

    const cooling =
        build.cooling;


    if (
        !motherboard ||
        !cooling
    ) {

        return null;
    }


    const motherboardSocket =
        normalizeText(
            getCompatibility(
                "motherboard"
            ).socket
        )
            .toUpperCase();


    const coolingCompatibility =
        getCompatibility(
            "cooling"
        );


    const sockets =
        cleanArray(
            coolingCompatibility
                .socket_support
        )
            .map(
                socket =>
                    socket.toUpperCase()
            );


    if (
        motherboardSocket &&
        sockets.length
    ) {

        const compatible =
            sockets.includes(
                motherboardSocket
            );


        return {

            title:
                "Motherboard ↔ Cooling",

            level:
                compatible
                    ? "ok"
                    : "bad",

            text:
                compatible

                    ? `Cooling supports ${motherboardSocket}.`

                    : `Cooling does not list support for ${motherboardSocket}.`

        };

    }


    return {

        title:
            "Motherboard ↔ Cooling",

        level:
            "warn",

        text:
            "CPU socket support information is unavailable."

    };

}


/* ============================================================
   CHECK GPU ↔ CASE
   ============================================================ */

function checkGraphicsCase() {

    const graphics =
        build.graphics_card;

    const pcCase =
        build.case;


    if (
        !graphics ||
        !pcCase
    ) {

        return null;
    }


    const gpuLength =
        Number(
            getCompatibility(
                "graphics_card"
            ).length_mm
        );


    const caseClearance =
        Number(
            getCompatibility(
                "case"
            ).gpu_clearance_mm
        );


    if (
        gpuLength &&
        caseClearance
    ) {

        const compatible =
            gpuLength <=
            caseClearance;


        return {

            title:
                "Graphics Card ↔ Case",

            level:
                compatible
                    ? "ok"
                    : "bad",

            text:
                compatible

                    ? `GPU is ${gpuLength}mm; case clearance is ${caseClearance}mm.`

                    : `GPU is ${gpuLength}mm, but case clearance is ${caseClearance}mm.`

        };

    }


    return {

        title:
            "Graphics Card ↔ Case",

        level:
            "warn",

        text:
            "GPU length or case clearance is unavailable."

    };

}


/* ============================================================
   GENERIC PAIR CHECKER
   ============================================================ */

function checkPair(
    relation
) {

    const {
        a,
        b,
        title
    } = relation;


    /*
     ------------------------------------------------------------
     If either component is disabled, ignore relationship.
     ------------------------------------------------------------
    */

    if (
        !BUILDER_CONFIG[a]?.enabled ||
        !BUILDER_CONFIG[b]?.enabled
    ) {

        return null;
    }


    /*
     ------------------------------------------------------------
     If either component isn't selected,
     don't show a warning.
     ------------------------------------------------------------
    */

    if (
        !build[a] ||
        !build[b]
    ) {

        return null;
    }


    /*
     ------------------------------------------------------------
     Route to the correct checker.
     ------------------------------------------------------------
    */

    const pair =
        [a, b]
            .sort()
            .join("|");


    switch (pair) {

        case "motherboard|ram":

            return checkMotherboardRAM();


        case "case|motherboard":

            return checkMotherboardCase();


        case "graphics_card|power_supply":

            return checkGraphicsPSU();


        case "cooling|motherboard":

            return checkMotherboardCooling();


        case "case|graphics_card":

            return checkGraphicsCase();


        default:

            return {

                title,

                level:
                    "warn",

                text:
                    "Compatibility checking for these components has not been implemented yet."

            };

    }

}


/* ============================================================
   MAIN COMPATIBILITY ENGINE
   ============================================================ */

function checks() {

    const out = [];


    /*
     Only relationships explicitly enabled above
     are evaluated.
    */

    COMPATIBILITY_RELATIONS
        .forEach(
            relation => {

                const result =
                    checkPair(
                        relation
                    );


                if (result) {

                    out.push(
                        result
                    );

                }

            }
        );


    return out;

}


/* ============================================================
   PRODUCT MODAL
   ============================================================ */

function openModal(
    type
) {

    if (
        !BUILDER_CONFIG[type]?.enabled
    ) {

        return;
    }


    currentType = type;

    brand = "All";


    const modal =
        document.getElementById(
            "modal"
        );


    if (!modal) {

        return;
    }


    modal.classList.add(
        "open"
    );


    modal.setAttribute(
        "aria-hidden",
        "false"
    );


    const title =
        document.getElementById(
            "modal-title"
        );


    if (title) {

        title.textContent =
            `Choose ${labels[type]}`;
    }


    const search =
        document.getElementById(
            "search"
        );


    if (search) {

        search.value = "";

        search.focus();
    }


    renderFilters();

    renderList();

}


/* ============================================================
   CLOSE MODAL
   ============================================================ */

function closeModal() {

    const modal =
        document.getElementById(
            "modal"
        );


    if (!modal) {

        return;
    }


    modal.classList.remove(
        "open"
    );


    modal.setAttribute(
        "aria-hidden",
        "true"
    );

}


/* ============================================================
   FILTERS
   ============================================================ */

function renderFilters() {

    const filters =
        document.getElementById(
            "filters"
        );


    if (!filters) {

        return;
    }


    const brands = [

        "All",

        ...new Set(

            productsBy(
                currentType
            )
                .map(
                    product =>
                        String(
                            product.Brand || ""
                        ).trim()
                )
                .filter(Boolean)

        )

    ];


    filters.innerHTML =
        brands
            .map(
                brandName => `

                    <button
                        type="button"
                        class="chip ${
                            brandName === brand
                                ? "active"
                                : ""
                        }"
                        data-brand="${escapeHTML(
                            brandName
                        )}"
                    >

                        ${
                            escapeHTML(
                                brandName
                            )
                        }

                    </button>

                `
            )
            .join("");


    filters
        .querySelectorAll(
            ".chip"
        )
        .forEach(
            button => {

                button.addEventListener(
                    "click",
                    () => {

                        brand =
                            button.dataset.brand;


                        filters
                            .querySelectorAll(
                                ".chip"
                            )
                            .forEach(
                                chip => {

                                    chip.classList.toggle(
                                        "active",
                                        chip.dataset.brand ===
                                            brand
                                    );

                                }
                            );


                        renderList();

                    }
                );

            }
        );

}


/* ============================================================
   PRODUCT LIST
   ============================================================ */

function renderList() {

    const searchInput =
        document.getElementById(
            "search"
        );


    const list =
        document.getElementById(
            "list"
        );


    if (
        !searchInput ||
        !list
    ) {

        return;
    }


    const query =
        searchInput.value
            .trim()
            .toLowerCase();


    const filtered =
        productsBy(
            currentType
        )
            .filter(
                product => {

                    const matchesBrand =
                        brand === "All" ||
                        String(
                            product.Brand || ""
                        ).trim() === brand;


                    const productName =
                        String(
                            product[
                                "Product Name"
                            ] || ""
                        )
                            .toLowerCase();


                    const category =
                        String(
                            product.Category || ""
                        )
                            .toLowerCase();


                    return (
                        matchesBrand &&
                        (
                            productName.includes(
                                query
                            ) ||
                            category.includes(
                                query
                            )
                        )
                    );

                }
            );


    list.innerHTML =
        filtered.length

            ? filtered
                .map(
                    product =>
                        productChoiceHTML(
                            product
                        )
                )
                .join("")

            : `

                <div class="empty">
                    No products found.
                </div>

              `;

}


/* ============================================================
   PRODUCT MODAL CARD
   ============================================================ */

function productChoiceHTML(
    product
) {

    const id =
        String(
            product[
                "Product ID"
            ]
        );


    const name =
        escapeHTML(
            product[
                "Product Name"
            ] ||
            "Unnamed product"
        );


    const productBrand =
        escapeHTML(
            product.Brand || ""
        );


    const category =
        escapeHTML(
            String(
                product.Category || ""
            ).toUpperCase()
        );


    const productImage =
        escapeHTML(
            image(product)
        );


    const price =
        money(
            safePrice(product)
        );


    const productURL =
        product[
            "Product URL"
        ]
            ? escapeHTML(
                product[
                    "Product URL"
                ]
            )
            : "";


    return `

        <div class="choice">

            <img
                src="${productImage}"
                alt=""
                onerror="this.style.display='none'"
            >


            <div>

                <div class="pname">
                    ${name}
                </div>


                <div class="meta">

                    ${productBrand}

                    ${
                        productBrand &&
                        category
                            ? " · "
                            : ""
                    }

                    ${category}

                </div>


                <div class="price">
                    PKR ${price}
                </div>

            </div>


            <div class="product-actions">

                <strong>
                    PKR ${price}
                </strong>


                <button
                    type="button"
                    class="btn add-product-btn"
                    data-product-id="${escapeHTML(id)}"
                >
                    Add Product
                </button>


                ${
                    productURL

                        ? `

                            <a
                                class="btn view-product-btn"
                                href="${productURL}"
                                target="_blank"
                                rel="noopener noreferrer"
                            >
                                View Product
                            </a>

                          `

                        : ""
                }

            </div>

        </div>

    `;

}


/* ============================================================
   PRODUCT SELECTION
   ============================================================ */

function selectProduct(
    id
) {

    const product =
        PRODUCTS.find(
            item =>
                String(
                    item[
                        "Product ID"
                    ]
                ) ===
                String(id)
        );


    if (!product) {

        return;
    }


    /*
     ------------------------------------------------------------
     Make sure the product actually belongs to the current
     builder type before selecting it.
     ------------------------------------------------------------
    */

    if (
        resolveProductType(
            product
        ) !== currentType
    ) {

        return;
    }


    build[currentType] =
        product;


    closeModal();

    render();

}


/* ============================================================
   WHATSAPP BUILD MESSAGE
   ============================================================ */

function buildWhatsAppMessage(
    type = "quotation"
) {

    const selected =
        selectedEntries();


    if (!selected.length) {

        return null;
    }


    const total =
        selectedTotal();


    const intro =
        type === "help"

            ? "Hi GB Tech! I need help with this PC build."

            : "Hi GB Tech! I would like to share my PC build quotation.";


    const componentLines =
        selected
            .map(
                (
                    [
                        componentType,
                        product
                    ]
                ) => {

                    const category =
                        String(
                            labels[
                                componentType
                            ] ||
                            componentType
                        ).toUpperCase();


                    const name =
                        product[
                            "Product Name"
                        ] ||
                        "Unnamed product";


                    const price =
                        `PKR ${money(
                            safePrice(
                                product
                            )
                        )}`;


                    return `• ${category}: ${name} — ${price}`;

                }
            )
            .join("\n");


    return `${intro}

GB Tech — Build Your Own PC

Selected components:
${componentLines}

Estimated total: PKR ${money(total)}

Please review this build and let me know if you recommend any changes or if there are any compatibility concerns.

Build tool:
https://build-your-own-pc.gb-tech.pk/`;

}


/* ============================================================
   OPEN WHATSAPP
   ============================================================ */

function openWhatsApp(
    message
) {

    if (!message) {

        alert(
            "Please select at least one component first."
        );

        return false;
    }


    const url =
        `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(
            message
        )}`;


    const newWindow =
        window.open(
            url,
            "_blank"
        );


    if (!newWindow) {

        alert(
            "WhatsApp could not be opened. Please allow pop-ups for this site."
        );

        return false;
    }


    return true;

}


/* ============================================================
   ASK GB TECH ABOUT BUILD
   ============================================================ */

function askGBTechAboutBuild() {

    const selected =
        selectedEntries();


    if (!selected.length) {

        const message =
            "Hi GB Tech, I would like some help choosing components for a PC build.";


        window.open(
            `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(
                message
            )}`,
            "_blank"
        );


        return;
    }


    const total =
        selectedTotal();


    const selectedProducts =
        selected.map(
            (
                [
                    type,
                    product
                ]
            ) => {

                const name =
                    product[
                        "Product Name"
                    ] ||
                    "Product";


                const price =
                    safePrice(
                        product
                    );


                return `${labels[type]}: ${name}${
                    price
                        ? ` — PKR ${money(price)}`
                        : ""
                }`;

            }
        );


    const message = [

        "Hi GB Tech, I would like some help with my PC build.",

        "",

        "Selected components:",

        ...selectedProducts.map(
            item =>
                `• ${item}`
        ),

        "",

        `Estimated build total: PKR ${money(total)}`,

        "",

        "Could you please review this build and advise me if any changes are recommended?"

    ].join("\n");


    window.open(
        `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(
            message
        )}`,
        "_blank"
    );

}


/* ============================================================
   SEARCH
   ============================================================ */

const searchElement =
    document.getElementById(
        "search"
    );


if (searchElement) {

    searchElement.addEventListener(
        "input",
        renderList
    );

}


/* ============================================================
   PRODUCT BUTTON DELEGATION
   ============================================================ */

const productListElement =
    document.getElementById(
        "list"
    );


if (productListElement) {

    productListElement.addEventListener(
        "click",
        event => {

            const button =
                event.target.closest(
                    ".add-product-btn"
                );


            if (!button) {

                return;
            }


            event.preventDefault();

            event.stopPropagation();


            selectProduct(
                button.dataset.productId
            );

        }
    );

}


/* ============================================================
   KEYBOARD
   ============================================================ */

document.addEventListener(
    "keydown",
    event => {

        if (
            event.key ===
            "Escape"
        ) {

            closeModal();

        }

    }
);


/* ============================================================
   CLICK OUTSIDE MODAL
   ============================================================ */

const modalElement =
    document.getElementById(
        "modal"
    );


if (modalElement) {

    modalElement.addEventListener(
        "click",
        event => {

            if (
                event.target.id ===
                "modal"
            ) {

                closeModal();

            }

        }
    );

}


/* ============================================================
   PDF IMAGE LOADER
   ============================================================ */

function loadImageAsDataURL(
    src
) {

    return new Promise(
        (
            resolve,
            reject
        ) => {

            const img =
                new Image();


            img.onload =
                () => {

                    const canvas =
                        document.createElement(
                            "canvas"
                        );


                    canvas.width =
                        img.naturalWidth;

                    canvas.height =
                        img.naturalHeight;


                    const context =
                        canvas.getContext(
                            "2d"
                        );


                    context.drawImage(
                        img,
                        0,
                        0,
                        img.naturalWidth,
                        img.naturalHeight
                    );


                    resolve({

                        data:
                            canvas.toDataURL(
                                "image/png"
                            ),

                        width:
                            img.naturalWidth,

                        height:
                            img.naturalHeight

                    });

                };


            img.onerror =
                () => {

                    reject(
                        new Error(
                            "Could not load image: " +
                            src
                        )
                    );

                };


            img.src =
                src;

        }
    );

}


/* ============================================================
   PDF COMPATIBILITY TITLE
   ============================================================ */

function pdfSafeCompatibilityTitle(
    title
) {

    return String(
        title || ""
    )
        .replace(
            /↔/g,
            " / "
        )
        .replace(
            /\s+/g,
            " "
        )
        .trim();

}


/* ============================================================
   PDF QUOTATION
   ============================================================ */

async function downloadSelectedPDF() {

    const {
        jsPDF
    } =
        window.jspdf || {};


    if (!jsPDF) {

        alert(
            "PDF library could not be loaded. Please check your internet connection."
        );

        return;
    }


    const selected =
        selectedEntries();


    if (
        !selected.length
    ) {

        alert(
            "Please select your PC components first."
        );

        return;
    }


    const doc =
        new jsPDF({

            unit:
                "mm",

            format:
                "a4",

            orientation:
                "portrait"

        });


    const pageWidth =
        doc.internal.pageSize
            .getWidth();


    const pageHeight =
        doc.internal.pageSize
            .getHeight();


    const margin = 15;


    const contentWidth =
        pageWidth -
        margin * 2;


    const DARK =
        [17, 19, 23];


    const GOLD =
        [214, 179, 92];


    const TEXT =
        [45, 45, 45];


    const MUTED =
        [105, 105, 105];


    const RED =
        [180, 48, 48];


    const RED_BG =
        [253, 239, 239];


    const GREEN =
        [52, 125, 68];


    /* ========================================================
       HEADER
       ======================================================== */

    const headerY = 10;

    const headerHeight = 32;


    doc.setFillColor(
        ...DARK
    );


    doc.roundedRect(
        margin,
        headerY,
        contentWidth,
        headerHeight,
        5,
        5,
        "F"
    );


    let logoLoaded =
        false;


    try {

        const logo =
            await loadImageAsDataURL(
                "media/GB tech logo.png"
            );


        const maxLogoWidth =
            48;


        const maxLogoHeight =
            26;


        const aspectRatio =
            logo.width /
            logo.height;


        let logoWidth =
            maxLogoWidth;


        let logoHeight =
            logoWidth /
            aspectRatio;


        if (
            logoHeight >
            maxLogoHeight
        ) {

            logoHeight =
                maxLogoHeight;


            logoWidth =
                logoHeight *
                aspectRatio;

        }


        const logoX =
            margin + 7;


        const logoY =
            headerY +
            (
                headerHeight -
                logoHeight
            ) / 2;


        doc.addImage(
            logo.data,
            "PNG",
            logoX,
            logoY,
            logoWidth,
            logoHeight
        );


        logoLoaded =
            true;

    }
    catch (error) {

        console.warn(
            "Could not load PDF logo.",
            error
        );

    }


    const titleX =
        logoLoaded
            ? margin + 58
            : margin + 8;


    doc.setTextColor(
        255,
        255,
        255
    );


    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.setFontSize(
        17
    );


    doc.text(
        "PC BUILD QUOTATION",
        titleX,
        headerY + 12
    );


    doc.setFont(
        "helvetica",
        "normal"
    );


    doc.setFontSize(
        9
    );


    doc.setTextColor(
        205,
        210,
        220
    );


    doc.text(
        "GB Tech — Build Your Own PC",
        titleX,
        headerY + 20
    );


    doc.text(
        `Generated: ${new Date().toLocaleDateString("en-GB")}`,
        titleX,
        headerY + 27
    );


    /* ========================================================
       SELECTED COMPONENTS
       ======================================================== */

    let y =
        headerY +
        headerHeight +
        13;


    doc.setTextColor(
        ...TEXT
    );


    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.setFontSize(
        13
    );


    doc.text(
        "SELECTED COMPONENTS",
        margin,
        y
    );


    y += 7;


    const tableRows =
        selected.map(
            (
                [
                    type,
                    product
                ]
            ) => [

                String(
                    labels[type] ||
                    type
                ).toUpperCase(),

                product[
                    "Product Name"
                ] ||
                    "—",

                product.Brand ||
                    "—",

                `PKR ${money(
                    safePrice(
                        product
                    )
                )}`

            ]
        );


    const total =
        selected.reduce(
            (
                sum,
                [, product]
            ) =>
                sum +
                safePrice(
                    product
                ),
            0
        );


    doc.autoTable({

        startY: y,

        margin: {
            left: margin,
            right: margin
        },

        tableWidth:
            contentWidth,

        head: [[
            "COMPONENT",
            "PRODUCT",
            "BRAND",
            "PRICE"
        ]],

        body:
            tableRows,

        theme:
            "grid",

        styles: {

            font:
                "helvetica",

            fontSize:
                8.5,

            cellPadding:
                4,

            textColor:
                TEXT,

            lineColor:
                [218, 218, 218],

            lineWidth:
                0.2,

            valign:
                "middle",

            overflow:
                "linebreak"

        },

        headStyles: {

            fillColor:
                DARK,

            textColor:
                GOLD,

            fontStyle:
                "bold",

            fontSize:
                8.5,

            cellPadding:
                4,

            valign:
                "middle"

        },

        bodyStyles: {

            fillColor:
                [249, 249, 249]

        },

        alternateRowStyles: {

            fillColor:
                [243, 243, 243]

        },

        columnStyles: {

            0: {

                cellWidth:
                    40,

                fontStyle:
                    "bold"

            },

            1: {

                cellWidth:
                    86

            },

            2: {

                cellWidth:
                    25

            },

            3: {

                cellWidth:
                    29,

                halign:
                    "right",

                fontStyle:
                    "bold"

            }

        },

        didParseCell(
            data
        ) {

            data.cell.styles.charSpace =
                0;

        }

    });


    /* ========================================================
       TOTAL BAR
       ======================================================== */

    y =
        doc.lastAutoTable.finalY +
        8;


    const totalHeight =
        11;


    if (
        y + totalHeight >
        pageHeight - 55
    ) {

        doc.addPage();

        y = 18;

    }


    doc.setFillColor(
        ...DARK
    );


    doc.roundedRect(
        margin,
        y,
        contentWidth,
        totalHeight,
        3.5,
        3.5,
        "F"
    );


    doc.setTextColor(
        ...GOLD
    );


    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.setFontSize(
        9.5
    );


    const totalBaseline =
        y + 7;


    doc.text(
        "TOTAL BUILD",
        margin + 7,
        totalBaseline
    );


    doc.text(
        `PKR ${money(total)}`,
        pageWidth - margin - 7,
        totalBaseline,
        {
            align:
                "right"
        }
    );


    /* ========================================================
       COMPATIBILITY
       ======================================================== */

    y +=
        totalHeight +
        10;


    if (
        y >
        pageHeight - 75
    ) {

        doc.addPage();

        y = 20;

    }


    doc.setTextColor(
        ...TEXT
    );


    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.setFontSize(
        10.5
    );


    doc.text(
        "COMPATIBILITY CHECK",
        margin,
        y
    );


    y += 7;


    const compatibility =
        checks();


    const issues =
        compatibility.filter(
            item =>
                item.level === "bad" ||
                item.level === "warn"
        );


    if (
        !issues.length
    ) {

        doc.setFont(
            "helvetica",
            "bold"
        );


        doc.setFontSize(
            8.5
        );


        doc.setTextColor(
            ...GREEN
        );


        doc.text(
            "No compatibility conflicts were identified from the available specifications.",
            margin,
            y
        );


        y += 12;

    }
    else {

        issues.forEach(
            issue => {

                const title =
                    pdfSafeCompatibilityTitle(
                        issue.title
                    );


                const message =
                    String(
                        issue.text || ""
                    )
                        .replace(
                            /\s+/g,
                            " "
                        )
                        .trim();


                doc.setFont(
                    "helvetica",
                    "normal"
                );


                doc.setFontSize(
                    7.5
                );


                const messageLines =
                    doc.splitTextToSize(
                        message,
                        contentWidth - 14
                    );


                const boxHeight =
                    23 +
                    Math.max(
                        0,
                        (
                            messageLines.length -
                            1
                        ) * 3.5
                    );


                if (
                    y + boxHeight >
                    pageHeight - 55
                ) {

                    doc.addPage();

                    y = 20;

                }


                doc.setFillColor(
                    ...RED_BG
                );


                doc.roundedRect(
                    margin,
                    y,
                    contentWidth,
                    boxHeight,
                    3,
                    3,
                    "F"
                );


                doc.setTextColor(
                    ...RED
                );


                doc.setFont(
                    "helvetica",
                    "bold"
                );


                doc.setFontSize(
                    8.5
                );


                doc.text(
                    issue.level === "bad"
                        ? "Compatibility issue found"
                        : "Compatibility information unavailable",
                    margin + 7,
                    y + 7
                );


                doc.setTextColor(
                    ...TEXT
                );


                doc.setFont(
                    "helvetica",
                    "bold"
                );


                doc.setFontSize(
                    8
                );


                doc.text(
                    title,
                    margin + 7,
                    y + 13
                );


                doc.setFont(
                    "helvetica",
                    "normal"
                );


                doc.setFontSize(
                    7.5
                );


                doc.setTextColor(
                    ...MUTED
                );


                doc.text(
                    messageLines,
                    margin + 7,
                    y + 18,
                    {
                        lineHeightFactor:
                            1.15
                    }
                );


                y +=
                    boxHeight +
                    6;

            }
        );

    }


    /* ========================================================
       IMPORTANT INFORMATION
       ======================================================== */

    if (
        y >
        pageHeight - 65
    ) {

        doc.addPage();

        y = 20;

    }


    y += 2;


    doc.setDrawColor(
        210,
        210,
        210
    );


    doc.setLineWidth(
        0.25
    );


    doc.line(
        margin,
        y,
        pageWidth - margin,
        y
    );


    y += 8;


    doc.setTextColor(
        ...TEXT
    );


    doc.setFont(
        "helvetica",
        "bold"
    );


    doc.setFontSize(
        10
    );


    doc.text(
        "IMPORTANT INFORMATION",
        margin,
        y
    );


    y += 7;


    doc.setFont(
        "helvetica",
        "normal"
    );


    doc.setFontSize(
        7.5
    );


    doc.setTextColor(
        ...MUTED
    );


    const disclaimers = [

        "Prices shown are estimates and may change due to supplier pricing, market conditions, or other factors.",

        "Compatibility should be independently confirmed before purchase. The builder's checks are intended as guidance only.",

        "Product availability and stock status may change between generating this quotation and placing an order.",

        "Product specifications are based on the information available in the GB Tech product data at the time of generation."

    ];


    disclaimers.forEach(
        text => {

            const lines =
                doc.splitTextToSize(
                    `• ${text}`,
                    contentWidth
                );


            doc.text(
                lines,
                margin,
                y,
                {

                    charSpace:
                        0,

                    lineHeightFactor:
                        1.25

                }
            );


            y +=
                lines.length *
                3.8 +
                3;

        }
    );


    /* ========================================================
       FOOTER
       ======================================================== */

    const footerLineY =
        pageHeight -
        18;


    doc.setDrawColor(
        ...GOLD
    );


    doc.setLineWidth(
        0.25
    );


    doc.line(
        margin,
        footerLineY,
        pageWidth - margin,
        footerLineY
    );


    doc.setFont(
        "helvetica",
        "normal"
    );


    doc.setFontSize(
        7.5
    );


    doc.setTextColor(
        120,
        120,
        120
    );


    doc.text(
        "GB Tech — Your Ultimate Gaming Hub",
        margin,
        pageHeight - 10
    );


    doc.text(
        "gb-tech.pk",
        pageWidth - margin,
        pageHeight - 10,
        {
            align:
                "right"
        }
    );


    doc.save(
        "GB-Tech-PC-Build-Quotation.pdf"
    );

}


/* ============================================================
   OPTIONAL PDF FOOTER
   ============================================================ */

function addPDFFooter(
    doc,
    pageWidth,
    pageHeight
) {

    doc.setDrawColor(
        225,
        226,
        229
    );


    doc.line(
        15,
        pageHeight - 15,
        pageWidth - 15,
        pageHeight - 15
    );


    doc.setFont(
        "helvetica",
        "normal"
    );


    doc.setFontSize(
        7
    );


    doc.setTextColor(
        130,
        134,
        140
    );


    doc.text(
        "GB Tech — Build Your Own PC",
        15,
        pageHeight - 9
    );


    doc.text(
        "Generated quotation",
        pageWidth - 15,
        pageHeight - 9,
        {
            align:
                "right"
        }
    );

}


/* ============================================================
   START
   ============================================================ */

loadProducts();