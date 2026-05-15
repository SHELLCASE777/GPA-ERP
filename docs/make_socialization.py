"""
GPA Cost Control ERP V5.0 — Socialization Document Generator
Produces a professional PDF suitable for non-technical staff onboarding.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.colors import HexColor
import os

# ── Brand colours ─────────────────────────────────────────────────────────────
NAVY    = HexColor("#1E293B")
BLUE    = HexColor("#2563EB")
ACCENT  = HexColor("#F59E0B")
GREEN   = HexColor("#16A34A")
RED     = HexColor("#DC2626")
LIGHT   = HexColor("#F1F5F9")
MID     = HexColor("#94A3B8")
WHITE   = colors.white

OUT = r"C:\Users\theco\Codex\gpa-erp\docs\GPA-ERP-Socialization-v4.pdf"

W, H = A4
MARGIN = 2 * cm
# Usable content width inside margins
CW = W - 2 * MARGIN


# ── Page template (header/footer) ─────────────────────────────────────────────
class PageTemplate:
    def __init__(self, title):
        self.doc_title = title

    def __call__(self, canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(NAVY)
        canvas.rect(0, H - 18*mm, W, 18*mm, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(MARGIN, H - 11*mm, "GPA COST CONTROL ERP V5.0")
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(W - MARGIN, H - 11*mm, self.doc_title)

        # Footer bar
        canvas.setFillColor(LIGHT)
        canvas.rect(0, 0, W, 12*mm, fill=1, stroke=0)
        canvas.setFillColor(MID)
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(MARGIN, 4.5*mm, "DOKUMEN SOSIALISASI — RAHASIA INTERNAL")
        canvas.drawRightString(W - MARGIN, 4.5*mm, f"Halaman {doc.page}")
        canvas.restoreState()


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    base = getSampleStyleSheet()
    s = {}

    s["cover_title"] = ParagraphStyle("cover_title",
        fontSize=32, leading=38, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_CENTER, spaceAfter=6)
    s["cover_sub"] = ParagraphStyle("cover_sub",
        fontSize=14, leading=18, textColor=HexColor("#CBD5E1"), fontName="Helvetica",
        alignment=TA_CENTER, spaceAfter=4)
    s["cover_tag"] = ParagraphStyle("cover_tag",
        fontSize=10, leading=14, textColor=ACCENT, fontName="Helvetica-Bold",
        alignment=TA_CENTER)

    s["h1"] = ParagraphStyle("h1",
        fontSize=18, leading=22, textColor=NAVY, fontName="Helvetica-Bold",
        spaceBefore=14, spaceAfter=8, borderPad=0)
    s["h2"] = ParagraphStyle("h2",
        fontSize=13, leading=17, textColor=BLUE, fontName="Helvetica-Bold",
        spaceBefore=10, spaceAfter=5)
    s["h3"] = ParagraphStyle("h3",
        fontSize=10.5, leading=14, textColor=NAVY, fontName="Helvetica-Bold",
        spaceBefore=7, spaceAfter=3)

    s["body"] = ParagraphStyle("body",
        fontSize=9.5, leading=14, textColor=HexColor("#334155"),
        fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=5)
    s["bullet"] = ParagraphStyle("bullet",
        fontSize=9.5, leading=13.5, textColor=HexColor("#334155"),
        fontName="Helvetica", leftIndent=14, spaceAfter=3,
        bulletIndent=4, bulletFontName="Helvetica", bulletFontSize=9.5)
    s["note"] = ParagraphStyle("note",
        fontSize=8.5, leading=12, textColor=HexColor("#64748B"),
        fontName="Helvetica-Oblique", spaceAfter=4)
    s["toc_entry"] = ParagraphStyle("toc_entry",
        fontSize=10, leading=16, textColor=NAVY, fontName="Helvetica",
        leftIndent=0, spaceAfter=2)
    s["toc_sub"] = ParagraphStyle("toc_sub",
        fontSize=9, leading=14, textColor=MID, fontName="Helvetica",
        leftIndent=16, spaceAfter=1)
    s["label"] = ParagraphStyle("label",
        fontSize=8, leading=10, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_CENTER)
    # Table cell styles — these wrap correctly inside Paragraph
    s["th"] = ParagraphStyle("th",
        fontSize=9, leading=12, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_LEFT)
    s["th_c"] = ParagraphStyle("th_c",
        fontSize=8, leading=11, textColor=WHITE, fontName="Helvetica-Bold",
        alignment=TA_CENTER)
    s["cell"] = ParagraphStyle("cell",
        fontSize=9, leading=12, textColor=HexColor("#334155"), fontName="Helvetica",
        alignment=TA_LEFT)
    s["cell_bold"] = ParagraphStyle("cell_bold",
        fontSize=9, leading=12, textColor=NAVY, fontName="Helvetica-Bold",
        alignment=TA_LEFT)
    s["cell_center"] = ParagraphStyle("cell_center",
        fontSize=8.5, leading=11, textColor=NAVY, fontName="Helvetica",
        alignment=TA_CENTER)

    return s


# ── Helper: wrap a 2-D list of strings into Paragraph objects ─────────────────
def wrap_table(data, styles, header_style="th", cell_style="cell"):
    """Convert all str cells to Paragraphs so text wraps inside columns."""
    result = []
    for ri, row in enumerate(data):
        new_row = []
        for ci, cell in enumerate(row):
            if isinstance(cell, str):
                st = styles[header_style] if ri == 0 else styles[cell_style]
                new_row.append(Paragraph(cell, st))
            else:
                new_row.append(cell)
        result.append(new_row)
    return result


def divider(color=BLUE, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=6, spaceBefore=2)


def spacer(h=6):
    return Spacer(1, h)


def info_box(lines, s, bg=LIGHT, border=BLUE):
    content = [[Paragraph(l, s["body"])] for l in lines]
    t = Table(content, colWidths=[CW - 20])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (0,0), 8),
        ("BOTTOMPADDING", (0,-1), (-1,-1), 8),
        ("TOPPADDING", (0,1), (-1,-1), 2),
        ("LINEAFTER", (0,0), (0,-1), 3, border),
    ]))
    return t


# ── Shared table style builder ─────────────────────────────────────────────────
def base_table_style(extra=None):
    style = [
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("GRID", (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, HexColor("#F8FAFC")]),
    ]
    if extra:
        style.extend(extra)
    return style


# ── Cover page ────────────────────────────────────────────────────────────────
def cover_page(s):
    story = []

    cover_data = [[
        Paragraph("GPA", s["cover_title"]),
    ],[
        Paragraph("COST CONTROL ERP", s["cover_title"]),
    ],[
        Paragraph("V5.0", ParagraphStyle("cv", fontSize=18, leading=22,
            textColor=ACCENT, fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)),
    ],[
        Spacer(1, 10),
    ],[
        Paragraph("DOKUMEN SOSIALISASI SISTEM", s["cover_sub"]),
    ],[
        Paragraph("Panduan Pengenalan untuk Seluruh Pengguna", s["cover_sub"]),
    ],[
        Spacer(1, 20),
    ],[
        Paragraph("Sistem Manajemen Biaya Proyek Terintegrasi", s["cover_tag"]),
    ],[
        Paragraph("Multi-project · Multi-role · Real-time Approval", s["cover_tag"]),
    ]]

    cover_table = Table(cover_data, colWidths=[CW])
    cover_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,-1), (-1,-1), 30),
        ("LEFTPADDING", (0,0), (-1,-1), 20),
        ("RIGHTPADDING", (0,0), (-1,-1), 20),
    ]))
    story.append(cover_table)
    story.append(spacer(20))

    meta = [
        ["Versi Dokumen", "1.0"],
        ["Tanggal", "Mei 2026"],
        ["Status", "INTERNAL — TIDAK UNTUK DISEBARKAN"],
        ["Departemen", "IT / Operations"],
    ]
    meta_wrapped = wrap_table(meta, s, header_style="cell_bold", cell_style="cell")
    meta_table = Table(meta_wrapped, colWidths=[5*cm, CW - 5*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,-1), LIGHT),
        ("LINEBELOW", (0,0), (-1,-2), 0.5, HexColor("#E2E8F0")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(meta_table)
    story.append(PageBreak())
    return story


# ── Table of contents ─────────────────────────────────────────────────────────
def toc_page(s):
    story = []
    story.append(Paragraph("Daftar Isi", s["h1"]))
    story.append(divider())
    story.append(spacer(8))

    entries = [
        ("1", "Pendahuluan & Tujuan Sistem", None),
        ("2", "Arsitektur & Gambaran Umum", None),
        ("3", "Modul-Modul Sistem", None),
        ("", "3.1  Dashboard", "sub"),
        ("", "3.2  Action Center", "sub"),
        ("", "3.3  Project Command", "sub"),
        ("", "3.4  Revenue (Piutang Usaha)", "sub"),
        ("", "3.5  Spending (Pengeluaran)", "sub"),
        ("", "3.6  Inventory & Aset", "sub"),
        ("", "3.7  Legal & Proposal", "sub"),
        ("", "3.8  Reports", "sub"),
        ("", "3.9  Vault (Admin)", "sub"),
        ("", "3.10  Alur Khusus: Petty Cash", "sub"),
        ("4", "Peran & Hak Akses", None),
        ("5", "Alur Persetujuan Pengeluaran", None),
        ("6", "Panduan Memulai per Peran", None),
        ("7", "Fitur yang Akan Datang — HRIS & Pengembangan Lanjutan", None),
    ]

    for num, title, kind in entries:
        prefix = f"{num}.  " if num else "       "
        style = s["toc_sub"] if kind == "sub" else s["toc_entry"]
        row = Table([[
            Paragraph(f'<font color="#94A3B8">{prefix}</font><font color="#1E293B">{title}</font>', style),
            Paragraph('<font color="#94A3B8">· · ·</font>',
                ParagraphStyle("dot", fontSize=9, alignment=TA_LEFT, textColor=MID)),
        ]], colWidths=[CW - 1.5*cm, 1.5*cm])
        row.setStyle(TableStyle([
            ("LINEBELOW", (0,0), (-1,-1), 0.3, HexColor("#E2E8F0")),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(row)

    story.append(PageBreak())
    return story


# ── Section 1: Introduction ───────────────────────────────────────────────────
def section_intro(s):
    story = []
    story.append(Paragraph("1. Pendahuluan & Tujuan Sistem", s["h1"]))
    story.append(divider())
    story.append(Paragraph(
        "GPA Cost Control ERP V5.0 adalah sistem manajemen biaya proyek berbasis web yang dirancang "
        "khusus untuk kebutuhan perusahaan konstruksi dan jasa. Sistem ini mengintegrasikan seluruh "
        "siklus keuangan proyek — dari pengajuan anggaran, persetujuan bertingkat, pencatatan piutang "
        "usaha, hingga penutupan periode — dalam satu platform terpadu yang dapat diakses dari mana saja.",
        s["body"]))

    story.append(spacer(6))
    story.append(Paragraph("Tujuan Sosialisasi Ini", s["h2"]))
    bullets = [
        "Memperkenalkan sistem ERP kepada seluruh pengguna di semua tingkatan organisasi",
        "Menjelaskan modul-modul yang tersedia dan fungsinya masing-masing",
        "Memandu setiap pengguna memahami peran dan tanggung jawabnya dalam sistem",
        "Menjelaskan alur kerja persetujuan pengeluaran yang baru",
        "Menjawab pertanyaan umum yang mungkin timbul selama masa transisi",
    ]
    for b in bullets:
        story.append(Paragraph(f"&#8226;  {b}", s["bullet"]))

    story.append(spacer(8))
    story.append(info_box([
        "<b>Mengapa ERP ini penting?</b>",
        "Selama ini, pencatatan pengeluaran proyek dilakukan secara manual atau tersebar di berbagai "
        "spreadsheet. Hal ini menyebabkan kesulitan dalam pemantauan anggaran secara real-time, "
        "keterlambatan persetujuan, dan risiko kehilangan data. Sistem ERP ini menyelesaikan semua "
        "masalah tersebut sekaligus.",
    ], s))

    story.append(spacer(10))
    story.append(Paragraph("Prinsip Utama Sistem", s["h2"]))

    # Use Paragraph objects directly — no plain strings
    col1 = 5.5 * cm
    col2 = CW - col1
    principles = [
        [Paragraph("Prinsip", s["th"]),          Paragraph("Penjelasan", s["th"])],
        [Paragraph("Revenue-Driven Budget", s["cell_bold"]),
         Paragraph("Anggaran proyek ditentukan dari piutang usaha (AR) yang sudah dikonfirmasi, bukan hanya nilai kontrak", s["cell"])],
        [Paragraph("Multi-Step Approval", s["cell_bold"]),
         Paragraph("Setiap pengeluaran melewati rantai persetujuan sesuai matriks: jumlah & kategori menentukan siapa yang harus menyetujui", s["cell"])],
        [Paragraph("Immutable Audit Trail", s["cell_bold"]),
         Paragraph("Setiap aksi tercatat secara permanen — tidak ada yang bisa dihapus atau diubah tanpa jejak", s["cell"])],
        [Paragraph("Role-Based Access", s["cell_bold"]),
         Paragraph("Setiap pengguna hanya bisa melihat dan melakukan aksi sesuai perannya", s["cell"])],
    ]
    t = Table(principles, colWidths=[col1, col2])
    t.setStyle(TableStyle(base_table_style([
        ("BACKGROUND", (0,1), (0,-1), LIGHT),
    ])))
    story.append(t)
    story.append(PageBreak())
    return story


# ── Section 2: Architecture ───────────────────────────────────────────────────
def section_arch(s):
    story = []
    story.append(Paragraph("2. Arsitektur & Gambaran Umum", s["h1"]))
    story.append(divider())
    story.append(Paragraph(
        "Sistem berjalan sepenuhnya berbasis web — tidak memerlukan instalasi aplikasi. "
        "Pengguna cukup membuka browser dan mengakses URL yang diberikan oleh tim IT.",
        s["body"]))
    story.append(spacer(6))

    col_a, col_b, col_c = 4.5*cm, 4.5*cm, CW - 9*cm
    arch = [
        [Paragraph("Komponen", s["th"]),        Paragraph("Teknologi", s["th"]),         Paragraph("Fungsi", s["th"])],
        [Paragraph("Frontend (Tampilan)", s["cell_bold"]),
         Paragraph("Next.js 14 + React", s["cell"]),
         Paragraph("Antarmuka pengguna yang diakses via browser", s["cell"])],
        [Paragraph("Backend (Server)", s["cell_bold"]),
         Paragraph("FastAPI (Python)", s["cell"]),
         Paragraph("Logika bisnis, validasi, dan API data", s["cell"])],
        [Paragraph("Database", s["cell_bold"]),
         Paragraph("PostgreSQL", s["cell"]),
         Paragraph("Penyimpanan data permanen dan terstruktur", s["cell"])],
        [Paragraph("Autentikasi", s["cell_bold"]),
         Paragraph("JWT Token", s["cell"]),
         Paragraph("Login aman dengan sesi otomatis berakhir setelah 8 jam", s["cell"])],
    ]
    t = Table(arch, colWidths=[col_a, col_b, col_c])
    t.setStyle(TableStyle(base_table_style([
        ("BACKGROUND", (0,0), (-1,0), BLUE),
    ])))
    story.append(t)
    story.append(spacer(12))

    story.append(Paragraph("Cara Mengakses Sistem", s["h2"]))
    steps = [
        ("1", "Buka browser (Chrome, Edge, Firefox, Safari)"),
        ("2", "Masukkan URL sistem yang diberikan oleh tim IT"),
        ("3", "Login dengan email dan password yang diberikan admin"),
        ("4", "Anda akan diarahkan ke halaman sesuai peran Anda"),
    ]
    for num, text in steps:
        row = Table([[
            Paragraph(num, ParagraphStyle("n", fontSize=10, fontName="Helvetica-Bold",
                textColor=WHITE, alignment=TA_CENTER)),
            Paragraph(text, s["body"]),
        ]], colWidths=[0.7*cm, CW - 0.7*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), BLUE),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING", (1,0), (1,0), 10),
            ("LINEBELOW", (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
        ]))
        story.append(row)
        story.append(spacer(2))

    story.append(spacer(10))
    story.append(info_box([
        "<b>Tip Keamanan:</b> Jangan bagikan password Anda kepada siapapun. "
        "Sistem akan otomatis logout setelah 8 jam tidak aktif. "
        "Jika akun Anda terkunci, hubungi admin sistem.",
    ], s, bg=HexColor("#FEF3C7"), border=ACCENT))
    story.append(PageBreak())
    return story


# ── Section 3: Modules ────────────────────────────────────────────────────────
def section_modules(s):
    story = []
    story.append(Paragraph("3. Modul-Modul Sistem", s["h1"]))
    story.append(divider())
    story.append(Paragraph(
        "Sistem ERP ini terdiri dari 9 modul utama. Tidak semua pengguna dapat mengakses "
        "semua modul — akses ditentukan oleh peran (role) yang ditetapkan admin.",
        s["body"]))
    story.append(spacer(8))

    modules = [
        ("Dashboard", BLUE,
         "Ringkasan KPI proyek, total pengeluaran, status persetujuan, dan aktivitas terkini dalam satu halaman. Diakses semua peran."),
        ("Action Center", HexColor("#7C3AED"),
         "Daftar tugas yang menunggu tindakan Anda: pengeluaran yang perlu diverifikasi, disetujui, atau dibayar. Notifikasi aksi tertunda."),
        ("Project Command", HexColor("#0891B2"),
         "Manajemen proyek: daftar proyek, anggaran, burn rate, nilai kontrak, dan status. Import proyek massal via Excel/CSV."),
        ("Revenue (Piutang)", GREEN,
         "Pengelolaan invoice/piutang usaha (Account Receivable). Invoice yang dikonfirmasi menjadi plafon anggaran proyek."),
        ("Spending", HexColor("#EA580C"),
         "Modul utama pengeluaran: buat pengeluaran baru, pantau status persetujuan, laporan petty cash, pencarian & filter lengkap."),
        ("Inventory & Aset", HexColor("#CA8A04"),
         "Pencatatan barang masuk/keluar, stok saat ini, aset perusahaan, dan transaksi penyesuaian. Alert stok minimum."),
        ("Legal & Proposal", HexColor("#BE185D"),
         "Manajemen dokumen legal: SPK, kontrak, proposal. Alur submit → tanda tangan digital MD/PM → arsip."),
        ("Reports", NAVY,
         "Laporan keuangan, rekap pengeluaran per proyek, analisis anggaran vs aktual. Export ke Excel (coming soon)."),
        ("Vault", MID,
         "Konfigurasi sistem: cost codes, cost centres, matriks persetujuan, manajemen pengguna, log audit. Hanya Super Admin."),
    ]

    icon_col = 1.4 * cm
    desc_col = CW - icon_col
    for i, (name, color, desc) in enumerate(modules):
        num = f"3.{i+1}"
        story.append(Paragraph(f"{num}  {name}", s["h2"]))
        abbr = name[:2].upper()
        row = Table([[
            Table([[Paragraph(abbr, ParagraphStyle("icon",
                fontSize=13, fontName="Helvetica-Bold", textColor=WHITE,
                alignment=TA_CENTER))]],
                colWidths=[icon_col], rowHeights=[1.1*cm]),
            Paragraph(desc, s["body"]),
        ]], colWidths=[icon_col + 0.3*cm, desc_col - 0.3*cm])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), color),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (1,0), (1,0), 10),
            ("RIGHTPADDING", (1,0), (1,0), 6),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(row)
        story.append(spacer(6))

    story.append(PageBreak())
    return story


# ── Section 3b: Petty Cash Workflow ──────────────────────────────────────────
def section_petty_cash(s):
    story = []
    story.append(Paragraph("3.10  Alur Khusus: Petty Cash (Kas Kecil)", s["h1"]))
    story.append(divider())
    story.append(Paragraph(
        "Petty Cash adalah mekanisme penggantian pengeluaran tunai kecil yang dilakukan "
        "secara berkala (biasanya per bulan). Alurnya berbeda dari pengeluaran biasa — "
        "GA atau PM merekap semua pengeluaran kecil dalam satu <b>Laporan Petty Cash</b>, "
        "lalu sistem otomatis membuat draft expense per baris saat laporan diposting.",
        s["body"]))
    story.append(spacer(4))
    story.append(info_box([
        "<b>Kapan pakai Petty Cash?</b>  Gunakan Petty Cash untuk pengeluaran tunai kecil "
        "yang sudah terjadi (parkir, fotokopi, ATK, konsumsi rapat, dll). "
        "Untuk pengeluaran besar yang perlu persetujuan sebelum dibayar, gunakan Expense biasa.",
    ], s, bg=HexColor("#FEF3C7"), border=ACCENT))
    story.append(spacer(10))

    story.append(Paragraph("Langkah-Langkah Petty Cash", s["h2"]))

    pc_steps = [
        (HexColor("#0891B2"), "1", "Buat Laporan",
         "Spending → Petty Cash Reports → [+ New Report]. Isi bulan, proyek, dan cost centre laporan."),
        (HexColor("#7C3AED"), "2", "Tambah Baris",
         "Klik [+ Add Line] untuk setiap pengeluaran: tanggal, deskripsi, jumlah (Rp), foto struk (opsional)."),
        (HexColor("#EA580C"), "3", "Review Total",
         "Pastikan total laporan sesuai dengan jumlah uang yang dikeluarkan. Edit atau hapus baris jika ada kesalahan."),
        (GREEN,               "4", "Post Laporan",
         "Klik [Post Report]. Sistem otomatis membuat <b>Draft Expense</b> untuk setiap baris laporan."),
        (BLUE,                "5", "Expense Masuk Alur Normal",
         "Draft expense yang terbuat langsung masuk alur persetujuan biasa: Submit → Verify → Approve → Pay."),
    ]

    status_col = 2.8 * cm
    desc_col   = CW - status_col
    for color, num, label, desc in pc_steps:
        row = Table([[
            Paragraph(f'<b>{num}</b><br/><font size="8">{label}</font>',
                ParagraphStyle("pcn", fontSize=13, fontName="Helvetica-Bold",
                    textColor=WHITE, alignment=TA_CENTER, leading=16)),
            Paragraph(desc, s["body"]),
        ]], colWidths=[status_col, desc_col])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), color),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (1,0), (1,0), 12),
            ("RIGHTPADDING", (1,0), (1,0), 6),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(KeepTogether([row, spacer(3)]))
        if num != "5":
            story.append(Paragraph(
                '<font color="#94A3B8">          ▼</font>',
                ParagraphStyle("arr2", fontSize=12, alignment=TA_LEFT)))
            story.append(spacer(2))

    story.append(spacer(10))

    # Summary comparison table
    story.append(Paragraph("Perbandingan: Expense Biasa vs Petty Cash", s["h2"]))
    comp_col = CW / 3
    comp = [
        [Paragraph("Aspek", s["th"]),
         Paragraph("Expense Biasa", s["th"]),
         Paragraph("Petty Cash", s["th"])],
        [Paragraph("Kapan dibuat", s["cell_bold"]),
         Paragraph("Sebelum atau sesudah pengeluaran", s["cell"]),
         Paragraph("Setelah uang dikeluarkan (rekapan bulanan)", s["cell"])],
        [Paragraph("Ukuran transaksi", s["cell_bold"]),
         Paragraph("Semua nilai (besar maupun kecil)", s["cell"]),
         Paragraph("Pengeluaran tunai kecil", s["cell"])],
        [Paragraph("Diisi oleh", s["cell_bold"]),
         Paragraph("Staff / PM / GA / siapa saja", s["cell"]),
         Paragraph("GA atau PM yang pegang kas kecil", s["cell"])],
        [Paragraph("Hasil setelah diposting", s["cell_bold"]),
         Paragraph("Langsung masuk antrian persetujuan", s["cell"]),
         Paragraph("Otomatis buat Draft Expense per baris", s["cell"])],
    ]
    t = Table(comp, colWidths=[comp_col, comp_col, comp_col])
    t.setStyle(TableStyle(base_table_style()))
    story.append(t)
    story.append(PageBreak())
    return story


# ── Section 4: Roles ──────────────────────────────────────────────────────────
def section_roles(s):
    story = []
    story.append(Paragraph("4. Peran & Hak Akses", s["h1"]))
    story.append(divider())
    story.append(Paragraph(
        "Setiap pengguna memiliki satu peran yang menentukan modul apa yang bisa diakses "
        "dan aksi apa yang bisa dilakukan. Tabel berikut merangkum hak akses per peran.",
        s["body"]))
    story.append(spacer(8))

    Y = Paragraph("YES",     ParagraphStyle("y", fontSize=7.5, fontName="Helvetica-Bold", textColor=GREEN,  alignment=TA_CENTER))
    N = Paragraph("-",       ParagraphStyle("n", fontSize=8,   fontName="Helvetica",      textColor=MID,    alignment=TA_CENTER))
    P = Paragraph("PARTIAL", ParagraphStyle("p", fontSize=7,   fontName="Helvetica",      textColor=ACCENT, alignment=TA_CENTER))

    feat_col = 5.2 * cm
    role_col = (CW - feat_col) / 7   # 7 role columns, equal width

    def feat(txt):
        return Paragraph(txt, s["cell"])

    header = [Paragraph(h, s["th_c"]) for h in
              ["Fitur / Aksi", "S.ADMIN", "MD", "PM", "C.CTRL", "FINANCE", "GA", "STAFF"]]
    header[0] = Paragraph("Fitur / Aksi", s["th"])

    rows = [
        [feat("Dashboard & Action Center"),    Y, Y, Y, Y, Y, Y, Y],
        [feat("Lihat Semua Proyek"),           Y, Y, Y, Y, Y, P, N],
        [feat("Buat / Edit Proyek"),           Y, Y, Y, N, N, N, N],
        [feat("Buat Pengeluaran"),             Y, Y, Y, Y, Y, Y, Y],
        [feat("Submit Pengeluaran"),           Y, Y, Y, Y, Y, Y, Y],
        [feat("Verifikasi Pengeluaran"),       Y, N, N, Y, N, N, N],
        [feat("Setujui Pengeluaran"),          Y, Y, Y, N, N, N, N],
        [feat("Bayar Pengeluaran"),            Y, N, N, N, Y, N, N],
        [feat("Kelola Petty Cash"),            Y, Y, Y, Y, Y, Y, N],
        [feat("Kelola Piutang (AR)"),          Y, Y, N, N, Y, N, N],
        [feat("Konfirmasi AR"),                Y, Y, N, N, Y, N, N],
        [feat("Kelola Inventory"),             Y, N, Y, N, N, Y, N],
        [feat("Buat / Sign Dokumen Legal"),    Y, Y, Y, N, N, N, N],
        [feat("Konfigurasi Vault"),            Y, N, N, N, N, N, N],
        [feat("Manajemen Pengguna"),           Y, N, N, N, N, N, N],
        [feat("Lihat Laporan"),                Y, Y, Y, Y, Y, P, N],
    ]

    table_data = [header] + rows
    col_widths = [feat_col] + [role_col] * 7
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle(base_table_style([
        ("ALIGN", (1,0), (-1,-1), "CENTER"),
        ("BACKGROUND", (0,1), (0,-1), LIGHT),
    ])))
    story.append(t)
    story.append(spacer(8))
    story.append(Paragraph(
        "YES = akses penuh  ·  PARTIAL = akses terbatas  ·  - = tidak ada akses",
        s["note"]))
    story.append(PageBreak())
    return story


# ── Section 5: Approval Workflow ──────────────────────────────────────────────
def section_workflow(s):
    story = []
    story.append(Paragraph("5. Alur Persetujuan Pengeluaran", s["h1"]))
    story.append(divider())
    story.append(Paragraph(
        "Setiap pengeluaran melewati alur persetujuan bertingkat. Rantai persetujuan "
        "ditentukan secara otomatis berdasarkan jumlah dan kategori biaya sesuai matriks "
        "yang dikonfigurasi di Vault. Berikut adalah alur lengkapnya:",
        s["body"]))
    story.append(spacer(10))

    steps = [
        (BLUE,                "DRAFT",       "Pengeluaran dibuat oleh Staff/PM/GA. Bisa diedit, belum masuk sistem persetujuan."),
        (HexColor("#7C3AED"), "SUBMITTED",   "Pengeluaran disubmit. Sistem membangun rantai persetujuan otomatis dari matriks."),
        (HexColor("#0891B2"), "VERIFIED",    "Cost Control memverifikasi keabsahan pengeluaran (gate pertama — wajib dilewati)."),
        (GREEN,               "APPROVED",    "Pejabat sesuai matriks (Finance/MD/dll) menyetujui satu per satu sesuai urutan."),
        (HexColor("#16A34A"), "PAID",        "Finance menandai pembayaran sudah dilakukan. Pengeluaran selesai."),
        (NAVY,                "HARD LOCKED", "Super Admin mengunci periode. Data tidak bisa diubah lagi."),
    ]

    status_col = 3.2 * cm
    desc_col   = CW - status_col

    for i, (color, status, desc) in enumerate(steps):
        row = Table([[
            Paragraph(status, ParagraphStyle("st", fontSize=8, fontName="Helvetica-Bold",
                textColor=WHITE, alignment=TA_CENTER)),
            Paragraph(desc, s["body"]),
        ]], colWidths=[status_col, desc_col])
        row.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), color),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (1,0), (1,0), 12),
            ("RIGHTPADDING", (1,0), (1,0), 6),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ]))
        story.append(KeepTogether([row, spacer(2)]))
        if i < len(steps) - 1:
            story.append(Paragraph(
                '<font color="#94A3B8">          ▼</font>',
                ParagraphStyle("arr", fontSize=14, alignment=TA_LEFT)))
            story.append(spacer(2))

    story.append(spacer(10))
    story.append(Paragraph("Penolakan (REJECTED)", s["h2"]))
    story.append(Paragraph(
        "Pengeluaran bisa ditolak di tahap manapun (kecuali PAID dan HARD LOCKED) "
        "dengan menyertakan alasan. Pengaju akan mendapat notifikasi dan bisa "
        "memperbaiki serta meresubmit pengeluaran.",
        s["body"]))

    story.append(spacer(10))
    story.append(Paragraph("Contoh Matriks Persetujuan", s["h2"]))
    story.append(Paragraph(
        "Konfigurasi aktual dapat berbeda sesuai kebijakan perusahaan dan diatur di Vault.",
        s["note"]))
    story.append(spacer(4))

    col_v = 4.8 * cm
    col_k = 3.2 * cm
    col_r = CW - col_v - col_k
    matrix = [
        [Paragraph("Nilai Pengeluaran", s["th"]),
         Paragraph("Kategori", s["th"]),
         Paragraph("Rantai Persetujuan", s["th"])],
        [Paragraph("< Rp 5.000.000", s["cell"]),
         Paragraph("Semua", s["cell"]),
         Paragraph("Cost Control → Finance", s["cell"])],
        [Paragraph("Rp 5jt – Rp 50jt", s["cell"]),
         Paragraph("Semua", s["cell"]),
         Paragraph("Cost Control → Finance → MD", s["cell"])],
        [Paragraph("Rp 50jt – Rp 500jt", s["cell"]),
         Paragraph("Semua", s["cell"]),
         Paragraph("Cost Control → Finance → MD", s["cell"])],
        [Paragraph("> Rp 500.000.000", s["cell"]),
         Paragraph("Semua", s["cell"]),
         Paragraph("Cost Control → Finance → MD → Super Admin", s["cell"])],
    ]
    t = Table(matrix, colWidths=[col_v, col_k, col_r])
    t.setStyle(TableStyle(base_table_style()))
    story.append(t)
    story.append(PageBreak())
    return story


# ── Section 6: Getting started ────────────────────────────────────────────────
def section_getting_started(s):
    story = []
    story.append(Paragraph("6. Panduan Memulai per Peran", s["h1"]))
    story.append(divider())
    story.append(spacer(4))

    guides = [
        ("STAFF / GA", HexColor("#EA580C"), [
            "Login → Dashboard → lihat ringkasan aktivitas Anda",
            "Klik [+ New Expense] di pojok kanan atas untuk buat pengeluaran baru",
            "Isi: Proyek, Cost Code, Jumlah, Deskripsi, Vendor (opsional)",
            "Klik [Create Draft] — pengeluaran tersimpan sebagai DRAFT",
            "Cek draf Anda di halaman Spending, klik [...] → Submit",
            "Pantau status di kolom STATUS — tunggu notifikasi jika ditolak",
        ]),
        ("COST CONTROL", HexColor("#0891B2"), [
            "Login → Action Center → lihat daftar pengeluaran yang menunggu verifikasi",
            "Klik pengeluaran untuk melihat detail lengkap",
            "Verifikasi keabsahan: jumlah, cost code, deskripsi, receipt",
            "Klik [Verify] jika valid, atau [Reject] dengan alasan jika tidak valid",
            "Pengeluaran yang diverifikasi otomatis lanjut ke approver berikutnya",
            "Kelola Cost Codes & Cost Centres via menu Vault (jika diberi akses)",
        ]),
        ("PM / MD", HexColor("#7C3AED"), [
            "Login → Action Center → lihat pengeluaran yang menunggu persetujuan Anda",
            "Review detail pengeluaran: jumlah, kategori, budget proyek tersisa",
            "Klik [Approve] untuk menyetujui, atau [Reject] dengan alasan",
            "Pantau Project Command → pilih proyek → lihat burn rate & committed spend",
            "Jika budget proyek minus (merah), tinjau AR yang perlu dikonfirmasi",
            "Legal: buat/review dokumen di menu Legal & Proposals, tandatangani jika perlu",
        ]),
        ("FINANCE", GREEN, [
            "Login → Spending → filter Status: Approved → lihat yang siap dibayar",
            "Klik pengeluaran yang sudah disetujui → [Pay] setelah transfer dilakukan",
            "Kelola piutang usaha di menu Revenue → konfirmasi invoice yang sudah diterima",
            "Invoice yang dikonfirmasi otomatis menambah plafon anggaran proyek",
            "Rekap pembayaran bisa dilihat di Spending dengan filter Status: Paid",
        ]),
        ("SUPER ADMIN", NAVY, [
            "Setup awal: Login → Vault → Cost Codes: buat hierarki kode biaya",
            "Vault → Cost Centres: daftarkan departemen/lokasi proyek",
            "Vault → Approval Rules: konfigurasi matriks persetujuan (jumlah & kategori)",
            "Users → Create User: buat akun untuk setiap anggota tim, tentukan role",
            "Tutup periode: Spending → filter Status: Paid → Hard Lock setelah rekonsiliasi",
            "Audit Log tersedia di Vault → Audit Log untuk melihat semua aktivitas sistem",
        ]),
    ]

    for role, color, steps in guides:
        role_header = Table([[
            Paragraph(f"  {role}", ParagraphStyle("rh",
                fontSize=11, fontName="Helvetica-Bold", textColor=WHITE,
                leading=15)),
        ]], colWidths=[CW])
        role_header.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), color),
            ("TOPPADDING", (0,0), (-1,-1), 7),
            ("BOTTOMPADDING", (0,0), (-1,-1), 7),
            ("LEFTPADDING", (0,0), (-1,-1), 10),
        ]))
        step_items = [
            Paragraph(f"<font color='#2563EB'><b>{i+1}.</b></font>  {step}", s["bullet"])
            for i, step in enumerate(steps)
        ]
        story.append(KeepTogether([role_header, spacer(2)] + step_items + [spacer(10)]))

    return story


# ── Section 7: Coming Soon ────────────────────────────────────────────────────
def section_coming_soon(s):
    TEAL   = HexColor("#0D9488")
    PURPLE = HexColor("#7C3AED")
    ORANGE = HexColor("#EA580C")
    GOLD   = HexColor("#CA8A04")

    story = []
    story.append(Paragraph("7. Fitur yang Akan Datang — HRIS & Pengembangan Lanjutan", s["h1"]))
    story.append(divider())
    story.append(Paragraph(
        "Sistem GPA Cost Control ERP terus dikembangkan secara aktif. Selain modul ERP yang "
        "sudah berjalan, tim sedang membangun modul <b>HRIS (Human Resource Information System)</b> "
        "yang akan menjadikan sistem ini sebagai solusi lengkap manajemen perusahaan — "
        "dari biaya proyek hingga penggajian karyawan.",
        s["body"]))
    story.append(spacer(10))

    # ── HRIS Feature Block (prominent / full-width) ───────────────────────────
    hris_header = Table([[
        Paragraph(
            '<b>HRIS — Human Resource Information System</b>',
            ParagraphStyle("hris_h", fontSize=13, fontName="Helvetica-Bold",
                textColor=WHITE, leading=17)),
        Paragraph(
            '<b>ROADMAP</b>',
            ParagraphStyle("hris_badge", fontSize=9, fontName="Helvetica-Bold",
                textColor=WHITE, alignment=TA_CENTER, leading=12)),
    ]], colWidths=[CW - 2.6*cm, 2.6*cm])
    hris_header.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (0,0), NAVY),
        ("BACKGROUND", (1,0), (1,0), MID),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 11),
        ("BOTTOMPADDING", (0,0), (-1,-1), 11),
        ("LEFTPADDING", (0,0), (0,0), 14),
        ("LEFTPADDING", (1,0), (1,0), 4),
        ("RIGHTPADDING", (1,0), (1,0), 4),
    ]))

    hris_intro = Paragraph(
        "Modul HRIS akan terintegrasi langsung dengan ERP — data karyawan, absensi, dan "
        "penggajian terhubung ke cost centre dan approval matrix yang sudah ada. "
        "Tidak perlu sistem HR terpisah.",
        s["body"])

    # Four sub-module cards inside the HRIS block
    hris_modules = [
        (TEAL,   "H1", "Data Karyawan & Organisasi",
         ["Master data karyawan (NIK, NPWP, BPJS, rekening)",
          "Struktur organisasi & grade jabatan",
          "Tipe kepegawaian: Tetap, PKWT, Outsource",
          "Org chart visual & penyimpanan dokumen (KTP, ijazah)"]),
        (PURPLE, "H2", "Absensi & Cuti",
         ["Pencatatan absensi harian (manual atau import fingerprint)",
          "Lembur: tarif regular, weekend, hari libur (Permenaker)",
          "Jenis cuti: tahunan, sakit, melahirkan, tanpa gaji",
          "Saldo cuti otomatis & approval oleh atasan langsung"]),
        (ORANGE, "H3", "Penggajian (Payroll)",
         ["Komponen gaji fleksibel (tunjangan transport, makan, jabatan)",
          "BPJS TK (JKK, JKM, JHT, JP) & BPJS Kesehatan otomatis",
          "PPh 21 gross-up / netto, PTKP per status, tarif 2024",
          "THR otomatis, slip gaji PDF, transfer bank CSV (BCA/Mandiri/BNI)"]),
        (GREEN,  "H4", "Rekrutmen & Onboarding",
         ["Tracking lamaran: Diterima → Screening → Interview → Offer",
          "Surat penawaran (offer letter) PDF otomatis",
          "Checklist onboarding untuk HR dan karyawan baru",
          "Karyawan baru otomatis terbuat dari data pelamar"]),
    ]

    mod_col_w = (CW - 4*mm) / 2
    mod_rows = []
    for i in range(0, len(hris_modules), 2):
        pair = hris_modules[i:i+2]
        row_cells = []
        for color, code, title, bullets in pair:
            cell_items = [
                Paragraph(f'<b>{code} — {title}</b>',
                    ParagraphStyle(f"mc_{code}", fontSize=9, fontName="Helvetica-Bold",
                        textColor=color, leading=13, spaceAfter=4)),
            ]
            for b in bullets:
                cell_items.append(Paragraph(
                    f'<font color="#64748B">&#8226;</font>  {b}',
                    ParagraphStyle(f"mb_{code}", fontSize=8, textColor=HexColor("#334155"),
                        leading=11, leftIndent=6)))
            inner = Table([[ci] for ci in cell_items], colWidths=[mod_col_w - 16*mm])
            inner.setStyle(TableStyle([
                ("TOPPADDING",    (0,0), (-1,-1), 2),
                ("BOTTOMPADDING", (0,0), (-1,-1), 2),
                ("LEFTPADDING",   (0,0), (-1,-1), 0),
                ("LINEBEFORE",    (0,0), (0,-1), 3, color),
                ("LEFTPADDING",   (0,0), (0,-1), 8),
            ]))
            row_cells.append(inner)
        if len(row_cells) == 1:
            row_cells.append(Paragraph("", s["body"]))
        mod_rows.append(row_cells)

    mod_grid = Table(mod_rows, colWidths=[mod_col_w, mod_col_w])
    mod_grid.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HexColor("#F8FAFC")),
        ("BOX",           (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
        ("INNERGRID",     (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]))

    hris_integration = Table([[Paragraph(
        "<b>Integrasi dengan ERP:</b> Penggajian otomatis ter-posting sebagai Expense ke cost "
        "centre yang sesuai. Absensi dan lembur karyawan langsung masuk ke perhitungan gaji "
        "bulan berikutnya — tidak ada entry manual ganda antara HR dan Finance.",
        ParagraphStyle("hint", fontSize=8.5, textColor=HexColor("#334155"), leading=12))
    ]], colWidths=[CW])
    hris_integration.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HexColor("#FFF7ED")),
        ("BOX",           (0,0), (-1,-1), 1, ACCENT),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
        ("RIGHTPADDING",  (0,0), (-1,-1), 12),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ]))

    story.append(KeepTogether([
        hris_header,
        Table([[hris_intro]], colWidths=[CW], style=TableStyle([
            ("BACKGROUND",    (0,0), (-1,-1), HexColor("#F1F5F9")),
            ("LEFTPADDING",   (0,0), (-1,-1), 14),
            ("RIGHTPADDING",  (0,0), (-1,-1), 14),
            ("TOPPADDING",    (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ])),
        mod_grid,
        hris_integration,
        spacer(10),
    ]))

    # ── Regular feature cards ─────────────────────────────────────────────────
    features = [
        (
            PURPLE, "SEGERA",
            "Notifikasi Email & Push",
            "Peringatan otomatis ke email saat pengeluaran disubmit, diverifikasi, disetujui, "
            "ditolak, atau dibayar. Tidak perlu cek sistem terus-menerus — sistem yang menghubungi Anda.",
            ["Notifikasi email saat status expense berubah",
             "Pengingat untuk approver yang belum merespons",
             "Ringkasan harian aktivitas proyek"],
        ),
        (
            GREEN, "SEGERA",
            "Export Laporan ke Excel",
            "Ekspor data pengeluaran, rekap proyek, dan analisis anggaran langsung ke file "
            "Excel (.xlsx) dengan format yang siap presentasi.",
            ["Export pengeluaran per proyek & periode",
             "Rekap perbandingan anggaran vs aktual",
             "Laporan petty cash per bulan"],
        ),
        (
            GOLD, "SOON",
            "Dashboard Real-Time yang Lebih Cepat",
            "Endpoint dashboard terpadu yang memuat semua KPI dalam satu request — "
            "halaman utama akan terasa jauh lebih responsif terutama pada koneksi lambat.",
            ["Loading dashboard lebih cepat",
             "Grafik burn rate real-time per proyek",
             "Widget ringkasan aktivitas hari ini"],
        ),
        (
            NAVY, "SOON",
            "Aplikasi Mobile (Android & iOS)",
            "Versi aplikasi native untuk smartphone — ideal untuk GA dan Staff yang sering "
            "di lapangan dan perlu submit pengeluaran dari lokasi proyek.",
            ["Submit & foto struk langsung dari lapangan",
             "Approve expense di mana saja",
             "Notifikasi push native"],
        ),
    ]

    BADGE_COLORS = {
        "SEGERA":   GREEN,
        "SOON":     ACCENT,
        "ROADMAP":  MID,
    }

    for color, badge, title, desc, bullets in features:
        badge_color = BADGE_COLORS.get(badge, MID)

        header = Table([[
            Paragraph(
                f'<font size="11"><b>{title}</b></font>',
                ParagraphStyle("fth", fontSize=11, fontName="Helvetica-Bold",
                    textColor=WHITE, leading=14)),
            Paragraph(
                f'<b>{badge}</b>',
                ParagraphStyle("fbadge", fontSize=8, fontName="Helvetica-Bold",
                    textColor=WHITE, alignment=TA_CENTER)),
        ]], colWidths=[CW - 2.2*cm, 2.2*cm])
        header.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), color),
            ("BACKGROUND", (1,0), (1,0), badge_color),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 8),
            ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ("LEFTPADDING", (0,0), (0,0), 12),
            ("LEFTPADDING", (1,0), (1,0), 4),
            ("RIGHTPADDING", (1,0), (1,0), 4),
        ]))

        body_items = [Paragraph(desc, s["body"]), spacer(4)]
        for b in bullets:
            body_items.append(Paragraph(
                f'<font color="#2563EB">&#8226;</font>  {b}',
                s["bullet"]))

        body_tbl = Table(
            [[item] for item in body_items],
            colWidths=[CW])
        body_tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), HexColor("#F8FAFC")),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("RIGHTPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING", (0,0), (0,0), 8),
            ("BOTTOMPADDING", (0,-1), (-1,-1), 8),
            ("TOPPADDING", (0,1), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-2), 0),
            ("LINEAFTER", (0,0), (0,-1), 3, color),
        ]))

        story.append(KeepTogether([header, body_tbl, spacer(8)]))

    story.append(spacer(6))
    story.append(info_box([
        "<b>Catatan Pengembangan:</b> Jadwal rilis fitur di atas bersifat indikatif dan dapat "
        "berubah. Tim IT akan menginformasikan setiap pembaruan sistem melalui email internal "
        "sebelum pembaruan dilakukan. Data yang sudah ada tidak akan terdampak oleh pembaruan.",
    ], s, bg=HexColor("#F0FDF4"), border=GREEN))

    return story


# ── Main ──────────────────────────────────────────────────────────────────────
def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = SimpleDocTemplate(
        OUT,
        pagesize=A4,
        topMargin=22*mm,
        bottomMargin=18*mm,
        leftMargin=MARGIN,
        rightMargin=MARGIN,
        title="GPA ERP V5.0 — Dokumen Sosialisasi",
        author="GPA IT Department",
        subject="ERP Socialization Document",
    )

    s = make_styles()
    template = PageTemplate("Dokumen Sosialisasi ERP V5.0")

    story = []
    story += cover_page(s)
    story += toc_page(s)
    story += section_intro(s)
    story += section_arch(s)
    story += section_modules(s)
    story += section_petty_cash(s)
    story += section_roles(s)
    story += section_workflow(s)
    story += section_getting_started(s)
    story += section_coming_soon(s)

    doc.build(story, onFirstPage=template, onLaterPages=template)

    from pypdf import PdfReader
    pages = len(PdfReader(OUT).pages)
    print(f"PDF saved to: {OUT}")
    print(f"Pages: {pages}")


if __name__ == "__main__":
    build()
