"""
Módulo centralizado para cargar variables de entorno
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def load_env_for_app():
    """Carga el archivo .env desde la ubicación estándar del sistema"""
    # 1️⃣ ruta estándar mac / win / linux
    if sys.platform == "darwin":
        env_path = Path.home() / "Library" / "Application Support" / "CV_Generator_Pro" / ".env"
    elif sys.platform == "win32":
        env_path = Path(os.environ.get("APPDATA", Path.home())) / "CV_Generator_Pro" / ".env"
    else:
        env_path = Path.home() / ".config" / "CV_Generator_Pro" / ".env"

    # Crear directorio si no existe
    env_path.parent.mkdir(parents=True, exist_ok=True)
    
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ .env cargado desde: {env_path}")
        return True
    else:
        print(f"❌ .env NO encontrado en: {env_path}")
        print(f"📝 Crea el archivo aquí: {env_path}")
        return False

# Cargar automáticamente cuando se importa este módulo
load_env_for_app()
print("🔥 env_loader IMPORTADO")
