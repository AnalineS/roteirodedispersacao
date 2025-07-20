# Deploy Simples para Netlify
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOY AUTOMATICO PARA NETLIFY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar arquivos necessários
Write-Host "1. Verificando arquivos necessarios..." -ForegroundColor Yellow
$requiredFiles = @("index.html", "package.json", "netlify.toml", "functions/api.js")
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

$deployDir = "deploy_netlify_package"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Copiar arquivos principais
$filesToCopy = @("index.html", "package.json", "netlify.toml")
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
$zipPath = "deploy_netlify.zip"
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
Write-Host "1. Acesse: https://app.netlify.com" -ForegroundColor White
Write-Host "2. Clique em 'Add new site' > 'Deploy manually'" -ForegroundColor White
Write-Host "3. Arraste o arquivo: $zipPath" -ForegroundColor White
Write-Host "4. Aguarde o deploy automatico" -ForegroundColor White
Write-Host "5. Configure o dominio personalizado se necessario" -ForegroundColor White
Write-Host ""
Write-Host "URL final: https://roteirodedispensacao.netlify.app" -ForegroundColor Cyan
Write-Host "" 