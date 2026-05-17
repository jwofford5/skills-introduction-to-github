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
   - `*italic text*` → italic run within paragraph (single asterisk; must NOT swallow `**bold**`)
   - `` `code` `` → monospace run
   - `> blockquote` → callout box (rendered as Word table — see step 4)
   - ` ```fenced code``` ` → Courier code block, or routed to structured diagram renderer if the code matches a known diagram fingerprint (see step 5)
   - `| col | col |` table syntax → Word table
   - `<!-- ... -->` HTML comments → skip (do not render)
   - Blank line between paragraphs → paragraph break
   - `---` → horizontal rule / visual separator (do NOT auto-convert to page break)

   **Inline parsing must use ordered-alternation regex** so `**bold**` is consumed as bold before its inner content matches the `*italic*` rule. A naïve `*[^*]+*` pattern run first will eat the inner half of every bold run. Reference pattern: `(\*\*[^*]+\*\*|`[^`]+`|\*[^*\n]+?\*)` with bold matched first. Italic uses non-greedy single-line matching so an unmatched asterisk in a long paragraph doesn't swallow downstream text.

2. **Derives styling from the document's actual context** — in this order of priority:

   1. **Layout Notes in `06_formatted.md`** (highest priority) — the Painter captured the document's real design decisions: colors, fonts, spacing, callout box specs, accent colors, special elements. These always override the baseline defaults below.
   2. **WORK_ORDER.md** — the document type and any user-stated style preferences.
   3. **Baseline defaults by document type** (lowest priority — fallback only for properties not specified above):

   > **Important:** Colors, accent schemes, callout boxes, special borders, and any other design element documented in the Layout Notes or visible in the original document are part of the document's identity — apply them faithfully. Do not strip design choices based on document type assumptions.

   **Corporate / Government baseline:**
   - Font: Times New Roman, 11pt body
   - Heading 1: Times New Roman 18pt, bold, dark red (#8B0000) — used for the cover title only
   - Heading 2 (numbered sections): Times New Roman 14pt, bold, ALL CAPS, black, with 1pt dark red horizontal rule below; `keep_with_next` = True
   - Heading 3 (subsections): Times New Roman 12pt, bold, Title Case, black; `keep_with_next` = True
   - Heading 4 (sub-subsections): Times New Roman 11pt, bold, italic, black; `keep_with_next` = True
   - Margins: 1 inch all sides
   - Line spacing: 1.15 or as noted in layout annotations
   - Color: black for body and most headings; dark red (#8B0000) as accent for cover, heading rules, callout headers, and figure-table borders
   - **No `page_break_before` on Heading 2.** Sections flow naturally. The only forced page breaks are: (1) after the cover page, and (2) after the TOC field — so the first body section starts at the top of a fresh page. Both are deliberate front-matter transitions, not stranded mid-section whitespace. Do NOT force breaks between body sections — that strands half-empty pages and looks unprofessional.

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
   - **Use spacer columns between sibling nodes.** Adjacent cells with dark red borders share an edge and read as one wide compartmentalized block, not as separate boxes. Insert a narrow no-border, no-fill column between each pair of siblings so each node is a visibly separate box with whitespace around it. For an N-leaf chart: build a `(2N - 1)`-column grid where odd-indexed columns are spacers and even-indexed columns are content. Reasonable widths: 1.30" per content column, 0.43" per spacer (4 content + 3 spacers = ~6.5" content width on Letter).

6. **Set table column widths on `w:tblGrid` / `w:gridCol`, not just `cell.width`.** This is a non-obvious OOXML requirement that bit us during the org-chart rebuild: setting only `cell.width = Inches(X)` was *not* enough — Word and Pages applied autofit and collapsed the narrow spacer columns to almost nothing, breaking the layout. For any layout-critical table (callout boxes, org charts, comparison tables with intentionally uneven columns), assign widths directly to the `w:gridCol` elements in `w:tblGrid` (twips, where 1" = 1440):

   ```python
   tblGrid = table._tbl.find(qn("w:tblGrid"))
   for gridCol, width_in in zip(tblGrid.findall(qn("w:gridCol")), col_widths_in):
       gridCol.set(qn("w:w"), str(int(width_in * 1440)))
       gridCol.set(qn("w:type"), "dxa")
   ```

   Combine with `table.autofit = False` and matching `cell.width` per column. Skipping the `tblGrid` step yields visually-wrong renders that pass automated checks (heading count, table count, file size) but fail visual inspection.

7. **Adds running header** on pages 2 and beyond:
   ```python
   section = doc.sections[0]
   section.different_first_page_header_footer = True
   # Add header with document title and page number to section.header
   # Leave section.first_page_header blank
   ```

8. **Sets heading paragraph format:**
   ```python
   heading_paragraph.paragraph_format.keep_with_next = True
   ```

9. **Binds tight lists so they don't split across pages.** A list of ≤ 6 items (the "tight list" threshold) should stay together as a single block. Apply `keep_with_next` to every list item except the last, so Word treats the list as one indivisible group. Additionally, if a tight list immediately follows a paragraph that ends with a colon (a classic introducer pattern, e.g., "The MARCH algorithm steps:"), apply `keep_with_next` to that paragraph too — otherwise the lead-in can strand at the bottom of one page while its bullets continue on the next. For lists of > 6 items, allow natural pagination so a long list doesn't push half a page of white space ahead of itself.

10. **Saves the file:**
    ```python
    output_path = "restoration_project/FINAL_DOCUMENT.docx"
    doc.save(output_path)
    print(f"Saved: {output_path}")
    ```

11. **Attempts PDF conversion.** Try, in order:

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

12. **Set `<w:updateFields w:val="true"/>` in `word/settings.xml`** so the TOC field auto-populates when the document is opened. Without this, the TOC shows "Right-click and choose Update Field to populate the Table of Contents." until the user manually refreshes.

13. **Replace any plain-text TOC in the source content with a Word TOC field.** When parsing, detect the "TABLE OF CONTENTS" Heading 2 and:
    - Render the heading itself
    - Insert a TOC field (`TOC \o "1-3" \h \z \u`) immediately after
    - Suppress all subsequent blocks (list items, hyphenated dot-leader lines) until the next Heading 2

14. **Suppress redundant duplicates:**
    - The first H1 (document title) — already rendered as the cover; don't render it in the body
    - Any paragraph whose text equals the immediately-preceding heading text (e.g., `**FIGURE 1: EXAMPLE BASIC URVI ORGANIZATION**` right after `## FIGURE 1: EXAMPLE BASIC URVI ORGANIZATION`)
    - Cover-page subtitle/prep lines that appear in the source markdown before the first H2 (already rendered programmatically on the cover)

---

## Step 5: Self-Verify

### Automated checks (necessary but not sufficient)

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

Also string-check that each Work-Order-mandated change is present (e.g., for the URVI doc, that `Rescue Group Supervisor (RGS):` appears in Key Definitions, that `personal protective equipment (PPE)` is defined on first use, etc.).

If the file size is suspiciously small or heading count is zero, investigate and fix the parsing script before reporting completion.

### Visual inspection (required — automated checks miss layout bugs)

**Text-only checks do not catch layout problems.** Headings can be counted as correct while the page break falls in the wrong place. Tables can be detected as present while their borders render with gaps. This bit us during URVI restoration — the MARCH Algorithm definition rendered with its lead paragraph + first bullet on page 20 and the remaining four bullets on page 21. Every automated check passed; the doc was visually broken.

After generating the PDF, **read at least these pages** and confirm they look right:

1. **Cover page** — title centered, agency lines correct, version line at bottom
2. **Page 2** — TOC begins with no header on the cover (different-first-page header is working)
3. **The page after the TOC** — first body section starts at the top (forced page break landed correctly)
4. **Any page containing a callout box** — box borders are unbroken on all four sides, text wraps inside the box, no right-edge gap
5. **Any page containing a structured diagram** — sibling boxes are visibly separate (whitespace between them), connectors line up under their parents
6. **Every page containing a definition list, checklist, or bullet group that's referenced as a single unit in the Work Order** — confirm the group is intact on one page, not split mid-list
7. **The last page of the body** — no orphaned content; references and figures fit appropriately

If a visual issue exists, do not mark assembly complete. Fix the renderer (typically `keep_with_next`, cell shading, column widths via `w:tblGrid`, or page-break placement) and regenerate before claiming success.

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
