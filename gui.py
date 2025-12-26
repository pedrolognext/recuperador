#!/usr/bin/env python3
"""
GUI Profesional para Generador de CVs desde PDF
"""

import os
import sys
import json
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

# Cargar variables de entorno desde ubicación estándar
import env_loader
from env_loader import get_app_base_dir

from main import process_cv_from_pdf

# Configuración - usar Application Support en lugar de directorio del ejecutable
CONFIG_FILE = get_app_base_dir() / ".cv_generator_config.json"
LOGO_FILE = "logo.png"

# Colores del tema profesional
COLORS = {
    "primary": "#2563eb",
    "primary_dark": "#1e40af",
    "secondary": "#10b981",
    "background": "#f8fafc",
    "surface": "#ffffff",
    "text": "#1e293b",
    "text_light": "#64748b",
    "border": "#e2e8f0",
    "error": "#ef4444",
    "warning": "#f59e0b"
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(cfg: dict) -> None:
    try:
        # Asegurar que el directorio existe
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


class CVGeneratorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        
        # DEBUG: Mostrar información del sistema
        print("CWD:", os.getcwd())
        print("ENV KEY:", os.getenv("OPENAI_API_KEY"))
        print("LLAMA KEY:", os.getenv("LLAMA_CLOUD_API_KEY"))
        print("SYS PLATFORM:", sys.platform)
        print("EXECUTABLE:", sys.executable)
        print("FROZEN:", getattr(sys, 'frozen', False))
        
        self.title("CV Generator Pro")
        self.geometry("1000x750")
        self.configure(bg=COLORS["background"])
        
        try:
            self.state('zoomed')  # Windows
        except:
            pass
        
        self.cfg = load_config()
        
        # Variables
        self.pdf_path_var = tk.StringVar(value=self.cfg.get("last_pdf", ""))
        self.output_dir_var = tk.StringVar(value=self.cfg.get("output_dir", os.getcwd()))
        self.reference_var = tk.StringVar(value=self.cfg.get("last_reference", ""))
        self.candidate_name_var = tk.StringVar(value=self.cfg.get("last_name", ""))
        self.language_var = tk.StringVar(value=self.cfg.get("language", "es"))
        self.status_var = tk.StringVar(value="Listo para comenzar")
        self.processing = False
        
        self._setup_styles()
        self._build_ui()
    
    def _setup_styles(self) -> None:
        style = ttk.Style()
        style.theme_use('clam')
        
        # Estilo para botones pequeños (Seleccionar)
        style.configure(
            "Primary.TButton",
            background=COLORS["primary"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("Helvetica", 9, "bold"),
            padding=(12, 8)
        )
        style.map("Primary.TButton",
            foreground=[("disabled", "#94a3b8"), ("active", "white"), ("!disabled", "white")],
            background=[("disabled", "#cbd5e1"), ("active", COLORS["primary_dark"]), ("!disabled", COLORS["primary"])],
            relief=[("pressed", "flat"), ("!pressed", "flat")]
        )
        
        # Estilo para botón grande (GENERAR CV)
        style.configure(
            "Success.TButton",
            background=COLORS["secondary"],
            foreground="white",
            borderwidth=0,
            focuscolor="none",
            font=("Helvetica", 14, "bold"),
            padding=(14, 12)
        )
        style.map("Success.TButton",
            foreground=[("disabled", "#94a3b8"), ("active", "white"), ("!disabled", "white")],
            background=[("disabled", "#cbd5e1"), ("active", "#059669"), ("!disabled", COLORS["secondary"])],
            relief=[("pressed", "flat"), ("!pressed", "flat")]
        )
        
        style.configure(
            "Title.TLabel",
            font=("Helvetica", 20, "bold"),
            foreground=COLORS["text"],
            background=COLORS["background"]
        )
        
        style.configure(
            "Subtitle.TLabel",
            font=("Helvetica", 10),
            foreground=COLORS["text_light"],
            background=COLORS["background"]
        )
    
    def _build_ui(self) -> None:
        main_container = tk.Frame(self, bg=COLORS["background"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # HEADER
        header_frame = tk.Frame(main_container, bg=COLORS["background"])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title = ttk.Label(
            header_frame,
            text="📄 CV Generator Pro",
            style="Title.TLabel"
        )
        title.pack(side=tk.LEFT)
        
        subtitle = ttk.Label(
            header_frame,
            text="Genera CVs profesionales desde PDFs de forma automática",
            style="Subtitle.TLabel"
        )
        subtitle.pack(side=tk.LEFT, padx=(15, 0), pady=(10, 0))
        
        # CONTENT (dos columnas)
        content_frame = tk.Frame(main_container, bg=COLORS["background"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        left_column = tk.Frame(content_frame, bg=COLORS["background"])
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        right_column = tk.Frame(content_frame, bg=COLORS["background"])
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # === COLUMNA IZQUIERDA: CONTROLES ===
        
        # CARD 1: Archivo PDF
        pdf_card = self._create_card(left_column, "📁 Archivo PDF")
        
        pdf_input_frame = tk.Frame(pdf_card, bg=COLORS["surface"])
        pdf_input_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.pdf_entry = tk.Entry(
            pdf_input_frame,
            textvariable=self.pdf_path_var,
            font=("Helvetica", 10),
            insertbackground="black",
            relief="solid",
            borderwidth=1,
            bg=COLORS["surface"],
            fg=COLORS["text"]  # 🔑 CLAVE para macOS
        )
        self.pdf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        
        pdf_btn = ttk.Button(
            pdf_input_frame,
            text="Seleccionar",
            command=self._choose_pdf,
            style="Primary.TButton",
            cursor="hand2"
        )
        pdf_btn.pack(side=tk.LEFT)
        
        # CARD 2: Configuración
        config_card = self._create_card(left_column, "⚙️ Configuración del CV")
        
        # Referencia
        self._create_input_row(
            config_card,
            "Referencia:",
            self.reference_var,
            "ej: CAND0001 L.L.L"
        )
        
        # Nombre
        self._create_input_row(
            config_card,
            "Nombre Candidato:",
            self.candidate_name_var,
            "(opcional - se extrae del PDF)"
        )
        
        # Idioma
        lang_frame = tk.Frame(config_card, bg=COLORS["surface"])
        lang_frame.pack(fill=tk.X, padx=15, pady=10)
        
        lang_label = tk.Label(
            lang_frame,
            text="Idioma del documento:",
            font=("Helvetica", 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        )
        lang_label.pack(anchor=tk.W, pady=(0, 8))
        
        lang_buttons = tk.Frame(lang_frame, bg=COLORS["surface"])
        lang_buttons.pack(fill=tk.X)
        
        tk.Radiobutton(
            lang_buttons,
            text="🇪🇸 Español",
            variable=self.language_var,
            value="es",
            font=("Helvetica", 10),
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activeforeground=COLORS["text"],  # 🔑 Para macOS
            selectcolor=COLORS["surface"],
            activebackground=COLORS["surface"],
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=(0, 30))
        
        tk.Radiobutton(
            lang_buttons,
            text="🇬🇧 English",
            variable=self.language_var,
            value="en",
            font=("Helvetica", 10),
            bg=COLORS["surface"],
            fg=COLORS["text"],
            activeforeground=COLORS["text"],  # 🔑 Para macOS
            selectcolor=COLORS["surface"],
            activebackground=COLORS["surface"],
            cursor="hand2"
        ).pack(side=tk.LEFT)
        
        # CARD 3: Carpeta de salida
        output_card = self._create_card(left_column, "💾 Carpeta de Salida")
        
        output_frame = tk.Frame(output_card, bg=COLORS["surface"])
        output_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.output_entry = tk.Entry(
            output_frame,
            textvariable=self.output_dir_var,
            font=("Helvetica", 10),
            insertbackground="black",
            relief="solid",
            borderwidth=1,
            bg=COLORS["surface"],
            fg=COLORS["text"]  # 🔑 CLAVE para macOS
        )
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))
        
        output_btn = ttk.Button(
            output_frame,
            text="Seleccionar",
            command=self._choose_output_dir,
            style="Primary.TButton",
            cursor="hand2"
        )
        output_btn.pack(side=tk.LEFT)
        
        # BOTÓN GENERAR
        generate_frame = tk.Frame(left_column, bg=COLORS["background"])
        generate_frame.pack(fill=tk.X, pady=20)
        
        self.generate_btn = ttk.Button(
            generate_frame,
            text="🚀 GENERAR CV",
            command=self._on_generate,
            style="Success.TButton",
            cursor="hand2"
        )
        self.generate_btn.pack(fill=tk.X, ipady=5)
        
        # Status bar
        status_frame = tk.Frame(left_column, bg=COLORS["surface"], relief="solid", borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Helvetica", 9),
            bg=COLORS["surface"],
            fg=COLORS["text_light"],
            anchor=tk.W,
            padx=15,
            pady=10
        )
        status_label.pack(fill=tk.X)
        
        # === COLUMNA DERECHA: CONSOLA ===
        
        console_card = self._create_card(right_column, "📊 Consola de Progreso", full_height=True)
        
        console_container = tk.Frame(console_card, bg=COLORS["surface"])
        console_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.console_text = tk.Text(
            console_container,
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="#d4d4d4",
            font=("Consolas", 9),
            relief="flat",
            padx=10,
            pady=10
        )
        self.console_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(
            console_container,
            orient=tk.VERTICAL,
            command=self.console_text.yview
        )
        self.console_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mensaje inicial
        self._append_console("=" * 80 + "\n")
        self._append_console("  CV GENERATOR PRO - Sistema de Generación Automática de CVs\n")
        self._append_console("=" * 80 + "\n\n")
        
        # Información de debug del sistema
        self._append_console("🔧 INFORMACIÓN DEL SISTEMA:\n")
        self._append_console(f"   📁 Directorio actual: {os.getcwd()}\n")
        self._append_console(f"   🐍 Python: {sys.executable}\n")
        self._append_console(f"   💻 Plataforma: {sys.platform}\n")
        self._append_console(f"   📦 Ejecutable: {getattr(sys, 'frozen', False)}\n")
        self._append_console(f"   🔑 OpenAI Key: {'✅ Configurada' if os.getenv('OPENAI_API_KEY') else '❌ No encontrada'}\n")
        self._append_console(f"   🦙 Llama Key: {'✅ Configurada' if os.getenv('LLAMA_CLOUD_API_KEY') else '❌ No encontrada'}\n")
        self._append_console("\n")
        
        self._append_console("✅ Sistema inicializado correctamente\n")
        self._append_console("📌 Selecciona un PDF y configura los parámetros para comenzar\n")
        self._append_console("\n💡 Tips:\n")
        self._append_console("   • La referencia es obligatoria (ej: CAND0001 L.L.L)\n")
        self._append_console("   • El nombre es opcional (se extrae automáticamente del PDF)\n")
        self._append_console("   • Selecciona el idioma según el contenido del PDF\n")
        self._append_console("\n" + "-" * 80 + "\n\n")
    
    def _create_card(self, parent, title, full_height=False) -> tk.Frame:
        card = tk.Frame(parent, bg=COLORS["surface"], relief="solid", borderwidth=1)
        if full_height:
            card.pack(fill=tk.BOTH, expand=True, pady=5)
        else:
            card.pack(fill=tk.X, pady=5)
        
        header = tk.Frame(card, bg=COLORS["surface"])
        header.pack(fill=tk.X, padx=15, pady=15)
        
        title_label = tk.Label(
            header,
            text=title,
            font=("Helvetica", 11, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        )
        title_label.pack(side=tk.LEFT)
        
        sep = tk.Frame(card, bg=COLORS["border"], height=1)
        sep.pack(fill=tk.X, padx=15)
        
        return card
    
    def _create_input_row(self, parent, label_text, variable, placeholder=""):
        row = tk.Frame(parent, bg=COLORS["surface"])
        row.pack(fill=tk.X, padx=15, pady=10)
        
        label = tk.Label(
            row,
            text=label_text,
            font=("Helvetica", 10, "bold"),
            bg=COLORS["surface"],
            fg=COLORS["text"]
        )
        label.pack(anchor=tk.W, pady=(0, 5))
        
        entry = tk.Entry(
            row,
            textvariable=variable,
            font=("Helvetica", 10),
            insertbackground="black",
            relief="solid",
            borderwidth=1,
            bg=COLORS["surface"],
            fg=COLORS["text"]  # 🔑 CLAVE para macOS
        )
        entry.pack(fill=tk.X, ipady=8)
        
        if placeholder:
            hint = tk.Label(
                row,
                text=placeholder,
                font=("Helvetica", 8),
                bg=COLORS["surface"],
                fg=COLORS["text_light"]
            )
            hint.pack(anchor=tk.W, pady=(3, 0))
    
    def _choose_pdf(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar PDF del CV",
            initialdir=os.path.dirname(self.pdf_path_var.get()) or os.getcwd(),
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if path:
            self.pdf_path_var.set(path)
            self.cfg["last_pdf"] = path
            save_config(self.cfg)
            self._append_console(f"📄 PDF seleccionado: {os.path.basename(path)}\n")
    
    def _choose_output_dir(self) -> None:
        path = filedialog.askdirectory(
            title="Seleccionar carpeta de salida",
            initialdir=self.output_dir_var.get() or os.getcwd()
        )
        if path:
            self.output_dir_var.set(path)
            self.cfg["output_dir"] = path
            save_config(self.cfg)
            self._append_console(f"💾 Carpeta de salida: {path}\n")
    
    def _on_generate(self) -> None:
        if self.processing:
            messagebox.showwarning("Aviso", "Ya hay un proceso en ejecución")
            return
        
        # Validar PDF
        pdf_path = self.pdf_path_var.get().strip()
        if not pdf_path:
            messagebox.showerror("Error", "Por favor selecciona un archivo PDF")
            return
        
        if not os.path.isfile(pdf_path):
            messagebox.showerror("Error", f"El archivo PDF no existe:\n{pdf_path}")
            return
        
        # Validar referencia
        reference = self.reference_var.get().strip()
        if not reference:
            messagebox.showerror("Error", "La referencia es obligatoria\n\nEjemplo: CAND0001 L.L.L")
            return
        
        # Validar carpeta de salida
        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            messagebox.showerror("Error", "Por favor selecciona una carpeta de salida")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Obtener configuración
        candidate_name = self.candidate_name_var.get().strip() or None
        language = self.language_var.get()
        
        # Guardar configuración
        self.cfg["last_reference"] = reference
        self.cfg["last_name"] = self.candidate_name_var.get().strip()
        self.cfg["language"] = language
        save_config(self.cfg)
        
        # Preparar UI
        self.processing = True
        self.generate_btn.state(["disabled"])  # ttk.Button usa state([...])
        self.status_var.set("⏳ Procesando...")
        self.console_text.delete("1.0", tk.END)
        
        # Ejecutar en thread separado
        thread = threading.Thread(
            target=self._worker_generate,
            args=(pdf_path, output_dir, language, reference, candidate_name),
            daemon=True
        )
        thread.start()
    
    def _worker_generate(self, pdf_path: str, output_dir: str, language: str, reference: str, candidate_name: str) -> None:
        try:
            original_stdout = sys.stdout
            sys.stdout = ConsoleRedirector(self)
            
            output_path = os.path.join(output_dir, f"CV_{reference.replace(' ', '_')}.docx")
            
            result = process_cv_from_pdf(
                pdf_path=pdf_path,
                logo_path=LOGO_FILE,
                output_path=output_path,
                language=language,
                custom_reference=reference,
                custom_name=candidate_name
            )
            
            sys.stdout = original_stdout
            
            if result:
                self._done(True, result)
            else:
                self._done(False, "Error al generar el CV")
                
        except Exception as e:
            sys.stdout = original_stdout
            self._append_console(f"\n❌ ERROR CRÍTICO: {type(e).__name__}: {str(e)}\n")
            import traceback
            self._append_console(traceback.format_exc())
            self._done(False, str(e))
    
    def _append_console(self, text: str) -> None:
        self.console_text.insert(tk.END, text)
        self.console_text.see(tk.END)
        self.console_text.update()
    
    def _done(self, success: bool, message: str = "") -> None:
        self.processing = False
        self.generate_btn.state(["!disabled"])  # ttk.Button usa state([...]) para habilitar
        
        if success:
            self.status_var.set("✅ Completado exitosamente")
            messagebox.showinfo(
                "¡Éxito!",
                f"CV generado correctamente:\n\n{message}\n\n¡Proceso completado!"
            )
        else:
            self.status_var.set("❌ Error en el proceso")
            messagebox.showerror(
                "Error",
                f"Ocurrió un error al generar el CV:\n\n{message}"
            )


class ConsoleRedirector:
    def __init__(self, app):
        self.app = app
    
    def write(self, text):
        self.app._append_console(text)
    
    def flush(self):
        pass


def main():
    if not os.path.isfile(LOGO_FILE):
        print(f"⚠️  Advertencia: No se encontró '{LOGO_FILE}' en la carpeta actual")
        print(f"   El CV se generará sin logo")
    
    app = CVGeneratorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
