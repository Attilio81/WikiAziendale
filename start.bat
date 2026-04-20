@echo off
setlocal

set ROOT=%~dp0
set BACKEND=%ROOT%backend
set FRONTEND=%ROOT%frontend

echo Sincronizzazione .env in backend/...
xcopy /Y "%ROOT%.env" "%BACKEND%\.env*" >nul 2>&1

echo Avvio backend (uvicorn)...
start "LLM Wiki - Backend" cmd /k "cd /d "%BACKEND%" && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Avvio frontend (vite)...
start "LLM Wiki - Frontend" cmd /k "cd /d "%FRONTEND%" && npm run dev -- --port 5175"

echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5175
echo Docs API: http://localhost:8000/docs
echo.
echo Chiudi le finestre dei terminali per fermare i server.
