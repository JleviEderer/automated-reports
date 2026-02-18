# HANDOVER — Session 2026-02-17

## What We Were Working On

Two sequential tasks for the PDF Report Generator pipeline:

### Task 1: Implement Report Type Preset System

Created a preset system so the pipeline supports multiple report types (consultant, marketing, internal memo) without duplicating the entire pipeline. One pipeline, swappable YAML presets injected into agent prompts.

**Why:** Two bugs in the previous render — (1) the Design Agent used gold (#F2B705) as the report's accent color because it picked up the billboard's own palette from the content frontmatter, and (2) the Content Agent invented a "Production Considerations" section that doesn't exist in the source data.

**Status: COMPLETE.** All 8 implementation steps done.

### Task 2: Run Pipeline 3x with Iterative Learning

Ran the full Content Agent → Design Agent → PDF Render → QA Agent pipeline three times, self-reviewing every page screenshot after each run and recording findings in `.claude/napkin.md`. Each subsequent run applied lessons from the previous.

**Status: COMPLETE.** Run 3 achieved a clean QA PASS with all issues from Runs 1-2 resolved.

## Run-by-Run Results

| Run | QA Status | Pages | Images | Key Issues |
|-----|-----------|-------|--------|------------|
| 1 | PASS WITH NOTES | 11 | All broken | Path bug, invented section, density gap (p8) |
| 2 | PASS WITH NOTES | 13 | All render | Density gap persists (p10) |
| 3 | **PASS** | 11 | All render | All issues resolved |

## What Worked and What Didn't

### Bugs Found and Fixed

1. **All images broken in PDF (Run 1)**
   - **Root cause:** Design Agent wrote `src="data/CCH_Logo.png"` but HTML lives at `output/report.html`, so the browser resolves to `output/data/CCH_Logo.png` which doesn't exist.
   - **Run 2 fix:** Post-processed with `sed -i 's|src="data/|src="../data/|g' output/report.html`
   - **Run 3 fix (permanent):** Told Design Agent to write `../data/` paths directly. No post-processing needed.

2. **Design Agent invented "Production Considerations" section (Run 1)**
   - **Root cause:** Without explicit constraint, the Design Agent synthesized scattered fabrication mentions into a new appendix subsection.
   - **Fix:** Added explicit instruction: "Render ONLY sections present in content.md. Do not add, remove, or rename any section."
   - **Verified fixed in Runs 2 and 3.**

3. **Recommendations page density gap (Runs 1-2)**
   - **Root cause:** Section header groups (SECTION label + H2 + decorative rule) wrapped in `page-break-inside: avoid` were too tall. When landing near a page bottom, the next content block wouldn't fit, trapping ~45-55% whitespace.
   - **Run 2 attempted fix:** "section-divider-light" with reduced margins — didn't fully fix.
   - **Run 3 fix (permanent):** Removed full section header treatment for Recommendations/Appendix. Used just `<h2>` with `page-break-after: avoid`, no section label, no decorative rule, no wrapping container.

4. **Playwright Chrome launch failed**
   - **Root cause:** Chrome was already running; Playwright MCP couldn't launch a persistent context.
   - **Fix:** Used Python Playwright API (`sync_playwright`) instead of Playwright MCP browser tools or Node.js scripts.

5. **Node.js `require('playwright')` module not found**
   - **Root cause:** Playwright was installed via Python pip, not npm.
   - **Fix:** Used Python Playwright API for all rendering.

### Techniques That Work

- Slate blue accent (#4a6580) for consultant reports
- Two-column layout for appendix content (color swatches + typography)
- `page.wait_for_function` to verify all images loaded before `page.pdf()`
- Billboard images at ~80% width with italic figcaptions
- Telling Design Agent to use `../data/` paths directly (no post-processing)
- Lighter heading treatment for sections after dense content prevents trapped whitespace
- Explicit "render ONLY sections in content.md" instruction eliminates invented sections
- PyMuPDF (`fitz`) for extracting per-page screenshots from PDF at 150 DPI

### Techniques That Don't Work

- `src="data/"` in HTML living in `output/` — resolves to wrong directory
- Relying on Design Agent to stay faithful to content.md without explicit constraint
- Section header groups with `page-break-inside: avoid` on SECTION labels — traps whitespace
- Section-level dividers before short end-of-page sections

## Key Decisions Made

| Decision | Why |
|----------|-----|
| Preset system: one pipeline, swappable YAML presets | Avoids duplicating the pipeline for each report type |
| Three presets: consultant (default), marketing, internal-memo | Covers the main use cases with distinct aesthetic registers |
| Python Playwright over Node.js for PDF rendering | Node.js playwright module not installed; Python pip version works |
| `../data/` paths in Design Agent prompt (not post-processing) | More reliable, eliminates a pipeline step |
| Agent .md files not modified during 3-run iteration | User instruction — lessons captured in napkin.md for potential graduation |
| Preset injection between base prompt and task instructions | Clean separation: base rules are universal, preset narrows the aesthetic |

## Lessons Learned and Gotchas

1. **Content frontmatter colors are source data, not design instructions.** The billboard's palette (#F2B705 gold) must not leak into the report's accent color. The preset system and explicit frontmatter notes fix this.

2. **PDF page density must be checked from per-page PDF screenshots, not browser viewport screenshots.** Browser screenshots don't show page breaks.

3. **The Design Agent will invent content if not explicitly told not to.** Always include: "Render ONLY sections present in content.md."

4. **CSS heading protection groups can create worse problems than they solve.** A heading wrapped in `page-break-inside: avoid` with a large surrounding container will push the entire block to the next page, leaving dead space. Use minimal heading protection.

5. **Serve from project root for PDF rendering** so relative paths to `data/` resolve correctly from `output/report.html`.

6. **Google Fonts CDN dependency.** The template loads EB Garamond and DM Sans from Google Fonts. PDF rendering needs internet access.

7. **`generate.py` can't produce HTML from scratch.** It checks for an existing `output/report.html`. The Design Agent subagent must run first to create the HTML.

## Clear Next Steps

1. **Graduate napkin lessons to CLAUDE.md:** Three fixes are verified across 3 runs and marked as graduated in `.claude/napkin.md`. They should be added as permanent rules in CLAUDE.md's Design Agent spawning instructions:
   - Always tell Design Agent to use `../data/` image paths
   - Always include "render ONLY sections in content.md" constraint
   - Use lighter heading treatment for sections that follow dense content

2. **Test with a different report type:** Run the pipeline with `marketing-report` or `internal-memo` preset on different source material to verify the preset system generalizes.

3. **Consider automating the image path instruction:** Instead of relying on the prompt to tell the Design Agent about `../data/`, could add a post-generation path fix as a guaranteed pipeline step in `src/generate.py`.

4. **Page density validation in `src/validate.py`:** The current validator checks HTML heuristics but doesn't actually measure per-page fill. The QA Agent does this visually from screenshots. Could add programmatic density checking via PyMuPDF pixel analysis.

5. **Consider bundling fonts locally.** The `fonts/` directory exists but is empty. Google Fonts CDN dependency means PDF rendering fails offline.

## Map of Important Files

### Created This Session

| File | Purpose |
|------|---------|
| `presets/consultant-report.yaml` | Default preset — editorial, restrained, authoritative |
| `presets/marketing-report.yaml` | Persuasive, brand-forward preset |
| `presets/internal-memo.yaml` | Functional, direct, minimal styling preset |
| `.claude/napkin.md` | Per-run learning journal with corrections, patterns, graduation queue |
| `output/report.pdf` | Final 11-page PDF (Run 3, clean QA PASS) |
| `output/report.html` | Final HTML source for the PDF |
| `output/qa-report.json` | QA Agent's machine-readable verdict |
| `output/qa-report.md` | QA Agent's human-readable summary |
| `output/page-1.png` through `page-11.png` | Per-page PDF screenshots at 150 DPI |

### Modified This Session

| File | What Changed |
|------|-------------|
| `.claude/agents/content/content.md` | Added source-fidelity rule + frontmatter note |
| `.claude/agents/design/design.md` | Type-neutral role, accent color clarification, preset font note |
| `.claude/agents/QA/qa.md` | Parameterized thresholds (body size, max colors, structure rules) |
| `src/validate.py` | Removed billboard-specific hardcodes (image count, table requirement) |
| `src/generate.py` | Added `--preset` flag, `load_preset()`, flexible `load_data()` |
| `CLAUDE.md` | Added `presets/` to file structure, Presets section, updated spawning template |

### Key Pre-existing Files

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Master project instructions — pipeline stages, orchestration protocol, spawning template |
| `.claude/agents/content/content.md` | Content Agent system prompt |
| `.claude/agents/design/design.md` | Design Agent system prompt |
| `.claude/agents/QA/qa.md` | QA Agent system prompt |
| `.claude/hooks/check-qa-pass.py` | Stop hook — blocks agent exit until QA passes |
| `data/content.md` | Content Agent output (structured markdown with YAML frontmatter) |
| `data/*.png` | Source billboard images + CCH logo (7 files total) |
| `src/generate.py` | CLI orchestrator — PDF rendering, QA loop |
| `src/validate.py` | Static analysis validator — fonts, AI filler, structure |
