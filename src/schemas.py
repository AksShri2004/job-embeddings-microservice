from typing import List, Optional, Dict
from pydantic import BaseModel, Field

class JobSections(BaseModel):
    required_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    description: Optional[str] = None

class JobData(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    experience_required: Optional[str] = None
    sections: JobSections

class CanonicalJob(BaseModel):
    job_id: str
    job_data: JobData

class EmbeddingData(BaseModel):
    text: Optional[str] = None
    vector: Optional[List[float]] = None

class Embeddings(BaseModel):
    title: EmbeddingData
    required_skills: EmbeddingData
    responsibilities: EmbeddingData
    qualifications: EmbeddingData
    description: EmbeddingData

class Metadata(BaseModel):
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    vector_dimension: int = 384
    sections_embedded: List[str]
    embedding_ready: bool

class JobOutput(BaseModel):
    job_id: str
    cleaned_job: JobData
    embeddings: Embeddings
    metadata: Metadata
