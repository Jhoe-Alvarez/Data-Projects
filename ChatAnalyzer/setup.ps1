# Script de instalación rápida para Chatlyzer
# Ejecutar en PowerShell: .\setup.ps1

Write-Host "🚀 Instalando Chatlyzer..." -ForegroundColor Green
Write-Host ""

# Verificar Python
Write-Host "📦 Verificando Python..." -ForegroundColor Cyan
try {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion encontrado" -ForegroundColor Green
} catch {
    Write-Host "❌ Python no está instalado o no está en PATH" -ForegroundColor Red
    Write-Host "   Descarga Python desde: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Instalar dependencias
Write-Host "📚 Instalando dependencias..." -ForegroundColor Cyan
pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Dependencias instaladas correctamente" -ForegroundColor Green
} else {
    Write-Host "❌ Error al instalar dependencias" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Crear carpeta .streamlit si no existe
if (-not (Test-Path ".streamlit")) {
    New-Item -ItemType Directory -Path ".streamlit" | Out-Null
    Write-Host "✓ Carpeta .streamlit creada" -ForegroundColor Green
}

Write-Host ""
Write-Host "✅ Instalación completada!" -ForegroundColor Green
Write-Host ""
Write-Host "Para iniciar la aplicación, ejecuta:" -ForegroundColor Cyan
Write-Host "   streamlit run app.py" -ForegroundColor White
Write-Host ""
