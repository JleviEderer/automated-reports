# Report Generator Source Of Truth

## Canonical Ownership Model

- `C:\Users\justi\Obsidian Vault\Projects\Automated-Workflows\Runtime Map.md` = durable machine-level runtime map
- `C:\Users\justi\.claude\skills\report-generator` = Claude Code skill runtime
- `C:\Users\justi\.claude\commands\report.md` = Claude Code slash command
- `C:\Users\justi\.agents\skills\report-generator` = Codex installed skill/playbook runtime
- `C:\Users\justi\dev\automated-reports-repo` = support repo for helper code, docs, audits, preset reference copies, and local pipeline utilities
- workspaces such as `C:\Users\justi\dev\Abaxx` = source material, outputs, benchmarks, and project-specific context

If you want a shared behavior change, update both installed runtime copies listed in the runtime map. If you want a Claude slash-command change, edit the command under `C:\Users\justi\.claude\commands`.

## Why This Repo Exists

This repo is useful for:
- helper code such as render and validation scripts
- benchmark docs and system documentation
- local wrappers and audits
- backup/reference copies of prompts and presets

This repo is not the live runtime for Claude Code or Codex.

## Working Rules

- Treat `C:\Users\justi\Obsidian Vault\Projects\Automated-Workflows\Runtime Map.md` as the authoritative map for live runtime paths.
- Treat `C:\Users\justi\.claude` and `C:\Users\justi\.agents` as installed runtime copies, not repo support folders.
- Treat repo-local agent and preset files as reference copies unless you are intentionally reconciling them against the global runtime.
- Do not assume editing this repo changes the live Claude or Codex systems.
- If you make a meaningful change in an installed runtime and want backup or versioning, copy it into this repo intentionally afterward.

## Drift Audit

Use:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\audit-claude-runtime.ps1
```

This is an audit tool, not an install/sync mechanism. It tells you where repo reference files have drifted from the global Claude runtime.

## Practical Decision Rule

- Shared runtime behavior change needed: update both installed runtime copies in the runtime map
- Claude command behavior change needed: edit `C:\Users\justi\.claude\commands\report.md`
- Project/workspace content change needed: edit the workspace
- Helper-code or documentation change needed: edit this repo
