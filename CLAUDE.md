# PDF Report Generator

## Purpose
Automated pipeline for producing professional, editorial-quality PDF reports from raw source material — documents, markdown, images, and data files. Reports must look handcrafted — as if designed by a human at a boutique consulting firm or editorial publication. Not AI-generated.

## Architecture
- HTML templates + print-optimized CSS → rendered to PDF
- Python CLI orchestrator in `/src`
- Data input: raw files (markdown, documents, images, data files) in a project folder → Content Agent structures into markdown with YAML frontmatter → injected into templates
- Tool selection is flexible — agents choose the best libraries for templating, rendering, and conversion

## File Structure
```
├── CLAUDE.md
├── .claude/agents/              # Subagent system prompts
│   ├── manifest/manifest.md     # Source manifest agent
│   ├── content/content.md       # Content writing agent
│   ├── design/design.md         # HTML/CSS design agent
│   └── QA/qa.md                 # QA validation agent
├── presets/                # Report type presets (YAML)
│   ├── consultant-report.yaml   # Default — editorial, restrained
│   ├── marketing-report.yaml    # Persuasive, brand-forward
│   └── internal-memo.yaml       # Functional, direct
├── src/                    # Python orchestration
├── templates/              # HTML templates
├── styles/                 # Print CSS
├── data/                   # Input data
├── output/                 # Final PDFs
└── fonts/                  # Local font files (optional)
```

## Design Principles (Defaults — Presets Can Override)
- Serif body fonts (Georgia, Garamond, Libre Baskerville). Never Inter, Roboto, Arial, or system fonts.
- Max 3 colors per report (including black). One muted accent color used sparingly. Presets may adjust the limit.
- Generous margins (≥1 inch). Whitespace is a design element.
- Prose-first. Bullet lists max 3–5 items, max 2 lists per page. Default to paragraphs.
- No AI tells: no "It's worth noting," no filler, no hedging, no monotonous structure.
- Every report passes the "screenshot test" — no one would guess AI made it.

## Presets

Report type presets live in `presets/*.yaml`. Each preset defines per-agent overrides for tone, structure, aesthetics, and QA thresholds. The pipeline mechanics (Content → Design → PDF → QA → loop) are universal — only the instructions each agent receives change by type.

**Available presets:**
- `consultant-report` (default) — Analytical, editorial, restrained. McKinsey meets Monocle.
- `marketing-report` — Persuasive, brand-forward, bolder accent colors.
- `internal-memo` — Functional, direct, minimal styling.

**How presets are injected:** The orchestrator reads the preset YAML and inserts a `## Report Type Constraints` block into each agent spawn prompt, between the base agent `.md` and the task instructions. See the Spawning Template below.

**Preset YAML structure:**
```yaml
name: "Preset Name"
description: "One-line description"
content:    # Injected into Content Agent spawns
  tone: ...
  structure: ...
  frontmatter_note: ...
design:     # Injected into Design Agent spawns
  aesthetic: ...
  accent_color: ...
  fonts: { body: ..., headings: ... }
  body_size: ...
  cover: ...
  columns: ...
qa:         # Injected into QA Agent spawns
  body_size_range: ...
  max_colors: ...
  screenshot_test: ...
  type_specific_notes: ...
```

## Iterative Quality Loop
This is a loop, not a linear pipeline. No report ships until QA passes.

```
INPUT → Source Manifest → Content Agent → Design Agent → PDF Render → QA Agent
                                                       │
                                              PASS? → OUTPUT
                                                │
                                           NO → Route feedback
                                                to failing agent
                                                → LOOP (max 3x)
```

**Loop rules:**
1. Max 3 iterations. After 3, output best version + QA notes.
2. Each iteration fixes only what QA flagged. No scope creep.
3. QA is the gatekeeper. Strict — better to iterate than ship bad output.

## Agent Orchestration Protocol

The main agent acts as the loop controller. It spawns subagents via `Task` calls, reads their output, and routes QA failures back to the correct agent. Do not delegate orchestration — the main agent owns the loop.

### Pipeline Stages

**Stage 0 — Cleanup**
- Main agent handles directly — no subagent
- Delete all contents of `output/` (stale HTML, PDF, QA reports, screenshots)
- Delete `data/content.md` if it exists (stale Content Agent output)
- Delete `data/source-manifest.yaml` if it exists (stale manifest)
- Do NOT delete other files in `data/` — those are raw source input
- Write `.report-in-progress` flag file
- This ensures the stop hook and QA loop start from a clean state

**Stage 0.5 — Source Manifest**
- Spawn via `Task` with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`
- Prompt: full contents of `.claude/agents/manifest/manifest.md` + the task-specific instructions
- Input: the main agent lists all files in `data/` (excluding `content.md` and `source-manifest.yaml`) and passes the file paths in the prompt
- Output: agent writes `data/source-manifest.yaml`
- On re-run: regenerate the manifest from scratch (it's fast and ensures consistency)

**Stage 1 — Content Agent**
- Spawn via `Task` with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`
- Prompt: full contents of `.claude/agents/content/content.md` + the task-specific instructions
- Input: all files in the `data/` folder (markdown, documents, images, data files). The main agent lists the folder contents and passes the file paths in the prompt. The Content Agent also reads `data/source-manifest.yaml` to resolve metric conflicts and prioritize sources.
- Output: agent writes `data/content.md`

**Stage 2 — Design Agent**
- Spawn via `Task` with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`
- Prompt: full contents of `.claude/agents/design/design.md` + the task-specific instructions
- Input: `data/content.md` + any image files in `data/` (`*.png`, `*.jpg`)
- Output: agent writes `output/report.html` (complete HTML with embedded CSS)

**Stage 3 — PDF Render**
- Main agent handles directly — no subagent
- Serve `output/report.html` via `python -m http.server` (Bash, background)
- Use Playwright MCP `browser_navigate` to open the page, then `browser_run_code` with `page.pdf()` to render
- **Before calling `page.pdf()`**, verify all images are loaded. Use `page.wait_for_function` to check that every `<img>` element has `naturalWidth > 0` and `complete === true`. Do not rely on a fixed timeout — large images can take longer than 3 seconds.
- Output: `output/report.pdf`
- After rendering the PDF, extract per-page screenshots using Python:
  ```python
  # Using pymupdf (fitz):
  import fitz
  doc = fitz.open('output/report.pdf')
  for i, page in enumerate(doc):
      pix = page.get_pixmap(dpi=150)
      pix.save(f'output/page-{i+1}.png')
  ```
- If pymupdf is not available, use Playwright to open the PDF in the browser and screenshot each page
- Pass these per-page screenshot paths to the QA Agent in Stage 4

**Stage 4 — QA Agent**
- Spawn via `Task` with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`
- Prompt: full contents of `.claude/agents/QA/qa.md` + the task-specific instructions
- Input: `output/report.html` + per-page PDF screenshots (`output/page-*.png`) + viewport screenshots (use `browser_take_screenshot` before spawning)
- Output: agent writes `output/qa-report.json` AND `output/qa-report.md`

### QA Loop Logic

After Stage 4, the main agent reads `output/qa-report.json` and follows this logic:

```
iteration = 1

cleanup:
  delete output/* and data/content.md and data/source-manifest.yaml
  write .report-in-progress

loop:
  run Stage 0.5 → Stage 1 → Stage 2 → Stage 3 → Stage 4
  read output/qa-report.json

  if status == "PASS":
      ship output/report.pdf → done
  if status == "PASS WITH NOTES":
      ship output/report.pdf + report notes to user → done
  if status == "FAIL" and iteration < 3:
      read routing field
      re-spawn failing agent(s) with QA feedback
      iteration += 1
      goto loop
  if status == "FAIL" and iteration >= 3:
      ship best output/report.pdf + output/qa-report.md to user → done
```

### Re-spawn Rules

When QA returns FAIL, check the `routing` field in `qa-report.json`:

- `"content"` → Re-spawn Content Agent (with QA feedback) → Design Agent → PDF Render → QA
- `"design"` → Re-spawn Design Agent (with QA feedback) → PDF Render → QA
- `"both"` → Re-spawn Content Agent first (with QA feedback) → Design Agent → PDF Render → QA

When re-spawning an agent with feedback, the prompt must include:
1. The agent's full system prompt from `.claude/agents/`
2. The specific issues quoted from `output/qa-report.json`
3. The instruction: "Fix ONLY these issues. Do not change anything else."

### Spawning Template

Every `Task` call follows this pattern. The preset block is injected between the base prompt and task instructions:

```
Task(
  subagent_type: "general-purpose",
  mode: "bypassPermissions",
  prompt: """
    <full contents of .claude/agents/{agent}/agent.md>

    ## Report Type Constraints
    <contents of preset[agent_key] from the active preset YAML>

    ## Task
    <task-specific instructions, input/output paths>

    ## QA Feedback (if re-run)
    <quoted issues from qa-report.json, if applicable>
    Fix ONLY these issues. Do not change anything else.
  """
)
```

The `agent_key` maps to the preset YAML section: `manifest` for Source Manifest Agent, `content` for Content Agent, `design` for Design Agent, `qa` for QA Agent. The Manifest Agent has no preset overrides (it operates identically across report types), so the `## Report Type Constraints` block is omitted for Stage 0.5 spawns.

### Stop Hook Safety Net

A Stop hook in `.claude/settings.json` prevents the agent from finishing before QA passes. The hook is gated by a `.report-in-progress` flag file — it only activates during report generation.

**Main agent responsibilities:**
- Stage 0 writes `.report-in-progress` (see Pipeline Stages above)
- The hook auto-cleans the flag on QA PASS or after 3 iterations
- If the agent tries to stop before QA passes, the hook blocks exit with the QA failure details

Do not rely on the hook as the primary loop driver. Follow the orchestration protocol above. The hook is a safety net.

## CSS Print Essentials
Always include in stylesheets:
- `@page` rules with proper margins, headers/footers via margin boxes
- `page-break-after: avoid` on headings
- `page-break-inside: avoid` on tables/figures
- `orphans: 3; widows: 3` on paragraphs
- Cover page suppresses headers/footers via `@page :first`
- Use `-webkit-print-color-adjust: exact` for backgrounds

## Quick Commands

These are shorthand triggers the main agent recognizes as pipeline commands. When the user types one of these, execute the corresponding pipeline behavior immediately — no clarification needed.

### `/run <preset> [--design-only]`

Single pipeline pass with QA loop. Produces one finished PDF.

```
/run marketing-report          # Full pipeline: Stage 0 → 0.5 → 1 → 2 → 3 → 4 → QA loop
/run consultant-report         # Same, with consultant preset
/run marketing-report --design-only  # Skip Stage 0.5 and Stage 1 (reuse existing content.md)
```

**Behavior:**
1. Read the preset from `presets/<preset>.yaml`
2. Run Stage 0 (cleanup) — always runs
3. If `--design-only`: skip Stage 0.5 and Stage 1, verify `data/content.md` exists (error if missing). Stage 0 cleanup must NOT delete `data/content.md` or `data/source-manifest.yaml` when `--design-only` is set.
4. Otherwise: run Stage 0.5 (Source Manifest) → Stage 1 (Content Agent)
5. Run Stage 2 (Design Agent) → Stage 3 (PDF Render) → Stage 4 (QA Agent)
6. Enter QA loop (max 3 iterations) per the Iterative Quality Loop rules above
7. Ship final PDF to user

Default preset if omitted: `consultant-report`.

### `/polish <preset> [--design-only]`

3-run self-improvement loop. Runs the Design Agent forward 3 times, self-reviewing screenshots between runs and writing observations to the napkin. Does NOT modify agent `.md` files — all learning stays in `.claude/napkin.md`.

```
/polish marketing-report          # Full pipeline × 3 with self-review
/polish consultant-report         # Same, with consultant preset
/polish marketing-report --design-only  # Skip Stage 0.5 and Stage 1 on all 3 runs
```

**Behavior:**
1. Read the preset from `presets/<preset>.yaml`
2. For each run (1 of 3, 2 of 3, 3 of 3):
   a. Run the `/run` pipeline (with `--design-only` if specified)
   b. After QA passes (or max iterations reached), review the per-page screenshots (`output/page-*.png`)
   c. Write observations to `.claude/napkin.md` under a new run heading — what worked, what didn't, specific page-level notes
   d. For runs 2 and 3: inject the napkin observations from previous runs into the Design Agent prompt as additional context (append after the preset block, before task instructions). This is how the Design Agent improves across runs without modifying its `.md` file.
   e. Archive the previous run's output before starting the next: copy `output/report.pdf` → `output/report-run-N.pdf`, copy `output/qa-report.md` → `output/qa-report-run-N.md`
3. After run 3: present all three PDFs (`output/report-run-1.pdf`, `output/report-run-2.pdf`, `output/report.pdf`) and summarize what changed across runs

**Rules:**
- Content stays frozen after run 1 (runs 2–3 are design-only regardless of `--design-only` flag). Stage 0.5 and Stage 1 only run once, on run 1.
- The napkin is the memory between runs. Do not pass the full QA report to the next run — distill it into napkin observations first.
- Do not modify any files in `.claude/agents/` or `presets/`. The `/polish` command is for iterative refinement, not rule changes. Graduation of lessons to permanent rules is a separate, user-initiated action.

Default preset if omitted: `consultant-report`.

### Flags

| Flag | Effect |
|------|--------|
| `--design-only` | Skip Stage 0.5 (Source Manifest) and Stage 1 (Content Agent). Reuses existing `data/content.md` and `data/source-manifest.yaml`. Errors if `data/content.md` is missing. |

## Commands
```bash
python src/generate.py --data data/ --template report --output output/report.pdf
python src/generate.py --data data/ --template report --output output/report.pdf --preset marketing-report
python src/generate.py --data data/ --template report --preview  # HTML preview
python src/validate.py output/report.pdf  # QA only
python src/generate.py --data data/ --template report --output output/report.pdf --iterate  # Full loop
```
