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


const productsBy = (type) => {
  return PRODUCTS.filter(product =>
    String(product?.Compatibility?.type || "")
      .toLowerCase() === type
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
   SHARE QUOTATION
   ============================================================ */

async function shareQuotationOnWhatsApp() {

  const selected =
    selectedEntries();


  if (!selected.length) {

    alert(
      "Please select your PC components first."
    );

    return;
  }


  /*
     Open WhatsApp immediately while the click
     still has user activation.

     This avoids popup blockers.
  */

  const message =
    buildWhatsAppMessage("quotation");


  openWhatsApp(message);


  /*
     Generate the exact same quotation PDF
     after opening WhatsApp.
  */

  await downloadSelectedPDF();

}


/* ============================================================
   ASK GB TECH ABOUT BUILD
   ============================================================ */

function askGBTechAboutBuild() {

  const message =
    buildWhatsAppMessage("help");


  openWhatsApp(message);
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

function loadImageAsDataURL(src) {

  return new Promise(
    (resolve, reject) => {

      const img =
        new Image();


      img.onload = () => {

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
          0
        );


        resolve(
          canvas.toDataURL(
            "image/png"
          )
        );

      };


      img.onerror =
        reject;


      img.src = src;

    }
  );
}


/* ============================================================
   PDF — DOWNLOAD BUILD
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


  if (!selected.length) {

    alert(
      "Please select your PC components first."
    );

    return;
  }


  const doc =
    new jsPDF({
      unit: "mm",
      format: "a4"
    });


  const pageWidth =
    doc.internal.pageSize.getWidth();


  const pageHeight =
    doc.internal.pageSize.getHeight();


  const margin = 15;


  /* ==========================================================
     PDF HEADER
     ========================================================== */

  const headerX = margin;
  const headerY = 12;

  const headerWidth =
    pageWidth - margin * 2;

  const headerHeight = 34;


  doc.setFillColor(
    17,
    19,
    23
  );


  doc.roundedRect(
    headerX,
    headerY,
    headerWidth,
    headerHeight,
    4,
    4,
    "F"
  );


  let logoLoaded = false;


  try {

    const logoData =
      await loadImageAsDataURL(
        "media/GB-tech logo white.png"
      );


    doc.addImage(
      logoData,
      "PNG",
      margin + 7,
      headerY + 5,
      42,
      0
    );


    logoLoaded = true;

  } catch (error) {

    console.warn(
      "Could not load PDF logo.",
      error
    );

  }


  const titleX =
    logoLoaded
      ? margin + 57
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
    18
  );


  doc.text(
    "PC BUILD QUOTATION",
    titleX,
    headerY + 13
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


  /* ==========================================================
     SELECTED COMPONENTS TITLE
     ========================================================== */

  let tableStartY =
    headerY +
    headerHeight +
    14;


  doc.setTextColor(
    40,
    40,
    40
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
    tableStartY
  );


  tableStartY += 7;


  /* ==========================================================
     TABLE DATA
     ========================================================== */

  const tableRows =
    selected.map(
      ([type, product]) => [

        labels[type]
          .toUpperCase(),

        product["Product Name"] ||
          "—",

        product.Brand ||
          "—",

        `PKR ${money(
          safePrice(product)
        )}`

      ]
    );


  const total =
    selected.reduce(
      (sum, [, product]) =>
        sum + safePrice(product),
      0
    );


  /* ==========================================================
     TABLE
     ========================================================== */

  doc.autoTable({

    startY: tableStartY,

    margin: {
      left: margin,
      right: margin
    },

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
        [45, 45, 45],

      lineColor:
        [218, 218, 218],

      lineWidth:
        .2,

      valign:
        "middle",

      overflow:
        "linebreak"

    },

    headStyles: {

      fillColor:
        [17, 19, 23],

      textColor:
        [255, 216, 109],

      fontStyle:
        "bold",

      halign:
        "left",

      cellPadding:
        4.5

    },

    alternateRowStyles: {

      fillColor:
        [248, 248, 248]

    },

    columnStyles: {

      /*
         COMPONENT deliberately wider.
      */

      0: {
        cellWidth: 38
      },

      /*
         PRODUCT gets the largest space.
      */

      1: {
        cellWidth: 88
      },

      2: {
        cellWidth: 25
      },

      3: {
        cellWidth: 29,

        halign:
          "right"
      }

    }

  });


  /* ==========================================================
     TOTAL BUILD
     ========================================================== */

  let y =
    doc.lastAutoTable.finalY + 10;


  if (
    y >
    pageHeight - 65
  ) {

    doc.addPage();

    y = 20;

  }


  doc.setFillColor(
    17,
    19,
    23
  );


  doc.roundedRect(
    margin,
    y,
    pageWidth - margin * 2,
    19,
    4,
    4,
    "F"
  );


  doc.setTextColor(
    255,
    216,
    109
  );


  doc.setFont(
    "helvetica",
    "bold"
  );


  doc.setFontSize(
    12
  );


  doc.text(
    "TOTAL BUILD",
    margin + 7,
    y + 12
  );


  doc.text(
    `PKR ${money(total)}`,
    pageWidth - margin - 7,
    y + 12,
    {
      align:
        "right"
    }
  );


  /* ==========================================================
     COMPATIBILITY NOTICE
     ========================================================== */

  y += 29;


  if (
    y >
    pageHeight - 45
  ) {

    doc.addPage();

    y = 20;

  }


  doc.setTextColor(
    45,
    45,
    45
  );


  doc.setFont(
    "helvetica",
    "bold"
  );


  doc.setFontSize(
    10
  );


  doc.text(
    "COMPATIBILITY NOTICE",
    margin,
    y
  );


  y += 6;


  doc.setFont(
    "helvetica",
    "normal"
  );


  doc.setFontSize(
    8.5
  );


  const notice =
    "This builder performs basic compatibility checks using the product specifications available in the GB Tech product data. It does not guarantee complete system compatibility. Always verify detailed specifications with the manufacturer before purchasing.";


  const noticeLines =
    doc.splitTextToSize(
      notice,
      pageWidth - margin * 2
    );


  doc.text(
    noticeLines,
    margin,
    y
  );


  /* ==========================================================
     FOOTER
     ========================================================== */

  doc.setDrawColor(
    214,
    179,
    92
  );


  doc.setLineWidth(
    .35
  );


  doc.line(
    margin,
    pageHeight - 18,
    pageWidth - margin,
    pageHeight - 18
  );


  doc.setFont(
    "helvetica",
    "normal"
  );


  doc.setFontSize(
    8
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


  /* ==========================================================
     SAVE
     ========================================================== */

  doc.save(
    "GB-Tech-PC-Build-Quotation.pdf"
  );
}


/* ============================================================
   START
   ============================================================ */

loadProducts();