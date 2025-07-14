# Script para atualizar o render.yaml no GitHub
Write-Host "🔄 Atualizando render.yaml no GitHub..." -ForegroundColor Yellow

# Verificar se o Git está instalado
try {
    git --version | Out-Null
    Write-Host "✅ Git encontrado!" -ForegroundColor Green
} catch {
    Write-Host "❌ Git não encontrado. Instalando..." -ForegroundColor Red
    Write-Host "Por favor, instale o Git de: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Depois execute este script novamente." -ForegroundColor Yellow
    exit 1
}

# Verificar se já é um repositório Git
if (Test-Path ".git") {
    Write-Host "✅ Repositório Git já inicializado" -ForegroundColor Green
} else {
    Write-Host "🔄 Inicializando repositório Git..." -ForegroundColor Yellow
    git init
    git remote add origin https://github.com/AnalineS/siteroteirodedispersacao.git
}

# Adicionar todos os arquivos
Write-Host "🔄 Adicionando arquivos..." -ForegroundColor Yellow
git add .

# Fazer commit
Write-Host "🔄 Fazendo commit..." -ForegroundColor Yellow
git commit -m "Atualizar render.yaml para usar app_simple:app"

# Fazer push para o GitHub
Write-Host "🔄 Enviando para o GitHub..." -ForegroundColor Yellow
git push -u origin main

Write-Host "✅ Arquivos enviados com sucesso!" -ForegroundColor Green
Write-Host "🌐 Agora vá para o Render e faça um novo deploy manual" -ForegroundColor Cyan
Write-Host "📝 O site deve ficar disponível em: https://roteiro-dispersacao.onrender.com" -ForegroundColor Cyan 