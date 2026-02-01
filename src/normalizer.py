import re
from typing import List, Optional, Any, Dict
from src.schemas import CanonicalJob, JobData, JobSections

def clean_string(text: Any) -> Optional[str]:
    if not text:
        return None
    if not isinstance(text, str):
        text = str(text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text if text else None

def clean_list(items: Any) -> List[str]:
    if not items:
        return []
    
    cleaned_items = []
    
    # Handle string that should be a list (simple split by newline or bullet points if explicitly structured)
    if isinstance(items, str):
        # Heuristic: split by newlines if it looks like a list
        if '\n' in items:
            raw_list = items.split('\n')
        else:
            # If no newlines, treat as single item
            raw_list = [items]
    elif isinstance(items, list):
        raw_list = items
    else:
        return []

    for item in raw_list:
        cleaned = clean_string(item)
        if cleaned:
            cleaned_items.append(cleaned)
            
    return cleaned_items

def get_first_value(data: Dict, keys: List[str]) -> Any:
    # Helper to normalize a key for comparison (lowercase, remove non-alphanumeric)
    def normalize_key(k: str) -> str:
        return re.sub(r'[^a-z0-9]', '', str(k).lower())

    # Create a map of normalized data keys to original keys
    normalized_data_keys = {normalize_key(k): k for k in data.keys()}
    
    for key in keys:
        norm_key = normalize_key(key)
        if norm_key in normalized_data_keys:
            return data[normalized_data_keys[norm_key]]
    return None

def normalize_job(raw_data: Dict, job_id: str) -> CanonicalJob:
    # Mappings - refined for LinkedIn & Naukri Schemas
    # Naukri: "Job Title", "Key Skills", "Job Experience Required", "joblocation_address", "Uniq Id"
    
    # ID fallback if passed explicitly in raw_data and job_id is just a uuid
    if "uniq_id" in raw_data:
        job_id = str(raw_data["uniq_id"])
    elif "jobid" in raw_data:
        job_id = str(raw_data["jobid"])

    title = clean_string(get_first_value(raw_data, ["title", "job_title", "role", "position", "job title"]))
    
    company = clean_string(get_first_value(raw_data, ["company_name", "company", "employer"]))
    
    location = clean_string(get_first_value(raw_data, ["location", "city", "place", "joblocation_address", "job location"]))
    
    employment_type = clean_string(get_first_value(raw_data, ["formatted_work_type", "work_type", "employment_type"]))
    
    experience_required = clean_string(get_first_value(raw_data, ["formatted_experience_level", "experience_required", "experience", "job experience required"]))
    
    # Sections
    required_skills = clean_list(get_first_value(raw_data, ["skills_desc", "required_skills", "skills", "key skills"]))
    
    responsibilities = clean_list(get_first_value(raw_data, ["responsibilities", "duties"]))
    qualifications = clean_list(get_first_value(raw_data, ["qualifications", "requirements", "education"]))
    
    description = clean_string(get_first_value(raw_data, ["description", "job_description", "job description"]))

    sections = JobSections(
        required_skills=required_skills,
        responsibilities=responsibilities,
        qualifications=qualifications,
        description=description
    )

    job_data = JobData(
        title=title,
        company=company,
        location=location,
        employment_type=employment_type,
        experience_required=experience_required,
        sections=sections
    )

    return CanonicalJob(job_id=job_id, job_data=job_data)
