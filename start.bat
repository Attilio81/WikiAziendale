@echo off
setlocal

set ROOT=%~dp0
set BACKEND=%ROOT%backend
set FRONTEND=%ROOT%frontend

echo ============================================================
echo  WikiAziendale - Setup e Avvio
echo ============================================================
echo.

REM --- Sincronizza .env ---
echo [1/4] Sincronizzazione .env in backend/...
xcopy /Y "%ROOT%.env" "%BACKEND%\.env*" >nul 2>&1

REM --- Dipendenze Python backend ---
echo [2/4] Installazione dipendenze Python backend...
pip install -e "%BACKEND%[dev]" --quiet
if errorlevel 1 (
    echo ERRORE: pip install fallito. Assicurati che Python sia nel PATH.
    pause
    exit /b 1
)

REM --- Dipendenze Node frontend ---
echo [3/4] Installazione dipendenze Node frontend...
if not exist "%FRONTEND%\node_modules" (
    echo     node_modules non trovato, eseguo npm install...
    pushd "%FRONTEND%"
    npm install
    popd
    if errorlevel 1 (
        echo ERRORE: npm install fallito. Assicurati che Node.js sia nel PATH.
        pause
        exit /b 1
    )
) else (
    echo     node_modules gia presente, salto npm install.
)

REM --- Avvio server ---
echo [4/4] Avvio server...
echo.

start "LLM Wiki - Backend" cmd /k "cd /d "%BACKEND%" && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
start "LLM Wiki - Frontend" cmd /k "cd /d "%FRONTEND%" && npm run dev -- --port 5175"

echo ============================================================
echo  Server avviati!
echo.
echo  Backend:   http://localhost:8000
echo  Frontend:  http://localhost:5175
echo  Docs API:  http://localhost:8000/docs
echo ============================================================
echo.
echo Chiudi le finestre dei terminali per fermare i server.
