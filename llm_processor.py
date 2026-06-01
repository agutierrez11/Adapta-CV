import json
import os
from typing import Optional, Literal, List
from openai import OpenAI
from pydantic import BaseModel, Field
import trafilatura

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
    phone: Optional[str] = None
    location: Optional[str] = None
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

    def extract_job_from_url(self, url: str) -> str:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            content = trafilatura.extract(downloaded)
            return content if content else "No se pudo extraer el contenido de la URL."
        return "No se pudo acceder a la URL."

    def optimize_cv(self, cv_text: str, job_description: str, language: str = "es") -> OptimizedCV:
        system_prompt = "You are an expert ATS resume optimizer. Respond ONLY with valid JSON."
        user_prompt = f"Optimize this CV for this job description in {language}. CV: {cv_text} | Job: {job_description}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if self.provider == "groq" else None
        )
        
        content = response.choices[0].message.content
        return OptimizedCV(**json.loads(content[content.find('{'):content.rfind('}')+1]))

    def analyze_ats(self, cv_text: str, job_description: str, language: str = "es") -> ATSAnalysis:
        system_prompt = "You are an ATS (Applicant Tracking System) simulator. Analyze the match between the CV and the job description. Respond ONLY with valid JSON."
        user_prompt = f"""
        Language: {language}
        Analyze the match between this CV and Job Description.
        CV: {cv_text}
        Job: {job_description}
        
        Return a JSON with:
        - match_score: (0-100)
        - missing_keywords: (list of important keywords from job not in CV)
        - suggestions: (how to improve the match)
        - strengths: (what matches well)
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"} if self.provider == "groq" else None
        )
        
        content = response.choices[0].message.content
        return ATSAnalysis(**json.loads(content[content.find('{'):content.rfind('}')+1]))

    def generate_cover_letter(self, cv_text: str, job_description: str, language: str = "es") -> str:
        system_prompt = "You are an expert career coach. Write a persuasive, professional cover letter."
        user_prompt = f"Write a cover letter in {language} based on this CV and job description. CV: {cv_text} | Job: {job_description}"
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
