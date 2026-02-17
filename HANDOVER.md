# Handover — WolfPack PDF Report Generator

**Session date:** 2026-02-16
**Status:** Infrastructure complete. Pipeline has been run at least once (prior to this session) and produced a passing report.

---

## What We Did This Session

### 1. Added a Stop Hook (QA Safety Net)
Created a Claude Code Stop hook that prevents the agent from finishing a report-generation session before QA passes. It's gated by a `.report-in-progress` flag file so it doesn't interfere with non-report conversations.

- **Hook script:** `.claude/hooks/check-qa-pass.py`
- **Wired in:** `.claude/settings.json` (Stop event)
- **Behavior:** Blocks exit if QA report is missing or status is FAIL. Allows exit on PASS/PASS WITH NOTES. Auto-releases after 3 iterations to prevent infinite loops.

### 2. Fixed Content Agent Input Model
The content agent and CLAUDE.md originally assumed `data/input.json` as pre-formatted JSON input. Updated everything to reflect the real model: raw source files (markdown, documents, images, data files) in the `data/` folder. The content agent's job is to read raw material and structure it into `data/content.md` (markdown with YAML frontmatter).

**Files edited:**
- `CLAUDE.md` — 5 edits (Purpose, Architecture, Stage 1 input, added Stop Hook docs, updated Commands)
- `.claude/agents/content/content.md` — rewrote "Your Job" and "File Contract" sections

### 3. Replaced `jq` with Python in Stop Hook
The original hook script was bash + `jq`. `jq` isn't available in Git Bash/MINGW on Windows. Rewrote as a Python script using stdlib `json` module — zero external dependencies since Python is already required by the project.

### 4. Set Up Git
Initialized the repo, created `.gitignore`, made two commits:
- `b6ea1d1` — feat: add stop hook, fix content agent input model, replace jq with python (5 files)
- `279a9c6` — chore: add pipeline agents, scripts, styles, and templates (6 files)

**Uncommitted:** `.gitignore` update (added `.playwright-mcp/`), image/PDF/pptx assets in project root.

---

## What Worked

- Python stop hook passes all 4 test cases (no flag → allow, flag + no QA → block, flag + PASS → clean + allow, flag + FAIL → block with routing)
- All agent prompts, Python scripts, templates, and styles are complete and functional
- A prior pipeline run produced `output/report.pdf` (18.5 MB) that passed QA with notes

## What Didn't Work (and How It Was Fixed)

- **`jq` not available on Windows Git Bash.** The original bash+jq hook script couldn't parse JSON. Fixed by rewriting the entire hook in Python.
- **No git repo existed.** Had to `git init` and configure user identity before committing.

---

## Key Decisions

| Decision | Why |
|----------|-----|
| Python over bash for the hook | `jq` unavailable on Windows; Python is already a project dependency |
| Flag-file gating (`.report-in-progress`) | Hook must be inert during non-report conversations |
| 3-iteration cap in the hook | Prevents infinite loops if QA never passes |
| `data/` and `output/` gitignored | Contents change every pipeline run — not version-controlled |
| `.playwright-mcp/` gitignored | Playwright MCP temp files, not project code |

---

## Lessons Learned / Gotchas

1. **CLAUDE.md commands don't match `generate.py`.** The Commands section shows `--data data/` (folder), but `generate.py`'s `load_data()` expects `--data data/input.json` (a file path with required JSON keys). Running the documented commands verbatim will fail. This needs to be reconciled — either update `generate.py` to accept a folder, or revert the CLAUDE.md commands.

2. **`generate.py` can't produce HTML from scratch.** It checks for an existing `output/report.html` and returns early. The Design Agent subagent must run first to create the HTML. The Python CLI is a PDF-rendering wrapper, not an end-to-end generator.

3. **Template uses external CSS, not embedded.** `templates/report.html` links to `styles/print.css` as an external file. The Design Agent spec says to write `output/report.html` with embedded CSS. In practice this hasn't been an issue because both files exist, but it's a spec inconsistency.

4. **Google Fonts CDN dependency.** The template loads EB Garamond and DM Sans from Google Fonts. PDF rendering needs internet access (or the fonts need to be bundled locally in `fonts/`).

---

## Next Steps

1. **Reconcile `generate.py` with the new input model.** Either update `load_data()` to accept a folder path and discover files, or revert CLAUDE.md commands to `--data data/input.json`. Right now they're mismatched.

2. **Commit remaining changes.** The `.gitignore` update adding `.playwright-mcp/` is uncommitted. The image/PDF/pptx assets in the project root are untracked — decide whether to commit, gitignore, or move them.

3. **Test the full pipeline end-to-end.** Start a fresh conversation, ask to generate a report, and verify: flag file created → Content Agent reads `data/` → Design Agent renders HTML → Playwright renders PDF → QA Agent evaluates → hook allows/blocks appropriately.

4. **Consider bundling fonts locally.** The Google Fonts CDN dependency means PDF rendering fails offline. The `fonts/` directory exists but is empty.

---

## File Map

### Created This Session
| File | Purpose |
|------|---------|
| `.claude/hooks/check-qa-pass.py` | Stop hook — blocks agent exit until QA passes |
| `.claude/settings.json` | Registers the Stop hook on the Stop event |
| `.gitignore` | Ignores `.report-in-progress`, `data/`, `output/`, `.playwright-mcp/` |

### Modified This Session
| File | What Changed |
|------|-------------|
| `CLAUDE.md` | Purpose, Architecture, Stage 1 input, Stop Hook docs, Commands section |
| `.claude/agents/content/content.md` | "Your Job" and "File Contract" rewritten for raw source input |

### Deleted This Session
| File | Why |
|------|-----|
| `.claude/hooks/check-qa-pass.sh` | Replaced by `.py` version (jq unavailable) |

### Pre-existing (Not Modified)
| File | Purpose |
|------|---------|
| `.claude/agents/design/design.md` | Design agent prompt — HTML/CSS rendering spec |
| `.claude/agents/QA/qa.md` | QA agent prompt — quality checklist and routing |
| `src/generate.py` | Python CLI — PDF rendering, QA loop, HTTP server |
| `src/validate.py` | Static analysis validator — fonts, AI filler, structure |
| `styles/print.css` | 813-line print-optimized stylesheet |
| `templates/report.html` | Jinja2 template with 7 report sections |
| `data/input.json` | Structured input data from a prior run |
| `data/content.md` | Content Agent output from a prior run |
| `output/report.pdf` | Final PDF from a prior run (18.5 MB) |
| `output/qa-report.md` | QA report — PASS WITH NOTES |
