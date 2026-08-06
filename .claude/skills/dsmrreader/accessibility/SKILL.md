---
name: accessibility
description: >
  Apply WCAG 2.2 AA accessibility standards when building or reviewing web UI code.
  Use this skill whenever the user asks to build, modify, or review any HTML, CSS, or
  frontend component — even if they don't explicitly mention accessibility. Also use it
  when the user asks to "make something accessible", "check for a11y issues", "add ARIA",
  fix keyboard navigation, or improve screen reader support.
---

# Accessibility (WCAG 2.2 AA)

Apply accessibility standards to all web UI work. Read `references/guidelines.md` for the
full reference — it covers semantic HTML, keyboard navigation, focus management, ARIA,
images/media, colour contrast, forms, motion, zoom, and a testing checklist.

## Workflow

**When building new UI:**
1. Use semantic HTML first — reach for ARIA only when native elements are insufficient.
2. After implementation, run through the **Testing Checklist** in `references/guidelines.md`.
3. Flag any items you cannot verify programmatically (screen reader behaviour, contrast on
   custom colours) so the user can check them manually.

**When reviewing existing UI:**
1. Scan for the **Common Mistakes** table in `references/guidelines.md` — these are the
   most frequent violations and the quickest wins.
2. Report findings grouped by severity: critical (blocks keyboard/screen reader users) →
   serious (WCAG failure) → moderate (best-practice gap).
3. Provide a concrete fix for each finding, not just a description of the problem.

## Non-negotiables

These four always apply, regardless of scope:

- Every `<img>` has a meaningful or empty `alt`.
- Every interactive element is reachable and operable by keyboard alone.
- Text contrast meets 4.5:1 (normal) / 3:1 (large / UI components).
- Every form input has a persistent, programmatically associated label.

## Quick reference

See `references/guidelines.md` for detailed rules on all 12 topic areas and the full
testing checklist to run before marking any feature complete.
