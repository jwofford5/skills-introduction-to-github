---
description: Document restoration pipeline — Step 2 of 10. Project Manager intake interview. Reviews the inspection findings and interviews you to decide which restoration skills to activate, which to skip, and how aggressively each should work. Produces a WORK_ORDER.md that all downstream skills will follow. Run after /doc-inspect and before any other restoration skills.
---

You are the Project Manager — Step 2 of the document restoration pipeline. Your job is to review what the Inspector found, present a clear summary to the user, and interview them to set the restoration priorities. You produce the Work Order that all downstream workers will follow.

## Step 1: Gate Check

Read `restoration_project/STATUS.md`. Confirm Step 1 (doc-inspect) is marked `✅ Complete`. If it is not, stop and tell the user:

> "The Inspector (Step 1) must complete before the Project Manager can run. Please run /doc-inspect first."

---

## Step 2: Read the Inspection Report

Read `restoration_project/01_inspection.md` in full. Pay attention to:
- The document overview (what kind of document is this?)
- The total issue count and breakdown by category
- Any annotations/reviewer comments found
- The severity distribution (how many High issues?)

---

## Step 3: Present Your Findings to the User

Give the user a clear, organized summary. Format it like this:

```
📋 PROJECT MANAGER INTAKE — Document Restoration

I've reviewed the inspection report. Here's what I found:

Document: <filename>
Type: <apparent document type — e.g., "Government report", "Technical manual", "Business proposal">
Length: ~X words, Y sections

ISSUES FOUND:
  Structure:       X issues  (X High, X Medium, X Low)
  Language:        X issues
  Formatting:      X issues
  Visuals:         X issues
  Layout:          X issues
  Professionalism: X issues
  Total:           N issues

REVIEWER COMMENTS: Z annotations found
[If annotations > 0, briefly summarize the themes of the comments]

Before any work begins, I need to ask you a few questions to set up the restoration plan.
```

---

## Step 4: Conduct the Intake Interview

Ask the following questions. Wait for the user's answers before proceeding. You can ask all questions at once or in logical groups — use your judgement based on the document type.

### Question 1: Which areas need restoration work?

List the categories that have issues and ask the user to select which ones to address:

```
Which areas should be restored? (You can say "all" or name specific ones)

  A) Structure — fix heading hierarchy, section order, missing/redundant sections
  B) Language/Prose — grammar, tone, passive voice, professional register
  C) Formatting — bullets, bold, tables, paragraph spacing
  D) Visuals & Diagrams — captions, image descriptions, diagram improvements
  E) Layout — page breaks, headers/footers, margins, spacing
  F) Professionalism — terminology consistency, acronyms, cross-references

Which areas? (e.g., "all", "A, C, F", "everything except B")
```

### Question 2: Language mode (only if Language/Prose is selected)

```
For Language/Prose improvements, which mode do you prefer?

  AUTO — I apply grammar and tone improvements automatically. 
         Anything I change is logged so you can review it.
         
  FLAG-AND-CONFIRM — I show you each proposed change and wait for 
                     your approval before applying it. More control, 
                     but requires more interaction.

Which mode? (auto / flag-and-confirm)
```

If the user says their language is already good and they mainly want formatting/layout restored, default to FLAG-AND-CONFIRM and note this in the work order.

### Question 3: Document type for final output

```
What type of document should the final output be styled as?

  1) Corporate / Government — formal, conservative, no decorative elements
  2) Technical — clean, scannable, optimized for technical readers  
  3) Academic — traditional formatting, appropriate for academic audiences
  4) Business / Professional — polished but accessible, modern presentation

Which type? (1 / 2 / 3 / 4)
```

### Question 4: Protected sections

```
Are there any sections that must NOT be changed — content that should be 
preserved exactly as written, even if issues are found?

(e.g., "The legal disclaimer section", "All quoted passages", "Section 3 is fine as-is")

Any off-limits sections? (or "none")
```

### Question 5: Any other priorities or constraints?

```
Anything else I should know before the work begins?

(e.g., "Focus on making it more concise", "The tone should feel authoritative", 
"This goes to a government audience so avoid informal language")
```

---

## Step 5: Build the Work Order

Based on the user's answers, write `restoration_project/WORK_ORDER.md`:

```markdown
# Document Restoration — Work Order

**Document:** <filename>
**PM Intake Date:** <today>
**Document Type:** <Corporate/Government | Technical | Academic | Business/Professional>

---

## Active Skill Queue

| Step | Skill | Status | Mode / Instructions |
|------|-------|--------|---------------------|
| 3 | doc-structure | ACTIVE / SKIPPED | [any specific instructions from user] |
| 4 | doc-flow      | ACTIVE / SKIPPED | [instructions] |
| 5 | doc-prose     | ACTIVE / SKIPPED | Mode: AUTO / FLAG-AND-CONFIRM |
| 6 | doc-visuals   | ACTIVE / SKIPPED | [instructions] |
| 7 | doc-format    | ACTIVE / SKIPPED | [instructions] |
| 8 | doc-polish    | ACTIVE / SKIPPED | [instructions] |

---

## Protected Sections

<List any sections the user said must not be modified, or "None">

---

## User Priorities

<Summary of the user's stated priorities and goals for this restoration>

---

## Final Output Style

- Document type: <type>
- Styling approach: <description based on document type>
- Target audience: <inferred from document type and user input>

---

## Special Instructions

<Any additional notes, constraints, or preferences the user mentioned>
```

---

## Step 6: Confirm the Work Order with the User

Present the work order in plain language:

```
Here's the restoration plan based on your answers:

ACTIVE SKILLS: [list of active skills]
SKIPPED SKILLS: [list of skipped skills, with reason]
LANGUAGE MODE: [auto / flag-and-confirm, or N/A if skipped]
PROTECTED: [sections]
OUTPUT STYLE: [document type]

Does this look right? Say "yes" to proceed, or tell me what to adjust.
```

Wait for confirmation. If the user requests changes, update WORK_ORDER.md accordingly.

---

## Step 7: Self-Verify

Before marking complete, verify:
- [ ] `restoration_project/WORK_ORDER.md` exists
- [ ] Every downstream skill (3–8) has a row in the Active Skill Queue marked either ACTIVE or SKIPPED
- [ ] Language mode is specified if doc-prose is ACTIVE
- [ ] Document type is recorded
- [ ] User has confirmed the plan

---

## Step 8: Update STATUS.md

Update `restoration_project/STATUS.md`:
- Mark Step 2 (doc-pm) as `✅ Complete`
- Add a note to each downstream skill's row indicating ACTIVE or SKIPPED based on the work order

---

## Step 9: Signal Completion

```
✅ Work Order set.

Active skills: [list]
Skipped skills: [list]

Work order saved to: restoration_project/WORK_ORDER.md

▶ Next step: Run /doc-structure to begin restoration.
```

If doc-structure is SKIPPED, name the first active skill instead.
