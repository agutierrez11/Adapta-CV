"""
Módulo de procesamiento de CV usando DeepSeek API.
Realiza optimización de CV para ATS manteniendo autenticidad.
"""

import json
import os
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field


class CVExperience(BaseModel):
    """Modelo para una experiencia laboral optimizada"""
    job_title: str = Field(..., description="Título del puesto")
    company: str = Field(..., description="Nombre de la empresa")
    duration: str = Field(..., description="Duración (ej: 'Enero 2020 - Marzo 2023')")
    achievements: list[str] = Field(
        ..., 
        description="Lista de logros y responsabilidades clave, alineados con la vacante"
    )


class CVEducation(BaseModel):
    """Modelo para educación"""
    degree: str = Field(..., description="Grado o certificación")
    institution: str = Field(..., description="Institución educativa")
    year: str = Field(..., description="Año de graduación")


class OptimizedCV(BaseModel):
    """Estructura del CV optimizado para ATS"""
    full_name: str = Field(..., description="Nombre completo")
    email: str = Field(..., description="Correo electrónico")
    phone: Optional[str] = Field(None, description="Teléfono (opcional)")
    location: Optional[str] = Field(None, description="Ubicación (opcional)")
    professional_summary: str = Field(
        ..., 
        description="Resumen profesional alineado con la vacante (2-3 líneas)"
    )
    key_skills: list[str] = Field(
        ..., 
        description="Habilidades clave extraídas de la vacante y presentes en el perfil"
    )
    experience: list[CVExperience] = Field(
        ..., 
        description="Experiencia laboral optimizada"
    )
    education: list[CVEducation] = Field(
        ..., 
        description="Educación y certificaciones"
    )
    languages: list[str] = Field(
        default_factory=list,
        description="Idiomas que domina"
    )
    certifications: list[str] = Field(
        default_factory=list,
        description="Certificaciones relevantes"
    )


class CVOptimizer:
    """Clase principal para optimizar CVs usando DeepSeek"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el optimizador con la API de DeepSeek.
        
        Args:
            api_key: Clave de API de DeepSeek. Si no se proporciona, 
                    se busca en la variable de entorno DEEPSEEK_API_KEY
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "DeepSeek API key no encontrada. "
                "Proporciona 'api_key' o establece DEEPSEEK_API_KEY"
            )
        
        # Configurar cliente OpenAI compatible con DeepSeek
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.deepseek.com"
        )
    
    def optimize_cv(
        self, 
        cv_text: str, 
        job_description: str,
        language: str = "es"
    ) -> OptimizedCV:
        """
        Optimiza un CV basado en una descripción de empleo.
        
        Args:
            cv_text: Texto del CV actual del usuario
            job_description: Descripción de la vacante
            language: Idioma del CV ('es' para español, 'en' para inglés)
        
        Returns:
            OptimizedCV: Estructura del CV optimizado
        """
        
        # Seleccionar idioma para el prompt
        lang_config = {
            "es": {
                "name": "español",
                "system_prompt": self._get_spanish_system_prompt(),
                "user_prompt": self._get_spanish_user_prompt()
            },
            "en": {
                "name": "English",
                "system_prompt": self._get_english_system_prompt(),
                "user_prompt": self._get_english_user_prompt()
            }
        }
        
        if language not in lang_config:
            language = "es"
        
        config = lang_config[language]
        
        # Construir el prompt del usuario
        user_message = config["user_prompt"].format(
            cv_text=cv_text,
            job_description=job_description
        )
        
        # Llamar a DeepSeek API
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=2000,
            messages=[
                {
                    "role": "system",
                    "content": config["system_prompt"]
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.7
        )
        
        # Extraer JSON de la respuesta
        response_text = response.choices[0].message.content
        
        # Intentar parsear JSON
        try:
            # Buscar JSON en la respuesta
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                cv_dict = json.loads(json_str)
                return OptimizedCV(**cv_dict)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(
                f"Error al procesar la respuesta del LLM: {str(e)}\n"
                f"Respuesta: {response_text[:500]}"
            )
    
    @staticmethod
    def _get_spanish_system_prompt() -> str:
        """Retorna el prompt del sistema en español"""
        return """Eres un experto en optimización de currículums para sistemas ATS (Applicant Tracking Systems).

Tu tarea es analizar el CV del usuario y la descripción de la vacante, luego generar un CV optimizado que:

1. **Mantiene la autenticidad**: NUNCA inventes experiencias, títulos, años o tecnologías que no estén en el CV original.
2. **Alinea semánticamente**: Identifica las palabras clave de la vacante y reescribe los puntos de experiencia del usuario para que resalten esa alineación de forma natural.
3. **Usa terminología exacta**: Si el usuario domina una tecnología pero la escribió diferente, reescribe para incluir el término exacto de la vacante.
4. **Destaca logros**: Reescribe responsabilidades usando la fórmula: "Logré X, medido por Y, haciendo Z".
5. **Respeta el formato ATS**: Genera un JSON limpio y estructurado que será convertido a Word/PDF con formato de una sola columna.

IMPORTANTE: Responde SOLO con un JSON válido, sin explicaciones adicionales."""
    
    @staticmethod
    def _get_english_system_prompt() -> str:
        """Retorna el prompt del sistema en inglés"""
        return """You are an expert in resume optimization for ATS (Applicant Tracking Systems).

Your task is to analyze the user's resume and the job description, then generate an optimized resume that:

1. **Maintains authenticity**: NEVER invent experiences, titles, years, or technologies not in the original resume.
2. **Aligns semantically**: Identify job description keywords and rewrite the user's experience points to highlight that alignment naturally.
3. **Uses exact terminology**: If the user has a skill but wrote it differently, rewrite to include the exact job description term.
4. **Highlights achievements**: Rewrite responsibilities using the formula: "Achieved X, measured by Y, by doing Z".
5. **Respects ATS format**: Generate clean, structured JSON that will be converted to Word/PDF in single-column format.

IMPORTANT: Respond ONLY with valid JSON, no additional explanations."""
    
    @staticmethod
    def _get_spanish_user_prompt() -> str:
        """Retorna el prompt del usuario en español"""
        return """Analiza el siguiente CV y descripción de vacante. Genera un CV optimizado en formato JSON.

--- CV ACTUAL ---
{cv_text}

--- DESCRIPCIÓN DE LA VACANTE ---
{job_description}

Retorna SOLO un JSON con esta estructura exacta (reemplaza los valores):
{{
    "full_name": "Nombre Completo",
    "email": "email@example.com",
    "phone": "+34 XXX XXX XXX",
    "location": "Ciudad, País",
    "professional_summary": "Resumen profesional de 2-3 líneas alineado con la vacante",
    "key_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
    "experience": [
        {{
            "job_title": "Título del Puesto",
            "company": "Nombre Empresa",
            "duration": "Enero 2020 - Marzo 2023",
            "achievements": [
                "Logro 1 alineado con la vacante",
                "Logro 2 alineado con la vacante"
            ]
        }}
    ],
    "education": [
        {{
            "degree": "Grado/Certificación",
            "institution": "Institución",
            "year": "2020"
        }}
    ],
    "languages": ["Español", "Inglés"],
    "certifications": ["Certificación 1", "Certificación 2"]
}}"""
    
    @staticmethod
    def _get_english_user_prompt() -> str:
        """Retorna el prompt del usuario en inglés"""
        return """Analyze the following resume and job description. Generate an optimized resume in JSON format.

--- CURRENT RESUME ---
{cv_text}

--- JOB DESCRIPTION ---
{job_description}

Return ONLY a JSON with this exact structure (replace the values):
{{
    "full_name": "Full Name",
    "email": "email@example.com",
    "phone": "+1 XXX XXX XXXX",
    "location": "City, Country",
    "professional_summary": "Professional summary of 2-3 lines aligned with the job",
    "key_skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"],
    "experience": [
        {{
            "job_title": "Job Title",
            "company": "Company Name",
            "duration": "January 2020 - March 2023",
            "achievements": [
                "Achievement 1 aligned with the job",
                "Achievement 2 aligned with the job"
            ]
        }}
    ],
    "education": [
        {{
            "degree": "Degree/Certification",
            "institution": "Institution",
            "year": "2020"
        }}
    ],
    "languages": ["Spanish", "English"],
    "certifications": ["Certification 1", "Certification 2"]
}}"""
