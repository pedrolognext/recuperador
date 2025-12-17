"""
Script para construir el ejecutable standalone con PyInstaller
"""
import PyInstaller.__main__
import os

# Configuración
APP_NAME = "CV_Generator_Pro"
MAIN_SCRIPT = "gui.py"

print("=" * 80)
print("🔨 Construyendo ejecutable con PyInstaller")
print("=" * 80)
print(f"\nNombre: {APP_NAME}")
print(f"Script principal: {MAIN_SCRIPT}")
print(f"Archivos incluidos: logo.png" + (", .env" if os.path.exists('.env') else ""))
print("\nIniciando construcción...\n")

# Construir lista de argumentos para PyInstaller
args = [
    MAIN_SCRIPT,
    f'--name={APP_NAME}',
    '--onefile',              # Un solo ejecutable
    '--windowed',             # Sin consola (solo GUI)
    '--clean',                # Limpia cache antes de construir
    f'--add-data=logo.png{os.pathsep}.',  # Incluir logo
]

# Agregar .env si existe
if os.path.exists('.env'):
    args.append(f'--add-data=.env{os.pathsep}.')

# Ejecutar PyInstaller
PyInstaller.__main__.run(args)

print("\n" + "=" * 80)
print("✅ Construcción completada")
print("=" * 80)
print(f"\nEl ejecutable está en: dist/{APP_NAME}.exe")
print("\nPara distribuir la aplicación:")
print(f"  1. Copia dist/{APP_NAME}.exe a donde quieras")
print("  2. Asegúrate de tener logo.png en la misma carpeta")
print("  3. Configura .env con las API keys")
print("\n¡Listo para usar!")
