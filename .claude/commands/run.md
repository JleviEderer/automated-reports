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

1. Read the preset from `presets/<preset>.yaml`
2. **Stage 0 (Cleanup)** — always runs per CLAUDE.md "Stage 0 — Cleanup" rules. Exception: when `--design-only` is set, do NOT delete `data/content.md` or `data/source-manifest.yaml`.
3. If `--design-only`:
   - Verify `data/content.md` exists. If missing, stop with an error message.
   - Skip Stage 0.5 and Stage 1.
4. Otherwise:
   - Run **Stage 0.5** (Source Manifest Agent)
   - Run **Stage 1** (Content Agent)
5. Run **Stage 2** (Design Agent) → **Stage 3** (PDF Render) → **Stage 4** (QA Agent)
6. Enter the **QA loop** (max 3 iterations) per CLAUDE.md's "QA Loop Logic" and "Re-spawn Rules" sections.
7. Ship final PDF to user.

Follow the Agent Orchestration Protocol, Pipeline Stages, Spawning Template, and Stop Hook Safety Net sections in CLAUDE.md for all stage execution details.