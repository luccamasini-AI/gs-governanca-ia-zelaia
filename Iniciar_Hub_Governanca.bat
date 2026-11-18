@echo off
chcp 65001 >nul
title Hub Web Moderno de Governanca em IA e Business Analytics - CitizenTech ZelaIA
echo ============================================================================
echo   FIAP - GLOBAL SOLUTION 2026.2 - GOVERNANCA EM IA E BUSINESS ANALYTICS
echo   Encerrando instancias anteriores na porta 8505 (se houver)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8505 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
echo   Iniciando o Hub Web Moderno (Bento Grid SaaS) em http://127.0.0.1:8505 ...
echo ============================================================================
python hub_governanca.py
pause
