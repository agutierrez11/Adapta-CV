"""
Módulo de procesamiento de CV usando DeepSeek y Groq API.
Realiza optimización de CV para ATS manteniendo autenticidad.
"""

import json
import os
from typing import Optional, Literal
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
    """Clase principal para optimizar CVs usando DeepSeek o Groq"""
    
    def __init__(self, provider: Literal["deepseek", "groq"] = "groq", api_key: Optional[str] = None):
        """
        Inicializa el optimizador.
        """
        self.provider = provider
        self.api_key = api_key
        
        if provider == "deepseek":
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
            self.base_url = "https://api.deepseek.com"
            self.model = "deepseek-chat"
        else:
            self.api_key = api_key or os.getenv("GROQ_API_KEY")
            self.base_url = "https://api.groq.com/openai/v1"
            self.model = "llama-3.3-70b-versatile"
            
        if not self.api_key:
            raise ValueError(f"API key para {provider} no encontrada.")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def optimize_cv(
        self, 
        cv_text: str, 
        job_description: str,
        language: str = "es"
    ) -> OptimizedCV:
        """
        Optimiza un CV basado en una descripción de empleo.
        """
        
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
        user_message = config["user_prompt"].format(
            cv_text=cv_text,
            job_description=job_description
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": config["system_prompt"]},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            response_format={"type": "json_object"} if self.provider == "groq" else None
        )
        
        response_text = response.choices[0].message.content
        
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                cv_dict = json.loads(json_str)
                return OptimizedCV(**cv_dict)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Error al procesar la respuesta: {str(e)}")
    
    @staticmethod
    def _get_spanish_system_prompt() -> str:
        return """Eres un experto en optimización de currículums para sistemas ATS.
Mantiene la autenticidad, alinea semánticamente, usa terminología exacta y destaca logros.
Responde SOLO con un JSON válido."""
    
    @staticmethod
    def _get_english_system_prompt() -> str:
        return """You are an expert in resume optimization for ATS.
Maintain authenticity, align semantically, use exact terminology, and highlight achievements.
Respond ONLY with valid JSON."""
    
    @staticmethod
    def _get_spanish_user_prompt() -> str:
        return """Analiza el CV y la vacante. Genera un JSON optimizado.
CV: {cv_text}
Vacante: {job_description}
JSON Structure:
{{
    "full_name": "", "email": "", "phone": "", "location": "",
    "professional_summary": "", "key_skills": [],
    "experience": [{{"job_title": "", "company": "", "duration": "", "achievements": []}}],
    "education": [{{"degree": "", "institution": "", "year": ""}}],
    "languages": [], "certifications": []
}}"""
    
    @staticmethod
    def _get_english_user_prompt() -> str:
        return """Analyze the resume and job. Generate optimized JSON.
Resume: {cv_text}
Job: {job_description}
JSON Structure:
{{
    "full_name": "", "email": "", "phone": "", "location": "",
    "professional_summary": "", "key_skills": [],
    "experience": [{{"job_title": "", "company": "", "duration": "", "achievements": []}}],
    "education": [{{"degree": "", "institution": "", "year": ""}}],
    "languages": [], "certifications": []
}}"""
