@echo off
REM Script para rodar git-pull-clean.bat em todos os repositórios git da pasta especificada

setlocal enabledelayedexpansion

set "ROOTDIR=C:\Users\Ana\Meu Drive\Imagens site Junin\gemini v2"

for /d /r "%ROOTDIR%" %%G in (.) do (
    if exist "%%G\.git" (
        echo Encontrado repositório: %%G
        pushd "%%G"
        call "%ROOTDIR%\git-pull-clean.bat"
        popd
    )
)

echo Todos os git pull + limpeza desktop.ini finalizados. 