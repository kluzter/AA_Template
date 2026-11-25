#!/bin/bash
cd "$(dirname "$0")" || exit 1

PY=""
for c in python3.13 python3.12 /usr/local/bin/python3.13 /usr/local/bin/python3.12 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if sys.version_info[:2] in [(3,12),(3,13)] else 1)' 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "No encontré Python 3.13 ni 3.12. Instala Python 3.13 desde python.org y vuelve a intentar."
  exit 1
fi

error() { echo; echo "Algo falló. Toma captura de esta ventana y compártela."; exit 1; }

if [ ! -x .venv/bin/python ]; then
  echo "Creando el entorno del proyecto (solo la primera vez)..."
  "$PY" -m venv .venv || error
fi
echo "Instalando librerías de requirements.txt ..."
.venv/bin/python -m pip install --quiet --disable-pip-version-check -r requirements.txt || error
echo "Abriendo la app. Para detenerla presiona Ctrl + C"
.venv/bin/python -m streamlit run app.py
