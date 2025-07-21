@echo off
echo ========================================
echo   DEPLOY MANUAL PARA RENDER
echo ========================================
echo.

echo 1. Verificando arquivos necessários...
if not exist "app.py" (
    echo ERRO: app.py não encontrado!
    pause
    exit /b 1
)

if not exist "requirements.txt" (
    echo ERRO: requirements.txt não encontrado!
    pause
    exit /b 1
)

if not exist "render.yaml" (
    echo ERRO: render.yaml não encontrado!
    pause
    exit /b 1
)

echo ✅ Todos os arquivos necessários encontrados!
echo.

echo 2. Criando pacote de deploy...
if exist "deploy_package" rmdir /s /q "deploy_package"
mkdir "deploy_package"

echo    Copiando arquivos principais...
copy "app.py" "deploy_package\"
copy "requirements.txt" "deploy_package\"
copy "runtime.txt" "deploy_package\"
copy "gunicorn.conf.py" "deploy_package\"
copy "render.yaml" "deploy_package\"

echo    Copiando pastas...
xcopy "templates" "deploy_package\templates\" /e /i /y
xcopy "static" "deploy_package\static\" /e /i /y
xcopy "PDFs" "deploy_package\PDFs\" /e /i /y

echo ✅ Pacote de deploy criado!
echo.

echo 3. Criando arquivo ZIP...
if exist "deploy_render_manual.zip" del "deploy_render_manual.zip"
powershell -command "Compress-Archive -Path 'deploy_package\*' -DestinationPath 'deploy_render_manual.zip'"

echo ✅ Arquivo ZIP criado: deploy_render_manual.zip
echo.

echo 4. INSTRUÇÕES PARA DEPLOY NO RENDER:
echo.
echo   1. Acesse: https://dashboard.render.com
echo   2. Clique em "New +" → "Web Service"
echo   3. Faça upload do arquivo: deploy_render_manual.zip
echo   4. Configure:
echo      - Name: roteiro-dispersacao-chatbot
echo      - Environment: Python
echo      - Build Command: pip install -r requirements.txt
echo      - Start Command: gunicorn app:app
echo   5. Clique em "Create Web Service"
echo.
echo   6. Configure as variáveis de ambiente:
echo      - LANGFLOW_API_KEY: sua_chave_langflow
echo      - RENDER_API_KEY: sua_chave_render
echo      - OPENAI_API_KEY: sua_chave_openai (opcional)
echo.
echo   7. Aguarde o deploy (pode levar alguns minutos)
echo   8. Acesse: https://roteiro-dispersacao-chatbot.onrender.com
echo.

echo ========================================
echo   DEPLOY MANUAL CONCLUÍDO!
echo ========================================
echo.
echo Arquivo ZIP criado: deploy_render_manual.zip
echo Tamanho: 
powershell -command "(Get-Item 'deploy_render_manual.zip').Length / 1MB"
echo MB
echo.
pause 