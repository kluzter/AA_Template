@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "PY="
for %%V in (3.13 3.12) do (
  if not defined PY (
    py -%%V --version >nul 2>&1 && set "PY=py -%%V"
  )
)
if not defined PY (
  python -c "import sys; sys.exit(0 if sys.version_info[:2] in [(3,12),(3,13)] else 1)" >nul 2>&1 && set "PY=python"
)
if not defined PY goto sin_python

if not exist ".venv\Scripts\python.exe" (
  echo Creando el entorno del proyecto, solo la primera vez...
  %PY% -m venv .venv || goto error
)
echo Instalando librerias de requirements.txt ...
".venv\Scripts\python.exe" -m pip install --quiet --disable-pip-version-check -r requirements.txt || goto error
echo Abriendo la app. Para detenerla presiona Ctrl + C
".venv\Scripts\python.exe" -m streamlit run app.py || goto error
pause
exit /b 0

:sin_python
echo.
echo No encontre Python 3.13 ni 3.12.
echo Instala Python 3.13 desde python.org y vuelve a intentar.
pause
exit /b 1

:error
echo.
echo Algo fallo. Toma captura de esta ventana y compartela con tu equipo o tu profesor.
pause
exit /b 1
