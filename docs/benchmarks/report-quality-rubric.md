# Report Quality Benchmark Rubric

## Purpose

Use this rubric to benchmark report-generator runs over time and detect model drift, prompt regressions, or layout instability.

Canonical rubric location:
- `automated-reports-repo/docs/benchmarks/report-quality-rubric.md`

Project-specific scorecards belong in the workspace that owns the source data and report artifacts:
- `<workspace>/reports/benchmarks/`

Benchmark tracks are preset-specific:
- compare `bezos-6-pager` runs against other `bezos-6-pager` runs
- compare `consultant-report` runs against other `consultant-report` runs
- compare `marketing-report` runs against other `marketing-report` runs
- compare `internal-memo` runs against other `internal-memo` runs

Recommended workspace layout:
- `<workspace>/reports/benchmarks/bezos-6-pager/`
- `<workspace>/reports/benchmarks/consultant-report/`
- `<workspace>/reports/benchmarks/marketing-report/`
- `<workspace>/reports/benchmarks/internal-memo/`

Do not use a single mixed benchmark pool across presets. Different presets optimize for different lengths, layouts, and visual standards, so cross-preset scoring is not decision-useful unless you are explicitly comparing preset fit for the same source corpus.

## Benchmark Inputs

For each benchmark run, capture:
- final PDF
- page screenshots or page images
- `output/qa-report.json`
- `output/qa-report.md`
- `output/content.md`
- the closest prior baseline using the same preset and similar source set

Prefer comparing against the strongest prior run for the same preset, not merely the most recent run.
Only compare across presets for a separate question such as "which preset best fits this corpus."

## Scoring

Score each category using the weights below.

| Category | Weight | What To Measure |
|---|---:|---|
| Runtime efficiency | 15 | QA iterations, severity trend, obvious loop thrash, amount of fixing required to reach acceptable output |
| Constraint compliance | 20 | Preset compliance, page count/length, appendix behavior, orphan control, typography/color adherence |
| Visual polish | 20 | Page density, spacing, section flow, table cleanliness, overall screenshot test |
| Editorial quality | 20 | Clarity, specificity, strategic coherence, absence of filler or AI tells |
| Data integrity | 15 | Metric consistency, sourcing discipline, no fabricated or conflicting claims |
| Baseline comparison | 10 | Whether the new run is worse, flat, or better than the strongest prior baseline |

Total possible score: 100

## Category Anchors

### Runtime Efficiency
- `13-15`: Reaches clean pass quickly with little or no QA churn
- `10-12`: Some rework, but loop is controlled and efficient
- `7-9`: Noticeable thrash or multiple iterations, still lands acceptably
- `0-6`: Heavy loop churn, repeated failures, or manual rescue required

### Constraint Compliance
- `18-20`: Fully compliant or only trivial cosmetic tolerance calls
- `14-17`: Passes, but with one visible compromise
- `8-13`: Multiple borderline exceptions
- `0-7`: Fails major preset constraints

### Visual Polish
- `18-20`: Feels handcrafted; balanced page flow; no distracting layout issues
- `14-17`: Strong overall, with one visible weakness
- `8-13`: Acceptable but noticeably rough
- `0-7`: Visibly poor or clearly broken

### Editorial Quality
- `18-20`: Dense, specific, persuasive, decision-useful
- `14-17`: Good, but less sharp or less elegant than benchmark quality
- `8-13`: Serviceable, generic, or uneven
- `0-7`: Weak reasoning or obvious model tells

### Data Integrity
- `14-15`: Metrics and claims are consistent and well-grounded
- `10-13`: Minor ambiguity, no serious factual concern
- `5-9`: Multiple unsupported or weakly supported claims
- `0-4`: Serious factual or sourcing defects

### Baseline Comparison
- `9-10`: Clearly better than the prior best baseline
- `7-8`: Roughly flat or mixed tradeoff versus baseline
- `4-6`: Mild regression
- `0-3`: Clear regression

## Grade Bands

| Score | Grade | Meaning |
|---|---|---|
| 90-100 | A | New benchmark-quality reference |
| 80-89 | B | Good run; acceptable with mild caveats |
| 70-79 | C | Usable but degraded; investigate |
| 0-69 | D/F | Regression or failure; do not treat as healthy baseline |

## Required Benchmark Notes

Each scorecard should record:
- date
- preset
- source context
- baseline file(s)
- final score and grade
- short judgment: better, flat, or worse than baseline
- 3-6 concrete observations
- whether the run should replace the existing benchmark reference

## Decision Rule

Do not replace the current benchmark reference unless the new run is:
- at least as strong editorially
- at least as clean visually
- not materially worse in runtime efficiency

If the tradeoff is mixed, keep the earlier benchmark as the primary reference and log the new run as a comparison point.
