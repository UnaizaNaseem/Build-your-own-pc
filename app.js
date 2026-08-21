/* ============================================================
   GB TECH — BUILD YOUR OWN PC
   APPLICATION LOGIC
   ============================================================ */

const PRODUCTS = [];

let build = {};
let currentType = "";
let brand = "All";

const WHATSAPP_NUMBER = "923055183777";

const categories = [
  "motherboard",
  "graphics_card",
  "ram",
  "case",
  "cooling",
  "power_supply",
  "fan"
];

const labels = {
  motherboard: "Motherboard",
  graphics_card: "Graphics Card",
  ram: "RAM",
  case: "Case",
  cooling: "CPU Cooling",
  power_supply: "Power Supply",
  fan: "Case Fans"
};


/* ============================================================
   HELPERS
   ============================================================ */

const money = (value) => {
  return new Intl.NumberFormat("en-PK", {
    maximumFractionDigits: 0
  }).format(Number(value) || 0);
};


const safePrice = (product) => {
  return Number(product?.Price) || 0;
};


const image = (product) => {
  return product?.Image || "";
};


/* ============================================================
   PRODUCT CATEGORY RESOLVER

   Compatibility.type is useful for compatibility checks,
   but it should NOT be the only way we decide where a product
   appears in the builder.

   GB Tech's actual Category path is the fallback.

   This means products will not disappear simply because
   their compatibility data is incomplete.
   ============================================================ */

const getProductCategory = (product) => {
  return String(
    product?.Category || ""
  )
    .trim()
    .toLowerCase();
};


const getProductCompatibilityType = (product) => {
  return String(
    product?.Compatibility?.type || ""
  )
    .trim()
    .toLowerCase();
};


/* ============================================================
   DETERMINE BUILDER TYPE
   ============================================================ */

const resolveProductType = (product) => {

  const compatibilityType =
    getProductCompatibilityType(product);

  const category =
    getProductCategory(product);


  /* ----------------------------------------------------------
     FIRST:
     Trust an explicit compatibility type when it is one of
     our known builder types.
     ---------------------------------------------------------- */

  const validTypes = [
    "motherboard",
    "graphics_card",
    "ram",
    "case",
    "cooling",
    "power_supply",
    "fan"
  ];


  if (
    validTypes.includes(
      compatibilityType
    )
  ) {
    return compatibilityType;
  }


  /* ----------------------------------------------------------
     CATEGORY FALLBACK
     ---------------------------------------------------------- */

  if (
    category.includes("motherboard")
  ) {
    return "motherboard";
  }


  if (
    category.includes("graphics card") ||
    category.includes("graphics cards") ||
    category.includes("gpu") ||
    category.includes("video card")
  ) {
    return "graphics_card";
  }


  if (
    category.includes("ram") ||
    category.includes("memory")
  ) {
    return "ram";
  }


  if (
    category.includes("power supply") ||
    category.includes("power supplies") ||
    category.includes("psu")
  ) {
    return "power_supply";
  }


  if (
    category.includes("case") ||
    category.includes("chassis")
  ) {
    return "case";
  }


  /* ----------------------------------------------------------
     CASE FANS

     These must be checked BEFORE generic cooling.
     ---------------------------------------------------------- */

  if (
    category.includes("case fan") ||
    category.includes("case fans") ||
    category.includes("fans") ||
    category.includes("fan")
  ) {
    return "fan";
  }


  /* ----------------------------------------------------------
     CPU COOLING / LIQUID COOLING

     This catches:

       PC Components > Cooling
       PC Components > Liquid Cooling
       PC Components > CPU Cooler
       PC Components > CPU Coolers
       etc.
     ---------------------------------------------------------- */

  if (
    category.includes("cooling") ||
    category.includes("cooler") ||
    category.includes("liquid") ||
    category.includes("aio") ||
    category.includes("radiator")
  ) {
    return "cooling";
  }


  return "";
};


/* ============================================================
   PRODUCTS BY BUILDER TYPE

   IMPORTANT:
   We now resolve the product from BOTH:

   1. Compatibility.type
   2. GB Tech Category

   Therefore products don't silently disappear.
   ============================================================ */

const productsBy = (type) => {

  return PRODUCTS.filter(
    product =>
      resolveProductType(product) === type
  );

};


const escapeHTML = (value) => {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
};


const selectedEntries = () => {
  return Object.entries(build)
    .filter(([, product]) => product);
};


const selectedTotal = () => {
  return selectedEntries().reduce(
    (total, [, product]) => total + safePrice(product),
    0
  );
};


/* ============================================================
   LOAD PRODUCTS
   ============================================================ */

async function loadProducts() {

  try {

    const response = await fetch(
      "./pc_components_normalized.json",
      {
        cache: "no-store"
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (!Array.isArray(data)) {
      throw new Error(
        "pc_components_normalized.json must contain an array."
      );
    }

    PRODUCTS.push(...data);

    render();

  } catch (error) {

    console.error(
      "Could not load product data:",
      error
    );

    document.getElementById("builder").innerHTML = `
      <div class="empty">
        Could not load product data.
        Make sure
        <b>pc_components_normalized.json</b>
        is in the same folder as index.html.
      </div>
    `;
  }
}


/* ============================================================
   MAIN BUILDER RENDER
   ============================================================ */

function render() {

  const builder = document.getElementById("builder");

  builder.innerHTML = categories
    .map((type, index) => {

      const product = build[type];

      return `
        <div class="step">

          <div class="stephead">

            <div class="stepname">
              ${index + 1}. ${escapeHTML(labels[type])}
            </div>

            <div class="selected">
              ${product ? "Selected" : "Not selected"}
            </div>

          </div>


          ${
            product
              ? selectedProductHTML(type, product)
              : `
                <button
                  type="button"
                  class="btn add-product-btn"
                  onclick="openModal('${type}')"
                >
                  Add ${escapeHTML(labels[type])}
                </button>
              `
          }

        </div>
      `;

    })
    .join("");

  updateSummary();
}


/* ============================================================
   SELECTED PRODUCT CARD
   ============================================================ */

function selectedProductHTML(type, product) {

  const productName =
    escapeHTML(product["Product Name"] || "Unnamed product");

  const productBrand =
    escapeHTML(product.Brand || "");

  const productImage =
    escapeHTML(image(product));

  const productPrice =
    money(safePrice(product));

  const productURL =
    product["Product URL"]
      ? escapeHTML(product["Product URL"])
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

      </div>

    </div>
  `;
}


/* ============================================================
   SUMMARY
   ============================================================ */

function updateSummary() {

  const total = selectedTotal();

  document.getElementById("total").textContent =
    `PKR ${money(total)}`;


  const compatibility = checks();


  document.getElementById("compat").innerHTML =
    compatibility
      .map(item => `
        <div class="compat ${item.level}">

          <span class="dot"></span>

          <div>

            <b>
              ${escapeHTML(item.title)}
            </b>

            <br>

            ${escapeHTML(item.text)}

          </div>

        </div>
      `)
      .join("");


  const hasBad =
    compatibility.some(
      item => item.level === "bad"
    );


  const hasWarning =
    compatibility.some(
      item => item.level === "warn"
    );


  const status =
    document.getElementById("status");


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
   COMPATIBILITY CHECKS
   ============================================================ */

function checks() {

  const out = [];

  const motherboard = build.motherboard;
  const ram = build.ram;
  const graphics = build.graphics_card;
  const pcCase = build.case;
  const cooling = build.cooling;
  const psu = build.power_supply;


  /* ----------------------------------------------------------
     MOTHERBOARD ↔ RAM
     ---------------------------------------------------------- */

  if (motherboard && ram) {

    const motherboardMemory =
      String(
        motherboard.Compatibility?.memory_type || ""
      ).toUpperCase();


    const ramMemory =
      String(
        ram.Compatibility?.memory_type || ""
      ).toUpperCase();


    const ramSpeed =
      String(
        ram.Compatibility?.speed || ""
      ).toUpperCase();


    const inferred =
      ramSpeed.includes("DDR5")
        ? "DDR5"
        : ramSpeed.includes("DDR4")
          ? "DDR4"
          : "";


    const ramType =
      ramMemory || inferred;


    if (motherboardMemory && ramType) {

      out.push({
        title: "Motherboard ↔ RAM",

        level:
          motherboardMemory === ramType
            ? "ok"
            : "bad",

        text:
          motherboardMemory === ramType
            ? `Motherboard uses ${motherboardMemory} and RAM is ${ramType}.`
            : `Motherboard uses ${motherboardMemory}, but RAM is ${ramType}.`
      });

    } else {

      out.push({
        title: "Motherboard ↔ RAM",
        level: "warn",
        text: "Memory type information is unavailable."
      });

    }
  }


  /* ----------------------------------------------------------
     MOTHERBOARD ↔ CASE
     ---------------------------------------------------------- */

  if (motherboard && pcCase) {

    const motherboardFormFactor =
      String(
        motherboard.Compatibility?.form_factor || ""
      ).toLowerCase();


    const caseFormFactor =
      String(
        pcCase.Compatibility?.form_factor || ""
      ).toLowerCase();


    if (
      motherboardFormFactor &&
      caseFormFactor
    ) {

      const compatible =
        caseFormFactor.includes(motherboardFormFactor) ||
        motherboardFormFactor.includes(caseFormFactor);


      out.push({

        title: "Motherboard ↔ Case",

        level:
          compatible
            ? "ok"
            : "bad",

        text:
          `Motherboard: ${motherboardFormFactor}; case support: ${caseFormFactor}.`

      });

    } else {

      out.push({

        title: "Motherboard ↔ Case",

        level: "warn",

        text:
          "Case or motherboard form-factor details are unavailable."

      });

    }
  }


  /* ----------------------------------------------------------
     GPU ↔ PSU
     ---------------------------------------------------------- */

  if (graphics && psu) {

    const watts =
      Number(
        psu.Compatibility?.wattage
      );


    const recommended =
      Number(
        graphics.Compatibility?.recommended_psu_wattage
      );


    if (watts && recommended) {

      out.push({

        title:
          "Graphics Card ↔ Power Supply",

        level:
          watts >= recommended
            ? "ok"
            : "bad",

        text:
          `PSU provides ${watts}W; GPU recommends ${recommended}W.`

      });

    } else {

      out.push({

        title:
          "Graphics Card ↔ Power Supply",

        level: "warn",

        text:
          "PSU wattage or GPU recommendation is unavailable."

      });

    }
  }


  /* ----------------------------------------------------------
     MOTHERBOARD ↔ COOLING
     ---------------------------------------------------------- */

  if (motherboard && cooling) {

    const sockets =
      cooling.Compatibility?.supported_sockets ||
      cooling.Compatibility?.socket_support ||
      [];


    const motherboardSocket =
      motherboard.Compatibility?.socket;


    if (
      motherboardSocket &&
      sockets.length
    ) {

      const compatible =
        sockets.includes(motherboardSocket);


      out.push({

        title:
          "Motherboard ↔ Cooling",

        level:
          compatible
            ? "ok"
            : "bad",

        text:
          compatible
            ? `Cooler supports ${motherboardSocket}.`
            : `Cooler does not list support for ${motherboardSocket}.`

      });

    } else {

      out.push({

        title:
          "Motherboard ↔ Cooling",

        level: "warn",

        text:
          "CPU socket support information is unavailable."

      });

    }
  }


  /* ----------------------------------------------------------
     GPU ↔ CASE
     ---------------------------------------------------------- */

  if (graphics && pcCase) {

    const gpuLength =
      Number(
        graphics.Compatibility?.length_mm
      );


    const caseClearance =
      Number(
        pcCase.Compatibility?.gpu_clearance_mm
      );


    if (
      gpuLength &&
      caseClearance
    ) {

      const compatible =
        gpuLength <= caseClearance;


      out.push({

        title:
          "Graphics Card ↔ Case",

        level:
          compatible
            ? "ok"
            : "bad",

        text:
          compatible
            ? `GPU is ${gpuLength}mm; case clearance is ${caseClearance}mm.`
            : `GPU is ${gpuLength}mm but case clearance is ${caseClearance}mm.`

      });

    } else {

      out.push({

        title:
          "Graphics Card ↔ Case",

        level: "warn",

        text:
          "GPU length or case clearance is unavailable."

      });

    }
  }


  /* ----------------------------------------------------------
     FAN ↔ CASE
     ---------------------------------------------------------- */

  if (build.fan && pcCase) {

    const fanSize =
      Number(
        build.fan.Compatibility?.size_mm
      );


    const caseFanSupport =
      pcCase.Compatibility?.fan_support;


    if (
      fanSize &&
      caseFanSupport
    ) {

      out.push({

        title:
          "Fan ↔ Case",

        level: "ok",

        text:
          `Fan size: ${fanSize}mm; case fan support is available.`

      });

    } else {

      out.push({

        title:
          "Fan ↔ Case",

        level: "warn",

        text:
          "Fan/case size information could not be verified."

      });

    }
  }


  return out;
}


/* ============================================================
   PRODUCT MODAL
   ============================================================ */

function openModal(type) {

  currentType = type;

  brand = "All";


  const modal =
    document.getElementById("modal");


  modal.classList.add("open");

  modal.setAttribute(
    "aria-hidden",
    "false"
  );


  document.getElementById("modal-title")
    .textContent =
      `Choose ${labels[type]}`;


  const search =
    document.getElementById("search");

  search.value = "";

  search.focus();


  renderFilters();

  renderList();
}


function closeModal() {

  const modal =
    document.getElementById("modal");


  modal.classList.remove("open");

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
    document.getElementById("filters");


  const brands = [
    "All",
    ...new Set(
      productsBy(currentType)
        .map(product =>
          String(product.Brand || "").trim()
        )
        .filter(Boolean)
    )
  ];


  filters.innerHTML =
    brands
      .map(brandName => `
        <button
          type="button"
          class="chip ${brandName === brand ? "active" : ""}"
          data-brand="${escapeHTML(brandName)}"
        >
          ${escapeHTML(brandName)}
        </button>
      `)
      .join("");


  filters
    .querySelectorAll(".chip")
    .forEach(button => {

      button.addEventListener(
        "click",
        () => {

          brand =
            button.dataset.brand;

          filters
            .querySelectorAll(".chip")
            .forEach(chip => {

              chip.classList.toggle(
                "active",
                chip.dataset.brand === brand
              );

            });

          renderList();

        }
      );

    });
}


/* ============================================================
   PRODUCT LIST
   ============================================================ */

function renderList() {

  const searchInput =
    document.getElementById("search");


  const query =
    searchInput.value
      .trim()
      .toLowerCase();


  const filtered =
    productsBy(currentType)
      .filter(product => {

        const matchesBrand =
          brand === "All" ||
          String(product.Brand || "").trim() === brand;


        const productName =
          String(
            product["Product Name"] || ""
          ).toLowerCase();


        const category =
          String(
            product.Category || ""
          ).toLowerCase();


        return (
          matchesBrand &&
          (
            productName.includes(query) ||
            category.includes(query)
          )
        );

      });


  document.getElementById("list").innerHTML =
    filtered.length
      ? filtered
          .map(product => productChoiceHTML(product))
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

function productChoiceHTML(product) {

  const id =
    String(product["Product ID"]);


  const name =
    escapeHTML(
      product["Product Name"] ||
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
    product["Product URL"]
      ? escapeHTML(
          product["Product URL"]
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
            productBrand && category
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

function selectProduct(id) {

  const product =
    PRODUCTS.find(
      item =>
        String(item["Product ID"]) ===
        String(id)
    );


  if (!product) {
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

function buildWhatsAppMessage(type = "quotation") {

  const selected =
    selectedEntries();


  if (!selected.length) {
    return null;
  }


  const total =
    selectedTotal();


  let intro =
    type === "help"
      ? "Hi GB Tech! I need help with this PC build."
      : "Hi GB Tech! I would like to share my PC build quotation.";


  const componentLines =
    selected
      .map(
        ([componentType, product]) => {

          const category =
            labels[componentType]
              .toUpperCase();


          const name =
            product["Product Name"] ||
            "Unnamed product";


          const price =
            `PKR ${money(
              safePrice(product)
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

function openWhatsApp(message) {

  if (!message) {

    alert(
      "Please select at least one component first."
    );

    return false;
  }


  const url =
    `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(message)}`;


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

  const selectedProducts = [];

  Object.keys(selected || {}).forEach(category => {

    const product = selected[category];

    if (!product) return;

    const productName =
      product.name ||
      product.title ||
      product.product_name ||
      "Product";

    const price =
      Number(
        product.price ||
        product.sale_price ||
        product.product_price ||
        0
      );

    selectedProducts.push(
      `${productName}${price ? ` — PKR ${price.toLocaleString()}` : ""}`
    );
  });


  if (!selectedProducts.length) {

    const message =
      "Hi GB Tech, I would like some help choosing components for a PC build.";

    window.open(
      `https://wa.me/923055183777?text=${encodeURIComponent(message)}`,
      "_blank"
    );

    return;
  }


  const totalElement =
    document.getElementById("total");

  const total =
    totalElement
      ? totalElement.innerText.trim()
      : "PKR 0";


  const message = [
    "Hi GB Tech, I would like some help with my PC build.",
    "",
    "Selected components:",
    ...selectedProducts.map(
      item => `• ${item}`
    ),
    "",
    `Estimated build total: ${total}`,
    "",
    "Could you please review this build and advise me if any changes are recommended?"
  ].join("\n");


  window.open(
    `https://wa.me/923055183777?text=${encodeURIComponent(message)}`,
    "_blank"
  );
}


/* ============================================================
   SEARCH
   ============================================================ */

document
  .getElementById("search")
  .addEventListener(
    "input",
    renderList
  );


/* ============================================================
   PRODUCT BUTTON DELEGATION
   ============================================================ */

document
  .getElementById("list")
  .addEventListener(
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


/* ============================================================
   KEYBOARD
   ============================================================ */

document.addEventListener(
  "keydown",
  event => {

    if (
      event.key === "Escape"
    ) {

      closeModal();

    }

  }
);


/* ============================================================
   CLICK OUTSIDE MODAL
   ============================================================ */

document
  .getElementById("modal")
  .addEventListener(
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


/* ============================================================
   PDF — LOAD LOCAL IMAGE
   ============================================================ */

/* ============================================================
   PDF — LOAD LOCAL IMAGE WITHOUT DISTORTION
   ============================================================ */

function loadImageAsDataURL(src) {
  return new Promise((resolve, reject) => {

    const img = new Image();

    img.onload = () => {

      const canvas = document.createElement("canvas");

      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;

      const context = canvas.getContext("2d");

      context.drawImage(
        img,
        0,
        0,
        img.naturalWidth,
        img.naturalHeight
      );

      resolve({
        data: canvas.toDataURL("image/png"),
        width: img.naturalWidth,
        height: img.naturalHeight
      });

    };

    img.onerror = () => {
      reject(new Error("Could not load image: " + src));
    };

    img.src = src;
  });
}

function pdfSafeCompatibilityTitle(title) {

  return String(title || "")
    .replace(/↔/g, " / ")
    .replace(/\s+/g, " ")
    .trim();

}


/* ============================================================
   PDF — GB TECH PC BUILD QUOTATION
   ============================================================ */

async function downloadSelectedPDF() {

  const { jsPDF } = window.jspdf || {};

  if (!jsPDF) {
    alert(
      "PDF library could not be loaded. Please check your internet connection."
    );
    return;
  }

  /*
    IMPORTANT:
    Your actual builder stores selected products in `build`.
    selectedEntries() returns:
    [
      ["motherboard", product],
      ["ram", product],
      ...
    ]
  */

  const selected = selectedEntries();

  if (!selected || !selected.length) {
    alert("Please select your PC components first.");
    return;
  }


  /* ============================================================
     PDF SETUP
     ============================================================ */

  const doc = new jsPDF({
    unit: "mm",
    format: "a4",
    orientation: "portrait"
  });

  const pageWidth =
    doc.internal.pageSize.getWidth();

  const pageHeight =
    doc.internal.pageSize.getHeight();

  const margin = 15;

  const contentWidth =
    pageWidth - (margin * 2);


  /* ============================================================
     COLORS
     ============================================================ */

  const DARK = [17, 19, 23];
  const GOLD = [214, 179, 92];

  const TEXT = [45, 45, 45];
  const MUTED = [105, 105, 105];

  const RED = [180, 48, 48];
  const RED_BG = [253, 239, 239];

  const GREEN = [52, 125, 68];


  /* ============================================================
     HEADER
     ============================================================ */

  const headerY = 10;
  const headerHeight = 32;

  doc.setFillColor(...DARK);

  doc.roundedRect(
    margin,
    headerY,
    contentWidth,
    headerHeight,
    5,
    5,
    "F"
  );


  /*
    LOAD LOGO
    Preserve original aspect ratio.
  */

  let logoLoaded = false;

  try {
    const logo = await loadImageAsDataURL(
    "media/GB tech logo.png"
  );

  /*
     Keep the original aspect ratio.
     The logo is intentionally larger but never stretched.
  */

  const maxLogoWidth = 48;
  const maxLogoHeight = 26;

  const aspectRatio =
    logo.width / logo.height;

  let logoWidth = maxLogoWidth;
  let logoHeight = logoWidth / aspectRatio;

  if (logoHeight > maxLogoHeight) {
    logoHeight = maxLogoHeight;
    logoWidth = logoHeight * aspectRatio;
  }

  const logoX =
    margin + 7;

  const logoY =
    headerY + (headerHeight - logoHeight) / 2;

  doc.addImage(
    logo.data,
    "PNG",
    logoX,
    logoY,
    logoWidth,
    logoHeight
  );

  logoLoaded = true;


  } catch (error) {

    
  console.warn(
    "Could not load PDF logo.",
    error
  );
  }


  /* ============================================================
     HEADER TEXT
     ============================================================ */

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

  doc.setFontSize(17);

  doc.text(
    "PC BUILD QUOTATION",
    titleX,
    headerY + 12
  );


  doc.setFont(
    "helvetica",
    "normal"
  );

  doc.setFontSize(9);

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


  /* ============================================================
     SELECTED COMPONENTS
     ============================================================ */

  let y =
    headerY +
    headerHeight +
    13;

  doc.setTextColor(...TEXT);

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(13);

  doc.text(
    "SELECTED COMPONENTS",
    margin,
    y
  );

  y += 7;


  /* ============================================================
     TABLE DATA
     ============================================================ */

  const tableRows =
    selected.map(
      ([type, product]) => {

        return [
          String(
            labels[type] || type
          ).toUpperCase(),

          product["Product Name"] ||
            "—",

          product.Brand ||
            "—",

          `PKR ${money(
            safePrice(product)
          )}`
        ];
      }
    );


  /* ============================================================
     TOTAL
     ============================================================ */

  const total =
    selected.reduce(
      (sum, [, product]) => {

        return (
          sum +
          safePrice(product)
        );

      },
      0
    );


  /* ============================================================
     PRODUCT TABLE
     ============================================================ */

  doc.autoTable({

    startY: y,

    margin: {
      left: margin,
      right: margin
    },

    tableWidth:
      contentWidth,

    head: [
      [
        "COMPONENT",
        "PRODUCT",
        "BRAND",
        "PRICE"
      ]
    ],

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

      /*
        Category stays wide.
      */

      0: {
        cellWidth: 40,
        fontStyle: "bold"
      },

      /*
        Product is the widest.
      */

      1: {
        cellWidth: 86
      },

      2: {
        cellWidth: 25
      },

      3: {
        cellWidth: 29,
        halign: "right",
        fontStyle: "bold"
      }
    },

    didParseCell(data) {

      /*
        Explicitly eliminate character spacing.
      */

      data.cell.styles.charSpace = 0;
    }
  });


  /* ============================================================
     THIN TOTAL BUILD BAR
     ============================================================ */

  y =
    doc.lastAutoTable.finalY +
    8;


  /*
    MUCH thinner than before.

    11mm high instead of 19mm/25mm.
  */

  const totalHeight = 11;


  /*
    Keep it on the same page where possible.
  */

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


  /*
    Small text.
    Both sides use the EXACT same vertical baseline.
  */

  doc.setTextColor(
    ...GOLD
  );

  doc.setFont(
    "helvetica",
    "bold"
  );

  doc.setFontSize(9.5);


  /*
    This baseline is deliberately centered
    vertically inside the 11mm bar.
  */

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
      align: "right"
    }
  );


  /* ============================================================
     COMPATIBILITY CHECK
     ============================================================ */

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

  doc.setFontSize(10.5);

  doc.text(
    "COMPATIBILITY CHECK",
    margin,
    y
  );

  y += 7;


  /*
    Use the SAME compatibility engine as the website.
    Your app.js already defines checks() for:
    - Motherboard ↔ RAM
    - Motherboard ↔ Case
    - GPU ↔ PSU
    - Motherboard ↔ Cooling
    - GPU ↔ Case
    - Fan ↔ Case
  */

  const compatibility =
    checks();


  const issues =
    compatibility.filter(
      item =>
        item.level === "bad" ||
        item.level === "warn"
    );


  /* ============================================================
     NO ISSUES
     ============================================================ */

  if (!issues.length) {

    doc.setFont(
      "helvetica",
      "bold"
    );

    doc.setFontSize(8.5);

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


  /* ============================================================
   ISSUES
   ============================================================ */

else {

  issues.forEach(issue => {

    /*
      Clean the component names before sending them
      to jsPDF.

      This prevents the weird spaced-out appearance
      caused by unsupported Unicode characters.
    */
    const rawTitle = String(issue.title || "");

    const title = rawTitle
      .replace(/↔/g, " / ")
      .replace(/[^\x20-\x7E]/g, "")
      .replace(/\s+/g, " ")
      .trim();


    /*
      Clean compatibility message
    */
    const message = String(issue.text || "")
      .replace(/\s+/g, " ")
      .trim();


    /*
      Calculate description height
    */
    doc.setFont(
      "helvetica",
      "normal"
    );

    doc.setFontSize(7.5);

    const messageLines =
      doc.splitTextToSize(
        message,
        contentWidth - 14
      );


    const boxHeight =
      23 +
      Math.max(
        0,
        (messageLines.length - 1) * 3.5
      );


    /*
      RED COMPATIBILITY BOX
    */
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


    /*
      ISSUE LABEL
    */
    doc.setTextColor(
      ...RED
    );

    doc.setFont(
      "helvetica",
      "bold"
    );

    doc.setFontSize(8.5);

    doc.text(
      "Compatibility issue found",
      margin + 7,
      y + 7
    );


    /*
      COMPONENT NAMES

      Example:

      MOTHERBOARD / RAM
    */
    doc.setTextColor(
      ...TEXT
    );

    doc.setFont(
      "helvetica",
      "bold"
    );

    doc.setFontSize(8);

    doc.text(
      title,
      margin + 7,
      y + 13
    );


    /*
      EXPLANATION
    */
    doc.setFont(
      "helvetica",
      "normal"
    );

    doc.setFontSize(7.5);

    doc.setTextColor(
      ...MUTED
    );

    doc.text(
      messageLines,
      margin + 7,
      y + 18,
      {
        lineHeightFactor: 1.15
      }
    );


    /*
      Space before next section
    */
    y += boxHeight + 6;

  });

}


  /* ============================================================
     IMPORTANT INFORMATION
     ============================================================ */

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

  doc.setFontSize(10);

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

  doc.setFontSize(7.5);

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
          charSpace: 0,
          lineHeightFactor: 1.25
        }
      );

      y +=
        (lines.length * 3.8) +
        3;
    }
  );


  /* ============================================================
     FOOTER
     ============================================================ */

  const footerLineY =
    pageHeight - 18;


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

  doc.setFontSize(7.5);

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
      align: "right"
    }
  );


  /* ============================================================
     DOWNLOAD
     ============================================================ */

  doc.save(
    "GB-Tech-PC-Build-Quotation.pdf"
  );
}

function addPDFFooter(doc, pageWidth, pageHeight) {

  doc.setDrawColor(225, 226, 229);

  doc.line(
    15,
    pageHeight - 15,
    pageWidth - 15,
    pageHeight - 15
  );

  doc.setFont("helvetica", "normal");
  doc.setFontSize(7);

  doc.setTextColor(130, 134, 140);

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
      align: "right"
    }
  );
}


/* ============================================================
   START
   ============================================================ */

loadProducts();