param(
  [string]$Output = ".codex/trinity_report.md"
)

$now = Get-Date -Format 'dd MMMM yyyy HH:mm'  # Malaysia time assumed local
$branch = (git branch --show-current)
$statusShort = (git status -sb)
$statusLines = git status --porcelain
$untracked = $statusLines | Where-Object { $_ -like "?? *" } | ForEach-Object { $_.Substring(3) }
$untrackedCount = ($untracked | Measure-Object).Count
$trackedChanged = $statusLines | Where-Object { $_ -notlike "?? *" } | ForEach-Object { $_.Substring(3) }
$trackedChangedCount = ($trackedChanged | Measure-Object).Count
$dirty = if ($statusLines.Count -gt 0) { "dirty" } else { "clean" }

# Hot zones proxy (last 50 commits)
$hotItems = git log -50 --name-only --pretty=format:"" | Where-Object { $_ -ne "" } | Group-Object | Sort-Object Count -Descending | Select-Object -First 10
$hotList = $hotItems | ForEach-Object { "- $($_.Name) (x$($_.Count))" }

# Change surface
$diffStat = git diff --stat
$diffFiles = git diff --name-only
$changedCount = ($diffFiles | Measure-Object).Count

# Entropy proxy: weighted by hot zone overlap
$hotNames = $hotItems | ForEach-Object { $_.Name }
$hotTouched = ($diffFiles | Where-Object { $hotNames -contains $_ }).Count
$entropy = [math]::Round((($trackedChangedCount + $untrackedCount) * 0.7) + ($hotTouched * 1.5), 2)

# Risk heuristic
$risk = if ($entropy -ge 8) { "HIGH" } elseif ($entropy -ge 4) { "MODERATE" } else { "LOW" }
$verdict = if ($risk -eq "HIGH") { "SABAR" } else { "SEAL" }

$guidance = if ($risk -eq "HIGH") { "Decompose changes and cool." } elseif ($risk -eq "MODERATE") { "Proceed with review." } else { "Proceed." }

$template = @'
# Trinity Report — {0} MYT

## Δ Mind (Sense)
- Branch: {1}
- Status: {2}
- Tracked changes: {3}
- Untracked files: {4}
- Hot-zone overlap: {5}

## Ω Heart (Act)
- Entropy proxy (ΔS*): {6}
- Risk: {7}
- Guidance: {8}

## Ψ Soul (Judge)
- Verdict: {9}
- Note: This is a heuristic until arifos_core.trinity.forge is available.

## Hot Zones (last 50 commits)
{10}

## Diff (current working tree)
~~~
{11}
~~~
'@

$content = $template -f $now, $branch, $dirty, $trackedChangedCount, $untrackedCount, $hotTouched, $entropy, $risk, $guidance, $verdict, ($hotList -join "`n"), $diffStat
$content | Set-Content $Output

Write-Output "Trinity report written to $Output"
