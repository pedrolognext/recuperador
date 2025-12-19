"""
Servicios para extraer información de PDFs y estructurarla con ChatGPT
"""
import os
import asyncio
import json
from pathlib import Path
from llama_cloud_services import LlamaParse
from openai import OpenAI
# Cargar variables de entorno desde ubicación estándar
import env_loader


# --------------------------------------------------------------------------
# SERVICIO 1: Extracción de PDF con LlamaParse
# --------------------------------------------------------------------------

def extract_text_from_pdf(pdf_path, output_dir="temp_output", language="es"):
    """
    Extrae texto plano de un PDF usando LlamaParse
    
    Args:
        pdf_path: Ruta al archivo PDF
        output_dir: Directorio temporal para guardar resultados
        language: Idioma del PDF ("es" para español, "en" para inglés)
    
    Returns:
        str: Texto extraído del PDF
    """
    # Configurar API key
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    
    # Crear parser
    parser = LlamaParse(
        api_key=api_key,
        num_workers=2,
        verbose=True,
        language=language  # Usar idioma seleccionado
    )
    
    # Crear directorio de salida
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True, parents=True)
    
    # Ejecutar parsing asíncrono
    async def parse_pdf():
        pdf_path_obj = Path(pdf_path)
        
        print(f"📄 Procesando PDF: {pdf_path_obj.resolve()}")
        print(f"   Existe: {pdf_path_obj.exists()}")
        
        if pdf_path_obj.exists():
            print(f"   Tamaño: {pdf_path_obj.stat().st_size} bytes")
        
        # Parsear PDF
        result = await parser.aparse(str(pdf_path_obj))
        
        # Obtener documentos de texto (sin split por página)
        text_docs = result.get_text_documents(split_by_page=False)
        
        # Combinar todo el texto
        combined_text = "\n\n".join([doc.text for doc in text_docs])
        
        # Guardar en archivo temporal
        output_file = output_path / "extracted_text.txt"
        output_file.write_text(combined_text, encoding="utf-8")
        
        print(f"✅ Texto extraído guardado en: {output_file.resolve()}")
        
        return combined_text
    
    # Ejecutar con asyncio
    return asyncio.run(parse_pdf())


# --------------------------------------------------------------------------
# SERVICIO 2: Estructuración con ChatGPT
# --------------------------------------------------------------------------

def structure_cv_with_chatgpt(raw_text, openai_api_key=None, language="es"):
    """
    Envía el texto extraído a ChatGPT para estructurarlo en formato JSON
    
    Args:
        raw_text: Texto plano del CV extraído del PDF
        openai_api_key: API key de OpenAI (opcional, usa variable de entorno)
        language: Idioma objetivo ("es" o "en")
    
    Returns:
        dict: Datos estructurados del CV con las siguientes claves:
            - profile_data
            - experience_list
            - education_list
            - certifications_list
    """
    # Configurar cliente OpenAI
    if openai_api_key is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise ValueError("Se requiere OPENAI_API_KEY como variable de entorno o parámetro")
    
    client = OpenAI(api_key=openai_api_key)
    
    # Adaptar prompt según el idioma
    if language == "en":
        prompt = f"""Extract information from the following CV EXACTLY as it appears, respecting the ORIGINAL SECTIONS. Use this JSON structure:

{{
  "profile_data": {{
    "name": "Full EXACT name from CV",
    "role": "EXACT professional title as appears",
    "reference": "Reference code if exists, otherwise generate one like 'CAND#### X.X.X.'",
    "summary": "COMPLETE and TEXTUAL professional summary, without summarizing",
    "languages": [
      {{"lang": "EXACT language", "level": "EXACT level"}}
    ],
    "skills": [
      "PRIORITIZE technical skills: tools, technologies, languages, software, platforms"
    ]
  }},
  "experience_list": [
    {{
      "company": "EXACT company name",
      "role": "EXACT position",
      "dates": "EXACT dates as they appear",
      "description": "COMPLETE and TEXTUAL project/context description, without summarizing",
      "achievements": [
        "TEXTUAL copy of each achievement/responsibility, without summarizing",
        "Keep ALL listed responsibilities"
      ]
    }}
  ],
  "education_list": [
    "ONLY elements under 'Education' section - DO NOT include certifications here"
  ],
  "certifications_list": [
    "ONLY elements under 'Certifications' section - DO NOT put them in education"
  ]
}}

CRITICAL RULES - FOLLOW THESE EXACTLY:
1. DO NOT SUMMARIZE ANYTHING - copy text exactly as it appears
2. DO NOT CHANGE technical words, company names, technologies
3. DO NOT OMIT information - include EVERYTHING you find
4. DO NOT MIX SECTIONS - keep Education and Certifications separate
5. DO NOT REORGANIZE skills - keep them as individual list
6. RESPECT the CV's original section structure
7. Each skill must be a separate element in the array, not grouped
8. PRIORITIZE ALWAYS technical skills over soft skills
9. INCLUDE ALL tools, technologies and software mentioned
10. DO NOT omit specific technologies like Java, Angular, PostgreSQL, JIRA, etc.
11. KEEP content in ENGLISH if it's in English

CORRECT SKILLS EXAMPLE:
If the CV says:
• Google professional tools
• Microsoft Office tools  
• IT Agile and Scrum
• Data Analysis
• JIRA/Confluence
• Java
• Angular

Then skills should be:
"skills": [
  "Google professional tools",
  "Microsoft Office tools", 
  "IT Agile and Scrum",
  "Data Analysis",
  "JIRA/Confluence",
  "Java",
  "Angular"
]

IMPORTANT FOR SKILLS:
- PRIORITIZE technical skills (tools, software, programming languages, platforms)
- INCLUDE all mentioned technologies (Java, Angular, PostgreSQL, etc.)
- INCLUDE work tools (JIRA, Confluence, Postman, Eclipse, etc.)
- INCLUDE platforms and services (Google tools, Microsoft Office, AWS, etc.)
- IF THERE ARE both soft skills and technical skills, PRIORITIZE technical ones
- DO NOT omit specific tools like "TOAD/SQL DEV/PostgreSQL" or "Postman/Soap UI/Eclipse"

CV TEXT:
{raw_text}

JSON:"""
    else:  # español
        prompt = f"""Extrae la información del siguiente CV EXACTAMENTE como aparece, respetando las SECCIONES ORIGINALES. Usa esta estructura JSON:

{{
  "profile_data": {{
    "name": "Nombre completo EXACTO del CV",
    "role": "Título profesional EXACTO como aparece",
    "reference": "Código de referencia si existe, sino genera uno como 'CAND#### X.X.X.'",
    "summary": "Copia TEXTUAL del resumen profesional completo, sin resumir",
    "languages": [
      {{"lang": "Idioma EXACTO", "level": "Nivel EXACTO"}}
    ],
    "skills": [
      "PRIORIZA skills técnicas: herramientas, tecnologías, lenguajes, software, plataformas"
    ]
  }},
  "experience_list": [
    {{
      "company": "Nombre EXACTO de la empresa",
      "role": "Puesto EXACTO",
      "dates": "Fechas EXACTAS como aparecen",
      "description": "Descripción COMPLETA y TEXTUAL del proyecto/contexto, sin resumir",
      "achievements": [
        "Copia TEXTUAL de cada logro/responsabilidad, sin resumir",
        "Mantén TODAS las responsabilidades listadas"
      ]
    }}
  ],
  "education_list": [
    "SOLO elementos que estén bajo la sección 'Educación' - NO incluyas certificaciones aquí"
  ],
  "certifications_list": [
    "SOLO elementos que estén bajo la sección 'Certificaciones' - NO los pongas en educación"
  ]
}}

REGLAS CRÍTICAS - SIGUE ESTAS EXACTAMENTE:
1. NO RESUMAS NADA - copia el texto exactamente como aparece
2. NO CAMBIES palabras técnicas, nombres de empresas, tecnologías
3. NO OMITAS información - incluye TODO lo que encuentres
4. NO MEZCLES SECCIONES - mantén separadas Educación y Certificaciones
6. NO REORGANICES las skills - mantenlas como lista individual
7. RESPETA la estructura de secciones del CV original
8. Si hay una sección "Skills" separada, NO la pongas en otras secciones
9. Si hay una sección "Certificaciones" separada, NO la pongas en "Educación"
10. Cada skill debe ser un elemento separado en el array, no agrupado
11. PRIORIZA SIEMPRE skills técnicas sobre soft skills
12. INCLUYE TODAS las herramientas, tecnologías y software mencionados
13. NO omitas tecnologías específicas como Java, Angular, PostgreSQL, JIRA, etc.
14. MANTÉN el contenido en ESPAÑOL si está en español

EJEMPLO DE SKILLS CORRECTOS:
Si el CV dice:
• Google professional tools
• Microsoft Office tools  
• IT Agile and Scrum
• Data Analysis
• JIRA/Confluence
• Java
• Angular

Entonces skills debe ser:
"skills": [
  "Google professional tools",
  "Microsoft Office tools", 
  "IT Agile and Scrum",
  "Data Analysis",
  "JIRA/Confluence",
  "Java",
  "Angular"
]

IMPORTANTE PARA SKILLS:
- PRIORIZA skills técnicas (herramientas, software, lenguajes de programación, plataformas)
- INCLUYE todas las tecnologías mencionadas (Java, Angular, PostgreSQL, etc.)
- INCLUYE herramientas de trabajo (JIRA, Confluence, Postman, Eclipse, etc.)
- INCLUYE plataformas y servicios (Google tools, Microsoft Office, AWS, etc.)
- SI HAY TANTO soft skills como technical skills, PRIORIZA las técnicas
- NO omitas herramientas específicas como "TOAD/SQL DEV/PostgreSQL" o "Postman/Soap UI/Eclipse"

TEXTO DEL CV:
{raw_text}

JSON:"""
    
    print("🤖 Enviando texto a ChatGPT para estructuración...")
    
    # Llamada a ChatGPT
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an information extractor that copies CV content EXACTLY without summarizing, modifying or interpreting. Your job is to faithfully transcribe information as it appears in the original document." if language == "en" else "Eres un extractor de información que copia EXACTAMENTE el contenido de CVs sin resumir, modificar o interpretar. Tu trabajo es transcribir fielmente la información tal como aparece en el documento original."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,  # Baja temperatura para respuestas más consistentes
        response_format={"type": "json_object"}
    )
    
    # Extraer respuesta
    json_text = response.choices[0].message.content
    
    print("✅ Respuesta recibida de ChatGPT")
    
    # Parsear JSON
    try:
        structured_data = json.loads(json_text)
        return structured_data
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear JSON de ChatGPT: {e}")
        print(f"Respuesta recibida:\n{json_text}")
        raise


# --------------------------------------------------------------------------
# SERVICIO 3: Validación de datos estructurados
# --------------------------------------------------------------------------

def validate_cv_data(data):
    """
    Valida que los datos estructurados tengan el formato correcto
    
    Args:
        data: Diccionario con los datos estructurados
    
    Returns:
        bool: True si es válido, False si falta algo crítico
    """
    required_keys = ["profile_data", "experience_list", "education_list", "certifications_list"]
    
    for key in required_keys:
        if key not in data:
            print(f"⚠️  Falta clave requerida: {key}")
            return False
    
    # Validar estructura de profile_data
    profile_required = ["name", "role", "reference", "summary", "languages", "skills"]
    for key in profile_required:
        if key not in data["profile_data"]:
            print(f"⚠️  Falta clave en profile_data: {key}")
            return False
    
    print("✅ Datos validados correctamente")
    return True
