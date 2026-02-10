Param(
    [string]$EnvFile = ".env",
    [string]$ImageName,
    [string]$ImageTag,
    [ValidateSet('dev','prod')][string]$Profile = 'dev',
    [switch]$Push,
    [switch]$Up
)

function Load-EnvFile {
    param($Path)
    if (-not (Test-Path $Path)) { return }
    Get-Content $Path | ForEach-Object {
        if ($_ -match '^\s*#') { return }
        if ($_ -match '^\s*$') { return }
        $parts = $_ -split '=', 2
        if ($parts.Count -ne 2) { return }
        $name = $parts[0].Trim()
        $value = $parts[1].Trim()
        if ($name -and $value -ne '') { Set-Item -Path Env:$name -Value $value }
    }
}

# Load .env if present
Load-EnvFile -Path $EnvFile

# Override with parameters if provided
if ($ImageName) { $env:IMAGE_NAME = $ImageName }
if ($ImageTag)  { $env:IMAGE_TAG  = $ImageTag }

Write-Host "Profile: $Profile"
Write-Host "IMAGE_NAME=${env:IMAGE_NAME}" -ForegroundColor Cyan
Write-Host "IMAGE_TAG=${env:IMAGE_TAG}" -ForegroundColor Cyan

$composeFiles = @('docker-compose.yaml')
if ($Profile -eq 'dev') { $composeFiles += 'docker-compose.dev.yaml' } else { $composeFiles += 'docker-compose.prod.yaml' }

$composeArgs = $composeFiles | ForEach-Object { "-f `"$_`"" } -join ' '

$buildCmd = "docker-compose $composeArgs build"
Write-Host "Running: $buildCmd"
$buildExit = Invoke-Expression $buildCmd; if ($LASTEXITCODE -ne 0) { Write-Error "Build failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }

if ($Push) {
    $pushCmd = "docker-compose $composeArgs push"
    Write-Host "Running: $pushCmd"
    Invoke-Expression $pushCmd; if ($LASTEXITCODE -ne 0) { Write-Error "Push failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }
}

if ($Up) {
    $upCmd = "docker-compose $composeArgs up -d"
    Write-Host "Running: $upCmd"
    Invoke-Expression $upCmd; if ($LASTEXITCODE -ne 0) { Write-Error "Up failed (exit $LASTEXITCODE)"; exit $LASTEXITCODE }
}

Write-Host "Done."
