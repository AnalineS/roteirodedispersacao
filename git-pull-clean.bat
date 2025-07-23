@echo off
REM Script para executar git pull e remover todos os arquivos desktop.ini

git pull %*

REM Remove todos os arquivos desktop.ini do repositório e subpastas
del /s /q desktop.ini

REM Opcional: Remover desktop.ini do controle de versão, se estiver versionado
git rm --cached -f desktop.ini 2>nul

echo "git pull finalizado e arquivos desktop.ini removidos." 