param(
    [string]$ClaudeHome = 'C:\Users\justi\.claude'
)

$repoRoot = Split-Path -Parent $PSScriptRoot

$mappedFiles = @(
    @{
        Label = 'agent: content'
        Source = Join-Path $repoRoot '.claude\agents\content\content.md'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\agents\content.md'
    },
    @{
        Label = 'agent: design'
        Source = Join-Path $repoRoot '.claude\agents\design\design.md'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\agents\design.md'
    },
    @{
        Label = 'agent: manifest'
        Source = Join-Path $repoRoot '.claude\agents\manifest\manifest.md'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\agents\manifest.md'
    },
    @{
        Label = 'agent: qa'
        Source = Join-Path $repoRoot '.claude\agents\QA\qa.md'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\agents\qa.md'
    },
    @{
        Label = 'preset: consultant-report'
        Source = Join-Path $repoRoot 'presets\consultant-report.yaml'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\presets\consultant-report.yaml'
    },
    @{
        Label = 'preset: marketing-report'
        Source = Join-Path $repoRoot 'presets\marketing-report.yaml'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\presets\marketing-report.yaml'
    },
    @{
        Label = 'preset: internal-memo'
        Source = Join-Path $repoRoot 'presets\internal-memo.yaml'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\presets\internal-memo.yaml'
    },
    @{
        Label = 'preset: bezos-6-pager'
        Source = Join-Path $repoRoot 'presets\bezos-6-pager.yaml'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\presets\bezos-6-pager.yaml'
    }
)

$runtimeOnlyChecks = @(
    @{
        Label = 'skill protocol'
        RepoExpected = Join-Path $repoRoot 'SKILL.md'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\SKILL.md'
    },
    @{
        Label = 'agent: reviewer'
        RepoExpected = Join-Path $repoRoot '.claude\agents\reviewer\reviewer.md'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\agents\reviewer.md'
    },
    @{
        Label = 'preset: stock-pitch'
        RepoExpected = Join-Path $repoRoot 'presets\stock-pitch.yaml'
        Installed = Join-Path $ClaudeHome 'skills\report-generator\presets\stock-pitch.yaml'
    },
    @{
        Label = 'global command: report'
        RepoExpected = Join-Path $repoRoot 'commands\report.md'
        Installed = Join-Path $ClaudeHome 'commands\report.md'
    }
)

$results = @()

foreach ($item in $mappedFiles) {
    $sourceExists = Test-Path -LiteralPath $item.Source
    $installedExists = Test-Path -LiteralPath $item.Installed

    if (-not $sourceExists -and -not $installedExists) {
        $status = 'missing-both'
    } elseif (-not $sourceExists) {
        $status = 'missing-source'
    } elseif (-not $installedExists) {
        $status = 'missing-installed'
    } else {
        $sourceHash = (Get-FileHash -LiteralPath $item.Source).Hash
        $installedHash = (Get-FileHash -LiteralPath $item.Installed).Hash
        $status = if ($sourceHash -eq $installedHash) { 'match' } else { 'differs' }
    }

    $results += [pscustomobject]@{
        Category  = 'mapped'
        Label     = $item.Label
        Status    = $status
        Source    = $item.Source
        Installed = $item.Installed
    }
}

foreach ($item in $runtimeOnlyChecks) {
    $repoExists = Test-Path -LiteralPath $item.RepoExpected
    $installedExists = Test-Path -LiteralPath $item.Installed

    $status = if ($installedExists -and -not $repoExists) {
        'runtime-only'
    } elseif ($installedExists -and $repoExists) {
        'present-in-both'
    } elseif (-not $installedExists -and $repoExists) {
        'repo-only'
    } else {
        'missing-both'
    }

    $results += [pscustomobject]@{
        Category  = 'coverage'
        Label     = $item.Label
        Status    = $status
        Source    = $item.RepoExpected
        Installed = $item.Installed
    }
}

$results | Sort-Object Category, Label | Format-Table -AutoSize

$summary = $results | Group-Object Status | Sort-Object Name | ForEach-Object {
    [pscustomobject]@{
        Status = $_.Name
        Count  = $_.Count
    }
}

Write-Host ''
Write-Host 'Summary'
$summary | Format-Table -AutoSize
