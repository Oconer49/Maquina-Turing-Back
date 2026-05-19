@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

echo === Configuracion del backend (Simulador Turing) ===
echo.

set "PYTHON_CMD="

where py >nul 2>&1
if %ERRORLEVEL%==0 (
  py -3 -c "import sys" >nul 2>&1
  if !ERRORLEVEL!==0 set "PYTHON_CMD=py -3"
)

if not defined PYTHON_CMD (
  for %%P in (
    "%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "C:\Python313\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
  ) do (
    if exist %%P set "PYTHON_CMD=%%~P"
  )
)

if not defined PYTHON_CMD (
  echo [ERROR] Python 3.11+ no esta instalado o no esta en el PATH.
  echo.
  echo 1. Descarga Python desde: https://www.python.org/downloads/
  echo 2. Durante la instalacion marca: "Add python.exe to PATH"
  echo 3. Cierra y abre PowerShell de nuevo.
  echo 4. Vuelve a ejecutar este archivo: setup-backend.bat
  echo.
  pause
  exit /b 1
)

echo Usando Python: %PYTHON_CMD%
echo.

%PYTHON_CMD% -m venv .venv
if %ERRORLEVEL% neq 0 (
  echo [ERROR] No se pudo crear el entorno virtual.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if %ERRORLEVEL% neq 0 (
  echo [ERROR] Fallo la instalacion de dependencias.
  pause
  exit /b 1
)

echo.
echo === Listo ===
echo Ejecuta start-backend.bat para iniciar el servidor en http://localhost:8000
echo.
pause
