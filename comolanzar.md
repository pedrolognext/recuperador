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
5. Compilar: `pyinstaller --onefile --windowed --name=CV_Generator_Pro --add-data="logo.png:." gui.py`

El archivo ejecutable se debe usar con un .env con clave de openai y llamacloud.
