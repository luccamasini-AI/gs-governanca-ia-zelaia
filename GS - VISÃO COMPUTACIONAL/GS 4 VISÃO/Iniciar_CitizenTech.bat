@echo off
chcp 65001 >nul
title CitizenTech - Modulo de Visao Computacional para Manutencao Urbana
cd /d "%~dp0"

echo ============================================================================
echo   CITIZENTECH - VISAO COMPUTACIONAL PARA MANUTENCAO URBANA
echo   Inicializando ambiente e servidor web interativo (Streamlit)...
echo ============================================================================
echo.

where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where py >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo [ERRO] Python nao foi encontrado no PATH deste computador.
        echo Por favor, instale o Python 3.10+ e tente novamente.
        pause
        exit /b 1
    )
)

%PYTHON_CMD% -c "import streamlit, cv2, PIL, numpy, pandas" >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Instalando dependencias leves necessarias ^(streamlit, opencv, pillow, numpy, pandas^)...
    %PYTHON_CMD% -m pip install -r requirements.txt
)

echo.
echo [OK] Abrindo o prototipo CitizenTech no navegador padrao...
echo      ^(Para encerrar o servidor, basta fechar esta janela ou pressionar Ctrl+C^)
echo.

%PYTHON_CMD% -m streamlit run app_citizentech.py --server.headless false
pause
