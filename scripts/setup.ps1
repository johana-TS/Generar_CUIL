# setup.ps1 - Script de configuración para Windows

Write-Host "Creando entorno virtual..." -ForegroundColor Green
python -m venv .venv

Write-Host "Activando entorno virtual..." -ForegroundColor Green
$venvActivate = Join-Path $PSScriptRoot "..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    . $venvActivate
}

Write-Host "Instalando dependencias..." -ForegroundColor Green
pip install --upgrade pip
pip install -r (Join-Path $PSScriptRoot "..\requirements.txt")

Write-Host "¡Configuración completada! Las dependencias han sido instaladas." -ForegroundColor Green
Write-Host "Para activar el entorno virtual manualmente en el futuro, ejecuta: .venv\Scripts\Activate.ps1" -ForegroundColor Yellow
