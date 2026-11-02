# Import upstream OSIRIS into globe/osiris
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$Target = Join-Path $PSScriptRoot "osiris"
$Temp = Join-Path $env:TEMP ("osiris-import-" + [guid]::NewGuid().ToString("N"))
$Source = Join-Path $Temp "source"

if (Test-Path $Target) {
  throw "Target already exists: $Target. Move or rename it before importing; this script will not overwrite existing work."
}

try {
  git clone --depth 1 https://github.com/simplifaisoul/osiris.git $Source
  if ($LASTEXITCODE -ne 0) { throw "git clone failed." }

  New-Item -ItemType Directory -Path $Target -Force | Out-Null

  $Include = @(
    "src", "public", "engine", "intel", "tools", "docs", ".github",
    "README.md", "LICENSE", "SECURITY.md", "DOCKER.md", "Dockerfile",
    "docker-compose.yml", "deploy.sh", "package.json", "package-lock.json",
    "next.config.ts", "postcss.config.mjs", "tsconfig.json",
    "eslint.config.mjs", "vitest.config.ts", ".env.example",
    ".dockerignore", ".gitattributes", ".gitignore"
  )

  foreach ($Item in $Include) {
    $From = Join-Path $Source $Item
    if (Test-Path $From) {
      $To = Join-Path $Target $Item
      Copy-Item -LiteralPath $From -Destination $To -Recurse -Force
    }
  }

  # Remove non-source runtime/cache material if present.
  Get-ChildItem -LiteralPath $Target -Directory -Recurse -Force |
    Where-Object { $_.Name -in @("node_modules", "__pycache__", ".next", ".venv", "venv", "coverage") } |
    Sort-Object FullName -Descending |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

  Get-ChildItem -LiteralPath $Target -File -Recurse -Force |
    Where-Object { $_.Extension -eq ".pyc" -or $_.Name -eq ".env" } |
    Remove-Item -Force -ErrorAction SilentlyContinue

  Write-Host "OSIRIS source imported to $Target" -ForegroundColor Green
  Write-Host "Next: cd globe/osiris; npm install; npm run dev"
}
finally {
  if (Test-Path $Temp) { Remove-Item -LiteralPath $Temp -Recurse -Force -ErrorAction SilentlyContinue }
}
