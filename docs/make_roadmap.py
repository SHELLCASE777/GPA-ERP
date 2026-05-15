"""
GPA ERP → Commercial ERP+HRIS Product
Product Roadmap PDF Generator
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.lib.colors import HexColor
import os

# ── Brand colours ──────────────────────────────────────────────────────────────
NAVY    = HexColor("#1E293B")
BLUE    = HexColor("#2563EB")
ACCENT  = HexColor("#F59E0B")
GREEN   = HexColor("#16A34A")
TEAL    = HexColor("#0D9488")
PURPLE  = HexColor("#7C3AED")
ORANGE  = HexColor("#EA580C")
RED     = HexColor("#DC2626")
LIGHT   = HexColor("#F1F5F9")
LIGHT2  = HexColor("#E2E8F0")
MID     = HexColor("#94A3B8")
DARK    = HexColor("#334155")
WHITE   = colors.white

OUT = r"C:\Users\theco\Codex\gpa-erp\docs\GPA-ERP-Product-Roadmap.pdf"
W, H = A4
MARGIN = 2 * cm
CW = W - 2 * MARGIN


# ── Styles ─────────────────────────────────────────────────────────────────────
ss = getSampleStyleSheet()

def mk(name, parent="Normal", **kw):
    return ParagraphStyle(name, parent=ss[parent], **kw)

h1  = mk("H1", "Normal", fontSize=22, textColor=NAVY,    leading=28, spaceAfter=6,  fontName="Helvetica-Bold")
h2  = mk("H2", "Normal", fontSize=14, textColor=NAVY,    leading=18, spaceAfter=4,  fontName="Helvetica-Bold", spaceBefore=14)
h3  = mk("H3", "Normal", fontSize=11, textColor=BLUE,    leading=14, spaceAfter=3,  fontName="Helvetica-Bold", spaceBefore=8)
body= mk("Body","Normal", fontSize=9,  textColor=DARK,    leading=13, spaceAfter=4)
sm  = mk("Sm",  "Normal", fontSize=8,  textColor=DARK,    leading=11, spaceAfter=2)
smg = mk("SmG", "Normal", fontSize=8,  textColor=MID,     leading=11)
cap = mk("Cap", "Normal", fontSize=7.5,textColor=MID,     leading=10, alignment=TA_CENTER)
cell= mk("Cell","Normal", fontSize=8.5,textColor=DARK,    leading=12, wordWrap="CJK")
cellb=mk("CellB","Normal",fontSize=8.5,textColor=NAVY,   leading=12, fontName="Helvetica-Bold", wordWrap="CJK")
cellc=mk("CellC","Normal",fontSize=8.5,textColor=WHITE,  leading=12, fontName="Helvetica-Bold", wordWrap="CJK", alignment=TA_CENTER)
ctr = mk("Ctr", "Normal", fontSize=9,  textColor=DARK,    leading=12, alignment=TA_CENTER)
ctrs= mk("CtrS","Normal", fontSize=8,  textColor=MID,     leading=11, alignment=TA_CENTER)


def P(text, style=body): return Paragraph(str(text), style)
def SP(h=4):             return Spacer(1, h*mm)
def HR():                return HRFlowable(width="100%", thickness=0.5, color=LIGHT2, spaceAfter=4)


# ── Page template ──────────────────────────────────────────────────────────────
def page_template(canvas, doc):
    canvas.saveState()
    # Top bar
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 16*mm, W, 16*mm, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, H - 16*mm, 4*mm, 16*mm, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica-Bold", 8.5)
    canvas.drawString(MARGIN, H - 10*mm, "GPA COST CONTROL ERP")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(W - MARGIN, H - 10*mm, "PRODUCT ROADMAP — COMMERCIAL EDITION")

    # Bottom bar
    canvas.setFillColor(LIGHT)
    canvas.rect(0, 0, W, 11*mm, fill=1, stroke=0)
    canvas.setFillColor(MID)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(MARGIN, 4*mm, "CONFIDENTIAL — INTERNAL DOCUMENT")
    canvas.drawRightString(W - MARGIN, 4*mm, f"Page {doc.page}")
    canvas.restoreState()


# ── Cover page ─────────────────────────────────────────────────────────────────
def cover_page():
    story = []
    story.append(SP(10))

    # Large title block
    story.append(Paragraph(
        '<font color="#2563EB"><b>GPA</b></font> <font color="#1E293B">COST CONTROL ERP</font>',
        mk("CoverT","Normal", fontSize=32, leading=40, alignment=TA_CENTER, fontName="Helvetica-Bold")
    ))
    story.append(SP(2))
    story.append(Paragraph(
        "Commercial ERP + HRIS Product Roadmap",
        mk("CoverS","Normal", fontSize=16, leading=22, alignment=TA_CENTER, textColor=DARK)
    ))
    story.append(SP(6))
    story.append(HRFlowable(width="60%", thickness=2, color=ACCENT, hAlign="CENTER", spaceAfter=6))
    story.append(SP(4))
    story.append(Paragraph(
        "From internal tool → market-ready construction ERP",
        mk("CoverTag","Normal", fontSize=12, leading=16, alignment=TA_CENTER, textColor=MID)
    ))
    story.append(SP(14))

    # Vision statement box
    vision_data = [[
        P('<b>"One system for running a construction company —<br/>from site costs to payroll."</b>',
          mk("VT","Normal", fontSize=12, leading=18, alignment=TA_CENTER, textColor=NAVY,
             fontName="Helvetica-Bold"))
    ]]
    vision_tbl = Table(vision_data, colWidths=[CW])
    vision_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HexColor("#EFF6FF")),
        ("BOX",        (0,0), (-1,-1), 1.5, BLUE),
        ("LEFTPADDING",(0,0), (-1,-1), 16),
        ("RIGHTPADDING",(0,0),(-1,-1), 16),
        ("TOPPADDING", (0,0), (-1,-1), 16),
        ("BOTTOMPADDING",(0,0),(-1,-1), 16),
    ]))
    story.append(vision_tbl)
    story.append(SP(14))

    # Summary cards
    cards = [
        ("🎯", "Target Market", "Construction & project-based\ncompanies in Indonesia"),
        ("💼", "Business Model", "On-premise license\n+ Implementation fee"),
        ("📅", "Timeline", "6 months to\nfirst external sale"),
        ("💰", "Revenue Target", "Rp 600 juta Year 1\n(3 clients)"),
    ]
    card_data = [[
        Table([[
            P(f'<b>{icon}</b>', mk("CI","Normal",fontSize=18,alignment=TA_CENTER,leading=22)),
            P(f'<b>{title}</b>', mk("CT","Normal",fontSize=9,alignment=TA_CENTER,leading=12,
                                    textColor=NAVY,fontName="Helvetica-Bold")),
            P(desc.replace("\n","<br/>"), mk("CD","Normal",fontSize=8,alignment=TA_CENTER,
                                              leading=11,textColor=DARK)),
        ]], colWidths=[(CW/4)-4])
        for icon, title, desc in cards
    ]]
    card_tbl = Table(card_data, colWidths=[(CW/4)-2]*4, hAlign="CENTER")
    card_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT),
        ("BOX",        (0,0), (0,-1), 0.5, LIGHT2),
        ("BOX",        (1,0), (1,-1), 0.5, LIGHT2),
        ("BOX",        (2,0), (2,-1), 0.5, LIGHT2),
        ("BOX",        (3,0), (3,-1), 0.5, LIGHT2),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("RIGHTPADDING",(0,0),(-1,-1), 6),
        ("ROUNDEDCORNERS", (0,0), (-1,-1), 4),
    ]))
    story.append(card_tbl)
    story.append(SP(16))
    story.append(Paragraph("Prepared: May 2026 — CONFIDENTIAL",
        mk("CF","Normal",fontSize=8,alignment=TA_CENTER,textColor=MID)))
    story.append(PageBreak())
    return story


# ── Table of Contents ──────────────────────────────────────────────────────────
def toc():
    story = [P("<b>TABLE OF CONTENTS</b>", h1), HR(), SP(2)]
    items = [
        ("1", "Current ERP State — Readiness Assessment", "3"),
        ("2", "What Needs to Be Built", "4"),
        ("  2.1", "Productization Layer", "4"),
        ("  2.2", "HRIS H1 — Employee & Organisation", "5"),
        ("  2.3", "HRIS H2 — Attendance & Leave", "6"),
        ("  2.4", "HRIS H3 — Payroll", "7"),
        ("  2.5", "HRIS H4 — Recruitment & Onboarding", "8"),
        ("3", "Six-Month Execution Timeline", "9"),
        ("4", "Technical Debt to Clear", "10"),
        ("5", "Commercial Packaging & Pricing", "11"),
        ("6", "Competitive Positioning", "12"),
        ("7", "Revenue Projections", "12"),
        ("8", "Risks & Mitigations", "13"),
        ("9", "Immediate Next Steps", "14"),
    ]
    toc_rows = [[P(f"<b>{n}</b>", cell), P(title, cell), P(pg, mk("PG","Normal",fontSize=8.5,alignment=TA_RIGHT,textColor=MID))]
                for n, title, pg in items]
    toc_tbl = Table(toc_rows, colWidths=[14*mm, CW-30*mm, 14*mm])
    toc_tbl.setStyle(TableStyle([
        ("LINEBELOW", (0,0), (-1,-1), 0.3, LIGHT2),
        ("TOPPADDING",(0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",(0,0),(0,-1), 0),
        ("VALIGN",   (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(toc_tbl)
    story.append(PageBreak())
    return story


# ── Section 1: ERP Readiness ───────────────────────────────────────────────────
def section_readiness():
    story = [P("<b>1. Current ERP State — Readiness Assessment</b>", h1), HR()]
    story.append(P(
        "The GPA Cost Control ERP V5.0 was built and battle-tested at PT Garuda. "
        "The ERP core is ~90% production-ready. HRIS is the major greenfield. "
        "Below is the current readiness per module.", body
    ))
    story.append(SP(3))

    modules = [
        ("Auth & RBAC",        100, "JWT, 7 roles, menu permissions, full"),
        ("Action Center",       95, "Role-based queues, batch ops"),
        ("Project Command",     95, "CRUD, import Excel, budget bar, health dots"),
        ("Revenue (AR)",        95, "Full lifecycle, confirmed AR drives budget ceiling"),
        ("Spending / Expenses", 95, "Full workflow, receipt upload, voucher print"),
        ("Petty Cash",          90, "Batch entry, auto-creates draft expenses"),
        ("Inventory & Assets",  90, "Full CRUD + transaction log"),
        ("Legal & Proposals",   90, "Full workflow, MD signature upload"),
        ("Notifications",       85, "In-app bell with polling; email not yet"),
        ("Settings",            90, "Profile, password, user management done"),
        ("Dashboard",           85, "Functional; needs unified API endpoint"),
        ("Reports",             75, "Data renders; Excel export button not wired"),
        ("HRIS — All modules",   0, "Not started — primary build target"),
    ]

    def bar_color(pct):
        if pct == 0:   return RED
        if pct >= 90:  return GREEN
        if pct >= 75:  return BLUE
        return ORANGE

    rows = []
    for name, pct, note in modules:
        filled = int(pct / 5)  # out of 20 segments
        empty  = 20 - filled
        bar_char = "█" * filled + "░" * empty
        color = bar_color(pct)
        rows.append([
            P(f"<b>{name}</b>", cell),
            P(f'<font color="#{color.hexval()[2:]}">{bar_char}</font>  <b>{pct}%</b>',
              mk("Bar","Normal",fontSize=7.5,leading=11,fontName="Courier")),
            P(note, smg),
        ])

    tbl = Table(rows, colWidths=[46*mm, 52*mm, CW-100*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0),  LIGHT),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",  (0,0), (-1,-1), 0.3, LIGHT2),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("VALIGN",    (0,0), (-1,-1), "MIDDLE"),
        # Last row (HRIS) highlighted
        ("BACKGROUND", (0,12), (-1,12), HexColor("#FEF2F2")),
        ("TEXTCOLOR",  (0,12), (0,12), RED),
    ]))
    story.append(tbl)
    story.append(SP(4))
    story.append(P(
        "<b>Key insight:</b> The ERP engine is proven. The commercialization investment is "
        "primarily in HRIS (~42 developer-days) and the productization scaffolding (~9 days) "
        "that allows clean installation at a new client's server.", body
    ))
    story.append(PageBreak())
    return story


# ── Section 2A: Productization ─────────────────────────────────────────────────
def section_productization():
    story = [P("<b>2. What Needs to Be Built</b>", h1), HR()]
    story.append(P("<b>2.1  Productization Layer</b>", h2))
    story.append(P(
        "These are not features — they are the scaffolding required to ship the product "
        "to a second client cleanly. Without this layer, every new install requires "
        "manual database patches and hardcoded config.", body
    ))
    story.append(SP(2))

    items = [
        ("Company Config Table", "1 day", BLUE,
         "Company name, logo, NPWP, address — used in all PDF headers and payslips. "
         "Each client customizes this via the admin panel after install."),
        ("Alembic Migrations", "2 days", RED,
         "Replace the ad-hoc _ensure_incremental_schema() function with proper versioned "
         "Alembic migrations. Required before any second install — otherwise schema drift "
         "is unmanageable."),
        ("Installer Script", "1 day", GREEN,
         "setup.bat / setup.py: creates virtualenv, installs dependencies, runs migrations, "
         "seeds roles and menus. One command turns a blank server into a running system."),
        ("First-Run Setup Wizard", "1 day", TEAL,
         "On first launch with empty DB, redirect to /setup. Admin fills in company profile "
         "and creates the first SUPER_ADMIN account. No manual DB seeding needed."),
        ("Backup / Restore CLI", "1 day", PURPLE,
         "python manage.py backup → pg_dump to timestamped archive. "
         "python manage.py restore → safely restores. Critical for on-premise support contracts."),
        ("Environment Config Wizard", "0.5 day", ORANGE,
         ".env generator script: DB URL, SECRET_KEY, port, company slug. "
         "Forces required secrets — no more hardcoded fallbacks."),
        ("White-Label PDF Templates", "1 day", BLUE,
         "All generated PDFs (expense voucher, payslips, legal docs) pull company name "
         "and logo from the config table instead of hardcoded strings."),
        ("Excel Export — Reports", "1 day", GREEN,
         "Wire the existing Export button in the Reports page. "
         "Currently renders data but has no onClick handler. Blocks every sales demo."),
    ]

    rows = [
        [P(f"<b>{t}</b>", cellb), P(effort, mk("Eff","Normal",fontSize=8.5,textColor=WHITE,
                                                  alignment=TA_CENTER,fontName="Helvetica-Bold",
                                                  leading=12)), P(desc, cell)]
        for t, effort, color, desc in items
    ]
    col_colors = [BLUE, RED, GREEN, TEAL, PURPLE, ORANGE, BLUE, GREEN]

    tbl = Table(rows, colWidths=[48*mm, 16*mm, CW-66*mm])
    style = [
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",  (0,0), (-1,-1), 0.3, LIGHT2),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("VALIGN",    (0,0), (-1,-1), "TOP"),
    ]
    for i, (_, _, color, _) in enumerate(items):
        style.append(("BACKGROUND", (1,i), (1,i), color))
        style.append(("TEXTCOLOR",  (1,i), (1,i), WHITE))
    tbl.setStyle(TableStyle(style))
    story.append(tbl)
    story.append(SP(3))

    # Total effort callout
    effort_box = [[P("<b>Total Productization: ~9 developer-days</b>",
                     mk("EB","Normal",fontSize=10,textColor=NAVY,fontName="Helvetica-Bold",
                        alignment=TA_CENTER,leading=14)),
                   P("Complete in Month 1 alongside Garuda stabilization.",
                     mk("ES","Normal",fontSize=8.5,textColor=DARK,alignment=TA_CENTER,leading=12))]]
    eb_tbl = Table(effort_box, colWidths=[CW])
    eb_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), HexColor("#F0FDF4")),
        ("BOX",       (0,0),(-1,-1), 1.5, GREEN),
        ("TOPPADDING",(0,0),(-1,-1), 10),
        ("BOTTOMPADDING",(0,0),(-1,-1), 10),
    ]))
    story.append(eb_tbl)
    story.append(PageBreak())
    return story


# ── Section 2B: HRIS modules helper ───────────────────────────────────────────
def hris_module(story, number, title, subtitle, color, effort_be, effort_fe, features, integration_note):
    story.append(P(f"<b>{number}  {title}</b>", h2))
    story.append(P(subtitle, body))
    story.append(SP(2))

    # Effort badges
    badge_data = [[
        P(f"Backend: {effort_be} days",
          mk("BD","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",
             alignment=TA_CENTER,leading=12)),
        P(f"Frontend: {effort_fe} days",
          mk("FD","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",
             alignment=TA_CENTER,leading=12)),
        P(f"Total: {effort_be+effort_fe} days",
          mk("TD","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",
             alignment=TA_CENTER,leading=12)),
    ]]
    badge_tbl = Table(badge_data, colWidths=[CW/3-3, CW/3-3, CW/3-3], hAlign="LEFT")
    badge_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1), color),
        ("BACKGROUND",(1,0),(1,-1), DARK),
        ("BACKGROUND",(2,0),(2,-1), NAVY),
        ("TOPPADDING",(0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
        ("RIGHTPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(badge_tbl)
    story.append(SP(3))

    # Feature table
    feat_rows = [[P(f, cell)] for f in features]
    feat_tbl = Table(feat_rows, colWidths=[CW])
    feat_tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBEFORE",(0,0),(0,-1), 3, color),
    ]))
    story.append(feat_tbl)
    story.append(SP(3))

    # Integration note
    int_data = [[P(f"<b>Integration with ERP:</b> {integration_note}", sm)]]
    int_tbl = Table(int_data, colWidths=[CW])
    int_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), HexColor("#FFF7ED")),
        ("BOX",       (0,0),(-1,-1), 1, ACCENT),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(int_tbl)
    story.append(PageBreak())


def section_hris():
    story = []

    # H1 Employee
    story.append(P("<b>2.2  HRIS H1 — Employee & Organisation</b>", h2))
    story.append(P(
        "The foundation of HRIS. Every other module (payroll, attendance, recruitment) "
        "depends on having accurate employee master data.", body
    ))
    story.append(SP(2))

    badge_data = [[
        P("Backend: 5 days", mk("BD","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Frontend: 5 days", mk("FD","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Total: 10 days", mk("TD","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
    ]]
    b = Table(badge_data, colWidths=[CW/3-3, CW/3-3, CW/3-3])
    b.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1), TEAL),
        ("BACKGROUND",(1,0),(1,-1), DARK),
        ("BACKGROUND",(2,0),(2,-1), NAVY),
        ("TOPPADDING",(0,0),(-1,-1), 6), ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(b)
    story.append(SP(3))

    features_h1 = [
        "Employee master record: NIK, NPWP, BPJS TK no., BPJS Kesehatan no., bank account details",
        "Departments & job grades — hierarchical org structure, links to approval matrix",
        "Employment types: Permanent (PKWT), Contract (PKWTT), Outsource",
        "Org chart: visual tree view, exportable to PDF",
        "Document store: upload KTP, SKCK, ijazah, BPJS cards per employee",
        "Link to ERP user: employee.user_id → users.id (optional — not all employees log in to the system)",
        "Employment history: start date, promotion dates, termination with reason",
    ]
    fr = [[P(f, cell)] for f in features_h1]
    ft = Table(fr, colWidths=[CW])
    ft.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBEFORE",(0,0),(0,-1), 3, TEAL),
    ]))
    story.append(ft)
    story.append(SP(3))
    int_data = [[P("<b>Integration with ERP:</b> Employee records link to the existing Users table for login. "
                   "Department hierarchy informs the approval matrix — department heads can be auto-assigned "
                   "as approvers for their team's expenses.", sm)]]
    it = Table(int_data, colWidths=[CW])
    it.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1), HexColor("#FFF7ED")),
        ("BOX",(0,0),(-1,-1), 1, ACCENT),("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 8), ("BOTTOMPADDING",(0,0),(-1,-1), 8)]))
    story.append(it)
    story.append(PageBreak())

    # H2 Attendance
    story.append(P("<b>2.3  HRIS H2 — Attendance & Leave</b>", h2))
    story.append(P(
        "Daily attendance tracking and leave management. Feeds directly into payroll "
        "calculation — absent days reduce base pay, overtime adds to it.", body
    ))
    story.append(SP(2))

    badge_data2 = [[
        P("Backend: 5 days", mk("BD2","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Frontend: 5 days", mk("FD2","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Total: 10 days", mk("TD2","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
    ]]
    b2 = Table(badge_data2, colWidths=[CW/3-3, CW/3-3, CW/3-3])
    b2.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1), PURPLE),
        ("BACKGROUND",(1,0),(1,-1), DARK),
        ("BACKGROUND",(2,0),(2,-1), NAVY),
        ("TOPPADDING",(0,0),(-1,-1), 6), ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(b2)
    story.append(SP(3))

    features_h2 = [
        "Daily attendance: manual entry or CSV import from fingerprint / face recognition machine",
        "Overtime recording: regular hours, weekend rate (1.5×), holiday rate (2×) per Permenaker 2023",
        "Leave types: Annual (cuti tahunan 12 days/yr), Sick, Personal, Maternity/Paternity, Unpaid",
        "Leave balance engine: auto-accrual, configurable carry-over policy per company",
        "Approval flow: Staff → direct Manager → HR — reuses the existing ERP approval pattern",
        "Calendar UI: monthly view per employee + team calendar for managers",
        "Absensi rekap: monthly summary exportable to Excel for payroll input",
    ]
    fr2 = [[P(f, cell)] for f in features_h2]
    ft2 = Table(fr2, colWidths=[CW])
    ft2.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBEFORE",(0,0),(0,-1), 3, PURPLE),
    ]))
    story.append(ft2)
    story.append(SP(3))
    int_data2 = [[P("<b>Integration with ERP:</b> Attendance data feeds into the Payroll module (H3). "
                    "Overtime hours and absent days are automatically pulled into the monthly payroll run, "
                    "eliminating manual reconciliation between HR and Finance.", sm)]]
    it2 = Table(int_data2, colWidths=[CW])
    it2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1), HexColor("#FFF7ED")),
        ("BOX",(0,0),(-1,-1), 1, ACCENT),("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 8), ("BOTTOMPADDING",(0,0),(-1,-1), 8)]))
    story.append(it2)
    story.append(PageBreak())

    # H3 Payroll
    story.append(P("<b>2.4  HRIS H3 — Payroll</b>", h2))
    story.append(P(
        "The highest-value HRIS module. Indonesian payroll is complex — PPh 21, BPJS TK, "
        "BPJS Kesehatan, THR, and bank disbursement. Getting this right is the main technical "
        "risk and the main reason clients will pay for the system.", body
    ))
    story.append(SP(2))

    badge_data3 = [[
        P("Backend: 8 days", mk("BD3","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Frontend: 6 days", mk("FD3","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Total: 14 days", mk("TD3","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
    ]]
    b3 = Table(badge_data3, colWidths=[CW/3-3, CW/3-3, CW/3-3])
    b3.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1), ORANGE),
        ("BACKGROUND",(1,0),(1,-1), DARK),
        ("BACKGROUND",(2,0),(2,-1), NAVY),
        ("TOPPADDING",(0,0),(-1,-1), 6), ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(b3)
    story.append(SP(3))

    features_h3 = [
        "Salary component engine: Basic, transport, meal, positional, project allowances — fully configurable",
        "BPJS Ketenagakerjaan: JKK + JKM (employer), JHT (2% employer + 3.7% employee), JP (2% + 1%)",
        "BPJS Kesehatan: 4% employer + 1% employee, capped at BPJS ceiling",
        "PPh 21: gross-up or netto method, PTKP per status (TK/0, K/0, K/1, K/2, K/3), progressive tariffs 2024",
        "THR: 1/12 x months of service x basic salary, auto-calculated at Lebaran period",
        "Payroll run workflow: Period lock → Calculate → Review → Approve → Post (with immutable audit log)",
        "Payslip PDF: company header, employee details, earnings/deductions breakdown, net pay in terbilang",
        "Bank disbursement CSV: BCA, Mandiri, BNI, BRI payroll file formats",
        "Payroll rekap: summary by department and cost centre — links directly to ERP cost centre codes",
    ]
    fr3 = [[P(f, cell)] for f in features_h3]
    ft3 = Table(fr3, colWidths=[CW])
    ft3.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBEFORE",(0,0),(0,-1), 3, ORANGE),
    ]))
    story.append(ft3)
    story.append(SP(3))

    # Risk note
    risk_data = [[P(
        "<b>Critical Risk:</b> PPh 21 calculations must be validated by a certified accountant (Akuntan Publik) "
        "before shipping to any client. A miscalculation creates tax liability for the client. "
        "Budget 2-3 days for accountant review in Month 5.", sm)]]
    rt = Table(risk_data, colWidths=[CW])
    rt.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1), HexColor("#FEF2F2")),
        ("BOX",(0,0),(-1,-1), 1.5, RED),("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 8), ("BOTTOMPADDING",(0,0),(-1,-1), 8)]))
    story.append(rt)
    story.append(SP(3))
    int_data3 = [[P("<b>Integration with ERP:</b> Payroll cost posts to ERP expenses by cost centre. "
                    "Salary disbursement = an approved Expense. Finance sees total labour cost "
                    "broken down by project/department without double-entry.", sm)]]
    it3 = Table(int_data3, colWidths=[CW])
    it3.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1), HexColor("#FFF7ED")),
        ("BOX",(0,0),(-1,-1), 1, ACCENT),("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 8), ("BOTTOMPADDING",(0,0),(-1,-1), 8)]))
    story.append(it3)
    story.append(PageBreak())

    # H4 Recruitment
    story.append(P("<b>2.5  HRIS H4 — Recruitment & Onboarding</b>", h2))
    story.append(P(
        "Lowest technical priority — but rounds out the 'one system' sales pitch. "
        "Recruitment is often what HR managers ask about first.", body
    ))
    story.append(SP(2))

    badge_data4 = [[
        P("Backend: 4 days", mk("BD4","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Frontend: 4 days", mk("FD4","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
        P("Total: 8 days", mk("TD4","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
    ]]
    b4 = Table(badge_data4, colWidths=[CW/3-3, CW/3-3, CW/3-3])
    b4.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,-1), GREEN),
        ("BACKGROUND",(1,0),(1,-1), DARK),
        ("BACKGROUND",(2,0),(2,-1), NAVY),
        ("TOPPADDING",(0,0),(-1,-1), 6), ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(b4)
    story.append(SP(3))

    features_h4 = [
        "Job postings: internal-only in v1 (no job board API integration)",
        "Applicant tracking: Received → Screening → Interview → Offer → Hired/Rejected",
        "Interview scheduling: date, interviewer assignment, notes and scoring",
        "Offer letter: auto-generated PDF with salary, position, start date",
        "Onboarding checklist: tasks assigned to HR and new hire, completion tracking",
        "Auto-create employee: on 'Hired' status, pre-fills Employee master from applicant record",
    ]
    fr4 = [[P(f, cell)] for f in features_h4]
    ft4 = Table(fr4, colWidths=[CW])
    ft4.setStyle(TableStyle([
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 5), ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LINEBEFORE",(0,0),(0,-1), 3, GREEN),
    ]))
    story.append(ft4)
    story.append(SP(3))
    int_data4 = [[P("<b>Integration with ERP:</b> New hire's Employee record auto-creates a login User account "
                    "and assigns the correct role. Onboarding tasks can include 'Complete expense training' "
                    "and 'Submit first petty cash request' linked to the ERP workflows.", sm)]]
    it4 = Table(int_data4, colWidths=[CW])
    it4.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1), HexColor("#FFF7ED")),
        ("BOX",(0,0),(-1,-1), 1, ACCENT),("LEFTPADDING",(0,0),(-1,-1), 10),
        ("TOPPADDING",(0,0),(-1,-1), 8), ("BOTTOMPADDING",(0,0),(-1,-1), 8)]))
    story.append(it4)
    story.append(PageBreak())
    return story


# ── Section 3: Timeline Gantt ──────────────────────────────────────────────────
def section_timeline():
    story = [P("<b>3. Six-Month Execution Timeline</b>", h1), HR()]
    story.append(P(
        "Total build effort: ~51 developer-days across 6 months. "
        "Month 1 runs in parallel with Garuda stabilization.", body
    ))
    story.append(SP(4))

    months = ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5", "Month 6"]
    phases = [
        ("ERP Stabilization",    [1,0,0,0,0,0], BLUE),
        ("Productization Layer", [1,0,0,0,0,0], TEAL),
        ("Excel Export + Fixes", [1,0,0,0,0,0], GREEN),
        ("Alembic Migrations",   [1,0,0,0,0,0], PURPLE),
        ("HRIS H1: Employee",    [0,1,0,0,0,0], TEAL),
        ("HRIS H2: Attendance",  [0,0,1,0,0,0], PURPLE),
        ("HRIS H3: Payroll Pt1", [0,0,0,1,0,0], ORANGE),
        ("HRIS H3: Payroll Pt2", [0,0,0,0,1,0], ORANGE),
        ("HRIS H4: Recruitment", [0,0,0,0,1,0], GREEN),
        ("Documentation",        [0,0,0,0,0,1], BLUE),
        ("Pilot Client Onboard", [0,0,0,0,0,1], ACCENT),
    ]

    BAR_W = (CW - 44*mm) / 6

    header_row = [P("<b>Phase</b>", cellb)] + [P(f"<b>{m}</b>", mk("MH","Normal",fontSize=8,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=11)) for m in months]
    rows = [header_row]

    for phase, active, color in phases:
        row = [P(phase, cell)]
        for a in active:
            if a:
                row.append(P("", mk("Fill","Normal",fontSize=1,leading=1)))
            else:
                row.append(P("", mk("Empty","Normal",fontSize=1,leading=1)))
        rows.append(row)

    gantt_tbl = Table(rows, colWidths=[44*mm] + [BAR_W]*6)
    style = [
        ("BACKGROUND", (0,0),  (-1,0),  NAVY),
        ("TEXTCOLOR",  (0,0),  (-1,0),  WHITE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",  (0,0), (-1,-1), 0.3, LIGHT2),
        ("TOPPADDING", (0,0), (-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("VALIGN",    (0,0), (-1,-1), "MIDDLE"),
    ]
    for row_i, (_, active, color) in enumerate(phases, start=1):
        for col_i, a in enumerate(active, start=1):
            if a:
                style.append(("BACKGROUND", (col_i, row_i), (col_i, row_i), color))
    gantt_tbl.setStyle(TableStyle(style))
    story.append(gantt_tbl)
    story.append(SP(5))

    # Milestone summary
    story.append(P("<b>Key Milestones</b>", h3))
    milestones = [
        ("End of Month 1", GREEN,  "Garuda fully stable. Clean installer script. Alembic migrations running. Excel export live."),
        ("End of Month 2", TEAL,   "Employee master + org chart complete. HR department can manage employee records."),
        ("End of Month 3", PURPLE, "Attendance and leave management live. First integration test with payroll engine."),
        ("End of Month 4", ORANGE, "Payroll calculation engine (BPJS + PPh 21) complete. Accountant review begins."),
        ("End of Month 5", ORANGE, "Full payslip PDF + bank CSV. Recruitment module complete. Accountant sign-off."),
        ("End of Month 6", ACCENT, "Documentation done. Demo environment ready. First external client contract signed."),
    ]
    for date, color, desc in milestones:
        ms_row = [[
            P(f"<b>{date}</b>", mk("MD","Normal",fontSize=8.5,textColor=WHITE,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
            P(desc, cell),
        ]]
        ms_tbl = Table(ms_row, colWidths=[30*mm, CW-32*mm])
        ms_tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,-1), color),
            ("TOPPADDING",(0,0),(-1,-1), 7), ("BOTTOMPADDING",(0,0),(-1,-1), 7),
            ("LEFTPADDING",(0,0),(-1,-1), 8), ("RIGHTPADDING",(0,0),(-1,-1), 8),
            ("VALIGN",   (0,0),(-1,-1), "MIDDLE"),
            ("LINEBELOW",(0,0),(-1,-1), 0.5, LIGHT2),
        ]))
        story.append(ms_tbl)
    story.append(PageBreak())
    return story


# ── Section 4: Technical Debt ──────────────────────────────────────────────────
def section_tech_debt():
    story = [P("<b>4. Technical Debt to Clear Before Selling</b>", h1), HR()]
    story.append(P(
        "These items will not crash the app at Garuda — but they will create problems "
        "in a client's server room or create legal/security liability.", body
    ))
    story.append(SP(3))

    items = [
        ("MUST", RED,    "Replace _ensure_incremental_schema()",
         "ad-hoc ALTER TABLE is unmanageable across multiple client installs",
         "Alembic migrations (Month 1)"),
        ("MUST", RED,    "CORS locked to wildcard *",
         "any domain can make authenticated requests in production",
         "Lock to client's specific domain on install via .env"),
        ("MUST", RED,    "SECRET_KEY has hardcoded fallback",
         "predictable secret key in dev deployments",
         "Force env var — raise error if not set"),
        ("HIGH", ORANGE, "No rate limiting",
         "brute-force login attacks possible, no API abuse protection",
         "slowapi middleware: 5 req/s per IP on /auth/login"),
        ("HIGH", ORANGE, "No HTTP request logging",
         "no forensic trail if something goes wrong at client site",
         "structlog middleware: log method, path, status, duration"),
        ("HIGH", ORANGE, "Password reset flow missing",
         "admin must manually reset passwords in DB — not acceptable for clients",
         "SMTP-based reset link, 15-minute expiry token"),
        ("MEDIUM", BLUE, "No email notifications",
         "all notifications are in-app only — users miss events when not logged in",
         "SMTP integration with Mailpit for local dev, SMTP2Go for production"),
        ("LOW", MID,    "allow_credentials=False with wildcard CORS",
         "technically inconsistent — will break if cookies are ever introduced",
         "Align: either enable credentials with explicit origins, or keep both false/wildcard"),
    ]

    rows = []
    for severity, color, issue, risk, fix in items:
        rows.append([
            P(f"<b>{severity}</b>", mk("Sev","Normal",fontSize=8,textColor=WHITE,
                                        fontName="Helvetica-Bold",alignment=TA_CENTER,leading=11)),
            P(f"<b>{issue}</b><br/><font color='#94A3B8' size='7.5'>{risk}</font>", cell),
            P(fix, sm),
        ])

    tbl = Table(rows, colWidths=[16*mm, 80*mm, CW-98*mm])
    style = [
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("TOPPADDING",(0,0),(-1,-1), 7),
        ("BOTTOMPADDING",(0,0),(-1,-1), 7),
        ("LEFTPADDING",(0,0),(-1,-1), 6),
        ("VALIGN",(0,0),(-1,-1), "TOP"),
    ]
    for i, (_, color, _, _, _) in enumerate(items):
        style.append(("BACKGROUND",(0,i),(0,i), color))
    tbl.setStyle(TableStyle(style))
    story.append(tbl)
    story.append(PageBreak())
    return story


# ── Section 5: Pricing ─────────────────────────────────────────────────────────
def section_pricing():
    story = [P("<b>5. Commercial Packaging & Pricing</b>", h1), HR()]
    story.append(P(
        "On-premise license model. Client owns the software and hosts it on their own server. "
        "Revenue comes from the license fee, implementation project, and annual support contract.", body
    ))
    story.append(SP(4))

    # Tier cards
    tiers = [
        ("STARTER", BLUE,   "ERP Only",
         "Rp 75 juta", "Rp 30 juta", "Rp 15 juta/thn",
         ["Project Command", "Spending & Expenses", "Petty Cash",
          "Revenue (AR)", "Inventory & Assets", "Legal & Proposals",
          "Reports & Audit Log"]),
        ("PROFESSIONAL", TEAL, "ERP + HRIS Dasar",
         "Rp 150 juta", "Rp 50 juta", "Rp 30 juta/thn",
         ["Semua modul Starter", "HRIS H1: Employee & Org",
          "HRIS H2: Attendance & Leave", "Email notifications",
          "Backup/restore included"]),
        ("ENTERPRISE", NAVY, "Full ERP + Full HRIS",
         "Rp 250 juta", "Rp 75 juta", "Rp 50 juta/thn",
         ["Semua modul Professional", "HRIS H3: Payroll",
          "HRIS H4: Recruitment", "Customization 8 hours included",
          "Priority support SLA 24 jam"]),
    ]

    for tier_name, color, subtitle, license_fee, impl_fee, support_fee, features in tiers:
        tier_data = [
            [P(f"<b>{tier_name}</b>", mk("TN","Normal",fontSize=13,textColor=WHITE,
                                          fontName="Helvetica-Bold",alignment=TA_CENTER,leading=16)),
             P(subtitle, mk("TS","Normal",fontSize=9,textColor=WHITE,
                             alignment=TA_CENTER,leading=12))],
            [P(f"<b>Lisensi: {license_fee}</b>",
               mk("TF","Normal",fontSize=10,textColor=NAVY,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=14)),
             P(f"Implementasi: {impl_fee}  |  Support: {support_fee}",
               mk("TS2","Normal",fontSize=8,textColor=DARK,alignment=TA_CENTER,leading=12))],
            [P("<br/>".join(f"• {f}" for f in features),
               mk("TL","Normal",fontSize=8.5,textColor=DARK,leading=13))],
        ]
        tier_tbl = Table(tier_data, colWidths=[CW])
        tier_tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0), color),
            ("BACKGROUND",(0,1),(-1,1), LIGHT),
            ("BACKGROUND",(0,2),(-1,2), WHITE),
            ("BOX",       (0,0),(-1,-1), 1, LIGHT2),
            ("TOPPADDING",(0,0),(-1,-1), 8),
            ("BOTTOMPADDING",(0,0),(-1,-1), 8),
            ("LEFTPADDING",(0,0),(-1,-1), 12),
            ("RIGHTPADDING",(0,0),(-1,-1), 12),
            ("SPAN",      (0,0),(-1,0)),
            ("SPAN",      (0,2),(-1,2)),
        ]))
        story.append(tier_tbl)
        story.append(SP(3))

    story.append(SP(2))
    story.append(P("<i>Customization di luar paket: Rp 2–3 juta/jam. "
                   "Training tambahan: Rp 5 juta/hari on-site.</i>", smg))
    story.append(PageBreak())
    return story


# ── Section 6+7: Competition + Revenue ────────────────────────────────────────
def section_competition_revenue():
    story = [P("<b>6. Competitive Positioning</b>", h1), HR()]

    comp_rows = [
        [P("<b>Competitor</b>", cellb), P("<b>Weakness</b>", cellb), P("<b>Our Edge</b>", cellb)],
        [P("SAP Business One", cell),
         P("Rp 500 juta+ license, 6-month implementation, requires certified SAP consultant", cell),
         P("10x cheaper, 4-week implementation, no consultant required", cell)],
        [P("Odoo", cell),
         P("Too generic — HRIS is shallow, construction modules are third-party add-ons", cell),
         P("Construction-specific: WBS, cost codes, AR drives budget ceiling", cell)],
        [P("ACCURATE / Krishand", cell),
         P("Desktop-only, no approval workflows, no mobile, no project cost tracking", cell),
         P("Modern web, mobile-ready, full 5-step approval matrix, immutable audit log", cell)],
        [P("Spreadsheets + manual", cell),
         P("No audit trail, errors not caught, no role separation, version conflicts", cell),
         P("Full lifecycle with hard-lock, role-based access, real-time dashboard", cell)],
    ]
    comp_tbl = Table(comp_rows, colWidths=[36*mm, 70*mm, CW-108*mm])
    comp_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), NAVY),
        ("TEXTCOLOR", (0,0),(-1,0), WHITE),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, HexColor("#FAFBFC")]),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("TOPPADDING",(0,0),(-1,-1), 6), ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
        ("VALIGN",(0,0),(-1,-1), "TOP"),
        ("BACKGROUND",(2,1),(-1,-1), HexColor("#F0FDF4")),
    ]))
    story.append(comp_tbl)
    story.append(PageBreak())

    story.append(P("<b>7. Revenue Projections</b>", h1))
    story.append(HR())
    story.append(P(
        "Conservative projections based on on-premise sales cycle (3–4 months close time). "
        "Year 1 target: 3 clients. Support contracts compound from Year 2.", body
    ))
    story.append(SP(4))

    rev_rows = [
        [P("<b></b>", cellb), P("<b>Year 1</b>", cellb), P("<b>Year 2</b>", cellb), P("<b>Year 3</b>", cellb)],
        [P("New clients", cell), P("3", ctr), P("5", ctr), P("8", ctr)],
        [P("Avg license revenue / client", cell), P("Rp 175 juta", ctr), P("Rp 200 juta", ctr), P("Rp 225 juta", ctr)],
        [P("Avg implementation / client", cell), P("Rp 55 juta", ctr), P("Rp 60 juta", ctr), P("Rp 65 juta", ctr)],
        [P("New client revenue", cell), P("Rp 690 juta", ctr), P("Rp 1,3 M", ctr), P("Rp 2,3 M", ctr)],
        [P("Annual support (existing clients)", cell), P("—", ctr), P("Rp 90 juta", ctr), P("Rp 240 juta", ctr)],
        [P("<b>Total Revenue</b>", cellb), P("<b>Rp 690 juta</b>", mk("RevH","Normal",fontSize=9,textColor=GREEN,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
         P("<b>Rp 1,4 M</b>", mk("RevH2","Normal",fontSize=9,textColor=GREEN,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12)),
         P("<b>Rp 2,5 M</b>", mk("RevH3","Normal",fontSize=9,textColor=GREEN,fontName="Helvetica-Bold",alignment=TA_CENTER,leading=12))],
    ]
    rev_tbl = Table(rev_rows, colWidths=[70*mm, (CW-70*mm)/3, (CW-70*mm)/3, (CW-70*mm)/3])
    rev_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0), NAVY),
        ("TEXTCOLOR", (0,0),(-1,0), WHITE),
        ("ROWBACKGROUNDS",(0,1),(-1,-2), [WHITE, HexColor("#FAFBFC")]),
        ("BACKGROUND",(0,-1),(-1,-1), HexColor("#F0FDF4")),
        ("LINEBELOW",(0,0),(-1,-1), 0.3, LIGHT2),
        ("TOPPADDING",(0,0),(-1,-1), 6), ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("LEFTPADDING",(0,0),(-1,-1), 8),
        ("VALIGN",(0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(rev_tbl)
    story.append(SP(4))
    story.append(P(
        "<b>Breakeven:</b> 2 clients at Professional tier fully cover the development investment. "
        "Client 3 onward is net profit. Annual support contracts become material revenue in Year 2.", body
    ))
    story.append(PageBreak())
    return story


# ── Section 8: Risks ───────────────────────────────────────────────────────────
def section_risks():
    story = [P("<b>8. Risks & Mitigations</b>", h1), HR()]
    story.append(SP(2))

    risks = [
        ("HIGH", RED,
         "PPh 21 calculation error",
         "Incorrect tax creates liability for client. A tax dispute costs more than the license fee.",
         "Engage a certified accountant (Brevet A/B) to validate the tax engine before shipping. "
         "Add a disclaimer in the license that client is responsible for reviewing output."),
        ("HIGH", RED,
         "Garuda as sole reference",
         "Potential clients want to see another live installation. One reference is thin.",
         "Target a second friendly company (close relationship, discounted deal) as reference client "
         "before the first commercial sale. Offer a 'Beta Partner' deal at cost."),
        ("MEDIUM", ORANGE,
         "Construction market is small",
         "Indonesia has ~3,000 mid-size construction companies. Niche market.",
         "Start with construction, then expand to O&M, EPC, mining. The cost control "
         "module works for any project-based business. HRIS is universal."),
        ("MEDIUM", ORANGE,
         "Payroll complexity underestimated",
         "Indonesian payroll has many edge cases (TK0/K3 PTKP, multi-job, bonus treatment).",
         "Build a comprehensive test suite with 50+ payroll scenarios covering all PTKP "
         "statuses, overtime combinations, and THR edge cases before release."),
        ("LOW", BLUE,
         "Client data security on-premise",
         "If client's server is compromised, we may be blamed.",
         "License agreement clearly states client is responsible for server security. "
         "Provide a hardening guide in the admin documentation."),
        ("LOW", BLUE,
         "Product name tied to Garuda",
         "Clients may not want software named after a competitor's company.",
         "Rebrand before Month 6 docs are printed. All config uses COMPANY_NAME env var "
         "— renaming is a one-line change in the codebase."),
    ]

    for severity, color, risk_title, impact, mitigation in risks:
        r_data = [
            [P(f"<b>{severity}</b>",
               mk("RS","Normal",fontSize=8,textColor=WHITE,fontName="Helvetica-Bold",
                  alignment=TA_CENTER,leading=11)),
             P(f"<b>{risk_title}</b>", cellb),
             P(""),
            ],
            [P(""),
             P(f"<b>Impact:</b> {impact}", sm),
             P(f"<b>Mitigation:</b> {mitigation}", sm),
            ],
        ]
        r_tbl = Table(r_data, colWidths=[18*mm, (CW-20*mm)/2, (CW-20*mm)/2])
        r_tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,-1), color),
            ("BACKGROUND",(1,0),(-1,0), LIGHT),
            ("SPAN",      (0,0),(0,-1)),
            ("BOX",       (0,0),(-1,-1), 0.5, LIGHT2),
            ("TOPPADDING",(0,0),(-1,-1), 7),
            ("BOTTOMPADDING",(0,0),(-1,-1), 7),
            ("LEFTPADDING",(0,0),(-1,-1), 8),
            ("VALIGN",   (0,0),(-1,-1), "TOP"),
        ]))
        story.append(r_tbl)
        story.append(SP(2))
    story.append(PageBreak())
    return story


# ── Section 9: Next Steps ──────────────────────────────────────────────────────
def section_next_steps():
    story = [P("<b>9. Immediate Next Steps</b>", h1), HR()]
    story.append(P("Actions to take this week to start the commercialization clock.", body))
    story.append(SP(3))

    steps = [
        ("1", BLUE,   "Wire Excel Export on Reports",
         "1 day",
         "The Export button exists with no onClick handler. This is the first thing "
         "every potential client will try in a demo. Fix it this week."),
        ("2", RED,    "Set up Alembic",
         "2 days",
         "Run: alembic init alembic. Create the first migration from the current schema. "
         "This is foundational — everything else depends on it. Do not start HRIS "
         "development before Alembic is running."),
        ("3", TEAL,   "Build Company Config table",
         "1 day",
         "Model: CompanyConfig(name, logo_path, npwp, address, city, phone). "
         "Admin panel to edit. All PDF templates read from this table."),
        ("4", ORANGE, "Write the HRIS data model",
         "1 day (design only)",
         "Sketch the full ER diagram: Employee, Department, JobGrade, "
         "AttendanceRecord, LeaveRequest, LeaveBalance, PayrollRun, PayrollLine. "
         "Lock the relationships before writing any code."),
        ("5", PURPLE, "Identify Beta Partner client",
         "Ongoing",
         "Find one friendly construction company willing to be a Beta Partner — "
         "discounted or free in exchange for feedback and reference. Start conversations now "
         "so they're ready when the product is (Month 6)."),
        ("6", GREEN,  "Lock product name",
         "This week",
         "The name affects all documentation, domain, and branding. "
         "Decide before Month 6 — but note it now so it doesn't get forgotten."),
    ]

    for num, color, title, effort, desc in steps:
        s_data = [[
            P(f"<b>{num}</b>", mk("SN","Normal",fontSize=14,textColor=WHITE,fontName="Helvetica-Bold",
                                   alignment=TA_CENTER,leading=18)),
            P(f"<b>{title}</b><br/><font size='8' color='#94A3B8'>Effort: {effort}</font>", cellb),
            P(desc, cell),
        ]]
        s_tbl = Table(s_data, colWidths=[14*mm, 52*mm, CW-68*mm])
        s_tbl.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,-1), color),
            ("TOPPADDING",(0,0),(-1,-1), 10),
            ("BOTTOMPADDING",(0,0),(-1,-1), 10),
            ("LEFTPADDING",(0,0),(-1,-1), 8),
            ("VALIGN",(0,0),(-1,-1), "MIDDLE"),
            ("LINEBELOW",(0,0),(-1,-1), 0.5, LIGHT2),
        ]))
        story.append(s_tbl)
        story.append(SP(1.5))

    story.append(SP(6))
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT2))
    story.append(SP(4))
    story.append(Paragraph(
        "GPA Cost Control ERP V5.0 — Commercial Roadmap — Confidential",
        mk("Foot","Normal",fontSize=8,textColor=MID,alignment=TA_CENTER,leading=12)
    ))
    return story


# ── Build PDF ──────────────────────────────────────────────────────────────────
def build():
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    doc = SimpleDocTemplate(
        OUT,
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=22*mm, bottomMargin=16*mm,
        title="GPA ERP — Commercial Product Roadmap",
        author="GPA Technology",
    )

    story = []
    story += cover_page()
    story += toc()
    story += section_readiness()
    story += section_productization()
    story += section_hris()
    story += section_timeline()
    story += section_tech_debt()
    story += section_pricing()
    story += section_competition_revenue()
    story += section_risks()
    story += section_next_steps()

    doc.build(story, onFirstPage=page_template, onLaterPages=page_template)
    print(f"PDF saved: {OUT}")


if __name__ == "__main__":
    build()
