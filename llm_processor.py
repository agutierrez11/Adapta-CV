import json
import os
import pandas as pd
from typing import Optional, Literal, List
from openai import OpenAI
from pydantic import BaseModel, Field
import trafilatura
from jobspy import scrape_jobs

class CVExperience(BaseModel):
    job_title: str
    company: str
    duration: str
    achievements: list[str]

class CVEducation(BaseModel):
    degree: str
    institution: str
    year: str

class OptimizedCV(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = ""
    location: Optional[str] = ""
    professional_summary: str
    key_skills: list[str]
    experience: list[CVExperience]
    education: list[CVEducation]
    languages: list[str] = []
    certifications: list[str] = []

class ATSAnalysis(BaseModel):
    match_score: int = Field(..., ge=0, le=100)
    missing_keywords: List[str]
    suggestions: List[str]
    strengths: List[str]

class CVOptimizer:
    def __init__(self, provider: Literal["deepseek", "groq"] = "groq", api_key: Optional[str] = None):
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
            
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def search_jobs(self, query: str, location: str = "Remote", results: int = 5) -> pd.DataFrame:
        """Busca empleos en múltiples plataformas usando jobspy."""
        try:
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "glassdoor", "zip_recruiter"],
                search_term=query,
                location=location,
                results_wanted=results,
                hours_old=72,
                country_indeed='spain' if location.lower() == 'spain' else 'usa',
            )
            # Seleccionamos solo las columnas interesantes
            if not jobs.empty:
                return jobs[['title', 'company', 'location', 'job_url', 'site']]
            return pd.DataFrame()
        except Exception as e:
            print(f"Error buscando empleos: {e}")
            return pd.DataFrame()

    def extract_job_from_url(self, url: str) -> str:
        if not url: return ""
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded)
            return content if content else "No se pudo extraer el contenido automáticamente."
        return "Error de acceso a la URL."

    def optimize_cv(self, cv_text: str, job_description: str, language: str = "es") -> OptimizedCV:
        system_prompt = f"""You are an expert ATS resume optimizer. 
Content must be in {language}. 
Respond ONLY with a valid JSON matching this exact structure:
{{
    "full_name": "Full Name",
    "email": "email@example.com",
    "phone": "+123456789",
    "location": "City, Country",
    "professional_summary": "Summary aligned with the job description.",
    "key_skills": ["Skill 1", "Skill 2"],
    "experience": [
        {{
            "job_title": "Job Title",
            "company": "Company Name",
            "duration": "Dates (e.g., Enero 2020 - Presente)",
            "achievements": ["Achievement 1", "Achievement 2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "Institution Name",
            "year": "Graduation Year (e.g., 2020)"
        }}
    ],
    "languages": ["Spanish (Native)", "English (Advanced)"],
    "certifications": ["Certification Name - Issuer - Year"]
}}"""
        user_prompt = f"CV: {cv_text} | Job: {job_description}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"} if self.provider == "groq" else None
        )
        
        content = response.choices[0].message.content
        data = json.loads(content[content.find('{'):content.rfind('}')+1])
        if len(data) == 1 and isinstance(list(data.values())[0], dict):
            data = list(data.values())[0]
            
        # Normalizar experiencia
        if 'experience' in data and isinstance(data['experience'], list):
            for exp in data['experience']:
                if isinstance(exp, dict):
                    if 'duration' not in exp or not exp['duration']:
                        exp['duration'] = exp.get('dates') or exp.get('period') or exp.get('time') or exp.get('years') or "N/A"
                    if 'achievements' not in exp:
                        exp['achievements'] = []
                    elif not isinstance(exp['achievements'], list):
                        exp['achievements'] = [str(exp['achievements'])]
                        
        # Normalizar educación
        if 'education' in data and isinstance(data['education'], list):
            for edu in data['education']:
                if isinstance(edu, dict):
                    if 'year' not in edu or not edu['year']:
                        edu['year'] = edu.get('dates') or edu.get('year') or edu.get('date') or edu.get('graduated') or "N/A"
                        
        # Normalizar idiomas (languages)
        if 'languages' in data and isinstance(data['languages'], list):
            normalized_languages = []
            for lang in data['languages']:
                if isinstance(lang, dict):
                    name = lang.get('language') or lang.get('name') or lang.get('idioma') or ""
                    level = lang.get('level') or lang.get('proficiency') or lang.get('nivel') or ""
                    if name and level:
                        normalized_languages.append(f"{name} ({level})")
                    elif name:
                        normalized_languages.append(name)
                elif isinstance(lang, str):
                    normalized_languages.append(lang)
            data['languages'] = normalized_languages
            
        # Normalizar certificaciones
        if 'certifications' in data and isinstance(data['certifications'], list):
            normalized_certs = []
            for cert in data['certifications']:
                if isinstance(cert, dict):
                    name = cert.get('name') or cert.get('title') or cert.get('nombre') or ""
                    issuer = cert.get('issuer') or cert.get('authority') or cert.get('institution') or ""
                    year = cert.get('year') or cert.get('date') or ""
                    parts = [name]
                    if issuer: parts.append(issuer)
                    if year: parts.append(year)
                    normalized_certs.append(" - ".join(filter(None, parts)))
                elif isinstance(cert, str):
                    normalized_certs.append(cert)
            data['certifications'] = normalized_certs

        # Asegurar campos obligatorios u opcionales
        if 'phone' not in data or data['phone'] is None:
            data['phone'] = ""
        if 'location' not in data or data['location'] is None:
            data['location'] = ""
            
        return OptimizedCV(**data)

    def analyze_ats(self, cv_text: str, job_description: str, language: str = "es") -> ATSAnalysis:
        system_prompt = "ATS Analyzer. Return JSON with: 'match_score', 'missing_keywords', 'suggestions', 'strengths'."
        user_prompt = f"CV: {cv_text} | Job: {job_description}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
            response_format={"type": "json_object"} if self.provider == "groq" else None
        )
        
        content = response.choices[0].message.content
        data = json.loads(content[content.find('{'):content.rfind('}')+1])
        if len(data) == 1 and isinstance(list(data.values())[0], dict):
            data = list(data.values())[0]
            
        # Normalizar match_score si el LLM devuelve una fracción (ej: 0.8 en lugar de 80)
        if 'match_score' in data:
            try:
                score = float(data['match_score'])
                if 0.0 <= score <= 1.0:
                    data['match_score'] = int(score * 100)
                else:
                    data['match_score'] = int(round(score))
            except Exception:
                data['match_score'] = 0
                
        return ATSAnalysis(**data)

    def generate_cover_letter(self, cv_text: str, job_description: str, language: str = "es") -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Write a professional cover letter."},
                {"role": "user", "content": f"Language: {language}. CV: {cv_text} | Job: {job_description}"}
            ]
        )
        return response.choices[0].message.content
