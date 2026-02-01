from fastapi import FastAPI, Body, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from src.normalizer import normalize_job
from src.embedder import generate_embeddings, get_metadata
from src.schemas import JobOutput
from src.database import connect_to_mongo, close_mongo_connection, save_job
import uuid
import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Conductor Job Embedding Service")

# Security Configuration
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)
CONDUCTOR_API_KEY = os.getenv("CONDUCTOR_API_KEY")

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if not CONDUCTOR_API_KEY:
        # If no key is set in env, we might want to fail open or closed. 
        # Failing closed (secure by default) is better for a "restrict" request.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server API Key not configured"
        )
    
    if api_key_header != CONDUCTOR_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    return api_key_header

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.post("/process", response_model=JobOutput, dependencies=[Depends(get_api_key)])
async def process_job(payload: dict = Body(...)):
    # Extract ID or generate
    # We look for common ID fields or generate one
    job_id = payload.get("job_id") or payload.get("id") or str(uuid.uuid4())
    
    # 1. Normalize
    canonical_job = normalize_job(payload, job_id)
    
    # 2. Embed
    embeddings = generate_embeddings(canonical_job.job_data)
    
    # 3. Metadata
    metadata = get_metadata(embeddings)
    
    job_output = JobOutput(
        job_id=job_id,
        cleaned_job=canonical_job.job_data,
        embeddings=embeddings,
        metadata=metadata
    )
    
    # 4. Save to DB
    await save_job(job_output)
    
    return job_output

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
