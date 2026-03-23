3-run self-improvement loop. Runs the Design Agent forward 3 times, self-reviewing screenshots between runs and writing observations to the napkin. Does NOT modify agent `.md` files — all learning stays in `.claude/napkin.md`.

## Argument Parsing

Parse `$ARGUMENTS` for:
- **Preset name**: first positional argument (default: `consultant-report`)
- **`--design-only` flag**: if present, skip Stage 0.5 and Stage 1 on run 1 (runs 2-3 are always design-only regardless)

Examples:
```
/polish                              → preset=consultant-report, design-only=false
/polish marketing-report             → preset=marketing-report, design-only=false
/polish marketing-report --design-only → preset=marketing-report, design-only=true
```

## Execution

Read and follow the report-generator skill at `~/.claude/skills/report-generator/SKILL.md`.

Execute it with these parameters:
- `--source` = `./data` (resolved to absolute path from this repo's root)
- `--output` = `./output` (resolved to absolute path from this repo's root)
- `--preset` = parsed preset name from above
- `--design-only` = parsed flag from above
- `--mode` = `polish`

The skill contains the full orchestration protocol including the 3-run polish loop, agent prompts, presets, and pipeline logic. Follow it exactly.

## Rules

- Content stays frozen after run 1 (runs 2-3 are design-only regardless of `--design-only` flag).
- The napkin is the memory between runs. Do not pass the full QA report to the next run — distill it into napkin observations first.
- Do not modify any files in `~/.claude/skills/report-generator/agents/` or `~/.claude/skills/report-generator/presets/`. The `/polish` command is for iterative refinement, not rule changes. Graduation of lessons to permanent rules is a separate, user-initiated action.
