/**
 * GPA Cost Control ERP V5.0 — Introduction Deck
 * pptxgenjs script — 11 slides, Indonesian language, intro style
 * Run: node make_deck.js
 */

const pptxgen = require("pptxgenjs");

// ── Palette ────────────────────────────────────────────────────────────────
const C = {
  navy:    "1E293B",
  navyMid: "334155",
  blue:    "2563EB",
  blueSoft:"DBEAFE",
  amber:   "F59E0B",
  amberSoft:"FEF3C7",
  green:   "16A34A",
  greenSoft:"DCFCE7",
  teal:    "0891B2",
  tealSoft:"CFFAFE",
  purple:  "7C3AED",
  purpleSoft:"EDE9FE",
  white:   "FFFFFF",
  offwhite:"F8FAFC",
  gray100: "F1F5F9",
  gray200: "E2E8F0",
  gray400: "94A3B8",
  gray500: "64748B",
  gray700: "374151",
  gray900: "111827",
};

// ── Helpers ────────────────────────────────────────────────────────────────
const W = 10;   // slide width inches
const H = 5.625; // slide height inches

function sectionHeader(slide, title, subtitle) {
  // Slim navy top bar
  slide.addShape("rect", { x: 0, y: 0, w: W, h: 0.6, fill: { color: C.navy }, line: { color: C.navy } });
  slide.addText(title, {
    x: 0.4, y: 0, w: W - 0.8, h: 0.6,
    fontSize: 13, bold: true, color: C.white, valign: "middle", margin: 0,
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.4, y: 0.62, w: W - 0.8, h: 0.3,
      fontSize: 9, color: C.gray500, valign: "top", margin: 0,
    });
  }
}

function card(slide, x, y, w, h, opts = {}) {
  const { fill = C.white, line = C.gray200, shadow = true, radius = false } = opts;
  const shapeType = radius ? "roundRect" : "rect";
  const shapeOpts = {
    x, y, w, h,
    fill: { color: fill },
    line: { color: line, width: 0.5 },
  };
  if (shadow) {
    shapeOpts.shadow = { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 };
  }
  if (radius) {
    shapeOpts.rectRadius = 0.1;
  }
  slide.addShape(shapeType, shapeOpts);
}

function pill(slide, x, y, label, fillColor, textColor = C.white) {
  slide.addShape("roundRect", {
    x, y, w: 1.2, h: 0.28,
    fill: { color: fillColor },
    line: { color: fillColor },
    rectRadius: 0.14,
  });
  slide.addText(label, {
    x, y, w: 1.2, h: 0.28,
    fontSize: 7.5, bold: true, color: textColor,
    align: "center", valign: "middle", margin: 0,
  });
}

// ── Presentation setup ─────────────────────────────────────────────────────
const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.author  = "GPA ERP Team";
pres.title   = "GPA Cost Control ERP V5.0 — Pengenalan";


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 1 — COVER
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Left accent stripe
  s.addShape("rect", { x: 0, y: 0, w: 0.22, h: H, fill: { color: C.blue }, line: { color: C.blue } });

  // Blue glow block (decorative)
  s.addShape("rect", { x: 6.5, y: 0, w: 3.5, h: H, fill: { color: C.navyMid }, line: { color: C.navyMid } });

  // Grid dots (decorative — simple shape array)
  for (let row = 0; row < 5; row++) {
    for (let col = 0; col < 4; col++) {
      s.addShape("ellipse", {
        x: 6.8 + col * 0.65, y: 0.3 + row * 1.0, w: 0.06, h: 0.06,
        fill: { color: C.blue, transparency: 60 },
        line: { color: C.blue, transparency: 60 },
      });
    }
  }

  // Amber accent line
  s.addShape("rect", { x: 0.6, y: 2.65, w: 1.2, h: 0.06, fill: { color: C.amber }, line: { color: C.amber } });

  // Title
  s.addText("GPA Cost Control ERP", {
    x: 0.55, y: 0.9, w: 5.8, h: 0.9,
    fontSize: 34, bold: true, color: C.white,
    fontFace: "Calibri", margin: 0,
  });
  s.addText("V5.0", {
    x: 0.55, y: 1.78, w: 5.8, h: 0.7,
    fontSize: 34, bold: true, color: C.amber,
    fontFace: "Calibri", margin: 0,
  });

  // Subtitle
  s.addText("Sistem Manajemen Biaya Proyek Terpadu", {
    x: 0.55, y: 2.8, w: 5.8, h: 0.4,
    fontSize: 12, color: C.gray400, fontFace: "Calibri", margin: 0,
  });

  // Tagline
  s.addText("Satu sistem. Semua proyek. Semua pengeluaran.", {
    x: 0.55, y: 3.35, w: 5.8, h: 0.35,
    fontSize: 10, italic: true, color: C.gray400, fontFace: "Calibri", margin: 0,
  });

  // Three highlight pills
  const pills = [
    { label: "9 Modul", color: C.blue },
    { label: "7 Role", color: C.teal },
    { label: "Audit Trail", color: C.amber },
  ];
  pills.forEach((p, i) => {
    pill(s, 0.55 + i * 1.4, 4.2, p.label, p.color);
  });

  // Bottom "by GPA" text
  s.addText("PT Graha Perkasa Abadi  ·  2026", {
    x: 0.55, y: 5.15, w: 5.8, h: 0.3,
    fontSize: 8, color: C.gray500, margin: 0,
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 2 — AGENDA
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offwhite };
  sectionHeader(s, "Agenda", "Apa yang akan kita bahas hari ini");

  const items = [
    { no: "01", label: "Apa itu GPA ERP?" },
    { no: "02", label: "Modul-modul utama" },
    { no: "03", label: "Alur kerja pengeluaran" },
    { no: "04", label: "Siapa menggunakan apa?" },
    { no: "05", label: "Langkah selanjutnya" },
  ];

  items.forEach((item, i) => {
    const y = 1.05 + i * 0.82;
    card(s, 0.6, y, 8.8, 0.68, { shadow: false, line: C.gray200 });
    // Number badge
    s.addShape("rect", { x: 0.6, y, w: 0.55, h: 0.68, fill: { color: C.navy }, line: { color: C.navy } });
    s.addText(item.no, {
      x: 0.6, y, w: 0.55, h: 0.68,
      fontSize: 13, bold: true, color: C.white,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(item.label, {
      x: 1.3, y: y + 0.04, w: 8.0, h: 0.6,
      fontSize: 14, color: C.gray900, valign: "middle", fontFace: "Calibri", margin: 0,
    });
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 3 — WHY WE BUILT THIS
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offwhite };
  sectionHeader(s, "Mengapa GPA ERP Dibangun?", "Dari tantangan nyata ke solusi nyata");

  // Divider arrow in center
  s.addShape("rect", { x: 4.82, y: 0.95, w: 0.36, h: 3.85,
    fill: { color: C.gray100 }, line: { color: C.gray200, width: 0.5 } });
  s.addText("→", {
    x: 4.78, y: 2.6, w: 0.44, h: 0.44,
    fontSize: 22, color: C.blue, align: "center", valign: "middle", margin: 0,
  });

  const rows = [
    { pain: "Spreadsheet tidak terkontrol", sol: "Sistem terpusat real-time" },
    { pain: "Tidak ada approval trail",     sol: "Alur persetujuan otomatis" },
    { pain: "Laporan manual & lambat",      sol: "Dashboard & laporan instan" },
  ];

  rows.forEach((row, i) => {
    const y = 1.05 + i * 1.28;
    // Pain card (left)
    card(s, 0.4, y, 4.3, 1.0, { fill: "FFF1F2", line: "FECDD3", shadow: false });
    s.addShape("rect", { x: 0.4, y, w: 0.22, h: 1.0, fill: { color: "EF4444" }, line: { color: "EF4444" } });
    s.addText("✗", { x: 0.42, y, w: 0.22, h: 1.0, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(row.pain, {
      x: 0.75, y: y + 0.1, w: 3.85, h: 0.8,
      fontSize: 11, color: "991B1B", fontFace: "Calibri", valign: "middle", margin: 0,
    });

    // Solution card (right)
    card(s, 5.3, y, 4.3, 1.0, { fill: "F0FDF4", line: "BBF7D0", shadow: false });
    s.addShape("rect", { x: 5.3, y, w: 0.22, h: 1.0, fill: { color: C.green }, line: { color: C.green } });
    s.addText("✓", { x: 5.3, y, w: 0.22, h: 1.0, fontSize: 10, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
    s.addText(row.sol, {
      x: 5.65, y: y + 0.1, w: 3.8, h: 0.8,
      fontSize: 11, color: "166534", fontFace: "Calibri", valign: "middle", margin: 0,
    });
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 4 — WHAT IS GPA ERP
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Large quote / definition
  s.addText('"', {
    x: 0.4, y: 0.4, w: 0.8, h: 1.2,
    fontSize: 80, color: C.blue, fontFace: "Georgia", margin: 0,
  });
  s.addText(
    "Platform berbasis web untuk mengelola biaya proyek, pendapatan, dan aset perusahaan secara real-time dengan kontrol penuh.",
    {
      x: 0.6, y: 1.0, w: 8.8, h: 1.4,
      fontSize: 17, color: C.white, fontFace: "Calibri",
      align: "left", valign: "top", margin: 0,
    }
  );

  // Three stat cards
  const stats = [
    { value: "9",  label: "Modul Terintegrasi", color: C.blue },
    { value: "7",  label: "Role Pengguna",       color: C.amber },
    { value: "∞",  label: "Audit Trail Lengkap", color: C.green },
  ];

  stats.forEach((st, i) => {
    const x = 0.5 + i * 3.1;
    const y = 3.0;
    card(s, x, y, 2.8, 1.9, { fill: C.navyMid, line: C.navyMid, shadow: false });
    s.addShape("rect", { x, y, w: 2.8, h: 0.06, fill: { color: st.color }, line: { color: st.color } });
    s.addText(st.value, {
      x, y: y + 0.2, w: 2.8, h: 0.9,
      fontSize: 48, bold: true, color: st.color, align: "center", fontFace: "Calibri", margin: 0,
    });
    s.addText(st.label, {
      x, y: y + 1.1, w: 2.8, h: 0.55,
      fontSize: 9.5, color: C.gray400, align: "center", fontFace: "Calibri", margin: 0,
    });
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 5 — THE 9 MODULES
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offwhite };
  sectionHeader(s, "9 Modul Utama", "Semua yang dibutuhkan — dalam satu sistem");

  const modules = [
    { icon: "◈", name: "Dashboard",            color: C.blue },
    { icon: "⚡", name: "Action Center",         color: C.amber },
    { icon: "📋", name: "Project Command",       color: C.teal },
    { icon: "💰", name: "Revenue & AR",           color: C.green },
    { icon: "💳", name: "Spending & Expenses",   color: "DC2626" },
    { icon: "🪙", name: "Petty Cash",             color: C.purple },
    { icon: "📦", name: "Inventory & Assets",    color: "0891B2" },
    { icon: "📄", name: "Legal & Proposals",     color: "D97706" },
    { icon: "📊", name: "Reports",               color: "374151" },
  ];

  const cols = 3, rows = 3;
  const cardW = 2.8, cardH = 1.05;
  const gapX = 0.25, gapY = 0.18;
  const startX = (W - (cols * cardW + (cols - 1) * gapX)) / 2;
  const startY = 0.85;

  modules.forEach((mod, i) => {
    const col = i % cols;
    const row = Math.floor(i / cols);
    const x = startX + col * (cardW + gapX);
    const y = startY + row * (cardH + gapY);

    card(s, x, y, cardW, cardH, { shadow: true, line: C.gray200 });
    // Color stripe left
    s.addShape("rect", { x, y, w: 0.22, h: cardH, fill: { color: mod.color }, line: { color: mod.color } });
    // Icon circle
    s.addShape("ellipse", {
      x: x + 0.35, y: y + 0.22, w: 0.55, h: 0.55,
      fill: { color: mod.color, transparency: 85 },
      line: { color: mod.color, transparency: 70 },
    });
    s.addText(mod.icon, {
      x: x + 0.35, y: y + 0.22, w: 0.55, h: 0.55,
      fontSize: 14, align: "center", valign: "middle", margin: 0,
    });
    s.addText(mod.name, {
      x: x + 1.0, y: y + 0.1, w: cardW - 1.1, h: cardH - 0.2,
      fontSize: 10.5, bold: true, color: C.gray900, valign: "middle", fontFace: "Calibri", margin: 0,
    });
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 6 — EXPENSE APPROVAL FLOW
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offwhite };
  sectionHeader(s, "Alur Persetujuan Pengeluaran", "Setiap pengeluaran tercatat, disetujui, dan tidak bisa diubah setelah dibayar");

  const steps = [
    { label: "Staff\nSubmit",        color: C.blue,   icon: "👤" },
    { label: "Cost Control\nVerifikasi", color: C.teal, icon: "🔍" },
    { label: "Manager / MD\nSetuju",  color: C.amber,  icon: "✅" },
    { label: "Finance\nBayar",        color: C.green,  icon: "💳" },
    { label: "Terkunci\nAudit Trail", color: C.navy,   icon: "🔒" },
  ];

  const boxW = 1.5, boxH = 1.5;
  const arrowW = 0.35;
  const totalW = steps.length * boxW + (steps.length - 1) * arrowW;
  const startX = (W - totalW) / 2;
  const y = 1.8;

  steps.forEach((step, i) => {
    const x = startX + i * (boxW + arrowW);

    // Card
    card(s, x, y, boxW, boxH, { fill: C.white, shadow: true, line: step.color });
    s.addShape("rect", { x, y, w: boxW, h: 0.08, fill: { color: step.color }, line: { color: step.color } });

    // Icon circle
    s.addShape("ellipse", {
      x: x + (boxW - 0.65) / 2, y: y + 0.18, w: 0.65, h: 0.65,
      fill: { color: step.color, transparency: 85 },
      line: { color: step.color, transparency: 50 },
    });
    s.addText(step.icon, {
      x: x + (boxW - 0.65) / 2, y: y + 0.18, w: 0.65, h: 0.65,
      fontSize: 18, align: "center", valign: "middle", margin: 0,
    });

    s.addText(step.label, {
      x: x + 0.05, y: y + 0.9, w: boxW - 0.1, h: 0.55,
      fontSize: 8.5, bold: true, color: C.gray700, align: "center", valign: "middle",
      fontFace: "Calibri", margin: 0,
    });

    // Arrow between steps
    if (i < steps.length - 1) {
      const ax = x + boxW;
      s.addShape("rect", { x: ax + 0.04, y: y + (boxH / 2) - 0.03, w: arrowW - 0.08, h: 0.06,
        fill: { color: C.gray400 }, line: { color: C.gray400 } });
      s.addText("▶", {
        x: ax + arrowW - 0.2, y: y + (boxH / 2) - 0.16, w: 0.2, h: 0.32,
        fontSize: 9, color: C.gray400, align: "center", valign: "middle", margin: 0,
      });
    }
  });

  // Status pill labels below
  const statusLabels = [
    { x: startX + 0 * (boxW + arrowW), text: "DRAFT",    color: C.blue },
    { x: startX + 1 * (boxW + arrowW), text: "PENDING",  color: C.teal },
    { x: startX + 2 * (boxW + arrowW), text: "APPROVED", color: C.amber },
    { x: startX + 3 * (boxW + arrowW), text: "PAID",     color: C.green },
    { x: startX + 4 * (boxW + arrowW), text: "LOCKED",   color: C.navy },
  ];

  statusLabels.forEach((st) => {
    pill(s, st.x + (boxW - 1.2) / 2, y + boxH + 0.16, st.text, st.color);
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 7 — PETTY CASH
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offwhite };
  sectionHeader(s, "Petty Cash — Cara Lama vs Cara Baru", "Manajemen kas kecil menjadi lebih mudah dan akuntabel");

  // Left column — old way
  card(s, 0.4, 0.85, 4.3, 4.4, { fill: "FFF1F2", line: "FECDD3", shadow: false });
  s.addShape("rect", { x: 0.4, y: 0.85, w: 4.3, h: 0.5, fill: { color: "EF4444" }, line: { color: "EF4444" } });
  s.addText("Cara Lama", {
    x: 0.5, y: 0.85, w: 4.1, h: 0.5,
    fontSize: 12, bold: true, color: C.white, valign: "middle", margin: 0,
  });

  const oldItems = [
    "📄  Struk kertas, mudah hilang",
    "📊  Rekap manual di spreadsheet",
    "⏱️  Harus tunggu akhir bulan",
    "❌  Tidak ada trail persetujuan",
    "🔎  Sulit diaudit & ditelusuri",
  ];
  oldItems.forEach((item, i) => {
    s.addText(item, {
      x: 0.55, y: 1.52 + i * 0.6, w: 4.0, h: 0.5,
      fontSize: 10.5, color: "991B1B", fontFace: "Calibri", valign: "middle", margin: 0,
    });
  });

  // VS badge
  s.addShape("ellipse", {
    x: 4.6, y: 2.7, w: 0.8, h: 0.8,
    fill: { color: C.navy }, line: { color: C.navy },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.15 },
  });
  s.addText("VS", { x: 4.6, y: 2.7, w: 0.8, h: 0.8,
    fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });

  // Right column — new way
  card(s, 5.3, 0.85, 4.3, 4.4, { fill: "F0FDF4", line: "BBF7D0", shadow: false });
  s.addShape("rect", { x: 5.3, y: 0.85, w: 4.3, h: 0.5, fill: { color: C.green }, line: { color: C.green } });
  s.addText("Cara Baru — GPA ERP", {
    x: 5.4, y: 0.85, w: 4.1, h: 0.5,
    fontSize: 12, bold: true, color: C.white, valign: "middle", margin: 0,
  });

  const newItems = [
    "📸  Foto struk — OCR otomatis",
    "📋  Batch entry: paste dari Excel",
    "⚡  Langsung tercatat real-time",
    "✅  Approval otomatis setelah submit",
    "🔒  Audit trail lengkap & permanen",
  ];
  newItems.forEach((item, i) => {
    s.addText(item, {
      x: 5.45, y: 1.52 + i * 0.6, w: 4.0, h: 0.5,
      fontSize: 10.5, color: "166534", fontFace: "Calibri", valign: "middle", margin: 0,
    });
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 8 — WHO USES WHAT (Role matrix)
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.offwhite };
  sectionHeader(s, "Siapa Menggunakan Apa?", "Akses disesuaikan dengan peran setiap pengguna");

  const roles = [
    { role: "MD",            color: C.navy,   job: "Managing Director",  modul: "Action Center, Reports, Legal",     action: "Approve pengeluaran besar, tanda tangan dokumen" },
    { role: "PM",            color: C.blue,   job: "Project Manager",    modul: "Project Command, Spending, Legal",  action: "Monitor anggaran proyek, kelola pengeluaran" },
    { role: "Cost Control",  color: C.teal,   job: "Cost Controller",    modul: "Spending, Petty Cash, Reports",     action: "Verifikasi semua pengeluaran (gate pertama)" },
    { role: "Finance",       color: C.green,  job: "Keuangan",           modul: "Revenue AR, Spending, Reports",     action: "Bayar expense approved, kelola invoice AR" },
    { role: "GA / Staff",    color: C.amber,  job: "General Affairs",    modul: "Petty Cash, Inventory, Expenses",   action: "Submit pengeluaran, kelola petty cash & aset" },
  ];

  // Table header
  const hY = 0.78;
  s.addShape("rect", { x: 0.3, y: hY, w: 9.4, h: 0.4, fill: { color: C.navy }, line: { color: C.navy } });
  const hCols = [
    { x: 0.35, w: 1.5, label: "Role" },
    { x: 1.9,  w: 2.0, label: "Jabatan" },
    { x: 3.95, w: 3.0, label: "Modul Utama" },
    { x: 7.0,  w: 2.65, label: "Aksi Utama" },
  ];
  hCols.forEach((col) => {
    s.addText(col.label, {
      x: col.x, y: hY, w: col.w, h: 0.4,
      fontSize: 9, bold: true, color: C.white, valign: "middle", fontFace: "Calibri", margin: 4,
    });
  });

  roles.forEach((r, i) => {
    const rowY = hY + 0.4 + i * 0.75;
    const rowFill = i % 2 === 0 ? C.white : C.gray100;
    s.addShape("rect", { x: 0.3, y: rowY, w: 9.4, h: 0.75, fill: { color: rowFill }, line: { color: C.gray200, width: 0.5 } });

    // Role pill
    s.addShape("roundRect", {
      x: 0.38, y: rowY + 0.18, w: 1.35, h: 0.35,
      fill: { color: r.color }, line: { color: r.color }, rectRadius: 0.05,
    });
    s.addText(r.role, {
      x: 0.38, y: rowY + 0.18, w: 1.35, h: 0.35,
      fontSize: 8, bold: true, color: C.white, align: "center", valign: "middle", margin: 0,
    });

    s.addText(r.job, { x: 1.9, y: rowY, w: 2.0, h: 0.75, fontSize: 9, color: C.gray700, valign: "middle", fontFace: "Calibri", margin: 4 });
    s.addText(r.modul, { x: 3.95, y: rowY, w: 3.0, h: 0.75, fontSize: 8.5, color: C.gray700, valign: "middle", fontFace: "Calibri", margin: 4 });
    s.addText(r.action, { x: 7.0, y: rowY, w: 2.65, h: 0.75, fontSize: 8.5, color: C.gray700, valign: "middle", fontFace: "Calibri", margin: 4 });
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 9 — MOBILE READY
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Right panel — light
  s.addShape("rect", { x: 5.2, y: 0, w: 4.8, h: H, fill: { color: C.offwhite }, line: { color: C.offwhite } });

  // Left: main content
  s.addShape("rect", { x: 0.45, y: 1.5, w: 0.12, h: 2.5, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText("Akses dari\nMana Saja", {
    x: 0.7, y: 1.3, w: 4.2, h: 1.2,
    fontSize: 30, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addText("Tidak perlu install aplikasi", {
    x: 0.7, y: 2.55, w: 4.2, h: 0.4,
    fontSize: 11, color: C.gray400, italic: true, fontFace: "Calibri", margin: 0,
  });

  const features = [
    { icon: "📤", text: "Submit pengeluaran dari lapangan" },
    { icon: "📸", text: "Scan struk langsung dari kamera" },
    { icon: "✅", text: "Approve expense dari mana saja" },
    { icon: "📊", text: "Pantau dashboard proyek real-time" },
  ];
  features.forEach((f, i) => {
    s.addText(`${f.icon}  ${f.text}`, {
      x: 0.7, y: 3.1 + i * 0.44, w: 4.2, h: 0.4,
      fontSize: 10.5, color: C.white, fontFace: "Calibri", valign: "middle", margin: 0,
    });
  });

  // Right panel: simulated phone wireframe
  const phoneX = 5.9, phoneY = 0.35, phoneW = 2.2, phoneH = 4.9;
  s.addShape("roundRect", {
    x: phoneX, y: phoneY, w: phoneW, h: phoneH,
    fill: { color: C.white },
    line: { color: C.gray200, width: 1.5 },
    rectRadius: 0.2,
    shadow: { type: "outer", blur: 16, offset: 4, angle: 135, color: "000000", opacity: 0.15 },
  });
  // Phone top bar
  s.addShape("roundRect", {
    x: phoneX, y: phoneY, w: phoneW, h: 0.55,
    fill: { color: C.navy }, line: { color: C.navy }, rectRadius: 0.2,
  });
  s.addText("GPA ERP", {
    x: phoneX, y: phoneY + 0.05, w: phoneW, h: 0.45,
    fontSize: 9, bold: true, color: C.white, align: "center", valign: "middle", margin: 0,
  });
  // Mock content rows
  const mockRows = ["Submit Expense", "Petty Cash", "Dashboard", "Approval"];
  mockRows.forEach((label, i) => {
    s.addShape("rect", {
      x: phoneX + 0.18, y: phoneY + 0.68 + i * 0.88, w: phoneW - 0.36, h: 0.7,
      fill: { color: C.gray100 }, line: { color: C.gray200, width: 0.3 },
    });
    s.addText(label, {
      x: phoneX + 0.22, y: phoneY + 0.68 + i * 0.88, w: phoneW - 0.44, h: 0.7,
      fontSize: 8.5, color: C.gray700, valign: "middle", fontFace: "Calibri", margin: 0,
    });
  });

  // URL banner bottom
  s.addShape("rect", { x: 5.2, y: H - 0.45, w: 4.8, h: 0.45, fill: { color: C.blue }, line: { color: C.blue } });
  s.addText("Buka di browser: erp.garuda.id", {
    x: 5.25, y: H - 0.45, w: 4.7, h: 0.45,
    fontSize: 9.5, color: C.white, valign: "middle", margin: 0,
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 10 — COMING SOON (HRIS)
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Tagline top
  s.addText("SEGERA HADIR", {
    x: 0, y: 0.2, w: W, h: 0.4,
    fontSize: 9, bold: true, color: C.amber, align: "center",
    charSpacing: 5, margin: 0,
  });

  s.addText("HRIS — Human Resource\nInformation System", {
    x: 0.5, y: 0.6, w: W - 1, h: 1.1,
    fontSize: 26, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0,
  });
  s.addText("Dari biaya proyek ke penggajian — satu platform.", {
    x: 0.5, y: 1.68, w: W - 1, h: 0.38,
    fontSize: 10.5, italic: true, color: C.gray400, align: "center", margin: 0,
  });

  const hrisCards = [
    { icon: "👥", title: "Karyawan & Organisasi",  sub: "Data karyawan, departemen,\njabatan, org chart",      color: C.teal },
    { icon: "📅", title: "Absensi & Cuti",          sub: "Rekap kehadiran, jenis cuti,\npersetujuan online",     color: C.purple },
    { icon: "💵", title: "Penggajian (Payroll)",     sub: "PPh 21, BPJS TK/Kes,\nslip gaji PDF, export bank",  color: C.amber },
    { icon: "🎯", title: "Rekrutmen",                sub: "Lowongan, seleksi,\nonboarding checklist",            color: C.green },
  ];

  hrisCards.forEach((card_item, i) => {
    const x = 0.5 + i * 2.3;
    const y = 2.3;
    const cardW = 2.1, cardH = 2.8;
    card(s, x, y, cardW, cardH, { fill: C.navyMid, line: C.navyMid, shadow: false });
    s.addShape("rect", { x, y, w: cardW, h: 0.07, fill: { color: card_item.color }, line: { color: card_item.color } });

    // Icon circle
    s.addShape("ellipse", {
      x: x + (cardW - 0.7) / 2, y: y + 0.22, w: 0.7, h: 0.7,
      fill: { color: card_item.color, transparency: 75 },
      line: { color: card_item.color, transparency: 60 },
    });
    s.addText(card_item.icon, {
      x: x + (cardW - 0.7) / 2, y: y + 0.22, w: 0.7, h: 0.7,
      fontSize: 20, align: "center", valign: "middle", margin: 0,
    });

    s.addText(card_item.title, {
      x: x + 0.08, y: y + 1.05, w: cardW - 0.16, h: 0.6,
      fontSize: 10, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0,
    });
    s.addText(card_item.sub, {
      x: x + 0.08, y: y + 1.65, w: cardW - 0.16, h: 1.0,
      fontSize: 8.5, color: C.gray400, align: "center", fontFace: "Calibri", margin: 0,
    });
  });
}


// ══════════════════════════════════════════════════════════════════════════════
// SLIDE 11 — CLOSING / NEXT STEPS
// ══════════════════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // Full width amber bottom stripe
  s.addShape("rect", { x: 0, y: H - 0.55, w: W, h: 0.55, fill: { color: C.amber }, line: { color: C.amber } });
  s.addText("Satu sistem. Lebih efisien. Lebih akuntabel.", {
    x: 0, y: H - 0.55, w: W, h: 0.55,
    fontSize: 11.5, bold: true, color: C.navy, align: "center", valign: "middle", margin: 0,
  });

  // Heading
  s.addText("Mulai Sekarang", {
    x: 0.6, y: 0.35, w: 9, h: 0.75,
    fontSize: 32, bold: true, color: C.white, fontFace: "Calibri", margin: 0,
  });
  s.addText("Langkah-langkah untuk memulai:", {
    x: 0.6, y: 1.1, w: 9, h: 0.38,
    fontSize: 10.5, color: C.gray400, margin: 0,
  });

  const steps = [
    { no: "1", label: "Login ke sistem", detail: "Akun sudah disiapkan oleh IT · erp.garuda.id", color: C.blue },
    { no: "2", label: "Ikuti pelatihan per divisi", detail: "Jadwal pelatihan akan diinformasikan oleh HR", color: C.amber },
    { no: "3", label: "Hubungi IT untuk bantuan", detail: "Support: it@garuda.id  ·  Ext. 100", color: C.teal },
  ];

  steps.forEach((step, i) => {
    const x = 0.5 + i * 3.1;
    const y = 1.65;
    const cardW = 2.85, cardH = 2.55;
    card(s, x, y, cardW, cardH, { fill: C.navyMid, line: C.navyMid, shadow: false });
    s.addShape("rect", { x, y, w: cardW, h: 0.07, fill: { color: step.color }, line: { color: step.color } });

    // Number badge
    s.addShape("ellipse", {
      x: x + (cardW - 0.65) / 2, y: y + 0.2, w: 0.65, h: 0.65,
      fill: { color: step.color }, line: { color: step.color },
    });
    s.addText(step.no, {
      x: x + (cardW - 0.65) / 2, y: y + 0.2, w: 0.65, h: 0.65,
      fontSize: 20, bold: true, color: C.white, align: "center", valign: "middle", margin: 0,
    });

    s.addText(step.label, {
      x: x + 0.1, y: y + 1.0, w: cardW - 0.2, h: 0.6,
      fontSize: 11, bold: true, color: C.white, align: "center", fontFace: "Calibri", margin: 0,
    });
    s.addText(step.detail, {
      x: x + 0.1, y: y + 1.65, w: cardW - 0.2, h: 0.75,
      fontSize: 8.5, color: C.gray400, align: "center", fontFace: "Calibri", margin: 0,
    });
  });
}


// ── Write file ──────────────────────────────────────────────────────────────
const OUT = "C:\\Users\\theco\\Codex\\gpa-erp\\docs\\GPA-ERP-Introduction-Deck.pptx";
pres.writeFile({ fileName: OUT })
  .then(() => console.log(`✅  Saved: ${OUT}`))
  .catch((err) => { console.error("❌  Error:", err); process.exit(1); });
