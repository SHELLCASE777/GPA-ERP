#!/usr/bin/env python3
"""GPA-ERP Documentation PDF Generator — renders Mermaid diagrams via mmdc."""

import subprocess, sys, os, re, tempfile, json, textwrap
from pathlib import Path

PYTHON  = Path(sys.executable)
VENV_PY = Path(r"C:\Users\theco\Codex\gpa-erp\.venv\Scripts\python.exe")
PY      = VENV_PY if VENV_PY.exists() else PYTHON

DOCS_DIR = Path(r"C:\Users\theco\Codex\gpa-erp\docs")
TEMP     = Path(tempfile.mkdtemp())
print(f"Temp dir: {TEMP}")

# ── Imports ──────────────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image as RLImage,
    Table, TableStyle, PageBreak, HRFlowable, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Colors ────────────────────────────────────────────────────────────────────
cPRIM  = colors.HexColor('#0f172a')
cACCT  = colors.HexColor('#1d4ed8')
cTEXT  = colors.HexColor('#334155')
cMUTE  = colors.HexColor('#64748b')
cBORD  = colors.HexColor('#cbd5e1')
cLIGHT = colors.HexColor('#eff6ff')
cHDBG  = colors.HexColor('#1e3a8a')
cHDFG  = colors.white
cROW1  = colors.HexColor('#f8fafc')
cROW2  = colors.white
cGREEN = colors.HexColor('#166534')
cRED   = colors.HexColor('#991b1b')

PW, PH = A4
MARGIN = 1.6 * cm
CW     = PW - 2 * MARGIN   # usable content width

# ── Styles ────────────────────────────────────────────────────────────────────
BASE = getSampleStyleSheet()

def S(name, parent='Normal', **kw):
    return ParagraphStyle(name, parent=BASE[parent], **kw)

STYLES = {
    'h1':      S('H1',  fontSize=22, fontName='Helvetica-Bold', textColor=cPRIM,
                 spaceBefore=0, spaceAfter=14, leading=28),
    'h2':      S('H2',  fontSize=15, fontName='Helvetica-Bold', textColor=cACCT,
                 spaceBefore=18, spaceAfter=8,  leading=22),
    'h3':      S('H3',  fontSize=11, fontName='Helvetica-Bold', textColor=cPRIM,
                 spaceBefore=12, spaceAfter=5,  leading=16),
    'body':    S('BD',  fontSize=10, fontName='Helvetica',      textColor=cTEXT,
                 spaceBefore=2,  spaceAfter=5,  leading=15),
    'bullet':  S('BU',  fontSize=10, fontName='Helvetica',      textColor=cTEXT,
                 spaceBefore=2,  spaceAfter=2,  leading=14,
                 leftIndent=14,  bulletIndent=4),
    'check':   S('CK',  fontSize=10, fontName='Helvetica',      textColor=cTEXT,
                 spaceBefore=2,  spaceAfter=2,  leading=14, leftIndent=14),
    'code':    S('CD',  fontSize=8,  fontName='Courier',        textColor=cPRIM,
                 spaceBefore=4,  spaceAfter=4,  leading=12, leftIndent=8,
                 backColor=cROW1),
    'caption': S('CAP', fontSize=8.5,fontName='Helvetica-Oblique', textColor=cMUTE,
                 spaceBefore=2, spaceAfter=10, leading=12, alignment=TA_CENTER),
    'tbl_hd':  S('TH',  fontSize=9,  fontName='Helvetica-Bold', textColor=cHDFG,
                 leading=12),
    'tbl_td':  S('TD',  fontSize=9,  fontName='Helvetica',      textColor=cTEXT,
                 leading=12),
    'tbl_td_c':S('TDC', fontSize=9,  fontName='Helvetica',      textColor=cTEXT,
                 leading=12, alignment=TA_CENTER),
}

# ── Mermaid renderer ──────────────────────────────────────────────────────────
MERMAID_CFG = {
    "theme": "default",
    "themeVariables": {
        "primaryColor":       "#dbeafe",
        "primaryTextColor":   "#1e3a8a",
        "primaryBorderColor": "#2563eb",
        "lineColor":          "#334155",
        "secondaryColor":     "#f1f5f9",
        "tertiaryColor":      "#f8fafc",
        "edgeLabelBackground":"#ffffff",
        "clusterBkg":         "#f8fafc",
        "clusterBorder":      "#e2e8f0",
        "fontFamily":         "Helvetica, Arial, sans-serif",
        "fontSize":           "14px",
    },
    "flowchart": {"curve": "basis", "padding": 20, "useMaxWidth": True},
    "sequence":  {"mirrorActors": False, "useMaxWidth": True},
    "er":        {"useMaxWidth": True},
}

cfg_path = TEMP / "mmdc_cfg.json"
cfg_path.write_text(json.dumps(MERMAID_CFG), encoding='utf-8')

_diag_counter = 0

def render_mermaid(code: str, label: str = "") -> Path | None:
    global _diag_counter
    _diag_counter += 1
    slug = re.sub(r'\W+', '_', label)[:30] if label else f"diag_{_diag_counter}"
    mmd = TEMP / f"{slug}.mmd"
    png = TEMP / f"{slug}.png"
    mmd.write_text(code, encoding='utf-8')

    cmd = [
        'npx', '-y', '@mermaid-js/mermaid-cli',
        '-i', str(mmd),
        '-o', str(png),
        '-c', str(cfg_path),
        '-b', 'white',
        '--width', '1200',
        '--height', '900',
    ]
    print(f"  Rendering: {slug} ...", end=' ', flush=True)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=180,
                           cwd=str(TEMP), shell=True)
        if png.exists() and png.stat().st_size > 500:
            print("OK")
            return png
        print(f"FAILED\n    stdout: {r.stdout[-300:]}\n    stderr: {r.stderr[-300:]}")
    except Exception as e:
        print(f"ERROR: {e}")
    return None

# ── Markdown parser ───────────────────────────────────────────────────────────
def md_inline(text: str) -> str:
    """Convert inline markdown to ReportLab XML."""
    # Bold+italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*',     r'<b>\1</b>',         text)
    # Italic
    text = re.sub(r'\*(.+?)\*',          r'<i>\1</i>',         text)
    # Inline code
    text = re.sub(r'`([^`]+)`', lambda m:
        f'<font name="Courier" size="8.5" color="#0f172a">{escape_xml(m.group(1))}</font>',
        text)
    # Links → just label
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    return text

def escape_xml(t: str) -> str:
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def safe_inline(text: str) -> str:
    """Escape XML then apply inline markdown."""
    # Extract backtick spans first
    parts = re.split(r'(`[^`]+`)', text)
    result = []
    for p in parts:
        if p.startswith('`') and p.endswith('`'):
            inner = escape_xml(p[1:-1])
            result.append(f'<font name="Courier" size="8.5" color="#0f172a">{inner}</font>')
        else:
            s = escape_xml(p)
            s = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', s)
            s = re.sub(r'\*\*(.+?)\*\*',     r'<b>\1</b>',         s)
            s = re.sub(r'\*(.+?)\*',          r'<i>\1</i>',         s)
            s = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', s)
            result.append(s)
    return ''.join(result)

def parse_md(content: str) -> list:
    """Parse markdown into block dicts."""
    blocks = []
    lines  = content.split('\n')
    i      = 0

    while i < len(lines):
        raw  = lines[i]
        line = raw.strip()

        # ── Mermaid block ────────────────────────────────────────────────────
        if line == '```mermaid':
            code_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '```':
                code_lines.append(lines[i])
                i += 1
            blocks.append({'type': 'mermaid', 'code': '\n'.join(code_lines)})

        # ── Generic code block ───────────────────────────────────────────────
        elif line.startswith('```'):
            lang = line[3:].strip()
            code_lines = []
            i += 1
            while i < len(lines) and lines[i].strip() != '```':
                code_lines.append(lines[i])
                i += 1
            blocks.append({'type': 'code', 'lang': lang, 'code': '\n'.join(code_lines)})

        # ── Headings ─────────────────────────────────────────────────────────
        elif line.startswith('### '):
            blocks.append({'type': 'h3', 'text': line[4:]})
        elif line.startswith('## '):
            blocks.append({'type': 'h2', 'text': line[3:]})
        elif line.startswith('# '):
            blocks.append({'type': 'h1', 'text': line[2:]})

        # ── Horizontal rule ──────────────────────────────────────────────────
        elif line == '---':
            blocks.append({'type': 'hr'})

        # ── Table ────────────────────────────────────────────────────────────
        elif line.startswith('|') and i + 1 < len(lines) and re.match(r'[\s|:-]+', lines[i+1].strip()):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                rows.append(cells)
                i += 1
            # Remove separator row (---|---|---)
            if len(rows) > 1 and re.match(r'^[\s\-:]+$', rows[1][0]):
                rows.pop(1)
            blocks.append({'type': 'table', 'rows': rows})
            continue

        # ── Bullet list ──────────────────────────────────────────────────────
        elif re.match(r'^[-*] ', line):
            items = []
            while i < len(lines) and re.match(r'^[-*] ', lines[i].strip()):
                text = lines[i].strip()[2:]
                # checkbox?
                if text.startswith('[ ]'):
                    items.append({'check': False, 'text': text[3:].strip()})
                elif text.startswith('[x]') or text.startswith('[X]'):
                    items.append({'check': True,  'text': text[3:].strip()})
                else:
                    items.append({'text': text})
                i += 1
            blocks.append({'type': 'list', 'items': items})
            continue

        # ── Paragraph ────────────────────────────────────────────────────────
        elif line:
            # Gather continuation lines
            para_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith('#') \
                  and not lines[i].strip().startswith('|') and not lines[i].strip().startswith('```') \
                  and not lines[i].strip().startswith('- ') and not lines[i].strip().startswith('* ') \
                  and lines[i].strip() != '---':
                para_lines.append(lines[i].strip())
                i += 1
            blocks.append({'type': 'para', 'text': ' '.join(para_lines)})
            continue

        i += 1

    return blocks

# ── ReportLab builders ────────────────────────────────────────────────────────
def build_table(rows: list) -> Table:
    """Build a styled ReportLab table from markdown rows."""
    if not rows:
        return Spacer(1, 0)

    header = rows[0]
    data   = rows[1:]
    ncols  = len(header)

    # Determine col widths by content (rough heuristic)
    col_w = [CW / ncols] * ncols  # equal by default

    def cell(text, style):
        return Paragraph(safe_inline(text), STYLES[style])

    tdata = [[cell(h, 'tbl_hd') for h in header]]
    for row in data:
        while len(row) < ncols:
            row.append('')
        tdata.append([cell(c, 'tbl_td') for c in row])

    t = Table(tdata, colWidths=col_w, repeatRows=1)
    t.setStyle(TableStyle([
        # Header
        ('BACKGROUND',  (0,0), (-1,0),  cHDBG),
        ('TEXTCOLOR',   (0,0), (-1,0),  cHDFG),
        ('FONTNAME',    (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',    (0,0), (-1,0),  9),
        ('TOPPADDING',  (0,0), (-1,0),  6),
        ('BOTTOMPADDING',(0,0),(-1,0),  6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING',(0,0), (-1,-1), 8),
        # Body rows
        ('FONTSIZE',    (0,1), (-1,-1), 9),
        ('TOPPADDING',  (0,1), (-1,-1), 5),
        ('BOTTOMPADDING',(0,1),(-1,-1), 5),
        ('ROWBACKGROUNDS',(0,1),(-1,-1),[cROW1, cROW2]),
        # Grid
        ('GRID',        (0,0), (-1,-1), 0.5, cBORD),
        ('BOX',         (0,0), (-1,-1), 1,   cACCT),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t

def build_code_block(code: str, lang: str = '') -> list:
    """Render a code block as styled paragraphs."""
    out = []
    # Truncate very long code blocks
    code_lines = code.split('\n')
    if len(code_lines) > 25:
        code_lines = code_lines[:25] + [f'... ({len(code_lines)-25} more lines)']
    for ln in code_lines:
        txt = escape_xml(ln) if ln.strip() else ' '
        out.append(Paragraph(txt, STYLES['code']))
    return out

def mermaid_to_flowable(code: str, label: str = '', n: int = 0) -> list:
    """Render Mermaid → PNG → ReportLab Image. Fall back to code block."""
    png = render_mermaid(code, label or f"diagram_{n}")
    if png:
        try:
            from PIL import Image as PILImg
            with PILImg.open(png) as im:
                iw, ih = im.size
            # Scale to fit content width with max height
            max_w  = CW
            max_h  = 14 * cm
            scale  = min(max_w / iw, max_h / ih, 1.0)
            dw, dh = iw * scale, ih * scale
            img = RLImage(str(png), width=dw, height=dh)
            cap = Paragraph(escape_xml(label), STYLES['caption']) if label else None
            flowables = [Spacer(1, 4), img]
            if cap:
                flowables.append(cap)
            flowables.append(Spacer(1, 8))
            return flowables
        except Exception as e:
            print(f"  Image embed error: {e}")
    # Fallback: show code
    out = [Spacer(1, 4),
           Paragraph('<i>[Diagram — render failed, showing source]</i>', STYLES['caption'])]
    out += build_code_block(code)
    out.append(Spacer(1, 8))
    return out

def blocks_to_flowables(blocks: list) -> list:
    story = []
    diag_n = 0
    for b in blocks:
        t = b['type']
        if t == 'h1':
            story.append(Paragraph(safe_inline(b['text']), STYLES['h1']))
            story.append(HRFlowable(width=CW, thickness=2, color=cACCT, spaceAfter=6))
        elif t == 'h2':
            story.append(Paragraph(safe_inline(b['text']), STYLES['h2']))
        elif t == 'h3':
            story.append(Paragraph(safe_inline(b['text']), STYLES['h3']))
        elif t == 'hr':
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width=CW, thickness=0.5, color=cBORD, spaceAfter=6))
        elif t == 'para':
            story.append(Paragraph(safe_inline(b['text']), STYLES['body']))
        elif t == 'list':
            for item in b['items']:
                txt = safe_inline(item['text'])
                if 'check' in item:
                    mark = '&#9745;' if item['check'] else '&#9744;'
                    story.append(Paragraph(f'{mark}  {txt}', STYLES['check']))
                else:
                    story.append(Paragraph(f'&bull;  {txt}', STYLES['bullet']))
        elif t == 'table':
            story.append(Spacer(1, 4))
            story.append(build_table(b['rows']))
            story.append(Spacer(1, 8))
        elif t == 'code':
            story.append(Spacer(1, 4))
            story += build_code_block(b['code'], b.get('lang', ''))
            story.append(Spacer(1, 6))
        elif t == 'mermaid':
            diag_n += 1
            story += mermaid_to_flowable(b['code'], f'Figure {diag_n}', diag_n)
    return story

# ── Cover page builder ────────────────────────────────────────────────────────
def cover_page(title: str, subtitle: str, doc_no: str) -> list:
    story = [Spacer(1, 3 * cm)]

    # Doc number badge
    badge_data = [[Paragraph(f'<b>{doc_no}</b>', S('badge', fontSize=10,
                  fontName='Helvetica-Bold', textColor=cACCT, alignment=TA_CENTER))]]
    badge = Table(badge_data, colWidths=[CW])
    badge.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), cLIGHT),
        ('BOX',          (0,0), (-1,-1), 1.5, cACCT),
        ('TOPPADDING',   (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0), (-1,-1), 6),
        ('ALIGN',        (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(badge)
    story.append(Spacer(1, 1.5 * cm))

    story.append(Paragraph(escape_xml(title),
        S('cv_title', fontSize=28, fontName='Helvetica-Bold',
          textColor=cPRIM, leading=36, alignment=TA_CENTER)))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(escape_xml(subtitle),
        S('cv_sub', fontSize=14, fontName='Helvetica',
          textColor=cMUTE, leading=20, alignment=TA_CENTER)))
    story.append(Spacer(1, 2 * cm))

    # Decorative rule
    story.append(HRFlowable(width=CW * 0.6, thickness=3, color=cACCT,
                             spaceAfter=2 * cm, lineCap='round',
                             hAlign='CENTER'))

    meta = [
        ['Project', 'GPA-ERP V5.0'],
        ['Type',    'Construction Cost Control ERP'],
        ['Stack',   'FastAPI · Next.js 14 · PostgreSQL'],
        ['Version', 'V5.0'],
    ]
    meta_data = [[Paragraph(escape_xml(k), S('mk', fontSize=9, fontName='Helvetica-Bold',
                             textColor=cHDFG)),
                  Paragraph(escape_xml(v), S('mv', fontSize=9, fontName='Helvetica',
                             textColor=cHDFG))]
                 for k, v in meta]
    mt = Table(meta_data, colWidths=[CW * 0.3, CW * 0.7])
    mt.setStyle(TableStyle([
        ('BACKGROUND',   (0,0), (-1,-1), cHDBG),
        ('BOX',          (0,0), (-1,-1), 0, cBORD),
        ('TOPPADDING',   (0,0), (-1,-1), 7),
        ('BOTTOMPADDING',(0,0), (-1,-1), 7),
        ('LEFTPADDING',  (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[colors.HexColor('#1e3a8a'), colors.HexColor('#1e40af')]),
    ]))
    story.append(mt)
    story.append(PageBreak())
    return story

# ── Page template with header/footer ─────────────────────────────────────────
def make_on_page(doc_title: str):
    def on_page(canvas, doc):
        canvas.saveState()
        # Header bar
        canvas.setFillColor(cHDBG)
        canvas.rect(MARGIN, PH - 1.1*cm, CW, 0.75*cm, fill=1, stroke=0)
        canvas.setFillColor(cHDFG)
        canvas.setFont('Helvetica-Bold', 8)
        canvas.drawString(MARGIN + 6, PH - 0.78*cm, 'GPA-ERP V5.0  |  Documentation')
        canvas.setFont('Helvetica', 8)
        canvas.drawRightString(PW - MARGIN - 6, PH - 0.78*cm, doc_title)
        # Footer
        canvas.setFillColor(cBORD)
        canvas.rect(MARGIN, 0.8*cm, CW, 0.5, fill=1, stroke=0)
        canvas.setFillColor(cMUTE)
        canvas.setFont('Helvetica', 7.5)
        canvas.drawString(MARGIN, 0.55*cm, 'GPA-ERP — Confidential Internal Document')
        canvas.drawRightString(PW - MARGIN, 0.55*cm, f'Page {doc.page}')
        canvas.restoreState()
    return on_page

# ── Main generator ────────────────────────────────────────────────────────────
DOCS = [
    {
        'file':     '01-user-roles.md',
        'out':      '01-user-roles.pdf',
        'title':    'User Roles & Permissions',
        'subtitle': 'Role definitions, module access matrix, and workflow diagrams',
        'no':       'DOC-01',
    },
    {
        'file':     '02-erd.md',
        'out':      '02-erd.pdf',
        'title':    'Entity Relationship Diagram',
        'subtitle': 'Database schema with all 17 tables and relationships',
        'no':       'DOC-02',
    },
    {
        'file':     '03-data-relationships.md',
        'out':      '03-data-relationships.pdf',
        'title':    'Data Relationship Diagram',
        'subtitle': 'Module-level data flow and business logic connections',
        'no':       'DOC-03',
    },
    {
        'file':     '04-architecture.md',
        'out':      '04-architecture.pdf',
        'title':    'Logical & Technical Architecture',
        'subtitle': 'System design, request lifecycle, and architectural decisions',
        'no':       'DOC-04',
    },
]

for doc_meta in DOCS:
    src  = DOCS_DIR / doc_meta['file']
    dest = DOCS_DIR / doc_meta['out']
    print(f"\n{'='*60}")
    print(f"Building: {doc_meta['out']}")
    print(f"{'='*60}")

    content = src.read_text(encoding='utf-8')
    blocks  = parse_md(content)
    story   = cover_page(doc_meta['title'], doc_meta['subtitle'], doc_meta['no'])
    story  += blocks_to_flowables(blocks)

    pdf = SimpleDocTemplate(
        str(dest),
        pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=1.4 * cm, bottomMargin=1.4 * cm,
        title=doc_meta['title'],
        author='GPA-ERP System',
        subject='GPA-ERP Documentation V5.0',
    )
    on_page = make_on_page(doc_meta['title'])
    pdf.build(story, onFirstPage=on_page, onLaterPages=on_page)
    size_kb = dest.stat().st_size // 1024
    print(f"  Saved: {dest.name} ({size_kb} KB)")

print(f"\nDone! PDFs saved to: {DOCS_DIR}")
