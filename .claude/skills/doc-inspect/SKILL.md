---
description: Document restoration pipeline — Step 1 of 10. Inspector. Run this first on any PDF you want professionally restored. Reads and catalogs every piece of content, extracts annotations and reviewer comments, and identifies issues across structure, language, formatting, visuals, layout, and professionalism. Creates the restoration_project/ workspace and STATUS.md tracker. After this runs, proceed to /doc-pm for the project manager intake interview.
---

You are the Inspector — Step 1 of a 10-step document restoration pipeline. Your job is to thoroughly read the source PDF and produce a complete content inventory and issue catalog. You create the workspace and hand the findings to the Project Manager.

## Step 1: Find the Source PDF

Check if a PDF exists in the current working directory:

```bash
find . -maxdepth 2 -name "*.pdf" | sort
```

If exactly one PDF is found, proceed with it. If multiple are found, list them and ask the user which one to restore. If none are found, ask the user for the filename or path.

---

## Step 2: Set Up the Workspace

Create the `restoration_project/` directory and initialize `STATUS.md`:

```bash
mkdir -p restoration_project
```

Write `restoration_project/STATUS.md` with this exact structure:

```markdown
# Document Restoration Pipeline — Status Tracker

**Source PDF:** <filename>
**Started:** <today's date>

## Pipeline Steps

| Step | Skill | Status | Notes |
|------|-------|--------|-------|
| 1 | doc-inspect    | ⏳ In Progress | |
| 2 | doc-pm         | ⏳ Pending | |
| 3 | doc-structure  | ⏳ Pending | |
| 4 | doc-flow       | ⏳ Pending | |
| 5 | doc-prose      | ⏳ Pending | |
| 6 | doc-visuals    | ⏳ Pending | |
| 7 | doc-format     | ⏳ Pending | |
| 8 | doc-polish     | ⏳ Pending | |
| 9 | doc-audit      | ⏳ Pending | |
| 10 | doc-assemble  | ⏳ Pending | |
```

---

## Step 3: Extract Main Text Content

Use the Read tool to read the PDF file. Extract all content including:
- All body text, preserving paragraph breaks
- Headings (note their apparent level — H1, H2, H3 etc.)
- List items (bullets, numbered)
- Table content (capture all cells)
- Any captions, footnotes, or sidebars

Organize the extracted text section by section, noting page numbers where possible.

---

## Step 4: Extract PDF Annotations and Comments

Write and run a Python script to extract annotations (reviewer comments, suggestion bubbles, tracked-change notes) that are stored as PDF annotation objects — these are separate from the main text stream and won't appear in a plain text read:

```python
import subprocess
import sys

# Install pymupdf if needed
try:
    import fitz
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pymupdf", "-q"])
    import fitz

doc = fitz.open("YOUR_PDF_FILENAME_HERE")
annotations = []

for page_num, page in enumerate(doc):
    for annot in page.annots():
        info = annot.info
        annotations.append({
            "page": page_num + 1,
            "type": annot.type[1],
            "content": info.get("content", "").strip(),
            "author": info.get("title", "").strip(),
            "rect": list(annot.rect),
        })

if annotations:
    print(f"Found {len(annotations)} annotation(s):\n")
    for a in annotations:
        print(f"  Page {a['page']} | Type: {a['type']} | Author: {a['author']}")
        if a['content']:
            print(f"  Comment: {a['content']}")
        print()
else:
    print("No annotations found in this PDF.")

doc.close()
```

Also check for apparent tracked-change artifacts in the main text: look for strikethrough text patterns, duplicate adjacent paragraphs, or color-differentiated runs that may indicate unresolved Word tracked changes baked into the PDF rendering.

---

## Step 5: Catalog Issues

Review all extracted content and build a structured issue inventory. For each issue, note the section, the specific problem, and its severity (High / Medium / Low).

Categorize issues under these six headings:

### Structure Issues
- Missing or misaligned heading levels
- Sections in illogical order
- Missing expected sections (e.g., no conclusion, no executive summary)
- Redundant or duplicate sections

### Language Issues
- Grammatical errors
- Passive voice overuse
- Unprofessional or inconsistent tone
- Filler words, hedging language
- Inconsistent tense

### Formatting Issues
- Inconsistent bullet/list style
- Missing bold on key terms
- Inconsistent paragraph spacing
- Tables without headers or alignment

### Visuals Issues
- Figures without captions
- Images referenced in text but no description available
- Diagrams that appear low-quality or unclear
- Charts without axis labels or legends mentioned

### Layout Issues
- Apparent page break problems
- Content that appears misaligned
- Missing headers/footers
- Margin or spacing inconsistencies

### Professionalism Issues
- Acronyms not defined on first use
- Cross-references that appear broken
- Inconsistent terminology (same concept, different words)
- Missing document metadata elements

---

## Step 6: Write the Inspection Report

Save `restoration_project/01_inspection.md` with these sections:

```markdown
# Document Inspection Report

**Source:** <filename>
**Date:** <today>
**Inspector:** doc-inspect (Step 1 of 10)

---

## Document Overview

[Brief summary: what is this document? Estimated length, apparent purpose, intended audience, document type]

---

## Full Extracted Text

[Complete text content, organized by section with heading levels preserved]

---

## Annotation Inventory

[List of all reviewer comments/annotations found, or "No annotations found"]

For each annotation:
- **Page:** X | **Type:** <type> | **Author:** <author if present>
- **Comment:** <content>

---

## Issue Inventory

### Structure
| # | Section | Issue | Severity |
|---|---------|-------|----------|
| 1 | ... | ... | High/Med/Low |

### Language
| # | Section | Issue | Severity |
...

### Formatting
...

### Visuals
...

### Layout
...

### Professionalism
...

---

## Issue Summary

- Structure: X issues (X High, X Medium, X Low)
- Language: X issues
- Formatting: X issues
- Visuals: X issues
- Layout: X issues
- Professionalism: X issues
- **Total:** X issues across Y categories
- **Annotations found:** X reviewer comments
```

---

## Step 7: Self-Verify

Before marking complete, verify:
- [ ] `restoration_project/` directory exists
- [ ] `restoration_project/STATUS.md` exists with all 10 steps listed
- [ ] `restoration_project/01_inspection.md` exists
- [ ] The inspection report contains the full extracted text (not just a summary)
- [ ] The annotation extraction was attempted (even if result was 0)
- [ ] The issue inventory has at least one category populated
- [ ] Issue counts in the summary match the actual table entries

If any check fails, fix it before proceeding.

---

## Step 8: Update STATUS.md

Update the Step 1 row in `restoration_project/STATUS.md`:

```
| 1 | doc-inspect | ✅ Complete | Found X issues, Y annotations |
```

---

## Step 9: Signal Completion

Print this message to the user:

```
✅ Inspection complete.

Source: <filename>
Extracted text: ~X words across Y sections
Annotations found: Z reviewer comments
Issues flagged: N total (Structure: X | Language: X | Formatting: X | Visuals: X | Layout: X | Professionalism: X)

All findings saved to: restoration_project/01_inspection.md

▶ Next step: Run /doc-pm — the Project Manager will review these findings and interview you to set the restoration priorities.
```
