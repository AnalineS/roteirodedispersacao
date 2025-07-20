@echo off
echo ========================================
echo 🚀 DEPLOY AUTOMATICO PARA RENDER
echo ========================================
echo.

echo Executando script PowerShell...
powershell -ExecutionPolicy Bypass -File "deploy_simple.ps1"

echo.
echo ========================================
echo DEPLOY CONCLUIDO!
echo ========================================
echo.
echo 📋 PROXIMOS PASSOS:
echo 1. Acesse: https://dashboard.render.com
echo 2. Clique em "New +" e selecione "Web Service"
echo 3. Faça upload do arquivo deploy_render.zip
echo 4. Configure o serviço conforme instruções acima
echo 5. Aguarde o build (5-10 minutos)
echo.
echo 🌐 URL final: https://roteiro-dispersacao.onrender.com
echo.
pause 