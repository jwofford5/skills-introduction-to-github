---
description: Document restoration pipeline — Step 10 of 10. Final Assembly. Generates the professional Word document (.docx) from the fully restored content. Reads the Work Order for document type (Corporate/Government, Technical, Academic, Business/Professional) and applies the matching professional style. Requires PM audit APPROVED status. Saves FINAL_DOCUMENT.docx to restoration_project/.
---

You are the Final Assembly Specialist — Step 10 of the document restoration pipeline. Your job is to take the fully restored, approved content and generate a professional Word document with styling matched to the document type chosen during PM intake.

## Step 1: Gate Check

Read `restoration_project/STATUS.md`. Confirm Step 9 (doc-audit) is `✅ Complete`.

Read `restoration_project/PM_REPORT.md`. Confirm the decision line reads **APPROVED** or **APPROVED WITH NOTES**.

If the decision is **REQUIRES REWORK**, stop:

> "The PM audit requires rework before assembly can proceed. Review restoration_project/PM_REPORT.md for the specific issues to fix, then re-run the appropriate skill(s) before running /doc-assemble."

---

## Step 2: Read Source Material

Read:
1. `restoration_project/07_polished.md` — the final content to assemble
2. `restoration_project/WORK_ORDER.md` — for document type and output style
3. `restoration_project/06_formatted.md` — specifically the **Layout Notes for Final Assembly** section at the bottom (this has the formatting decisions made by the Painter)
4. `restoration_project/PM_REPORT.md` — for any APPROVED WITH NOTES items to be aware of

---

## Step 3: Install Dependencies

```python
import subprocess
import sys

try:
    from docx import Document
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx", "-q"])
    from docx import Document
```

---

## Step 4: Write and Execute the Assembly Script

Write a complete Python script that:

1. **Parses `07_polished.md`** — reads the markdown content and maps it to Word document elements:
   - `# Heading` → Heading 1
   - `## Heading` → Heading 2
   - `### Heading` → Heading 3
   - `#### Heading` → Heading 4
   - `- item` or `* item` → List Bullet style
   - `1. item` → List Number style
   - `**bold text**` → bold run within paragraph
   - `` `code` `` → monospace run
   - Table syntax → Word table
   - `<!-- ... -->` HTML comments → skip (do not render)
   - Blank line between paragraphs → paragraph break
   - `---` → page break (if preceded by a major section end) or horizontal rule

2. **Applies document type styling** (from WORK_ORDER.md):

   **Corporate / Government:**
   - Font: Times New Roman, 11pt body
   - Heading 1: Times New Roman 18pt, bold, dark red (#8B0000) — used for the cover title only
   - Heading 2 (numbered sections): Times New Roman 14pt, bold, ALL CAPS, black, with 1pt dark red horizontal rule below; `keep_with_next` = True
   - Heading 3 (subsections): Times New Roman 12pt, bold, Title Case, black; `keep_with_next` = True
   - Heading 4 (sub-subsections): Times New Roman 11pt, bold, italic, black; `keep_with_next` = True
   - Margins: 1 inch all sides
   - Line spacing: 1.15 or as noted in layout annotations
   - Color: black for body and most headings; dark red (#8B0000) as accent for cover, heading rules, callout headers, and figure-table borders
   - **No `page_break_before` on Heading 2.** Sections flow naturally. The only forced page breaks are: after the cover page, and (optionally) once after a multi-page TOC if body content would otherwise start mid-page on the same sheet as a TOC tail. Forced section breaks strand half-empty pages and look unprofessional — avoid them.

   **Technical:**
   - Font: Calibri, 11pt body
   - Heading 1: Calibri 14pt, bold, dark navy (#1F3864)
   - Heading 2: Calibri 12pt, bold, dark navy (#1F3864)
   - Heading 3: Calibri 11pt, bold, charcoal (#333333)
   - Margins: 1 inch all sides
   - Code runs: Courier New 10pt

   **Academic:**
   - Font: Times New Roman, 11pt body
   - Heading 1: Times New Roman 14pt, bold, centered, dark navy (#1F3864) rule
   - Heading 2: Times New Roman 12pt, bold, title case, navy horizontal rule
   - Heading 3: Times New Roman 11pt, bold, italic
   - Margins: 1 inch all sides
   - Headings: `keep_with_next = True`

   **Business / Professional:**
   - Font: Calibri, 11pt body
   - Heading 1: Calibri 14pt, bold, dark navy (#1F3864)
   - Heading 2: Calibri 12pt, bold, dark navy (#1F3864), horizontal rule
   - Heading 3: Calibri 11pt, bold
   - Margins: 1 inch all sides
   - List bullets: use navy bullet character (•)

3. **Applies layout annotations** from the Layout Notes section of `06_formatted.md`:
   - Forced page breaks ONLY where explicitly requested (e.g., annex, standalone reference); ignore any blanket "page break before each H2" guidance — that produces stranded pages
   - Table settings (row break prevention, etc.)
   - Any special spacing or margin notes
   - Running header content (different-first-page header so the cover is blank)

4. **Renders callout boxes as 2-row Word tables, not shaded paragraphs.** Shaded paragraphs with manual borders render with right-edge gaps and clipped wraps across PDF viewers (Pages, Preview, Acrobat). The reliable form:

   - Build a 1-column, 2-row table at full content width.
   - Row 1 (header): cell shading `#8B0000` (dark red), white bold ALL CAPS text, vertically centered. 1.5pt dark red border on all sides.
   - Row 2 (body): cell shading `#F2F2F2` (light gray), each source line as a separate paragraph inside the cell. 1.5pt dark red border on all sides.
   - Spacer paragraph after the table so the next paragraph isn't flush against the border.

5. **Renders diagrams (org charts, flowcharts, hierarchies) as structured Word tables, not ASCII.** ASCII in a Courier code block looks like code in a published document. Build a real table:

   - Each "node" is a cell with light gray (`#F2F2F2`) fill, 1pt dark red border, centered bold title (optionally a smaller-italic subtitle line).
   - Each "connector" row is a borderless, fillless row containing a centered dark red vertical-bar character (`│`).
   - Parent boxes span their children's columns via cell merges.
   - Detect the ASCII diagram source by checking for known structural strings (e.g., "Unified Command" + "RTF" for the URVI org chart) and route to the structured-table renderer.

4. **Adds running header** on pages 2 and beyond:
   ```python
   section = doc.sections[0]
   section.different_first_page_header_footer = True
   # Add header with document title and page number to section.header
   # Leave section.first_page_header blank
   ```

5. **Sets heading paragraph format:**
   ```python
   heading_paragraph.paragraph_format.keep_with_next = True
   ```

6. **Saves the file:**
   ```python
   output_path = "restoration_project/FINAL_DOCUMENT.docx"
   doc.save(output_path)
   print(f"Saved: {output_path}")
   ```

7. **Attempts PDF conversion.** Try, in order:

   **macOS path (preferred when LibreOffice is absent):**
   ```applescript
   tell application "Microsoft Word"
       activate
       open file name "<docx-abs-path>"
       set theDoc to active document
       update fields theDoc      -- populates the Word TOC field
       save theDoc                -- re-saves the .docx with TOC text baked in
       close theDoc saving no
   end tell
   ```
   Then:
   ```applescript
   tell application "Pages"
       activate
       set theDoc to open (POSIX file "<docx-abs-path>")
       delay 2
       export theDoc to (POSIX file "<pdf-abs-path>") as PDF
       close theDoc saving no
   end tell
   ```
   Word for Mac's AppleScript dictionary varies by version and frequently rejects `save as <doc> file format format PDF` with `-1708` "doesn't understand". Use Word only to refresh fields, then hand the .docx to Pages for the actual PDF export — Pages handles this reliably across versions.

   **Linux / LibreOffice path:**
   ```python
   result = subprocess.run(
       ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir",
        "restoration_project", output_path],
       capture_output=True, timeout=60
   )
   ```

   If both fail, print: "PDF conversion not available — open the .docx in Word and use File → Save As → PDF."

8. **Set `<w:updateFields w:val="true"/>` in `word/settings.xml`** so the TOC field auto-populates when the document is opened. Without this, the TOC shows "Right-click and choose Update Field to populate the Table of Contents." until the user manually refreshes.

9. **Replace any plain-text TOC in the source content with a Word TOC field.** When parsing, detect the "TABLE OF CONTENTS" Heading 2 and:
   - Render the heading itself
   - Insert a TOC field (`TOC \o "1-3" \h \z \u`) immediately after
   - Suppress all subsequent blocks (list items, hyphenated dot-leader lines) until the next Heading 2

10. **Suppress redundant duplicates:**
    - The first H1 (document title) — already rendered as the cover; don't render it in the body
    - Any paragraph whose text equals the immediately-preceding heading text (e.g., `**FIGURE 1: EXAMPLE BASIC URVI ORGANIZATION**` right after `## FIGURE 1: EXAMPLE BASIC URVI ORGANIZATION`)
    - Cover-page subtitle/prep lines that appear in the source markdown before the first H2 (already rendered programmatically on the cover)

---

## Step 5: Self-Verify

Run these checks after the script completes:

```python
import os
from docx import Document

path = "restoration_project/FINAL_DOCUMENT.docx"

# Check file exists and has real content
assert os.path.exists(path), "File not created"
assert os.path.getsize(path) > 5000, f"File too small: {os.path.getsize(path)} bytes"

# Check section count
doc = Document(path)
headings = [p for p in doc.paragraphs if p.style.name.startswith('Heading')]
print(f"Headings in document: {len(headings)}")
print(f"Total paragraphs: {len(doc.paragraphs)}")
print(f"Tables: {len(doc.tables)}")
print("Verification complete.")
```

If the file size is suspiciously small or heading count is zero, investigate and fix the parsing script before reporting completion.

---

## Step 6: Update STATUS.md

```
| 10 | doc-assemble | ✅ Complete | FINAL_DOCUMENT.docx generated ([X] pages, [Y] sections) |
```

---

## Step 7: Signal Completion

```
✅ Restoration complete.

Your document is ready: restoration_project/FINAL_DOCUMENT.docx
[If PDF generated]: PDF also saved: restoration_project/FINAL_DOCUMENT.pdf

Document stats:
  - Sections: X
  - Total headings: X
  - Tables: X
  - Estimated pages: X (based on word count)

Style applied: [document type] format

To create a PDF (if not auto-generated):
  Open FINAL_DOCUMENT.docx in Microsoft Word → File → Save As → PDF
  This preserves colors and fonts exactly.

The full pipeline is complete. All intermediate files are saved in restoration_project/ 
for reference or if you need to re-run any step.
```
