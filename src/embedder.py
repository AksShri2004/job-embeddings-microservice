from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import numpy as np
from src.schemas import JobData, Embeddings, EmbeddingData, Metadata

# Load environment variables
load_dotenv()

# Global model instance
_MODEL = None

def get_model():
    global _MODEL
    if _MODEL is None:
        # Load the model with optional token
        token = os.getenv("HF_TOKEN")
        print(f"Loading embedding model BAAI/bge-small-en-v1.5... (Token present: {bool(token)})")
        _MODEL = SentenceTransformer('BAAI/bge-small-en-v1.5', token=token)
    return _MODEL

def generate_text_representation(field_name: str, value: Any) -> Optional[str]:
    if not value:
        return None
    
    if isinstance(value, str):
        return value
    
    if isinstance(value, list):
        if not value:
            return None
        # For skills, comma separated looks good.
        if field_name == "required_skills":
            return ", ".join(value)
        # For other lists like responsibilities/qualifications, join with period or newline
        # bge models handle text chunks well.
        return " ".join(value)
        
    return str(value)

def generate_embeddings(job_data: JobData) -> Embeddings:
    model = get_model()
    
    sections_to_embed = {
        "title": job_data.title,
        "required_skills": job_data.sections.required_skills,
        "responsibilities": job_data.sections.responsibilities,
        "qualifications": job_data.sections.qualifications,
        "description": job_data.sections.description
    }
    
    embedding_results = {}
    
    for key, value in sections_to_embed.items():
        text = generate_text_representation(key, value)
        vector = None
        
        if text:
            # Generate embedding
            # normalize_embeddings=True ensures L2 normalization
            emb = model.encode(text, normalize_embeddings=True)
            vector = emb.tolist()
            
        embedding_results[key] = EmbeddingData(text=text, vector=vector)
        
    return Embeddings(
        title=embedding_results["title"],
        required_skills=embedding_results["required_skills"],
        responsibilities=embedding_results["responsibilities"],
        qualifications=embedding_results["qualifications"],
        description=embedding_results["description"]
    )

def get_metadata(embeddings: Embeddings) -> Metadata:
    sections_embedded = []
    if embeddings.title.vector: sections_embedded.append("title")
    if embeddings.required_skills.vector: sections_embedded.append("required_skills")
    if embeddings.responsibilities.vector: sections_embedded.append("responsibilities")
    if embeddings.qualifications.vector: sections_embedded.append("qualifications")
    if embeddings.description.vector: sections_embedded.append("description")
    
    # "embedding_ready=false if critical sections cannot be embedded"
    # Let's assume title and at least one other section is critical, or just if anything was embedded.
    # The prompt says "Continue best-effort... embedding_ready=false if critical sections cannot be embedded".
    # I'll define "critical" as having at least a title or description.
    is_ready = bool(sections_embedded) 
    
    return Metadata(
        embedding_model="BAAI/bge-small-en-v1.5",
        vector_dimension=384,
        sections_embedded=sections_embedded,
        embedding_ready=is_ready
    )
