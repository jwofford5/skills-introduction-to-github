"""
Emotional Intelligence — APA Academic Paper Assembly
Generates restoration_project/FINAL_DOCUMENT.docx from 07_polished.md
per the Layout Notes in 06_formatted.md and APA 7th edition style.
"""
import os
import re
import sys
import subprocess

SOURCE = "restoration_project/07_polished.md"
OUTPUT = "restoration_project/FINAL_DOCUMENT.docx"

try:
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document
    from docx.shared import Pt, Inches, RGBColor, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

BLACK = RGBColor(0x00, 0x00, 0x00)

# ---------------------------------------------------------------------------
# Layout constants (from Layout Notes)
# ---------------------------------------------------------------------------
FONT_NAME = "Times New Roman"
FONT_SIZE_BODY = 12       # pt
FONT_SIZE_HEADER = 10     # pt
LINE_SPACING_DOUBLE = 2.0
INDENT_FIRST_LINE = Inches(0.5)
HANGING_INDENT = Inches(0.5)
RUNNING_HEAD = "EMOTIONAL INTELLIGENCE"


# ---------------------------------------------------------------------------
# XML helpers
# ---------------------------------------------------------------------------

def set_run_font(run, name=FONT_NAME, size_pt=FONT_SIZE_BODY,
                 bold=False, italic=False, color=None):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:cs"), name)


def set_double_spacing(paragraph):
    pf = paragraph.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)


def keep_with_next(paragraph):
    pPr = paragraph._element.get_or_add_pPr()
    el = OxmlElement("w:keepNext")
    pPr.append(el)


def add_page_break(doc):
    p = doc.add_paragraph()
    run = p.add_run()
    br = OxmlElement("w:br")
    br.set(qn("w:type"), "page")
    run._element.append(br)
    return p


def add_page_number_field(paragraph):
    """Insert a PAGE field into the given paragraph."""
    run = paragraph.add_run()
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.set(qn("xml:space"), "preserve")
    instrText.text = " PAGE "
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._element.append(fldChar1)
    run._element.append(instrText)
    run._element.append(fldChar2)
    set_run_font(run, size_pt=FONT_SIZE_HEADER)


def enable_auto_update_fields(doc):
    settings = doc.settings.element
    for existing in settings.findall(qn("w:updateFields")):
        settings.remove(existing)
    el = OxmlElement("w:updateFields")
    el.set(qn("w:val"), "true")
    settings.append(el)


# ---------------------------------------------------------------------------
# Running header
# ---------------------------------------------------------------------------

def set_running_header(section):
    """APA style: short title flush left + page number flush right on ALL pages."""
    section.different_first_page_header_footer = False
    header = section.header
    header.is_linked_to_previous = False

    p = header.paragraphs[0] if header.paragraphs else header.add_paragraph()
    for r in list(p.runs):
        r.text = ""

    # Tab stop: right-aligned at 6.5" (content width on Letter with 1" margins)
    pPr = p._element.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab_right = OxmlElement("w:tab")
    tab_right.set(qn("w:val"), "right")
    tab_right.set(qn("w:pos"), "9360")  # 6.5" × 1440 twips/inch
    tabs.append(tab_right)
    pPr.append(tabs)

    run_title = p.add_run(RUNNING_HEAD)
    set_run_font(run_title, size_pt=FONT_SIZE_HEADER)

    p.add_run("\t")
    add_page_number_field(p)


# ---------------------------------------------------------------------------
# Title page
# ---------------------------------------------------------------------------

def build_title_page(doc):
    """APA 7th title page: title, author, affiliation, course, date."""
    # Push title down ~1/3 of the page (about 5 blank double-spaced lines)
    for _ in range(5):
        bp = doc.add_paragraph()
        set_double_spacing(bp)

    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_double_spacing(title_p)
    run = title_p.add_run("Emotional Intelligence")
    set_run_font(run, bold=True)

    for _ in range(2):
        sp = doc.add_paragraph()
        set_double_spacing(sp)

    fields = [
        ("Author", ""),
        ("Institutional Affiliation", ""),
        ("Course Name and Number", ""),
        ("Instructor", ""),
        ("2026-05-17", ""),
    ]
    labels = [
        "Author",
        "Institutional Affiliation",
        "Course",
        "Instructor",
        "2026-05-17",
    ]
    for label in labels:
        lp = doc.add_paragraph()
        lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_double_spacing(lp)
        run = lp.add_run(label)
        set_run_font(run)


# ---------------------------------------------------------------------------
# Inline markdown rendering
# ---------------------------------------------------------------------------

def add_inline_runs(paragraph, text, bold=False, italic=False,
                    size_pt=FONT_SIZE_BODY):
    """Handle **bold**, *italic* inline marks. Ignores nested combinations
    to keep the parser simple and robust against imperfect markdown."""
    pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*\n]+?\*)")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            run = paragraph.add_run(text[pos:m.start()])
            set_run_font(run, bold=bold, italic=italic, size_pt=size_pt)
        tok = m.group(0)
        if tok.startswith("**"):
            run = paragraph.add_run(tok[2:-2])
            set_run_font(run, bold=True, italic=italic, size_pt=size_pt)
        else:
            run = paragraph.add_run(tok[1:-1])
            set_run_font(run, bold=bold, italic=True, size_pt=size_pt)
        pos = m.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        set_run_font(run, bold=bold, italic=italic, size_pt=size_pt)


# ---------------------------------------------------------------------------
# APA heading styles
# ---------------------------------------------------------------------------

def make_heading(doc, text, level):
    """
    APA 7th heading levels:
      Level 1 (##):  Centered Bold
      Level 2 (###): Flush Left Bold
      Level 3 (####): Flush Left Bold Italic
    """
    p = doc.add_paragraph()
    set_double_spacing(p)
    keep_with_next(p)

    if level == 1:
        # Document title (only used for the paper title on the first body page)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        set_run_font(run, bold=True)
    elif level == 2:
        # APA Level 1 heading: centered bold
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        set_run_font(run, bold=True)
    elif level == 3:
        # APA Level 2 heading: flush left bold
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        set_run_font(run, bold=True)
    else:
        # APA Level 3 heading: flush left bold italic
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = p.add_run(text)
        set_run_font(run, bold=True, italic=True)

    return p


# ---------------------------------------------------------------------------
# Body paragraph
# ---------------------------------------------------------------------------

def make_paragraph(doc, text, indent=True, hanging=False):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    set_double_spacing(p)
    pf = p.paragraph_format
    if hanging:
        pf.left_indent = HANGING_INDENT
        pf.first_line_indent = -HANGING_INDENT
    elif indent:
        pf.first_line_indent = INDENT_FIRST_LINE
    add_inline_runs(p, text)
    return p


# ---------------------------------------------------------------------------
# List items
# ---------------------------------------------------------------------------

def make_list_item(doc, text, numbered=False, number=None):
    p = doc.add_paragraph()
    set_double_spacing(p)
    pf = p.paragraph_format
    pf.left_indent = INDENT_FIRST_LINE
    pf.first_line_indent = -INDENT_FIRST_LINE

    if numbered and number is not None:
        run = p.add_run(f"{number}. ")
        set_run_font(run)

    add_inline_runs(p, text)
    return p


# ---------------------------------------------------------------------------
# Bullet list (APA uses indented run-in items for bulleted lists)
# ---------------------------------------------------------------------------

def make_list(doc, items):
    numbered_counter = 1
    for (kind, text) in items:
        is_numbered = (kind == "numbered")
        if is_numbered:
            make_list_item(doc, text, numbered=True, number=numbered_counter)
            numbered_counter += 1
        else:
            p = doc.add_paragraph()
            set_double_spacing(p)
            pf = p.paragraph_format
            pf.left_indent = INDENT_FIRST_LINE
            pf.first_line_indent = -INDENT_FIRST_LINE
            bullet_run = p.add_run("• ")
            set_run_font(bullet_run)
            add_inline_runs(p, text)


# ---------------------------------------------------------------------------
# Table (APA style: no vertical lines, horizontal lines only)
# ---------------------------------------------------------------------------

def make_table(doc, lines):
    rows = []
    for ln in lines:
        if re.match(r"^\s*\|?\s*:?-+", ln):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return

    ncols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.autofit = True

    # Remove all borders, then add only the APA horizontal lines
    def set_table_borders(tbl):
        tblPr = tbl._tbl.find(qn("w:tblPr"))
        if tblPr is None:
            tblPr = OxmlElement("w:tblPr")
            tbl._tbl.insert(0, tblPr)
        tblBorders = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{side}")
            el.set(qn("w:val"), "nil")
            tblBorders.append(el)
        tblPr.append(tblBorders)

    set_table_borders(table)

    def add_row_border(row, position, size=6):
        for cell in row.cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = tcPr.find(qn("w:tcBorders"))
            if tcBorders is None:
                tcBorders = OxmlElement("w:tcBorders")
                tcPr.append(tcBorders)
            el = OxmlElement(f"w:{position}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), str(size))
            el.set(qn("w:color"), "000000")
            tcBorders.append(el)

    # APA: line above header, line below header, line below last row
    add_row_border(table.rows[0], "top", size=8)
    add_row_border(table.rows[0], "bottom", size=6)
    add_row_border(table.rows[-1], "bottom", size=8)

    for i, row_data in enumerate(rows):
        cells = row_data + [""] * (ncols - len(row_data))
        for j, cell_text in enumerate(cells):
            tc = table.rows[i].cells[j]
            tc.text = ""
            p = tc.paragraphs[0]
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(3)
            is_header = (i == 0)
            add_inline_runs(p, cell_text, bold=is_header, size_pt=11)

    # Spacer after table
    sp = doc.add_paragraph()
    set_double_spacing(sp)


# ---------------------------------------------------------------------------
# Code block (for the four-branch diagram)
# ---------------------------------------------------------------------------

def make_code_block(doc, lines):
    for ln in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        pf = p.paragraph_format
        pf.left_indent = INDENT_FIRST_LINE
        run = p.add_run(ln)
        run.font.name = "Courier New"
        run.font.size = Pt(10)


# ---------------------------------------------------------------------------
# Markdown parser
# ---------------------------------------------------------------------------

class Block:
    def __init__(self, kind, text=None, level=None, items=None, lines=None):
        self.kind = kind
        self.text = text
        self.level = level
        self.items = items or []
        self.lines = lines or []


def strip_html_comments(text):
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def parse_markdown(md):
    md = strip_html_comments(md)
    lines = md.split("\n")
    blocks = []
    i = 0

    def flush_para(buf):
        if buf:
            text = " ".join(line.strip() for line in buf).strip()
            if text:
                blocks.append(Block("para", text=text))

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Heading
        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            level = len(m.group(1))
            blocks.append(Block("heading", text=m.group(2).strip(), level=level))
            i += 1
            continue

        # HR
        if stripped == "---":
            blocks.append(Block("hr"))
            i += 1
            continue

        # Code fence
        if stripped.startswith("```"):
            j = i + 1
            code_lines = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                code_lines.append(lines[j])
                j += 1
            blocks.append(Block("code", lines=code_lines))
            i = j + 1
            continue

        # Table
        if "|" in stripped and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i + 1]):
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            blocks.append(Block("table", lines=table_lines))
            continue

        # List
        if re.match(r"^\s*[-*•]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            list_lines = []
            while i < len(lines):
                ln = lines[i]
                if re.match(r"^\s*[-*•]\s+", ln) or re.match(r"^\s*\d+\.\s+", ln):
                    list_lines.append(ln)
                    i += 1
                elif not ln.strip():
                    break
                elif re.match(r"^\s{2,}\S", ln):
                    list_lines[-1] += " " + ln.strip()
                    i += 1
                else:
                    break
            items = []
            for ln in list_lines:
                mb = re.match(r"^\s*[-*•]\s+(.*)$", ln)
                mn = re.match(r"^\s*\d+\.\s+(.*)$", ln)
                if mb:
                    items.append(("bullet", mb.group(1).strip()))
                elif mn:
                    items.append(("numbered", mn.group(1).strip()))
            blocks.append(Block("list", items=items))
            continue

        # Paragraph
        buf = []
        while i < len(lines):
            ln = lines[i]
            s = ln.strip()
            if not s:
                break
            if (re.match(r"^#{1,6}\s+", s) or s == "---" or
                    s.startswith("```") or
                    re.match(r"^\s*[-*•]\s+", ln) or
                    re.match(r"^\s*\d+\.\s+", ln)):
                break
            if "|" in s and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i + 1]):
                break
            buf.append(ln)
            i += 1
        flush_para(buf)

    return blocks


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------

def is_abstract_heading(text):
    return text.strip().lower() == "abstract"


def is_references_heading(text):
    return text.strip().lower() == "references"


def main():
    with open(SOURCE, "r", encoding="utf-8") as f:
        md = f.read()

    blocks = parse_markdown(md)

    doc = Document()

    # Page setup: Letter, 1" margins
    section = doc.sections[0]
    section.page_height = Inches(11)
    section.page_width = Inches(8.5)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # Default style
    normal = doc.styles["Normal"]
    normal.font.name = FONT_NAME
    normal.font.size = Pt(FONT_SIZE_BODY)

    # Running header (APA: all pages including title page)
    set_running_header(section)

    # Title page
    build_title_page(doc)

    # Page break → abstract page
    add_page_break(doc)

    # --- Parse and render body ---
    # Track state
    in_references = False
    abstract_mode = False  # abstract paragraph not indented
    title_seen = False      # skip the H1 doc title (already on title page)
    keywords_next = False   # next paragraph after abstract is keywords line

    for blk in blocks:
        if blk.kind == "hr":
            continue

        if blk.kind == "heading":
            level = blk.level
            text = blk.text.strip()

            # H1: document title — skip (already on title page)
            if level == 1:
                if not title_seen:
                    title_seen = True
                continue

            if is_abstract_heading(text):
                abstract_mode = True
                in_references = False
                # Abstract heading: centered bold (APA Level 1)
                make_heading(doc, text, 2)
                keywords_next = False
                continue

            if is_references_heading(text):
                in_references = True
                abstract_mode = False
                make_heading(doc, text, 2)
                continue

            abstract_mode = False
            in_references = False
            make_heading(doc, text, level)
            continue

        if blk.kind == "para":
            text = blk.text.strip()
            if not text:
                continue

            # Keywords line (italic "Keywords:" prefix)
            if text.lower().startswith("*keywords:*") or text.lower().startswith("keywords:"):
                kp = doc.add_paragraph()
                set_double_spacing(kp)
                kp.paragraph_format.first_line_indent = INDENT_FIRST_LINE
                add_inline_runs(kp, text)
                continue

            if in_references:
                # Reference entries: hanging indent, no first-line indent
                make_paragraph(doc, text, indent=False, hanging=True)
                continue

            if abstract_mode:
                # Abstract: no first-line indent (APA style)
                make_paragraph(doc, text, indent=False)
                continue

            make_paragraph(doc, text, indent=True)
            continue

        if blk.kind == "list":
            make_list(doc, blk.items)
            continue

        if blk.kind == "table":
            make_table(doc, blk.lines)
            continue

        if blk.kind == "code":
            make_code_block(doc, blk.lines)
            continue

    enable_auto_update_fields(doc)

    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    doc.save(OUTPUT)
    print(f"Saved: {OUTPUT}")

    # Verify
    assert os.path.exists(OUTPUT), "File not created"
    size = os.path.getsize(OUTPUT)
    assert size > 5000, f"File too small: {size} bytes"

    doc2 = Document(OUTPUT)
    headings = [p for p in doc2.paragraphs if p.style.name.startswith("Heading")]
    word_count = len(" ".join(p.text for p in doc2.paragraphs).split())
    print(f"File size: {size:,} bytes")
    print(f"Total paragraphs: {len(doc2.paragraphs)}")
    print(f"Headings: {len(headings)}")
    print(f"Tables: {len(doc2.tables)}")
    print(f"Estimated word count: {word_count}")
    est_pages = max(1, word_count // 250)
    print(f"Estimated pages: ~{est_pages}")

    # PDF via LibreOffice
    try:
        result = subprocess.run(
            ["libreoffice", "--headless", "--convert-to", "pdf",
             "--outdir", "restoration_project", OUTPUT],
            capture_output=True, timeout=60
        )
        pdf_path = OUTPUT.replace(".docx", ".pdf")
        if result.returncode == 0 and os.path.exists(pdf_path):
            print(f"PDF generated: {pdf_path}")
        else:
            print("LibreOffice not available — open .docx in Word → File → Save As → PDF.")
    except Exception as e:
        print(f"PDF conversion skipped: {e}")
        print("Open .docx in Word → File → Save As → PDF.")


if __name__ == "__main__":
    main()
