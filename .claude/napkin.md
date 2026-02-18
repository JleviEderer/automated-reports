# Napkin — PDF Report Generator

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|
| 2026-02-17 | user correction | Treated Content Agent's "Production Considerations" consolidation as a bug — it was good behavior | Content Agent consolidating scattered info into a new section is fine. Use `suggested_additions` frontmatter field so QA flags for human review without auto-failing. |
| 2026-02-17 | self | All images broken in PDF — relative path resolves to `/output/data/` | Image src must be `../data/filename.png` (relative to HTML in output/) or fix after generation with sed |
| 2026-02-17 | self | Recommendations heading + 1 line then ~50% blank (Run 1 p8, Run 2 p10) | Section header groups with `page-break-inside: avoid` push large blocks to next page. Must reduce header group size OR drop the section-level break before short sections entirely. |
| 2026-02-17 | self | Design Agent writes `data/` paths but HTML lives in `output/` | Always post-process: `sed -i 's|src="data/|src="../data/|g' output/report.html` |

## Design Lessons (per-run observations)
### Run 1
**Result: PASS WITH NOTES (11 pages, all images broken)**
- Slate blue accent, 2 fonts (EB Garamond + DM Sans) — both correct
- ALL images broken due to relative path bug (`data/` resolves to `/output/data/`)
- Content Agent consolidated fabrication mentions into "Production Considerations" — good synthesis, but we incorrectly treated it as a bug
- Page 8 density problem: Recs heading + 1 line + 55% blank
- Good: variant tags, two-column layouts, rating pills, callout box

### Run 2
**Result: PASS WITH NOTES (13 pages, all images render)**
- Images fixed via sed path rewrite (`data/` → `../data/`). All 7 images render perfectly.
- "Production Considerations" removed — in hindsight this was a regression, not a fix. The consolidation was useful.
- Fonts and accent color maintained from Run 1. No regressions.
- Page 10 SAME density problem as Run 1: Recommendations heading + 1 intro sentence + ~45% blank at bottom. The "section-divider-light" fix reduced spacing but didn't prevent the heading protection group from creating dead space when the next content block (Tier 1) won't fit.
- Page 2: Design Principles heading at bottom with intro + ~25% blank — acceptable since heading has body text.
- Pages 4-8: billboard images render beautifully at good size. Figcaptions are clean italic.
- Page 9: Comparative table + V4 conclusion — very dense, good.
- Page 12: two-column appendix (color swatches + typography notes) looks polished.
- Page 13: Image inventory + footer with working logo. Final page exempt from density.
- Went from 11 pages (Run 1, no images) to 13 pages (with images) — expected increase.

### Run 3
**Result: PASS (11 pages, all images render, no density issues)**
- Design Agent wrote `../data/` paths directly — no post-processing needed. All 7 images render.
- No consolidated sections (Production Considerations was suppressed). In hindsight, the Content Agent should have been allowed to consolidate with a `suggested_additions` frontmatter marker.
- Lighter heading treatment for Recommendations: no SECTION label, no decorative rule, no wrapping container. Just `<h2>` with `page-break-after: avoid`. This eliminated the density problem from Runs 1-2.
- Page 7 (v3.1 billboard + Single Wolf intro): images render beautifully, good density, variant tags work well.
- Page 8 (Single Wolf analysis + Comparative Evaluation heading): billboard image renders, comparative table heading lands naturally at bottom with intro text — no trapped whitespace.
- Page 9 (Comparative matrix table + Distance Readability): table renders cleanly without splitting. Distance readability section flows naturally with 1000+ft / 500ft / 200ft distance markers.
- Page 10 (Recommendations): THE FIX WORKED. Recommendations heading with full Tier 1 + Tier 2 content + "Bridging the Two Flagships" callout — all on one page. No density gap. ~85% filled.
- Page 11 (Appendix): Two-column layout (color swatches + typography). Image inventory table. Footer with CCH logo renders. Clean final page.
- Down from 13 pages (Run 2) to 11 pages — tighter layout without sacrificing readability.
- Clean QA PASS — no issues, no notes blocking.

## Patterns That Work
- Slate blue accent (#4a6580) for consultant reports
- Two-column layout for shorter parallel content (Design Principles, Appendix)
- Variant tags with colored slate-blue background
- Callout/pull-quote boxes for key conclusions
- Continuous flow with visual dividers instead of forced page breaks
- Tell Design Agent to use `../data/` paths directly (eliminates post-processing)
- `page.wait_for_function` to verify all images loaded before PDF render
- Billboard images at ~80% width with italic figcaptions look professional
- Lighter heading treatment (just `<h2>` + `page-break-after: avoid`, no section label/rule/container) for sections after dense content — prevents trapped whitespace
- Content Agent marks consolidated sections via `suggested_additions` frontmatter — QA flags for human review without auto-failing

## Patterns That Don't Work
- `src="data/"` in HTML living in `output/` — resolves to wrong directory
- Design Agent adding sections on its own (without Content Agent's `suggested_additions` marking)
- Section header groups (`page-break-inside: avoid`) on SECTION labels create dead space when content after the intro won't fit on the same page — the heading protection works but traps whitespace
- Putting section-level dividers before short end-of-page sections (Distance Readability → Recommendations transition is the worst offender)

## Graduation Queue
All lessons promoted. Queue empty.

### Promoted to permanent rules:
- `../data/` image paths → `design.md` File Contract
- Lighter heading for short sections → `design.md` Page Break Strategy
- `suggested_additions` frontmatter flow → `content.md` Writing Rules + `design.md` File Contract + `qa.md` Content checklist + `consultant-report.yaml` structure
- `page.wait_for_function` image load verification → `CLAUDE.md` Stage 3
