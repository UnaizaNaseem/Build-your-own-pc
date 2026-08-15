/* ============================================================
   GB TECH PC BUILDER — JAVASCRIPT / LOGIC ONLY
   ============================================================
   This file controls:
   - Loading product data
   - Product selection
   - Search and brand filters
   - Compatibility checks
   - Total price
   - Product links
   - PDF download

   PRODUCT DATA IS NOT HARDCODED HERE.

   Products are loaded from:
   ./pc_components_normalized.json
   ============================================================ */


const PRODUCTS = [];


// ============================================================
// COMPONENT CATEGORIES
// ============================================================

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


// ============================================================
// CURRENT BUILD STATE
// ============================================================

let build = {};

let currentType = "";

let brand = "All";


// Make build available globally if needed
window.gbTechBuild = build;


// ============================================================
// GENERAL HELPERS
// ============================================================

const money = (value) => {

  return new Intl.NumberFormat("en-PK", {
    maximumFractionDigits: 0
  }).format(Number(value) || 0);

};


const productsBy = (type) => {

  return PRODUCTS.filter(product => {

    return (
      product.Compatibility?.type || ""
    ).toLowerCase() === type;

  });

};


const image = (product) => {

  return product?.Image || "";

};


const safePrice = (product) => {

  return Number(product?.Price) || 0;

};


// Prevent product data from being interpreted as HTML
function escapeHtml(value) {

  return String(value ?? "")

    .replaceAll("&", "&amp;")

    .replaceAll("<", "&lt;")

    .replaceAll(">", "&gt;")

    .replaceAll('"', "&quot;")

    .replaceAll("'", "&#039;");

}


// ============================================================
// LOAD PRODUCT DATA
// ============================================================

async function loadProducts() {

  try {

    const response = await fetch(
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


    const data = await response.json();


    if (!Array.isArray(data)) {

      throw new Error(
        "pc_components_normalized.json must contain an array of products."
      );

    }


    PRODUCTS.push(...data);


    render();


  } catch (error) {

    console.error(
      "Could not load product data:",
      error
    );


    const builder =
      document.getElementById("builder");


    if (builder) {

      builder.innerHTML = `

        <div class="empty">

          Could not load product data.

          <br><br>

          Make sure

          <b>
            pc_components_normalized.json
          </b>

          is in the same folder as

          <b>
            index.html
          </b>.

        </div>

      `;

    }

  }

}


// ============================================================
// MAIN BUILDER RENDER
// ============================================================

function render() {

  const builder =
    document.getElementById("builder");


  if (!builder) return;


  builder.innerHTML = categories.map(
    (type, index) => {

      const product =
        build[type];


      // ------------------------------------------------------
      // CATEGORY WITH NO PRODUCT SELECTED
      // ------------------------------------------------------

      if (!product) {

        return `

          <div class="step">

            <div class="stephead">

              <div class="stepname">

                ${index + 1}.
                ${labels[type]}

              </div>

              <div class="selected">

                Not selected

              </div>

            </div>


            <button
              class="btn"
              type="button"
              onclick="openModal('${type}')"
            >

              Choose ${labels[type]}

            </button>

          </div>

        `;

      }


      // ------------------------------------------------------
      // SELECTED PRODUCT
      // ------------------------------------------------------

      const productName =
        escapeHtml(
          product["Product Name"]
        );


      const productBrand =
        escapeHtml(
          product.Brand || ""
        );


      const productImage =
        escapeHtml(
          image(product)
        );


      const productUrl =
        escapeHtml(
          product["Product URL"] || ""
        );


      return `

        <div class="step">

          <div class="stephead">

            <div class="stepname">

              ${index + 1}.
              ${labels[type]}

            </div>

            <div class="selected">

              Selected

            </div>

          </div>


          <div
            class="product selected-product"
            data-selected-product="true"
          >

            ${
              productImage
                ? `

                  <img
                    src="${productImage}"
                    alt="${productName}"
                    onerror="this.style.display='none'"
                  >

                `
                : ""
            }


            <div>

              <div class="pname">

                ${productName}

              </div>


              <div class="meta">

                ${productBrand}

              </div>


              <div class="price">

                PKR ${money(
                  safePrice(product)
                )}

              </div>

            </div>


            <div class="product-actions">

              <button
                class="btn"
                type="button"
                onclick="openModal('${type}')"
              >

                Change

              </button>


              ${
                productUrl
                  ? `

                    <a
                      class="learn-more-btn"
                      href="${productUrl}"
                      target="_blank"
                      rel="noopener noreferrer"
                      onclick="event.stopPropagation()"
                    >

                      View Product

                    </a>

                  `
                  : ""
              }

            </div>

          </div>

        </div>

      `;

    }
  ).join("");


  updateSummary();

}


// ============================================================
// UPDATE SUMMARY
// ============================================================

function updateSummary() {

  const total =
    Object.values(build)

      .reduce(
        (sum, product) => {

          return (
            sum +
            safePrice(product)
          );

        },
        0
      );


  const totalElement =
    document.getElementById("total");


  if (totalElement) {

    totalElement.textContent =
      `PKR ${money(total)}`;

  }


  // ----------------------------------------------------------
  // COMPATIBILITY
  // ----------------------------------------------------------

  const checksResult =
    checks();


  const compatibilityElement =
    document.getElementById("compat");


  if (compatibilityElement) {

    compatibilityElement.innerHTML =
      checksResult

        .map(check => `

          <div
            class="compat ${check.level}"
          >

            <span class="dot"></span>

            <div>

              <b>
                ${escapeHtml(check.title)}
              </b>

              <br>

              ${escapeHtml(check.text)}

            </div>

          </div>

        `)

        .join("");

  }


  // ----------------------------------------------------------
  // BUILD STATUS
  // ----------------------------------------------------------

  const hasBad =
    checksResult.some(
      check => check.level === "bad"
    );


  const hasWarning =
    checksResult.some(
      check => check.level === "warn"
    );


  const status =
    document.getElementById("status");


  if (!status) return;


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


// ============================================================
// COMPATIBILITY CHECKS
// ============================================================

function checks() {

  const output = [];


  const motherboard =
    build.motherboard;


  const ram =
    build.ram;


  const gpu =
    build.graphics_card;


  const pcCase =
    build.case;


  const cooling =
    build.cooling;


  const psu =
    build.power_supply;


  const fan =
    build.fan;


  // ==========================================================
  // MOTHERBOARD ↔ RAM
  // ==========================================================

  if (motherboard && ram) {

    const motherboardMemory =

      (
        motherboard
          .Compatibility
          ?.memory_type || ""
      ).toUpperCase();


    const ramMemory =

      (
        ram
          .Compatibility
          ?.memory_type || ""
      ).toUpperCase();


    const speed =

      (
        ram
          .Compatibility
          ?.speed || ""
      ).toUpperCase();


    const inferredRam =

      speed.includes("DDR5")

        ? "DDR5"

        : speed.includes("DDR4")

          ? "DDR4"

          : "";


    const ramType =
      ramMemory || inferredRam;


    if (
      motherboardMemory &&
      ramType
    ) {

      const compatible =
        motherboardMemory === ramType;


      output.push({

        title:
          "Motherboard ↔ RAM",

        level:
          compatible
            ? "ok"
            : "bad",

        text:

          compatible

            ? `Motherboard uses ${motherboardMemory} and RAM is ${ramType}.`

            : `Motherboard uses ${motherboardMemory}, but RAM is ${ramType}.`

      });


    } else {

      output.push({

        title:
          "Motherboard ↔ RAM",

        level:
          "warn",

        text:
          "Memory type information is unavailable."

      });

    }

  }


  // ==========================================================
  // MOTHERBOARD ↔ CASE
  // ==========================================================

  if (motherboard && pcCase) {

    const motherboardFormFactor =

      (
        motherboard
          .Compatibility
          ?.form_factor || ""
      ).toLowerCase();


    const caseFormFactor =

      (
        pcCase
          .Compatibility
          ?.form_factor || ""
      ).toLowerCase();


    if (
      motherboardFormFactor &&
      caseFormFactor
    ) {

      const compatible =

        caseFormFactor.includes(
          motherboardFormFactor
        )

        ||

        motherboardFormFactor.includes(
          caseFormFactor
        );


      output.push({

        title:
          "Motherboard ↔ Case",

        level:
          compatible
            ? "ok"
            : "bad",

        text:
          `Motherboard: ${motherboardFormFactor}; case support: ${caseFormFactor}.`

      });


    } else {

      output.push({

        title:
          "Motherboard ↔ Case",

        level:
          "warn",

        text:
          "Case or motherboard form-factor details are unavailable."

      });

    }

  }


  // ==========================================================
  // GPU ↔ PSU
  // ==========================================================

  if (gpu && psu) {

    const watts = Number(
      psu
        .Compatibility
        ?.wattage
    );


    const recommended = Number(
      gpu
        .Compatibility
        ?.recommended_psu_wattage
    );


    if (
      watts &&
      recommended
    ) {

      const compatible =
        watts >= recommended;


      output.push({

        title:
          "Graphics Card ↔ Power Supply",

        level:
          compatible
            ? "ok"
            : "bad",

        text:

          compatible

            ? `PSU provides ${watts}W; GPU recommends ${recommended}W.`

            : `PSU provides ${watts}W, but GPU recommends ${recommended}W.`

      });


    } else {

      output.push({

        title:
          "Graphics Card ↔ Power Supply",

        level:
          "warn",

        text:
          "PSU wattage or GPU recommendation is unavailable."

      });

    }

  }


  // ==========================================================
  // MOTHERBOARD ↔ COOLING
  // ==========================================================

  if (motherboard && cooling) {

    const sockets =

      cooling
        .Compatibility
        ?.supported_sockets

      ||

      cooling
        .Compatibility
        ?.socket_support

      ||

      [];


    const motherboardSocket =

      motherboard
        .Compatibility
        ?.socket;


    if (
      motherboardSocket &&
      sockets.length
    ) {

      const compatible =
        sockets.includes(
          motherboardSocket
        );


      output.push({

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

      output.push({

        title:
          "Motherboard ↔ Cooling",

        level:
          "warn",

        text:
          "CPU socket support information is unavailable."

      });

    }

  }


  // ==========================================================
  // GPU ↔ CASE
  // ==========================================================

  if (gpu && pcCase) {

    const gpuLength = Number(
      gpu
        .Compatibility
        ?.length_mm
    );


    const caseClearance = Number(
      pcCase
        .Compatibility
        ?.gpu_clearance_mm
    );


    if (
      gpuLength &&
      caseClearance
    ) {

      const compatible =
        gpuLength <= caseClearance;


      output.push({

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

      output.push({

        title:
          "Graphics Card ↔ Case",

        level:
          "warn",

        text:
          "GPU length or case clearance is unavailable."

      });

    }

  }


  // ==========================================================
  // FAN ↔ CASE
  // ==========================================================

  if (fan && pcCase) {

    const fanSize = Number(
      fan
        .Compatibility
        ?.size_mm
    );


    const caseFanSupport =
      pcCase
        .Compatibility
        ?.fan_support;


    if (
      fanSize &&
      caseFanSupport
    ) {

      output.push({

        title:
          "Fan ↔ Case",

        level:
          "ok",

        text:
          `Fan size: ${fanSize}mm; case fan support is available.`

      });


    } else {

      output.push({

        title:
          "Fan ↔ Case",

        level:
          "warn",

        text:
          "Fan/case size information could not be verified."

      });

    }

  }


  return output;

}


// ============================================================
// PRODUCT MODAL
// ============================================================

function openModal(t) {
  currentType = t;
  brand = "All";

  document.getElementById("modal").classList.add("open");
  document.getElementById("search").value = "";

  const brands = [
    "All",
    ...new Set(
      productsBy(t)
        .map(p => p.Brand)
        .filter(Boolean)
    )
  ];

  const filters = document.getElementById("filters");

  filters.innerHTML = brands.map(b => `
    <button
      type="button"
      class="chip ${b === "All" ? "active" : ""}"
      data-brand="${b}"
    >
      ${b}
    </button>
  `).join("");

  /* Attach filter click events */
  filters.querySelectorAll(".chip").forEach(button => {
    button.addEventListener("click", function () {

      brand = this.dataset.brand;

      /* Update active button */
      filters.querySelectorAll(".chip").forEach(chip => {
        chip.classList.remove("active");
      });

      this.classList.add("active");

      /* Re-render products */
      renderList();
    });
  });

  renderList();
}


function closeModal() {
  document.getElementById("modal").classList.remove("open");
}


function setBrand(b) {
  brand = b;

  const filters = document.getElementById("filters");

  filters.querySelectorAll(".chip").forEach(chip => {
    chip.classList.toggle(
      "active",
      chip.dataset.brand === b
    );
  });

  renderList();
}

// ============================================================
// CLOSE MODAL
// ============================================================

function closeModal() {

  const modal =
    document.getElementById(
      "modal"
    );


  if (!modal) return;


  modal.classList.remove(
    "open"
  );


  modal.setAttribute(
    "aria-hidden",
    "true"
  );

}


// ============================================================
// BRAND FILTER
// ============================================================

function setBrand(selectedBrand) {

  brand =
    selectedBrand;


  document
    .querySelectorAll(".chip")
    .forEach(chip => {

      chip.classList.toggle(
        "active",
        chip.textContent.trim() === brand
      );

    });


  renderList();

}


// ============================================================
// PRODUCT LIST
// ============================================================

function renderList() {

  const search =
    document.getElementById(
      "search"
    );


  const query =
    search
      ? search.value
          .toLowerCase()
          .trim()
      : "";


  const products =
    productsBy(currentType)

      .filter(product => {

        const matchesBrand =

          brand === "All" ||

          product.Brand === brand;


        const name =

          (
            product["Product Name"] ||
            ""
          ).toLowerCase();


        return (
          matchesBrand &&
          name.includes(query)
        );

      });


  const list =
    document.getElementById(
      "list"
    );


  if (!list) return;


  list.innerHTML =

    products.length

      ? products
          .map(
            product =>
              renderChoice(product)
          )
          .join("")

      : `

          <div class="empty">

            No products found.

          </div>

        `;

}


// ============================================================
// RENDER INDIVIDUAL PRODUCT CHOICE
// ============================================================

function renderChoice(product) {

  const name =
    escapeHtml(
      product["Product Name"]
    );


  const productBrand =
    escapeHtml(
      product.Brand || ""
    );


  const category =
    escapeHtml(
      product.Category || ""
    );


  const productImage =
    escapeHtml(
      image(product)
    );


  const productUrl =
    escapeHtml(
      product["Product URL"] || ""
    );


  const productId =
    product["Product ID"];


  return `

    <div
      class="choice"
      onclick='selectProduct(${JSON.stringify(productId)})'
    >

      ${
        productImage

          ? `

            <img
              src="${productImage}"
              alt="${name}"
              onerror="this.style.display='none'"
            >

          `

          : ""
      }


      <div>

        <div class="pname">

          ${name}

        </div>


        <div class="meta">

          ${productBrand}

          ${
            category
              ? ` · ${category}`
              : ""
          }

        </div>


        <div class="price">

          PKR ${money(
            safePrice(product)
          )}

        </div>

      </div>


      <div class="product-actions">

        <strong>

          PKR ${money(
            safePrice(product)
          )}

        </strong>


        ${
          productUrl

            ? `

              <a
                class="learn-more-btn"
                href="${productUrl}"
                target="_blank"
                rel="noopener noreferrer"
                onclick="event.stopPropagation()"
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


// ============================================================
// SELECT PRODUCT
// ============================================================

function selectProduct(id) {

  const product =
    PRODUCTS.find(
      item =>
        String(
          item["Product ID"]
        ) === String(id)
    );


  if (!product) return;


  build[currentType] =
    product;


  closeModal();


  render();

}


// ============================================================
// SEARCH EVENT
// ============================================================

const searchInput =
  document.getElementById(
    "search"
  );


if (searchInput) {

  searchInput.addEventListener(
    "input",
    renderList
  );

}


// ============================================================
// KEYBOARD EVENTS
// ============================================================

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


// ============================================================
// CLOSE MODAL WHEN CLICKING BACKDROP
// ============================================================

const modal =
  document.getElementById(
    "modal"
  );


if (modal) {

  modal.addEventListener(
    "click",
    event => {

      if (
        event.target.id === "modal"
      ) {

        closeModal();

      }

    }
  );

}


// ============================================================
// PDF DOWNLOAD
// ============================================================

async function downloadSelectedPDF() {

  const {
    jsPDF
  } = window.jspdf || {};


  if (!jsPDF) {

    alert(
      "PDF library could not be loaded. Please check your internet connection and try again."
    );

    return;

  }


  const selectedProducts =

    Object.entries(build)

      .filter(
        ([, product]) =>
          product
      )

      .map(
        ([type, product]) => ({
          type,
          product
        })
      );


  if (
    !selectedProducts.length
  ) {

    alert(
      "Please select your PC components first."
    );

    return;

  }


  const doc =
    new jsPDF();


  const margin = 18;

  const pageWidth = 210;

  const contentWidth =
    pageWidth - margin * 2;

  let y = 20;


  // ----------------------------------------------------------
  // PDF TITLE
  // ----------------------------------------------------------

  doc.setFontSize(18);

  doc.setFont(
    undefined,
    "bold"
  );


  doc.text(
    "GB TECH — PC BUILD",
    margin,
    y
  );


  y += 10;


  // ----------------------------------------------------------
  // DATE
  // ----------------------------------------------------------

  doc.setFontSize(10);

  doc.setFont(
    undefined,
    "normal"
  );


  doc.text(
    `Generated: ${new Date().toLocaleDateString()}`,
    margin,
    y
  );


  y += 12;


  // ----------------------------------------------------------
  // COMPONENT HEADING
  // ----------------------------------------------------------

  doc.setFontSize(12);

  doc.setFont(
    undefined,
    "bold"
  );


  doc.text(
    "Selected Components",
    margin,
    y
  );


  y += 8;


  // ----------------------------------------------------------
  // PRODUCTS
  // ----------------------------------------------------------

  doc.setFontSize(10);

  doc.setFont(
    undefined,
    "normal"
  );


  selectedProducts.forEach(
    ({ type, product }) => {

      const line =

        `${labels[type]}: ${
          product["Product Name"]
        } — PKR ${
          money(
            safePrice(product)
          )
        }`;


      const lines =
        doc.splitTextToSize(
          `• ${line}`,
          contentWidth
        );


      // New page if necessary

      if (
        y +
        lines.length * 5 >
        275
      ) {

        doc.addPage();

        y = 20;

      }


      doc.text(
        lines,
        margin,
        y
      );


      y +=
        lines.length * 5 + 3;

    }
  );


  // ----------------------------------------------------------
  // TOTAL
  // ----------------------------------------------------------

  const total =

    Object.values(build)

      .reduce(
        (sum, product) =>

          sum +
          safePrice(product),

        0
      );


  y += 6;


  if (y > 250) {

    doc.addPage();

    y = 20;

  }


  doc.setFontSize(12);

  doc.setFont(
    undefined,
    "bold"
  );


  doc.text(
    `Total: PKR ${money(total)}`,
    margin,
    y
  );


  y += 12;


  // ----------------------------------------------------------
  // DISCLAIMER
  // ----------------------------------------------------------

  doc.setFontSize(9);

  doc.setFont(
    undefined,
    "bold"
  );


  doc.text(
    "Compatibility Notice",
    margin,
    y
  );


  y += 5;


  doc.setFont(
    undefined,
    "normal"
  );


  const notice =

    "This tool performs basic compatibility checks using available product specifications. " +
    "It does not guarantee complete system compatibility. " +
    "Always verify detailed specifications with the manufacturer before purchasing.";


  const noticeLines =

    doc.splitTextToSize(
      notice,
      contentWidth
    );


  doc.text(
    noticeLines,
    margin,
    y
  );


  // ----------------------------------------------------------
  // SAVE
  // ----------------------------------------------------------

  doc.save(
    "GB-Tech-PC-Build.pdf"
  );

}


// ============================================================
// START APPLICATION
// ============================================================

loadProducts();