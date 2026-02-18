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
- Main agent handles directly — no subagent
- Scan every file in `data/` (excluding `content.md` and `source-manifest.yaml`)
- For each file, read content and extract the best available date signal: document dates, "as of" dates, earnings call quarters, filing dates, metadata timestamps
- Classify each source as `factual` (contains numeric metrics, financial data, performance stats that change over time), `contextual` (contains strategic rationale, expert commentary, technical explanations, qualitative analysis that doesn't go stale), or `both`
- Produce `data/source-manifest.yaml` with:
  - `sources`: list of entries, each with `file`, `estimated_date`, `date_confidence` (high/medium/low), `content_type` (factual/contextual/both), and `key_metrics` (list of metric name/value pairs extracted from the file)
  - `conflicts`: list of any metric that appears in multiple sources with different values, showing each source's value and date, with a `resolution` that defaults to most-recent-source-wins — **only for factual content**. Contextual content is never deprioritized based on age alone.
- Do NOT rename any source files. The manifest is the only output.
- On re-run: regenerate the manifest from scratch (it's fast and ensures consistency)
- Example manifest structure:
  ```yaml
  sources:
    - file: "Abaxx_Q3_2025_InvestorCall.md"
      estimated_date: "2025-11-15"
      date_confidence: high
      content_type: factual
      key_metrics:
        - name: "Q3 LNG contracts"
          value: "9,486"
        - name: "Connected firms"
          value: "150+"

    - file: "Why incumbents_CME&ICE_ can't beat Abaxx_DeepSky AI.docx"
      estimated_date: "2025-09-01"
      date_confidence: medium
      content_type: contextual
      key_metrics: []

  conflicts:
    - metric: "Connected firms"
      sources:
        - file: "Abaxx_Q3_2025_InvestorCall.md"
          value: "150+"
          date: "2025-11-15"
        - file: "Abaxx_Problem_Solutions_Doc_September2025.docx"
          value: "120+"
          date: "2025-09-01"
      resolution: "Use Abaxx_Q3_2025_InvestorCall.md (most recent, factual)"
  ```

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

The `agent_key` maps to the preset YAML section: `content` for Content Agent, `design` for Design Agent, `qa` for QA Agent.

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

## Commands
```bash
python src/generate.py --data data/ --template report --output output/report.pdf
python src/generate.py --data data/ --template report --output output/report.pdf --preset marketing-report
python src/generate.py --data data/ --template report --preview  # HTML preview
python src/validate.py output/report.pdf  # QA only
python src/generate.py --data data/ --template report --output output/report.pdf --iterate  # Full loop
```
