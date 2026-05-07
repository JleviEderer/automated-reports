# Folder Role

## Role

This folder is the support/helper-code/reference repo for the report-generation system.

Use it for:
- helper code such as render and validation utilities
- docs and runbooks
- audits against the live Claude runtime
- reference snapshots of prompts and presets

This folder is not the canonical live runtime for Claude Code or Codex.

## Runtime Locations

- `C:\Users\justi\Obsidian Vault\Projects\Automated-Workflows\Runtime Map.md` = durable runtime map
- `C:\Users\justi\.claude\skills\report-generator` = Claude Code skill runtime
- `C:\Users\justi\.claude\commands\report.md` = Claude Code slash command
- `C:\Users\justi\.agents\skills\report-generator` = Codex installed skill/playbook runtime

## Decision Rule

- Need shared report-generator behavior changed: update both installed runtime copies listed in the runtime map
- Need Claude slash-command behavior changed: edit `C:\Users\justi\.claude\commands\report.md`
- Need helper-code, docs, or drift inspection: edit this repo
- Need to check whether repo references still match the live runtime: run `powershell -ExecutionPolicy Bypass -File .\scripts\audit-claude-runtime.ps1`

## Related Folders

- `C:\Users\justi\dev\Abaxx` = active workspace
- `C:\Users\justi\dev\research-to-report-repo` = backup/distribution/recovery repo
- `C:\Users\justi\dev\automation-systems\report-generator-workspace-copy-archive-2026-04-09` = archive only
