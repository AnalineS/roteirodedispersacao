# Deploy Simples para Render
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY AUTOMATICO PARA RENDER" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar arquivos necessários
Write-Host "1. Verificando arquivos necessarios..." -ForegroundColor Yellow
$requiredFiles = @("app_optimized.py", "requirements.txt", "runtime.txt", "render.yaml")
$missingFiles = @()

foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "Arquivos faltando:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "   - $file" -ForegroundColor Red
    }
    exit 1
}

Write-Host "Todos os arquivos necessarios encontrados" -ForegroundColor Green

# Criar pacote de deploy
Write-Host ""
Write-Host "2. Criando pacote de deploy..." -ForegroundColor Yellow

$deployDir = "deploy_package"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copiar arquivos
$filesToCopy = @("app_optimized.py", "requirements.txt", "runtime.txt", "gunicorn.conf.py", "render.yaml")
foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Copy-Item $file $deployDir
        Write-Host "   Copiado: $file" -ForegroundColor Green
    }
}

# Copiar diretórios
$dirsToCopy = @("templates", "static", "PDFs", "functions")
foreach ($dir in $dirsToCopy) {
    if (Test-Path $dir) {
        Copy-Item $dir $deployDir -Recurse
        Write-Host "   Copiado: $dir/" -ForegroundColor Green
    }
}

# Criar ZIP
$zipPath = "deploy_render.zip"
if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path "$deployDir\*" -DestinationPath $zipPath -Force

$size = (Get-Item $zipPath).Length / 1MB
Write-Host "Pacote criado: $zipPath ($([math]::Round($size, 2)) MB)" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY PRONTO!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "INSTRUCOES PARA DEPLOY:" -ForegroundColor White
Write-Host "1. Acesse: https://dashboard.render.com" -ForegroundColor White
Write-Host "2. Clique em 'New +' e selecione 'Web Service'" -ForegroundColor White
Write-Host "3. Faça upload do arquivo: $zipPath" -ForegroundColor White
Write-Host "4. Configure:" -ForegroundColor White
Write-Host "   - Name: roteiro-dispersacao" -ForegroundColor Gray
Write-Host "   - Environment: Python" -ForegroundColor Gray
Write-Host "   - Build Command: pip install -r requirements.txt" -ForegroundColor Gray
Write-Host "   - Start Command: gunicorn app_optimized:app --bind 0.0.0.0:`$PORT --workers 1 --timeout 120" -ForegroundColor Gray
Write-Host "5. Clique em 'Create Web Service'" -ForegroundColor White
Write-Host ""
Write-Host "URL final: https://roteiro-dispersacao.onrender.com" -ForegroundColor Cyan
Write-Host "" 