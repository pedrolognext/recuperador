## Para Windows:
Para lanzar el .exe y que se cree hay que ir a powershell a la carpeta y abrir el entorno virtual que es: 
PS C:\proyectos\recuperador> .\venv\bin\Activate.ps1
Con el ya activo hacer: 
pyinstaller --onefile --windowed --name=CV_Generator_Pro --add-data="logo.png;." gui.py

Es importante que sea powershell.

## Para macOS:
1. Instalar Python 3.x
2. Crear entorno virtual: `python3 -m venv venv`
3. Activar entorno: `source venv/bin/activate`
4. Instalar dependencias: `pip install -r requirements.txt`

5. Compilar - (recomendada, más simple):
   ```bash
   pyinstaller --windowed --name=CV_Generator_Pro \
     --add-data="logo.png:." \
     --add-data="env_loader.py:." \
     --collect-all docx \
     --hidden-import=docx.oxml \
     --hidden-import=docx.parts \
     gui.py
   ```

⚠️ **IMPORTANTE**: En macOS NO usar --onefile porque python-docx no puede resolver las rutas de templates correctamente.
El resultado será un `.app` que funciona como cualquier aplicación de Mac.

## 🔑 Configuración del archivo .env

El archivo ejecutable necesita un archivo `.env` con las claves de API. La ubicación depende del sistema operativo:

### 📁 Windows:
Coloca el archivo `.env` en la **misma carpeta** que el archivo `CV_Generator_Pro.exe`:
```
📁 Carpeta del ejecutable/
├── CV_Generator_Pro.exe
└── .env
```

### 📁 macOS:
Crea el archivo `.env` en la carpeta de **Application Support**:
```
~/Library/Application Support/CV_Generator_Pro/.env
```

**Ruta completa en macOS:**
```
/Users/[tu_usuario]/Library/Application Support/CV_Generator_Pro/.env
```

### 📝 Contenido del archivo .env (ambos sistemas):
```
OPENAI_API_KEY=sk-tu_clave_de_openai_aqui
LLAMA_CLOUD_API_KEY=llx-tu_clave_de_llamacloud_aqui
```


