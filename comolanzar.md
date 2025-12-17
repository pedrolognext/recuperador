para lanzar el .exe y que se cree hay que ir a powershell a la carpeta y abrir el entorno virtual que es: 
PS C:\proyectos\recuperador> .\venv\bin\Activate.ps1
 con el ya activo hacer: 
 pyinstaller --onefile --windowed --name=CV_Generator_Pro --add-data="logo.png;." gui.py

es importante que sea powershell. 

el archivo .exe se debe usar con un .env con clave de openai y llamacloud.
