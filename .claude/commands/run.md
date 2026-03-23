Single pipeline pass with QA loop. Produces one finished PDF.

## Argument Parsing

Parse `$ARGUMENTS` for:
- **Preset name**: first positional argument (default: `consultant-report`)
- **`--design-only` flag**: if present, skip Stage 0.5 and Stage 1

Examples:
```
/run                              → preset=consultant-report, design-only=false
/run marketing-report             → preset=marketing-report, design-only=false
/run marketing-report --design-only → preset=marketing-report, design-only=true
```

## Execution

**Step 1 — Read the napkin.** Invoke the `napkin` skill before doing anything else. This surfaces accumulated lessons into working memory for the pipeline run.

**Step 2 — Run the pipeline.** Read and follow the report-generator skill at `~/.claude/skills/report-generator/SKILL.md`.

Execute it with these parameters:
- `--source` = `./data` (resolved to absolute path from this repo's root)
- `--output` = `./output` (resolved to absolute path from this repo's root)
- `--preset` = parsed preset name from above
- `--design-only` = parsed flag from above
- `--mode` = `run`

The skill contains the full orchestration protocol, agent prompts, presets, and pipeline logic. Follow it exactly.

**Step 3 — Write back to the napkin.** After the pipeline completes (any terminal QA status), invoke the `napkin` skill again to log observations. The napkin skill owns all writes — do NOT manually append a run entry. Let it capture what actually happened, including any mid-run corrections, unexpected agent behavior, or design decisions worth remembering.
