import os
from dotenv import load_dotenv

load_dotenv()

# El directorio raíz: si MULTILINKS_ROOT_DIR existe en .env, lo usa (producción).
# Si no existe (local), asume que la raíz es un nivel arriba de la carpeta 'backend' actual.
DEFAULT_LOCAL_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DIR = os.getenv("MULTILINKS_ROOT_DIR", DEFAULT_LOCAL_ROOT)

# Subdirectorios principales
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
DATA_DIR = os.path.join(BACKEND_DIR, "data")
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")
USUARIOS_DIR = os.path.join(ROOT_DIR, "usuarios")

# Asegurarse de que existan al iniciar la app
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(USUARIOS_DIR, exist_ok=True)
