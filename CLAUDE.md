# PDF Report Generator

## Purpose
Automated pipeline for producing professional, editorial-quality PDF reports from raw source material - documents, markdown, images, and data files. Reports must look handcrafted - as if designed by a human at a boutique consulting firm or editorial publication. Not AI-generated.

## Architecture

The report-generator runtime is split across Claude Code and Codex. The durable machine-level source of truth is `C:\Users\justi\Obsidian Vault\Projects\Automated-Workflows\Runtime Map.md`.

Claude Code has the slash-command runtime at `~/.claude/skills/report-generator/`. Codex has an installed skill/playbook copy at `~/.agents/skills/report-generator/`. Shared behavior changes should be mirrored into both installed runtime copies unless the change is explicitly runtime-specific.

- Agent prompts: `~/.claude/skills/report-generator/agents/` (manifest, content, design, QA)
- Presets: `~/.claude/skills/report-generator/presets/` (consultant-report, marketing-report, internal-memo, bezos-6-pager)
- Orchestration protocol: `~/.claude/skills/report-generator/SKILL.md` (pipeline stages, QA loop, spawning template, path resolution)

This project folder (`data/`, `output/`) is the default workspace for the Abaxx report corpus.

Canonical ownership:
- Runtime paths are governed by the Obsidian runtime map
- Claude slash-command behavior lives in `~/.claude/skills/report-generator/` and `~/.claude/commands/report.md`
- Codex skill/playbook behavior lives in `~/.agents/skills/report-generator/`
- This repo is a support workspace with helper code, docs, audits, and reference copies
- Do not assume edits here change either installed runtime

### Pipeline Flow
```
INPUT -> Source Manifest -> Content Agent -> Design Agent -> PDF Render -> QA Agent
                                                  |
                                         PASS? -> OUTPUT
                                           |
                                      NO -> Route feedback -> LOOP (max 3x)
```

### Local Files (this repo)
```
CLAUDE.md                 # This file - project context
.claude/agents/           # Reference snapshots of prompts used by the global skill
.claude/commands/         # Repo-local wrappers that invoke the global skill
.claude/napkin.md         # Per-repo learning from report runs
.codex/napkin.md          # Codex runbook notes; preferred Codex spelling
presets/                  # Reference snapshots of preset YAMLs
data/                     # Raw source input for Abaxx reports
output/                   # Pipeline output (PDF, HTML, screenshots)
templates/                # Generated HTML templates (Design Agent output)
styles/                   # Generated print CSS (Design Agent output)
fonts/                    # Local font files (optional)
```

## Design Principles (Defaults - Presets Can Override)
- Serif body fonts (Georgia, Garamond, Libre Baskerville). Never Inter, Roboto, Arial, or system fonts.
- Max 3 colors per report (including black). One muted accent color used sparingly. Presets may adjust the limit.
- Generous margins (>= 1 inch). Whitespace is a design element.
- Prose-first. Bullet lists max 3-5 items, max 2 lists per page. Default to paragraphs.
- No AI tells: no "It's worth noting," no filler, no hedging, no monotonous structure.
- Every report passes the "screenshot test" - no one would guess AI made it.

## Presets

Report type presets live in the installed runtime copies listed in the runtime map. Claude Code reads `~/.claude/skills/report-generator/presets/`; Codex reads `~/.agents/skills/report-generator/presets/`. Each preset defines per-agent overrides for tone, structure, aesthetics, and QA thresholds.

Available presets:
- `consultant-report` (default) - Analytical, editorial, restrained. McKinsey meets Monocle.
- `marketing-report` - Persuasive, brand-forward, bolder accent colors.
- `internal-memo` - Functional, direct, minimal styling. Hard 2-page max.
- `bezos-6-pager` - Amazon-style 6-page narrative memo. Dense prose, fixed structure, data-driven.

## Quick Commands

Pipeline commands in `.claude/commands/` invoke the global skill with repo-local paths:
- `/run <preset> [--design-only]` - single pipeline pass with QA loop
- `/polish <preset> [--design-only]` - 3-run self-improvement loop with napkin-driven learning
- `/eval [--scope <full|napkin-only|qa-only>]` - audit the learning system's health (napkin integrity, QA consistency, coverage gaps, graduation queue, variance)

Default preset: `consultant-report`. Use `--design-only` to skip Stage 0.5 and Stage 1 when `output/content.md` already exists.

## Using The Skill From Other Directories

From any directory with source material:
```
"Generate a report from ./research/abaxx using the bezos-6-pager preset"
"Generate a marketing report from these files, output to ./reports"
```

The skill auto-resolves paths and keeps the source directory read-only.

## Stop Hook Safety Net

A Stop hook in `.claude/settings.json` prevents the agent from finishing before QA passes. The hook is gated by a `.report-in-progress` flag file - it only activates during report generation.

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
python src/generate.py --data data/ --template report --preview
python src/validate.py output/report.pdf
python src/generate.py --data data/ --template report --output output/report.pdf --iterate
```
