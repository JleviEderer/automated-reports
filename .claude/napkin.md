# Napkin — PDF Report Generator

## Corrections
| Date | Source | What Went Wrong | What To Do Instead |
|------|--------|----------------|-------------------|
| 2026-02-17 | user correction | Treated Content Agent's "Production Considerations" consolidation as a bug — it was good behavior | Content Agent consolidating scattered info into a new section is fine. Use `suggested_additions` frontmatter field so QA flags for human review without auto-failing. |
| 2026-02-17 | self | All images broken in PDF — relative path resolves to `/output/data/` | Image src must be `../data/filename.png` (relative to HTML in output/) or fix after generation with sed |
| 2026-02-17 | self | Recommendations heading + 1 line then ~50% blank (Run 1 p8, Run 2 p10) | Section header groups with `page-break-inside: avoid` push large blocks to next page. Must reduce header group size OR drop the section-level break before short sections entirely. |
| 2026-02-17 | self | Design Agent writes `data/` paths but HTML lives in `output/` | Always post-process: `sed -i 's|src="data/|src="../data/|g' output/report.html` |
| 2026-02-19 | user correction | Content/Design Agents hallucinated ticker "ABX:TSX" (Barrick Gold) — correct ticker is "ABXX:CBOE Canada" (Abaxx Technologies). No source file contained the wrong ticker. Napkin then recorded it as a "pattern that works," laundering the hallucination into future runs. | Never fabricate company metadata (tickers, exchanges, legal names). If not in source material, omit or mark [VERIFY]. When promoting napkin observations to patterns, verify that verifiable facts trace back to source data, not agent fabrication. |

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

### Run 4 (Marketing Report — Abaxx Technologies)
**Result: PASS WITH NOTES (15 pages, 2 iterations)**
- Preset: marketing-report. Deep navy (#1A1A2E) + gold (#D4AF37) accent. DM Sans headings + Libre Baskerville body.
- Iteration 1 FAIL: Two orphaned headings (pages 2 and 12). Fixed by extending `.section-header-group` wrappers to include first `<p>`.
- Iteration 2 PASS WITH NOTES: Both fixes confirmed. Path Forward section flagged as suggested addition.
- CSS double-margin bug: `.section { padding: 0 1.25in }` doubled with `@page { margin: 1.25in }` → 23 pages. Fixed with `@media print` rules zeroing section padding.
- Cover page text flush left after print fix: cover uses `@page :first { margin: 0 }` so needs its own padding restored in print media query.
- Stage 0.5 (Source Manifest) consumed excessive main-agent context by reading all 21 source files directly. Moved to subagent to preserve context window.
- Port management: test ports before using. Had to cycle through 8765→8766→8767.

### Run 5 (Marketing Report v2 — Run 1 of 3)
**Result: PASS WITH NOTES (18 pages, 1 iteration)**
- Preset: marketing-report. Deep navy (#1A2B4A) + gold (#C8A55A) accent. DM Sans headings + Libre Baskerville body.
- Clean first-pass QA: no orphaned headings, no density failures, all metrics verified.
- Two suggested additions flagged: "Weather Derivatives" and "Abaxx-MineHub Supply Chain Integration."

**What works well:**
- Cover (p1): Navy gradient + gold accent rule + white DM Sans title. Clean and minimal.
- Metric cards (p3, p5): Gold values on white background with gray labels. Strong visual anchors.
- Pull quotes (p2, p6, p9, p11): Gold left border + italic text. Good distribution (~1 per 3 pages).
- Section labels (gold small caps overline) create clear hierarchy without forced page breaks.
- Callout box styling is consistent and effective throughout.
- Pages 4, 5, 6, 7, 8, 9, 11, 12, 13 all have good density (75-95%).

**Improvements needed for Run 2:**
1. **Cover too static for marketing preset** — preset says "Can include a hero element, tagline, or key visual. More dynamic layout." Current cover looks consultant-grade, not marketing-grade. Add a bold key stat, tagline, or stronger visual hierarchy.
2. **Page 8 is a wall of text** — 95% filled with zero visual elements. Needs a pull quote or stat callout to break monotony. This is the Digital Title section's densest block.
3. **Page 10 only ~60% filled** — ID++ section ends mid-page. The "Legal Finality" section header group on p11 should flow onto p10 with lighter heading treatment (bare `<h2>`, no section label/rule/container). This is the same trapped-whitespace pattern from Runs 1-3.
4. **"Global Network Expansion" (p14) lacks section label** — all other sections have gold overline labels. This section has none, breaking visual consistency. Either add the label or use it as a deliberate de-emphasis.
5. **No two-column layouts used** — marketing preset explicitly allows "Two columns acceptable for feature sections." The product pipeline (p14) or network regions (p14-15) could use a two-column treatment for visual variety.
6. **Page 18 final page** — disclaimer could be smaller/lighter. The "The early evidence says yes." closer is strong but the disclaimer styling is too prominent.
7. **18 pages is long** — could tighten by flowing sections more continuously. Pages 10, 14, and 15 have room to absorb content from subsequent pages.
8. **More stat callouts possible** — marketing preset is "brand-forward." Key stats like "$1T in collateral," "First VCM physical delivery," "680+ Chinese firms" could be highlighted with stat cards like p3/p5.

### Run 6 (Marketing Report v2 — Run 2 of 3)
**Result: PASS WITH NOTES (19 pages, 2 iterations — 1st was FAIL due to cover overflow + orphaned heading)**
- Cover overflow: `min-height: 100vh` doesn't map to one printed page → spilled onto page 2. Fixed with `height: 10in`.
- Orphaned heading: "Global Network Expansion" section-header-group didn't include first paragraph → naked heading at page bottom. Fixed by wrapping stat-callout + first `<p>` inside the group.
- After fixes: 19 pages, clean PASS WITH NOTES.

**What improved from Run 1 (Run 5):**
- Cover (p1): dramatically better — key stats ($850M, 150+, Q3 '25, $50M+), gold tagline "Exchange · Digital Title · Identity Infrastructure", "Investor Overview" label. Truly marketing-grade.
- Stat callouts throughout: 9,486 (LNG), "First" (VCM), "$1 Trillion" (collateral), "3 Pilots", "680+" (Chinese firms), "10K/1M/50%" (scale metrics). Breaks up text walls effectively.
- Two-column layouts: pilot descriptions (p9, Gold/MMF/In-Transit) and product pipeline (p14, Silver/PGMs/Uranium/Weather). Excellent visual variety.
- Digital Title section (p8-9) no longer a text wall — $1T stat callout + 3 Pilots callout + two-column pilot grid.
- "Global Reach" section label added to Global Network Expansion — consistency restored.
- Disclaimer (p19) is smaller/lighter text — much more subtle.

**What still needs improvement for Run 3:**
1. **Page 14 (~50-55% filled)** — product pipeline two-column grid leaves significant whitespace below. The Global Network section header group (with stat + paragraph inside) is too large to flow onto this page. Solutions: (a) use lighter heading for Global Network (bare `<h2>`, no section label/rule) so it can start on p14, or (b) add the Robin Girmes weather quote as a pull quote to fill more of p14.
2. **Page 7 visual monotony** — "Why Incumbents" is all prose, no visual elements. Add a stat callout for "$9.3B ICE net revenues" or "59% operating margin" to break up the text and reinforce the argument.
3. **19 pages still long** — target was 15-16. Key opportunities to compress:
   - Pages 17-18 ("Macro Tailwind" + "What Comes Next") could share a page if headings use lighter treatment
   - Page 7 could flow more tightly from the Trojan Horse section on p6 if the section divider is lighter
4. **Cover `height: 10in`** — works for letter size but is fragile. Should use `height: 100%` or calculate from `@page` size minus margins. Add this to the graduation queue.
5. **Page 11 section transition** — "Legal Finality" heading with body text starts at bottom of page. No orphan (has ~4 lines below), but the heading lands very low. Acceptable but tight.

### Run 7 (Marketing Report v2 — Run 3 of 3)
**Result: PASS WITH NOTES (16 pages, 1 iteration — clean first-pass QA)**
- Down from 19 pages (Run 2) to 16 pages. Hit the 15-16 page target.
- First-pass QA pass — no FAIL iterations needed. All accumulated napkin lessons applied correctly by the Design Agent.

**What improved from Run 2 (Run 6):**
- **Page count 19→16**: Lighter heading treatments, continuous section flow, and tighter spacing compressed 3 full pages without sacrificing readability.
- **Page 7 ("Why Incumbents")**: $9.3B stat callout added — was all-prose in Runs 1-2. Now has strong visual anchor at top of page. Four substantial paragraphs below fill the page well.
- **Page 13 (Product Pipeline + Global Network)**: Four-card two-column grid (Silver, PGMs, Uranium, Weather) flows directly into "Global Network Expansion" with 680+ stat callout and two paragraphs — all on one page. The lighter heading treatment for Global Network (bare `<h2>`, no section label/rule) allows it to flow naturally from the pipeline content. This was the p14 density problem from Run 2, now eliminated.
- **Pages 14-15 (Path to Scale + Macro Tailwind + What Comes Next)**: Three sections share two pages with continuous flow. In Run 2 these occupied pages 15-18 (four pages). The lighter heading treatment and removal of heavy section dividers between late sections enabled the compression.
- **Page 8 (Digital Title)**: $1 Trillion stat callout + 3 Pilots stat callout create excellent visual rhythm. Was a text wall in Run 1.
- **Page 9 (Digital Title cont. + ID++)**: Three pilot cards in two-column + single-card layout. TAM paragraph. ID++ section begins. Dense and visually varied.
- **Cover (p1)**: Maintained all Run 2 improvements — eyebrow with ABXX:CBOE Canada ticker, key stats ($850M, 150+, Q3 '25, $50M+), gold tagline, "Investor Overview" label. No regressions.

**Remaining minor issues (not worth another iteration):**
1. **Page 16 disclaimer spillover** — two lines of disclaimer text on an otherwise blank final page. Could tighten disclaimer or adjust p15 spacing to absorb. Exempt from density rule. Purely cosmetic.
2. **Page 12 (~55-60% density)** — Weather Derivatives section is the lightest body page. Above threshold but visually lighter than neighbors. A pull quote from Robin Girmes would fill this out, but the Content Agent didn't include one in the source material.
3. **Cover `height: 10in`** — still using the fragile fixed height from Run 2's fix. Works for letter size but won't adapt to A4 or other page sizes. Needs a more robust solution (graduation queue item).

**Key takeaway:** The napkin-driven iteration loop works. Three runs progressively fixed: cover quality (static→marketing-grade), text walls (prose-only→stat callouts+cards), trapped whitespace (heavy headers→lighter treatment), and page count (18→19→16). All without modifying agent `.md` files — just injecting accumulated lessons into the Design Agent prompt.

### Run 8 (Marketing Report — standalone /run)
**Result: PASS WITH NOTES (13 pages, 1 iteration — clean first-pass QA)**
- Preset: marketing-report. Deep navy (#1a2332) + gold (#C8A55A) accent. DM Sans headings + Libre Baskerville body.
- Clean first-pass QA — no FAIL iterations needed. All accumulated napkin lessons applied correctly.
- 13 pages — shortest marketing report yet (vs 18→19→16 in Runs 5-7).
- 7 stat callouts, 2 pull quotes, 2 two-column card grids. Good visual variety.
- Two suggested additions flagged: "The Collateral Revolution" and "Why Incumbents Cannot Replicate This."
- Page 13 final page ~30% filled (exempt). Bullet list on p12 at max 5 items (acceptable).
- All data integrity checks passed — manifest conflict resolutions correctly followed.
- No orphaned headings, no density failures, no text walls.
- Port management: killed stale python processes before starting server. Used port 8770.

**What worked well:**
- Injecting accumulated design lessons directly into the Design Agent prompt continues to produce first-pass QA passes.
- 13 pages is notably compact for the same source material that produced 18 pages in Run 5. The lighter-headings-in-final-third rule and continuous flow are well internalized.
- Cover maintained marketing-grade quality with key stats, gold tagline, ABXX:CBOE Canada eyebrow.
- Source Manifest Agent handled all 21 files cleanly in subagent (39 metrics, 5 conflicts).

## Hallucination Laundering Risk

When promoting napkin observations to "Patterns That Work," verify that the "pattern" traces back to source data, not to an agent's fabrication. The napkin is a self-reinforcement loop — if a hallucinated fact enters an observation (e.g., "ABX:TSX eyebrow looks good"), it gets promoted to a pattern, then injected into future agent prompts as validated truth.

**Rules:**
- Any pattern involving verifiable external facts (ticker symbols, exchange names, legal entity names, founding dates, URLs, officer titles) must be confirmed against source material before graduation.
- Flag these patterns for human confirmation — do not auto-graduate them.
- If a correction invalidates a pattern, update ALL references in the napkin (observations, patterns, graduation queue) in the same edit.

## Graduation Queue
- Stage 0.5 → subagent: promoted to CLAUDE.md + new agent prompt at `.claude/agents/manifest/manifest.md`

### Candidates (from Runs 5-7):
- Cover `height: 10in` is fragile — needs a robust print-safe alternative. Consider `height: 100%` on `@page :first` context, or calculate from page size minus margins. Revisit when A4 support needed.
- Napkin-driven iteration (injecting accumulated lessons into Design Agent prompt without modifying agent `.md`) is effective for multi-run refinement

### Promoted to permanent rules:
- `../data/` image paths → `design.md` File Contract
- Lighter heading for short sections → `design.md` Page Break Strategy
- `suggested_additions` frontmatter flow → `content.md` Writing Rules + `design.md` File Contract + `qa.md` Content checklist + `consultant-report.yaml` structure
- `page.wait_for_function` image load verification → `CLAUDE.md` Stage 3
- Stat callouts (gold/accent left border, large number, small label) → `design.md` Components + `marketing-report.yaml` + `consultant-report.yaml`
- Two-column card grids for pipeline/product lists → `design.md` Components + `marketing-report.yaml`
- Lighter headings in final third of document → `design.md` Page Break Strategy (strengthened from "short/late sections" to "final third" rule)
- Disclaimer must not spill onto separate page → `design.md` Components + `qa.md` Page Density & Breaks
