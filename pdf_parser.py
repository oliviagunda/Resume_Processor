"""PDF parsing and text extraction utilities."""
import os
import re
import logging
from typing import Dict, List, Any, Optional
from pypdf import PdfReader
from dataclasses import dataclass

from config import config

# Set up logging
logging.basicConfig(level=getattr(logging, config.app.log_level))
logger = logging.getLogger(__name__)


@dataclass
class ParsedResume:
    """Data class for parsed resume information."""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    total_experience: float = 0.0
    companies: List[Dict[str, str]] = None
    skills: List[str] = None
    raw_text: str = ""
    
    def __post_init__(self):
        if self.companies is None:
            self.companies = []
        if self.skills is None:
            self.skills = []


class ResumeParser:
    """Parser for extracting information from resume PDFs."""
    
    def __init__(self):
        # Common regex patterns for data extraction
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(?:\+?1[-.\s]?)?\(?[2-9]\d{2}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            'name': r'^[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',
        }
        
        # Common skill keywords to look for
        self.skill_keywords = {
            'programming': [
                'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go',
                'swift', 'kotlin', 'typescript', 'scala', 'r', 'matlab', 'sql'
            ],
            'web': [
                'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express',
                'django', 'flask', 'spring', 'laravel', 'rails'
            ],
            'data': [
                'pandas', 'numpy', 'scikit-learn', 'tensorflow', 'pytorch',
                'apache spark', 'hadoop', 'tableau', 'power bi'
            ],
            'cloud': [
                'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform'
            ],
            'databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'oracle'
            ]
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file using pypdf."""
        text = ""
        try:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                page_text = page.extract_text()
                #print(f'page content is : {page_text}')
                if page_text:
                    text += page_text + "\n"
                    # print(f"text ====  {text}")
            logger.info(f"Successfully extracted text from {pdf_path}")
            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract name from resume text."""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and len(line.split()) >= 2:
                # Simple heuristic: if line looks like a name
                if re.match(r'^[A-Z][a-zA-Z]+\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?$', line):
                    print(f"Name: {line}")
                    return line
        return None
    
    def extract_email(self, text: str) -> Optional[str]:
        """Extract email from resume text."""
        emails = re.findall(self.patterns['email'], text)
        return emails[0] if emails else None
    
    def extract_phone(self, text: str) -> Optional[str]:
        """Extract phone number from resume text."""
        phones = re.findall(self.patterns['phone'], text)
        return phones[0] if phones else None
    
    def extract_experience_years(self, text: str) -> float:
        """Extract total years of experience."""
        # Look for patterns like "5 years", "2+ years", etc.
        experience_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?\s+(?:of\s+)?experience',
            r'experience.*?(\d+(?:\.\d+)?)\s*(?:\+)?\s*years?',
            r'(\d+(?:\.\d+)?)\s*yr[s]?\s+exp',
        ]
        
        experience_years = []
        text_lower = text.lower()
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                try:
                    experience_years.append(float(match))
                except ValueError:
                    continue
        
        # Return the maximum found (assuming most recent/comprehensive)
        return max(experience_years) if experience_years else 0.0
    
    def extract_companies(self, text: str) -> List[Dict[str, str]]:
        """Extract company names and tenure information."""
        companies = []
        
        # Look for common patterns in experience sections
        experience_patterns = [
            r'([A-Z][a-zA-Z\s&]+(?:Inc|LLC|Corp|Ltd|Company))\s*[,\-\s]*(\d{4}\s*[–\-]\s*(?:\d{4}|Present))',
            r'([A-Z][a-zA-Z\s&]+)\s*[,\-\s]*(\d{4}\s*[–\-]\s*(?:\d{4}|Present|Current))',
        ]
        
        for pattern in experience_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for company, tenure in matches:
                companies.append({
                    'company_name': company.strip(),
                    'tenure': tenure.strip()
                })
        
        # Remove duplicates while preserving order
        seen = set()
        unique_companies = []
        for company in companies:
            company_key = company['company_name'].lower()
            if company_key not in seen:
                seen.add(company_key)
                unique_companies.append(company)
        
        return unique_companies[:5]  # Limit to top 5 companies
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text."""
        skills_found = set()
        text_lower = text.lower()
        
        # Search for predefined skill keywords
        for category, skills in self.skill_keywords.items():
            for skill in skills:
                if skill.lower() in text_lower:
                    skills_found.add(skill.title())
        
        # Look for skills section
        skills_section_patterns = [
            r'(?:Technical\s+Skills|Skills|Technologies|Programming\s+Languages)[\s:]*\n([^\n]+(?:\n[^\n]+)*?)(?:\n\s*\n|\Z)',
            r'(?:Skills|Technologies)[\s:]*([^\n]+)',
        ]
        
        for pattern in skills_section_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                # Extract individual skills from the section
                skills_text = match.replace(',', ' ').replace('•', ' ').replace('-', ' ')
                potential_skills = re.split(r'[,\n\|•\-]', skills_text)
                
                for skill in potential_skills:
                    skill = skill.strip()
                    if len(skill) > 2 and len(skill) < 25:  # Filter reasonable skill names
                        skills_found.add(skill)
        
        return list(skills_found)[:20]  # Limit to top 20 skills
    
    def parse_resume(self, pdf_path: str) -> ParsedResume:
        """Parse a resume PDF and extract all relevant information."""
        logger.info(f"Parsing resume: {pdf_path}")
        
        # Extract text from PDF
        raw_text = self.extract_text_from_pdf(pdf_path)
        
        if not raw_text:
            logger.warning(f"No text extracted from {pdf_path}")
            return ParsedResume(raw_text=raw_text)
        
        # Extract information
        parsed = ParsedResume(
            name=self.extract_name(raw_text),
            email=self.extract_email(raw_text),
            phone=self.extract_phone(raw_text),
            total_experience=self.extract_experience_years(raw_text),
            companies=self.extract_companies(raw_text),
            skills=self.extract_skills(raw_text),
            raw_text=raw_text
        )
        
        logger.info(f"Successfully parsed resume: {parsed.name or 'Unknown'}")
        return parsed
    
    def parse_resumes_from_folder(self, folder_path: str) -> List[ParsedResume]:
        """Parse all PDF files in a folder."""
        parsed_resumes = []
        
        if not os.path.exists(folder_path):
            logger.error(f"Folder not found: {folder_path}")
            return parsed_resumes
        
        pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
        logger.info(f"Found {len(pdf_files)} PDF files in {folder_path}")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(folder_path, pdf_file)
            parsed_resume = self.parse_resume(pdf_path)
            parsed_resumes.append(parsed_resume)
        
        return parsed_resumes


# Global parser instance
resume_parser = ResumeParser()