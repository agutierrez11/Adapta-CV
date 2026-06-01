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
        system_prompt = f"Expert ATS optimizer. Return JSON with EXACTLY: 'full_name', 'email', 'phone', 'location', 'professional_summary', 'key_skills', 'experience', 'education', 'languages', 'certifications'. Content in {language}."
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
