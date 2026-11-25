# Nombre del proyecto

Qué problema resuelve (2 líneas).

- App publicada: (pega aquí la URL de share.streamlit.io)
- Python: 3.13

## Cómo ejecutarlo en tu computadora

1. Instala GitHub Desktop y Python 3.13 (o 3.12).
2. En GitHub Desktop: File > Clone repository, elige este repositorio.
3. Antes de trabajar: Fetch origin y, si aparece, Pull origin.
4. Windows: Repository > Show in Explorer y doble clic en `ejecutar_windows.bat`.
   Mac: Repository > Open in Terminal y escribe `bash ejecutar_mac.command`.
5. Se abre http://localhost:8501. Para detener: Ctrl + C en la ventana negra.

A mano (equivalente):

    python -m venv .venv
    # Windows: .venv\Scripts\activate      Mac: source .venv/bin/activate
    python -m pip install -r requirements.txt
    python -m streamlit run app.py

## Reglas del equipo

1. Pull antes de empezar. Commit y push al terminar.
2. Una persona por archivo a la vez.
3. Si corre en tu compu, entonces haces push. Nunca antes.
4. No se suben contraseñas, llaves ni datos confidenciales del cliente.
