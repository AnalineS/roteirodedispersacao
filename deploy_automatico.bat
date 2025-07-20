@echo off
echo ========================================
echo DEPLOY AUTOMATICO PARA RENDER
echo ========================================

echo.
echo 1. Verificando arquivos necessarios...
if not exist "app_optimized.py" (
    echo ERRO: app_optimized.py nao encontrado!
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERRO: requirements.txt nao encontrado!
    pause
    exit /b 1
)

echo ✓ Arquivos principais encontrados

echo.
echo 2. Verificando estrutura de pastas...
if not exist "templates" mkdir templates
if not exist "static" mkdir static
if not exist "PDFs" mkdir PDFs

echo ✓ Estrutura de pastas verificada

echo.
echo 3. Criando arquivo ZIP para deploy...
powershell -Command "Compress-Archive -Path 'app_optimized.py', 'requirements.txt', 'runtime.txt', 'gunicorn.conf.py', 'render.yaml', 'templates', 'static', 'PDFs', 'functions' -DestinationPath 'deploy_render.zip' -Force"

if exist "deploy_render.zip" (
    echo ✓ Arquivo ZIP criado com sucesso: deploy_render.zip
) else (
    echo ERRO: Falha ao criar arquivo ZIP
    pause
    exit /b 1
)

echo.
echo 4. Verificando tamanho do arquivo...
powershell -Command "$size = (Get-Item 'deploy_render.zip').Length; Write-Host 'Tamanho do ZIP:' ([math]::Round($size/1MB, 2)) 'MB'"

echo.
echo ========================================
echo DEPLOY PRONTO!
echo ========================================
echo.
echo INSTRUCOES PARA DEPLOY:
echo 1. Acesse: https://dashboard.render.com
echo 2. Clique em "New +" e selecione "Web Service"
echo 3. Conecte seu repositorio GitHub ou faça upload do arquivo deploy_render.zip
echo 4. Configure:
echo    - Name: roteiro-dispersacao
echo    - Environment: Python
echo    - Build Command: pip install -r requirements.txt
echo    - Start Command: gunicorn app_optimized:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
echo 5. Clique em "Create Web Service"
echo.
echo O arquivo deploy_render.zip esta pronto para upload!
echo.
pause 