$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $root 'content/pages.json'
$pages = Get-Content -LiteralPath $manifestPath -Raw | ConvertFrom-Json
$files = $pages.href | Where-Object { $_ -like 'pg*.html' } | Sort-Object -Unique

foreach ($file in $files) {
    $path = Join-Path $root $file
    $html = Get-Content -LiteralPath $path -Raw

    # Activity section types make the shared runtime add correctness checking and
    # the Tuma button. These pages are now static reproductions of the print book.
    $html = [regex]::Replace(
        $html,
        'data-section-type="activity_[^"]+"',
        'data-section-type="text"',
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )

    # Preserve the visible answer space while removing focus, typing, and answer
    # metadata. Existing classes retain the printed line/box dimensions.
    $html = [regex]::Replace(
        $html,
        '<input\b([^>]*)>',
        {
            param($match)
            $attrs = $match.Groups[1].Value
            $classMatch = [regex]::Match($attrs, 'class="([^"]*)"', 'IgnoreCase')
            $classValue = if ($classMatch.Success) { $classMatch.Groups[1].Value } else { '' }
            $classValue = ($classValue -replace '\bfocus:[^\s"]+', '' -replace '\boutline-none\b', '' -replace '\s+', ' ').Trim()
            return '<span class="adt-static-answer-space ' + $classValue + '" aria-hidden="true"></span>'
        },
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )

    $html = [regex]::Replace(
        $html,
        '<textarea\b([^>]*)>[\s\S]*?</textarea>',
        {
            param($match)
            $attrs = $match.Groups[1].Value
            $classMatch = [regex]::Match($attrs, 'class="([^"]*)"', 'IgnoreCase')
            $classValue = if ($classMatch.Success) { $classMatch.Groups[1].Value } else { '' }
            $classValue = ($classValue -replace '\bfocus:[^\s"]+', '' -replace '\bresize-none\b', '' -replace '\boutline-none\b', '' -replace '\s+', ' ').Trim()
            return '<div class="adt-static-answer-space ' + $classValue + '" aria-hidden="true"></div>'
        },
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )

    # Remove page-level answer keys; no correctness data should remain client-side.
    $html = [regex]::Replace(
        $html,
        '<script\b[^>]*>(?=[\s\S]*?window\.correctAnswers)[\s\S]*?</script>',
        '',
        [System.Text.RegularExpressions.RegexOptions]::IgnoreCase
    )

    $html = $html -replace '\s+data-activity-item="[^"]*"', ''
    Set-Content -LiteralPath $path -Value $html -Encoding utf8NoBOM -NoNewline
}

Write-Host "Converted $($files.Count) manifest pages to static book pages."
