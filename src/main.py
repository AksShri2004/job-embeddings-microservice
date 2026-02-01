from fastapi import FastAPI, Body
from src.normalizer import normalize_job
from src.embedder import generate_embeddings, get_metadata
from src.schemas import JobOutput
from src.database import connect_to_mongo, close_mongo_connection, save_job
import uuid
import uvicorn

app = FastAPI(title="Conductor Job Embedding Service")

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.post("/process", response_model=JobOutput)
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
