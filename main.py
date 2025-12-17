"""
Aplicación principal para generar CVs desde PDFs
Flujo: PDF -> LlamaParse -> ChatGPT -> Word
"""
import os
import sys
from pathlib import Path
from services import extract_text_from_pdf, structure_cv_with_chatgpt, validate_cv_data
from gemini import generate_cv
from dotenv import load_dotenv

load_dotenv()


def process_cv_from_pdf(pdf_path, logo_path="logo.png", output_path=None, language="es", custom_reference=None, custom_name=None):
    """
    Procesa un CV desde PDF y genera un documento Word formateado
    
    Args:
        pdf_path: Ruta al archivo PDF del CV
        logo_path: Ruta al logo para el documento (default: logo.png)
        output_path: Ruta de salida para el documento Word (default: auto-generado)
        language: Idioma del documento ("es" o "en")
        custom_reference: Referencia personalizada (ej: "CAND0001 L.L.L")
        custom_name: Nombre personalizado del candidato
    
    Returns:
        str: Ruta al archivo generado
    """
    print("=" * 80)
    print("🚀 INICIANDO PROCESAMIENTO DE CV DESDE PDF")
    print("=" * 80)
    
    # Validar que existe el PDF
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        print(f"❌ Error: No se encontró el archivo PDF: {pdf_path}")
        return None
    
    # Validar que existe el logo
    logo_file = Path(logo_path)
    if not logo_file.exists():
        print(f"⚠️  Advertencia: No se encontró el logo: {logo_path}")
        print(f"   El documento se generará sin logo")
        # Podrías decidir continuar o abortar aquí
    
    try:
        # PASO 1: Extraer texto del PDF
        print(f"\n📥 PASO 1: Extrayendo texto del PDF (idioma: {language.upper()})...")
        print("-" * 80)
        raw_text = extract_text_from_pdf(pdf_path, language=language)
        print(f"\n✅ Texto extraído: {len(raw_text)} caracteres")
        
        # PASO 2: Estructurar con ChatGPT
        print(f"\n🤖 PASO 2: Estructurando datos con ChatGPT (idioma: {language.upper()})...")
        print("-" * 80)
        structured_data = structure_cv_with_chatgpt(raw_text, language=language)
        
        # Sobrescribir nombre si se proporciona custom_name
        if custom_name:
            structured_data['profile_data']['name'] = custom_name
        
        # PASO 3: Validar datos
        print("\n✔️  PASO 3: Validando estructura de datos...")
        print("-" * 80)
        if not validate_cv_data(structured_data):
            print("❌ Error: Los datos estructurados no son válidos")
            return None
        
        # PASO 4: Generar documento Word
        print(f"\n📝 PASO 4: Generando documento Word (idioma: {language.upper()})...")
        print("-" * 80)
        
        doc = generate_cv(
            logo_path=logo_path,
            profile_data=structured_data['profile_data'],
            experience_list=structured_data['experience_list'],
            education_list=structured_data['education_list'],
            certifications_list=structured_data['certifications_list'],
            language=language,
            custom_reference=custom_reference
        )
        
        # Determinar nombre del archivo de salida
        if output_path is None:
            # Generar nombre basado en el nombre del candidato
            candidate_name = structured_data['profile_data']['name']
            safe_name = candidate_name.replace(" ", "_")
            output_path = f"CV_{safe_name}.docx"
        
        # Guardar documento
        doc.save(output_path)
        
        print("=" * 80)
        print(f"✅ ¡CV GENERADO EXITOSAMENTE!")
        print(f"📄 Archivo: {Path(output_path).resolve()}")
        print("=" * 80)
        
        return output_path
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Función principal con interfaz de línea de comandos"""
    print("\n" + "=" * 80)
    print("📋 GENERADOR DE CVs DESDE PDF")
    print("=" * 80)
    
    # Si se pasa argumento de línea de comandos
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        logo_path = sys.argv[2] if len(sys.argv) > 2 else "logo.png"
        output_path = sys.argv[3] if len(sys.argv) > 3 else None
        
        process_cv_from_pdf(pdf_path, logo_path, output_path)
    else:
        # Modo interactivo
        print("\n📝 Modo Interactivo")
        print("-" * 80)
        
        pdf_path = input("📄 Ruta del PDF del CV: ").strip()
        if not pdf_path:
            print("❌ Ruta del PDF es requerida")
            return
        
        logo_path = input("🖼️  Ruta del logo (Enter para 'logo.png'): ").strip()
        if not logo_path:
            logo_path = "logo.png"
        
        language = input("🌍 Idioma (es/en, Enter para 'es'): ").strip().lower()
        if language not in ["es", "en"]:
            language = "es"
        
        custom_reference = input("🔖 Referencia personalizada (Enter para auto): ").strip()
        if not custom_reference:
            custom_reference = None
        
        custom_name = input("👤 Nombre personalizado (Enter para auto): ").strip()
        if not custom_name:
            custom_name = None
        
        output_path = input("💾 Ruta de salida (Enter para auto-generar): ").strip()
        if not output_path:
            output_path = None
        
        process_cv_from_pdf(pdf_path, logo_path, output_path, language, custom_reference, custom_name)


if __name__ == "__main__":
    main()

