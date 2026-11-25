"""Revisa que el proyecto pueda correr en otra computadora y en share.streamlit.io.

Uso (desde la carpeta del proyecto):   python revisar.py
No necesita instalar nada.
"""
import ast
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
IGNORAR = {".git", ".venv", "venv", "__pycache__", ".ipynb_checkpoints"}

# nombre al importar -> nombre en requirements.txt (cuando son distintos)
PAQUETES = {
    "sklearn": "scikit-learn", "PIL": "pillow", "cv2": "opencv-python-headless",
    "yaml": "pyyaml", "bs4": "beautifulsoup4", "dotenv": "python-dotenv",
    "docx": "python-docx", "pptx": "python-pptx", "dateutil": "python-dateutil",
    "snowflake": "snowflake", "google": "google",
}
RUTAS_LOCALES = re.compile(r"""["'](/content/|/Users/|/home/|[A-Za-z]:[\\/])|drive/MyDrive""")
SECRETOS = re.compile(
    r"""(ghp_[A-Za-z0-9]{20,}|github_pat_\w{20,}|sk-[A-Za-z0-9_\-]{20,}|AIza[A-Za-z0-9_\-]{30,}"""
    r"""|(password|api_key|apikey|token|secret)\s*=\s*["'][^"']{6,}["'])""",
    re.IGNORECASE,
)

errores, avisos = [], []


def archivos():
    for p in RAIZ.rglob("*"):
        if p.is_file() and not IGNORAR.intersection(p.relative_to(RAIZ).parts):
            yield p


def normalizar(nombre):
    return re.sub(r"[-_.]+", "-", nombre.strip().lower())


def leer_requirements():
    ruta = RAIZ / "requirements.txt"
    if not ruta.exists():
        errores.append("Falta requirements.txt en la carpeta principal.")
        return None
    paquetes = set()
    for linea in ruta.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        linea = linea.split("#")[0].strip()
        if linea.startswith(("!", "%", "pip ")):
            errores.append(f"requirements.txt: escribe solo nombres de librerías, no '{linea}'.")
            continue
        m = re.match(r"[A-Za-z0-9_.\-]+", linea)
        if m:
            paquetes.add(normalizar(m.group()))
    return paquetes


def main():
    if not (RAIZ / "app.py").exists():
        errores.append("Falta app.py en la carpeta principal.")
    requeridos = leer_requirements()
    todos = list(archivos())
    locales = {p.stem for p in todos if p.suffix == ".py"}
    locales |= {p.name for p in RAIZ.iterdir() if p.is_dir()}

    for p in todos:
        nombre = p.relative_to(RAIZ).as_posix()
        mb = p.stat().st_size / 1024 / 1024
        if mb > 100:
            errores.append(f"{nombre}: pesa {mb:.0f} MB. GitHub bloquea archivos de más de 100 MB.")
        elif mb > 25:
            avisos.append(f"{nombre}: pesa {mb:.0f} MB. No se puede subir desde la página web (límite 25 MB).")
        if nombre in (".streamlit/secrets.toml", ".env"):
            avisos.append(f"{nombre}: existe en tu compu. Confirma que NO aparezca en GitHub Desktop.")
            continue
        if p.suffix not in {".py", ".toml", ".txt", ".json"} or p.name == "revisar.py" or mb > 2:
            continue
        texto = p.read_text(encoding="utf-8-sig", errors="replace")
        if SECRETOS.search(texto):
            errores.append(f"{nombre}: parece contener una contraseña o llave. Quítala antes de subir.")
        if p.suffix != ".py":
            continue

        magia = False
        for n, linea in enumerate(texto.splitlines(), 1):
            limpia = linea.strip()
            if limpia.startswith(("!", "%%")) or re.match(r"%(cd|pip|matplotlib|load_ext)\b", limpia):
                errores.append(f"{nombre}, línea {n}: '{limpia[:40]}' solo funciona en Colab. Bórrala.")
                magia = True
            if not limpia.startswith("#") and RUTAS_LOCALES.search(linea):
                errores.append(f"{nombre}, línea {n}: ruta que solo existe en una máquina. Usa Path(__file__).parent.")
        try:
            arbol = ast.parse(texto)
        except SyntaxError as e:
            if not magia:
                errores.append(f"{nombre}, línea {e.lineno}: error de sintaxis ({e.msg}).")
            continue
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                modulos = [a.name for a in nodo.names]
            elif isinstance(nodo, ast.ImportFrom) and nodo.level == 0 and nodo.module:
                modulos = [nodo.module]
            else:
                continue
            for modulo in modulos:
                base = modulo.split(".")[0]
                if modulo.startswith("google.colab") or (
                    isinstance(nodo, ast.ImportFrom) and modulo == "google"
                    and any(a.name == "colab" for a in nodo.names)
                ):
                    errores.append(f"{nombre}: usa google.colab, que no existe fuera de Colab.")
                    continue
                if base in sys.stdlib_module_names or base in locales or requeridos is None:
                    continue
                if base in ("google", "snowflake"):
                    if not any(r.startswith(base) for r in requeridos):
                        errores.append(f"{nombre}: importa '{modulo}' y no veo su paquete en requirements.txt.")
                    continue
                paquete = normalizar(PAQUETES.get(base, base))
                alternativas = {paquete}
                if base == "cv2":
                    alternativas.add("opencv-python")
                if not alternativas & requeridos:
                    errores.append(f"{nombre}: importas '{base}' y falta '{paquete}' en requirements.txt.")

    print("\n=== Revisión del proyecto ===")
    for a in dict.fromkeys(avisos):
        print(f"  AVISO  {a}")
    for e in dict.fromkeys(errores):
        print(f"  ERROR  {e}")
    if errores:
        print(f"\n{len(set(errores))} cosa(s) por corregir antes de hacer push.")
        return 1
    print("  OK  Listo para commit y push.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
