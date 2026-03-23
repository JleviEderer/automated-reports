List all available report presets with descriptions and page targets.

## Execution

1. Glob `~/.claude/skills/report-generator/presets/*.yaml` to find all preset files
2. For each file, read the YAML and extract:
   - `name` (top-level field)
   - `description` (top-level field)
   - Page target: look for `qa.page_range`, `qa.max_pages`, or `design.page_target` / `design.page_limit` — use whichever exists
3. Print a formatted list. Mark `consultant-report` as `(default)`.

## Output Format

Print exactly this structure (values come from the YAML files, not hardcoded):

```
Available presets:

  <filename-without-extension> (default if consultant-report)
  <description field from YAML>
  Pages: <page target extracted above>

  ... repeat for each preset ...

Usage: /run <preset>  or  /polish <preset>
```

## Rules

- Read from the YAML files — do not hardcode descriptions or page counts
- Sort alphabetically by filename
- If a preset has no page target field, show "Pages: not specified"
- Do not modify any files — this is a read-only command