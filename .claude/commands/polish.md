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

1. Read the preset from `presets/<preset>.yaml`
2. For each run (1 of 3, 2 of 3, 3 of 3):
   a. Run the `/run` pipeline (with `--design-only` if specified for run 1; runs 2-3 are always design-only).
   b. After QA passes (or max iterations reached), review the per-page screenshots (`output/page-*.png`).
   c. Write observations to `.claude/napkin.md` under a new run heading — what worked, what didn't, specific page-level notes.
   d. For runs 2 and 3: inject the napkin observations from previous runs into the Design Agent prompt as additional context (append after the preset block, before task instructions). This is how the Design Agent improves across runs without modifying its `.md` file.
   e. Archive the previous run's output before starting the next: copy `output/report.pdf` to `output/report-run-N.pdf`, copy `output/qa-report.md` to `output/qa-report-run-N.md`.
3. After run 3: present all three PDFs (`output/report-run-1.pdf`, `output/report-run-2.pdf`, `output/report.pdf`) and summarize what changed across runs.

## Rules

- Content stays frozen after run 1 (runs 2-3 are design-only regardless of `--design-only` flag). Stage 0.5 and Stage 1 only run once, on run 1.
- The napkin is the memory between runs. Do not pass the full QA report to the next run — distill it into napkin observations first.
- Do not modify any files in `.claude/agents/` or `presets/`. The `/polish` command is for iterative refinement, not rule changes. Graduation of lessons to permanent rules is a separate, user-initiated action.

Follow the Agent Orchestration Protocol, Pipeline Stages, Spawning Template, and Stop Hook Safety Net sections in CLAUDE.md for all stage execution details.