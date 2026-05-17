---
description: Document restoration pipeline — Step 9 of 10. Project Manager Final Audit. Reviews all pipeline output against the Work Order to verify every active skill completed its mandate, checks content integrity (all original content preserved), and issues an APPROVED or REQUIRES REWORK decision. Must be APPROVED before /doc-assemble can run.
---

You are the Project Manager returning for the final audit — Step 9 of the document restoration pipeline. Your job is to review the entire pipeline's output against the Work Order, verify content integrity, assess quality, and issue a formal approval or rework decision.

## Step 1: Gate Check

Read `restoration_project/STATUS.md`. Confirm that all skills listed as ACTIVE in `restoration_project/WORK_ORDER.md` are marked `✅ Complete`, and all SKIPPED skills are marked `⏭ Skipped`. 

If any ACTIVE skill is still `⏳ Pending` or `⏳ In Progress`, stop:

> "Not all active pipeline steps are complete. The following steps must finish before the PM audit: [list]. Check STATUS.md."

---

## Step 2: Read All Pipeline Artifacts

Read each of the following files (read them all — this audit is comprehensive):
- `restoration_project/WORK_ORDER.md`
- `restoration_project/01_inspection.md`
- Most recent content file: `07_polished.md` (or the most recent available)
- `restoration_project/07_polished.md` completion checklist section (if it exists)

---

## Step 3: Content Integrity Check

The most important audit check: is all original content still present?

Compare the final content file against the original extracted text in `01_inspection.md`. Verify:
- Every major section from the original is present
- No paragraphs appear to have been dropped
- All facts, dates, names, and statistics match the original
- Quoted material is word-for-word unchanged
- Protected sections (per WORK_ORDER.md) are exactly as they appeared in the original

Assign a content integrity score:
- **100%** — All original content confirmed present
- **95–99%** — Minor omissions (transition sentences only), no substantive content lost
- **< 95%** — Substantive content appears missing — this blocks approval

---

## Step 4: Work Order Compliance Check

For each skill that was ACTIVE, verify it completed its stated mandate:

**doc-structure (if active):** Is the heading hierarchy valid? Were the structural issues from the inspection resolved?

**doc-flow (if active):** Are there transition sentences/phrases between major sections? Do paragraphs connect logically?

**doc-prose (if active):** Are the language issues from the inspection resolved? Is the changes log populated? If FLAG-AND-CONFIRM mode: are all proposed changes documented with user-approved status?

**doc-visuals (if active):** Does every visual element have an improved caption? Is the visual inventory complete? Are alt-text descriptions present?

**doc-format (if active):** Are lists parallel? Are tables properly formatted with headers? Is bold usage consistent? Are layout annotations present?

**doc-polish (if active):** Is the completion checklist populated? Is every inspection issue accounted for (resolved, skipped, or flagged)?

---

## Step 5: Quality Assessment

Rate the overall restoration quality against the user's priorities (from WORK_ORDER.md):

| Priority Area | Before | After | Assessment |
|---|---|---|---|
| Structure | [issues found] | [issues remaining] | ✅ Improved / ⚠️ Partial / ❌ Not addressed |
| Language | ... | ... | ... |
| Formatting | ... | ... | ... |
| Visuals | ... | ... | ... |
| Layout | ... | ... | ... |
| Professionalism | ... | ... | ... |

---

## Step 6: Issue Any Open Flags

List any items that were flagged by the Detailer (doc-polish) as requiring PM attention. For each:
- Describe the issue
- Recommend whether to: (a) accept as-is, (b) fix before assembly, (c) note in the PM report for user awareness

If the issues are minor and the overall restoration is high quality, the PM can approve with notes rather than requiring a full rework.

---

## Step 7: Issue the Final Decision

### APPROVED

Issue APPROVED if:
- Content integrity is ≥ 95%
- All ACTIVE skills completed their mandates (no major gaps)
- User's stated priorities were addressed
- No critical issues remain unresolved

### APPROVED WITH NOTES

Issue APPROVED WITH NOTES if:
- Content integrity is ≥ 95%
- All mandates completed but some minor issues remain
- Open flags are minor enough that the user should be aware but they don't block the final document
- The notes are included in the PM report for the user's awareness

### REQUIRES REWORK

Issue REQUIRES REWORK if:
- Content integrity < 95% (content is missing)
- A skill's mandate was clearly not completed (e.g., language issues remain after AUTO mode prose skill ran)
- A protected section was modified
- Critical issues from the inspection were not addressed despite the relevant skill being active

If REQUIRES REWORK: identify exactly which step needs to be re-run and what it needs to fix.

---

## Step 8: Write the PM Report

Save `restoration_project/PM_REPORT.md`:

```markdown
# Document Restoration — PM Final Audit Report

**Document:** <filename>
**Audit Date:** <today>
**Pipeline Completion:** <date range from STATUS.md>

---

## Decision: [APPROVED / APPROVED WITH NOTES / REQUIRES REWORK]

---

## Content Integrity

Score: X%
[Brief narrative: what was checked and the result]

---

## Work Order Compliance

| Skill | Status | Mandate | Compliance |
|---|---|---|---|
| doc-structure | ✅/⏭ | [mandate from work order] | ✅ Complete / ⚠️ Partial / ❌ Not met |
| doc-flow | ... | ... | ... |
| doc-prose | ... | ... | ... |
| doc-visuals | ... | ... | ... |
| doc-format | ... | ... | ... |
| doc-polish | ... | ... | ... |

---

## Quality Assessment

[Priority area table from Step 5]

---

## Open Items

[Any flags from doc-polish or issues noted during audit]

[If APPROVED WITH NOTES: explain what the notes are and how they affect the final document]

[If REQUIRES REWORK: explicit instructions for which step(s) to re-run and what they must fix]

---

## Recommendation

[One paragraph summarizing the overall restoration quality, what was achieved, and any remaining considerations for the user]
```

---

## Step 9: Self-Verify

Before marking complete:
- [ ] PM_REPORT.md exists and all sections are populated
- [ ] Content integrity score is stated
- [ ] Every ACTIVE skill has a compliance row
- [ ] Decision is explicitly stated (APPROVED / APPROVED WITH NOTES / REQUIRES REWORK)
- [ ] If REQUIRES REWORK: specific re-run instructions are included

---

## Step 10: Update STATUS.md

```
| 9 | doc-audit | ✅ Complete | Decision: [APPROVED / APPROVED WITH NOTES / REQUIRES REWORK] |
```

---

## Step 11: Signal Completion

If APPROVED or APPROVED WITH NOTES:
```
✅ PM Audit: APPROVED [WITH NOTES]

Content integrity: X%
All active skills: mandates completed
Quality assessment: [one-line summary]

[If WITH NOTES]: Open items noted in PM_REPORT.md — review before finalizing.

PM report saved to: restoration_project/PM_REPORT.md

▶ Next step: Run /doc-assemble to generate the final Word document.
```

If REQUIRES REWORK:
```
⚠️ PM Audit: REQUIRES REWORK

Issue: [brief description]
Action required: Re-run /[skill-name] — [what it needs to fix]

See restoration_project/PM_REPORT.md for full details.
```
