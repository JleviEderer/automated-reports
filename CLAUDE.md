# PDF Report Generator

## Purpose
Automated pipeline for producing professional, editorial-quality PDF reports from raw source material — documents, markdown, images, and data files. Reports must look handcrafted — as if designed by a human at a boutique consulting firm or editorial publication. Not AI-generated.

## Architecture
- HTML templates + print-optimized CSS → rendered to PDF
- Python CLI orchestrator in `/src`
- Data input: raw files (markdown, documents, images, data files) in a project folder → Content Agent structures into JSON → injected into templates
- Tool selection is flexible — agents choose the best libraries for templating, rendering, and conversion

## File Structure
```
├── CLAUDE.md
├── .claude/agents/              # Subagent system prompts
│   ├── content/content.md       # Content writing agent
│   ├── design/design.md         # HTML/CSS design agent
│   └── QA/qa.md                 # QA validation agent
├── src/                    # Python orchestration
├── templates/              # HTML templates
├── styles/                 # Print CSS
├── data/                   # Input data
├── output/                 # Final PDFs
└── fonts/                  # Local font files (optional)
```

## Design Principles (All Agents Must Follow)
- Serif body fonts (Georgia, Garamond, Libre Baskerville). Never Inter, Roboto, Arial, or system fonts.
- Max 3 colors per report (including black). One muted accent color used sparingly.
- Generous margins (≥1 inch). Whitespace is a design element.
- Prose-first. Bullet lists max 3–5 items, max 2 lists per page. Default to paragraphs.
- No AI tells: no "It's worth noting," no filler, no hedging, no monotonous structure.
- Every report passes the "screenshot test" — no one would guess AI made it.

## Iterative Quality Loop
This is a loop, not a linear pipeline. No report ships until QA passes.

```
INPUT → Content Agent → Design Agent → PDF Render → QA Agent
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
- Delete `data/content.json` if it exists (stale Content Agent output)
- Do NOT delete other files in `data/` — those are raw source input
- Write `.report-in-progress` flag file
- This ensures the stop hook and QA loop start from a clean state

**Stage 1 — Content Agent**
- Spawn via `Task` with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`
- Prompt: full contents of `.claude/agents/content/content.md` + the task-specific instructions
- Input: all files in the `data/` folder (markdown, documents, images, data files). The main agent lists the folder contents and passes the file paths in the prompt.
- Output: agent writes `data/content.json`

**Stage 2 — Design Agent**
- Spawn via `Task` with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`
- Prompt: full contents of `.claude/agents/design/design.md` + the task-specific instructions
- Input: `data/content.json` + any image files in project root (`*.png`)
- Output: agent writes `output/report.html` (complete HTML with embedded CSS)

**Stage 3 — PDF Render**
- Main agent handles directly — no subagent
- Serve `output/report.html` via `python -m http.server` (Bash, background)
- Use Playwright MCP `browser_navigate` to open the page, then `browser_run_code` with `page.pdf()` to render
- Output: `output/report.pdf`

**Stage 4 — QA Agent**
- Spawn via `Task` with `subagent_type: "general-purpose"`, `mode: "bypassPermissions"`
- Prompt: full contents of `.claude/agents/QA/qa.md` + the task-specific instructions
- Input: `output/report.html` + screenshots (use `browser_take_screenshot` before spawning)
- Output: agent writes `output/qa-report.json` AND `output/qa-report.md`

### QA Loop Logic

After Stage 4, the main agent reads `output/qa-report.json` and follows this logic:

```
iteration = 1

cleanup:
  delete output/* and data/content.json
  write .report-in-progress

loop:
  run Stage 1 → Stage 2 → Stage 3 → Stage 4
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

Every `Task` call follows this pattern:

```
Task(
  subagent_type: "general-purpose",
  mode: "bypassPermissions",
  prompt: """
    <full contents of .claude/agents/{agent}/agent.md>

    ## Task
    <task-specific instructions, input/output paths>

    ## QA Feedback (if re-run)
    <quoted issues from qa-report.json, if applicable>
    Fix ONLY these issues. Do not change anything else.
  """
)
```

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
python src/generate.py --data data/ --template report --preview  # HTML preview
python src/validate.py output/report.pdf  # QA only
python src/generate.py --data data/ --template report --output output/report.pdf --iterate  # Full loop
```
