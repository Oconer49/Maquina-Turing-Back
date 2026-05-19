@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo [ERROR] No existe el entorno virtual .venv
  echo Ejecuta primero: setup-backend.bat
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
echo Servidor API: http://localhost:8000
echo Documentacion: http://localhost:8000/docs
echo.
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
