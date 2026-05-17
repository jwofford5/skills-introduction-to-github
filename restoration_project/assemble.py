"""
URVI Framework — Final Assembly Script
Generates restoration_project/FINAL_DOCUMENT.docx from 07_polished.md per
the Layout Notes and the Corporate / Government style spec in the Work Order.
"""
import os
import re
import sys
from copy import deepcopy
from docx import Document
from docx.shared import Pt, Inches, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn, nsmap
from docx.oxml import OxmlElement

SOURCE = "restoration_project/07_polished.md"
OUTPUT = "restoration_project/FINAL_DOCUMENT.docx"

DARK_RED = RGBColor(0x8B, 0x00, 0x00)
LIGHT_GRAY = "F2F2F2"
BLACK = RGBColor(0x00, 0x00, 0x00)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

class Block:
    def __init__(self, kind, text=None, level=None, items=None, lines=None, meta=None):
        self.kind = kind          # heading | para | bullet | numbered | hr | blockquote | code | layout
        self.text = text
        self.level = level
        self.items = items or []
        self.lines = lines or []
        self.meta = meta or {}


def strip_html_comments(text):
    """Remove <!-- ... --> blocks but keep layout/visual/polish comments out of body text."""
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def parse_markdown(md):
    """Parse the polished markdown into a flat list of Block objects."""
    # Remove HTML comments entirely (they're metadata, not body content)
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

        # Skip empty
        if not stripped:
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m:
            level = len(m.group(1))
            blocks.append(Block("heading", text=m.group(2).strip(), level=level))
            i += 1
            continue

        # Horizontal rule
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

        # Blockquote (callout box)
        if stripped.startswith(">"):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote_lines.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            blocks.append(Block("blockquote", lines=quote_lines))
            continue

        # Table
        if "|" in stripped and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i+1]):
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1
            blocks.append(Block("table", lines=table_lines))
            continue

        # Bullet / numbered lists (collect contiguous run)
        if re.match(r"^\s*[-*]\s+", line) or re.match(r"^\s*\d+\.\s+", line):
            list_lines = []
            kind = "bullet" if re.match(r"^\s*[-*]\s+", line) else "numbered"
            while i < len(lines):
                ln = lines[i]
                if re.match(r"^\s*[-*]\s+", ln) or re.match(r"^\s*\d+\.\s+", ln):
                    list_lines.append(ln)
                    i += 1
                elif ln.strip() == "":
                    # blank line ends list
                    break
                elif re.match(r"^\s{2,}\S", ln):
                    # continuation indent — append to last
                    list_lines[-1] += " " + ln.strip()
                    i += 1
                else:
                    break
            items = []
            for ln in list_lines:
                m_b = re.match(r"^\s*[-*]\s+(.*)$", ln)
                m_n = re.match(r"^\s*\d+\.\s+(.*)$", ln)
                if m_b:
                    items.append(("bullet", m_b.group(1).strip()))
                elif m_n:
                    items.append(("numbered", m_n.group(1).strip()))
            blocks.append(Block("list", items=items, meta={"kind": kind}))
            continue

        # Paragraph (gather contiguous non-empty, non-special lines)
        buf = []
        while i < len(lines):
            ln = lines[i]
            s = ln.strip()
            if not s:
                break
            if re.match(r"^(#{1,6})\s+", s) or s == "---" or s.startswith("```") or s.startswith(">") or re.match(r"^\s*[-*]\s+", ln) or re.match(r"^\s*\d+\.\s+", ln):
                break
            if "|" in s and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-+", lines[i+1]):
                break
            buf.append(ln)
            i += 1
        flush_para(buf)

    return blocks


# ---------------------------------------------------------------------------
# Word document construction
# ---------------------------------------------------------------------------

def set_run_font(run, name="Times New Roman", size_pt=11, bold=False, italic=False, color=None, all_caps=False):
    run.font.name = name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color is not None:
        run.font.color.rgb = color
    if all_caps:
        run.font.all_caps = True
    # East-Asian font override (Word needs explicit rFonts for non-default fonts)
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    rFonts.set(qn("w:ascii"), name)
    rFonts.set(qn("w:hAnsi"), name)
    rFonts.set(qn("w:cs"), name)


def add_inline_runs(paragraph, text, base_font="Times New Roman", base_size=11, bold=False, italic=False, color=None):
    """Handle inline **bold**, *italic*, `code` within a paragraph text."""
    # Split on **bold** and `code` and *italic*
    # Tokens: (text, is_bold, is_italic, is_code)
    tokens = []
    pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            tokens.append((text[pos:m.start()], False, False, False))
        tok = m.group(0)
        if tok.startswith("**"):
            tokens.append((tok[2:-2], True, False, False))
        elif tok.startswith("`"):
            tokens.append((tok[1:-1], False, False, True))
        pos = m.end()
    if pos < len(text):
        tokens.append((text[pos:], False, False, False))
    if not tokens:
        tokens = [(text, False, False, False)]

    for tk_text, tk_bold, tk_italic, tk_code in tokens:
        run = paragraph.add_run(tk_text)
        if tk_code:
            set_run_font(run, name="Courier New", size_pt=10, bold=bold or tk_bold, italic=italic or tk_italic, color=color)
        else:
            set_run_font(run, name=base_font, size_pt=base_size, bold=bold or tk_bold, italic=italic or tk_italic, color=color)


def shade_paragraph(paragraph, hex_color):
    pPr = paragraph._element.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    pPr.append(shd)


def add_paragraph_border(paragraph, position, size=8, color="8B0000"):
    """Add a single border to a paragraph. position: 'bottom' | 'top' | 'left' | 'right'."""
    pPr = paragraph._element.get_or_add_pPr()
    pBdr = pPr.find(qn("w:pBdr"))
    if pBdr is None:
        pBdr = OxmlElement("w:pBdr")
        pPr.append(pBdr)
    el = OxmlElement(f"w:{position}")
    el.set(qn("w:val"), "single")
    el.set(qn("w:sz"), str(size))
    el.set(qn("w:space"), "1")
    el.set(qn("w:color"), color)
    pBdr.append(el)


def set_page_break_before(paragraph):
    pPr = paragraph._element.get_or_add_pPr()
    pbb = OxmlElement("w:pageBreakBefore")
    pPr.append(pbb)


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


def make_heading(doc, text, level, is_first_h2):
    # Use Word's built-in Heading styles so auto-TOC, navigation, and outline view all work.
    style_name = f"Heading {min(level, 9)}"
    p = doc.add_paragraph(style=style_name)
    pf = p.paragraph_format
    pf.space_before = Pt(12)
    pf.space_after = Pt(6)
    keep_with_next(p)

    if level == 1:
        run = p.add_run(text)
        set_run_font(run, name="Times New Roman", size_pt=18, bold=True, color=DARK_RED)
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    elif level == 2:
        run = p.add_run(text.upper())
        set_run_font(run, name="Times New Roman", size_pt=14, bold=True, color=BLACK, all_caps=True)
        add_paragraph_border(p, "bottom", size=6, color="8B0000")
        if not is_first_h2:
            set_page_break_before(p)
    elif level == 3:
        run = p.add_run(text)
        set_run_font(run, name="Times New Roman", size_pt=12, bold=True, color=BLACK)
    elif level == 4:
        run = p.add_run(text)
        set_run_font(run, name="Times New Roman", size_pt=11, bold=True, italic=True, color=BLACK)
    else:
        run = p.add_run(text)
        set_run_font(run, name="Times New Roman", size_pt=11, bold=True)
    return p


def make_callout_box(doc, lines):
    """Render a blockquote as a callout: dark red header row + light gray body."""
    if not lines:
        return
    # First line is treated as the header (UPPERCASE label like "**THE THREE-PHASE..."**)
    header_text = lines[0]
    body_lines = lines[1:]
    # Strip leading bold markers from header
    header_clean = re.sub(r"^\*\*(.+?)\*\*$", r"\1", header_text.strip())

    # Header paragraph
    p_head = doc.add_paragraph()
    p_head.paragraph_format.space_before = Pt(6)
    p_head.paragraph_format.space_after = Pt(0)
    keep_with_next(p_head)
    set_run_font(p_head.add_run(header_clean.upper()), name="Times New Roman", size_pt=11, bold=True, color=WHITE, all_caps=True)
    shade_paragraph(p_head, "8B0000")
    add_paragraph_border(p_head, "top", size=12, color="8B0000")
    add_paragraph_border(p_head, "left", size=12, color="8B0000")
    add_paragraph_border(p_head, "right", size=12, color="8B0000")

    # Body paragraphs
    for idx, raw in enumerate(body_lines):
        p_body = doc.add_paragraph()
        p_body.paragraph_format.space_before = Pt(0)
        p_body.paragraph_format.space_after = Pt(3 if idx < len(body_lines) - 1 else 6)
        add_inline_runs(p_body, raw, base_size=11)
        shade_paragraph(p_body, LIGHT_GRAY)
        add_paragraph_border(p_body, "left", size=12, color="8B0000")
        add_paragraph_border(p_body, "right", size=12, color="8B0000")
        if idx == len(body_lines) - 1:
            add_paragraph_border(p_body, "bottom", size=12, color="8B0000")


def make_list(doc, items):
    """Render a list of (kind, text) tuples."""
    for kind, txt in items:
        # Checklist items: text starts with ☐
        if txt.startswith("☐"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.25)
            p.paragraph_format.first_line_indent = Inches(-0.25)
            p.paragraph_format.space_after = Pt(3)
            # Use Wingdings ☐ glyph (cleaner) — fall back to Unicode if Wingdings unavailable
            run = p.add_run("☐ ")
            set_run_font(run, name="Times New Roman", size_pt=11)
            # Remaining text after ☐
            remainder = txt[1:].lstrip()
            add_inline_runs(p, remainder, base_size=11)
            continue

        # Phase transition header style (already bold ** in source)
        p = doc.add_paragraph(style="List Bullet" if kind == "bullet" else "List Number")
        p.paragraph_format.space_after = Pt(3)
        # Strip out existing default run added by style
        for r in list(p.runs):
            r.text = ""
        add_inline_runs(p, txt, base_size=11)


def make_paragraph(doc, text):
    # Special handling: Phase transition labels like "**PHASE 1 → PHASE 2:**"
    if text.startswith("**PHASE") and text.endswith("**"):
        clean = text.strip("*")
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(3)
        keep_with_next(p)
        set_run_font(p.add_run(clean), name="Times New Roman", size_pt=11, bold=True, color=DARK_RED)
        return

    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    add_inline_runs(p, text, base_size=11)


def make_code_block(doc, lines):
    """Render a code block (used for the ASCII org chart in Figure 1)."""
    for ln in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        set_run_font(p.add_run(ln), name="Courier New", size_pt=9)


def make_table(doc, lines):
    """Parse and render a markdown table."""
    rows = []
    for ln in lines:
        if re.match(r"^\s*\|?\s*:?-+", ln):  # separator row
            continue
        # Trim leading/trailing pipes
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return
    ncols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.style = "Light Grid Accent 1"
    table.autofit = True
    for i, row in enumerate(rows):
        # Pad short rows
        cells = row + [""] * (ncols - len(row))
        for j, cell in enumerate(cells):
            tc = table.rows[i].cells[j]
            tc.text = ""
            p = tc.paragraphs[0]
            if i == 0:
                # Header row: bold
                add_inline_runs(p, cell, base_size=10, bold=True)
            else:
                add_inline_runs(p, cell, base_size=10)


# ---------------------------------------------------------------------------
# Header + footer
# ---------------------------------------------------------------------------

def add_page_number(paragraph):
    """Insert a PAGE field into the given paragraph (right side after a tab)."""
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
    set_run_font(run, name="Times New Roman", size_pt=10)


def set_running_header(section, doc_title):
    section.different_first_page_header_footer = True
    # First-page header stays blank
    first_header = section.first_page_header
    for p in first_header.paragraphs:
        for r in list(p.runs):
            r.text = ""
    # Regular header on pages 2+
    header = section.header
    header.is_linked_to_previous = False
    # Use first paragraph
    p = header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # Clear any existing content
    for r in list(p.runs):
        r.text = ""
    # Add title on left, tab, page number on right
    pPr = p._element.get_or_add_pPr()
    # Add tab stops: center and right (right at 6.5" given 1" margins on Letter)
    tabs = OxmlElement("w:tabs")
    tab_right = OxmlElement("w:tab")
    tab_right.set(qn("w:val"), "right")
    tab_right.set(qn("w:pos"), "9360")  # twips = 6.5 inches
    tabs.append(tab_right)
    pPr.append(tabs)
    run = p.add_run(doc_title)
    set_run_font(run, name="Times New Roman", size_pt=10)
    p.add_run("\t")
    add_page_number(p)


# ---------------------------------------------------------------------------
# Cover page
# ---------------------------------------------------------------------------

def build_cover_page(doc):
    # The cover page is the first section. Add several blank paragraphs to push title down a bit.
    for _ in range(6):
        doc.add_paragraph()

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_after = Pt(18)
    set_run_font(p_title.add_run("UNIFIED RESPONSE TO VIOLENT INCIDENTS (URVI)"), name="Times New Roman", size_pt=18, bold=True, color=DARK_RED)

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(36)
    set_run_font(p_sub.add_run("Framework for Los Angeles County Operational Guidelines"), name="Times New Roman", size_pt=13, italic=True, color=BLACK)

    p_prep = doc.add_paragraph()
    p_prep.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p_prep.add_run("Prepared by the URVI Guidelines Committee"), name="Times New Roman", size_pt=11)

    p_org = doc.add_paragraph()
    p_org.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_org.paragraph_format.space_after = Pt(0)
    set_run_font(p_org.add_run("Los Angeles County Public Safety Agencies"), name="Times New Roman", size_pt=11)

    # Vertical gap
    for _ in range(8):
        doc.add_paragraph()

    p_ver = doc.add_paragraph()
    p_ver.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p_ver.add_run("Version 1.0 | Effective: [DATE]"), name="Times New Roman", size_pt=10)


# ---------------------------------------------------------------------------
# Main assembly
# ---------------------------------------------------------------------------

def main():
    with open(SOURCE, "r", encoding="utf-8") as f:
        md = f.read()

    # Stop before the "## Completion Checklist" — that's audit/polish metadata, not body content.
    # Also stop before "## Layout Notes for Final Assembly" — those are instructions for THIS step.
    cutoff_idx = md.find("\n## Layout Notes for Final Assembly")
    if cutoff_idx == -1:
        cutoff_idx = md.find("\n## Completion Checklist")
    if cutoff_idx != -1:
        md = md[:cutoff_idx]

    blocks = parse_markdown(md)

    doc = Document()

    # Configure section: Letter, 1" margins
    section = doc.sections[0]
    section.page_height = Inches(11)
    section.page_width = Inches(8.5)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    # Default style
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)

    # ----- Cover Page -----
    build_cover_page(doc)
    add_page_break(doc)

    # ----- Body -----
    # Running header on pages 2+, none on cover (different_first_page_header_footer)
    set_running_header(section, "Unified Response to Violent Incidents (URVI)")

    h2_count = 0
    skip_first_h1 = False
    for blk in blocks:
        if blk.kind == "heading":
            if blk.level == 1:
                # The first H1 is the doc title — already rendered as cover; skip it.
                if not skip_first_h1:
                    skip_first_h1 = True
                    continue
                make_heading(doc, blk.text, 1, is_first_h2=False)
            elif blk.level == 2:
                # Detect numbered major sections (e.g., "1. EXECUTIVE SUMMARY", "TABLE OF CONTENTS", "FIGURE 1: ...")
                is_first_h2 = (h2_count == 0)
                make_heading(doc, blk.text, 2, is_first_h2=is_first_h2)
                h2_count += 1
            else:
                make_heading(doc, blk.text, blk.level, is_first_h2=False)
        elif blk.kind == "para":
            make_paragraph(doc, blk.text)
        elif blk.kind == "list":
            make_list(doc, blk.items)
        elif blk.kind == "blockquote":
            make_callout_box(doc, blk.lines)
        elif blk.kind == "code":
            make_code_block(doc, blk.lines)
        elif blk.kind == "table":
            make_table(doc, blk.lines)
        elif blk.kind == "hr":
            # Treat as visual separator — small spacing paragraph; suppress consecutive HRs
            continue

    # ----- Save -----
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    doc.save(OUTPUT)
    print(f"Saved: {OUTPUT}")

    # ----- Self-verify -----
    assert os.path.exists(OUTPUT), "File not created"
    size = os.path.getsize(OUTPUT)
    assert size > 5000, f"File too small: {size} bytes"
    doc2 = Document(OUTPUT)
    headings = [p for p in doc2.paragraphs if p.style.name.startswith("Heading")]
    print(f"File size: {size:,} bytes")
    print(f"Total paragraphs: {len(doc2.paragraphs)}")
    print(f"Headings detected (built-in style): {len(headings)}")
    print(f"Tables: {len(doc2.tables)}")

    # Word counts for sanity
    total_text = "\n".join(p.text for p in doc2.paragraphs)
    word_count = len(total_text.split())
    print(f"Estimated word count: {word_count}")
    # Estimate pages ~ 350 words/page for Times New Roman 11pt 1.15 spacing
    est_pages = max(1, (word_count // 350) + 4)  # +cover, +TOC, +figure, +section page breaks
    print(f"Estimated pages: ~{est_pages}")


if __name__ == "__main__":
    main()
