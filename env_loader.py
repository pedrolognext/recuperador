"""
Módulo centralizado para cargar variables de entorno y gestionar directorios
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def get_app_base_dir(app_name="CV_Generator_Pro"):
    """Obtiene el directorio base de la aplicación según el sistema operativo"""
    if sys.platform == "darwin":  # macOS
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":  # Windows
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:  # Linux
        base = Path.home() / ".config"

    app_dir = base / app_name
    app_dir.mkdir(parents=True, exist_ok=True)
    return app_dir

def get_app_temp_dir(app_name="CV_Generator_Pro"):
    """Obtiene el directorio temporal de la aplicación"""
    temp_dir = get_app_base_dir(app_name) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir

def load_env_for_app():
    """Carga el archivo .env desde la ubicación estándar del sistema"""
    env_path = get_app_base_dir() / ".env"
    
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
